"""Tests de herramientas/render.py. Sin red: los renders reales solo corren si hay Playwright y un navegador local."""
from __future__ import annotations

import importlib
import json
import pathlib
import shutil
import struct
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[2]
HTML = RAIZ / "plantillas" / "html"
EJEMPLOS = HTML / "ejemplos"


@pytest.fixture
def render(instancia):
    import render as modulo
    return importlib.reload(modulo)


def _marca_acme(instancia: pathlib.Path) -> pathlib.Path:
    destino = instancia / "clientes" / "acme" / "marca"
    shutil.copytree(HTML / "marca-ejemplo", destino)
    return destino


def _png(ruta: pathlib.Path) -> tuple[int, int]:
    cabecera = ruta.read_bytes()[:24]
    assert cabecera[:8] == b"\x89PNG\r\n\x1a\n", f"{ruta.name} no es un PNG"
    return struct.unpack(">II", cabecera[16:24])


# ───────────────────────────── plantillado ─────────────────────────────
def test_sustitucion_escapa_html(render):
    salida, faltan = render.renderizar_texto('<p title="{{t}}">{{a.b}}</p>', {"a": {"b": "<script>&"}, "t": 'x"y'})
    assert salida == '<p title="x&quot;y">&lt;script&gt;&amp;</p>'
    assert faltan == []


def test_secciones_listas_invertidas_y_anidadas(render):
    plantilla = ("{{#lista}}{{@indice}}/{{@total}}:{{.}};{{/lista}}"
                 "{{^vacia}}sin elementos{{/vacia}}"
                 "{{#dict}}[{{x}}]{{/dict}}"
                 "{{#filas}}<tr>{{#.}}<td>{{.}}</td>{{/.}}</tr>{{/filas}}")
    datos = {"lista": ["a", "b"], "vacia": [], "dict": {"x": 1}, "filas": [["1", "2"], ["3", "4"]]}
    salida, _ = render.renderizar_texto(plantilla, datos)
    assert salida == "1/2:a;2/2:b;sin elementos[1]<tr><td>1</td><td>2</td></tr><tr><td>3</td><td>4</td></tr>"


def test_condicion_con_interrogacion_no_filtra_contexto(render):
    # {{#kpis.0}} entraría en el primer elemento y su «nota» aparecería en los demás; {{#kpis?}} no entra.
    plantilla = "{{#kpis?}}{{#kpis}}[{{n}}{{#nota}}:{{nota}}{{/nota}}]{{/kpis}}{{/kpis?}}{{#otra?}}no{{/otra?}}"
    salida, _ = render.renderizar_texto(plantilla, {"kpis": [{"n": "a", "nota": "x"}, {"n": "b"}], "otra": []})
    assert salida == "[a:x][b]"


def test_datos_que_faltan_y_filtros(render, tmp_path):
    (tmp_path / "foto.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")
    plantilla = "{{nada}}|{{n|num}}|{{d|eur}}|{{p|pct}}|{{t|mayusculas}}|{{img|uri}}|{{web|uri}}|{{rota|uri}}"
    datos = {"n": 12345.5, "d": 3180, "p": 70.3, "t": "año", "img": "foto.svg", "web": "https://ejemplo.com/a.png",
             "rota": "no-existe.png"}
    salida, faltan = render.renderizar_texto(plantilla, datos, base=tmp_path)
    partes = salida.split("|")
    assert partes[:5] == ["", "12.345,50", "3.180 €", "70,3 %", "AÑO"]
    assert partes[5].startswith("data:image/svg+xml;base64,")
    assert partes[6] == "https://ejemplo.com/a.png" and partes[7] == ""
    assert "nada" in faltan and any("no-existe.png" in f for f in faltan)


def test_errores_de_sintaxis(render):
    for mala in ("{{#a}}sin cerrar", "{{/a}}", "{{#a}}{{/b}}", "{{}}"):
        with pytest.raises(render.ErrorUsuario):
            render.renderizar_texto(mala, {})
    with pytest.raises(render.ErrorUsuario):
        render.renderizar_texto("{{x|inventado}}", {"x": 1})


