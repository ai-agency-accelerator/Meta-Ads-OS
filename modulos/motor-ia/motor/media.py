"""Utilidades de medios sobre FFmpeg/ffprobe (deterministas y baratas)."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
import wave
from functools import lru_cache
from pathlib import Path
from typing import Any, Sequence

import numpy as np

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"

# Cómo instalar cada herramienta del sistema en cada plataforma (se muestra en `motor setup` y en los errores).
INSTALL_HINTS = {
    "ffmpeg": {"darwin": "brew install ffmpeg", "linux": "sudo apt install ffmpeg  (o el gestor de tu distribución)",
               "win32": "winget install Gyan.FFmpeg  (y abre una terminal nueva)"},
    "tesseract": {"darwin": "brew install tesseract", "linux": "sudo apt install tesseract-ocr",
                  "win32": "winget install UB-Mannheim.TesseractOCR  (y añade su carpeta al PATH)"},
}


def install_hint(tool: str) -> str:
    hints = INSTALL_HINTS.get("ffmpeg" if tool == "ffprobe" else tool, {})
    plat = "darwin" if sys.platform == "darwin" else "win32" if sys.platform.startswith("win") else "linux"
    return hints.get(plat, f"instala {tool} y asegúrate de que está en el PATH")


def tool_status() -> dict[str, bool]:
    return {t: bool(shutil.which(t)) for t in ("ffmpeg", "ffprobe", "tesseract")}


class FFmpegError(RuntimeError):
    pass


def _exe(name: str, fallback: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    if fallback != name and Path(fallback).exists():
        return fallback
    raise FFmpegError(f"no encuentro `{name}` en el PATH. Arreglo: {install_hint(name)}")


def filter_path(path: Path | str) -> str:
    """Ruta escapada para usarla como valor dentro de un filtro de FFmpeg (`fontfile=`, `subtitles=`, `lut3d=`).

    FFmpeg analiza el grafo en dos niveles: el del grafo (comillas, «\\», «[»,«]», «,», «;») y el de las opciones del
    filtro («:» separa opciones). Una ruta de Windows («C:\\…») o con comillas rompería cualquiera de los dos. Se usa
    la forma con «/» (FFmpeg la acepta en todos los sistemas) y se escapa para los dos niveles, sin comillas.
    """
    s = Path(path).as_posix() if not isinstance(path, str) else path.replace("\\", "/")
    s = s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")  # nivel de opciones
    return re.sub(r"([\\'\[\],;])", r"\\\1", s)  # nivel de grafo


def write_concat_list(paths: Sequence[Path], lst: Path) -> Path:
    """Lista para el demuxer `concat` válida en Mac, Linux y Windows (rutas con «/» y comillas escapadas)."""
    lines = []
    for p in paths:
        q = Path(p).resolve().as_posix().replace("'", "'\\''")
        lines.append(f"file '{q}'\n")
    lst.write_text("".join(lines), encoding="utf-8")
    return lst


@lru_cache(maxsize=1)
def _encoders() -> str:
    try:
        p = subprocess.run([_exe("ffmpeg", FFMPEG), "-hide_banner", "-encoders"], capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=30, stdin=subprocess.DEVNULL)
        return p.stdout
    except Exception:  # noqa: BLE001
        return ""


def h264_encoder() -> str:
    """Codificador H.264: libx264 por defecto (el mismo resultado en todos los sistemas). `MOTOR_H264_ENCODER` pide otro
    (p. ej. `h264_videotoolbox` en Mac) y solo se usa si esta compilación de FFmpeg lo trae."""
    enc = _encoders()
    wanted = (os.environ.get("MOTOR_H264_ENCODER") or "").strip()
    if wanted and re.search(rf"\b{re.escape(wanted)}\b", enc):
        return wanted
    if not enc or re.search(r"\blibx264\b", enc):
        return "libx264"
    for alt in ("h264_videotoolbox", "h264_mf", "libopenh264", "h264_nvenc", "h264_qsv", "h264_vaapi"):
        if re.search(rf"\b{alt}\b", enc):
            return alt
    return "libx264"


def h264(crf: int | str = 18, preset: str = "veryfast") -> list[str]:
    """Argumentos de vídeo H.264 equivalentes en calidad con el codificador disponible."""
    enc = h264_encoder()
    if enc == "libx264":
        return ["-c:v", "libx264", "-preset", preset, "-crf", str(crf)]
    rate = {True: "14M", False: "4M"}[int(crf) <= 20]
    return ["-c:v", enc, "-b:v", rate, "-maxrate", rate]


def run(args: Sequence[str], *, timeout: float = 900, quiet: bool = True) -> tuple[str, float]:
    """Ejecuta ffmpeg. Devuelve (stderr, segundos)."""
    cmd = [_exe("ffmpeg", FFMPEG), "-hide_banner", "-nostdin", "-y"] + (["-loglevel", "error"] if quiet else []) + list(map(str, args))
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, stdin=subprocess.DEVNULL)
    dt = time.time() - t0
    if p.returncode != 0:
        raise FFmpegError(f"ffmpeg falló ({p.returncode}): {p.stderr[-2000:]}\nCMD: {' '.join(cmd)[:1500]}")
    return p.stderr, dt


def run_capture(args: Sequence[str], timeout: float = 900) -> str:
    """Ejecuta ffmpeg con loglevel info y devuelve stderr (para filtros de análisis)."""
    cmd = [_exe("ffmpeg", FFMPEG), "-hide_banner", "-nostdin", "-nostats"] + list(map(str, args))
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, stdin=subprocess.DEVNULL)
    return p.stderr


def probe(path: Path | str) -> dict[str, Any]:
    p = subprocess.run(
        [_exe("ffprobe", FFPROBE), "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60, stdin=subprocess.DEVNULL,
    )
    try:
        return json.loads(p.stdout or "{}")
    except json.JSONDecodeError:
        return {}


def duration(path: Path | str) -> float:
    info = probe(path)
    try:
        return float(info["format"]["duration"])
    except Exception:
        for st in info.get("streams", []):
            if st.get("duration"):
                return float(st["duration"])
    return 0.0


def has_audio(path: Path | str) -> bool:
    return any(s.get("codec_type") == "audio" for s in probe(path).get("streams", []))


def video_size(path: Path | str) -> tuple[int, int]:
    for s in probe(path).get("streams", []):
        if s.get("codec_type") == "video":
            return int(s["width"]), int(s["height"])
    return (0, 0)


def pcm_to_wav(pcm: bytes, path: Path, rate: int = 24000, channels: int = 1, width: int = 2) -> Path:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(width)
        w.setframerate(rate)
        w.writeframes(pcm)
    return path


def to_wav(src: Path, dst: Path, rate: int = 48000, mono: bool = True) -> Path:
    run(["-i", src, "-ac", 1 if mono else 2, "-ar", rate, "-c:a", "pcm_s16le", dst])
    return dst


def read_wav_mono(path: Path, rate: int = 16000) -> np.ndarray:
    """Devuelve float32 [-1,1] mono al sample rate pedido (vacío si el fichero no tiene audio)."""
    import tempfile

    if not has_audio(path):
        return np.zeros(0, dtype=np.float32)
    tmp = Path(tempfile.mkdtemp(prefix="motor_pcm_")) / f"a.{rate}.raw"
    run(["-i", path, "-ac", 1, "-ar", rate, "-f", "s16le", tmp])
    data = np.frombuffer(tmp.read_bytes(), dtype=np.int16).astype(np.float32) / 32768.0
    tmp.unlink(missing_ok=True)
    return data


def extract_frames(video: Path, out_dir: Path, fps: float = 2.0, width: int = 512, *, start: float = 0.0,
                   duration: float | None = None) -> list[tuple[float, Path]]:
    """Extrae fotogramas a `fps` (opcionalmente solo el tramo [start, start+duration]) y devuelve [(t, path)]."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in out_dir.glob("f_*.jpg"):
        f.unlink()
    if duration and duration * fps < 1:
        fps = 1.2 / max(duration, 0.05)  # ventana corta: al menos un fotograma
    win = (["-ss", f"{start:.3f}"] if start > 0 else []) + (["-t", f"{duration:.3f}"] if duration else [])
    try:
        run(win + ["-i", video, "-vf", f"fps={fps},scale={width}:-2:out_range=pc,format=yuvj420p", "-q:v", 3,
                   out_dir / "f_%05d.jpg"])
    except FFmpegError:
        return []  # tramo vacío o fuera del clip: sin fotogramas (el llamante lo trata como «sin datos»)
    frames = sorted(out_dir.glob("f_*.jpg"))
    return [(start + (i + 0.5) / fps, p) for i, p in enumerate(frames)]


