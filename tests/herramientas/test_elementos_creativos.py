"""elementos_creativos.py (B12): esquema, etiquetas, estadística, análisis, retención, diversidad, suministro y
fotogramas. Sin red: la API de Meta va con HttpSimulado y las descargas, simuladas. FFmpeg real si está instalado."""
from __future__ import annotations

import csv
import importlib
import json
import shutil
import socket
import subprocess
import urllib.request
from datetime import date

import pytest

from http_simulado import HttpSimulado

HOY = date(2026, 11, 9)
FF = shutil.which("ffmpeg")
con_ffmpeg = pytest.mark.skipif(not FF, reason="FFmpeg no instalado")


@pytest.fixture(autouse=True)
def _sin_red(monkeypatch):
    def bloqueado(*_a, **_k):
        raise RuntimeError("Test sin red")

    monkeypatch.setattr(socket.socket, "connect", bloqueado)
    monkeypatch.setattr(socket, "create_connection", bloqueado)
    monkeypatch.setattr(socket, "getaddrinfo", bloqueado)


@pytest.fixture
def ec(instancia):
    import elementos_creativos as modulo
    return importlib.reload(modulo)


@pytest.fixture
def cliente(instancia):
    return instancia / "clientes" / "acme"


# ---------------------------------------------------------------- ayudas
def ad_id(i: int) -> str:
    return f"1200000000{i:05d}"


def anuncio(i, angulo="tiempo-perdido", concepto="caso-gestoria", formato="ugc", gasto=600.0, citas=None,
            veredicto="", fecha="2026-10-01", hook="h1", impresiones=10000, hook_rate=30, hold_rate=20, ctr=1.0,
            leads=None, conjunto="BROAD_LEAD", clientes_pago=None) -> dict:
    nombre = f"{fecha.replace('-', '')}_{angulo}_{concepto}_{formato}_{hook}"
    return {"ad_id": ad_id(i), "nombre": nombre, "fecha": fecha, "campana": "ES_LEADS_ADQ", "conjunto": conjunto,
            "angulo": angulo, "concepto": concepto, "formato": formato, "hook": hook, "gasto": gasto,
            "impresiones": impresiones, "hook_rate": hook_rate if formato not in ("estatico", "carrusel") else "",
            "hold_rate": hold_rate if formato not in ("estatico", "carrusel") else "", "ctr": ctr,
            "citas": "" if citas is None else citas, "leads": "" if leads is None else leads,
            "clientes_pago": "" if clientes_pago is None else clientes_pago, "veredicto": veredicto}


def escribir_registro(cliente, filas) -> None:
    import registro_creativo as rc
    with (cliente / "registro-creativo.csv").open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(rc.COLUMNAS), extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for f in filas:
            w.writerow(f)


def etiquetar(ec, filas: dict[int, dict]) -> None:
    ec.poner("acme", [{"ad_id": ad_id(i), **v} for i, v in filas.items()], por="test", hoy=HOY)


def leer_elementos(cliente) -> dict[str, dict]:
    ruta = cliente / "datos" / "elementos-creativos.csv"
    return {f["ad_id"]: f for f in csv.DictReader(ruta.open(encoding="utf-8"))}


def correr(ec, capsys, *args) -> tuple[int, str, str]:
    codigo = ec.main(list(args))
    salida = capsys.readouterr()
    return codigo, salida.out, salida.err


# ---------------------------------------------------------------- esquema
def test_esquema_fijo_y_columnas(ec):
    assert ec.COLUMNAS[:2] == ["ad_id", "nombre"]
    assert ec.COLUMNAS[-5:] == ["huella_visual", "fuente_visual", "etiquetado_por", "fecha_etiquetado", "notas"]
    for col in ("quien_habla", "primer_fotograma", "texto_0s", "duracion_s", "ritmo", "demo", "prueba_social", "cifra",
                "cta", "subtitulos", "menciona_ia", "filtro"):
        assert col in ec.COLUMNAS
    assert len(set(ec.COLUMNAS)) == len(ec.COLUMNAS)
    assert set(ec.ELEMENTOS_ANALISIS) == (set(ec.ETIQUETAS) - {"duracion_s"}) | {"duracion", "formato", "via"}
    for e in ec.ESQUEMA:  # valores en kebab sin acentos ni comodines
        assert e.valores is None or all(v == ec.normalizar_valor(v) and v not in ec.COMODINES for v in e.valores)
    # ninguna columna se parece a un dato personal (hook datos_personales)
    assert not {"email", "telefono", "nombre_completo", "apellidos", "dni", "direccion"} & set(ec.COLUMNAS)


def test_esquema_cli_json(ec, capsys):
    codigo, out, _ = correr(ec, capsys, "etiquetas", "esquema", "--json")
    datos = json.loads(out)
    assert codigo == 0 and datos["archivo"] == "clientes/<slug>/datos/elementos-creativos.csv"
    assert "duda" in datos["criterio_duda"] and len(datos["etiquetas"]) == len(ec.ESQUEMA)


@pytest.mark.parametrize("entrada,esperado", [("Voz en off", "voz-en-off"), ("Rápido", "rapido"), ("Sí", "si"),
                                              ("ANTES_DESPUES", "antes-despues"), ("12,5", "12.5")])
def test_normalizar_valor(ec, entrada, esperado):
    assert ec.normalizar_valor(entrada) == esperado


