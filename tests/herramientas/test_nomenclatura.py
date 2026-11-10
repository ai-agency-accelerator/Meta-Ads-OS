import pathlib
import subprocess
import sys
from datetime import date

import pytest

import nomenclatura as nom

HERRAMIENTA = pathlib.Path(__file__).resolve().parents[2] / "herramientas" / "nomenclatura.py"


def test_parsear_anuncio_valido():
    p = nom.parsear_anuncio("20261110_tiempo-perdido_demo-antes-despues_demo_h2")
    assert p == {"fecha": date(2026, 11, 10), "angulo": "tiempo-perdido", "concepto": "demo-antes-despues",
                 "formato": "demo", "hook": "h2"}
    assert nom.parsear_anuncio("20261110_a_b_estatico_h2-c3")["hook"] == "h2-c3"


@pytest.mark.parametrize("nombre", [
    "20261131_a_b_demo_h1",                 # fecha imposible
    "20261110_Tiempo_b_demo_h1",            # mayúsculas
    "20261110_a_b_video_h1",                # formato fuera de la lista
    "20261110_a_b_demo_h0",                 # hook 0
    "20261110_a_b_demo",                    # faltan partes
    "2026111_a_b_demo_h1",                  # fecha corta
    "",
])
def test_parsear_anuncio_invalido(nombre):
    assert nom.parsear_anuncio(nombre) is None


def test_parsear_tolera_copia_pero_validar_no():
    nombre = "20261110_tiempo-perdido_demo_demo_h2 - Copia 2"
    assert nom.parsear_anuncio(nombre)["concepto"] == "demo"
    assert nom.parsear_anuncio("20261110_a_b_ugc_h1 – Copy")["formato"] == "ugc"
    ok, msg = nom.validar("anuncio", nombre)
    assert not ok and "copia" in msg and "Sugerencia: 20261110_tiempo-perdido_demo_demo_h2" in msg


def test_generar_anuncio_normaliza():
    n = nom.generar_anuncio(date(2026, 11, 10), "Tiempo perdido", "Demo antes/después", "Estático", 2, 1)
    assert n == "20261110_tiempo-perdido_demo-antes-despues_estatico_h2-c1"
    assert nom.parsear_anuncio(n)
    assert nom.generar_anuncio(date(2026, 1, 5), "Niño pequeño", "año", "carousel", 1) == \
        "20260105_nino-pequeno_ano_carrusel_h1"


@pytest.mark.parametrize("kwargs", [
    {"formato": "video"}, {"hook": 0}, {"hook": True}, {"angulo": "!!!"}, {"cuerpo": 0},
])
def test_generar_anuncio_errores(kwargs):
    base = {"fecha": date(2026, 11, 10), "angulo": "a", "concepto": "b", "formato": "demo", "hook": 1}
    with pytest.raises(ValueError):
        nom.generar_anuncio(**{**base, **kwargs})


def test_validar_anuncio_con_sugerencias():
    ok, msg = nom.validar("anuncio", "20261110_tiempo-perdido_demo-antes-despues_demo_h2")
    assert ok and msg.startswith("OK")
    ok, msg = nom.validar("anuncio", "2026-11-10_Tiempo Perdido_Demo_Static_H2")
    assert not ok and "Sugerencia: 20261110_tiempo-perdido_demo_estatico_h2" in msg
    ok, msg = nom.validar("anuncio", "20261110_tiempo_perdido_demo_demo_h2")
    assert not ok and "5 partes" in msg and "Sugerencia" not in msg  # ambiguo: no se inventa
    ok, msg = nom.validar("anuncio", "20261110_a_b_video_h1")
    assert not ok and "Formato 'video'" in msg


def test_validar_campana():
    assert nom.validar("campana", "ES_LEADS_ADQ_HV")[0]
    assert nom.validar("campana", "ES-MX_SALES_TEST_CC")[0]
    ok, msg = nom.validar("campana", "es_ventas_adq_costcap")
    assert not ok and "Sugerencia: ES_SALES_ADQ_CC" in msg
    ok, msg = nom.validar("campana", "ES_LEADS_ADQ_XX")
    assert not ok and "Puja 'XX'" in msg
    ok, msg = nom.validar("campana", "ES_LEADS_ADQ")
    assert not ok and "4 partes" in msg


def test_validar_conjunto():
    assert nom.validar("conjunto", "BROAD-A+_LEAD")[0]
    ok, msg = nom.validar("conjunto", "Broad A+_lead")
    assert not ok and "Sugerencia: BROAD-A+_LEAD" in msg
    assert not nom.validar("conjunto", "BROAD")[0]


def test_validar_nivel_y_vacio():
    assert nom.validar("otro", "x") == (False, "Nivel 'otro' no válido: usa campana, conjunto, anuncio")
    assert not nom.validar("anuncio", "  ")[0]
    assert not nom.validar("anuncio", " 20261110_a_b_demo_h1")[0]  # espacios


def test_cli_validar_con_python_aislado():
    ok = subprocess.run([sys.executable, "-I", str(HERRAMIENTA), "validar", "anuncio",
                         "20261110_tiempo-perdido_demo-antes-despues_demo_h2"], capture_output=True, text=True)
    assert ok.returncode == 0 and ok.stdout.startswith("OK")
    mal = subprocess.run([sys.executable, "-I", str(HERRAMIENTA), "validar", "campana", "es_leads"],
                         capture_output=True, text=True)
    assert mal.returncode == 1 and "4 partes" in mal.stdout


def test_cli_generar_y_errores(capsys):
    assert nom.main(["generar", "--fecha", "2026-11-10", "--angulo", "Á", "--concepto", "b", "--formato", "ugc",
                     "--hook", "3", "--json"]) == 0
    assert '"nombre": "20261110_a_b_ugc_h3"' in capsys.readouterr().out
    assert nom.main(["generar", "--fecha", "2026-13-10", "--angulo", "a", "--concepto", "b", "--formato", "ugc",
                     "--hook", "3"]) == 1
    with pytest.raises(SystemExit) as e:
        nom.main(["validar", "nivel-raro", "x"])
    assert e.value.code == 1
