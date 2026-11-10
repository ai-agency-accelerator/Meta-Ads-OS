"""Utilidades de los tests de `scripts/` (bloque B9). Se importa como `apoyo_scripts` (no como `conftest`)."""
from __future__ import annotations

import os
import pathlib
import shutil
import sys

import pytest

RAIZ_PRODUCTO = pathlib.Path(__file__).resolve().parents[2]
SCRIPTS = RAIZ_PRODUCTO / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

BASH = shutil.which("bash")
GIT = shutil.which("git")
necesita_bash = pytest.mark.skipif(not BASH or os.name == "nt", reason="necesita bash en Mac o Linux")
necesita_git = pytest.mark.skipif(not GIT, reason="necesita git")
