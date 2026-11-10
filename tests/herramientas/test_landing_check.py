import json
import urllib.parse

import pytest

import _comun
import landing_check as lc

HTML = """<!doctype html><html><head><title>Acme Automations · Demo</title>
<meta name="description" content="Automatiza tu atenci&oacute;n al cliente">
<meta name="viewport" content="width=device-width">
<script>!function(f,b,e,v){}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '000000000000000'); fbq('track', 'PageView'); fbq('consent', 'grant');</script>
<script src="https://www.googletagmanager.com/gtm.js?id=GTM-ABC1234"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-ABCDEF1234"></script>
<script src="https://cdn.cookiebot.com/uc.js"></script>
<link href="https://assets.leadconnectorhq.com/x.css">
</head><body><h1>Recupera 10 horas a la semana</h1>
<a class="btn btn-primary" href="#demo">Reservar <b>demo</b></a><button class="cta">Reservar demo</button>
<form action="/lead"></form><iframe src="https://calendly.com/acme/demo"></iframe>
<script>fbq('trackCustom', 'Demo_Click')</script></body></html>"""


def test_analizar_html():
    r = lc.analizar_html(HTML)
    assert r["pixel_ids"] == ["000000000000000"] and r["fbevents_js"] is True and r["consent_fbq"] is True
    assert r["eventos_fbq"] == ["Demo_Click", "PageView"]
    assert r["gtm"] == ["GTM-ABC1234"] and r["ga4"] == ["G-ABCDEF1234"]
    assert r["plataforma"] == ["GoHighLevel"] and r["cmp"] == ["Cookiebot"] and r["calendario"] == ["Calendly"]
    assert r["title"] == "Acme Automations · Demo" and r["meta_description"] == "Automatiza tu atención al cliente"
    assert r["h1"] == ["Recupera 10 horas a la semana"] and r["ctas"] == ["Reservar demo"]
    assert r["formularios"] == 1 and r["viewport_movil"] is True
    vacio = lc.analizar_html("<html></html>")
    assert vacio["pixel_ids"] == [] and vacio["title"] == "" and vacio["plataforma"] == []


@pytest.fixture
def web(instancia, monkeypatch):
    """Red simulada. Depende de `instancia` para parchear `_comun` después de que la fixture lo recargue."""
    pedidas = []

    def get_texto(url, timeout=40):
        pedidas.append(url)
        if "rota" in url:
            raise OSError("sin conexión")
        if "redirige" in url:
            return HTML, "https://acme.example/gracias", 200  # pierde fbclid y UTM
        return HTML, url, 200

    def get_json(url, params=None, **kw):
        assert "pagespeedonline" in url and params["strategy"] == "mobile"
        return {"lighthouseResult": {"categories": {"performance": {"score": 0.42}},
                                     "audits": {"largest-contentful-paint": {"displayValue": "5,1 s"}}},
                "loadingExperience": {"metrics": {"LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 3100,
                                                                                  "category": "AVERAGE"}}}}

    monkeypatch.setattr(_comun, "get_texto", get_texto)
    monkeypatch.setattr(_comun, "get_json", get_json)
    monkeypatch.delenv("PAGESPEED_API_KEY", raising=False)
    return pedidas


def test_chequear_conserva_parametros(web):
    r = lc.chequear("acme.example/demo?ref=x#form", dataset="000000000000000")
    pedida = urllib.parse.urlsplit(web[0])
    assert pedida.fragment == "form" and urllib.parse.parse_qs(pedida.query)["ref"] == ["x"]
    assert r["fbclid_conservado"] is True and r["utm_conservadas"] is True
    assert r["pixel_coincide_ficha"] is True
    assert r["pagespeed"]["puntuacion_lab"] == 42 and r["pagespeed"]["LCP_campo_p75_ms"] == 3100
    assert "LCP p75 de usuarios reales 3.1 s → mejorable" in lc.texto(r)


def test_chequear_detecta_perdida_y_pixel_ajeno(web):
    r = lc.chequear("https://acme.example/redirige", con_pagespeed=False, dataset="999999999999999")
    assert r["fbclid_conservado"] is False and r["utm_conservadas"] is False and "pagespeed" not in r
    t = lc.texto(r)
    assert "se pierde la atribución del clic" in t and "no es el dataset de la ficha" in t


def test_pagespeed_que_falla_no_rompe(web, monkeypatch):
    def roto(*a, **k):
        raise RuntimeError("HTTP 429: Quota exceeded")
    monkeypatch.setattr(_comun, "get_json", roto)
    r = lc.chequear("https://acme.example/demo")
    assert "Quota" in r["pagespeed"]["error"] and "PAGESPEED_API_KEY" in lc.texto(r)


