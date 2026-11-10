"""capi.py: normalización y hash con los vectores de Meta, validación y envío (HTTP simulado)."""
from __future__ import annotations

import importlib
import json
import time
import urllib.request
from datetime import datetime, timedelta, timezone

import pytest

from http_simulado import HttpSimulado

EMAIL_HASH = "62a14e44f765419d10fea99367361a727c12365e2520f32218d505ed9aa0f62f"  # john_smith@gmail.com (Meta)
TEL_HASH = "e323ec626319ca94ee8bff2e4c87cf613be6ea19919ed1364124e16807ab3176"    # 16505551212 (Meta)


@pytest.fixture
def capi(instancia):
    import capi as modulo
    return importlib.reload(modulo)


def _evento(**cambios) -> dict:
    ev = {"event_name": "Lead", "event_time": int(time.time()) - 60, "action_source": "website",
          "event_id": "lead_1", "event_source_url": "https://acme-automations.example/gracias",
          "user_data": {"em": [EMAIL_HASH], "client_user_agent": "Mozilla/5.0", "client_ip_address": "203.0.113.7"}}
    ev.update(cambios)
    return ev


def _payload(tmp_path, *eventos, nombre="payload.json") -> str:
    ruta = tmp_path / nombre
    ruta.write_text(json.dumps({"data": list(eventos)}), encoding="utf-8")
    return str(ruta)


# ---------------------------------------------------------------- normalizar y hashear

def test_vectores_oficiales_de_meta(capi):
    assert capi.hashear("em", "  John_Smith@Gmail.com ") == EMAIL_HASH
    assert capi.hashear("ph", "+1 (650) 555-1212") == TEL_HASH
    assert capi.hashear("ph", "650 555 1212", prefijo="1") == TEL_HASH


def test_no_hashea_dos_veces(capi):
    assert capi.hashear("em", EMAIL_HASH.upper()) == EMAIL_HASH


@pytest.mark.parametrize("clave,entrada,esperado", [
    ("ph", "0034 612-34-56-78", "34612345678"),
    ("fn", " Valéry ", "valéry"),
    ("ln", "O'Neil-Smith", "oneilsmith"),
    ("ct", "San Sebastián de los Reyes", "sansebastiándelosreyes"),
    ("zp", "94035-1234", "94035"),
    ("zp", "M1 1AE", "m11ae"),
    ("country", "ES", "es"),
    ("db", "1997-02-16", "19970216"),
    ("ge", "Mujer", "f"),
    ("external_id", " CUST_12 ", "CUST_12"),
])
def test_normalizacion(capi, clave, entrada, esperado):
    assert capi.normalizar(clave, entrada) == esperado


def test_telefono_sin_prefijo_se_rechaza(capi):
    with pytest.raises(capi.Invalido):
        capi.normalizar("ph", "612 34 56 78")
    assert capi.normalizar("ph", "612 34 56 78", prefijo="34") == "34612345678"
    assert capi.normalizar("ph", "34612345678", prefijo="34") == "34612345678"


def test_hashear_user_data_respeta_claves_sin_hash(capi):
    ud = capi.hashear_user_data({"em": "john_smith@gmail.com", "fbc": "fb.1.1700000000000.AbC",
                                 "client_ip_address": "203.0.113.7", "lead_id": 123456789012345})
    assert ud["em"] == [EMAIL_HASH]
    assert ud["fbc"] == "fb.1.1700000000000.AbC" and ud["lead_id"] == 123456789012345


def test_fbc_desde_fbclid_conserva_mayusculas(capi):
    assert capi.fbc_desde_fbclid("IwAR1xYz", 1700000000000) == "fb.1.1700000000000.IwAR1xYz"


# ---------------------------------------------------------------- validar

def test_evento_correcto_sin_errores(capi):
    errores, avisos = capi.validar({"data": [_evento()]})
    assert errores == [] and avisos == []


