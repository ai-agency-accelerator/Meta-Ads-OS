"""Fixtures de los tests de hooks. Usan la fixture `instancia` de tests/conftest.py (cliente ficticio `acme`)."""
from __future__ import annotations

import importlib
import io
import json
import os
import subprocess
import sys

import pytest

from ayudas_hooks import HOOKS

VARIABLES_FUERA = ("META_TOKEN", "MOTOR_MOCK", "CLAUDE_ENV_FILE", "META_API_VERSION", "META_ADS_OS_HOY")


def _entorno_limpio(instancia, extra=None) -> dict:
    entorno = {k: v for k, v in os.environ.items() if not k.startswith(VARIABLES_FUERA)}
    entorno["HOME"] = str(instancia / ".home")  # nunca leer la configuración real del usuario
    entorno["USERPROFILE"] = entorno["HOME"]
    entorno.update(extra or {})
    return entorno


@pytest.fixture
def correr(instancia):
    """Ejecuta un hook como lo hace Claude Code: proceso aparte, JSON por stdin, respuesta por stdout."""
    (instancia / ".home").mkdir(exist_ok=True)

    def _correr(nombre: str, entrada, env=None, crudo: bytes | None = None):
        datos = crudo if crudo is not None else json.dumps(entrada).encode("utf-8")
        r = subprocess.run([sys.executable, "-I", str(HOOKS / f"{nombre}.py")], input=datos, capture_output=True,
                           env=_entorno_limpio(instancia, env), cwd=str(instancia), timeout=60)
        assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
        salida = r.stdout.decode("utf-8").strip()
        return json.loads(salida) if salida else None

    return _correr


@pytest.fixture
def en_proceso(instancia, monkeypatch, capsys):
    """Ejecuta main() del hook en este proceso (para simular HTTP o forzar un fallo interno)."""
    for k in list(os.environ):
        if k.startswith(VARIABLES_FUERA):
            monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("HOME", str(instancia / ".home"))

    def _ejecutar(nombre: str, entrada: dict):
        import _lib
        _lib.olvidar_fichas()
        modulo = importlib.import_module(nombre)
        monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(json.dumps(entrada).encode("utf-8")),
                                                           encoding="utf-8"))
        codigo = modulo.main()
        texto = capsys.readouterr().out.strip()
        return codigo, (json.loads(texto) if texto else None)

    return _ejecutar
