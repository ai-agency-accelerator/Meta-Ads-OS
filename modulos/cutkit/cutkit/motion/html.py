"""cutkit.motion.html — render_spec (dict) → proyecto HyperFrames (index.html + fonts/ + media/ + boxes.js).

Contrato HF 0.8.114 (README del módulo):
- root `#root[data-composition-id=main][data-start=0][data-duration][data-width][data-height][data-fps]`;
- TODO `<video>`/`<img>` está en el HTML estático: el A-roll (`<video id="aroll" muted>`) dentro de envoltorios de
  cámara SIN data-start; cada `items[].media` como etiqueta con data-start/data-duration/data-media-start, `muted`,
  dentro de `.ck-mwrap > .ck-mzoom` (sin data-start), con id = media[].id (el componente lo recibe en ctx.media);
- items no-media: `<div class="clip ck-item" data-start data-duration data-track-index>` (root del componente);
- una `gsap.timeline({paused:true})` registrada en `window.__timelines["main"]` DESPUÉS de cargar fuentes e imágenes;
- runtime.js/.css y TODOS los `components/*.js|css` (también los del agente de gráficos) van inline.
"""
from __future__ import annotations

import copy
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any

from ..paths import FUENTES, RAIZ

HERE = Path(__file__).resolve().parent
REPO = RAIZ                      # rutas relativas de medios: respecto a la raíz del producto
FONTS_DIR = FUENTES
COMPONENTS_DIR = HERE / "components"

GSAP_URL = "https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"
CUSTOMEASE_URL = "https://cdn.jsdelivr.net/npm/gsap@3.15/dist/CustomEase.min.js"

# Fuentes OFL que el runtime da por supuestas (--ck-sans/ui/mono), incluidas en `recursos/fuentes/`. Regla de estilo:
# sin serif cursiva decorativa; `--ck-serif` apunta a Montserrat y esa familia no se carga aunque el render_spec la
# traiga (ver BANNED_FONT_FAMILIES).
DEFAULT_FONTS = [
    {"family": "Montserrat", "file": str(FONTS_DIR / "Montserrat[wght].ttf"), "weight": "100 900", "style": "normal"},
    {"family": "Montserrat", "file": str(FONTS_DIR / "Montserrat-Italic[wght].ttf"), "weight": "100 900", "style": "italic"},
    {"family": "Inter", "file": str(FONTS_DIR / "Inter[opsz,wght].ttf"), "weight": "100 900", "style": "normal"},
    {"family": "JetBrains Mono", "file": str(FONTS_DIR / "JetBrainsMono[wght].ttf"), "weight": "100 800", "style": "normal"},
]

BANNED_FONT_FAMILIES = {"instrument serif"}   # regla de estilo: sin serif cursiva decorativa

TRACK_INDEX = {"layout": 1, "camera": 2, "broll": 3, "graphic": 4, "caption": 5, "transition": 6, "overlay": 7}
# capas fuera de #ck-content (las transiciones filtran/transforman la escena entera)
OUTSIDE_CONTENT = {"transition", "overlay", "caption"}   # los subtítulos quedan por ENCIMA de las transiciones (contraste)
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".avif"}


