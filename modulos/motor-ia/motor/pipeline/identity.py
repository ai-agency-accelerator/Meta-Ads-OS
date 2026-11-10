"""Identidad facial con licencia comercial: YuNet (MIT) para detectar + SFace (Apache-2.0) para embeddings.

InsightFace/ArcFace NO se usa: sus pesos son solo para investigación no comercial.

Umbrales de arranque (coseno SFace), a calibrar por actor:
  - suelo OpenCV Zoo «misma persona»: ≥0.363
  - objetivo del motor: mediana ≥0.50 y p10 ≥0.42 frente al centroide del actor
  - fallo duro: ≥0.5 s seguidos por debajo de 0.363
"""

from __future__ import annotations

import threading
import time
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np

from ..costs import record_local
from ..media import extract_frames
from ..models import Asset, IdentityProfile
from ..store import ctx

_DET_LOCK = threading.Lock()
FLOOR = 0.363
TARGET_MEDIAN = 0.50
TARGET_P10 = 0.42
MIN_FACE_PX = 70


def _models_dir() -> Path:
    return ctx().settings.models_dir / "face"


@lru_cache(maxsize=1)
def _detector():
    d = _models_dir()
    for name in ("face_detection_yunet_2026may.onnx", "face_detection_yunet_2023mar.onnx"):
        p = d / name
        if p.exists():
            try:
                return cv2.FaceDetectorYN.create(str(p), "", (320, 320), 0.75, 0.3, 5000)
            except cv2.error:
                continue
    raise RuntimeError("Modelo YuNet no encontrado: ejecuta `motor setup`")


@lru_cache(maxsize=1)
def _recognizer():
    p = _models_dir() / "face_recognition_sface_2021dec.onnx"
    if not p.exists():
        raise RuntimeError("Modelo SFace no encontrado: ejecuta `motor setup`")
    return cv2.FaceRecognizerSF.create(str(p), "")


def detect(img: np.ndarray) -> np.ndarray | None:
    """Devuelve la cara más grande [x,y,w,h, 10 landmarks, score] o None. Reescala si es muy grande."""
    h, w = img.shape[:2]
    scale = min(1.0, 960 / max(h, w))
    small = cv2.resize(img, (int(w * scale), int(h * scale))) if scale < 1 else img
    det = _detector()
    with _DET_LOCK:  # un único FaceDetectorYN compartido: setInputSize+detect no es seguro entre hilos
        det.setInputSize((small.shape[1], small.shape[0]))
        _, faces = det.detect(small)
    if faces is None or len(faces) == 0:
        return None
    f = max(faces, key=lambda r: r[2] * r[3]).copy()
    f[:14] = f[:14] / scale
    return f


def embed_image(img: np.ndarray) -> tuple[np.ndarray | None, float]:
    """Embedding SFace normalizado y tamaño de cara en px (0 si no hay cara)."""
    face = detect(img)
    if face is None or min(face[2], face[3]) < MIN_FACE_PX:
        return None, float(0 if face is None else min(face[2], face[3]))
    rec = _recognizer()
    with _DET_LOCK:
        aligned = rec.alignCrop(img, face)
        feat = rec.feature(aligned).flatten().astype(np.float32)
    feat /= np.linalg.norm(feat) + 1e-9
    return feat, float(min(face[2], face[3]))


def embed_path(path: Path) -> np.ndarray | None:
    img = cv2.imread(str(path))
    if img is None:
        return None
    return embed_image(img)[0]


def cos(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / ((np.linalg.norm(a) * np.linalg.norm(b)) + 1e-9))


def build_profile(assets: list[Asset]) -> IdentityProfile:
    t0 = time.time()
    feats = []
    used = []
    for a in assets:
        e = embed_path(ctx().assets.abspath(a))
        if e is not None:
            feats.append(e)
            used.append(a.id)
    prof = IdentityProfile(reference_asset_ids=used)
    if feats:
        c = np.mean(feats, axis=0)
        c /= np.linalg.norm(c) + 1e-9
        prof.centroid = [round(float(x), 6) for x in c]
        if len(feats) > 1:
            sims = [cos(feats[i], feats[j]) for i in range(len(feats)) for j in range(i + 1, len(feats))]
            prof.self_similarity = round(float(np.mean(sims)), 4)
            # umbral por actor: algo por debajo de su propia coherencia (sin tope artificial), nunca bajo el suelo
            prof.threshold = round(max(FLOOR + 0.03, min(0.60, float(np.percentile(sims, 10)) - 0.08)), 3)
            prof.calibrated = True
    record_local("identity", "sface", time.time() - t0, note=f"{len(feats)} refs")
    return prof


