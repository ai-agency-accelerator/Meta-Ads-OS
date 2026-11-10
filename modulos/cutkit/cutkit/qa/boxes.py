"""Cajas de texto visibles por instante: del DOM de HyperFrames (`window.__ckBoxes(t)`, exacto) o, si no hay
proyecto HF, del OCR del render. También lee los tweens GSAP del proyecto HF y, si el plan no trae caras, las estima
sobre los fotogramas del render con el detector de `cutkit.analyze` (Apple Vision en Mac, Haar de OpenCV en el resto).

OCR, por orden: Apple Vision (Mac con el extra `mac`, sin corrección de idioma para no «arreglar» tildes) →
`tesseract` del sistema si está en el PATH (`--psm 11` más una pasada `--psm 3` para el texto dentro de recuadros,
salida TSV) → sin OCR (la QA lo marca con `qa.sin_ocr` y no mide el texto). `CK_OCR=vision|tesseract|no` fuerza uno.

Formato esperado de `window.__ckBoxes(t)` (lo exporta `cutkit/motion` en `hf/boxes.js`; se acepta con tolerancia):
    [{"id"|"item": "it_012", "text": "…", "x": px, "y": px, "w": px, "h": px  (o "box": [x0, y0, x1, y1]),
      "fontSize"|"font_px": px, "role"|"track": "caption|key|headline|label|decorative", "opacity": 0..1}, …]
en píxeles del lienzo (1080×1920), origen arriba-izquierda. Si la función devuelve una promesa, se espera.
"""
from __future__ import annotations

import csv
import functools
import http.server
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path
from typing import Any

from .context import QAContext, TextBox, caption_words, item_texts, tokens

OcrLine = tuple[str, float, tuple[float, float, float, float]]   # texto, confianza 0..1, (x0, y0, x1, y1) px

# ───────────────────────────── DOM (Playwright)
_SEEK_AND_BOXES = """async (t) => {
  if (typeof window.__ckSeek === 'function') { const r = window.__ckSeek(t); if (r && r.then) await r; }
  else if (window.__timelines && window.__timelines.main) { window.__timelines.main.seek(t, false); }
  if (typeof window.__ckBoxes !== 'function') return null;
  let r = window.__ckBoxes(t); if (r && r.then) r = await r;
  // rectángulo del A-roll en pantalla (layout + cámara) y su opacidad efectiva, para situar la cara
  let cam = null;
  const root = document.getElementById('root');
  const v = document.querySelector('#ck-cam video') || document.getElementById('aroll');
  if (root && v) {
    const R = root.getBoundingClientRect(), q = v.getBoundingClientRect();
    const sx = (parseFloat(root.getAttribute('data-width')) || R.width) / R.width;
    const sy = (parseFloat(root.getAttribute('data-height')) || R.height) / R.height;
    let o = 1;
    for (let n = v; n && n.nodeType === 1; n = n.parentElement) {
      const cs = getComputedStyle(n);
      if (cs.display === 'none' || cs.visibility === 'hidden') { o = 0; break; }
      o *= parseFloat(cs.opacity || '1');
    }
    cam = [(q.left - R.left) * sx, (q.top - R.top) * sy, q.width * sx, q.height * sy, o];
  }
  return {r, cam};
}"""

_TWEENS = """() => {
  const tl = window.__timelines && window.__timelines.main; if (!tl || !tl.getChildren) return null;
  const skip = new Set(['ease','duration','delay','onComplete','onStart','onUpdate','immediateRender','overwrite','stagger',
    'data','id','repeat','yoyo','paused','callbackScope','runBackwards','startAt','lazy','inherit','keyframes','repeatDelay',
    'onCompleteParams','onStartParams','onUpdateParams','yoyoEase','reversed','smoothChildTiming','autoRemoveChildren']);
  const out = [];
  for (const tw of tl.getChildren(true, true, false)) {
    let s = tw.startTime(), p = tw.parent;
    while (p && p !== tl) { s = p.startTime() + s / (p.timeScale() || 1); p = p.parent; }
    const v = tw.vars || {}; const props = Object.keys(v).filter(k => !skip.has(k));
    let targets = []; try { targets = tw.targets().slice(0, 3).map(e => (e && (e.id || (e.className && e.className.baseVal === undefined ? e.className : '') || e.tagName)) + ''); } catch (e) {}
    const ease = typeof v.ease === 'string' ? v.ease : (v.ease ? 'custom' : 'default');
    const vals = {}; for (const k of props) { const x = v[k]; if (typeof x === 'number' || typeof x === 'string') vals[k] = x; }
    out.push({start: s, dur: tw.duration(), ease, props, vals, targets, stagger: v.stagger !== undefined,
              role: (v.data && (v.data.role || v.data.kind)) || null});
  }
  return out;
}"""

