"""Fixtures de los tests de `scripts/` (bloque B9). Sin red: los programas externos se simulan con atajos."""
from __future__ import annotations

import shutil
import stat
import sys

import pytest

from apoyo_scripts import RAIZ_PRODUCTO


def _atajo(carpeta: pathlib.Path, nombre: str, salida: str) -> None:
    f = carpeta / nombre
    f.write_text(f"#!/bin/sh\necho '{salida}'\n", encoding="utf-8")
    f.chmod(f.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


@pytest.fixture
def bin_falso(tmp_path):
    """Carpeta de PATH con lo mínimo que usan los scripts: utilidades reales, python, git y atajos de uv y FFmpeg.

    Devuelve (carpeta, función para quitar un programa).
    """
    carpeta = tmp_path / "bin"
    carpeta.mkdir()
    for prog in ("uname", "dirname", "sed", "head", "tr", "awk", "cp", "mkdir", "chmod", "git", "cat", "grep",
                 "sort", "date", "mv", "rm", "ls", "env", "sh", "bash"):
        real = shutil.which(prog)
        if real:
            (carpeta / prog).symlink_to(real)
    (carpeta / "python3").symlink_to(sys.executable)
    _atajo(carpeta, "uv", "uv 9.9.9 (prueba)")
    _atajo(carpeta, "ffmpeg", "ffmpeg version 9.9 Copyright (c) prueba")

    def quitar(prog: str) -> None:
        (carpeta / prog).unlink()

    return carpeta, quitar


@pytest.fixture
def copia_producto(tmp_path):
    """Copia mínima del producto para ejecutar el instalador sin tocar el repositorio real."""
    destino = tmp_path / "os"
    for parte in ("scripts", "plantillas", "herramientas"):
        if (RAIZ_PRODUCTO / parte).is_dir():
            shutil.copytree(RAIZ_PRODUCTO / parte, destino / parte,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for archivo in ("pyproject.toml", "CHANGELOG.md", ".gitignore", "clientes/README.md", "aprendizajes/README.md"):
        if (RAIZ_PRODUCTO / archivo).is_file():
            (destino / archivo).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(RAIZ_PRODUCTO / archivo, destino / archivo)
    return destino
