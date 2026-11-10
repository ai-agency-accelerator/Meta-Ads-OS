"""reglas_meta.py: propuesta desde la ficha, madurez, validador anti-folklore, crear/pausar con confirmación, sin red."""
from __future__ import annotations

import importlib
import json

import urllib.request

import pytest

from http_simulado import HttpSimulado

ECONOMIA = """
## Economía (con `herramientas/economia.py`)
| Métrica | Break-even | Target | Fuente o supuesto |
|---|---|---|---|
| Coste por venta / CAC | 2.400 € | | economia.py |
| CPL | {be} | {target} | economia.py |
| Coste por lead cualificado | | 150 € | economia.py |
| Coste por cita / por show | | | |
"""


@pytest.fixture
def rm(instancia, monkeypatch):
    import meta_ads
    importlib.reload(meta_ads)
    import reglas_meta
    modulo = importlib.reload(reglas_meta)
    monkeypatch.setattr(meta_ads.time, "sleep", lambda *_: None)
    monkeypatch.delenv("META_TOKEN_ACME", raising=False)
    monkeypatch.setenv("META_TOKEN", "token-de-prueba")
    _economia(instancia)
    return modulo


def _economia(instancia, target="80 €", be="120 €"):
    f = instancia / "clientes" / "acme" / "ficha.md"
    texto = f.read_text(encoding="utf-8").split("\n## Economía")[0]
    f.write_text(texto + ECONOMIA.format(target=target, be=be), encoding="utf-8")


def _cuenta_real(instancia):
    f = instancia / "clientes" / "acme" / "ficha.md"
    f.write_text(f.read_text(encoding="utf-8").replace("act_000000000000000", "act_12345"), encoding="utf-8")


def _topes(instancia, cambio):
    f = instancia / "clientes" / "acme" / "ficha.md"
    f.write_text(f.read_text(encoding="utf-8").replace("cambio_dia: 100", f"cambio_dia: {cambio}"), encoding="utf-8")


def _corre(rm, capsys, *args) -> tuple[int, str, str]:
    try:
        rm.main(list(args))
        codigo = 0
    except SystemExit as e:
        codigo = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    salida = capsys.readouterr()
    return codigo, salida.out, salida.err


def _http(monkeypatch, http: HttpSimulado | None = None) -> HttpSimulado:
    http = http or HttpSimulado()
    monkeypatch.setattr(urllib.request, "urlopen", http)
    return http


def _propuesta(rm, capsys, instancia, *extra) -> tuple[dict, str]:
    codigo, out, err = _corre(rm, capsys, "proponer", "--cliente", "acme", "--json", *extra)
    assert codigo == 0, err
    datos = json.loads(out)
    return datos, str(instancia / datos["archivo"])


def _regla(datos: dict, clave: str) -> dict:
    return next(r for r in datos["reglas"] if r["clave"] == clave)


def _filtro(regla: dict, campo: str) -> dict:
    return next(f for f in regla["api"]["evaluation_spec"]["filters"] if f["field"] == campo)


# ---------------------------------------------------------------- proponer

def test_proponer_lee_el_cpa_de_la_ficha_y_escribe_importes_en_centimos(rm, capsys, instancia):
    datos, ruta = _propuesta(rm, capsys, instancia)
    assert ruta.endswith(f"clientes/acme/planes/reglas-{rm.date.today().isoformat()}.json")
    assert json.loads(open(ruta, encoding="utf-8").read())["reglas"] == datos["reglas"]
    assert datos["cpa_objetivo"] == 80 and "target" in datos["cpa_origen"] and datos["madurez_dias"] == 0
    kill = _regla(datos, "anuncio-sin-conversion")
    assert datos["modo"] == "sombra"  # KB 07 §6.2: toda regla nueva arranca avisando
    assert kill["accion"] == "NOTIFICATION" and kill["nivel"] == "AD" and kill["api"]["name"].endswith("-sombra")
    assert _regla(datos, "gasto-hoy-fuera-de-tope")["accion"] == "PAUSE"  # la seguridad de dinero no espera
    # sin --conversiones-semana se supone cuenta pequeña: kill a 4× por anuncio (KB 07, implicaciones; I6)
    assert any("cuenta pequeña" in a for a in datos["avisos"])
    assert _filtro(kill, "lifetime_spent - today_spent")["value"] == 32000  # 4 × 80 € en céntimos
    assert _filtro(kill, "results") == {"field": "results", "value": 1, "operator": "LESS_THAN"}
    assert _filtro(kill, "time_preset")["value"] == "LIFETIME"
    assert _filtro(kill, "hours_since_creation")["value"] == 72
    assert _filtro(kill, "adset.optimization_goal")["value"] == ["OFFSITE_CONVERSIONS", "LEAD_GENERATION"]
    assert _filtro(_regla(datos, "gasto-hoy-fuera-de-tope"), "spent")["value"] == 22000  # 2,2 × 100 €
    assert _filtro(_regla(datos, "gasto-hoy-alto"), "spent")["value"] == 17500  # 1,75 × 100 €
    assert _filtro(_regla(datos, "cpa-disparado"), "spent - 16000 * results")["value"] == 0
    assert _regla(datos, "gasto-hoy-fuera-de-tope")["api"]["schedule_spec"] == {"schedule_type": "SEMI_HOURLY"}
    assert kill["api"]["schedule_spec"] == {"schedule_type": "CUSTOM",
                                            "schedule": [{"start_minute": 360, "end_minute": 360}]}
    for r in datos["reglas"]:
        assert r["api"]["evaluation_spec"]["evaluation_type"] == "SCHEDULE"
        assert r["api"]["execution_spec"]["execution_type"] in ("NOTIFICATION", "PAUSE")
        assert _filtro(r, "attribution_window")["value"] == "ACCOUNT_DEFAULT"
        assert r["por_que"] and r["evidencia"] and r["ads_manager"]
        assert all(e.startswith("[") for e in r["evidencia"])
    assert any("destinatarios" in p for p in datos["pendientes"])
    assert any("cuenta real" in p for p in datos["pendientes"])  # la ficha de ejemplo tiene act_000…


