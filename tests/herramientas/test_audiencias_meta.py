"""audiencias_meta.py: etapas hasheadas sin texto en claro, control estable, crear y sincronizar con confirmación,
lotes de reemplazo y medición contra el control. Sin red: el HTTP se simula."""
from __future__ import annotations

import csv
import importlib
import json
import re
import urllib.request

import pytest

from http_simulado import HttpSimulado

FECHA = "2026-11-09"
AUD = "987654321"


@pytest.fixture
def am(instancia, monkeypatch):
    import capi
    import meta_ads
    importlib.reload(capi)
    importlib.reload(meta_ads)
    import audiencias_meta as modulo
    modulo = importlib.reload(modulo)
    monkeypatch.setattr(modulo.meta_ads.time, "sleep", lambda *_: None)
    monkeypatch.delenv("META_TOKEN_ACME", raising=False)
    monkeypatch.setenv("META_TOKEN", "token-global")
    return modulo


@pytest.fixture
def ficha_real(instancia):
    f = instancia / "clientes" / "acme" / "ficha.md"
    f.write_text(f.read_text(encoding="utf-8").replace("act_000000000000000", "act_12345"), encoding="utf-8")
    return f


def _http(monkeypatch, http: HttpSimulado | None = None) -> HttpSimulado:
    http = http or HttpSimulado()
    monkeypatch.setattr(urllib.request, "urlopen", http)
    return http


def _csv(ruta, cabecera, filas) -> str:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cabecera)
        w.writerows(filas)
    return str(ruta)


