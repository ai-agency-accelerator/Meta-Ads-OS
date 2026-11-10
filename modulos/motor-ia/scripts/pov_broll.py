"""Planos POV de ambiente para anuncios de apps y SaaS «sin cara». Sin personas identificables y sin texto.

Por qué existe: el flujo clásico del motor gira alrededor de una presentadora. Un anuncio POV solo necesita planos de
ambiente en primera persona (alguien que llega a la oficina, abre el portátil, sale a la calle) que luego se montan con
la grabación REAL de la app. Regla: la IA pone el ambiente, nunca gente que pase por usuarios o clientes reales, y el
montaje lleva la etiqueta de IA. Los planos se definen en un JSON (ejemplo: `examples/pov_planos_ejemplo.json`).

Uso (desde la raíz de Meta Ads OS; el subcomando va SIEMPRE justo después del nombre del script):

  uv run --project modulos/motor-ia python modulos/motor-ia/scripts/pov_broll.py <subcomando> --planos <planos.json> …

  list                              → planos definidos, estado y coste estimado (gratis)
  keyframe <plano> [--n 2]          → candidatos de primer fotograma (de pago, ≈0,07 $ cada uno con precios de 2026-10)
  gen <plano> <asset> [--toma 0]    → vídeo de N s desde el fotograma elegido (de pago, ≈0,10 $/s)

Con `MOTOR_MOCK=1` o `--simular` se usan proveedores simulados (0 $). El estado vive en
`data/work/pov/<nombre>/state.json`.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

IMAGE_MODEL = "gemini-3.1-flash-image"
OMNI_MODEL = "gemini-omni-1.1-flash"
DEFAULT_STYLE = ("Realistic smartphone photo, natural colors, true-to-life exposure, not cinematic, not a render. "
                 "No text, no legible signs, no logos, no watermark.")


class PlanosError(ValueError):
    pass


def load_planos(path: str | Path) -> dict[str, Any]:
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        raise PlanosError(f"no encuentro {p}")
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise PlanosError(f"JSON no válido (línea {e.lineno}): {e.msg}") from None
    errs = validate_planos(d)
    if errs:
        raise PlanosError("planos no válidos:\n  - " + "\n  - ".join(errs))
    return d


def validate_planos(d: Any) -> list[str]:
    if not isinstance(d, dict):
        return ["el archivo debe ser un objeto JSON"]
    errs = []
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{1,60}", str(d.get("nombre", ""))):
        errs.append("«nombre» en minúsculas con guiones (se usa como carpeta de estado)")
    planos = d.get("planos")
    if not isinstance(planos, dict) or not planos:
        return errs + ["«planos» debe ser un objeto {nombre: {segundos, fotograma_en, movimiento_en}}"]
    for name, sh in planos.items():
        if not isinstance(sh, dict):
            errs.append(f"plano «{name}»: debe ser un objeto")
            continue
        for k in ("fotograma_en", "movimiento_en"):
            if not str(sh.get(k, "")).strip():
                errs.append(f"plano «{name}»: falta «{k}»")
        if not isinstance(sh.get("segundos", 5), (int, float)) or not 3 <= sh.get("segundos", 5) <= 10:
            errs.append(f"plano «{name}»: «segundos» entre 3 y 10")
        text = f"{sh.get('fotograma_en', '')} {sh.get('movimiento_en', '')}".lower()
        if re.search(r"(?<!first-)\b(face|faces|woman|women|man|men|people|person|crowd)\b", text) and "no people" not in text:
            errs.append(f"plano «{name}»: menciona personas; un POV de ambiente no debe mostrar a nadie identificable "
                        "(añade «no people» si es intencionado que no aparezca nadie)")
    return errs


def _simulated() -> bool:
    from motor.store import ctx

    return ctx().settings.mock


def _state_path(d: dict[str, Any]) -> Path:
    from motor.store import ctx

    p = ctx().settings.work_dir / "pov" / d["nombre"]
    p.mkdir(parents=True, exist_ok=True)
    return p / "state.json"


def _state(d: dict[str, Any]) -> dict[str, Any]:
    p = _state_path(d)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _save(d: dict[str, Any], s: dict[str, Any]) -> None:
    _state_path(d).write_text(json.dumps(s, indent=1, ensure_ascii=False), encoding="utf-8")


def _shot(d: dict[str, Any], name: str) -> dict[str, Any]:
    if name not in d["planos"]:
        raise PlanosError(f"no hay plano «{name}» (hay: {', '.join(d['planos'])})")
    return d["planos"][name]


def list_shots(d: dict[str, Any]) -> dict[str, Any]:
    from motor.costs import price

    s = _state(d)
    img, omni = price("gemini", IMAGE_MODEL, "1k", 0.067), price("gemini", OMNI_MODEL, "720p", 0.101)
    return {name: {"segundos": sh.get("segundos", 5), "fotogramas": s.get(name, {}).get("keyframes", []),
                   "videos": s.get(name, {}).get("videos", []),
                   "coste_estimado_usd": round(2 * img + omni * sh.get("segundos", 5), 3)}
            for name, sh in d["planos"].items()}


def keyframe(d: dict[str, Any], name: str, n: int = 2) -> list[str]:
    from motor.costs import scope
    from motor.providers.base import ImageRequest

    sh = _shot(d, name)
    prompt = f"{sh['fotograma_en'].strip()} {d.get('estilo_en', DEFAULT_STYLE)}"
    if _simulated():
        from motor.providers.mock import MockImage

        prov: Any = MockImage()
    else:
        from motor.providers.gemini import GeminiImage

        prov = GeminiImage(IMAGE_MODEL)
    with scope(None, f"pov:{d['nombre']}:{name}:kf"):
        cands = prov.generate(ImageRequest(prompt=prompt, aspect="9:16", n=n))
    s = _state(d)
    s.setdefault(name, {}).setdefault("keyframes", []).extend(a.id for a in cands)
    _save(d, s)
    return [a.id for a in cands]


def gen(d: dict[str, Any], name: str, kf_id: str, take: int = 0) -> str:
    from motor.costs import scope
    from motor.providers.base import VideoRequest
    from motor.store import ctx

    sh = _shot(d, name)
    kf = ctx().db.get_asset(kf_id)
    req = VideoRequest(prompt=sh["movimiento_en"], first_frame=kf, duration=sh.get("segundos", 5), aspect="9:16",
                       audio=True, seed=take)
    if _simulated():
        from motor.providers.mock import MockVideo

        prov: Any = MockVideo()
    else:
        from motor.providers.gemini import GeminiOmni

        prov = GeminiOmni(OMNI_MODEL)
    with scope(None, f"pov:{d['nombre']}:{name}:v{take}"):
        a = prov.generate(req)
    s = _state(d)
    s.setdefault(name, {}).setdefault("videos", []).append(a.id)
    _save(d, s)
    return a.id


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="pov_broll.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name: str, help_: str) -> argparse.ArgumentParser:
        sp = sub.add_parser(name, help=help_)
        sp.add_argument("--planos", required=True, help="JSON con los planos")
        sp.add_argument("--simular", action="store_true", help="proveedores simulados (equivale a MOTOR_MOCK=1; 0 $)")
        return sp

    add("list", "planos, estado y coste estimado (gratis)")
    sp = add("keyframe", "candidatos de primer fotograma (de pago)")
    sp.add_argument("plano")
    sp.add_argument("--n", type=int, default=2)
    sp = add("gen", "vídeo desde el fotograma elegido (de pago)")
    sp.add_argument("plano")
    sp.add_argument("asset")
    sp.add_argument("--toma", type=int, default=0)
    a = ap.parse_args(argv)
    if a.simular:
        os.environ["MOTOR_MOCK"] = "1"
        from motor import config, store
        from motor.providers import registry

        config.reset_settings()
        store.set_ctx(None)
        registry.reset()
    try:
        d = load_planos(a.planos)
        if a.cmd == "list":
            res: Any = list_shots(d)
        elif a.cmd == "keyframe":
            res = {"fotogramas": keyframe(d, a.plano, a.n)}
        else:
            res = {"video": gen(d, a.plano, a.asset, a.toma)}
        if a.cmd != "list":
            from motor.store import ctx

            res["simulado"] = ctx().settings.mock
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0
    except PlanosError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
