"""Interfaces de proveedores.

Cada capacidad es un Protocol pequeño. El router y las etapas del pipeline solo conocen estas
interfaces; los adaptadores concretos (Gemini, fal, OpenAI, mock…) se registran en `registry`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from ..models import Asset, Word


class ProviderError(RuntimeError):
    """Error del proveedor. `retryable` indica si tiene sentido reintentar."""

    def __init__(self, msg: str, *, retryable: bool = False, moderation: bool = False, billing: bool = False,
                 status_code: int | None = None, accepted: bool = False, remote_id: str | None = None):
        super().__init__(msg)
        self.billing = billing  # saldo/crédito agotado: no reintentar, pausar el proyecto
        # accepted: el proveedor YA aceptó (y probablemente cobra) el trabajo; reintentar = pagar dos veces
        self.accepted = accepted
        self.remote_id = remote_id
        self.status_code = status_code
        self.retryable = retryable and not billing and not accepted
        self.moderation = moderation


BILLING_MARKERS = ("402", "prepayment credits", "credits are depleted", "insufficient balance", "exhausted balance",
                   "billing account", "payment required", "insufficient_quota", "out of credits")


def is_billing(e: BaseException) -> bool:
    if getattr(e, "billing", False):
        return True
    s = str(e).lower()
    return any(m in s for m in BILLING_MARKERS)


@dataclass
class ImageRequest:
    prompt: str
    refs: list[Asset] = field(default_factory=list)  # identidad, producto, look, localización
    ref_roles: list[str] = field(default_factory=list)  # descripción del papel de cada referencia
    aspect: str = "9:16"
    size: str = "1k"
    seed: int | None = None
    n: int = 1


@dataclass
class VideoRequest:
    prompt: str
    first_frame: Asset | None = None
    last_frame: Asset | None = None
    refs: list[Asset] = field(default_factory=list)  # referencias de identidad/producto
    duration: float = 5.0
    aspect: str = "9:16"
    resolution: str = "720p"
    audio: bool = False  # audio nativo (diálogo/ambiente)
    negative_prompt: str = ""
    seed: int | None = None


@dataclass
class TalkingRequest:
    """Plano hablado: retrato/fotograma + texto (diálogo nativo) o audio (lip-sync)."""

    prompt: str
    portrait: Asset | None = None
    audio: Asset | None = None
    dialogue: str = ""
    locale: str = "es-ES"
    voice_hint: str = ""
    duration: float = 6.0
    aspect: str = "9:16"
    resolution: str = "720p"
    refs: list[Asset] = field(default_factory=list)
    seed: int | None = None


@dataclass
class TTSResult:
    audio: Asset
    words: list[Word] = field(default_factory=list)


@runtime_checkable
class LLM(Protocol):
    name: str

    def json(self, system: str, prompt: str, schema: dict[str, Any] | None = None, *, images: list[Asset] | None = None,
             step: str = "llm", temperature: float = 0.7, model: str | None = None) -> Any: ...

    def text(self, system: str, prompt: str, *, step: str = "llm", temperature: float = 0.7, model: str | None = None) -> str: ...


@runtime_checkable
class ImageGen(Protocol):
    name: str

    def generate(self, req: ImageRequest) -> list[Asset]: ...


@runtime_checkable
class VideoGen(Protocol):
    name: str

    def generate(self, req: VideoRequest) -> Asset: ...


@runtime_checkable
class TalkingGen(Protocol):
    name: str

    def generate(self, req: TalkingRequest) -> Asset: ...


@runtime_checkable
class LipSync(Protocol):
    name: str

    def sync(self, video: Asset, audio: Asset) -> Asset: ...


@runtime_checkable
class TTS(Protocol):
    name: str

    def speak(self, text: str, *, voice: str, locale: str, style: str = "", speed: float = 1.0) -> TTSResult: ...


@runtime_checkable
class MusicGen(Protocol):
    name: str

    def generate(self, prompt: str, duration: float) -> Asset: ...


@runtime_checkable
class Transcriber(Protocol):
    name: str

    def words(self, audio: Asset, locale: str, text_hint: str = "") -> list[Word]: ...


@runtime_checkable
class VideoJudge(Protocol):
    name: str

    def review(self, video: Asset, prompt: str, schema: dict[str, Any], *, refs: list[Asset] | None = None,
               fps: float = 2.0, step: str = "qa") -> Any: ...


@runtime_checkable
class Upscaler(Protocol):
    name: str

    def upscale(self, video: Asset, width: int, height: int) -> Asset: ...
