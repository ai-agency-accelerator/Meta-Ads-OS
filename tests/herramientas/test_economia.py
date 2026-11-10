import json
import math
from types import SimpleNamespace

import pytest

import economia
from economia import Funnel, Oferta

# Los tres ejemplos de la antigua calculadora de la KB (05-leadgen-high-ticket-crm/calculadora_funnel.py) con sus
# resultados: la integración en economia.py tiene que dar exactamente lo mismo.
EJEMPLOS = [
    (Oferta("Curso", precio=2000, iva=0.21, pct_pago_unico=0.6, n_cuotas=4, recargo_cuotas=0.10, impago_cuotas=0.15,
            tasa_reembolso=0.08, pasarela=0.03, coste_entrega=0.10, comision_closer=0.10, comision_setter=0.05),
     Funnel(0.4, 0.5, 0.60, 0.15), 10000, 15, (1070.2312, 19.2642, 2842.7739)),
    (Oferta("Servicio B2B", precio=5000, tasa_reembolso=0.02, pasarela=0.01, coste_entrega=0.50, comision_closer=0.10),
     Funnel(0.4, 0.5, 0.75, 0.25), 10000, 40, (1910.0, 71.625, 7906.25)),
    (Oferta("Coaching", precio=10000, iva=0.21, pct_pago_unico=0.5, n_cuotas=6, recargo_cuotas=0.10,
            impago_cuotas=0.20, tasa_reembolso=0.05, pasarela=0.03, coste_entrega=0.20, comision_closer=0.10,
            comision_setter=0.05),
     Funnel(0.40, 0.70, 0.65, 0.20), 20000, 60, (4603.168, 167.5553, 35851.7723)),
]


@pytest.mark.parametrize("o,f,inv,cpl,esperado", EJEMPLOS)
def test_paridad_con_la_calculadora_de_la_kb(o, f, inv, cpl, esperado):
    contrib, be_cpl, beneficio = esperado
    assert economia.cash_por_venta(o)["contribucion_por_venta"] == pytest.approx(contrib, abs=1e-4)
    be = economia.break_evens(o, f, 0.5)
    assert be["BE_CPL"] == pytest.approx(be_cpl, abs=1e-4)
    assert be["TARGET_CPL"] == pytest.approx(be_cpl / 2, abs=1e-4)
    assert economia.simular(o, f, inv, cpl)["beneficio_tras_ads"] == pytest.approx(beneficio, abs=1e-4)


def test_sensibilidad():
    o, f = EJEMPLOS[1][0], EJEMPLOS[1][1]
    s = economia.sensibilidad_be_cpl(o, f)
    assert list(s) == ["show 50%", "show 60%", "show 70%", "show 80%"]
    assert s["show 50%"]["cierre 20%"] == round(1910 * 0.5 * 0.2 * 0.5 * 0.4, 2)


def _json(argv, capsys):
    assert economia.main(argv) == 0
    return json.loads(capsys.readouterr().out)


def test_leadgen_cli_y_json_en_cualquier_posicion(capsys):
    args = ["--precio", "5000", "--reembolsos", "0.02", "--pasarela-pct", "0.01", "--entrega-pct", "0.5",
            "--closer-pct", "0.1", "--cualif", "0.4", "--agenda", "0.5", "--show", "0.75", "--cierre", "0.25",
            "--inversion", "10000", "--cpl", "40"]
    d1 = _json(["leadgen", *args, "--json"], capsys)
    d2 = _json(["--json", "leadgen", *args], capsys)
    assert d1 == d2
    assert d1["cash por venta"]["contribucion_por_venta"] == 1910.0
    assert d1["break-even y target (margen objetivo 50%)"]["BE_CPL"] == 71.62
    assert d1["simulación: inversión 10,000 a CPL 40"]["beneficio_tras_ads"] == 7906.25
    assert economia.main(["leadgen", *args]) == 0
    assert "== leadgen (importes en €)" in capsys.readouterr().out


