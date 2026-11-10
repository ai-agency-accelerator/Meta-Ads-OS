"""Tests de herramientas/paginas.py (páginas de captación). Sin red: no se abre ningún navegador ni webhook.

El JavaScript se prueba con `node --test tests/herramientas/paginas_js.test.cjs` si hay Node; si no, ese test se salta.
"""
from __future__ import annotations

import copy
import importlib
import io
import json
import os
import pathlib
import re
import shutil
import struct
import subprocess
import sys
import zlib

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[2]
PAGINAS = RAIZ / "plantillas" / "paginas"
EJEMPLO = PAGINAS / "ejemplos" / "acme-embudo.json"
WEBINAR = PAGINAS / "ejemplos" / "nimbo-webinar.json"
VECTORES = json.loads((pathlib.Path(__file__).parent / "paginas_vectores.json").read_text(encoding="utf-8"))


@pytest.fixture
def pg(instancia):
    import render
    importlib.reload(render)
    import paginas as modulo
    return importlib.reload(modulo)


def _config(tmp_path: pathlib.Path, cambios=None, base=EJEMPLO) -> pathlib.Path:
    """Copia del ejemplo con la marca en ruta absoluta (para poder guardarla fuera de plantillas/)."""
    cfg = json.loads(base.read_text(encoding="utf-8"))
    if "marca" in cfg:
        cfg["marca"]["ruta"] = str((base.parent / cfg["marca"]["ruta"]).resolve())
    if cambios:
        cambios(cfg)
    ruta = tmp_path / f"config-{len(list(tmp_path.glob('config-*.json')))}.json"
    ruta.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    return ruta


def _generar(pg, tmp_path, cambios=None, tipos=None, base=EJEMPLO, **kw):
    salida = tmp_path / f"salida-{len(list(tmp_path.glob('salida-*')))}"
    gen = pg.Generador(str(_config(tmp_path, cambios, base)), str(salida), **kw)
    res = gen.generar(tipos or [t for t in pg.TIPOS if t in gen.paginas])
    return salida, res


def _config_js(html: str) -> dict:
    m = re.search(r'<script type="application/json" id="pos-config">(.*?)</script>', html, re.S)
    assert m, "falta #pos-config"
    return json.loads(m.group(1))


# ───────────────────────────── fórmulas ─────────────────────────────
@pytest.mark.parametrize("caso", VECTORES["casos"], ids=lambda c: c["formula"])
def test_vectores_de_formulas(pg, caso):
    r = pg.calcular_expresion(caso["formula"], VECTORES["variables"])
    if isinstance(caso["esperado"], (int, float)):
        assert r == pytest.approx(caso["esperado"])
    else:
        assert r == caso["esperado"]


@pytest.mark.parametrize("caso", VECTORES["errores"], ids=lambda c: c["formula"])
def test_errores_de_formulas(pg, caso):
    with pytest.raises(pg.ErrorExpresion, match=re.escape(caso["contiene"])):
        pg.calcular_expresion(caso["formula"], VECTORES["variables"])


def test_comprobar_formula_sin_evaluar(pg):
    grupos = {"procesos": {"personas", "horas", "nombre"}}
    pg.comprobar_formula("suma(procesos, personas * horas) * coste", {"coste"}, grupos)
    pg.comprobar_formula("mayor(procesos, horas, nombre)", set(), grupos)
    for formula, mensaje in (("coste * x", "Variable desconocida «x»"),
                             ("procesos * 2", "es un grupo"),
                             ("suma(coste, 1)", "pregunta de tipo grupo"),
                             ("mayor(procesos, horas, coste)", "campo del grupo"),
                             ("limitar(coste, 1)", "limitar() lleva 3"),
                             ("redondear()", "redondear() lleva entre 1 y 2"),
                             ("suma(procesos, sueldo)", "Variable desconocida «sueldo»")):
        with pytest.raises(pg.ErrorExpresion, match=re.escape(mensaje)):
            pg.comprobar_formula(formula, {"coste"}, grupos)


def test_escenarios_del_ejemplo_dan_el_nivel_honesto(pg):
    res = pg.probar(str(EJEMPLO))
    assert res["ok"] is True
    niveles = {e["nombre"]: e["nivel"] for e in res["escenarios"]}
    assert niveles == {"Pequeña, una tarea ligera": "bajo", "Mediana, dos tareas": "medio",
                       "Equipo de operaciones": "alto"}
    medio = next(e for e in res["escenarios"] if e["nivel"] == "medio")
    # el ejemplo sigue la calculadora del playbook de consultoras (§4.3): payback ≤ 12 caso claro, 12–18 dudoso
    # tipos de tarea del 25 % al 60 % automatizable, la regla de /iman-de-leads (antes 15–70 %)
    assert medio["valores"]["coste_recuperable"] == 8100 and medio["valores"]["ahorro_neto"] == 6900
    assert 12 < medio["valores"]["retorno_meses"] <= 18
    assert medio["valores"]["tarea_top"] == "Pedidos"
    bajo = next(e for e in res["escenarios"] if e["nivel"] == "bajo")
    assert bajo["valores"]["retorno_meses"] is None  # sin ahorro neto no hay retorno: se enseña «—»
    assert medio["valor_evento"] == 100  # valor esperado del lead, no el ahorro (contrato §16)


def test_probar_con_respuestas_propias_y_cli(pg, tmp_path, capsys):
    r = tmp_path / "respuestas.json"
    r.write_text(json.dumps({"respuestas": {"tamano": 0, "procesos": [{"nombre": "A", "personas": 1, "horas": 1,
                                                                       "tipo": 3}], "herramientas": 2},
                             "espera_nivel": "alto"}), encoding="utf-8")
    assert pg.main(["probar", "--config", str(EJEMPLO), "--respuestas", str(r), "--json"]) == 1  # sale «bajo»
    salida = json.loads(capsys.readouterr().out)
    assert salida["escenarios"][0]["nivel"] == "bajo" and salida["ok"] is False