# ---------------------------------------------------------------- etiquetas
def test_preparar_conserva_lo_etiquetado_y_marca_no_aplica(ec, cliente):
    escribir_registro(cliente, [anuncio(1, gasto=900), anuncio(2, formato="estatico", concepto="dato-horas", gasto=300),
                                anuncio(3, gasto=0)])
    r = ec.preparar("acme")
    assert (r["filas"], r["creadas"], r["archivo"]) == (2, 2, "clientes/acme/datos/elementos-creativos.csv")
    etiquetar(ec, {1: {"quien_habla": "fundador"}})
    r = ec.preparar("acme")
    assert r["creadas"] == 0
    filas = leer_elementos(cliente)
    assert filas[ad_id(1)]["quien_habla"] == "fundador" and filas[ad_id(1)]["soporte"] == "video"
    estatico = filas[ad_id(2)]
    assert estatico["soporte"] == "imagen"
    assert (estatico["ritmo"], estatico["subtitulos"], estatico["duracion_s"]) == ("no-aplica",) * 3
    pend = ec.pendientes("acme")
    assert [p["ad_id"] for p in pend] == [ad_id(1), ad_id(2)]           # de más a menos gasto
    assert pend[0]["estado"] == "parcial" and pend[1]["estado"] == "pendiente"
    assert "ritmo" not in pend[1]["faltan"]                                  # un estático no necesita ritmo


def test_poner_normaliza_y_valida_todo_antes_de_escribir(ec, cliente, capsys, tmp_path):
    escribir_registro(cliente, [anuncio(1), anuncio(2)])
    ec.preparar("acme")
    antes = (cliente / "datos" / "elementos-creativos.csv").read_text(encoding="utf-8")
    malo = tmp_path / "etiquetas.json"
    malo.write_text(json.dumps([{"ad_id": ad_id(1), "quien_habla": "Fundador"},
                                {"ad_id": ad_id(2), "quien_habla": "influencer"}]), encoding="utf-8")
    codigo, _, err = correr(ec, capsys, "etiquetas", "poner", "--cliente", "acme", "--archivo", str(malo))
    assert codigo == 1 and "No se ha escrito nada" in err and "influencer" in err
    assert (cliente / "datos" / "elementos-creativos.csv").read_text(encoding="utf-8") == antes
    codigo, _, _ = correr(ec, capsys, "etiquetas", "poner", "--cliente", "acme", "--ad", ad_id(1),
                          "quien_habla=Voz en off", "texto_0s=Sí", "gancho=duda", "--por", "critico-creativo",
                          "--fecha", "2026-11-09")
    assert codigo == 0
    f = leer_elementos(cliente)[ad_id(1)]
    assert (f["quien_habla"], f["texto_0s"], f["gancho"]) == ("voz-en-off", "si", "duda")
    assert (f["etiquetado_por"], f["fecha_etiquetado"]) == ("critico-creativo", "2026-11-09")


def test_poner_rechaza_columnas_automaticas_y_no_aplica_fuera_de_video(ec, cliente):
    escribir_registro(cliente, [anuncio(1)])
    with pytest.raises(ec.ErrorUsuario, match="no se puede poner a mano"):
        ec.poner("acme", [{"ad_id": ad_id(1), "huella_visual": "ffffffffffffffff"}])
    with pytest.raises(ec.ErrorUsuario, match="no-aplica"):
        ec.poner("acme", [{"ad_id": ad_id(1), "quien_habla": "no-aplica"}])


def test_validar_detecta_duplicados_y_valores(ec, cliente, capsys):
    escribir_registro(cliente, [anuncio(1)])
    ruta = cliente / "datos" / "elementos-creativos.csv"
    filas = [{c: "" for c in ec.COLUMNAS} | {"ad_id": ad_id(1), "quien_habla": "influencer"},
             {c: "" for c in ec.COLUMNAS} | {"ad_id": ad_id(1)}]
    with ruta.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=ec.COLUMNAS)
        w.writeheader()
        w.writerows(filas)
    codigo, out, _ = correr(ec, capsys, "etiquetas", "validar", "--cliente", "acme")
    assert codigo == 1 and "repetido" in out and "influencer" in out


# ---------------------------------------------------------------- estadística
def test_wilson_y_newcombe_contra_valores_publicados(ec):
    lo, hi = ec.wilson(81, 263)                       # Newcombe (1998), tabla I
    assert (round(lo, 4), round(hi, 4)) == (0.2553, 0.3662)
    d, lo, hi = ec.newcombe(56, 70, 48, 80)           # Newcombe (1998), método 10: 0,0524 a 0,3339
    assert (round(d, 4), round(lo, 4), round(hi, 4)) == (0.2, 0.0524, 0.3339)


def test_fisher_bilateral(ec):
    assert ec.fisher(3, 1, 1, 3) == pytest.approx(34 / 70)
    assert ec.fisher(4, 0, 0, 4) == pytest.approx(2 / 70)
    assert ec.fisher(2, 2, 2, 2) == pytest.approx(1.0)


def test_benjamini_hochberg(ec):
    assert ec.benjamini_hochberg([0.01, 0.04, 0.03, 0.5]) == pytest.approx([0.04, 0.16 / 3, 0.16 / 3, 0.5])


def test_razon_de_costes_y_sobredispersion(ec):
    r = ec.razon_costes(100, 10, 100, 20)
    assert r["razon"] == pytest.approx(2.0)
    assert r["ic"] == pytest.approx([0.936, 4.273], abs=1e-3)
    ancho = ec.razon_costes(100, 10, 100, 20, phi=4.0)
    assert ancho["ic"][0] < r["ic"][0] and ancho["ic"][1] > r["ic"][1] and ancho["p"] > r["p"]
    # anuncios del mismo grupo con tasas muy distintas → φ > 1
    phi = ec.dispersion_poisson([[(100, 1), (100, 19)], [(100, 10), (100, 10)]])
    assert phi > 1
    assert ec.dispersion_poisson([[(100, 10)], [(100, 5)]]) is None  # sin réplica


