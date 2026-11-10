"""Gráficos deterministas con Pillow: textos tipo sticker, tarjetas CTA, marco de móvil y etiqueta IA.

Nada de texto generado por IA: todo el texto en pantalla se compone aquí con fuentes reales.
"""

from __future__ import annotations

import re
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from ..config import PACKAGE_ROOT
from ..media import h264, run

ASSETS = PACKAGE_ROOT / "assets"


def font(weight: str = "ExtraBold", size: int = 64, path: str | None = None) -> ImageFont.FreeTypeFont:
    p = Path(path) if path else ASSETS / f"Montserrat-{weight}.ttf"
    if not p.exists():
        p = ASSETS / "Montserrat-Bold.ttf"
    return ImageFont.truetype(str(p), size)


def hex_rgb(h: str, alpha: int = 255) -> tuple[int, int, int, int]:
    h = h.lstrip("#")
    if len(h) != 6:
        return (17, 17, 17, alpha)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


_EMOJI = re.compile("[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0000FE0F\U0000200D\U0001F1E6-\U0001F1FF]+")


def strip_unsupported(text: str) -> str:
    """Montserrat no tiene emojis: se eliminan para no dibujar cuadrados vacíos."""
    return re.sub(r"\s{2,}", " ", _EMOJI.sub("", text)).strip()


