"""Plantilla del receptor de las páginas (plantillas/integraciones/paginas/): la regla del consentimiento (§17).

El código de los nodos Code de n8n se ejecuta con Node, tal cual está en el JSON, con los envíos de ejemplo (que salen
del `construirEnvio` real de paginas.js). Lo que llega a Meta se valida con `capi.validar`. Sin Node, se salta.
"""
from __future__ import annotations

import copy
import importlib
import json
import pathlib
import re
import shutil
import subprocess
import time

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[2]
CARPETA = RAIZ / "plantillas" / "integraciones" / "paginas"
FLUJO = CARPETA / "n8n-paginas-capi.json"
CON = CARPETA / "ejemplos" / "envio-con-consentimiento.json"
SIN = CARPETA / "ejemplos" / "envio-sin-consentimiento.json"

# Ejecuta el jsCode de un nodo como lo hace n8n: `$input.all()` devuelve los items; `require` solo da crypto.
ARNES = r"""
const fs = require('fs');
const [flujo, nodo, entrada] = process.argv.slice(2);
const n = JSON.parse(fs.readFileSync(flujo, 'utf8')).nodes.find((x) => x.name === nodo);
const items = JSON.parse(fs.readFileSync(entrada, 'utf8'));
const $input = { all: () => items };
const req = (m) => { if (m !== 'crypto') throw new Error('require no permitido: ' + m); return require('crypto'); };
try {
  const salida = new Function('$input', 'require', n.parameters.jsCode)($input, req);
  process.stdout.write(JSON.stringify({ ok: salida }));
} catch (e) {
  process.stdout.write(JSON.stringify({ error: String(e.message || e) }));
}
"""


@pytest.fixture
def capi(instancia):
    import capi as modulo
    return importlib.reload(modulo)


