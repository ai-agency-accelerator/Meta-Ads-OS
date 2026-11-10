"""Fixtures de los tests del motor de vídeo con IA (sin red ni gasto).

El entorno raíz no tiene las dependencias del motor: lo que las necesita se ejecuta en su propio entorno con
`uv run --offline --project modulos/motor-ia …` (si uv o ese entorno no están, el test se salta y dice por qué).
Lo que es biblioteca estándar (configuración y validación de recetas) se importa directamente.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

import pytest

from motor_ia_apoyo import MODULO, RAIZ_PRODUCTO, cargar, entorno_limpio


def pytest_configure(config):
    config.addinivalue_line("markers", "lento: prueba larga del motor (se activa con MOTOR_E2E=1)")


@pytest.fixture(scope="session")
def uv_motor():
    """Devuelve `correr(args, env) -> CompletedProcess` dentro del entorno del motor, o salta el test."""
    uv = shutil.which("uv")
    if not uv:
        pytest.skip("uv no está instalado")

    def correr(args: list[str], env: dict[str, str], timeout: int = 180) -> subprocess.CompletedProcess:
        return subprocess.run([uv, "run", "--offline", "--quiet", "--project", str(MODULO), *args], cwd=RAIZ_PRODUCTO,
                              env=env, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)

    probe = correr(["python", "-c", "import motor.cli, typer, pydantic"], entorno_limpio(), timeout=300)
    if probe.returncode != 0:
        pytest.skip("el entorno del motor no está instalado (ejecuta `uv run --project modulos/motor-ia motor status` "
                    f"una vez con red): {probe.stderr.strip()[-200:]}")
    return correr


@pytest.fixture
def config_motor(tmp_path, monkeypatch):
    """`motor/config.py` (solo biblioteca estándar) apuntando a una raíz temporal; nunca lee el `.env` real."""
    raiz = tmp_path / "os"
    (raiz / "contexto").mkdir(parents=True)
    for k in list(os.environ):
        if k.startswith("MOTOR_") or k.endswith(("_API_KEY", "_KEY")):
            monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("META_ADS_OS_RAIZ", str(raiz))
    monkeypatch.setenv("MOTOR_DATA_DIR", str(tmp_path / "data"))
    mod = cargar(MODULO / "motor" / "config.py", "_motor_config_test")
    monkeypatch.setattr(mod, "MODULE_ROOT", tmp_path / "modulo_sin_env")
    mod.reset_settings()
    yield mod, raiz
    sys.modules.pop("_motor_config_test", None)