# ───────────────────────────────────────────────────────── utilidades
def _esc(s: Any) -> str:
    return (str(s).replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;"))


def _num(v: float, nd: int = 4) -> str:
    s = f"{float(v):.{nd}f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def _snap(t: float, fps: float) -> float:
    return round(float(t) * fps) / fps


def _floor6(t: float) -> float:
    """Redondeo HACIA ABAJO a 6 decimales: el atributo nunca puede quedar por encima del instante exacto del
    fotograma (64,4667 > 1934/30 = 64,46666… dejaba el clip oculto en su primer fotograma → negro)."""
    import math
    return math.floor(float(t) * 1e6 + 1e-6) / 1e6


def _timing(t0: float, t1: float) -> tuple[str, str]:
    """(data-start, data-duration) con inicio y fin redondeados hacia abajo: visible en [t0, t1) fotograma a fotograma."""
    a, b = _floor6(t0), _floor6(t1)
    return f"{a:.6f}".rstrip("0").rstrip(".") or "0", f"{max(1e-6, b - a):.6f}".rstrip("0").rstrip(".")


def _place(source: str | os.PathLike | None, dest: Path, base_dir: Path | None) -> bool:
    """Enlaza (duro) o copia `source` → `dest`. Devuelve True si `dest` existe al final."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not source:
        return dest.exists()
    src = Path(source)
    if not src.is_absolute():
        for b in [base_dir, Path.cwd(), REPO]:
            if b and (Path(b) / src).exists():
                src = Path(b) / src
                break
    if not src.exists():
        return dest.exists()
    src = src.resolve()
    if dest.exists():
        try:
            if os.path.samefile(src, dest):
                return True
            st_s, st_d = src.stat(), dest.stat()
            if st_s.st_size == st_d.st_size and int(st_s.st_mtime) <= int(st_d.st_mtime):
                return True
        except OSError:
            pass
        dest.unlink()
    try:
        os.link(src, dest)
    except OSError:
        shutil.copy2(src, dest)
    return True


def _safe_font_name(path: Path) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", path.name).replace("-.", ".")


def _rel(p: str) -> str:
    return str(p).lstrip("./") if not str(p).startswith("../") else str(p)


def _is_image(src: str, kind: str | None = None) -> bool:
    if kind:
        return kind in ("image", "svg")
    return Path(str(src)).suffix.lower() in IMAGE_EXT


# ───────────────────────────────────────────────────────── piezas
def _fonts_block(spec: dict, out_dir: Path) -> tuple[str, list[str]]:
    fonts = [f for f in (spec.get("fonts") or []) if str(f.get("family", "")).strip().lower() not in BANNED_FONT_FAMILIES]
    have = {(f.get("family"), f.get("style", "normal")) for f in fonts}
    for f in DEFAULT_FONTS:
        if (f["family"], f["style"]) not in have:
            fonts.append(f)
    css, loads, seen = [], [], set()
    for f in fonts:
        src = Path(f["file"])
        if not src.is_absolute():
            cand = [FONTS_DIR / src.name, REPO / src, Path(spec.get("base_dir") or ".") / src]
            src = next((c for c in cand if c.exists()), src)
        if not src.exists():
            continue
        name = _safe_font_name(src)
        if name in seen:
            continue
        seen.add(name)
        _place(src, out_dir / "fonts" / name, None)
        fmt = {"ttf": "truetype", "otf": "opentype", "woff2": "woff2", "woff": "woff"}.get(src.suffix.lower().lstrip("."), "truetype")
        weight = str(f.get("weight", "400"))
        style = f.get("style", "normal")
        css.append(
            f'@font-face {{ font-family: "{f["family"]}"; src: url("fonts/{name}") format("{fmt}"); '
            f"font-weight: {weight}; font-style: {style}; font-display: block; }}"
        )
        w = weight.split()[-1] if " " in weight else weight
        for ww in ({"100 900": ["400", "800"], "100 800": ["400"]}.get(weight, [w])):
            loads.append(f'{"italic " if style == "italic" else ""}{ww} 40px "{f["family"]}"')
    return "\n".join(css), loads


def _component_assets() -> tuple[str, str]:
    """Todos los components/*.js|css (los que empiezan por _ son plantillas y no se cargan)."""
    js, css = [], []
    for p in sorted(COMPONENTS_DIR.glob("*.css")):
        if not p.name.startswith("_"):
            css.append(f"/* ── components/{p.name} ── */\n" + p.read_text(encoding="utf-8"))
    for p in sorted(COMPONENTS_DIR.glob("*.js")):
        if not p.name.startswith("_"):
            js.append(f"/* ── components/{p.name} ── */\n" + p.read_text(encoding="utf-8"))
    return "\n".join(js), "\n".join(css)


def _aroll_block(spec: dict, out_dir: Path, base: Path | None) -> str:
    a = spec.get("aroll") or {}
    src = a.get("src")
    fps = spec.get("fps", 30)
    inner = ""
    if src:
        _place(a.get("path") or src, out_dir / _rel(src), base)
        if _is_image(src, a.get("kind")):
            # vista previa: fotograma fijo (sin data-start: siempre visible)
            inner = f'<img id="aroll" src="{_esc(_rel(src))}" alt="" />'
        else:
            dur = _snap(a.get("duration") or spec.get("duration") or 0, fps)
            inner = (
                f'<video id="aroll" src="{_esc(_rel(src))}" muted playsinline data-start="0" '
                f'data-duration="{_timing(0, dur)[1]}" data-media-start="{_num(a.get("media_start", 0), 6)}" data-track-index="0"></video>'
            )
    bg = ""
    if src and not _is_image(src, a.get("kind")) and any(
            (it.get("component") == "layout.split_top") for it in spec.get("items") or []):
        # copia desenfocada para rellenar los laterales cuando el split escala la cara < 1 (sin data-start propio en el
        # envoltorio; el <video> va con su ventana, como el A-roll)
        dur = _snap(a.get("duration") or spec.get("duration") or 0, fps)
        bg = (f'<div id="ck-cam-bg" class="ck-cam-bg"><video id="aroll_bg" src="{_esc(_rel(src))}" muted playsinline '
              f'data-start="0" data-duration="{_timing(0, dur)[1]}" data-media-start="{_num(a.get("media_start", 0), 6)}" '
              f'data-track-index="0"></video></div>')
    split = ""
    if a.get("split_src"):
        # bruto ya montado en 50/50 (misma toma y tiempos que el A-roll): se monta sincronizado y SOLO se ve su
        # mitad de abajo (clip ≥ costura); la de arriba (escritorio) no se ve nunca. Lo enciende layout.split_top.
        _place(a.get("split_path") or a["split_src"], out_dir / _rel(a["split_src"]), base)
        seam = int(a.get("split_seam") or 960)
        dur = _snap(a.get("duration") or spec.get("duration") or 0, fps)
        split = (f'<div id="ck-split-cam" class="ck-split-cam" style="clip-path: inset({seam}px 0px 0px 0px)">'
                 f'<video id="aroll_split" src="{_esc(_rel(a["split_src"]))}" muted playsinline data-start="0" '
                 f'data-duration="{_timing(0, dur)[1]}" data-media-start="{_num(a.get("media_start", 0), 6)}" '
                 f'data-track-index="0"></video></div>')
    return bg + split + (
        '<div id="ck-cam" class="ck-cam"><div id="ck-cam-push"><div id="ck-cam-move"><div id="ck-cam-frame">'
        f"{inner}</div></div></div></div>"
    )


def _items_block(spec: dict, out_dir: Path, base: Path | None) -> tuple[str, str]:
    """Devuelve (html dentro de #ck-content, html fuera de #ck-content)."""
    fps = spec.get("fps", 30)
    inside, outside = [], []
    for it in spec.get("items") or []:
        track = it.get("track", "graphic")
        t0 = max(0.0, _snap(it["t0"], fps))
        t1 = max(t0 + 1.0 / fps, _snap(it["t1"], fps))
        ds, dd = _timing(t0, t1)
        ti = TRACK_INDEX.get(track, 4)
        dest = outside if track in OUTSIDE_CONTENT else inside
        for m in it.get("media") or []:
            msrc = m.get("src")
            if not msrc:
                continue
            _place(m.get("path") or msrc, out_dir / _rel(msrc), base)
            mid = _esc(m["id"])
            asset = f' data-asset="{_esc(m["asset"])}"' if m.get("asset") else ""
            common = f'data-start="{ds}" data-duration="{dd}" data-track-index="{TRACK_INDEX["broll"]}"{asset}'
            if _is_image(msrc, m.get("kind")):
                tag = f'<img id="{mid}" class="clip ck-media" src="{_esc(_rel(msrc))}" alt="" {common} />'
            else:
                # 21-oct-2026: un vídeo con entrada propia (`start`: la cue de su línea en title.lockup_grid) arranca ahí y
                # dura hasta el final del item; `loop` lo repite desde su `media_start` (HyperFrames lee el atributo)
                vcommon = common
                if m.get("start") is not None:
                    vs = min(max(t0, _snap(float(m["start"]), fps)), t1 - 1.0 / fps)
                    vds, vdd = _timing(vs, t1)
                    vcommon = f'data-start="{vds}" data-duration="{vdd}" data-track-index="{TRACK_INDEX["broll"]}"{asset}'
                loop = " loop" if m.get("loop") else ""
                tag = (f'<video id="{mid}" class="ck-media" src="{_esc(_rel(msrc))}" muted playsinline{loop} {vcommon} '
                       f'data-media-start="{_num(m.get("media_start", 0), 6)}"></video>')
            dest.append(f'<div class="ck-mwrap" id="mw_{mid}" data-ck-item="{_esc(it["id"])}"><div class="ck-mzoom">{tag}</div></div>')
        dest.append(
            f'<div id="{_esc(it["id"])}" class="clip ck-item ck-track-{_esc(track)}" data-start="{ds}" '
            f'data-duration="{dd}" data-track-index="{ti}" data-ck-component="{_esc(it.get("component") or "")}"></div>'
        )
    return "\n      ".join(inside), "\n    ".join(outside)


def _matte_pass(spec: dict, out_dir: Path) -> str:
    """Sujeto recortado por fotograma (cutkit/tools/matte.py) para los componentes con `matte: True` en el registro
    (p. ej. title.behind_subject). Mapea el tramo de programa del item a la fuente (timeline.json + media_index.json
    junto al program.mp4), calcula o reutiliza la caché de recortes RGBA y deja en `item.props._matte`
    {fps, frames:[{pf, src, top, cx}], crop, cut_scale, size}. Devuelve <img> ocultos de precarga (el bootstrap y HF
    los decodifican antes de capturar → el componente los dibuja en su canvas, síncrono y determinista).
    Sin mate posible (vista previa con fotograma fijo, error), el componente cae a su variante sin sujeto."""
    try:
        from cutkit.motion.registry import COMPONENTS
    except Exception:  # noqa: BLE001
        return ""
    names = {n for n, c in COMPONENTS.items() if isinstance(c, dict) and c.get("matte")}
    items = [it for it in spec.get("items") or [] if it.get("component") in names
             and (it.get("props") or {}).get("subject", "auto") != "none"]
    if not items:
        return ""
    ar = spec.get("aroll") or {}
    apath = ar.get("path")
    fps = float(spec.get("fps", 30))
    off = float(ar.get("media_start", 0.0) or 0.0)        # composición recortada (lab/preview): t_programa = t + off
    poff = int(round(off * fps))
    tags = []
    for it in items:
        props = it.setdefault("props", {})
        try:
            from cutkit.tools.matte import matte_range, program_window
            wins = program_window(apath, float(it["t0"]) + off, float(it["t1"]) + off, fps) if apath else []
            if not wins:
                props["_matte_error"] = "sin mapa programa→fuente (A-roll no es un program.mp4 de una versión)"
                continue
            res = int(COMPONENTS[it["component"]].get("matte_res", 1260))
            frames, meta = [], None
            for w in wins:
                meta = matte_range(w["src"], f0=w["f0"], f1=w["f1"], cutout=res, verbose=True)
                d = Path(meta["dir"])
                rel = f"media/mattes/{d.name}"
                rows = {r["f"]: r for r in meta["frames"]}
                for pf in range(w["pf0"], w["pf1"] + 1):
                    f = min(w["f1"], w["f0"] + (pf - w["pf0"]))
                    name = f"c_{f:05d}.webp"
                    _place(d / name, out_dir / rel / name, None)
                    r = rows.get(f, {})
                    frames.append({"pf": pf - poff, "src": f"{rel}/{name}", "top": r.get("top"), "cx": r.get("cx")})
            props["_matte"] = {"fps": fps, "frames": frames, "crop": meta["crop"], "cut_scale": meta["cut_scale"],
                               "size": meta["size"], "cut_size": meta["cut_size"]}
            for k, fr in enumerate(frames):
                tags.append(f'<img id="pl_{_esc(it["id"])}_{k}" class="ck-preload" src="{_esc(fr["src"])}" alt="" decoding="sync" />')
        except Exception as e:  # noqa: BLE001
            props["_matte_error"] = f"{type(e).__name__}: {e}"
            print(f"[html] mate de {it.get('id')}: {props['_matte_error']} → sin sujeto")
    if not tags:
        return ""
    return '<div id="ck-preload" aria-hidden="true" style="display:none">' + "".join(tags) + "</div>"


def _vframes_pass(spec: dict, out_dir: Path) -> None:
    """Fotogramas de los VÍDEOS de items cuyo componente tiene `video_frames: True` en el registro (escenas 3D que
    pintan el vídeo como textura). Se extraen con ffmpeg (JPEG, fps del proyecto, desde `media_start`) a una caché
    por hash junto a los media del run, se enlazan en `media/vframes/<hash>/` y se deja `props._vframes`
    {dir, count, fps, w, h}. La escena los carga por índice en el seek (hf-seek waitUntil): sin precarga masiva."""
    try:
        from cutkit.motion.registry import COMPONENTS
    except Exception:  # noqa: BLE001
        return
    names = {n for n, c in COMPONENTS.items() if isinstance(c, dict) and c.get("video_frames")}
    fps = float(spec.get("fps", 30))
    import hashlib
    import subprocess
    for it in spec.get("items") or []:
        if it.get("component") not in names:
            continue
        vids = [m for m in it.get("media") or [] if (m.get("kind") == "video" or str(m.get("src", "")).lower().endswith((".mp4", ".mov", ".webm")))]
        if not vids:
            continue
        m = vids[0]
        src = Path(m.get("path") or m.get("src"))
        if not src.is_absolute():
            src = (REPO / src) if (REPO / src).exists() else (out_dir / _rel(str(m.get("src"))))
        if not src.exists():
            it.setdefault("props", {})["_vframes_error"] = f"no existe {src}"
            continue
        dur = max(1.0 / fps, float(it["t1"]) - float(it["t0"])) + 2.0 / fps
        ms = float(m.get("media_start", 0.0) or 0.0)
        st = src.stat()
        key = hashlib.sha1(f"{src.resolve()}|{st.st_size}|{st.st_mtime_ns}|{ms:.4f}|{dur:.4f}|{fps}|v1".encode()).hexdigest()[:16]
        root = next((a for a in src.resolve().parents if a.name == "media"), src.resolve().parent)
        cache = root / "vframes" / key
        if not (cache / "done.json").exists():
            cache.mkdir(parents=True, exist_ok=True)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ms:.4f}", "-i", str(src), "-t", f"{dur:.4f}",
                            "-vf", f"fps={fps:g}", "-q:v", "2", str(cache / "f_%04d.jpg")], check=True)
            (cache / "done.json").write_text("{}")
        frames = sorted(cache.glob("f_*.jpg"))
        if not frames:
            it.setdefault("props", {})["_vframes_error"] = "ffmpeg no produjo fotogramas"
            continue
        rel = f"media/vframes/{key}"
        for fr in frames:
            _place(fr, out_dir / rel / fr.name, None)
        try:
            from PIL import Image
            w, h = Image.open(frames[0]).size
        except Exception:  # noqa: BLE001
            w, h = 1920, 1080
        it.setdefault("props", {})["_vframes"] = {"dir": rel, "count": len(frames), "fps": fps, "w": w, "h": h}