def test_ecommerce(capsys):
    d = _json(["ecommerce", "--aov", "60", "--cogs-pct", "0.3", "--fee-pais", "0.03", "--cpa", "40", "--json"], capsys)
    neto = 60 / 1.21
    cm1 = neto - neto * 0.3 - 60 * 0.02
    assert d["pedido"]["contribución por pedido (CM1)"] == round(cm1, 2)
    assert d["break-even (primera compra)"]["CPA break-even (incluye fee país)"] == round(cm1 / 1.03, 2)
    assert d["break-even (primera compra)"]["ROAS break-even en Ads Manager"] == round(60 / (cm1 / 1.03), 2)
    assert d["con tu CPA actual"]["¿rentable en primera compra?"] == "no"
    d = _json(["ecommerce", "--aov", "60", "--cogs-pct", "0.99", "--json"], capsys)
    assert "aviso" in d and d["break-even (primera compra)"]["ROAS break-even en Ads Manager"] is None


def test_suscripcion(capsys):
    d = _json(["suscripcion", "--precio-mes", "121", "--churn", "0.1", "--trial-a-pago", "0.5", "--json"], capsys)
    assert d["suscriptor"]["LTV en contribución"] == 800.0
    pay = d["CAC máximo con payback ≤ 6 meses"]
    assert pay["por suscriptor de pago"] == round(800 * (1 - 0.9 ** 6), 2)
    assert pay["por prueba / alta (× conversión prueba→pago)"] == round(800 * (1 - 0.9 ** 6) * 0.5, 2)


@pytest.mark.parametrize("texto,esperado", [("30-45", (30, 37.5, 45)), ("45-30", (30, 37.5, 45)), ("40", (40, 40, 40)),
                                            ("0,3-0,5", (0.3, 0.4, 0.5))])
def test_rango(texto, esperado):
    assert economia.rango(texto, "x") == pytest.approx(esperado)


@pytest.mark.parametrize("texto,tasa", [("abc", False), ("0", False), ("40", True), ("0-0.5", True), (None, False)])
def test_rango_errores(texto, tasa):
    with pytest.raises(economia.ErrorUsuario):
        economia.rango(texto, "x", tasa=tasa)


def test_poisson_cuantil():
    assert economia.poisson_cuantil(0, 0.9) == 0
    assert economia.poisson_cuantil(2.0, 0.10) == 0 and economia.poisson_cuantil(2.0, 0.90) == 4
    assert economia.poisson_cuantil(100, 0.10) < 100 < economia.poisson_cuantil(100, 0.90)


def _prev(**kw):
    base = dict(modo="prevision", modelo="servicios", inversion="1000,4000", inversion_ref=None, cpl="40", cpa=None,
                curva="0.7", fee_pais=0.0, cualif="0.5", agenda="0.5", show="0.8", cierre="0.25",
                contribucion_venta=3000.0, precio=None, activacion=None, pago=None, precio_mes=None, margen=0.8,
                churn=None, contribucion_pedido=None, iva=0.0)
    base.update(kw)
    return economia.prevision(SimpleNamespace(**base))


def test_prevision_servicios_con_curva_fija():
    r = _prev()
    e1, e4 = r["escenarios"]
    assert e1["inversion"] == 1000 and e1["leads"]["base"] == 25 and e1["ventas"]["base"] == 1.25
    assert e1["cac"]["base"] == 800 and e1["coste_por_cita"]["base"] == 160
    c4 = 40 * 4 ** 0.3  # conversiones ∝ gasto^0,7 → el CPL sube con (I/ref)^(1−b)
    assert e4["coste_por_lead"]["base"] == round(c4, 2) and e4["leads"]["base"] == round(4000 / c4, 2)
    assert e4["beneficio_tras_ads"]["base"] == round(4000 / c4 * 0.05 * 3000 - 4000, 2)
    lam = 4000 / c4 * 0.05
    assert e4["ruido_ventas"]["prob_cero"] == round(math.exp(-lam), 4)
    assert e4["ruido_ventas"]["p10"] <= lam <= e4["ruido_ventas"]["p90"]
    assert r["supuestos"]["origen_curva"] == "--curva" and r["supuestos"]["valor_por_venta"] == 3000
    assert any("casi azar" in a for a in r["avisos"])  # 1,25 ventas esperadas a 1.000


