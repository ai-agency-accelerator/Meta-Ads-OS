"""Ingesta: sondea las fuentes y crea intermedios normalizados (vídeo CFR 30 fps sin audio + voz WAV 48 kHz).

Comprueba que hay audio de verdad (un bruto grabado con una cámara virtual puede llegar mudo) y normaliza
resolución, fps y color.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from . import sistema
from .paths import run_dir
from .spec import FPS_SHORTS, Source


def sh(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def probe(path: str | Path) -> dict:
    j = json.loads(sh(["ffprobe", "-v", "error", "-show_entries",
                       "format=duration:stream=codec_type,width,height,r_frame_rate,color_transfer,sample_rate",
                       "-of", "json", str(path)]).stdout)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), None)
    fps = None
    if v:
        n, d = v["r_frame_rate"].split("/")
        fps = float(n) / float(d)
    return {"duration": float(j["format"]["duration"]), "width": v and v["width"], "height": v and v["height"],
            "fps": fps, "transfer": v and v.get("color_transfer"), "has_audio": a is not None,
            "sample_rate": a and int(a["sample_rate"])}


def audio_level_db(path: str | Path) -> float:
    """Volumen medio en dBFS; ~-91 significa pista muda."""
    p = subprocess.run(["ffmpeg", "-v", "info", "-i", str(path), "-af", "volumedetect", "-vn", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"mean_volume:\s*(-?[\d.]+) dB", p.stderr)
    return float(m.group(1)) if m else -120.0


def ingest_source(slug: str, sid: str, path: str | Path, vertical: bool = True, force: bool = False) -> Source:
    rd = run_dir(slug)
    path = Path(path).resolve()
    info = probe(path)
    if not info["has_audio"]:
        raise RuntimeError(f"{path.name}: no tiene pista de audio")
    lvl = audio_level_db(path)
    if lvl < -60:
        raise RuntimeError(f"{path.name}: el audio está mudo (volumen medio {lvl:.1f} dBFS). Revisa el micrófono.")
    # intermedio con margen sobre el lienzo 1080×1920: los punch-in y reencuadres (≤×1,33) no amplían por encima de la fuente
    W, H = (1440, 2560) if vertical else (2560, 1440)
    mez = rd / "media" / f"src_{sid}.mp4"
    wav = rd / "media" / f"src_{sid}.wav"
    if force or not mez.exists():
        vf = [f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos", f"crop={W}:{H}", f"fps={FPS_SHORTS}"]
        if (info["transfer"] or "") in ("arib-std-b67", "smpte2084"):   # HDR del iPhone → SDR (una sola vez)
            vf.insert(0, "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
                         "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
        sh(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-vf", ",".join(vf), "-an",
            *sistema.codec_video("intermedio", FPS_SHORTS), "-color_primaries", "bt709", "-color_trc", "bt709",
            "-colorspace", "bt709", str(mez)])
    if force or not wav.exists():
        sh(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-vn", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s24le", str(wav)])
    mi = probe(mez)
    return Source(id=sid, path=str(path), mezzanine=str(mez), audio=str(wav), duration=min(mi["duration"], info["duration"]),
                  width=mi["width"], height=mi["height"], fps=mi["fps"])


def copy_into_run(slug: str, path: str | Path) -> Path:
    rd = run_dir(slug)
    dst = rd / "media" / Path(path).name
    if not dst.exists():
        try:
            dst.hardlink_to(Path(path).resolve())
        except OSError:
            shutil.copy2(path, dst)
    return dst
