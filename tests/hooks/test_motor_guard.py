"""motor_guard: órdenes de pago del motor (contrato §14), modo simulado y lecturas de archivos del motor."""
from __future__ import annotations

import pytest

from ayudas_hooks import decision, leer_log, motivo, pre_bash

M = "uv run --project modulos/motor-ia motor"


@pytest.mark.parametrize("orden", [
    f"{M} status",
    f"{M} costs p-0001",
    f"{M} plan-import clientes/acme/creativos/plan.json acme producto",
    f'{M} variant p-0001 hook_text "¿Pierdes 10 horas a la semana?"',
    f"{M} variant p-0001 aspect 4:5",
    f"MOTOR_MOCK=1 {M} run p-0001",
    f"MOTOR_MOCK=1 {M} edit p-0001 \"sube la música\"",
    f"export MOTOR_MOCK=1 && {M} demo",
    "cat modulos/motor-ia/scripts/flow_style.py",
    "python3 modulos/motor-ia/scripts/pov_broll.py list",
    "python3 -I herramientas/motor_proyectos.py",
])
def test_ordenes_gratis_o_simuladas_pasan(instancia, correr, orden):
    assert correr("motor_guard", pre_bash(instancia, orden)) is None


@pytest.mark.parametrize("orden,texto", [
    (f"{M} run p-0001", "producir un anuncio"),
    (f"{M} regen p-0001 escena-2", "regenerar"),
    (f"{M} demo", "prueba real"),
    (f'{M} actor create --handle @nora --appearance "30 años"', "actor"),
    (f'{M} edit p-0001 "cambia el plano 3" --yes', "edición de pago"),
    (f'{M} variant p-0001 spoken_cta "Reserva tu llamada"', "spoken_cta"),
    (f"{M} variant p-0001 language en-US", "language"),
    (f"{M} gc", "borra temporales"),
    ("python3 modulos/motor-ia/scripts/flow_style.py gen_a escena-1", "flow_style.py"),
    ("cd modulos/motor-ia && .venv/bin/motor run p-0002", "producir un anuncio"),
    (f"MOTOR_MOCK=1 true && {M} run p-0003", "producir un anuncio"),  # el simulado solo vale para su orden
    # Hallazgo 15: `edit` sin `--yes` también llama al LLM y ejecuta órdenes de hasta 0,05 $.
    (f'{M} edit p-0001 "sube la música"', "hasta ~0,05 $"),
    (f'{M} edit P1 "regenera la escena 3"', "hasta ~0,05 $"),
    # Hallazgo 8: entradas exactas del informe.
    ("MOTOR_MOCK=1 env -u MOTOR_MOCK uv run --project modulos/motor-ia motor run P1", "producir un anuncio"),
    ("export MOTOR_MOCK=1; env -u MOTOR_MOCK uv run --project modulos/motor-ia motor run P1",
     "producir un anuncio"),
    ("MOTOR_MOCK=1 env -i PATH=/usr/bin uv run --project modulos/motor-ia motor run P1", "producir un anuncio"),
    ("uv run --project modulos/motor-ia python -m motor.cli run P1", "producir un anuncio"),
    ("cd modulos/motor-ia && .venv/bin/python -m motor run P1", "producir un anuncio"),
    ("uv run --project modulos/motor-ia motor serve", "servidor que puede producir vídeo de pago"),
    ("uv run --project modulos/motor-ia motor -- run P1", "producir un anuncio"),
])
def test_ordenes_de_pago_preguntan(instancia, correr, orden, texto):
    salida = correr("motor_guard", pre_bash(instancia, orden))
    assert decision(salida) == "ask"
    assert texto in motivo(salida) and "/motor" in motivo(salida)
    assert leer_log(instancia, "motor.jsonl")[-1]["comando"].startswith(orden[:20])


def test_mock_del_entorno_de_la_sesion(instancia, correr):
    assert correr("motor_guard", pre_bash(instancia, f"{M} run p-0001"), env={"MOTOR_MOCK": "1"}) is None


def test_fallo_interno_deja_pasar(instancia, en_proceso, monkeypatch):
    import motor_guard

    def rota(seg):
        raise RuntimeError("fallo simulado")

    monkeypatch.setattr(motor_guard, "orden_de_pago", rota)
    codigo, salida = en_proceso("motor_guard", pre_bash(instancia, f"{M} run p-0001"))
    assert codigo == 0 and salida is None
    assert leer_log(instancia, "hooks.jsonl")[-1]["decision"] == "error"


CK = "uv run --project modulos/cutkit ck"


