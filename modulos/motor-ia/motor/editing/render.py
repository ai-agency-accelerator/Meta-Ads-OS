"""Render de la timeline con FFmpeg, no destructivo y con caché por segmento.

Etapas:
  1. Cada VideoClip se normaliza (1080×1920, fps fijo, GOP cerrado, sin audio) → segmento cacheado
     por hash(asset, recorte, zoom, tamaño). Cambiar el hook solo re-renderiza ese segmento.
  2. Concatenación sin recodificar (concat demuxer, mismos parámetros en todos los segmentos).
  3. Pasada única de acabado: overlays (stickers, logos, etiqueta IA), subtítulos ASS, grano,
     corrección suave → H.264 CRF 18 + audio mezclado y normalizado.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

from ..costs import record_local
from ..media import duration as media_duration, filter_path, h264, h264_encoder, run, write_concat_list
from ..models import Asset, AssetKind, Overlay, Timeline, VideoClip
from ..store import ctx
from . import audio as audio_mod
from .captions import build_ass

RENDER_VERSION = 4  # súbelo al cambiar la cadena de render: invalida la caché de segmentos
# todos los segmentos idénticos en rango/matriz: si difieren, FFmpeg reconstruye el grafo final a mitad y pierde capas
COLOR = ["-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709"]
def _x264() -> list[str]:
    return [*h264(17), "-pix_fmt", "yuv420p", "-profile:v", "high"]


def _seg_key(clip: VideoClip, tl: Timeline) -> str:
    raw = json.dumps({"a": clip.asset_id, "in": clip.src_in, "d": round(clip.duration, 3), "sp": clip.speed, "fit": clip.fit, "g": clip.grade,
                      "z": [k.model_dump() for k in clip.zoom], "w": tl.width, "h": tl.height, "fps": tl.fps, "v": RENDER_VERSION},
                     sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:20]


def _zoom_expr(clip: VideoClip, fps: int) -> tuple[str, str, str] | None:
    """Expresiones (escala, cx, cy) en función de t=in/fps, lineales por tramos (punch-in / push-in)."""
    if not clip.zoom:
        return None
    ks = sorted(clip.zoom, key=lambda k: k.t)
    t = f"(in/{fps})"
    if len(ks) == 1:
        k = ks[0]
        return f"{k.scale}", f"{k.x}", f"{k.y}"

    def piecewise(attr: str) -> str:
        expr = f"{getattr(ks[-1], attr)}"
        for a, b in reversed(list(zip(ks[:-1], ks[1:]))):
            va, vb = getattr(a, attr), getattr(b, attr)
            span = max(b.t - a.t, 1e-3)
            seg = f"({va}+({vb}-{va})*({t}-{a.t})/{span})"
            expr = f"if(lt({t},{b.t}),{seg},{expr})"
        return f"if(lt({t},{ks[0].t}),{getattr(ks[0], attr)},{expr})"

    return piecewise("scale"), piecewise("x"), piecewise("y")


def _perspective_zoom(s: str, cx: str, cy: str) -> str:
    """Zoom subpíxel con `perspective` (sin el temblor de zoompan): ventana fuente centrada en (cx,cy)."""
    hw = f"(W/(2*({s})))"
    hh = f"(H/(2*({s})))"
    x0 = f"max(0,min(W-2*{hw},W*({cx})-{hw}))"
    y0 = f"max(0,min(H-2*{hh},H*({cy})-{hh}))"
    x1 = f"{x0}+2*{hw}"
    y1 = f"{y0}+2*{hh}"
    return (f"perspective=x0='{x0}':y0='{y0}':x1='{x1}':y1='{y0}':x2='{x0}':y2='{y1}':x3='{x1}':y3='{y1}'"
            f":interpolation=cubic:sense=source:eval=frame")


def render_segment(clip: VideoClip, tl: Timeline) -> Path:
    out_dir = ctx().work("segments")
    out = out_dir / f"seg_{_seg_key(clip, tl)}.mp4"
    if out.exists() and out.stat().st_size > 0:
        return out
    asset = ctx().db.get_asset(clip.asset_id)
    src = ctx().assets.abspath(asset)
    W, H, fps = tl.width, tl.height, tl.fps
    d = clip.duration
    t0 = time.time()
    if asset.kind == AssetKind.image:
        inp = ["-loop", 1, "-framerate", fps, "-t", f"{d + 0.5:.3f}", "-i", src]
        trim = ""
    else:
        src_d = asset.duration or media_duration(src)
        need = clip.src_in + d * clip.speed
        loop = ["-stream_loop", -1] if src_d and need > src_d + 0.05 and src_d < 1.0 else []
        inp = loop + ["-ss", f"{clip.src_in:.3f}", "-i", src]
        pad = max(0.0, need - (src_d or need)) if not loop else 0.0
        trim = f",tpad=stop_mode=clone:stop_duration={pad + 0.1:.3f}" if pad > 0 else ""
    sc = "flags=lanczos+accurate_rnd+full_chroma_int"
    if clip.fit == "cover":
        fit = f"scale={W}:{H}:force_original_aspect_ratio=increase:{sc},crop={W}:{H}"
    else:  # contain sobre su propia imagen desenfocada (nunca bandas negras)
        fit = (f"split[a][b];[b]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:2[bg];"
               f"[a]scale={W}:{H}:force_original_aspect_ratio=decrease:{sc}[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2")
    speed = f",setpts=PTS/{clip.speed}" if abs(clip.speed - 1.0) > 1e-3 else ""
    vf = f"{fit},setsar=1{speed}{trim},fps={fps}"
    z = _zoom_expr(clip, fps)
    if z:
        vf += "," + _perspective_zoom(*z)
    if clip.grade:
        vf += ",eq=" + ":".join(f"{k}={v}" for k, v in clip.grade.items() if k in ("saturation", "contrast", "brightness", "gamma"))
    up = (asset.height or H) < H * 0.9  # fuente de menor resolución (Omni 720p): realce suave de luma
    if up and asset.kind == AssetKind.video:
        vf += ",unsharp=5:5:0.45:5:5:0.0"
    # RGB (capturas, tarjetas) y YUV de rango completo → BT.709 rango limitado, igual para todos los segmentos
    vf += ",scale=out_color_matrix=bt709:out_range=tv,format=yuv420p"
    nframes = max(1, round(d * fps))  # número exacto de fotogramas: sin desfase acumulado con el audio continuo
    tmp = out.with_suffix(".part.mp4")
    run(inp + ["-filter_complex" if clip.fit != "cover" else "-vf", vf, "-frames:v", nframes, "-an", *_x264(), *COLOR,
               "-r", fps, "-g", fps, "-keyint_min", fps, "-sc_threshold", 0, "-video_track_timescale", 15360, tmp])
    os.replace(tmp, out)  # escritura atómica: un render interrumpido nunca queda en caché
    record_local("render", "ffmpeg-segment", time.time() - t0, note=clip.scene_id)
    return out


def _concat(segments: list[Path], out: Path) -> Path:
    lst = write_concat_list(segments, out.with_suffix(".txt"))
    run(["-f", "concat", "-safe", 0, "-i", lst, "-c", "copy", out])
    return out


def _overlay_inputs(tl: Timeline, work: Path, base_d: float) -> tuple[list[str], list[str], str]:
    """Construye entradas y filtros de overlays. Devuelve (inputs, filtros, etiqueta_salida).

    Dos trampas de FFmpeg 8.0 comprobadas al construir el motor:
      - si una entrada superpuesta acaba ANTES que el vídeo base, el planificador se interbloquea (0 % CPU);
      - repetir una imagen DENTRO del grafo (`loop=-1:1`) deja de emitir hacia el fotograma 183 (la etiqueta de IA
        desaparecía a los 6 s).
    Solución: toda capa dura AL MENOS lo que el base (bucle en el demuxer: `-loop 1 -t base_d` para imágenes,
    `-stream_loop -1 -t base_d` para vídeos), y la visibilidad la controla `enable`.
    """
    inputs: list[str] = []
    filters: list[str] = []
    cur = "base"
    n = 1  # 0 es el vídeo base
    fps = tl.fps
    for ov in tl.overlays:
        if not ov.asset_id or ov.start >= base_d - 0.05:
            continue
        end = min(ov.start + ov.duration, base_d)
        a = ctx().db.get_asset(ov.asset_id)
        p = ctx().assets.abspath(a)
        w = int(tl.width * ov.w) // 2 * 2
        if a.kind == AssetKind.image:
            inputs += ["-loop", 1, "-framerate", fps, "-t", f"{base_d:.3f}", "-i", str(p)]
            src = f"[{n}:v]scale={w}:-1,format=rgba"
        else:  # vídeo: bucle en el demuxer (tpad/trim dentro del grafo también se interbloquea en 8.0)
            inputs += ["-stream_loop", -1, "-t", f"{base_d:.3f}", "-i", str(p)]
            src = f"[{n}:v]scale={w}:-1,format=rgba,fps={fps},setpts=PTS-STARTPTS+{ov.start:.3f}/TB"
        fade = ""
        if ov.animation in ("pop", "fade"):
            # sin fundido de entrada en t=0: el fotograma 0 (la miniatura del feed) ya lleva el hook
            fin = f",fade=t=in:st={ov.start:.3f}:d=0.15:alpha=1" if ov.start > 0.05 else ""
            fade = f"{fin},fade=t=out:st={max(ov.start, end - 0.12):.3f}:d=0.12:alpha=1"
        lab = f"o{n}"
        filters.append(f"{src}{fade}[{lab}]")
        nxt = f"v{n}"
        filters.append(f"[{cur}][{lab}]overlay=x=(W*{ov.x})-w/2:y=(H*{ov.y})-h/2:"
                       f"enable='between(t,{ov.start:.3f},{end:.3f})':eof_action=pass[{nxt}]")
        cur = nxt
        n += 1
    return inputs, filters, cur


def render(tl: Timeline, out: Path, *, accent_hex: str | None = None, with_captions: bool = True) -> Path:
    """Render completo. Devuelve la ruta del MP4 final."""
    t0 = time.time()
    work = ctx().work("render", out.stem)
    if not tl.clips:
        raise ValueError("timeline vacía")
    clips = sorted(tl.clips, key=lambda c: c.start)
    tl.duration = max(c.start + c.duration for c in clips)
    segments = [render_segment(c, tl) for c in clips]
    base = _concat(segments, work / "base.mp4")
    base_d = media_duration(base) or tl.duration
    tl.duration = min(tl.duration, base_d)

    audio_wav = None
    if tl.audio:
        audio_wav = audio_mod.mix(tl, work / "mix.wav", phone_look=bool(tl.look.get("phone_audio", True)))

    inputs = ["-i", str(base)]
    ov_inputs, filters, cur = _overlay_inputs(tl, work, base_d)
    inputs += ov_inputs
    chain = []
    grain = float(tl.look.get("grain", 0) or 0)
    if grain > 0:
        chain.append(f"noise=alls={int(grain * 100)}:allf=t")
    if tl.look.get("lut"):
        chain.append(f"lut3d=file={filter_path(tl.look['lut'])}")
    if with_captions and tl.captions.enabled and tl.captions.words:
        ass = build_ass(tl.captions, tl.width, tl.height, work / "captions.ass", accent_hex)
        fontsdir = Path(__file__).resolve().parent.parent / "assets"
        chain.append(f"subtitles=filename={filter_path(ass)}:fontsdir={filter_path(fontsdir)}")
    chain.append("scale=out_color_matrix=bt709:out_range=tv,format=yuv420p")
    chain.append("setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709:range=tv")
    filters.append(f"[{cur}]{','.join(chain)}[vout]")
    filters.insert(0, "[0:v]null[base]")
    args = inputs[:]
    if audio_wav:
        args += ["-i", str(audio_wav)]
    args += ["-filter_complex", ";".join(filters), "-map", "[vout]"]
    if audio_wav:
        args += ["-map", f"{_audio_index(inputs)}:a", "-c:a", "aac", "-b:a", "192k"]
    final = h264(18, preset="medium") + (["-maxrate", "12M", "-bufsize", "24M"] if h264_encoder() == "libx264" else [])
    args += [*COLOR, *final, "-pix_fmt", "yuv420p",
             "-r", tl.fps, "-g", tl.fps * 2, "-movflags", "+faststart", "-t", f"{base_d:.3f}", str(out)]
    run(args)
    record_local("render", "ffmpeg-final", time.time() - t0, note=out.name)
    return out


def _audio_index(inputs: list[str]) -> int:
    """El WAV de audio va justo después de todas las entradas de vídeo/imagen."""
    return sum(1 for x in inputs if x == "-i")


def overlay_from_png(png: Path, *, start: float, duration: float, x: float = 0.5, y: float = 0.2, w: float = 0.8,
                     kind: str = "image", animation: str = "pop") -> Overlay:
    a: Asset = ctx().assets.ingest(png, source="render:graphic")
    return Overlay(kind=kind, asset_id=a.id, start=start, duration=duration, x=x, y=y, w=w, animation=animation)  # type: ignore[arg-type]
