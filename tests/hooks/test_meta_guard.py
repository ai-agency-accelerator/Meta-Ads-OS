"""meta_guard: registro, topes por cambio (céntimos, monedas, cliente), tope total con token, paciencia y Bash."""
from __future__ import annotations

import json
from datetime import datetime, timedelta

import pytest

from ayudas_hooks import CUENTA, SESION, decision, escribir_log, ficha, leer_log, motivo, post_mcp, respuesta_mcp
from ayudas_hooks import pre_bash as _pre_bash
from ayudas_hooks import pre_mcp as _pre_mcp

T = "mcp__meta-ads__"
OPERADOR = {"agent_id": "agente-op", "agent_type": "operador-meta"}


def pre_mcp(raiz, tool, entrada, principal=False, **extra):
    """Por defecto, como `operador-meta` (el único que escribe en Meta); `principal=True`, desde la sesión principal."""
    return _pre_mcp(raiz, tool, entrada, **{**({} if principal else OPERADOR), **extra})


def pre_bash(raiz, orden, principal=False, **extra):
    return _pre_bash(raiz, orden, **{**({} if principal else OPERADOR), **extra})


def _ts(dias: float = 0) -> str:
    return (datetime.now() - timedelta(days=dias)).isoformat(timespec="seconds")


# ─────────────────────────────── permitir


def test_lectura_no_decide_y_queda_registrada(instancia, correr):
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_get_ad_entities",
                                          {"ad_account_id": CUENTA, "entity_type": "campaign"}))
    assert salida is None
    filas = leer_log(instancia, "meta-mcp.jsonl")
    assert filas[-1]["tool"] == T + "ads_get_ad_entities" and filas[-1]["session"] == SESION
    assert set(filas[-1]) >= {"ts", "evento", "tool", "agente", "session", "input"}


def test_bash_de_lectura_no_decide(instancia, correr):
    for orden in ("python3 -I herramientas/meta_ads.py --cliente acme vigente",
                  "python3 -I herramientas/meta_ads.py crear clientes/acme/planes/plan.json --simular",
                  "curl -G https://graph.facebook.com/v26.0/act_000000000000000/campaigns -d fields=name"):
        assert correr("meta_guard", pre_bash(instancia, orden)) is None, orden


# ─────────────────────────────── preguntar


def test_crear_campana_pregunta_y_recuerda_la_pausa(instancia, correr):
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_create_campaign",
                                          {"ad_account_id": CUENTA, "name": "ES_LEADS_ADQ_HV",
                                           "objective": "OUTCOME_LEADS"}))
    assert decision(salida) == "ask"
    assert "PAUSA" in motivo(salida) and "acme" in motivo(salida)


def test_presupuesto_en_centimos_bajo_el_tope_pregunta(instancia, correr):
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_update_entity",
                                          {"ad_account_id": CUENTA, "entity_id": "120000000000000001",
                                           "fields": {"daily_budget": 5000}}))
    assert decision(salida) == "ask"
    assert "50 €/día" in motivo(salida)


def test_activar_pregunta_con_aviso_de_gasto(instancia, correr):
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_activate_entity",
                                          {"ad_account_id": CUENTA, "entity_id": "120000000000000001"}))
    assert decision(salida) == "ask"
    assert "EMPIEZA A GASTAR" in motivo(salida)


def test_valor_ambiguo_pregunta_por_la_unidad(instancia, correr):
    (instancia / "clientes" / "acme" / "ficha.md").write_text(ficha("acme", CUENTA, 30, 90), encoding="utf-8")
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_update_entity",
                                          {"ad_account_id": CUENTA, "entity_id": "120000000000000001",
                                           "daily_budget": 50}))
    assert decision(salida) == "ask"
    assert "céntimos" in motivo(salida)


def test_cliente_no_deducible_usa_el_tope_mas_estricto(instancia, correr):
    otra = instancia / "clientes" / "clinica-sonrisa"
    otra.mkdir()
    (otra / "ficha.md").write_text(ficha("clinica-sonrisa", "act_000000000000001", 50, 150), encoding="utf-8")
    entrada = pre_mcp(instancia, T + "ads_update_entity", {"entity_id": "120000000000000077", "daily_budget": 4000})
    salida = correr("meta_guard", entrada)
    assert decision(salida) == "ask" and "más estricto" in motivo(salida)
    entrada["tool_input"]["daily_budget"] = 6000
    assert decision(correr("meta_guard", entrada)) == "deny"


