import csv
import json
from datetime import date

import pytest

import embudo

HOY = date(2026, 11, 20)
A, B = "120000000000001", "120000000000002"
NOMBRE_A, NOMBRE_B = "20261001_a_b_ugc_h1", "20261001_c_d_demo_h1"


def _csv(ruta, cols, filas):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8", newline="") as h:
        w = csv.writer(h)
        w.writerow(cols)
        w.writerows(filas)
    return ruta


@pytest.fixture
def datos(instancia, tmp_path):
    privado = instancia / "clientes" / "acme" / "privado"
    leads = _csv(privado / "leads_2026-10.csv",
                 ["fecha", "email", "telefono", "ad_id", "utm_content", "cualificado", "cita", "show", "venta",
                  "cash", "fecha_cash"],
                 [["2026-10-05T09:00:00.000Z", "ana@ejemplo.com", "+34600000001", A, NOMBRE_A, "sí", "2026-10-08",
                   "1", "2026-10-15", "3000", "2026-10-15"],
                  ["2026-10-06", "b@ejemplo.com", "", A, NOMBRE_A, "1", "1", "0", "0", "", ""],
                  ["2026-10-07", "c@ejemplo.com", "", B, NOMBRE_B, "no", "", "", "", "", ""],
                  ["11/10/2026", "d@ejemplo.com", "", "", "", "", "", "", "", "", ""],
                  ["2026-10-13", "e@ejemplo.com", "", "", NOMBRE_A, "1", "1", "1", "1", "2000", "2026-12-01"],
                  ["2026-10-14", "f@ejemplo.com", "", B, "", "0", "0", "0", "0", "", ""],
                  ["2026-10-15", "g@ejemplo.com", "", B, "", "1", "", "", "", "", ""],
                  ["2026-11-10", "h@ejemplo.com", "", A, "", "", "", "", "", "", ""],
                  ["sin fecha", "i@ejemplo.com", "", A, "", "", "", "", "", "", ""]])
    meta = _csv(tmp_path / "meta_dia.csv", ["anuncio", "anuncio_id", "gasto_eur", "desde", "hasta"],
                [[NOMBRE_A, A, 500, "2026-10-05", "2026-10-05"], [NOMBRE_A, A, 200, "2026-10-07", "2026-10-07"],
                 [NOMBRE_B, B, 300, "2026-10-06", "2026-10-06"], [NOMBRE_A, A, 600, "2026-10-13", "2026-10-13"],
                 [NOMBRE_B, B, 400, "2026-10-14", "2026-10-14"], [NOMBRE_A, A, 100, "2026-11-10", "2026-11-10"]])
    return instancia, leads, meta


def test_cohortes_por_semana(datos):
    _, leads, meta = datos
    r = embudo.cohortes("acme", "semana", str(leads), str(meta), hoy=HOY)
    s = {f["lunes"]: f for f in r["cohortes"]}
    assert list(s) == ["2026-10-05", "2026-10-12", "2026-11-09"]
    w1, w2, w3 = s["2026-10-05"], s["2026-10-12"], s["2026-11-09"]
    assert w1["semana"] == "2026-W41" and w1["madura"] is True and w3["madura"] is False
    assert (w1["leads"], w1["cualificados"], w1["citas"], w1["shows"], w1["ventas"]) == (4, 2, 2, 1, 1)  # 11/10/2026 es domingo de la W41
    assert (w1["gasto"], w1["cpl"], w1["coste_venta"], w1["cash_30d"], w1["cash_total"]) == (1000, 250, 1000, 3000, 3000)
    assert (w2["leads"], w2["ventas"], w2["cash_30d"], w2["cash_60d"], w2["cash_90d"]) == (3, 1, 0, 2000, 2000)
    assert w2["gasto"] == 1000 and w3["gasto"] == 100
    assert r["total"]["leads"] == 8 and r["total"]["gasto"] == 2100
    assert any("sin fecha de creación" in a for a in r["avisos"])
    assert any("1 de 8 leads no tienen anuncio" in a for a in r["avisos"])
    assert any("2026-W46" in a and "inmaduras" in a for a in r["avisos"])


def test_cohortes_por_anuncio_y_union_por_nombre(datos):
    _, leads, meta = datos
    r = embudo.cohortes("acme", "anuncio", str(leads), str(meta), hoy=HOY)
    filas = {f["ad_id"] or f["anuncio"]: f for f in r["cohortes"]}
    a = filas[A]
    assert a["anuncio"] == NOMBRE_A and a["leads"] == 4 and a["ventas"] == 2  # incluye el lead que solo traía utm_content
    assert a["gasto"] == 1400 and a["coste_venta"] == 700 and a["pct_maduros"] == 75.0
    assert filas[B]["leads"] == 3 and filas[B]["gasto"] == 700
    assert filas["(sin anuncio)"]["gasto"] is None
    assert [f["ad_id"] for f in r["cohortes"]][:2] == [A, B]  # de más a menos gasto


