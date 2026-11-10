"""formularios_meta.py: plantillas revisadas sin red, creación solo con --confirmo e idempotente, auditoría de
formularios y descarga de leads con lo personal en privado/ y solo agregados en datos/."""
from __future__ import annotations

import copy
import csv
import importlib
import json
import pathlib
import urllib.request
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from http_simulado import HttpSimulado

RAIZ_PRODUCTO = pathlib.Path(__file__).resolve().parents[2]
PLANTILLAS = RAIZ_PRODUCTO / ".claude" / "skills" / "formulario-instantaneo" / "plantillas"
NOMBRES = ["diagnostico-corto", "llamada-cualificada", "recurso-o-taller"]
VARIABLES = ("META_TOKEN", "META_TOKEN_ACME", "META_TOKEN_PAGINA", "META_TOKEN_PAGINA_ACME", "META_APP_SECRET",
             "META_APP_SECRET_ACME", "META_API_VERSION")


@pytest.fixture
def fm(instancia, monkeypatch):
    import meta_ads
    import formularios_meta
    importlib.reload(meta_ads)
    modulo = importlib.reload(formularios_meta)
    monkeypatch.setattr(meta_ads.time, "sleep", lambda *_: None)
    for v in VARIABLES:
        monkeypatch.delenv(v, raising=False)
    return modulo


@pytest.fixture
def ficha_real(instancia):
    """La ficha de acme con una Página con forma real (ID corto para no parecer una fuga)."""
    f = instancia / "clientes" / "acme" / "ficha.md"
    f.write_text(f.read_text(encoding="utf-8").replace('pagina: ""', 'pagina: "222222"'), encoding="utf-8")
    return f


def _http(monkeypatch, http: HttpSimulado | None = None) -> HttpSimulado:
    http = http or HttpSimulado()
    monkeypatch.setattr(urllib.request, "urlopen", http)
    return http


def _plantilla(nombre: str) -> dict:
    return json.loads((PLANTILLAS / f"{nombre}.json").read_text(encoding="utf-8"))


def _lista_para_crear(instancia, nombre: str, **cambios) -> str:
    """La plantilla con URLs del cliente y la revisión de políticas hecha, guardada en su carpeta de planes."""
    p = json.loads(json.dumps(_plantilla(nombre)).replace("acme-automations.example", "www.acme-automations.es"))
    p["revision_politicas"] = "OK · 2026-11-09 · revisor-politicas"
    p.update(cambios)
    ruta = instancia / "clientes" / "acme" / "planes" / f"2026-11-09_{nombre}.json"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(p, ensure_ascii=False), encoding="utf-8")
    return str(ruta)


def _correr(fm, *args) -> int:
    try:
        fm.main([str(a) for a in args])
    except SystemExit as e:
        return int(e.code or 0)
    return 0


def _cambios(instancia) -> list[dict]:
    f = instancia / "logs" / "cambios.jsonl"
    return [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines()] if f.exists() else []


def _http_crear(monkeypatch, existentes=None, guardadas=None) -> HttpSimulado:
    http = HttpSimulado()
    http.cuando("GET", r"/222222$", {"id": "222222", "access_token": "tok-pagina-derivado"})
    http.cuando("GET", r"/222222/leadgen_forms$", {"data": existentes or []})
    http.cuando("POST", r"/222222/leadgen_forms$", {"id": "444444"})

    def releer(p):
        form = http.de("POST", r"/leadgen_forms$")[-1]["form"]
        n = len(json.loads(form["questions"])) if guardadas is None else guardadas
        return {"id": "444444", "name": form["name"], "status": "ACTIVE",
                "is_optimized_for_quality": form["is_optimized_for_quality"] == "true",
                "questions": [{"type": "CUSTOM"}] * n}
    http.cuando("GET", r"/444444$", releer)
    return _http(monkeypatch, http)


# ---------------------------------------------------------------- plantillas (sin red)

@pytest.mark.parametrize("nombre", NOMBRES)
def test_plantillas_simulan_sin_red(fm, monkeypatch, capsys, nombre):
    http = _http(monkeypatch)  # sin reglas: cualquier petición haría fallar el test
    assert _correr(fm, "crear", PLANTILLAS / f"{nombre}.json", "--simular") == 0
    salida = capsys.readouterr().out
    assert "No se ha tocado Meta" in salida and "revisión de políticas pendiente" in salida
    assert http.peticiones == []
    errores, pendientes, _ = fm.revisa_plantilla(_plantilla(nombre))
    assert errores == []
    assert any("de ejemplo" in x for x in pendientes)


@pytest.mark.parametrize("nombre", NOMBRES)
def test_plantillas_son_genericas_y_en_espanol(nombre):
    texto = (PLANTILLAS / f"{nombre}.json").read_text(encoding="utf-8")
    p = json.loads(texto)
    assert "/Users/" not in texto and "act_" not in texto
    assert p["idioma"] == "ES_ES" and p["revision_politicas"] == "pendiente"
    urls = [p["privacidad"]["url"], p["final"]["url"]] + [f["url"] for f in (p.get("finales_alternativos") or {}).values()]
    assert all(u.startswith("https://acme-automations.example/") for u in urls)
    assert p["parametros"]["formulario"] == nombre
    assert any(q.get("encaje") for q in p["preguntas"])