THREE_DIR = HERE / "three"


def _three_block(spec: dict, out_dir: Path) -> str:
    """Capa 3D OPCIONAL (cutkit/motion/three): solo si algún item usa una escena de `three/scenes/<componente>.js`.
    Copia three/fontkit vendorizados + ck3d.js + las escenas usadas a `out_dir/ck3d/` y escribe `ck3d/assets.js`
    (fuentes declaradas en `fonts3d` del registro, en base64, y el texto de los SVG de sus media) para que el
    montaje sea síncrono también en file:// (vista previa). Devuelve las etiquetas <script> o ""."""
    scenes = {p.name[:-3]: p for p in (THREE_DIR / "scenes").glob("*.js")} if (THREE_DIR / "scenes").exists() else {}
    items = [it for it in spec.get("items") or [] if it.get("component") in scenes]
    if not items:
        return ""
    import base64
    dst = out_dir / "ck3d"
    dst.mkdir(parents=True, exist_ok=True)
    files = ["vendor/three.ck.min.js", "vendor/fontkit.ck.min.js", "ck3d.js"]
    for f in files:
        _place(THREE_DIR / f, dst / Path(f).name, None)
    used = sorted({it["component"] for it in items})
    for name in used:
        _place(scenes[name], dst / scenes[name].name, None)
    try:
        from cutkit.motion.registry_three import GRAPHICS_3D
    except Exception:  # noqa: BLE001
        GRAPHICS_3D = {}
    want = []
    for name in used:
        for fam in GRAPHICS_3D.get(name, {}).get("fonts3d", ["Montserrat"]):
            if fam not in want:
                want.append(fam)
    fonts: dict[str, str] = {}
    for f in DEFAULT_FONTS:   # "Familia" = estilo normal · "Familia|italic" = cursiva
        if (f["family"] if f["style"] == "normal" else f'{f["family"]}|{f["style"]}') in want and Path(f["file"]).exists():
            fonts[f'{f["family"]}|{f["style"]}'] = base64.b64encode(Path(f["file"]).read_bytes()).decode("ascii")
    svgs: dict[str, str] = {}
    for it in items:
        for m in it.get("media") or []:
            src = m.get("src") or ""
            p = out_dir / _rel(src)
            if src.lower().endswith(".svg") and p.exists():
                svgs[_rel(src)] = p.read_text(encoding="utf-8", errors="replace")
    (dst / "assets.js").write_text(
        "/* cutkit · ck3d/assets.js (generado por html.py) */\nwindow.__CK3D_ASSETS = "
        + json.dumps({"fonts": fonts, "svg": svgs}, ensure_ascii=False).replace("</", "<\\/") + ";\n", encoding="utf-8")
    tags = ["ck3d/three.ck.min.js", "ck3d/fontkit.ck.min.js", "ck3d/assets.js", "ck3d/ck3d.js"] + [f"ck3d/{scenes[n].name}" for n in used]
    return "\n    ".join(f'<script src="{t}"></script>' for t in tags)