# Hojas de texto de los gráficos (no subtítulos) con su visibilidad real: opacidad × parte NO recortada por un antepasado
# con overflow oculto (las máscaras de subida dejan el texto fuera de su caja). Para la puerta mo.text_entry.
_TEXT_LEAVES = r"""async (t) => {
  if (typeof window.__ckSeek === 'function') { const r = window.__ckSeek(t); if (r && r.then) await r; }
  const root = document.getElementById('root'); if (!root) return [];
  const R = root.getBoundingClientRect();
  const sx = (parseFloat(root.getAttribute('data-width')) || R.width) / R.width;
  const sy = (parseFloat(root.getAttribute('data-height')) || R.height) / R.height;
  const win = (el) => { for (let n = el; n && n.nodeType === 1; n = n.parentElement) { if (n.hasAttribute('data-start') && !n.hasAttribute('data-composition-id')) {
    const s = parseFloat(n.getAttribute('data-start')) || 0, d = n.getAttribute('data-duration');
    if (t < s - 1e-6) return false; if (d != null && t >= s + parseFloat(d) - 1e-6) return false; } } return true; };
  const out = [];
  for (const el of root.querySelectorAll('*')) {
    if (el.tagName === 'SCRIPT' || el.tagName === 'STYLE' || el.namespaceURI === 'http://www.w3.org/2000/svg') continue;
    let direct = ''; for (let c = el.firstChild; c; c = c.nextSibling) if (c.nodeType === 3) direct += c.nodeValue;
    direct = direct.replace(/\s+/g, ' ').trim(); if (!direct) continue;
    const item = el.closest('.ck-item'); if (!item || /ck-track-caption/.test(item.className)) continue;
    if (!win(el)) continue;
    let op = 1, hidden = false;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement) { const cs = getComputedStyle(n); if (cs.display === 'none' || cs.visibility === 'hidden') { hidden = true; break; } op *= parseFloat(cs.opacity || '1'); }
    if (hidden || op < 0.02) continue;
    const r = el.getBoundingClientRect(); if (r.width < 1 || r.height < 1) continue;
    let keep = 1;
    for (let n = el.parentElement; n && n !== root; n = n.parentElement) {
      const cs = getComputedStyle(n);
      if (cs.overflow === 'hidden' || cs.overflowX === 'hidden' || cs.overflowY === 'hidden' || cs.overflow === 'clip') {
        const q = n.getBoundingClientRect();
        const ix = Math.max(0, Math.min(r.right, q.right) - Math.max(r.left, q.left)), iy = Math.max(0, Math.min(r.bottom, q.bottom) - Math.max(r.top, q.top));
        keep = Math.min(keep, (ix * iy) / (r.width * r.height));
      }
      const cp = cs.clipPath; if (cp && cp !== 'none' && /inset\(/.test(cp)) { const m = cp.match(/inset\(([^)]*)\)/); if (m) { const v = m[1].split(/\s+/).map(parseFloat); if (v.some((x) => x > 1)) keep = Math.min(keep, 0.5); } }
    }
    // id estable del nodo entre instantes (para seguir la MISMA hoja aunque se mueva: recentrados, filas que suben)
    if (!el.__ckq) { window.__ckqN = (window.__ckqN || 0) + 1; el.__ckq = window.__ckqN; }
    out.push({ item: item.id, nid: el.__ckq, text: direct, x: (r.left - R.left) * sx, y: (r.top - R.top) * sy, w: r.width * sx, h: r.height * sy, vis: op * keep });
  }
  return out;
}"""


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a: Any) -> None:  # silencio
        pass


class _QuietServer(http.server.ThreadingHTTPServer):
    def handle_error(self, request: Any, client_address: Any) -> None:   # el navegador corta descargas de vídeo: normal
        pass