def test_regla_de_paciencia(instancia, correr):
    escribir_log(instancia, "cambios.jsonl", [{"ts": _ts(3), "session": "otra", "sistema": "meta", "via": "mcp",
                                               "accion": "ads_update_entity", "entidad_id": "120000000000000002",
                                               "cliente": "acme", "detalle": "daily_budget=3000"}])
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_update_entity",
                                          {"entity_id": "120000000000000002", "daily_budget": 4000}))
    assert decision(salida) == "ask"
    assert "paciencia" in motivo(salida) and "hace 3 días" in motivo(salida)


def test_lifetime_sin_fechas_se_bloquea(instancia, correr):
    # Hallazgo 9: sin fechas no se sabe cuánto gasta al día, así que no se puede comprobar el tope.
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_update_entity",
                                          {"ad_account_id": CUENTA, "entity_id": "120000000000000003",
                                           "lifetime_budget": 50000}))
    assert decision(salida) == "deny" and "sin fechas" in motivo(salida) and "start_time" in motivo(salida)


def test_bash_presupuesto_bajo_el_tope_pregunta(instancia, correr):
    salida = correr("meta_guard", pre_bash(instancia, "python3 -I herramientas/meta_ads.py --cliente acme "
                                                      "presupuesto 120000000000000004 60 --confirmo"))
    assert decision(salida) == "ask" and "60 €/día" in motivo(salida)


def test_bash_pausar_y_activar_preguntan(instancia, correr):
    assert decision(correr("meta_guard", pre_bash(instancia, "python3 -I herramientas/meta_ads.py pausar "
                                                             "120000000000000005"))) == "ask"
    for ruta in ('"herramientas\\meta_ads.py"', "herramientas\\meta_ads.py"):  # Windows, con y sin comillas
        salida = correr("meta_guard", pre_bash(instancia, f"py -3 -I {ruta} activar 120000000000000005 --confirmo"))
        assert decision(salida) == "ask" and "EMPIEZA A GASTAR" in motivo(salida)


# ─────────────────────────────── bloquear


def test_presupuesto_por_encima_del_tope_se_bloquea(instancia, correr):
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_update_entity",
                                          {"ad_account_id": CUENTA, "entity_id": "120000000000000001",
                                           "fields": json.dumps({"daily_budget": 15000})}))
    assert decision(salida) == "deny"
    assert "150 €/día" in motivo(salida) and "100 €/día" in motivo(salida)


def test_moneda_sin_decimales(instancia, correr):
    (instancia / "clientes" / "acme" / "ficha.md").write_text(ficha("acme", CUENTA, 10000, 30000, moneda="JPY"),
                                                              encoding="utf-8")
    entrada = pre_mcp(instancia, T + "ads_create_ad_set",
                      {"ad_account_id": CUENTA, "name": "BROAD_LEAD", "daily_budget": 15000})
    assert decision(correr("meta_guard", entrada)) == "deny"
    entrada["tool_input"]["daily_budget"] = 8000
    assert decision(correr("meta_guard", entrada)) == "ask"


def test_ficha_sin_topes_bloquea_presupuestos_y_activaciones(instancia, correr):
    (instancia / "clientes" / "acme" / "ficha.md").write_text(ficha("acme", CUENTA, 0, 0), encoding="utf-8")
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_create_ad_set",
                                          {"ad_account_id": CUENTA, "name": "BROAD_LEAD", "daily_budget": 1000}))
    assert decision(salida) == "deny" and "topes" in motivo(salida)
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_activate_entity",
                                          {"ad_account_id": CUENTA, "entity_id": "120000000000000001"}))
    assert decision(salida) == "deny"


def test_sin_ninguna_ficha_se_bloquea(instancia, correr):
    (instancia / "clientes" / "acme" / "ficha.md").unlink()
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_update_entity",
                                          {"entity_id": "120000000000000001", "daily_budget": 1000}))
    assert decision(salida) == "deny"


def test_cliente_deducido_por_el_id_registrado(instancia, correr):
    otra = instancia / "clientes" / "clinica-sonrisa"
    otra.mkdir()
    (otra / "ficha.md").write_text(ficha("clinica-sonrisa", "act_000000000000001", 50, 150), encoding="utf-8")
    escribir_log(instancia, "cambios.jsonl", [{"ts": _ts(20), "session": "x", "sistema": "meta", "via": "mcp",
                                               "accion": "ads_create_ad_set", "entidad_id": "120000000000000088",
                                               "cliente": "clinica-sonrisa", "detalle": ""}])
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_update_entity",
                                          {"entity_id": "120000000000000088", "daily_budget": 6000}))
    assert decision(salida) == "deny" and "clinica-sonrisa" in motivo(salida)