# ───────────────────────────── generar ─────────────────────────────
def test_generar_embudo_completo(pg, tmp_path):
    salida, res = _generar(pg, tmp_path)
    for archivo in ("index.html", "diagnostico.html", "reserva.html", "gracias.html", "recursos/paginas.js",
                    "recursos/diagnostico.js", "recursos/logo.svg"):
        assert (salida / archivo).is_file(), archivo
    assert (salida / "recursos" / "paginas.js").read_bytes() == (PAGINAS / "paginas.js").read_bytes()
    landing = (salida / "index.html").read_text(encoding="utf-8")
    assert '<meta name="generator" content="meta-ads-os/paginas">' in landing
    assert '<html lang="es">' in landing
    cfg = _config_js(landing)
    assert cfg["webhook"]["url"] == "https://hooks.example/acme/lead"
    assert cfg["pixel_id"] == "000000000000000" and cfg["base_legal_servidor"] == "consentimiento"
    # el píxel solo lo carga paginas.js tras aceptar: nada de fbevents.js ni fbq('init') en el HTML
    assert "fbevents.js" not in landing and "fbq(" not in landing
    assert "data-pos-consentimiento" in landing and "data-pos-aceptar" in landing and "data-pos-rechazar" in landing
    # arranque del diagnóstico en el hero: la primera pregunta enlaza con la respuesta preseleccionada
    assert 'href="diagnostico.html?r_tamano=0"' in landing
    assert 'class="pos-barra"' in landing and "data-pos-hero" in landing
    assert '<script src="recursos/paginas.js" defer></script>' in landing

    diag = (salida / "diagnostico.html").read_text(encoding="utf-8")
    cfg_diag = _config_js(diag)["pagina"]["diagnostico"]
    assert [p["id"] for p in cfg_diag["preguntas"]] == ["tamano", "procesos", "herramientas", "plazo"]
    assert cfg_diag["valor_evento"] == {"bajo": 0, "medio": 100, "alto": 230}
    assert diag.count("data-pos-paso ") == 4
    assert "<template data-pos-grupo-plantilla>" in diag and "q-procesos-__i__-nombre" in diag
    assert 'data-pos-formulario="diagnostico"' in diag and 'data-evento="Lead"' in diag
    assert 'class="pos-trampa"' in diag
    assert 'data-pos-supuesto="coste_hora"' in diag and 'value="80"' in diag  # el 0.8 se edita como 80 %
    # lo que decide el nivel no lo edita el prospecto: bajando la inversión nadie «compra» el nivel alto
    for fijo in ("inversion", "mantenimiento", "umbral"):
        assert f'data-pos-supuesto="{fijo}"' not in diag and f'<p id="s-{fijo}">' in diag, fijo
    assert '<script src="recursos/diagnostico.js" defer></script>' in diag
    assert 'autocomplete="email"' in diag and 'type="tel"' in diag

    reserva = (salida / "reserva.html").read_text(encoding="utf-8")
    cal = _config_js(reserva)["pagina"]["calendario"]
    assert cal["url"].startswith("https://") and cal["parametros"]["email"] == "email"
    assert 'data-pos-nivel-mensaje="alto"' in reserva and "noindex" in reserva
    gracias = (salida / "gracias.html").read_text(encoding="utf-8")
    assert '<meta name="robots" content="noindex, nofollow">' in gracias
    assert res["ok"] and any("EJEMPLO" in a for a in res["avisos"])


def test_validar_el_ejemplo_solo_falla_por_los_casos_de_ejemplo(pg, tmp_path):
    salida, _ = _generar(pg, tmp_path)
    res = pg.validar(str(salida))
    errores = [(p["archivo"], x["id"]) for p in res["paginas"] for x in p["problemas"] if x["nivel"] == "error"]
    assert errores == [("index.html", "contenido.ejemplo")]
    for p in res["paginas"]:
        assert p["peso_kb"] < 200, p  # rápido en el navegador interno de Instagram


def _sin_casos_de_ejemplo(cfg):
    cfg["paginas"]["landing"]["secciones"] = [s for s in cfg["paginas"]["landing"]["secciones"] if s["tipo"] != "casos"]


def test_validar_pasa_con_casos_reales(pg, tmp_path):
    salida, _ = _generar(pg, tmp_path, _sin_casos_de_ejemplo)
    res = pg.validar(str(salida))
    assert res["ok"] is True and res["errores"] == 0
    assert pg.main(["validar", str(salida)]) == 0


def test_rutas_publicas_sin_html(pg, tmp_path):
    """Con ruta_publica «/diagnostico» (hostings que quitan el .html), validar no da los enlaces por rotos."""
    def rutas(cfg):
        _sin_casos_de_ejemplo(cfg)
        for tipo, ruta in (("landing", "/"), ("diagnostico", "/diagnostico"), ("reserva", "/reserva"),
                           ("gracias", "/gracias")):
            cfg["paginas"][tipo]["ruta_publica"] = ruta
    salida, _ = _generar(pg, tmp_path, rutas)
    assert 'href="/diagnostico?r_tamano=0"' in (salida / "index.html").read_text(encoding="utf-8")
    res = pg.validar(str(salida))
    assert res["errores"] == 0 and res["avisos"] == 0
    # una ruta relativa que no existe sí es un error; una desde la raíz, solo aviso (puede ser de otra parte del sitio)
    (salida / "otra.html").write_text((salida / "gracias.html").read_text(encoding="utf-8").replace(
        'href="/"', 'href="no-existe.html"').replace('href="https://acme.example/privacidad"', 'href="/blog/"'),
        encoding="utf-8")
    problemas = {(x["id"], x["nivel"], x["detalle"].split(",")[0]) for p in pg.validar(str(salida))["paginas"]
                 if p["archivo"] == "otra.html" for x in p["problemas"]}
    assert ("enlaces.rotos", "error", "Enlace a no-existe.html") in problemas
    assert ("enlaces.rotos", "aviso", "Enlace a /blog/") in problemas


def test_validar_detecta_fallos(pg, tmp_path):
    carpeta = tmp_path / "rota"
    carpeta.mkdir()
    (carpeta / "grande.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\0" * (1100 * 1024))
    (carpeta / "index.html").write_text("""<!doctype html><html><head>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<meta name="generator" content="meta-ads-os/paginas"><meta name="pos-tipo" content="landing">
<script src="https://connect.facebook.net/en_US/fbevents.js"></script>
<script>fbq('init', '000000000000000');</script>
<script type="application/json" id="pos-config">{"pixel_id": "000000000000000", "webhook": {"url": "http://x.example"}</script>
</head><body>
<img src="grande.png"><img src="falta.webp" alt="x" width="1" height="1">
<form id="f" data-pos-formulario="lead"><input name="email" type="text"><button type="submit"></button></form>
<a href="otra.html">Otra</a><a href="#nada">Ancla</a><a href="#"></a>
<p id="dup"></p><p id="dup"></p>
</body></html>""", encoding="utf-8")
    res = pg.validar(str(carpeta))
    ids = {x["id"] for x in res["paginas"][0]["problemas"] if x["nivel"] == "error"}
    for esperado in ("doc.idioma", "doc.titulo", "doc.zoom", "doc.h1", "img.alt", "img.dimensiones", "img.peso",
                     "img.falta", "pixel.sin_consentimiento", "tracking.config", "tracking.runtime", "a11y.etiquetas",
                     "a11y.botones", "a11y.enlaces", "a11y.ids", "enlaces.rotos", "form.evento"):
        assert esperado in ids, esperado
    avisos = {x["id"] for x in res["paginas"][0]["problemas"] if x["nivel"] == "aviso"}
    assert {"form.email", "enlaces.ancla", "form.trampa", "js.bloqueante"} <= avisos
    assert pg.main(["validar", str(carpeta), "--json"]) == 1