def frame_at(video: Path, t: float, out: Path, width: int = 720) -> Path:
    vf = f"scale={width}:-2" + (":out_range=pc,format=yuvj420p" if str(out).lower().endswith((".jpg", ".jpeg")) else "")
    run(["-ss", f"{max(t, 0):.3f}", "-i", video, "-frames:v", 1, "-vf", vf, "-q:v", 2, out])
    return out


def last_frame(video: Path, out: Path, width: int = 1080) -> Path:
    d = duration(video)
    return frame_at(video, max(d - 0.08, 0), out, width)


def silence(path: Path, seconds: float, rate: int = 48000) -> Path:
    run(["-f", "lavfi", "-i", f"anullsrc=r={rate}:cl=mono", "-t", f"{seconds:.3f}", "-c:a", "pcm_s16le", path])
    return path


def loudness(path: Path) -> dict[str, float]:
    """Integrated loudness (LUFS) y true peak con ebur128."""
    err = run_capture(["-i", str(path), "-filter_complex", "ebur128=peak=true", "-f", "null", "-"])
    out: dict[str, float] = {}
    tail = err[err.rfind("Summary:"):] if "Summary:" in err else err
    for line in tail.splitlines():
        line = line.strip()
        if line.startswith("I:"):
            try:
                out["lufs"] = float(line.split()[1])
            except Exception:
                pass
        if line.startswith("Peak:"):
            try:
                out["true_peak"] = float(line.split()[1])
            except Exception:
                pass
    return out