def test_main_con_cliente_guarda(web, instancia, capsys):
    assert lc.main(["https://Acme.example/demo", "--sin-pagespeed", "--cliente", "acme", "--json"]) == 0
    r = json.loads(capsys.readouterr().out)
    assert r["pixel_coincide_ficha"] is True and r["guardado"].startswith("clientes/acme/auditorias/landing_")
    assert r["guardado"].endswith("_acme.example.md") and (instancia / r["guardado"]).exists()


def test_main_errores(web, instancia, capsys):
    assert lc.main(["https://rota.example", "--sin-pagespeed"]) == 1
    assert "No se pudo descargar" in capsys.readouterr().err
    assert lc.main(["https://acme.example", "--cliente", "nadie"]) == 2
    assert lc.main(["https://acme.example", "--sin-pagespeed"]) == 0
    assert capsys.readouterr().out.startswith("# Chequeo de landing: https://acme.example")


# ---------------------------------------------------------------- píxel tras consentimiento

def _pagina_generada(tmp_path, pixel="123456789012345", **kw) -> str:
    """Una página real de herramientas/paginas.py (la de gracias del ejemplo de Acme)."""
    import importlib
    import pathlib
    import paginas
    paginas = importlib.reload(paginas)
    base = pathlib.Path(paginas.__file__).resolve().parents[1] / "plantillas" / "paginas" / "ejemplos"
    cfg = json.loads((base / "acme-embudo.json").read_text(encoding="utf-8"))
    cfg["marca"]["ruta"] = str((base / cfg["marca"]["ruta"]).resolve())
    cfg["tracking"]["pixel_id"] = pixel
    ruta = tmp_path / "config.json"
    ruta.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    salida = tmp_path / "salida"
    paginas.Generador(str(ruta), str(salida), **kw).generar(["gracias"])
    return (salida / "gracias.html").read_text(encoding="utf-8")


@pytest.mark.parametrize("en_linea", [False, True])
def test_pagina_generada_es_pixel_tras_consentimiento(instancia, tmp_path, en_linea):
    r = lc.analizar_html(_pagina_generada(tmp_path, en_linea=en_linea))
    assert r["pixel_ids"] == [] and r["pagina_generada"] is True
    assert r["pixel_tras_consentimiento"] == ["123456789012345"] and r["pixel_diferido_por"] == "paginas.py"
    t = lc.texto({"url": "https://acme.example/gracias", "estado_http": 200, "url_final": "https://acme.example/gracias",
                  "fbclid_conservado": True, "utm_conservadas": True, **r})
    assert "123456789012345 tras consentimiento (paginas.py)" in t and "fbevents.js: tras consentimiento" in t
    assert "no visible" not in t.split("Meta Pixel en el HTML:")[1].split("\n")[0]
    assert "paginas.py validar" in t and "puede cargarse vía GTM" not in t


def test_pagina_generada_sin_pixel(instancia, tmp_path):
    r = lc.analizar_html(_pagina_generada(tmp_path, pixel=""))
    assert r["pixel_tras_consentimiento"] == [] and r["pagina_generada_sin_pixel"] is True
    t = lc.texto({"url": "u", "estado_http": 200, "url_final": "u", "fbclid_conservado": True,
                  "utm_conservadas": True, **r})
    assert "sin `tracking.pixel_id`" in t


def test_pixel_bloqueado_por_el_gestor_de_cookies():
    html = ('<script type="text/plain" data-cookieconsent="marketing">fbq("init", "222222222222222");'
            'fbq("track","PageView")</script><script>fbq("init", "333333333333333")</script>')
    r = lc.analizar_html(html)
    assert r["pixel_ids"] == ["222222222222222", "333333333333333"]
    assert r["pixel_tras_consentimiento"] == ["222222222222222"]
    assert r["pixel_diferido_por"] == "gestor de consentimiento" and r["pagina_generada"] is False
    assert lc._pixel_texto(r) == "333333333333333 · 222222222222222 tras consentimiento (gestor de consentimiento)"


def test_dataset_de_la_ficha_con_pixel_diferido(web, monkeypatch, tmp_path, instancia):
    html = _pagina_generada(tmp_path)
    monkeypatch.setattr(_comun, "get_texto", lambda url, timeout=40: (html, url, 200))
    assert lc.chequear("https://acme.example/gracias", False, "123456789012345")["pixel_coincide_ficha"] is True
    otro = lc.chequear("https://acme.example/gracias", False, "999999999999999")
    assert otro["pixel_coincide_ficha"] is False and "no es el dataset de la ficha" in lc.texto(otro)
