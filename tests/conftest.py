"""Fixtures compartidas. Ningún test usa red ni la instancia real del usuario."""
from __future__ import annotations

import importlib
import pathlib
import shutil
import sys

import pytest

RAIZ_PRODUCTO = pathlib.Path(__file__).resolve().parent.parent
sys.path[:0] = [str(RAIZ_PRODUCTO / "herramientas"), str(RAIZ_PRODUCTO / ".claude" / "hooks")]

FICHA_ACME = """---
slug: acme
nombre: Acme Automations
estado: activo
tipo: servicios-high-ticket
relacion: propio
moneda: EUR
zona_horaria: Europe/Madrid
meta:
  cuenta: act_000000000000000
  pagina: ""
  instagram: ""
  dataset: "000000000000000"
  catalogo: ""
  evento_principal: Lead
  ventana_atribucion: 7d_click_1d_view
topes:
  cambio_dia: 100
  total_dia: 300
crm:
  tipo: ghl
  servidor_mcp: ghl
stripe: false
mejoras_automaticas: off
explorar_explotar: 0.3
---

# Acme Automations (empresa ficticia de ejemplo)
"""


@pytest.fixture
def instancia(tmp_path, monkeypatch):
    """Instancia falsa con un cliente `acme` y la plantilla de cliente copiada.

    Fija META_ADS_OS_RAIZ y CLAUDE_PROJECT_DIR en el directorio temporal y recarga `_comun`.
    Devuelve la ruta raíz de la instancia.
    """
    raiz = tmp_path / "os"
    shutil.copytree(RAIZ_PRODUCTO / "plantillas" / "cliente", raiz / "clientes" / "acme")
    (raiz / "clientes" / "acme" / "ficha.md").write_text(FICHA_ACME, encoding="utf-8")
    (raiz / "contexto").mkdir(parents=True)
    (raiz / "logs").mkdir()
    monkeypatch.setenv("META_ADS_OS_RAIZ", str(raiz))
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(raiz))
    import _comun
    importlib.reload(_comun)
    yield raiz
    monkeypatch.delenv("META_ADS_OS_RAIZ")
    importlib.reload(_comun)