def test_sin_pixel_ni_nada_que_pedir_no_hay_banner(pg, tmp_path):
    """Sin píxel, el banner solo sobra si el servidor tampoco necesita el permiso (interés legítimo o sin webhook)."""
    def interes_legitimo(cfg):
        cfg["tracking"]["pixel_id"] = ""
        cfg["tracking"]["base_legal_servidor"] = "interes_legitimo"

    def sin_webhook(cfg):
        cfg["tracking"]["pixel_id"] = ""
        cfg["tracking"]["webhook"] = {}
    for cambio in (interes_legitimo, sin_webhook):
        salida, res = _generar(pg, tmp_path, cambio, ["gracias"])
        html = (salida / "gracias.html").read_text(encoding="utf-8")
        assert "data-pos-consentimiento" not in html and "data-pos-preferencias" not in html
        assert _config_js(html)["consentimiento"]["banner"] is False
        assert any("pixel_id" in a for a in res["avisos"])


def test_solo_servidor_tambien_pide_consentimiento(pg, tmp_path):
    """Hallazgo 6: con eventos_navegador: false o sin pixel_id, y base_legal_servidor por defecto (consentimiento),
    la página pide el permiso que autoriza el envío por servidor. Antes no había banner y todo salía con
    enviar_a_meta: false para siempre."""
    def sin_navegador(cfg):
        _sin_casos_de_ejemplo(cfg)
        cfg["tracking"]["eventos_navegador"] = False

    def sin_pixel(cfg):
        _sin_casos_de_ejemplo(cfg)
        cfg["tracking"]["pixel_id"] = ""
    for cambio in (sin_navegador, sin_pixel):
        salida, _ = _generar(pg, tmp_path, cambio)
        html = (salida / "gracias.html").read_text(encoding="utf-8")
        assert "data-pos-consentimiento" in html and "data-pos-preferencias" in html
        assert _config_js(html)["consentimiento"]["banner"] is True
        banner = html.split("data-pos-consentimiento", 1)[1].split("</section>", 1)[0]
        assert "servidor" in banner and "píxel" not in banner  # dice lo que de verdad pasa: no hay píxel
        assert pg.validar(str(salida))["errores"] == 0
        # una página así sin banner (lo que generaba antes: sin el elemento y con banner false en el config) es un
        # error de validar, no un «gestor propio»
        cfg = _config_js(html)
        cfg["consentimiento"] = {"banner": False, "caducidad_dias": 180}
        antigua = re.sub(r'(<script type="application/json" id="pos-config">)(.*?)(</script>)',
                         lambda m: m.group(1) + json.dumps(cfg) + m.group(3), html, flags=re.S)
        for roto in (html.replace("data-pos-consentimiento", "data-sin-banner"),
                     antigua.replace("data-pos-consentimiento", "data-sin-banner")):
            (salida / "gracias.html").write_text(roto, encoding="utf-8")
            problemas = {(x["id"], x["nivel"]) for p in pg.validar(str(salida))["paginas"]
                         if p["archivo"] == "gracias.html" for x in p["problemas"]}
            assert ("consentimiento.banner", "error") in problemas
    # con píxel y servidor, el texto por defecto dice las dos cosas
    salida, _ = _generar(pg, tmp_path, _sin_casos_de_ejemplo, ["gracias"])
    banner = (salida / "gracias.html").read_text(encoding="utf-8").split("data-pos-consentimiento", 1)[1]
    assert "píxel" in banner.split("</section>", 1)[0] and "servidor" in banner.split("</section>", 1)[0]


def test_modo_prueba_sin_webhook(pg, tmp_path):
    def sin_webhook(cfg):
        cfg["tracking"]["webhook"] = {}
    salida, res = _generar(pg, tmp_path, sin_webhook, ["gracias"])
    assert _config_js((salida / "gracias.html").read_text(encoding="utf-8"))["webhook"]["url"] == ""
    assert any("modo prueba" in a for a in res["avisos"])
    avisos = {x["id"] for p in pg.validar(str(salida))["paginas"] for x in p["problemas"]}
    assert "tracking.webhook" in avisos


def test_marca_del_cliente(pg, instancia, tmp_path):
    shutil.copytree(RAIZ / "plantillas" / "html" / "marca-ejemplo", instancia / "clientes" / "acme" / "marca")

    def sin_marca(cfg):
        cfg.pop("marca")
    salida, res = _generar(pg, tmp_path, sin_marca, ["gracias"], cliente="acme")
    html = (salida / "gracias.html").read_text(encoding="utf-8")
    marca = re.search(r'<style id="pos-marca">(.*?)</style>', html, re.S).group(1)
    assert "--c-primario:#1F4FD1" in marca and "--c-fondo:#F7F8FB" in marca
    assert (salida / "recursos" / "logo.svg").is_file()
    assert 'alt="Acme Automations"' in html
    assert res["marca"].endswith("marca.json")


def test_contraste_de_marca_se_corrige(pg):
    marca = pg.render.cargar_marca(None, RAIZ / "plantillas" / "html" / "marca-ejemplo")
    marca["colores"]["texto_sobre_primario"] = "#2A55DA"  # casi el mismo azul que el primario
    avisos: list[str] = []
    t = pg.tokens_marca(marca, avisos)
    assert pg.render.contraste(t["--c-sobre-primario"], t["--c-primario"]) >= 4.5
    assert pg.render.contraste(t["--c-texto-suave"], t["--c-superficie"]) >= 4.5
    assert pg.render.contraste(t["--c-borde-control"], t["--c-fondo"]) >= 3.0
    assert any("botones" in a for a in avisos)


def test_escapa_html_y_json(pg, tmp_path):
    def malicioso(cfg):
        cfg["paginas"]["landing"]["hero"]["titular"] = '<script>alert("x")</script>'
        cfg["paginas"]["diagnostico"]["niveles"][2]["texto"] = "Fin </script><script>alert(1)</script>"
    salida, _ = _generar(pg, tmp_path, malicioso, ["landing", "diagnostico"])
    landing = (salida / "index.html").read_text(encoding="utf-8")
    assert '<script>alert("x")' not in landing and "&lt;script&gt;alert(&quot;x&quot;)" in landing
    diag = (salida / "diagnostico.html").read_text(encoding="utf-8")
    assert "<script>alert(1)" not in diag and "\\u003c/script\\u003e" in diag
    assert _config_js(diag)["pagina"]["diagnostico"]["niveles"][2]["texto"].startswith("Fin </script>")


