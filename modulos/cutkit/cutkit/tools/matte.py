"""cutkit.tools.matte — mate por fotograma del sujeto (Apple Vision) con refinado de estudio, cacheado por hash.

Solo Mac (necesita el extra `mac`: `uv sync --project modulos/cutkit --extra mac`). En Linux y Windows los componentes
que recortan al sujeto (titular detrás de la persona) no están disponibles y el director usa la alternativa sin recorte.

    uv run --project modulos/cutkit python -m cutkit.tools.matte <proyecto>/edicion/media/src_main.mp4 --from 9.6 --to 11.1 [--cutout 1080]
    uv run --project modulos/cutkit python -m cutkit.tools.matte … --preview datos/mate.jpg   # hoja de control sobre rosa

Pipeline (por fotograma, a la resolución de la fuente):
  1. Vision `VNGeneratePersonSegmentationRequest`, calidad `accurate` (1512×2016, ~65 ms/f en M4).
  2. Borde refinado SOLO en la banda de incertidumbre (±14 px del contorno): filtro guiado en color con el propio
     fotograma como guía → el contorno sigue el pelo y las patillas de las gafas en vez de la máscara blanda de Vision.
  3. Estabilidad temporal: media de ±2 fotogramas ponderada por similitud de color (lo que no se mueve se promedia y
     deja de temblar; lo que se mueve conserva su propio mate → sin estela).
  4. Limpieza: islas fuera del cuerpo eliminadas, niveles (sin velo ni halo), choke de 0,5 px y feather σ≈0,8 px.
  5. Descontaminación del color (despill): F = (I − (1−α)·B) / α con B = fondo estimado por convolución normalizada;
     el verde de las plantas y el blanco de la pared dejan de teñir el borde. En el recorte RGBA el color del sujeto
     se extiende bajo los píxeles transparentes (sin orla al comprimir o escalar).

Salida en `<media>/mattes/<hash>/` (hash = fuente [ruta, tamaño, mtime] + tramo en fotogramas + parámetros):
  a_<f>.png        mate 8 bits a resolución de la fuente (f = nº de fotograma de la fuente)
  c_<f>.webp       recorte RGBA (color descontaminado) recortado a la caja del sujeto en todo el tramo y escalado a
                   `cutout` px de ancho de FUENTE (p. ej. 1080 → escala 0,75 de 1440), si se pide
  meta.json        {source, fps, f0, f1, size, frames:[{f, top, bbox}], crop:[x,y,w,h] (px fuente), cut_scale, …}
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

import numpy as np

from ..paths import DATOS

PARAMS_V = 4              # sube al cambiar el refinado (invalida la caché)
MARGIN = 2                # fotogramas extra a cada lado para el suavizado temporal


# ───────────────────────────────────────────────────────── E/S
def probe(video: Path) -> dict:
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,nb_frames",
                        "-show_entries", "format=duration", "-of", "json", str(video)], capture_output=True, text=True, check=True)
    j = json.loads(p.stdout)
    s = j["streams"][0]
    num, den = (int(x) for x in s["r_frame_rate"].split("/"))
    return {"width": int(s["width"]), "height": int(s["height"]), "fps": num / den, "duration": float(j["format"]["duration"])}


def read_frames(video: Path, f0: int, n: int, fps: float, w: int, h: int) -> np.ndarray:
    """n fotogramas RGB desde el fotograma f0 (seek exacto: ss medio fotograma antes del pts de f0)."""
    ss = max(0.0, (f0 - 0.5) / fps)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ss:.6f}", "-i", str(video), "-frames:v", str(n), "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    arr = np.frombuffer(raw, np.uint8)
    k = arr.size // (w * h * 3)
    return arr[: k * w * h * 3].reshape(k, h, w, 3)


def cache_root(video: Path) -> Path:
    video = Path(video).resolve()
    if video.parent.name == "media":
        return video.parent / "mattes"
    return DATOS / "mates"


def cache_key(video: Path, f0: int, f1: int, extra: str = "") -> str:
    st = Path(video).resolve().stat()
    s = f"{Path(video).resolve()}|{st.st_size}|{st.st_mtime_ns}|{f0}|{f1}|v{PARAMS_V}|{extra}"
    return hashlib.sha1(s.encode()).hexdigest()[:16]


# ───────────────────────────────────────────────────────── Vision
class _Vision:
    def __init__(self):
        import Quartz  # noqa: F401  (pyobjc)
        import Vision
        self.Vision = Vision
        self.req = Vision.VNGeneratePersonSegmentationRequest.alloc().initWithCompletionHandler_(None)
        self.req.setQualityLevel_(Vision.VNGeneratePersonSegmentationRequestQualityLevelAccurate)
        self.req.setOutputPixelFormat_(1278226488)   # kCVPixelFormatType_OneComponent8 ('L008')

    @staticmethod
    def _cgimage(rgb: np.ndarray):
        import Quartz
        from Foundation import NSData
        h, w, _ = rgb.shape
        rgba = np.dstack([rgb, np.full((h, w), 255, np.uint8)])
        data = NSData.dataWithBytes_length_(rgba.tobytes(), rgba.nbytes)
        prov = Quartz.CGDataProviderCreateWithCFData(data)
        cs = Quartz.CGColorSpaceCreateWithName(Quartz.kCGColorSpaceSRGB)
        return Quartz.CGImageCreate(w, h, 8, 32, w * 4, cs, Quartz.kCGImageAlphaNoneSkipLast, prov, None, False,
                                    Quartz.kCGRenderingIntentDefault)

    def mask(self, rgb: np.ndarray) -> np.ndarray:
        import Quartz
        h = self.Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(self._cgimage(rgb), None)
        ok, err = h.performRequests_error_([self.req], None)
        if not ok:
            raise RuntimeError(f"Vision falló: {err}")
        pb = self.req.results()[0].pixelBuffer()
        Quartz.CVPixelBufferLockBaseAddress(pb, 1)
        try:
            w, hh, bpr = Quartz.CVPixelBufferGetWidth(pb), Quartz.CVPixelBufferGetHeight(pb), Quartz.CVPixelBufferGetBytesPerRow(pb)
            buf = Quartz.CVPixelBufferGetBaseAddress(pb).as_buffer(bpr * hh)
            m = np.frombuffer(buf, np.uint8).reshape(hh, bpr)[:, :w].copy()
        finally:
            Quartz.CVPixelBufferUnlockBaseAddress(pb, 1)
        return m


# ───────────────────────────────────────────────────────── refinado
def _box(x, r):
    import cv2
    return cv2.boxFilter(x, -1, (2 * r + 1, 2 * r + 1), borderType=cv2.BORDER_REFLECT)


def guided_color(I: np.ndarray, p: np.ndarray, r: int, eps: float) -> np.ndarray:
    """Filtro guiado con guía en color (He et al.). I: HxWx3 float32 [0,1], p: HxW float32."""
    mI = [_box(I[..., c], r) for c in range(3)]
    mp = _box(p, r)
    cov = [_box(I[..., c] * p, r) - mI[c] * mp for c in range(3)]
    var = {}
    for i in range(3):
        for j in range(i, 3):
            var[i, j] = _box(I[..., i] * I[..., j], r) - mI[i] * mI[j] + (eps if i == j else 0.0)
    # inversa 3×3 simétrica en forma cerrada (cofactores), vectorizada: ~10× más rápida que np.linalg.solve
    a11, a12, a13, a22, a23, a33 = var[0, 0], var[0, 1], var[0, 2], var[1, 1], var[1, 2], var[2, 2]
    c11 = a22 * a33 - a23 * a23; c12 = a13 * a23 - a12 * a33; c13 = a12 * a23 - a13 * a22
    c22 = a11 * a33 - a13 * a13; c23 = a12 * a13 - a11 * a23; c33 = a11 * a22 - a12 * a12
    det = a11 * c11 + a12 * c12 + a13 * c13
    det = np.where(np.abs(det) < 1e-12, 1e-12, det)
    x, y, z = cov
    a = np.stack([(c11 * x + c12 * y + c13 * z) / det, (c12 * x + c22 * y + c23 * z) / det, (c13 * x + c23 * y + c33 * z) / det], -1)
    b = mp - (a * np.stack(mI, -1)).sum(-1)
    ma = np.stack([_box(a[..., c], r) for c in range(3)], -1)
    mb = _box(b, r)
    return (ma * I).sum(-1) + mb


def refine_spatial(rgb: np.ndarray, m_raw: np.ndarray, band_px: int = 14) -> np.ndarray:
    """Mate de Vision → alfa a resolución completa con el borde guiado por el color del fotograma."""
    import cv2
    H, W = rgb.shape[:2]
    a0 = cv2.resize(m_raw, (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255.0
    hard = (a0 > 0.5).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * band_px + 1, 2 * band_px + 1))
    band = cv2.dilate(hard, k) & (1 - cv2.erode(hard, k))
    ys, xs = np.nonzero(band)
    if len(ys) == 0:
        return a0
    y0, y1 = max(0, ys.min() - 16), min(H, ys.max() + 17)
    x0, x1 = max(0, xs.min() - 16), min(W, xs.max() + 17)
    # a media resolución (rápido) y luego se sube: el guiado fino lo da la guía a resolución completa
    I = rgb[y0:y1, x0:x1].astype(np.float32) / 255.0
    p = a0[y0:y1, x0:x1]
    s = 2
    Is = cv2.resize(I, None, fx=1 / s, fy=1 / s, interpolation=cv2.INTER_AREA)
    ps = cv2.resize(p, None, fx=1 / s, fy=1 / s, interpolation=cv2.INTER_AREA)
    q = guided_color(Is, ps, r=5, eps=2e-3)
    q = cv2.resize(q, (x1 - x0, y1 - y0), interpolation=cv2.INTER_LINEAR)
    q2 = guided_color(I, np.clip(q, 0, 1).astype(np.float32), r=2, eps=4e-3)   # pasada fina a resolución completa
    out = a0.copy()
    sub = out[y0:y1, x0:x1]
    bsub = band[y0:y1, x0:x1].astype(bool)
    # transición suave entre la banda refinada y el mate original
    wband = cv2.GaussianBlur(band[y0:y1, x0:x1].astype(np.float32), (0, 0), 3.0)
    wband = np.where(bsub, 1.0, wband)
    sub[:] = np.clip(wband * np.clip(q2, 0, 1) + (1 - wband) * sub, 0, 1)
    return out


def temporal_stabilize(alphas: list[np.ndarray], frames: np.ndarray, sigma: float = 0.035) -> list[np.ndarray]:
    """Media ±2 f ponderada por similitud de luminancia (borrosa) → sin temblor en lo quieto, sin estela en lo que se mueve."""
    import cv2
    n = len(alphas)
    Y = [cv2.GaussianBlur(cv2.cvtColor(f, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0, (0, 0), 2.0) for f in frames]
    g = {-2: 0.35, -1: 0.75, 0: 1.0, 1: 0.75, 2: 0.35}
    out = []
    for i in range(n):
        acc = np.zeros_like(alphas[i]); ws = np.zeros_like(alphas[i])
        for kk, gk in g.items():
            j = i + kk
            if j < 0 or j >= n:
                continue
            w = gk * np.exp(-((Y[i] - Y[j]) ** 2) / (sigma * sigma)) if kk else np.full_like(acc, gk)
            acc += w * alphas[j]; ws += w
        out.append(acc / np.maximum(ws, 1e-6))
    return out


def cleanup(a: np.ndarray, lo: float = 0.05, hi: float = 0.96, choke: float = 0.5, feather: float = 0.8) -> np.ndarray:
    import cv2
    a = np.clip((a - lo) / (hi - lo), 0, 1).astype(np.float32)
    # islas: se conserva el componente principal (y lo que toque el borde inferior: hombros cortados por el encuadre)
    hard = (a > 0.5).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(hard, 8)
    if n > 2:
        H = a.shape[0]
        keep = np.zeros(n, bool)
        main = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        keep[main] = True
        for c in range(1, n):
            if stats[c, cv2.CC_STAT_TOP] + stats[c, cv2.CC_STAT_HEIGHT] >= H - 2 and stats[c, cv2.CC_STAT_AREA] > 2000:
                keep[c] = True
        body = keep[lab].astype(np.uint8)
        near = cv2.dilate(body, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))).astype(np.float32)
        a = a * near
    if choke > 0:   # choke subpíxel: desplaza el umbral medio hacia dentro
        a = np.clip(a - choke * 0.12, 0, 1) / (1 - choke * 0.12)
    if feather > 0:
        a = cv2.GaussianBlur(a, (0, 0), feather)
    return np.clip(a, 0, 1)


def decontaminate(rgb: np.ndarray, a: np.ndarray, sigma: float = 22.0, spill_px: float = 36.0) -> np.ndarray:
    """Color del sujeto sin el fondo mezclado en el borde (despill) + extensión bajo lo transparente."""
    import cv2
    I = rgb.astype(np.float32) / 255.0
    H, W = a.shape
    s = 4
    small = lambda x: cv2.resize(x, (W // s, H // s), interpolation=cv2.INTER_AREA)
    big = lambda x: cv2.resize(x, (W, H), interpolation=cv2.INTER_LINEAR)
    wb = small((1 - a) ** 4)
    Bn = cv2.GaussianBlur(small(I) * wb[..., None], (0, 0), sigma / s)
    Bd = cv2.GaussianBlur(wb, (0, 0), sigma / s)[..., None]
    B = big(Bn / np.maximum(Bd, 1e-4))
    A = a[..., None]
    F = (I - (1 - A) * B) / np.maximum(A, 0.08)
    F = np.clip(F, 0, 1)
    # solo en el borde (α intermedio); dentro del sujeto, el color original
    t = np.clip((0.985 - A) / 0.25, 0, 1)
    F = I * (1 - t) + F * t
    # extensión del color del sujeto bajo lo transparente (para comprimir/escalar sin orla)
    wf = small(np.clip(a * 2 - 1, 0, 1) ** 2)
    En = cv2.GaussianBlur(small(F) * wf[..., None], (0, 0), 6)
    Ed = cv2.GaussianBlur(wf, (0, 0), 6)[..., None]
    E = big(En / np.maximum(Ed, 1e-4))
    u = np.clip((0.06 - A) / 0.06, 0, 1)
    F = F * (1 - u) + E * u
    # supresión de verde (follaje/ventana) cerca del contorno: G ≤ (R+B)/2. No toca la piel (R ≫ G) ni el interior.
    hard = (a > 0.5).astype(np.uint8)
    dist = cv2.distanceTransform(hard, cv2.DIST_L2, 5)
    wsp = np.clip((spill_px - dist) / (spill_px * 0.5), 0, 1)[..., None]
    lim = (F[..., 0:1] + F[..., 2:3]) / 2
    G = F[..., 1:2]
    F = np.concatenate([F[..., 0:1], G - wsp * np.maximum(G - lim, 0), F[..., 2:3]], -1)
    return (np.clip(F, 0, 1) * 255 + 0.5).astype(np.uint8)


# ───────────────────────────────────────────────────────── API
def matte_range(video: str | Path, t0: float | None = None, t1: float | None = None, *, f0: int | None = None,
                f1: int | None = None, cutout: int | None = None, pad: int = 32, force: bool = False,
                verbose: bool = True) -> dict:
    """Mate (y recorte RGBA opcional) de los fotogramas [f0, f1] (inclusive) de `video`. Devuelve meta (con `dir`)."""
    import cv2
    from PIL import Image
    video = Path(video).resolve()
    info = probe(video)
    fps, W, H = info["fps"], info["width"], info["height"]
    if f0 is None:
        f0 = int(round(float(t0) * fps))
    if f1 is None:
        f1 = int(round(float(t1) * fps))
    nmax = int(round(info["duration"] * fps)) - 1
    f0, f1 = max(0, f0), min(nmax, f1)
    key = cache_key(video, f0, f1, f"cut{cutout or 0}p{pad}")
    out = cache_root(video) / key
    mp = out / "meta.json"
    if mp.exists() and not force:
        meta = json.loads(mp.read_text())
        meta["dir"] = str(out)
        return meta
    out.mkdir(parents=True, exist_ok=True)
    t = time.time()
    g0, g1 = max(0, f0 - MARGIN), min(nmax, f1 + MARGIN)
    frames = read_frames(video, g0, g1 - g0 + 1, fps, W, H)
    if len(frames) < f1 - f0 + 1:
        raise RuntimeError(f"solo {len(frames)} fotogramas leídos de {video.name} ({g0}–{g1})")
    vis = _Vision()
    raw = [vis.mask(fr) for fr in frames]
    t_vis = time.time() - t
    alphas = [refine_spatial(fr, m) for fr, m in zip(frames, raw)]
    alphas = temporal_stabilize(alphas, frames)
    alphas = [cleanup(a) for a in alphas]
    rows = []
    union = None
    for i, f in enumerate(range(g0, g1 + 1)):
        if f < f0 or f > f1:
            continue
        a = alphas[i]
        cv2.imwrite(str(out / f"a_{f:05d}.png"), (a * 255 + 0.5).astype(np.uint8))
        ys, xs = np.nonzero(a > 0.5)
        bb = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1] if len(ys) else [0, 0, 0, 0]
        cols = np.nonzero((a > 0.5).any(0))[0]
        rows.append({"f": f, "t": round(f / fps, 6), "top": bb[1], "bbox": bb,
                     "cx": float(cols.mean()) if len(cols) else W / 2})
        u = np.nonzero(a > 0.02)
        if len(u[0]):
            box = [int(u[1].min()), int(u[0].min()), int(u[1].max()) + 1, int(u[0].max()) + 1]
            union = box if union is None else [min(union[0], box[0]), min(union[1], box[1]), max(union[2], box[2]), max(union[3], box[3])]
    meta = {"version": PARAMS_V, "source": str(video), "fps": fps, "f0": f0, "f1": f1, "size": [W, H], "frames": rows,
            "engine": "Vision.VNGeneratePersonSegmentationRequest(accurate)", "mask_size": list(raw[0].shape[::-1])}
    if cutout:
        sc = cutout / W
        ux0, uy0, ux1, uy1 = union or [0, 0, W, H]
        cx0, cy0 = max(0, ux0 - pad), max(0, uy0 - pad)
        cx1, cy1 = min(W, ux1 + pad), min(H, uy1 + pad)
        meta["crop"] = [cx0, cy0, cx1 - cx0, cy1 - cy0]
        meta["cut_scale"] = sc
        meta["cut_size"] = [int(round((cx1 - cx0) * sc)), int(round((cy1 - cy0) * sc))]
        for i, f in enumerate(range(g0, g1 + 1)):
            if f < f0 or f > f1:
                continue
            a = alphas[i]
            F = decontaminate(frames[i], a)
            rgba = np.dstack([F, (a * 255 + 0.5).astype(np.uint8)])[cy0:cy1, cx0:cx1]
            im = Image.fromarray(rgba, "RGBA").resize(tuple(meta["cut_size"]), Image.LANCZOS)
            im.save(out / f"c_{f:05d}.webp", "WEBP", quality=94, alpha_quality=100, method=3)
    meta["seconds"] = {"vision": round(t_vis, 2), "total": round(time.time() - t, 2)}
    mp.write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    meta["dir"] = str(out)
    if verbose:
        print(f"[matte] {video.name} f{f0}–{f1} ({f1 - f0 + 1} f): Vision {t_vis:.1f} s · total {time.time() - t:.1f} s → {out}")
    return meta


# ───────────────────────────────────────────────────────── programa → fuente
def program_window(aroll_path: str | Path, t0: float, t1: float, fps: float) -> list[dict]:
    """Tramos de fuente que cubren [t0, t1) de programa: [{src (mezzanine), f0, f1, pf0}] (pf = fotograma de programa).
    Lee `timeline.json` junto al `program.mp4` de la versión y `media_index.json` del run. [] si no se puede mapear."""
    ap = Path(aroll_path)
    tlp = ap.parent / "timeline.json"
    mip = ap.parent.parent.parent / "media_index.json"
    if not (tlp.exists() and mip.exists()):
        return []
    tl = json.loads(tlp.read_text())
    srcs = {s["id"]: s["mezzanine"] for s in json.loads(mip.read_text())["sources"]}
    p0, p1 = int(round(t0 * fps)), int(round(t1 * fps)) - 1
    out = []
    for s in tl.get("aroll", []):
        a, b = int(round(s["prog_in"] * fps)), int(round(s["prog_out"] * fps)) - 1
        lo, hi = max(a, p0), min(b, p1)
        if lo > hi or s["src"] not in srcs:
            continue
        si = int(round(s["src_in"] * fps))
        so = int(round(s["src_out"] * fps)) - 1        # más allá: fotograma congelado (hold_after)
        out.append({"src": srcs[s["src"]], "pf0": lo, "pf1": hi, "f0": min(so, si + lo - a), "f1": min(so, si + hi - a)})
    return out


def preview_sheet(meta: dict, out_path: str | Path, frames: int = 4, bg=(243, 134, 161)) -> Path:
    """Hoja de control: recortes sobre el color del lienzo, 100 % en la cabeza (pelo, gafas) + mate."""
    import cv2
    d = Path(meta["dir"])
    rows = meta["frames"]
    pick = [rows[int(round(i * (len(rows) - 1) / max(1, frames - 1)))] for i in range(frames)]
    tiles = []
    for r in pick:
        f = r["f"]
        a = cv2.imread(str(d / f"a_{f:05d}.png"), 0).astype(np.float32) / 255
        c = d / f"c_{f:05d}.webp"
        if c.exists():
            from PIL import Image
            rgba = np.asarray(Image.open(c).convert("RGBA")).astype(np.float32) / 255
            al = rgba[..., 3:4]
            comp = rgba[..., :3] * al + np.array(bg, np.float32)[None, None] / 255 * (1 - al)
            img = (comp * 255).astype(np.uint8)
            x, y, w, h = r["bbox"][0], r["top"], 900, 900
            sc = meta["cut_scale"]
            cx, cy = int((meta["crop"][0]) * sc), int(meta["crop"][1] * sc)
            yy = max(0, int(r["top"] * sc) - cy - 40)
            xx = max(0, int((r["cx"]) * sc) - cx - 450)
            tile = img[yy:yy + 760, xx:xx + 900]
        else:
            tile = (np.dstack([a] * 3) * 255).astype(np.uint8)[r["top"]:r["top"] + 760, :900]
        tiles.append(cv2.cvtColor(tile, cv2.COLOR_RGB2BGR))
    hmin = min(t.shape[0] for t in tiles)
    sheet = np.hstack([t[:hmin] for t in tiles])
    cv2.imwrite(str(out_path), sheet, [cv2.IMWRITE_JPEG_QUALITY, 92])
    return Path(out_path)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--from", dest="t0", type=float, required=True, help="inicio (s de la fuente)")
    ap.add_argument("--to", dest="t1", type=float, required=True, help="fin (s de la fuente, inclusive)")
    ap.add_argument("--cutout", type=int, default=None, help="genera recortes RGBA a este ancho de fuente (p. ej. 1080)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--preview", default=None, help="hoja de control JPG")
    a = ap.parse_args(argv)
    meta = matte_range(a.video, a.t0, a.t1, cutout=a.cutout, force=a.force)
    print(json.dumps({k: meta[k] for k in ("dir", "f0", "f1", "size", "mask_size") if k in meta} | {"seconds": meta.get("seconds")}, ensure_ascii=False))
    if a.preview:
        print(preview_sheet(meta, a.preview))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