def _leer(ruta) -> list[dict]:
    with open(ruta, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


OPS = ["opportunity_id", "contact_id", "pipeline", "etapa", "estado", "valor", "creada", "cambio_etapa", "motivo"]
OPORTUNIDADES = [
    ["o1", "c1", "Ventas", "Nuevo lead", "open", "", "2026-11-01", "2026-11-01", ""],
    ["o2", "c2", "Ventas", "Llamada agendada", "open", "", "2026-11-02", "2026-11-05", ""],
    ["o3", "c3", "Ventas", "No show", "open", "", "2026-10-15", "2026-10-20", ""],
    ["o4", "c4", "Ventas", "Propuesta enviada", "open", "6000", "2026-09-20", "2026-10-01", ""],
    # I6: las pérdidas de c5 y c7 tienen más de 60 días (perdido-timing es de 60 a 180 días desde la pérdida)
    ["o5", "c5", "Ventas", "Propuesta enviada", "lost", "8000", "2026-09-01", "2026-09-05", "Ahora no es el momento"],
    ["o6", "c6", "Ventas", "Purchase", "won", "9000", "2026-08-01", "2026-09-01", ""],
    ["o7", "c7", "Ventas", "Propuesta enviada", "lost", "5000", "2026-08-01", "2026-09-01", "Precio"],
    ["o8", "c4", "Ventas", "Nuevo lead", "lost", "", "2026-05-01", "2026-05-02", "Duplicado"],
    ["o9", "c8", "Ventas", "Etapa rara", "open", "", "2026-11-01", "2026-11-01", ""],
    ["o10", "c9", "Ventas", "Propuesta enviada", "open", "", "2026-10-01", "2026-10-25", ""],
    ["o11", "c10", "Partners", "Propuesta enviada", "open", "", "2026-10-01", "2026-11-03", ""],
]
CONTACTOS = ["contact_id", "fecha_alta", "nombre", "email", "telefono", "origen", "de_meta", "utm_source", "campana",
             "anuncio", "ad_id", "etiquetas"]


def _contacto(n: int, etiquetas: str = "", ad: str = "111") -> list[str]:
    return [f"c{n}", "2026-09-01", f"Persona {n}", f"p{n}@acme-automations.example", f"600 000 {n:03d}", "facebook",
            "si", "fb_ad", "ES_LEADS_ADQ_HV", f"anuncio-{ad}", ad, etiquetas]


@pytest.fixture
def exportacion(instancia):
    privado = instancia / "clientes" / "acme" / "privado"
    contactos = [_contacto(n, ad="111" if n in (4, 5) else "222") for n in range(1, 11)]
    contactos[8][-1] = "cliente-potencial, no-contactar"  # c9: baja
    return (_csv(privado / "ghl-oportunidades.csv", OPS, OPORTUNIDADES),
            _csv(privado / "ghl-contactos.csv", CONTACTOS, contactos))


def _etapas(am, exportacion, *extra, json_=True, capsys=None):
    ops, cts = exportacion
    args = ["etapas", "--cliente", "acme", "--archivo", ops, "--contactos", cts, "--prefijo", "34", "--pais", "es",
            "--fecha", FECHA, *extra]
    am.main(args + (["--json"] if json_ else []))
    if capsys is not None:
        return json.loads(capsys.readouterr().out)
    return None


def _carpeta(instancia):
    return instancia / "clientes" / "acme" / "privado" / "audiencias" / FECHA


def _hash_email(am, n: int) -> str:
    return am.capi.sha256(f"p{n}@acme-automations.example")


# ---------------------------------------------------------------- contrato con capi.py

def test_capi_mantiene_lo_que_se_reutiliza(am):
    """Si B14 renombra o cambia esto, audiencias_meta.py deja de hashear igual que capi.py."""
    for nombre in ("sha256", "es_hash", "hashear_para_lista", "SALIDA_LISTA", "ALIAS_COLUMNAS", "Invalido",
                   "_leer_tabla", "_columnas_pedidas", "_cabecera_normal", "_ruta", "_rel"):
        assert hasattr(am.capi, nombre), nombre
    salida = {c for cols in am.capi.SALIDA_LISTA.values() for c in cols}
    assert salida == set(am.ESQUEMA)
    assert am.capi.hashear_para_lista("em", " P1@Acme-Automations.example ") == (_hash_email(am, 1),)


@pytest.mark.parametrize("nombre,etapa", [
    ("Nuevo lead", "lead"), ("Diagnóstico completado", "diagnostico"), ("Lead cualificado", "cualificado"),
    ("No cualificado", "perdido"), ("Llamada agendada", "llamada"), ("Reunión agendada", "llamada"),
    ("No-show", "no-show"), ("No se presentó", "no-show"), ("No asistió", "no-show"),
    ("Llamada realizada", "asistio"), ("Asistió", "asistio"), ("Propuesta enviada", "propuesta"),
    ("Purchase", "ganado"), ("Cerrado ganado", "ganado"), ("Cerrado perdido", "perdido"), ("Descartado", "perdido"),
    ("Etapa rara", None), ("Asistió al taller", None), ("Llamada asistida", "asistio"),
])
def test_clasifica_nombres_de_etapa(am, nombre, etapa):
    assert am.clasificar(nombre) == etapa


def test_mapa_manda_sobre_los_patrones(am):
    assert am.clasificar("Etapa rara", am._mapa("Etapa rara=asistio")) == "asistio"
    assert am.clasificar("Nurture", am._mapa("Nurture=ignorar")) == "ignorar"
    with pytest.raises(am.Invalido):
        am._mapa("Etapa rara=inventada")


# ---------------------------------------------------------------- etapas

def test_etapas_escribe_solo_hashes(am, instancia, exportacion, capsys):
    _etapas(am, exportacion, "--control", "0", json_=False)
    salida = capsys.readouterr().out
    assert "@" not in salida and "600 000" not in salida
    carpeta = _carpeta(instancia)
    for archivo in carpeta.glob("*.csv"):
        texto = archivo.read_text(encoding="utf-8")
        assert "@" not in texto and "600" not in texto.replace("6000", ""), archivo.name
    filas = _leer(carpeta / "propuesta.csv")
    assert list(filas[0]) == ["email", "phone", "country"]
    for fila in filas:
        assert all(re.fullmatch(r"[0-9a-f]{64}", v) for v in fila.values())
    emails = {f["email"] for f in filas}
    assert _hash_email(am, 4) in emails and _hash_email(am, 10) in emails
    assert _hash_email(am, 9) not in emails  # baja por etiqueta
    assert filas[0]["country"] == am.capi.sha256("es")
    telefono = {f["phone"] for f in filas if f["email"] == _hash_email(am, 4)}
    assert telefono == {am.capi.sha256("34600000004")}
    manifiesto = (carpeta / "manifiesto.json").read_text(encoding="utf-8")
    assert "@" not in manifiesto and "600000" not in manifiesto
    m = json.loads(manifiesto)
    assert m["excluidos"]["baja_o_dnd"] == 1
    assert m["sin_mapear"] == {"Etapa rara": 1}
    assert any(x["etapa_crm"] == "Propuesta enviada" and x["etapa"] == "propuesta" for x in m["mapa"])
    assert not (carpeta / "propuesta-completa.csv").exists()  # sin control no hace falta


def test_etapas_deduplica_y_separa_perdido_por_timing(am, exportacion, capsys):
    m = _etapas(am, exportacion, "--control", "0", "--sin-archivos", capsys=capsys)
    segs = m["segmentos"]
    assert segs["propuesta"]["total"] == 2  # c4 (aunque tenga un lead perdido) y c10; c9 está de baja
    assert segs["perdido"]["total"] == 2  # c5 y c7
    assert segs["perdido-timing"]["total"] == 1  # c5: «Ahora no es el momento»
    assert segs["ganado"]["total"] == 1 and segs["no-show"]["total"] == 1 and segs["llamada"]["total"] == 1
    assert "nombre" in " ".join(m["avisos"])  # nombre completo sin apellido: no se sube
    assert [c["tipo"] for c in m["columnas"]] == ["em", "ph", "country"]
    assert m["estancadas"]["propuesta"]["mas_de_14_dias"] == 1  # c4, desde el 2026-10-01


def test_etapas_filtra_por_pipeline_y_respeta_el_mapa(am, exportacion, capsys):
    m = _etapas(am, exportacion, "--control", "0", "--sin-archivos", "--pipeline", "ventas",
                "--mapa", "Etapa rara=asistio", capsys=capsys)
    assert m["segmentos"]["propuesta"]["total"] == 1
    assert m["segmentos"]["asistio"]["total"] == 1
    assert m["sin_mapear"] == {}


def test_control_estable_y_completa_solo_para_excluir(am, instancia, exportacion, monkeypatch, capsys):
    monkeypatch.setattr(am, "en_control", lambda semilla, clave, fraccion: clave == "id:c4")
    m = _etapas(am, exportacion, capsys=capsys)
    p = m["segmentos"]["propuesta"]
    assert (p["tratamiento"], p["control"], p["control_activo"]) == (1, 1, True)
    assert m["segmentos"]["ganado"]["control_activo"] is False  # fuera de --control-en: lista entera
    carpeta = _carpeta(instancia)
    tratamiento = {f["email"] for f in _leer(carpeta / "propuesta.csv")}
    completa = {f["email"] for f in _leer(carpeta / "propuesta-completa.csv")}
    assert _hash_email(am, 4) not in tratamiento and _hash_email(am, 4) in completa
    asignacion = _leer(carpeta / "asignacion.csv")
    c4 = [x for x in asignacion if x["clave"] == am._clave_hash("id:c4")]
    assert {(x["segmento"], x["grupo"]) for x in c4} == {("propuesta", "control")}
    assert "@" not in (carpeta / "asignacion.csv").read_text(encoding="utf-8")


def test_asignacion_determinista_y_proporcional(am):
    claves = [f"id:c{n}" for n in range(3000)]
    primera = [am.en_control("acme:etapas", k, 0.2) for k in claves]
    assert primera == [am.en_control("acme:etapas", k, 0.2) for k in claves]
    assert 0.17 < sum(primera) / len(claves) < 0.23
    assert primera != [am.en_control("otra", k, 0.2) for k in claves]


def test_agrupar_une_segmentos(am, exportacion, capsys):
    m = _etapas(am, exportacion, "--sin-archivos", "--agrupar", "reenganche=no-show,propuesta", capsys=capsys)
    assert m["segmentos"]["reenganche"]["total"] == 3
    assert m["segmentos"]["reenganche"]["control_activo"] is True


def test_por_anuncio_sin_datos_personales(am, instancia, exportacion, capsys):
    _etapas(am, exportacion, "--control", "0", "--por-anuncio", capsys=capsys)
    ruta = instancia / "clientes" / "acme" / "datos" / f"etapas-por-anuncio_{FECHA}.csv"
    texto = ruta.read_text(encoding="utf-8")
    assert "@" not in texto
    fila = next(x for x in _leer(ruta) if x["anuncio"] == "111")
    assert fila["contactos"] == "2" and fila["llegaron_a_propuesta"] == "2"  # c4 abierta y c5 perdida en propuesta
    assert fila["ahora_perdido"] == "1"


def test_etapas_no_pisa_sin_sobrescribir(am, exportacion, capsys):
    _etapas(am, exportacion, capsys=capsys)
    with pytest.raises(SystemExit) as e:
        _etapas(am, exportacion)
    assert e.value.code == 1
    _etapas(am, exportacion, "--sobrescribir", capsys=capsys)


def test_etapas_exige_privado_del_mismo_cliente(am, instancia, exportacion):
    fuera = _csv(instancia / "clientes" / "acme" / "datos" / "ops.csv", OPS, OPORTUNIDADES)
    otro = _csv(instancia / "clientes" / "nimbo" / "privado" / "ops.csv", OPS, OPORTUNIDADES)
    for ruta in (fuera, otro):
        with pytest.raises(SystemExit) as e:
            am.main(["etapas", "--cliente", "acme", "--archivo", ruta, "--fecha", FECHA])
        assert e.value.code == 1


def test_etapas_sin_email_ni_telefono(am, exportacion, capsys):
    with pytest.raises(SystemExit) as e:
        am.main(["etapas", "--cliente", "acme", "--archivo", exportacion[0], "--fecha", FECHA])
    assert e.value.code == 1
    assert "--contactos" in capsys.readouterr().err


# ---------------------------------------------------------------- crear

def _reglas_cuenta(http: HttpSimulado, aceptadas: bool = True, audiencias: list | None = None) -> HttpSimulado:
    http.cuando("GET", r"/act_12345$", {"id": "act_12345", "tos_accepted": {"custom_audience_tos": 1}} if aceptadas
                else {"id": "act_12345"})
    http.cuando("GET", r"/act_12345/customaudiences$", {"data": audiencias or []})
    return http


def _cambios(instancia) -> list[dict]:
    ruta = instancia / "logs" / "cambios.jsonl"
    return [json.loads(x) for x in ruta.read_text(encoding="utf-8").splitlines()] if ruta.exists() else []


def test_crear_sin_confirmo_no_sale_a_la_red(am, ficha_real, monkeypatch):
    http = _http(monkeypatch)
    with pytest.raises(SystemExit) as e:
        am.main(["crear", "ETAPA_PROPUESTA_GHL", "--cliente", "acme"])
    assert e.value.code == 1 and http.peticiones == []
    am.main(["crear", "ETAPA_PROPUESTA_GHL", "--cliente", "acme", "--simular"])
    assert http.peticiones == []


def test_crear_con_cuenta_de_ejemplo_o_sin_token(am, monkeypatch):
    http = _http(monkeypatch)
    with pytest.raises(SystemExit) as e:
        am.main(["crear", "ETAPA_PROPUESTA_GHL", "--cliente", "acme", "--confirmo"])
    assert e.value.code == 2
    monkeypatch.delenv("META_TOKEN")
    with pytest.raises(SystemExit) as e:
        am.main(["crear", "ETAPA_PROPUESTA_GHL", "--cliente", "acme", "--confirmo"])
    assert e.value.code == 2 and http.peticiones == []


def test_crear_exige_condiciones_aceptadas(am, ficha_real, monkeypatch, capsys):
    http = _http(monkeypatch, _reglas_cuenta(HttpSimulado(), aceptadas=False))
    with pytest.raises(SystemExit) as e:
        am.main(["crear", "ETAPA_PROPUESTA_GHL", "--cliente", "acme", "--confirmo"])
    assert e.value.code == 2
    assert "customaudiences/tos/?act=12345" in capsys.readouterr().err
    assert http.de("POST", r".") == []


def test_crear_no_duplica(am, instancia, ficha_real, monkeypatch, capsys):
    http = _http(monkeypatch, _reglas_cuenta(HttpSimulado(), audiencias=[{"id": AUD, "name": "ETAPA_PROPUESTA_GHL"}]))
    am.main(["crear", "etapa_propuesta_ghl", "--cliente", "acme", "--confirmo"])
    assert AUD in capsys.readouterr().out
    assert http.de("POST", r".") == [] and _cambios(instancia) == []


def test_crear_registra_y_da_la_fila(am, instancia, ficha_real, monkeypatch, capsys):
    http = _reglas_cuenta(HttpSimulado())
    http.cuando("POST", r"/act_12345/customaudiences$", {"id": AUD})
    _http(monkeypatch, http)
    am.main(["crear", "ETAPA_PROPUESTA_GHL", "--cliente", "acme", "--retencion", "180", "--etiqueta",
             "QUALIFIED_LEADS", "--confirmo"])
    form = http.de("POST", r"/customaudiences$")[0]["form"]
    assert form["name"] == "ETAPA_PROPUESTA_GHL" and form["subtype"] == "CUSTOM"
    assert form["customer_file_source"] == "USER_PROVIDED_ONLY" and form["retention_days"] == "180"
    assert json.loads(form["audience_labels"]) == ["QUALIFIED_LEADS"]
    cambio = _cambios(instancia)[-1]
    assert (cambio["accion"], cambio["entidad_id"], cambio["cliente"]) == ("crear_audiencia", AUD, "acme")
    salida = capsys.readouterr().out
    assert "audiencias_meta.py" in salida and AUD in salida


# ---------------------------------------------------------------- sincronizar

def _hasheado(instancia, n: int, nombre: str = "propuesta.csv") -> str:
    import capi
    filas = [[capi.sha256(f"p{i}@acme-automations.example"), capi.sha256(f"3460000{i:04d}")] for i in range(n)]
    filas.append(filas[0])  # repetida
    return _csv(instancia / "clientes" / "acme" / "privado" / "audiencias" / FECHA / nombre, ["email", "phone"], filas)


def _reglas_audiencia(http: HttpSimulado, cuenta: str = "12345", estado: int = 200, tamano: int = 1200):
    http.cuando("GET", rf"/{AUD}$", {"id": AUD, "account_id": cuenta, "name": "ETAPA_PROPUESTA_GHL",
                                    "subtype": "CUSTOM", "operation_status": {"code": estado},
                                    "approximate_count_lower_bound": tamano})
    return _reglas_cuenta(http)


def test_sincronizar_rechaza_texto_en_claro(am, instancia, ficha_real, monkeypatch, capsys):
    http = _http(monkeypatch)
    ruta = _csv(instancia / "clientes" / "acme" / "privado" / "claro.csv", ["email", "phone"],
                [["p1@acme-automations.example", "34600000001"]])
    with pytest.raises(SystemExit) as e:
        am.main(["sincronizar", AUD, "--cliente", "acme", "--archivo", ruta, "--confirmo"])
    assert e.value.code == 1 and http.peticiones == []
    error = capsys.readouterr().err
    assert "sin hashear" in error and "@" not in error and "34600000001" not in error


@pytest.mark.parametrize("problema", ["fuera", "columna", "completa"])
def test_sincronizar_rechaza_archivos_dudosos(am, instancia, ficha_real, monkeypatch, problema):
    http = _http(monkeypatch)
    if problema == "fuera":
        ruta = _csv(instancia / "clientes" / "nimbo" / "privado" / "x.csv", ["email"], [["a" * 64]])
    elif problema == "columna":
        ruta = _csv(instancia / "clientes" / "acme" / "privado" / "x.csv", ["email", "value"], [["a" * 64, "9000"]])
    else:
        ruta = _hasheado(instancia, 3, "propuesta-completa.csv")
    with pytest.raises(SystemExit) as e:
        am.main(["sincronizar", AUD, "--cliente", "acme", "--archivo", ruta, "--reemplazar", "--confirmo"])
    assert e.value.code == 1 and http.peticiones == []


def test_sincronizar_simulado_y_sin_confirmo(am, instancia, ficha_real, monkeypatch, capsys):
    http = _http(monkeypatch)
    ruta = _hasheado(instancia, 3)
    am.main(["sincronizar", AUD, "--cliente", "acme", "--archivo", ruta, "--reemplazar", "--simular", "--json"])
    r = json.loads(capsys.readouterr().out)
    assert (r["personas"], r["repetidas"], r["lotes"], r["esquema"]) == (3, 1, 1, ["EMAIL", "PHONE"])
    with pytest.raises(SystemExit) as e:
        am.main(["sincronizar", AUD, "--cliente", "acme", "--archivo", ruta, "--reemplazar"])
    assert e.value.code == 1 and http.peticiones == []


def test_sincronizar_reemplaza_en_lotes_con_una_sesion(am, instancia, ficha_real, monkeypatch, capsys):
    monkeypatch.setattr(am, "LOTE", 2)
    http = _reglas_audiencia(HttpSimulado())
    http.cuando("POST", rf"/{AUD}/usersreplace$", lambda p: {"audience_id": AUD, "num_received": 2,
                                                            "num_invalid_entries": 0})
    _http(monkeypatch, http)
    am.main(["sincronizar", AUD, "--cliente", "acme", "--archivo", _hasheado(instancia, 5), "--reemplazar",
             "--confirmo"])
    envios = http.de("POST", r"/usersreplace$")
    assert len(envios) == 3 and http.de("POST", r"/users$") == []
    sesiones = [json.loads(p["form"]["session"]) for p in envios]
    assert [s["batch_seq"] for s in sesiones] == [1, 2, 3]
    assert [s["last_batch_flag"] for s in sesiones] == [False, False, True]
    assert len({s["session_id"] for s in sesiones}) == 1 and sesiones[0]["session_id"] > 0
    assert all(s["estimated_num_total"] == 5 for s in sesiones)
    payload = json.loads(envios[0]["form"]["payload"])
    assert payload["schema"] == ["EMAIL", "PHONE"] and len(payload["data"]) == 2
    assert all(re.fullmatch(r"[0-9a-f]{64}", v) for fila in payload["data"] for v in fila)
    cambio = _cambios(instancia)[-1]
    assert cambio["accion"] == "reemplazar_audiencia" and cambio["entidad_id"] == AUD
    assert "personas=5" in cambio["detalle"]
    assert "change-log.md" in capsys.readouterr().out


def test_sincronizar_sin_reemplazar_anade_y_avisa(am, instancia, ficha_real, monkeypatch, capsys):
    http = _reglas_audiencia(HttpSimulado())
    http.cuando("POST", rf"/{AUD}/users$", {"num_received": 3, "num_invalid_entries": 0})
    _http(monkeypatch, http)
    am.main(["sincronizar", AUD, "--cliente", "acme", "--archivo", _hasheado(instancia, 3), "--confirmo"])
    assert len(http.de("POST", r"/users$")) == 1
    assert "reinicia el aprendizaje" in capsys.readouterr().err
    assert _cambios(instancia)[-1]["accion"] == "anadir_audiencia"


@pytest.mark.parametrize("cuenta,estado", [("99999", 200), ("12345", 414), ("12345", 471)])
def test_sincronizar_comprueba_la_audiencia(am, instancia, ficha_real, monkeypatch, cuenta, estado):
    http = _http(monkeypatch, _reglas_audiencia(HttpSimulado(), cuenta=cuenta, estado=estado))
    with pytest.raises(SystemExit) as e:
        am.main(["sincronizar", AUD, "--cliente", "acme", "--archivo", _hasheado(instancia, 3), "--reemplazar",
                 "--confirmo"])
    assert e.value.code == 1 and http.de("POST", r".") == []


def test_sincronizar_corte_a_mitad_queda_registrado(am, instancia, ficha_real, monkeypatch, capsys):
    monkeypatch.setattr(am, "LOTE", 2)
    http = _reglas_audiencia(HttpSimulado())
    http.cuando("POST", rf"/{AUD}/usersreplace$", [
        {"num_received": 2, "num_invalid_entries": 0},
        (400, {"error": {"code": 2650, "error_subcode": 1870158, "message": "Session expired"}})])
    _http(monkeypatch, http)
    with pytest.raises(SystemExit) as e:
        am.main(["sincronizar", AUD, "--cliente", "acme", "--archivo", _hasheado(instancia, 5), "--reemplazar",
                 "--confirmo"])
    assert e.value.code == 1
    error = capsys.readouterr().err
    assert "lote 2 de 3" in error and "caducó" in error
    assert _cambios(instancia)[-1]["accion"] == "reemplazar_audiencia_parcial"


# ---------------------------------------------------------------- listar

def test_listar_marca_las_pequenas(am, ficha_real, monkeypatch, capsys):
    _http(monkeypatch, _reglas_cuenta(HttpSimulado(), audiencias=[
        {"id": AUD, "name": "ETAPA_PROPUESTA_GHL", "subtype": "CUSTOM", "approximate_count_lower_bound": 1000,
         "approximate_count_upper_bound": 1200, "delivery_status": {"code": 300}, "operation_status": {"code": 200},
         "time_updated": 1762646400},
        {"id": "123456789", "name": "Visitas web", "subtype": "WEBSITE", "delivery_status": {"code": 200},
         "operation_status": {"code": 200}}]))
    am.main(["listar", "--cliente", "acme", "--buscar", "etapa", "--json"])
    r = json.loads(capsys.readouterr().out)
    assert r["condiciones_aceptadas"] is True
    assert [x["id"] for x in r["audiencias"]] == [AUD]
    assert r["audiencias"][0]["entrega"] == "demasiado pequeña"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["audiencias"][0]["actualizada"])


