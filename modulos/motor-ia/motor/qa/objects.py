"""Objetos en la mano (el «segundo móvil» de los selfies generados) con CLIP ViT-B/16 en ONNX, sin torch, gratis.

Fallo real visto en clips generados y en retratos maestros: la persona sostiene OTRO móvil mientras «se graba»
(físicamente imposible y delata IA). Los detectores COCO no lo ven (móvil de canto ≈0,1). CLIP zero-shot por
ventanas sí lo separa (auditoría QA): positivos 0,83–0,985, negativos ≤0,67 sobre 57 imágenes sin móvil.

Regla: ≥2 fotogramas con p≥0,80, o 1 con p≥0,95 → `extra_object`. Se usa ANTES de pagar vídeo (referencias del
actor y fotogramas clave) y después (tramo usado de cada clip). Calibrar con más datos antes de confiar a ciegas.
"""

from __future__ import annotations

import threading
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

from ..store import ctx

MEAN = np.array([0.48145466, 0.4578275, 0.40821073], np.float32)
STD = np.array([0.26862954, 0.26130258, 0.27577711], np.float32)
POS = ["a photo of a hand holding a smartphone", "a black smartphone held in a hand", "a person holding a mobile phone"]
NEG = ["a photo of a hand", "an empty open hand", "a person's arm in a knitted sweater", "a knitted sweater",
       "a coffee machine on a kitchen counter", "kitchen shelves with jars and utensils", "a dish rack with cups",
       "a kitchen towel on a counter", "a woman's face", "a window with daylight", "a white kitchen cabinet",
       "a hand holding a mug", "a hand holding a kitchen utensil", "a pot plant"]
P_FRAME, P_STRONG = 0.80, 0.95
URLS = {f: f"https://huggingface.co/Xenova/clip-vit-base-patch16/resolve/main/{'onnx/' if f.endswith('.onnx') else ''}{f}"
        for f in ("vision_model_quantized.onnx", "text_model_quantized.onnx", "tokenizer.json")}
_LOCK = threading.Lock()


def _dir() -> Path:
    return ctx().settings.models_dir / "clip"


def available() -> bool:
    import os

    import importlib.util

    if ctx().settings.mock and not os.environ.get("MOTOR_MOCK_OBJECTS"):
        return False  # los fotogramas simulados (fondo plano + texto) no son imágenes naturales: CLIP da falsos positivos
    if importlib.util.find_spec("onnxruntime") is None or importlib.util.find_spec("tokenizers") is None:
        return False  # sin el extra `local` el detector no corre (queda como «sin datos», nunca como aprobado)
    return (_dir() / "vision_model_quantized.onnx").exists()


@lru_cache(maxsize=1)
def _vision():
    import onnxruntime as ort

    return ort.InferenceSession(str(_dir() / "vision_model_quantized.onnx"), providers=["CPUExecutionProvider"])


@lru_cache(maxsize=1)
def _text_emb() -> np.ndarray:
    """Embeddings de los textos (se calculan una vez y se guardan: el modelo de texto no se vuelve a cargar)."""
    cache = _dir() / "text_emb_v1.npy"
    if cache.exists():
        return np.load(cache)
    import onnxruntime as ort
    from tokenizers import Tokenizer

    tok = Tokenizer.from_file(str(_dir() / "tokenizer.json"))
    txt = ort.InferenceSession(str(_dir() / "text_model_quantized.onnx"), providers=["CPUExecutionProvider"])
    enc = [tok.encode(p).ids for p in POS + NEG]
    L = max(map(len, enc))
    ids = np.array([e + [49407] * (L - len(e)) for e in enc], np.int64)  # relleno con EOS (CLIP usa el argmax)
    e = txt.run(None, {"input_ids": ids})[0]
    e = e / np.linalg.norm(e, axis=1, keepdims=True)
    np.save(cache, e)
    return e


def _prep(rgb: np.ndarray) -> np.ndarray:
    import cv2

    x = cv2.resize(rgb, (224, 224), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255.0
    return ((x - MEAN) / STD).transpose(2, 0, 1)


def _windows(H: int, W: int):
    for frac in (0.30, 0.45):  # manos: 70 % inferior del encuadre selfie
        side = int(frac * W)
        stride = max(1, side // 2)
        for y in range(int(0.30 * H), H - side + 1, stride):
            for x in range(0, W - side + 1, stride):
                yield x, y, side


def frame_score(rgb: np.ndarray) -> tuple[float, tuple[int, int, int]]:
    import cv2

    if max(rgb.shape[:2]) > 1280:
        k = 1280 / max(rgb.shape[:2])
        rgb = cv2.resize(rgb, (int(rgb.shape[1] * k), int(rgb.shape[0] * k)))
    H, W = rgb.shape[:2]
    boxes = list(_windows(H, W))
    if not boxes:
        return 0.0, (0, 0, 0)
    batch = np.stack([_prep(rgb[y:y + s, x:x + s]) for x, y, s in boxes])
    with _LOCK:
        e = _vision().run(None, {"pixel_values": batch})[0]
    e /= np.linalg.norm(e, axis=1, keepdims=True)
    logits = 100.0 * e @ _text_emb().T
    p = np.exp(logits - logits.max(1, keepdims=True))
    p /= p.sum(1, keepdims=True)
    pos = p[:, : len(POS)].sum(1)
    k = int(pos.argmax())
    return float(pos[k]), boxes[k]


def image_has_phone(path: Path) -> dict[str, Any]:
    import cv2

    if not available():
        return {"available": False}
    img = cv2.imread(str(path))
    if img is None:
        return {"available": True, "p": 0.0, "phone": False}
    p, box = frame_score(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    return {"available": True, "p": round(p, 3), "box": box, "phone": p >= P_FRAME}


def clip_has_phone(video: Path, start: float = 0.0, dur: float | None = None, fps: float = 2.0, tag: str = "") -> dict[str, Any]:
    """¿Aparece un móvil en la mano en el tramo [start, start+dur] del clip?"""
    import cv2

    from ..media import extract_frames

    if not available():
        return {"available": False}
    frames = extract_frames(video, ctx().work("qa_objects", tag or video.stem), fps=fps, width=720, start=start, duration=dur)
    scores = []
    for t, f in frames:
        img = cv2.imread(str(f))
        if img is None:
            continue
        p, _ = frame_score(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        scores.append((round(t, 2), round(p, 3)))
    hits = [t for t, p in scores if p >= P_FRAME]
    strong = any(p >= P_STRONG for _, p in scores)
    return {"available": True, "frames": len(scores), "hits": hits, "max": max((p for _, p in scores), default=0.0),
            "phone": len(hits) >= 2 or strong}
