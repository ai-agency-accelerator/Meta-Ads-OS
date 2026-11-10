"""stripe_datos.py: clave restringida, solo GET, importes bien convertidos y cruce por anuncio por cohorte."""
from __future__ import annotations

import csv
import importlib
import json
import urllib.request
from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from http_simulado import HttpSimulado

AD_ID = "120000000000001"
DESDE, HASTA = "2026-11-02", "2026-11-08"
PERIODO = ["--desde", DESDE, "--hasta", HASTA]
CLAVE = "rk_test_ficticia"


def _precio(centimos, intervalo="month", cada=1, moneda="eur", **extra):
    return {"price": {"unit_amount": centimos, "currency": moneda,
                      "recurring": {"interval": intervalo, "interval_count": cada, **extra}}}


CLIENTES = [
    {"id": "cus_1", "created": 1762160400, "email": "ana@ejemplo.test", "name": "Ana",
     "metadata": {"utm_source": "fb_ad", "ad_id": AD_ID, "utm_content": "20261116_x_y_demo_h1",
                  "utm_campaign": "ES_SAAS_ADQ_HV", "fbc": "fb.1.1762160400000.abc"}},
    {"id": "cus_2", "created": 1762246800, "email": "bea@ejemplo.test", "name": "Bea", "metadata": {}},
    {"id": "cus_3", "created": 1762333200, "email": "carla@ejemplo.test", "name": "Carla",
     "metadata": {"utm_source": "google"}},
]
SUSCRIPCIONES = [
    {"id": "sub_1", "customer": "cus_1", "status": "active", "currency": "eur", "trial_start": 1762160400,
     "trial_end": 1763370000, "items": {"data": [dict(_precio(4900), quantity=1)]}, "metadata": {}},
    {"id": "sub_2", "customer": "cus_2", "status": "trialing", "currency": "eur", "trial_start": 1762246800,
     "trial_end": 1763456400, "items": {"data": [dict(_precio(4900), quantity=1)]},
     "metadata": {"utm_source": "facebook", "utm_content": "20261116_x_y_estatico_h2"}},
    {"id": "sub_9", "customer": "cus_fuera", "status": "active", "currency": "eur",
     "items": {"data": [dict(_precio(9900), quantity=1)]}, "metadata": {}},
]
CARGOS = [
    {"id": "ch_1", "customer": "cus_1", "status": "succeeded", "paid": True, "amount": 4900, "amount_captured": 4900,
     "amount_refunded": 0, "currency": "eur", "created": 1763370000},
    {"id": "ch_2", "customer": "cus_1", "status": "succeeded", "paid": True, "amount": 4900, "amount_captured": 4900,
     "amount_refunded": 4900, "currency": "eur", "created": 1763370100},
    {"id": "ch_3", "customer": "cus_3", "status": "succeeded", "paid": True, "amount": 9900, "amount_captured": 9900,
     "amount_refunded": 0, "currency": "eur", "created": 1762333300},
    {"id": "ch_4", "customer": "cus_2", "status": "failed", "paid": False, "amount": 4900, "amount_captured": 0,
     "amount_refunded": 0, "currency": "eur", "created": 1763456500},
    {"id": "ch_5", "customer": "cus_1", "status": "succeeded", "paid": True, "amount": 1000, "amount_captured": 1000,
     "amount_refunded": 0, "currency": "usd", "created": 1763456600},
]


@pytest.fixture
def stripe(instancia, monkeypatch):
    import _comun
    import stripe_datos as modulo
    modulo = importlib.reload(modulo)
    monkeypatch.setattr(_comun.time, "sleep", lambda *_: None)
    monkeypatch.delenv("STRIPE_KEY_ACME", raising=False)
    monkeypatch.delenv("STRIPE_API_VERSION", raising=False)
    monkeypatch.setenv("STRIPE_KEY", CLAVE)
    monkeypatch.setattr("builtins.input", lambda *_: pytest.fail("una lectura ha pedido datos por teclado"))
    return modulo


