"""Reintentos con backoff exponencial para errores transitorios (429, 5xx, timeouts)."""

from __future__ import annotations

import random
import time
from typing import Callable, TypeVar

from .base import ProviderError, is_billing

T = TypeVar("T")

TRANSIENT_MARKERS = ("429", "500", "502", "503", "504", "RESOURCE_EXHAUSTED", "UNAVAILABLE", "DEADLINE", "timed out", "Timeout",
                     "temporarily", "overloaded", "INTERNAL")


# Para creaciones NO idempotentes (Veo/Omni): solo reintentar cuando es seguro que no se creó el trabajo.
SAFE_RETRY_MARKERS = ("429", "503", "RESOURCE_EXHAUSTED", "UNAVAILABLE")


def is_transient(e: Exception, markers: tuple[str, ...] = TRANSIENT_MARKERS) -> bool:
    if is_billing(e) or getattr(e, "accepted", False):
        return False  # sin saldo, o trabajo ya aceptado por el proveedor: reintentar no sirve o cobra dos veces
    code = getattr(e, "status_code", None)
    if markers is SAFE_RETRY_MARKERS and code is not None:
        return code in (429, 500, 503)  # creación no idempotente: solo si el código dice que NO se creó (sin id aceptado)
    s = f"{type(e).__name__} {e}"
    if isinstance(e, ProviderError) and markers is TRANSIENT_MARKERS:
        return e.retryable
    return any(m in s for m in markers)


def with_retries(fn: Callable[[], T], *, attempts: int = 4, base: float = 3.0, cap: float = 60.0,
                 on_retry: Callable[[int, Exception], None] | None = None,
                 markers: tuple[str, ...] = TRANSIENT_MARKERS) -> T:
    last: Exception | None = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            last = e
            if i == attempts - 1 or not is_transient(e, markers):
                raise
            if on_retry:
                on_retry(i, e)
            time.sleep(min(cap, base * (2 ** i)) * (0.7 + 0.6 * random.random()))
    assert last is not None
    raise last