def test_lifetime_con_fechas_se_compara_por_dia(instancia, correr):
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_create_ad_set",
                                          {"ad_account_id": CUENTA, "name": "BROAD_LEAD", "lifetime_budget": 140000,
                                           "start_time": "2026-11-10T00:00:00+0100",
                                           "end_time": "2026-11-17T00:00:00+0100"}))
    assert decision(salida) == "deny" and "7 días" in motivo(salida)


def test_borrados_bloqueados(instancia, correr):
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_delete_custom_audience", {"audience_id": "1234567"}))
    assert decision(salida) == "deny"


def test_crear_ya_activo_se_bloquea(instancia, correr):
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_create_ad",
                                          {"ad_account_id": CUENTA, "name": "x", "status": "ACTIVE"}))
    assert decision(salida) == "deny" and "PAUSA" in motivo(salida)


def test_solo_operador_meta_escribe(instancia, correr):
    entrada = pre_mcp(instancia, T + "ads_update_entity", {"ad_account_id": CUENTA, "entity_id": "120000000000000001",
                                                           "status": "PAUSED"},
                      agent_id="agente-123", agent_type="analista-meta")
    assert decision(correr("meta_guard", entrada)) == "deny"
    entrada["agent_type"] = "operador-meta"
    assert decision(correr("meta_guard", entrada)) == "ask"


def test_bash_presupuesto_por_encima_del_tope(instancia, correr):
    orden = "ls && python3 -I herramientas/meta_ads.py --cliente acme presupuesto 120000000000000004 150 --confirmo"
    assert decision(correr("meta_guard", pre_bash(instancia, orden))) == "deny"
    envuelta = "bash -c 'python3 -I herramientas/meta_ads.py presupuesto 120000000000000004 150 --confirmo'"
    assert decision(correr("meta_guard", pre_bash(instancia, envuelta))) == "deny"


def test_bash_plan_que_suma_mas_que_el_tope(instancia, correr):
    planes = instancia / "clientes" / "acme" / "planes"
    planes.mkdir(exist_ok=True)
    plan = {"cliente": "acme", "campana": {"nombre": "ES_LEADS_ADQ_HV"},
            "conjuntos": [{"nombre": "BROAD_LEAD", "presupuesto_diario_eur": 60, "anuncios": []},
                          {"nombre": "LAL-1_LEAD", "presupuesto_diario_eur": 60, "anuncios": []}]}
    (planes / "lanzamiento.json").write_text(json.dumps(plan), encoding="utf-8")
    salida = correr("meta_guard", pre_bash(instancia, "python3 -I herramientas/meta_ads.py crear "
                                                      "clientes/acme/planes/lanzamiento.json"))
    assert decision(salida) == "deny" and "120 €/día" in motivo(salida)


def test_bash_escritura_directa_en_graph(instancia, correr):
    orden = ("curl -X POST https://graph.facebook.com/v26.0/act_000000000000000/campaigns "
             "-F name=ES_LEADS_ADQ_HV")
    assert decision(correr("meta_guard", pre_bash(instancia, orden))) == "deny"


def test_bash_de_subagente_de_lectura(instancia, correr):
    entrada = pre_bash(instancia, "python3 -I herramientas/meta_ads.py pausar 120000000000000005",
                       agent_id="agente-9", agent_type="auditor-cuenta")
    assert decision(correr("meta_guard", entrada)) == "deny"


# ─────────────────────────────── tope total con token (HTTP simulado)


def _graph_falsa(monkeypatch, activos_eur: dict, campana_cbo: float = 0):
    import _lib

    def falsa(url, token, timeout=6.0):
        assert "access_token" not in url
        if "fields=currency" in url:
            return {"currency": "EUR"}
        data = [{"id": i, "status": "ACTIVE", "daily_budget": str(int(v * 100)),
                 "campaign": {"id": "900", "status": "ACTIVE", "daily_budget": str(int(campana_cbo * 100))}}
                for i, v in activos_eur.items()]
        return {"data": data}

    monkeypatch.setattr(_lib, "http_get_json", falsa)
    monkeypatch.setenv("META_TOKEN", "token-de-prueba-no-real")


def test_tope_total_bloquea_si_se_supera(instancia, en_proceso, monkeypatch):
    _graph_falsa(monkeypatch, {"111111": 80, "222222": 90, "333333": 80})  # 250 € activos; tope total 300
    _, salida = en_proceso("meta_guard", pre_mcp(instancia, T + "ads_update_entity",
                                                 {"ad_account_id": CUENTA, "entity_id": "333333",
                                                  "daily_budget": 9900}))  # 80 → 99: 269 €, pasa
    assert decision(salida) == "ask" and "250 € → 269 €" in motivo(salida)
    _graph_falsa(monkeypatch, {"111111": 80, "222222": 90, "333333": 80, "444444": 60})  # 310 €: ya por encima
    _, salida = en_proceso("meta_guard", pre_mcp(instancia, T + "ads_update_entity",
                                                 {"ad_account_id": CUENTA, "entity_id": "333333",
                                                  "daily_budget": 9900}))
    assert decision(salida) == "deny" and "300 €" in motivo(salida)


