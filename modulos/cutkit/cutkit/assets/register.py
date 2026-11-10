"""`register_file(...)`: registra en la biblioteca y en `assets.json` un medio que YA está producido.

Para lo que no sale de una `AssetRequest` resoluble de una vez: recortes de un vídeo oficial descargado a mano,
pantallas del producto grabadas con datos de demo del cliente, B-roll generado con el motor de IA, montajes de varias
capturas… El archivo se ingiere por sha256 en `datos/biblioteca/` (blob inmutable), se clona a su ruta final dentro de
`<proyecto>/edicion/media/` (si no está ya ahí) y se añade o actualiza su `Asset` en `<proyecto>/edicion/assets.json`
sin tocar el resto del manifiesto.

    from cutkit.assets.register import register_file
    register_file("demo-crm", "panel_scroll",
                  "clientes/acme-automations/creativos/2026-11-09_demo-crm/edicion/media/video/panel_scroll.mp4",
                  origin="usuario", source_url="https://acme-automations.example/panel",
                  license="propio (grabación del cliente)", notes="panel con datos de demo",
                  provenance={"src_in": 65.0, "src_out": 67.6})

`path` relativa se busca desde la carpeta actual, la del proyecto y la raíz del producto; `dest` relativa es
relativa a la raíz del producto.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, get_args

from cutkit.spec import Asset

from . import library
from .probe import media_type_of, probe
from .resolver import edit_dir


def register_file(slug: str, asset_id: str, path: Path | str, *, origin: str, source_url: str | None = None,
                  license: str = "", notes: str = "", provenance: dict[str, Any] | None = None,
                  dest: Path | str | None = None, run_dir: Path | str | None = None, cost_usd: float = 0.0,
                  request_kind: str = "file") -> Asset:
    """Ingiere `path` en la biblioteca, lo deja en `dest` (por defecto, donde está) y lo anota en assets.json.

    `provenance` (dict) se guarda en la biblioteca (meta) y como clave de búsqueda: el mismo recorte del mismo
    origen se encuentra después con `library.lookup(request_kind, source_url or path, provenance)`.
    """
    validos = get_args(Asset.model_fields["origin"].annotation)
    if origin not in validos:
        raise ValueError(f"origin no válido: {origin!r} (usa uno de: {', '.join(validos)})")
    out_dir = edit_dir(slug, run_dir)
    proyecto = out_dir.parent if out_dir.name in ("edicion", "edit") else out_dir
    src = library.user_path(path, proyecto)
    if not src.is_file():
        raise FileNotFoundError(f"no existe el archivo {path}")
    dst = library.abs_path(Path(dest).expanduser()) if dest else src
    library.init()
    pi = probe(src)
    prov = dict(provenance or {})
    rec = library.ingest(src, kind=request_kind, query=source_url or library.rel_or_abs(src), params=prov,
                         media_type=media_type_of(src), origin=origin, source_url=source_url, license=license,
                         cost_usd=cost_usd, notes=notes, meta={"provenance": prov, "asset_id": asset_id},
                         probe_info=pi, move=False)
    if dst.resolve() != src.resolve():
        library.clone_file(library.abs_path(rec["path"]), dst)
    library.mark_used(rec["sha256"], f"{slug}/{asset_id}")
    pi = probe(dst)
    asset = Asset(id=asset_id, kind=media_type_of(dst), path=library.rel_or_abs(dst), sha256=rec["sha256"],
                  origin=origin, source_url=source_url, license=license, width=pi.get("width"),
                  height=pi.get("height"), duration=pi.get("duration"), notes=notes)
    manifest_path = out_dir / "assets.json"
    data: dict[str, Any] = {"slug": slug, "assets": {}, "requests": []}
    if manifest_path.exists():
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if data.get("slug") not in (None, slug):
        raise ValueError(f"{manifest_path} es de otro vídeo ({data.get('slug')})")
    data.setdefault("assets", {})[asset_id] = json.loads(asset.model_dump_json())
    data["spent_usd"] = round(float(data.get("spent_usd", 0.0)) + float(cost_usd), 4)
    if cost_usd:
        data.setdefault("costs", {})[asset_id] = round(float(cost_usd), 4)
    tmp = manifest_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(manifest_path)
    return asset


__all__ = ["register_file"]
