"""cutkit.assets — de `AssetRequest` a archivos congelados, con biblioteca persistente y licencia de cada pieza.

API:
    resolve(slug, requests, run_dir=None, budget_usd=2.0, *, dry_run=False, cliente=None) -> ResolvedManifest
        (subclase de AssetManifest con `failed`, `costs` y `reused`; escribe <proyecto>/edicion/assets.json)
    probe(path) -> {width, height, duration, fps, codec, has_audio, format, bytes}
    load_manifest(slug, run_dir=None) -> ResolvedManifest | None

CLI interno:  python -m cutkit.assets resolve <slug> --requests requests.json [--run-dir D] [--cliente C]
              python -m cutkit.assets probe <archivo>  ·  python -m cutkit.assets search [texto] [--kind K]

Módulos: `library` (CAS + SQLite en datos/biblioteca/), `web` (capturas y scroll con Playwright, extra `avanzado`),
`logo` (del cliente y de terceros aportados en su marca/logos/; nunca descarga), `stock` (Pexels/Pixabay con tu
clave) y `generate` (sin generación: el B-roll con IA lo hace el motor `modulos/motor-ia`, con su control de gasto).
"""

from __future__ import annotations

from .probe import media_type_of, probe
from .resolver import ResolvedManifest, edit_dir, load_manifest, resolve

__all__ = ["resolve", "probe", "media_type_of", "load_manifest", "edit_dir", "ResolvedManifest"]
