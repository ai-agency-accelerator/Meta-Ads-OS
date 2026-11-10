"""Capturas y grabaciones de scroll de webs REALES con Playwright (su Chromium propio, nunca tu navegador).

Requiere el extra `avanzado` y el Chromium de Playwright (si falta, el error dice cómo instalarlo):

    uv sync --project modulos/cutkit --extra avanzado && uv run --project modulos/cutkit playwright install chromium

Lo que hace para vídeo:
- emulación de móvil de verdad (`is_mobile`, táctil, UA de iPhone) o escritorio;
- banners de cookies: primero se pulsa «Rechazar»/«Solo necesarias» (o «Aceptar» si no hay otra), luego
  se ocultan por CSS y, por último, se esconde cualquier capa fija que siga hablando de cookies;
- espera a las fuentes (`document.fonts.ready`) y a las imágenes perezosas (pasada de scroll previa);
- **scroll determinista**: NO se usa `record_video` (VP8 de bitrate bajo, texto con ruido). Se calcula la
  posición de cada fotograma con una curva suave, se fija, se espera a dos `requestAnimationFrame`, se
  captura y ffmpeg monta el vídeo a fps fijo (H.264, CRF 16): nítido y sin saltos.
- `svg_a_png`: rasteriza un SVG con el mismo Chromium (para logos SVG cuando hace falta un PNG).

No se automatiza ningún inicio de sesión: para apps privadas (paneles, CRM con datos), graba tú la pantalla y
regístrala como archivo.
"""

from __future__ import annotations

import asyncio
import base64
import importlib.util
import math
import shutil
import subprocess
import threading
from pathlib import Path
from typing import Any, Awaitable, Callable, TypeVar

from cutkit.sistema import requiere

_T = TypeVar("_T")

INSTALAR = ("uv sync --project modulos/cutkit --extra avanzado && "
            "uv run --project modulos/cutkit playwright install chromium")
_LINUX_DEPS = "uv run --project modulos/cutkit playwright install --with-deps chromium"

DESKTOP_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/140.0.0.0 Safari/537.36")
MOBILE_UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
             "Version/18.6 Mobile/15E148 Safari/604.1")

# Banners de consentimiento habituales (CMP conocidas y patrones genéricos): se ocultan por CSS.
COOKIE_SELECTORS = [
    "#onetrust-banner-sdk", "#onetrust-consent-sdk", ".cookie-banner", "[id*='cookie' i][class*='banner' i]",
    "[aria-label*='cookie' i]", "#CybotCookiebotDialog", ".cc-window", "#didomi-host", ".fc-consent-root",
]


class PlaywrightNoDisponible(RuntimeError):
    """Falta Playwright o su Chromium; el mensaje dice cómo instalarlo."""


def disponible() -> bool:
    """¿Está instalado el paquete de Playwright? (no comprueba el Chromium: eso se ve al lanzarlo)."""
    return importlib.util.find_spec("playwright") is not None


def _async_playwright():
    try:
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise PlaywrightNoDisponible(f"Falta Playwright (capturas web y SVG→PNG). Instálalo: {INSTALAR}") from exc
    return async_playwright


async def _launch(p):
    """Chromium sin ventana; si no está descargado o le faltan librerías, error con el arreglo."""
    try:
        return await p.chromium.launch(headless=True)
    except Exception as exc:  # noqa: BLE001 - Playwright lanza su propio Error genérico
        msg = str(exc)
        if "Executable doesn't exist" in msg or "playwright install" in msg:
            raise PlaywrightNoDisponible(
                f"Falta el Chromium de Playwright. Instálalo: uv run --project modulos/cutkit playwright install "
                f"chromium (en Linux, si faltan librerías del sistema: {_LINUX_DEPS})") from exc
        if "shared libraries" in msg or "missing dependencies" in msg.lower():
            raise PlaywrightNoDisponible(f"A Chromium le faltan librerías del sistema. Instálalas: {_LINUX_DEPS}") from exc
        raise