def test_enlaces_peligrosos_y_config_invalida(pg, tmp_path, capsys):
    def js(cfg):
        cfg["paginas"]["landing"]["hero"]["cta"]["href"] = "javascript:alert(1)"
    with pytest.raises(pg.ErrorUsuario, match="no permitido"):
        _generar(pg, tmp_path, js, ["landing"])

    def formula_mala(cfg):
        cfg["paginas"]["diagnostico"]["calculos"][1]["formula"] = "suma(procesos, personas * sueldo)"
    ruta = _config(tmp_path, formula_mala)
    assert pg.main(["generar", "diagnostico", "--config", str(ruta), "--salida", str(tmp_path / "x"), "--json"]) == 1
    error = json.loads(capsys.readouterr().out)
    assert error["ok"] is False and error["codigo"] == 1 and "sueldo" in error["error"]

    def id_reservado(cfg):
        cfg["paginas"]["diagnostico"]["preguntas"][1]["campos"][0]["id"] = "y"
    with pytest.raises(pg.ErrorUsuario, match="reservada"):
        _generar(pg, tmp_path, id_reservado, ["diagnostico"])

    def sin_contacto(cfg):
        cfg["paginas"]["diagnostico"]["formulario"]["campos"] = ["nombre", "empresa"]
    with pytest.raises(pg.ErrorUsuario, match="email o teléfono"):
        _generar(pg, tmp_path, sin_contacto, ["diagnostico"])


def test_avisa_si_no_hay_recomendacion_honesta_ni_escenario_correcto(pg, tmp_path):
    def sin_bajo(cfg):
        d = cfg["paginas"]["diagnostico"]
        d["niveles"] = [n for n in d["niveles"] if n["id"] != "bajo"]
        d["valor_evento"].pop("bajo")
    _, res = _generar(pg, tmp_path, sin_bajo, ["diagnostico"])
    assert any("tono «bajo»" in a for a in res["avisos"])
    assert any("esperabas «bajo»" in a for a in res["avisos"])


def test_fragmento_ghl_y_en_linea(pg, tmp_path):
    salida, res = _generar(pg, tmp_path, _sin_casos_de_ejemplo, en_linea=True, fragmento_ghl=True)
    assert sorted(p.name for p in (salida / "ghl").iterdir()) == ["diagnostico.html", "gracias.html", "index.html",
                                                                  "reserva.html"]
    assert not (salida / "recursos" / "paginas.js").exists()
    completo = (salida / "reserva.html").read_text(encoding="utf-8")
    assert "<script>" in completo and "PaginasOS" in completo and 'src="recursos/paginas.js"' not in completo
    frag = (salida / "ghl" / "reserva.html").read_text(encoding="utf-8")
    assert not re.search(r"<(html|body|head)[\s>]", frag)  # <header> sí puede estar
    assert 'id="pos-config"' in frag and "PaginasOS" in frag
    regla_body = re.compile(r"\bbody\{margin:\s*0")  # el fragmento no toca html ni body de la página de GHL
    assert not regla_body.search(frag) and regla_body.search(completo)
    assert any("recursos_url" in a for a in res["avisos"])
    errores = [x for p in pg.validar(str(salida))["paginas"] for x in p["problemas"] if x["nivel"] == "error"]
    assert errores == []


def test_no_borra_archivos_ajenos(pg, tmp_path):
    salida = tmp_path / "web"
    (salida / "recursos").mkdir(parents=True)
    (salida / "privacidad.html").write_text("<p>mía</p>", encoding="utf-8")
    (salida / "recursos" / "foto.webp").write_bytes(b"x")
    pg.Generador(str(_config(tmp_path)), str(salida)).generar(["gracias"])
    assert (salida / "privacidad.html").read_text(encoding="utf-8") == "<p>mía</p>"
    assert (salida / "recursos" / "foto.webp").exists()


def test_webinar_con_calendario(pg, tmp_path):
    salida, res = _generar(pg, tmp_path, base=WEBINAR)
    web = (salida / "index.html").read_text(encoding="utf-8")
    assert 'data-pos-cuenta="2026-12-03T18:00:00+01:00"' in web and "Jueves, 18:00 h" in web
    assert 'id="registro"' in web and 'data-tipo-envio="registro_webinar"' in web
    gracias = (salida / "gracias.html").read_text(encoding="utf-8")
    assert "calendar.google.com/calendar/render" in gracias and "20261203T170000Z%2F20261203T174500Z" in gracias
    ics = next((salida / "recursos").glob("*.ics")).read_bytes().decode("utf-8")  # sin traducir \r\n
    assert "DTSTART:20261203T170000Z" in ics and "DTEND:20261203T174500Z" in ics
    assert ics.count("\r\n") == ics.count("\n")  # RFC 5545: líneas terminadas en CRLF
    assert pg.validar(str(salida))["ok"] is True
    # lo que pide /webinar (B20): horas por país, registro como CompleteRegistration, preguntas de compromiso y de
    # cualificación, casillas separadas por canal, WhatsApp en gracias y la edición en content_name
    assert "Canarias: 17:00 h" in web and "México (CDMX): 11:00 h" in web
    assert 'data-evento="CompleteRegistration"' in web and '<select class="pos-select" id="registro-facturas_mes"' in web
    assert 'name="acepta_whatsapp"' in web and 'name="acepta_novedades"' in web and "acepta_comunicaciones" not in web
    assert 'name="acepta_whatsapp" data-pos-campo="casilla" data-etiqueta="Whatsapp">' in web  # nunca obligatoria
    assert _config_js(web)["content_name"] == "webinar-conciliacion-2026-12-03"
    assert 'href="https://wa.me/34600000000?text=' in gracias and 'target="_blank" rel="noopener"' in gracias


def test_webinar_y_gracias_en_carpetas_separadas(pg, tmp_path):
    """El flujo de /webinar: un config por página y una carpeta por página (registro/ y gracias/)."""
    def solo_registro(cfg):
        cfg["paginas"].pop("gracias")
        cfg["paginas"]["webinar"]["formulario"]["siguiente"] = "../gracias/"

    def solo_gracias(cfg):
        evento = cfg["paginas"].pop("webinar")["evento"]
        cfg["paginas"]["gracias"]["archivo"] = "index.html"
        cfg["paginas"]["gracias"]["anadir_calendario"] = evento
    registro, res = _generar(pg, tmp_path, solo_registro, base=WEBINAR)
    assert 'data-siguiente="../gracias/"' in (registro / "index.html").read_text(encoding="utf-8")
    assert not any("@gracias" in a for a in res["avisos"])
    gracias, _ = _generar(pg, tmp_path, solo_gracias, base=WEBINAR)
    html = (gracias / "index.html").read_text(encoding="utf-8")
    assert "DTSTART:20261203T170000Z" in next((gracias / "recursos").glob("*.ics")).read_text(encoding="utf-8")
    assert "Canarias: 17:00 h" in html
    for carpeta in (registro, gracias):
        assert pg.validar(str(carpeta))["errores"] == 0

    def sin_evento(cfg):
        cfg["paginas"].pop("webinar")
    with pytest.raises(pg.ErrorUsuario, match="si generas gracias aparte"):
        _generar(pg, tmp_path, sin_evento, ["gracias"], base=WEBINAR)

    def sin_siguiente(cfg):
        cfg["paginas"].pop("gracias")
    _, res = _generar(pg, tmp_path, sin_siguiente, base=WEBINAR)
    assert any("Enlace a @gracias" in a and "../gracias/" in a for a in res["avisos"])


