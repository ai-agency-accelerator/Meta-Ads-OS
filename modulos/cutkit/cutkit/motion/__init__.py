"""cutkit.motion — runtime HTML/GSAP + librería de componentes para HyperFrames.

- `build_project(render_spec, out_dir)` (html.py): proyecto HF listo para `lint`/`check`/`render`.
- `COMPONENTS`, `validate_props`, `sfx_events` (registry.py): catálogo con props (JSON Schema), duraciones, SFX y criterio.
- `python -m cutkit.motion.preview <componente> --props p.json --at 0.2,0.5,1.0 --out dir` (preview.py).
"""
from cutkit.motion.html import build_project
from cutkit.motion.registry import COMPONENTS, get, sfx_events, validate_props

__all__ = ["build_project", "COMPONENTS", "get", "sfx_events", "validate_props"]
