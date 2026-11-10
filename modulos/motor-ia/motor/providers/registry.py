"""Registro de proveedores: decide qué adaptador usar para cada capacidad según las claves
disponibles y la configuración. Cambiar de proveedor = cambiar una línea aquí o una variable.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from ..store import ctx
from . import mock
from .base import ProviderError


def _mock() -> bool:
    return ctx().settings.mock


def _has(key: str) -> bool:
    return (not _mock()) and ctx().settings.has(key)


def provider_of(model: str) -> str:
    """Proveedor que factura un modelo/ruta (para saber si un respaldo evita un error de saldo)."""
    m = model.lower()
    if any(k in m for k in ("omni", "veo", "gemini", "lyria", "imagen")):
        return "gemini"
    if any(k in m for k in ("kling", "wan", "minimax", "seedream", "seedance", "fal")):
        return "fal"
    return m.split(":")[0]


@lru_cache(maxsize=None)
def llm(kind: str = "default") -> Any:
    if _has("GEMINI_API_KEY"):
        from .gemini import CREATIVE_LLM, DEFAULT_LLM, GeminiLLM

        return GeminiLLM(CREATIVE_LLM if kind == "creative" else DEFAULT_LLM)
    if _has("OPENAI_API_KEY"):
        from .openai_compat import OpenAILLM

        return OpenAILLM()
    return mock.MockLLM()


@lru_cache(maxsize=None)
def image(tier: str = "standard") -> Any:
    if _has("GEMINI_API_KEY"):
        from .gemini import IMAGE_MODEL, IMAGE_MODEL_PRO, GeminiImage

        return GeminiImage(IMAGE_MODEL_PRO if tier == "pro" else IMAGE_MODEL)
    if _has("FAL_KEY"):
        from .fal import FalSeedreamEdit

        return FalSeedreamEdit()
    return mock.MockImage()


@lru_cache(maxsize=None)
def video(model: str = "omni") -> Any:
    """model: omni (por defecto) | veo-lite | veo-fast | veo | kling-3 | wan | minimax"""
    if model == "omni" and _has("GEMINI_API_KEY"):
        from .gemini import GeminiOmni

        return GeminiOmni()
    if model.startswith("veo") and _has("GEMINI_API_KEY"):
        from .gemini import VEO_FAST, VEO_LITE, VEO_STD, GeminiVeo

        return GeminiVeo({"veo-lite": VEO_LITE, "veo-fast": VEO_FAST, "veo": VEO_STD}.get(model, VEO_LITE))
    if model in ("kling-3", "wan", "minimax") and _has("FAL_KEY"):
        from .fal import FalVideo

        return FalVideo(model)
    if _has("GEMINI_API_KEY"):
        from .gemini import VEO_LITE, GeminiVeo

        return GeminiVeo(VEO_LITE)
    return mock.MockVideo()


@lru_cache(maxsize=None)
def talking(kind: str = "native") -> Any:
    """native: diálogo nativo del modelo de vídeo · avatar: retrato+audio (requiere fal/HeyGen)."""
    if kind == "avatar":
        if _has("FAL_KEY"):
            from .fal import FalKlingAvatar

            return FalKlingAvatar()
        if ctx().settings.mock:
            return mock.MockTalking()
        # nunca caer en silencio a otro modo (el diálogo nativo ignoraría la voz persistente del actor)
        raise ProviderError("el modo lipsync necesita FAL_KEY (Kling Avatar v2 / LipSync); añade la clave o usa talk_mode='native'")
    if kind == "veo" and _has("GEMINI_API_KEY"):
        from .gemini import VEO_FAST, GeminiVeoTalking

        return GeminiVeoTalking(VEO_FAST)
    if _has("GEMINI_API_KEY"):
        from .gemini import GeminiOmniTalking

        return GeminiOmniTalking()
    return mock.MockTalking()


@lru_cache(maxsize=None)
def lipsync() -> Any | None:
    if _has("FAL_KEY"):
        from .fal import FalKlingLipSync

        return FalKlingLipSync()
    if _mock():
        return mock.MockLipSync()
    return None  # sin proveedor de lip-sync: el pipeline usa diálogo nativo


@lru_cache(maxsize=None)
def tts() -> Any:
    if _has("GEMINI_API_KEY"):
        from .gemini import GeminiTTS

        return GeminiTTS()
    return mock.MockTTS()


@lru_cache(maxsize=None)
def music() -> Any:
    if _has("GEMINI_API_KEY"):
        from .gemini import GeminiMusic

        return GeminiMusic()
    return mock.MockMusic()


@lru_cache(maxsize=None)
def judge() -> Any:
    if _has("GEMINI_API_KEY"):
        from .gemini import GeminiJudge

        return GeminiJudge()
    return mock.MockJudge()


@lru_cache(maxsize=None)
def transcriber() -> Any:
    try:
        from .local_asr import WhisperTranscriber

        return WhisperTranscriber()
    except Exception:
        return mock.MockTranscriber()


def reset() -> None:
    for f in (llm, image, video, talking, lipsync, tts, music, judge, transcriber):
        f.cache_clear()


def status() -> dict[str, str]:
    """Qué adaptador está activo para cada capacidad (para la UI y la documentación)."""
    out = {}
    for name, f in (("llm", llm), ("image", image), ("video", video), ("talking", talking), ("lipsync", lipsync),
                    ("tts", tts), ("music", music), ("judge", judge), ("transcriber", transcriber)):
        try:
            p = f()
            out[name] = "—" if p is None else f"{type(p).__name__}({getattr(p, 'model', getattr(p, 'name', ''))})"
        except Exception as e:  # noqa: BLE001
            out[name] = f"error: {e}"
    return out