def _lista(datos):
    return lambda p: {"object": "list", "data": datos, "has_more": False}


def _http(monkeypatch, **cambios) -> HttpSimulado:
    def subs(p):
        estado = p["query"].get("status")
        datos = [s for s in SUSCRIPCIONES if estado == "all" or s["status"] == estado]
        return {"object": "list", "data": datos, "has_more": False}

    respuestas = {"customers": _lista(CLIENTES), "subscriptions": subs, "charges": _lista(CARGOS)}
    respuestas.update(cambios)
    http = HttpSimulado()
    for recurso, r in respuestas.items():
        http.cuando("GET", rf"^/v1/{recurso}$", r)
    monkeypatch.setattr(urllib.request, "urlopen", http)
    return http


def _sin_datos_personales(texto: str) -> None:
    for dato in ("ejemplo.test", "Ana", "Bea", "Carla", "fb.1.", CLAVE):
        assert dato not in texto


@pytest.mark.parametrize("clave", ["sk_live_ficticia", "sk_test_ficticia", "pk_live_ficticia", ""])
def test_solo_claves_restringidas(stripe, monkeypatch, capsys, clave):
    monkeypatch.setenv("STRIPE_KEY", clave)
    http = _http(monkeypatch)
    with pytest.raises(SystemExit) as e:
        stripe.main(["clientes", "--cliente", "acme"])
    assert e.value.code == 2 and http.peticiones == []
    assert clave == "" or clave not in capsys.readouterr().err  # la clave nunca se imprime


def test_clave_por_cliente_y_cabeceras(stripe, monkeypatch, capsys):
    monkeypatch.setenv("STRIPE_KEY_ACME", "rk_live_de_acme")
    http = _http(monkeypatch)
    stripe.main(["clientes", "--cliente", "acme", "--json", "--sin-archivos", *PERIODO])
    p = http.peticiones[0]
    assert p["cabeceras"]["authorization"] == "Bearer rk_live_de_acme"
    assert p["cabeceras"]["stripe-version"] == stripe.VERSION_API
    inicio = int(datetime(2026, 11, 2, tzinfo=ZoneInfo("Europe/Madrid")).timestamp())
    assert int(p["query"]["created[gte]"]) == inicio and int(p["query"]["created[lt]"]) == inicio + 7 * 86400
    assert "rk_live_de_acme" not in p["url"]


def test_pagina_con_starting_after(stripe, monkeypatch, capsys):
    paginas = [{"data": CLIENTES[:1], "has_more": True}, {"data": CLIENTES[1:], "has_more": False}]
    http = _http(monkeypatch, customers=paginas)
    stripe.main(["clientes", "--cliente", "acme", "--json", "--sin-archivos", *PERIODO])
    assert json.loads(capsys.readouterr().out)["clientes"] == 3
    consultas = [p["query"] for p in http.de("GET", r"/customers$")]
    assert "starting_after" not in consultas[0] and consultas[1]["starting_after"] == "cus_1"
    assert consultas[0]["limit"] == "100"


def test_clientes_privado_y_resumen_sin_pii(stripe, instancia, monkeypatch, capsys):
    _http(monkeypatch)
    stripe.main(["clientes", "--cliente", "acme", "--json", *PERIODO])
    salida = capsys.readouterr().out
    _sin_datos_personales(salida)
    resumen = json.loads(salida)
    assert (resumen["clientes"], resumen["de_meta"], resumen["de_meta_con_ad_id"]) == (3, 1, 1)
    privado = instancia / "clientes" / "acme" / "privado" / f"stripe-clientes_{DESDE}_{HASTA}.csv"
    filas = list(csv.DictReader(privado.open(encoding="utf-8")))
    assert filas[0]["email"] == "ana@ejemplo.test" and filas[0]["fbc"] == "sí"
    assert "fb.1." not in privado.read_text(encoding="utf-8")  # ni siquiera en privado hace falta el fbc