def test_proponer_no_trae_folklore_ni_subidas_de_presupuesto(rm, capsys, instancia):
    for extra in ([], ["--evento", "Schedule", "--cpa", "300"], ["--activo"]):
        datos, _ = _propuesta(rm, capsys, instancia, *extra)
        texto = json.dumps([r["api"] for r in datos["reglas"]])
        assert "frequency" not in texto and "CHANGE_BUDGET" not in texto and "UNPAUSE" not in texto
        descartadas = " ".join(d["regla"] for d in datos["descartadas"])
        assert "Frecuencia" in descartadas and "20 %" in descartadas


def test_proponer_usa_el_break_even_si_no_hay_target(rm, capsys, instancia):
    _economia(instancia, target="", be="1.200,50 €")
    datos, _ = _propuesta(rm, capsys, instancia)
    assert datos["cpa_objetivo"] == 1200.5 and "break-even" in datos["cpa_origen"]
    assert any("break-even" in a for a in datos["avisos"])


@pytest.mark.parametrize("celda, valor", [("80 €", 80), ("1.200,50 €", 1200.5), ("≈ 95", 95), ("80.5 (sin IVA)", 80.5),
                                          ("1.200", 1200), ("", None), ("0", None), ("—", None)])
def test_numero_entiende_el_formato_espanol(rm, celda, valor):
    assert rm.numero(celda) == valor


def test_proponer_coste_de_la_fila_del_evento(rm, capsys, instancia):
    datos, _ = _propuesta(rm, capsys, instancia, "--evento", "lead_cualificado")
    assert datos["evento"] == "LeadCualificado" and datos["cpa_objetivo"] == 150 and datos["madurez_dias"] == 3
    assert _filtro(_regla(datos, "conjunto-sin-conversion"), "optimization_goal")["value"] == [
        "OFFSITE_CONVERSIONS", "QUALITY_LEAD"]


@pytest.mark.parametrize("extra, codigo, texto", [
    (["--evento", "Schedule"], 2, "coste por cita"),           # la fila existe pero está vacía
    (["--evento", "LlamadaAsistida"], 2, "--cpa"),             # evento sin fila en la ficha
    (["--multiplicador", "1.5"], 1, "37 %"),
    (["--evento", "Purchase", "--cpa", "2000", "--madurez", "45"], 1, "evento anterior"),
    (["--madurez", "-1"], 1, "negativa"),
    (["--campanas", "12a"], 1, "no es un ID"),
])
def test_proponer_errores(rm, capsys, instancia, extra, codigo, texto):
    c, _, err = _corre(rm, capsys, "proponer", "--cliente", "acme", *extra)
    assert c == codigo and texto in err
    assert not list((instancia / "clientes" / "acme" / "planes").glob("reglas-*.json"))


def test_proponer_sin_topes_sale_2(rm, capsys, instancia):
    _topes(instancia, 0)
    c, _, err = _corre(rm, capsys, "proponer", "--cliente", "acme")
    assert c == 2 and "topes" in err
    assert not list((instancia / "clientes" / "acme" / "planes").glob("reglas-*.json"))


def test_proponer_no_pisa_una_propuesta_anterior(rm, capsys, instancia):
    _, ruta1 = _propuesta(rm, capsys, instancia)
    _, ruta2 = _propuesta(rm, capsys, instancia, "--multiplicador", "4")
    assert ruta1 != ruta2 and ruta2.endswith("-2.json")


def test_multiplicador_entre_2_y_3_avisa(rm, capsys, instancia):
    datos, _ = _propuesta(rm, capsys, instancia, "--multiplicador", "2.5")
    assert any("8,2 %" in a for a in datos["avisos"])
    assert _filtro(_regla(datos, "anuncio-sin-conversion"), "lifetime_spent - today_spent")["value"] == 20000


def test_madurez_descuenta_el_gasto_que_aun_no_ha_convertido(rm, capsys, instancia):
    datos, _ = _propuesta(rm, capsys, instancia, "--evento", "Schedule", "--cpa", "300", "--activo",
                          "--conversiones-semana", "40")
    assert datos["madurez_dias"] == 3
    kill = _regla(datos, "anuncio-sin-conversion")
    assert _filtro(kill, "lifetime_spent - last_7_days_spent")["value"] == 90000
    assert kill["accion"] == "PAUSE"  # por la API sí puede pausar…
    assert any("solo enviar notificación" in p for p in kill["ads_manager"])  # …en Ads Manager solo avisa
    # 900 € en 4 días madurados (7 − 3) pide 225 €/día, por encima del tope de 100 €: la ventana pasa a 14 días.
    sin = _regla(datos, "sin-conversiones")
    assert _filtro(sin, "time_preset")["value"] == "LAST_14D"
    assert _filtro(sin, "last_14d_spent - last_3d_spent")["value"] == 90000
    assert "81,82 EUR/día" in sin["resumen"]
    # 3 resultados a 2× 300 € = 1.800 €: en 11 días madurados no cabe con 100 €/día; en 25, sí.
    cpa = _regla(datos, "cpa-disparado")
    assert _filtro(cpa, "time_preset")["value"] == "LAST_28D"
    assert _filtro(cpa, "last_28d_results - last_3d_results") == {
        "field": "last_28d_results - last_3d_results", "value": 2, "operator": "GREATER_THAN"}
    assert _filtro(cpa, "(last_28d_spent - last_3d_spent) - 60000 * (last_28d_results - last_3d_results)")