def test_casillas_y_zonas_invalidas(pg, tmp_path):
    def casilla_mala(cfg):
        cfg["paginas"]["webinar"]["formulario"]["marketing"] = [{"id": "whatsapp", "texto": "Sí"}]
    with pytest.raises(pg.ErrorUsuario, match="acepta_<canal>"):
        _generar(pg, tmp_path, casilla_mala, ["webinar"], base=WEBINAR)

    def campo_reservado(cfg):
        cfg["paginas"]["webinar"]["formulario"]["campos"].append({"id": "acepta_todo", "tipo": "casilla"})
    with pytest.raises(pg.ErrorUsuario, match="acepta_"):
        _generar(pg, tmp_path, campo_reservado, ["webinar"], base=WEBINAR)

    def zona_mala(cfg):
        cfg["paginas"]["webinar"]["evento"]["otras_zonas"] = [{"nombre": "Luna", "zona": "Luna/Mar_de_la_Tranquilidad"}]
    with pytest.raises(pg.ErrorUsuario, match="nombre IANA"):
        _generar(pg, tmp_path, zona_mala, ["webinar"], base=WEBINAR)

    def sin_casillas_ni_evento(cfg):
        cfg["paginas"]["webinar"]["formulario"]["marketing"] = False
        cfg["paginas"]["webinar"]["formulario"].pop("evento")
        cfg["paginas"]["webinar"]["secciones"].append({"tipo": "formulario", "titulo": "Reserva tu plaza"})
    # con gracias: validar comprueba también adónde lleva el formulario (data-siguiente)
    salida, _ = _generar(pg, tmp_path, sin_casillas_ni_evento, ["webinar", "gracias"], base=WEBINAR)
    web = (salida / "index.html").read_text(encoding="utf-8")
    hero = web.split('id="registro"', 1)[1].split("</form>", 1)[0]
    assert 'name="acepta_' not in hero
    # en un webinar, el registro es CompleteRegistration por defecto (también en un formulario de sección)
    assert web.count('data-evento="CompleteRegistration"') == 2 and 'data-evento="Lead"' not in web
    # la sección no repite el id del formulario del hero
    assert web.count('id="registro"') == 1 and '<section class="pos-seccion" id="registro-2"' in web
    errores = [x for p in pg.validar(str(salida))["paginas"] for x in p["problemas"] if x["nivel"] == "error"]
    assert errores == []


def test_imagenes_dimensiones_y_alt(pg, tmp_path):
    def png(ancho, alto):
        ihdr = struct.pack(">IIBBBBB", ancho, alto, 8, 2, 0, 0, 0)
        trozo = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))  # noqa: E731
        return b"\x89PNG\r\n\x1a\n" + trozo(b"IHDR", ihdr) + trozo(b"IEND", b"")
    (tmp_path / "hero.png").write_bytes(png(1200, 800))
    (tmp_path / "logo.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 64"></svg>',
                                       encoding="utf-8")
    assert pg.dimensiones_imagen(tmp_path / "hero.png") == (1200, 800)
    assert pg.dimensiones_imagen(tmp_path / "logo.svg") == (320, 64)

    def con_imagen(cfg):
        cfg["paginas"]["landing"]["hero"]["media"] = {"tipo": "imagen", "src": str(tmp_path / "hero.png"),
                                                      "alt": "Panel de pedidos automatizado"}
    salida, _ = _generar(pg, tmp_path, con_imagen, ["landing", "diagnostico"])
    html = (salida / "index.html").read_text(encoding="utf-8")
    assert 'src="recursos/img/hero.png" alt="Panel de pedidos automatizado" width="1200" height="800"' in html
    assert (salida / "recursos" / "img" / "hero.png").is_file()

    def sin_alt(cfg):
        cfg["paginas"]["landing"]["hero"]["media"] = {"tipo": "imagen", "src": str(tmp_path / "hero.png")}
    with pytest.raises(pg.ErrorUsuario, match="alt"):
        _generar(pg, tmp_path, sin_alt, ["landing"])


# ───────────────────────────── JavaScript (Node) ─────────────────────────────
def test_javascript_con_node(pg, tmp_path):
    node = shutil.which("node")
    if not node:
        pytest.skip("Node no está instalado: el JS de las páginas se prueba con `node --test` donde lo haya")
    version = subprocess.run([node, "--version"], capture_output=True, text=True).stdout.strip()
    if int(version.lstrip("v").split(".")[0]) < 18:
        pytest.skip(f"Node {version}: hace falta 18 o superior para node --test")
    gen = pg.Generador(str(EJEMPLO), None)
    _, diag = gen.diagnostico(gen.paginas["diagnostico"])
    escenarios = []
    for esc in gen.paginas["diagnostico"]["escenarios"] + [{"nombre": "supuestos editados", "supuestos": {"coste_hora": 40},
                                                            "respuestas": pg.respuestas_por_defecto(diag)}]:
        r = pg.calcular(diag, esc["respuestas"], esc.get("supuestos"))
        escenarios.append(dict(copy.deepcopy(esc), python={"nivel": r["nivel"], "valores": r["valores"]}))
    paridad = tmp_path / "paridad.json"
    paridad.write_text(json.dumps({"diagnostico": diag, "escenarios": escenarios}, ensure_ascii=False), encoding="utf-8")
    entorno = dict(os.environ, PAGINAS_PARIDAD=str(paridad))
    r = subprocess.run([node, "--test", str(pathlib.Path(__file__).parent / "paginas_js.test.cjs")],
                       capture_output=True, text=True, env=entorno, cwd=str(RAIZ), timeout=120)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-2000:]
    assert "# fail 0" in r.stdout or "ℹ fail 0" in r.stdout
    assert "# skipped 0" in r.stdout or "ℹ skipped 0" in r.stdout