def test_suscripciones_pruebas_y_mrr(stripe, monkeypatch, capsys):
    http = _http(monkeypatch)
    stripe.main(["suscripciones", "--cliente", "acme", "--json", *PERIODO])
    resumen = json.loads(capsys.readouterr().out)
    assert resumen["suscripciones_nuevas"] == 3 and resumen["pruebas_iniciadas"] == 2
    assert resumen["mrr_cuenta"] == 148.0 and resumen["suscripciones_activas"] == 2
    estados = [p["query"]["status"] for p in http.de("GET", r"/subscriptions$")]
    assert estados == ["all", "active"]


def test_pagos_neto_y_reembolsos(stripe, instancia, monkeypatch, capsys):
    _http(monkeypatch)
    stripe.main(["pagos", "--cliente", "acme", "--json", *PERIODO])
    resumen = json.loads(capsys.readouterr().out)
    assert resumen["cobrado_neto"] == {"EUR": 148.0, "USD": 10.0}
    assert resumen["reembolsado"] == {"EUR": 49.0} and resumen["clientes_con_cobro"] == 2
    assert (instancia / "clientes" / "acme" / "privado" / f"stripe-pagos_{DESDE}_{HASTA}.csv").exists()


def test_por_anuncio_cohorte(stripe, instancia, monkeypatch, capsys):
    http = _http(monkeypatch)
    stripe.main(["por-anuncio", "--cliente", "acme", "--json", *PERIODO])
    salida = capsys.readouterr().out
    _sin_datos_personales(salida)
    resumen = json.loads(salida)
    assert (resumen["de_meta"], resumen["no_meta"], resumen["cobertura_anuncio_pct"]) == (2, 1, 100.0)
    assert resumen["cargos_en_otras_monedas"] == {"USD": 1}

    ruta = instancia / "clientes" / "acme" / "datos" / f"stripe-por-anuncio_{DESDE}_{HASTA}.csv"
    filas = list(csv.DictReader(ruta.open(encoding="utf-8")))
    assert list(filas[0]) == stripe.COLUMNAS_ANUNCIO
    h1, h2 = filas
    assert (h1["ad_id"], h1["utm_content"], h1["campana"]) == (AD_ID, "20261116_x_y_demo_h1", "ES_SAAS_ADQ_HV")
    assert [h1[k] for k in ("registros", "pruebas", "clientes_pago", "cash", "reembolsos", "mrr", "moneda")] == \
        ["1", "1", "1", "49.0", "49.0", "49.0", "EUR"]
    assert (h2["utm_content"], h2["pruebas"], h2["clientes_pago"], h2["mrr"]) == ("20261116_x_y_estatico_h2", "1", "0", "0.0")
    _sin_datos_personales(ruta.read_text(encoding="utf-8"))
    import registro_creativo  # el agregado es la entrada de negocio de `registro_creativo.py` (B1)
    por_id, por_nombre, presentes = registro_creativo.agregar_negocio(registro_creativo.leer_csv(ruta), "stripe")
    assert {"leads", "pruebas", "clientes_pago", "cash"} <= presentes  # registros cuenta como leads
    assert por_id[AD_ID]["cash"] == 49.0 and por_nombre["20261116_x_y_estatico_h2"]["pruebas"] == 1
    leads = instancia / "clientes" / "acme" / "privado" / f"clientes-stripe_{DESDE}_{HASTA}.csv"
    _sin_datos_personales(leads.read_text(encoding="utf-8"))
    import embudo  # el archivo por cliente es la entrada de `embudo.py cohortes --modelo saas` (B1)
    filas_embudo, _ = embudo.leer_leads(leads)
    ana = next(f for f in filas_embudo if f["ad_id"] == AD_ID)
    assert (ana["prueba"], ana["cliente_pago"], ana["cash"], ana["mrr"]) == (True, True, 49.0, 49.0)

    assert {p["metodo"] for p in http.peticiones} == {"GET"}
    for p in http.de("GET", r"/(subscriptions|charges)$"):  # lo de después, hasta hoy: sin límite superior
        assert "created[lt]" not in p["query"] and "created[gte]" in p["query"]