# ---------------------------------------------------------------- medir

def test_fisher_y_potencia(am):
    assert am.fisher(3, 1, 1, 3) == pytest.approx(0.4857, abs=1e-4)  # la cata de té de Fisher
    assert am.fisher(0, 0, 0, 0) == 1.0
    assert am.fisher(10, 0, 0, 10) < 0.001
    n = am.control_necesario(0.30, 0.20, 4)
    assert 150 < n < 400
    assert am.control_necesario(0.2, 0.2, 4) is None


def test_veredictos(am):
    assert am.veredicto(5, 20, 1, 5)["veredicto"] == "faltan datos"
    assert am.veredicto(30, 80, 3, 40)["veredicto"] == "suma"
    assert am.veredicto(3, 80, 15, 40)["veredicto"] == "resta"
    assert am.veredicto(20, 80, 10, 40)["veredicto"] == "no distinguible"


def _propuestas(instancia, n: int, ganados: set[int] = frozenset(), nombre: str = "ops.csv", etiquetas=None):
    filas = [[f"o{i}", f"c{i}", "Ventas", "Purchase" if i in ganados else "Propuesta enviada",
              "won" if i in ganados else "open", "", "2026-10-01", "2026-10-01", ""] for i in range(n)]
    cab = OPS
    if etiquetas:
        cab = OPS + ["etiquetas"]
        filas = [f + [etiquetas(i)] for i, f in enumerate(filas)]
    ops = _csv(instancia / "clientes" / "acme" / "privado" / nombre, cab, filas)
    cts = _csv(instancia / "clientes" / "acme" / "privado" / f"ct-{nombre}", CONTACTOS,
               [_contacto(i) for i in range(n)])
    return ops, cts


