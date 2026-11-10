"""Producto real, nunca inventado: pantallas de app reales en un móvil, packshots reales animados,
captura automática de webs/apps con Playwright y control de fidelidad (OCR) del producto generado.

Todo es determinista y cuesta ≈0: los píxeles de marca salen de assets reales del cliente.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import time
from pathlib import Path

from PIL import Image, ImageFilter

from ..costs import record_local
from ..editing.graphics import hex_rgb, phone_frame, status_bar_height
from ..media import h264, run, write_concat_list
from ..models import Asset, AssetKind, BrandKit, Product
from ..store import ctx

W, H, FPS = 1080, 1920, 30


def _bg_from(image: Path | None, out: Path, brand: BrandKit | None, darken: float = 0.35) -> Path:
    """Fondo: versión desenfocada y oscurecida de una imagen de la escena, o degradado de marca."""
    if image and image.exists():
        im = Image.open(image).convert("RGB")
        im = im.resize((W, int(im.height * W / im.width)) if im.width else (W, H))
        if im.height < H:
            im = im.resize((int(im.width * H / im.height), H))
        left, top = (im.width - W) // 2, (im.height - H) // 2
        im = im.crop((left, top, left + W, top + H)).filter(ImageFilter.GaussianBlur(28))
        im = Image.blend(im, Image.new("RGB", (W, H), (0, 0, 0)), darken)
    else:
        c1 = hex_rgb((brand.colors.get("primary") if brand else "#1d1d1f") or "#1d1d1f")[:3]
        c2 = tuple(min(255, int(v * 1.6) + 20) for v in c1)
        im = Image.new("RGB", (W, H))
        px = im.load()
        for y in range(H):
            t = y / H
            col = tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))
            for x in range(W):
                px[x, y] = col
    im.save(out, quality=92)
    return out


def _screen_content(sources: list[Asset], duration: float, sw: int, sh: int, out: Path) -> Path:
    """Vídeo del contenido de pantalla: grabación real, o capturas reales con scroll suave / pasos."""
    vids = [s for s in sources if s.kind == AssetKind.video]
    imgs = [s for s in sources if s.kind == AssetKind.image]
    if vids:
        src = ctx().assets.abspath(vids[0])
        run(["-stream_loop", -1, "-i", src, "-t", f"{duration:.3f}", "-vf",
             f"scale={sw}:{sh}:force_original_aspect_ratio=increase,crop={sw}:{sh},fps={FPS},format=yuv420p",
             "-an", *h264(16), out])
        return out
    if not imgs:
        raise ValueError("no hay capturas ni grabaciones reales de la app")
    per = duration / len(imgs)
    parts = []
    for i, a in enumerate(imgs):
        p = ctx().assets.abspath(a)
        im = Image.open(p)
        scaled_h = int(im.height * sw / im.width)
        part = out.with_name(f"{out.stem}_{i}.mp4")
        if scaled_h > sh * 1.15:
            # captura larga: scroll suave (ease-in-out) desde arriba
            travel = scaled_h - sh
            ease = f"(1-cos(PI*min(t/{per:.3f},1)))/2"
            run(["-loop", 1, "-t", f"{per:.3f}", "-i", p, "-vf",
                 f"scale={sw}:-2,crop={sw}:{sh}:0:'{travel}*{ease}',fps={FPS},format=yuv420p",
                 *h264(16), part])
        else:
            run(["-loop", 1, "-t", f"{per:.3f}", "-i", p, "-vf",
                 f"scale={sw}:{sh}:force_original_aspect_ratio=decrease,pad={sw}:{sh}:(ow-iw)/2:(oh-ih)/2:color=white,fps={FPS},format=yuv420p",
                 *h264(16), part])
        parts.append(part)
    lst = write_concat_list(parts, out.with_suffix(".txt"))
    run(["-f", "concat", "-safe", 0, "-i", lst, "-c", "copy", out])
    return out


def screen_text(a: Asset) -> str:
    """Texto OCR de una captura (cacheado): sirve para elegir qué pantalla real enseña cada plano."""
    from ..costs import cache_get, cache_key, cache_put

    k = cache_key("ocr_screen", a.id)
    hit = cache_get(k)
    if hit is not None:
        return hit["text"]
    text = ocr_text(ctx().assets.abspath(a))
    cache_put(k, {"text": text})
    return text


def pick_screens(product: Product, focus: str = "", index: int = 0, n: int = 1) -> list[Asset]:
    """Las capturas reales que mejor encajan con lo que cuenta el plano (palabras del plano ↔ OCR de cada pantalla).

    Sin coincidencias, reparto por orden (el plano k de app enseña la pantalla k) para que dos planos de app no
    repitan la misma secuencia.
    """
    from ..providers.local_asr import norm

    shots = [ctx().db.get_asset(i) for i in product.screenshot_asset_ids]
    if len(shots) <= n:
        return shots
    def keys(text: str) -> set[str]:
        return {norm(w)[:5] for w in text.split() if len(norm(w)) >= 4}

    words = keys(focus)
    scored = []
    for i, a in enumerate(shots):
        lines = [ln.strip() for ln in screen_text(a).splitlines() if ln.strip()]
        # titular = primera línea con aspecto de encabezado (≥2 palabras, ≥8 letras): pesa el triple que el resto
        heading = next((ln for ln in lines if len(ln.split()) >= 2 and sum(c.isalpha() for c in ln) >= 8), "")
        h, body = keys(heading), keys(" ".join(lines))
        scored.append((3 * len(words & h) + len(words & (body - h)), i, a))
    best = max(scored, key=lambda x: x[0])[0]
    if best == 0:
        return [shots[(index + j) % len(shots)] for j in range(n)]
    return [a for _, _, a in sorted(scored, key=lambda x: (-x[0], x[1]))[:n]]


def app_screen_clip(product: Product, duration: float, *, background: Asset | None = None, brand: BrandKit | None = None,
                    tag: str = "", focus: str = "", index: int = 0) -> Asset:
    """Móvil genérico con la app REAL en pantalla sobre fondo de la escena, con ligera vida de cámara en mano.

    `focus` (descripción del plano) elige qué pantalla real se enseña; con grabación de pantalla se usa la grabación.
    """
    t0 = time.time()
    work = ctx().work("product", f"app_{product.id}_{tag}")
    if product.screen_recording_asset_ids:
        sources = [ctx().db.get_asset(i) for i in product.screen_recording_asset_ids]
    else:
        sources = pick_screens(product, focus, index, n=1 if duration < 4.5 else 2)
    sw, sh = 600, 1300
    frame_png, (bx, by, _, _) = phone_frame(work / "frame.png", screen_w=sw, screen_h=sh)
    sb = status_bar_height(sh)
    screen = _screen_content(sources, duration, sw, sh - sb, work / "screen.mp4")
    bg = _bg_from(ctx().assets.abspath(background) if background else None, work / "bg.jpg", brand)
    fw, fh = sw + 2 * bx, sh + 2 * by
    scale = 0.70 * W / fw
    pw, ph = int(fw * scale) // 2 * 2, int(fh * scale) // 2 * 2
    out = work / "app_clip.mp4"
    # composición: pantalla bajo el marco → móvil → leve balanceo (rotación+desplazamiento) sobre el fondo
    fc = (
        f"[1:v]format=rgba,pad={sw}:{sh}:0:{sb}:color=white,"  # hueco de la barra de estado (la dibuja el marco)
        f"pad={fw}:{fh}:{bx}:{by}:color=black@0[scr];"  # rgba ANTES del pad: si no, esquinas negras
        f"[scr][2:v]overlay=0:0:format=auto[phone0];"
        f"[phone0]scale={pw}:{ph},format=rgba,"
        f"rotate='0.012*sin(2*PI*t/3.1)':c=none:ow=rotw(0.03):oh=roth(0.03)[phone];"
        f"[0:v]scale={W}:{H},zoompan=z='1.0+0.0004*on':d=1:s={W}x{H}:fps={FPS}[bgz];"
        f"[bgz][phone]overlay=x='(W-w)/2+6*sin(2*PI*t/2.3)':y='(H-h)/2+8*sin(2*PI*t/2.9)':format=auto,"
        f"format=yuv420p[v]"
    )
    run(["-loop", 1, "-t", f"{duration:.3f}", "-i", bg, "-i", screen, "-loop", 1, "-t", f"{duration:.3f}", "-i", frame_png,
         "-filter_complex", fc, "-map", "[v]", "-t", f"{duration:.3f}", "-r", FPS, *h264(17), "-an", out])
    record_local("product", "ffmpeg-app-composite", time.time() - t0)
    return ctx().assets.ingest(out, source="render:app_screen", move=True,
                               meta={"product": product.id, "real_pixels": True, "screens": [x.id for x in sources]})


def cutout(asset: Asset) -> Path:
    """Recorta el producto de un packshot sobre fondo claro (blanco de estudio) → PNG con alfa y bordes suaves.

    Relleno por inundación desde los bordes: solo se quita el fondo CONECTADO al borde, nunca huecos claros del propio
    producto. Cacheado por asset.
    """
    import cv2
    import numpy as np

    out = ctx().work("product", "cutouts") / f"{asset.id}.png"
    if out.exists():
        return out
    bgr = cv2.imread(str(ctx().assets.abspath(asset)), cv2.IMREAD_COLOR)
    h, w = bgr.shape[:2]
    # fondo = claro y SIN color (blanco de estudio y su sombra gris neutra); el producto tiene color o es oscuro
    chroma = bgr.max(axis=2).astype(np.int16) - bgr.min(axis=2).astype(np.int16)
    value = bgr.max(axis=2)
    bgmask = ((chroma < 16) & (value > 150)).astype(np.uint8)
    ff = np.zeros((h + 2, w + 2), np.uint8)
    reach = bgmask.copy()
    for x, y in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)):
        if reach[y, x]:
            cv2.floodFill(reach, ff, (x, y), 2)
    alpha = np.where(reach == 2, 0, 255).astype(np.uint8)
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(alpha, 8)  # fuera motas blancas sueltas (se veían en la tarjeta)
    if n > 2:
        keep = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        big = [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] >= 0.02 * stats[keep, cv2.CC_STAT_AREA]]
        alpha = np.where(np.isin(lab, big), 255, 0).astype(np.uint8)
    alpha = cv2.erode(alpha, np.ones((3, 3), np.uint8), iterations=1)  # 1 px hacia dentro: sin borde serrado ni halo
    alpha = cv2.GaussianBlur(alpha, (0, 0), 1.4)
    ys, xs = np.where(alpha > 10)
    rgba = np.dstack([cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB), alpha])
    if len(xs):
        rgba = rgba[max(0, ys.min() - 4): ys.max() + 5, max(0, xs.min() - 4): xs.max() + 5]
    Image.fromarray(rgba, "RGBA").save(out)
    return out


def plate_from(image: Path | None, out: Path) -> Path | None:
    """Fondo de la habitación SIN la persona: recorta del fotograma la franja más alejada de la cara (desenfocada luego
    por `_bg_from`, solo aporta colores y formas de la estancia; si no, se adivina su silueta detrás del producto)."""
    if image is None or not Path(image).exists():
        return None
    import cv2

    from . import identity

    img = cv2.imread(str(image))
    if img is None:
        return None
    h, w = img.shape[:2]
    f = identity.detect(img)
    if f is None:
        return Path(image)
    cx = float(f[0] + f[2] / 2) / w
    band = img[:, int(w * 0.58):] if cx < 0.5 else img[:, : int(w * 0.42)]
    band = band[: int(h * 0.55)]  # parte alta: pared, ventana, estanterías (lejos del cuerpo)
    cv2.imwrite(str(out), band)
    return out


def _product_with_shadow(cut: Path, max_w: int, max_h: int, out: Path) -> Path:
    """Producto recortado + sombra de contacto suave (el producto «se apoya», no flota pegado)."""
    im = Image.open(cut).convert("RGBA")
    im.thumbnail((max_w, max_h))
    pad = int(im.height * 0.18)
    canvas = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    a = im.getchannel("A").point(lambda v: int(v * 0.55))
    shadow = Image.new("RGBA", im.size, (20, 16, 30, 255))
    shadow.putalpha(a)
    sh.alpha_composite(shadow, (pad + int(im.width * 0.02), pad + int(im.height * 0.07)))
    sh = sh.filter(ImageFilter.GaussianBlur(max(6, im.width // 40)))
    canvas.alpha_composite(sh)
    from PIL import ImageDraw as _D  # sombra de CONTACTO: elipse oscura y difusa bajo la base
    cs = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    _D.Draw(cs).ellipse((pad + int(im.width * 0.06), pad + int(im.height * 0.86), pad + int(im.width * 0.94), pad + int(im.height * 1.04)),
                        fill=(15, 10, 25, 120))
    canvas.alpha_composite(cs.filter(ImageFilter.GaussianBlur(max(8, im.width // 28))))
    canvas.alpha_composite(im, (pad, pad))
    canvas.save(out)
    return out


def packshot_clip(product: Product, duration: float, *, brand: BrandKit | None = None, tag: str = "",
                  background: Asset | None = None, framing: str = "full") -> Asset:
    """Packshot REAL animado: el producto recortado (píxeles reales, cero deformación) sobre la escena desenfocada,
    con sombra de contacto, acercamiento CENTRADO muy lento y una flotación mínima de cámara en mano."""
    t0 = time.time()
    work = ctx().work("product", f"pack_{product.id}_{tag}")
    if product.footage_asset_ids:
        src = ctx().db.get_asset(product.footage_asset_ids[0])
        out = work / "footage.mp4"
        run(["-stream_loop", -1, "-i", ctx().assets.abspath(src), "-t", f"{duration:.3f}", "-vf",
             f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},format=yuv420p", "-an",
             *h264(17), out])
        return ctx().assets.ingest(out, source="render:product_footage", meta={"product": product.id, "real_pixels": True}, move=True)
    if not product.packshot_asset_ids:
        raise ValueError("no hay packshot real del producto")
    pack = ctx().db.get_asset(product.packshot_asset_ids[0])
    cut = cutout(pack)
    plate = None
    if background is not None:
        src_bg = ctx().assets.abspath(background)
        has_people = (background.meta or {}).get("people", True)
        plate = plate_from(src_bg, work / "plate.jpg") if has_people else src_bg
    bg = _bg_from(plate, work / "bg.jpg", brand, darken=0.08)  # claro: un fondo oscurecido chocaba con la habitación
    detail = framing == "detail"
    fg = _product_with_shadow(cut, int(W * (1.35 if detail else 0.86)), int(H * (0.8 if detail else 0.52)), work / f"fg_{framing}.png")
    fw, fh = Image.open(fg).size
    out = work / f"packshot_{framing}.mp4"
    d = f"{duration:.3f}"
    # FIJO (sin acercamiento: los productos con patrones regulares —rejillas, tramas, texto fino— hacen moiré al escalar)
    # con un vaivén mínimo de cámara en mano. «detail»: un extremo del producto más grande, para no repetir el mismo
    # plano; ~70 % del producto con su extremo derecho dentro (nunca «medio producto fuera») y alto, lejos de los subtítulos
    x, y = ("W*0.93-w", "H*0.40-h/2") if detail else ("(W-w)/2", "(H-h)/2-H*0.03")
    fc = (f"[0:v]scale={W}:{H},format=rgba[bg];[1:v]format=rgba[p];"
          f"[bg][p]overlay=x={x}+3*sin(2*PI*t/3.7):y={y}+4*sin(2*PI*t/4.3):format=auto,format=yuv420p[v]")
    run(["-loop", 1, "-framerate", FPS, "-t", d, "-i", bg, "-loop", 1, "-framerate", FPS, "-t", d, "-i", fg,
         "-filter_complex", fc, "-map", "[v]", "-t", d, "-r", FPS, *h264(17), "-an", out])
    record_local("product", "ffmpeg-packshot", time.time() - t0)
    return ctx().assets.ingest(out, source="render:packshot", meta={"product": product.id, "real_pixels": True, "size": [fw, fh]},
                               move=True)


def _launch(p):
    """Chrome o Edge del sistema si existen; si no, el Chromium de Playwright (`playwright install chromium`)."""
    errors = []
    for channel in ("chrome", "msedge", None):
        try:
            return p.chromium.launch(channel=channel, headless=True) if channel else p.chromium.launch(headless=True)
        except Exception as e:  # noqa: BLE001
            errors.append(f"{channel or 'chromium'}: {str(e).splitlines()[0][:120]}")
    raise RuntimeError("no hay navegador para capturar. Arreglo: instala Google Chrome o ejecuta "
                       "`uv run --project modulos/motor-ia playwright install chromium`. Detalle: " + " | ".join(errors))


def capture_url(url: str, *, out_png: Path | None = None, device: str = "iPhone 15", full_page: bool = True,
                wait_ms: int = 2500) -> Asset:
    """Captura REAL de una web/app web en un móvil emulado (Playwright + Chrome/Edge del sistema o Chromium).

    Para un archivo local usa su URI (`Path(...).as_uri()`), que es válida en Mac, Linux y Windows."""
    from playwright.sync_api import sync_playwright

    t0 = time.time()
    out_png = out_png or ctx().work("captures") / (re.sub(r"[^a-z0-9]+", "_", url.lower())[:60] + ".png")
    with sync_playwright() as p:
        dev = p.devices.get(device) or p.devices["iPhone 13"]
        browser = _launch(p)
        page = browser.new_context(**dev).new_page()
        page.goto(url, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(wait_ms)
        for sel in ("button:has-text('Aceptar')", "button:has-text('Accept')", "#onetrust-accept-btn-handler"):
            try:
                page.locator(sel).first.click(timeout=800)
                break
            except Exception:
                pass
        page.screenshot(path=str(out_png), full_page=full_page)
        browser.close()
    record_local("product", "playwright-capture", time.time() - t0, note=url)
    return ctx().assets.ingest(out_png, source="capture:playwright", meta={"url": url, "real_pixels": True})


def ocr_text(image: Path, langs: str = "spa+eng", psm: str = "11") -> str:
    """OCR con Tesseract (datos locales spa/eng)."""
    tess = shutil.which("tesseract")
    if not tess:
        return ""
    tessdata = ctx().settings.models_dir / "tessdata"
    env = {"TESSDATA_PREFIX": str(tessdata)} if tessdata.exists() else None
    import os

    p = subprocess.run([tess, str(image), "-", "-l", langs, "--psm", psm], capture_output=True, timeout=60, stdin=subprocess.DEVNULL,
                       env={**os.environ, **(env or {})})
    return p.stdout.decode("utf-8", errors="ignore")  # tesseract puede escribir bytes no UTF-8 en sus mensajes


def label_fidelity(frame: Path, expected: list[str]) -> dict:
    """¿Se lee el texto real de la etiqueta en el fotograma? (para producto GENERADO, no compuesto)."""
    from ..providers.local_asr import norm

    txt = norm(ocr_text(frame))
    found = [e for e in expected if norm(e) and norm(e) in txt]
    return {"expected": expected, "found": found, "ratio": (len(found) / len(expected)) if expected else 1.0}