def test_por_anuncio_sin_archivos(stripe, instancia, monkeypatch, capsys):
    _http(monkeypatch)
    stripe.main(["por-anuncio", "--cliente", "acme", "--json", "--sin-archivos", *PERIODO])
    assert "csv" not in json.loads(capsys.readouterr().out)
    for carpeta in ("datos", "privado"):
        d = instancia / "clientes" / "acme" / carpeta
        assert not d.exists() or not list(d.glob("stripe-*"))


@pytest.mark.parametrize("codigo,texto", [(401, "STRIPE_KEY"), (403, "charges")])
def test_permisos_son_configuracion(stripe, monkeypatch, capsys, codigo, texto):
    _http(monkeypatch, charges=(codigo, {"error": {"message": "permiso", "type": "invalid_request_error"}}))
    with pytest.raises(SystemExit) as e:
        stripe.main(["pagos", "--cliente", "acme", *PERIODO])
    assert e.value.code == 2 and texto in capsys.readouterr().err


@pytest.mark.parametrize("item,esperado", [
    (dict(_precio(4900), quantity=1), 49.0),
    (dict(_precio(4900), quantity=3), 147.0),
    (dict(_precio(120000, "year"), quantity=1), 100.0),
    (dict(_precio(30000, "month", 3), quantity=1), 100.0),
    (dict(_precio(1000, "week"), quantity=1), round(10 * 52.1775 / 12, 6)),
    (dict(_precio(6000, moneda="jpy"), quantity=1), 6000.0),
    (dict(_precio(100, usage_type="metered")), 0.0),
    ({"price": {"unit_amount": None, "currency": "eur", "recurring": {"interval": "month"}}, "quantity": 1}, 0.0),
    ({"price": {"unit_amount": 5000, "currency": "eur"}, "quantity": 1}, 0.0),  # pago único: no es recurrente
])
def test_mrr(stripe, item, esperado):
    assert round(stripe.mrr({"items": {"data": [item]}}), 6) == esperado


@pytest.mark.parametrize("cargo,esperado", [
    ({"status": "succeeded", "paid": True, "amount": 4900, "amount_captured": 4900, "amount_refunded": 900,
      "currency": "eur"}, 40.0),
    ({"status": "succeeded", "paid": True, "amount": 4900, "amount_captured": None, "currency": "eur"}, 49.0),
    ({"status": "succeeded", "paid": True, "amount": 4900, "amount_captured": 2000, "currency": "eur"}, 20.0),
    ({"status": "succeeded", "paid": True, "amount": 3000, "amount_captured": 3000, "currency": "jpy"}, 3000.0),
    ({"status": "pending", "paid": False, "amount": 4900, "currency": "eur"}, 0.0),
    ({"status": "succeeded", "paid": True, "amount": 4900, "amount_captured": 4900, "amount_refunded": 6000,
      "currency": "eur"}, 0.0),
])
def test_neto(stripe, cargo, esperado):
    assert stripe.neto(cargo) == esperado


def test_atribucion(stripe):
    assert stripe.atribucion({"utm_source": "google"}, {"utm_source": "ig", "utm_content": "h3"})["anuncio"] == "h3"
    assert stripe.atribucion({"ad_id": AD_ID})["es_meta"]
    assert not stripe.atribucion({"utm_source": "figma"})["es_meta"]
    assert stripe.atribucion(None, {})["es_meta"] is False


def test_fechas_por_defecto_hasta_ayer(stripe):
    class A:
        desde = hasta = None
    desde, hasta = stripe.periodo(A())
    assert hasta == date.today().fromordinal(date.today().toordinal() - 1) and (hasta - desde).days == 6
