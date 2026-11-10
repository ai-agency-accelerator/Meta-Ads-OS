"""stripe_guard: Stripe de solo lectura (MCP, CLI y curl)."""
from __future__ import annotations

import pytest

from ayudas_hooks import decision, leer_log, motivo, pre_bash, pre_mcp

S = "mcp__stripe__"


@pytest.mark.parametrize("tool,entrada", [
    ("stripe_api_read", {"stripe_api_operation_id": "GetCustomers", "parameters": {"limit": 10}}),
    ("stripe_api_search", {"intent": "suscripciones activas", "resource": "subscriptions"}),
    ("get_stripe_account_info", {}),
    ("list_subscriptions", {"status": "trialing"}),
    ("search_stripe_documentation", {"question": "metadata en customers"}),
])
def test_lecturas_pasan(instancia, correr, tool, entrada):
    assert decision(correr("stripe_guard", pre_mcp(instancia, S + tool, entrada))) == "allow"
    assert leer_log(instancia, "stripe-mcp.jsonl")[-1]["tool"] == S + tool


def test_servidor_por_cliente(instancia, correr):
    assert decision(correr("stripe_guard", pre_mcp(instancia, "mcp__stripe-nimbo__stripe_api_write",
                                                   {"stripe_api_operation_id": "PostRefunds"}))) == "deny"
    assert decision(correr("stripe_guard", pre_mcp(instancia, "mcp__stripe-nimbo__stripe_api_read",
                                                   {"stripe_api_operation_id": "GetSubscriptions"}))) == "allow"


@pytest.mark.parametrize("tool,entrada", [
    ("stripe_api_write", {"stripe_api_operation_id": "PostRefunds", "parameters": {"charge": "ch_1"}}),
    ("stripe_api_read", {"stripe_api_operation_id": "PostCustomers", "parameters": {}}),
    ("create_refund", {"payment_intent": "pi_1"}),
    ("cancel_subscription", {"subscription": "sub_1"}),
    ("send_money", {"amount": 1000}),
    ("herramienta_nueva_desconocida", {}),
])
def test_escrituras_y_desconocidas_se_bloquean(instancia, correr, tool, entrada):
    assert decision(correr("stripe_guard", pre_mcp(instancia, S + tool, entrada))) == "deny"


@pytest.mark.parametrize("orden,esperado", [
    ("stripe customers list --limit 5", None),
    ("stripe get /v1/subscriptions", None),
    ("stripe customers create --email prueba@example.com", "deny"),
    ("stripe subscriptions cancel sub_123", "deny"),
    ("stripe post /v1/refunds -d charge=ch_1", "deny"),
    ("stripe trigger payment_intent.succeeded", "deny"),
    ("curl https://api.stripe.com/v1/customers -G -d limit=3", None),
    ("curl -X POST https://api.stripe.com/v1/refunds -d charge=ch_1", "deny"),
])
def test_cli_y_curl(instancia, correr, orden, esperado):
    assert decision(correr("stripe_guard", pre_bash(instancia, orden))) == esperado


def test_fallo_interno_falla_cerrado(instancia, en_proceso, monkeypatch):
    import stripe_guard

    def rota(*a):
        raise TypeError("fallo simulado")

    monkeypatch.setattr(stripe_guard, "es_lectura", rota)
    codigo, salida = en_proceso("stripe_guard", pre_mcp(instancia, S + "stripe_api_read",
                                                        {"stripe_api_operation_id": "PostRefunds"}))
    assert codigo == 0 and decision(salida) == "ask"
    assert any(r["decision"] == "error" for r in leer_log(instancia, "hooks.jsonl"))
    codigo, salida = en_proceso("stripe_guard", pre_mcp(instancia, S + "stripe_api_read", {}, agent_id="a1",
                                                        agent_type="analista-meta"))
    assert codigo == 0 and decision(salida) == "deny"


# Hallazgo 10 de la revisión de seguridad: la operación salía de la primera clave encontrada al recorrer todo, así
# que un `params.operation` de lectura tapaba el `stripe_api_operation_id` de escritura. Entrada exacta del informe.
def test_operacion_anidada_no_tapa_la_de_primer_nivel(instancia, correr):
    entrada = {"params": {"operation": "GetCharges"}, "stripe_api_operation_id": "PostRefunds"}
    salida = correr("stripe_guard", pre_mcp(instancia, S + "stripe_api_read", entrada))
    assert decision(salida) == "deny" and "PostRefunds" in motivo(salida)


@pytest.mark.parametrize("entrada,esperado", [
    ({"stripe_api_operation_id": "GetCharges", "parameters": {"operation_id": "PostRefunds"}}, "deny"),
    ({"stripe_api_operation_id": "GetCharges", "operation": "GetCustomers"}, "ask"),
    ({"parameters": {"limit": 3}}, "ask"),
    ({"stripe_api_operation_id": "post /v1/refunds"}, "deny"),
])
def test_conflictos_y_operacion_ausente(instancia, correr, entrada, esperado):
    assert decision(correr("stripe_guard", pre_mcp(instancia, S + "stripe_api_read", entrada))) == esperado
