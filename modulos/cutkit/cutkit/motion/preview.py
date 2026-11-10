"""Vista previa de un componente aislado: mini composición + PNG a varios instantes (Playwright + seek de la timeline).

    uv run python -m cutkit.motion.preview caption.lockup --props p.json --at 0.2,0.5,1.0 --out datos/vistas \
        [--bg clientes/acme/creativos/2026-11-09_demo-crm/brutos/full.mp4 --bg-time 12.0] [--layout layout.split_top] [--media captura.png] [--dur 3] [--t0 0.1]

- Fondo: un fotograma del vídeo (`--bg` vídeo + `--bg-time`, se extrae con ffmpeg) o una imagen; sin `--bg`, fondo
  liso.
- `--layout` añade un item de layout bajo el componente (para ver media/subtítulos en el split, la tarjeta…).
- Las props pueden traer tiempos relativos al item (`words[].t0` …) si se pasa `--relative`: se suman a `--t0`.
- Salida: <out>/<componente>_<t>.png y <out>/<componente>_hoja.jpg (hoja de contacto con todos los instantes).
"""
from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import subprocess
import sys
from pathlib import Path

from cutkit.motion.html import build_project
from cutkit.motion.registry import COMPONENTS, validate_props

from cutkit.paths import RAIZ

REPO = RAIZ
DEFAULT_FACE = [0.27, 0.25, 0.48, 0.41]     # caja típica de una persona a cámara en vertical (x, y, w, h normalizados)
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".webm", ".mkv"}


def _frame(video: Path, t: float, out: Path, width: int = 1080, height: int = 1920) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    vf = f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", "-vf", vf, str(out)],
                   check=True)
    return out


