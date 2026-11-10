"""Presupuesto y claves del motor (contrato §14) sobre una raíz temporal. Solo biblioteca estándar, sin red."""
from __future__ import annotations

import os


def _prefs(raiz, texto: str) -> None:
    (raiz / "contexto" / "preferencias.md").write_text(texto, encoding="utf-8")


def test_sin_nada_5_dolares(config_motor):
    cfg, raiz = config_motor
    s = cfg.settings()
    assert (s.budget_global_usd, s.budget_per_project_usd, s.budget_source) == (5.0, 5.0, "por defecto")
    assert s.root == raiz.resolve() and s.mock is False


def test_solo_preferencias_anidadas_da_12(config_motor):
    cfg, raiz = config_motor
    _prefs(raiz, "---\nperfil: agencia\nmotor:\n  presupuesto_usd: 12\n---\n\n# Preferencias\n")
    s = cfg.settings()
    assert s.budget_global_usd == 12.0 and s.budget_source == "contexto/preferencias.md"


def test_preferencias_tolerantes(config_motor):
    cfg, raiz = config_motor
    for texto, esperado in (("---\nmotor:\n    presupuesto_usd: \"12,5\"  # comentario\n---\n", 12.5),
                            ("motor:\n  activo: true\n  presupuesto_usd: $20\n", 20.0),
                            ("motor_presupuesto_usd: 7\n", 7.0),
                            ("---\nmotor:\n  activo: true\notro:\n  presupuesto_usd: 99\n---\n", 5.0)):
        _prefs(raiz, texto)
        cfg.reset_settings()
        assert cfg.settings().budget_global_usd == esperado, texto


def test_entorno_y_env_de_la_raiz_mandan(config_motor, monkeypatch):
    cfg, raiz = config_motor
    _prefs(raiz, "---\nmotor:\n  presupuesto_usd: 12\n---\n")
    (raiz / ".env").write_text("MOTOR_PRESUPUESTO_USD=8\nGEMINI_API_KEY=clave-falsa\n", encoding="utf-8")
    s = cfg.settings()
    assert s.budget_global_usd == 8.0 and s.budget_source == "MOTOR_PRESUPUESTO_USD" and s.has("GEMINI_API_KEY")
    monkeypatch.setenv("MOTOR_PRESUPUESTO_USD", "30")
    cfg.reset_settings()
    assert cfg.settings().budget_global_usd == 30.0


def test_alias_antiguo_y_secretos_con_separador_del_sistema(config_motor, tmp_path, monkeypatch):
    cfg, _ = config_motor
    monkeypatch.setenv("MOTOR_BUDGET_GLOBAL_USD", "15")
    a, b = tmp_path / "a.env", tmp_path / "b.env"
    a.write_text("FAL_KEY=falsa\n", encoding="utf-8")
    b.write_text("GEMINI_API_KEY=no-autorizada\n", encoding="utf-8")
    monkeypatch.setenv("MOTOR_SECRETS_FILES", os.pathsep.join([str(a), str(b)]))
    monkeypatch.setenv("MOTOR_SECRETS_ALLOW", "FAL_KEY")
    s = cfg.settings()
    assert s.budget_global_usd == 15.0 and s.has("FAL_KEY") and not s.has("GEMINI_API_KEY")