def test_dhash_y_hamming(ec):
    assert ec.dhash_de_pixeles(bytes(range(72))) == "0" * 16
    assert ec.dhash_de_pixeles(bytes(range(72))[::-1]) == "f" * 16
    assert ec.distancia_hamming("0" * 16, "f" * 16) == 64
    assert ec.distancia_hamming("0" * 16, "0" * 15 + "3") == 2
    assert ec.distancia_hamming("", "0" * 16) is None


def test_ritmo_y_aspecto(ec):
    assert ec.ritmo_por_cortes(30, 19)[1] == "rapido"      # 1,5 s por plano
    assert ec.ritmo_por_cortes(30, 6)[1] == "medio"        # ~4,3 s
    assert ec.ritmo_por_cortes(30, 0)[1] == "lento"        # plano único
    assert [ec.clasificar_aspecto(*x) for x in ((1080, 1920), (1080, 1350), (1080, 1080), (1920, 1080), (1000, 400))] \
        == ["9x16", "4x5", "1x1", "16x9", "otro"]


# ---------------------------------------------------------------- analizar
def _cuenta_fundador(citas_con=12, citas_sin=4):
    """6 anuncios con fundador (3 conceptos) a 50 €/cita y 6 con voz en off (3 conceptos) a 150 €/cita."""
    filas, etiquetas = [], {}
    for i in range(12):
        con = i < 6
        filas.append(anuncio(i + 1, angulo=f"angulo-{i % 3}", concepto=f"concepto-{'a' if con else 'b'}{i % 3}",
                             gasto=600, citas=citas_con if con else citas_sin))
        etiquetas[i + 1] = {"quien_habla": "fundador" if con else "voz-en-off"}
    return filas, etiquetas


def test_analizar_senal_en_la_capa_de_decision(ec, cliente):
    filas, etiquetas = _cuenta_fundador()
    escribir_registro(cliente, filas)
    etiquetar(ec, etiquetas)
    r = ec.analizar("acme", hoy=HOY)
    assert r["capa_decision"] == "citas" and r["anuncios"]["en_capa"] == 12
    f = next(x for x in r["coste"] if x["elemento"] == "quien_habla")
    assert f["razon"] == pytest.approx(1 / 3) and f["ic"][1] < 1 and f["q"] < 0.10
    assert f["estado"] == "senal-a-favor"
    assert any(x["elemento"] == "quien_habla = fundador" and x["evidencia"] == "[EMPIRICAL]"
               for x in r["sintesis"]["repetir"])
    assert "no causas" in r["lectura"]


def test_analizar_n_insuficiente(ec, cliente):
    filas, etiquetas = _cuenta_fundador(citas_con=1, citas_sin=4)
    escribir_registro(cliente, filas)
    etiquetar(ec, etiquetas)
    r = ec.analizar("acme", hoy=HOY)
    f = next(x for x in r["coste"] if x["elemento"] == "quien_habla")
    assert f["estado"] == "n-insuficiente" and "q" not in f
    assert not r["sintesis"]["repetir"] and not r["sintesis"]["dejar"]


def test_analizar_confundido_con_el_concepto(ec, cliente):
    filas, etiquetas = _cuenta_fundador()
    for f in filas[:6]:  # todos los de fundador en un único concepto
        f["angulo"], f["concepto"] = "tiempo-perdido", "caso-gestoria"
    filas[0]["veredicto"] = "ganador"
    escribir_registro(cliente, filas)
    etiquetar(ec, etiquetas)
    r = ec.analizar("acme", hoy=HOY)
    f = next(x for x in r["coste"] if x["elemento"] == "quien_habla")
    assert f["estado"] == "confundido"
    assert any(x["elemento"] == "quien_habla = fundador" and "otro concepto" in x["por"]
               for x in r["sintesis"]["probar"])


def test_analizar_excluye_inmaduros_y_baja_de_capa(ec, cliente):
    filas, etiquetas = _cuenta_fundador()
    for f in filas:
        f["leads"] = 30
    for f in filas[:8]:
        f["fecha"] = "2026-11-03"   # 6 días: sus citas no han madurado
    escribir_registro(cliente, filas)
    etiquetar(ec, etiquetas)
    r = ec.analizar("acme", hoy=HOY)
    # quedan 4 anuncios maduros con 16 citas (<20): baja a leads, que no necesita madurar
    assert r["capa_decision"] == "leads"
    assert r["capas_descartadas"][0] == {"capa": "citas", "eventos": 16, "anuncios": 4}
    assert any("capa superficial" in a for a in r["avisos"])
    r = ec.analizar("acme", hoy=HOY, capa="citas")
    assert r["anuncios"]["inmaduros"] == 8 and any("no han madurado" in a for a in r["avisos"])


def test_analizar_sin_capa_usa_ganadores_y_perdedores(ec, cliente):
    filas, etiquetas = [], {}
    for i in range(8):
        gana = i < 4
        filas.append(anuncio(i + 1, concepto=f"concepto-{i}", veredicto="ganador" if gana else "perdedor"))
        etiquetas[i + 1] = {"cifra": "gancho" if gana else "no"}
    escribir_registro(cliente, filas)
    etiquetar(ec, etiquetas)
    r = ec.analizar("acme", hoy=HOY)
    assert r["capa_decision"] is None and not r["coste"]
    f = next(x for x in r["ganadores_perdedores"] if x["elemento"] == "cifra")
    assert (f["ganadores"], f["perdedores"], f["estado"]) == ([4, 4], [0, 4], "mas-en-ganadores")
    assert f["p"] == pytest.approx(2 / 70) and f["ic"][0] > 0
    assert any(x["elemento"] == "cifra = gancho" for x in r["sintesis"]["repetir"])


