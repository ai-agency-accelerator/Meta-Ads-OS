"""Hojas de contacto: fotogramas a 2 fps, 270 px de ancho, en hojas de 6×4 con su timecode. Los fotogramas dentro
de un issue `block` llevan marco rojo y los de un `warn` marco ámbar (para ver el problema en 10 s)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ..paths import FONTS
from .context import QAContext, tc

RED, AMBER, BG, FG = (230, 57, 70), (244, 162, 97), (16, 18, 28), (240, 240, 240)


def _font(size: int) -> ImageFont.ImageFont:
    for name in ("Montserrat[wght].ttf", "Montserrat-Bold.ttf", "Inter[wght].ttf"):
        p = FONTS / name
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                pass
    cands = sorted(FONTS.glob("*.ttf"))
    if cands:
        return ImageFont.truetype(str(cands[0]), size)
    return ImageFont.load_default()


def build(ctx: QAContext) -> list[Path]:
    s = ctx.cfg["sampling"]
    frames = ctx.frames_sheet
    for old in ctx.vdir.glob("qa_sheet_*.jpg"):
        old.unlink()
    if not frames:
        return []
    cols, rows = s["sheet_cols"], s["sheet_rows"]
    per = cols * rows
    first = Image.open(frames[0][1])
    fw, fh = first.size
    lab, pad, head = 22, 6, 34
    font, hfont = _font(15), _font(18)
    spans = [(i.t0, i.t1, i.severity) for i in ctx.issues
             if i.t0 is not None and i.t1 is not None and not i.check.startswith("judge.")
             and ((i.severity == "block" and i.t1 - i.t0 <= 10) or (i.severity == "warn" and i.t1 - i.t0 <= 5))]
    out = []
    for k in range(0, len(frames), per):
        chunk = frames[k:k + per]
        sheet = Image.new("RGB", (cols * (fw + pad) + pad, head + rows * (fh + lab + pad) + pad), BG)
        d = ImageDraw.Draw(sheet)
        d.text((pad, 8), f"{ctx.slug}/{ctx.vid} · {tc(chunk[0][0])}–{tc(chunk[-1][0])} · hoja {k // per + 1}", fill=FG, font=hfont)
        for j, (t, p) in enumerate(chunk):
            x = pad + (j % cols) * (fw + pad)
            y = head + (j // cols) * (fh + lab + pad)
            im = Image.open(p).convert("RGB")
            sheet.paste(im, (x, y))
            sev = None
            for a, b, sv in spans:
                if a - 0.25 <= t <= b + 0.25:
                    sev = "block" if sv == "block" or sev == "block" else "warn"
            if sev:
                col = RED if sev == "block" else AMBER
                d.rectangle([x - 2, y - 2, x + fw + 1, y + fh + 1], outline=col, width=4)
            d.text((x + 2, y + fh + 2), tc(t), fill=(RED if sev == "block" else AMBER if sev else FG), font=font)
        path = ctx.vdir / f"qa_sheet_{k // per + 1:02d}.jpg"
        sheet.save(path, quality=85)
        out.append(path)
    return out
