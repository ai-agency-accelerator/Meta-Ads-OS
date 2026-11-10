"""API interna + interfaz web mínima. `motor serve` → http://127.0.0.1:8765

Los trabajos largos (crear actor, generar anuncio, regenerar escena, variantes) van a una cola en segundo
plano con progreso persistido en la base de datos.
"""

from __future__ import annotations

import hmac
import io
import json
import os
import re
import threading
import traceback
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, StreamingResponse
from pydantic import BaseModel

from ..costs import summarize
from ..models import Actor, BrandKit, Brief, Job, Product, Project
from ..store import ctx

app = FastAPI(title="Motor de anuncios", version="0.1.0")
_pool = ThreadPoolExecutor(max_workers=1)  # generación secuencial: respeta límites de proveedores
_lock = threading.Lock()
UI = Path(__file__).resolve().parent.parent / "ui" / "index.html"

ID_RE = re.compile(r"^(proj|var|brand|prod|actor|job|scn|shot)_[0-9a-f]{6,24}$")
ASSET_RE = re.compile(r"^[0-9a-f]{24}$")
IMG_EXT = {".png", ".jpg", ".jpeg", ".webp"}
VID_EXT = {".mp4", ".mov", ".webm", ".m4v"}
MAX_UPLOAD = 300 * 1024 * 1024
INLINE_MIME = ("image/", "video/", "audio/")


def _id(x: str) -> str:
    if not ID_RE.match(x or ""):
        raise HTTPException(400, "id no válido")
    return x


def _read_upload(f: UploadFile, allowed: set[str]) -> tuple[bytes, str]:
    ext = Path(f.filename or "").suffix.lower()
    if ext not in allowed:
        raise HTTPException(400, f"tipo de fichero no permitido: {ext or '(sin extensión)'}")
    data = f.file.read(MAX_UPLOAD + 1)
    if len(data) > MAX_UPLOAD:
        raise HTTPException(413, "fichero demasiado grande")
    return data, ext


def _check_url(u: str) -> str:
    """Solo http(s) y nunca hacia la red local (evita leer file:///…/.env o servicios internos)."""
    import ipaddress
    import socket
    from urllib.parse import urlparse

    pu = urlparse(u)
    if pu.scheme not in ("http", "https") or not pu.hostname:
        raise HTTPException(400, "solo se pueden capturar URLs http(s)")
    try:
        for info in socket.getaddrinfo(pu.hostname, None):
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                raise HTTPException(400, "URL hacia la red local no permitida")
    except socket.gaierror:
        raise HTTPException(400, "no se puede resolver el dominio")
    return u


@app.middleware("http")
async def _security(request: Request, call_next):
    s = ctx().settings
    hosts = [h.strip() for h in (os.environ.get("MOTOR_ALLOWED_HOSTS") or "127.0.0.1,localhost,testserver").split(",") if h.strip()]
    host = (request.headers.get("host") or "").split(":")[0]
    if hosts != ["*"] and host not in hosts:
        return PlainTextResponse("host no permitido", status_code=400)
    token = os.environ.get("MOTOR_API_TOKEN") or s.key("MOTOR_API_TOKEN")
    if token and request.url.path != "/":
        sent = request.headers.get("authorization", "").removeprefix("Bearer ").strip() or request.cookies.get("motor_token", "")
        if not hmac.compare_digest(sent, token):
            return PlainTextResponse("no autorizado", status_code=401)
    resp = await call_next(request)
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    return resp


@app.on_event("startup")
def _reconcile() -> None:
    """Tras una caída: los trabajos que estaban corriendo quedan «interrumpidos» (reanudables con /run)."""
    from ..models import Project

    for j in ctx().db.jobs(limit=500):
        if j.status in ("queued", "running"):
            j.status, j.message = "failed", "interrumpido (el servidor se reinició) → vuelve a lanzarlo para reanudar"
            ctx().db.put_job(j)
    for p in ctx().db.list(Project):
        if p.status == "running":
            p.status = "interrupted"
            p.log.append("INTERRUMPIDO: el proceso se detuvo a mitad; `motor run` reanuda sin repetir lo hecho")
            ctx().db.put(p)


