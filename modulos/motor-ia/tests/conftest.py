"""Fixtures de los tests del motor: modo simulado aislado (0 $, sin red, datos en un directorio temporal)."""

from __future__ import annotations

import pytest


@pytest.fixture
def motor_simulado(tmp_path, monkeypatch):
    """MOTOR_MOCK=1 con datos y raíz temporales; instanciar un proveedor real de Gemini hace fallar el test."""
    monkeypatch.setenv("MOTOR_MOCK", "1")
    monkeypatch.setenv("MOTOR_MOCK_TONO", "1")
    monkeypatch.setenv("MOTOR_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("META_ADS_OS_RAIZ", str(tmp_path / "os"))
    monkeypatch.setenv("GEMINI_API_KEY", "clave-falsa-que-no-se-debe-usar")
    from motor import config, store
    from motor.providers import gemini, registry

    def prohibido(*_a, **_k):
        raise AssertionError("en simulado no se puede instanciar un proveedor real")

    for cls in (gemini.GeminiImage, gemini.GeminiOmni, gemini.GeminiVeo):
        monkeypatch.setattr(cls, "__init__", prohibido)
    config.reset_settings()
    store.set_ctx(None)
    registry.reset()
    yield tmp_path
    config.reset_settings()
    store.set_ctx(None)
    registry.reset()