def test_analizar_duda_no_cuenta_y_huecos(ec, cliente):
    filas, etiquetas = _cuenta_fundador()
    escribir_registro(cliente, filas)
    etiquetas[1] = {"quien_habla": "duda"}
    etiquetar(ec, etiquetas)
    r = ec.analizar("acme", hoy=HOY)
    f = next(x for x in r["coste"] if x["elemento"] == "quien_habla")
    assert f["anuncios"] == [5, 6]
    huecos = [x for x in r["sintesis"]["probar"] if "no probado" in x["por"]]
    assert any(x["elemento"] == "quien_habla = cliente" for x in huecos)
    assert all(x["evidencia"] == "[HYPOTHESIS]" for x in r["sintesis"]["probar"])


def test_atencion_hold_sin_videos_cortos(ec, cliente):
    filas = [anuncio(i + 1, concepto=f"c{i}", hook_rate=40 if i < 3 else 20, impresiones=20000) for i in range(6)]
    escribir_registro(cliente, filas)
    etiquetar(ec, {i + 1: {"texto_0s": "si" if i < 3 else "no"} for i in range(6)})
    r = ec.analizar("acme", hoy=HOY)
    f = next(x for x in r["atencion"] if x["metrica"] == "hook_rate" and x["elemento"] == "texto_0s")
    assert f["tasa"] == pytest.approx([0.4, 0.2]) and f["estado"] == "senal-a-favor"
    assert any(x["elemento"] == "texto_0s = si" and "atención" in x["por"] for x in r["sintesis"]["probar"])


def test_analizar_guarda_json_con_rutas_relativas(ec, cliente, capsys):
    filas, etiquetas = _cuenta_fundador()
    escribir_registro(cliente, filas)
    etiquetar(ec, etiquetas)
    codigo, out, _ = correr(ec, capsys, "analizar", "--cliente", "acme", "--fecha", "2026-11-09", "--guardar", "--json")
    datos = json.loads(out)
    assert codigo == 0 and datos["archivo"] == "clientes/acme/datos/analisis-creativo/2026-11-09_elementos.json"
    assert (cliente / "datos" / "analisis-creativo" / "2026-11-09_elementos.json").exists()
    assert "/Users/" not in out and str(cliente) not in out
    codigo, out, _ = correr(ec, capsys, "analizar", "--cliente", "acme", "--fecha", "2026-11-09")
    assert codigo == 0 and "Qué repetir" in out and "Qué probar" in out and "Qué dejar" in out


def test_errores_de_cli(ec, capsys):
    assert correr(ec, capsys, "analizar", "--cliente", "acme")[0] == 1          # registro vacío
    assert correr(ec, capsys, "analizar", "--cliente", "nadie")[0] == 2         # sin ficha
    assert correr(ec, capsys, "analizar", "--cliente", "acme", "--fecha", "9-11-2026")[0] == 1
    assert correr(ec, capsys, "suministro", "--cliente", "acme", "--gasto-mensual", "-5")[0] == 1


def test_valores_que_van_siempre_juntos_se_prueban_una_vez(ec, cliente):
    filas, etiquetas = _cuenta_fundador()
    for v in etiquetas.values():
        v["primer_fotograma"] = "cara" if v["quien_habla"] == "fundador" else "pantalla"
        v["persona"] = "ninguna" if v["quien_habla"] == "fundador" else "real"     # justo al revés
    escribir_registro(cliente, filas)
    etiquetar(ec, etiquetas)
    r = ec.analizar("acme", hoy=HOY)
    cara = next(x for x in r["coste"] if x["elemento"] == "primer_fotograma")
    assert cara["estado"] == "alias" and cara["alias_de"] == "quien_habla = fundador" and "q" not in cara
    persona = next(x for x in r["coste"] if x["elemento"] == "persona")
    assert persona["estado"] == "alias" and persona["alias_de"] == "quien_habla = fundador al revés"
    rep = next(x for x in r["coste"] if x["elemento"] == "quien_habla")
    assert "primer_fotograma = cara" in rep["juntos"] and rep["q"] == pytest.approx(rep["p"])   # una sola prueba
    assert "no se pueden separar" in r["sintesis"]["repetir"][0]["por"]
    assert not any(k.startswith("_") for x in r["coste"] + r["atencion"] for k in x)


# ---------------------------------------------------------------- diversidad
def test_diversidad_agrupa_por_nombre_etiquetas_y_huella(ec, cliente):
    filas = [anuncio(1, gasto=600), anuncio(2, hook="h2", gasto=300),                      # mismo concepto
             anuncio(3, angulo="miedo-rgpd", concepto="mapa-datos", gasto=100),
             anuncio(4, angulo="miedo-rgpd", concepto="que-preguntamos", gasto=50),          # mismas etiquetas que 3
             anuncio(5, angulo="precio", concepto="rangos", gasto=40),
             anuncio(6, angulo="adopcion", concepto="quien-lo-usa", gasto=10),               # huella casi igual a 5
             anuncio(7, formato="estatico", gasto=0.5)]                                     # otro soporte: aparte
    escribir_registro(cliente, filas)
    comun = {"estructura": "explicacion", "quien_habla": "fundador", "consciencia": "problema",
             "audiencia_nombrada": "sector", "primer_fotograma": "cara", "persona": "real", "tono": "didactico"}
    ec.preparar("acme")
    etiquetar(ec, {3: comun, 4: comun})
    ruta = cliente / "datos" / "elementos-creativos.csv"
    texto = ruta.read_text(encoding="utf-8")
    filas_csv = list(csv.DictReader(texto.splitlines()))
    for f in filas_csv:
        f["huella_visual"] = {ad_id(5): "00000000000000ff", ad_id(6): "00000000000000f0"}.get(f["ad_id"], "")
    with ruta.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=ec.COLUMNAS)
        w.writeheader()
        w.writerows(filas_csv)
    r = ec.diversidad("acme", hoy=HOY)
    grupos = [sorted(a["ad_id"] for a in g["anuncios"]) for g in r["cuenta"]["detalle"]]
    assert sorted([ad_id(1), ad_id(2)]) in grupos
    assert sorted([ad_id(3), ad_id(4)]) in grupos
    assert sorted([ad_id(5), ad_id(6)]) in grupos
    assert [ad_id(7)] in grupos
    assert r["cuenta"]["grupos"] == 4
    cuotas = [900 / 1100.5, 150 / 1100.5, 50 / 1100.5, 0.5 / 1100.5]
    assert r["cuenta"]["conceptos_efectivos"] == pytest.approx(1 / sum(c * c for c in cuotas))
    assert r["cuenta"]["cuota_top2"] == pytest.approx(900 / 1100.5)
    assert any("primer fotograma casi idéntico (4/64 bits)" in m for g in r["cuenta"]["detalle"] for m in g["motivos"])
    assert any("se llevan el 82 %" in a for a in r["avisos"])