def test_medir_contra_el_control(am, instancia, monkeypatch, capsys):
    monkeypatch.setattr(am, "en_control", lambda semilla, clave, fraccion: int(clave[4:]) < 40)
    ops, cts = _propuestas(instancia, 120)
    am.main(["etapas", "--cliente", "acme", "--archivo", ops, "--contactos", cts, "--prefijo", "34", "--fecha", FECHA,
             "--json"])
    capsys.readouterr()
    ganados = set(range(40, 70)) | {0, 1, 2}  # 30 de 80 en tratamiento, 3 de 40 en control
    nuevo, _ = _propuestas(instancia, 120, ganados, "ops-dic.csv")
    manifiesto = str(_carpeta(instancia) / "manifiesto.json")
    am.main(["medir", "--cliente", "acme", "--manifiesto", manifiesto, "--archivo", nuevo, "--fecha", "2026-12-21",
             "--json"])
    r = json.loads(capsys.readouterr().out)
    res = next(x for x in r["resultados"] if x["segmento"] == "propuesta")
    assert res["exito"] == "ganado"
    assert (res["tratamiento"]["n"], res["tratamiento"]["exitos"]) == (80, 30)
    assert (res["control"]["n"], res["control"]["exitos"]) == (40, 3)
    assert res["veredicto"] == "suma"
    assert not any("días desde la primera subida" in x for x in r["avisos"])
    am.main(["medir", "--cliente", "acme", "--manifiesto", manifiesto, "--archivo", nuevo, "--fecha", "2026-11-15"])
    assert "días desde la primera subida" in capsys.readouterr().out