def _run(make_coro: Callable[[], Awaitable[_T]]) -> _T:
    """Ejecuta una corrutina desde código síncrono (en un hilo aparte si ya hay un bucle asyncio activo)."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(make_coro())
    box: dict[str, Any] = {}

    def runner() -> None:
        try:
            box["r"] = asyncio.run(make_coro())
        except BaseException as exc:  # noqa: BLE001 - se relanza en el hilo que llama
            box["e"] = exc

    t = threading.Thread(target=runner, name="cutkit-playwright")
    t.start()
    t.join()
    if "e" in box:
        raise box["e"]
    return box["r"]

# Viewports por defecto (CSS px) y escala de dispositivo.
VIEWPORTS = {
    "mobile": {"width": 393, "height": 852, "scale": 3, "mobile": True},     # iPhone 15/16 Pro
    "desktop": {"width": 1280, "height": 800, "scale": 2, "mobile": False},
    "desktop-hd": {"width": 1440, "height": 900, "scale": 2, "mobile": False},
    "tablet": {"width": 820, "height": 1180, "scale": 2, "mobile": True},
}

MAX_FULLPAGE_DEVICE_PX = 16000   # Chromium corta o deja en blanco capturas más altas

_REJECT_RE = (r"^\s*(rechaz(ar|o)( todo| todas| todas las cookies| cookies)?|denegar|no acepto|"
              r"solo (las )?(necesarias|esenciales)|usar solo cookies necesarias|"
              r"reject( all)?( cookies)?|decline( all)?|deny|only (necessary|essential)( cookies)?|"
              r"necessary only|essential only|refuse)\s*$")
_ACCEPT_RE = (r"^\s*(aceptar( todo| todas| todas las cookies| cookies)?|acepto|de acuerdo|entendido|"
              r"accept( all)?( cookies)?|allow all|agree|i agree|got it|ok|okay|understood)\s*$")

# JS: pulsa el botón de consentimiento dentro de contenedores de cookies/consentimiento.
_CONSENT_JS = r"""
([rejectRe, acceptRe]) => {
  const rej = new RegExp(rejectRe, 'i'), acc = new RegExp(acceptRe, 'i');
  const hint = /cookie|consent|gdpr|cmp|privacy|privacidad|didomi|onetrust|cookiebot|usercentrics|truste/i;
  const containers = Array.from(document.querySelectorAll(
    '[id*=cookie i],[class*=cookie i],[id*=consent i],[class*=consent i],[id*=gdpr i],[class*=gdpr i],' +
    '[id*=cmp i],[class*=cmp i],[aria-label*=cookie i],[aria-label*=consent i],[role=dialog],[aria-modal=true],' +
    '#usercentrics-root,#didomi-host,#onetrust-banner-sdk,#CybotCookiebotDialog'));
  const ok = containers.filter(c => {
    const label = (c.id || '') + ' ' + (c.className || '') + ' ' + (c.getAttribute('aria-label') || '');
    return hint.test(label) || /cookie|consent|privacidad|privacy/i.test((c.innerText || '').slice(0, 3000));
  });
  const visible = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  for (const re of [rej, acc]) {
    for (const c of ok) {
      const btns = c.querySelectorAll('button, a, [role=button], input[type=button], input[type=submit]');
      for (const b of btns) {
        const t = (b.innerText || b.value || b.getAttribute('aria-label') || '').trim();
        if (t && t.length < 60 && re.test(t) && visible(b)) { b.click(); return t; }
      }
    }
  }
  return null;
}
"""

# JS: esconde capas fijas/pegadas que siguen hablando de cookies (último recurso).
_NUKE_JS = r"""
() => {
  let n = 0;
  for (const el of document.querySelectorAll('body *')) {
    const s = getComputedStyle(el);
    if (s.position !== 'fixed' && s.position !== 'sticky') continue;
    const t = (el.innerText || '').slice(0, 2000);
    if (/cookie|consentimiento|consent|gdpr/i.test(t) && el.getBoundingClientRect().height < innerHeight * 0.9) {
      el.style.setProperty('display', 'none', 'important'); n++;
    }
  }
  return n;
}
"""

# JS: elemento que realmente hace scroll (algunas webs usan un contenedor interno).
_SCROLLER_JS = r"""
() => {
  const se = document.scrollingElement || document.documentElement;
  if (se.scrollHeight - innerHeight > 4) return {inner: false, max: se.scrollHeight - innerHeight};
  let best = null, bestMax = 0;
  for (const el of document.querySelectorAll('body *')) {
    const s = getComputedStyle(el);
    if (!/(auto|scroll)/.test(s.overflowY)) continue;
    const m = el.scrollHeight - el.clientHeight;
    if (m > bestMax && el.clientHeight > innerHeight * 0.5) { best = el; bestMax = m; }
  }
  if (best) { best.setAttribute('data-ck-scroller', '1'); return {inner: true, max: bestMax}; }
  return {inner: false, max: 0};
}
"""

_HIDE_SCROLLBARS_CSS = ("html{scroll-behavior:auto !important;scrollbar-width:none !important}"
                        "*{scroll-behavior:auto !important}::-webkit-scrollbar{display:none !important;"
                        "width:0 !important;height:0 !important}")


def viewport_of(params: dict[str, Any]) -> dict[str, Any]:
    """Traduce `params.viewport` (mobile | desktop | 'WxH' | [w, h]) + `scale` a la config del contexto."""
    vp = params.get("viewport", "desktop")
    if isinstance(vp, (list, tuple)) and len(vp) == 2:
        cfg = {"width": int(vp[0]), "height": int(vp[1]), "scale": 2, "mobile": int(vp[0]) < 600}
    elif isinstance(vp, str) and "x" in vp.lower() and vp.lower().replace("x", "").isdigit():
        w, h = (int(x) for x in vp.lower().split("x"))
        cfg = {"width": w, "height": h, "scale": 2, "mobile": w < 600}
    else:
        key = str(vp).lower()
        if key not in VIEWPORTS:
            raise ValueError(f"viewport no válido: {vp!r} (mobile | desktop | desktop-hd | tablet | 'WxH')")
        cfg = dict(VIEWPORTS[key])
    if params.get("scale"):
        cfg["scale"] = float(params["scale"])
    return cfg


async def _open(p, url: str, params: dict[str, Any], *, reduced_motion: str,
                before_goto=None) -> tuple[Any, Any, dict]:
    """Abre la página lista para capturar: carga, cookies fuera, fuentes y estilo extra.

    `before_goto(ctx, page)` (opcional, async) corre antes de navegar: p. ej. instalar el reloj falso.
    """
    vp = viewport_of(params)
    browser = await _launch(p)
    ctx_kwargs: dict[str, Any] = dict(
        viewport={"width": vp["width"], "height": vp["height"]}, device_scale_factor=vp["scale"],
        color_scheme="dark" if params.get("dark") else "light", reduced_motion=reduced_motion,
        locale=params.get("locale", "es-ES"), user_agent=MOBILE_UA if vp["mobile"] else DESKTOP_UA,
        is_mobile=vp["mobile"], has_touch=vp["mobile"])
    ctx = await browser.new_context(**ctx_kwargs)
    page = await ctx.new_page()
    if before_goto is not None:
        await before_goto(ctx, page)
    timeout = int(params.get("timeout_ms", 45000))
    resp = await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
    if resp is not None and resp.status >= 400:
        await browser.close()
        raise RuntimeError(f"{url} respondió HTTP {resp.status}")
    try:
        await page.wait_for_load_state("networkidle", timeout=min(12000, timeout))
    except Exception:  # noqa: BLE001 - webs con conexiones abiertas: seguimos
        pass
    await page.wait_for_timeout(int(params.get("wait_ms", 800)))
    info: dict[str, Any] = {"status": resp.status if resp else None, "viewport": vp}
    # 1) cookies: pulsar el botón (rechazar primero), también dentro de iframes de CMP
    clicked = None
    for frame in [page.main_frame, *page.frames[1:]]:
        try:
            clicked = await frame.evaluate(_CONSENT_JS, [_REJECT_RE, _ACCEPT_RE])
        except Exception:  # noqa: BLE001 - iframes de otro origen o ya cerrados
            clicked = None
        if clicked:
            break
    if clicked:
        await page.wait_for_timeout(700)
    info["consent_clicked"] = clicked
    # 2) ocultar por CSS lo que quede + barras de scroll + selectores pedidos
    hide = list(params.get("hide") or []) + COOKIE_SELECTORS
    css = [",".join(hide) + "{display:none !important;visibility:hidden !important}", _HIDE_SCROLLBARS_CSS]
    if params.get("css"):
        css.append(str(params["css"]))
    await page.add_style_tag(content="\n".join(css))
    # 3) último recurso: capas fijas que siguen hablando de cookies
    info["nuked_overlays"] = await page.evaluate(_NUKE_JS)
    # 4) fuentes cargadas
    try:
        await page.evaluate("() => document.fonts.ready.then(() => document.fonts.status)")
    except Exception:  # noqa: BLE001
        pass
    info["title"] = await page.title()
    info["final_url"] = page.url
    return browser, page, info


async def _warm_lazy(page, max_px: float, step_px: float) -> None:
    """Pasada de scroll rápida para que carguen las imágenes perezosas; vuelve arriba."""
    y = 0.0
    while y < max_px:
        y = min(max_px, y + step_px)
        await page.evaluate("(y) => { const s = document.querySelector('[data-ck-scroller]');"
                            " s ? s.scrollTo(0, y) : window.scrollTo(0, y); }", y)
        await page.wait_for_timeout(120)
    try:
        await page.wait_for_load_state("networkidle", timeout=5000)
    except Exception:  # noqa: BLE001
        pass
    await page.evaluate("() => { const s = document.querySelector('[data-ck-scroller]');"
                        " s ? s.scrollTo(0, 0) : window.scrollTo(0, 0); }")
    await page.wait_for_timeout(600)


# ───────────────────────────── captura ─────────────────────────────

async def _capture(url: str, out: Path, params: dict[str, Any]) -> dict:
    async_playwright = _async_playwright()

    async with async_playwright() as p:
        browser, page, info = await _open(p, url, params, reduced_motion="reduce")
        try:
            kwargs: dict[str, Any] = {"path": str(out), "animations": "disabled", "caret": "hide", "type": "png"}
            if params.get("mask"):
                kwargs["mask"] = [page.locator(s) for s in params["mask"]]
                kwargs["mask_color"] = params.get("mask_color", "#1A1A1A")
            if params.get("selector"):
                loc = page.locator(params["selector"]).first
                await loc.wait_for(state="visible", timeout=int(params.get("timeout_ms", 45000)))
                await loc.scroll_into_view_if_needed()
                await page.wait_for_timeout(300)
                await loc.screenshot(**kwargs)
            elif params.get("full_page"):
                sc = await page.evaluate(_SCROLLER_JS)
                await _warm_lazy(page, sc["max"], info["viewport"]["height"] * 0.8)
                height = await page.evaluate("() => document.documentElement.scrollHeight")
                cap = MAX_FULLPAGE_DEVICE_PX / info["viewport"]["scale"]
                if height > cap:
                    info["truncated_to_css_px"] = int(cap)
                    kwargs["clip"] = {"x": 0, "y": 0, "width": info["viewport"]["width"], "height": int(cap)}
                await page.screenshot(full_page=True, **kwargs)
            else:
                await page.screenshot(**kwargs)
        finally:
            await browser.close()
    return info


def capture(url: str, out: Path, params: dict[str, Any] | None = None) -> dict:
    """Captura PNG de `url` (viewport, página completa o elemento). Devuelve info de la página."""
    _async_playwright()                       # sin Playwright: error claro antes de empezar
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    return _run(lambda: _capture(url, out, dict(params or {})))


# ───────────────────────────── scroll en vídeo ─────────────────────────────

def _ease(t: float, kind: str) -> float:
    if kind == "linear":
        return t
    if kind == "cubic":
        return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2
    return -(math.cos(math.pi * t) - 1) / 2   # sine (por defecto): arranque y frenada suaves


def scroll_positions(seconds: float, fps: int, distance: float, *, hold_start: float = 0.4,
                     hold_end: float = 0.4, start: float = 0.0, ease: str = "sine") -> list[float]:
    """Posición de scroll (CSS px) de cada fotograma: pausa inicial, recorrido suave, pausa final."""
    n = max(1, round(seconds * fps))
    move = max(1e-6, seconds - hold_start - hold_end)
    out = []
    for i in range(n):
        t = i / fps
        u = min(1.0, max(0.0, (t - hold_start) / move))
        out.append(start + distance * _ease(u, ease))
    return out


async def _scroll(url: str, frames_dir: Path, params: dict[str, Any]) -> dict:
    async_playwright = _async_playwright()

    seconds = float(params.get("seconds", 6))
    fps = int(params.get("fps", 30))
    async with async_playwright() as p:
        browser, page, info = await _open(p, url, params, reduced_motion="no-preference")
        try:
            vh = info["viewport"]["height"]
            sc = await page.evaluate(_SCROLLER_JS)
            max_scroll = float(sc["max"])
            start = 0.0
            if params.get("start_selector"):
                start = float(await page.evaluate(
                    "(s) => { const e = document.querySelector(s); return e ? e.getBoundingClientRect().top"
                    " + scrollY : 0 }", params["start_selector"]))
            # Distancia por defecto: `speed` alturas de pantalla por segundo durante el recorrido.
            hold_s, hold_e = float(params.get("hold_start", 0.4)), float(params.get("hold_end", 0.4))
            speed = float(params.get("speed", 0.35))
            distance = float(params.get("distance_px") or speed * vh * max(0.5, seconds - hold_s - hold_e))
            distance = max(0.0, min(distance, max_scroll - start))
            info.update(max_scroll=max_scroll, distance_px=round(distance, 1), start_px=round(start, 1))
            await _warm_lazy(page, min(max_scroll, start + distance + vh), vh * 0.8)
            positions = scroll_positions(seconds, fps, distance, hold_start=hold_s, hold_end=hold_e,
                                         start=start, ease=params.get("ease", "sine"))
            js = ("(y) => new Promise(r => { const s = document.querySelector('[data-ck-scroller]');"
                  " s ? s.scrollTo(0, y) : window.scrollTo(0, y);"
                  " requestAnimationFrame(() => requestAnimationFrame(r)); })")
            for i, y in enumerate(positions):
                await page.evaluate(js, y)
                await page.screenshot(path=str(frames_dir / f"f_{i:05d}.jpg"), type="jpeg", quality=95,
                                      caret="hide")
            info["frames"] = len(positions)
        finally:
            await browser.close()
    return info


def record_scroll(url: str, out: Path, params: dict[str, Any] | None = None) -> dict:
    """Vídeo MP4 (H.264, `fps` fijo) de un scroll suave por la web real. Devuelve info."""
    _async_playwright()
    requiere("ffmpeg")                        # antes de grabar, no después
    params = dict(params or {})
    out = Path(out)
    frames_dir = out.with_suffix(".frames")
    shutil.rmtree(frames_dir, ignore_errors=True)
    frames_dir.mkdir(parents=True)
    try:
        info = _run(lambda: _scroll(url, frames_dir, params))
        fps = int(params.get("fps", 30))
        cmd = [requiere("ffmpeg"), "-y", "-v", "error", "-framerate", str(fps), "-i", str(frames_dir / "f_%05d.jpg"),
               "-vf", "crop=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264", "-preset", "slow",
               "-crf", str(params.get("crf", 16)), "-pix_fmt", "yuv420p", "-r", str(fps),
               "-movflags", "+faststart", str(out)]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            raise RuntimeError(f"ffmpeg falló: {r.stderr[-400:]}")
        return info
    finally:
        shutil.rmtree(frames_dir, ignore_errors=True)


# ───────────────────────────── recorrido determinista (paradas + animaciones a velocidad real) ─────────────────────────────
#
# `record_scroll` mueve el scroll con precisión, pero las animaciones propias de la web siguen el reloj de pared: como
# cada captura tarda ~0,1–0,3 s, un pulso CSS de 2 s sale ×5 de rápido. `record_tour` congela el tiempo de la página y
# lo avanza 1/fps por fotograma:
#   - JS (setTimeout, setInterval, requestAnimationFrame, performance.now, Date): reloj falso de Playwright
#     (`clock.install` antes de navegar → `pause_at` al empezar → `run_for(1000/fps)` por fotograma);
#   - animaciones CSS, transiciones y Web Animations: `document.getAnimations()` en pausa y `currentTime` fijado;
#   - `<video>`: en pausa y `currentTime` fijado (se espera a `seeked`).
# El recorrido son paradas (`stops`): una posición (px CSS, selector CSS o texto visible) con su pausa y el viaje
# hasta la siguiente con easing. Resultado: vídeo nítido a fps fijo, scroll sin saltos y animaciones a su velocidad.

_FIND_JS = r"""
([sel, text, align, offset, vh]) => {
  let el = null;
  if (sel) el = document.querySelector(sel);
  if (!el && text) {
    const want = text.replace(/\s+/g, ' ').trim().toLowerCase();
    let best = null, bestA = Infinity;
    for (const e of document.querySelectorAll('body *')) {
      const t = (e.innerText || '').replace(/\s+/g, ' ').trim().toLowerCase();
      if (!t || !t.includes(want)) continue;
      const r = e.getBoundingClientRect();
      const a = r.width * r.height;
      if (r.height > 0 && a < bestA) { best = e; bestA = a; }
    }
    el = best;
  }
  if (!el) return null;
  const r = el.getBoundingClientRect();
  const top = r.top + scrollY;
  if (align === 'center') return top + r.height / 2 - vh / 2 + offset;
  if (align === 'bottom') return top + r.height - vh + offset;
  return top - offset;
}
"""

_SEEK_JS = r"""
async ([T, restart]) => {
  for (const a of document.getAnimations()) {
    try {
      if (a.__ck === undefined) a.__ck = (a.currentTime == null ? 0 : a.currentTime) - T;
      a.pause();
      a.currentTime = Math.max(0, a.__ck + T);
    } catch (e) {}
  }
  const waits = [];
  for (const v of document.querySelectorAll('video')) {
    try {
      if (!(v.duration > 0)) continue;
      if (v.__ck === undefined) v.__ck = restart ? -T / 1000 : v.currentTime - T / 1000;
      v.pause();
      let want = v.__ck + T / 1000;
      want = v.loop ? ((want % v.duration) + v.duration) % v.duration : Math.min(Math.max(0, want), v.duration - 0.001);
      if (Math.abs(v.currentTime - want) > 0.001) {
        waits.push(new Promise(res => { const t = setTimeout(res, 400); v.addEventListener('seeked', () => { clearTimeout(t); res(); }, { once: true }); }));
        v.currentTime = want;
      }
    } catch (e) {}
  }
  if (waits.length) await Promise.all(waits);
  return true;
}
"""

_EASES = {
    "linear": lambda t: t,
    "sine": lambda t: -(math.cos(math.pi * t) - 1) / 2,
    "cubic": lambda t: 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2,
    "quint": lambda t: 16 * t ** 5 if t < 0.5 else 1 - (-2 * t + 2) ** 5 / 2,
    "expo_out": lambda t: 1.0 if t >= 1 else 1 - 2 ** (-10 * t),
}


def tour_positions(ys: list[float], holds: list[float], moves: list[float], eases: list[str], fps: int) -> list[float]:
    """Scroll (px CSS) de cada fotograma: pausa en cada parada y viaje suave a la siguiente."""
    out: list[float] = []
    for i, y in enumerate(ys):
        out += [y] * max(0, round(holds[i] * fps))
        if i + 1 < len(ys):
            n = max(1, round(moves[i] * fps))
            f = _EASES.get(eases[i], _EASES["sine"])
            out += [y + (ys[i + 1] - y) * f((k + 1) / n) for k in range(n)]
    return out or [ys[0]]


async def _tour(url: str, frames_dir: Path, params: dict[str, Any]) -> dict:
    async_playwright = _async_playwright()

    fps = int(params.get("fps", 30))
    deterministic = bool(params.get("deterministic", True))

    async def install_clock(ctx, page):
        if deterministic:
            await ctx.clock.install()

    async with async_playwright() as p:
        browser, page, info = await _open(p, url, params, reduced_motion="no-preference",
                                          before_goto=install_clock)
        try:
            vh = info["viewport"]["height"]
            sc = await page.evaluate(_SCROLLER_JS)
            max_scroll = float(sc["max"])
            # `warm_to` (px CSS): precarga solo hasta ahí, para que lo que se anima «al entrar» en pantalla
            # (IntersectionObserver) se dispare DURANTE la grabación y no en la pasada de precarga.
            warm_to = params.get("warm_to")
            await _warm_lazy(page, max_scroll if warm_to is None else min(max_scroll, float(warm_to)), vh * 0.8)
            await page.wait_for_timeout(int(params.get("settle_ms", 1200)))
            stops = list(params.get("stops") or [{"y": 0, "hold": float(params.get("seconds", 4))}])
            ys, holds, moves, eases, resolved = [], [], [], [], []
            for s in stops:
                if "y" in s:
                    y = float(s["y"])
                else:
                    y = await page.evaluate(_FIND_JS, [s.get("selector"), s.get("text"), s.get("align", "top"),
                                                       float(s.get("offset", 0)), vh])
                    if y is None:
                        raise RuntimeError(f"parada no encontrada: {s}")
                y = max(0.0, min(float(y), max_scroll))
                ys.append(y)
                holds.append(float(s.get("hold", 0.4)))
                moves.append(float(s.get("move", 1.2)))
                eases.append(str(s.get("ease", params.get("ease", "sine"))))
                resolved.append(round(y, 1))
            positions = tour_positions(ys, holds, moves, eases, fps)
            info.update(max_scroll=max_scroll, stops_px=resolved, frames=len(positions))
            scroll_js = ("(y) => { const s = document.querySelector('[data-ck-scroller]');"
                         " s ? s.scrollTo(0, y) : window.scrollTo(0, y); }")
            if deterministic:   # se pausa ANTES de colocar el scroll: lo que se anima al entrar empieza en el fotograma 0
                now = await page.evaluate("() => Date.now()")
                await page.clock.pause_at(int(now) + 50)
            await page.evaluate(scroll_js, positions[0])
            await page.wait_for_timeout(int(params.get("pre_ms", 700)))
            shot: dict[str, Any] = {"type": "jpeg", "quality": int(params.get("jpeg_quality", 95)), "caret": "hide"}
            if params.get("clip"):
                c = params["clip"]
                shot["clip"] = {"x": float(c.get("x", 0)), "y": float(c["y"]), "width": float(c.get("w", info["viewport"]["width"])),
                                "height": float(c["h"])}
            frame_ms = 1000.0 / fps
            for i, y in enumerate(positions):
                await page.evaluate(scroll_js, y)
                if deterministic:
                    await page.clock.run_for(int(round((i + 1) * frame_ms)) - int(round(i * frame_ms)))
                    await page.evaluate(_SEEK_JS, [i * frame_ms, bool(params.get("restart_media"))])
                await page.screenshot(path=str(frames_dir / f"f_{i:05d}.jpg"), **shot)
        finally:
            await browser.close()
    return info


def record_tour(url: str, out: Path, params: dict[str, Any] | None = None) -> dict:
    """MP4 (H.264, fps fijo) de un recorrido por la web real con paradas y animaciones a velocidad real.

    params: viewport/scale/dark/hide/css (como `capture`), `stops` [{y | selector | text, align top|center|bottom,
    offset, hold s, move s, ease}], `fps` (30), `clip` {x?, y, w?, h} en px CSS del viewport, `out_size` [w, h]
    (escala y recorta al centro), `deterministic` (True), `crf` (16), `warm_to` (px CSS hasta donde precargar),
    `restart_media` (los <video> de la página empiezan en 0 en el primer fotograma), `settle_ms`, `keep_frames`.
    """
    _async_playwright()
    requiere("ffmpeg")
    params = dict(params or {})
    out = Path(out)
    frames_dir = out.with_suffix(".frames")
    shutil.rmtree(frames_dir, ignore_errors=True)
    frames_dir.mkdir(parents=True)
    try:
        info = _run(lambda: _tour(url, frames_dir, params))
        fps = int(params.get("fps", 30))
        vf = "crop=trunc(iw/2)*2:trunc(ih/2)*2"
        if params.get("out_size"):
            w, h = (int(v) for v in params["out_size"])
            vf = (f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,"
                  f"crop={w}:{h}:(iw-{w})/2:(ih-{h})/2,setsar=1")
        cmd = [requiere("ffmpeg"), "-y", "-v", "error", "-framerate", str(fps), "-i", str(frames_dir / "f_%05d.jpg"),
               "-vf", vf, "-c:v", "libx264", "-preset", "slow", "-crf", str(params.get("crf", 16)),
               "-pix_fmt", "yuv420p", "-r", str(fps), "-movflags", "+faststart", str(out)]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        if r.returncode != 0:
            raise RuntimeError(f"ffmpeg falló: {r.stderr[-400:]}")
        return info
    finally:
        if not params.get("keep_frames"):
            shutil.rmtree(frames_dir, ignore_errors=True)


# ───────────────────────────── SVG → PNG ─────────────────────────────

async def _svg_png(data: bytes, out: Path, w: int, h: int) -> None:
    async_playwright = _async_playwright()
    b64 = base64.b64encode(data).decode("ascii")
    html = ("<!doctype html><html><head><style>html,body{margin:0;padding:0;background:transparent}"
            f"img{{display:block;width:{w}px;height:{h}px}}</style></head>"
            f"<body><img id=\"svg\" alt=\"\" src=\"data:image/svg+xml;base64,{b64}\"></body></html>")
    async with async_playwright() as p:
        browser = await _launch(p)
        try:
            page = await browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
            await page.set_content(html, wait_until="load")
            try:
                await page.evaluate("() => document.getElementById('svg').decode()")
            except Exception as exc:  # noqa: BLE001 - la promesa de decode() se rechaza si el SVG no se pinta
                raise ValueError("Chromium no puede dibujar este SVG (¿está bien formado?)") from exc
            await page.screenshot(path=str(out), type="png", omit_background=True)
        finally:
            await browser.close()


def svg_a_png(svg: Path | str, out: Path | str, size: int = 1024) -> Path:
    """Rasteriza `svg` a PNG con fondo transparente, con el lado mayor en `size` px y el aspecto de su viewBox.

    Usa el Chromium de Playwright (extra `avanzado`); sin él lanza `PlaywrightNoDisponible`.
    """
    from .probe import svg_dimensiones

    _async_playwright()
    svg, out = Path(svg), Path(out)
    data = svg.read_bytes()
    _, _, vw, vh = svg_dimensiones(data)
    if b"http://www.w3.org/2000/svg" not in data:       # SVG copiado de una web: sin xmlns no se pinta como imagen
        data = data.replace(b"<svg", b'<svg xmlns="http://www.w3.org/2000/svg"', 1)
    k = int(size) / max(vw, vh)
    w, h = max(1, round(vw * k)), max(1, round(vh * k))
    out.parent.mkdir(parents=True, exist_ok=True)
    _run(lambda: _svg_png(data, out, w, h))
    return out