def test_diversidad_dimension_sin_variedad(ec, cliente):
    escribir_registro(cliente, [anuncio(i + 1, concepto=f"c{i}") for i in range(4)])
    etiquetar(ec, {i + 1: {"quien_habla": "fundador"} for i in range(4)})
    r = ec.diversidad("acme", hoy=HOY)
    assert {"dimension": "quien_habla", "valor": "fundador", "cuota": 1.0} in r["dimensiones_sin_variedad"]
    assert "[OFFICIAL META]" in r["lectura"] and "[HYPOTHESIS]" in r["lectura"]


# ---------------------------------------------------------------- suministro
def test_suministro_formula(ec):
    r = ec.suministro("acme", gasto_mensual=3000, coste_objetivo=60, hoy=HOY)
    assert r["capa"] == "leads" and r["presupuesto_exploracion_mes"] == 900
    assert r["conceptos_nuevos_mes"] == {"prudente_3x": 5.0, "central_2_5x": 6.0, "optimista_2x": 7.5}
    assert r["recomendado"] == "5 conceptos nuevos al mes"
    assert r["techo_anuncios_nuevos_mes"]["maximo"] == round(4 * 30.4 / 7)   # 98,7 €/día: 2–4 por semana (13/05 §3)
    assert "[STRONG INFERENCE]" in r["formula"] and "[HYPOTHESIS]" in r["formula"]


def test_suministro_target_de_la_ficha_y_tope(ec, cliente):
    ficha = cliente / "ficha.md"
    ficha.write_text(ficha.read_text(encoding="utf-8") + "\n## Economía\n\n| Métrica | Break-even | Target |\n"
                     "|---|---|---|\n| CPL | 90 € | 60 € |\n| Coste por cita | 300 € | 200 € |\n", encoding="utf-8")
    r = ec.suministro("acme", hoy=HOY)
    assert r["coste_objetivo"] == 60 and "Target" in r["origen"]["coste"]
    assert r["gasto_mensual"] == pytest.approx(300 * 30.4) and any("máximo" in a for a in r["avisos"])
    r = ec.suministro("acme", gasto_mensual=3000, capa="citas", hoy=HOY)
    assert r["coste_objetivo"] == 200 and r["conceptos_nuevos_mes"]["prudente_3x"] == 1.5


def test_suministro_poco_presupuesto(ec):
    r = ec.suministro("acme", gasto_mensual=500, coste_objetivo=200, hoy=HOY)
    assert r["recomendado"] == "1 concepto nuevo cada 4 meses"
    assert any("no llega" in a for a in r["avisos"])


def test_suministro_sin_coste_objetivo(ec, capsys):
    codigo, _, err = correr(ec, capsys, "suministro", "--cliente", "acme", "--gasto-mensual", "3000")
    assert codigo == 1 and "--coste-objetivo" in err


def test_suministro_gasto_del_csv_de_meta(ec, cliente):
    import meta_ads
    ruta = cliente / "datos" / "meta-anuncios_2026-11-02_2026-11-08.csv"
    with ruta.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=meta_ads.COLUMNAS, extrasaction="ignore")
        w.writeheader()
        w.writerow({"ad_id": ad_id(1), "anuncio": "x", "desde": "2026-11-02", "hasta": "2026-11-08", "gasto": 700})
    r = ec.suministro("acme", meta_csv=str(ruta), coste_objetivo=50, hoy=HOY)
    assert r["gasto_mensual"] == pytest.approx(100 * 30.4)
    assert r["origen"]["gasto"].startswith("media diaria de clientes/acme/datos/")


def test_suministro_iteraciones_solo_de_ganadores_nuevos(ec, cliente):
    filas = [anuncio(1, veredicto="ganador"), anuncio(2, concepto="otro", veredicto="ganador")]
    filas[0]["fecha_veredicto"], filas[1]["fecha_veredicto"] = "2026-11-01", "2026-08-01"
    escribir_registro(cliente, filas)
    r = ec.suministro("acme", gasto_mensual=3000, coste_objetivo=60, hoy=HOY)
    assert (r["ganadores_activos"], r["ganadores_nuevos_30d"]) == (2, 1)
    assert (r["iteraciones_mes"]["minimo"], r["iteraciones_mes"]["maximo"]) == (3, 5)