BOXES_JS = r"""/* cutkit · boxes.js — utilidades de QA y vista previa (no cambian el render).
 * window.__ckSeek(t)  → hace seek de la timeline; sin el runtime de HyperFrames emula la visibilidad de los clips
 *                       y busca el fotograma de los <video> (vista previa en Playwright). Devuelve una Promise.
 * window.__ckBoxes(t) → tras el seek, cajas (px del lienzo) de los textos visibles:
 *                       {t, blocks:[{item, component, kind, text, x, y, w, h, opacity}], leaves:[{text, x, y, w, h, font_px, opacity}]}
 */
(function () {
  function clipWindowOk(el, t) {
    for (var n = el; n && n.nodeType === 1; n = n.parentElement) {
      if (n.hasAttribute('data-start') && !n.hasAttribute('data-composition-id')) {
        var s = parseFloat(n.getAttribute('data-start')) || 0;
        var d = n.getAttribute('data-duration');
        if (t < s - 1e-6) return false;
        if (d != null && t >= s + parseFloat(d) - 1e-6) return false;
      }
    }
    return true;
  }
  function effOpacity(el) {
    var o = 1;
    for (var n = el; n && n.nodeType === 1; n = n.parentElement) {
      var cs = getComputedStyle(n);
      if (cs.display === 'none' || cs.visibility === 'hidden') return 0;
      o *= parseFloat(cs.opacity || '1');
    }
    return o;
  }
  function hasHF() { return !!(window.__hyperframes && !window.__ckForceEmulate); }
  window.__ckLastT = 0;
  window.__ckSeek = function (t) {
    window.__ckLastT = t;
    var tl = window.__timelines && window.__timelines.main;
    if (tl) tl.seek(t, true);
    if (hasHF()) return Promise.resolve(t);
    var timed = document.querySelectorAll('[data-start]');
    var waits = [];
    for (var i = 0; i < timed.length; i++) {
      var el = timed[i];
      if (el.hasAttribute('data-composition-id')) continue;
      var ok = clipWindowOk(el, t);
      el.style.visibility = ok ? '' : 'hidden';
      if (ok && el.tagName === 'VIDEO' && el.readyState >= 1) {
        var ms0 = parseFloat(el.getAttribute('data-media-start')) || 0;
        var lt = t - (parseFloat(el.getAttribute('data-start')) || 0);
        var want = lt + ms0;
        // `loop` (como HyperFrames): pasado el final de la fuente, vuelve a su media_start
        if (el.loop && isFinite(el.duration) && el.duration - ms0 > 0.05 && lt >= el.duration - ms0) want = ms0 + (lt % (el.duration - ms0));
        if (Math.abs(el.currentTime - want) > 0.01) {
          waits.push(new Promise(function (res) { el.addEventListener('seeked', res, { once: true }); setTimeout(res, 1500); }));
          el.currentTime = Math.max(0, want);
        }
      }
    }
    return Promise.all(waits).then(function () { return t; });
  };
  window.__ckBoxes = function (t) {
    if (t != null && !hasHF()) window.__ckSeek(t);
    else if (t != null) { var tl = window.__timelines && window.__timelines.main; if (tl) tl.seek(t, true); }
    var tt = t != null ? t : window.__ckLastT;
    var root = document.getElementById('root');
    var R = root.getBoundingClientRect();
    var sx = (parseFloat(root.getAttribute('data-width')) || R.width) / R.width;
    var sy = (parseFloat(root.getAttribute('data-height')) || R.height) / R.height;
    function rect(el) { var r = el.getBoundingClientRect(); return { x: (r.left - R.left) * sx, y: (r.top - R.top) * sy, w: r.width * sx, h: r.height * sy }; }
    var leaves = [], blocks = [];
    var all = root.querySelectorAll('*');
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      if (el.tagName === 'SCRIPT' || el.tagName === 'STYLE' || el.namespaceURI === 'http://www.w3.org/2000/svg') continue;
      var direct = '';
      for (var c = el.firstChild; c; c = c.nextSibling) if (c.nodeType === 3) direct += c.nodeValue;
      direct = direct.replace(/\s+/g, ' ').trim();
      if (!direct) continue;
      if (!clipWindowOk(el, tt)) continue;
      var op = effOpacity(el);
      if (op < 0.05) continue;
      var r = rect(el);
      if (r.w < 1 || r.h < 1) continue;
      leaves.push({ text: direct, x: r.x, y: r.y, w: r.w, h: r.h, font_px: parseFloat(getComputedStyle(el).fontSize), opacity: op });
    }
    var bl = root.querySelectorAll('[data-ck-text]');
    for (var j = 0; j < bl.length; j++) {
      var b = bl[j];
      if (!clipWindowOk(b, tt)) continue;
      var item = b.closest('.ck-item');
      var vis = [];
      var inner = b.querySelectorAll('*');
      var txt = '';
      for (var k = 0; k < inner.length; k++) {
        var e = inner[k];
        var d = '';
        for (var c2 = e.firstChild; c2; c2 = c2.nextSibling) if (c2.nodeType === 3) d += c2.nodeValue;
        if (!d.trim()) continue;
        if (effOpacity(e) < 0.05) continue;
        vis.push(rect(e)); txt += d;
      }
      if (!vis.length) continue;
      var x0 = Math.min.apply(null, vis.map(function (q) { return q.x; })), y0 = Math.min.apply(null, vis.map(function (q) { return q.y; }));
      var x1 = Math.max.apply(null, vis.map(function (q) { return q.x + q.w; })), y1 = Math.max.apply(null, vis.map(function (q) { return q.y + q.h; }));
      blocks.push({ item: item ? item.id : null, component: item ? item.getAttribute('data-ck-component') : null, kind: b.getAttribute('data-ck-text'),
        text: txt.replace(/\s+/g, ' ').trim(), x: x0, y: y0, w: x1 - x0, h: y1 - y0, opacity: effOpacity(b) });
    }
    return { t: tt, blocks: blocks, leaves: leaves };
  };
})();
"""


