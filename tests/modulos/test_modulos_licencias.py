"""Auditoría de licencias de los módulos de vídeo (`modulos/motor-ia` y `modulos/cutkit`), sin red.

Todo archivo binario o de terceros que viaje con un módulo tiene que estar en su `LICENCIAS.md`, llevar su licencia al
lado (fuentes y bundles) y no ser un medio pesado: los vídeos, audios y modelos se generan o se descargan en el
ordenador de cada usuario, nunca se versionan.
"""
from __future__ import annotations

import pathlib

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[2]
MODULOS = {"motor-ia": RAIZ / "modulos" / "motor-ia", "cutkit": RAIZ / "modulos" / "cutkit"}
# Lo que nunca viaja: entornos, cachés y datos que se crean en cada ordenador (ver el .gitignore de cada módulo)
IGNORAR = {".venv", "data", "datos", "__pycache__", ".pytest_cache", "node_modules", "motor.egg-info", "cutkit.egg-info"}
FUENTES = {".ttf", ".otf", ".woff", ".woff2", ".ttc"}
IMAGENES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico"}
MEDIOS = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".mp4", ".mov", ".webm", ".mkv"}
MODELOS = {".onnx", ".bin", ".task", ".pt", ".pth", ".safetensors", ".tflite", ".traineddata"}
MAX_BYTES = 2_000_000


def _archivos(modulo: pathlib.Path):
    for p in modulo.rglob("*"):
        if p.is_file() and not IGNORAR & set(p.relative_to(modulo).parts):
            yield p


def _de_terceros(p: pathlib.Path) -> bool:
    s = p.suffix.lower()
    return s in FUENTES | IMAGENES | MEDIOS | MODELOS or p.name.endswith(".min.js")


@pytest.mark.parametrize("nombre", sorted(MODULOS))
def test_todo_lo_binario_o_de_terceros_esta_en_licencias(nombre):
    modulo = MODULOS[nombre]
    licencias = (modulo / "LICENCIAS.md").read_text(encoding="utf-8")
    faltan = [str(p.relative_to(modulo)) for p in _archivos(modulo) if _de_terceros(p) and p.name not in licencias]
    assert not faltan, f"añade a modulos/{nombre}/LICENCIAS.md: {faltan}"


@pytest.mark.parametrize("nombre", sorted(MODULOS))
def test_fuentes_y_bundles_llevan_su_licencia_al_lado(nombre):
    problemas = []
    for p in _archivos(MODULOS[nombre]):
        if p.suffix.lower() in FUENTES and not list(p.parent.glob("OFL*.txt")) + list(p.parent.glob("LICEN[CS]E*")):
            problemas.append(f"{p.name}: falta el texto de su licencia (OFL-*.txt) en la misma carpeta")
        if p.name.endswith(".min.js") and not list(p.parent.glob("LICENSE*.txt")):
            problemas.append(f"{p.name}: falta LICENSE*.txt en la misma carpeta")
    assert not problemas, "\n".join(problemas)


@pytest.mark.parametrize("nombre", sorted(MODULOS))
def test_sin_medios_ni_modelos_ni_archivos_pesados(nombre):
    modulo = MODULOS[nombre]
    malos = [f"{p.relative_to(modulo)} ({p.stat().st_size // 1024} KB)" for p in _archivos(modulo)
             if p.suffix.lower() in MEDIOS | MODELOS or (p.stat().st_size > MAX_BYTES and p.name != "uv.lock")]
    assert not malos, f"no versiones medios, modelos ni archivos de más de 2 MB en modulos/{nombre}: {malos}"


def test_licencias_de_cutkit_cubren_lo_delicado():
    texto = (MODULOS["cutkit"] / "LICENCIAS.md").read_text(encoding="utf-8")
    for clave in ("CC0", "MMS_FA", "CC-BY-NC", "OFL", "LICENSE.dependencias.txt", "Apache 2.0", "GSAP", "HyperFrames",
                  "derecho de cita"):
        assert clave in texto, clave
    deps = (MODULOS["cutkit"] / "cutkit" / "motion" / "three" / "vendor" / "LICENSE.dependencias.txt").read_text(
        encoding="utf-8")
    for paquete in ("@swc/helpers", "restructure", "unicode-trie", "pako", "brotli"):
        assert paquete in deps, paquete