def test_simular_json_da_el_payload(fm, monkeypatch, capsys):
    _http(monkeypatch)
    assert _correr(fm, "crear", PLANTILLAS / "recurso-o-taller.json", "--simular", "--json") == 0
    datos = json.loads(capsys.readouterr().out)
    assert datos["ok"] and datos["simulado"]
    assert datos["payload"]["is_optimized_for_quality"] == "false"
    assert datos["payload"]["name"] == "acme_guia-que-automatizar_v1"


def test_construir_traduce_a_la_api(fm):
    payload = fm.construir(_plantilla("llamada-cualificada"))
    tipos = [q["type"] for q in payload["questions"]]
    assert tipos == ["CUSTOM"] * 6 + ["FULL_NAME", "WORK_EMAIL", "PHONE", "COMPANY_NAME"]
    inversion = payload["questions"][3]
    assert inversion["key"] == "inversion" and inversion["options"][0] == {"key": "menos_3000",
                                                                            "value": "Menos de 3.000 €"}
    assert "options" not in payload["questions"][5] and payload["questions"][5]["inline_context"]
    assert payload["questions"][7]["should_enforce_work_email"] is True
    assert payload["is_optimized_for_quality"] == "true"
    assert payload["phone_otp_verification_type"] == "OTP_REQUIRED" and "is_phone_sms_verify_enabled" not in payload
    assert payload["block_display_for_non_targeted_viewer"] == "true"
    assert payload["locale"] == "ES_ES"
    assert payload["privacy_policy"] == {"url": "https://acme-automations.example/privacidad",
                                         "link_text": "Política de privacidad de Acme Automations"}
    gracias = payload["thank_you_page"]
    assert gracias["button_type"] == "VIEW_WEBSITE" and gracias["country_code"] == "ES"
    assert gracias["website_url"] == payload["follow_up_action_url"] == "https://acme-automations.example/reservar-llamada"
    assert payload["context_card"]["style"] == "LIST_STYLE" and len(payload["context_card"]["content"]) == 3
    assert payload["custom_disclaimer"]["checkboxes"] == [
        {"key": "novedades", "text": "Quiero recibir por email casos y novedades de Acme Automations",
         "is_required": False, "is_checked_by_default": False}]
    assert payload["tracking_parameters"]["oferta"] == "llamada"
    assert "status" not in payload and "logica" not in json.dumps(payload)


def test_construir_llamar_y_parrafo(fm):
    p = _plantilla("recurso-o-taller")
    p["final"] = {"titulo": "Te llamamos", "boton": "llamar", "telefono": "+34 600 000 000"}
    payload = fm.construir(p)
    assert payload["thank_you_page"]["button_type"] == "CALL_BUSINESS"
    assert payload["thank_you_page"]["business_phone_number"] == "+34600000000"
    assert "follow_up_action_url" not in payload
    assert payload["context_card"]["style"] == "PARAGRAPH_STYLE"


def _base_valida() -> dict:
    p = _plantilla("recurso-o-taller")
    p["revision_politicas"] = "OK"
    return p


@pytest.mark.parametrize("texto, categoria", [
    ("¿Cuánto ganas al año?", "información financiera"),
    ("¿Tienes alguna enfermedad crónica?", "salud"),
    ("¿Cuál es tu DNI?", "identificadores oficiales"),
    ("¿A qué partido político votas?", "afiliación política"),
])
def test_datos_restringidos_son_error(fm, texto, categoria):
    p = _base_valida()
    p["preguntas"][1]["texto"] = texto
    errores, _, _ = fm.revisa_plantilla(p)
    assert any(categoria in e for e in errores)


def test_revision_de_la_plantilla(fm):
    def revisa(**cambios):
        p = _base_valida()
        for k, v in cambios.items():
            p[k] = v
        return fm.revisa_plantilla(p)

    assert revisa()[0] == []
    assert any("email ni teléfono" in e for e in revisa(preguntas=[_base_valida()["preguntas"][0]])[0])
    assert any("`verificar_telefono` necesita" in e for e in revisa(verificar_telefono=True)[0])
    assert any("creatividad_enriquecida" in e for e in revisa(tipo="creatividad_enriquecida")[0])
    assert any("privacidad.url" in e for e in revisa(privacidad={})[0])
    assert any("https://" in e for e in revisa(privacidad={"url": "http://acme.es/p"})[0])
    muchas = [{"clave": f"p{i}", "tipo": "opciones", "texto": f"Pregunta {i}",
               "opciones": [{"clave": "a", "texto": "A"}, {"clave": "b", "texto": "B"}]} for i in range(16)]
    assert any("Meta admite 15" in e for e in revisa(preguntas=muchas + [{"tipo": "email"}])[0])
    p = _base_valida()
    p["preguntas"][0]["encaje"] = ["no_existe"]
    p["preguntas"].append({"clave": "rara", "tipo": "desconocido", "texto": "x"})
    errores = fm.revisa_plantilla(p)[0]
    assert any("no_existe" in e for e in errores) and any("desconocido" in e for e in errores)
    p = _base_valida()
    p["preguntas"][1]["texto"] = "¿Cuál es tu email de contacto?"
    assert any("prellenada" in a for a in fm.revisa_plantilla(p)[2])
    p["preguntas"][1]["texto"] = "¿Cuánto factura tu empresa al año?"
    assert any("zona gris" in a for a in fm.revisa_plantilla(p)[2])
    p = _base_valida()
    p["logica"] = [{"si": {"pregunta": "tamano", "respuesta": ["solo_yo"]}, "ir_a": "final:no_existe"}]
    assert any("finales_alternativos" in e for e in fm.revisa_plantilla(p)[0])
    p["api"] = {"status": "ACTIVE"}
    assert any("api.status" in e for e in fm.revisa_plantilla(p)[0])