# ───────────────────────────────────────────────────────── pelo medido (no estimado)
def _hair_track(src: Path, faces: list, cache_dir: Path) -> list[list[float]]:
    """Parte de arriba del pelo MEDIDA en los fotogramas clave del A-roll (≈1/s): primera fila, desde arriba, en la
    que > 35 % de las columnas centrales de la cara son oscuras (luma < 75) y lo siguen 6 filas más. Si el fondo es
    oscuro (detección pegada al inicio del barrido) se usa la estimación por la caja (y − 0,55·h). Caché por tamaño y
    fecha del fichero. Devuelve [[t, y_norm], …]."""
    import subprocess

    import numpy as np

    try:
        st = src.stat()
    except OSError:
        return []
    key = f"{src.name}:{st.st_size}:{int(st.st_mtime)}"
    cache = cache_dir / "hair_track.json"
    if cache.exists():
        try:
            c = json.loads(cache.read_text())
            if c.get("key") == key:
                return c["track"]
        except Exception:  # noqa: BLE001
            pass
    W, H = 270, 480
    try:
        pts = subprocess.run(["ffprobe", "-v", "error", "-skip_frame", "nokey", "-select_streams", "v:0", "-show_entries",
                              "frame=pts_time", "-of", "csv=p=0", str(src)], capture_output=True, text=True, timeout=120).stdout
        times = [float(x.split(",")[0]) for x in pts.split() if x.strip()]
        raw = subprocess.run(["ffmpeg", "-v", "error", "-skip_frame", "nokey", "-i", str(src), "-vf",
                              f"scale={W}:{H},format=gray", "-vsync", "0", "-f", "rawvideo", "-"],
                             capture_output=True, timeout=300).stdout
    except Exception:  # noqa: BLE001
        return []
    frames = np.frombuffer(raw, np.uint8)
    n = len(frames) // (W * H)
    frames = frames[: n * W * H].reshape(n, H, W).astype(np.float32)
    rows = [r for r in faces if isinstance(r, (list, tuple)) and len(r) >= 5]
    track = []
    for i in range(min(n, len(times))):
        t = times[i]
        if not rows:
            break
        r = min(rows, key=lambda q: abs(q[0] - t))
        _, x, y, w, h = map(float, r[:5])
        x0, x1 = int((x + w * 0.25) * W), max(int((x + w * 0.75) * W), int((x + w * 0.25) * W) + 4)
        band = frames[i][:, x0:x1]
        dark = (band < 75).mean(axis=1)
        y0 = max(0, int((y - 0.9 * h) * H))
        yf = int(y * H)
        hit = None
        for yy in range(y0, max(y0 + 1, yf)):
            if dark[yy] > 0.35 and dark[yy:yy + 6].min() > 0.3:
                hit = yy
                break
        est = y - 0.55 * h
        if hit is None or hit <= y0 + 1:
            val = est                                   # fondo oscuro o sin pelo detectable → estimación
        else:
            val = hit / H
            if not (y - 0.85 * h <= val <= y - 0.25 * h):
                val = est
        track.append([round(t, 3), round(val, 4)])
    try:
        cache.write_text(json.dumps({"key": key, "track": track}))
    except OSError:
        pass
    return track


