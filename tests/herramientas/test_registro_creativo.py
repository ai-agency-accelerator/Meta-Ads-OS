import csv
import json
from datetime import date

import pytest

import registro_creativo as rc

HOY = date(2026, 11, 20)
CABECERA = ("ad_id,nombre,fecha,campana,conjunto,angulo,concepto,formato,hook,via,identidad,ruta_creativo,gasto,"
            "impresiones,"
            "hook_rate,hold_rate,ctr,cpm,resultado_meta,coste_resultado_meta,leads,cualificados,citas,shows,pruebas,"
            "activaciones,clientes_pago,cash,coste_cita,coste_venta,n_suficiente,veredicto,fecha_veredicto,motivo")
ECONOMIA = """
## Economía (con `herramientas/economia.py`)
| Métrica | Break-even | Target | Fuente o supuesto |
|---|---|---|---|
| Coste por venta / CAC | 2.000 € | 1.200 € | calculado |
| CPL | 40 | 25 | |
| Coste por lead cualificado | | | |
| Coste por cita / por show | 200 / 260 | 120 / 160 | |

## Medición
"""
META_COLS = ["anuncio", "campaña", "gasto_eur", "impresiones", "clics_enlace", "leads", "desde", "hasta",
             "anuncio_id", "vistas_3s", "thruplay", "conjunto"]
A, B, C, D, E, F = (f"12000000000000{i}" for i in range(1, 7))
ANUNCIOS = [
    # nombre, id, gasto, impresiones, clics, leads Meta, vistas 3 s, thruplay
    ("20261101_tiempo-perdido_demo-antes-despues_demo_h1", A, 900, 30000, 360, 36, 9000, 1800, "2026-11-01"),
    ("20261101_tiempo-perdido_demo-antes-despues_demo_h1", A, 500, 20000, 240, 24, 6000, 1200, "2026-11-02"),
    ("20261101_tiempo-perdido_demo-antes-despues_demo_h2", B, 800, 30000, 150, 30, 6000, 600, "2026-11-01"),
    ("20261115_ahorro_calculadora_estatico_h1", C, 300, 8000, 60, 10, 0, 0, "2026-11-15"),
    ("Anuncio sin nombre bueno", D, 0, 0, 0, 0, 0, 0, "2026-11-01"),
    ("20261101_dup_x_ugc_h1", E, 100, 3000, 20, 3, 900, 100, "2026-11-01"),
    ("20261101_dup_x_ugc_h1", F, 100, 3000, 20, 3, 900, 100, "2026-11-01"),
]


def _escribir(ruta, cols, filas, delim=","):
    with ruta.open("w", encoding="utf-8", newline="") as h:
        w = csv.writer(h, delimiter=delim)
        w.writerow(cols)
        w.writerows(filas)
    return ruta


@pytest.fixture
def datos(instancia, tmp_path):
    ficha = instancia / "clientes" / "acme" / "ficha.md"
    ficha.write_text(ficha.read_text(encoding="utf-8") + ECONOMIA, encoding="utf-8")
    meta = _escribir(tmp_path / "meta.csv", META_COLS,
                     [[n, "ES_LEADS_ADQ_HV", g, imp, cl, ld, d, d, ad, v3, tp, "BROAD-A+_LEAD"]
                      for n, ad, g, imp, cl, ld, v3, tp, d in ANUNCIOS] + [["TOTAL", "", 2700, 0, 0, 0, "", "", "", 0, 0, ""]])
    ghl = _escribir(tmp_path / "ghl.csv", ["ad_id", "utm_content", "leads", "cualificados", "citas", "shows",
                                           "ventas", "cash"],
                    [[A, "", 60, 30, 12, 9, 1, 5000], [B, "", 30, 10, 0, 0, 0, 0],
                     ["", "20261115_ahorro_calculadora_estatico_h1", 10, 3, 0, 0, 0, 0],
                     ["", "20261101_dup_x_ugc_h1", 4, 1, 0, 0, 0, 0],
                     ["999999999999999", "", 2, 0, 0, 0, 0, 0]])
    return instancia, meta, ghl


def _registro(instancia):
    ruta = instancia / "clientes" / "acme" / "registro-creativo.csv"
    with ruta.open(encoding="utf-8", newline="") as h:
        return {f["ad_id"]: f for f in csv.DictReader(h)}, ruta.read_text(encoding="utf-8").splitlines()[0]


def test_objetivos_de_la_ficha():
    assert rc.objetivos_ficha(ECONOMIA) == {"clientes_pago": 1200, "leads": 25, "citas": 120, "shows": 160}


