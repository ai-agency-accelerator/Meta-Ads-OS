"""control_publicacion: nomenclatura (contrato §7) y veredicto de políticas del LEEME.md antes de publicar."""
from __future__ import annotations

import json

import pytest

from ayudas_hooks import CUENTA, decision, leer_log, motivo, pre_bash, pre_mcp

T = "mcp__meta-ads__"
NOMBRE = "20261110_tiempo-perdido_demo-antes-despues_demo_h2"


def _pieza(instancia, veredicto: str | None, carpeta: str = "2026-11-10_demo-antes-despues"):
    destino = instancia / "clientes" / "acme" / "creativos" / carpeta
    destino.mkdir(parents=True, exist_ok=True)
    linea = f"- **Veredicto de políticas:** {veredicto} · 2026-11-10 · revisor-politicas\n" if veredicto else \
        "- Coste: 1,20 $\n"
    # El comentario de la plantilla menciona los valores: no debe confundirse con la línea real.
    comentario = "<!-- Veredicto ∈ OK | OK con cambios | NO publicar (lo escribe revisor-politicas). -->\n"
    (destino / "LEEME.md").write_text(f"# {NOMBRE}\n\n{comentario}\n- **Estado:** listo\n{linea}- QA: aprobado\n",
                                      encoding="utf-8")
    return destino


def _crear_anuncio(instancia, nombre=NOMBRE):
    return pre_mcp(instancia, T + "ads_create_ad", {"ad_account_id": CUENTA, "name": nombre,
                                                    "adset_id": "120000000000000010",
                                                    "creative": {"creative_id": "120000000000000020"}})


@pytest.mark.parametrize("veredicto", ["OK", "OK con cambios aplicados", "ok con cambios aplicados"])
def test_anuncio_con_nombre_valido_y_politicas_ok_pasa(instancia, correr, veredicto):
    _pieza(instancia, veredicto)
    assert correr("control_publicacion", _crear_anuncio(instancia)) is None


def test_lecturas_y_otras_herramientas_no_deciden(instancia, correr):
    assert correr("control_publicacion", pre_mcp(instancia, T + "ads_get_ad_entities", {"ad_account_id": CUENTA})) \
        is None
    assert correr("control_publicacion", pre_bash(instancia, "python3 -I herramientas/meta_ads.py crear "
                                                             "clientes/acme/planes/x.json --simular")) is None


def test_sin_leeme_o_sin_veredicto_pregunta(instancia, correr):
    salida = correr("control_publicacion", _crear_anuncio(instancia))
    assert decision(salida) == "ask" and "revisor-politicas" in motivo(salida)
    _pieza(instancia, None)
    salida = correr("control_publicacion", _crear_anuncio(instancia))
    assert decision(salida) == "ask" and "no tiene veredicto" in motivo(salida)


@pytest.mark.parametrize("veredicto", ["OK con cambios", "pendiente", "Aprobado", "OK ✅", "revisar el claim"])
def test_veredicto_pendiente_o_desconocido_pregunta(instancia, correr, veredicto):
    """Contrato §6: «OK con cambios» (sin aplicar), «pendiente» y cualquier otro texto piden confirmación."""
    _pieza(instancia, veredicto)
    salida = correr("control_publicacion", _crear_anuncio(instancia))
    assert decision(salida) == "ask" and veredicto.lower() in motivo(salida)


def test_campana_y_conjunto_fuera_de_nomenclatura_preguntan(instancia, correr):
    salida = correr("control_publicacion", pre_mcp(instancia, T + "ads_create_campaign",
                                                   {"ad_account_id": CUENTA, "name": "Campaña noviembre"}))
    assert decision(salida) == "ask" and "ES_LEADS_ADQ_HV" in motivo(salida)
    assert correr("control_publicacion", pre_mcp(instancia, T + "ads_create_ad_set",
                                                 {"ad_account_id": CUENTA, "name": "BROAD-A+_LEAD"})) is None


def test_nombre_de_anuncio_invalido_se_bloquea_con_propuesta(instancia, correr):
    salida = correr("control_publicacion", _crear_anuncio(instancia, "2026-11-10_Tiempo Perdido_Demo_DEMO_H2"))
    assert decision(salida) == "deny"
    assert "Propuesta: 20261110_tiempo-perdido_demo_demo_h2" in motivo(salida)