def add_impostors(prof: IdentityProfile, impostors: list[Asset]) -> IdentityProfile:
    """Calibra contra caras parecidas: el umbral sube por encima del p99 de los impostores frente al centroide.

    Medido (auditoría de identidad): personas reales distintas (LFW) ≤0,48 frente a la actriz; «gemelas» generadas
    con la misma descripción ≈0,72. Sin impostores el umbral solo caza cambios catastróficos.
    """
    if not prof.centroid:
        return prof
    c = np.array(prof.centroid, dtype=np.float32)
    for a in impostors:
        if a.id in prof.impostor_asset_ids or a.id in prof.reference_asset_ids:
            continue
        e = embed_path(ctx().assets.abspath(a))
        if e is None:
            continue
        prof.impostor_asset_ids.append(a.id)
        prof.impostor_embeddings.append([round(float(x), 6) for x in e])
    if prof.impostor_embeddings:
        sims = [cos(np.array(e, dtype=np.float32), c) for e in prof.impostor_embeddings]
        prof.impostor_p99 = round(float(np.percentile(sims, 99)), 4)
        # el umbral NO se sube al p99 de las gemelas (~0,72: rechazaría tomas buenas con giros de cabeza); la
        # decisión «gemela» la toma el margen frente a impostores en video_identity
    return prof


def impostor_margin(e: np.ndarray, prof: IdentityProfile) -> float | None:
    """sim(centroide) − máx sim(impostor). >0 = más cerca de la actriz que de cualquier gemela conocida."""
    if not prof.impostor_embeddings or not prof.centroid:
        return None
    own = cos(e, np.array(prof.centroid, dtype=np.float32))
    other = max(cos(e, np.array(x, dtype=np.float32)) for x in prof.impostor_embeddings)
    return own - other


def image_similarity(asset: Asset, prof: IdentityProfile) -> float | None:
    if not prof.centroid:
        return None
    e = embed_path(ctx().assets.abspath(asset))
    if e is None:
        return None
    return cos(e, np.array(prof.centroid, dtype=np.float32))


def video_identity(video: Asset, prof: IdentityProfile, fps: float = 3.0, start: float = 0.0, dur: float | None = None) -> dict:
    """Similitud por fotograma frente al centroide (opcionalmente solo en el tramo que usa el montaje)."""
    t0 = time.time()
    frames = extract_frames(ctx().assets.abspath(video), ctx().work("qa", f"id_{video.id[:10]}_{start:.2f}"), fps=fps, width=720,
                            start=start, duration=dur)
    centroid = np.array(prof.centroid, dtype=np.float32) if prof.centroid else None
    series = []
    for t, p in frames:
        img = cv2.imread(str(p))
        if img is None or centroid is None:
            continue
        e, px = embed_image(img)
        margin = impostor_margin(e, prof) if e is not None else None
        series.append({"t": round(t, 2), "sim": None if e is None else round(cos(e, centroid), 4), "face_px": int(px),
                       "margin": None if margin is None else round(margin, 4)})
    sims = [s["sim"] for s in series if s["sim"] is not None]
    margins = [s["margin"] for s in series if s.get("margin") is not None]
    out: dict = {"frames": len(series), "with_face": len(sims), "series": series}
    if margins:
        out["impostor_margin_median"] = round(float(np.median(margins)), 4)
        out["closer_to_impostor_frac"] = round(sum(m < 0 for m in margins) / len(margins), 3)
    if sims:
        out.update(
            median=round(float(np.median(sims)), 4),
            p10=round(float(np.percentile(sims, 10)), 4),
            min=round(float(np.min(sims)), 4),
        )
        # tramos seguidos bajo el suelo
        bad, run_start, worst = [], None, 0.0
        for s in series:
            low = s["sim"] is not None and s["sim"] < FLOOR
            if low and run_start is None:
                run_start = s["t"]
            if not low and run_start is not None:
                if s["t"] - run_start >= 0.5:
                    bad.append((run_start, s["t"]))
                run_start = None
        if run_start is not None and series[-1]["t"] - run_start >= 0.5:
            bad.append((run_start, series[-1]["t"]))
        out["drift_spans"] = bad
        threshold = prof.threshold or TARGET_P10
        # calibrado con tomas reales durante la construcción: la actriz correcta en un cuarto nuevo queda ligeramente por
        # encima de su «gemela» (margen +0,02, 32 % de fotogramas más cerca de ella) y otra actriz claramente por debajo
        # (−0,08, 100 %). Se rechaza solo si está claramente más cerca de un impostor; la zona dudosa → revisar
        mm = float(np.median(margins)) if margins else None
        frac = sum(m < 0 for m in margins) / len(margins) if margins else 0.0
        enough = len(margins) >= 4  # con 1–3 fotogramas el margen frente a la «gemela» no es una prueba (visto en real)
        twin = enough and mm < 0 and frac > 0.5
        out["twin_risk"] = bool(margins) and not twin and (mm < 0.03 or frac > 0.3)
        out["passed"] = bool(out["median"] >= max(threshold + 0.06, FLOOR + 0.05) and out["p10"] >= threshold
                             and not bad and not twin)
        if twin:
            out["reason"] = "se parece más a un impostor conocido que a la actriz"
    else:
        out["passed"] = None  # sin caras medibles: no aplica
    record_local("qa", "sface-video", time.time() - t0, note=video.id[:10])
    return out
