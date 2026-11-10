import json
import os
import pathlib
import re
import subprocess
import sys
from datetime import date

import estado

HERRAMIENTA = pathlib.Path(__file__).resolve().parents[2] / "herramientas" / "estado.py"
HOY = date(2026, 11, 11)  # miércoles: la última semana completa es 2026-11-02 → 2026-11-08 (ISO 2026-W45)


def _marcar(raiz, hasta_id=None, ids=()):
    """Marca todos los puntos hasta `hasta_id` (incluido) o los ids concretos."""
    f = raiz / "clientes" / "acme" / "estado.md"
    lineas, marcando = [], hasta_id is not None
    for l in f.read_text(encoding="utf-8").splitlines():
        m = re.search(r"\[ \] (F\d\.[\w-]+)", l)
        if m and (marcando or m.group(1) in ids):
            l = l.replace("[ ]", "[x]", 1)
            if m.group(1) == hasta_id:
                marcando = False
        lineas.append(l)
    f.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def _cl(raiz, filas):
    f = raiz / "clientes" / "acme" / "change-log.md"
    f.write_text(f.read_text(encoding="utf-8") + "".join(filas), encoding="utf-8")


def test_resumen_forma_exacta_y_fase_inicial(instancia):
    r = estado.resumen(HOY)
    assert r["fecha"] == "2026-11-11"
    assert len(r["clientes"]) == 1
    c = r["clientes"][0]
    assert set(c) == {"slug", "fase", "pendientes", "evaluaciones_vencidas", "informe_semanal_pendiente",
                      "brief_hoy", "cola_produccion"}
    assert c["slug"] == "acme" and c["fase"] == "F0"
    assert c["pendientes"] == ["F0.ficha", "F0.economia", "F0.oferta", "F0.funnel", "F0.topes"]
    assert c["evaluaciones_vencidas"] == [] and c["informe_semanal_pendiente"] is False
    assert c["brief_hoy"] is False and c["cola_produccion"] == 0


def test_fase_avanza_y_completa(instancia):
    _marcar(instancia, "F0.topes")
    c = estado.resumen(HOY)["clientes"][0]
    assert c["fase"] == "F1" and c["pendientes"][0] == "F1.portfolio"
    _marcar(instancia, "F6.condiciones")
    c = estado.resumen(HOY)["clientes"][0]
    assert c["fase"] == "F6" and c["pendientes"] == []


def test_fase_con_huecos_en_fases_anteriores(instancia):
    _marcar(instancia, ids=("F0.ficha", "F0.economia", "F0.oferta", "F0.topes", "F1.cuenta"))
    c = estado.resumen(HOY)["clientes"][0]
    assert c["fase"] == "F0" and c["pendientes"] == ["F0.funnel"]


def test_evaluaciones_vencidas(instancia):
    _cl(instancia, [
        "| 2026-11-01 10:00 | operador-meta | conjunto | 120000000000001 | 50 → 70 €/día | escalar | CPA ≤ 40 | 2026-11-08 | |\n",
        "| 2026-11-04 10:00 | yo | anuncio | 120000000000002 | activo → pausa | kill 3× CPA | — | 2026-11-11 |  |\n",
        "| 2026-11-05 10:00 | yo | anuncio | 120000000000003 | nuevo hook | test | CTR | 2026-11-12 | |\n",
        "| 2026-10-20 10:00 | yo | campaña | 120000000000004 | puja | test | CPA | 2026-10-27 | Funcionó: CPA −12 % |\n",
        "| 2026-10-21 10:00 | yo | campaña | 120000000000005 | texto con \\| barra | x | y | 2026-10-28 (7 días) | |\n",
    ])
    v = estado.resumen(HOY)["clientes"][0]["evaluaciones_vencidas"]
    assert [e["objeto"] for e in v] == ["120000000000005", "120000000000001", "120000000000002"]
    assert v[0] == {"fecha": "2026-10-28", "objeto": "120000000000005", "cambio": "texto con | barra"}
    assert v[1]["cambio"] == "50 → 70 €/día"


def test_informe_semanal(instancia):
    assert estado.semana_analizada(HOY) == (date(2026, 11, 2), date(2026, 11, 8))
    _marcar(instancia, "F4.activa")
    assert estado.resumen(HOY)["clientes"][0]["informe_semanal_pendiente"] is True
    informes = instancia / "clientes" / "acme" / "informes"
    (informes / "diario").mkdir(parents=True)
    (informes / "diario" / "2026-W45.md").write_text("no cuenta", encoding="utf-8")
    assert estado.resumen(HOY)["clientes"][0]["informe_semanal_pendiente"] is True
    (informes / "semanal").mkdir()
    (informes / "semanal" / "2026-W45.md").write_text("ok", encoding="utf-8")
    assert estado.resumen(HOY)["clientes"][0]["informe_semanal_pendiente"] is False
    # el de la semana anterior no vale
    (informes / "semanal" / "2026-W45.md").unlink()
    (informes / "semanal" / "2026-W44.md").write_text("viejo", encoding="utf-8")
    assert estado.resumen(HOY)["clientes"][0]["informe_semanal_pendiente"] is True
    # con fecha en el nombre, entre el domingo de cierre y hoy
    (informes / "informe-semanal-2026-11-09.md").write_text("ok", encoding="utf-8")
    assert estado.resumen(HOY)["clientes"][0]["informe_semanal_pendiente"] is False


def test_brief_hoy(instancia):
    d = instancia / "clientes" / "acme" / "informes" / "diario"
    d.mkdir(parents=True)
    (d / "2026-11-10.md").write_text("ayer", encoding="utf-8")
    assert estado.resumen(HOY)["clientes"][0]["brief_hoy"] is False
    (d / "2026-11-11.md").write_text("hoy", encoding="utf-8")
    assert estado.resumen(HOY)["clientes"][0]["brief_hoy"] is True


