"""Utilidades compartidas por los tests del motor (no es un test: lo importan `conftest.py` y los `test_motor_ia_*`)."""
from __future__ import annotations

import importlib.util
import os
import pathlib
import sys

RAIZ_PRODUCTO = pathlib.Path(__file__).resolve().parents[3]
MODULO = RAIZ_PRODUCTO / "modulos" / "motor-ia"


def entorno_limpio(**extra: str) -> dict[str, str]:
    """Entorno para un subproceso del motor: sin claves reales, sin ajustes MOTOR_* heredados ni el VIRTUAL_ENV raíz."""
    env = {k: v for k, v in os.environ.items()
           if k != "VIRTUAL_ENV" and not k.startswith("MOTOR_") and not k.endswith(("_API_KEY", "_KEY"))}
    env.update(extra)
    return env


def cargar(ruta: pathlib.Path, nombre: str):
    """Importa un archivo del motor que solo usa biblioteca estándar al importarse (config, scripts)."""
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def cargar_script(nombre: str):
    return cargar(MODULO / "scripts" / f"{nombre}.py", f"_motor_script_{nombre}")