# ───────────────────────────────────────────────────────── normalización (antes de escribir el HTML)
BACKDROP_LAYOUTS = {"layout.broll_full", "layout.card_float"}   # fondo opaco: si el contenido acaba antes, queda un plano vacío


def normalize_spec(spec: dict) -> dict:
    """Arreglos deterministas de tiempos entre layouts y contenido (evitan parpadeos a negro):
    - un gráfico/recurso dentro de un layout con fondo opaco que acaba ≤ 0,4 s antes que su layout se ALARGA hasta el
      corte del layout (sostiene su estado final) y sale en corte (`props.exit = "cut"`);
    - todo gráfico/recurso que acaba en el corte de su layout (±2 f) sale en corte (`exit: "cut"`) salvo que ya traiga `exit`.
    Escribe lo que cambia en `item["_ck_norm"]` para la trazabilidad."""
    fps = float(spec.get("fps", 30))
    fr = 1.0 / fps
    items = spec.get("items") or []
    layouts = sorted((i for i in items if i.get("track") == "layout"), key=lambda i: float(i["t0"]))
    # subtítulos: nunca dos páginas a la vez (el compilador las solapa ~1–3 f y el pop de entrada montaba dos palabras):
    # la saliente acaba EXACTAMENTE donde entra la siguiente. HF muestra cada clip en [t0, t1): sin solape y sin el
    # fotograma vacío que dejaba el «− 1 f» anterior (parpadeo en cada relevo: el relevo va en el mismo fotograma)
    caps = sorted((i for i in items if i.get("track") == "caption"), key=lambda i: float(i["t0"]))
    for cur, nxt in zip(caps, caps[1:]):
        lim = _snap(float(nxt["t0"]), fps)
        if float(cur["t1"]) > lim and lim > float(cur["t0"]) + fr:
            cur.setdefault("_ck_norm", {})["t1_from"] = float(cur["t1"])
            cur["t1"] = lim
    # el panel de un split que entra deslizando nunca cae vacío: el gráfico/recurso que empieza ≤ 0,6 s después del
    # corte se adelanta al corte (cae con el panel desde el fotograma 0; sus cues internos no cambian)
    for it in items:
        if it.get("track") not in ("graphic", "broll"):
            continue
        t0 = float(it["t0"])
        L = next((l for l in layouts if l.get("component") == "layout.split_top"
                  and (l.get("props") or {}).get("enter") == "slide"
                  and float(l["t0"]) + fr / 2 < t0 <= float(l["t0"]) + 0.6 + 1e-6 and t0 < float(l["t1"])), None)
        if not L:
            continue
        d = t0 - float(L["t0"])
        it["_ck_norm"] = dict(it.get("_ck_norm") or {}, t0_from=t0, reason="adelantado al corte del split deslizado")
        it["t0"] = float(L["t0"])
        for m in it.get("media") or []:
            if (m.get("kind") or "video") == "video" and m.get("media_start") is not None:
                m["media_start"] = max(0.0, float(m["media_start"]) - d)
    # un gráfico/recurso que empieza o acaba a ≤ 2 f de un cambio de layout se encaja a ese cambio (si no, sale 1 f
    # sobre el layout equivocado: panel vacío o cara sin su lienzo)
    bounds = sorted({round(float(L["t0"]), 4) for L in layouts} | {round(float(L["t1"]), 4) for L in layouts})
    for it in items:
        if it.get("track") not in ("graphic", "broll"):
            continue
        for key in ("t0", "t1"):
            v = float(it[key])
            near = [b for b in bounds if 1e-4 < abs(b - v) <= 2 * fr + 1e-4]
            if near:
                b = min(near, key=lambda x: abs(x - v))
                if key == "t1" and b <= float(it["t0"]) + fr:
                    continue
                it.setdefault("_ck_norm", {})[f"{key}_from"] = v
                if key == "t0":
                    for m in it.get("media") or []:
                        if (m.get("kind") or "video") == "video" and m.get("media_start") is not None:
                            m["media_start"] = max(0.0, float(m["media_start"]) + (b - v))
                it[key] = b
    for it in items:
        if it.get("track") not in ("graphic", "broll"):
            continue
        t0, t1 = float(it["t0"]), float(it["t1"])
        lay = next((L for L in layouts if float(L["t0"]) - 1e-3 <= t0 < float(L["t1"]) - 1e-3), None)
        if not lay:
            continue
        lt1 = float(lay["t1"])
        props = it.setdefault("props", {})
        if lay.get("component") in BACKDROP_LAYOUTS and 2 * fr < lt1 - t1 <= 0.4 + 1e-6:
            it["_ck_norm"] = {"t1_from": t1, "reason": "contenido acababa antes que su layout con fondo opaco"}
            it["t1"] = t1 = lt1
            props.setdefault("exit", "cut")
        if abs(lt1 - t1) <= 2 * fr + 1e-6:
            props.setdefault("exit", "cut")
    return spec


