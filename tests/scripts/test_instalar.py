"""scripts/instalar.sh: idempotente, nunca pisa la instancia, avisa de lo que falta."""
from __future__ import annotations

import json
import os
import subprocess

from apoyo_scripts import necesita_bash

ENV_ARCHIVO = "." + "env"


def _instalar(raiz, bin_dir, *args):
    entorno = {"PATH": str(bin_dir), "HOME": str(raiz.parent), "LANG": "C.UTF-8"}
    return subprocess.run(["bash", "scripts/instalar.sh", *args], cwd=raiz, env=entorno, capture_output=True,
                          text=True, timeout=120)


@necesita_bash
def test_instala_y_crea_la_instancia(copia_producto, bin_falso):
    bin_dir, _ = bin_falso
    r = _instalar(copia_producto, bin_dir)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RESULTADO: listo" in r.stdout
    for carpeta in ("contexto", "clientes", "aprendizajes", "logs", "informes/diario"):
        assert (copia_producto / carpeta).is_dir(), carpeta
    for archivo in ("operador.md", "preferencias.md", "instalacion.json"):
        assert (copia_producto / "contexto" / archivo).is_file(), archivo
    estado = json.loads((copia_producto / "contexto" / "instalacion.json").read_text(encoding="utf-8"))
    assert estado["fases"]["tecnica"]["estado"] == "hecho"
    assert estado["fases"]["perfil"]["estado"] == "pendiente"
    assert estado["sistema"]["uv"] == "9.9.9"
    assert estado["producto"]["version"]
    env = copia_producto / ENV_ARCHIVO
    assert env.read_bytes() == (copia_producto / "plantillas" / "env.ejemplo").read_bytes()
    assert oct(env.stat().st_mode & 0o777) == oct(0o600)


@necesita_bash
def test_segunda_vez_no_pisa_nada(copia_producto, bin_falso):
    bin_dir, _ = bin_falso
    assert _instalar(copia_producto, bin_dir).returncode == 0
    operador = copia_producto / "contexto" / "operador.md"
    operador.write_text("# Operador\n- Empresa: Acme Automations\n", encoding="utf-8")
    env = copia_producto / ENV_ARCHIVO
    env.write_text("META_TOKEN=valor-propio\n", encoding="utf-8")
    inst = copia_producto / "contexto" / "instalacion.json"
    datos = json.loads(inst.read_text(encoding="utf-8"))
    datos["fases"]["perfil"]["estado"] = "hecho"
    inst.write_text(json.dumps(datos), encoding="utf-8")

    r = _instalar(copia_producto, bin_dir)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "ya existía (no lo toco" in r.stdout
    assert operador.read_text(encoding="utf-8") == "# Operador\n- Empresa: Acme Automations\n"
    assert env.read_text(encoding="utf-8") == "META_TOKEN=valor-propio\n"
    despues = json.loads(inst.read_text(encoding="utf-8"))
    assert despues["fases"]["perfil"]["estado"] == "hecho"
    assert despues["fases"]["tecnica"]["estado"] == "hecho"


@necesita_bash
def test_comprobar_no_escribe(copia_producto, bin_falso):
    bin_dir, _ = bin_falso
    r = _instalar(copia_producto, bin_dir, "--comprobar")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "solo comprobación" in r.stdout
    assert not (copia_producto / "contexto").exists()
    assert not (copia_producto / ENV_ARCHIVO).exists()


@necesita_bash
def test_sin_uv_falla_con_instrucciones(copia_producto, bin_falso):
    bin_dir, quitar = bin_falso
    quitar("uv")
    r = _instalar(copia_producto, bin_dir)
    assert r.returncode == 1
    assert "No encuentro uv" in r.stdout
    assert "--instalar-uv" in r.stdout
    assert "RESULTADO: faltan requisitos" in r.stdout
    assert not (copia_producto / "contexto").exists()


@necesita_bash
def test_sin_ffmpeg_solo_avisa(copia_producto, bin_falso):
    bin_dir, quitar = bin_falso
    quitar("ffmpeg")
    r = _instalar(copia_producto, bin_dir)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "[AVISO]  No encuentro FFmpeg" in r.stdout


@necesita_bash
def test_estado_danado_se_copia_y_se_rehace(copia_producto, bin_falso):
    bin_dir, _ = bin_falso
    (copia_producto / "contexto").mkdir()
    (copia_producto / "contexto" / "instalacion.json").write_text("{roto", encoding="utf-8")
    r = _instalar(copia_producto, bin_dir)
    assert r.returncode == 0, r.stdout + r.stderr
    copias = list((copia_producto / "contexto").glob("instalacion.json.danado-*"))
    assert len(copias) == 1 and copias[0].read_text(encoding="utf-8") == "{roto"
    assert json.loads((copia_producto / "contexto" / "instalacion.json").read_text(encoding="utf-8"))


@necesita_bash
def test_opcion_desconocida(copia_producto, bin_falso):
    bin_dir, _ = bin_falso
    assert _instalar(copia_producto, bin_dir, "--nada").returncode == 2


def test_scripts_con_finales_de_linea_unix():
    """Un .sh con CRLF falla en Git Bash con «$'\\r': command not found»."""
    from apoyo_scripts import SCRIPTS
    for f in SCRIPTS.glob("*.sh"):
        assert b"\r\n" not in f.read_bytes(), f.name
    assert os.access(SCRIPTS / "instalar.sh", os.R_OK)