# ───────────────────────────── formatos y zonas ─────────────────────────────
def test_parsear_formatos(render):
    assert render.parsear_formatos("1x1, 4:5,9X16,4x5") == ["1x1", "4x5", "9x16"]
    assert render.parsear_formatos(None) == ["1x1", "4x5", "9x16"]
    assert render.parsear_formatos(None, ["1x1", "4x5"]) == ["1x1", "4x5"]
    for malo in ("16x9", ",", "4x5,2x3"):
        with pytest.raises(ValueError):
            render.parsear_formatos(malo)
    with pytest.raises(ValueError, match="no admite"):
        render.parsear_formatos("9x16", ["1x1", "4x5"])


def test_zonas_seguras(render):
    z = render.zona_segura("9x16")
    assert (z["arriba"], z["abajo"], z["izquierda"], z["derecha"]) == (269, 672, 65, 65)
    assert z["exclusiones"][0]["x0"] == 853 and z["exclusiones"][0]["y0"] == 1152
    assert render.zona_segura("4x5")["arriba"] == 54 and render.zona_segura("1x1")["exclusiones"] == []


# ───────────────────────────── marca ─────────────────────────────
def test_marca_por_defecto(render):
    m = render.cargar_marca()
    assert m["_origen"] == "defecto" and m["colores"]["primario"] == render.MARCA_DEFECTO["colores"]["primario"]
    assert any("marca neutra" in a for a in m["_avisos"])


def test_marca_del_cliente_con_valores_por_defecto_y_rutas_relativas(render, instancia):
    carpeta = instancia / "clientes" / "acme" / "marca"
    carpeta.mkdir(parents=True)
    (carpeta / "logo.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>", encoding="utf-8")
    (carpeta / "marca.json").write_text(json.dumps({
        "colores": {"primario": "#FF0000", "acento": "rojo"},
        "tipografias": {"titulos": {"familia": "Marca Sans", "archivo": "fuentes/NoExiste.ttf", "peso": 700}},
        "logo": {"principal": "logo.svg"},
    }), encoding="utf-8")
    m = render.cargar_marca("acme")
    assert m["_origen"] == "clientes/acme/marca/marca.json"
    assert m["nombre"] == "Acme Automations"  # de la ficha, porque marca.json no trae nombre
    assert m["colores"]["primario"] == "#FF0000"
    assert m["colores"]["acento"] == render.MARCA_DEFECTO["colores"]["acento"]
    assert m["colores"]["fondo"] == render.MARCA_DEFECTO["colores"]["fondo"]
    assert any("no es hexadecimal" in a for a in m["_avisos"])
    avisos: list[str] = []
    ctx = render.contexto_marca(m, avisos)
    assert ctx["logo"]["principal"].startswith("data:image/svg+xml;base64,")
    assert ctx["logo"]["claro"] == ctx["logo"]["principal"]
    css = render.css_inyectado(m, render.contexto_formato("9x16"), avisos)
    assert "--color-primario:#FF0000" in css and "--zs-arriba:269px" in css and "@font-face" in css
    assert any("NoExiste.ttf" in a for a in avisos)


def test_marca_cliente_sin_marca_y_errores(render, instancia):
    m = render.cargar_marca("acme")
    assert m["_origen"] == "defecto" and m["nombre"] == "Acme Automations"
    assert any("marca.json no existe" in a for a in m["_avisos"])
    with pytest.raises(render.ErrorUsuario):
        render.cargar_marca("no-existe")
    with pytest.raises(render.ErrorUsuario):
        render.cargar_marca("../fuera")
    roto = instancia / "roto.json"
    roto.write_text("{no es json", encoding="utf-8")
    with pytest.raises(render.ErrorUsuario):
        render.cargar_marca(ruta=roto)