def test_tope_total_sin_red_pregunta(instancia, en_proceso, monkeypatch):
    import _lib

    def caida(url, token, timeout=6.0):
        raise RuntimeError("HTTP 500")

    monkeypatch.setattr(_lib, "http_get_json", caida)
    monkeypatch.setenv("META_TOKEN", "token-de-prueba-no-real")
    _, salida = en_proceso("meta_guard", pre_mcp(instancia, T + "ads_activate_entity",
                                                 {"ad_account_id": CUENTA, "entity_id": "333333"}))
    assert decision(salida) == "ask" and "No he podido comprobar el tope diario total" in motivo(salida)
    assert "token-de-prueba" not in json.dumps(salida)


# ─────────────────────────────── PostToolUse


def test_escritura_ejecutada_va_a_cambios(instancia, correr):
    entrada = post_mcp(instancia, T + "ads_create_ad_set", {"ad_account_id": CUENTA, "name": "BROAD_LEAD",
                                                            "daily_budget": 3000},
                       respuesta_mcp({"id": "120000000000000123", "status": "PAUSED"}))
    assert correr("meta_guard", entrada) is None
    fila = leer_log(instancia, "cambios.jsonl")[-1]
    assert fila["sistema"] == "meta" and fila["via"] == "mcp" and fila["cliente"] == "acme"
    assert fila["entidad_id"] == "120000000000000123" and fila["session"] == SESION
    assert set(fila) == {"ts", "session", "sistema", "via", "accion", "entidad_id", "cliente", "detalle"}


def test_escritura_fallida_no_va_a_cambios(instancia, correr):
    entrada = post_mcp(instancia, T + "ads_update_entity", {"entity_id": "120000000000000123", "status": "PAUSED"},
                       {"isError": True, "content": [{"type": "text", "text": "Error: permission denied"}]})
    correr("meta_guard", entrada)
    assert leer_log(instancia, "cambios.jsonl") == []


def test_registro_sin_datos_personales(instancia, correr):
    correr("meta_guard", pre_mcp(instancia, T + "ads_update_custom_audience_users",
                                 {"audience_id": "1234567", "users": ["ana.garcia@gmail.com", "+34 612 345 678"]}))
    texto = (instancia / "logs" / "meta-mcp.jsonl").read_text(encoding="utf-8")
    assert "ana.garcia" not in texto and "612 345 678" not in texto


# ─────────────────────────────── fallo interno


def test_fallo_interno_falla_cerrado_y_lo_registra(instancia, en_proceso, monkeypatch):
    # Hallazgo 4: un fallo dentro de una escritura en Meta no puede dejarla sin decisión.
    import meta_guard

    def rota(e):
        raise ValueError("fallo simulado")

    monkeypatch.setattr(meta_guard, "pre_mcp", rota)
    monkeypatch.setattr(meta_guard, "pre_bash", rota)
    codigo, salida = en_proceso("meta_guard", pre_mcp(instancia, T + "ads_activate_entity", {"entity_id": "1"}))
    assert codigo == 0 and decision(salida) == "deny" and "No he podido comprobar los topes" in motivo(salida)
    errores = [f for f in leer_log(instancia, "hooks.jsonl") if f["decision"] == "error"]
    assert errores[-1]["hook"] == "meta_guard" and "fallo simulado" in errores[-1]["error"]
    _, salida = en_proceso("meta_guard", pre_mcp(instancia, T + "ads_update_entity", {"entity_id": "1"},
                                                 principal=True))
    assert decision(salida) == "deny" and "No he podido comprobar los topes" in motivo(salida)
    _, salida = en_proceso("meta_guard", pre_bash(instancia, f"{MA} pausar 120000000000000005", principal=True))
    assert decision(salida) == "deny"
    _, salida = en_proceso("meta_guard", pre_mcp(instancia, T + "ads_get_ad_entities", {"ad_account_id": CUENTA}))
    assert salida is None  # las lecturas no se bloquean por un fallo
    _, salida = en_proceso("meta_guard", pre_mcp(instancia, T + "ads_delete_entity", {"entity_id": "1"}))
    assert decision(salida) == "deny"