@pytest.mark.parametrize("veredicto", ["NO publicar", "NO publicar (promesa de ingresos)"])
def test_politicas_no_publicar_se_bloquea(instancia, correr, veredicto):
    _pieza(instancia, veredicto)
    salida = correr("control_publicacion", _crear_anuncio(instancia))
    assert decision(salida) == "deny" and "NO publicar" in motivo(salida)


def test_la_carpeta_con_el_nombre_base_manda(instancia, correr):
    """creativos/<nombre-base>/ (nombre del anuncio sin _h<n>) gana a otra pieza del mismo concepto."""
    _pieza(instancia, "NO publicar", carpeta="2026-11-10_demo-antes-despues")
    _pieza(instancia, "OK", carpeta="20261110_tiempo-perdido_demo-antes-despues_demo")
    assert correr("control_publicacion", _crear_anuncio(instancia)) is None


def _plan(instancia, nombre_anuncio: str, video: str):
    planes = instancia / "clientes" / "acme" / "planes"
    planes.mkdir(exist_ok=True)
    plan = {"cliente": "acme", "campana": {"nombre": "ES_LEADS_ADQ_HV", "objetivo": "OUTCOME_LEADS"},
            "conjuntos": [{"nombre": "BROAD_LEAD", "presupuesto_diario_eur": 30,
                           "anuncios": [{"nombre": nombre_anuncio, "video": video, "texto": "Texto de prueba"}]}]}
    (planes / "noviembre.json").write_text(json.dumps(plan), encoding="utf-8")
    return "python3 -I herramientas/meta_ads.py crear clientes/acme/planes/noviembre.json"


def test_plan_por_bash(instancia, correr):
    carpeta = _pieza(instancia, "OK")
    orden = _plan(instancia, NOMBRE, str(carpeta / "final_9x16.mp4"))
    assert correr("control_publicacion", pre_bash(instancia, orden)) is None
    orden = _plan(instancia, "Hook 2 demo", "../creativos/2026-11-10_demo-antes-despues/final.mp4")
    assert decision(correr("control_publicacion", pre_bash(instancia, orden))) == "deny"


def test_plan_por_bash_con_comodin_que_da_meta_ads(instancia, correr):
    # Hallazgo 3: un comodín que da un único script se revisa como ese script (y el `cd` se sigue).
    (instancia / "herramientas").mkdir(exist_ok=True)
    (instancia / "herramientas" / "meta_ads.py").write_text("# falso\n", encoding="utf-8")
    orden = _plan(instancia, "Hook 2 demo", "../creativos/2026-11-10_demo-antes-despues/final.mp4")
    orden = orden.replace("herramientas/meta_ads.py", "herramientas/meta_ad?.py")
    assert decision(correr("control_publicacion", pre_bash(instancia, orden))) == "deny"
    orden = "cd herramientas && python3 -I meta_ad?.py crear ../clientes/acme/planes/noviembre.json"
    assert decision(correr("control_publicacion", pre_bash(instancia, orden))) == "deny"


def test_plan_con_pieza_rechazada(instancia, correr):
    carpeta = _pieza(instancia, "NO publicar")
    orden = _plan(instancia, NOMBRE, "../creativos/" + carpeta.name + "/final.mp4")
    assert decision(correr("control_publicacion", pre_bash(instancia, orden))) == "deny"


def test_fallo_interno_deja_pasar(instancia, en_proceso, monkeypatch):
    import control_publicacion

    def rota(*a, **k):
        raise OSError("fallo simulado")

    monkeypatch.setattr(control_publicacion, "revisar_politicas", rota)
    codigo, salida = en_proceso("control_publicacion", _crear_anuncio(instancia))
    assert codigo == 0 and salida is None
    assert leer_log(instancia, "hooks.jsonl")[-1]["hook"] == "control_publicacion"


@pytest.mark.parametrize("sufijo", ["_9x16", "_4x5", "_1x1"])
def test_creatividad_con_sufijo_de_formato(instancia, correr, sufijo):
    """cutkit y render.py añaden el formato al archivo: la creatividad con ese nombre se reconoce igual."""
    _pieza(instancia, "OK", carpeta="20261110_tiempo-perdido_demo-antes-despues_demo")
    salida = correr("control_publicacion", pre_mcp(instancia, T + "ads_create_creative",
                                                   {"ad_account_id": CUENTA, "name": NOMBRE + sufijo}))
    assert salida is None
