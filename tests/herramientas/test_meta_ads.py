"""meta_ads.py: plan simulado sin red, creación en pausa, mejoras apagadas, topes, confirmación e idempotencia."""
from __future__ import annotations

import copy
import pathlib
import csv
import importlib
import json
import sys
import types
import urllib.request

import pytest

from http_simulado import HttpSimulado

RAIZ_PRODUCTO = __import__("pathlib").Path(__file__).resolve().parents[2]
PLANTILLA = RAIZ_PRODUCTO / "plantillas" / "plan-campana.json"


@pytest.fixture
def meta(instancia, monkeypatch):
    import meta_ads as modulo
    modulo = importlib.reload(modulo)
    monkeypatch.setattr(modulo.time, "sleep", lambda *_: None)
    monkeypatch.delenv("META_TOKEN_ACME", raising=False)
    monkeypatch.setenv("META_TOKEN", "token-global")
    return modulo


@pytest.fixture
def ficha_real(instancia):
    """La ficha de acme con IDs con forma real (cortos para no parecer una fuga)."""
    f = instancia / "clientes" / "acme" / "ficha.md"
    texto = (f.read_text(encoding="utf-8").replace("act_000000000000000", "act_12345")
             .replace('dataset: "000000000000000"', 'dataset: "111111"').replace('pagina: ""', 'pagina: "222222"')
             .replace('instagram: ""', 'instagram: "333333"'))
    f.write_text(texto, encoding="utf-8")
    return f


def _http(monkeypatch, http: HttpSimulado) -> HttpSimulado:
    monkeypatch.setattr(urllib.request, "urlopen", http)
    return http


def _plan_real(instancia, destino: str = "web") -> str:
    """Plan con un vídeo y una imagen locales, en la carpeta del cliente."""
    cliente = instancia / "clientes" / "acme"
    (cliente / "creativos" / "20261116_prueba").mkdir(parents=True, exist_ok=True)
    (cliente / "creativos" / "20261116_prueba" / "h1.mp4").write_bytes(b"\x00\x00\x00 ftypmp42" + b"0" * 64)
    (cliente / "creativos" / "20261116_prueba" / "h2.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 64)
    seg = {"geo_locations": {"countries": ["ES"]}, "age_min": 25}
    plan = {"campana": {"nombre": "ES_LEADS_ADQ_HV", "objetivo": "OUTCOME_LEADS"}, "evento": "LEAD",
            "conjuntos": [
                {"nombre": "BROAD-H1_LEAD", "presupuesto_diario": 20, "segmentacion": seg,
                 "anuncios": [{"nombre": "20261116_tiempo-perdido_demo-antes-despues_demo_h1",
                               "video": "creativos/20261116_prueba/h1.mp4", "texto": "Texto aprobado",
                               "titulo": "Titular", "url": "https://acme.test/diagnostico"}]},
                {"nombre": "BROAD-H2_LEAD", "presupuesto_diario": 20.5, "segmentacion": seg,
                 "anuncios": [{"nombre": "20261116_tiempo-perdido_demo-antes-despues_estatico_h2",
                               "imagen": "creativos/20261116_prueba/h2.png", "texto": "Texto aprobado",
                               "url": "https://acme.test/diagnostico"}]}]}
    if destino == "formulario":
        for c in plan["conjuntos"]:
            c["destino"] = "formulario"
            c["formulario_id"] = "444444"
            for an in c["anuncios"]:
                an.pop("url")
                an["cta"] = "SIGN_UP"
    ruta = cliente / "planes" / "2026-11-prueba.json"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(plan), encoding="utf-8")
    return str(ruta)


def _http_crear(monkeypatch, mejoras_activas=None, rechazo=None) -> HttpSimulado:
    contador = {"n": 0}

    def nuevo_id(_p):
        contador["n"] += 1
        return {"id": f"9000{contador['n']}"}

    def get_objeto(p):
        campos = p["query"].get("fields", "")
        if campos == "currency":
            return {"currency": "EUR"}
        if campos == "status":
            return {"status": {"video_status": "ready"}}
        if campos == "degrees_of_freedom_spec":
            spec = {f: {"enroll_status": "OPT_OUT"} for f in ("text_optimizations", "video_auto_crop")}
            for f in mejoras_activas or []:
                spec[f] = {"enroll_status": "OPT_IN"}
            return {"degrees_of_freedom_spec": {"creative_features_spec": spec}}
        raise AssertionError(f"GET inesperado: {campos}")

    creatividades = [rechazo] if rechazo else []
    creatividades += [nuevo_id] * 5
    http = HttpSimulado()
    http.cuando("GET", r"/v\d+\.0/(act_12345|\d+)$", get_objeto)
    http.cuando("GET", r"/thumbnails$", {"data": [{"uri": "https://scontent.example/t.jpg", "is_preferred": True}]})
    http.cuando("POST", r"/act_12345/campaigns$", nuevo_id)
    http.cuando("POST", r"/act_12345/adsets$", nuevo_id)
    http.cuando("POST", r"/act_12345/advideos$", {"id": "70001"})
    http.cuando("POST", r"/act_12345/adimages$", {"images": {"h2.png": {"hash": "abc123hash"}}})
    http.cuando("POST", r"/act_12345/adcreatives$", creatividades)
    http.cuando("POST", r"/act_12345/ads$", nuevo_id)
    return _http(monkeypatch, http)


# ---------------------------------------------------------------- plan simulado

def test_plantilla_simulada_sin_red(meta, monkeypatch, capsys):
    http = _http(monkeypatch, HttpSimulado())
    monkeypatch.delenv("META_TOKEN", raising=False)  # simular no necesita token
    meta.main(["crear", str(PLANTILLA), "--simular", "--cliente", "acme"])
    salida = capsys.readouterr().out
    assert http.peticiones == []
    assert "ES_LEADS_ADQ_HV" in salida and "BROAD-H1_LEAD" in salida and "40,00 EUR/día" in salida
    assert "No se ha tocado Meta" in salida and "url de ejemplo" in salida


def test_plantilla_es_generica():
    texto = PLANTILLA.read_text(encoding="utf-8")
    plan = json.loads(texto)
    assert "Acme Automations" in texto and "/Users/" not in texto
    for clave in ("pagina_id", "instagram_id"):
        assert set(plan[clave]) == {"0"}
    for c in plan["conjuntos"]:
        assert all(set(aud["id"]) == {"0"} for aud in c["segmentacion"]["excluded_custom_audiences"])
        assert all(".example/" in an["url"] for an in c["anuncios"])