@pytest.mark.parametrize("cambios,fragmento", [
    ({"event_time": int(time.time() * 1000)}, "milisegundos"),
    ({"event_time": int(time.time()) - 8 * 86400}, "más de 7 días"),
    ({"event_time": int(time.time()) + 3600}, "futuro"),
    ({"action_source": "web"}, "action_source"),
    ({"event_source_url": None}, "event_source_url es obligatorio"),
    ({"user_data": {"em": ["ana@ejemplo.com"], "client_user_agent": "UA"}}, "parece en claro"),
    ({"user_data": {"client_user_agent": "UA", "fbc": "f" * 64}}, "hasheado"),
    ({"event_name": "Purchase"}, "Purchase necesita"),
    ({"custom_data": {"value": -10, "currency": "EUR"}}, "negativo"),
    ({"custom_data": {"value": 10, "currency": "EURO"}}, "ISO 4217"),
    ({"custom_data": {"nota": "ana@ejemplo.com"}}, "custom_data lleva un email"),
    ({"event_source_url": "https://x.example/gracias?email=ana%40ejemplo.com"}, "datos personales"),
])
def test_errores_que_meta_rechazaria(capi, cambios, fragmento):
    errores, _ = capi.validar({"data": [_evento(**cambios)]})
    assert any(fragmento in e for e in errores), errores


def test_evento_crm_conversion_leads(capi):
    ev = {"event_name": "LeadCualificado", "event_time": int(time.time()) - 60, "action_source": "system_generated",
          "user_data": {"lead_id": 1234567890123456, "em": [EMAIL_HASH]},
          "custom_data": {"event_source": "crm", "lead_event_source": "GHL"}}
    assert capi.validar({"data": [ev]}) == ([], [])
    ev["action_source"] = "website"
    ev["custom_data"] = {"event_source": "crm"}
    errores, _ = capi.validar({"data": [ev]})
    assert any("system_generated" in e for e in errores) and any("lead_event_source" in e for e in errores)


def test_avisos_no_bloquean(capi):
    errores, avisos = capi.validar({"data": [_evento(event_name="lead", event_id=None)]})
    assert errores == []
    assert any("«Lead»" in a for a in avisos) and any("event_id" in a for a in avisos)


def test_lote_demasiado_grande(capi):
    errores, _ = capi.validar({"data": [_evento(event_id=f"e{i}") for i in range(1001)]})
    assert any("1001 eventos" in e for e in errores)


# ---------------------------------------------------------------- CLI

def test_construir_hashea_y_no_deja_pii(capi, tmp_path, capsys):
    salida = tmp_path / "ev.json"
    capi.main(["construir", "--evento", "Lead", "--url", "https://acme-automations.example/gracias",
               "--email", "John_Smith@gmail.com", "--telefono", "+1 650 555 1212", "--ua", "Mozilla/5.0",
               "--fbclid", "IwAR1xYz", "--event-id", "lead_9", "--salida", str(salida)])
    payload = json.loads(salida.read_text(encoding="utf-8"))
    ud = payload["data"][0]["user_data"]
    assert ud["em"] == [EMAIL_HASH] and ud["ph"] == [TEL_HASH]
    assert ud["fbc"].startswith("fb.1.") and ud["fbc"].endswith(".IwAR1xYz")
    assert "smith@gmail" not in salida.read_text(encoding="utf-8").lower()


def test_construir_evento_crm(capi, capsys):
    capi.main(["construir", "--evento", "LeadCualificado", "--crm", "GHL", "--lead-id", "1234567890123456",
               "--email", "john_smith@gmail.com"])
    ev = json.loads(capsys.readouterr().out)["data"][0]
    assert ev["event_name"] == "LeadCualificado" and ev["action_source"] == "system_generated"
    assert ev["custom_data"] == {"event_source": "crm", "lead_event_source": "GHL"}
    assert ev["user_data"]["lead_id"] == 1234567890123456