@pytest.mark.parametrize("valor, esperado", [
    ("OK", "ok"), ("OK · 2026-11-09 · revisor-politicas", "ok"), ("OK con cambios aplicados · 2026-11-09", "ok"),
    ("OK con cambios", "pendiente"), ("pendiente", "pendiente"), ("", "pendiente"),
    ("NO publicar · datos de salud", "no"),
])
def test_veredicto_de_politicas(fm, valor, esperado):
    assert fm.veredicto({"revision_politicas": valor}) == esperado


def test_no_publicar_bloquea_incluso_simulando(fm, monkeypatch, capsys, instancia):
    http = _http(monkeypatch)
    ruta = _lista_para_crear(instancia, "recurso-o-taller", revision_politicas="NO publicar")
    assert _correr(fm, "crear", ruta, "--simular") == 1
    assert "NO publicar" in capsys.readouterr().err and http.peticiones == []


# ---------------------------------------------------------------- crear

def test_crear_sin_confirmo_no_toca_meta(fm, monkeypatch, capsys, instancia, ficha_real):
    http = _http(monkeypatch)
    monkeypatch.setenv("META_TOKEN", "tok-sistema")
    assert _correr(fm, "crear", _lista_para_crear(instancia, "recurso-o-taller"), "--cliente", "acme") == 1
    assert "--confirmo" in capsys.readouterr().err
    assert http.peticiones == [] and _cambios(instancia) == []


def test_crear_con_pendientes_no_toca_meta(fm, monkeypatch, capsys, instancia, ficha_real):
    http = _http(monkeypatch)
    monkeypatch.setenv("META_TOKEN", "tok-sistema")
    ruta = _lista_para_crear(instancia, "recurso-o-taller", revision_politicas="pendiente")
    assert _correr(fm, "crear", ruta, "--cliente", "acme", "--confirmo") == 1
    assert "revisión de políticas pendiente" in capsys.readouterr().err and http.peticiones == []


def test_crear_sin_pagina_es_pendiente(fm, monkeypatch, capsys, instancia):
    http = _http(monkeypatch)
    assert _correr(fm, "crear", _lista_para_crear(instancia, "recurso-o-taller"), "--cliente", "acme",
                   "--confirmo") == 1
    assert "falta la Página" in capsys.readouterr().err and http.peticiones == []


def test_crear_confirmado_registra_y_es_idempotente(fm, monkeypatch, capsys, instancia, ficha_real):
    monkeypatch.setenv("META_TOKEN", "tok-sistema")
    http = _http_crear(monkeypatch)
    ruta = _lista_para_crear(instancia, "recurso-o-taller")
    assert _correr(fm, "crear", ruta, "--cliente", "acme", "--confirmo") == 0
    salida = capsys.readouterr()
    assert "444444" in salida.out and "Fila para el change log" in salida.out
    assert "tok-" not in salida.out + salida.err

    # El token de la Página se pide con el del sistema y es el que firma el POST.
    assert http.de("GET", r"/222222$")[0]["query"]["fields"] == "access_token"
    post = http.de("POST", r"/222222/leadgen_forms$")
    assert len(post) == 1 and post[0]["form"]["access_token"] == "tok-pagina-derivado"
    enviado = post[0]["form"]
    esperado = fm.construir(json.loads(pathlib.Path(ruta).read_text(encoding="utf-8")))
    assert enviado["name"] == "acme_guia-que-automatizar_v1"
    assert json.loads(enviado["questions"]) == esperado["questions"]
    assert json.loads(enviado["thank_you_page"]) == esperado["thank_you_page"]
    assert enviado["is_optimized_for_quality"] == "false" and "status" not in enviado

    cambios = _cambios(instancia)
    assert len(cambios) == 1
    assert cambios[0]["accion"] == "crear_formulario" and cambios[0]["entidad_id"] == "444444"
    assert cambios[0]["cliente"] == "acme" and cambios[0]["sistema"] == "meta"
    assert "tok-" not in json.dumps(cambios)
    estado = json.loads((instancia / "clientes" / "acme" / "planes" / "formularios.json").read_text(encoding="utf-8"))
    guardado = estado["formularios"]["222222:acme_guia-que-automatizar_v1"]
    assert guardado["id"] == "444444" and guardado["encaje"] == {"tamano": ["10_49", "50_mas"]}
    assert not guardado["plantilla"].startswith("/")

    # Segunda vez: no se duplica ni se llama a Meta.
    antes = len(http.peticiones)
    assert _correr(fm, "crear", ruta, "--cliente", "acme", "--confirmo") == 0
    assert "Ya creado" in capsys.readouterr().out
    assert len(http.peticiones) == antes and len(_cambios(instancia)) == 1