@pytest.mark.parametrize("tope, sin, cpa", [(100, "LAST_3D", "LAST_14D"), (30, "LAST_14D", "LAST_28D"),
                                            (10, None, None)])
def test_las_alertas_usan_la_ventana_mas_corta_que_puede_saltar(rm, capsys, instancia, tope, sin, cpa):
    _topes(instancia, tope)
    datos, _ = _propuesta(rm, capsys, instancia, "--conversiones-semana", "40")  # CPL 80 €: 240 € sin leads, o
    # 480 € para 3 leads a 160 €
    reglas = {r["clave"]: r for r in datos["reglas"]}
    for clave, esperado in (("sin-conversiones", sin), ("cpa-disparado", cpa)):
        if esperado:
            assert _filtro(reglas[clave], "time_preset")["value"] == esperado
        else:
            assert clave not in reglas
    if tope == 10:
        motivos = " ".join(d["por_que"] for d in datos["descartadas"])
        assert "no saltaría" in motivos and "/brief-diario" in motivos and "informe semanal" in motivos


def test_madurez_larga_descarta_las_alertas_que_no_caben(rm, capsys, instancia):
    datos, _ = _propuesta(rm, capsys, instancia, "--evento", "Purchase", "--cpa", "2000")
    assert datos["madurez_dias"] == 28  # Purchase en servicios-high-ticket: venta B2B lenta
    claves = {r["clave"] for r in datos["reglas"]}
    assert "sin-conversiones" not in claves and "cpa-disparado" not in claves
    assert _filtro(_regla(datos, "conjunto-sin-conversion"), "lifetime_spent - last_30_days_spent")
    assert sum("madurez" in d["por_que"] for d in datos["descartadas"]) == 2


def test_activo_pausa_y_cambia_el_nombre(rm, capsys, instancia):
    datos, _ = _propuesta(rm, capsys, instancia, "--activo", "--multiplicador", "4", "--conversiones-semana", "40")
    assert datos["modo"] == "activo"
    kill = _regla(datos, "conjunto-sin-conversion")
    assert kill["accion"] == "PAUSE" and kill["api"]["name"] == "PROTECT_OS_conjunto-sin-conversion_4x80EUR"
    assert any("desactivar conjuntos" in p for p in kill["ads_manager"])
    assert not any("≥4×" in a for a in datos["avisos"])


def test_campanas_y_destinatarios(rm, capsys, instancia):
    datos, _ = _propuesta(rm, capsys, instancia, "--campanas", "555555,666666", "--avisar", "777777")
    assert _filtro(_regla(datos, "anuncio-sin-conversion"), "campaign.id")["value"] == [555555, 666666]
    assert not any(f["field"] == "campaign.id" for f in
                   _regla(datos, "gasto-hoy-fuera-de-tope")["api"]["evaluation_spec"]["filters"])
    for r in datos["reglas"]:
        assert r["api"]["execution_spec"]["execution_options"] == [
            {"field": "user_ids", "value": [777777], "operator": "EQUAL"}]
    assert not any("destinatarios" in p for p in datos["pendientes"])


def test_evento_normaliza_nombres(rm):
    assert rm.evento("COMPLETE_REGISTRATION")[0].nombre == "CompleteRegistration"
    assert rm.evento("Diagnóstico completado")[0].nombre == "DiagnosticoCompletado"
    e, conocido = rm.evento("EventoRaro")
    assert not conocido and e.madurez == 7


@pytest.mark.parametrize("extra", [[], ["--evento", "Schedule", "--cpa", "300"], ["--evento", "LlamadaAsistida",
                                   "--cpa", "400"], ["--evento", "PropuestaEnviada", "--cpa", "900"],
                                   ["--evento", "Purchase", "--cpa", "2000"], ["--multiplicador", "2"]])
@pytest.mark.parametrize("modo", [[], ["--activo"]])
def test_el_conjunto_por_defecto_pasa_su_propio_validador(rm, capsys, instancia, extra, modo):
    datos, _ = _propuesta(rm, capsys, instancia, *extra, *modo, "--avisar", "777777")
    cpa = rm.a_minimo(datos["cpa_objetivo"], "EUR")
    for r in datos["reglas"]:
        graves = [t for g, t in rm.analizar(r["api"], cpa) if g == "bloquea"]
        assert not graves, (r["api"]["name"], graves)
        for f in r["api"]["evaluation_spec"]["filters"]:
            assert len(rm._tokens(f["field"])) <= 6  # límite de Meta para fórmulas


# ---------------------------------------------------------------- validador

def _api(accion="PAUSE", filtros=None, opciones=None, **extra) -> dict:
    ex = {"execution_type": accion, "execution_options": [{"field": "user_ids", "value": [1], "operator": "EQUAL"}]
          + (opciones or [])}
    return {"name": "x", "evaluation_spec": {"evaluation_type": "SCHEDULE", "filters": [
        {"field": "entity_type", "value": "ADSET", "operator": "EQUAL"}] + (filtros or [])},
            "execution_spec": ex, "schedule_spec": {"schedule_type": "DAILY"}, **extra}


def _f(campo, op, valor):
    return {"field": campo, "operator": op, "value": valor}


def _graves(rm, api, cpa=8000):
    return [t for g, t in rm.analizar(api, cpa) if g == "bloquea"]


def test_validador_rechaza_subir_presupuesto_y_encender(rm):
    sube = _api("CHANGE_BUDGET", [_f("time_preset", "EQUAL", "LAST_7D"), _f("cost_per", "LESS_THAN", 5000)],
                [_f("change_spec", "EQUAL", {"amount": 20, "unit": "PERCENTAGE"})])
    assert any("SUBE presupuesto" in t for t in _graves(rm, sube))
    assert any("ENCIENDE" in t for t in _graves(rm, _api("UNPAUSE", [_f("time_preset", "EQUAL", "YESTERDAY")])))
    assert _graves(rm, _api("REBALANCE_BUDGET")) and _graves(rm, _api("ROTATE")) and _graves(rm, _api("CHANGE_BID"))