def test_construir_desde_entrada_en_claro(capi, tmp_path):
    entrada = tmp_path / "claro.json"
    hace_una_hora = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(timespec="seconds")
    entrada.write_text(json.dumps({"data": [{
        "event_name": "Purchase", "event_time": hace_una_hora, "action_source": "system_generated",
        "user_data": {"em": "John_Smith@gmail.com", "ph": "+16505551212", "fbclid": "IwAR9", "external_id": "cus_1"},
        "custom_data": {"value": 99.0, "currency": "EUR"}}]}), encoding="utf-8")
    salida = tmp_path / "hash.json"
    capi.main(["construir", "--entrada", str(entrada), "--salida", str(salida)])
    ev = json.loads(salida.read_text(encoding="utf-8"))["data"][0]
    assert ev["user_data"]["em"] == [EMAIL_HASH] and ev["user_data"]["ph"] == [TEL_HASH]
    assert "fbclid" not in ev["user_data"] and ev["user_data"]["fbc"].endswith(".IwAR9")
    assert isinstance(ev["event_time"], int)


def test_validar_cli_codigos(capi, tmp_path, capsys):
    bueno = _payload(tmp_path, _evento())
    malo = _payload(tmp_path, _evento(action_source="web"), nombre="malo.json")
    with pytest.raises(SystemExit) as e:
        capi.main(["validar", bueno])
    assert e.value.code == 0
    assert "Válido." in capsys.readouterr().out
    with pytest.raises(SystemExit) as e:
        capi.main(["validar", malo, "--json"])
    assert e.value.code == 1
    assert json.loads(capsys.readouterr().out)["ok"] is False


def test_enviar_sin_codigo_ni_confirmacion_no_envia(capi, tmp_path, monkeypatch):
    http = HttpSimulado()
    monkeypatch.setattr(urllib.request, "urlopen", http)
    monkeypatch.setenv("META_CAPI_TOKEN", "token-secreto")
    ruta = _payload(tmp_path, _evento())
    for extra in ([], ["--real"]):
        with pytest.raises(SystemExit) as e:
            capi.main(["enviar", ruta, "--cliente", "acme", *extra])
        assert e.value.code == 1
    assert http.peticiones == []


def test_enviar_con_test_code(capi, instancia, tmp_path, monkeypatch, capsys):
    http = HttpSimulado().cuando("POST", r"/v\d+\.0/000000000000000/events$", None)
    monkeypatch.setattr(urllib.request, "urlopen", http)
    monkeypatch.setenv("META_CAPI_TOKEN", "token-secreto")
    with pytest.raises(SystemExit) as e:  # el dataset de la ficha de acme es el de ejemplo (ceros)
        capi.main(["enviar", _payload(tmp_path, _evento()), "--cliente", "acme", "--test-code", "TEST123"])
    assert e.value.code == 2 and http.peticiones == []

    http = HttpSimulado().cuando("POST", r"/v\d+\.0/123456789012345/events$",
                                 {"events_received": 1, "messages": [], "fbtrace_id": "Abc"})
    monkeypatch.setattr(urllib.request, "urlopen", http)
    capi.main(["enviar", _payload(tmp_path, _evento()), "--cliente", "acme", "--test-code", "TEST123",
               "--dataset", "123456789012345"])
    peticion = http.peticiones[0]
    assert peticion["form"]["test_event_code"] == "TEST123"
    assert json.loads(peticion["form"]["data"])[0]["event_name"] == "Lead"
    assert "token-secreto" not in peticion["url"] and "token-secreto" not in capsys.readouterr().out
    fila = json.loads((instancia / "logs" / "cambios.jsonl").read_text(encoding="utf-8").strip())
    assert fila["sistema"] == "capi" and fila["accion"] == "enviar_prueba" and "TEST123" in fila["detalle"]
    assert "token" not in fila["detalle"]


def test_enviar_real_con_confirmacion(capi, instancia, tmp_path, monkeypatch):
    http = HttpSimulado().cuando("POST", r"/events$", {"events_received": 1, "fbtrace_id": "X"})
    monkeypatch.setattr(urllib.request, "urlopen", http)
    monkeypatch.setenv("META_CAPI_TOKEN_ACME", "token-de-acme")
    capi.main(["enviar", _payload(tmp_path, _evento()), "--cliente", "acme", "--dataset", "123456789012345",
               "--real", "--confirmo"])
    assert "test_event_code" not in http.peticiones[0]["form"]
    assert http.peticiones[0]["form"]["access_token"] == "token-de-acme"
    assert json.loads((instancia / "logs" / "cambios.jsonl").read_text().strip())["accion"] == "enviar_real"