def test_gasto_por_anuncio_desde_el_registro(datos):
    instancia, leads, _ = datos
    reg = instancia / "clientes" / "acme" / "registro-creativo.csv"
    cab = reg.read_text(encoding="utf-8").strip().split(",")
    filas = [{k: "" for k in cab} | {"ad_id": A, "nombre": NOMBRE_A, "gasto": "999.5"}]
    with reg.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=cab)
        w.writeheader()
        w.writerows(filas)
    r = embudo.cohortes("acme", "anuncio", str(leads), hoy=HOY)
    a = next(f for f in r["cohortes"] if f["ad_id"] == A)
    assert a["gasto"] == 999.5 and any("registro creativo" in x for x in r["avisos"])


def test_etapas_de_pipeline(instancia, tmp_path):
    leads = _csv(tmp_path / "pipeline.csv", ["Date Added", "Stage", "utm_content"],
                 [["2026-10-05", "New Lead", NOMBRE_A], ["2026-10-05", "Qualified", NOMBRE_A],
                  ["2026-10-06", "Booked Call", NOMBRE_A], ["2026-10-06", "Showed", NOMBRE_A],
                  ["2026-10-07", "Closed Won", NOMBRE_A], ["2026-10-07", "Lost", NOMBRE_A]])
    r = embudo.cohortes("acme", "semana", str(leads), hoy=HOY)
    t = r["total"]
    assert (t["leads"], t["cualificados"], t["citas"], t["shows"], t["ventas"]) == (6, 4, 3, 2, 1)
    assert any("etapa actual del pipeline" in a for a in r["avisos"])


def test_saas_ltv_y_payback(instancia, tmp_path):
    leads = _csv(tmp_path / "stripe.csv", ["created_at", "ad_id", "trial", "activado", "fecha_primer_pago", "mrr",
                                           "fecha_baja"],
                 [["2026-09-01", A, "1", "1", "2026-09-15", "100", ""],
                  ["2026-09-02", A, "1", "1", "2026-09-16", "100", "2026-10-16"],
                  ["2026-09-03", A, "1", "0", "", "", ""],
                  ["2026-09-04", A, "1", "1", "", "", ""]])
    meta = _csv(tmp_path / "m.csv", ["anuncio_id", "anuncio", "gasto_eur"], [[A, NOMBRE_A, 400]])
    r = embudo.cohortes("acme", "anuncio", str(leads), str(meta), hoy=HOY, modelo="saas", margen=0.8, churn=0.05)
    a = r["cohortes"][0]
    assert (a["leads"], a["pruebas"], a["activaciones"], a["clientes_pago"], a["mrr_nuevo"], a["bajas"]) == \
        (4, 4, 3, 2, 200, 1)
    assert a["cac"] == 200 and a["coste_prueba"] == 100
    assert r["saas"]["ltv"] == 1600 and r["saas"]["origen_churn"] == "--churn"
    assert a["payback_meses"] == 2.5
    r2 = embudo.cohortes("acme", "anuncio", str(leads), str(meta), hoy=HOY, modelo="saas")
    assert r2["saas"]["ltv"] is None and any("--churn" in x for x in r2["avisos"])


def test_guardar_sin_datos_personales(datos):
    instancia, leads, meta = datos
    r = embudo.cohortes("acme", "semana", str(leads), str(meta), hoy=HOY)
    rutas = embudo.guardar(r)
    embudo.guardar(embudo.cohortes("acme", "anuncio", str(leads), str(meta), hoy=HOY))
    embudo.guardar(r)  # se sustituye la sección, no se duplica
    md = (instancia / "clientes" / "acme" / "cohortes-leads.md").read_text(encoding="utf-8")
    assert md.startswith("# Cohortes de leads: <cliente>")
    assert md.count("## Por semana") == 1 and md.count("## Por anuncio") == 1
    assert "| 2026-W41 (2026-10-05) | sí | 4 |" in md
    for p in rutas + [instancia / "clientes" / "acme" / "datos" / "cohortes_anuncio.csv"]:
        texto = p.read_text(encoding="utf-8")
        assert "@" not in texto and "+34" not in texto
    assert {p.name for p in rutas} == {"cohortes_semana.csv", "cohortes-leads.md"}


def test_main(datos, capsys):
    _, leads, meta = datos
    assert embudo.main(["cohortes", "--cliente", "acme", "--por", "semana", "--meta", str(meta),
                        "--fecha", "2026-11-20", "--json"]) == 0  # sin --leads: el más reciente de privado/
    out = capsys.readouterr().out
    assert "@" not in out and json.loads(out)["leads_archivo"] == "leads_2026-10.csv"
    assert embudo.main(["cohortes", "--cliente", "acme", "--por", "anuncio", "--leads", str(leads),
                        "--fecha", "2026-11-20"]) == 0
    assert "| Anuncio | Campaña | % maduros |" in capsys.readouterr().out
    assert embudo.main(["cohortes", "--cliente", "acme", "--por", "semana", "--leads", str(leads),
                        "--desde", "2027-01-01"]) == 1
    assert embudo.main(["cohortes", "--cliente", "acme", "--por", "semana", "--margen", "80"]) == 1
    assert embudo.main(["cohortes", "--cliente", "nadie", "--por", "semana", "--leads", str(leads)]) == 2


