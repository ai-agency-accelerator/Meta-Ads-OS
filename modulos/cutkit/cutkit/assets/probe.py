"""`probe(path)`: medidas de un medio (ancho, alto, duración, fps, audio) con ffprobe.

SVG: ffprobe no lo lee; se usa `svg_dimensiones` (atributos `viewBox`, `width` y `height` de la raíz, con
`xml.etree`). Imágenes que ffprobe no entiende: Pillow.
"""

from __future__ import annotations

import io
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from fractions import Fraction
from pathlib import Path
from typing import Any

IMAGE_EXT = {"png", "jpg", "jpeg", "webp", "gif", "bmp", "tif", "tiff", "avif", "heic"}
VIDEO_EXT = {"mp4", "mov", "m4v", "webm", "mkv", "avi"}
AUDIO_EXT = {"wav", "mp3", "m4a", "aac", "flac", "ogg", "opus", "aiff"}

# Unidades absolutas de CSS en px (96 px = 1 in). Las relativas (%, em…) no dan un tamaño propio.
_UNIDADES = {"": 1.0, "px": 1.0, "pt": 96 / 72, "pc": 16.0, "in": 96.0, "cm": 96 / 2.54, "mm": 96 / 25.4,
             "q": 96 / 101.6}
_LONGITUD = re.compile(r"^\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\s*([a-zA-Z%]*)\s*$")
_NUMERO = re.compile(r"[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?")


def media_type_of(path: Path | str) -> str:
    """Tipo de `Asset.kind` según la extensión: image | video | svg | audio | html."""
    ext = Path(path).suffix.lstrip(".").lower()
    if ext == "svg":
        return "svg"
    if ext in IMAGE_EXT:
        return "image"
    if ext in VIDEO_EXT:
        return "video"
    if ext in AUDIO_EXT:
        return "audio"
    if ext in ("html", "htm"):
        return "html"
    return "image"


def _longitud(valor: str | None) -> float | None:
    """`"120"`, `"120px"`, `"2.5in"`… → px. None si falta, es relativa (`%`, `em`) o no es positiva."""
    if not valor:
        return None
    m = _LONGITUD.match(valor)
    if not m or m.group(2).lower() not in _UNIDADES:
        return None
    px = float(m.group(1)) * _UNIDADES[m.group(2).lower()]
    return px if px > 0 else None


def svg_dimensiones(svg: Path | str | bytes) -> tuple[float, float, float, float]:
    """(x, y, ancho, alto) del `viewBox` de la raíz; si no tiene, (0, 0, width, height).

    `svg` es una ruta, o el contenido en texto o bytes. Solo lee la etiqueta raíz (no recorre el dibujo).
    Lanza `ValueError` si no es un SVG o no declara un tamaño utilizable.
    """
    if isinstance(svg, Path) or (isinstance(svg, str) and not svg.lstrip().startswith("<")):
        datos = Path(svg).read_bytes()
    else:
        datos = svg.encode("utf-8") if isinstance(svg, str) else svg
    try:
        _, raiz = next(ET.iterparse(io.BytesIO(datos), events=("start",)))
    except (ET.ParseError, StopIteration) as exc:
        raise ValueError(f"no es un SVG legible: {exc}") from exc
    if raiz.tag.rsplit("}", 1)[-1].lower() != "svg":
        raise ValueError(f"la raíz es <{raiz.tag}>, no <svg>")
    vb = raiz.get("viewBox") or raiz.get("viewbox")
    if vb:
        nums = [float(n) for n in _NUMERO.findall(vb)]
        if len(nums) == 4 and nums[2] > 0 and nums[3] > 0:
            return nums[0], nums[1], nums[2], nums[3]
    w, h = _longitud(raiz.get("width")), _longitud(raiz.get("height"))
    if w and h:
        return 0.0, 0.0, w, h
    raise ValueError("SVG sin viewBox ni width/height absolutos")


def _fps(rate: str | None) -> float | None:
    try:
        f = Fraction(rate) if rate else None
        return round(float(f), 3) if f else None
    except (ValueError, ZeroDivisionError):
        return None


def probe(path: Path | str) -> dict[str, Any]:
    """{width, height, duration, fps, codec, has_audio, format, bytes} (None donde no aplique)."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)
    info: dict[str, Any] = {"width": None, "height": None, "duration": None, "fps": None, "codec": None,
                            "has_audio": False, "format": None, "bytes": p.stat().st_size}
    mtype = media_type_of(p)
    if mtype == "svg":
        info.update(format="svg", codec="svg")
        try:
            _, _, w, h = svg_dimensiones(p)
            info.update(width=round(w), height=round(h))
        except (ValueError, OSError):   # SVG sin tamaño declarado: sin medidas
            pass
        return info
    ffprobe = shutil.which("ffprobe")
    if ffprobe is None and mtype in ("video", "audio"):
        from cutkit.sistema import requiere

        requiere("ffprobe")              # lanza FaltaHerramienta con cómo instalarlo en tu sistema
    data: dict[str, Any] = {}
    if ffprobe:
        try:
            out = subprocess.run(
                [ffprobe, "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(p)],
                capture_output=True, text=True, timeout=60)
            data = json.loads(out.stdout or "{}")
        except Exception:  # noqa: BLE001 - salida rara: las imágenes se miden con Pillow abajo
            data = {}
    streams = data.get("streams") or []
    v = next((s for s in streams if s.get("codec_type") == "video"), None)
    a = next((s for s in streams if s.get("codec_type") == "audio"), None)
    fmt = data.get("format") or {}
    if v:
        info.update(width=v.get("width"), height=v.get("height"), codec=v.get("codec_name"))
        # La rotación (vídeos de móvil) intercambia ancho y alto a efectos de composición.
        rot = 0
        for sd in v.get("side_data_list") or []:
            if "rotation" in sd:
                rot = int(sd["rotation"])
        if abs(rot) in (90, 270) and info["width"] and info["height"]:
            info["width"], info["height"] = info["height"], info["width"]
    info["has_audio"] = a is not None
    info["format"] = fmt.get("format_name")
    if mtype in ("video", "audio"):
        dur = fmt.get("duration") or (v or a or {}).get("duration")
        info["duration"] = round(float(dur), 3) if dur not in (None, "N/A") else None
        if v:
            info["fps"] = _fps(v.get("avg_frame_rate")) or _fps(v.get("r_frame_rate"))
    if mtype == "image" and not info["width"]:
        try:
            from PIL import Image

            with Image.open(p) as im:
                info.update(width=im.width, height=im.height, format=(im.format or "").lower())
        except Exception:  # noqa: BLE001
            pass
    return info


__all__ = ["probe", "media_type_of", "svg_dimensiones"]