def test_medir_por_etiquetas_de_ghl(am, instancia, capsys):
    def etiquetas(i):
        return "etapas-propuesta" + (", holdout-etapas" if i % 3 == 0 else "")
    ops, _ = _propuestas(instancia, 60, set(range(1, 60, 3)), etiquetas=etiquetas)
    am.main(["medir", "--cliente", "acme", "--archivo", ops, "--etiqueta-grupo", "etapas-propuesta",
             "--etiqueta-control", "holdout-etapas", "--exito", "ganado", "--json"])
    res = json.loads(capsys.readouterr().out)["resultados"][0]
    assert (res["control"]["n"], res["control"]["exitos"]) == (20, 0)
    assert (res["tratamiento"]["n"], res["tratamiento"]["exitos"]) == (40, 20)
    assert res["veredicto"] == "faltan datos"  # menos de 30 en control


@pytest.mark.parametrize("extra", [["--fecha", "09/11/2026"], ["--control", "0.6"], ["--motivo-timing", "("],
                                   ["--control-en", "inventado"], ["--agrupar", "propuesta=no-show"]])
def test_opciones_invalidas_salen_con_1(am, exportacion, extra):
    ops, cts = exportacion
    with pytest.raises(SystemExit) as e:
        am.main(["etapas", "--cliente", "acme", "--archivo", ops, "--contactos", cts, "--sin-archivos", *extra])
    assert e.value.code == 1