def test_crear_con_token_de_pagina_no_lo_pide(fm, monkeypatch, capsys, instancia, ficha_real):
    monkeypatch.setenv("META_TOKEN_PAGINA_ACME", "tok-pagina-directo")
    monkeypatch.setenv("META_APP_SECRET", "secreto")
    http = _http_crear(monkeypatch)
    assert _correr(fm, "crear", _lista_para_crear(instancia, "recurso-o-taller"), "--cliente", "acme",
                   "--confirmo") == 0
    assert http.de("GET", r"/222222$") == []
    post = http.de("POST", r"/leadgen_forms$")[0]["form"]
    assert post["access_token"] == "tok-pagina-directo" and post["appsecret_proof"]


def test_crear_para_si_la_pagina_ya_tiene_ese_nombre(fm, monkeypatch, capsys, instancia, ficha_real):
    monkeypatch.setenv("META_TOKEN_PAGINA", "tok-pagina")
    http = _http_crear(monkeypatch, existentes=[{"id": "555555", "name": "acme_guia-que-automatizar_v1",
                                                 "status": "ACTIVE"}])
    assert _correr(fm, "crear", _lista_para_crear(instancia, "recurso-o-taller"), "--cliente", "acme",
                   "--confirmo") == 1
    err = capsys.readouterr().err
    assert "555555" in err and "no se editan" in err
    assert http.de("POST", r"/leadgen_forms$") == [] and _cambios(instancia) == []


def test_crear_para_con_100_formularios_para_no_sobrescribir(fm, monkeypatch, capsys, instancia, ficha_real):
    monkeypatch.setenv("META_TOKEN_PAGINA", "tok-pagina")
    http = _http_crear(monkeypatch, existentes=[{"id": str(600000 + i), "name": f"viejo_{i}"} for i in range(100)])
    assert _correr(fm, "crear", _lista_para_crear(instancia, "recurso-o-taller"), "--cliente", "acme",
                   "--confirmo") == 1
    assert "sobrescribe el más antiguo" in capsys.readouterr().err
    assert http.de("POST", r"/leadgen_forms$") == [] and _cambios(instancia) == []


def test_verificar_telefono_no_vale_con_telefono_de_trabajo(fm):
    p = _base_valida()
    p["preguntas"].append({"tipo": "telefono_trabajo"})
    p["verificar_telefono"] = True
    assert any("no vale `telefono_trabajo`" in e for e in fm.revisa_plantilla(p)[0])
    p["preguntas"].append({"tipo": "telefono"})
    assert fm.revisa_plantilla(p)[0] == []


@pytest.mark.parametrize("valor, v27, v26", [
    (True, {"phone_otp_verification_type": "OTP_REQUIRED"}, {"is_phone_sms_verify_enabled": "true"}),
    ("obligatorio", {"phone_otp_verification_type": "OTP_REQUIRED"}, {"is_phone_sms_verify_enabled": "true"}),
    (False, {"phone_otp_verification_type": "NOT_ENABLED"}, {"is_phone_sms_verify_enabled": "false"}),
    ("no", {"phone_otp_verification_type": "NOT_ENABLED"}, {"is_phone_sms_verify_enabled": "false"}),
])
def test_verificar_telefono_segun_la_version(fm, valor, v27, v26):
    p = _base_valida()
    p["preguntas"].append({"tipo": "telefono"})
    p["verificar_telefono"] = valor
    campos = ("phone_otp_verification_type", "is_phone_sms_verify_enabled", "ad_account_id")
    assert {k: v for k, v in fm.construir(p, version="v27.0").items() if k in campos} == v27
    assert {k: v for k, v in fm.construir(p, version="v26.0").items() if k in campos} == v26
    assert fm.revisa_plantilla(p)[0] == []
    sin = _base_valida()
    assert not any(k in fm.construir(sin) for k in campos)  # sin la clave, lo que diga Meta


def test_verificacion_opcional(fm, monkeypatch):
    p = _base_valida()
    p["preguntas"].append({"tipo": "telefono"})
    p["verificar_telefono"] = "opcional"
    payload = fm.construir(p, version="v27.0", cuenta="act_12345")
    assert payload["phone_otp_verification_type"] == "OTP_OPTIONAL" and payload["ad_account_id"] == "12345"
    errores, _, avisos = fm.revisa_plantilla(p)
    assert errores == [] and any("OTP_OPTIONAL" in a for a in avisos)
    monkeypatch.setenv("META_API_VERSION", "v26.0")
    assert any("v27.0 o posterior" in e for e in fm.revisa_plantilla(p)[0])
    with pytest.raises(ValueError):
        fm.construir(p)
    p["verificar_telefono"] = "siempre"
    assert any("`verificar_telefono` es true" in e for e in fm.revisa_plantilla(p)[0])


