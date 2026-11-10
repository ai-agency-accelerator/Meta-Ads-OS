"""ghl.py: solo lectura, datos personales solo en privado/ y cruce por anuncio por cohorte."""
from __future__ import annotations

import csv
import importlib
import json
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from http_simulado import HttpSimulado

AD_ID = "120000000000001"
DESDE, HASTA = "2026-11-02", "2026-11-08"
PERIODO = ["--desde", DESDE, "--hasta", HASTA]

CONTACTOS = [
    {"id": "cA", "dateAdded": "2026-11-03T09:00:00.000Z", "firstName": "Ana", "email": "ana@ejemplo.test",
     "phone": "+34600000001",
     "attributionSource": {"utmSource": "fb_ad", "utmContent": "20261116_x_y_demo_h1", "campaign": "ES_LEADS_ADQ_HV",
                           "url": f"https://acme.test/diagnostico?utm_source=fb_ad&ad_id={AD_ID}"}},
    {"id": "cB", "dateAdded": "2026-11-04T09:00:00.000Z", "firstName": "Bea", "email": "bea@ejemplo.test",
     "attributionSource": {"utmSource": "facebook", "utmContent": "20261116_x_y_estatico_h2"}},
    {"id": "cC", "dateAdded": "2026-11-05T09:00:00.000Z", "firstName": "Carla", "email": "carla@ejemplo.test",
     "source": "Google", "attributionSource": {"utmSource": "google", "medium": "cpc"}},
]
PIPELINES = {"pipelines": [{"id": "p1", "name": "Ventas", "stages": [
    {"id": "s1", "name": "Nuevo", "position": 0}, {"id": "s2", "name": "Cualificado", "position": 1},
    {"id": "s3", "name": "Cerrado", "position": 2}]}]}
OPORTUNIDADES = {"opportunities": [
    {"id": "o1", "contactId": "cA", "pipelineId": "p1", "pipelineStageId": "s3", "status": "won", "monetaryValue": 3000},
    {"id": "o2", "contactId": "cB", "pipelineId": "p1", "pipelineStageId": "s1", "status": "open", "monetaryValue": 0}],
    "meta": {"total": 2}}
CALENDARIOS = {"calendars": [{"id": "cal1", "name": "Diagnóstico"}]}
CITAS = {"events": [
    {"id": "e1", "contactId": "cA", "appointmentStatus": "showed", "startTime": "2026-11-04T10:00:00+01:00",
     "dateAdded": "2026-11-03T11:00:00.000Z"},
    {"id": "e2", "contactId": "cB", "appointmentStatus": "cancelled", "startTime": "2026-11-05T10:00:00+01:00",
     "dateAdded": "2026-11-04T10:00:00.000Z"}]}
PAGOS = {"data": [
    {"_id": "t1", "contactId": "cA", "amount": 1000, "amountRefunded": 0, "currency": "EUR", "status": "succeeded"},
    {"_id": "t2", "contactId": "cC", "amount": 500, "amountRefunded": 500, "currency": "EUR", "status": "refunded"},
    {"_id": "t3", "contactId": "cA", "amount": 200, "currency": "EUR", "status": "failed"}], "totalCount": 3}


