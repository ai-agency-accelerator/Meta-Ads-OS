"""Subtítulos nativos de TikTok/Reels en ASS (libass): palabra a palabra con la palabra activa resaltada.

Reglas: ≤4 palabras por bloque (corte en puntuación), 1–2 líneas, dentro de la zona segura
(centro horizontal, ~y=0.62–0.70 del alto), fuente Montserrat ExtraBold (OFL) con contorno.
"""

from __future__ import annotations

import re
from pathlib import Path

from ..config import PACKAGE_ROOT
from ..models import CaptionTrack, Word

FONT_DIR = PACKAGE_ROOT / "assets"
FONT_NAME = "Montserrat ExtraBold"

STYLES = {
    # nombre: (tamaño relativo al ancho, color texto, color activo, contorno, sombra, mayúsculas)
    "tiktok_bold": (0.066, "&H00FFFFFF", "&H0000E5FF", 7, 0, True),
    "clean": (0.072, "&H00FFFFFF", "&H00FFFFFF", 6, 1, False),  # +30 %: legible en móvil sin sonido
    "brand": (0.062, "&H00FFFFFF", None, 6, 0, False),
}


def _ass_color(hex_rgb: str) -> str:
    h = hex_rgb.lstrip("#")
    if len(h) != 6:
        return "&H0000E5FF"
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H00{b}{g}{r}".upper()


def _ts(t: float) -> str:
    t = max(0.0, t)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def chunk_words(words: list[Word], max_words: int = 4, max_gap: float = 0.6) -> list[list[Word]]:
    chunks: list[list[Word]] = []
    cur: list[Word] = []
    for w in words:
        if cur and (len(cur) >= max_words or w.start - cur[-1].end > max_gap):
            chunks.append(cur)
            cur = []
        cur.append(w)
        if re.search(r"[.!?…,;:]$", w.text):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def _clean(text: str, upper: bool) -> str:
    t = text.replace("{", "(").replace("}", ")").replace("\\", "/")
    t = re.sub(r"[,;:]$", "", t)
    return t.upper() if upper else t


def build_ass(track: CaptionTrack, width: int, height: int, out: Path, accent_hex: str | None = None) -> Path:
    size_rel, primary, active, outline, shadow, upper = STYLES.get(track.style, STYLES["tiktok_bold"])
    if track.style == "brand" or active is None:
        active = _ass_color(accent_hex or "#FFE500")
    fontsize = int(width * size_rel)
    margin_v = int(height * (1 - track.position_y))
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{FONT_NAME},{fontsize},{primary},{primary},&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,{outline},{shadow},2,{int(width*0.08)},{int(width*0.08)},{margin_v},1
Style: Box,{FONT_NAME},{fontsize},{primary},{primary},&H40141414,&H40141414,-1,0,0,0,100,100,0,0,3,{max(8, outline + 6)},0,2,{int(width*0.08)},{int(width*0.08)},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    chunks = chunk_words(track.words, track.max_words_per_line)
    for ci, chunk in enumerate(chunks):
        texts = [_clean(w.text, upper) for w in chunk]
        nxt = chunks[ci + 1][0].start if ci + 1 < len(chunks) else None
        # el estilo se decide por BLOQUE (la caja no aparece y desaparece a mitad de frase)
        c0, c1 = chunk[0].start, chunk[-1].end
        boxed = any(a <= (c0 + c1) / 2 <= b for a, b in track.boxed_spans)
        style = "Box" if boxed else "Cap"
        grow = "" if boxed else "\\fscx106\\fscy106"  # escalar dentro de la caja deja una costura doble
        for i, w in enumerate(chunk):
            start = w.start
            end = chunk[i + 1].start if i + 1 < len(chunk) else max(w.end, w.start + 0.25)
            if nxt is not None:
                end = min(end, nxt)  # nunca dos bloques en pantalla a la vez
            if end <= start:
                continue
            parts = []
            for j, t in enumerate(texts):
                if j == i:
                    parts.append(f"{{\\c{active}{grow}}}{t}{{\\c{primary}\\fscx100\\fscy100}}")
                else:
                    parts.append(t)
            pop = ""  # sin fundido de entrada: se veía como un subtítulo «fantasma» semitransparente
            if any(a <= start < b for a, b in track.hidden_spans):
                continue
            lines.append(f"Dialogue: 0,{_ts(start)},{_ts(end)},{style},,0,0,0,,{pop}{' '.join(parts)}\n")
    out.write_text("".join(lines), encoding="utf-8")
    return out


def shift_words(words: list[Word], offset: float) -> list[Word]:
    return [Word(text=w.text, start=w.start + offset, end=w.end + offset) for w in words]