# ---------------------------------------------------------------- retención
def test_retencion_agrega_y_diagnostica(ec, cliente):
    import meta_ads
    escribir_registro(cliente, [anuncio(1)])
    ec.preparar("acme")
    ruta = cliente / "datos" / "meta-anuncios_2026-11-02_2026-11-08.csv"
    base = {"desde": "2026-11-02", "hasta": "2026-11-08"}
    filas = [  # el anuncio 1 en dos países: se suman recuentos y se pondera la curva
        base | {"ad_id": ad_id(1), "anuncio": "a1", "pais": "ES", "impresiones": 6000, "vistas_3s": 1800,
                "thruplay": 300, "video_p25": 900, "video_p100": 90, "reproducciones": 2000, "tiempo_medio_s": 6,
                "curva_retencion": "100|80|50|40"},
        base | {"ad_id": ad_id(1), "anuncio": "a1", "pais": "PT", "impresiones": 4000, "vistas_3s": 1200,
                "thruplay": 200, "video_p25": 600, "video_p100": 60, "reproducciones": 1000, "tiempo_medio_s": 9,
                "curva_retencion": "100|70|60|50"},
        base | {"ad_id": ad_id(2), "anuncio": "a2", "impresiones": 10000, "vistas_3s": 3200, "thruplay": 600,
                "video_p25": 1500, "reproducciones": 3500},
        base | {"ad_id": ad_id(3), "anuncio": "a3", "impresiones": 10000, "vistas_3s": 1000, "thruplay": 100,
                "video_p25": 400, "reproducciones": 1200},
        base | {"ad_id": ad_id(4), "anuncio": "a4", "impresiones": 500, "vistas_3s": 300},        # pocas impresiones
    ]
    with ruta.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=meta_ads.COLUMNAS, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)
    r = ec.retencion("acme", str(ruta))
    por = {x["ad_id"]: x for x in r["anuncios"]}
    assert set(por) == {ad_id(1), ad_id(2), ad_id(3)}
    a1 = por[ad_id(1)]
    assert a1["hook_rate"] == pytest.approx(0.3) and a1["hold_rate"] == pytest.approx(500 / 3000)
    assert a1["retencion"]["p25"] == pytest.approx(0.5) and a1["retencion"]["p100"] == pytest.approx(0.05)
    assert a1["tiempo_medio_s"] == pytest.approx((6 * 2000 + 9 * 1000) / 3000)
    assert a1["curva"] == pytest.approx([100, 76.7, 53.3, 43.3], abs=0.05)
    assert a1["mayor_caida"]["entre"] == "1 s y 2 s"
    assert r["mediana_hook_rate"] == pytest.approx(0.3)
    assert por[ad_id(3)]["diagnostico"].startswith("apertura")              # 10 % < 50 % de la mediana


def test_retencion_csv_antiguo_avisa(ec, cliente, tmp_path):
    ruta = tmp_path / "antiguo.csv"
    ruta.write_text("ad_id,anuncio,impresiones,vistas_3s,thruplay\n120000000000001,a,5000,1500,200\n", encoding="utf-8")
    r = ec.retencion("acme", str(ruta))
    assert any("no trae columnas de retención" in a for a in r["avisos"])
    assert r["archivo"] == "antiguo.csv"


# ---------------------------------------------------------------- fotogramas
def _ff(*args) -> None:
    subprocess.run([FF, "-v", "error", "-y", *args], check=True, capture_output=True)


def _video_dos_planos(destino) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    _ff("-f", "lavfi", "-i", "color=c=red:s=360x640:d=3:r=10", "-f", "lavfi", "-i", "color=c=blue:s=360x640:d=3:r=10",
        "-filter_complex", "[0:v][1:v]concat=n=2:v=1[v]", "-map", "[v]", "-pix_fmt", "yuv420p", str(destino))


@con_ffmpeg
def test_fotogramas_de_video_local(ec, cliente, capsys):
    a = anuncio(1, formato="founder")
    escribir_registro(cliente, [a])
    base = a["nombre"].rsplit("_", 1)[0]
    _video_dos_planos(cliente / "creativos" / base / f"{base}_h1_9x16.mp4")
    (cliente / "creativos" / base / f"{base}_h2_9x16.mp4").write_bytes(b"no es este")
    codigo, out, _ = correr(ec, capsys, "fotogramas", "--cliente", "acme", "--ad", ad_id(1), "--fecha", "2026-11-09",
                            "--json")
    assert codigo == 0
    r = json.loads(out)["anuncios"][0]
    carpeta = cliente / "creativos" / "_fotogramas" / ad_id(1)
    for img in ("f0.jpg", "arranque.jpg", "hoja.jpg", "indice.json"):
        assert (carpeta / img).stat().st_size > 0
    indice = json.loads((carpeta / "indice.json").read_text(encoding="utf-8"))
    assert indice["duracion_s"] == pytest.approx(6, abs=0.2) and indice["relacion_aspecto"] == "9x16"
    assert len(indice["cortes"]) == 1 and indice["ritmo_sugerido"] == "medio"
    assert len(indice["huella_visual"]) == 16 and indice["fuente"] == "local"
    # el índice es ciego (sin nombre ni ruta, I6); el archivo de origen va en la salida de la orden
    assert "archivo_origen" not in indice and "nombre" not in indice
    assert r["archivo_origen"].endswith("_h1_9x16.mp4") and not r["archivo_origen"].startswith("/")
    assert r["imagenes"][0] == f"clientes/acme/creativos/_fotogramas/{ad_id(1)}/f0.jpg"
    fila = leer_elementos(cliente)[ad_id(1)]
    assert (fila["soporte"], fila["relacion_aspecto"], fila["fuente_visual"]) == ("video", "9x16", "local")
    assert float(fila["duracion_s"]) == pytest.approx(6, abs=0.2) and fila["huella_visual"] == indice["huella_visual"]
    assert fila["ritmo"] == ""            # la sugerencia no se escribe sola: la confirma quien etiqueta