def _shift_times(obj, dt: float):
    if isinstance(obj, dict):
        return {k: (v + dt if k in ("t0", "t1") and isinstance(v, (int, float)) else _shift_times(v, dt)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_shift_times(v, dt) for v in obj]
    return obj


def make_spec(component: str, props: dict, out: Path, *, dur: float, t0: float, layout: str | None, layout_props: dict,
              media: list[str], bg: str | None, bg_time: float, face: list[float], cues: dict) -> dict:
    W, H, fps = 1080, 1920, 30
    media_dir = out / "_project" / "media"
    media_dir.mkdir(parents=True, exist_ok=True)
    aroll = None
    bg_path = Path(bg) if bg else None
    if bg_path and bg_path.exists():
        if bg_path.suffix.lower() in VIDEO_EXT:
            png = _frame(bg_path, bg_time, media_dir / "bg.png")
        else:
            png = media_dir / ("bg" + bg_path.suffix.lower())
            shutil.copy2(bg_path, png)
        aroll = {"src": f"media/{png.name}", "kind": "image", "duration": dur, "faces": [[0.0, *face], [dur, *face]]}
    spec_c = COMPONENTS.get(component, {})
    track = spec_c.get("track", "graphic")
    items = []
    if layout:
        items.append({"id": "it_layout", "track": "layout", "t0": 0.0, "t1": dur, "component": layout, "props": layout_props})
    it = {"id": "it_prev", "track": track, "t0": t0, "t1": dur, "component": component, "props": props, "cues": cues}
    mlist = []
    for i, m in enumerate(media):
        mp = Path(m)
        if mp.suffix.lower() in VIDEO_EXT:
            mp = _frame(mp, 0.5, media_dir / f"m{i}.png", 1920, 1080)
        else:
            dst = media_dir / f"m{i}{mp.suffix.lower()}"
            shutil.copy2(mp, dst)
            mp = dst
        mlist.append({"id": f"m_prev_{i}", "kind": "image", "src": f"media/{mp.name}"})
    if mlist:
        it["media"] = mlist
    items.append(it)
    return {"fps": fps, "width": W, "height": H, "duration": dur, "slug": f"preview-{component}",
            "tokens": {"caption_y": 0.58}, "aroll": aroll, "items": items}


async def _shoot(index: Path, times: list[float], out: Path, name: str) -> list[Path]:
    from playwright.async_api import async_playwright

    shots = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        logs: list[str] = []
        page.on("console", lambda m: logs.append(f"[{m.type}] {m.text}"))
        page.on("pageerror", lambda e: logs.append(f"[pageerror] {e}"))
        await page.goto(index.as_uri())
        await page.wait_for_function("!!(window.__timelines && window.__timelines.main)", polling=100, timeout=30000)
        rep = await page.evaluate("window.__ckReport")
        if rep and (rep.get("errors") or rep.get("missing")):
            print("[preview] runtime:", json.dumps({k: rep[k] for k in ("errors", "missing")}, ensure_ascii=False)[:2000])
        for t in times:
            await page.evaluate(f"window.__ckSeek({t})")
            await page.wait_for_timeout(30)
            f = out / f"{name}_{t:.2f}.png"
            await page.screenshot(path=str(f), clip={"x": 0, "y": 0, "width": 1080, "height": 1920})
            shots.append(f)
        for line in logs:
            if "error" in line.lower() or "warn" in line.lower():
                print("[preview]", line)
        await browser.close()
    return shots


def contact_sheet(shots: list[Path], out: Path, labels: list[str] | None = None, thumb_w: int = 360) -> Path | None:
    try:
        from PIL import Image, ImageDraw
    except Exception:  # noqa: BLE001
        return None
    ims = [Image.open(s).convert("RGB") for s in shots]
    th = int(thumb_w * 1920 / 1080)
    sheet = Image.new("RGB", (thumb_w * len(ims) + 8 * (len(ims) + 1), th + 48), (24, 24, 28))
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate(ims):
        x = 8 + i * (thumb_w + 8)
        sheet.paste(im.resize((thumb_w, th)), (x, 40))
        d.text((x + 4, 12), (labels[i] if labels else shots[i].stem), fill=(250, 210, 80))
    sheet.save(out, quality=88)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("component")
    ap.add_argument("--props", help="JSON con las props (fichero o literal)")
    ap.add_argument("--at", default="0.2,0.5,1.0", help="instantes en segundos de la mini composición")
    ap.add_argument("--out", required=True)
    ap.add_argument("--dur", type=float, default=None)
    ap.add_argument("--t0", type=float, default=0.0, help="inicio del item")
    ap.add_argument("--relative", action="store_true", help="los t0/t1 de las props son relativos a --t0")
    ap.add_argument("--layout", default=None)
    ap.add_argument("--layout-props", default="{}")
    ap.add_argument("--media", action="append", default=[])
    ap.add_argument("--bg", default=None)
    ap.add_argument("--bg-time", type=float, default=12.0)
    ap.add_argument("--face", default=",".join(map(str, DEFAULT_FACE)))
    ap.add_argument("--cues", default="{}")
    a = ap.parse_args(argv)

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    props = {}
    if a.props:
        pp = Path(a.props)
        props = json.loads(pp.read_text(encoding="utf-8")) if pp.exists() else json.loads(a.props)
    if a.relative:
        props = _shift_times(props, a.t0)
    errs = validate_props(a.component, props) if a.component in COMPONENTS else []
    for e in errs:
        print("[preview] props:", e)
    times = [float(x) for x in a.at.split(",") if x.strip()]
    dur = a.dur or max(times) + 0.5
    lp = Path(a.layout_props)
    layout_props = json.loads(lp.read_text()) if lp.exists() else json.loads(a.layout_props)
    cues = json.loads(a.cues)
    spec = make_spec(a.component, props, out, dur=dur, t0=a.t0, layout=a.layout, layout_props=layout_props, media=a.media,
                     bg=a.bg, bg_time=a.bg_time, face=[float(x) for x in a.face.split(",")], cues=cues)
    index = build_project(spec, out / "_project")
    name = a.component.replace(".", "_")
    shots = asyncio.run(_shoot(index, times, out, name))
    sheet = contact_sheet(shots, out / f"{name}_hoja.jpg", [f"{a.component} t={t:.2f}" for t in times])
    for s in shots:
        print(s)
    if sheet:
        print(sheet)
    return 0


if __name__ == "__main__":
    sys.exit(main())
