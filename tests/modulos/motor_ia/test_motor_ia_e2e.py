"""Extremo a extremo del motor en simulado (0 $, sin red; 1–3 min de render con FFmpeg).

Decisión: se salta por defecto para que `uv run pytest tests/modulos -q` sea rápido; actívalo con `MOTOR_E2E=1`
(la CI y la integración lo ejecutan así). Mismo test que `modulos/motor-ia/tests/test_e2e_mock.py`.
"""
from __future__ import annotations

import os
import shutil

import pytest

from motor_ia_apoyo import MODULO, entorno_limpio


@pytest.mark.lento
@pytest.mark.skipif(os.environ.get("MOTOR_E2E") != "1", reason="prueba larga: actívala con MOTOR_E2E=1")
@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="falta FFmpeg")
def test_e2e_simulado(uv_motor, tmp_path):
    env = entorno_limpio(MOTOR_MOCK="1", META_ADS_OS_RAIZ=str(tmp_path / "os"), MOTOR_MOCK_TONO="1")
    p = uv_motor(["python", "-m", "pytest", "-q", "-p", "no:cacheprovider", str(MODULO / "tests" / "test_e2e_mock.py")],
                 env, timeout=1200)
    assert p.returncode == 0, p.stdout[-3000:] + p.stderr[-2000:]
