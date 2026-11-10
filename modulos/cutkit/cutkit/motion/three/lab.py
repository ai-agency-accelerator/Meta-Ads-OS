"""cutkit.motion.three.lab — banco de pruebas de componentes (3D o 2D) sobre un TRAMO REAL de un render_spec (sin tocar el plan).

Recorta la ventana [desde, hasta] del render_spec de una versión (A-roll con su desfase, layouts, transiciones,
subtítulos…), cambia el componente de UN item (p. ej. logo.reveal → scene.logo_reveal3d) y construye el proyecto HF
con `build_project`. Opcionalmente lo renderiza con HyperFrames y multiplexa el audio de la mezcla de la versión.

    uv run python -m cutkit.motion.three.lab <slug> v003 --item it_d012 --component scene.logo_reveal3d \
        --from 9.3 --to 11.4 --out /tmp/lab3d [--props '{"material":"metal"}'] [--render] [--frames 0.4,0.9,1.25]

Salida: <out>/hf/ (proyecto), <out>/<componente>.mp4 (sin audio) y <out>/<componente>_audio.mp4 si hay mezcla,
<out>/frames/f_<t>.png (fotogramas extraídos del MP4).
"""
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import time
from pathlib import Path

from cutkit.motion.html import build_project
from cutkit.paths import HF_VERSION, version_dir


def _shift(o, dt: float):
    if isinstance(o, dict):
        return {k: (v - dt if k in ("t0", "t1") and isinstance(v, (int, float)) else _shift(v, dt)) for k, v in o.items()}
    if isinstance(o, list):
        return [_shift(v, dt) for v in o]
    return o


def window_spec(spec: dict, a: float, b: float, item_id: str | None = None, component: str | None = None,
                extra_props: dict | None = None, overrides: dict | None = None) -> dict:
    """render_spec recortado a [a, b] y desplazado a t=0; `item_id` pasa a `component` (+ props extra).
    overrides = {item_id: {"component": …, "props": {…} (se fusionan), "props_replace": {…} (sustituyen)}}."""
    s = copy.deepcopy(spec)
    items = []
    for it in spec.get("items") or []:
        if it["t1"] <= a or it["t0"] >= b:
            continue
        it = copy.deepcopy(it)
        t0, t1 = max(a, it["t0"]), min(b, it["t1"])
        if it["t0"] < a:                                   # recortado por el inicio: su vídeo avanza lo mismo
            for m in it.get("media") or []:
                m["media_start"] = float(m.get("media_start", 0.0) or 0.0) + (a - it["t0"])
        it["props"] = _shift(it.get("props") or {}, a)
        it["cues"] = {k: v - a for k, v in (it.get("cues") or {}).items()}
        it["t0"], it["t1"] = t0 - a, t1 - a
        if item_id and it["id"] == item_id:
            if component:
                it["component"] = component
            it["props"].update(extra_props or {})
        ov = (overrides or {}).get(it["id"])
        if ov:
            if ov.get("component"):
                it["component"] = ov["component"]
            if "props_replace" in ov:
                it["props"] = dict(ov["props_replace"])
            it["props"].update(ov.get("props") or {})
        items.append(it)
    s["items"] = items
    s["duration"] = round(b - a, 4)
    ar = s.get("aroll") or {}
    ar["media_start"] = float(ar.get("media_start", 0.0)) + a
    ar["duration"] = b - a
    ar["faces"] = [[f[0] - a] + list(f[1:]) for f in ar.get("faces", []) if a - 1 <= f[0] <= b + 1]
    s["aroll"] = ar
    s["slug"] = f'lab-{component or "window"}'
    return s


def render(hf_dir: Path, out: Path, workers: str = "auto") -> float:
    out = Path(out).resolve()          # HF resuelve -o desde su cwd (hf_dir)
    t = time.time()
    p = subprocess.run(["npx", "--yes", f"hyperframes@{HF_VERSION}", "render", ".", "-o", str(out), "-q", "looks", "-w", workers,
                        "--browser-timeout", "300", "--player-ready-timeout", "180000"], cwd=hf_dir, capture_output=True, text=True)
    (out.parent / (out.stem + "_hf.log")).write_text(p.stdout[-20000:] + "\n---\n" + p.stderr[-20000:])
    if p.returncode != 0 or not out.exists():
        raise RuntimeError(f"hyperframes render falló ({p.returncode}); ver {out.stem}_hf.log")
    return time.time() - t


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("vid")
    ap.add_argument("--item", default=None, help="id del item del render_spec (p. ej. it_d012)")
    ap.add_argument("--override", default="{}", help='JSON {item_id: {"component", "props", "props_replace"}} (varios items)')
    ap.add_argument("--component", default=None, help="componente que lo sustituye (p. ej. scene.logo_reveal3d)")
    ap.add_argument("--props", default="{}", help="props extra (JSON)")
    ap.add_argument("--from", dest="a", type=float, required=True)
    ap.add_argument("--to", dest="b", type=float, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--render", action="store_true", help="renderiza con HyperFrames y multiplexa el audio de la versión")
    ap.add_argument("--workers", default="auto")
    ap.add_argument("--frames", default="", help="instantes (s, relativos a --from) a extraer del MP4")
    args = ap.parse_args(argv)

    vd = version_dir(args.slug, args.vid)
    spec = json.loads((vd / "render_spec.json").read_text())
    out = Path(args.out).resolve()
    s = window_spec(spec, args.a, args.b, args.item, args.component, json.loads(args.props), json.loads(args.override))
    build_project(s, out / "hf")
    print(json.dumps([(i["id"], i["component"], round(i["t0"], 3), round(i["t1"], 3)) for i in s["items"]], ensure_ascii=False))
    if not args.render:
        return 0
    ov = json.loads(args.override)
    name = (args.component or next((v.get("component") for v in ov.values() if v.get("component", "").split(".")[0] not in ("layout", "")), None)
            or "ventana").replace("/", "_")
    mp4 = out / f"{name}.mp4"
    dt = render(out / "hf", mp4, args.workers)
    print(f"[lab] HF {dt:.1f} s → {mp4}")
    mix = vd / "audio" / "mix.wav"
    if mix.exists():
        mo = out / f"{name}_audio.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-ss", f"{args.a:.3f}", "-t", f"{args.b - args.a:.3f}", "-i", str(mix),
                        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", str(mo)], check=True)
        print(f"[lab] con audio → {mo}")
    if args.frames:
        fd = out / "frames"
        fd.mkdir(parents=True, exist_ok=True)
        for t in [float(x) for x in args.frames.split(",") if x.strip()]:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(mp4), "-frames:v", "1", str(fd / f"f_{t:.2f}.png")], check=True)
        print(f"[lab] fotogramas → {fd}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
