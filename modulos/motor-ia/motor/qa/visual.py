"""Detectores visuales locales (MediaPipe, gratis).

`mouth_motion`: la boca se mueve en un plano pedido sin diálogo (fallo visto en clips reales de Omni). Solo se
analiza el tramo del clip que usa la timeline. Probado: plano mudo σ(jawOpen)=0,00; plano hablado σ=0,13.

Descartado tras probarlo: detectar un segundo móvil en la mano con EfficientDet (COCO «cell phone»). Con el móvil
de canto las puntuaciones (~0,1) no se distinguen de clips sin móvil; ese fallo lo revisa el juez multimodal.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

from ..media import extract_frames
from ..store import ctx

JAW_MOVING_STD = 0.07  # desviación típica de «jawOpen» por encima de la cual hay habla/gesticulación de boca


@lru_cache(maxsize=1)
def _landmarker():
    path = ctx().settings.models_dir / "face" / "face_landmarker.task"
    if not path.exists():
        return None
    from mediapipe.tasks.python import vision
    from mediapipe.tasks.python.core.base_options import BaseOptions

    opts = vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=str(path)), output_face_blendshapes=True,
                                        num_faces=1)
    return vision.FaceLandmarker.create_from_options(opts)


def _frames(video: Path, start: float, dur: float, fps: float, tag: str) -> list[np.ndarray]:
    import cv2

    work = ctx().work("qa_visual", tag)
    paths = extract_frames(video, work, fps=fps, start=start, duration=dur, width=540)
    out = []
    for _t, p in paths:
        im = cv2.imread(str(p))
        if im is not None:
            out.append(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
    return out


def mouth_motion(video: Path, start: float, dur: float, tag: str, fps: float = 6.0) -> dict[str, Any]:
    lm = _landmarker()
    if lm is None:
        return {"available": False}
    import mediapipe as mp

    jaw = []
    for rgb in _frames(video, start, dur, fps, tag + "_mo"):
        res = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
        if res.face_blendshapes:
            d = {c.category_name: c.score for c in res.face_blendshapes[0]}
            jaw.append(d.get("jawOpen", 0.0))
    if len(jaw) < 4:
        return {"available": True, "frames": len(jaw), "moving": None}
    std = float(np.std(jaw))
    return {"available": True, "frames": len(jaw), "jaw_std": round(std, 3), "jaw_max": round(max(jaw), 3),
            "moving": std > JAW_MOVING_STD}


def burned_text(video: Path, start: float = 0.0, dur: float | None = None, tag: str = "", n: int = 3,
                expected: str = "") -> dict[str, Any]:
    """¿El modelo de vídeo ha incrustado subtítulos/texto? OCR de la franja inferior en `n` fotogramas del clip FUENTE
    (sin nuestros rótulos). Visto en real: Omni añade subtítulos en las extensiones si no se le prohíbe."""
    import re

    from PIL import Image

    from ..pipeline.product import ocr_text

    from ..providers.local_asr import norm

    vocab = {norm(w) for w in expected.split() if len(norm(w)) >= 4}
    d = dur if dur is not None else 3.0
    frames = extract_frames(video, ctx().work("qa_text", tag or Path(video).stem), fps=max(0.2, n / max(d, 0.5)),
                            start=start, duration=d, width=1080)
    hits = []
    for t, f in frames[:n]:
        im = Image.open(f)
        w, h = im.size
        crop = im.crop((int(w * 0.06), int(h * 0.62), int(w * 0.94), int(h * 0.96))).convert("L")
        cp = f.with_name(f.stem + "_low.png")
        crop.resize((crop.width * 2, crop.height * 2)).save(cp)
        words = [x for x in re.findall(r"[A-Za-zÁÉÍÓÚáéíóúÑñ]{3,}", ocr_text(cp, "spa+eng", psm="6"))]
        # un subtítulo incrustado TRANSCRIBE lo que se dice: ≥2 palabras del OCR tienen que coincidir con el guion
        # (las texturas de jerséis o sábanas dan «palabras» basura que no coinciden con nada)
        # solo palabras de ≥4 letras: la basura del OCR («NON», «NUE») casa por azar con «con», «que»…
        matched = [w for w in words if len(w) >= 4 and _near_any(w, vocab)] if vocab else words
        # ≥2 palabras DISTINTAS del guion («NAAA» y «NADA» de una textura casan las dos con «nada»: no cuenta)
        distinct = {_nearest(w, vocab) for w in matched} if vocab else set(words)
        if (vocab and len(distinct) >= 2) or (not vocab and len(words) >= 4):
            hits.append({"t": round(t, 2), "text": " ".join(words[:8]), "matched": matched[:6]})
    return {"frames": len(frames[:n]), "hits": hits, "burned": len(hits) >= max(1, len(frames[:n]) // 2)}


def _near_any(word: str, vocab: set[str]) -> bool:
    """Coincidencia tolerante a errores de OCR (una letra de diferencia)."""
    from ..providers.local_asr import norm

    w = norm(word)
    if len(w) < 3:
        return False
    if w in vocab:
        return True
    for v in vocab:
        if abs(len(v) - len(w)) <= 1 and sum(a != b for a, b in zip(v, w)) + abs(len(v) - len(w)) <= 1:
            return True
    return False


def _nearest(word: str, vocab: set[str]) -> str:
    from ..providers.local_asr import norm

    w = norm(word)
    if w in vocab:
        return w
    return min(vocab, key=lambda v: sum(a != b for a, b in zip(v, w)) + abs(len(v) - len(w)))
