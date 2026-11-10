"""ghl_guard: clasificación de execute_operation, registro y llamadas directas a la API de GHL."""
from __future__ import annotations

import pytest

from ayudas_hooks import SESION, decision, leer_log, motivo, post_mcp, pre_bash, pre_mcp, respuesta_mcp

EJ = "mcp__ghl__execute_operation"


@pytest.mark.parametrize("entrada", [
    {"operation_id": "contacts_get-contact", "params": {"contactId": "aBcDeF123456"}},
    {"operation_id": "opportunities_search-opportunity", "body": {"pipelineId": "p1"}},
    {"operation_id": "conversations_get-messages", "params": {"conversationId": "c1"}},
    {"operation_id": "payments_list-transactions", "params": {"startAt": "2026-11-01"}},
    {"operationId": "getContacts"},
    {"method": "GET", "path": "/calendars/events"},
])
def test_lecturas_no_deciden(instancia, correr, entrada):
    # El hook nunca da allow a execute_operation: las lecturas no deciden y pregunta la regla `ask` de settings.json.
    assert correr("ghl_guard", pre_mcp(instancia, EJ, entrada)) is None


# Hallazgo 1 de la revisión de seguridad: la operación salía de la primera clave `name`/`operation_id` que apareciera,
# también dentro del cuerpo. Entradas exactas del informe.
SMS_CUERPO = {"name": "list-vip", "type": "SMS", "contactId": "abc123", "message": "hola"}


@pytest.mark.parametrize("entrada", [
    {"body": SMS_CUERPO, "operation_id": "conversations_send-a-new-message"},
    {"operation_id": "conversations_send-a-new-message", "body": SMS_CUERPO},
])
def test_sms_se_bloquea_en_cualquier_orden_de_claves(instancia, correr, entrada):
    assert decision(correr("ghl_guard", pre_mcp(instancia, EJ, entrada))) == "deny"


def test_nombre_en_el_cuerpo_no_es_la_operacion(instancia, correr):
    entrada = {"body": {"name": "Search VIP", "email": "vip@example.com"}, "operation_id": "contacts_create-contact"}
    salida = correr("ghl_guard", pre_mcp(instancia, EJ, entrada))
    assert decision(salida) == "ask" and "contacts_create-contact" in motivo(salida)
    salida = correr("ghl_guard", pre_mcp(instancia, EJ, entrada, agent_id="a1", agent_type="analista-meta"))
    assert decision(salida) == "deny"


def test_borrado_con_nombre_de_lectura_en_el_cuerpo(instancia, correr):
    entrada = {"body": {"name": "get"}, "operation_id": "contacts_delete-contact"}
    assert decision(correr("ghl_guard", pre_mcp(instancia, EJ, entrada))) == "deny"


def test_varios_ids_de_operacion_preguntan(instancia, correr):
    salida = correr("ghl_guard", pre_mcp(instancia, EJ, {"operation_id": "contacts_get-contact",
                                                         "name": "contacts_update-contact"}))
    assert decision(salida) == "ask" and "varios" in motivo(salida)
    salida = correr("ghl_guard", pre_mcp(instancia, EJ, {"operation_id": "contacts_get-contact",
                                                         "name": "contacts_delete-contact"}))
    assert decision(salida) == "deny"


def test_id_de_operacion_anidado_peligroso(instancia, correr):
    entrada = {"operation_id": "contacts_get-contact",
               "params": {"operation_id": "conversations_send-a-new-message"}}
    assert decision(correr("ghl_guard", pre_mcp(instancia, EJ, entrada))) == "deny"


def test_herramientas_de_descubrimiento_pasan(instancia, correr):
    assert decision(correr("ghl_guard", pre_mcp(instancia, "mcp__ghl__search_operations",
                                                {"query": "contacts"}))) == "allow"
    assert decision(correr("ghl_guard", pre_mcp(instancia, "mcp__ghl__describe_operation",
                                                {"operation_id": "contacts_get-contact"}))) == "allow"


def test_servidor_por_subcuenta_de_agencia(instancia, correr):
    tool = "mcp__ghl-acme__execute_operation"
    salida = correr("ghl_guard", pre_mcp(instancia, tool, {"operation_id": "opportunities_update-opportunity"}))
    assert decision(salida) == "ask" and "«acme»" in motivo(salida)
    assert correr("ghl_guard", pre_mcp(instancia, tool, {"operation_id": "contacts_get-contact"})) is None
    salida = correr("ghl_guard", pre_mcp(instancia, tool, {"operation_id": "conversations_send-a-new-message"}))
    assert decision(salida) == "deny"
    assert decision(correr("ghl_guard", pre_mcp(instancia, "mcp__ghl-acme__list_locations", {}))) == "allow"


