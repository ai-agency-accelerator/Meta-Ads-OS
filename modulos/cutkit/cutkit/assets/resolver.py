"""`resolve(slug, requests, run_dir, budget_usd) -> AssetManifest`: de peticiones a archivos congelados.

Por cada `AssetRequest` (ya decidida por el director):

    biblioteca (misma kind+query+params, no caducada) → si no: obtener según `kind`
        file        copia de un archivo local tuyo (origen «usuario»); rutas relativas a la carpeta actual,
                    al proyecto (`brutos/…`) o a la raíz del producto
        logo        del cliente (marca.json) o de terceros aportados en marca/logos/ (nunca se descarga)
        web_capture Playwright (móvil / escritorio / página completa / elemento; oscuro opcional)
        web_scroll  Playwright fotograma a fotograma → ffmpeg 30 fps
        stock       Pexels / Pixabay solo con tu clave (se registra la licencia de cada archivo)
        gen_image   no disponible en cutkit: el B-roll con IA lo genera el motor (`generate.py`)
        gen_video   ídem
        music       delega en cutkit.audio.music.ensure
    → ingest en datos/biblioteca/<sha[:2]>/<sha>.<ext> (+ library.db)
    → clon en <run_dir>/media/<asset_id>.<ext> + ffprobe
    → <run_dir>/assets.json (AssetManifest con el gasto)

`run_dir` es la carpeta de edición del vídeo: `<proyecto>/edicion` (con `CUTKIT_RUNS=<dir>`, `<dir>/<slug>/edit`).
Si se pasa la carpeta del proyecto, se usa su `edicion/`. Nunca inventa: si algo no se puede obtener, la petición
queda en `manifest.failed` con el motivo y el director elige otra cosa.

Gasto: cutkit no llama a modelos de pago (el B-roll con IA lo hace el motor con su guardián). `budget_usd` se anota en
el manifiesto y `spent_usd` suma lo que declaren las piezas (p. ej. la música, si su módulo generó una pista).
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, get_args

from pydantic import Field

from cutkit.paths import CLIENTES, cliente_de
from cutkit.paths import run_dir as _run_dir
from cutkit.spec import Asset, AssetManifest, AssetRequest

from . import library
from .probe import media_type_of, probe

# Orden de proceso (lo local primero, la red después).
KIND_ORDER = {"file": 0, "logo": 1, "web_capture": 2, "web_scroll": 3, "stock": 4, "music": 5,
              "gen_image": 6, "gen_video": 7}
# Caducidad por defecto de lo reutilizado (días). None = no caduca (determinista o inmutable).
DEFAULT_MAX_AGE = {"web_capture": 7, "web_scroll": 7, "stock": None, "gen_image": None, "gen_video": None,
                   "file": None, "music": None}
ORIGIN = {"file": "usuario", "logo": "logo", "web_capture": "web_capture", "web_scroll": "web_scroll",
          "stock": "stock", "gen_image": "gen_image", "gen_video": "gen_video", "music": "music_gen"}
# Se obtienen siempre desde su fuente local (barato, y así se nota si cambias el archivo original).
ALWAYS_FRESH = {"logo"}
# Con dry_run solo se sirve lo local; lo que iría a la red queda pendiente.
NETWORK_KINDS = {"web_capture", "web_scroll", "stock", "music"}


class ResolvedManifest(AssetManifest):
    """AssetManifest + lo que el director necesita para decidir (se ignora al cargar como AssetManifest)."""

    failed: dict[str, str] = Field(default_factory=dict)     # request.id → motivo
    costs: dict[str, float] = Field(default_factory=dict)    # request.id → USD gastados en ESTA resolución
    reused: list[str] = Field(default_factory=list)          # request.id servidos desde la biblioteca
    resolved_at: str = ""


class _Fail(RuntimeError):
    pass


def edit_dir(slug: str, run_dir: Path | str | None) -> Path:
    """Carpeta de edición: la de `paths.run_dir(slug)` por defecto; acepta también la del proyecto o `<dir>/<slug>`."""
    if run_dir is None:
        return _run_dir(slug)
    d = Path(run_dir)
    if d.name.endswith(f"_{slug}") and (d / "edicion").is_dir():
        return d / "edicion"
    if d.name == slug and (d / "edit").is_dir():
        return d / "edit"
    return d


def _cliente(slug: str, out_dir: Path) -> str | None:
    """Cliente dueño de la carpeta de edición (`clientes/<c>/creativos/<proyecto>/edicion`) o del slug."""
    try:
        rel = out_dir.resolve().relative_to(CLIENTES.resolve())
        if len(rel.parts) >= 2 and rel.parts[1] == "creativos":
            return rel.parts[0]
    except ValueError:
        pass
    try:
        return cliente_de(slug)
    except ValueError:                  # slug con formato no válido para buscar proyectos
        return None


def _max_age(req: AssetRequest) -> float | None:
    if "max_age_days" in req.params:
        return float(req.params["max_age_days"]) if req.params["max_age_days"] is not None else None
    return DEFAULT_MAX_AGE.get(req.kind)


# ───────────────────────────── obtención por tipo ─────────────────────────────

def _obtain(req: AssetRequest, slug: str, out_dir: Path, cliente: str | None) -> dict[str, Any]:
    """Obtiene el archivo (en un temporal de la biblioteca o su ruta local) y devuelve los datos para ingerirlo."""
    q, p = req.query, dict(req.params)
    if req.kind == "file":
        proyecto = out_dir.parent if out_dir.name in ("edicion", "edit") else out_dir
        src = library.user_path(q, proyecto)
        if not src.is_file():
            raise _Fail(f"no existe el archivo {q} (busco desde la carpeta actual, {library.rel_or_abs(proyecto)}/ "
                        "y la raíz del producto)")
        return {"path": src, "move": False, "source_url": p.get("source_url"), "license": p.get("license", "propio"),
                "notes": p.get("notes") or f"archivo local {library.rel_or_abs(src)}", "meta": {"src": str(src)}}

    if req.kind == "logo":
        from .logo import LogoFailure, resolve_logo

        try:
            r = resolve_logo(q, p, cliente=cliente)
        except LogoFailure as exc:
            raise _Fail(str(exc)) from exc
        notes = [f"logo de {r['entity']} ({r['source']}: {r['original']})", *r["notes"]]
        return {"path": r["path"], "move": r["move"], "source_url": r["source_url"], "license": r["license"],
                "notes": "; ".join(dict.fromkeys(notes)),
                "meta": {k: v for k, v in r.items() if k not in ("path", "move")}}

    if req.kind in ("web_capture", "web_scroll"):
        from .web import PlaywrightNoDisponible

        what = "captura" if req.kind == "web_capture" else "scroll"
        tmp = library.new_tmp("png" if req.kind == "web_capture" else "mp4")
        try:
            if req.kind == "web_capture":
                from .web import capture

                info = capture(q, tmp, p)
            else:
                from .web import record_scroll, record_tour

                # con `stops`: recorrido determinista por paradas (animaciones de la web a velocidad real)
                info = (record_tour if p.get("stops") else record_scroll)(q, tmp, p)
        except PlaywrightNoDisponible as exc:
            tmp.unlink(missing_ok=True)
            raise _Fail(f"{what} de {q} no disponible: {exc}") from exc
        except Exception as exc:  # noqa: BLE001
            tmp.unlink(missing_ok=True)
            raise _Fail(f"{what} fallida de {q}: {type(exc).__name__}: {str(exc)[:300]}") from exc
        if req.kind == "web_capture":
            vp = info["viewport"]
            notes = f"captura {vp['width']}x{vp['height']}@{vp['scale']}x{' oscuro' if p.get('dark') else ''}"
        else:
            notes = f"scroll {p.get('seconds', 6)} s a {p.get('fps', 30)} fps, {info.get('distance_px')} px CSS"
        notes += f"; «{info.get('title', '')[:60]}»"
        if info.get("consent_clicked"):
            notes += f"; cookies: pulsado «{info['consent_clicked']}»"
        # Captura de una web. Si es del cliente (su producto, su landing), es material propio. Si es de un tercero, el
        # derecho de cita (art. 32 de la Ley de Propiedad Intelectual) cubre fines docentes o de investigación, no la
        # publicidad: hace falta permiso del titular. La licencia lo dice para que lo revise quien entrega el anuncio.
        return {"path": tmp, "move": True, "source_url": info.get("final_url") or q,
                "license": "captura web: solo si la web es del cliente o hay permiso del titular (el derecho de cita "
                           "no cubre publicidad)", "notes": notes, "meta": info}

    if req.kind == "stock":
        from .stock import StockFailure, fetch

        base = library.new_tmp("bin").with_suffix("")
        try:
            r = fetch(q, p, base)
        except StockFailure as exc:
            raise _Fail(str(exc)) from exc
        author = f" · autor {r['author']}" if r.get("author") else ""
        return {"path": r["path"], "move": True, "source_url": r["source_url"], "license": r["license"],
                "notes": f"{r['provider']}{author} · {r['license_detail']}", "meta": r | {"path": str(r["path"])}}

    if req.kind in ("gen_image", "gen_video"):
        from .generate import GenFailure, generate

        try:
            generate(req.kind, q, p)
        except GenFailure as exc:
            raise _Fail(str(exc)) from exc
        raise _Fail(f"{req.kind}: no disponible en cutkit")

    if req.kind == "music":
        try:
            from cutkit.audio import music  # módulo de audio: aquí solo se delega
        except Exception as exc:  # noqa: BLE001
            raise _Fail(f"music: cutkit.audio.music no disponible ({exc})") from exc
        tmpdir = library.new_tmp("d")
        tmpdir.mkdir(parents=True, exist_ok=True)
        try:
            a = music.ensure(q, float(p.get("duration", p.get("seconds", 60))), tmpdir)
        except Exception as exc:  # noqa: BLE001
            raise _Fail(f"music: {type(exc).__name__}: {str(exc)[:300]}") from exc
        src = library.abs_path(a.path)
        cost = float(a.get("cost_usd") or 0.0) if isinstance(a, dict) else 0.0
        return {"path": src, "move": False, "source_url": a.source_url, "license": a.license or "generated-google",
                "notes": a.notes, "meta": {"music_asset": a.model_dump()}, "origin": a.origin, "cost": cost}

    raise _Fail(f"kind no soportado: {req.kind}")


# ───────────────────────────── una petición ─────────────────────────────

def _resolve_one(req: AssetRequest, slug: str, out_dir: Path, cliente: str | None,
                 dry_run: bool) -> tuple[Asset | None, float, bool, str | None]:
    """(asset, coste, reutilizado, error)."""
    refresh = bool(req.params.get("refresh"))
    rec = None
    reused = False
    cost = 0.0
    if req.kind not in ALWAYS_FRESH and not refresh:
        rec = library.lookup(req.kind, req.query, req.params, max_age_days=_max_age(req))
        reused = rec is not None
    if rec is None:
        if dry_run and req.kind in NETWORK_KINDS:
            return None, 0.0, False, f"dry-run: no está en la biblioteca; se obtendría con {req.kind} ({req.query[:80]})"
        try:
            got = _obtain(req, slug, out_dir, cliente)
        except _Fail as exc:
            return None, 0.0, False, str(exc)
        except Exception as exc:  # noqa: BLE001 - cualquier fallo inesperado no tumba el resto
            return None, 0.0, False, f"{type(exc).__name__}: {str(exc)[:300]}"
        cost = float(got.get("cost", 0.0))
        src = Path(got["path"])
        pi = probe(src)
        rec = library.ingest(src, kind=req.kind, query=req.query, params=req.params,
                             media_type=media_type_of(src), origin=got.get("origin") or ORIGIN[req.kind],
                             source_url=got.get("source_url"), license=got.get("license", ""), cost_usd=cost,
                             notes=got.get("notes", ""), meta=got.get("meta"), probe_info=pi,
                             move=bool(got.get("move")))
    blob = library.abs_path(rec["path"])
    # `params.subdir` (opcional): subcarpeta de media/ (p. ej. «video»); no cambia la clave de la biblioteca
    dst = out_dir / "media" / str(req.params.get("subdir") or "") / f"{req.id}.{rec['ext']}"
    library.clone_file(blob, dst)
    library.mark_used(rec["sha256"], f"{slug}/{req.id}")
    pi = probe(dst)
    notes = rec.get("notes") or ""
    if reused:
        notes = f"reutilizado de la biblioteca ({rec['created'][:10]}); {notes}"
    origin = rec["origin"] if rec["origin"] in get_args(Asset.model_fields["origin"].annotation) else "library"
    asset = Asset(id=req.id, kind=media_type_of(dst), path=library.rel_or_abs(dst), sha256=rec["sha256"],
                  origin=origin, source_url=rec.get("source_url"), license=rec.get("license") or "",
                  width=pi.get("width"), height=pi.get("height"), duration=pi.get("duration"), notes=notes)
    return asset, cost, reused, None


# ───────────────────────────── API pública ─────────────────────────────

def resolve(slug: str, requests: list[AssetRequest] | list[dict], run_dir: Path | str | None = None,
            budget_usd: float = 2.0, *, dry_run: bool = False, workers: int = 4,
            cliente: str | None = None) -> ResolvedManifest:
    """Resuelve las peticiones, congela los archivos en `<run_dir>/media/` y escribe `<run_dir>/assets.json`.

    - Si ya hay un `assets.json`, se conserva lo anterior (y su gasto).
    - Paralelo (`workers`): capturas, scrolls y descargas se solapan.
    - `dry_run=True`: no sale a la red; sirve lo local (archivos, logos) y lo que ya esté en la biblioteca, y deja
      el resto como pendiente en `failed`.
    - `cliente`: de quién son los logos; por defecto, el dueño del proyecto.
    """
    reqs = [r if isinstance(r, AssetRequest) else AssetRequest.model_validate(r) for r in requests]
    ids = [r.id for r in reqs]
    if len(set(ids)) != len(ids):
        raise ValueError("Hay ids de AssetRequest repetidos")
    out_dir = edit_dir(slug, run_dir)
    media_dir = out_dir / "media"
    media_dir.mkdir(parents=True, exist_ok=True)
    cliente = cliente or _cliente(slug, out_dir)
    manifest_path = out_dir / "assets.json"
    prev: dict[str, Any] = {}
    if manifest_path.exists():
        try:
            prev = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            prev = {}
    if prev.get("slug") not in (None, slug):
        prev = {}
    prev_spent = float(prev.get("spent_usd", 0.0))
    library.init()
    library.clean_tmp()

    # Si un id cambia de extensión (p. ej. svg → png), no dejar el archivo viejo.
    for r in reqs:
        for old in (media_dir / str(r.params.get("subdir") or "")).glob(f"{r.id}.*"):
            if old.is_file():
                old.chmod(0o644)
                old.unlink()

    ordered = sorted(reqs, key=lambda r: KIND_ORDER.get(r.kind, 9))
    results: dict[str, tuple] = {}
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futs = {r.id: pool.submit(_resolve_one, r, slug, out_dir, cliente, dry_run) for r in ordered}
        for rid, f in futs.items():
            results[rid] = f.result()

    assets = {k: Asset.model_validate(v) for k, v in (prev.get("assets") or {}).items()}
    failed = {k: v for k, v in (prev.get("failed") or {}).items() if k not in ids}
    old_reqs = {r["id"]: r for r in prev.get("requests") or [] if r.get("id") not in ids}
    costs: dict[str, float] = {}
    reused: list[str] = []
    for r in reqs:
        asset, cost, was_reused, err = results[r.id]
        if asset is not None:
            assets[r.id] = asset
            failed.pop(r.id, None)
        else:
            assets.pop(r.id, None)
            failed[r.id] = err or "fallo desconocido"
        if cost:
            costs[r.id] = round(cost, 4)
        if was_reused:
            reused.append(r.id)
    manifest = ResolvedManifest(
        slug=slug, assets=assets,
        requests=[AssetRequest.model_validate(x) for x in old_reqs.values()] + reqs,
        budget_usd=budget_usd, spent_usd=round(prev_spent + sum(costs.values()), 4),
        failed=failed, costs=costs, reused=reused, resolved_at=library.now_iso())
    tmp = manifest_path.with_suffix(".json.tmp")
    tmp.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    tmp.replace(manifest_path)
    return manifest


def load_manifest(slug: str, run_dir: Path | str | None = None) -> ResolvedManifest | None:
    p = edit_dir(slug, run_dir) / "assets.json"
    if not p.exists():
        return None
    return ResolvedManifest.model_validate_json(p.read_text(encoding="utf-8"))


__all__ = ["resolve", "load_manifest", "ResolvedManifest", "edit_dir"]