def test_sin_leads(instancia, capsys):
    assert embudo.main(["cohortes", "--cliente", "acme", "--por", "semana"]) == 1
    assert "privado" in capsys.readouterr().err


@pytest.mark.parametrize("texto,esperado", [
    ("2026-10-05T09:00:00.000Z", date(2026, 10, 5)), ("05/10/2026", date(2026, 10, 5)),
    ("1759654800", date(2025, 10, 5)), ("1759654800000", date(2025, 10, 5)), ("mañana", None), ("", None),
])
def test_fecha_de(texto, esperado):
    assert embudo.fecha_de(texto) == esperado


def test_etapas_consultivas_del_contrato(instancia, tmp_path):
    """Etapas del §16 en español, con tildes, en el orden de un pipeline de consultora."""
    etapas = ["Nuevo lead", "Diagnóstico completado", "Cualificado", "Llamada agendada", "No se presentó",
              "Llamada asistida", "Propuesta enviada", "Purchase", "Perdido", "No cualificado", "Cliente potencial",
              "Asistió al taller", "Etapa rara"]
    leads = _csv(tmp_path / "pipeline.csv", ["Fecha", "Etapa", "utm_content"],
                 [["2026-10-05", e, NOMBRE_A] for e in etapas])
    r = embudo.cohortes("acme", "semana", str(leads), hoy=HOY)
    t = r["total"]
    # ganado implica propuesta, asistió, llamada y cualificado; el no-show agendó; perdidos y taller, solo leads
    assert (t["leads"], t["cualificados"], t["citas"], t["shows"], t["propuestas"], t["ventas"]) == (13, 6, 5, 3, 2, 1)
    assert (t["perdidos"], t["no_shows"], t["diagnosticos"]) == (2, 1, None)
    assert t["tasa_propuesta"] == round(2 / 3 * 100, 1)
    assert any("«etapa rara» (1)" in a for a in r["avisos"])
    assert not any("nuevo lead" in a or "taller" in a for a in r["avisos"])
    md = embudo.tabla_markdown(r)
    assert "| Propuestas |" in md and "Diagnósticos" not in md and "Coste por propuesta" in md


def test_columnas_si_no_de_diagnostico_y_propuesta(instancia, tmp_path):
    leads = _csv(tmp_path / "leads.csv", ["fecha", "ad_id", "diagnostico", "cualificado", "llamada", "show",
                                          "propuesta enviada", "venta", "cash"],
                 [["2026-10-05", A, "1", "1", "1", "1", "1", "1", "5000"],
                  ["2026-10-05", A, "1", "1", "1", "1", "1", "0", ""],
                  ["2026-10-06", A, "1", "0", "0", "0", "0", "0", ""],
                  ["2026-10-06", A, "0", "0", "0", "0", "0", "0", ""]])
    meta = _csv(tmp_path / "m.csv", ["anuncio_id", "anuncio", "gasto_eur"], [[A, NOMBRE_A, 1000]])
    r = embudo.cohortes("acme", "anuncio", str(leads), str(meta), hoy=HOY)
    a = r["cohortes"][0]
    assert (a["diagnosticos"], a["cualificados"], a["citas"], a["propuestas"], a["ventas"]) == (3, 2, 2, 2, 1)
    assert (a["coste_diagnostico"], a["coste_propuesta"], a["perdidos"]) == (333.33, 500, None)
    md = embudo.tabla_markdown(r)
    assert "Diagnósticos" in md and "Propuestas" in md


# ---------------------------------------------------------------- I6: revisión de corrección
def test_cash_y_mrr_con_miles_espanoles(instancia, tmp_path):
    """Hallazgo 13: una hoja en español escribe «4.800» (4.800 €) y «1.200,50»; antes salían 4,8 € y 1,2 €."""
    ruta = tmp_path / "leads.csv"
    ruta.write_text("fecha;ad_id;venta;cash;fecha_cash\n"
                    f"2026-09-10;{A};1;4.800;2026-09-20\n"
                    f"2026-09-11;{A};1;1.200,50;2026-09-25\n", encoding="utf-8")
    r = embudo.cohortes("acme", "semana", str(ruta), hoy=HOY)
    assert r["total"]["cash_30d"] == 6000.5 and r["total"]["cash_total"] == 6000.5
    saas = tmp_path / "saas.csv"
    saas.write_text(f"created_at;ad_id;fecha_primer_pago;mrr\n2026-09-01;{A};2026-09-15;1.200\n", encoding="utf-8")
    r = embudo.cohortes("acme", "semana", str(saas), hoy=HOY, modelo="saas")
    assert r["total"]["mrr_nuevo"] == 1200


def test_valor_de_la_oportunidad_no_es_cash(instancia, tmp_path):
    """Hallazgo 30b: «valor» (monetaryValue de una oportunidad abierta de GHL) no es dinero cobrado."""
    ruta = _csv(tmp_path / "ops.csv", ["fecha", "ad_id", "etapa", "valor"],
                [["2026-09-10", A, "Propuesta enviada", "9000"]])
    r = embudo.cohortes("acme", "semana", str(ruta), hoy=HOY)
    assert r["total"]["cash_total"] == 0
