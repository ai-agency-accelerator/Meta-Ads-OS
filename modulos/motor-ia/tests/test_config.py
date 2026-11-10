"""Configuración del motor: raíz del producto, claves del `.env` de la raíz y presupuesto (contrato §14). Sin red."""

from __future__ import annotations

import os

import pytest

from motor import config

VARS = ("MOTOR_PRESUPUESTO_USD", "MOTOR_BUDGET_GLOBAL_USD", "MOTOR_PRESUPUESTO_PROYECTO_USD", "MOTOR_BUDGET_PER_PROJECT_USD",
        "MOTOR_SECRETS_FILES", "MOTOR_SECRETS_ALLOW", "MOTOR_MOCK", *config.KNOWN_KEYS)


@pytest.fixture
def raiz(tmp_path, monkeypatch):
    """Raíz temporal del producto (nunca la real) con `contexto/` y datos del motor en tmp."""
    r = tmp_path / "os"
    (r / "contexto").mkdir(parents=True)
    for v in VARS:
        monkeypatch.delenv(v, raising=False)
    monkeypatch.setenv("META_ADS_OS_RAIZ", str(r))
    monkeypatch.setenv("MOTOR_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setattr(config, "MODULE_ROOT", tmp_path / "modulo_sin_env")  # que no lea un .env antiguo del módulo
    config.reset_settings()
    yield r
    config.reset_settings()


def _prefs(r, text: str) -> None:
    (r / "contexto" / "preferencias.md").write_text(text, encoding="utf-8")


def test_sin_nada_el_presupuesto_es_5(raiz):
    s = config.settings()
    assert s.budget_global_usd == 5.0 and s.budget_per_project_usd == 5.0 and s.budget_source == "por defecto"
    assert s.root == raiz.resolve()


def test_preferencias_anidadas(raiz):
    _prefs(raiz, "---\nperfil: agencia\nmotor:\n  presupuesto_usd: 12\n---\n\n# Preferencias\n")
    s = config.settings()
    assert s.budget_global_usd == 12.0 and s.budget_source == "contexto/preferencias.md"
    assert s.budget_per_project_usd == 12.0


@pytest.mark.parametrize("texto,esperado", [
    ("---\nmotor:\n    presupuesto_usd: \"12,5\"  # sube cuando quieras\n---\n", 12.5),
    ("motor:\n  activo: true\n  presupuesto_usd: $20\n", 20.0),
    ("- motor_presupuesto_usd: 7\n", 7.0),  # clave plana antigua (compatibilidad)
    ("---\nmotor:\n  activo: true\notro:\n  presupuesto_usd: 99\n---\n", 5.0),  # fuera del bloque motor: no cuenta
])
def test_preferencias_tolerantes(raiz, texto, esperado):
    _prefs(raiz, texto)
    assert config.settings().budget_global_usd == esperado


def test_el_entorno_manda_sobre_preferencias(raiz, monkeypatch):
    _prefs(raiz, "---\nmotor:\n  presupuesto_usd: 12\n---\n")
    monkeypatch.setenv("MOTOR_PRESUPUESTO_USD", "30")
    s = config.settings()
    assert s.budget_global_usd == 30.0 and s.budget_source == "MOTOR_PRESUPUESTO_USD"


def test_el_env_de_la_raiz_manda_sobre_preferencias(raiz):
    _prefs(raiz, "---\nmotor:\n  presupuesto_usd: 12\n---\n")
    (raiz / ".env").write_text("MOTOR_PRESUPUESTO_USD=8\nGEMINI_API_KEY=clave-falsa-de-prueba\n", encoding="utf-8")
    s = config.settings()
    assert s.budget_global_usd == 8.0
    assert s.has("GEMINI_API_KEY")


def test_alias_antiguo_y_presupuesto_por_proyecto(raiz, monkeypatch):
    monkeypatch.setenv("MOTOR_BUDGET_GLOBAL_USD", "15")
    monkeypatch.setenv("MOTOR_PRESUPUESTO_PROYECTO_USD", "4")
    s = config.settings()
    assert s.budget_global_usd == 15.0 and s.budget_per_project_usd == 4.0


def test_secrets_files_usa_el_separador_del_sistema(raiz, tmp_path, monkeypatch):
    a, b = tmp_path / "a.env", tmp_path / "b.env"
    a.write_text("FAL_KEY=falsa-a\n", encoding="utf-8")
    b.write_text("OPENAI_API_KEY=falsa-b\nGEMINI_API_KEY=no-autorizada\n", encoding="utf-8")
    monkeypatch.setenv("MOTOR_SECRETS_FILES", os.pathsep.join([str(a), str(b)]))
    monkeypatch.setenv("MOTOR_SECRETS_ALLOW", "FAL_KEY,OPENAI_API_KEY")
    s = config.settings()
    assert s.has("FAL_KEY") and s.has("OPENAI_API_KEY") and not s.has("GEMINI_API_KEY")


def test_mock(raiz, monkeypatch):
    monkeypatch.setenv("MOTOR_MOCK", "1")
    assert config.settings().mock is True