@pytest.mark.parametrize("texto,entero,esperado", [
    ("1234.5", False, 1234.5), ("1234,5", False, 1234.5), ("1.234,56", False, 1234.56), ("12,345", True, 12345),
    ("12.345", True, 12345), ("€ 99", False, 99), ("", False, None), ("—", False, None),
])
def test_num(texto, entero, esperado):
    assert rc.num(texto, entero) == esperado


def test_actualizar_cruza_y_decide(datos):
    instancia, meta, ghl = datos
    r = rc.actualizar("acme", str(meta), str(ghl), hoy=HOY)
    filas, cabecera = _registro(instancia)
    assert cabecera == CABECERA
    assert r["capa_decision"] == "citas" and r["anuncios_actualizados"] == 6
    assert r["referencias"]["citas"] == {"valor": 120.0, "origen": "objetivo"}
    assert r["referencias"]["cualificados"]["origen"] == "media de la cuenta"

    a = filas[A]  # dos filas diarias sumadas
    assert (a["gasto"], a["impresiones"], a["hook_rate"], a["hold_rate"], a["ctr"], a["cpm"]) == \
        ("1400", "50000", "30", "20", "1.2", "28")
    assert (a["angulo"], a["concepto"], a["formato"], a["hook"], a["fecha"]) == \
        ("tiempo-perdido", "demo-antes-despues", "demo", "h1", "2026-11-01")
    assert (a["leads"], a["citas"], a["clientes_pago"], a["cash"]) == ("60", "12", "1", "5000")
    assert (a["coste_cita"], a["coste_venta"], a["resultado_meta"], a["coste_resultado_meta"]) == \
        ("116.67", "1400", "60", "23.33")
    assert a["veredicto"] == "ganador" and a["n_suficiente"] == "si" and "provisional" in a["motivo"]
    assert a["fecha_veredicto"] == "2026-11-20" and a["campana"] == "ES_LEADS_ADQ_HV"

    # 0 citas con 6,7× el coste objetivo por cita y 19 días: descartado en la capa más profunda que ha madurado
    # (los shows maduran a los 21 días, MADUREZ; I6 hallazgo 3)
    b = filas[B]
    assert b["veredicto"] == "perdedor" and "0 citas" in b["motivo"] and b["n_suficiente"] == "si"

    c = filas[C]  # 5 días: capas de negocio sin madurar; pocos leads para decidir
    assert c["veredicto"] == "en-test" and c["n_suficiente"] == "no" and "sin madurar" in c["motivo"]
    assert c["hook_rate"] == "" and c["hold_rate"] == "" and c["leads"] == "10"

    d = filas[D]
    assert d["veredicto"] == "sin-datos" and d["angulo"] == ""

    for x in (E, F):  # nombre compartido: el resultado de negocio no se reparte ni se pone a 0
        assert filas[x]["leads"] == "" and filas[x]["veredicto"] == "en-test"
    assert any("lo comparten 2 anuncios" in av for av in r["avisos"])
    assert any("999999999999999" in av for av in r["avisos"])
    assert any("sin nomenclatura" in av for av in r["avisos"])


def test_actualizar_conserva_lo_manual_y_columnas_extra(datos):
    instancia, meta, ghl = datos
    ruta = instancia / "clientes" / "acme" / "registro-creativo.csv"
    previa = {k: "" for k in CABECERA.split(",")} | {"ad_id": B, "via": "ia", "ruta_creativo": "creativos/b/",
                                                     "veredicto": "ganador", "motivo": "manual: cierra bien en llamada"}
    viejo = {k: "" for k in CABECERA.split(",")} | {"ad_id": "120000000000099", "nombre": "20260901_a_b_ugc_h1",
                                                    "fecha": "2026-09-01", "gasto": "50", "veredicto": "perdedor"}
    with ruta.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=CABECERA.split(",") + ["nota_propia"])
        w.writeheader()
        w.writerow(previa | {"nota_propia": "x"})
        w.writerow(viejo | {"nota_propia": ""})
    r = rc.actualizar("acme", str(meta), str(ghl), hoy=HOY)
    filas, cabecera = _registro(instancia)
    assert cabecera == CABECERA + ",nota_propia"
    assert filas[B]["via"] == "ia" and filas[B]["ruta_creativo"] == "creativos/b/"
    assert filas[B]["veredicto"] == "ganador" and filas[B]["motivo"].startswith("manual:")
    assert filas[B]["nota_propia"] == "x" and filas[B]["gasto"] == "800"
    assert filas["120000000000099"]["veredicto"] == "perdedor"  # fuera de la exportación: intacto
    assert any("nota_propia" in av for av in r["avisos"])


