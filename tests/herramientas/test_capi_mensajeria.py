"""capi.py en mensajería (Click to WhatsApp, Messenger, Instagram Direct): etapas del §16, construcción, validación,
lectura de webhooks y envío con HTTP simulado. También comprueba las plantillas de `plantillas/integraciones/mensajeria/`
(estructura, sin secretos y la misma lógica que la herramienta, ejecutando su JavaScript con Node si está instalado)."""
from __future__ import annotations

import copy
import importlib
import json
import pathlib
import re
import shutil
import subprocess
import time
import urllib.request

import pytest

from http_simulado import HttpSimulado

RAIZ = pathlib.Path(__file__).resolve().parents[2]
PLANTILLAS = RAIZ / "plantillas" / "integraciones" / "mensajeria"
EJEMPLOS = PLANTILLAS / "ejemplos"
TEL_HASH = "e323ec626319ca94ee8bff2e4c87cf613be6ea19919ed1364124e16807ab3176"  # 16505551212 (vector de Meta)
WABA, PAGINA, IG = "100000000000001", "100000000000002", "170000000000003"
CLID = "ARAkEjemploClicDeAnuncio0000000000000001"
PSID, IGSID = "2000000000000001", "3000000000000001"


@pytest.fixture
def capi(instancia):
    import capi as modulo
    return importlib.reload(modulo)


def _ejemplo(nombre: str, reciente: bool = True) -> dict:
    """Webhook de ejemplo; con `reciente`, la hora del mensaje pasa a ser hace 10 minutos."""
    datos = json.loads((EJEMPLOS / nombre).read_text(encoding="utf-8"))
    if reciente:
        ahora = int(time.time()) - 600
        for entrada in datos.get("entry", []):
            for cambio in entrada.get("changes", []):
                for m in cambio["value"].get("messages", []):
                    m["timestamp"] = str(ahora)
            for m in entrada.get("messaging", []):
                m["timestamp"] = ahora * 1000
    return datos


def _guardar(ruta: pathlib.Path, datos) -> str:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    return str(ruta)


def _ev(canal="whatsapp", evento="QualifiedLead", **ud) -> dict:
    base = {"whatsapp": {"whatsapp_business_account_id": WABA, "ctwa_clid": CLID},
            "messenger": {"page_id": PAGINA, "page_scoped_user_id": PSID},
            "instagram": {"instagram_business_account_id": IG, "ig_sid": IGSID}}[canal]
    base.update(ud)
    return {"event_name": evento, "event_time": int(time.time()) - 60, "action_source": "business_messaging",
            "messaging_channel": canal, "user_data": {k: v for k, v in base.items() if v is not None}}


def _construir(capi, capsys, *args) -> dict:
    capi.main(["construir", *args])
    return json.loads(capsys.readouterr().out)["data"][0]


# ---------------------------------------------------------------- etapas del contrato §16

@pytest.mark.parametrize("etapa,cualifica_en,esperado", [
    ("lead", "cualificado", "LeadSubmitted"),
    ("cualificado", "cualificado", "QualifiedLead"),
    ("ganado", "cualificado", "Purchase"),
    ("llamada", "llamada", "QualifiedLead"),
    ("asistio", "asistio", "QualifiedLead"),
    ("propuesta", "propuesta", "QualifiedLead"),
    ("ganado", "llamada", "Purchase"),
])
def test_etapa_a_evento(capi, etapa, cualifica_en, esperado):
    assert capi.evento_de_etapa(etapa, cualifica_en) == esperado


@pytest.mark.parametrize("etapa,fragmento", [
    ("llamada", "Schedule"),
    ("diagnostico", "personalizados"),
    ("asistio", "--cualifica-en asistio"),
    ("propuesta", "CRM"),
    ("perdido", "exclusiones"),
    ("inventada", "contrato §16"),
])
def test_etapas_sin_evento_explican_que_hacer(capi, etapa, fragmento):
    with pytest.raises(capi.Invalido, match=re.escape(fragmento)):
        capi.evento_de_etapa(etapa)


def test_cualificado_no_se_duplica_si_la_llamada_es_el_filtro(capi):
    with pytest.raises(capi.Invalido, match="duplicaría"):
        capi.evento_de_etapa("cualificado", "llamada")


def test_etapas_coinciden_con_el_contrato(capi):
    contrato = (RAIZ / "docs" / "desarrollo" / "contratos.md").read_text(encoding="utf-8")
    seccion = contrato.split("## 16.", 1)[1].split("\n## ", 1)[0]
    ids = re.findall(r"^\| `([a-z]+)` \|", seccion, re.M)
    assert tuple(ids) == capi.ETAPAS


# ---------------------------------------------------------------- construir

def test_whatsapp_con_clic(capi, capsys):
    ev = _construir(capi, capsys, "--canal", "whatsapp", "--etapa", "cualificado", "--waba", WABA, "--ctwa-clid", CLID)
    assert ev["event_name"] == "QualifiedLead" and ev["action_source"] == "business_messaging"
    assert ev["messaging_channel"] == "whatsapp"
    assert ev["user_data"] == {"whatsapp_business_account_id": WABA, "ctwa_clid": CLID}  # nada hasheado
    assert isinstance(ev["event_time"], int) and "event_source_url" not in ev


def test_whatsapp_con_clic_ignora_datos_y_avisa(capi, capsys):
    ev = _construir(capi, capsys, "--canal", "whatsapp", "--etapa", "lead", "--waba", WABA, "--ctwa-clid", CLID,
                    "--telefono", "+1 650 555 1212")
    assert "ph" not in ev["user_data"]