# ───────────────────────────────────────────────────────── API
def build_project(render_spec: dict, out_dir: Path) -> Path:
    """Escribe `out_dir/index.html` (+ fonts/, media enlazada, boxes.js) y devuelve la ruta del index."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    spec = copy.deepcopy(render_spec)
    base = Path(spec["base_dir"]) if spec.get("base_dir") else None
    W, H = int(spec.get("width", 1080)), int(spec.get("height", 1920))
    fps = spec.get("fps", 30)
    duration = _snap(spec.get("duration") or 0, fps)
    spec["duration"] = duration
    spec.setdefault("items", [])
    normalize_spec(spec)
    spec["items"] = sorted(spec["items"], key=lambda it: (float(it.get("t0", 0)), str(it.get("id"))))
    preload = _matte_pass(spec, out_dir)   # "" si ningún item pide sujeto recortado
    _vframes_pass(spec, out_dir)           # fotogramas de vídeo para escenas 3D que los piden

    font_css, font_loads = _fonts_block(spec, out_dir)
    comp_js, comp_css = _component_assets()
    runtime_js = (HERE / "runtime.js").read_text(encoding="utf-8")
    runtime_css = (HERE / "runtime.css").read_text(encoding="utf-8")
    aroll = _aroll_block(spec, out_dir, base)
    inside, outside = _items_block(spec, out_dir, base)
    three_js = _three_block(spec, out_dir)   # "" si no hay escenas 3D (capa opcional)
    (out_dir / "boxes.js").write_text(BOXES_JS, encoding="utf-8")

    # pelo medido en el A-roll (los layouts y la cámara lo usan en vez de la estimación por la caja de la cara)
    a = spec.get("aroll") or {}
    if a.get("src") and not _is_image(a["src"], a.get("kind")) and not a.get("hair"):
        a["hair"] = _hair_track(out_dir / _rel(a["src"]), a.get("faces") or [], out_dir)

    # el spec embebido no necesita rutas absolutas del disco
    emb = copy.deepcopy(spec)
    emb.pop("fonts", None)
    if isinstance(emb.get("aroll"), dict):
        emb["aroll"].pop("path", None)
        emb["aroll"].pop("split_path", None)
    for it in emb["items"]:
        for m in it.get("media") or []:
            m.pop("path", None)
    spec_json = json.dumps(emb, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    html = f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>cutkit · {_esc(spec.get("slug", "composición"))}</title>
    <script src="{GSAP_URL}"></script>
    <script src="{CUSTOMEASE_URL}"></script>
    <style>
{font_css}
{runtime_css}
{comp_css}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{_timing(0, duration)[1]}" data-width="{W}" data-height="{H}" data-fps="{_num(fps)}">
      <div id="ck-stage">
        <div id="ck-content">
          <div id="ck-bg"></div>
          {aroll}
          {inside}
        </div>
        {outside}
      </div>
      {preload}
    </div>
    <script type="application/json" id="ck-spec">{spec_json}</script>
    <script>
{runtime_js}
    </script>
    <script>
{comp_js}
    </script>
    {three_js}
    <script src="boxes.js"></script>
    <script>
      (function () {{
        if (window.CustomEase) gsap.registerPlugin(CustomEase);
        var spec = JSON.parse(document.getElementById("ck-spec").textContent);
        var FONTS = {json.dumps(font_loads, ensure_ascii=False)};
        var fontsReady = Promise.all(FONTS.map(function (f) {{ return document.fonts.load(f).catch(function () {{}}); }}))
          .then(function () {{ return document.fonts.ready; }});
        var imgsReady = Promise.all(Array.prototype.map.call(document.images, function (im) {{
          return (im.decode ? im.decode() : Promise.resolve()).catch(function () {{}});
        }}));
        Promise.all([fontsReady, imgsReady]).then(function () {{
          var tl = gsap.timeline({{ paused: true }});
          CK.run(spec, tl);
          // el kit nunca anima en t=0 exacto (T = máx(t, 0,001)) y HyperFrames rebobina a t al buscar: sin esto el
          // fotograma 0 sale con el estado de montaje (todo oculto). t=0 se pinta como t=0,002.
          var OFF = 0.002, rawTT = tl.totalTime;
          tl.totalTime = function (v, s) {{
            return arguments.length ? rawTT.call(this, Math.max(0, v) + OFF, s) : Math.max(0, rawTT.call(this) - OFF);
          }};
          tl.totalTime(0, true);
          window.__timelines = window.__timelines || {{}};
          window.__timelines["main"] = tl;
          if (window.__hfForceTimelineRebind) window.__hfForceTimelineRebind();
        }});
      }})();
    </script>
  </body>
</html>
"""
    index = out_dir / "index.html"
    index.write_text(html, encoding="utf-8")
    return index
