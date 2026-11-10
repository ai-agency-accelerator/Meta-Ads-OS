"""Utilidades de sistema multiplataforma (Mac, Linux y Windows con Git Bash).

- `requiere(binario)`: comprueba FFmpeg, Node… y explica cómo instalarlos en cada sistema.
- `codec_video(calidad)`: argumentos de codificación H.264. Por defecto `libx264` (igual en todos los sistemas);
  en Mac usa VideoToolbox (hardware) solo para intermedios si está disponible o si `CK_CODIFICADOR=videotoolbox`.
- `npx()`: el ejecutable de npx (`npx.cmd` en Windows).
"""
from __future__ import annotations

import functools
import os
import shutil
import subprocess
import sys

ARREGLOS = {
    "ffmpeg": {"darwin": "brew install ffmpeg", "linux": "sudo apt install ffmpeg (o el gestor de tu distribución)",
               "win32": "winget install Gyan.FFmpeg (y reabre la terminal)"},
    "ffprobe": {"darwin": "brew install ffmpeg", "linux": "sudo apt install ffmpeg",
                "win32": "winget install Gyan.FFmpeg"},
    "node": {"darwin": "brew install node", "linux": "instala Node 20+ desde nodejs.org o con tu gestor",
             "win32": "winget install OpenJS.NodeJS.LTS"},
    "npx": {"darwin": "brew install node", "linux": "instala Node 20+ (trae npx)", "win32": "winget install OpenJS.NodeJS.LTS"},
    "whisper-cli": {"darwin": "brew install whisper-cpp", "linux": "compila whisper.cpp (github.com/ggml-org/whisper.cpp)",
                    "win32": "descarga el binario de whisper.cpp de su página de versiones y ponlo en el PATH"},
    "tesseract": {"darwin": "brew install tesseract tesseract-lang", "linux": "sudo apt install tesseract-ocr tesseract-ocr-spa",
                  "win32": "winget install UB-Mannheim.TesseractOCR"},
}


class FaltaHerramienta(RuntimeError):
    """Falta un programa del sistema; el mensaje dice cómo instalarlo."""


def plataforma() -> str:
    return "win32" if sys.platform.startswith("win") else ("darwin" if sys.platform == "darwin" else "linux")


def arreglo(binario: str) -> str:
    return ARREGLOS.get(binario, {}).get(plataforma(), f"instala {binario} y añádelo al PATH")


def requiere(binario: str) -> str:
    ruta = shutil.which(binario)
    if not ruta:
        raise FaltaHerramienta(f"Falta «{binario}». Instálalo: {arreglo(binario)}")
    return ruta


def npx() -> str:
    return requiere("npx.cmd" if plataforma() == "win32" and shutil.which("npx.cmd") else "npx")


@functools.lru_cache(maxsize=1)
def _encoders() -> str:
    try:
        return subprocess.run([requiere("ffmpeg"), "-hide_banner", "-encoders"], capture_output=True, text=True,
                              timeout=30).stdout
    except Exception:  # noqa: BLE001
        return ""


def videotoolbox() -> bool:
    pref = os.environ.get("CK_CODIFICADOR", "auto").lower()
    if pref == "libx264":
        return False
    return plataforma() == "darwin" and "h264_videotoolbox" in _encoders()


def codec_video(calidad: str = "intermedio", fps: int = 30) -> list[str]:
    """Argumentos de vídeo H.264 en yuv420p.

    - `intermedio`: alta calidad para trabajar (VideoToolbox 20 Mb/s en Mac si existe; si no, libx264 CRF 14).
    - `master`: entrega (libx264 CRF 18, preset medium; igual en todos los sistemas).
    - `proxy`: vista previa ligera.
    """
    gop = ["-g", str(fps)]
    if calidad == "intermedio" and videotoolbox():
        return ["-c:v", "h264_videotoolbox", "-b:v", "20M", *gop, "-pix_fmt", "yuv420p"]
    if calidad == "proxy":
        if videotoolbox():
            return ["-c:v", "h264_videotoolbox", "-b:v", "3M", "-pix_fmt", "yuv420p"]
        return ["-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-pix_fmt", "yuv420p"]
    crf = "14" if calidad == "intermedio" else "18"
    preset = "veryfast" if calidad == "intermedio" else "medium"
    return ["-c:v", "libx264", "-preset", preset, "-crf", crf, *gop, "-pix_fmt", "yuv420p"]