def test_bajas_solo_para_excluir(am, instancia, exportacion, ficha_real, monkeypatch, capsys):
    m = _etapas(am, exportacion, "--bajas", capsys=capsys)
    assert m["bajas"]["personas"] == 1 and m["bajas"]["archivo"] == "bajas.csv"
    bajas = _leer(_carpeta(instancia) / "bajas.csv")
    assert [f["email"] for f in bajas] == [_hash_email(am, 9)]
    http = _http(monkeypatch)
    with pytest.raises(SystemExit) as e:
        am.main(["sincronizar", AUD, "--cliente", "acme", "--archivo", str(_carpeta(instancia) / "bajas.csv"),
                 "--reemplazar", "--confirmo"])
    assert e.value.code == 1 and http.peticiones == []
    am.main(["sincronizar", AUD, "--cliente", "acme", "--archivo", str(_carpeta(instancia) / "bajas.csv"),
             "--exclusion", "--simular"])


def test_timing_por_etiqueta_si_no_hay_motivo(am, instancia, capsys):
    privado = instancia / "clientes" / "acme" / "privado"
    ops = _csv(privado / "sin-motivo.csv", OPS[:-1], [f[:-1] for f in OPORTUNIDADES])
    contactos = [_contacto(n) for n in range(1, 11)]
    contactos[6][-1] = "mal-momento"  # c7, perdido
    cts = _csv(privado / "ct-sin-motivo.csv", CONTACTOS, contactos)
    am.main(["etapas", "--cliente", "acme", "--archivo", ops, "--contactos", cts, "--prefijo", "34", "--fecha", FECHA,
             "--sin-archivos", "--json"])
    m = json.loads(capsys.readouterr().out)
    assert m["segmentos"]["perdido-timing"]["total"] == 1
    assert not any("motivo de pérdida" in x for x in m["avisos"])