def _serve(root: Path) -> tuple[http.server.ThreadingHTTPServer, str]:
    h = functools.partial(_QuietHandler, directory=str(root))
    srv = _QuietServer(("127.0.0.1", 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def _parse_dom_box(t: float, b: dict[str, Any]) -> TextBox | None:
    try:
        if "box" in b and isinstance(b["box"], (list, tuple)):
            x0, y0, x1, y1 = map(float, b["box"][:4])
        else:
            x0, y0 = float(b.get("x", b.get("left"))), float(b.get("y", b.get("top")))
            x1, y1 = x0 + float(b.get("w", b.get("width"))), y0 + float(b.get("h", b.get("height")))
    except Exception:
        return None
    fp = b.get("font_px", b.get("fontSize", b.get("font_size")))
    try:
        fp = float(str(fp).replace("px", "")) if fp is not None else None
    except Exception:
        fp = None
    return TextBox(t=t, text=str(b.get("text", "")), x0=x0, y0=y0, x1=x1, y1=y1, source="dom",
                   item=b.get("item") or b.get("item_id") or b.get("id"), role=b.get("role") or b.get("track"),
                   font_px=fp, opacity=float(b.get("opacity", 1.0) or 0.0))


def dom_probe(ctx: QAContext, fps: float) -> bool:
    """Abre hf/index.html, lee los tweens y, si existe `__ckBoxes`, las cajas a `fps`. True si hubo cajas del DOM."""
    hf = ctx.vdir / "hf"
    if not (hf / "index.html").exists():
        return False
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        ctx.notes.append(f"Playwright no disponible ({exc}); se usa OCR.")
        return False
    srv, base = _serve(hf)
    got = False
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch()
            pg = br.new_page(viewport={"width": ctx.timeline.width, "height": ctx.timeline.height})
            # sin el runtime de HyperFrames nadie crea window.__timelines: lo creamos antes de que corra el proyecto
            pg.add_init_script("window.__timelines = window.__timelines || {};")
            pg.goto(f"{base}/index.html", wait_until="load", timeout=60000)
            try:
                pg.wait_for_function("() => !!(window.__timelines && window.__timelines.main)", polling=100, timeout=20000)
            except Exception:
                ctx.notes.append("El proyecto HF no registró window.__timelines.main en 20 s.")
            try:
                tw = pg.evaluate(_TWEENS)
                if tw:
                    ctx.tweens = tw
            except Exception as exc:
                ctx.notes.append(f"No se pudieron leer los tweens GSAP: {type(exc).__name__}")
            has = pg.evaluate("() => typeof window.__ckBoxes === 'function'")
            if has:
                n = int(ctx.duration * fps) + 1
                for k in range(n):
                    t = round(k / fps, 3)
                    res = pg.evaluate(_SEEK_AND_BOXES, t) or {}
                    if res.get("cam"):
                        ctx.cam_rects.append((t, *map(float, res["cam"])))
                    r = res.get("r") or []
                    if isinstance(r, dict):   # formato de cutkit/motion: {t, blocks:[…], leaves:[…]}
                        blocks = r.get("blocks") or []
                        leaves = []
                        for lf in r.get("leaves") or []:
                            cx, cy = lf.get("x", 0) + lf.get("w", 0) / 2, lf.get("y", 0) + lf.get("h", 0) / 2
                            owner = next((bl for bl in blocks if bl.get("x", 0) <= cx <= bl.get("x", 0) + bl.get("w", 0)
                                          and bl.get("y", 0) <= cy <= bl.get("y", 0) + bl.get("h", 0)), None)
                            leaves.append(dict(lf, item=owner and owner.get("item"),
                                               role=owner and (owner.get("kind") or owner.get("component"))))
                        r = leaves or blocks
                    for b in r:
                        tb = _parse_dom_box(t, b)
                        if tb and tb.opacity > 0.05 and tb.w > 1 and tb.h > 1:
                            ctx.boxes.append(tb)
                got = True
                ctx.boxes_source = f"dom@{fps:g}fps"
                try:
                    _entry_probe(pg, ctx)
                except Exception as exc:  # noqa: BLE001
                    ctx.notes.append(f"mo.text_entry: no se pudo sondear ({type(exc).__name__}: {str(exc)[:120]})")
                try:
                    _parity_probe(pg, ctx)
                except Exception as exc:  # noqa: BLE001
                    ctx.notes.append(f"ly.line_parity: no se pudo sondear ({type(exc).__name__}: {str(exc)[:120]})")
            else:
                ctx.notes.append("hf/index.html sin window.__ckBoxes: zonas seguras y tamaños por OCR.")
            br.close()
    except Exception as exc:
        ctx.notes.append(f"Fallo al sondear el DOM de HF ({type(exc).__name__}: {str(exc)[:160]}); se usa OCR.")
        got = False
    finally:
        srv.shutdown()
    return got


# ───────────────────────────── OCR (Apple Vision → tesseract → sin OCR)
_LANGS_VISION = ("es-ES", "en-US")      # español primero; el inglés ayuda con nombres de herramientas
_LANGS_TESS = ("spa", "eng")
_TESS_MIN_WORD_CONF = 30.0              # palabras de tesseract por debajo: ruido de la imagen leído como texto


def _vision_disponible() -> bool:
    return sys.platform == "darwin" and all(importlib.util.find_spec(m) is not None for m in ("Vision", "objc"))


def ocr_backend() -> tuple[str | None, str]:
    """(motor, motivo): motor = 'vision' | 'tesseract' | None; motivo explica por qué no hay OCR."""
    pref = os.environ.get("CK_OCR", "auto").strip().lower()
    if pref in ("no", "0", "off", "ninguno", "none"):
        return None, "desactivado con CK_OCR=no"
    vision, tess = _vision_disponible(), shutil.which("tesseract") is not None
    if pref == "vision":
        return ("vision", "") if vision else (None, "CK_OCR=vision pero Apple Vision no está (extra `mac`, solo Mac)")
    if pref == "tesseract":
        return ("tesseract", "") if tess else (None, "CK_OCR=tesseract pero tesseract no está en el PATH")
    if vision:
        return "vision", ""
    if tess:
        return "tesseract", ""
    return None, "no hay Apple Vision (extra `mac`) ni tesseract en el PATH"


def _ocr_vision(path: str) -> list[OcrLine] | None:
    """Apple Vision sin corrección de idioma (la corrección «arregla» palabras y escondería errores de tildes).
    None si Vision no está o falla tres veces seguidas (fallos transitorios del motor neuronal)."""
    try:
        import objc
        import Vision
        from PIL import Image

        with Image.open(path) as im:
            W, H = im.size
            buf = io.BytesIO()
            im.convert("RGB").save(buf, format="PNG")
    except Exception:  # noqa: BLE001
        return None
    for intento in range(3):
        out: list[OcrLine] = []
        with objc.autorelease_pool():
            req = Vision.VNRecognizeTextRequest.alloc().init()
            req.setRecognitionLevel_(0)                     # 0 = precisa
            req.setUsesLanguageCorrection_(False)
            req.setRecognitionLanguages_(list(_LANGS_VISION))
            handler = Vision.VNImageRequestHandler.alloc().initWithData_options_(buf.getvalue(), None)
            ret = handler.performRequests_error_([req], None)
            ok = ret[0] if isinstance(ret, tuple) else bool(ret)
            if ok:
                for r in req.results() or []:
                    bb = r.boundingBox()                    # normalizada, origen abajo-izquierda
                    x, y, w, h = bb.origin.x, bb.origin.y, bb.size.width, bb.size.height
                    try:
                        cand = r.topCandidates_(1)[0]
                        text, conf = str(cand.string()), float(cand.confidence())
                    except Exception:  # noqa: BLE001
                        continue
                    out.append((text, conf, (x * W, (1 - y - h) * H, (x + w) * W, (1 - y) * H)))
                return out
        time.sleep(0.3 * (intento + 1))
    return None


@functools.lru_cache(maxsize=1)
def _tess_langs() -> tuple[str | None, list[str]]:
    """('spa+eng' o lo que haya instalado, idiomas que faltan)."""
    try:
        r = subprocess.run([shutil.which("tesseract") or "tesseract", "--list-langs"], capture_output=True, text=True,
                           timeout=30)
        have = {ln.strip() for ln in (r.stdout + "\n" + r.stderr).splitlines() if ln.strip() and " " not in ln.strip()}
    except (OSError, subprocess.SubprocessError):
        have = set()
    usar = [lg for lg in _LANGS_TESS if lg in have]
    return ("+".join(usar) or None), [lg for lg in _LANGS_TESS if lg not in have]


@functools.lru_cache(maxsize=1)
def _tess_sauvola() -> bool:
    """¿tesseract ≥ 5? (umbral local Sauvola: aguanta degradados y fondos de vídeo; en la 4 no existe)."""
    try:
        r = subprocess.run([shutil.which("tesseract") or "tesseract", "--version"], capture_output=True, text=True,
                           timeout=30)
        ver = (r.stdout or r.stderr).split()[1]
        return int(ver.lstrip("v").split(".")[0]) >= 5
    except (OSError, subprocess.SubprocessError, IndexError, ValueError):
        return False


def _lineas(words: list[tuple[str, float, float, float, float, float]]) -> list[OcrLine]:
    """Une palabras de tesseract (texto, conf, x0, y0, x1, y1) en líneas: misma franja vertical y hueco pequeño."""
    lines: list[list] = []
    for w in sorted(words, key=lambda w: w[2]):            # de izquierda a derecha
        h = w[5] - w[3]
        for ln in lines:
            lh = ln[-1][5] - ln[-1][3]
            solape = min(w[5], ln[-1][5]) - max(w[3], ln[-1][3])
            hueco = w[2] - max(x[4] for x in ln)            # negativo si las cajas se pisan (tesseract a veces las alarga)
            if solape >= 0.5 * min(h, lh) and hueco <= 1.2 * max(h, lh):
                ln.append(w)
                break
        else:
            lines.append([w])
    out: list[OcrLine] = []
    for ln in lines:
        out.append((" ".join(x[0] for x in ln), sum(x[1] for x in ln) / len(ln),
                    (min(x[2] for x in ln), min(x[3] for x in ln), max(x[4] for x in ln), max(x[5] for x in ln))))
    return out


# Pasadas de tesseract (salida TSV). `--psm 11` (texto disperso: subtítulos y rótulos sueltos) descarta el texto que
# va dentro de un recuadro (tarjetas, botones); `--psm 3` (segmentación automática) lo recupera. Medido en fotogramas
# sintéticos 1080×1920 con subtítulos con contorno, palabra resaltada, tarjetas y paneles de color: psm 11 solo, 18/33
# palabras; psm 11 + psm 3 con umbral Sauvola, 33/33 y casi sin ruido.
_TESS_PASADAS = ("11", "3")


def _palabras(exe: str, path: str, psm: str, langs: str | None, sauvola: bool) -> list[tuple] | None:
    cmd = [exe, path, "stdout", "--psm", psm, *(["-l", langs] if langs else []),
           *(["-c", "thresholding_method=2"] if sauvola else []), "tsv"]
    env = dict(os.environ, OMP_THREAD_LIMIT="1")    # ya se paraleliza por fotogramas
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
                           env=env)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    words = []
    for row in csv.DictReader(io.StringIO(r.stdout), delimiter="\t", quoting=csv.QUOTE_NONE):
        try:
            if row.get("level") != "5":
                continue
            text, conf = (row.get("text") or "").strip(), float(row.get("conf") or -1)
            if not text or conf < _TESS_MIN_WORD_CONF:
                continue
            x0, y0 = float(row["left"]), float(row["top"])
            words.append((text, conf / 100.0, x0, y0, x0 + float(row["width"]), y0 + float(row["height"])))
        except (TypeError, ValueError, KeyError):
            continue
    return words


def _iou(a: tuple, b: tuple) -> float:
    inter = max(0.0, min(a[4], b[4]) - max(a[2], b[2])) * max(0.0, min(a[5], b[5]) - max(a[3], b[3]))
    union = (a[4] - a[2]) * (a[5] - a[3]) + (b[4] - b[2]) * (b[5] - b[3]) - inter
    return inter / union if union > 0 else 0.0


def _sin_duplicados(words: list[tuple]) -> list[tuple]:
    """La misma palabra leída en dos pasadas (IoU > 0,5): se queda la de más confianza."""
    kept: list[tuple] = []
    for w in sorted(words, key=lambda w: -w[1]):
        if not any(_iou(w, k) > 0.5 for k in kept):
            kept.append(w)
    return kept


def _ocr_tesseract(path: str, langs: str | None = None, sauvola: bool = False) -> list[OcrLine] | None:
    """tesseract del sistema: pasadas `--psm 11` y `--psm 3` unidas, en líneas. None si fallan las dos."""
    exe = shutil.which("tesseract")
    if exe is None:
        return None
    pasadas = [_palabras(exe, path, psm, langs, sauvola) for psm in _TESS_PASADAS]
    if all(p is None for p in pasadas):
        return None
    return _lineas(_sin_duplicados([w for p in pasadas if p for w in p]))


def _sin_ocr(ctx: QAContext, motivo: str) -> None:
    from ..sistema import arreglo

    ctx.boxes_source = "sin OCR"
    ctx.metrics["ocr"] = {"motor": None, "motivo": motivo}
    ctx.add("qa.sin_ocr", "warn",
            f"Sin OCR ({motivo}): no se miden zonas seguras, tamaños ni solapes del texto del render; revísalos a ojo "
            f"en las hojas de contacto. Para medirlos instala tesseract ({arreglo('tesseract')}) o, en Mac, el extra "
            "`mac` (uv sync --project modulos/cutkit --extra mac).", evidence={"motivo": motivo})


def ocr_boxes(ctx: QAContext, workers: int = 4) -> None:
    frames = ctx.frames_full
    if not frames:
        ctx.notes.append("Sin fotogramas para OCR.")
        return
    motor, motivo = ocr_backend()
    if motor is None:
        _sin_ocr(ctx, motivo)
        return
    paths = [str(p) for _, p in frames]
    res: list[list[OcrLine] | None]
    if motor == "vision":
        try:
            with ProcessPoolExecutor(max_workers=workers) as ex:
                res = list(ex.map(_ocr_vision, paths, chunksize=4))
        except Exception as exc:  # noqa: BLE001
            ctx.notes.append(f"OCR en paralelo falló ({type(exc).__name__}); se hace en serie.")
            res = [_ocr_vision(p) for p in paths]
    else:
        langs, faltan = _tess_langs()
        if "spa" in faltan:
            from ..sistema import arreglo

            ctx.notes.append(f"tesseract sin el idioma español (spa): leerá peor las tildes. Instálalo: "
                             f"{arreglo('tesseract')}.")
        # cada tesseract va a un hilo (OMP_THREAD_LIMIT=1): se reparten los fotogramas entre los núcleos
        with ThreadPoolExecutor(max_workers=max(1, workers, min(8, os.cpu_count() or 1))) as ex:
            res = list(ex.map(functools.partial(_ocr_tesseract, langs=langs, sauvola=_tess_sauvola()), paths))
    fallos = sum(r is None for r in res)
    if fallos == len(res):
        _sin_ocr(ctx, f"{motor} falló en todos los fotogramas")
        return
    if fallos:
        ctx.notes.append(f"OCR ({motor}) falló en {fallos} de {len(res)} fotogramas: esos instantes no se miden.")
    for (t, _), lines in zip(frames, res):
        for text, conf, (x0, y0, x1, y1) in lines or []:
            if conf < 0.4 or len(text.strip()) < 2:
                continue
            ctx.boxes.append(TextBox(t=t, text=text, x0=x0, y0=y0, x1=x1, y1=y1, source="ocr", conf=conf))
    ctx.boxes_source = f"ocr@{ctx.cfg['sampling']['ocr_fps']:g}fps"
    ctx.metrics["ocr"] = {"motor": motor, "fotogramas": len(res), "fallos": fallos}
    attribute(ctx)


def attribute(ctx: QAContext) -> None:
    """Atribuye cada caja OCR al ítem (subtítulo o gráfico) cuyo texto la contiene."""
    wt = ctx.word_text()
    cache: dict[str, set[str]] = {}

    def item_tok(it) -> set[str]:
        if it.id not in cache:
            txt = item_texts(it)
            if it.track == "caption":
                txt += [wt.get(w, "") for w in caption_words(it, ctx.timeline.word_times)]
                txt += [x.get("text", "") for x in (it.props.get("words") or []) if isinstance(x, dict)]
            cache[it.id] = set(tokens(" ".join(txt)))
        return cache[it.id]
    for b in ctx.boxes:
        if b.source != "ocr" or b.item:
            continue
        bt = tokens(b.text)
        if not bt:
            continue
        best, score = None, 0.0
        for it in ctx.active(b.t - 0.05, b.t + 0.05, ["caption", "graphic", "broll", "overlay", "layout"]):
            it_t = item_tok(it)
            if not it_t:
                continue
            sc = sum(1 for w in bt if w in it_t) / len(bt)
            if it.track == "caption" and sum(1 for w in it_t if w in bt) / len(it_t) < 0.5:
                continue   # una palabra suelta («GPT») no convierte la etiqueta de un gráfico en subtítulo
            if sc > score or (sc == score and best is not None and best.track == "caption" and it.track != "caption"):
                best, score = it, sc
        if best is not None and score >= 0.6:
            b.item = best.id
            b.role = "caption" if best.track == "caption" else (best.props.get("role") or best.track)


# ───────────────────────────── caras en el render (detector de cutkit.analyze: Apple Vision u OpenCV Haar)
_FACE_W = 540                                        # ancho de análisis (px): rápido y suficiente para caras de A-roll
_CARAS: dict[tuple, tuple[str, list]] = {}         # caché de la última detección (la usan las dos funciones de abajo)


def _caras_render(ctx: QAContext) -> tuple[str, list[tuple[float, tuple[float, float, float, float], int, int]]]:
    """(motor, [(t, (x, y, w, h) normalizados de la cara mayor, ancho, alto del fotograma)]) del render."""
    key = tuple((t, str(p)) for t, p in ctx.frames_full)
    if key in _CARAS:
        return _CARAS[key]
    import cv2

    from ..analyze import _detector_caras

    detectar = _detector_caras()
    motor = "Apple Vision" if detectar.__name__ == "vision" else "OpenCV (Haar)"
    out = []
    for t, p in ctx.frames_full:
        img = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        H, W = img.shape[:2]
        if W > _FACE_W:
            img = cv2.resize(img, (_FACE_W, max(1, round(H * _FACE_W / W))), interpolation=cv2.INTER_AREA)
        try:
            det = detectar(img)
        except Exception:  # noqa: BLE001 - un fotograma raro no tumba la detección
            continue
        if det:
            out.append((t, tuple(float(v) for v in det[0][:4]), W, H))
    _CARAS.clear()
    _CARAS[key] = (motor, out)
    return motor, out


def detect_faces(ctx: QAContext) -> None:
    """Respaldo si el plan no trae caras (`render_spec.aroll.faces` ni el MediaIndex): las del render."""
    if ctx.faces or not ctx.frames_full:
        return
    try:
        motor, det = _caras_render(ctx)
    except Exception as exc:  # noqa: BLE001
        ctx.notes.append(f"No se pudieron detectar caras en el render ({type(exc).__name__}: {str(exc)[:120]}).")
        return
    ctx.faces = [(t, x, y, w, h) for t, (x, y, w, h), _, _ in det]
    ctx.notes.append(f"Caras estimadas con {motor} en {len(det)}/{len(ctx.frames_full)} fotogramas del render "
                     "(el plan no trae render_spec.aroll.faces).")


def stale_render(ctx: QAContext) -> float:
    """Segundos que el proyecto HF o la timeline son MÁS NUEVOS que render.mp4 (0 si el render está al día)."""
    r = ctx.render.stat().st_mtime
    newer = [p.stat().st_mtime - r for p in (ctx.vdir / "hf" / "index.html", ctx.vdir / "timeline.json") if p.exists()]
    return max([0.0] + newer)


def detect_render_faces(ctx: QAContext) -> None:
    """Zonas de ojos y boca EN EL RENDER (fotogramas del OCR): verdad del píxel cuando las cajas vienen del OCR o el
    render no corresponde a la compilación actual. El detector da la caja de la cara, no puntos faciales: ojos y boca
    salen de las mismas proporciones de la caja que usa `checks_captions` con las caras del plan."""
    if not ctx.frames_full:
        return
    from .checks_captions import EYES, MOUTH

    try:
        motor, det = _caras_render(ctx)
    except Exception as exc:  # noqa: BLE001
        ctx.notes.append(f"No se pudieron detectar caras en el render ({type(exc).__name__}: {str(exc)[:120]}).")
        return
    out = []
    for t, (x, y, w, h), W, H in det:
        fx0, fy0, fw, fh = x * W, y * H, w * W, h * H
        eyes = (fx0 + EYES[0] * fw, fy0 + EYES[1] * fh, fx0 + EYES[2] * fw, fy0 + EYES[3] * fh)
        mouth = (fx0 + MOUTH[0] * fw, fy0 + MOUTH[1] * fh, fx0 + MOUTH[2] * fw, fy0 + MOUTH[3] * fh)
        out.append((t, eyes, mouth))
    ctx.render_faces = out
    if out:
        ctx.notes.append(f"Ojos y boca del render estimados con {motor} en {len(out)}/{len(ctx.frames_full)} "
                         "fotogramas (proporciones de la caja facial).")


# 20-oct-2026 (regla del orquestador para la v002 de un vídeo de prueba, kit v14): una hoja de texto tiene entrada si llega al
# 90 % de lo que llega a verse en ≥ 5 f (contando su primer fotograma visible) O recorre ≥ 20 px (centro o semitamaño de su
# caja) entre su primer fotograma visible y 12 f después. Antes: ≥ 80 % en su primer fotograma y quieta (dejaba pasar los
# fundidos de 6–8 f que llegan al 90 % en 4 f: «ya puesto» a la vista).
ENTRY_FIRST_FRAMES = 8     # la hoja puede aparecer en cualquiera de los 8 primeros fotogramas del bloque o de su cue
ENTRY_MIN_FRAMES = 5       # fotogramas hasta el 90 % de su meseta (contando el primero visible) para contar como fundido
ENTRY_MIN_PX = 20.0        # …o recorrido mínimo (px) de su caja en la entrada
ENTRY_SPAN_FRAMES = 12     # la meseta y el recorrido se miden 12 f después del primer visible (o al acabar el bloque)


# ly.line_parity (18-oct-2026): rótulos paralelos de un mismo grupo (`data-ck-group`, los marca gx.lineParity) con su
# número de líneas REAL en pantalla (tops distintos de los rectángulos de línea del texto)
_PARITY = r"""async (t) => {
  if (typeof window.__ckSeek === 'function') { const r = window.__ckSeek(t); if (r && r.then) await r; }
  const groups = {};
  document.querySelectorAll('[data-ck-group]').forEach((n) => {
    const item = n.closest('.ck-item'); if (!item) return;
    for (let e = n; e && e.nodeType === 1; e = e.parentElement) { const cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden') return; }
    const range = document.createRange(); range.selectNodeContents(n);
    const rs = Array.from(range.getClientRects()).filter((q) => q.width > 1 && q.height > 1);
    if (!rs.length) return;
    const tops = []; rs.sort((a, b) => a.top - b.top).forEach((q) => { if (!tops.length || q.top - tops[tops.length - 1] > q.height * 0.5) tops.push(q.top); });
    const txt = (n.innerText || n.textContent || '').replace(/\s+/g, ' ').trim();   // innerText: el <br> cuenta como espacio
    const key = item.id + '|' + n.getAttribute('data-ck-group');
    (groups[key] = groups[key] || []).push({ text: txt.slice(0, 40), lines: tops.length, single: n.getAttribute('data-ck-single') === '1' || !/ /.test(txt) });
  });
  return Object.keys(groups).map((k) => ({ key: k, labels: groups[k] }));
}"""


def _parity_probe(pg: Any, ctx: QAContext) -> None:
    """ly.line_parity: en cada grupo de rótulos paralelos (mismo item y grupo), ¿todos con el mismo número de líneas?
    Un rótulo de una sola palabra no se puede partir: no cuenta como discrepancia si el resto va en dos. Mide cada item a
    mitad de su vida. Guarda los grupos que fallan en ctx.metrics["_line_parity"] (lo convierte checks_motion)."""
    found, seen = [], set()
    for it in ctx.timeline.items:
        if it.track not in ("graphic", "overlay") or it.t1 - it.t0 < 0.2:
            continue
        for g in pg.evaluate(_PARITY, round((it.t0 + it.t1) / 2, 3)) or []:
            if not g["key"].startswith(it.id + "|") or g["key"] in seen:
                continue
            seen.add(g["key"])
            multi = [x for x in g["labels"] if not x["single"]]
            counts = sorted({x["lines"] for x in multi})
            if len(counts) > 1 or (any(x["lines"] > 1 for x in multi) and any(x["single"] and x["lines"] > 1 for x in g["labels"])):
                found.append({"item": it.id, "grupo": g["key"].split("|", 1)[1], "t": round((it.t0 + it.t1) / 2, 3),
                              "rotulos": g["labels"][:8], "decision_ids": list(it.decision_ids or [])})
    ctx.metrics["_line_parity"] = {"grupos": len(seen), "fallos": found}


def _entry_probe(pg: Any, ctx: QAContext) -> None:
    """mo.text_entry: en los primeros fotogramas de cada gráfico de texto (y de cada cue), ¿aparece texto sin entrada?
    Para cada hoja de texto NUEVA (no estaba en el fotograma anterior ni continúa de un plano anterior en el mismo sitio)
    cuyo primer fotograma visible cae en los 8 primeros del bloque o de su cue, se mide:
      · n90: fotogramas hasta llegar al 90 % de su meseta (opacidad × parte no recortada por su máscara; la meseta es lo
        máximo que llega a verse en sus 12 f siguientes: un rótulo bajo un grupo atenuado no tiene que llegar a 0,9);
      · recorrido: lo que se mueve su caja (centro o semitamaño) entre el primer visible y 12 f después.
    Falla si n90 < 5 f Y recorrido < 20 px (20-oct-2026, kit v14). El tecleo y las cascadas letra a letra (hojas de una
    letra) no cuentan. Con el bloque en t = 0 no hay fotograma anterior: lo visible en el primero NO cuenta como «ya en
    pantalla» (antes `max(0, t − 1 f)` lo daba por continuado y el rótulo del primer fotograma se escapaba).
    Guarda los casos en ctx.metrics["_text_entry"] (lo convierte en issues checks_motion)."""
    fps = float(getattr(ctx.timeline, "fps", 30) or 30)
    fr = 1.0 / fps
    skip = ("media.", "layout.", "camera.", "transition", "caption", "scene.capture3d", "scene.logo")
    items = [it for it in ctx.timeline.items if it.track in ("graphic", "overlay") and it.component
             and not str(it.component).startswith(skip)]
    cache: dict[float, list[dict]] = {}

    def leaves(t: float) -> list[dict]:
        if t < -1e-6:                       # antes del primer fotograma del vídeo no hay nada en pantalla
            return []
        t = round(max(0.0, t), 4)
        if t not in cache:
            try:
                cache[t] = pg.evaluate(_TEXT_LEAVES, t) or []
            except Exception:
                cache[t] = []
        return cache[t]

    def node(L: list[dict], a: dict) -> dict | None:
        """La misma hoja en otro instante: por id de nodo (si el sondeo lo da) o por texto e item."""
        if a.get("nid") is not None:
            return next((b for b in L if b.get("nid") == a["nid"]), None)
        return next((b for b in L if b["item"] == a["item"] and b["text"] == a["text"]), None)

    def travel(a: dict, b: dict) -> float:
        ca = (a["x"] + a["w"] / 2, a["y"] + a["h"] / 2)
        cb = (b["x"] + b["w"] / 2, b["y"] + b["h"] / 2)
        return max(((ca[0] - cb[0]) ** 2 + (ca[1] - cb[1]) ** 2) ** 0.5, abs(a["w"] - b["w"]) / 2, abs(a["h"] - b["h"]) / 2)

    found: list[dict] = []
    for it in items:
        cues = sorted(float(v) for v in (it.cues or {}).values()
                      if isinstance(v, (int, float)) and it.t0 + fr < float(v) < it.t1 - 0.12)
        for tau in [it.t0] + cues:
            if it.t1 - tau <= 6 * fr:
                continue
            frames = [tau + (j + 0.5) * fr for j in range(ENTRY_FIRST_FRAMES) if tau + (j + 0.5) * fr < it.t1 - 5 * fr]
            before = leaves(tau - fr)
            L0 = [x for x in before if x["vis"] >= 0.3]      # ya en pantalla (continúa un plano anterior)
            seen = {x.get("nid") for x in before if x["item"] == it.id and x["vis"] > 0.02}
            seen_txt = {x["text"] for x in before if x["item"] == it.id and x["vis"] > 0.02}
            done: set = set()
            for tj in frames:
                for a in leaves(tj):
                    if a["item"] != it.id or a["vis"] <= 0.02:
                        continue
                    key = a.get("nid") if a.get("nid") is not None else a["text"]
                    if key in done or (a.get("nid") is not None and a["nid"] in seen) \
                            or (a.get("nid") is None and a["text"] in seen_txt):
                        done.add(key)
                        continue
                    done.add(key)                                  # su primer fotograma visible es tj
                    if len(a["text"].strip()) <= 1:               # tecleo / cascada letra a letra
                        continue
                    if any(b["text"] == a["text"] and abs(b["x"] - a["x"]) <= 6 and abs(b["y"] - a["y"]) <= 6 for b in L0):
                        continue
                    seq = [a] + [node(leaves(tj + k * fr), a) for k in range(1, ENTRY_MIN_FRAMES)]
                    t_far = min(tj + ENTRY_SPAN_FRAMES * fr, it.t1 - 1.5 * fr)
                    far = node(leaves(t_far), a) if t_far > tj + fr else None
                    known = [b for b in seq if b is not None] + ([far] if far is not None else [])
                    peak = max(b["vis"] for b in known)
                    n90 = next((k + 1 for k, b in enumerate(seq) if b is not None and b["vis"] >= 0.9 * peak), None)
                    if n90 is None or n90 >= ENTRY_MIN_FRAMES:     # llega al 90 % en ≥ 5 f: tiene fundido
                        continue
                    mov = max(travel(a, b) for b in known[1:]) if len(known) > 1 else 0.0
                    if mov >= ENTRY_MIN_PX:
                        continue
                    found.append({"item": it.id, "t": round(tau, 3), "t_visible": round(tj, 3), "texto": a["text"][:60],
                                  "vis": round(a["vis"], 2), "en_cue": tau != it.t0, "n90_f": n90, "recorrido_px": round(mov, 1),
                                  "prueba": (f"llega al 90 % en {n90} f y se mueve {mov:.0f} px "
                                             f"(mínimo: {ENTRY_MIN_FRAMES} f o {ENTRY_MIN_PX:.0f} px)"),
                                  "decision_ids": list(it.decision_ids or [])})
    ctx.metrics["_text_entry"] = found
    ctx.metrics["text_entry_probe"] = {"items": len(items), "muestras": len(cache), "casos": len(found)}


def collect(ctx: QAContext) -> None:
    s = ctx.cfg["sampling"]
    got = dom_probe(ctx, s["boxes_fps"])
    lag = stale_render(ctx)
    if got and lag > 5:
        # el DOM describe una compilación posterior al render: las cajas no son las del vídeo → OCR del render
        ctx.add("qa.stale_render", "warn",
                f"hf/index.html o timeline.json son {lag / 60:.0f} min más nuevos que render.mp4: el QA mide texto con OCR "
                "del render; vuelve a renderizar para medir con el DOM.", evidence={"retraso_s": round(lag)})
        ctx.boxes, ctx.boxes_source, got = [], "", False
    if not got:
        ocr_boxes(ctx)
        detect_render_faces(ctx)
    detect_faces(ctx)
    ctx.metrics["text_boxes"] = {"source": ctx.boxes_source, "n": len(ctx.boxes)}