def test_cola_produccion(instancia):
    """§6: cuentan las piezas cuyo LEEME.md dice `- **Estado:** borrador` o `listo`; manda el LEEME."""
    creativos = instancia / "clientes" / "acme" / "creativos"
    leemes = {
        "20261101_borrador": "# Pieza\n\n- **Estado:** borrador\n- **Veredicto de políticas:** pendiente\n",
        "20261102_listo": "# Pieza\r\n- **Estado:** listo \r\n- **Veredicto de políticas:** OK\r\n",  # CRLF de Windows
        "20261103_publicado": "# Pieza\n- **Estado:** publicado\n",
        "20261104_descartado": "# Pieza\n- **Estado:** descartado\n",
        "20261105_sin-formato": "# Pieza\nEstado: listo\n- **Estado:** listo para revisar\n",
        "_lotes/2026-11-01_lote-a": "- **Estado:** borrador\n",
        "_plantilla": "- **Estado:** borrador\n",
        ".oculta": "- **Estado:** listo\n",
    }
    for nombre, texto in leemes.items():
        (creativos / nombre).mkdir(parents=True)
        (creativos / nombre / "LEEME.md").write_text(texto, encoding="utf-8", newline="")
    (creativos / "2026-11-05-estudio").mkdir()  # carpeta del workflow estudio-creativo, sin LEEME.md
    (creativos / "suelto.md").write_text("- **Estado:** listo\n", encoding="utf-8")
    assert estado.cola_produccion(instancia / "clientes" / "acme") == 2
    # el registro creativo no manda: una pieza en `listo` citada en ruta_creativo sigue en la cola
    reg = instancia / "clientes" / "acme" / "registro-creativo.csv"
    cab = reg.read_text(encoding="utf-8").strip().split(",")
    fila = {k: "" for k in cab} | {"ad_id": "120000000000001", "ruta_creativo": "creativos/20261102_listo/v.mp4"}
    reg.write_text(",".join(cab) + "\n" + ",".join(fila[k] for k in cab) + "\n", encoding="utf-8")
    assert estado.resumen(HOY)["clientes"][0]["cola_produccion"] == 2


def test_clientes_en_pausa_y_filtro(instancia):
    import _comun
    pausa = instancia / "clientes" / "nimbo"
    pausa.mkdir()
    ficha = (instancia / "clientes" / "acme" / "ficha.md").read_text(encoding="utf-8")
    (pausa / "ficha.md").write_text(ficha.replace("slug: acme", "slug: nimbo").replace("estado: activo",
                                                                                        "estado: pausa"),
                                    encoding="utf-8")
    (instancia / "clientes" / "README.md").write_text("no es un cliente", encoding="utf-8")
    assert [c["slug"] for c in estado.resumen(HOY)["clientes"]] == ["acme"]
    assert [c["slug"] for c in estado.resumen(HOY, todos=True)["clientes"]] == ["acme", "nimbo"]
    nimbo = estado.resumen(HOY, cliente="nimbo")["clientes"]
    assert nimbo[0]["slug"] == "nimbo" and nimbo[0]["fase"] == "F0"  # sin estado.md: lista de la plantilla
    assert _comun.RAIZ == instancia


def test_main_json_y_errores(instancia, capsys):
    assert estado.main(["resumen", "--fecha", "2026-11-11", "--json"]) == 0
    datos = json.loads(capsys.readouterr().out)
    assert datos["clientes"][0]["slug"] == "acme"
    assert estado.main(["resumen", "--fecha", "11/11/2026"]) == 1
    assert estado.main(["resumen", "--cliente", "no-existe"]) == 1
    assert estado.main(["resumen", "--cliente", "acme"]) == 0
    assert "acme · F0" in capsys.readouterr().out


def test_cli_aislado_sobre_la_instancia(instancia):
    env = {**os.environ, "META_ADS_OS_RAIZ": str(instancia)}
    r = subprocess.run([sys.executable, "-I", str(HERRAMIENTA), "resumen", "--json", "--fecha", "2026-11-11"],
                       capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr
    datos = json.loads(r.stdout)
    assert datos["fecha"] == "2026-11-11" and datos["clientes"][0]["fase"] == "F0"


# ---------------------------------------------------------------- I6 (revisión independiente)

def test_i6_plantilla_trae_los_ids_del_contrato():
    """Hallazgo 30d: `F0.iman` y `F3.prueba` (contrato §4) están en la plantilla, como hitos opcionales."""
    plantilla = HERRAMIENTA.parents[1] / "plantillas" / "cliente" / "estado.md"
    texto = plantilla.read_text(encoding="utf-8")
    ids = [i for i, _ in estado.leer_items(texto)]
    assert "F0.iman" in ids and "F3.prueba" in ids
    assert {i for i in ids if estado.es_opcional(texto, i)} == {"F0.iman", "F3.prueba"}


def test_i6_opcionales_no_cuentan_como_pendientes():
    texto = ("- [x] F0.ficha — Ficha (verifica: archivo)\n"
             "- [ ] F0.iman — Imán de entrada (verifica: archivo). Opcional.\n"
             "- [ ] F1.cuenta — Cuenta (verifica: mcp)\n")
    assert estado.fase_y_pendientes(estado.leer_items(texto)) == ("F1", ["F1.cuenta"])
    todo = texto.replace("[ ] F1.cuenta", "[x] F1.cuenta")
    assert estado.fase_y_pendientes(estado.leer_items(todo)) == ("F6", [])
