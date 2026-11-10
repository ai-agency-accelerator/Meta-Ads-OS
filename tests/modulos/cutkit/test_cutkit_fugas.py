"""Ningún rastro de la instancia de origen en cutkit: ni rutas personales, ni nombres, marcas, IDs o carpetas antiguas.

Los nombres concretos se comparan por huella (sha256 de la palabra en minúsculas, 16 caracteres) para que el test no
los contenga en claro. Reutiliza las huellas del test del motor (mismo origen) y añade las propias de cutkit.
"""
from __future__ import annotations

import hashlib
import re

from cutkit_apoyo import MODULO, RAIZ_PRODUCTO

_TEST_MOTOR = RAIZ_PRODUCTO / "tests" / "modulos" / "motor_ia" / "test_motor_ia_fugas.py"
HUELLAS = set(re.findall(r'"([0-9a-f]{16})"', _TEST_MOTOR.read_text(encoding="utf-8"))) | {
    "d00aa58329c4732b", "9e66a118b9a0fb8c", "b1802fc2ce7fbf54",
}
PALABRA = re.compile(r"[a-z0-9_]+")
GENERICO = re.compile(
    r"/users/[a-z]|\\users\\[a-z]|/home/[a-z]+/|"                     # rutas de un usuario concreto
    r"\bact_\d{10,}|"                                                   # cuentas publicitarias reales
    r"thumbkit|research_notes|media_library|quote-art32|"              # herramientas y carpetas de la instancia de origen
    r"(?<![a-z_])brand/logos|(?<![a-z_])runs/<|\bbrand_e52a|\bprod_aff4",
    re.I,
)
TEXTO = {".py", ".md", ".json", ".yaml", ".yml", ".toml", ".html", ".txt", ".js", ".css", ".sh", ".cjs"}
IGNORAR = {".venv", "datos", "__pycache__", ".pytest_cache", "node_modules"}
# Textos de terceros que se copian literales (licencias de npm) y bundles minificados
TERCEROS = {"LICENSE.three.txt", "LICENSE.fontkit.txt", "LICENSE.dependencias.txt", "three.ck.min.js",
            "fontkit.ck.min.js"}


def _huella(palabra: str) -> str:
    return hashlib.sha256(palabra.encode()).hexdigest()[:16]


def _archivos():
    for p in MODULO.rglob("*"):
        rel = p.relative_to(MODULO)
        if p.is_file() and p.suffix.lower() in TEXTO and not IGNORAR & set(rel.parts) and p.name not in TERCEROS \
                and p.name != "uv.lock":
            yield p


def test_sin_fugas_personales():
    hallazgos = []
    for p in _archivos():
        for n, linea in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if GENERICO.search(linea) or any(_huella(w) in HUELLAS for w in PALABRA.findall(linea.lower())):
                hallazgos.append(f"{p.relative_to(MODULO)}:{n}: {linea.strip()[:120]}")
    assert not hallazgos, "\n".join(hallazgos)


def test_las_huellas_detectan_lo_que_deben():
    """Comprobación del propio test con datos inventados (sin nombres reales)."""
    assert len(HUELLAS) >= 12, "no se han podido leer las huellas del test del motor"
    assert GENERICO.search("ver " + "/" + "Users/alguien/x") and GENERICO.search("act_1234567890123")
    assert not GENERICO.search("CUTKIT_RUNS=<dir> · clientes/acme/marca/logos/ · act_000")
    assert _huella("acme") not in HUELLAS and _huella("nimbo") not in HUELLAS