def test_entrada_ilegible_deja_pasar(instancia, correr):
    assert correr("meta_guard", None, crudo=b"{esto no es json") is None


def test_python_antiguo_cede_al_siguiente_interprete(instancia, en_proceso, monkeypatch):
    import _lib
    monkeypatch.setattr(_lib, "VERSION_MINIMA", (99, 0))
    codigo, salida = en_proceso("meta_guard", pre_mcp(instancia, T + "ads_activate_entity", {"entity_id": "1"}))
    assert codigo == 3 and salida is None


# ─────────────────────────────── planes: presupuesto nuevo (CBO, conjuntos existentes, `api`)

MA = "python3 -I herramientas/meta_ads.py"


def _plan(instancia, plan: dict, nombre: str = "plan.json") -> str:
    planes = instancia / "clientes" / "acme" / "planes"
    planes.mkdir(exist_ok=True)
    (planes / nombre).write_text(json.dumps(plan), encoding="utf-8")
    return f"clientes/acme/planes/{nombre}"


def test_plan_cbo_cuenta_solo_la_campana(instancia, correr):
    ruta = _plan(instancia, {"cliente": "acme", "campana": {"nombre": "ES_LEADS_ADQ_HV", "presupuesto_diario": 80},
                             "conjuntos": [{"nombre": "BROAD_LEAD", "presupuesto_diario": 60},
                                           {"nombre": "LAL-1_LEAD", "presupuesto_diario": 60}]})
    salida = correr("meta_guard", pre_bash(instancia, f"{MA} crear {ruta}"))
    assert decision(salida) == "ask" and "80 €/día de presupuesto nuevo" in motivo(salida)


def test_plan_con_conjuntos_existentes_no_los_suma(instancia, correr):
    ruta = _plan(instancia, {"cliente": "acme", "campana": {"id": "120000000000000100"},
                             "conjuntos": [{"id": "120000000000000101", "presupuesto_diario": 90},
                                           {"nombre": "NUEVO_LEAD", "presupuesto_diario": 40}]})
    salida = correr("meta_guard", pre_bash(instancia, f"{MA} crear {ruta}"))
    assert decision(salida) == "ask"
    assert "1 conjunto(s) nuevo(s) y 1 existente(s)" in motivo(salida) and "40 €/día" in motivo(salida)


def test_plan_con_presupuesto_en_api_cuenta_en_centimos(instancia, correr):
    ruta = _plan(instancia, {"cliente": "acme", "campana": {"nombre": "ES_LEADS_ADQ_HV"},
                             "conjuntos": [{"nombre": "BROAD_LEAD", "api": {"daily_budget": 15000}}]})
    salida = correr("meta_guard", pre_bash(instancia, f"{MA} crear {ruta}"))
    assert decision(salida) == "deny" and "150 €/día" in motivo(salida)  # tope por cambio de acme: 100


def test_plan_que_crea_activo_se_bloquea(instancia, correr):
    ruta = _plan(instancia, {"cliente": "acme", "campana": {"nombre": "ES_LEADS_ADQ_HV", "api": {"status": "ACTIVE"}},
                             "conjuntos": [{"nombre": "BROAD_LEAD", "presupuesto_diario": 20}]})
    salida = correr("meta_guard", pre_bash(instancia, f"{MA} crear {ruta}"))
    assert decision(salida) == "deny" and "PAUSA" in motivo(salida)


def test_activar_plan_suma_solo_el_presupuesto_nuevo(instancia, en_proceso, monkeypatch):
    _graph_falsa(monkeypatch, {"111111": 200})  # 200 € activos; tope total 300
    ruta = _plan(instancia, {"cliente": "acme", "campana": {"nombre": "ES_LEADS_ADQ_HV", "presupuesto_diario": 50},
                             "conjuntos": [{"nombre": "BROAD_LEAD", "presupuesto_diario": 80}]})
    _, salida = en_proceso("meta_guard", pre_bash(instancia, f"{MA} activar --plan {ruta} --confirmo"))
    assert decision(salida) == "ask" and "200 € → 250 €" in motivo(salida)


# ─────────────────────────────── reglas automáticas, formularios instantáneos y audiencias (Bash)

RM = "python3 -I herramientas/reglas_meta.py"
FM = "python3 -I herramientas/formularios_meta.py"
AM = "python3 -I herramientas/audiencias_meta.py"


def _regla(nombre: str, accion: str, tipo: str = "SCHEDULE") -> dict:
    return {"api": {"name": nombre, "status": "ENABLED", "evaluation_spec": {"evaluation_type": tipo, "filters": []},
                    "execution_spec": {"execution_type": accion}}}