def test_prevision_bandas_ordenadas_y_extrapolacion():
    r = _prev(inversion="500,1000,6000", inversion_ref="1000", cpl="30-50", curva=None, cualif="0.4-0.6",
              cierre="0.2-0.3")
    for e in r["escenarios"]:
        assert e["ventas"]["pesimista"] < e["ventas"]["base"] < e["ventas"]["optimista"]
        assert e["cac"]["pesimista"] > e["cac"]["base"] > e["cac"]["optimista"]
    abajo, ref, arriba = r["escenarios"]
    assert ref["coste_por_lead"] == {"pesimista": 50, "base": 40, "optimista": 30}
    # por debajo de la referencia el caso pesimista usa b=0,8 (abarata menos); por encima, b=0,6 (encarece más)
    assert abajo["coste_por_lead"]["pesimista"] == round(50 * 0.5 ** 0.2, 2)
    assert arriba["coste_por_lead"]["pesimista"] == round(50 * 6 ** 0.4, 2)
    assert r["supuestos"]["curva_b"] == {"pesimista": 0.6, "base": 0.7, "optimista": 0.8}
    assert "06-framework-escalado.md" in r["supuestos"]["origen_curva"]
    assert any("más de 3×" in a for a in r["avisos"])


def test_prevision_contribucion_desde_la_oferta():
    r = _prev(contribucion_venta=None, precio=5000.0, pct_pago_unico=1.0, descuento_pago_unico=0.0, cuotas=1,
              recargo_cuotas=0.0, impago_cuotas=0.0, reembolsos=0.02, pasarela_pct=0.01, entrega_pct=0.5,
              closer_pct=0.1, setter_pct=0.0, coste_fijo=0.0, nombre="Oferta")
    assert r["supuestos"]["valor_por_venta"] == 1910.0
    r = _prev(contribucion_venta=None)
    assert "beneficio_tras_ads" not in r["escenarios"][0] and any("--precio" in a for a in r["avisos"])


def test_prevision_saas():
    r = _prev(modelo="saas", inversion="2000", cpl="20", activacion="0.5", pago="0.2", precio_mes=100.0, churn=0.05)
    e = r["escenarios"][0]
    assert e["registros"]["base"] == 100 and e["activados"]["base"] == 50 and e["clientes_pago"]["base"] == 10
    assert e["cac"]["base"] == 200 and e["mrr_nuevo"]["base"] == 1000
    assert e["payback_meses"]["base"] == 2.6  # 80 + 76 + 72,2… con churn del 5 %
    assert e["contribucion_ltv"]["base"] == 16000 and e["beneficio_ltv_tras_ads"]["base"] == 14000
    assert "ruido_clientes_pago" in e


def test_prevision_ecommerce_con_fee():
    r = _prev(modelo="ecommerce", inversion="3000", cpa="30", contribucion_pedido=45.0, fee_pais=0.03)
    e = r["escenarios"][0]
    assert e["ventas"]["base"] == 100 and e["coste_total_con_fee"] == 3090
    assert e["beneficio_tras_ads"]["base"] == 100 * 45 - 3090