def test_contraste_wcag(render, tmp_path):
    assert render.contraste("#FFFFFF", "#000000") == 21.0
    archivo = tmp_path / "marca.json"
    archivo.write_text(json.dumps({"colores": {"primario": "#FFFF00", "texto_sobre_primario": "#FFFFFF"}}), encoding="utf-8")
    assert any("Contraste bajo" in a for a in render.cargar_marca(ruta=archivo)["_avisos"])


def test_marca_de_ejemplo_es_valida(render):
    m = render.cargar_marca(ruta=HTML / "marca-ejemplo" / "marca.json")
    avisos = list(m["_avisos"])
    ctx = render.contexto_marca(m, avisos)
    assert avisos == [] and ctx["logo"]["principal"] and ctx["logo"]["claro"] != ctx["logo"]["principal"]


# ───────────────────────────── plantillas del producto ─────────────────────────────
@pytest.mark.parametrize("nombre,formatos", [("estatico", ["1x1", "4x5", "9x16"]), ("carrusel", ["1x1", "4x5"]),
                                             ("informe-cliente", ["a4"])])
def test_plantillas_con_sus_ejemplos(render, nombre, formatos):
    plantilla = HTML / f"{nombre}.html"
    texto = plantilla.read_text(encoding="utf-8")
    if formatos != ["a4"]:
        assert render.formatos_de_plantilla(texto) == formatos
    datos, base = render.leer_datos(str(EJEMPLOS / f"{nombre}.json"))
    marca = render.cargar_marca(ruta=HTML / "marca-ejemplo" / "marca.json")
    for f in formatos:
        avisos: list[str] = []
        html = render.construir_html(plantilla, datos, base, marca, render.contexto_formato(f), avisos)
        assert avisos == [], avisos  # los ejemplos traen todos los datos que usa la plantilla
        assert "{{" not in html and "}}" not in html
        assert '<style id="render-marca">' in html and "<base href=\"file://" in html
        assert "http://" not in html.replace("http://www.w3.org", "")  # sin dependencias externas


def test_ejemplos_sin_datos_reales():
    texto = " ".join(p.read_text(encoding="utf-8") for p in EJEMPLOS.glob("*.json"))
    assert "/Users/" not in texto and "@" not in texto
    for ficticia in ("Acme Automations", "Nimbo", "Clínica Sonrisa"):
        assert ficticia in texto


# ───────────────────────────── CLI y códigos de salida ─────────────────────────────
def test_cli_plantilla_o_datos_inexistentes(render, tmp_path, capsys):
    assert render.main(["png", str(tmp_path / "no.html"), "--salida", str(tmp_path)]) == 1
    assert "No existe la plantilla" in capsys.readouterr().err
    assert render.main(["png", str(HTML / "estatico.html"), "--datos", str(tmp_path / "no.json"),
                        "--salida", str(tmp_path), "--json"]) == 1
    salida = json.loads(capsys.readouterr().out)
    assert salida == {"ok": False, "codigo": 1, "error": salida["error"]} and "datos" in salida["error"]
    assert render.main(["png", str(HTML / "carrusel.html"), "--formatos", "9x16", "--salida", str(tmp_path)]) == 1
    assert render.main(["pdf", str(HTML / "informe-cliente.html"), "--salida", str(tmp_path / "x.png")]) == 1


def test_cli_sin_playwright_da_codigo_2(render, tmp_path, monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "playwright", None)
    monkeypatch.setitem(sys.modules, "playwright.sync_api", None)
    codigo = render.main(["png", str(HTML / "estatico.html"), "--datos", str(EJEMPLOS / "estatico.json"),
                          "--formatos", "4x5", "--salida", str(tmp_path / "salida")])
    assert codigo == 2
    assert "uv sync --extra render" in capsys.readouterr().err
    codigo = render.main(["pdf", str(HTML / "informe-cliente.html"), "--salida", str(tmp_path / "i.pdf"), "--json"])
    assert codigo == 2 and json.loads(capsys.readouterr().out)["codigo"] == 2


