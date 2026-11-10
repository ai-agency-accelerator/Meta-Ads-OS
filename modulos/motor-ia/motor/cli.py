"""CLI del motor. Desde la raíz de Meta Ads OS: `uv run --project modulos/motor-ia motor <orden>`.

Gratis (sin llamadas de pago):
  motor setup                     # modelos locales (caras, OCR, CLIP) y comprobación de FFmpeg/Tesseract
  motor status                    # proveedores activos, claves (✔/·), gasto y presupuesto
  motor brand add --name Nimbo --primary "#2F5BEA" --accent "#12B76A" --cta "Pruébalo 14 días gratis"
  motor product add --brand <id> --name Nimbo --kind app --capture-url https://… --benefit "…"
  motor project new --brand <id> --product <id> --actor @presentadora_01 --objective "pruebas gratuitas" --duration 25
  motor plan-import plans.json --brand <id> --product <id> --actor @presentadora_01
  motor variant <project_id> hook_text "¿Cuánto tardas en contestar a un lead?"   # texto, formato, subtítulos, música
  motor costs [<project_id>]
  motor serve                     # interfaz interna en http://127.0.0.1:8765

De pago (el hook `motor_guard` pide confirmación; con MOTOR_MOCK=1 se simulan a coste 0):
  motor actor create --handle @presentadora_01 --appearance "mujer de 32 años…" --wardrobe "jersey azul marino"
  motor run <project_id>
  motor regen <project_id> <scene_id|índice>
  motor edit <project_id> "regenera la escena 3" --yes
  motor variant <project_id> spoken_cta|language …
  motor demo                      # prueba de referencia completa con Nimbo (anuncio de ~24 s + variantes)
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(add_completion=False, help="Motor autónomo de anuncios en vídeo")
brand_app = typer.Typer(help="Marcas")
product_app = typer.Typer(help="Productos")
actor_app = typer.Typer(help="Actores persistentes")
project_app = typer.Typer(help="Proyectos (anuncios)")
app.add_typer(brand_app, name="brand")
app.add_typer(product_app, name="product")
app.add_typer(actor_app, name="actor")
app.add_typer(project_app, name="project")
con = Console()

FACE_MODELS = {
    "face_detection_yunet_2026may.onnx": "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2026may.onnx",
    "face_detection_yunet_2023mar.onnx": "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    "face_recognition_sface_2021dec.onnx": "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx",
    "face_landmarker.task": "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task",
}
TESS = {
    "spa.traineddata": "https://github.com/tesseract-ocr/tessdata_fast/raw/main/spa.traineddata",
    "eng.traineddata": "https://github.com/tesseract-ocr/tessdata_fast/raw/main/eng.traineddata",
}


def _progress(p: float, m: str) -> None:
    con.print(f"[cyan]{p * 100:5.1f}%[/] {m}")


@app.command()
def setup(clip: bool = typer.Option(True, "--clip/--sin-clip",
                                    help="CLIP (detector de objeto en la mano, ≈150 MB); ver LICENCIAS.md")) -> None:
    """Descarga los modelos locales gratuitos (caras, OCR y, si no pasas --sin-clip, CLIP) y comprueba FFmpeg/Tesseract."""
    import httpx

    from .media import install_hint, tool_status
    from .store import ctx

    s = ctx().settings
    from .qa.objects import URLS as CLIP

    groups = [("face", FACE_MODELS), ("tessdata", TESS)] + ([("clip", CLIP)] if clip else [])
    for sub, files in groups:
        d = s.models_dir / sub
        d.mkdir(parents=True, exist_ok=True)
        for name, url in files.items():
            p = d / name
            if p.exists() and p.stat().st_size > 1000:
                continue
            con.print(f"descargando {name}…")
            with httpx.stream("GET", url, follow_redirects=True, timeout=300) as r:
                r.raise_for_status()
                with open(p, "wb") as f:
                    for chunk in r.iter_bytes():
                        f.write(chunk)
    for tool, ok in tool_status().items():
        extra = "" if ok else f" → {install_hint(tool)}" + (" (opcional: OCR de pantallas y etiqueta de IA)" if tool == "tesseract" else "")
        con.print(f"{tool}: {'ok' if ok else '[red]NO ENCONTRADO[/]'}{extra}")
    status()


@app.command()
def status() -> None:
    """Proveedores activos, claves disponibles y gasto."""
    from .costs import summarize
    from .providers.registry import status as pstatus
    from .store import ctx

    s = ctx().settings
    t = Table(title="Proveedores")
    t.add_column("capacidad")
    t.add_column("adaptador")
    for k, v in pstatus().items():
        t.add_row(k, v)
    con.print(t)
    from .config import KNOWN_KEYS
    from .media import install_hint, tool_status

    shown = [k for k in KNOWN_KEYS if k in ("GEMINI_API_KEY", "FAL_KEY", "OPENAI_API_KEY") or s.has(k)]
    con.print("claves: " + ", ".join(f"{k}={'✔' if s.has(k) else '·'}" for k in shown) + "  (en el .env de la raíz)")
    total = summarize()
    spent = float(total["total_usd"])
    con.print(f"gasto total registrado: [bold]{spent:.3f} $[/] · presupuesto global {s.budget_global_usd:.2f} $ "
              f"({s.budget_source}) · disponible {max(0.0, s.budget_global_usd - spent):.2f} $ · "
              f"por proyecto {s.budget_per_project_usd:.2f} $")
    con.print(f"modo simulado (MOTOR_MOCK): {'sí, coste 0' if s.mock else 'no'} · datos: {s.data_dir}")
    missing = [t for t, ok in tool_status().items() if not ok and t != "tesseract"]
    for t in missing:
        con.print(f"[red]falta {t}[/] → {install_hint(t)}")


# ───────────────────────────── marcas ─────────────────────────────


@brand_app.command("add")
def brand_add(name: str = typer.Option(...), primary: str = "#111111", accent: str = "#FF3B30", text: str = "#FFFFFF",
              logo: Optional[Path] = None, cta: list[str] = typer.Option([]), claim: list[str] = typer.Option([]),
              dont: list[str] = typer.Option([]), tone: str = "cercano, directo, nada corporativo",
              label_policy: str = "visible") -> None:
    from .models import BrandKit
    from .store import ctx

    b = BrandKit(name=name, colors={"primary": primary, "accent": accent, "text": text}, ctas=cta, approved_claims=claim,
                 dont_rules=dont, tone=tone, ai_label_policy=label_policy)  # type: ignore[arg-type]
    if logo:
        b.logo_asset_ids = [ctx().assets.ingest(logo, source="upload:logo").id]
    ctx().db.put(b)
    con.print(f"marca creada: [bold]{b.id}[/]")


@brand_app.command("list")
def brand_list() -> None:
    from .models import BrandKit
    from .store import ctx

    for b in ctx().db.list(BrandKit):
        con.print(f"{b.id}  {b.name}  {b.colors}")


# ───────────────────────────── productos ─────────────────────────────


@product_app.command("add")
def product_add(brand: str = typer.Option(...), name: str = typer.Option(...), kind: str = "physical", description: str = "",
                benefit: list[str] = typer.Option([]), proof: list[str] = typer.Option([]), objection: list[str] = typer.Option([]),
                price: Optional[str] = None, url: Optional[str] = None, screenshot: list[Path] = typer.Option([]),
                recording: list[Path] = typer.Option([]), packshot: list[Path] = typer.Option([]),
                footage: list[Path] = typer.Option([]), capture_url: list[str] = typer.Option([]),
                label_text: list[str] = typer.Option([]), visual: str = "") -> None:
    from .models import Product
    from .pipeline.product import capture_url as cap
    from .store import ctx

    c = ctx()
    p = Product(brand_id=brand, name=name, kind=kind, description=description, benefits=benefit, proof_points=proof,  # type: ignore[arg-type]
                objections=objection, price=price, url=url, expected_label_text=label_text, visual_description=visual)
    p.screenshot_asset_ids = [c.assets.ingest(f, source="upload:screenshot").id for f in screenshot]
    p.screen_recording_asset_ids = [c.assets.ingest(f, source="upload:recording").id for f in recording]
    p.packshot_asset_ids = [c.assets.ingest(f, source="upload:packshot").id for f in packshot]
    p.footage_asset_ids = [c.assets.ingest(f, source="upload:footage").id for f in footage]
    for u in capture_url:
        p.screenshot_asset_ids.append(cap(u).id)
    c.db.put(p)
    con.print(f"producto creado: [bold]{p.id}[/] ({len(p.screenshot_asset_ids)} capturas, {len(p.packshot_asset_ids)} packshots)")


@product_app.command("list")
def product_list(brand: Optional[str] = typer.Option(None, help="filtra por id de marca")) -> None:
    from .models import Product
    from .store import ctx

    for p in ctx().db.list(Product):
        if brand and p.brand_id != brand:
            continue
        con.print(f"{p.id}  {p.name}  ({p.kind})  marca={p.brand_id}  capturas={len(p.screenshot_asset_ids)}  "
                  f"packshots={len(p.packshot_asset_ids)}")


# ───────────────────────────── actores ─────────────────────────────


@actor_app.command("create")
def actor_create(handle: str = typer.Option(...), appearance: str = typer.Option(...), wardrobe: str = "", persona: str = "",
                 locale: str = "es-ES", voice: Optional[str] = None, voice_hint: str = "", gender: str = "female",
                 location: str = "") -> None:
    from .pipeline.actors import create_actor

    a = create_actor(handle, appearance, persona=persona, wardrobe=wardrobe, locale=locale, voice_id=voice, voice_hint=voice_hint,
                     gender=gender, location_hint=location)
    con.print(f"actor creado: [bold]{a.handle}[/] ({a.id}) · vistas={len(a.sheet_asset_ids)} · "
              f"umbral identidad={a.identity.threshold} · coherencia hoja={a.identity.self_similarity}")


@actor_app.command("list")
def actor_list() -> None:
    from .models import Actor
    from .store import ctx

    for a in ctx().db.list(Actor):
        con.print(f"{a.id}  {a.handle}  vistas={len(a.sheet_asset_ids)}  voces={list(a.voices)}  {a.appearance[:60]}")


# ───────────────────────────── proyectos ─────────────────────────────


@project_app.command("new")
def project_new(brand: str = typer.Option(...), product: str = typer.Option(...), actor: Optional[str] = None,
                objective: str = "conversión", audience: str = "", message: list[str] = typer.Option([]),
                locale: str = "es-ES", duration: float = 25.0, platform: str = "reels", mode: str = "native",
                style: str = "", budget: Optional[float] = None, angles: int = 6, name: str = "") -> None:
    from .models import Actor, Brief
    from .orchestrator import create_project
    from .store import ctx

    actor_ids = [ctx().db.find(Actor, actor).id] if actor else []
    b = Brief(brand_id=brand, product_id=product, objective=objective, audience=audience, key_messages=message, locale=locale,
              duration_s=duration, platform=platform, actor_ids=actor_ids, style_notes=style, budget_usd=budget, n_angles=angles)  # type: ignore[arg-type]
    p = create_project(b, name=name, talk_mode=mode)
    con.print(f"proyecto creado: [bold]{p.id}[/]")


@app.command()
def run(project_id: str, vlm: bool = True, music: bool = True, rounds: int = 2) -> None:
    """Ejecuta el proyecto de principio a fin (reanudable)."""
    from .orchestrator import run as orun

    res = orun(project_id, _progress, use_vlm=vlm, music=music, max_rounds=rounds)
    con.print_json(json.dumps(res, ensure_ascii=False))


@app.command()
def regen(project_id: str, scene: str, action: str = "reroll_seed") -> None:
    """Regenera SOLO una escena (id, número «3» o «S3») y vuelve a montar; el resto sale de caché."""
    from .orchestrator import regen_scene

    res = regen_scene(project_id, scene, action, _progress)
    con.print_json(json.dumps(res, ensure_ascii=False))


@app.command()
def edit(project_id: str, instruction: str, yes: bool = typer.Option(False, "--yes", help="confirma órdenes de pago")) -> None:
    """Orden en lenguaje natural: «regenera la escena 3», «cambia el hook», «hazlo en alemán», «CTA: Descárgala ya»."""
    from .commands import apply

    res = apply(project_id, instruction, _progress, confirm=yes)
    con.print_json(json.dumps(res, ensure_ascii=False, default=str))


@app.command()
def variant(project_id: str, kind: str, value: str = typer.Argument(None), vlm: bool = False) -> None:
    """Crea una variante: hook_text | cta | captions | aspect | music | spoken_cta | language."""
    from .variants import make_variant

    res = make_variant(project_id, kind, value, use_vlm=vlm)
    con.print_json(json.dumps(res, ensure_ascii=False))


@app.command("plan-import")
def plan_import(path: str, brand: str, product: str, actor: str = typer.Option(..., help="handle del actor, p. ej. @presentadora_01"),
                duration: float = 22.0, locale: str = "es-ES") -> None:
    """Importa planes del estudio creativo multiagente (guion + storyboard) como proyectos listos para `motor run`."""
    from pathlib import Path as _P

    from .plans import import_file, validate

    for p in import_file(_P(path), brand, product, actor, duration_s=duration, locale=locale):
        con.print(f"{p.id} · {p.name} · {len(p.shots)} planos · coste estimado {p.variant_spec.get('estimated_cost_usd')} $ · "
                  f"avisos: {validate(p.variant_spec['plan'], locale) or 'ninguno'}")


@app.command()
def gc(segments: bool = typer.Option(False, help="borra también la caché de segmentos de render"),
       dry_run: bool = typer.Option(False, "--dry-run")) -> None:
    """Libera disco: temporales de trabajo (QA, renders intermedios, capturas de depuración). Nunca toca assets ni exports."""
    import shutil as _sh

    from .store import ctx

    work = ctx().settings.work_dir
    freed = 0
    for d in sorted(work.iterdir()) if work.exists() else []:
        if d.name == "segments" and not segments:
            continue
        size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
        freed += size
        con.print(f"{'(simulado) ' if dry_run else ''}borrando {d.name}: {size / 1e6:.1f} MB")
        if not dry_run:
            _sh.rmtree(d, ignore_errors=True)
    con.print(f"liberado: {freed / 1e6:.1f} MB · libre ahora: {_sh.disk_usage(ctx().settings.data_dir).free / 1e9:.1f} GB")


@app.command()
def costs(project_id: Optional[str] = typer.Argument(None)) -> None:
    from .costs import summarize

    con.print_json(json.dumps(summarize(project_id), ensure_ascii=False))


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    """Interfaz interna."""
    import uvicorn

    uvicorn.run("motor.api.server:app", host=host, port=port, log_level="info")


@app.command()
def demo(duration: float = 24.0, vlm: bool = True) -> None:
    """Prueba de referencia: marca + app real + actor persistente + anuncio multiescena + variantes."""
    from .demo import run_demo

    res = run_demo(duration=duration, use_vlm=vlm, progress=_progress)
    con.print_json(json.dumps(res, ensure_ascii=False))


def main() -> None:  # pragma: no cover
    app()


if __name__ == "__main__":  # pragma: no cover
    sys.exit(app())