def test_identidad_en_su_sitio_y_desde_el_leeme(datos):
    instancia, meta, ghl = datos
    cliente = instancia / "clientes" / "acme"
    ruta = cliente / "registro-creativo.csv"
    # registro antiguo con «identidad» al final y un valor escrito a mano
    antigua = [c for c in CABECERA.split(",") if c != "identidad"] + ["identidad"]
    with ruta.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=antigua)
        w.writeheader()
        w.writerow({k: "" for k in antigua} | {"ad_id": C, "identidad": "pagina"})
    pieza = cliente / "creativos" / "20261101_tiempo-perdido_demo-antes-despues_demo"
    pieza.mkdir(parents=True)
    (pieza / "LEEME.md").write_text(
        "# Pieza\n\n## Prueba social y derechos\n- **Identidad:** colaboracion (socio: creador)\n"
        "| ad_id | Identidad | Socio (alias) | Cabecera (ambas | una) | Publicación existente o contenido nuevo |\n"
        "|---|---|---|---|---|\n"
        f"| {A} | colaboracion | creadora-1 | ambas | contenido nuevo |\n"
        f"| {B} | Página | — | una | contenido nuevo |\n"
        f"| {C} | colaboracion | creadora-1 | ambas | contenido nuevo |\n", encoding="utf-8")
    r = rc.actualizar("acme", str(meta), str(ghl), hoy=HOY)
    filas, cabecera = _registro(instancia)
    assert cabecera == CABECERA
    assert (filas[A]["identidad"], filas[B]["identidad"]) == ("colaboracion", "pagina")
    assert filas[C]["identidad"] == "pagina"  # lo escrito a mano manda
    assert filas[E]["identidad"] == ""
    assert not any("fuera del contrato" in av for av in r["avisos"])


def test_simular_no_escribe(datos):
    instancia, meta, ghl = datos
    ruta = instancia / "clientes" / "acme" / "registro-creativo.csv"
    antes = ruta.read_text(encoding="utf-8")
    r = rc.actualizar("acme", str(meta), str(ghl), hoy=HOY, simular=True)
    assert r["guardado"] is False and ruta.read_text(encoding="utf-8") == antes


def test_objetivo_por_cli_y_sin_ghl(datos):
    instancia, meta, _ = datos
    r = rc.actualizar("acme", str(meta), objetivos_cli=["resultado_meta=10"], hoy=HOY)
    filas, _ = _registro(instancia)
    # sin negocio decide con los resultados de Meta; A tiene 60 leads a 23,33 > 10 de objetivo
    assert r["capa_decision"] == "resultado_meta"
    assert filas[A]["veredicto"] == "perdedor" and "resultados de Meta" in filas[A]["motivo"]
    with pytest.raises(rc.ErrorUsuario):
        rc.actualizar("acme", str(meta), objetivos_cli=["ventas=10"], hoy=HOY)


def test_exportacion_ads_manager_en_espanol(instancia, tmp_path):
    ruta = tmp_path / "ads-manager.csv"
    ruta.write_text(
        "﻿\"Nombre de la campaña\";\"Nombre del conjunto de anuncios\";\"Nombre del anuncio\";"
        "\"Identificador del anuncio\";\"Importe gastado (EUR)\";\"Impresiones\";\"Clics en el enlace\";"
        "\"Resultados\";\"Inicio del informe\"\n"
        "\"ES_LEADS_ADQ_HV\";\"BROAD_LEAD\";\"20261101_a_b_ugc_h1\";\"120000000000010\";\"123,45\";\"10000\";\"100\";"
        "\"5\";\"2026-11-01\"\n"
        ";;;;\"123,45\";\"10000\";;;\n", encoding="utf-8")
    rc.actualizar("acme", str(ruta), hoy=HOY)
    filas, _ = _registro(instancia)
    f = filas["120000000000010"]
    assert (f["gasto"], f["ctr"], f["resultado_meta"], f["coste_resultado_meta"], f["cpm"]) == \
        ("123.45", "1", "5", "24.69", "12.35")
    assert f["conjunto"] == "BROAD_LEAD" and len(filas) == 1