def test_whatsapp_sin_clic_empareja_por_telefono_hasheado(capi, capsys):
    capi.main(["construir", "--canal", "whatsapp", "--etapa", "lead", "--waba", WABA, "--pagina", PAGINA,
               "--telefono", "+1 (650) 555-1212"])
    salida = capsys.readouterr()
    ud = json.loads(salida.out)["data"][0]["user_data"]
    assert ud == {"page_id": PAGINA, "whatsapp_business_account_id": WABA, "ph": [TEL_HASH]}
    assert "sin ctwa_clid" in salida.err and "650" not in salida.out


def test_whatsapp_sin_clic_ni_pagina_no_construye(capi):
    with pytest.raises(SystemExit) as e:
        capi.main(["construir", "--canal", "whatsapp", "--etapa", "lead", "--waba", WABA, "--telefono", "+16505551212"])
    assert e.value.code == 1


def test_messenger_e_instagram(capi, capsys):
    ev = _construir(capi, capsys, "--canal", "messenger", "--etapa", "lead", "--pagina", PAGINA, "--psid", PSID)
    assert ev["user_data"] == {"page_id": PAGINA, "page_scoped_user_id": PSID}
    ev = _construir(capi, capsys, "--canal", "instagram", "--etapa", "cualificado", "--ig-cuenta", IG, "--igsid", IGSID)
    assert ev["user_data"] == {"instagram_business_account_id": IG, "ig_sid": IGSID}
    assert ev["messaging_channel"] == "instagram"


def test_ganado_lleva_valor_y_moneda(capi, capsys):
    with pytest.raises(SystemExit) as e:
        capi.main(["construir", "--canal", "whatsapp", "--etapa", "ganado", "--waba", WABA, "--ctwa-clid", CLID])
    assert e.value.code == 1 and "--valor" in capsys.readouterr().err
    ev = _construir(capi, capsys, "--canal", "whatsapp", "--etapa", "ganado", "--waba", WABA, "--ctwa-clid", CLID,
                    "--valor", "4800", "--moneda", "eur")
    assert ev["event_name"] == "Purchase" and ev["custom_data"] == {"value": 4800.0, "currency": "EUR"}


def test_ficha_da_cuentas_y_moneda(capi, instancia, capsys):
    ficha = instancia / "clientes" / "acme" / "ficha.md"
    texto = ficha.read_text(encoding="utf-8").replace('  pagina: ""', f'  pagina: "{PAGINA}"\n  waba: "{WABA}"')
    ficha.write_text(texto, encoding="utf-8")
    ev = _construir(capi, capsys, "--canal", "whatsapp", "--etapa", "ganado", "--cliente", "acme", "--ctwa-clid", CLID,
                    "--valor", "3000")
    assert ev["user_data"]["whatsapp_business_account_id"] == WABA and ev["custom_data"]["currency"] == "EUR"
    ev = _construir(capi, capsys, "--canal", "messenger", "--etapa", "lead", "--cliente", "acme", "--psid", PSID)
    assert ev["user_data"]["page_id"] == PAGINA


