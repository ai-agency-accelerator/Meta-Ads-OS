"""Ningún rastro de la instancia de origen en el motor: ni rutas personales, ni marcas, clientes, IDs o casos reales.

Los nombres concretos que no pueden aparecer se comparan por huella (sha256 de la palabra en minúsculas), para que
este test no los contenga en claro. Lo genérico (rutas de usuario, IDs con forma real, nombres antiguos del motor) se
busca con expresiones regulares.
"""
from __future__ import annotations

import hashlib
import re

from motor_ia_apoyo import MODULO

# Huellas de nombres de personas, marcas, clientes, carpetas y lugares de la instancia de origen.
HUELLAS = {
    "470adaa55fab37a1", "7f8501c85370a944", "7985a8b8e1885ff7", "6326e0e8cfdaab9a", "87e4571bc7b47363",
    "d1220c5bb333d6e7", "c0a46612b21b1d9e", "0bd36bfd4d80867c", "20d4bc8e0cb2f290", "dcd03e4d72d79de4",
    "2b7b780d32479f9a", "ac357b482949c85e",
}
PALABRA = re.compile(r"[a-z0-9_]+")
GENERICO = re.compile(
    r"/users/[a-z]|\\users\\[a-z]|/home/[a-z]+/|"                       # rutas de un usuario concreto
    r"\b(?:brand|prod|proj|actor|asset)_(?!0{10}\b)[0-9a-f]{10}\b|"      # IDs reales del motor (los de ejemplo son ceros)
    r"\bact_\d{10,}|"                                                     # cuentas publicitarias
    r"almohad|\bpillow\b(?![-_>=\s]*[0-9])|"                              # producto del caso de origen («Pillow» librería sí)
    r"engine/|\bads/|ugc-creative-studio|/producir-ugc|/variantes-ugc|research_notes",  # nombres antiguos del motor
    re.I,
)
TEXTO = {".py", ".md", ".json", ".yaml", ".yml", ".toml", ".html", ".txt", ".js", ".css", ".cfg"}
IGNORAR = {".venv", "data", "__pycache__", ".pytest_cache", "motor.egg-info"}


def _huella(palabra: str) -> str:
    return hashlib.sha256(palabra.encode()).hexdigest()[:16]


def _archivos():
    for p in MODULO.rglob("*"):
        if p.is_file() and p.suffix.lower() in TEXTO and not IGNORAR & set(p.relative_to(MODULO).parts) \
                and p.name != "uv.lock":
            yield p


def test_sin_fugas_personales():
    hallazgos = []
    for p in _archivos():
        for n, linea in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            limpia = re.sub(r"\bPillow\b|pillow>=\d", "", linea)
            if GENERICO.search(limpia) or any(_huella(w) in HUELLAS for w in PALABRA.findall(limpia.lower())):
                hallazgos.append(f"{p.relative_to(MODULO)}:{n}: {linea.strip()[:120]}")
    assert not hallazgos, "\n".join(hallazgos)


def test_las_huellas_detectan_lo_que_deben():
    """Comprobación del propio test con datos inventados (sin nombres reales)."""
    assert GENERICO.search("ver " + "/" + "Users/alguien/x") and GENERICO.search("brand_1a2b3c4d5e")
    assert not GENERICO.search("brand_0000000000 · from PIL import Image · pillow>=10")
    assert _huella("nimbo") not in HUELLAS