class JobCancelled(RuntimeError):
    pass


def _job(kind: str, project_id: str | None, fn: Callable[[Callable[[float, str], None]], Any], payload: dict | None = None) -> Job:
    j = Job(kind=kind, project_id=project_id, payload=payload or {})
    ctx().db.put_job(j)

    def progress(p: float, m: str) -> None:
        with _lock:
            jj = ctx().db.get_job(j.id)
            if jj.status == "cancelled":
                raise JobCancelled(j.id)  # cancelación cooperativa: se detiene en el siguiente punto de control
            jj.progress, jj.message, jj.status = round(p, 3), m, "running"
            ctx().db.put_job(jj)

    def runner() -> None:
        try:
            progress(0.0, "en cola → empezando")
            res = fn(progress)
            jj = ctx().db.get_job(j.id)
            jj.status, jj.progress, jj.result = "done", 1.0, (res if isinstance(res, dict) else {"result": str(res)})
            jj.message = "terminado"
            ctx().db.put_job(jj)
        except JobCancelled:
            jj = ctx().db.get_job(j.id)
            jj.message = "cancelado por el usuario (lo ya generado se conserva)"
            ctx().db.put_job(jj)
        except Exception as e:  # noqa: BLE001
            jj = ctx().db.get_job(j.id)
            jj.status, jj.message = "failed", f"{type(e).__name__}: {str(e)[:400]}"
            jj.result = {"trace": traceback.format_exc()[-2000:]}
            ctx().db.put_job(jj)

    _pool.submit(runner)
    return j


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return UI.read_text(encoding="utf-8")


@app.get("/api/status")
def api_status() -> dict[str, Any]:
    from ..providers.registry import status

    s = ctx().settings
    return {"providers": status(), "keys": {k: s.has(k) for k in ("GEMINI_API_KEY", "FAL_KEY", "OPENAI_API_KEY", "HEYGEN_API_KEY")},
            "spend": summarize(), "budget_global_usd": s.budget_global_usd, "budget_per_project_usd": s.budget_per_project_usd,
            "mock": s.mock}


# ── marcas ──
class BrandIn(BaseModel):
    name: str
    primary: str = "#111111"
    accent: str = "#FF3B30"
    text: str = "#FFFFFF"
    ctas: list[str] = []
    claims: list[str] = []
    dont: list[str] = []
    tone: str = "cercano, directo, nada corporativo"
    label_policy: str = "visible"


@app.get("/api/brands")
def brands() -> list[dict]:
    return [b.model_dump() for b in ctx().db.list(BrandKit)]


@app.post("/api/brands")
def brand_create(b: BrandIn) -> dict:
    bk = BrandKit(name=b.name, colors={"primary": b.primary, "accent": b.accent, "text": b.text}, ctas=b.ctas,
                  approved_claims=b.claims, dont_rules=b.dont, tone=b.tone, ai_label_policy=b.label_policy)  # type: ignore[arg-type]
    ctx().db.put(bk)
    return bk.model_dump()


@app.post("/api/brands/{brand_id}/logo")
def brand_logo(brand_id: str, file: UploadFile = File(...)) -> dict:
    b = ctx().db.get(BrandKit, _id(brand_id))
    data, ext = _read_upload(file, IMG_EXT)
    a = ctx().assets.ingest_bytes(data, ext, source="upload:logo")
    b.logo_asset_ids = [a.id]
    ctx().db.put(b)
    return b.model_dump()


# ── productos ──
@app.get("/api/products")
def products() -> list[dict]:
    return [p.model_dump() for p in ctx().db.list(Product)]