@pytest.fixture
def ghl(instancia, monkeypatch):
    import _comun
    import ghl as modulo
    modulo = importlib.reload(modulo)
    monkeypatch.setattr(modulo.time, "sleep", lambda *_: None)
    monkeypatch.setattr(_comun.time, "sleep", lambda *_: None)
    for var in ("GHL_TOKEN_ACME", "GHL_LOCATION_ACME"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("GHL_TOKEN", "pit-ficticio")
    monkeypatch.setenv("GHL_LOCATION", "loc123")
    monkeypatch.setattr("builtins.input", lambda *_: pytest.fail("una lectura ha pedido datos por teclado"))
    return modulo


def _http(monkeypatch, **cambios) -> HttpSimulado:
    respuestas = {"contactos": {"contacts": CONTACTOS, "total": 3}, "pipelines": PIPELINES,
                  "oportunidades": OPORTUNIDADES, "calendarios": CALENDARIOS, "citas": CITAS, "pagos": PAGOS}
    respuestas.update(cambios)
    http = HttpSimulado()
    http.cuando("POST", r"^/contacts/search$", respuestas["contactos"])
    http.cuando("GET", r"^/opportunities/pipelines$", respuestas["pipelines"])
    http.cuando("GET", r"^/opportunities/search$", respuestas["oportunidades"])
    http.cuando("GET", r"^/calendars/$", respuestas["calendarios"])
    http.cuando("GET", r"^/calendars/events$", respuestas["citas"])
    http.cuando("GET", r"^/payments/transactions$", respuestas["pagos"])
    monkeypatch.setattr(urllib.request, "urlopen", http)
    return http


def _sin_datos_personales(texto: str) -> None:
    for dato in ("ejemplo.test", "Ana", "Bea", "Carla", "+346", "pit-ficticio"):
        assert dato not in texto


def test_sin_credenciales_es_configuracion(ghl, monkeypatch, capsys):
    monkeypatch.delenv("GHL_TOKEN")
    http = _http(monkeypatch)
    with pytest.raises(SystemExit) as e:
        ghl.main(["contactos", "--cliente", "acme"])
    assert e.value.code == 2 and http.peticiones == []
    assert "GHL_TOKEN_ACME" in capsys.readouterr().err


def test_credenciales_por_cliente(ghl, monkeypatch, capsys):
    monkeypatch.setenv("GHL_TOKEN_ACME", "pit-de-acme")
    monkeypatch.setenv("GHL_LOCATION_ACME", "locacme")
    http = _http(monkeypatch)
    ghl.main(["contactos", "--cliente", "acme", "--json", "--sin-archivos", *PERIODO])
    p = http.peticiones[0]
    assert p["cabeceras"]["authorization"] == "Bearer pit-de-acme" and p["json"]["locationId"] == "locacme"


def test_contactos_privado_y_resumen_sin_pii(ghl, instancia, monkeypatch, capsys):
    http = _http(monkeypatch)
    ghl.main(["contactos", "--cliente", "acme", "--json", *PERIODO])
    salida = capsys.readouterr().out
    _sin_datos_personales(salida)
    resumen = json.loads(salida)
    assert (resumen["contactos"], resumen["de_meta"], resumen["de_meta_con_ad_id"]) == (3, 2, 1)
    p = http.peticiones[0]
    assert p["metodo"] == "POST" and p["cabeceras"]["version"] == "2021-07-28"
    assert p["json"]["filters"][0]["value"] == {"gte": "2026-11-01T23:00:00Z", "lte": "2026-11-08T23:00:00Z"}
    privado = instancia / "clientes" / "acme" / "privado" / f"ghl-contactos_{DESDE}_{HASTA}.csv"
    filas = list(csv.DictReader(privado.open(encoding="utf-8")))
    assert filas[0]["email"] == "ana@ejemplo.test" and filas[0]["ad_id"] == AD_ID
    assert not (instancia / "clientes" / "acme" / "datos").exists() or not list(
        (instancia / "clientes" / "acme" / "datos").glob("ghl-*"))


def test_contactos_pagina(ghl, monkeypatch, capsys):
    monkeypatch.setattr(ghl, "PAGINA_CONTACTOS", 2)
    pagina1 = {"contacts": [dict(CONTACTOS[0], searchAfter=[1, "cA"]), dict(CONTACTOS[1], searchAfter=[2, "cB"])]}
    http = _http(monkeypatch, contactos=[pagina1, {"contacts": [CONTACTOS[2]]}])
    ghl.main(["contactos", "--cliente", "acme", "--json", "--sin-archivos", *PERIODO])
    assert json.loads(capsys.readouterr().out)["contactos"] == 3
    cuerpos = [p["json"] for p in http.de("POST", r"/contacts/search$")]
    assert cuerpos[0]["page"] == 1 and cuerpos[1]["searchAfter"] == [2, "cB"]


def test_solo_busca_nunca_escribe(ghl):
    api = ghl.GHL("x", "loc")
    for ruta in ("/contacts/", "/opportunities/", "/contacts/upsert"):
        with pytest.raises(ghl.ErrorGHL):
            api.buscar(ruta, {})


def test_oportunidades(ghl, monkeypatch, capsys):
    http = _http(monkeypatch)
    ghl.main(["oportunidades", "--cliente", "acme", "--json", "--sin-archivos", *PERIODO])
    resumen = json.loads(capsys.readouterr().out)
    assert resumen["por_estado"] == {"won": 1, "open": 1} and resumen["valor_ganado"] == 3000
    assert {"pipeline": "Ventas", "etapa": "Cerrado", "n": 1} in resumen["por_etapa"]
    q = http.de("GET", r"/opportunities/search$")[0]["query"]
    assert (q["status"], q["date"], q["endDate"], q["location_id"]) == ("all", "11-02-2026", "11-08-2026", "loc123")


def test_oportunidades_con_motivo_de_perdida(ghl, instancia, monkeypatch, capsys):
    perdidas = {"opportunities": OPORTUNIDADES["opportunities"] + [
        {"id": "o3", "contactId": "cC", "pipelineId": "p1", "pipelineStageId": "s2", "status": "lost",
         "lostReasonId": "lr1"},
        {"id": "o4", "contactId": "cC", "pipelineId": "p1", "pipelineStageId": "s1", "status": "lost"}]}
    http = _http(monkeypatch, oportunidades=perdidas)
    http.cuando("GET", r"^/opportunities/lost-reason$", {"lostReasons": [{"id": "lr1", "name": "Precio"}], "total": 1})
    ghl.main(["oportunidades", "--cliente", "acme", "--json", *PERIODO])
    resumen = json.loads(capsys.readouterr().out)
    assert resumen["por_motivo_perdida"] == {"Precio": 1, "(sin motivo)": 1} and "aviso" not in resumen
    assert http.de("GET", r"/lost-reason$")[0]["query"]["locationId"] == "loc123"
    filas = list(csv.DictReader((instancia / resumen["csv_privado"]).open(encoding="utf-8")))
    assert [f["motivo_perdida"] for f in filas] == ["", "", "Precio", ""]
    # sin permiso para leer los motivos: salen los IDs y un aviso, sin romper la orden
    http = _http(monkeypatch, oportunidades=perdidas)
    http.cuando("GET", r"^/opportunities/lost-reason$", (403, {"message": "scope"}))
    ghl.main(["oportunidades", "--cliente", "acme", "--json", "--sin-archivos", *PERIODO])
    resumen = json.loads(capsys.readouterr().out)
    assert resumen["por_motivo_perdida"] == {"lr1": 1, "(sin motivo)": 1} and "opportunities.readonly" in resumen["aviso"]


def test_sin_perdidas_no_pide_motivos(ghl, monkeypatch, capsys):
    http = _http(monkeypatch)
    ghl.main(["oportunidades", "--cliente", "acme", "--json", "--sin-archivos", *PERIODO])
    assert json.loads(capsys.readouterr().out)["por_motivo_perdida"] == {} and not http.de("GET", r"/lost-reason$")


def test_oportunidades_pagina(ghl, monkeypatch, capsys):
    monkeypatch.setattr(ghl, "PAGINA", 1)
    primera = {"opportunities": OPORTUNIDADES["opportunities"][:1], "meta": {"startAfter": 1, "startAfterId": "o1"}}
    segunda = {"opportunities": OPORTUNIDADES["opportunities"][1:], "meta": {"startAfter": 2, "startAfterId": "o2"}}
    http = _http(monkeypatch, oportunidades=[primera, segunda, {"opportunities": [], "meta": {}}])
    ghl.main(["oportunidades", "--cliente", "acme", "--json", "--sin-archivos", *PERIODO])
    assert json.loads(capsys.readouterr().out)["oportunidades"] == 2
    assert http.de("GET", r"/opportunities/search$")[1]["query"]["startAfterId"] == "o1"


def test_citas_y_show_rate(ghl, monkeypatch, capsys):
    http = _http(monkeypatch)
    ghl.main(["citas", "--cliente", "acme", "--json", "--sin-archivos", *PERIODO])
    resumen = json.loads(capsys.readouterr().out)
    assert (resumen["citas"], resumen["shows"], resumen["show_rate"]) == (1, 1, 100.0)
    assert (resumen["canceladas"], resumen["canceladas_ya_pasadas"], resumen["show_rate_estricto"]) == (1, 1, 50.0)
    p = http.de("GET", r"/calendars/events$")[0]
    assert p["cabeceras"]["version"] == "2021-04-15" and p["query"]["calendarId"] == "cal1"
    madrid = datetime(2026, 11, 2, tzinfo=ZoneInfo("Europe/Madrid"))  # el día empieza en la zona de la ficha
    assert int(p["query"]["startTime"]) == int(madrid.timestamp() * 1000)


def test_pagos_neto(ghl, instancia, monkeypatch, capsys):
    _http(monkeypatch)
    ghl.main(["pagos", "--cliente", "acme", "--json", *PERIODO])
    resumen = json.loads(capsys.readouterr().out)
    assert resumen["cobrado_neto"] == {"EUR": 1000.0} and resumen["clientes_con_cobro"] == 1
    assert (instancia / "clientes" / "acme" / "privado" / f"ghl-pagos_{DESDE}_{HASTA}.csv").exists()


def test_por_anuncio_cohorte(ghl, instancia, monkeypatch, capsys):
    http = _http(monkeypatch)
    ghl.main(["por-anuncio", "--cliente", "acme", "--json", *PERIODO])
    salida = capsys.readouterr().out
    _sin_datos_personales(salida)
    resumen = json.loads(salida)
    assert (resumen["de_meta"], resumen["no_meta"], resumen["cobertura_anuncio_pct"]) == (2, 1, 100.0)
    assert resumen["horas_hasta_cita_mediana"] == 2.0
    assert resumen["pipelines_sin_etapa_cualificada"] == []

    ruta = instancia / "clientes" / "acme" / "datos" / f"ghl-por-anuncio_{DESDE}_{HASTA}.csv"
    filas = list(csv.DictReader(ruta.open(encoding="utf-8")))
    assert list(filas[0]) == ghl.COLUMNAS_ANUNCIO
    a, b = filas
    assert (a["ad_id"], a["utm_content"], a["campana"]) == (AD_ID, "20261116_x_y_demo_h1", "ES_LEADS_ADQ_HV")
    assert [a[k] for k in ("leads", "cualificados", "citas", "shows", "clientes_pago", "cash", "valor_ganado")] == \
        ["1", "1", "1", "1", "1", "1000.0", "3000.0"]
    assert (b["ad_id"], b["utm_content"], b["citas"], b["cualificados"]) == ("", "20261116_x_y_estatico_h2", "0", "0")
    _sin_datos_personales(ruta.read_text(encoding="utf-8"))
    import registro_creativo  # el agregado es la entrada de negocio de `registro_creativo.py` (B1)
    por_id, por_nombre, presentes = registro_creativo.agregar_negocio(registro_creativo.leer_csv(ruta), "ghl")
    assert {"leads", "cualificados", "citas", "shows", "clientes_pago", "cash"} <= presentes
    assert por_id[AD_ID]["cash"] == 1000.0 and por_nombre["20261116_x_y_estatico_h2"]["leads"] == 1
    leads = instancia / "clientes" / "acme" / "privado" / f"leads-ghl_{DESDE}_{HASTA}.csv"
    texto = leads.read_text(encoding="utf-8")
    assert "ejemplo.test" not in texto and "Ana" not in texto  # ni en privado hace falta el contacto
    import embudo  # el archivo por lead es la entrada de `embudo.py cohortes` (B1)
    filas_embudo, _ = embudo.leer_leads(leads)
    ana = next(f for f in filas_embudo if f["ad_id"] == AD_ID)
    assert (ana["cualificado"], ana["cita"], ana["show"], ana["venta"], ana["cash"]) == (True, True, True, True, 1000.0)

    assert {p["metodo"] for p in http.peticiones} == {"GET", "POST"}
    assert {p["path"] for p in http.de("POST", r".")} == {"/contacts/search"}


def test_por_anuncio_etapa_cualificada_a_medida(ghl, monkeypatch, capsys):
    _http(monkeypatch)
    ghl.main(["por-anuncio", "--cliente", "acme", "--json", "--sin-archivos", "--cualificado", "Nuevo", *PERIODO])
    filas = {f["utm_content"]: f for f in json.loads(capsys.readouterr().out)["por_anuncio"]}
    assert filas["20261116_x_y_estatico_h2"]["cualificados"] == 1


def test_por_anuncio_sin_archivos(ghl, instancia, monkeypatch, capsys):
    _http(monkeypatch)
    ghl.main(["por-anuncio", "--cliente", "acme", "--json", "--sin-archivos", *PERIODO])
    assert "csv" not in json.loads(capsys.readouterr().out)
    for carpeta in ("datos", "privado"):
        d = instancia / "clientes" / "acme" / carpeta
        assert not d.exists() or not list(d.glob("ghl-*"))


@pytest.mark.parametrize("codigo", [401, 403])
def test_token_rechazado_es_configuracion(ghl, monkeypatch, codigo):
    _http(monkeypatch, pipelines=(codigo, {"message": "Unauthorized", "statusCode": codigo}))
    with pytest.raises(SystemExit) as e:
        ghl.main(["oportunidades", "--cliente", "acme", *PERIODO])
    assert e.value.code == 2


def test_busqueda_rechazada_es_configuracion(ghl, monkeypatch):
    _http(monkeypatch, contactos=(401, {"message": "Invalid JWT"}))
    with pytest.raises(SystemExit) as e:
        ghl.main(["contactos", "--cliente", "acme", *PERIODO])
    assert e.value.code == 2


def test_fechas_mal_es_error_de_usuario(ghl, monkeypatch):
    http = _http(monkeypatch)
    with pytest.raises(SystemExit) as e:
        ghl.main(["contactos", "--cliente", "acme", "--desde", "2026-11-09", "--hasta", "2026-11-01"])
    assert e.value.code == 1 and http.peticiones == []


def test_atribucion_desde_campo_personalizado(ghl):
    contacto = {"customFields": [{"id": "cf1", "value": AD_ID}], "attributionSource": {"medium": "form"}}
    at = ghl.atribucion(contacto, "cf1")
    assert at["es_meta"] and at["ad_id"] == AD_ID
    at = ghl.atribucion({"customFields": [{"id": "cf1", "value": "20261116_x_y_demo_h1"}]}, "cf1")
    assert at["es_meta"] and at["anuncio"] == "20261116_x_y_demo_h1" and at["ad_id"] == ""


def test_atribucion_prefiere_el_toque_de_meta(ghl):
    contacto = {"attributions": [{"utmSource": "google", "isFirst": True},
                                 {"utmSource": "ig", "utmContent": "anuncio+con+espacios", "isFirst": False}]}
    at = ghl.atribucion(contacto)
    assert at["es_meta"] and at["anuncio"] == "anuncio con espacios"
    assert not ghl.atribucion({"attributionSource": {"utmSource": "newsletter"}})["es_meta"]
    assert not ghl.atribucion({"attributionSource": {"utmSource": "figma"}})["es_meta"]  # «fig» no es Meta


# ---------------------------------------------------------------- I6 (revisión independiente)

def _pipeline(*etapas: str) -> dict:
    return {"pipelines": [{"id": "p1", "name": "Ventas", "stages": [
        {"id": f"s{i}", "name": n, "position": i} for i, n in enumerate(etapas)]}]}


def _cualificados(ghl, monkeypatch, capsys, pipeline: dict, ops: list[dict]) -> dict:
    tres = [dict(CONTACTOS[0]), dict(CONTACTOS[1]),
            dict(CONTACTOS[1], id="cD", attributionSource={"utmSource": "fb_ad", "utmContent": "20261116_x_y_ugc_h3"})]
    _http(monkeypatch, contactos={"contacts": tres}, pipelines=pipeline,
          oportunidades={"opportunities": ops, "meta": {}}, citas={"events": []}, pagos={"data": []})
    ghl.main(["por-anuncio", "--cliente", "acme", "--json", "--sin-archivos", *PERIODO])
    return {f["utm_content"]: f["cualificados"] for f in json.loads(capsys.readouterr().out)["por_anuncio"]}


def test_i6_perdido_al_final_no_es_cualificado(ghl, monkeypatch, capsys):
    """Hallazgo 1: pipeline de la guía (ghl-meta.md, contrato §16) con «Perdido» detrás de «Purchase»."""
    pl = _pipeline("Lead", "Cualificado", "Llamada agendada", "Llamada asistida", "Propuesta enviada", "Purchase",
                   "Perdido")
    ops = [{"id": "o1", "contactId": "cA", "pipelineId": "p1", "pipelineStageId": "s6", "status": "lost"},
           {"id": "o2", "contactId": "cB", "pipelineId": "p1", "pipelineStageId": "s0", "status": "open"},
           {"id": "o3", "contactId": "cD", "pipelineId": "p1", "pipelineStageId": "s1", "status": "open"}]
    c = _cualificados(ghl, monkeypatch, capsys, pl, ops)
    assert c == {"20261116_x_y_demo_h1": 0, "20261116_x_y_estatico_h2": 0, "20261116_x_y_ugc_h3": 1}


def test_i6_no_cualificado_delante_no_cuenta(ghl, monkeypatch, capsys):
    """Hallazgo 1, variante: «No cualificado» delante de «Cualificado» (abierta o perdida) no es cualificado."""
    pl = _pipeline("Nuevo", "No cualificado", "Cualificado", "Cita agendada")
    ops = [{"id": "o1", "contactId": "cA", "pipelineId": "p1", "pipelineStageId": "s1", "status": "open"},
           {"id": "o2", "contactId": "cB", "pipelineId": "p1", "pipelineStageId": "s1", "status": "lost"},
           {"id": "o3", "contactId": "cD", "pipelineId": "p1", "pipelineStageId": "s3", "status": "open"}]
    c = _cualificados(ghl, monkeypatch, capsys, pl, ops)
    assert c == {"20261116_x_y_demo_h1": 0, "20261116_x_y_estatico_h2": 0, "20261116_x_y_ugc_h3": 1}


def test_i6_perdida_tras_cualificar_sigue_contando(ghl, monkeypatch, capsys):
    """Una oportunidad marcada «lost» en «Propuesta enviada» sí llegó a cualificarse: cuenta (la cohorte mide hasta
    dónde llegó cada lead, no si sigue abierto)."""
    pl = _pipeline("Lead", "Unqualified", "Cualificado", "Propuesta enviada", "Purchase", "Perdido")
    ops = [{"id": "o1", "contactId": "cA", "pipelineId": "p1", "pipelineStageId": "s3", "status": "lost"},
           {"id": "o2", "contactId": "cB", "pipelineId": "p1", "pipelineStageId": "s1", "status": "abandoned"},
           {"id": "o3", "contactId": "cD", "pipelineId": "p1", "pipelineStageId": "s5", "status": "lost"}]
    c = _cualificados(ghl, monkeypatch, capsys, pl, ops)
    assert c == {"20261116_x_y_demo_h1": 1, "20261116_x_y_estatico_h2": 0, "20261116_x_y_ugc_h3": 0}


def test_i6_contactos_exporta_dnd(ghl, instancia, monkeypatch, capsys):
    """Hallazgo 15: `contactos` exporta el DND (global y por canal) para que `audiencias_meta.py --bajas` lo vea."""
    cs = [dict(CONTACTOS[0], dnd=True), dict(CONTACTOS[1], dndSettings={"Email": {"status": "active"},
                                                                         "SMS": {"status": "inactive"}}),
          dict(CONTACTOS[2])]
    _http(monkeypatch, contactos={"contacts": cs})
    ghl.main(["contactos", "--cliente", "acme", "--json", *PERIODO])
    privado = instancia / "clientes" / "acme" / "privado" / f"ghl-contactos_{DESDE}_{HASTA}.csv"
    filas = {f["contact_id"]: f for f in csv.DictReader(privado.open(encoding="utf-8"))}
    assert (filas["cA"]["dnd"], filas["cB"]["dnd"], filas["cC"]["dnd"]) == ("sí", "sí", "no")
    assert "email" in filas["cB"]["dnd_canales"].lower() and "sms" not in filas["cB"]["dnd_canales"].lower()


def test_i6_oportunidades_exporta_cambio_de_estado(ghl, instancia, monkeypatch, capsys):
    """Hallazgo 20: la fecha de la pérdida (lastStatusChangeAt) va al CSV privado para `audiencias_meta.py`."""
    ops = {"opportunities": [dict(OPORTUNIDADES["opportunities"][1], status="lost",
                                  lastStageChangeAt="2026-07-01T10:00:00.000Z",
                                  lastStatusChangeAt="2026-10-20T10:00:00.000Z")], "meta": {}}
    _http(monkeypatch, oportunidades=ops)
    ghl.main(["oportunidades", "--cliente", "acme", "--json", *PERIODO])
    privado = instancia / "clientes" / "acme" / "privado" / f"ghl-oportunidades_{DESDE}_{HASTA}.csv"
    fila = next(csv.DictReader(privado.open(encoding="utf-8")))
    assert (fila["cambio_etapa"], fila["cambio_estado"]) == ("2026-07-01T10:00:00", "2026-10-20T10:00:00")