def test_plan_por_encima_del_tope(meta, instancia, monkeypatch, capsys):
    plan = json.loads(PLANTILLA.read_text(encoding="utf-8"))
    plan["conjuntos"][0]["presupuesto_diario"] = 90
    ruta = instancia / "plan.json"
    ruta.write_text(json.dumps(plan), encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        meta.main(["crear", str(ruta), "--simular", "--cliente", "acme"])
    assert e.value.code == 1
    assert "110,00 EUR/día" in capsys.readouterr().err


def test_topes_sin_definir_bloquean(meta, instancia, capsys):
    f = instancia / "clientes" / "acme" / "ficha.md"
    f.write_text(f.read_text(encoding="utf-8").replace("cambio_dia: 100", "cambio_dia: 0"), encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        meta.main(["crear", str(PLANTILLA), "--simular", "--cliente", "acme"])
    assert e.value.code == 1 and "no tiene topes" in capsys.readouterr().err


def test_errores_de_estructura(meta, instancia, capsys):
    plan = json.loads(PLANTILLA.read_text(encoding="utf-8"))
    plan["campana"]["presupuesto_diario"] = 30  # CBO con presupuesto también en los conjuntos
    plan["conjuntos"][1]["anuncios"][0]["url"] = "http://sin-https.example"
    plan["conjuntos"][1]["segmentacion"].pop("geo_locations")
    ruta = instancia / "plan.json"
    ruta.write_text(json.dumps(plan), encoding="utf-8")
    with pytest.raises(SystemExit):
        meta.main(["crear", str(ruta), "--simular", "--cliente", "acme"])
    err = capsys.readouterr().err
    assert "CBO" in err and "https://" in err and "geo_locations" in err


def test_nomenclatura_invalida_bloquea(meta, monkeypatch, capsys):
    falso = types.ModuleType("nomenclatura")
    falso.validar = lambda nivel, nombre: (nivel != "anuncio", "formato AAAAMMDD_angulo_concepto_formato_hN")
    monkeypatch.setitem(sys.modules, "nomenclatura", falso)
    with pytest.raises(SystemExit) as e:
        meta.main(["crear", str(PLANTILLA), "--simular", "--cliente", "acme"])
    assert e.value.code == 1 and "nomenclatura" in capsys.readouterr().err


def test_sin_nomenclatura_solo_avisa(meta, monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "nomenclatura", None)  # import → ImportError
    meta.main(["crear", str(PLANTILLA), "--simular", "--cliente", "acme"])
    assert "no se ha podido validar la nomenclatura" in capsys.readouterr().out


def test_crear_real_se_niega_con_pendientes(meta, monkeypatch, capsys):
    http = _http(monkeypatch, HttpSimulado())
    with pytest.raises(SystemExit) as e:
        meta.main(["crear", str(PLANTILLA), "--cliente", "acme"])
    assert e.value.code == 1 and http.peticiones == []
    assert "Antes de crear falta" in capsys.readouterr().err


# ---------------------------------------------------------------- crear de verdad (HTTP simulado)

def test_crear_todo_en_pausa_y_sin_mejoras(meta, instancia, ficha_real, monkeypatch, capsys):
    http = _http_crear(monkeypatch)
    plan = _plan_real(instancia)
    meta.main(["crear", plan, "--cliente", "acme"])

    campana = http.de("POST", r"/campaigns$")[0]["form"]
    assert campana["status"] == "PAUSED" and campana["is_adset_budget_sharing_enabled"] == "False"
    conjuntos = [p["form"] for p in http.de("POST", r"/adsets$")]
    assert [c["status"] for c in conjuntos] == ["PAUSED", "PAUSED"]
    assert [c["daily_budget"] for c in conjuntos] == ["2000", "2050"]  # céntimos
    assert json.loads(conjuntos[0]["promoted_object"]) == {"pixel_id": "111111", "custom_event_type": "LEAD"}
    assert http.de("POST", r"/advideos$")[0]["host"] == "graph-video.facebook.com"
    creatividades = [p["form"] for p in http.de("POST", r"/adcreatives$")]
    for cr in creatividades:
        spec = json.loads(cr["degrees_of_freedom_spec"])["creative_features_spec"]
        assert set(spec) == set(meta.MEJORAS) and {v["enroll_status"] for v in spec.values()} == {"OPT_OUT"}
        assert cr["url_tags"].startswith("utm_source=fb_ad&")  # la ficha de acme usa GHL
        assert "ad_id={{ad.id}}" in cr["url_tags"]
        historia = json.loads(cr["object_story_spec"])
        assert historia["page_id"] == "222222" and historia["instagram_user_id"] == "333333"
    video = json.loads(creatividades[0]["object_story_spec"])["video_data"]
    assert video["video_id"] == "70001" and video["image_url"].endswith("t.jpg")
    assert json.loads(creatividades[1]["object_story_spec"])["link_data"]["image_hash"] == "abc123hash"
    assert {p["form"]["status"] for p in http.de("POST", r"/ads$")} == {"PAUSED"}

    estado = json.loads((instancia / "clientes" / "acme" / "planes" / "2026-11-prueba.estado.json").read_text())
    assert estado["cuenta"] == "act_12345" and len(estado["anuncios"]) == 2
    acciones = [json.loads(x)["accion"] for x in (instancia / "logs" / "cambios.jsonl").read_text().splitlines()]
    assert acciones.count("crear_anuncio") == 2 and "crear_campana" in acciones and "subir_video" in acciones
    salida = capsys.readouterr().out
    assert "TODO EN PAUSA" in salida and "| operador-meta (meta_ads.py) | campaña |" in salida
    assert "token-global" not in salida


def test_crear_es_idempotente(meta, instancia, ficha_real, monkeypatch):
    plan = _plan_real(instancia)
    _http_crear(monkeypatch)
    meta.main(["crear", plan, "--cliente", "acme"])
    http = _http_crear(monkeypatch)
    meta.main(["crear", plan, "--cliente", "acme"])
    assert [p for p in http.peticiones if p["metodo"] == "POST"] == []


def test_crear_avisa_de_mejoras_que_quedan_activas(meta, instancia, ficha_real, monkeypatch, capsys):
    _http_crear(monkeypatch, mejoras_activas=["inline_comment"])
    meta.main(["crear", _plan_real(instancia), "--cliente", "acme"])
    assert "inline_comment" in capsys.readouterr().out


def test_mejora_rechazada_se_reintenta_sin_ella(meta, instancia, ficha_real, monkeypatch):
    rechazo = (400, {"error": {"message": "Invalid parameter", "code": 100,
                               "error_user_msg": "image_background_gen no es compatible con este formato"}})
    http = _http_crear(monkeypatch, rechazo=rechazo)
    meta.main(["crear", _plan_real(instancia), "--cliente", "acme"])
    intentos = http.de("POST", r"/adcreatives$")
    assert len(intentos) == 3
    spec = json.loads(intentos[1]["form"]["degrees_of_freedom_spec"])["creative_features_spec"]
    assert "image_background_gen" not in spec and "text_optimizations" in spec
    estado = json.loads((instancia / "clientes" / "acme" / "planes" / "2026-11-prueba.estado.json").read_text())
    assert any(v.get("mejoras_no_aceptadas") == ["image_background_gen"] for v in estado["anuncios"].values())


def test_crear_formulario_instantaneo(meta, instancia, ficha_real, monkeypatch):
    http = _http_crear(monkeypatch)
    meta.main(["crear", _plan_real(instancia, destino="formulario"), "--cliente", "acme"])
    conjunto = http.de("POST", r"/adsets$")[0]["form"]
    assert conjunto["optimization_goal"] == "LEAD_GENERATION" and conjunto["destination_type"] == "ON_AD"
    assert json.loads(conjunto["promoted_object"]) == {"page_id": "222222"}
    creatividades = [p["form"] for p in http.de("POST", r"/adcreatives$")]
    assert all("url_tags" not in cr for cr in creatividades)
    video = json.loads(creatividades[0]["object_story_spec"])["video_data"]["call_to_action"]
    assert video == {"type": "SIGN_UP", "value": {"lead_gen_form_id": "444444", "link": "https://fb.me/"}}
    imagen = json.loads(creatividades[1]["object_story_spec"])["link_data"]
    assert imagen["link"] == "https://fb.me/" and imagen["call_to_action"]["value"] == {"lead_gen_form_id": "444444"}


def _reescribe_plan(ruta: str, cambio) -> str:
    plan = json.loads(pathlib.Path(ruta).read_text(encoding="utf-8"))
    cambio(plan)
    pathlib.Path(ruta).write_text(json.dumps(plan), encoding="utf-8")
    return ruta


def test_quality_lead_lleva_el_dataset_del_crm(meta, instancia, ficha_real, monkeypatch):
    def cambio(plan):
        plan["conjuntos"][0]["optimizar"] = "QUALITY_LEAD"
        plan["conjuntos"][1]["optimizar"] = "QUALITY_LEAD"
        plan["conjuntos"][1]["dataset_crm"] = "555555"
    http = _http_crear(monkeypatch)
    meta.main(["crear", _reescribe_plan(_plan_real(instancia, destino="formulario"), cambio), "--cliente", "acme"])
    conjuntos = [p["form"] for p in http.de("POST", r"/adsets$")]
    assert {c["optimization_goal"] for c in conjuntos} == {"QUALITY_LEAD"}
    assert json.loads(conjuntos[0]["promoted_object"]) == {"page_id": "222222", "pixel_id": "111111"}  # el de la ficha
    assert json.loads(conjuntos[1]["promoted_object"]) == {"page_id": "222222", "pixel_id": "555555"}


def test_quality_lead_y_optimizar_se_validan(meta, instancia, ficha_real, capsys):
    web = _reescribe_plan(_plan_real(instancia), lambda p: p["conjuntos"][0].update(optimizar="QUALITY_LEAD"))
    with pytest.raises(SystemExit) as e:
        meta.main(["crear", web, "--simular", "--cliente", "acme"])
    assert e.value.code == 1 and "QUALITY_LEAD (Conversion Leads) va con destino formulario" in capsys.readouterr().err
    form = _reescribe_plan(_plan_real(instancia, destino="formulario"),
                           lambda p: p["conjuntos"][0].update(optimizar="OFFSITE_CONVERSIONS"))
    with pytest.raises(SystemExit):
        meta.main(["crear", form, "--simular", "--cliente", "acme"])
    assert "LEAD_GENERATION o QUALITY_LEAD" in capsys.readouterr().err
    ok = _reescribe_plan(form, lambda p: p["conjuntos"][0].update(optimizar="QUALITY_LEAD"))
    meta.main(["crear", ok, "--simular", "--cliente", "acme"])
    salida = capsys.readouterr().out
    assert "formulario instantáneo (QUALITY_LEAD)" in salida and "[CONTESTED]" in salida


def test_segmentacion_ventas_con_dispositivo(meta):
    seg = {"geo_locations": {"countries": ["ES"]}, "user_os": ["Windows"],
           "targeting_automation": {"advantage_audience": 0}}
    c = {"segmentacion": seg}
    plan = {"campana": {"objetivo": "OUTCOME_SALES"}}
    salida = meta.segmentacion_api(c, plan, "OUTCOME_SALES")
    assert salida["targeting_automation"] == {"advantage_audience": 0, "individual_setting": {"device": 0}}
    assert "individual_setting" not in seg["targeting_automation"]  # no toca el plan
    assert meta.segmentacion_api(c, plan, "OUTCOME_LEADS") == seg  # solo Ventas
    assert meta.segmentacion_api({**c, "expansion_dispositivos": True}, plan, "OUTCOME_SALES") == seg
    assert meta.segmentacion_api(c, {"expansion_dispositivos": True}, "OUTCOME_SALES") == seg
    especial = {"campana": {"categorias_especiales": ["EMPLOYMENT"]}}
    assert meta.segmentacion_api(c, especial, "OUTCOME_SALES") == seg  # no aplica a categorías especiales
    sin = {"segmentacion": {"geo_locations": {"countries": ["ES"]}}}
    assert meta.segmentacion_api(sin, plan, "OUTCOME_SALES") == sin["segmentacion"]
    puesto = {"segmentacion": {**seg, "targeting_automation": {"individual_setting": {"device": 1}}}}
    assert meta.segmentacion_api(puesto, plan, "OUTCOME_SALES")["targeting_automation"] == {
        "individual_setting": {"device": 1}}  # un valor puesto a mano se respeta


def test_crear_ventas_con_dispositivo_manda_device_0(meta, instancia, ficha_real, monkeypatch, capsys):
    def cambio(plan):
        plan["campana"]["objetivo"] = "OUTCOME_SALES"
        plan["evento"] = "PURCHASE"
        for c in plan["conjuntos"]:
            c["segmentacion"]["user_device"] = ["iPhone"]
        plan["conjuntos"][1]["expansion_dispositivos"] = True
    ruta = _reescribe_plan(_plan_real(instancia), cambio)
    meta.main(["crear", ruta, "--simular", "--cliente", "acme"])
    salida = capsys.readouterr().out
    assert "device = 0" in salida and "expansion_dispositivos: true" in salida
    http = _http_crear(monkeypatch)
    meta.main(["crear", ruta, "--cliente", "acme"])
    conjuntos = [json.loads(p["form"]["targeting"]) for p in http.de("POST", r"/adsets$")]
    assert conjuntos[0]["targeting_automation"] == {"individual_setting": {"device": 0}}
    assert "targeting_automation" not in conjuntos[1]


def test_api_no_activa_ni_esquiva_el_tope(meta, instancia, ficha_real, capsys):
    """`api` se envía tal cual a Meta: ni estado activo ni presupuestos que no cuenten para el tope."""
    def cambio(plan):
        plan["campana"]["api"] = {"status": "ACTIVE", "daily_budget": 5000}
        plan["conjuntos"][0]["api"] = {"daily_budget": 9000}
        plan["conjuntos"][1]["anuncios"][0]["api"] = {"configured_status": "active"}
    ruta = _reescribe_plan(_plan_real(instancia), cambio)
    with pytest.raises(SystemExit) as e:
        meta.main(["crear", ruta, "--simular", "--cliente", "acme"])
    err = capsys.readouterr().err
    assert e.value.code == 1
    assert "campaña: api.status = ACTIVE — todo se crea en pausa" in err
    assert "api.configured_status = active" in err
    assert "el presupuesto de la campaña va en campana.presupuesto_diario" in err
    assert "api.daily_budget no — el presupuesto diario va en presupuesto_diario" in err
    # 20 + 20,5 de los conjuntos + 50 y 90 de «api» (en céntimos) = 180,50 > 100 de tope
    assert "el plan suma 180,50 EUR/día" in err
    plan = json.loads(pathlib.Path(ruta).read_text(encoding="utf-8"))
    assert meta.total_plan(plan, "EUR") == pytest.approx(180.5)
    assert meta.total_plan(plan, "JPY") == pytest.approx(40.5 + 5000 + 9000)  # sin decimales: sin dividir


def test_api_con_presupuesto_total_y_estado_en_pausa(meta, instancia, ficha_real, monkeypatch, capsys):
    def cambio(plan):
        c = plan["conjuntos"][1]
        c.pop("presupuesto_diario")
        c.update(inicio="2026-11-16 08:00", fin="2026-11-26 08:00", api={"lifetime_budget": 30000})
        plan["conjuntos"][0]["api"] = {"status": "PAUSED", "bid_strategy": "COST_CAP", "bid_amount": 1500}
        plan["conjuntos"][0]["anuncios"][0]["api"] = {"status": "PAUSED", "name": "otro"}
    ruta = _reescribe_plan(_plan_real(instancia), cambio)
    meta.main(["crear", ruta, "--simular", "--cliente", "acme"])
    salida = capsys.readouterr().out
    assert "api.lifetime_budget = 300,00 EUR en 10 días; para el tope cuenta como 30,00 EUR/día" in salida
    assert "total 50,00 EUR/día" in salida
    http = _http_crear(monkeypatch)
    meta.main(["crear", ruta, "--cliente", "acme"])
    c1, c2 = [p["form"] for p in http.de("POST", r"/adsets$")]
    assert (c1["status"], c1["bid_strategy"], c1["bid_amount"], c1["daily_budget"]) == (
        "PAUSED", "COST_CAP", "1500", "2000")
    assert c2["lifetime_budget"] == "30000" and "daily_budget" not in c2 and c2["status"] == "PAUSED"
    assert {p["form"]["status"] for p in http.de("POST", r"/ads$")} == {"PAUSED"}
    assert http.de("POST", r"/ads$")[0]["form"]["name"] == "otro"


@pytest.mark.parametrize("cambio, mensaje", [
    (lambda c: c.update(api={"lifetime_budget": 30000}), "lleva presupuesto_diario y api.lifetime_budget"),
    (lambda c: (c.pop("presupuesto_diario"), c.update(api={"lifetime_budget": 30000})),
     "api.lifetime_budget necesita inicio y fin"),
    (lambda c: c.update(api={"lifetime_budget": "300.50"}), "va en la unidad mínima"),
    (lambda c: c.update(api="status=ACTIVE"), "«api» tiene que ser un objeto JSON"),
])
def test_api_de_conjunto_mal_formado(meta, instancia, ficha_real, capsys, cambio, mensaje):
    ruta = _reescribe_plan(_plan_real(instancia), lambda p: cambio(p["conjuntos"][1]))
    with pytest.raises(SystemExit):
        meta.main(["crear", ruta, "--simular", "--cliente", "acme"])
    assert mensaje in capsys.readouterr().err


def test_expansion_dispositivos_tiene_que_ser_booleano(meta, instancia, ficha_real, capsys):
    ruta = _reescribe_plan(_plan_real(instancia), lambda p: p.update(expansion_dispositivos="si"))
    with pytest.raises(SystemExit):
        meta.main(["crear", ruta, "--simular", "--cliente", "acme"])
    assert "expansion_dispositivos es true o false" in capsys.readouterr().err


@pytest.mark.parametrize("modo, esperado", [("revisar", {"product_extensions"}), ("on", None)])
def test_mejoras_revisar_y_on(meta, instancia, ficha_real, monkeypatch, modo, esperado):
    ficha_real.write_text(ficha_real.read_text(encoding="utf-8").replace("mejoras_automaticas: off",
                                                                         f"mejoras_automaticas: {modo}"),
                          encoding="utf-8")
    http = _http_crear(monkeypatch)
    meta.main(["crear", _plan_real(instancia), "--cliente", "acme"])
    for p in http.de("POST", r"/adcreatives$"):
        if esperado is None:
            assert "degrees_of_freedom_spec" not in p["form"]
        else:
            spec = json.loads(p["form"]["degrees_of_freedom_spec"])["creative_features_spec"]
            assert set(spec) == esperado and spec["product_extensions"] == {"enroll_status": "OPT_OUT"}


def _plan_publicaciones(instancia) -> str:
    def cambio(plan):
        plan["conjuntos"][0]["anuncios"][0] = {"nombre": "20261116_tiempo-perdido_post-fundador_founder_h1",
                                               "publicacion_ig": "17900000000000123", "cta": "LEARN_MORE",
                                               "url": "https://acme.test/diagnostico"}
        plan["conjuntos"][1]["anuncios"][0] = {"nombre": "20261116_tiempo-perdido_post-fundador_estatico_h2",
                                               "publicacion_fb": "222222_987654321", "texto": "Se ignora",
                                               "url": "https://acme.test/diagnostico"}
    return _reescribe_plan(_plan_real(instancia), cambio)


def test_crear_desde_publicaciones_existentes(meta, instancia, ficha_real, monkeypatch, capsys):
    ruta = _plan_publicaciones(instancia)
    meta.main(["crear", ruta, "--simular", "--cliente", "acme"])
    salida = capsys.readouterr().out
    assert "publicacion_ig 17900000000000123" in salida and "texto se ignora" in salida
    http = _http_crear(monkeypatch)
    meta.main(["crear", ruta, "--cliente", "acme"])
    assert not http.de("POST", r"/advideos$") and not http.de("POST", r"/adimages$")
    ig, fb = [p["form"] for p in http.de("POST", r"/adcreatives$")]
    assert (ig["object_id"], ig["instagram_user_id"], ig["source_instagram_media_id"]) == (
        "222222", "333333", "17900000000000123")
    assert fb["object_story_id"] == "222222_987654321" and fb["instagram_user_id"] == "333333"
    for cr in (ig, fb):
        assert "object_story_spec" not in cr and cr["url_tags"].startswith("utm_source=fb_ad&")
        assert json.loads(cr["call_to_action"]) == {"type": "LEARN_MORE",
                                                   "value": {"link": "https://acme.test/diagnostico"}}
        assert set(json.loads(cr["degrees_of_freedom_spec"])["creative_features_spec"]) == set(meta.MEJORAS)
    acciones = [json.loads(x) for x in (instancia / "logs" / "cambios.jsonl").read_text().splitlines()]
    assert any(x["detalle"].endswith("desde una publicación de Facebook") for x in acciones)
    estado = json.loads((instancia / "clientes" / "acme" / "planes" / "2026-11-prueba.estado.json").read_text())
    assert {v["publicacion"] for v in estado["anuncios"].values()} == {"17900000000000123", "222222_987654321"}


def test_publicaciones_mal_formadas(meta, instancia, ficha_real, capsys):
    def cambio(plan):
        plan["conjuntos"][0]["anuncios"][0]["publicacion_ig"] = "https://www.instagram.com/p/Cabc/"
        plan["conjuntos"][1]["anuncios"][0]["publicacion_fb"] = "999999_987654321"
    ruta = _reescribe_plan(_plan_publicaciones(instancia), cambio)
    with pytest.raises(SystemExit):
        meta.main(["crear", ruta, "--simular", "--cliente", "acme"])
    err = capsys.readouterr().err
    assert "ID numérico del medio de Instagram" in err and "es de la Página 999999" in err
    form = _reescribe_plan(_plan_real(instancia, destino="formulario"),
                           lambda p: p["conjuntos"][0]["anuncios"][0].update(video=None, texto=None,
                                                                             publicacion_ig="17900000000000123"))
    with pytest.raises(SystemExit):
        meta.main(["crear", form, "--simular", "--cliente", "acme"])
    assert "con formulario instantáneo" in capsys.readouterr().err
    dos = _reescribe_plan(_plan_publicaciones(instancia),
                          lambda p: p["conjuntos"][0]["anuncios"][0].update(video="creativos/20261116_prueba/h1.mp4"))
    with pytest.raises(SystemExit):
        meta.main(["crear", dos, "--simular", "--cliente", "acme"])
    assert "uno y solo uno" in capsys.readouterr().err


def test_moneda_distinta_es_error_de_configuracion(meta, instancia, ficha_real, monkeypatch):
    http = _http(monkeypatch, HttpSimulado().cuando("GET", r"/act_12345$", {"currency": "USD"}))
    with pytest.raises(SystemExit) as e:
        meta.main(["crear", _plan_real(instancia), "--cliente", "acme"])
    assert e.value.code == 2 and not http.de("POST", r".")


def test_sin_token_es_error_de_configuracion(meta, monkeypatch, ficha_real):
    monkeypatch.delenv("META_TOKEN")
    with pytest.raises(SystemExit) as e:
        meta.main(["vigente", "--cliente", "acme"])
    assert e.value.code == 2


def test_token_por_cliente(meta, ficha_real, monkeypatch):
    monkeypatch.setenv("META_TOKEN_ACME", "token-de-acme")
    http = _http(monkeypatch, HttpSimulado().cuando("GET", r"/act_12345/adsets$", {"data": []}))
    meta.main(["vigente", "--cliente", "acme", "--json"])
    assert http.peticiones[0]["query"]["access_token"] == "token-de-acme"


def test_token_caducado(meta, ficha_real, monkeypatch):
    _http(monkeypatch, HttpSimulado().cuando("GET", r"/adsets$", (400, {"error": {"code": 190, "message": "expired"}})))
    with pytest.raises(SystemExit) as e:
        meta.main(["vigente", "--cliente", "acme"])
    assert e.value.code == 2


# ---------------------------------------------------------------- activar, presupuesto y pausar

def _http_cambios(monkeypatch, activo_cuenta: int = 0) -> HttpSimulado:
    campanas = {"data": [{"id": "500", "name": "ES_LEADS_ADQ_HV", "status": "PAUSED", "effective_status": "PAUSED"}]}
    conjuntos = {"data": [{"id": "501", "name": "BROAD-H1_LEAD", "status": "PAUSED", "daily_budget": "4000",
                           "campaign_id": "500"}]}
    anuncios = {"data": [{"id": "502", "name": "20261116_x_y_demo_h1", "status": "PAUSED"}]}

    def adsets(p):
        if "effective_status" in p["query"]:  # presupuesto activo de la cuenta
            if not activo_cuenta:
                return {"data": []}
            return {"data": [{"id": "900", "name": "OTRO", "daily_budget": str(activo_cuenta * 100),
                              "campaign": {"id": "899", "name": "OTRA"}}]}
        return conjuntos

    http = HttpSimulado()
    http.cuando("GET", r"/act_12345/campaigns$", campanas)
    http.cuando("GET", r"/act_12345/adsets$", adsets)
    http.cuando("GET", r"/act_12345/ads$", anuncios)
    http.cuando("GET", r"/500/adsets$", conjuntos)
    http.cuando("POST", r"/v\d+\.0/50\d$", {"success": True})
    return _http(monkeypatch, http)


def test_activar_sin_confirmo_no_activa(meta, ficha_real, monkeypatch, capsys):
    http = _http_cambios(monkeypatch)
    with pytest.raises(SystemExit) as e:
        meta.main(["activar", "500", "501", "502", "--cliente", "acme"])
    assert e.value.code == 1 and not http.de("POST", r".")
    assert "40,00 EUR" in capsys.readouterr().out


def test_activar_con_confirmo_de_abajo_arriba(meta, instancia, ficha_real, monkeypatch, capsys):
    http = _http_cambios(monkeypatch)
    meta.main(["activar", "500", "501", "502", "--cliente", "acme", "--confirmo"])
    posts = http.de("POST", r".")
    assert [p["path"].rsplit("/", 1)[1] for p in posts] == ["502", "501", "500"]
    assert {p["form"]["status"] for p in posts} == {"ACTIVE"}
    filas = [json.loads(x) for x in (instancia / "logs" / "cambios.jsonl").read_text().splitlines()]
    assert [f["accion"] for f in filas] == ["activar"] * 3 and filas[0]["cliente"] == "acme"
    assert "| ACTIVE" not in capsys.readouterr().err


def test_activar_respeta_tope_total(meta, ficha_real, monkeypatch, capsys):
    http = _http_cambios(monkeypatch, activo_cuenta=280)
    with pytest.raises(SystemExit) as e:
        meta.main(["activar", "500", "501", "502", "--cliente", "acme", "--confirmo"])
    assert e.value.code == 1 and not http.de("POST", r".")
    assert "320,00" in capsys.readouterr().err


def test_presupuesto(meta, instancia, ficha_real, monkeypatch, capsys):
    http = _http_cambios(monkeypatch)
    with pytest.raises(SystemExit) as e:
        meta.main(["presupuesto", "501", "150", "--cliente", "acme", "--confirmo"])
    assert e.value.code == 1 and "tope por cambio" in capsys.readouterr().err
    with pytest.raises(SystemExit) as e:
        meta.main(["presupuesto", "501", "60", "--cliente", "acme"])
    assert e.value.code == 1 and not http.de("POST", r".")
    meta.main(["presupuesto", "501", "60", "--cliente", "acme", "--confirmo"])
    assert http.de("POST", r"/501$")[0]["form"]["daily_budget"] == "6000"
    fila = json.loads((instancia / "logs" / "cambios.jsonl").read_text().strip())
    assert fila["accion"] == "presupuesto" and "40.0 → 60.0 EUR/día" in fila["detalle"]


def test_pausar_no_pide_confirmacion(meta, ficha_real, monkeypatch):
    http = _http_cambios(monkeypatch)
    meta.main(["pausar", "501", "--cliente", "acme"])
    assert http.de("POST", r"/501$")[0]["form"]["status"] == "PAUSED"


# ---------------------------------------------------------------- lecturas

def test_anuncios_csv_en_datos_y_columnas_del_registro(meta, instancia, ficha_real, monkeypatch, capsys):
    fila = {"ad_id": "120000000000601", "ad_name": "20261116_x_y_demo_h1", "adset_id": "501", "adset_name": "BROAD-H1_LEAD",
            "campaign_id": "500", "campaign_name": "ES_LEADS_ADQ_HV", "spend": "100.00", "impressions": "10000",
            "reach": "8000", "frequency": "1.25", "inline_link_clicks": "150", "date_start": "2026-11-02",
            "date_stop": "2026-11-08",
            "actions": [{"action_type": "lead", "value": "10"}, {"action_type": "video_view", "value": "2500"},
                        {"action_type": "landing_page_view", "value": "120"}],
            "conversions": [{"action_type": "schedule_total", "value": "2"}],
            "video_thruplay_watched_actions": [{"action_type": "video_view", "value": "500"}]}
    http = HttpSimulado()
    http.cuando("GET", r"/act_12345$", {"currency": "EUR"})
    http.cuando("GET", r"/act_12345/insights$", {"data": [fila]})
    http.cuando("GET", r"/act_12345/adsets$", {"data": [{"campaign_id": "500",
                                                         "promoted_object": {"custom_event_type": "LEAD"}}]})
    _http(monkeypatch, http)
    meta.main(["anuncios", "--cliente", "acme", "--desde", "2026-11-02", "--hasta", "2026-11-08"])
    ruta = instancia / "clientes" / "acme" / "datos" / "meta-anuncios_2026-11-02_2026-11-08.csv"
    filas = list(csv.DictReader(ruta.open(encoding="utf-8")))
    assert list(filas[0]) == meta.COLUMNAS
    f = filas[0]
    assert (f["resultado_meta"], f["coste_resultado_meta"], f["citas_meta"]) == ("10", "10.0", "2")
    assert (f["ctr"], f["hook_rate"], f["hold_rate"], f["cpm"]) == ("1.5", "25.0", "20.0", "10.0")
    assert "ES_LEADS_ADQ_HV" in capsys.readouterr().out
    import registro_creativo  # el CSV es la entrada de Meta de `registro_creativo.py` y de `embudo.py` (B1)
    ad = registro_creativo.agregar_meta(registro_creativo.leer_csv(ruta))["120000000000601"]
    assert (ad["gasto"], ad["impresiones"], ad["clics"], ad["vistas_3s"], ad["thruplay"], ad["resultado"]) == \
        (100.0, 10000, 150, 2500, 500, 10)
    assert (ad["nombre"], ad["inicio"]) == ("20261116_x_y_demo_h1", "2026-11-02")


def test_anuncios_sin_archivos_en_json(meta, instancia, ficha_real, monkeypatch, capsys):
    http = HttpSimulado()
    http.cuando("GET", r"/act_12345$", {"currency": "EUR"})
    http.cuando("GET", r"/act_12345/insights$", {"data": []})
    _http(monkeypatch, http)
    meta.main(["anuncios", "--cliente", "acme", "--desde", "2026-11-02", "--hasta", "2026-11-08", "--json",
               "--sin-archivos"])
    assert json.loads(capsys.readouterr().out)["filas"] == 0
    assert not list((instancia / "clientes" / "acme" / "datos").glob("meta-anuncios*"))


def test_anuncios_estado_lista_los_rechazados(meta, instancia, ficha_real, monkeypatch, capsys):
    ads = {"data": [
        {"id": "601", "name": "20261116_x_y_demo_h1", "effective_status": "DISAPPROVED", "campaign_id": "500",
         "campaign": {"name": "ES_LEADS_ADQ_HV"}, "ad_review_feedback": {"global": {"Afirmaciones": "Promesa de resultado"}}},
        {"id": "602", "name": "20261116_x_y_demo_h2", "effective_status": "WITH_ISSUES", "campaign_id": "700",
         "campaign": {"name": "OTRA"}, "issues_info": [{"error_summary": "Imagen con poco contraste"}]}]}
    http = HttpSimulado()
    http.cuando("GET", r"/act_12345$", {"currency": "EUR"})
    http.cuando("GET", r"/act_12345/ads$", ads)
    http.cuando("GET", r"/act_12345/insights$", {"data": []})
    _http(monkeypatch, http)
    meta.main(["anuncios", "--cliente", "acme", "--desde", "2026-11-02", "--hasta", "2026-11-08", "--json",
               "--sin-archivos", "--estado", "--campana", "es_leads"])
    datos = json.loads(capsys.readouterr().out)
    assert [(f["ad_id"], f["estado"], f["motivo"]) for f in datos["con_problemas"]] == [
        ("601", "DISAPPROVED", "Promesa de resultado")]
    assert json.loads(http.de("GET", r"/ads$")[0]["query"]["effective_status"]) == meta.PROBLEMAS
    sin = HttpSimulado().cuando("GET", r"/act_12345$", {"currency": "EUR"}).cuando("GET", r"/insights$", {"data": []})
    _http(monkeypatch, sin)
    meta.main(["anuncios", "--cliente", "acme", "--desde", "2026-11-02", "--hasta", "2026-11-08", "--json",
               "--sin-archivos"])
    assert "con_problemas" not in json.loads(capsys.readouterr().out) and not sin.de("GET", r"/ads$")


def test_vigente_suma_cbo_y_abo(meta, ficha_real, monkeypatch, capsys):
    conjuntos = {"data": [
        {"id": "1", "name": "A", "daily_budget": "2000", "campaign": {"id": "c1", "name": "ABO"}},
        {"id": "2", "name": "B", "campaign": {"id": "c2", "name": "CBO", "daily_budget": "5000"}},
        {"id": "3", "name": "C", "campaign": {"id": "c2", "name": "CBO", "daily_budget": "5000"}}]}
    http = HttpSimulado().cuando("GET", r"/adsets$", conjuntos).cuando("GET", r"/insights$", {"data": []})
    _http(monkeypatch, http)
    meta.main(["vigente", "--cliente", "acme", "--json"])
    assert json.loads(capsys.readouterr().out)["presupuesto_diario_activo"] == 70.0


def test_cuentas_marca_la_de_la_ficha(meta, ficha_real, monkeypatch, capsys):
    _http(monkeypatch, HttpSimulado().cuando("GET", r"/me/adaccounts$", {"data": [
        {"id": "act_12345", "name": "Acme Automations", "currency": "EUR", "timezone_name": "Europe/Madrid",
         "account_status": 1}]}))
    meta.main(["cuentas", "--cliente", "acme"])
    assert "← ficha" in capsys.readouterr().out


@pytest.mark.parametrize("moneda,importe,minimo", [("EUR", 20.5, 2050), ("JPY", 3000, 3000), ("CLP", 15000, 15000),
                                                   ("MXN", 350, 35000)])
def test_unidad_minima_por_moneda(meta, moneda, importe, minimo):
    assert meta.a_minimo(importe, moneda) == minimo
    assert meta.de_minimo(str(minimo), moneda) == importe


def test_plan_no_se_modifica(meta, monkeypatch):
    antes = copy.deepcopy(json.loads(PLANTILLA.read_text(encoding="utf-8")))
    _http(monkeypatch, HttpSimulado())
    meta.main(["crear", str(PLANTILLA), "--simular", "--cliente", "acme"])
    assert json.loads(PLANTILLA.read_text(encoding="utf-8")) == antes


def test_activos_lista_ids_para_el_plan(meta, ficha_real, monkeypatch, capsys):
    http = HttpSimulado()
    http.cuando("GET", r"/act_12345$", {"name": "Acme Automations", "currency": "EUR", "amount_spent": "123456"})
    http.cuando("GET", r"/promote_pages$", {"data": [{"id": "222222", "name": "Acme Automations"}]})
    http.cuando("GET", r"/instagram_accounts$", {"data": [{"id": "333333", "username": "acme.automations"}]})
    http.cuando("GET", r"/adspixels$", {"data": [{"id": "111111", "name": "Píxel Acme"}]})
    http.cuando("GET", r"/customaudiences$", {"data": []})
    _http(monkeypatch, http)
    meta.main(["activos", "--cliente", "acme", "--json"])
    datos = json.loads(capsys.readouterr().out)
    assert datos["gastado_total"] == 1234.56 and datos["limite_gasto_cuenta"] is None
    assert datos["paginas"][0]["id"] == "222222" and datos["topes_ficha"] == {"cambio_dia": 100, "total_dia": 300}
    meta.main(["activos", "--cliente", "acme"])
    assert "NINGUNO" in capsys.readouterr().out  # sin límite de gasto en la cuenta, se avisa


def test_campanas_ordenadas(meta, ficha_real, monkeypatch, capsys):
    http = HttpSimulado()
    http.cuando("GET", r"/act_12345/campaigns$", {"data": [
        {"id": "1", "objective": "OUTCOME_LEADS", "effective_status": "PAUSED", "start_time": "2026-10-01T00:00:00+0200"},
        {"id": "2", "objective": "OUTCOME_LEADS", "effective_status": "ACTIVE", "start_time": "2026-11-02T00:00:00+0100"}]})
    http.cuando("GET", r"/act_12345/insights$", {"data": [
        {"campaign_id": "1", "campaign_name": "VIEJA", "spend": "50.5"},
        {"campaign_id": "2", "campaign_name": "NUEVA", "spend": "10"},
        {"campaign_id": "3", "campaign_name": "BORRADA", "spend": "1"}]})
    _http(monkeypatch, http)
    meta.main(["campanas", "--cliente", "acme", "--json"])
    filas = json.loads(capsys.readouterr().out)
    assert [f["campana"] for f in filas] == ["NUEVA", "VIEJA", "BORRADA"]
    assert filas[-1]["estado"] == "archivada/borrada"


def test_eventos_por_dia_y_fuente(meta, ficha_real, monkeypatch, capsys):
    def stats(p):
        if p["query"]["aggregation"] == "event":
            return {"data": [{"start_time": "2026-11-05T10:00:00+0000",
                              "data": [{"value": "Lead", "count": 4}, {"value": "Schedule", "count": 1}]}]}
        return {"data": [{"start_time": "2026-11-05T10:00:00+0000",
                          "data": [{"value": "BROWSER", "count": 3}, {"value": "SERVER", "count": 2}]}]}
    http = _http(monkeypatch, HttpSimulado().cuando("GET", r"/111111/stats$", stats))
    meta.main(["eventos", "--cliente", "acme", "--desde", "2026-11-02", "--hasta", "2026-11-08", "--json"])
    datos = json.loads(capsys.readouterr().out)
    assert datos["dias"]["2026-11-05"] == {"eventos": {"Lead": 4, "Schedule": 1}, "fuente": {"BROWSER": 3, "SERVER": 2}}
    assert all(p["metodo"] == "GET" for p in http.peticiones)


def test_eventos_sin_dataset(meta, monkeypatch):
    with pytest.raises(SystemExit) as e:  # la ficha de acme trae el dataset a ceros
        meta.main(["eventos", "--cliente", "acme"])
    assert e.value.code == 2


def test_creatividades_detecta_mejoras_y_textos(meta, ficha_real, monkeypatch, capsys):
    _http(monkeypatch, HttpSimulado().cuando("GET", r"/500/ads$", {"data": [
        {"id": "1", "name": "limpio", "effective_status": "PAUSED", "creative": {"id": "c1"}},
        {"id": "2", "name": "con_mejoras", "effective_status": "PAUSED", "creative": {
            "id": "c2", "asset_feed_spec": {"bodies": [{"text": "a"}, {"text": "b"}]},
            "degrees_of_freedom_spec": {"creative_features_spec": {"text_optimizations": {"enroll_status": "OPT_IN"}}}}}]}))
    meta.main(["creatividades", "--cliente", "acme", "--campana-id", "500", "--json"])
    filas = {f["nombre"]: f for f in json.loads(capsys.readouterr().out)}
    assert not filas["limpio"]["problema"]
    assert filas["con_mejoras"]["mejoras_activas"] == ["text_optimizations"] and filas["con_mejoras"]["textos"] == 2


def test_lecturas_no_preguntan_nada(meta, ficha_real, monkeypatch, capsys):
    """Brief diario (contrato §15): las lecturas no pueden quedarse esperando una respuesta."""
    monkeypatch.setattr("builtins.input", lambda *_: pytest.fail("una lectura ha pedido datos por teclado"))
    _http(monkeypatch, HttpSimulado().cuando("GET", r"/adsets$", {"data": []}).cuando("GET", r"/insights$", {"data": []}))
    meta.main(["vigente", "--cliente", "acme", "--json"])
    assert json.loads(capsys.readouterr().out)["presupuesto_diario_activo"] == 0


# ---------------------------------------------------------------- añadir anuncios a lo que ya existe

def _plan_existente(instancia, conjunto_id="777777", campana_id=None) -> str:
    plan = json.loads(pathlib.Path(_plan_real(instancia)).read_text(encoding="utf-8"))
    anuncios = plan["conjuntos"][0]["anuncios"]
    plan = {"conjuntos": [{"id": conjunto_id, "nombre": "BROAD-H1_LEAD", "anuncios": anuncios}]}
    if campana_id:
        plan["campana"] = {"id": campana_id}
    ruta = instancia / "clientes" / "acme" / "planes" / "2026-11-existente.json"
    ruta.write_text(json.dumps(plan), encoding="utf-8")
    return str(ruta)


def _http_existente(monkeypatch, cuenta="12345", campana="666666") -> HttpSimulado:
    http = _http_crear(monkeypatch)
    http.reglas.insert(0, ["GET", __import__("re").compile(r"/777777$"), {"id": "777777", "account_id": cuenta,
                                                                          "name": "BROAD-H1_LEAD", "campaign_id": campana},
                           None])
    return http


def test_plan_con_conjunto_existente_simulado(meta, instancia, ficha_real, monkeypatch, capsys):
    http = _http(monkeypatch, HttpSimulado())
    meta.main(["crear", _plan_existente(instancia), "--simular", "--cliente", "acme"])
    salida = capsys.readouterr().out
    assert http.peticiones == [] and "existente" in salida and "sin presupuesto nuevo" in salida


def test_conjunto_existente_solo_crea_anuncios(meta, instancia, ficha_real, monkeypatch, capsys):
    http = _http_existente(monkeypatch)
    plan = _plan_existente(instancia)
    meta.main(["crear", plan, "--cliente", "acme"])
    assert not http.de("POST", r"/(campaigns|adsets)$")
    anuncio = http.de("POST", r"/ads$")[0]["form"]
    assert anuncio["adset_id"] == "777777" and anuncio["status"] == "PAUSED"
    estado = json.loads((instancia / "clientes" / "acme" / "planes" / "2026-11-existente.estado.json").read_text())
    assert estado["campana"] == "666666" and estado["existentes"] == ["777777", "666666"]
    assert "no se ha tocado" in capsys.readouterr().out
    # activar --plan solo toca lo que creó el plan (el anuncio), nunca el conjunto ni la campaña que ya existían
    nuevo = next(iter(estado["anuncios"].values()))["anuncio"]
    activa = HttpSimulado()
    activa.cuando("GET", r"/act_12345/(campaigns|adsets)$", {"data": []})
    activa.cuando("GET", r"/act_12345/ads$", {"data": [{"id": nuevo, "name": "x", "status": "PAUSED"}]})
    activa.cuando("POST", rf"/{nuevo}$", {"success": True})
    _http(monkeypatch, activa)
    meta.main(["activar", "--plan", plan, "--cliente", "acme", "--confirmo"])
    assert [p["path"].rsplit("/", 1)[1] for p in activa.de("POST", r".")] == [nuevo]


def test_conjunto_de_otra_cuenta_se_niega(meta, instancia, ficha_real, monkeypatch):
    http = _http_existente(monkeypatch, cuenta="99999")
    with pytest.raises(SystemExit) as e:
        meta.main(["crear", _plan_existente(instancia), "--cliente", "acme"])
    assert e.value.code == 1 and not http.de("POST", r".")


def test_conjunto_de_otra_campana_se_niega(meta, instancia, ficha_real, monkeypatch):
    http = _http_existente(monkeypatch)
    http.reglas.insert(0, ["GET", __import__("re").compile(r"/555555$"),
                           {"id": "555555", "account_id": "12345", "name": "OTRA", "objective": "OUTCOME_LEADS"}, None])
    with pytest.raises(SystemExit) as e:
        meta.main(["crear", _plan_existente(instancia, campana_id="555555"), "--cliente", "acme"])
    assert e.value.code == 1 and not http.de("POST", r".")


def test_conjunto_existente_no_lleva_presupuesto(meta, instancia, ficha_real, capsys):
    ruta = pathlib.Path(_plan_existente(instancia))
    plan = json.loads(ruta.read_text(encoding="utf-8"))
    plan["conjuntos"][0]["presupuesto_diario"] = 50
    ruta.write_text(json.dumps(plan), encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        meta.main(["crear", str(ruta), "--simular", "--cliente", "acme"])
    assert e.value.code == 1 and "presupuesto" in capsys.readouterr().err


def test_conjunto_nuevo_en_campana_cbo_existente(meta, instancia, ficha_real, monkeypatch):
    plan = json.loads(pathlib.Path(_plan_real(instancia)).read_text(encoding="utf-8"))
    plan["campana"] = {"id": "555555"}
    plan["conjuntos"] = plan["conjuntos"][:1]
    ruta = instancia / "clientes" / "acme" / "planes" / "2026-11-cbo.json"
    ruta.write_text(json.dumps(plan), encoding="utf-8")
    http = _http_crear(monkeypatch)
    http.reglas.insert(0, ["GET", __import__("re").compile(r"/555555$"),
                           {"id": "555555", "account_id": "12345", "objective": "OUTCOME_LEADS", "daily_budget": "5000"},
                           None])
    with pytest.raises(SystemExit):  # la campaña reparte el presupuesto: el conjunto no puede traer el suyo
        meta.main(["crear", str(ruta), "--cliente", "acme"])
    assert not http.de("POST", r".")
    plan["conjuntos"][0].pop("presupuesto_diario")
    ruta.write_text(json.dumps(plan), encoding="utf-8")
    meta.main(["crear", str(ruta), "--cliente", "acme"])
    conjunto = http.de("POST", r"/adsets$")[0]["form"]
    assert conjunto["campaign_id"] == "555555" and "daily_budget" not in conjunto
    assert not http.de("POST", r"/campaigns$")


# ---------------------------------------------------------------- I6: revisión de corrección
from datetime import datetime, timedelta, timezone  # noqa: E402

AHORA = datetime(2026, 11, 10, 10, 0, tzinfo=timezone.utc)


def test_fechas_de_graph_con_mas_0100(meta):
    """Hallazgo 22: «2026-12-01T23:59:59+0100» revienta `datetime.fromisoformat` antes de Python 3.11."""
    assert meta.dias_de({"inicio": "2026-12-01T00:00:00+0100", "fin": "2026-12-03T00:00:00+0100"}) == 2
    zona = timezone(timedelta(hours=1))
    assert meta._momento("2026-11-16T08:00:00+0100", zona).utcoffset() == timedelta(hours=1)
    assert meta._momento("2026-11-16 08:00", zona).tzinfo == zona


def test_presupuesto_activo_con_fin_en_formato_graph(meta, ficha_real, monkeypatch):
    """Hallazgo 22 (por la orden): `vigente` con un conjunto con fecha de fin no revienta y da el número."""
    conjuntos = {"data": [{"id": "900", "name": "A", "daily_budget": "5000", "end_time": "2099-12-01T23:59:59+0100",
                           "campaign": {"id": "899", "name": "C"}},
                          {"id": "901", "name": "B", "daily_budget": "9000", "end_time": "2020-01-01T00:00:00+0100",
                           "campaign": {"id": "898", "name": "D"}}]}
    _http(monkeypatch, HttpSimulado().cuando("GET", r"/act_12345/adsets$", conjuntos))
    ctx = meta.contexto("acme")
    total, activos = meta.presupuesto_activo(meta.conectar(ctx), ctx)
    assert total == 50.0 and [c["id"] for c in activos] == ["900"]


def test_diario_de_reparte_el_presupuesto_total(meta):
    """Hallazgo 8: un presupuesto total cuenta como su ritmo diario en lo que le queda de vida."""
    fin = (AHORA + timedelta(days=2)).isoformat()
    assert meta.diario_de({"lifetime_budget": "500000", "end_time": fin}, "EUR", AHORA) == 2500
    assert meta.diario_de({"lifetime_budget": "500000", "budget_remaining": "100000", "end_time": fin}, "EUR",
                          AHORA) == 500
    assert meta.diario_de({"daily_budget": "4000"}, "EUR", AHORA) == 40
    assert meta.diario_de({"lifetime_budget": "500000", "end_time": "2026-11-01T00:00:00+0100"}, "EUR", AHORA) == 0
    # sin fin conocido: entero en un día (nunca se subestima)
    assert meta.diario_de({"lifetime_budget": "500000"}, "EUR", AHORA) == 5000
    # empieza dentro de 3 días y dura 4: el ritmo es el de esos 4 días
    ini, fin = AHORA + timedelta(days=3), AHORA + timedelta(days=7)
    assert meta.diario_de({"lifetime_budget": "400000", "start_time": ini.isoformat(), "stop_time": fin.isoformat()},
                          "EUR", AHORA) == 1000


def test_presupuesto_que_entra_cuenta_lifetime_y_cbo(meta):
    """Hallazgo 8: (a) un conjunto en pausa con 5.000 € en 2 días son 2.500 €/día; (b) activar el único conjunto de
    una campaña CBO activa de 300 €/día mete 300 €/día. Antes salían 0 en los dos casos."""
    fin = (AHORA + timedelta(days=2)).isoformat()
    a = [{"id": "601", "nivel": "conjunto", "status": "PAUSED", "lifetime_budget": "500000", "end_time": fin,
          "campaign_id": "600"}]
    assert meta.presupuesto_que_entra(a, {}, {}, "EUR", AHORA) == 2500
    b = [{"id": "701", "nivel": "conjunto", "status": "PAUSED", "campaign_id": "700"}]
    campanas = {"700": {"id": "700", "status": "ACTIVE", "daily_budget": "30000", "otros_activos": False}}
    assert meta.presupuesto_que_entra(b, campanas, {}, "EUR", AHORA) == 300
    # con otro conjunto ya entregando, el presupuesto de la campaña ya estaba en juego
    campanas["700"]["otros_activos"] = True
    assert meta.presupuesto_que_entra(b, campanas, {}, "EUR", AHORA) == 0
    # la campaña en pausa y fuera de la orden: activar el conjunto no gasta
    campanas["700"] |= {"status": "PAUSED", "otros_activos": False}
    assert meta.presupuesto_que_entra(b, campanas, {}, "EUR", AHORA) == 0
    # campaña ABO en pausa: entran sus conjuntos activos (diarios o totales)
    c = [{"id": "800", "nivel": "campaña", "status": "PAUSED"}]
    hijos = {"800": [{"id": "801", "status": "ACTIVE", "daily_budget": "2000"},
                     {"id": "802", "status": "ACTIVE", "lifetime_budget": "100000", "end_time": fin}]}
    assert meta.presupuesto_que_entra(c, {}, hijos, "EUR", AHORA) == 520


def test_activar_frena_un_lifetime_por_encima_del_tope(meta, ficha_real, monkeypatch, capsys):
    """Hallazgo 8 por la orden, sin --confirmo: no se escribe nada en Meta."""
    fin = (datetime.now(timezone.utc) + timedelta(days=2, hours=1)).strftime("%Y-%m-%dT%H:%M:%S+0000")
    http = HttpSimulado()
    http.cuando("GET", r"/act_12345/campaigns$", {"data": []})
    http.cuando("GET", r"/act_12345/adsets$", lambda p: {"data": [] if "effective_status" in p["query"] else [
        {"id": "601", "name": "BROAD_LEAD", "status": "PAUSED", "lifetime_budget": "500000", "end_time": fin,
         "campaign_id": "600"}]})
    http.cuando("GET", r"/act_12345/ads$", {"data": []})
    _http(monkeypatch, http)
    with pytest.raises(SystemExit) as e:
        meta.main(["activar", "601", "--cliente", "acme"])
    assert e.value.code == 1 and not http.de("POST", r".")
    assert "2.500,00 EUR/día" in capsys.readouterr().err


@pytest.mark.parametrize("valor, esperado, aviso", [("off", "off", False), ("revisar", "revisar", False),
                                                    ("ON", "on", False), (False, "off", True), ("no", "off", True),
                                                    ("{}", "off", True), (True, "off", True), ("", "off", True)])
def test_mejoras_desconocidas_son_off(meta, valor, esperado, aviso):
    """Hallazgo 10: un valor que no es off, revisar ni on dejaba todas las mejoras de IA a Meta."""
    modo, texto = meta.mejoras_de({"mejoras_automaticas": valor} if valor != "" else {"mejoras_automaticas": ""})
    assert modo == esperado and bool(texto) == aviso


def test_ventana_de_atribucion_distinta_avisa(meta, instancia, ficha_real, capsys):
    """Bajo: `crear` no envía attribution_spec; si la ficha pide otra ventana que la de Meta, se dice."""
    ficha_real.write_text(ficha_real.read_text(encoding="utf-8").replace("ventana_atribucion: 7d_click_1d_view",
                                                                         "ventana_atribucion: 1d_click"),
                          encoding="utf-8")
    meta.main(["crear", _plan_real(instancia), "--simular", "--cliente", "acme"])
    assert "1d_click" in capsys.readouterr().out
