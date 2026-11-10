"""Fixtures de los tests de cutkit (sin red ni gasto).

El entorno raíz no tiene las dependencias de cutkit: lo que necesita NumPy, Pillow, PyYAML o FFmpeg se ejecuta en su
propio entorno con `uv run --offline --project modulos/cutkit …` (si uv o ese entorno no están, el test se salta y dice
por qué). La marca y las rutas (solo biblioteca estándar) se importan directamente.
"""
from __future__ import annotations

import importlib
import shutil
import subprocess
import sys

import pytest

from cutkit_apoyo import MODULO, RAIZ_PRODUCTO, codigo, entorno_limpio, leer_salida


@pytest.fixture(scope="session")
def uv_cutkit():
    """Devuelve `correr(args, env, timeout) -> CompletedProcess` dentro del entorno de cutkit, o salta el test."""
    uv = shutil.which("uv")
    if not uv:
        pytest.skip("uv no está instalado")

    def correr(args: list[str], env: dict[str, str] | None = None, timeout: int = 240) -> subprocess.CompletedProcess:
        return subprocess.run([uv, "run", "--offline", "--quiet", "--project", str(MODULO), *args], cwd=RAIZ_PRODUCTO,
                              env=env or entorno_limpio(), capture_output=True, text=True, timeout=timeout,
                              stdin=subprocess.DEVNULL)

    probe = correr(["python", "-I", "-c", "import cutkit.anuncio, cutkit.audio.sfx_sinteticos, typer, PIL, numpy"],
                   timeout=300)
    if probe.returncode != 0:
        pytest.skip("el entorno de cutkit no está instalado (ejecuta `uv run --project modulos/cutkit ck --help` una "
                    f"vez con red): {probe.stderr.strip()[-200:]}")
    return correr


@pytest.fixture(scope="session")
def py_cutkit(uv_cutkit):
    """`ejecutar(fuente, **env) -> objeto`: corre `fuente` con el Python de cutkit y devuelve lo que pase a `salida()`."""
    def ejecutar(fuente: str, timeout: int = 240, **env: str):
        p = uv_cutkit(["python", "-I", "-c", codigo(fuente)], entorno_limpio(**env), timeout)
        assert p.returncode == 0, p.stderr[-3000:]
        return leer_salida(p.stdout)
    return ejecutar


@pytest.fixture
def cutkit_lib(tmp_path, monkeypatch):
    """`cutkit.paths` y `cutkit.marca` (solo biblioteca estándar) apuntando a una raíz temporal.

    Devuelve `(paths, marca, raiz)`; al terminar, quita los módulos para que no se mezclen con otras raíces.
    """
    raiz = tmp_path / "os"
    (raiz / "clientes").mkdir(parents=True)
    monkeypatch.setenv("META_ADS_OS_RAIZ", str(raiz))
    monkeypatch.setenv("CUTKIT_DATOS", str(tmp_path / "datos"))
    monkeypatch.delenv("CUTKIT_RUNS", raising=False)
    monkeypatch.syspath_prepend(str(MODULO))
    for m in [m for m in sys.modules if m == "cutkit" or m.startswith("cutkit.")]:
        sys.modules.pop(m)
    paths = importlib.import_module("cutkit.paths")
    marca = importlib.import_module("cutkit.marca")
    yield paths, marca, raiz
    for m in [m for m in sys.modules if m == "cutkit" or m.startswith("cutkit.")]:
        sys.modules.pop(m)