@pytest.fixture
def node(tmp_path):
    binario = shutil.which("node")
    if not binario:
        pytest.skip("Node no está instalado: el código de los nodos de n8n se prueba donde lo haya")
    arnes = tmp_path / "arnes.cjs"
    arnes.write_text(ARNES, encoding="utf-8")

    def correr(nombre_nodo: str, items: list) -> dict:
        entrada = tmp_path / "entrada.json"
        entrada.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
        r = subprocess.run([binario, str(arnes), str(FLUJO), nombre_nodo, str(entrada)],
                           capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, r.stderr
        return json.loads(r.stdout)

    return correr


def _flujo() -> dict:
    return json.loads(FLUJO.read_text(encoding="utf-8"))


def _envio(ruta=CON, **cambios) -> dict:
    e = json.loads(ruta.read_text(encoding="utf-8"))
    e["event_time"] = int(time.time()) - 120  # el ejemplo es de 2026-11-10: para validar tiene que ser reciente
    e.update(cambios)
    return e


CONFIG = {"DATASET_ID": "1234567890123", "TEST_EVENT_CODE": "TEST12345", "ENVIO_REAL_APROBADO": False,
          "PREFIJO_TELEFONO": "34"}


def _puerta(node, envio: dict, ip: str = "203.0.113.7", config: dict | None = None) -> list:
    r = node("Consentimiento → eventos CAPI", [{"json": {"envio": envio, "ip": ip, "config": config or CONFIG}}])
    assert "ok" in r, r
    return r["ok"]


# ---------------------------------------------------------------- estructura

def test_estructura_y_conexiones():
    f = _flujo()
    nombres = {n["name"] for n in f["nodes"]}
    assert {"Páginas · envío", "Leer envío", "Guardar en el CRM (siempre)", "Configuración (rellena esto)",
            "Consentimiento → eventos CAPI", "Montar payload", "Enviar a la Conversions API"} <= nombres
    c = f["connections"]
    for origen, destinos in c.items():
        assert origen in nombres
        for rama in destinos["main"]:
            for d in rama:
                assert d["node"] in nombres
    # El CRM recibe todo; la CAPI solo lo que pasa por la puerta.
    salidas_leer = {d["node"] for d in c["Leer envío"]["main"][0]}
    assert salidas_leer == {"Guardar en el CRM (siempre)", "Configuración (rellena esto)"}
    assert c["Configuración (rellena esto)"]["main"][0][0]["node"] == "Consentimiento → eventos CAPI"
    assert c["Consentimiento → eventos CAPI"]["main"][0][0]["node"] == "Montar payload"
    assert c["Montar payload"]["main"][0][0]["node"] == "Enviar a la Conversions API"
    assert f.get("active") is False


def test_sin_secretos_ni_rutas_y_version_de_la_api(capi):
    texto = FLUJO.read_text(encoding="utf-8")
    assert "/Users/" not in texto and "access_token=" not in texto
    assert not re.search(r"EAA[A-Za-z0-9]{20,}", texto)  # forma de un token de Meta
    assert "<<URL_CRM" in texto and "<<DATASET_ID" in texto and "<<TEST_EVENT_CODE" in texto
    f = _flujo()
    for n in f["nodes"]:
        assert "credentials" not in n and "webhookId" not in n
    envio = next(n for n in f["nodes"] if n["name"] == "Enviar a la Conversions API")
    assert f"graph.facebook.com/{capi.VERSION}/" in envio["parameters"]["url"]
    for ruta in (CON, SIN):
        ejemplo = ruta.read_text(encoding="utf-8")
        assert "/Users/" not in ejemplo and ".example" in ejemplo


# ---------------------------------------------------------------- Leer envío

def test_leer_envio_acepta_json_y_texto(node):
    e = _envio()
    cab = {"x-forwarded-for": "198.51.100.4, 10.0.0.1"}
    for cuerpo in (e, json.dumps(e)):
        r = node("Leer envío", [{"json": {"body": cuerpo, "headers": cab}}])
        assert r["ok"][0]["json"]["envio"]["event_id"] == e["event_id"]
        assert r["ok"][0]["json"]["ip"] == "198.51.100.4"
    r = node("Leer envío", [{"json": {"body": e, "headers": {"cf-connecting-ip": "203.0.113.9"}}}])
    assert r["ok"][0]["json"]["ip"] == "203.0.113.9"


@pytest.mark.parametrize("cuerpo", ["no es json", {"origen": "otra-cosa", "version": 1},
                                    {"origen": "meta-ads-os/paginas", "version": 2}])
def test_leer_envio_rechaza_lo_que_no_es_de_las_paginas(node, cuerpo):
    r = node("Leer envío", [{"json": {"body": cuerpo, "headers": {}}}])
    assert "error" in r


# ---------------------------------------------------------------- la puerta del consentimiento

def test_con_consentimiento_salen_los_eventos_con_el_mismo_nombre_e_id(node, capi):
    e = _envio()
    salida = _puerta(node, e)
    assert len(salida) == 1
    eventos = salida[0]["json"]["eventos"]
    assert [(x["event_name"], x["event_id"]) for x in eventos] == [(x["event_name"], x["event_id"])
                                                                   for x in e["eventos"]]
    ud = eventos[0]["user_data"]
    assert ud["em"] == [capi.hashear("em", e["email"])]
    assert ud["ph"] == [capi.hashear("ph", e["telefono"], prefijo="34")]
    assert ud["fn"] == [capi.hashear("fn", e["nombre"])] and ud["ln"] == [capi.hashear("ln", e["apellidos"])]
    assert ud["client_ip_address"] == "203.0.113.7" and ud["fbp"] == e["fbp"] and ud["fbc"] == e["fbc"]
    assert eventos[1]["custom_data"] == {"value": 100, "currency": "EUR"}
    errores, _ = capi.validar({"data": eventos})
    assert errores == []


@pytest.mark.parametrize("cambios", [
    {"consentimiento_marketing": "pendiente", "enviar_a_meta": False},
    {"consentimiento_marketing": "no", "enviar_a_meta": False},
    # Incoherente: enviar_a_meta true sin «si» con base consentimiento. No sale.
    {"consentimiento_marketing": "pendiente", "enviar_a_meta": True},
    {"consentimiento_marketing": "no", "enviar_a_meta": True},
    {"enviar_a_meta": "true"},  # texto, no booleano
])
def test_sin_permiso_no_sale_nada(node, cambios):
    assert _puerta(node, _envio(**cambios)) == []


def test_el_ejemplo_sin_consentimiento_no_sale(node):
    e = _envio(SIN)
    assert e["enviar_a_meta"] is False and e["consentimiento_marketing"] != "si"
    assert _puerta(node, e) == []


def test_interes_legitimo_sale_sin_fbp(node, capi):
    # Lo que construirEnvio da con interés legítimo y el banner sin contestar: con ids, fbc y sin fbp.
    e = _envio(base_legal_servidor="interes_legitimo", consentimiento_marketing="pendiente", fbp="")
    salida = _puerta(node, e)
    assert len(salida) == 1
    eventos = salida[0]["json"]["eventos"]
    assert all("fbp" not in x["user_data"] for x in eventos)
    errores, _ = capi.validar({"data": eventos})
    assert errores == []


CONSTRUIR = r"""
const P = require(process.argv[2]);
const ahora = Date.now() - 120000;
const salida = [];
for (const consentimiento of ['si', 'no', 'pendiente']) {
  for (const baseLegal of ['consentimiento', 'interes_legitimo']) {
    salida.push(P.construirEnvio({ tipoEnvio: 'lead', pagina: 'index', url: 'https://acme-automations.example/?fbclid=X1',
      ahoraMs: ahora, campos: { email: 'ana.lopez@acme-cliente.example' }, atribucion: { fbclid: 'X1' },
      fbpCookie: 'fb.1.1.2', ua: 'Mozilla/5.0', consentimiento, baseLegal,
      eventos: [{ event_name: 'Lead', event_id: 'lead_x1' }] }));
  }
}
process.stdout.write(JSON.stringify(salida));
"""


def test_la_puerta_coincide_con_la_pagina_en_todas_las_combinaciones(node, tmp_path):
    """Lo que la página marca con enviar_a_meta es exactamente lo que la plantilla deja pasar."""
    script = tmp_path / "construir.cjs"
    script.write_text(CONSTRUIR, encoding="utf-8")
    r = subprocess.run([shutil.which("node"), str(script), str(RAIZ / "plantillas" / "paginas" / "paginas.js")],
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    envios = json.loads(r.stdout)
    assert len(envios) == 6
    for e in envios:
        salida = _puerta(node, e)
        assert bool(salida) is e["enviar_a_meta"], (e["consentimiento_marketing"], e["base_legal_servidor"])
        if salida:
            ud = salida[0]["json"]["eventos"][0]["user_data"]
            assert ("fbp" in ud) is (e["consentimiento_marketing"] == "si")


def test_un_solo_campo_nombre_no_manda_fn(node):
    e = _envio()
    e.pop("apellidos")
    eventos = _puerta(node, e)[0]["json"]["eventos"]
    assert "fn" not in eventos[0]["user_data"] and "ln" not in eventos[0]["user_data"]


def test_evento_sin_event_id_es_error(node):
    e = _envio()
    e["eventos"] = copy.deepcopy(e["eventos"])
    del e["eventos"][0]["event_id"]
    r = node("Consentimiento → eventos CAPI", [{"json": {"envio": e, "ip": "", "config": CONFIG}}])
    assert "error" in r and "event_id" in r["error"]


# ---------------------------------------------------------------- Montar payload

def _montar(node, config: dict) -> dict:
    eventos = _puerta(node, _envio())[0]["json"]["eventos"]
    return node("Montar payload", [{"json": {"eventos": eventos, "config": config}}])


def test_montar_con_codigo_de_prueba(node):
    r = _montar(node, CONFIG)
    cuerpo = r["ok"][0]["json"]["cuerpo"]
    assert cuerpo["test_event_code"] == "TEST12345" and len(cuerpo["data"]) == 2
    assert r["ok"][0]["json"]["dataset"] == "1234567890123"


@pytest.mark.parametrize("codigo", ["", "<<TEST_EVENT_CODE: código de Probar eventos>>"])
def test_sin_codigo_de_prueba_no_se_envia(node, codigo):
    r = _montar(node, {**CONFIG, "TEST_EVENT_CODE": codigo})
    assert "error" in r and "TEST_EVENT_CODE" in r["error"]


def test_envio_real_solo_con_aprobacion(node):
    r = _montar(node, {**CONFIG, "TEST_EVENT_CODE": "", "ENVIO_REAL_APROBADO": True})
    assert "test_event_code" not in r["ok"][0]["json"]["cuerpo"]


def test_dataset_sin_rellenar_es_error(node):
    r = _montar(node, {**CONFIG, "DATASET_ID": "<<DATASET_ID: el dataset del píxel de las páginas>>"})
    assert "error" in r and "DATASET_ID" in r["error"]