def test_segmentos_propios_de_un_pipeline_de_taller(am, instancia, capsys):
    privado = instancia / "clientes" / "acme" / "privado"
    filas = [["t1", "c1", "Taller", "Registrado", "open", "", "", "", ""],
             ["t2", "c2", "Taller", "Asistió al taller", "open", "", "", "", ""],
             ["t3", "c3", "Taller", "Vio la oferta", "open", "", "", "", ""],
             ["t4", "c4", "Taller", "Registrado", "open", "", "", "", ""],
             ["o4", "c4", "Ventas", "Llamada agendada", "open", "", "", "", ""]]
    ops = _csv(privado / "taller.csv", OPS, filas)
    cts = _csv(privado / "ct-taller.csv", CONTACTOS, [_contacto(n) for n in range(1, 5)])
    mapa = ("Registrado=propio:registrado-sin-asistir,Asistió al taller=propio:asistio-sin-llamada,"
            "Vio la oferta=propio:hasta-oferta-sin-reserva")
    am.main(["etapas", "--cliente", "acme", "--archivo", ops, "--contactos", cts, "--prefijo", "34", "--fecha", FECHA,
             "--mapa", mapa, "--control-en", "registrado-sin-asistir", "--sin-archivos", "--json"])
    m = json.loads(capsys.readouterr().out)
    segs = m["segmentos"]
    assert segs["registrado-sin-asistir"]["total"] == 1  # c4 agendó llamada en el pipeline de ventas
    assert segs["registrado-sin-asistir"]["control_activo"] is True
    assert segs["asistio-sin-llamada"]["total"] == 1 and segs["hasta-oferta-sin-reserva"]["total"] == 1
    assert segs["llamada"]["total"] == 1
    with pytest.raises(SystemExit):
        am.main(["etapas", "--cliente", "acme", "--archivo", ops, "--mapa", "Registrado=propio:propuesta"])


# ---------------------------------------------------------------- I6 (revisión independiente)

def test_i6_sin_columna_dnd_avisa(am, exportacion, capsys):
    """Hallazgo 15: sin columna DND no se puede excluir a quien tiene «No molestar»: se avisa en vez de decir «0»."""
    m = _etapas(am, exportacion, "--control", "0", "--sin-archivos", capsys=capsys)
    assert m["columna_dnd"] is False
    assert any("DND" in x and "ghl.py contactos" in x for x in m["avisos"])


def test_i6_dnd_de_ghl_contactos_excluye(am, instancia, capsys):
    """Hallazgo 15: la columna `dnd` que exporta ahora `ghl.py contactos` deja fuera al contacto y va a bajas.csv."""
    privado = instancia / "clientes" / "acme" / "privado"
    ops = _csv(privado / "ops-dnd.csv", OPS, [["o1", "c1", "Ventas", "Propuesta enviada", "open", "", "2026-10-01",
                                              "2026-10-01", ""],
                                             ["o2", "c2", "Ventas", "Propuesta enviada", "open", "", "2026-10-01",
                                              "2026-10-01", ""]])
    cts = _csv(privado / "ct-dnd.csv", CONTACTOS + ["dnd", "dnd_canales"],
               [_contacto(1) + ["sí", "todos"], _contacto(2) + ["no", ""]])
    am.main(["etapas", "--cliente", "acme", "--archivo", ops, "--contactos", cts, "--prefijo", "34", "--fecha", FECHA,
             "--control", "0", "--bajas", "--json"])
    m = json.loads(capsys.readouterr().out)
    assert m["columna_dnd"] is True and m["excluidos"]["baja_o_dnd"] == 1
    assert m["segmentos"]["propuesta"]["total"] == 1 and m["bajas"]["personas"] == 1
    assert not any("DND" in x for x in m["avisos"])


def _perdidos(instancia, filas, nombre="ops-perdidos.csv", cab=OPS):
    privado = instancia / "clientes" / "acme" / "privado"
    ops = _csv(privado / nombre, cab, filas)
    cts = _csv(privado / f"ct-{nombre}", CONTACTOS, [_contacto(n) for n in range(1, 6)])
    return ops, cts


def test_i6_perdido_timing_solo_de_60_a_180_dias(am, instancia, capsys):
    """Hallazgo 20: un «Ahora no» del 2026-10-20 con `--fecha 2026-11-09` (20 días) no entra en perdido-timing."""
    ops, cts = _perdidos(instancia, [
        ["o1", "c1", "Ventas", "Propuesta enviada", "lost", "", "2026-09-01", "2026-10-20", "Ahora no"],
        ["o2", "c2", "Ventas", "Propuesta enviada", "lost", "", "2026-06-01", "2026-07-01", "Ahora no"],
        ["o3", "c3", "Ventas", "Propuesta enviada", "lost", "", "2026-02-01", "2026-03-01", "Ahora no"],
        ["o4", "c4", "Ventas", "Propuesta enviada", "lost", "", "2026-06-01", "", "Ahora no"],
        ["o5", "c5", "Ventas", "Propuesta enviada", "open", "", "2026-10-01", "2026-10-01", ""]])
    base = ["etapas", "--cliente", "acme", "--archivo", ops, "--contactos", cts, "--prefijo", "34", "--fecha", FECHA,
            "--control", "0", "--sin-archivos", "--json"]
    am.main(base)
    m = json.loads(capsys.readouterr().out)
    assert m["segmentos"]["perdido-timing"]["total"] == 1  # solo c2 (131 días)
    assert m["segmentos"]["perdido"]["total"] == 4  # los cuatro siguen en perdido (exclusión)
    pt = m["perdido_timing"]
    assert (pt["dias"], pt["antes_de_tiempo"], pt["pasados"], pt["sin_fecha"]) == ([60, 180], 1, 1, 1)
    assert any("perdido-timing" in x and "sin fecha" in x for x in m["avisos"])
    am.main(base + ["--dias-perdida", "0-200"])
    assert json.loads(capsys.readouterr().out)["segmentos"]["perdido-timing"]["total"] == 2