def test_enviar_invalido_no_llega_a_meta(capi, tmp_path, monkeypatch):
    http = HttpSimulado()
    monkeypatch.setattr(urllib.request, "urlopen", http)
    monkeypatch.setenv("META_CAPI_TOKEN", "t")
    with pytest.raises(SystemExit) as e:
        capi.main(["enviar", _payload(tmp_path, _evento(action_source="web")), "--cliente", "acme",
                   "--dataset", "123456789012345", "--test-code", "TEST1"])
    assert e.value.code == 1 and http.peticiones == []


def test_error_de_meta_se_explica(capi, tmp_path, monkeypatch, capsys):
    http = HttpSimulado().cuando("POST", r"/events$", (400, {"error": {
        "message": "Invalid parameter", "code": 100, "error_subcode": 2804003,
        "error_user_msg": "El evento tiene un event_time no válido"}}))
    monkeypatch.setattr(urllib.request, "urlopen", http)
    monkeypatch.setenv("META_CAPI_TOKEN", "t")
    with pytest.raises(SystemExit) as e:
        capi.main(["enviar", _payload(tmp_path, _evento()), "--cliente", "acme", "--dataset", "123456789012345",
                   "--test-code", "TEST1"])
    assert e.value.code == 1
    assert "event_time no válido" in capsys.readouterr().err


def test_sin_token_es_error_de_configuracion(capi, tmp_path, monkeypatch):
    monkeypatch.delenv("META_CAPI_TOKEN", raising=False)
    monkeypatch.delenv("META_CAPI_TOKEN_ACME", raising=False)
    with pytest.raises(SystemExit) as e:
        capi.main(["enviar", _payload(tmp_path, _evento()), "--cliente", "acme", "--dataset", "123456789012345",
                   "--test-code", "TEST1"])
    assert e.value.code == 2


# ---------------------------------------------------------------- hashear --archivo (listas para públicos)

LISTA = ("Nombre;Apellidos;Correo;Móvil;País;Estado;Valor\n"
         "José;Núñez;Jose.Nunez@Ejemplo.test;612 34 56 78;ES;cliente;1500\n"
         "Ana;López;ana@ejemplo.test;+52 55 1234 5678;MX;cliente;300\n"
         "Ana;López;ana@ejemplo.test;+52 55 1234 5678;MX;cliente;300\n"
         ";;no-es-un-email;12;;baja;0\n"
         ";;;;;;\n")


@pytest.fixture
def lista(instancia):
    privado = instancia / "clientes" / "acme" / "privado"
    privado.mkdir(parents=True, exist_ok=True)
    ruta = privado / "clientes.csv"
    ruta.write_text(LISTA, encoding="utf-8")
    return ruta


def _filas(ruta):
    import csv as _csv
    return list(_csv.reader(ruta.read_text(encoding="utf-8").splitlines()))


def test_archivo_solo_hashes_y_cabeceras_de_meta(capi, lista, capsys):
    capi.main(["hashear", "--archivo", str(lista), "--columnas", "correo,móvil,nombre,apellidos,país",
               "--prefijo", "34", "--json"])
    salida = capsys.readouterr().out
    assert "ejemplo.test" not in salida and "612" not in salida and "José" not in salida
    r = json.loads(salida)
    assert (r["filas"], r["escritas"], r["duplicadas"], r["sin_identificadores"]) == (4, 2, 1, 1)
    correo = next(c for c in r["columnas"] if c["tipo"] == "em")
    assert (correo["validos"], correo["invalidos"]) == (3, 1)
    filas = _filas(lista.with_name("clientes-hash.csv"))
    assert filas[0] == ["email", "phone", "fn", "ln", "country"]
    jose = filas[1]
    assert jose[0] == capi.sha256("jose.nunez@ejemplo.test")
    assert jose[1] == capi.sha256("34612345678")
    assert jose[2] == capi.sha256("jose") and jose[3] == capi.sha256("nunez")  # sin tildes ni eñes
    assert jose[4] == capi.sha256("es")
    assert filas[2][1] == capi.sha256("525512345678")  # con + manda el prefijo del propio número
    texto = lista.with_name("clientes-hash.csv").read_text(encoding="utf-8")
    assert "ejemplo" not in texto and "cliente" not in texto and "1500" not in texto