def text_sticker(text: str, out: Path, *, width: int = 1080, max_chars: int = 22, bg: str = "#FFFFFF", fg: str = "#111111",
                 size: int = 58, weight: str = "ExtraBold", font_path: str | None = None, pad: int = 26, radius: int = 22) -> Path:
    """Caja redondeada con texto centrado (estilo texto nativo de TikTok)."""
    text = strip_unsupported(text)
    f = font(weight, size, font_path)
    lines = textwrap.wrap(text, width=max_chars) or [text]
    draw_tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    widths = [draw_tmp.textbbox((0, 0), ln, font=f)[2] for ln in lines]
    lh = int(size * 1.22)
    w = min(width - 80, max(widths) + pad * 2)
    h = lh * len(lines) + pad * 2 - int(size * 0.2)
    img = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((10, 14, w + 10, h + 14), radius=radius, fill=(0, 0, 0, 70))
    img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((10, 10, w + 10, h + 10), radius=radius, fill=hex_rgb(bg))
    y = 10 + pad - int(size * 0.12)
    for ln, lw in zip(lines, widths):
        d.text((10 + (w - lw) // 2, y), ln, font=f, fill=hex_rgb(fg))
        y += lh
    img.save(out)
    return out


def cta_card(out_png: Path, *, headline: str, sub: str = "", button: str = "", logo: Path | None = None, width: int = 1080,
             height: int = 1920, bg: str = "#111111", accent: str = "#FF3B30", fg: str = "#FFFFFF", product_img: Path | None = None,
             font_path: str | None = None) -> Path:
    img = Image.new("RGBA", (width, height), hex_rgb(bg))
    d = ImageDraw.Draw(img)
    y = int(height * 0.18)
    if logo and logo.exists():
        lg = Image.open(logo).convert("RGBA")
        lg.thumbnail((int(width * 0.42), int(height * 0.10)))
        img.alpha_composite(lg, ((width - lg.width) // 2, y))
        y += lg.height + int(height * 0.04)
    if product_img and product_img.exists():
        pi = Image.open(product_img).convert("RGBA")
        pi.thumbnail((int(width * 0.62), int(height * 0.34)))
        img.alpha_composite(pi, ((width - pi.width) // 2, y))
        y += pi.height + int(height * 0.04)
    fh = font("ExtraBold", int(width * 0.075), font_path)
    for ln in textwrap.wrap(headline, 18):
        lw = d.textbbox((0, 0), ln, font=fh)[2]
        d.text(((width - lw) // 2, y), ln, font=fh, fill=hex_rgb(fg))
        y += int(width * 0.09)
    if sub:
        fs = font("SemiBold", int(width * 0.042), font_path)
        y += int(height * 0.01)
        for ln in textwrap.wrap(sub, 32):
            lw = d.textbbox((0, 0), ln, font=fs)[2]
            d.text(((width - lw) // 2, y), ln, font=fs, fill=hex_rgb(fg, 220))
            y += int(width * 0.055)
    if button:
        fb = font("ExtraBold", int(width * 0.05), font_path)
        bw = d.textbbox((0, 0), button, font=fb)[2] + 100
        bh = int(width * 0.11)
        bx, by = (width - bw) // 2, max(y + int(height * 0.04), int(height * 0.66))
        d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=bh // 2, fill=hex_rgb(accent))
        tw = d.textbbox((0, 0), button, font=fb)[2]
        d.text((bx + (bw - tw) // 2, by + int(bh * 0.2)), button, font=fb, fill=(255, 255, 255, 255))
    img.convert("RGB").save(out_png)
    return out_png


def still_to_clip(png: Path, out_mp4: Path, duration: float, *, width: int = 1080, height: int = 1920, fps: int = 30,
                  zoom: float = 0.04) -> Path:
    """Imagen fija → clip con micro-zoom (evita que se vea congelada)."""
    frames = int(duration * fps)
    run([
        "-loop", 1, "-i", png, "-t", f"{duration:.3f}",
        "-vf", (
            f"scale={width*2}:{height*2},zoompan=z='1+{zoom}*on/{max(frames,1)}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={frames}:s={width}x{height}:fps={fps},format=yuv420p"
        ),
        *h264(18), "-r", fps, "-g", fps, "-an", out_mp4,
    ])
    return out_mp4


def phone_frame(out_png: Path, *, screen_w: int = 600, screen_h: int = 1300, bezel: int = 26, radius: int = 78,
                color: str = "#0B0B0C") -> tuple[Path, tuple[int, int, int, int]]:
    """Marco de móvil genérico (sin marcas) con pantalla transparente. Devuelve (png, rect_pantalla)."""
    W, H = screen_w + bezel * 2, screen_h + bezel * 2
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, W - 1, H - 1), radius=radius, fill=hex_rgb(color))
    d.rounded_rectangle((3, 3, W - 4, H - 4), radius=radius - 3, outline=(60, 60, 64, 255), width=3)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle((bezel, bezel, bezel + screen_w, bezel + screen_h), radius=radius - bezel, fill=255)
    alpha = img.getchannel("A")
    alpha.paste(0, mask=mask)
    img.putalpha(alpha)
    # isla dinámica (dentro de la barra de estado: no tapa la cabecera de la app)
    iw, ih = int(screen_w * 0.30), int(screen_w * 0.075)
    d2 = ImageDraw.Draw(img)
    d2.rounded_rectangle(((W - iw) // 2, bezel + 14, (W + iw) // 2, bezel + 14 + ih), radius=ih // 2, fill=(0, 0, 0, 255))
    # barra de estado: hora a la izquierda, cobertura y batería a la derecha
    sb = status_bar_height(screen_h)
    fy = bezel + (sb - 22) // 2
    d2.text((bezel + 44, fy - 4), "9:41", font=font("SemiBold", 24), fill=(20, 20, 20, 255))
    bx0 = bezel + screen_w - 44 - 40
    d2.rounded_rectangle((bx0, fy + 2, bx0 + 36, fy + 20), radius=5, outline=(20, 20, 20, 255), width=2)
    d2.rounded_rectangle((bx0 + 4, fy + 6, bx0 + 26, fy + 16), radius=2, fill=(20, 20, 20, 255))
    for k in range(4):
        h_ = 6 + k * 4
        d2.rectangle((bx0 - 52 + k * 8, fy + 20 - h_, bx0 - 47 + k * 8, fy + 20), fill=(20, 20, 20, 255))
    img.save(out_png)
    return out_png, (bezel, bezel, screen_w, screen_h)


def status_bar_height(screen_h: int) -> int:
    return int(screen_h * 0.055)


def ai_label(out_png: Path, text: str = "Contenido generado con IA", size: int = 30) -> Path:
    f = font("SemiBold", size)
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    w = d0.textbbox((0, 0), text, font=f)[2] + 36
    h = int(size * 1.7)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # opaca: tiene que leerse sobre cualquier fondo (sobre la cabecera de la app, con alfa 120 se confundía con su texto)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=(18, 18, 18, 200))
    d.text((18, int(size * 0.28)), text, font=f, fill=(255, 255, 255, 250))
    img.save(out_png)
    return out_png
