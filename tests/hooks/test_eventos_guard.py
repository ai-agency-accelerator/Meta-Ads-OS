"""eventos_guard: envíos a la Conversions API con y sin test_event_code."""
from __future__ import annotations

import json

import pytest

from ayudas_hooks import decision, leer_log, motivo, pre_bash

URL = "https://graph.facebook.com/v26.0/000000000000000/events"


@pytest.mark.parametrize("orden", [
    "python3 -I herramientas/capi.py construir --evento Lead --cliente acme",
    "python3 -I herramientas/capi.py validar clientes/acme/privado/evento.json",
    f"curl -G {URL.replace('/events', '')} -d fields=name",
    "python3 -I herramientas/estado.py resumen --json",
])
def test_ordenes_locales_pasan(instancia, correr, orden):
    assert correr("eventos_guard", pre_bash(instancia, orden)) is None


def test_envio_con_codigo_de_prueba_pregunta_informativo(instancia, correr):
    salida = correr("eventos_guard", pre_bash(instancia, "python3 -I herramientas/capi.py enviar --cliente acme "
                                                         "--test-code TEST12345 clientes/acme/privado/evento.json"))
    assert decision(salida) == "ask" and "PRUEBA" in motivo(salida) and "TEST12345" in motivo(salida)


@pytest.mark.parametrize("orden", [
    "python3 -I herramientas/capi.py enviar --cliente acme --real --confirmo clientes/acme/privado/evento.json",
    "python3 -I herramientas/capi.py enviar --cliente acme clientes/acme/privado/evento.json",
    f"curl -X POST {URL} -H 'Content-Type: application/json' -d @clientes/acme/privado/evento.json",
])
def test_evento_real_pregunta_con_aviso(instancia, correr, orden):
    (instancia / "clientes" / "acme" / "privado" / "evento.json").write_text(
        json.dumps({"data": [{"event_name": "Lead", "event_time": 1767225600}]}), encoding="utf-8")
    salida = correr("eventos_guard", pre_bash(instancia, orden))
    assert decision(salida) == "ask" and "EVENTO REAL" in motivo(salida) and "ensucia" in motivo(salida)


def test_curl_con_codigo_de_prueba_en_el_archivo(instancia, correr):
    (instancia / "clientes" / "acme" / "privado" / "prueba.json").write_text(
        json.dumps({"data": [{"event_name": "Lead"}], "test_event_code": "TEST999"}), encoding="utf-8")
    salida = correr("eventos_guard", pre_bash(instancia, f"curl -X POST {URL} -d @clientes/acme/privado/prueba.json"))
    assert decision(salida) == "ask" and "PRUEBA" in motivo(salida)


def test_capi_origen_es_local(instancia, correr):
    orden = "python3 -I herramientas/capi.py origen clientes/acme/privado/webhook.json --json"
    assert correr("eventos_guard", pre_bash(instancia, orden)) is None


def test_evento_real_desde_un_subagente_que_no_es_operador_se_bloquea(instancia, correr):
    orden = "python3 -I herramientas/capi.py enviar --cliente acme --real --confirmo clientes/acme/privado/evento.json"
    entrada = pre_bash(instancia, orden, agent_id="agente-5", agent_type="especialista-tracking")
    salida = correr("eventos_guard", entrada)
    assert decision(salida) == "deny" and "operador-meta" in motivo(salida) and "--test-code" in motivo(salida)
    entrada["agent_type"] = "operador-meta"
    assert decision(correr("eventos_guard", entrada)) == "ask"


def test_prueba_desde_un_subagente_pregunta(instancia, correr):
    orden = "python3 -I herramientas/capi.py enviar --cliente acme --test-code TEST4321 clientes/acme/privado/e.json"
    entrada = pre_bash(instancia, orden, agent_id="agente-5", agent_type="especialista-tracking")
    salida = correr("eventos_guard", entrada)
    assert decision(salida) == "ask" and "PRUEBA" in motivo(salida)


def test_fallo_interno_deja_pasar(instancia, en_proceso, monkeypatch):
    import eventos_guard

    def rota(*a):
        raise ValueError("fallo simulado")

    monkeypatch.setattr(eventos_guard, "evaluar", rota)
    codigo, salida = en_proceso("eventos_guard", pre_bash(instancia, "python3 -I herramientas/capi.py enviar --real"))
    assert codigo == 0 and salida is None
    assert leer_log(instancia, "hooks.jsonl")[-1]["hook"] == "eventos_guard"


# ─────────────────────────────── troceo esquivado (hallazgo 3 de la revisión de seguridad)

def test_comodin_en_capi_desde_un_subagente(instancia, correr):
    orden = "python3 -I herramientas/cap?.py enviar ev.json --cliente acme --real --confirmo"
    salida = correr("eventos_guard", pre_bash(instancia, orden, agent_id="a1", agent_type="analista-meta"))
    assert decision(salida) == "deny"
    salida = correr("eventos_guard", pre_bash(instancia, orden))
    assert decision(salida) == "ask" and "Conversions API" in motivo(salida)


def test_comodin_que_da_capi_se_trata_como_capi(instancia, correr):
    (instancia / "herramientas").mkdir(exist_ok=True)
    (instancia / "herramientas" / "capi.py").write_text("# falso\n", encoding="utf-8")
    orden = "python3 -I herramientas/cap?.py enviar ev.json --cliente acme --real --confirmo"
    salida = correr("eventos_guard", pre_bash(instancia, orden, agent_id="a1", agent_type="analista-meta"))
    assert decision(salida) == "deny" and "operador-meta" in motivo(salida)
    salida = correr("eventos_guard", pre_bash(instancia, "python3 -I herramientas/cap?.py enviar ev.json "
                                                         "--test-code TEST1"))
    assert decision(salida) == "ask" and "PRUEBA" in motivo(salida)


def test_dos_guiones_no_convierten_en_prueba(instancia, correr):
    orden = "python3 -I herramientas/capi.py enviar ev.json --real -- --test-code TEST1"
    salida = correr("eventos_guard", pre_bash(instancia, orden))
    assert decision(salida) == "ask" and "EVENTO REAL" in motivo(salida)


def test_comodines_que_no_envian_no_deciden(instancia, correr):
    for orden in ("ls herramientas/*.py", "python3 -I herramientas/cap?.py construir --evento Lead",
                  "grep -n enviar herramientas/*.py"):
        assert correr("eventos_guard", pre_bash(instancia, orden)) is None, orden