def test_verificacion_leida_y_auditoria(fm):
    assert fm.verificacion_leida({"phone_otp_verification_type": "OTP_OPTIONAL"}) == "opcional"
    assert fm.verificacion_leida({"phone_otp_verification_type": None, "is_phone_sms_verify_enabled": True}) == \
        "obligatoria"
    assert fm.verificacion_leida({"phone_otp_verification_type": None}) == "desconocida"  # formulario antiguo: null
    assert fm.verificacion_leida({"phone_otp_verification_type": "NOT_ENABLED"}) == "no"
    hallazgos = fm.auditar({"questions": [{"type": "PHONE"}], "phone_otp_verification_type": None})
    assert any(n == "⚠" and "verifica el teléfono" in t for n, t in hallazgos)
    hallazgos = fm.auditar({"questions": [{"type": "PHONE"}], "phone_otp_verification_type": "OTP_REQUIRED"})
    assert ("✓", "verifica el teléfono (obligatoria; código por WhatsApp o SMS)") in hallazgos


def test_crear_con_logica_exige_sin_logica(fm, monkeypatch, capsys, instancia, ficha_real):
    monkeypatch.setenv("META_TOKEN_PAGINA", "tok-pagina")
    http = _http_crear(monkeypatch)
    ruta = _lista_para_crear(instancia, "diagnostico-corto")
    assert _correr(fm, "crear", ruta, "--cliente", "acme", "--confirmo") == 1
    assert "lógica condicional" in capsys.readouterr().err and http.peticiones == []

    assert _correr(fm, "crear", ruta, "--cliente", "acme", "--confirmo", "--sin-logica") == 0
    assert "Sin lógica condicional" in capsys.readouterr().out
    assert len(http.de("POST", r"/leadgen_forms$")) == 1
    assert "sin la lógica condicional" in _cambios(instancia)[0]["detalle"]
    estado = json.loads((instancia / "clientes" / "acme" / "planes" / "formularios.json").read_text(encoding="utf-8"))
    assert estado["formularios"]["222222:acme_diagnostico-20min_v1"]["logica_pendiente"] is True


def test_crear_avisa_si_meta_guarda_otra_cosa(fm, monkeypatch, capsys, instancia, ficha_real):
    monkeypatch.setenv("META_TOKEN_PAGINA", "tok-pagina")
    _http_crear(monkeypatch, guardadas=1)
    assert _correr(fm, "crear", _lista_para_crear(instancia, "recurso-o-taller"), "--cliente", "acme",
                   "--confirmo") == 0
    assert "Al releerlo: preguntas: enviadas 4, guardadas 1" in capsys.readouterr().out


def test_crear_rechazado_por_meta_no_registra(fm, monkeypatch, capsys, instancia, ficha_real):
    monkeypatch.setenv("META_TOKEN_PAGINA", "tok-pagina")
    http = _http_crear(monkeypatch)
    http.reglas.insert(0, ["POST", __import__("re").compile(r"/leadgen_forms$"),
                           (400, {"error": {"code": 100, "message": "Invalid parameter",
                                            "error_user_msg": "La URL de privacidad no es válida"}}), None])
    assert _correr(fm, "crear", _lista_para_crear(instancia, "recurso-o-taller"), "--cliente", "acme",
                   "--confirmo") == 1
    err = capsys.readouterr().err
    assert "URL de privacidad" in err and "No se ha creado nada" in err
    assert _cambios(instancia) == []
    assert not (instancia / "clientes" / "acme" / "planes" / "formularios.json").exists()


def test_sin_token_sale_con_2(fm, monkeypatch, capsys, instancia, ficha_real):
    http = _http(monkeypatch)
    assert _correr(fm, "listar", "--cliente", "acme") == 2
    err = capsys.readouterr().err
    assert "META_TOKEN_PAGINA_ACME" in err and "guia" in err and http.peticiones == []


def test_token_caducado_sale_con_2(fm, monkeypatch, capsys, instancia, ficha_real):
    monkeypatch.setenv("META_TOKEN_PAGINA", "tok-pagina")
    _http(monkeypatch, HttpSimulado().cuando("GET", r"/leadgen_forms$",
                                             (400, {"error": {"code": 190, "message": "Session has expired"}})))
    assert _correr(fm, "listar", "--cliente", "acme") == 2
    assert "token" in capsys.readouterr().err


def test_pagina_sin_asignar_sale_con_2(fm, monkeypatch, capsys, instancia, ficha_real):
    monkeypatch.setenv("META_TOKEN", "tok-sistema")
    _http(monkeypatch, HttpSimulado().cuando("GET", r"/222222$", {"id": "222222"}))
    assert _correr(fm, "listar", "--cliente", "acme") == 2
    assert "tarea de crear anuncios" in capsys.readouterr().err


# ---------------------------------------------------------------- guía