def test_validador_rechaza_frecuencia(rm):
    api = _api("PAUSE", [_f("time_preset", "EQUAL", "LAST_7D"), _f("frequency", "GREATER_THAN", 3)])
    assert any("M37" in t for t in _graves(rm, api))


def test_validador_rechaza_pausar_por_rendimiento_de_hoy(rm):
    hoy = _api("PAUSE", [_f("time_preset", "EQUAL", "TODAY"), _f("cost_per", "GREATER_THAN", 12000)])
    assert any("TODAY" in t for t in _graves(rm, hoy))
    ayer = _api("PAUSE", [_f("time_preset", "EQUAL", "LIFETIME"), _f("yesterday_cost_per", "GREATER_THAN", 12000)])
    assert any("YESTERDAY" in t for t in _graves(rm, ayer))
    # Restar el gasto de hoy en una fórmula no es «medir hoy»: es descontar lo que no ha madurado.
    madurado = _api("PAUSE", [_f("time_preset", "EQUAL", "LIFETIME"), _f("hours_since_creation", "GREATER_THAN", 72),
                              _f("lifetime_spent - today_spent", "GREATER_THAN", 24000), _f("results", "LESS_THAN", 1)])
    assert not _graves(rm, madurado)


def test_validador_kill_nunca_por_debajo_de_2x(rm):
    def kill(umbral):
        return _api("PAUSE", [_f("time_preset", "EQUAL", "LIFETIME"), _f("hours_since_creation", "GREATER_THAN", 72),
                              _f("spent", "GREATER_THAN", umbral), _f("results", "EQUAL", 0)])
    assert any("Mata a 1×" in t and "36,8 %" in t for t in _graves(rm, kill(8000)))  # 1× el CPA de 80 €
    assert not _graves(rm, kill(20000))                                     # 2,5×: avisa pero no bloquea
    assert any("2,5×" in t for g, t in rm.analizar(kill(20000), 8000) if g == "aviso")
    assert not [t for t in rm.analizar(kill(24000), 8000)]                  # 3×: limpio


def test_validador_otros_bloqueos(rm):
    disparador = _api("NOTIFICATION")
    disparador["evaluation_spec"]["evaluation_type"] = "TRIGGER"
    assert any("disparador" in t for t in _graves(rm, disparador))
    sin_nivel = _api("NOTIFICATION")
    sin_nivel["evaluation_spec"]["filters"] = [_f("time_preset", "EQUAL", "LAST_7D")]
    assert any("entity_type" in t for t in _graves(rm, sin_nivel))
    assert any("time_preset" in t for t in _graves(rm, _api("NOTIFICATION", [_f("spent", "GREATER_THAN", 1)])))
    assert any("ACCOUNT_DEFAULT" in t for t in _graves(rm, _api("NOTIFICATION", [
        _f("time_preset", "EQUAL", "LAST_7D"), _f("attribution_window", "EQUAL", "7D_CLICK")])))
    assert any("1,75" in t for t in _graves(rm, _api("PAUSE", [_f("daily_ratio_spent", "GREATER_THAN", 1.2)])))


def test_validador_avisos(rm):
    viejo = _api("PAUSE", [_f("time_preset", "EQUAL", "LAST_7D"), _f("cost_per", "GREATER_THAN", 20000)],
                 created_time="2025-11-02T10:00:00+0000", status="HAS_ISSUES", disable_error_code=1)
    viejo["execution_spec"]["execution_options"] = []
    avisos = " ".join(t for g, t in rm.analizar(viejo, 8000) if g == "aviso")
    assert "recalíbralo" in avisos and "con problemas" in avisos and "Sin destinatarios" in avisos
    assert "Pausa por CPA" in avisos


def test_describir_filtro_pasa_centimos_a_euros(rm):
    assert rm.describir_filtro(_f("lifetime_spent - today_spent", "GREATER_THAN", 24000), "EUR").endswith("240,00 EUR")
    assert rm.describir_filtro(_f("ctr", "LESS_THAN", 0.5), "EUR") == "CTR < 0.5"
    assert rm.describir_filtro(_f("spent", "GREATER_THAN", 5000), "JPY").endswith("5.000 JPY")
    assert rm.describir_filtro(_f("time_preset", "EQUAL", "TODAY"), "EUR") is None


# ---------------------------------------------------------------- crear

def _http_meta(monkeypatch, existentes=(), conjuntos=(), moneda="EUR") -> HttpSimulado:
    contador = {"n": 0}

    def nuevo(_p):
        contador["n"] += 1
        return {"id": f"99900{contador['n']}"}

    http = HttpSimulado()
    http.cuando("GET", r"/act_12345$", {"currency": moneda})
    http.cuando("GET", r"/act_12345/adrules_library$", {"data": list(existentes)})
    http.cuando("GET", r"/act_12345/adsets$", {"data": list(conjuntos)})
    http.cuando("POST", r"/act_12345/adrules_library$", nuevo)
    return _http(monkeypatch, http)


def test_crear_simular_no_usa_la_red(rm, capsys, instancia, monkeypatch):
    _, ruta = _propuesta(rm, capsys, instancia)
    monkeypatch.delenv("META_TOKEN")  # ni siquiera necesita token
    http = _http(monkeypatch)
    c, out, _ = _corre(rm, capsys, "crear", ruta, "--cliente", "acme", "--simular", "--pasos")
    assert c == 0 and http.peticiones == []
    assert "No se ha tocado Meta" in out and "Ads Manager" in out and "Programación" in out
    assert "destinatarios" in out  # pendientes visibles, sin bloquear la simulación