# ───────────────────────────── hallazgos de la revisión del 2026-11-10 (I7) ─────────────────────────────
@pytest.mark.parametrize("caso", VECTORES["numeros_humanos"], ids=lambda c: repr(c["texto"]))
def test_numeros_humanos_vectores(pg, caso):
    """Hallazgo 11: la misma lectura de «1.200», «1.500,50» o «0.175» que numEntrada() de paginas.js y diagnostico.js."""
    r = pg.num_humano(caso["texto"])
    if caso["esperado"] is None:
        assert r is None
    else:
        assert r == pytest.approx(caso["esperado"])


def test_numeros_humanos_con_la_regla_comun(pg):
    """Las páginas no divergen de _comun.numero() (la regla de las demás herramientas) en lo que es un número."""
    import _comun
    if not hasattr(_comun, "numero"):
        pytest.skip("_comun.numero() aún no existe en esta copia")
    for c in VECTORES["numeros_humanos"]:
        if isinstance(c["texto"], str) and c["esperado"] is not None:
            assert _comun.numero(c["texto"]) == pytest.approx(c["esperado"]), c["texto"]


def test_config_con_numeros_escritos_a_la_espanola(pg, tmp_path):
    """Hallazgo 11: "valor_evento": {"alto": "1.200"} acababa como value 1,2 hacia Meta y "inversion": "9.000"
    como 9 €."""
    def humanos(cfg):
        d = cfg["paginas"]["diagnostico"]
        d["valor_evento"]["alto"] = "1.200"
        next(s for s in d["supuestos"] if s["id"] == "inversion")["valor"] = "9.000"
        horas = d["preguntas"][1]["campos"][2]
        horas["max"] = "1.000"
    salida, _ = _generar(pg, tmp_path, humanos, ["diagnostico"])
    html = (salida / "diagnostico.html").read_text(encoding="utf-8")
    diag = _config_js(html)["pagina"]["diagnostico"]
    assert diag["valor_evento"]["alto"] == 1200
    assert next(s for s in diag["supuestos"] if s["id"] == "inversion")["valor"] == 9000
    assert diag["preguntas"][1]["campos"][2]["max"] == 1000

    def ilegible(cfg):
        cfg["paginas"]["diagnostico"]["valor_evento"]["alto"] = "1.200 €"
    with pytest.raises(pg.ErrorUsuario, match="valor_evento"):
        _generar(pg, tmp_path, ilegible, ["diagnostico"])


def test_moneda_de_la_ficha(pg, instancia, tmp_path):
    """Hallazgo 12: ficha con moneda MXN y config sin sitio.moneda: value y cifras en MXN, no en EUR."""
    ficha = instancia / "clientes" / "acme" / "ficha.md"
    ficha.write_text(ficha.read_text(encoding="utf-8").replace("moneda: EUR", "moneda: MXN"), encoding="utf-8")

    def sin_moneda(cfg):
        cfg["sitio"].pop("moneda", None)
        for s in cfg["paginas"]["diagnostico"]["supuestos"]:
            s.pop("unidad", None)
    salida, res = _generar(pg, tmp_path, sin_moneda, ["diagnostico"], cliente="acme")
    html = (salida / "diagnostico.html").read_text(encoding="utf-8")
    assert _config_js(html)["moneda"] == "MXN"
    assert "(€)" not in html and "Inversión típica de un primer proyecto (MXN)" in html

    def en_euros(cfg):
        cfg["sitio"]["moneda"] = "EUR"
    _, res = _generar(pg, tmp_path, en_euros, ["diagnostico"], cliente="acme")
    assert any("MXN" in a and "EUR" in a for a in res["avisos"])  # sitio.moneda manda, pero avisa
    assert not any("€/año" in a for a in res["avisos"])  # en EUR la unidad «€/año» es coherente

    def con_unidades_en_euros(cfg):
        cfg["sitio"].pop("moneda", None)
    _, res = _generar(pg, tmp_path, con_unidades_en_euros, ["diagnostico"], cliente="acme")
    assert any("€/año" in a and "MXN" in a for a in res["avisos"])  # una unidad en € con otra moneda


@pytest.mark.parametrize("cid", ["origen", "momento", "ref", "ad_id", "utm_source", "event_id", "enviar_a_meta",
                                 "respuestas", "fbc"])
def test_ids_reservados_del_envio_v1(pg, tmp_path, cid):
    """Hallazgo 23: un campo con id «origen», «momento» o «ref» pisaba los metadatos del envío v1."""
    def campo(cfg):
        cfg["paginas"]["diagnostico"]["formulario"]["campos"].append({"id": cid, "etiqueta": "¿Cómo nos conociste?"})
    with pytest.raises(pg.ErrorUsuario, match="reservado"):
        _generar(pg, tmp_path, campo, ["diagnostico"])


def test_validar_detecta_campos_reservados(pg, tmp_path):
    salida, _ = _generar(pg, tmp_path, _sin_casos_de_ejemplo)
    html = (salida / "diagnostico.html").read_text(encoding="utf-8")
    (salida / "diagnostico.html").write_text(html.replace('name="empresa"', 'name="origen"', 1), encoding="utf-8")
    errores = {x["id"] for p in pg.validar(str(salida))["paginas"] for x in p["problemas"] if x["nivel"] == "error"}
    assert "form.reservado" in errores


def _configs_webinar_separados(tmp_path, archivo_gracias=None):
    """Los dos configs del paso 6 de /webinar: registro (solo webinar) y gracias (solo gracias, con el evento)."""
    def registro(cfg):
        cfg["paginas"].pop("gracias")
        cfg["paginas"]["webinar"].pop("archivo", None)
        cfg["paginas"]["webinar"]["formulario"]["siguiente"] = "../gracias/"

    def gracias(cfg):
        evento = cfg["paginas"].pop("webinar")["evento"]
        cfg["paginas"]["gracias"]["anadir_calendario"] = evento
        if archivo_gracias:
            cfg["paginas"]["gracias"]["archivo"] = archivo_gracias
    return _config(tmp_path, registro, WEBINAR), _config(tmp_path, gracias, WEBINAR)


def test_webinar_en_dos_carpetas_sin_404(pg, tmp_path):
    """Hallazgo 24: con las órdenes del paso 6 de /webinar, gracias/ solo tenía gracias.html y «../gracias/» daba 404."""
    reg, gra = _configs_webinar_separados(tmp_path)
    edicion = tmp_path / "paginas" / "edicion"
    assert pg.main(["generar", "webinar", "--config", str(reg), "--salida", str(edicion / "registro")]) == 0
    assert pg.main(["generar", "gracias", "--config", str(gra), "--salida", str(edicion / "gracias")]) == 0
    assert (edicion / "registro" / "index.html").is_file() and (edicion / "gracias" / "index.html").is_file()
    res = pg.validar(str(edicion))
    assert res["errores"] == 0, [x for p in res["paginas"] for x in p["problemas"] if x["nivel"] == "error"]
    assert pg.validar(str(edicion / "registro"))["errores"] == 0