@app.post("/api/products")
def product_create(brand_id: str = Form(...), name: str = Form(...), kind: str = Form("physical"), description: str = Form(""),
                         benefits: str = Form(""), proof: str = Form(""), objections: str = Form(""), capture_url: str = Form(""),
                         label_text: str = Form(""), visual: str = Form(""),
                         screenshots: list[UploadFile] = File(default=[]), packshots: list[UploadFile] = File(default=[]),
                         recordings: list[UploadFile] = File(default=[])) -> dict:
    c = ctx()
    lines = lambda s: [x.strip() for x in s.splitlines() if x.strip()]  # noqa: E731
    p = Product(brand_id=brand_id, name=name, kind=kind, description=description, benefits=lines(benefits),  # type: ignore[arg-type]
                proof_points=lines(proof), objections=lines(objections), expected_label_text=lines(label_text), visual_description=visual)
    for group, allowed, target, src in ((screenshots, IMG_EXT, p.screenshot_asset_ids, "upload:screenshot"),
                                        (packshots, IMG_EXT, p.packshot_asset_ids, "upload:packshot"),
                                        (recordings, VID_EXT, p.screen_recording_asset_ids, "upload:recording")):
        for f in group:
            if f.filename:
                data, ext = _read_upload(f, allowed)
                target.append(c.assets.ingest_bytes(data, ext, source=src).id)
    for u in lines(capture_url):
        from ..pipeline.product import capture_url as cap

        p.screenshot_asset_ids.append(cap(_check_url(u)).id)
    c.db.put(p)
    return p.model_dump()


# ── actores ──
class ActorIn(BaseModel):
    handle: str
    appearance: str
    wardrobe: str = ""
    persona: str = ""
    locale: str = "es-ES"
    voice: str | None = None
    voice_hint: str = ""
    gender: str = "female"
    location: str = ""


@app.get("/api/actors")
def actors() -> list[dict]:
    return [a.model_dump() for a in ctx().db.list(Actor)]


@app.post("/api/actors")
def actor_create(a: ActorIn) -> dict:
    from ..pipeline.actors import create_actor

    j = _job("actor", None, lambda prog: create_actor(a.handle, a.appearance, persona=a.persona, wardrobe=a.wardrobe, locale=a.locale,
                                                      voice_id=a.voice, voice_hint=a.voice_hint, gender=a.gender,
                                                      location_hint=a.location).model_dump(include={"id", "handle"}))
    return j.model_dump()


@app.get("/api/voices")
def voices(language_code: str = "es-ES") -> list[dict]:
    try:
        from ..providers.gemini import list_voices

        return list_voices(language_code)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(400, str(e))


# ── proyectos ──
class ProjectIn(BaseModel):
    brand_id: str
    product_id: str
    actor_id: str | None = None
    objective: str = "conversión"
    audience: str = ""
    messages: list[str] = []
    locale: str = "es-ES"
    duration_s: float = 25
    platform: str = "reels"
    mode: str = "native"
    style: str = ""
    name: str = ""
    budget_usd: float | None = None


@app.get("/api/projects")
def projects() -> list[dict]:
    out = []
    for p in ctx().db.list(Project):
        out.append({"id": p.id, "name": p.name, "status": p.status, "parent": p.parent_id, "locale": p.brief.locale,
                    "render": p.render_asset_id, "cost": summarize(p.id)["total_usd"], "created": p.created_at})
    return out


@app.post("/api/projects")
def project_create(b: ProjectIn) -> dict:
    from ..orchestrator import create_project

    brief = Brief(brand_id=b.brand_id, product_id=b.product_id, actor_ids=[b.actor_id] if b.actor_id else [], objective=b.objective,
                  audience=b.audience, key_messages=b.messages, locale=b.locale, duration_s=b.duration_s, platform=b.platform,  # type: ignore[arg-type]
                  style_notes=b.style, budget_usd=b.budget_usd)
    p = create_project(brief, name=b.name, talk_mode=b.mode)
    return {"id": p.id}


@app.get("/api/projects/{pid}")
def project_get(pid: str) -> dict:
    try:
        p = ctx().db.get(Project, _id(pid))
    except KeyError:
        raise HTTPException(404, "no existe")
    d = p.model_dump()
    d["scene_order"] = p.scene_order()
    d["cost"] = summarize(p.id)
    d["jobs"] = [j.model_dump() for j in ctx().db.jobs(p.id, limit=10)]
    if p.qa_reports:
        from ..qa.judge import summary_lines

        d["qa_lines"] = summary_lines(p.qa_reports[-1])
    return d