def test_reglas_crear_pregunta_y_dice_que_hacen(instancia, correr):
    ruta = _plan(instancia, {"cliente": "acme", "reglas": [_regla("OS_KILL_3X", "PAUSE"),
                                                           _regla("OS_AVISO_CPA", "NOTIFICATION")]}, "reglas.json")
    salida = correr("meta_guard", pre_bash(instancia, f"{RM} crear {ruta} --cliente acme --confirmo"))
    assert decision(salida) == "ask"
    assert "2 reglas" in motivo(salida) and "1 pausan, 1 avisan" in motivo(salida) and "24/7" in motivo(salida)


def test_reglas_fuera_de_avisar_o_pausar_se_bloquean(instancia, correr):
    for regla in (_regla("SUBE", "CHANGE_BUDGET"), _regla("ENCIENDE", "UNPAUSE"),
                  _regla("AL_MOMENTO", "PAUSE", "TRIGGER")):
        ruta = _plan(instancia, {"cliente": "acme", "reglas": [_regla("OS_KILL_3X", "PAUSE"), regla]}, "reglas.json")
        salida = correr("meta_guard", pre_bash(instancia, f"{RM} crear {ruta} --confirmo"))
        assert decision(salida) == "deny" and regla["api"]["name"] in motivo(salida)


def test_reglas_propuesta_ilegible_pregunta(instancia, correr):
    salida = correr("meta_guard", pre_bash(instancia, f"{RM} crear clientes/acme/planes/no-existe.json --confirmo"))
    assert decision(salida) == "ask" and "no he podido leer" in motivo(salida)


def test_reglas_pausar_y_reactivar_preguntan(instancia, correr):
    for sub, texto in (("pausar", "Desactivar"), ("reactivar", "Reactivar")):
        salida = correr("meta_guard", pre_bash(instancia, f"{RM} {sub} 120000000000000200 --cliente acme --confirmo"))
        assert decision(salida) == "ask" and texto in motivo(salida) and "120000000000000200" in motivo(salida)


def test_reglas_lectura_y_simulacion_no_deciden(instancia, correr):
    for orden in (f"{RM} listar --cliente acme", f"{RM} proponer --cliente acme --cpa 40",
                  f"{RM} historial --cliente acme --dias 7", f"{RM} destinatarios --cliente acme",
                  f"{RM} crear clientes/acme/planes/reglas.json --simular --pasos"):
        assert correr("meta_guard", pre_bash(instancia, orden)) is None, orden


def test_formulario_crear_pregunta_y_leads_avisan_de_datos_personales(instancia, correr):
    salida = correr("meta_guard", pre_bash(instancia, f"{FM} crear clientes/acme/planes/formulario.json --cliente acme "
                                                      "--confirmo"))
    assert decision(salida) == "ask" and "FORMULARIO INSTANTÁNEO" in motivo(salida)
    salida = correr("meta_guard", pre_bash(instancia, f"{FM} leads 120000000000000300 --cliente acme "
                                                      "--desde 2026-11-01"))
    assert decision(salida) == "ask" and "RGPD" in motivo(salida) and "privado/" in motivo(salida)
    salida = correr("meta_guard", pre_bash(instancia, f"{FM} leads 120000000000000300 --sin-archivos"))
    assert decision(salida) == "ask" and "privado/" not in motivo(salida)


def test_formulario_lectura_y_simulacion_no_deciden(instancia, correr):
    for orden in (f"{FM} listar --cliente acme", f"{FM} ver 120000000000000300",
                  f"{FM} guia clientes/acme/planes/formulario.json",
                  f"{FM} crear clientes/acme/planes/formulario.json --simular"):
        assert correr("meta_guard", pre_bash(instancia, orden)) is None, orden


def test_audiencias_crear_y_sincronizar_preguntan(instancia, correr):
    salida = correr("meta_guard", pre_bash(instancia, f"{AM} crear ACME_CRM_CUALIFICADOS --cliente acme --confirmo"))
    assert decision(salida) == "ask" and "ACME_CRM_CUALIFICADOS" in motivo(salida)
    salida = correr("meta_guard", pre_bash(instancia, f"{AM} sincronizar 120000000000000400 --archivo "
                                                      "clientes/acme/privado/audiencias/cualificados.csv "
                                                      "--reemplazar --confirmo"))
    assert decision(salida) == "ask" and "SUSTITUYE" in motivo(salida) and "RGPD" in motivo(salida)
    assert "Ojo" not in motivo(salida)
    salida = correr("meta_guard", pre_bash(instancia, f"{AM} sincronizar 120000000000000400 --archivo "
                                                      "datos/lista.csv --confirmo"))
    assert decision(salida) == "ask" and "AÑADE" in motivo(salida) and "Ojo" in motivo(salida)


