"""scripts/migrar.py y el formato de scripts/migraciones/README.md."""
from __future__ import annotations

import json
import re

import migrar
from apoyo_scripts import RAIZ_PRODUCTO

FICHA = "---\nslug: acme\ncrm:\n  tipo: ghl\n---\n\n# Acme Automations\n"


def _ejemplo_del_readme() -> str:
    readme = (RAIZ_PRODUCTO / "scripts" / "migraciones" / "README.md").read_text(encoding="utf-8")
    return re.search(r"```python\n(.*?)```", readme, re.S).group(1)


def _instancia(tmp_path, codigo: str, nombre: str = "0001_ficha-servidor-mcp.py"):
    raiz = tmp_path / "os"
    (raiz / "clientes" / "acme").mkdir(parents=True)
    (raiz / "clientes" / "acme" / "ficha.md").write_text(FICHA, encoding="utf-8")
    carpeta = tmp_path / "migraciones"
    carpeta.mkdir()
    (carpeta / nombre).write_text(codigo, encoding="utf-8")
    return raiz, carpeta


def _args(raiz, carpeta, *resto):
    return ["--raiz", str(raiz), "--carpeta", str(carpeta), *resto]


def test_producto_sin_migraciones_rotas():
    assert migrar.main(["pendientes", "--json"]) == 0


def test_ejemplo_del_readme_se_aplica_una_vez_con_copia(tmp_path, capsys):
    raiz, carpeta = _instancia(tmp_path, _ejemplo_del_readme())
    assert migrar.main(_args(raiz, carpeta, "pendientes", "--json")) == 0
    assert [m["id"] for m in json.loads(capsys.readouterr().out)] == ["0001_ficha-servidor-mcp"]

    assert migrar.main(_args(raiz, carpeta, "aplicar")) == 0
    salida = capsys.readouterr().out
    assert "[OK]     Migración 0001_ficha-servidor-mcp" in salida
    assert "servidor_mcp: ghl" in (raiz / "clientes" / "acme" / "ficha.md").read_text(encoding="utf-8")
    copias = list((raiz / "logs" / "copias-migracion").glob("*_0001_ficha-servidor-mcp/clientes/acme/ficha.md"))
    assert len(copias) == 1 and copias[0].read_text(encoding="utf-8") == FICHA

    assert migrar.main(_args(raiz, carpeta, "aplicar")) == 0
    assert "Sin migraciones pendientes" in capsys.readouterr().out


def test_migracion_que_falla_para_y_no_sigue(tmp_path, capsys):
    codigo = ("VERSION = '0.2.0'\nDESCRIPCION = 'falla'\nARCHIVOS = ['clientes/*/ficha.md']\n"
              "def necesaria(raiz):\n    return True\n"
              "def aplicar(raiz):\n    raise RuntimeError('formato inesperado')\n")
    raiz, carpeta = _instancia(tmp_path, codigo)
    (carpeta / "0002_otra.py").write_text(
        "VERSION='0.2.0'\nDESCRIPCION='otra'\ndef necesaria(r):\n    return True\n"
        "def aplicar(r):\n    (r / 'tocado').write_text('x')\n    return []\n", encoding="utf-8")
    assert migrar.main(_args(raiz, carpeta, "aplicar")) == 1
    assert "formato inesperado" in capsys.readouterr().out
    assert not (raiz / "tocado").exists()
    assert (raiz / "clientes" / "acme" / "ficha.md").read_text(encoding="utf-8") == FICHA


def test_migracion_incompleta_no_se_carga(tmp_path, capsys):
    raiz, carpeta = _instancia(tmp_path, "VERSION = '0.2.0'\nDESCRIPCION = 'sin funciones'\n")
    assert migrar.main(_args(raiz, carpeta, "aplicar")) == 2
    assert "falta necesaria" in capsys.readouterr().out


def test_nombres_que_no_siguen_el_formato_se_ignoran(tmp_path, capsys):
    raiz, carpeta = _instancia(tmp_path, "esto no es python", nombre="borrador.py")
    assert migrar.main(_args(raiz, carpeta, "aplicar")) == 0
    assert "Sin migraciones pendientes" in capsys.readouterr().out