def test_guia_markdown(fm, monkeypatch, capsys, instancia):
    http = _http(monkeypatch)
    salida = instancia / "clientes" / "acme" / "planes" / "diagnostico_formulario.md"
    assert _correr(fm, "guia", PLANTILLAS / "diagnostico-corto.json", "--cliente", "acme", "--salida", salida) == 0
    texto = salida.read_text(encoding="utf-8")
    assert "Mayor intención (Higher intent)" in texto
    assert "Lógica condicional" in texto and "si «tamano» = solo_yo" in texto
    assert "Book time" in texto and "Final alternativo «recurso»" in texto
    assert "lead-ads-testing" in texto and "## Antes de publicar" in texto
    assert http.peticiones == []


def test_guia_admite_creatividad_enriquecida(fm, monkeypatch, capsys, tmp_path):
    _http(monkeypatch)
    p = _plantilla("recurso-o-taller")
    p["tipo"] = "creatividad_enriquecida"
    ruta = tmp_path / "rica.json"
    ruta.write_text(json.dumps(p), encoding="utf-8")
    assert _correr(fm, "guia", ruta) == 0
    assert "Creatividad enriquecida" in capsys.readouterr().out
    assert _correr(fm, "crear", ruta, "--simular") == 1


# ---------------------------------------------------------------- listar y ver

def test_listar(fm, monkeypatch, capsys, instancia, ficha_real):
    monkeypatch.setenv("META_TOKEN_PAGINA", "tok-pagina")
    (instancia / "clientes" / "acme" / "planes").mkdir(exist_ok=True)
    (instancia / "clientes" / "acme" / "planes" / "formularios.json").write_text(json.dumps(
        {"formularios": {"222222:acme_v1": {"id": "444444", "plantilla": "clientes/acme/planes/x.json"}}}),
        encoding="utf-8")
    http = _http(monkeypatch, HttpSimulado().cuando("GET", r"/222222/leadgen_forms$", {"data": [
        {"id": "444444", "name": "acme_v1", "status": "ACTIVE", "locale": "es_ES",
         "created_time": "2026-11-01T10:00:00+0000", "leads_count": 37, "expired_leads_count": 0},
        {"id": "555555", "name": "antiguo", "status": "ARCHIVED", "leads_count": 120, "expired_leads_count": 80}]}))
    assert _correr(fm, "listar", "--cliente", "acme") == 0
    salida = capsys.readouterr().out
    assert "acme_v1" in salida and "← clientes/acme/planes/x.json" in salida and "antiguo" in salida
    assert http.peticiones[0]["query"]["fields"].startswith("id,name,status")
    assert _correr(fm, "listar", "--cliente", "acme", "--json") == 0
    datos = json.loads(capsys.readouterr().out)
    assert [f["leads"] for f in datos["formularios"]] == [37, 120]


def test_ver_audita_y_quita_campos_desconocidos(fm, monkeypatch, capsys, instancia, ficha_real):
    monkeypatch.setenv("META_TOKEN_PAGINA", "tok-pagina")
    form = {"id": "444444", "name": "acme_rapido", "status": "ACTIVE", "is_optimized_for_quality": False,
            "questions": [{"type": "CUSTOM", "key": "tamano", "label": "¿Cuántas personas sois?",
                           "options": [{"key": "a", "value": "1-9"}, {"key": "b", "value": "10+"}]},
                          {"type": "CUSTOM", "key": "ingresos", "label": "¿Cuánto ganas al mes?"},
                          {"type": "FULL_NAME", "key": "full_name"}],
            "privacy_policy_url": "https://acme.test/p", "tracking_parameters": [],
            "thank_you_page": {"title": "Gracias", "button_type": "NONE"}, "expired_leads_count": 3}
    error_campo = (400, {"error": {"code": 100, "message": "(#100) Tried accessing nonexisting field "
                                                           "(block_display_for_non_targeted_viewer) on node type "
                                                           "(LeadgenForm)"}})
    http = _http(monkeypatch, HttpSimulado().cuando("GET", r"/444444$", [error_campo, form]))
    assert _correr(fm, "ver", "444444", "--cliente", "acme") == 0
    salida = capsys.readouterr().out
    campos = [p["query"]["fields"].split(",") for p in http.peticiones]
    assert "block_display_for_non_targeted_viewer" in campos[0]
    assert "block_display_for_non_targeted_viewer" not in campos[1] and "questions" in campos[1]
    assert "✗ sin email ni teléfono" in salida
    assert "más volumen" in salida and "información financiera" in salida
    assert "sin parámetros de seguimiento" in salida and "pantalla final sin botón" in salida
    assert "3 leads caducados" in salida


def test_ver_error_que_no_es_de_campo_no_se_reintenta(fm, monkeypatch, capsys, instancia, ficha_real):
    monkeypatch.setenv("META_TOKEN_PAGINA", "tok-pagina")
    http = _http(monkeypatch, HttpSimulado().cuando("GET", r"/444444$",
                                                    (400, {"error": {"code": 803, "message": "Unknown object"}})))
    assert _correr(fm, "ver", "444444", "--cliente", "acme") == 1
    assert len(http.peticiones) == 1