@pytest.mark.parametrize("orden", [
    f'{CK} anuncio brutos/toma.mp4 --cliente acme --hook "¿Copias leads a mano?" --subtitulos toma.srt',
    f"{CK} anuncio brutos/toma.mp4 --cliente acme --subtitulos local",
    f"{CK} qa acme v1 --no-judge",
    f"{CK} run acme v1 --budget 0",
    f"{CK} instalar",
    f"CK_ASR=local {CK} anuncio brutos/toma.mp4 --cliente acme",
    "grep -n judge modulos/cutkit/cutkit/cli.py",
    "python3 modulos/motor-ia/scripts/flow_style.py validar --receta r.json",
    "python3 modulos/motor-ia/scripts/flow_style.py plan --receta r.json",
    "python3 modulos/motor-ia/scripts/flow_style.py gen_a k.png --receta r.json --simular",
    "python3 modulos/motor-ia/scripts/pov_broll.py keyframe calle --planos p.json --simular",
])
def test_cutkit_y_scripts_gratis_pasan(instancia, correr, orden):
    assert correr("motor_guard", pre_bash(instancia, orden)) is None


@pytest.mark.parametrize("orden,texto", [
    (f"{CK} anuncio brutos/toma.mp4 --cliente acme --subtitulos openai", "OpenAI"),
    (f"{CK} anuncio brutos/toma.mp4 --cliente acme --subtitulos=openai", "OpenAI"),
    (f"{CK} qa acme v1 --judge", "juez"),
    (f"{CK} run acme v1 --budget 2.5", "2.5 $"),
    (f"{CK} run acme v1 --budget=1", "1 $"),
    (f"CK_ASR=openai {CK} anuncio brutos/toma.mp4 --cliente acme", "OpenAI"),
    (f"CK_MUSICA_IA=1 {CK} anuncio brutos/toma.mp4 --cliente acme", "Lyria"),
    (f"export CK_MUSICA_IA=1 && {CK} anuncio brutos/toma.mp4 --cliente acme", "Lyria"),
    # Hallazgo 2: la misma regla de verdad que cutkit (1, true, si, sí, yes, en cualquier capitalización).
    ("CK_MUSICA_IA=true uv run --project modulos/cutkit ck anuncio acme v1", "Lyria"),
    ("CK_MUSICA_IA=si uv run --project modulos/cutkit ck anuncio acme v1", "Lyria"),
    (f"CK_MUSICA_IA=SÍ {CK} anuncio acme v1", "Lyria"),
    (f"CK_MUSICA_IA=Yes {CK} anuncio acme v1", "Lyria"),
    (f"CK_MUSICA_IA=1 uv run --project modulos/cutkit python -m cutkit anuncio acme v1", "Lyria"),
    ("python3 modulos/motor-ia/scripts/auto_produce.py --simular", "auto_produce.py"),
])
def test_opciones_de_pago_de_cutkit_preguntan(instancia, correr, orden, texto):
    salida = correr("motor_guard", pre_bash(instancia, orden))
    assert decision(salida) == "ask"
    assert texto in motivo(salida) and "/motor" in motivo(salida)


@pytest.mark.parametrize("valor", ["0", "no", "false", "nada"])
def test_cutkit_musica_ia_desactivada(instancia, correr, valor):
    assert correr("motor_guard", pre_bash(instancia, f"CK_MUSICA_IA={valor} {CK} anuncio acme v1")) is None


def test_cutkit_musica_ia_en_el_env_con_true(instancia, correr):
    # Hallazgo 2: el `.env` con `true` (no solo `1`) también es de pago. El hook no imprime el valor.
    (instancia / ".env").write_text("CK_MUSICA_IA=true\n", encoding="utf-8")
    salida = correr("motor_guard", pre_bash(instancia, "uv run --project modulos/cutkit ck anuncio acme v1"))
    assert decision(salida) == "ask" and "Lyria" in motivo(salida)
    salida = correr("motor_guard", pre_bash(instancia, f"env -u CK_MUSICA_IA {CK} anuncio acme v1"))
    assert decision(salida) == "ask"  # cutkit vuelve a leer el .env


@pytest.mark.parametrize("orden", [
    "python3 modulos/motor-ia/scripts/flow_st*.py gen_a escena-1",
    "S=flow_style; python3 modulos/motor-ia/scripts/$S.py gen_a escena-1",
    "uv run --project modulos/motor-ia python -c 'import runpy; runpy.run_module(\"motor\", run_name=\"__main__\")'",
])
def test_ejecucion_opaca_en_modulos(instancia, correr, orden):
    salida = correr("motor_guard", pre_bash(instancia, orden))
    assert decision(salida) == "ask" and "No puedo saber qué ejecuta" in motivo(salida)
    salida = correr("motor_guard", pre_bash(instancia, orden, agent_id="a1", agent_type="productor-ugc"))
    assert decision(salida) == "deny"


def test_cutkit_con_variables_de_pago_en_el_env(instancia, correr):
    (instancia / ".env").write_text("CK_MUSICA_IA=1\n", encoding="utf-8")
    salida = correr("motor_guard", pre_bash(instancia, f"{CK} anuncio brutos/toma.mp4 --cliente acme"))
    assert decision(salida) == "ask" and "Lyria" in motivo(salida)
    salida = correr("motor_guard", pre_bash(instancia, f"unset CK_MUSICA_IA; {CK} anuncio b.mp4"))
    assert decision(salida) == "ask"  # cutkit vuelve a leer el .env
    salida = correr("motor_guard", pre_bash(instancia, f"CK_MUSICA_IA=0 {CK} anuncio b.mp4"))
    assert salida is None
