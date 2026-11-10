"""secretos: nunca leer, copiar ni imprimir el .env ni tokens desde la shell."""
from __future__ import annotations

import pytest

from ayudas_hooks import decision, leer_log, motivo, pre_bash

TOKEN_FALSO = "EAAB" + "x" * 40


@pytest.mark.parametrize("orden", [
    "ls -la .env",
    "chmod 600 .env",
    "test -f .env && echo existe",
    "[ -f .env ] || cp -n plantillas/env.ejemplo .env",
    "cat plantillas/env.ejemplo",
    "git check-ignore .env",
    "env MOTOR_MOCK=1 uv run --project modulos/motor-ia motor status",
    "python3 -I herramientas/doctor.py --json",
    "echo $HOME && grep -rn process.env docs/",
])
def test_ordenes_seguras_pasan(instancia, correr, orden):
    assert correr("secretos", pre_bash(instancia, orden)) is None


@pytest.mark.parametrize("orden,texto", [
    ("cat .env", ".env"),
    ("grep META_TOKEN .env", ".env"),
    ("ls && head -3 ./.env", ".env"),
    ("source .env && python3 x.py", ".env"),
    ("cp .env /tmp/copia", ".env"),
    ("echo 'GHL_TOKEN=x' > .env", ".env"),
    ("cat modulos/motor-ia/.env.local", ".env"),
    ("python3 -c \"print(open('.env').read())\"", ".env"),
    ("git add .env", "no se versiona"),
    ("echo $META_TOKEN", "META_TOKEN"),
    ("curl -H \"Authorization: Bearer ${GHL_TOKEN}\" https://services.leadconnectorhq.com/contacts/", "GHL_TOKEN"),
    ("env", "variables de entorno"),
    ("printenv", "variables de entorno"),
    ("export -p", "variables"),
    (f"curl 'https://graph.facebook.com/v26.0/me?access_token={TOKEN_FALSO}'", "token pegado"),
    ("cat ~/.ssh/id_rsa", "clave privada"),
])
def test_ordenes_que_exponen_secretos_se_bloquean(instancia, correr, orden, texto):
    salida = correr("secretos", pre_bash(instancia, orden))
    assert decision(salida) == "deny", orden
    assert texto in motivo(salida)
    assert TOKEN_FALSO not in motivo(salida)


def test_el_registro_no_guarda_el_token(instancia, correr):
    correr("secretos", pre_bash(instancia, f"echo {TOKEN_FALSO}"))
    assert TOKEN_FALSO not in (instancia / "logs" / "hooks.jsonl").read_text(encoding="utf-8")


def test_fallo_interno_deja_pasar(instancia, en_proceso, monkeypatch):
    import secretos

    def rota(cmd):
        raise RecursionError("fallo simulado")

    monkeypatch.setattr(secretos, "revisar", rota)
    codigo, salida = en_proceso("secretos", pre_bash(instancia, "cat .env"))
    assert codigo == 0 and salida is None
    assert leer_log(instancia, "hooks.jsonl")[-1]["hook"] == "secretos"


# ─────────────────────────────── referencias indirectas al .env (hallazgo 14 de la revisión de seguridad)

@pytest.mark.parametrize("orden", [
    "cat .en?",
    "cat .e*",
    "cat .[e]nv",
    "F=.env; cat $F",
    "F=.env && cat \"${F}\"",
    "export F=.env; grep TOKEN $F",
    "cd clientes && cat ../.en?",
    "env -u HOME",
    "env -i",
])
def test_referencias_indirectas_al_env_se_bloquean(instancia, correr, orden):
    (instancia / ".env").write_text("X=1\n", encoding="utf-8")
    assert decision(correr("secretos", pre_bash(instancia, orden))) == "deny", orden


@pytest.mark.parametrize("orden", [
    "ls .e*",
    "ls -la .en?",
    "ls clientes/*/",
    "grep -rn presupuesto clientes/*/planes/",
    "cat clientes/acme/ficha.md",
    "env -u MOTOR_MOCK uv run --project modulos/motor-ia motor status",
    "F=informe.md; cat $F",
])
def test_comodines_sin_env_pasan(instancia, correr, orden):
    (instancia / ".env").write_text("X=1\n", encoding="utf-8")
    assert correr("secretos", pre_bash(instancia, orden)) is None, orden