def test_validar_detecta_el_404_del_webinar_separado(pg, tmp_path):
    """Hallazgo 24: el caso roto del informe (gracias/ sin index.html) ya no da «0 errores»."""
    reg, gra = _configs_webinar_separados(tmp_path, archivo_gracias="gracias.html")
    rota = tmp_path / "rota"
    pg.main(["generar", "webinar", "--config", str(reg), "--salida", str(rota / "registro")])
    pg.main(["generar", "gracias", "--config", str(gra), "--salida", str(rota / "gracias")])
    for carpeta in (rota, rota / "registro"):
        problemas = [x for p in pg.validar(str(carpeta))["paginas"] for x in p["problemas"]]
        assert any(x["id"] == "enlaces.rotos" and x["nivel"] == "error" and "../gracias/" in x["detalle"]
                   for x in problemas), problemas


def test_validar_resuelve_siguiente_y_ctas_del_config(pg, tmp_path):
    """Hallazgo 24: validar mira también data-siguiente, el siguiente de la reserva y los CTA de los niveles."""
    def rotos(cfg):
        _sin_casos_de_ejemplo(cfg)
        cfg["paginas"]["diagnostico"]["formulario"]["siguiente"] = "no-existe.html"
        cfg["paginas"]["reserva"]["siguiente"] = "tampoco.html"
        cfg["paginas"]["diagnostico"]["niveles"][0]["cta"] = {"texto": "Reserva", "href": "falta.html"}
    salida, _ = _generar(pg, tmp_path, rotos)
    detalles = {x["detalle"].split(",")[0] for p in pg.validar(str(salida))["paginas"] for x in p["problemas"]
                if x["id"] == "enlaces.rotos" and x["nivel"] == "error"}
    for href in ("no-existe.html", "tampoco.html", "falta.html"):
        assert f"Enlace a {href}" in detalles, detalles


def test_webinar_hora_y_zona_se_contrastan(pg, tmp_path):
    """Hallazgo 25: "inicio": "2026-03-31T18:00:00+01:00" (el horario de verano empezó el 2026-03-29) daba la página a
    las 18:00 y el calendario a las 19:00 de Madrid."""
    def verano_mal(cfg):
        cfg["paginas"]["webinar"]["evento"]["inicio"] = "2026-03-31T18:00:00+01:00"
    with pytest.raises(pg.ErrorUsuario, match=r"\+02:00"):
        _generar(pg, tmp_path, verano_mal, base=WEBINAR)

    def sin_desfase(cfg):
        ev = cfg["paginas"]["webinar"]["evento"]
        ev["inicio"] = "2026-03-31T18:00:00"
        ev["zona_horaria"] = "Europe/Madrid"
    salida, _ = _generar(pg, tmp_path, sin_desfase, base=WEBINAR)
    web = (salida / "index.html").read_text(encoding="utf-8")
    assert 'data-pos-cuenta="2026-03-31T18:00:00+02:00"' in web and "Martes, 18:00 h" in web
    assert "Canarias: 17:00 h" in web and "México (CDMX): 10:00 h" in web
    ics = next((salida / "recursos").glob("*.ics")).read_text(encoding="utf-8")
    assert "DTSTART:20260331T160000Z" in ics

    def zona_mala(cfg):
        cfg["paginas"]["webinar"]["evento"]["zona_horaria"] = "Hora/Peninsular"
    with pytest.raises(pg.ErrorUsuario, match="IANA"):
        _generar(pg, tmp_path, zona_mala, base=WEBINAR)


def test_webinar_toma_la_zona_de_la_ficha(pg, instancia, tmp_path):
    """Hallazgo 25: con --cliente y sin zona en el evento, la zona_horaria de la ficha."""
    ficha = instancia / "clientes" / "acme" / "ficha.md"
    ficha.write_text(ficha.read_text(encoding="utf-8").replace("Europe/Madrid", "America/Mexico_City"),
                     encoding="utf-8")

    def en_mexico(cfg):
        ev = cfg["paginas"]["webinar"]["evento"]
        ev.pop("zona")
        ev["inicio"] = "2026-12-03T11:00:00"
        ev["otras_zonas"] = [{"nombre": "España", "zona": "Europe/Madrid"}]
    salida, _ = _generar(pg, tmp_path, en_mexico, base=WEBINAR, cliente="acme")
    web = (salida / "index.html").read_text(encoding="utf-8")
    assert 'data-pos-cuenta="2026-12-03T11:00:00-06:00"' in web and "Jueves, 11:00 h" in web
    assert "Hora del centro de México" in web and "España: 18:00 h" in web

    def etiqueta_propia(cfg):
        cfg["paginas"]["webinar"]["evento"]["zona"] = "Hora de Bogotá"
    _, res = _generar(pg, tmp_path, etiqueta_propia, base=WEBINAR)
    assert any("zona_horaria" in a for a in res["avisos"])  # no se puede contrastar: avisa


def test_salida_en_consola_cp1252(pg, tmp_path, monkeypatch):
    """Hallazgo 28: con la salida en cp1252 estricto (Git Bash en Windows, salida redirigida), ✓ y → no revientan."""
    salida, _ = _generar(pg, tmp_path, _sin_casos_de_ejemplo)
    falsa = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict")
    monkeypatch.setattr(sys, "stdout", falsa)
    assert pg.main(["validar", str(salida)]) == 0
    assert pg.main(["generar", "gracias", "--config", str(_config(tmp_path, _sin_casos_de_ejemplo)),
                    "--salida", str(tmp_path / "otra")]) == 0
    falsa.flush()
    texto = falsa.buffer.getvalue().decode("cp1252")
    assert "Total: 0 errores" in texto and "? gracias.html" in texto


# ───────────────────────────── I8: embudo «Captación → VSL con calendario» (curso, módulo 15) ─────────────────────────────
VSL = PAGINAS / "ejemplos" / "acme-vsl-calendario.json"


def _png(ancho, alto):
    ihdr = struct.pack(">IIBBBBB", ancho, alto, 8, 2, 0, 0, 0)
    trozo = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))  # noqa: E731
    return b"\x89PNG\r\n\x1a\n" + trozo(b"IHDR", ihdr) + trozo(b"IEND", b"")