def test_audiencias_lectura_y_simulacion_no_deciden(instancia, correr):
    for orden in (f"{AM} listar --cliente acme --buscar CRM",
                  f"{AM} etapas --archivo clientes/acme/privado/ghl.csv",
                  f"{AM} crear ACME_CRM --simular",
                  f"{AM} sincronizar 120000000000000400 --archivo clientes/acme/privado/a.csv --simular"):
        assert correr("meta_guard", pre_bash(instancia, orden)) is None, orden


def test_otras_escrituras_en_meta_solo_las_hace_operador_meta(instancia, correr):
    for orden in (f"{RM} crear clientes/acme/planes/reglas.json --confirmo",
                  f"{RM} reactivar 120000000000000200 --confirmo",
                  f"{FM} crear clientes/acme/planes/formulario.json --confirmo",
                  f"{AM} crear ACME_CRM --confirmo",
                  f"{AM} sincronizar 120000000000000400 --archivo clientes/acme/privado/a.csv --confirmo"):
        entrada = pre_bash(instancia, orden, agent_id="agente-7", agent_type="estratega-creativo")
        assert decision(correr("meta_guard", entrada)) == "deny", orden
        entrada["agent_type"] = "operador-meta"
        assert decision(correr("meta_guard", entrada)) == "ask", orden


def test_leads_desde_un_subagente_preguntan(instancia, correr):
    entrada = pre_bash(instancia, f"{FM} leads 120000000000000300", agent_id="agente-8",
                       agent_type="especialista-funnel")
    assert decision(correr("meta_guard", entrada)) == "ask"


# ─────────────────────────────── revisión de seguridad (I5): entradas exactas del informe
# La cuenta del informe (act_123456789012) se cambia por la de la ficha de prueba (CUENTA); los topes de acme aquí son
# 100/300 en vez de 50/200, y los importes del informe los superan igual.

ANALISTA = {"agent_id": "agente-an", "agent_type": "analista-meta"}


def test_h3_comodines_variables_y_runpy_no_esquivan_el_hook(instancia, correr):
    ordenes = ["python3 -I herramientas/meta_ad?.py pausar 120000000000001 --cliente acme",
               "S=meta_ads; python3 -I herramientas/$S.py pausar 120000000000001 --cliente acme",
               "python3 -I -c \"import runpy,sys; sys.argv=['meta_ads.py','pausar','120000000000001','--cliente',"
               "'acme']; runpy.run_path(\\\"herramientas/meta_ads.py\\\", run_name=\\\"__main__\\\")\"",
               "python3 -I -m herramientas.meta_ads pausar 120000000000001",
               "python3 -c \"eval(compile(open('herr'+'amientas/meta_ads.py').read(), 'm', 'single'))\"",
               "uv run python herramientas/meta_ad*.py activar 120000000000001 --confirmo",
               "python3 -I herramientas/../herramientas/meta_ads.py pausar 120000000000001"]
    for orden in ordenes:
        salida = correr("meta_guard", pre_bash(instancia, orden, **ANALISTA))
        assert decision(salida) == "deny" and "ruta literal" in motivo(salida), orden
        salida = correr("meta_guard", pre_bash(instancia, orden, principal=True))
        assert decision(salida) == "ask" and "No puedo saber qué ejecuta" in motivo(salida), orden


def test_h3_comodin_que_da_un_unico_script_se_trata_como_ese_script(instancia, correr):
    (instancia / "herramientas").mkdir(exist_ok=True)
    (instancia / "herramientas" / "meta_ads.py").write_text("# falso\n", encoding="utf-8")
    orden = "python3 -I herramientas/meta_ad?.py pausar 120000000000001 --cliente acme"
    salida = correr("meta_guard", pre_bash(instancia, orden, **ANALISTA))
    assert decision(salida) == "deny" and "Solo `operador-meta`" in motivo(salida)
    salida = correr("meta_guard", pre_bash(instancia, orden))
    assert decision(salida) == "ask" and "120000000000001" in motivo(salida)
    salida = correr("meta_guard", pre_bash(instancia, "python3 -I herramientas/meta_ad?.py --cliente acme vigente"))
    assert salida is None


def test_h3_sin_falsos_positivos(instancia, correr):
    for orden in ("ls clientes/*/", "grep -rn presupuesto clientes/*/planes/", "ls herramientas/*.py",
                  "python3 -I herramientas/meta_ads.py --cliente acme vigente",
                  "python3 -I scripts/validar.py", "python3 -c 'print(1+1)'", "cat clientes/acme/ficha.md"):
        assert correr("meta_guard", pre_bash(instancia, orden, principal=True)) is None, orden