def test_sin_nomenclatura(datos, capsys):
    instancia, meta, ghl = datos
    malos = rc.sin_nomenclatura("acme", str(meta))
    assert [m["ad_id"] for m in malos] == [D]
    rc.actualizar("acme", str(meta), str(ghl), hoy=HOY)
    assert rc.main(["sin-nomenclatura", "--cliente", "acme", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)[0]["nombre"] == "Anuncio sin nombre bueno"


def test_main_errores(instancia, tmp_path, capsys):
    sin_id = _escribir(tmp_path / "m.csv", ["ad_name", "spend"], [["x", "1"]])
    assert rc.main(["actualizar", "--cliente", "acme", "--meta", str(sin_id)]) == 1
    assert "ID del anuncio" in capsys.readouterr().err
    assert rc.main(["actualizar", "--cliente", "acme", "--meta", str(tmp_path / "no.csv")]) == 1
    assert rc.main(["actualizar", "--cliente", "nadie", "--meta", str(sin_id)]) == 2
    assert rc.main(["actualizar", "--cliente", "acme", "--meta", str(sin_id), "--fecha", "ayer"]) == 1


def test_main_texto(datos, capsys):
    _, meta, ghl = datos
    assert rc.main(["actualizar", "--cliente", "acme", "--meta", str(meta), "--ghl", str(ghl),
                    "--fecha", "2026-11-20"]) == 0
    out = capsys.readouterr().out
    assert "Capa de decisión: citas" in out and "ganador 1" in out


def test_poisson_cdf():
    assert rc.poisson_cdf(0, 3) == pytest.approx(0.0498, abs=1e-4)
    assert rc.poisson_cdf(1, 1.25) == pytest.approx(0.6446, abs=1e-4)


# ---------------------------------------------------------------- I6: revisión de corrección

COLS_META_ADS = ["ad_id", "anuncio", "desde", "hasta", "gasto", "impresiones", "clics_enlace", "evento_resultado",
                 "resultado_meta"]


def _ficha_con(instancia, evento="Lead", economia=ECONOMIA):
    ficha = instancia / "clientes" / "acme" / "ficha.md"
    texto = ficha.read_text(encoding="utf-8").replace("evento_principal: Lead", f"evento_principal: {evento}")
    ficha.write_text(texto + economia, encoding="utf-8")


def test_resultado_meta_contra_el_objetivo_del_evento_optimizado(instancia, tmp_path):
    """Hallazgo 2: con evento_principal Schedule, los resultados de Meta son citas y se juzgan contra 120 €, no
    contra el CPL de 25 €."""
    _ficha_con(instancia, "Schedule")
    meta = _escribir(tmp_path / "meta.csv", COLS_META_ADS, [
        ["120000000000002", "20261001_a_b_ugc_h1", "2026-10-01", "2026-11-09", 600, 20000, 200,
         "offsite_conversion.fb_pixel_schedule", 5],
        ["120000000000001", "20261001_a_c_ugc_h1", "2026-10-01", "2026-11-09", 300, 10000, 100,
         "offsite_conversion.fb_pixel_schedule", 2]])
    r = rc.actualizar("acme", str(meta), hoy=date(2026, 11, 10))
    filas, _ = _registro(instancia)
    for ad in ("120000000000002", "120000000000001"):
        assert filas[ad]["veredicto"] == "en-test", filas[ad]["motivo"]
    assert r["referencias"]["resultado_meta"]["valor"] == 120.0


def test_resultado_meta_con_eventos_mezclados_cada_uno_contra_el_suyo(instancia, tmp_path):
    _ficha_con(instancia, "Schedule")
    meta = _escribir(tmp_path / "meta.csv", COLS_META_ADS, [
        ["120000000000002", "20261001_a_b_ugc_h1", "2026-10-01", "2026-11-09", 600, 20000, 200, "schedule_total", 5],
        ["120000000000003", "20261001_a_d_ugc_h1", "2026-10-01", "2026-11-09", 600, 20000, 200,
         "offsite_conversion.fb_pixel_lead", 4]])
    r = rc.actualizar("acme", str(meta), hoy=date(2026, 11, 10))
    filas, _ = _registro(instancia)
    assert filas["120000000000002"]["veredicto"] == "en-test"   # 5 citas a 120 €: en su objetivo
    assert filas["120000000000003"]["veredicto"] == "perdedor"  # 4 leads a 150 € con CPL objetivo 25 €
    assert "leads" in filas["120000000000003"]["motivo"]
    assert any("eventos distintos" in av for av in r["avisos"])
    assert "resultado_meta" not in r["referencias"]


def test_madurez_por_capa_no_mata_al_mejor_por_0_ventas_a_los_16_dias(instancia, tmp_path):
    """Hallazgo 3: 52 citas a 125 € y 40 shows, 0 ventas a los 16 días: la venta B2B aún no ha tenido tiempo
    (playbook de consultoras §10.2: la cohorte se lee a partir de 6–10 semanas)."""
    _ficha_con(instancia)
    meta = _escribir(tmp_path / "meta.csv", COLS_META_ADS, [
        ["120000000000031", "20261025_a_b_ugc_h1", "2026-10-25", "2026-11-09", 6500, 200000, 2000, "lead", 200],
        ["120000000000032", "20261025_a_c_ugc_h1", "2026-10-25", "2026-11-09", 3000, 100000, 1000, "lead", 100]])
    ghl = _escribir(tmp_path / "ghl.csv", ["ad_id", "leads", "cualificados", "citas", "shows", "ventas", "cash"],
                    [["120000000000031", 200, 90, 52, 40, 0, 0], ["120000000000032", 100, 40, 22, 17, 0, 0]])
    rc.actualizar("acme", str(meta), str(ghl), hoy=date(2026, 11, 10))
    filas, _ = _registro(instancia)
    mejor = filas["120000000000031"]
    assert mejor["veredicto"] != "perdedor", mejor["motivo"]
    assert "clientes de pago sin madurar (16 días" in mejor["motivo"]
    # Con la cohorte madura (60 días), 0 ventas con 5,4× el CAC objetivo sí descarta
    rc.actualizar("acme", str(meta), str(ghl), hoy=date(2026, 12, 24))
    filas, _ = _registro(instancia)
    assert filas["120000000000031"]["veredicto"] == "perdedor"
    assert "clientes de pago" in filas["120000000000031"]["motivo"]


def test_madurez_configurable_por_capa(instancia, tmp_path):
    _ficha_con(instancia)
    meta = _escribir(tmp_path / "meta.csv", COLS_META_ADS, [
        ["120000000000031", "20261025_a_b_ugc_h1", "2026-10-25", "2026-11-09", 6500, 200000, 2000, "lead", 200]])
    ghl = _escribir(tmp_path / "ghl.csv", ["ad_id", "leads", "citas", "ventas"], [["120000000000031", 200, 52, 0]])
    rc.actualizar("acme", str(meta), str(ghl), hoy=date(2026, 11, 10), madurez_cli=["clientes_pago=14"])
    filas, _ = _registro(instancia)
    assert filas["120000000000031"]["veredicto"] == "perdedor"
    with pytest.raises(rc.ErrorUsuario):
        rc.actualizar("acme", str(meta), str(ghl), hoy=date(2026, 11, 10), madurez_cli=["ventas=14"])
    assert rc.main(["actualizar", "--cliente", "acme", "--meta", str(meta), "--ghl", str(ghl), "--fecha",
                    "2026-11-10", "--madurez", "clientes_pago=14", "--simular"]) == 0


def test_sin_nomenclatura_no_toma_la_fecha_del_periodo(instancia, tmp_path):
    """Hallazgo 17: dos anuncios idénticos, uno con nomenclatura de hace 5 días y otro sin ella, en una exportación
    del 2026-09-01 al 2026-11-09: los dos reciben el mismo trato."""
    _ficha_con(instancia)
    meta = _escribir(tmp_path / "meta.csv", COLS_META_ADS, [
        ["120000000000012", "20261105_a_b_ugc_h1", "2026-09-01", "2026-11-09", 400, 20000, 200, "lead", 14],
        ["120000000000011", "Video nuevo cliente clinica", "2026-09-01", "2026-11-09", 400, 20000, 200, "lead", 14]])
    ghl = _escribir(tmp_path / "ghl.csv", ["ad_id", "leads", "citas"],
                    [["120000000000012", 14, 0], ["120000000000011", 14, 0]])
    rc.actualizar("acme", str(meta), str(ghl), hoy=date(2026, 11, 10))
    filas, _ = _registro(instancia)
    con, sin = filas["120000000000012"], filas["120000000000011"]
    assert con["veredicto"] == sin["veredicto"] == "en-test", (con["motivo"], sin["motivo"])
    assert sin["fecha"] == ""  # la fecha del periodo no es la del anuncio
    assert "fecha fiable" in sin["motivo"]


def test_sin_nomenclatura_con_exportacion_por_dia_usa_el_primer_dia_con_gasto(instancia, tmp_path):
    _ficha_con(instancia)
    filas_meta = [["120000000000011", "Video nuevo cliente clinica", d, d, 100, 5000, 50, "lead", 3]
                  for d in ("2026-09-20", "2026-09-21", "2026-09-22", "2026-09-23")]
    meta = _escribir(tmp_path / "meta.csv", COLS_META_ADS, filas_meta)
    ghl = _escribir(tmp_path / "ghl.csv", ["ad_id", "leads", "citas"], [["120000000000011", 12, 0]])
    rc.actualizar("acme", str(meta), str(ghl), hoy=date(2026, 11, 10))
    filas, _ = _registro(instancia)
    f = filas["120000000000011"]
    assert f["fecha"] == "2026-09-20"
    assert f["veredicto"] == "perdedor" and "citas" in f["motivo"]  # 51 días: las citas ya han madurado


def test_resultados_vacios_en_ads_manager_cuentan_como_cero(instancia, tmp_path):
    """Hallazgo 18: Ads Manager deja «Resultados» vacío cuando no hay ninguno; con 234,50 € de gasto (9,4× el CPL
    objetivo de 25 €) el anuncio es perdedor, igual que con el CSV de meta_ads.py, que escribe 0."""
    _ficha_con(instancia)
    ruta = tmp_path / "ads-manager.csv"
    ruta.write_text(
        "\"Nombre del anuncio\";\"Identificador del anuncio\";\"Importe gastado (EUR)\";\"Impresiones\";"
        "\"Resultados\";\"Inicio del informe\";\"Fin del informe\"\n"
        "\"20261001_a_b_ugc_h1\";\"120212345678901235\";\"234,50\";\"9000\";\"\";\"2026-10-01\";\"2026-11-09\"\n",
        encoding="utf-8")
    rc.actualizar("acme", str(ruta), hoy=date(2026, 11, 10))
    filas, _ = _registro(instancia)
    f = filas["120212345678901235"]
    assert f["resultado_meta"] == "0" and f["veredicto"] == "perdedor"


def test_ad_id_en_notacion_cientifica_es_un_error(instancia, tmp_path):
    """Bajo (fuera del tope): un CSV guardado con Excel redondea el ID; antes se perdía el 90 % del gasto sin aviso."""
    _ficha_con(instancia)
    meta = _escribir(tmp_path / "meta.csv", ["ad_id", "anuncio", "gasto"],
                     [["120212345678901234", "20261001_a_b_ugc_h1", 100], ["1.20212E+17", "20261001_a_c_ugc_h1", 900]])
    with pytest.raises(rc.ErrorUsuario, match="notación científica"):
        rc.actualizar("acme", str(meta), hoy=date(2026, 11, 10))


def test_cash_con_miles_espanoles(instancia, tmp_path):
    """Hallazgo 13: «4.800» de una hoja en español es 4.800 €, no 4,8 €."""
    _ficha_con(instancia)
    meta = _escribir(tmp_path / "meta.csv", COLS_META_ADS, [
        ["120000000000031", "20261001_a_b_ugc_h1", "2026-10-01", "2026-11-09", 500, 20000, 200, "lead", 20]])
    ghl = _escribir(tmp_path / "ghl.csv", ["ad_id", "leads", "ventas", "cash"], [["120000000000031", 20, 1, "4.800"]],
                    delim=";")
    rc.actualizar("acme", str(meta), str(ghl), hoy=date(2026, 11, 10))
    filas, _ = _registro(instancia)
    assert filas["120000000000031"]["cash"] == "4800"


def test_guarda_la_ultima_exportacion(instancia, tmp_path):
    """Hallazgo 19: qué anuncios y qué periodo trae la última exportación, para que el análisis no mezcle periodos."""
    _ficha_con(instancia)
    meta = _escribir(tmp_path / "meta.csv", COLS_META_ADS, [
        ["120000000000031", "20261001_a_b_ugc_h1", "2026-09-15", "2026-11-09", 500, 20000, 200, "lead", 20]])
    r = rc.actualizar("acme", str(meta), hoy=date(2026, 11, 10))
    ruta = instancia / "clientes" / "acme" / "datos" / "registro-creativo_ultima-exportacion.json"
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    assert datos["ad_ids"] == ["120000000000031"] and (datos["desde"], datos["hasta"]) == ("2026-09-15", "2026-11-09")
    assert r["ultima_exportacion"].endswith("registro-creativo_ultima-exportacion.json")
    ruta.unlink()
    rc.actualizar("acme", str(meta), hoy=date(2026, 11, 10), simular=True)
    assert not ruta.exists()