# ---------------------------------------------------------------- leads

FORM = {"id": "444444", "name": "acme_diagnostico", "questions": [
    {"type": "CUSTOM", "key": "tamano", "options": [{"key": "solo_yo", "value": "Solo yo"},
                                                    {"key": "10_49", "value": "De 10 a 49"},
                                                    {"key": "50_249", "value": "De 50 a 249"}]},
    {"type": "CUSTOM", "key": "contexto"},
    {"type": "FULL_NAME", "key": "full_name"}, {"type": "EMAIL", "key": "email"},
    {"type": "PHONE", "key": "phone_number"}]}


def _lead(i, cuando, tamano, ad="777001", organico=False):
    return {"id": f"90000{i}", "created_time": cuando, "form_id": "444444", "is_organic": organico,
            "ad_id": None if organico else ad, "ad_name": None if organico else f"anuncio_{ad}",
            "campaign_id": None if organico else "888001", "campaign_name": None if organico else "ES_LEADS",
            "platform": "ig" if i % 2 else "fb",
            "field_data": [{"name": "tamano", "values": [tamano]},
                           {"name": "contexto", "values": [f"Texto libre privado {i}"]},
                           {"name": "full_name", "values": [f"Persona Ejemplo {i}"]},
                           {"name": "email", "values": [f"persona{i}@acme.test"]},
                           {"name": "phone_number", "values": [f"+3460000000{i}"]}]}


LEADS = [
    _lead(1, "2026-11-03T10:15:00+0000", "10_49"),                       # clave de la opción, en horario
    _lead(2, "2026-11-04T21:30:00+0000", "De 50 a 249"),                 # texto de la opción, 22:30 en Madrid
    _lead(3, "2026-11-07T10:00:00+0000", "solo_yo", ad="777002"),       # sábado
    _lead(4, "2026-11-05T09:00:00+0000", "10_49", organico=True),
    _lead(5, "2026-11-01T22:30:00+0000", "10_49"),                       # 23:30 del día 1 en Madrid: fuera
]


def _http_leads(monkeypatch, paginas=None) -> HttpSimulado:
    http = HttpSimulado()
    http.cuando("GET", r"/444444$", FORM)
    siguiente = "https://graph.facebook.com/v26.0/444444/leads?after=abc&access_token=tok-pagina"
    http.cuando("GET", r"/444444/leads$", paginas or [{"data": LEADS[:2], "paging": {"next": siguiente}},
                                                      {"data": LEADS[2:]}])
    return _http(monkeypatch, http)


def _csv(ruta: pathlib.Path) -> list[dict]:
    with ruta.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_leads_separa_privado_de_agregados(fm, monkeypatch, capsys, instancia, ficha_real):
    monkeypatch.setenv("META_TOKEN_PAGINA", "tok-pagina")
    http = _http_leads(monkeypatch)
    plantilla = _lista_para_crear(instancia, "diagnostico-corto")
    assert _correr(fm, "leads", "444444", "--cliente", "acme", "--desde", "2026-11-02", "--hasta", "2026-11-08",
                   "--encaje", plantilla) == 0
    salida = capsys.readouterr().out

    # Filtro de fechas en la zona de la ficha y paginación.
    peticion = http.de("GET", r"/444444/leads$")[0]
    filtro = json.loads(peticion["query"]["filtering"])
    t0 = int(datetime(2026, 11, 2, tzinfo=ZoneInfo("Europe/Madrid")).timestamp())
    assert {"field": "time_created", "operator": "GREATER_THAN_OR_EQUAL", "value": t0} in filtro
    assert len(http.de("GET", r"/444444/leads$")) == 2

    cliente = instancia / "clientes" / "acme"
    privado = _csv(cliente / "privado" / "formulario-444444_2026-11-02_2026-11-08.csv")
    assert [f["leadgen_id"] for f in privado] == ["900001", "900002", "900003", "900004"]
    assert privado[0]["email"] == "persona1@acme.test" and privado[0]["fecha_hora"].startswith("2026-11-03T11:15")
    assert privado[1]["tamano"] == "De 50 a 249" and privado[3]["organico"] == "1"

    por_anuncio = _csv(cliente / "datos" / "formulario-444444_2026-11-02_2026-11-08.csv")
    respuestas = _csv(cliente / "datos" / "formulario-444444_2026-11-02_2026-11-08_respuestas.csv")
    agregado = (cliente / "datos" / "formulario-444444_2026-11-02_2026-11-08.csv").read_text(encoding="utf-8") + \
        (cliente / "datos" / "formulario-444444_2026-11-02_2026-11-08_respuestas.csv").read_text(encoding="utf-8")
    for dato_personal in ("@", "+346", "Persona Ejemplo", "Texto libre"):
        assert dato_personal not in agregado and dato_personal not in salida
    # La plantilla pide encaje también en urgencia y rol, que este formulario no tiene: solo cuenta tamaño.
    a1 = next(f for f in por_anuncio if f["ad_id"] == "777001")
    assert a1["leads"] == "2" and a1["encaje"] == "2" and a1["fuera_horario"] == "1" and a1["encaje_pct"] == "100.0"
    assert next(f for f in por_anuncio if f["ad_id"] == "777002")["encaje"] == "0"
    organico = next(f for f in por_anuncio if f["anuncio"] == "(orgánico)")
    assert organico["leads"] == "1" and organico["organicos"] == "1"
    total = {f["respuesta"]: f["leads"] for f in respuestas if f["ad_id"] == "TOTAL" and f["pregunta"] == "tamano"}
    assert total == {"10_49": "2", "50_249": "1", "solo_yo": "1"}
    assert not any(f["pregunta"] == "contexto" for f in respuestas)

    assert "4 leads" in salida and "Encaje declarado: 3 de 4" in salida and "no el cualificado" in salida
    assert "no tiene rol, urgencia" in salida and "tamano ∈ {10_49, 50_249}" in salida
    assert _cambios(instancia) == []  # leer leads no es una escritura en Meta