def test_h14_puntos_en_la_ruta_preguntan(instancia, correr):
    salida = correr("meta_guard", pre_bash(instancia, "python3 -I herramientas/../scripts/otro.py", principal=True))
    assert decision(salida) == "ask" and "`..`" in motivo(salida)


def test_h4_fechas_en_milisegundos_no_tumban_el_tope(instancia, correr):
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_create_ad_set",
                                          {"ad_account_id": CUENTA, "status": "PAUSED", "lifetime_budget": 9000000,
                                           "start_time": 1763164800000, "end_time": 1763251200000}))
    assert decision(salida) == "deny" and "supera el tope" in motivo(salida)
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_create_ad_set",
                                          {"ad_account_id": CUENTA, "status": "PAUSED", "daily_budget": 900000,
                                           "programacion": {"lifetime_budget": 1000, "start_time": 1e20,
                                                            "end_time": 2e20}}))
    assert decision(salida) == "deny" and "9.000 €/día" in motivo(salida)


def test_h5_promocionar_publicacion_se_bloquea(instancia, correr):
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_boost_ig_post",
                                          {"ad_account_id": CUENTA, "total_budget": 900000}))
    assert decision(salida) == "deny" and "Ads Manager" in motivo(salida)


def test_h6_borrar_o_archivar_por_estado(instancia, correr):
    base = {"entity_id": "120000000000001", "ad_account_id": CUENTA}
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_update_entity", {**base, "status": "DELETED"}))
    assert decision(salida) == "deny"
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_update_entity",
                                          {**base, "fields": {"configured_status": "deleted"}}))
    assert decision(salida) == "deny"
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_update_entity", {**base, "status": "ARCHIVED"}))
    assert decision(salida) == "ask" and "ARCHIVAR" in motivo(salida) and "deshacer" in motivo(salida)


def test_h7_lo_que_va_detras_de_dos_guiones_no_simula(instancia, correr):
    for orden in ("python3 -I herramientas/reglas_meta.py crear --cliente acme --confirmo -- --simular",
                  "python3 -I herramientas/meta_ads.py crear --cliente acme -- --simular"):
        assert decision(correr("meta_guard", pre_bash(instancia, orden, **ANALISTA))) == "deny", orden


@pytest.mark.parametrize("campos", [
    {"daily_min_spend_target": 900000},
    {"daily_budget": {"amount": 900000, "currency": "EUR"}},
    {"budget_amount": 900000},
    {"lifetime_budget": 900000},
    {"daily_budget": "nueve mil"},
])
def test_h9_presupuestos_que_no_se_pueden_leer_se_bloquean(instancia, correr, campos):
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_update_entity",
                                          {"entity_id": "120000000000001", "ad_account_id": CUENTA, **campos}))
    assert decision(salida) == "deny"
    assert "daily_budget" in motivo(salida) or "start_time" in motivo(salida)


def test_h9_bid_amount_no_es_presupuesto(instancia, correr):
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_update_entity",
                                          {"entity_id": "120000000000001", "ad_account_id": CUENTA,
                                           "bid_amount": 250}))
    assert decision(salida) == "ask"


def test_h11_la_sesion_principal_delega_en_operador_meta(instancia, correr):
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_create_campaign",
                                          {"ad_account_id": CUENTA, "name": "ES_LEADS_ADQ_HV",
                                           "objective": "OUTCOME_LEADS"}, principal=True))
    assert decision(salida) == "deny" and "delega en operador-meta" in motivo(salida)
    salida = correr("meta_guard", pre_bash(instancia, f"{MA} pausar 120000000000000005", principal=True))
    assert decision(salida) == "deny" and "operador-meta" in motivo(salida)
    salida = correr("meta_guard", pre_mcp(instancia, T + "ads_get_ad_entities", {"ad_account_id": CUENTA},
                                          principal=True))
    assert salida is None


def test_h12_importe_con_exponente_se_lee_como_meta_ads(instancia, correr):
    ruta = _plan(instancia, {"cliente": "acme", "campana": {"nombre": "ES_LEADS_ADQ_HV", "presupuesto_diario": "9e3"},
                             "conjuntos": [{"nombre": "BROAD_LEAD", "anuncios": []}]}, "p_exp.json")
    salida = correr("meta_guard", pre_bash(instancia, f"{MA} crear {ruta}"))
    assert decision(salida) == "deny" and "9.000 €/día" in motivo(salida)  # antes: «0 €/día»