@app.post("/api/projects/{pid}/run")
def project_run(pid: str, vlm: bool = True) -> dict:
    from ..orchestrator import run

    ctx().db.get(Project, _id(pid))
    return _job("run", pid, lambda prog: run(pid, prog, use_vlm=vlm)).model_dump()


class RegenIn(BaseModel):
    action: str = "reroll_seed"


@app.post("/api/projects/{pid}/scenes/{sid}/regen")
def scene_regen(pid: str, sid: str, body: RegenIn) -> dict:
    from ..orchestrator import regen_scene

    _id(pid)
    return _job("regen", pid, lambda prog: regen_scene(pid, sid, body.action, prog), {"scene": sid, "action": body.action}).model_dump()


class EditIn(BaseModel):
    instruction: str
    confirm: bool = False


@app.post("/api/projects/{pid}/edit")
def project_edit(pid: str, body: EditIn) -> dict:
    """«regenera la escena 3», «cambia el hook», «hazlo en alemán»… Las órdenes de pago piden confirmación con coste."""
    from ..commands import apply, plan

    _id(pid)
    pl = plan(pid, body.instruction)
    if pl["needs_confirmation"] and not body.confirm:
        return {**pl, "status": "needs_confirmation"}
    return _job("edit", pid, lambda prog: apply(pid, body.instruction, prog, confirm=True), body.model_dump()).model_dump()


class VariantIn(BaseModel):
    kind: str
    value: str | None = None


@app.post("/api/projects/{pid}/variants")
def project_variant(pid: str, body: VariantIn) -> dict:
    from ..variants import make_variant

    return _job("variant", pid, lambda prog: make_variant(pid, body.kind, body.value), body.model_dump()).model_dump()


@app.get("/api/jobs/{jid}")
def job(jid: str) -> dict:
    try:
        return ctx().db.get_job(_id(jid)).model_dump()
    except KeyError:
        raise HTTPException(404, "no existe")


@app.post("/api/jobs/{jid}/cancel")
def job_cancel(jid: str) -> dict:
    try:
        j = ctx().db.get_job(_id(jid))
    except KeyError:
        raise HTTPException(404, "no existe")
    if j.status in ("queued", "running"):
        j.status, j.message = "cancelled", "cancelación solicitada"
        ctx().db.put_job(j)
    return j.model_dump()


@app.get("/api/jobs")
def jobs() -> list[dict]:
    return [j.model_dump() for j in ctx().db.jobs(limit=30)]


@app.get("/api/assets/{aid}")
def asset(aid: str):
    if not ASSET_RE.match(aid):
        raise HTTPException(400, "id no válido")
    try:
        a = ctx().db.get_asset(aid)
    except KeyError:
        raise HTTPException(404, "no existe")
    mime = a.mime or "application/octet-stream"
    inline = mime.startswith(INLINE_MIME) and "svg" not in mime  # nada de HTML/SVG en el mismo origen que la UI
    return FileResponse(ctx().assets.abspath(a), media_type=mime if inline else "application/octet-stream",
                        content_disposition_type="inline" if inline else "attachment")


@app.get("/api/projects/{pid}/export")
def export_zip(pid: str):
    root = ctx().settings.exports_dir.resolve()
    d = (root / _id(pid)).resolve()
    if not d.is_relative_to(root) or not d.exists():
        raise HTTPException(404, "sin exportación todavía")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in d.iterdir():
            if f.is_file():
                z.write(f, f.name)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/zip", headers={"Content-Disposition": f"attachment; filename={pid}.zip"})


@app.get("/api/costs")
def costs(project_id: str | None = None) -> dict:
    return summarize(project_id)


def _json(o: Any) -> str:  # pragma: no cover
    return json.dumps(o, ensure_ascii=False)