def test_reserva_con_vsl_y_calendario(pg, tmp_path):
    """La página de reserva admite el VSL (las mismas claves que el del hero) y un texto encima del calendario: titular →
    vídeo → calendario → detalles. El vídeo no carga nada de terceros hasta que se pulsa; `Lead` sale en la captación."""
    salida, res = _generar(pg, tmp_path, base=VSL)
    assert res["paginas"] == ["landing", "reserva", "gracias"]
    reserva = (salida / "reserva.html").read_text(encoding="utf-8")
    assert 'class="pos-reserva pos-reserva--video"' in reserva
    assert 'data-pos-video="youtube" data-id="ID-de-tu-VSL"' in reserva
    assert "<iframe" not in reserva and "youtube.com" not in reserva  # el reproductor lo crea paginas.js al pulsar
    orden = [reserva.index(x) for x in ('id="pos-titular"', "data-pos-video=", "¿Encaja con lo que buscas?",
                                         "data-pos-calendario", "En la llamada", '<div class="pos-anfitrion', '<p class="pos-nota"')]
    assert orden == sorted(orden), orden
    cfg = _config_js(reserva)["pagina"]
    assert cfg["calendario"]["url"].startswith("https://") and cfg["evento_schedule"] == "servidor"
    assert cfg["siguiente"] == "gracias.html"
    # la captación: Lead al enviar los datos de contacto, y de ahí a la página del VSL con el calendario
    landing = (salida / "index.html").read_text(encoding="utf-8")
    assert 'data-evento="Lead"' in landing and 'data-siguiente="reserva.html"' in landing
    assert "data-pos-video" not in landing
    # el único aviso de generar es la miniatura, que el ejemplo deja a propósito para que se vea
    assert [a for a in res["avisos"] if "miniatura" not in a] == []
    v = pg.validar(str(salida))
    assert v["ok"] is True and v["errores"] == 0 and v["avisos"] == 0, v


def test_reserva_con_vsl_en_fragmento_ghl(pg, tmp_path):
    salida, _ = _generar(pg, tmp_path, base=VSL, fragmento_ghl=True)
    frag = (salida / "ghl" / "reserva.html").read_text(encoding="utf-8")
    assert '<meta name="pos-tipo" content="reserva">' in frag
    assert "data-pos-video=" in frag and "data-pos-calendario" in frag and "pos-reserva--video" in frag
    assert "<iframe" not in frag and 'id="pos-config"' in frag and "PaginasOS" in frag
    errores = [x for p in pg.validar(str(salida))["paginas"] for x in p["problemas"] if x["nivel"] == "error"]
    assert errores == []


def test_reserva_con_vsl_miniatura_y_foto_bajo_el_calendario(pg, tmp_path):
    (tmp_path / "mini.png").write_bytes(_png(1280, 720))
    (tmp_path / "foto.png").write_bytes(_png(160, 160))

    def con_imagenes(cfg):
        r = cfg["paginas"]["reserva"]
        r["video"]["miniatura"] = str(tmp_path / "mini.png")
        r["anfitrion"]["foto"] = str(tmp_path / "foto.png")
    salida, res = _generar(pg, tmp_path, con_imagenes, base=VSL)
    reserva = (salida / "reserva.html").read_text(encoding="utf-8")
    assert 'src="recursos/img/mini.png" alt="" width="1280" height="720" loading="eager"' in reserva
    assert 'src="recursos/img/foto.png" alt="" width="160" height="160" loading="lazy"' in reserva
    assert res["avisos"] == []
    assert pg.validar(str(salida))["avisos"] == 0  # sin img.lazy: la foto va debajo del calendario


def test_reserva_sin_video_queda_como_antes(pg, tmp_path):
    """Sin `video`, la reserva sigue a dos columnas y sin texto encima del calendario, salvo que lo pidas."""
    salida, _ = _generar(pg, tmp_path, tipos=["reserva"])
    reserva = (salida / "reserva.html").read_text(encoding="utf-8")
    assert '<div class="pos-reserva">' in reserva and 'class="pos-reserva pos-reserva--video"' not in reserva
    assert "data-pos-video" not in reserva
    agenda = reserva.split('class="pos-reserva__agenda"', 1)[1]
    assert agenda.lstrip('" id="calendario">\n').startswith('<div class="pos-calendario"')
    assert reserva.index("En la llamada") < reserva.index("data-pos-calendario")

    def con_texto(cfg):
        cfg["paginas"]["reserva"]["texto_calendario"] = "Elige hueco"
    salida, _ = _generar(pg, tmp_path, con_texto, ["reserva"])
    reserva = (salida / "reserva.html").read_text(encoding="utf-8")
    assert '<h2 class="pos-formulario__titulo">Elige hueco</h2>' in reserva and '<div class="pos-reserva">' in reserva


def test_reserva_con_video_por_defecto_y_mal_escrito(pg, tmp_path):
    def solo_id(cfg):
        r = cfg["paginas"]["reserva"]
        for k in ("titulo", "texto_calendario"):
            r.pop(k)
    salida, _ = _generar(pg, tmp_path, solo_id, ["reserva"], base=VSL)
    reserva = (salida / "reserva.html").read_text(encoding="utf-8")
    assert "Antes de elegir hora, mira este vídeo</h1>" in reserva
    assert '<h2 class="pos-formulario__titulo">Elige día y hora para la llamada</h2>' in reserva
    for malo, mensaje in (("https://youtu.be/abcdefghijk", "como en el hero"),
                          ({"proveedor": "youtube", "id": "https://www.youtube.com/watch?v=abc"}, "tras v="),
                          ({"proveedor": "wistia", "id": "abc123"}, "youtube, vimeo o mp4"),
                          ({"proveedor": "mp4"}, "falta el archivo")):
        def poner(cfg, malo=malo):
            cfg["paginas"]["reserva"]["video"] = malo
        with pytest.raises(pg.ErrorUsuario, match=re.escape(mensaje)):
            _generar(pg, tmp_path, poner, ["reserva"], base=VSL)


def test_validar_avisa_del_video_incrustado(pg, tmp_path):
    """Pegar el código de inserción de YouTube carga el reproductor (y sus cookies) antes de pulsar y sin consentimiento."""
    salida, _ = _generar(pg, tmp_path, base=VSL)
    html = (salida / "reserva.html").read_text(encoding="utf-8").replace(
        '<div class="pos-reserva__agenda"', '<iframe title="VSL" src="https://www.youtube.com/embed/abcdefghijk">'
        '</iframe><div class="pos-reserva__agenda"')
    (salida / "reserva.html").write_text(html, encoding="utf-8")
    problemas = {(x["id"], x["nivel"]) for p in pg.validar(str(salida))["paginas"] if p["archivo"] == "reserva.html"
                 for x in p["problemas"]}
    assert ("video.terceros", "aviso") in problemas
    assert pg.VIDEO_TERCEROS.search("https://player.vimeo.com/video/123") and pg.VIDEO_TERCEROS.search("//youtu.be/x")
    assert not pg.VIDEO_TERCEROS.search("https://reservas.acme.example/widget/booking/llamada")