@con_ffmpeg
def test_fotogramas_de_carrusel_y_cuadricula(ec, cliente, capsys):
    a = anuncio(1, formato="carrusel", concepto="pasos")
    b = anuncio(2, formato="founder")
    escribir_registro(cliente, [a, b])
    base = a["nombre"].rsplit("_", 1)[0]
    for i, color in enumerate(("white", "black", "green"), start=1):
        destino = cliente / "creativos" / base / f"{base}_h1_4x5_{i:02d}.png"
        destino.parent.mkdir(parents=True, exist_ok=True)
        _ff("-f", "lavfi", "-i", f"color=c={color}:s=1080x1350:d=1", "-frames:v", "1", str(destino))
    base_b = b["nombre"].rsplit("_", 1)[0]
    _video_dos_planos(cliente / "creativos" / base_b / f"{base_b}_h1_9x16.mp4")
    codigo, out, _ = correr(ec, capsys, "fotogramas", "--cliente", "acme", "--cuadricula", "--fecha", "2026-11-09",
                            "--json")
    r = json.loads(out)
    assert codigo == 0 and r["procesados"] == 2
    car = next(x for x in r["anuncios"] if x["ad_id"] == ad_id(1))
    assert car["soporte"] == "carrusel" and car["relacion_aspecto"] == "4x5"
    assert (cliente / "creativos" / "_fotogramas" / ad_id(1) / "hoja.jpg").exists()
    fila = leer_elementos(cliente)[ad_id(1)]
    assert (fila["soporte"], fila["ritmo"], fila["subtitulos"]) == ("carrusel", "no-aplica", "no-aplica")
    assert r["cuadricula"]["imagen"] == "clientes/acme/creativos/_fotogramas/cuadricula_2026-11-09.jpg"
    indice = (cliente / "creativos" / "_fotogramas" / "cuadricula_2026-11-09.md").read_text(encoding="utf-8")
    assert ad_id(1) in indice and ad_id(2) in indice


def test_fotogramas_sin_ffmpeg_es_configuracion(ec, cliente, capsys, monkeypatch):
    a = anuncio(1)
    escribir_registro(cliente, [a])
    base = a["nombre"].rsplit("_", 1)[0]
    (cliente / "creativos" / base).mkdir(parents=True)
    (cliente / "creativos" / base / f"{base}_h1_9x16.mp4").write_bytes(b"\x00")
    monkeypatch.setattr(ec, "_bin", lambda _n: None)
    codigo, _, err = correr(ec, capsys, "fotogramas", "--cliente", "acme", "--ad", ad_id(1))
    assert codigo == 2 and "FFmpeg" in err and "--api" in err


def test_fotogramas_sin_archivo_ni_api_falla_por_anuncio(ec, cliente, capsys):
    escribir_registro(cliente, [anuncio(1)])
    codigo, out, _ = correr(ec, capsys, "fotogramas", "--cliente", "acme", "--ad", ad_id(1))
    assert codigo == 1 and "--api" in out


def test_fotogramas_api_solo_lee_y_no_imprime_token_ni_urls(ec, cliente, capsys, monkeypatch):
    import meta_ads
    importlib.reload(meta_ads)
    monkeypatch.setattr(meta_ads.time, "sleep", lambda *_: None)
    monkeypatch.setenv("META_TOKEN", "token-secreto-de-prueba")
    monkeypatch.setattr(ec, "_bin", lambda _n: None)
    escribir_registro(cliente, [anuncio(1, formato="demo")])
    http = HttpSimulado()
    http.cuando("GET", rf"/{ad_id(1)}$", {"id": ad_id(1), "creative": {"id": "880001", "video_id": "990001"}})
    http.cuando("GET", r"/990001$", {"length": 42.5, "picture": "https://cdn.example/p.jpg?firma=x"})
    http.cuando("GET", r"/990001/thumbnails$", {"data": [{"uri": "https://cdn.example/otra.jpg", "is_preferred": False},
                                                          {"uri": "https://cdn.example/t.jpg", "is_preferred": True}]})
    monkeypatch.setattr(urllib.request, "urlopen", http)
    bajadas = []

    def descargar(url, destino, maximo):
        bajadas.append(url)
        destino.write_bytes(b"\xff\xd8\xff miniatura")

    monkeypatch.setattr(ec, "_descargar", descargar)
    codigo, out, err = correr(ec, capsys, "fotogramas", "--cliente", "acme", "--ad", ad_id(1), "--api", "--json")
    assert codigo == 0
    assert bajadas == ["https://cdn.example/t.jpg"]
    assert http.de("POST", ".") == [] and all(p["metodo"] == "GET" for p in http.peticiones)
    assert "token-secreto-de-prueba" not in out + err and "cdn.example" not in out + err
    indice = json.loads((cliente / "creativos" / "_fotogramas" / ad_id(1) / "indice.json").read_text(encoding="utf-8"))
    assert (indice["fuente"], indice["duracion_s"], indice["soporte"]) == ("api-miniatura", 42.5, "video")
    assert "cdn.example" not in json.dumps(indice)
    fila = leer_elementos(cliente)[ad_id(1)]
    assert (fila["duracion_s"], fila["fuente_visual"]) == ("42.5", "api-miniatura")
    assert any("miniatura" in a for a in json.loads(out)["avisos"])


# ---------------------------------------------------------------- I6: revisión de corrección
def _ultima_exportacion(cliente, ids, desde="2026-09-15", hasta="2026-11-08"):
    ruta = cliente / "datos" / "registro-creativo_ultima-exportacion.json"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps({"fecha": "2026-11-09", "desde": desde, "hasta": hasta, "meta": "meta.csv",
                                "ad_ids": sorted(ids)}), encoding="utf-8")