def test_archivo_detecta_columnas_y_conserva_valor(capi, lista, capsys):
    capi.main(["hashear", "--archivo", str(lista), "--prefijo", "34", "--conservar", "valor", "--json"])
    r = json.loads(capsys.readouterr().out)
    assert [c["tipo"] for c in r["columnas"]] == ["fn", "ln", "em", "ph", "country"]  # «Estado» no es la provincia
    filas = _filas(lista.with_name("clientes-hash.csv"))
    assert filas[0][-1] == "Valor" and filas[1][-1] == "1500"


def test_archivo_no_conserva_datos_personales(capi, lista):
    with pytest.raises(SystemExit) as e:
        capi.main(["hashear", "--archivo", str(lista), "--conservar", "correo"])
    assert e.value.code == 1 and not lista.with_name("clientes-hash.csv").exists()


def test_archivo_fecha_y_tipo_explicito(capi, instancia, capsys):
    ruta = instancia / "clientes" / "acme" / "privado" / "socios.csv"
    ruta.write_text("id_socio,nac,mail\nS-001,1990-04-07,a@b.test\n", encoding="utf-8")
    capi.main(["hashear", "--archivo", str(ruta), "--columnas", "id_socio=external_id,nac=db,mail=em", "--json"])
    filas = _filas(ruta.with_name("socios-hash.csv"))
    assert filas[0] == ["extern_id", "doby", "dobm", "dobd", "email"]
    assert filas[1][:4] == [capi.sha256("S-001"), capi.sha256("1990"), capi.sha256("04"), capi.sha256("07")]


def test_archivo_ya_hasheado_no_se_rehashea(capi, instancia, capsys):
    h = capi.sha256("ana@ejemplo.test")
    ruta = instancia / "clientes" / "acme" / "privado" / "hasheada.csv"
    ruta.write_text(f"email\n{h.upper()}\n", encoding="utf-8")
    capi.main(["hashear", "--archivo", str(ruta), "--json"])
    assert json.loads(capsys.readouterr().out)["columnas"][0]["ya_hasheados"] == 1
    assert _filas(ruta.with_name("hasheada-hash.csv"))[1] == [h]


def test_archivo_salida_fuera_de_privado_se_niega(capi, lista, instancia, capsys):
    fuera = instancia / "clientes" / "acme" / "datos" / "lista-hash.csv"
    with pytest.raises(SystemExit) as e:
        capi.main(["hashear", "--archivo", str(lista), "--salida", str(fuera)])
    assert e.value.code == 1 and not fuera.exists() and "privado" in capsys.readouterr().err


def test_archivo_entrada_fuera_de_privado_avisa(capi, instancia, capsys):
    fuera = instancia / "lista.csv"
    fuera.write_text("email\nana@ejemplo.test\n", encoding="utf-8")
    salida = instancia / "clientes" / "acme" / "privado" / "lista-hash.csv"
    capi.main(["hashear", "--archivo", str(fuera), "--salida", str(salida)])
    assert "fuera de clientes/<slug>/privado/" in capsys.readouterr().err and salida.exists()
    with pytest.raises(SystemExit) as e:  # sin --salida no hay sitio seguro por defecto
        capi.main(["hashear", "--archivo", str(fuera)])
    assert e.value.code == 1