# ───────────────────────────── renders reales (si hay navegador) ─────────────────────────────
@pytest.fixture(scope="module")
def navegador():
    pytest.importorskip("playwright.sync_api")
    sys.path.insert(0, str(RAIZ / "herramientas"))
    import render as modulo
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as pw:
            nav, canal = modulo._lanzar(pw)
            nav.close()
    except Exception as e:  # noqa: BLE001
        pytest.skip(f"sin navegador para Playwright: {e}")
    return canal


def test_png_real_tamanos_exactos(render, instancia, navegador, tmp_path, capsys):
    _marca_acme(instancia)
    salida = tmp_path / "estatico"
    codigo = render.main(["png", str(HTML / "estatico.html"), "--datos", str(EJEMPLOS / "estatico.json"),
                          "--formatos", "1x1,4x5,9x16", "--salida", str(salida), "--cliente", "acme", "--json"])
    assert codigo == 0
    res = json.loads(capsys.readouterr().out)
    assert res["marca"] == "clientes/acme/marca/marca.json"
    tamanos = {a["formato"]: _png(pathlib.Path(salida / pathlib.Path(a["ruta"]).name)) for a in res["archivos"]}
    assert tamanos == {"1x1": (1080, 1080), "4x5": (1080, 1350), "9x16": (1080, 1920)}
    assert not [a for a in res["avisos"] if "zona segura" in a or "no carga" in a or "no cabe" in a], res["avisos"]


def test_carrusel_real_una_imagen_por_tarjeta(render, navegador, tmp_path, capsys):
    salida = tmp_path / "carrusel"
    assert render.main(["png", str(HTML / "carrusel.html"), "--datos", str(EJEMPLOS / "carrusel.json"), "--formatos", "4x5",
                        "--salida", str(salida), "--marca", str(HTML / "marca-ejemplo"), "--nombre", "caso-nimbo"]) == 0
    archivos = sorted(salida.glob("caso-nimbo_4x5_*.png"))
    assert [a.name for a in archivos] == [f"caso-nimbo_4x5_{i:02d}.png" for i in range(1, 6)]
    assert {_png(a) for a in archivos} == {(1080, 1350)}


def test_pdf_real(render, navegador, tmp_path, capsys):
    pdf = tmp_path / "informe.pdf"
    assert render.main(["pdf", str(HTML / "informe-cliente.html"), "--datos", str(EJEMPLOS / "informe-cliente.json"),
                        "--salida", str(pdf), "--json"]) == 0
    res = json.loads(capsys.readouterr().out)
    assert pdf.read_bytes()[:5] == b"%PDF-" and res["paginas"] >= 2


def test_aviso_de_zona_segura_y_ajuste(render, navegador, tmp_path, capsys):
    plantilla = tmp_path / "prueba.html"
    plantilla.write_text(
        "<html><head><style>body{margin:0;width:var(--ancho);height:var(--alto)}"
        ".a{position:absolute;top:10px;left:10px;font-size:40px}"
        ".b{position:absolute;top:400px;left:100px;width:300px;height:100px;overflow:hidden}"
        ".b p{font-size:calc(var(--escala,1)*60px);line-height:1}</style></head><body>"
        "<div class='a' data-zona-segura='arriba'>Fuera</div>"
        "<div class='b' data-ajustar='caja'><p>Texto bastante largo que no cabe</p></div></body></html>",
        encoding="utf-8")
    assert render.main(["png", str(plantilla), "--formatos", "9x16", "--salida", str(tmp_path / "o"), "--json"]) == 0
    avisos = json.loads(capsys.readouterr().out)["avisos"]
    assert any("«arriba» fuera de la zona segura" in a for a in avisos), avisos
    assert any("«caja»" in a for a in avisos), avisos