def test_i6_perdida_con_fecha_de_estado(am, instancia, capsys):
    """Si la exportación trae el cambio de estado (`ghl.py oportunidades`: cambio_estado), manda sobre el de etapa:
    marcar perdido no mueve la etapa, así que el cambio de etapa puede ser de mucho antes de la pérdida."""
    cab = OPS + ["cambio_estado"]
    ops, cts = _perdidos(instancia, [
        ["o1", "c1", "Ventas", "Propuesta enviada", "lost", "", "2026-06-01", "2026-07-01", "Ahora no", "2026-10-20"]],
        nombre="ops-estado.csv", cab=cab)
    am.main(["etapas", "--cliente", "acme", "--archivo", ops, "--contactos", cts, "--prefijo", "34", "--fecha", FECHA,
             "--control", "0", "--sin-archivos", "--json"])
    m = json.loads(capsys.readouterr().out)
    assert "perdido-timing" not in m["segmentos"] and m["perdido_timing"]["antes_de_tiempo"] == 1


@pytest.mark.parametrize("valor", ["180-60", "sesenta", "60"])
def test_i6_dias_perdida_invalido(am, exportacion, valor):
    with pytest.raises(SystemExit) as e:
        _etapas(am, exportacion, "--dias-perdida", valor, "--sin-archivos")
    assert e.value.code == 1


def test_i6_corte_al_anadir_no_aconseja_reemplazar(am, instancia, ficha_real, monkeypatch, capsys):
    """Hallazgo 16: cortado a mitad en modo añadir, repetir con --reemplazar vaciaría la audiencia de exclusión."""
    monkeypatch.setattr(am, "LOTE", 2)
    http = _reglas_audiencia(HttpSimulado())
    http.cuando("POST", rf"/{AUD}/users$", [
        {"num_received": 2, "num_invalid_entries": 0},
        (400, {"error": {"code": 2650, "error_subcode": 1870158, "message": "Session expired"}})])
    _http(monkeypatch, http)
    with pytest.raises(SystemExit) as e:
        am.main(["sincronizar", AUD, "--cliente", "acme", "--archivo", _hasheado(instancia, 5), "--confirmo"])
    assert e.value.code == 1
    error = capsys.readouterr().err
    assert "Repite la orden entera con --reemplazar" not in error
    assert "sin --reemplazar" in error and "deduplica" in error


def test_i6_corte_al_reemplazar_sigue_aconsejando_reemplazar(am, instancia, ficha_real, monkeypatch, capsys):
    monkeypatch.setattr(am, "LOTE", 2)
    http = _reglas_audiencia(HttpSimulado())
    http.cuando("POST", rf"/{AUD}/usersreplace$", [
        {"num_received": 2, "num_invalid_entries": 0}, (400, {"error": {"code": 2650, "message": "Error"}})])
    _http(monkeypatch, http)
    with pytest.raises(SystemExit):
        am.main(["sincronizar", AUD, "--cliente", "acme", "--archivo", _hasheado(instancia, 5), "--reemplazar",
                 "--confirmo"])
    assert "con --reemplazar" in capsys.readouterr().err


def test_i6_medir_por_etiquetas_sin_columna_es_invalido(am, instancia, capsys):
    """Hallazgo 29: las oportunidades de `ghl.py` no traen etiquetas; sin --contactos la medida no vale."""
    ops, _ = _propuestas(instancia, 60, set(range(1, 60, 3)))
    with pytest.raises(SystemExit) as e:
        am.main(["medir", "--cliente", "acme", "--archivo", ops, "--etiqueta-grupo", "etapas-propuesta",
                 "--etiqueta-control", "holdout-etapas", "--exito", "ganado", "--json"])
    assert e.value.code == 1
    assert "--contactos" in capsys.readouterr().err


def test_i6_medir_por_etiquetas_sin_nadie_en_el_grupo_es_invalido(am, instancia, capsys):
    ops, _ = _propuestas(instancia, 60, set(range(1, 60, 3)), etiquetas=lambda i: "otra-etiqueta")
    with pytest.raises(SystemExit) as e:
        am.main(["medir", "--cliente", "acme", "--archivo", ops, "--etiqueta-grupo", "etapas-propuesta",
                 "--etiqueta-control", "holdout-etapas", "--exito", "ganado", "--json"])
    assert e.value.code == 1
    assert "etapas-propuesta" in capsys.readouterr().err


def test_i6_medir_por_etiquetas_con_contactos(am, instancia, capsys):
    """Con --contactos (las etiquetas están en los contactos), la medida sale: el flujo de /seguimiento-leads."""
    ops, cts = _propuestas(instancia, 60, set(range(1, 60, 3)))
    privado = instancia / "clientes" / "acme" / "privado"
    contactos = [_contacto(i, etiquetas="etapas-propuesta" + (";holdout-etapas" if i % 3 == 0 else ""))
                 for i in range(60)]
    cts = _csv(privado / "ct-etiquetas.csv", CONTACTOS, contactos)
    am.main(["medir", "--cliente", "acme", "--archivo", ops, "--contactos", cts, "--etiqueta-grupo",
             "etapas-propuesta", "--etiqueta-control", "holdout-etapas", "--exito", "ganado", "--json"])
    res = json.loads(capsys.readouterr().out)["resultados"][0]
    assert (res["control"]["n"], res["tratamiento"]["n"]) == (20, 40)