@pytest.mark.parametrize("entrada,texto", [
    ({"operation_id": "opportunities_update-opportunity", "body": {"status": "won"}}, "Escritura en GHL"),
    ({"operation_id": "contacts_add-tags", "body": {"tags": ["lead-meta"]}}, "Escritura en GHL"),
    ({"operation_id": "calendars_create-appointment", "body": {"startTime": "2026-11-12T10:00:00"}},
     "confirmaciones automáticas"),
    ({"operation_id": "frobnicate-widget"}, "no sé clasificar"),
    ({"arguments": {"x": 1}}, "no sé clasificar"),
])
def test_escrituras_y_desconocidas_preguntan(instancia, correr, entrada, texto):
    salida = correr("ghl_guard", pre_mcp(instancia, EJ, entrada))
    assert decision(salida) == "ask" and texto in motivo(salida)


@pytest.mark.parametrize("entrada", [
    {"operation_id": "conversations_send-a-new-message", "body": {"type": "SMS", "message": "Hola"}},
    {"operation_id": "contacts_add-contact-to-workflow", "params": {"workflowId": "w1"}},
    {"method": "POST", "path": "/conversations/messages"},
    {"operation_id": "contacts_delete-contact", "params": {"contactId": "aBcDeF123456"}},
    {"method": "DELETE", "path": "/opportunities/o1"},
    {"operation_id": "invoices_create-invoice", "body": {"total": 1500}},
    {"operation_id": "invoices_send-invoice", "params": {"invoiceId": "i1"}},
])
def test_mensajes_borrados_y_facturas_se_bloquean(instancia, correr, entrada):
    assert decision(correr("ghl_guard", pre_mcp(instancia, EJ, entrada))) == "deny"


def test_subagente_de_lectura_no_escribe(instancia, correr):
    entrada = pre_mcp(instancia, EJ, {"operation_id": "contacts_update-contact"}, agent_id="a1",
                      agent_type="especialista-crm")
    assert decision(correr("ghl_guard", entrada)) == "deny"


def test_registro_de_llamadas_y_de_escrituras(instancia, correr):
    entrada = {"operation_id": "contacts_upsert-contact", "body": {"email": "lucia.perez@gmail.com",
                                                                    "phone": "+34 655 443 322"}}
    correr("ghl_guard", pre_mcp(instancia, EJ, entrada))
    llamada = leer_log(instancia, "ghl-mcp.jsonl")[-1]
    assert llamada["operacion"] == "contacts_upsert-contact"
    texto = (instancia / "logs" / "ghl-mcp.jsonl").read_text(encoding="utf-8")
    assert "lucia.perez" not in texto and "655 443 322" not in texto
    correr("ghl_guard", post_mcp(instancia, EJ, entrada, respuesta_mcp({"contact": {"id": "aBcDeF123456"}})))
    cambio = leer_log(instancia, "cambios.jsonl")[-1]
    assert cambio["sistema"] == "ghl" and cambio["cliente"] == "acme" and cambio["session"] == SESION


def test_api_directa(instancia, correr):
    base = "https://services.leadconnectorhq.com"
    assert correr("ghl_guard", pre_bash(instancia, f"curl -s {base}/contacts/?locationId=l1")) is None
    salida = correr("ghl_guard", pre_bash(instancia, f"curl -X POST {base}/conversations/messages -d '{{}}'"))
    assert decision(salida) == "deny"
    salida = correr("ghl_guard", pre_bash(instancia, f"curl -X PUT {base}/opportunities/o1 -d '{{}}'"))
    assert decision(salida) == "ask"


def test_fallo_interno_falla_cerrado(instancia, en_proceso, monkeypatch):
    import ghl_guard

    def rota(*a):
        raise KeyError("fallo simulado")

    monkeypatch.setattr(ghl_guard, "clasificar", rota)
    codigo, salida = en_proceso("ghl_guard", pre_mcp(instancia, EJ, {"operation_id": "contacts_delete-contact"}))
    assert codigo == 0 and decision(salida) == "ask" and "No he podido clasificar" in motivo(salida)
    assert any(r["hook"] == "ghl_guard" and r["decision"] == "error" for r in leer_log(instancia, "hooks.jsonl"))
    codigo, salida = en_proceso("ghl_guard", pre_mcp(instancia, EJ, {"operation_id": "contacts_get-contact"},
                                                     agent_id="a1", agent_type="analista-meta"))
    assert codigo == 0 and decision(salida) == "deny"