def test_ficha_con_ids_de_ejemplo_no_cuenta(capi, instancia):
    ficha = instancia / "clientes" / "acme" / "ficha.md"
    ficha.write_text(ficha.read_text(encoding="utf-8").replace('  pagina: ""', '  pagina: ""\n  waba: "000000000000000"'),
                     encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        capi.main(["construir", "--canal", "whatsapp", "--etapa", "lead", "--cliente", "acme", "--ctwa-clid", CLID])
    assert e.value.code == 1


@pytest.mark.parametrize("extra,fragmento", [
    (["--evento", "Lead"], "LeadSubmitted"),
    (["--evento", "Schedule"], "Schedule no existe"),
    (["--evento", "LeadCualificado"], "QualifiedLead"),
    (["--etapa", "lead", "--url", "https://acme-automations.example/"], "--url no va"),
    (["--etapa", "lead", "--crm", "GHL"], "--crm no va"),
    (["--etapa", "lead", "--origen", "website"], "quita --origen"),
    ([], "--etapa cualificado"),
])
def test_construir_mensajeria_errores(capi, capsys, extra, fragmento):
    with pytest.raises(SystemExit) as e:
        capi.main(["construir", "--canal", "whatsapp", "--waba", WABA, "--ctwa-clid", CLID, *extra])
    assert e.value.code == 1
    assert fragmento in capsys.readouterr().err


def test_etapa_sin_canal_es_la_del_contrato(capi, capsys):
    """Antes, --etapa sin --canal era un error. Desde I7 da el event_name del §16 para la CAPI web o de CRM; con
    --canal sigue siendo el de mensajería."""
    ev = _construir(capi, capsys, "--etapa", "cualificado", "--crm", "GHL", "--email", "john_smith@gmail.com")
    assert ev["event_name"] == "LeadCualificado" and ev["action_source"] == "system_generated"
    ev = _construir(capi, capsys, "--canal", "whatsapp", "--etapa", "cualificado", "--waba", WABA, "--ctwa-clid", CLID)
    assert ev["event_name"] == "QualifiedLead"


def test_origen_business_messaging_sin_canal_es_error(capi, capsys):
    with pytest.raises(SystemExit) as e:
        capi.main(["construir", "--evento", "LeadSubmitted", "--origen", "business_messaging", "--email", "a@b.test"])
    assert e.value.code == 1 and "--canal" in capsys.readouterr().err


def test_fuera_de_la_ventana_del_clic_avisa(capi, capsys):
    hace_diez_dias = str(int(time.time()) - 10 * 86400)
    capi.main(["construir", "--canal", "whatsapp", "--etapa", "ganado", "--waba", WABA, "--ctwa-clid", CLID,
               "--valor", "5000", "--moneda", "EUR", "--entrada-conversacion", hace_diez_dias])
    assert "no lo atribuirá al clic" in capsys.readouterr().err


def test_salida_fuera_de_privado_avisa(capi, instancia, capsys):
    fuera = instancia / "clientes" / "acme" / "planes" / "ev.json"
    capi.main(["construir", "--canal", "messenger", "--etapa", "lead", "--pagina", PAGINA, "--psid", PSID,
               "--salida", str(fuera)])
    assert "privado/" in capsys.readouterr().err and fuera.exists()


def test_construir_web_no_cambia(capi, capsys):
    """La vía de siempre sigue igual: sin --origen es website. Sin --event-id no se inventa uno (I7): no coincidiría
    con el del píxel y taparía el aviso de deduplicación."""
    ev = _construir(capi, capsys, "--evento", "Lead", "--url", "https://acme-automations.example/gracias",
                    "--email", "john_smith@gmail.com", "--ua", "Mozilla/5.0", "--event-id", "lead_9")
    assert ev["action_source"] == "website" and ev["event_id"] == "lead_9"


# ---------------------------------------------------------------- validar

def test_eventos_correctos_por_canal(capi):
    for canal in ("whatsapp", "messenger", "instagram"):
        assert capi.validar({"data": [_ev(canal)]}) == ([], []), canal


@pytest.mark.parametrize("ev,fragmento", [
    (_ev(evento="Lead"), "LeadSubmitted"),
    (_ev(evento="Schedule"), "Schedule no existe"),
    (_ev(evento="LeadCualificado"), "no admite"),
    (_ev(whatsapp_business_account_id=None), "falta user_data.whatsapp_business_account_id"),
    (_ev(ctwa_clid=None), "necesita page_id"),
    (_ev(ctwa_clid=None, page_id=PAGINA, external_id=["a" * 64]), "external_id no cuenta"),
    (_ev("messenger", page_scoped_user_id=None), "PSID"),
    (_ev("instagram", ig_sid=None), "IGSID"),
    (_ev("messenger", page_id="mi-pagina"), "ID numérico"),
    (_ev(ctwa_clid="f" * 64), "hasheado"),
    (_ev(whatsapp_business_account_id="a" * 64), "hasheado"),
    (dict(_ev(), messaging_channel="telegram"), "messaging_channel «telegram»"),
    (dict(_ev(), action_source="website", event_source_url="https://x.example", user_data={
        "client_user_agent": "UA", "em": ["a" * 64]}), "solo va con action_source=business_messaging"),
    (dict(_ev(evento="Purchase")), "Purchase necesita"),
    (dict(_ev(), custom_data={"event_source": "crm", "lead_event_source": "GHL"}), "event_source=crm"),
])
def test_errores_de_mensajeria(capi, ev, fragmento):
    errores, _ = capi.validar({"data": [ev]})
    assert any(fragmento in e for e in errores), errores


def test_whatsapp_sin_clic_es_valido_con_aviso(capi):
    errores, avisos = capi.validar({"data": [_ev(ctwa_clid=None, page_id=PAGINA, ph=[TEL_HASH])]})
    assert errores == [] and any("menos precisa" in a for a in avisos)


def test_instagram_con_el_nombre_de_la_lista_general(capi):
    ev = _ev("instagram", instagram_business_account_id=None, ig_account_id=IG)
    errores, avisos = capi.validar({"data": [ev]})
    assert errores == [] and any("instagram_business_account_id" in a for a in avisos)


def test_hito_repetido_en_el_lote_avisa(capi):
    errores, avisos = capi.validar({"data": [_ev(), _ev(), _ev(evento="LeadSubmitted")]})
    assert errores == [] and sum("una sola vez" in a for a in avisos) == 1


def test_lote_mezclado_avisa_y_ctwa_clid_en_web_avisa(capi):
    web = {"event_name": "Lead", "event_time": int(time.time()) - 60, "action_source": "website",
           "event_id": "lead_1", "event_source_url": "https://acme-automations.example/gracias",
           "user_data": {"em": ["a" * 64], "client_user_agent": "UA", "ctwa_clid": CLID}}
    _, avisos = capi.validar({"data": [web, _ev()]})
    assert any("lotes separados" in a for a in avisos) and any("solo sirve con" in a for a in avisos)


def test_ctwa_clid_raro_avisa(capi):
    _, avisos = capi.validar({"data": [_ev(ctwa_clid="abc def")]})
    assert any("cópialo entero" in a for a in avisos)


# ---------------------------------------------------------------- webhooks (origen del clic)

def test_parsear_whatsapp_ctwa(capi):
    m, = capi.parsear_webhook(_ejemplo("whatsapp-ctwa.json", reciente=False))
    assert (m["canal"], m["cuenta"], m["anuncio"], m["ctwa_clid"]) == ("whatsapp", WABA, "120000000000000123", CLID)
    assert m["telefono"] == "16505551212" and m["momento"] == 1762851600 and m["avisos"] == []
    assert m["mensaje_id"] == "wamid.EJEMPLO000000000000000001"  # para no procesar dos veces un aviso reintentado


def test_parsear_estado_sin_clic(capi):
    m, = capi.parsear_webhook(_ejemplo("whatsapp-estado.json"))
    assert m["anuncio"] and m["ctwa_clid"] is None and any("Estados" in x for x in m["avisos"])


def test_parsear_usuario_con_nombre_de_usuario(capi):
    datos = _ejemplo("whatsapp-ctwa.json")
    valor = datos["entry"][0]["changes"][0]["value"]
    del valor["messages"][0]["from"]
    valor["messages"][0]["from_user_id"] = "XX.000000000000000001"
    valor["contacts"] = [{"profile": {"name": "Contacto"}, "user_id": "XX.000000000000000001"}]
    m, = capi.parsear_webhook(datos)
    assert m["tipo_identidad"] == "bsuid" and m["telefono"] is None and any("nombre de usuario" in x for x in m["avisos"])


def test_parsear_messenger_ignora_ecos_y_pasa_a_segundos(capi):
    mensajes = capi.parsear_webhook(_ejemplo("messenger-ctm.json", reciente=False))
    assert len(mensajes) == 1
    m = mensajes[0]
    assert (m["canal"], m["cuenta"], m["identidad"], m["anuncio"], m["ref"]) == (
        "messenger", PAGINA, PSID, "120000000000000124", "diag-nov")
    assert m["momento"] == 1762851600 and m["mensaje_id"] == "m_EJEMPLO000000000000000001"


def test_parsear_instagram(capi):
    m, = capi.parsear_webhook(_ejemplo("instagram-ctd.json"))
    assert (m["canal"], m["cuenta"], m["identidad"], m["tipo_identidad"]) == ("instagram", IG, IGSID, "igsid")


def test_parsear_organico_y_estados_de_entrega(capi):
    datos = _ejemplo("whatsapp-ctwa.json")
    del datos["entry"][0]["changes"][0]["value"]["messages"][0]["referral"]
    m, = capi.parsear_webhook(datos)
    assert m["anuncio"] is None and any("sin referral" in x for x in m["avisos"])
    entrega = {"object": "whatsapp_business_account", "entry": [{"id": WABA, "changes": [{"field": "messages",
               "value": {"statuses": [{"id": "wamid.X", "status": "delivered"}]}}]}]}
    assert capi.parsear_webhook(entrega) == []
    with pytest.raises(capi.Invalido, match="no reconozco"):
        capi.parsear_webhook({"object": "telegram"})


def test_origen_cli_tapa_y_guarda_completo_solo_en_privado(capi, instancia, capsys):
    ruta = _guardar(instancia / "clientes" / "acme" / "privado" / "webhook.json", _ejemplo("whatsapp-ctwa.json"))
    capi.main(["origen", ruta])
    salida = capsys.readouterr().out
    assert "120000000000000123" in salida and CLID not in salida and "16505551212" not in salida
    with pytest.raises(SystemExit) as e:
        capi.main(["origen", ruta, "--salida", str(instancia / "clientes" / "acme" / "datos" / "origen.json")])
    assert e.value.code == 1
    destino = instancia / "clientes" / "acme" / "privado" / "origen.json"
    capi.main(["origen", ruta, "--salida", str(destino), "--json"])
    r = json.loads(capsys.readouterr().out)
    assert r["de_anuncio"] == 1 and r["con_clic"] == 1 and CLID not in json.dumps(r)
    assert json.loads(destino.read_text(encoding="utf-8"))[0]["ctwa_clid"] == CLID


def test_origen_cli_webhook_raro(capi, tmp_path, capsys):
    with pytest.raises(SystemExit) as e:
        capi.main(["origen", _guardar(tmp_path / "x.json", {"object": "user"})])
    assert e.value.code == 1


@pytest.mark.parametrize("ejemplo,etapa,extra,canal", [
    ("whatsapp-ctwa.json", "cualificado", [], "whatsapp"),
    ("whatsapp-estado.json", "lead", ["--pagina", PAGINA], "whatsapp"),
    ("messenger-ctm.json", "lead", [], "messenger"),
    ("instagram-ctd.json", "cualificado", [], "instagram"),
])
def test_construir_desde_webhook_es_valido(capi, instancia, capsys, ejemplo, etapa, extra, canal):
    ruta = _guardar(instancia / "clientes" / "acme" / "privado" / ejemplo, _ejemplo(ejemplo))
    capi.main(["construir", "--desde-webhook", ruta, "--etapa", etapa, *extra])
    salida = capsys.readouterr()
    payload = json.loads(salida.out)
    assert payload["data"][0]["messaging_channel"] == canal
    assert capi.validar(payload)[0] == []
    assert "no lo atribuirá" not in salida.err


def test_construir_desde_webhook_estado_usa_telefono(capi, instancia, capsys):
    ruta = _guardar(instancia / "clientes" / "acme" / "privado" / "w.json", _ejemplo("whatsapp-estado.json"))
    ev = _construir(capi, capsys, "--desde-webhook", ruta, "--etapa", "lead", "--pagina", PAGINA)
    assert ev["user_data"]["ph"] == [TEL_HASH] and "ctwa_clid" not in ev["user_data"]


def test_construir_desde_webhook_canal_distinto(capi, instancia, capsys):
    ruta = _guardar(instancia / "clientes" / "acme" / "privado" / "w.json", _ejemplo("messenger-ctm.json"))
    with pytest.raises(SystemExit) as e:
        capi.main(["construir", "--desde-webhook", ruta, "--canal", "whatsapp", "--etapa", "lead"])
    assert e.value.code == 1 and "el webhook es de messenger" in capsys.readouterr().err


def test_construir_desde_webhook_antiguo_avisa(capi, instancia, capsys):
    ruta = _guardar(instancia / "clientes" / "acme" / "privado" / "w.json", _ejemplo("whatsapp-ctwa.json", False))
    capi.main(["construir", "--desde-webhook", ruta, "--etapa", "cualificado"])
    assert "no lo atribuirá al clic" in capsys.readouterr().err


# ---------------------------------------------------------------- enviar (HTTP simulado)

def _payload(instancia, *eventos) -> str:
    return _guardar(instancia / "clientes" / "acme" / "privado" / "ev-mensajeria.json", {"data": list(eventos)})


def test_enviar_mensajeria_con_test_code(capi, instancia, monkeypatch, capsys):
    http = HttpSimulado().cuando("POST", r"/v\d+\.0/123456789012345/events$",
                                 {"events_received": 1, "messages": [], "fbtrace_id": "Abc"})
    monkeypatch.setattr(urllib.request, "urlopen", http)
    monkeypatch.setenv("META_CAPI_MENSAJERIA_TOKEN_ACME", "token-mensajeria")
    monkeypatch.setenv("META_CAPI_TOKEN", "token-web")
    capi.main(["enviar", _payload(instancia, _ev()), "--cliente", "acme", "--dataset", "123456789012345",
               "--test-code", "TEST123"])
    peticion = http.peticiones[0]
    assert peticion["form"]["access_token"] == "token-mensajeria" and peticion["form"]["test_event_code"] == "TEST123"
    enviado = json.loads(peticion["form"]["data"])[0]
    assert enviado["action_source"] == "business_messaging" and enviado["user_data"]["ctwa_clid"] == CLID
    salida = capsys.readouterr().out
    assert "(whatsapp)" in salida and "token-mensajeria" not in salida
    fila = json.loads((instancia / "logs" / "cambios.jsonl").read_text(encoding="utf-8").strip())
    assert fila["accion"] == "enviar_prueba" and "mensajeria=whatsapp" in fila["detalle"]
    assert CLID not in fila["detalle"] and "token" not in fila["detalle"]


def test_enviar_mensajeria_sin_token_propio_prueba_el_general(capi, instancia, monkeypatch, capsys):
    http = HttpSimulado().cuando("POST", r"/events$", {"events_received": 1})
    monkeypatch.setattr(urllib.request, "urlopen", http)
    monkeypatch.delenv("META_CAPI_MENSAJERIA_TOKEN", raising=False)
    monkeypatch.delenv("META_CAPI_MENSAJERIA_TOKEN_ACME", raising=False)
    monkeypatch.setenv("META_CAPI_TOKEN", "token-web")
    capi.main(["enviar", _payload(instancia, _ev("messenger")), "--cliente", "acme", "--dataset", "123456789012345",
               "--test-code", "TEST1"])
    assert http.peticiones[0]["form"]["access_token"] == "token-web"
    assert "Sin META_CAPI_MENSAJERIA_TOKEN" in capsys.readouterr().err


def test_enviar_mensajeria_sin_ningun_token(capi, instancia, monkeypatch, capsys):
    http = HttpSimulado()
    monkeypatch.setattr(urllib.request, "urlopen", http)
    for var in ("META_CAPI_MENSAJERIA_TOKEN", "META_CAPI_MENSAJERIA_TOKEN_ACME", "META_CAPI_TOKEN",
                "META_CAPI_TOKEN_ACME"):
        monkeypatch.delenv(var, raising=False)
    with pytest.raises(SystemExit) as e:
        capi.main(["enviar", _payload(instancia, _ev()), "--cliente", "acme", "--dataset", "123456789012345",
                   "--test-code", "TEST1"])
    assert e.value.code == 2 and "META_CAPI_MENSAJERIA_TOKEN" in capsys.readouterr().err and http.peticiones == []


def test_enviar_usa_el_dataset_de_mensajeria_de_la_ficha(capi, instancia, monkeypatch):
    ficha = instancia / "clientes" / "acme" / "ficha.md"
    ficha.write_text(ficha.read_text(encoding="utf-8").replace(
        '  dataset: "000000000000000"', '  dataset: "000000000000000"\n  dataset_mensajeria: "987654321098765"'),
        encoding="utf-8")
    http = HttpSimulado().cuando("POST", r"/987654321098765/events$", {"events_received": 1})
    monkeypatch.setattr(urllib.request, "urlopen", http)
    monkeypatch.setenv("META_CAPI_MENSAJERIA_TOKEN", "t")
    capi.main(["enviar", _payload(instancia, _ev("instagram")), "--cliente", "acme", "--test-code", "TEST1"])
    assert len(http.peticiones) == 1


def test_enviar_mensajeria_con_dataset_de_ejemplo_es_configuracion(capi, instancia, monkeypatch, capsys):
    http = HttpSimulado()
    monkeypatch.setattr(urllib.request, "urlopen", http)
    monkeypatch.setenv("META_CAPI_MENSAJERIA_TOKEN", "t")
    with pytest.raises(SystemExit) as e:
        capi.main(["enviar", _payload(instancia, _ev()), "--cliente", "acme", "--test-code", "TEST1"])
    assert e.value.code == 2 and "dataset_mensajeria" in capsys.readouterr().err and http.peticiones == []


def test_enviar_mensajeria_sin_codigo_no_envia(capi, instancia, monkeypatch):
    http = HttpSimulado()
    monkeypatch.setattr(urllib.request, "urlopen", http)
    monkeypatch.setenv("META_CAPI_MENSAJERIA_TOKEN", "t")
    for extra in ([], ["--real"], ["--confirmo"]):
        with pytest.raises(SystemExit) as e:
            capi.main(["enviar", _payload(instancia, _ev()), "--cliente", "acme", "--dataset", "123456789012345",
                       *extra])
        assert e.value.code == 1
    assert http.peticiones == []


def test_enviar_lote_mezclado_no_envia(capi, instancia, monkeypatch, capsys):
    http = HttpSimulado()
    monkeypatch.setattr(urllib.request, "urlopen", http)
    monkeypatch.setenv("META_CAPI_TOKEN", "t")
    web = {"event_name": "Lead", "event_time": int(time.time()) - 60, "action_source": "website",
           "event_id": "lead_1", "event_source_url": "https://acme-automations.example/gracias",
           "user_data": {"em": ["a" * 64], "client_user_agent": "UA"}}
    with pytest.raises(SystemExit) as e:
        capi.main(["enviar", _payload(instancia, web, _ev()), "--cliente", "acme", "--dataset", "123456789012345",
                   "--test-code", "TEST1"])
    assert e.value.code == 1 and "por separado" in capsys.readouterr().err and http.peticiones == []


def test_enviar_mensajeria_invalida_no_llega_a_meta(capi, instancia, monkeypatch):
    http = HttpSimulado()
    monkeypatch.setattr(urllib.request, "urlopen", http)
    monkeypatch.setenv("META_CAPI_MENSAJERIA_TOKEN", "t")
    with pytest.raises(SystemExit) as e:
        capi.main(["enviar", _payload(instancia, _ev(evento="Lead")), "--cliente", "acme", "--dataset",
                   "123456789012345", "--test-code", "TEST1"])
    assert e.value.code == 1 and http.peticiones == []


def test_rechazo_de_meta_se_explica(capi, instancia, monkeypatch, capsys):
    http = HttpSimulado().cuando("POST", r"/events$", (400, {"error": {
        "message": "Invalid parameter", "code": 100, "error_subcode": 2804066,
        "error_user_msg": "El nombre del evento no es válido para business_messaging"}}))
    monkeypatch.setattr(urllib.request, "urlopen", http)
    monkeypatch.setenv("META_CAPI_MENSAJERIA_TOKEN", "t")
    with pytest.raises(SystemExit) as e:
        capi.main(["enviar", _payload(instancia, _ev()), "--cliente", "acme", "--dataset", "123456789012345",
                   "--test-code", "TEST1"])
    assert e.value.code == 1 and "2804066" in capsys.readouterr().err


def test_de_punta_a_punta_webhook_construir_validar_enviar(capi, instancia, monkeypatch, capsys):
    http = HttpSimulado().cuando("POST", r"/events$", {"events_received": 1, "fbtrace_id": "F"})
    monkeypatch.setattr(urllib.request, "urlopen", http)
    monkeypatch.setenv("META_CAPI_MENSAJERIA_TOKEN", "t")
    privado = instancia / "clientes" / "acme" / "privado"
    webhook = _guardar(privado / "webhook.json", _ejemplo("whatsapp-ctwa.json"))
    ev = privado / "ev.json"
    capi.main(["construir", "--desde-webhook", webhook, "--etapa", "lead", "--salida", str(ev)])
    with pytest.raises(SystemExit) as e:
        capi.main(["validar", str(ev)])
    assert e.value.code == 0
    capi.main(["enviar", str(ev), "--cliente", "acme", "--dataset", "123456789012345", "--test-code", "TEST9"])
    assert json.loads(http.peticiones[0]["form"]["data"])[0]["event_name"] == "LeadSubmitted"


# ---------------------------------------------------------------- plantillas de n8n, Make y webhook propio

def _n8n() -> dict:
    return json.loads((PLANTILLAS / "n8n-mensajeria-capi.json").read_text(encoding="utf-8"))


def test_plantillas_existen():
    for nombre in ("README.md", "n8n-mensajeria-capi.json", "make-mensajeria.md", "webhook-propio.md"):
        assert (PLANTILLAS / nombre).is_file(), nombre


def test_n8n_estructura_y_conexiones():
    flujo = _n8n()
    nombres = {n["name"] for n in flujo["nodes"]}
    assert len(nombres) == len(flujo["nodes"])
    for origen, salidas in flujo["connections"].items():
        assert origen in nombres
        for rama in salidas["main"]:
            for destino in rama:
                assert destino["node"] in nombres
    for nodo in flujo["nodes"]:
        assert nodo["type"].startswith("n8n-nodes-base.") and "credentials" not in nodo
    assert any(n["type"] == "n8n-nodes-base.webhook" for n in flujo["nodes"])


def test_n8n_sin_secretos_y_con_marcadores():
    texto = (PLANTILLAS / "n8n-mensajeria-capi.json").read_text(encoding="utf-8")
    assert not re.search(r"EAA[A-Za-z0-9]{20,}", texto) and "access_token=" not in texto
    assert "<<" in texto and "TEST_EVENT_CODE" in texto
    assert "/Users/" not in texto


def _codigo(nombre: str) -> str:
    return next(n for n in _n8n()["nodes"] if n["name"] == nombre)["parameters"]["jsCode"]


def test_n8n_misma_tabla_de_etapas_que_capi(capi):
    codigo = _codigo("Etapa → evento")
    tabla = json.loads(re.search(r"const EVENTOS_MENSAJERIA = (\[.*?\]);", codigo, re.S).group(1))
    assert tuple(tabla) == capi.EVENTOS_MENSAJERIA
    etapas = json.loads(re.search(r"const ETAPAS = (\[.*?\]);", codigo, re.S).group(1))
    assert tuple(etapas) == capi.ETAPAS


NODE = shutil.which("node")


CONFIG_PRUEBA = {"DATASET_ID": "123456789012345", "WABA_ID": WABA, "PAGE_ID": PAGINA, "IG_ID": IG,
                 "TEST_EVENT_CODE": "TEST123", "ENVIO_REAL_APROBADO": False, "CUALIFICA_EN": "cualificado",
                 "MONEDA": "EUR"}


def _ejecutar_codigo(nombre: str, items: list[dict], tmp_path, falla: bool = False):
    """Ejecuta el JavaScript de un nodo Code (modo «todos los elementos») con Node, sin n8n.

    Con `falla`, espera que el nodo lance un error y devuelve su mensaje."""
    arnes = tmp_path / "arnes.js"
    arnes.write_text(
        "const fs = require('fs');\n"
        "const items = JSON.parse(fs.readFileSync(0, 'utf8'));\n"
        "const $input = { all: () => items, first: () => items[0] };\n"
        f"const fn = new Function('$input', {json.dumps(_codigo(nombre))});\n"
        "process.stdout.write(JSON.stringify(fn($input)));\n", encoding="utf-8")
    r = subprocess.run([NODE, str(arnes)], input=json.dumps(items), capture_output=True, text=True, timeout=30)
    if falla:
        assert r.returncode != 0
        return r.stderr
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


@pytest.mark.skipif(not NODE, reason="Node no está instalado: la lógica JS del flujo de n8n no se ejecuta")
@pytest.mark.parametrize("ejemplo", ["whatsapp-ctwa.json", "whatsapp-estado.json", "messenger-ctm.json",
                                     "instagram-ctd.json"])
def test_n8n_extrae_el_mismo_origen_que_capi(capi, tmp_path, ejemplo):
    webhook = _ejemplo(ejemplo, reciente=False)
    salida = _ejecutar_codigo("Extraer origen del clic", [{"json": {"body": webhook}}], tmp_path)
    python = [m for m in capi.parsear_webhook(webhook) if m["anuncio"]]
    assert len(salida) == len(python)
    for js, py in zip(salida, python):
        j = js["json"]
        assert (j["mensajeria_canal"], j["mensajeria_cuenta"], j["mensajeria_anuncio"], j["mensajeria_clic"],
                j["mensajeria_entrada"]) == (py["canal"], py["cuenta"], py["anuncio"], py["ctwa_clid"] or "",
                                             str(py["momento"]))


def _cuerpo_crm(**cambios) -> dict:
    cuerpo = json.loads((EJEMPLOS / "crm-etapa.json").read_text(encoding="utf-8"))
    cuerpo.update({"momento": str(int(time.time()) - 60), **cambios})
    return cuerpo


@pytest.mark.skipif(not NODE, reason="Node no está instalado: la lógica JS del flujo de n8n no se ejecuta")
@pytest.mark.parametrize("cambios,esperado", [
    ({"etapa": "cualificado"}, "QualifiedLead"),
    ({"etapa": "lead", "mensajeria_enviados": ""}, "LeadSubmitted"),
    ({"etapa": "lead"}, None),                                # ya enviado: no se repite
    ({"etapa": "llamada"}, None),                             # sin evento de mensajería
    ({"etapa": "ganado", "valor": 4800}, "Purchase"),
    ({"etapa": "perdido"}, None),
    ({"mensajeria_canal": ""}, None),                         # no entró por mensajería
    ({"mensajeria_canal": "messenger", "mensajeria_cuenta": PAGINA, "mensajeria_persona": PSID,
      "mensajeria_clic": ""}, "QualifiedLead"),
    ({"mensajeria_canal": "instagram", "mensajeria_cuenta": IG, "mensajeria_persona": IGSID,
      "mensajeria_clic": ""}, "QualifiedLead"),
])
def test_n8n_etapa_a_evento(capi, tmp_path, cambios, esperado):
    salida = _ejecutar_codigo("Etapa → evento", [{"json": {"body": _cuerpo_crm(**cambios), "config": CONFIG_PRUEBA}}],
                              tmp_path)
    assert bool(salida) is bool(esperado)
    if esperado:
        j = salida[0]["json"]
        assert j["evento"]["event_name"] == esperado and j["necesita_hash"] is False
        assert capi.validar({"data": [j["evento"]]})[0] == []
        assert esperado in j["enviados"].split(",")


@pytest.mark.skipif(not NODE, reason="Node no está instalado: la lógica JS del flujo de n8n no se ejecuta")
@pytest.mark.parametrize("cambios,fragmento", [
    ({"etapa": "ganado", "valor": None}, "valor"),            # una venta sin importe no se pierde en silencio
    ({"mensajeria_clic": "", "telefono": ""}, "teléfono"),    # WhatsApp sin clic ni número
    ({"mensajeria_canal": "messenger", "mensajeria_persona": "", "mensajeria_clic": ""}, "PSID"),
])
def test_n8n_errores_a_la_vista(tmp_path, cambios, fragmento):
    error = _ejecutar_codigo("Etapa → evento", [{"json": {"body": _cuerpo_crm(**cambios), "config": CONFIG_PRUEBA}}],
                             tmp_path, falla=True)
    assert fragmento in error


@pytest.mark.skipif(not NODE, reason="Node no está instalado: la lógica JS del flujo de n8n no se ejecuta")
def test_n8n_cualifica_en_llamada(tmp_path):
    config = {**CONFIG_PRUEBA, "CUALIFICA_EN": "llamada"}
    cuerpo = _cuerpo_crm(etapa="llamada")
    salida = _ejecutar_codigo("Etapa → evento", [{"json": {"body": cuerpo, "config": config}}], tmp_path)
    assert salida[0]["json"]["evento"]["event_name"] == "QualifiedLead"
    cuerpo = _cuerpo_crm(etapa="cualificado")
    assert _ejecutar_codigo("Etapa → evento", [{"json": {"body": cuerpo, "config": config}}], tmp_path) == []


@pytest.mark.skipif(not NODE, reason="Node no está instalado: la lógica JS del flujo de n8n no se ejecuta")
def test_n8n_sin_codigo_de_prueba_no_monta_envio_real(tmp_path):
    item = {"json": {"evento": _ev(), "necesita_hash": False, "ph_normalizado": "", "contacto_id": "c1",
                     "enviados": "QualifiedLead", "config": {**CONFIG_PRUEBA, "TEST_EVENT_CODE": "<<TEST_EVENT_CODE>>"}}}
    assert "TEST_EVENT_CODE" in _ejecutar_codigo("Montar payload", [item], tmp_path, falla=True)
    item["json"]["config"]["ENVIO_REAL_APROBADO"] = True
    cuerpo = _ejecutar_codigo("Montar payload", [item], tmp_path)[0]["json"]["cuerpo"]
    assert "test_event_code" not in cuerpo


@pytest.mark.skipif(not NODE, reason="Node no está instalado: la lógica JS del flujo de n8n no se ejecuta")
@pytest.mark.parametrize("firma,secreto,fragmento", [
    ("buena", "secreto-de-prueba", None),
    ("sha256=" + "0" * 64, "secreto-de-prueba", "no válida"),   # aviso falso
    ("", "secreto-de-prueba", "no válida"),                     # sin cabecera
    ("buena", "", "META_APP_SECRET"),                           # n8n sin el secreto: falla cerrado
])
def test_n8n_verifica_la_firma_de_meta(tmp_path, firma, secreto, fragmento):
    import hashlib
    import hmac
    crudo = json.dumps(_ejemplo("whatsapp-ctwa.json", reciente=False)).encode()
    if firma == "buena":
        firma = "sha256=" + hmac.new(b"secreto-de-prueba", crudo, hashlib.sha256).hexdigest()
    (tmp_path / "crudo.json").write_bytes(crudo)
    arnes = tmp_path / "firma.js"
    arnes.write_text(
        "const fs = require('fs');\n"
        "const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;\n"
        f"const crudo = fs.readFileSync({json.dumps(str(tmp_path / 'crudo.json'))});\n"
        f"const items = [{{ json: {{ headers: {{ 'x-hub-signature-256': {json.dumps(firma)} }}, body: {{}} }} }}];\n"
        f"const fn = new AsyncFunction('$input', '$env', 'require', {json.dumps(_codigo('Verificar firma'))});\n"
        "fn.call({ helpers: { getBinaryDataBuffer: async () => crudo } }, { all: () => items, first: () => items[0] },\n"
        f"        {{ META_APP_SECRET: {json.dumps(secreto)} }}, require)\n"
        "  .then((r) => process.stdout.write(JSON.stringify(r)))\n"
        "  .catch((e) => { process.stderr.write(e.message); process.exit(1); });\n", encoding="utf-8")
    r = subprocess.run([NODE, str(arnes)], capture_output=True, text=True, timeout=30)
    if fragmento:
        assert r.returncode != 0 and fragmento in r.stderr
    else:
        assert r.returncode == 0, r.stderr
        assert json.loads(r.stdout)[0]["json"]["body"]["object"] == "whatsapp_business_account"


@pytest.mark.skipif(not NODE, reason="Node no está instalado: la lógica JS del flujo de n8n no se ejecuta")
def test_n8n_sin_clic_hashea_igual_que_capi(capi, tmp_path):
    cuerpo = _cuerpo_crm(mensajeria_clic="", etapa="cualificado")
    paso1 = _ejecutar_codigo("Etapa → evento", [{"json": {"body": cuerpo, "config": CONFIG_PRUEBA}}], tmp_path)
    assert paso1[0]["json"]["necesita_hash"] is True and paso1[0]["json"]["ph_normalizado"] == "16505551212"
    paso1[0]["json"]["ph_hash"] = capi.sha256(paso1[0]["json"]["ph_normalizado"])  # lo que hace el nodo Crypto
    paso2 = _ejecutar_codigo("Montar payload", paso1, tmp_path)
    cuerpo_meta = paso2[0]["json"]["cuerpo"]
    ev = cuerpo_meta["data"][0]
    assert ev["user_data"]["ph"] == [TEL_HASH] and ev["user_data"]["page_id"]
    assert cuerpo_meta["test_event_code"]
    errores, _ = capi.validar(copy.deepcopy(cuerpo_meta))
    assert errores == []