def test_prevision_cli_texto(capsys):
    assert economia.main(["prevision", "--inversion", "3000,6000", "--cpl", "30-45", "--cualif", "0.5",
                          "--cierre", "0.2", "--contribucion-venta", "2500"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("== previsión (servicios)") and "| Métrica | 3.000 € | 6.000 € |" in out
    assert "rango del 80 % por azar" in out and "Supuestos:" in out


def test_cliente_da_moneda_y_modelo(instancia, capsys):
    ficha = instancia / "clientes" / "acme" / "ficha.md"
    ficha.write_text(ficha.read_text(encoding="utf-8").replace("moneda: EUR", "moneda: USD")
                     .replace("tipo: servicios-high-ticket", "tipo: saas"), encoding="utf-8")
    assert economia.main(["prevision", "--cliente", "acme", "--inversion", "2000", "--cpl", "20",
                          "--activacion", "0.5", "--pago", "0.2"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("== previsión (saas)") and "2.000 $" in out
    assert economia.main(["--cliente", "acme", "suscripcion", "--precio-mes", "50", "--churn", "0.1"]) == 0
    assert "(importes en $)" in capsys.readouterr().out
    assert economia.main(["prevision", "--cliente", "nadie", "--inversion", "1000", "--cpl", "20"]) == 2


@pytest.mark.parametrize("argv", [
    ["leadgen", "--precio", "5000", "--show", "75"],
    ["leadgen", "--precio", "-1"],
    ["suscripcion", "--precio-mes", "50", "--churn", "5"],
    ["prevision", "--inversion", "1000", "--cpl", "40"],  # servicios sin --cierre
    ["prevision", "--modelo", "saas", "--inversion", "1000", "--cpl", "40"],
    ["prevision", "--modelo", "ecommerce", "--inversion", "1000"],
    ["prevision", "--inversion", "mil", "--cpl", "40", "--cierre", "0.2"],
    ["prevision", "--inversion", "1000", "--cpl", "40", "--cierre", "20"],
])
def test_errores_de_usuario_salen_con_1(argv, capsys):
    assert economia.main(argv) == 1
    assert capsys.readouterr().err.startswith("Error:")


def test_argumentos_mal_escritos_salen_con_1():
    with pytest.raises(SystemExit) as e:
        economia.main(["leadgen"])  # falta --precio
    assert e.value.code == 1


def test_tasas_con_tres_decimales_y_punto():
    """«0.175» es una tasa (0,175), no 175: un 0 delante nunca es separador de miles."""
    import economia
    from registro_creativo import num_humano

    assert num_humano("0.175") == 0.175 and num_humano("0,175") == 0.175
    assert num_humano("1.200") == 1200 and num_humano("12.500,5") == 12500.5
    assert economia.rango("0.175", "cierre", tasa=True) == (0.175, 0.175, 0.175)
    lo, _, hi = economia.rango("0.125-0.175", "cierre", tasa=True)
    assert (lo, hi) == (0.125, 0.175)


# ---------------------------------------------------------------- I6: revisión de corrección
# I8: la pasarela ya no es 3 % por defecto en leadgen (es 0 con aviso); estos casos la fijan para mantener las cifras.
LEADGEN = ["leadgen", "--precio", "5000", "--cualif", "0.5", "--agenda", "0.6", "--show", "0.7", "--cierre", "0.25",
           "--pasarela-pct", "0.03"]


def _be(d):
    return next(v for k, v in d.items() if k.startswith("break-even y target"))


def test_leadgen_con_fee_pais(capsys):
    """Hallazgo 14: el break-even de servicios descuenta la tasa por ubicación (ES 3 %), como ecommerce."""
    sin = _be(_json([*LEADGEN, "--json"], capsys))
    assert (sin["BE_CPL"], sin["TARGET_CPL"]) == (254.62, 127.31)
    d = _json([*LEADGEN, "--fee-pais", "0.03", "--inversion", "10000", "--cpl", "100", "--json"], capsys)
    con = _be(d)
    assert (con["BE_CPL"], con["TARGET_CPL"]) == (247.21, 123.6)
    assert con["BE_CPA"] == round(sin["BE_CPA"] / 1.03, 2)
    sim = next(v for k, v in d.items() if k.startswith("simulación"))
    assert sim["coste_total_con_fee"] == 10300
    assert sim["beneficio_tras_ads"] == round(sim["contribucion_total"] - 10300, 2)
    tabla = next(v for k, v in d.items() if k.startswith("sensibilidad"))
    assert tabla["show 70%"]["cierre 25%"] == 247.21


def test_argumentos_con_coma_decimal_y_miles(capsys):
    """Bajo: «--cierre 0,25» y «--precio 5.000» se leen como en el resto de herramientas (_comun.numero)."""
    coma = ["leadgen", "--precio", "5.000", "--cualif", "0,5", "--agenda", "0,6", "--show", "0,7", "--cierre", "0,25",
            "--fee-pais", "0,03", "--pasarela-pct", "0,03", "--json"]
    assert _be(_json(coma, capsys))["BE_CPL"] == 247.21
    with pytest.raises(SystemExit) as e:
        economia.main(["leadgen", "--precio", "cinco mil"])
    assert e.value.code == 1 and "no es un número" in capsys.readouterr().err


def test_iva_por_defecto_avisa(capsys):
    """Bajo: suscripcion supone IVA 21 % y prevision saas 0 %; si no se pasa --iva, se dice."""
    d = _json(["suscripcion", "--precio-mes", "121", "--churn", "0.1", "--json"], capsys)
    assert "IVA" in d.get("aviso", "") and d["suscriptor"]["precio mensual neto"] == 100.0
    d = _json(["suscripcion", "--precio-mes", "121", "--churn", "0.1", "--iva", "0", "--json"], capsys)
    assert "aviso" not in d
    d = _json(["prevision", "--modelo", "saas", "--inversion", "2000", "--cpl", "20", "--activacion", "0.5",
               "--pago", "0.2", "--precio-mes", "100", "--churn", "0.05", "--json"], capsys)
    assert any("IVA" in a for a in d["avisos"])


# ---------------------------------------------------------------- I8: supuestos visibles, pasarela y fee por mercado
LEADGEN_SIN_PASARELA = LEADGEN[:-2]


def _ficha(instancia, **campos):
    ficha = instancia / "clientes" / "acme" / "ficha.md"
    texto = ficha.read_text(encoding="utf-8")
    for clave, valor in campos.items():
        if f"\n{clave}:" in texto:
            texto = "\n".join(f"{clave}: {valor}" if l.startswith(f"{clave}:") else l for l in texto.split("\n"))
        else:
            texto = texto.replace("\nmoneda:", f"\n{clave}: {valor}\nmoneda:", 1)
    ficha.write_text(texto, encoding="utf-8")


def test_leadgen_pasarela_por_defecto_0_visible_y_con_aviso(capsys):
    d = _json([*LEADGEN_SIN_PASARELA, "--json"], capsys)
    assert d["supuestos"]["pasarela"]["valor"] == 0.0 and "por defecto" in d["supuestos"]["pasarela"]["origen"]
    assert "--pasarela-pct" in d["aviso"] and d["cash por venta"]["pasarela"] == 0.0
    assert _be(d)["BE_CPL"] == 262.5  # 5000 × 0,5 × 0,6 × 0,7 × 0,25 de lead a venta, sin pasarela
    d = _json([*LEADGEN, "--json"], capsys)
    assert d["supuestos"]["pasarela"] == {"valor": 0.03, "origen": "--pasarela-pct"} and "aviso" not in d
    assert economia.main(LEADGEN_SIN_PASARELA) == 0
    out = capsys.readouterr().out
    assert "   pasarela 0 % · por defecto" in out and "--pasarela-pct" in out
    assert "   IVA 0 % · por defecto (venta B2B" in out and "   fee país 0 % · por defecto, sin --cliente" in out


def test_ecommerce_y_suscripcion_muestran_sus_supuestos(capsys):
    d = _json(["ecommerce", "--aov", "60", "--json"], capsys)
    assert d["supuestos"]["pasarela"]["valor"] == 0.02 and d["supuestos"]["IVA"]["valor"] == 0.21
    assert "por defecto" in d["supuestos"]["IVA"]["origen"] and "aviso" not in d
    d = _json(["ecommerce", "--aov", "60", "--iva", "0", "--pasarela-pct", "0.015", "--json"], capsys)
    assert d["supuestos"]["IVA"] == {"valor": 0, "origen": "--iva"}
    assert d["supuestos"]["pasarela"] == {"valor": 0.015, "origen": "--pasarela-pct"}
    d = _json(["suscripcion", "--precio-mes", "50", "--churn", "0.1", "--json"], capsys)
    assert "pasarela" not in d["supuestos"] and d["supuestos"]["fee país"]["valor"] == 0.0


@pytest.mark.parametrize("mercados,fee", [("ES", 0.03), ("FR", 0.03), ("IT", 0.03), ("UK", 0.02), ("GB", 0.02),
                                          ("AT", 0.05), ("TR", 0.05), ("MX", 0.0), ("es", 0.03)])
def test_fee_por_mercado(mercados, fee):
    assert economia.fee_por_mercados(mercados)[0] == fee


def test_fee_por_varios_mercados_y_codigos_malos():
    fee, origen, avisos = economia.fee_por_mercados("ES, UK")
    assert fee == 0.03 and "ES 3 %" in origen and "UK 2 %" in origen and "la mayor" in avisos[0]
    fee, _, avisos = economia.fee_por_mercados("ES,FR,IT")
    assert fee == 0.03 and avisos == []
    fee, _, avisos = economia.fee_por_mercados("España")
    assert fee == 0.0 and "no es un código ISO" in avisos[0]
    assert economia.fee_por_mercados("")[0] == 0.0 and "no tiene `mercados`" in economia.fee_por_mercados(None)[1]


def test_cliente_aplica_el_fee_de_sus_mercados(instancia, capsys):
    """Con --cliente, el fee sale de `mercados` de la ficha; --fee-pais manda sobre la ficha."""
    d = _json([*LEADGEN, "--cliente", "acme", "--json"], capsys)
    assert d["supuestos"]["fee país"]["valor"] == 0.0 and "no tiene `mercados`" in d["supuestos"]["fee país"]["origen"]
    _ficha(instancia, mercados="ES  # opcional: códigos ISO")
    d = _json([*LEADGEN, "--cliente", "acme", "--json"], capsys)
    assert d["supuestos"]["fee país"]["valor"] == 0.03 and (_be(d)["BE_CPL"], _be(d)["TARGET_CPL"]) == (247.21, 123.6)
    d = _json([*LEADGEN, "--cliente", "acme", "--fee-pais", "0", "--json"], capsys)
    assert d["supuestos"]["fee país"] == {"valor": 0, "origen": "--fee-pais"} and _be(d)["BE_CPL"] == 254.62
    _ficha(instancia, mercados="AT, ES")
    d = _json(["ecommerce", "--aov", "60", "--cliente", "acme", "--json"], capsys)
    assert d["supuestos"]["fee país"]["valor"] == 0.05 and "la mayor" in d["aviso"]
    d = _json(["prevision", "--cliente", "acme", "--modelo", "servicios", "--inversion", "3000", "--cpl", "40",
               "--cierre", "0.2", "--precio", "5000", "--json"], capsys)
    assert d["supuestos"]["fee_pais"] == 0.05 and d["escenarios"][0]["coste_total_con_fee"] == 3150
    assert d["supuestos"]["fijados"]["pasarela"]["valor"] == 0.0 and any("Pasarela" in a for a in d["avisos"])


def test_cliente_con_stripe_pone_pasarela_3(instancia, capsys):
    _ficha(instancia, stripe="true")
    d = _json([*LEADGEN_SIN_PASARELA, "--cliente", "acme", "--json"], capsys)
    assert d["supuestos"]["pasarela"]["valor"] == 0.03 and "stripe: true" in d["supuestos"]["pasarela"]["origen"]
    assert _be(d)["BE_CPL"] == 254.62 and "Pasarela" not in d.get("aviso", "")
    d = _json(["ecommerce", "--aov", "60", "--cliente", "acme", "--json"], capsys)
    assert d["supuestos"]["pasarela"]["valor"] == 0.02  # en ecommerce, Stripe o no, el 2 % de siempre


def test_prevision_texto_muestra_los_supuestos(capsys):
    assert economia.main(["prevision", "--inversion", "3000", "--cpl", "40", "--cierre", "0.2", "--precio", "5000",
                          "--fee-pais", "0.03"]) == 0
    out = capsys.readouterr().out
    assert "Supuesto: pasarela 0 % · por defecto" in out and "Supuesto: fee país 3 % · --fee-pais" in out
    assert "Aviso: Pasarela al 0 %" in out
    assert economia.main(["prevision", "--inversion", "3000", "--cpl", "40", "--cierre", "0.2",
                          "--contribucion-venta", "2500"]) == 0
    assert "Supuesto: pasarela" not in capsys.readouterr().out  # con la contribución dada, la pasarela no interviene