def test_leads_usa_el_encaje_guardado_al_crear(fm, monkeypatch, capsys, instancia, ficha_real):
    monkeypatch.setenv("META_TOKEN_PAGINA", "tok-pagina")
    _http_leads(monkeypatch)
    (instancia / "clientes" / "acme" / "planes").mkdir(exist_ok=True)
    (instancia / "clientes" / "acme" / "planes" / "formularios.json").write_text(json.dumps(
        {"formularios": {"222222:x": {"id": "444444", "encaje": {"tamano": ["50_249"]}}}}), encoding="utf-8")
    assert _correr(fm, "leads", "444444", "--cliente", "acme", "--desde", "2026-11-02", "--hasta", "2026-11-08",
                   "--json", "--sin-archivos") == 0
    datos = json.loads(capsys.readouterr().out)
    assert datos["leads"] == 4 and datos["encaje"] == 1 and datos["encaje_pct"] == 25.0
    assert datos["fuera_horario"] == 2 and datos["organicos"] == 1
    assert "@" not in json.dumps(datos) and "csv_privado" not in datos
    assert not (instancia / "clientes" / "acme" / "privado" / "formulario-444444_2026-11-02_2026-11-08.csv").exists()


def test_leads_sin_encaje_ni_leads(fm, monkeypatch, capsys, instancia, ficha_real):
    monkeypatch.setenv("META_TOKEN_PAGINA", "tok-pagina")
    _http_leads(monkeypatch, paginas=[{"data": []}])
    assert _correr(fm, "leads", "444444", "--cliente", "acme", "--desde", "2026-11-02", "--hasta", "2026-11-08") == 0
    assert "Sin leads en el periodo" in capsys.readouterr().out
    assert not (instancia / "clientes" / "acme" / "datos" / "formulario-444444_2026-11-02_2026-11-08.csv").exists()


def test_leads_avisa_de_los_90_dias(fm, monkeypatch, capsys, instancia, ficha_real):
    monkeypatch.setenv("META_TOKEN_PAGINA", "tok-pagina")
    _http_leads(monkeypatch, paginas=[{"data": []}])
    desde = (date.today() - timedelta(days=120)).isoformat()
    assert _correr(fm, "leads", "444444", "--cliente", "acme", "--desde", desde, "--sin-archivos") == 0
    assert "más de 90 días" in capsys.readouterr().out


def test_leads_sin_permiso_explica_que_falta(fm, monkeypatch, capsys, instancia, ficha_real):
    monkeypatch.setenv("META_TOKEN_PAGINA", "tok-pagina")
    http = HttpSimulado().cuando("GET", r"/444444$", FORM)
    http.cuando("GET", r"/444444/leads$", (403, {"error": {"code": 200, "message": "Requires leads_retrieval"}}))
    _http(monkeypatch, http)
    assert _correr(fm, "leads", "444444", "--cliente", "acme") == 2
    assert "acceso a clientes potenciales" in capsys.readouterr().err


def test_leads_fechas_y_cliente_obligatorio(fm, monkeypatch, capsys, instancia, ficha_real):
    _http(monkeypatch)
    assert _correr(fm, "leads", "444444") == 1
    assert _correr(fm, "leads", "444444", "--cliente", "acme", "--desde", "2026-11-08", "--hasta", "2026-11-01") == 1
    assert _correr(fm, "leads", "444444", "--cliente", "acme", "--horario", "20-9") == 1


def test_encaje_casa_clave_o_texto(fm):
    opciones = fm.mapa_opciones(FORM)
    assert opciones["tamano"][fm._norm("De 10 a 49")] == "10_49"
    assert opciones["tamano"][fm._norm("10_49")] == "10_49"
    reglas = fm.reglas_encaje({"encaje": {"tamano": ["10_49"]}})
    assert fm.encaje_de({"tamano": "10_49"}, reglas) == 1
    assert fm.encaje_de({"tamano": "solo_yo"}, reglas) == 0
    assert fm.encaje_de({}, reglas) == 0
    assert fm.encaje_de({"tamano": "10_49"}, {}) == ""