def test_elegir_capa_con_madurez_por_capa(ec, cliente):
    """Hallazgo 3: a los 20 días los clientes de pago de una venta B2B no han madurado (56 días): se decide con citas."""
    filas, etiquetas = _cuenta_fundador()
    for f in filas:
        f["fecha"], f["clientes_pago"] = "2026-10-20", 2
    escribir_registro(cliente, filas)
    etiquetar(ec, etiquetas)
    r = ec.analizar("acme", hoy=HOY)
    assert r["capa_decision"] == "citas"
    assert r["capas_descartadas"][0] == {"capa": "clientes_pago", "eventos": 0, "anuncios": 0}
    assert ec.analizar("acme", hoy=HOY, madurez_cli=["clientes_pago=14"])["capa_decision"] == "clientes_pago"


def test_analizar_sin_fecha_fiable_cuenta_como_inmaduro(ec, cliente):
    """Hallazgo 17: sin fecha no se sabe si las citas han madurado; antes contaba como maduro."""
    filas, etiquetas = _cuenta_fundador()
    for f in filas:
        f["fecha"], f["leads"] = "", 30
    escribir_registro(cliente, filas)
    etiquetar(ec, etiquetas)
    r = ec.analizar("acme", hoy=HOY)
    assert r["capa_decision"] == "leads"
    assert any("fecha fiable" in a for a in r["avisos"]) or r["capas_descartadas"][0]["capa"] == "citas"


def test_solo_los_anuncios_de_la_ultima_exportacion(ec, cliente):
    """Hallazgo 19: un anuncio de mayo que no viene en la exportación de noviembre no entra en el análisis."""
    filas = [anuncio(1, veredicto="ganador", concepto="mayo", fecha="2026-05-04", gasto=900),
             anuncio(2, veredicto="ganador", concepto="nov-a", fecha="2026-09-20"),
             anuncio(3, veredicto="ganador", concepto="nov-b", fecha="2026-09-20")]
    escribir_registro(cliente, filas)
    _ultima_exportacion(cliente, [ad_id(2), ad_id(3)])
    r = ec.analizar("acme", hoy=HOY)
    assert r["anuncios"]["con_gasto"] == 2 and r["anuncios"]["fuera_de_exportacion"] == 1
    assert any("última exportación" in a for a in r["avisos"])
    assert ec.suministro("acme", gasto_mensual=3000, coste_objetivo=60, hoy=HOY)["ganadores_activos"] == 2
    assert ec.preparar("acme")["filas"] == 2
    assert {p["ad_id"] for p in ec.pendientes("acme")} == {ad_id(2), ad_id(3)}
    assert {x["ad_id"] for x in ec.fotogramas("acme", hoy=HOY)["anuncios"]} == {ad_id(2), ad_id(3)}
    assert ec.diversidad("acme", hoy=HOY)["cuenta"]["anuncios"] == 2
    assert ec.preparar("acme", todos=True)["filas"] == 3   # --todos: todo el registro


def test_la_cohorte_empieza_en_el_inicio_del_periodo(ec, cliente):
    """Un anuncio de septiembre en una exportación que empieza hace 6 días: sus citas del periodo no han madurado."""
    filas, etiquetas = _cuenta_fundador()
    for f in filas:
        f["leads"] = 30
    escribir_registro(cliente, filas)
    etiquetar(ec, etiquetas)
    _ultima_exportacion(cliente, [f["ad_id"] for f in filas], desde="2026-11-03")
    assert ec.analizar("acme", hoy=HOY)["capa_decision"] == "leads"


def test_suministro_explorar_explotar_con_coma(ec, cliente):
    """Bajo: «explorar_explotar: 0,5» pasaba a 0,3 sin avisar."""
    ficha = cliente / "ficha.md"
    ficha.write_text(ficha.read_text(encoding="utf-8").replace("explorar_explotar: 0.3", "explorar_explotar: 0,5"),
                     encoding="utf-8")
    r = ec.suministro("acme", gasto_mensual=6000, coste_objetivo=60, hoy=HOY)
    assert r["explorar_explotar"] == 0.5 and r["presupuesto_exploracion_mes"] == 3000
    ficha.write_text(ficha.read_text(encoding="utf-8").replace("explorar_explotar: 0,5", "explorar_explotar: mucho"),
                     encoding="utf-8")
    with pytest.raises(ec.ErrorUsuario, match="explorar_explotar"):
        ec.suministro("acme", gasto_mensual=6000, coste_objetivo=60, hoy=HOY)


def test_indice_de_fotogramas_es_ciego(ec, cliente, monkeypatch):
    """Bajo: el índice que ve el etiquetador no lleva el nombre del anuncio ni la ruta (llevan ángulo y concepto)."""
    a = anuncio(1, formato="demo")
    escribir_registro(cliente, [a])
    base = a["nombre"].rsplit("_", 1)[0]
    (cliente / "creativos" / base).mkdir(parents=True)
    (cliente / "creativos" / base / f"{base}_h1_9x16.mp4").write_bytes(b"\x00")
    monkeypatch.setattr(ec, "_bin", lambda _n: "/usr/bin/true")

    def extraer(ruta, destino):
        destino.mkdir(parents=True, exist_ok=True)
        return {"duracion_s": 6.0, "ancho": 1080, "alto": 1920, "cortes": [], "ritmo_sugerido": "lento",
                "imagenes": {"f0": "f0.jpg"}}

    monkeypatch.setattr(ec, "extraer_video", extraer)
    r = ec.fotogramas("acme", ads=[ad_id(1)], hoy=HOY)
    assert r["procesados"] == 1
    indice = (cliente / "creativos" / "_fotogramas" / ad_id(1) / "indice.json").read_text(encoding="utf-8")
    assert "tiempo-perdido" not in indice and "caso-gestoria" not in indice
    assert "nombre" not in json.loads(indice) and "archivo_origen" not in json.loads(indice)