def test_crear_sin_confirmo_no_escribe(rm, capsys, instancia, monkeypatch):
    _cuenta_real(instancia)
    _, ruta = _propuesta(rm, capsys, instancia, "--avisar", "777777")
    http = _http_meta(monkeypatch)
    c, out, err = _corre(rm, capsys, "crear", ruta, "--cliente", "acme")
    assert c == 1 and "--confirmo" in err and not http.de("POST", r".")
    assert not (instancia / "logs" / "cambios.jsonl").exists()


def test_crear_con_pendientes_no_toca_meta(rm, capsys, instancia, monkeypatch):
    _cuenta_real(instancia)
    _, ruta = _propuesta(rm, capsys, instancia)  # sin --avisar
    http = _http(monkeypatch)
    c, _, err = _corre(rm, capsys, "crear", ruta, "--cliente", "acme", "--confirmo")
    assert c == 1 and "destinatarios" in err and http.peticiones == []


def test_crear_con_confirmo_crea_registra_y_no_duplica(rm, capsys, instancia, monkeypatch):
    _cuenta_real(instancia)
    datos, ruta = _propuesta(rm, capsys, instancia, "--avisar", "777777")
    primera = datos["reglas"][0]["api"]["name"]
    http = _http_meta(monkeypatch, existentes=[{"id": "888001", "name": primera, "status": "ENABLED"}])
    c, out, err = _corre(rm, capsys, "crear", ruta, "--cliente", "acme", "--confirmo")
    assert c == 0, err
    posts = http.de("POST", r"/adrules_library$")
    assert len(posts) == len(datos["reglas"]) - 1  # la que ya existía no se duplica
    form = posts[0]["form"]
    assert form["status"] == "ENABLED" and form["access_token"] == "token-de-prueba"
    spec = json.loads(form["evaluation_spec"])
    assert spec["evaluation_type"] == "SCHEDULE" and {"field": "entity_type", "value": "ADSET",
                                                      "operator": "EQUAL"} in spec["filters"]
    assert json.loads(form["execution_spec"])["execution_options"][0]["value"] == [777777]
    assert json.loads(form["schedule_spec"])["schedule_type"] in ("CUSTOM", "SEMI_HOURLY")
    log = [json.loads(x) for x in (instancia / "logs" / "cambios.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(log) == len(posts) and {x["accion"] for x in log} == {"crear_regla"}
    assert all(x["cliente"] == "acme" and x["sistema"] == "meta" for x in log)
    estado = json.loads(open(ruta.replace(".json", ".estado.json"), encoding="utf-8").read())
    assert estado["reglas"][primera] == "888001" and len(estado["reglas"]) == len(datos["reglas"])
    assert "| regla |" in out and "token-de-prueba" not in out


def test_crear_activo_recuerda_desactivar_la_sombra(rm, capsys, instancia, monkeypatch):
    _cuenta_real(instancia)
    sombra, _ = _propuesta(rm, capsys, instancia, "--avisar", "777777", "--conversiones-semana", "40")
    existentes = [{"id": f"88800{i}", "name": r["api"]["name"], "status": "ENABLED"}
                  for i, r in enumerate(sombra["reglas"], 1)]
    activo, ruta = _propuesta(rm, capsys, instancia, "--avisar", "777777", "--activo", "--conversiones-semana", "40")
    http = _http_meta(monkeypatch, existentes=existentes)
    c, out, err = _corre(rm, capsys, "crear", ruta, "--cliente", "acme", "--confirmo")
    assert c == 0, err
    assert len(http.de("POST", r"/adrules_library$")) == 2  # solo las dos pausas por conversión cambian de nombre
    assert "pausar 888001 888002 --cliente acme --confirmo" in out


def test_crear_bloquea_si_hay_presupuestos_fuera_del_tope(rm, capsys, instancia, monkeypatch):
    _cuenta_real(instancia)
    _, ruta = _propuesta(rm, capsys, instancia, "--avisar", "777777")
    http = _http_meta(monkeypatch, conjuntos=[{"id": "444001", "name": "BROAD_LEAD", "daily_budget": "15000",
                                               "campaign": {"id": "555001", "name": "C"}}])
    c, _, err = _corre(rm, capsys, "crear", ruta, "--cliente", "acme", "--confirmo")
    assert c == 1 and "150,00 EUR/día" in err and not http.de("POST", r".")


def test_crear_moneda_distinta_sale_2(rm, capsys, instancia, monkeypatch):
    _cuenta_real(instancia)
    _, ruta = _propuesta(rm, capsys, instancia, "--avisar", "777777")
    http = _http_meta(monkeypatch, moneda="USD")
    c, _, err = _corre(rm, capsys, "crear", ruta, "--cliente", "acme", "--confirmo")
    assert c == 2 and "USD" in err and not http.de("POST", r".")


@pytest.mark.parametrize("cambio, texto", [
    (lambda api: api["execution_spec"].update(execution_type="CHANGE_BUDGET"), "SUBE presupuesto"),
    (lambda api: api["execution_spec"].update(execution_type="UNPAUSE"), "ENCIENDE"),
    (lambda api: api["evaluation_spec"]["filters"].append(
        {"field": "frequency", "value": 3, "operator": "GREATER_THAN"}), "M37"),
    (lambda api: next(f for f in api["evaluation_spec"]["filters"] if f["field"] == "time_preset").update(
        value="TODAY"), "TODAY"),
    (lambda api: next(f for f in api["evaluation_spec"]["filters"] if f["field"].startswith("lifetime_spent")).update(
        value=12000), "1,5×"),
])
def test_crear_rechaza_una_propuesta_editada_a_mano(rm, capsys, instancia, monkeypatch, cambio, texto):
    _cuenta_real(instancia)
    datos, ruta = _propuesta(rm, capsys, instancia, "--avisar", "777777", "--activo")
    cambio(_regla(datos, "anuncio-sin-conversion")["api"])
    datos.pop("archivo")
    open(ruta, "w", encoding="utf-8").write(json.dumps(datos))
    http = _http(monkeypatch)
    c, _, err = _corre(rm, capsys, "crear", ruta, "--cliente", "acme", "--confirmo")
    assert c == 1 and texto in err and http.peticiones == []


def test_crear_rechaza_otro_cliente_y_json_invalido(rm, capsys, instancia, tmp_path):
    malo = tmp_path / "malo.json"
    malo.write_text("{no es json", encoding="utf-8")
    assert _corre(rm, capsys, "crear", str(malo), "--cliente", "acme", "--simular")[0] == 1
    otro = tmp_path / "otro.json"
    otro.write_text(json.dumps({"formato": "reglas-meta-os/1", "cliente": "nimbo", "moneda": "EUR", "reglas": []}),
                    encoding="utf-8")
    c, _, err = _corre(rm, capsys, "crear", str(otro), "--cliente", "acme", "--simular")
    assert c == 1 and "nimbo" in err


def test_sin_token_sale_2_con_alternativa(rm, capsys, instancia, monkeypatch):
    _cuenta_real(instancia)
    monkeypatch.delenv("META_TOKEN")
    http = _http(monkeypatch)
    for orden in (["listar"], ["historial"], ["destinatarios"], ["pausar", "999001", "--confirmo"]):
        c, _, err = _corre(rm, capsys, *orden, "--cliente", "acme")
        assert c == 2 and "Ads Manager" in err and "MCP" in err
    assert http.peticiones == []


# ---------------------------------------------------------------- pausar y reactivar

def _http_regla(monkeypatch, regla: dict) -> HttpSimulado:
    http = HttpSimulado()
    http.cuando("GET", r"/999001$", regla)
    http.cuando("POST", r"/999001$", {"success": True})
    return _http(monkeypatch, http)


def test_pausar_pide_confirmo_y_desactiva_sin_borrar(rm, capsys, instancia, monkeypatch):
    _cuenta_real(instancia)
    http = _http_regla(monkeypatch, {"id": "999001", "name": "PROTECT_OS_x", "status": "ENABLED",
                                     "account_id": "12345"})
    c, _, err = _corre(rm, capsys, "pausar", "999001", "--cliente", "acme")
    assert c == 1 and "--confirmo" in err and not http.de("POST", r".")
    c, out, _ = _corre(rm, capsys, "pausar", "999001", "--cliente", "acme", "--confirmo")
    assert c == 0 and http.de("POST", r"/999001$")[0]["form"]["status"] == "DISABLED"
    assert not [p for p in http.peticiones if p["metodo"] == "DELETE"]
    log = json.loads((instancia / "logs" / "cambios.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert log["accion"] == "desactivar_regla" and log["entidad_id"] == "999001"
    assert "ENABLED → DISABLED" in out


def test_pausar_rechaza_reglas_de_otra_cuenta(rm, capsys, instancia, monkeypatch):
    _cuenta_real(instancia)
    http = _http_regla(monkeypatch, {"id": "999001", "name": "ajena", "status": "ENABLED", "account_id": "67890"})
    c, _, err = _corre(rm, capsys, "pausar", "999001", "--cliente", "acme", "--confirmo")
    assert c == 1 and "no es de la cuenta" in err and not http.de("POST", r".")


def test_reactivar_solo_reglas_que_avisan_o_pausan(rm, capsys, instancia, monkeypatch):
    _cuenta_real(instancia)
    sube = _api("CHANGE_BUDGET", [_f("time_preset", "EQUAL", "LAST_7D")])
    http = _http_regla(monkeypatch, {"id": "999001", "status": "DISABLED", "account_id": "12345", **sube})
    c, _, err = _corre(rm, capsys, "reactivar", "999001", "--cliente", "acme", "--confirmo")
    assert c == 1 and "SUBE" in err and not http.de("POST", r".")
    avisa = _api("NOTIFICATION", [_f("time_preset", "EQUAL", "YESTERDAY"), _f("impressions", "LESS_THAN", 100)])
    http = _http_regla(monkeypatch, {"id": "999001", "status": "DISABLED", "account_id": "12345", **avisa})
    c, _, _ = _corre(rm, capsys, "reactivar", "999001", "--cliente", "acme", "--confirmo")
    assert c == 0 and http.de("POST", r"/999001$")[0]["form"]["status"] == "ENABLED"


# ---------------------------------------------------------------- leer

def test_listar_audita_las_reglas_existentes(rm, capsys, instancia, monkeypatch):
    _cuenta_real(instancia)
    buena = _api("NOTIFICATION", [_f("time_preset", "EQUAL", "YESTERDAY"), _f("impressions", "LESS_THAN", 100)],
                 id="999001", status="ENABLED")
    buena["name"] = "ALERT_OS_sin-entrega-ayer"
    veinte = _api("CHANGE_BUDGET", [_f("time_preset", "EQUAL", "LAST_3D"), _f("cost_per", "LESS_THAN", 4000)],
                  [_f("change_spec", "EQUAL", {"amount": 20, "unit": "PERCENTAGE"})], id="999002", status="ENABLED")
    veinte["name"] = "Escalar 20%"
    frecuencia = _api("NOTIFICATION", [_f("time_preset", "EQUAL", "LAST_7D"), _f("frequency", "GREATER_THAN", 3)],
                      id="999003", status="DISABLED", created_time="2025-06-01T09:00:00+0000")
    frecuencia["name"] = "Fatiga"
    # Meta devuelve los specs como texto JSON: el analizador tiene que entenderlos igual.
    for r in (buena, veinte, frecuencia):
        for k in ("evaluation_spec", "execution_spec", "schedule_spec"):
            r[k] = json.dumps(r[k])
    http = HttpSimulado().cuando("GET", r"/act_12345/adrules_library$", {"data": [buena, veinte, frecuencia]})
    _http(monkeypatch, http)
    c, out, _ = _corre(rm, capsys, "listar", "--cliente", "acme")
    assert c == 0 and "3, 2 activas" in out and "del OS" in out
    # la alerta de frecuencia solo avisa (KB 07 §4.A.5); pausar por frecuencia sí estaría prohibido (I6)
    assert out.count("PROHIBIDA:") == 1 and "SUBE presupuesto" in out and "M37" in out
    assert "1 reglas activas hacen algo que el OS no haría" in out
    assert "pausar <id>" in out
    c, out, _ = _corre(rm, capsys, "listar", "--cliente", "acme", "--json")
    datos = json.loads(out)
    assert datos["cpa_objetivo"] == 80
    assert next(x for x in datos["reglas"] if x["id"] == "999001")["problemas"] == []
    assert next(x for x in datos["reglas"] if x["id"] == "999002")["condiciones"] == ["coste por resultado < 40,00 EUR"]
    assert http.de("GET", r"adrules_library")[0]["query"]["fields"].startswith("id,name,status")


def test_listar_cuenta_sin_reglas(rm, capsys, instancia, monkeypatch):
    _cuenta_real(instancia)
    _http(monkeypatch, HttpSimulado().cuando("GET", r"/act_12345/adrules_library$", {"data": []}))
    c, out, _ = _corre(rm, capsys, "listar", "--cliente", "acme")
    assert c == 0 and "no tiene reglas" in out and "proponer" in out


def test_historial_lee_y_corta_por_fecha(rm, capsys, instancia, monkeypatch):
    _cuenta_real(instancia)
    ahora = rm.datetime.now(rm.timezone.utc)
    reciente = (ahora - rm.timedelta(hours=5)).strftime("%Y-%m-%dT%H:%M:%S+0000")
    viejo = (ahora - rm.timedelta(days=20)).strftime("%Y-%m-%dT%H:%M:%S+0000")
    http = HttpSimulado()
    http.cuando("GET", r"/act_12345/adrules_library$", {"data": [{"id": "999001", "name": "PROTECT_OS_x"}]})
    http.cuando("GET", r"/act_12345/adrules_history$", {"data": [
        {"rule_id": "999001", "timestamp": reciente,
         "results": [{"object_id": "444001", "object_type": "ADSET", "actions": [{"action": "PAUSE"}]}]},
        {"rule_id": "999001", "timestamp": viejo, "results": [{"object_id": "444002", "actions": []}]}]})
    _http(monkeypatch, http)
    c, out, _ = _corre(rm, capsys, "historial", "--cliente", "acme", "--json")
    datos = json.loads(out)
    assert c == 0 and len(datos["acciones"]) == 1
    accion = datos["acciones"][0]
    assert (accion["regla"], accion["objeto"], accion["nivel"], accion["acciones"]) == (
        "PROTECT_OS_x", "444001", "ADSET", ["PAUSE"])
    assert http.de("GET", r"adrules_history")[0]["query"]["hide_no_changes"] == "true"


def test_historial_todas_incluye_avisos_y_salta_evaluaciones_vacias(rm, capsys, instancia, monkeypatch):
    _cuenta_real(instancia)
    hace = (rm.datetime.now(rm.timezone.utc) - rm.timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S+0000")
    http = HttpSimulado()
    http.cuando("GET", r"/act_12345/adrules_library$", {"data": []})
    http.cuando("GET", r"/act_12345/adrules_history$", {"data": [
        {"rule_id": "999001", "timestamp": hace, "results": []},
        {"rule_id": "999001", "timestamp": hace, "results": [{"object_id": "444001", "object_type": "AD",
                                                              "actions": [{"action": "NOTIFICATION"}]}]}]})
    _http(monkeypatch, http)
    c, out, _ = _corre(rm, capsys, "historial", "--cliente", "acme", "--todas", "--json")
    assert c == 0 and [x["objeto"] for x in json.loads(out)["acciones"]] == ["444001"]
    assert http.de("GET", r"adrules_history")[0]["query"]["hide_no_changes"] == "false"


def test_destinatarios(rm, capsys, instancia, monkeypatch):
    _cuenta_real(instancia)
    _http(monkeypatch, HttpSimulado().cuando("GET", r"/act_12345/users$", {"data": [{"id": "777777", "name": "Ana"}]}))
    c, out, _ = _corre(rm, capsys, "destinatarios", "--cliente", "acme", "--json")
    assert c == 0 and json.loads(out) == [{"id": "777777", "nombre": "Ana"}]


# ---------------------------------------------------------------- I6: revisión de corrección

@pytest.mark.parametrize("celda, valor", [("1 200 €", 1200), ("1 200 €", 1200), ("12 500", 12500), ("1,200", 1200),
                                          ("1,200.50", 1200.5), ("$1,500", 1500)])
def test_numero_con_miles_de_cualquier_formato(rm, celda, valor):
    """Hallazgo 4: antes 1, 1, 12, 1,2, 1,2 y 1,5 (reglas que pausaban a 3 € de gasto)."""
    assert rm.numero(celda) == valor


def test_proponer_ensena_la_celda_y_avisa_si_el_cpa_es_absurdo(rm, capsys, instancia):
    _economia(instancia, target="1 200 €")
    datos, _ = _propuesta(rm, capsys, instancia)
    assert datos["cpa_objetivo"] == 1200 and "«1 200 €»" in datos["cpa_origen"]
    _economia(instancia, target="1 €")
    datos, _ = _propuesta(rm, capsys, instancia)
    assert any("«1 €»" in a and "tope" in a for a in datos["avisos"])


def test_cuenta_pequena_por_defecto_kill_a_4x_solo_por_anuncio(rm, capsys, instancia):
    """Hallazgo 9: KB 07, implicaciones operativas: con <30 conversiones/semana por campaña, solo alertas + kill
    switch lifetime ≥4×C a nivel de anuncio con impressions > 2.000 (§4.B.1). El conjunto entero solo avisa."""
    datos, _ = _propuesta(rm, capsys, instancia, "--activo", "--avisar", "777777")
    assert datos["multiplicador"] == 4 and datos["cuenta_pequena"] is True
    kill = _regla(datos, "anuncio-sin-conversion")
    assert kill["accion"] == "PAUSE" and _filtro(kill, "lifetime_spent - today_spent")["value"] == 32000
    assert _filtro(kill, "impressions") == {"field": "impressions", "value": 2000, "operator": "GREATER_THAN"}
    conjunto = _regla(datos, "conjunto-sin-conversion")
    assert conjunto["tipo"] == "ALERT" and conjunto["accion"] == "NOTIFICATION"
    assert conjunto["api"]["name"] == "ALERT_OS_conjunto-sin-conversion_4x80EUR"
    assert any("--conversiones-semana" in a for a in datos["avisos"])
    # Con volumen (≥30/semana) vuelve el conjunto por defecto de antes: 3× y pausa también el conjunto.
    datos, _ = _propuesta(rm, capsys, instancia, "--activo", "--conversiones-semana", "45")
    assert datos["multiplicador"] == 3 and datos["cuenta_pequena"] is False
    assert _regla(datos, "conjunto-sin-conversion")["accion"] == "PAUSE"
    # --multiplicador manda sobre el valor por defecto
    datos, _ = _propuesta(rm, capsys, instancia, "--multiplicador", "5")
    assert datos["multiplicador"] == 5


def _regla_meta(rid, nombre, campanas=None, status="ENABLED"):
    filtros = [{"field": "entity_type", "value": "ADSET", "operator": "EQUAL"}]
    if campanas:
        filtros.append({"field": "campaign.id", "value": campanas, "operator": "IN"})
    return {"id": rid, "name": nombre, "status": status,
            "evaluation_spec": {"evaluation_type": "SCHEDULE", "filters": filtros}}


def test_crear_detecta_reglas_os_antiguas_con_otros_parametros(rm, capsys, instancia, monkeypatch):
    """Hallazgo 5: tras subir el tope y cambiar el CPA, las reglas viejas seguían ENABLED y pausaban a 0,8× el CPA."""
    _cuenta_real(instancia)
    _, ruta = _propuesta(rm, capsys, instancia, "--avisar", "777777", "--activo")
    viejas = [_regla_meta("777001", "PROTECT_OS_gasto-hoy-fuera-de-tope_2,2x50EUR"),
              _regla_meta("777002", "PROTECT_OS_conjunto-sin-conversion_3x40EUR"),
              _regla_meta("777003", "ALERT_OS_sin-conversiones-7d_3x40EUR", campanas=[111]),
              _regla_meta("777004", "ALERT_OS_gasto-hoy-alto_1,75x50EUR", status="DISABLED"),
              _regla_meta("777005", "PROTECT_OS_anuncio-sin-conversion_3x40EUR", campanas=[999])]
    _http_meta(monkeypatch, existentes=viejas)
    http = urllib.request.urlopen
    c, _, err = _corre(rm, capsys, "crear", ruta, "--cliente", "acme", "--confirmo")
    assert c == 1 and not http.de("POST", r".")
    assert "pausar 777001 777002 777003 777005 --cliente acme --confirmo" in err
    assert "777004" not in err  # desactivada: no estorba


def test_crear_ignora_reglas_os_de_otras_campanas(rm, capsys, instancia, monkeypatch):
    _cuenta_real(instancia)
    _, ruta = _propuesta(rm, capsys, instancia, "--avisar", "777777", "--activo", "--campanas", "555555")
    _http_meta(monkeypatch, existentes=[_regla_meta("777005", "PROTECT_OS_anuncio-sin-conversion_3x40EUR",
                                                    campanas=[999])])
    c, _, err = _corre(rm, capsys, "crear", ruta, "--cliente", "acme", "--confirmo")
    assert c == 0, err


def test_pasos_sin_token_comprueban_antes_los_presupuestos(rm, capsys, instancia, monkeypatch):
    """Hallazgo 21: por la ruta sin token, la regla de gasto se guiaba sin mirar los presupuestos activos."""
    datos, ruta = _propuesta(rm, capsys, instancia)
    pasos = _regla(datos, "gasto-hoy-fuera-de-tope")["ads_manager"]
    assert pasos[0].startswith("Antes de crearla") and "100,00 EUR" in pasos[0]
    monkeypatch.delenv("META_TOKEN")
    c, out, _ = _corre(rm, capsys, "crear", ruta, "--cliente", "acme", "--simular", "--pasos")
    assert c == 0 and "presupuestos activos" in out


def test_alerta_de_frecuencia_avisa_y_la_pausa_bloquea(rm):
    """Bajo: KB 07 §4.A.5 recomienda la alerta de frecuencia en prospección; lo que es folklore es pausar por ella."""
    filtros = [_f("time_preset", "EQUAL", "LAST_7D"), _f("frequency", "GREATER_THAN", 4)]
    assert not _graves(rm, _api("NOTIFICATION", filtros))
    assert any("M37" in t for g, t in rm.analizar(_api("NOTIFICATION", filtros), 8000) if g == "aviso")
    assert any("M37" in t for t in _graves(rm, _api("PAUSE", filtros)))