def test_archivo_no_pisa_ni_se_pisa(capi, lista, capsys):
    capi.main(["hashear", "--archivo", str(lista), "--prefijo", "34"])
    destino = lista.with_name("clientes-hash.csv")
    antes = destino.read_text(encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        capi.main(["hashear", "--archivo", str(lista), "--prefijo", "34"])
    assert e.value.code == 1 and destino.read_text(encoding="utf-8") == antes
    capi.main(["hashear", "--archivo", str(lista), "--prefijo", "34", "--sobrescribir"])
    with pytest.raises(SystemExit):
        capi.main(["hashear", "--archivo", str(lista), "--salida", str(lista), "--sobrescribir"])
    assert lista.read_text(encoding="utf-8") == LISTA


def test_archivo_ruta_relativa_a_la_raiz(capi, lista, capsys):
    capi.main(["hashear", "--archivo", "clientes/acme/privado/clientes.csv", "--prefijo", "34", "--json"])
    assert json.loads(capsys.readouterr().out)["salida"] == "clientes/acme/privado/clientes-hash.csv"


def test_archivo_telefonos_sin_prefijo_avisa(capi, lista, capsys):
    capi.main(["hashear", "--archivo", str(lista), "--columnas", "móvil", "--json"])
    r = json.loads(capsys.readouterr().out)
    assert r["escritas"] == 1 and any("--prefijo" in x for x in r["avisos"])


def test_archivo_columna_desconocida(capi, lista, capsys):
    with pytest.raises(SystemExit) as e:
        capi.main(["hashear", "--archivo", str(lista), "--columnas", "dni"])
    assert e.value.code == 1 and "dni" in capsys.readouterr().err
    with pytest.raises(SystemExit):
        capi.main(["hashear", "--archivo", str(lista), "--columnas", "valor"])  # existe pero no sé qué es
    assert "valor=<tipo>" in capsys.readouterr().err


def test_hashear_sin_valor_ni_archivo(capi):
    with pytest.raises(SystemExit) as e:
        capi.main(["hashear", "--tipo", "em"])
    assert e.value.code == 1


def test_archivo_de_excel_en_cp1252(capi, instancia, capsys):
    ruta = instancia / "clientes" / "acme" / "privado" / "excel.csv"
    ruta.write_bytes("Apellidos;Correo\nNúñez;Ana@Ejemplo.test\n".encode("cp1252"))
    capi.main(["hashear", "--archivo", str(ruta), "--json"])
    assert _filas(ruta.with_name("excel-hash.csv"))[1] == [capi.sha256("nunez"), capi.sha256("ana@ejemplo.test")]


# ---------------------------------------------------------------- interfaz estable (la usan otras piezas)

def test_interfaz_estable_para_otras_herramientas(capi):
    """audiencias_meta.py importa estas funciones; las plantillas de integraciones y las skills, estas opciones."""
    for nombre in ("sha256", "es_hash", "hashear_para_lista", "SALIDA_LISTA", "ALIAS_COLUMNAS", "Invalido",
                   "_leer_tabla", "_columnas_pedidas", "_cabecera_normal", "_ruta", "_rel"):
        assert hasattr(capi, nombre), nombre
    assert capi.ETAPAS == ("lead", "diagnostico", "cualificado", "llamada", "asistio", "propuesta", "ganado",
                           "perdido")  # contrato §16
    assert capi.SALIDA_LISTA["db"] == ("doby", "dobm", "dobd") and capi.SALIDA_LISTA["external_id"] == ("extern_id",)


def test_opciones_estables_en_la_ayuda(capi, capsys):
    opciones = {"hashear": ["--tipo", "--prefijo", "--archivo", "--columnas", "--salida", "--conservar",
                            "--sobrescribir", "--json"],
                "construir": ["--entrada", "--evento", "--origen", "--canal", "--etapa", "--cualifica-en",
                              "--desde-webhook", "--cliente", "--waba", "--ctwa-clid", "--pagina", "--psid",
                              "--ig-cuenta", "--igsid", "--entrada-conversacion", "--crm", "--momento", "--event-id",
                              "--url", "--email", "--telefono", "--external-id", "--ip", "--ua", "--fbc", "--fbclid",
                              "--fbp", "--lead-id", "--valor", "--moneda", "--custom", "--salida"],
                "validar": ["--json"], "origen": ["--salida", "--json"],
                "enviar": ["--cliente", "--dataset", "--test-code", "--real", "--confirmo", "--json"]}
    for orden, esperadas in opciones.items():
        with pytest.raises(SystemExit):
            capi.main([orden, "--help"])
        ayuda = capsys.readouterr().out
        for o in esperadas:
            assert o in ayuda, (orden, o)
    with pytest.raises(SystemExit):
        capi.main(["--help"])
    assert "Interfaz estable" in capsys.readouterr().out


# ---------------------------------------------------------------- nombres canónicos del §16 (hallazgo 7, I7)

RAIZ = __import__("pathlib").Path(__file__).resolve().parents[2]


def _tabla_del_contrato() -> dict:
    """Id de etapa → evento a Meta, leído de las tablas del §16 de docs/desarrollo/contratos.md."""
    import re
    texto = (RAIZ / "docs" / "desarrollo" / "contratos.md").read_text(encoding="utf-8")
    seccion = texto.split("\n## 16.", 1)[1].split("\n## 17.", 1)[0]
    tabla = {}
    for linea in seccion.splitlines():
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(celdas) >= 3 and re.fullmatch(r"`[a-z_]+`", celdas[0]):
            evento = re.search(r"`([A-Za-z]+)`", celdas[2])
            tabla[celdas[0].strip("`")] = evento.group(1) if evento else None
    return tabla


def test_la_tabla_canonica_es_la_del_contrato(capi):
    """Una sola tabla etapa → event_name: la del §16, y capi.py la usa tal cual."""
    tabla = _tabla_del_contrato()
    assert tabla == capi.EVENTO_ETAPA, (tabla, capi.EVENTO_ETAPA)
    assert set(capi.ETAPAS) | set(capi.ETAPAS_TALLER) == set(tabla)
    assert tabla["cualificado"] == "LeadCualificado" and tabla["perdido"] == "LeadPerdido"


@pytest.mark.parametrize("etapa,esperado", [("lead", "Lead"), ("diagnostico", "DiagnosticoCompletado"),
                                            ("cualificado", "LeadCualificado"), ("llamada", "Schedule"),
                                            ("asistio", "LlamadaAsistida"), ("propuesta", "PropuestaEnviada"),
                                            ("ganado", "Purchase"), ("perdido", "LeadPerdido"),
                                            ("registro_evento", "CompleteRegistration"),
                                            ("asistio_evento", "WebinarAsistido"),
                                            ("hasta_oferta", "WebinarHastaOferta")])
def test_construir_por_etapa_del_crm(capi, capsys, etapa, esperado):
    """Hallazgo 7: `construir --etapa cualificado --crm GHL` (sin --canal) da el nombre del §16, no «cualificado»."""
    extra = ["--valor", "4800", "--moneda", "EUR"] if etapa == "ganado" else []
    capi.main(["construir", "--etapa", etapa, "--crm", "GHL", "--lead-id", "1234567890123456",
               "--email", "john_smith@gmail.com"] + extra)
    ev = json.loads(capsys.readouterr().out)["data"][0]
    assert ev["event_name"] == esperado
    assert ev["action_source"] == "system_generated"
    assert ev["custom_data"]["event_source"] == "crm" and ev["custom_data"]["lead_event_source"] == "GHL"


def test_etapa_y_evento_que_no_coinciden(capi, capsys):
    with pytest.raises(SystemExit) as e:
        capi.main(["construir", "--etapa", "cualificado", "--evento", "Cualificado", "--crm", "GHL",
                   "--email", "john_smith@gmail.com"])
    assert e.value.code == 1 and "LeadCualificado" in capsys.readouterr().err
    capi.main(["construir", "--etapa", "cualificado", "--evento", "LeadCualificado", "--crm", "GHL",
               "--email", "john_smith@gmail.com"])
    assert json.loads(capsys.readouterr().out)["data"][0]["event_name"] == "LeadCualificado"


def test_etapa_del_crm_sin_crm_avisa(capi, capsys):
    capi.main(["construir", "--etapa", "asistio", "--email", "john_smith@gmail.com", "--origen", "system_generated"])
    captura = capsys.readouterr()
    assert json.loads(captura.out)["data"][0]["event_name"] == "LlamadaAsistida"
    assert "--crm" in captura.err


@pytest.mark.parametrize("nombre,canonico", [("cualificado", "LeadCualificado"), ("Cualificado", "LeadCualificado"),
                                             ("raw_lead", "Lead"), ("qualified", "LeadCualificado"),
                                             ("booked_call", "Schedule"), ("Cita agendada", "Schedule"),
                                             ("showed", "LlamadaAsistida"), ("won", "Purchase"),
                                             ("disqualified", "LeadPerdido"), ("WebinarAttended", "WebinarAsistido"),
                                             ("StayedToPitch", "WebinarHastaOferta")])
def test_validar_avisa_de_nombres_no_canonicos(capi, nombre, canonico):
    """Hallazgo 7: el mismo hito con dos nombres reparte el volumen de la etapa objetivo en el dataset."""
    ev = {"event_name": nombre, "event_time": int(time.time()) - 60, "action_source": "system_generated",
          "user_data": {"lead_id": 1234567890123456, "em": [EMAIL_HASH]},
          "custom_data": {"event_source": "crm", "lead_event_source": "GHL"}}
    if canonico == "Purchase":
        ev["custom_data"].update(value=4800, currency="EUR")
    errores, avisos = capi.validar({"data": [ev]})
    assert errores == []
    assert any(f"«{canonico}»" in a and "§16" in a for a in avisos), avisos


def test_construir_web_no_inventa_event_id(capi, capsys):
    """Un event_id inventado no coincide con el del píxel: no deduplica y además tapaba el aviso."""
    capi.main(["construir", "--evento", "Lead", "--url", "https://acme-automations.example/gracias",
               "--email", "john_smith@gmail.com", "--ua", "Mozilla/5.0"])
    captura = capsys.readouterr()
    ev = json.loads(captura.out)["data"][0]
    assert "event_id" not in ev
    assert "event_id" in captura.err and "deduplica" in captura.err


def test_validar_en_consola_cp1252(capi, tmp_path, monkeypatch):
    """Hallazgo 28: ⚠ y ✗ no existen en cp1252 (Git Bash en Windows con la salida redirigida)."""
    import io
    import sys
    falsa = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict")
    monkeypatch.setattr(sys, "stdout", falsa)
    with pytest.raises(SystemExit) as e:
        capi.main(["validar", _payload(tmp_path, _evento(event_name="lead", event_id=None))])
    assert e.value.code == 0
    falsa.flush()
    assert "Válido." in falsa.buffer.getvalue().decode("cp1252")


ANTIGUOS = (r'"event_name":\s*"[Cc]ualificado"', r"--evento\s+[Cc]ualificado\b", r"empezando por `raw_lead`",
            r"min[uú]scula[^\n]{0,40}`raw_lead`")


def test_sin_nombres_antiguos_en_capi_paginas_e_integraciones():
    """Hallazgo 7: ningún archivo de la CAPI, las páginas o las integraciones enseña los nombres antiguos."""
    import re
    archivos = [RAIZ / "herramientas" / "capi.py", RAIZ / "docs" / "guias" / "capi.md",
                RAIZ / "docs" / "guias" / "construir-landing.md", RAIZ / "docs" / "guias" / "webinar.md",
                RAIZ / "docs" / "guias" / "mensajeria.md", RAIZ / "docs" / "guias" / "iman-de-leads.md"]
    archivos += [p for d in (".claude/skills/implementar-capi", ".claude/skills/construir-landing",
                             ".claude/skills/iman-de-leads", ".claude/skills/webinar", "plantillas/integraciones",
                             "plantillas/paginas") for p in (RAIZ / d).rglob("*") if p.is_file()
                 and p.suffix in (".md", ".json", ".js", ".py", ".html")]
    for ruta in archivos:
        texto = ruta.read_text(encoding="utf-8")
        for patron in ANTIGUOS:
            assert not re.search(patron, texto), (ruta.relative_to(RAIZ), patron)
