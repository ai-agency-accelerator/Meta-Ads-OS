"""Marca del cliente (`clientes/<slug>/marca/marca.json`) y rutas de proyecto de cutkit. Solo biblioteca estándar."""
from __future__ import annotations

import json

import pytest

from cutkit_apoyo import FUENTES, MARCA_ACME


def _marca_cliente(raiz, datos, archivos: dict[str, bytes] | None = None):
    d = raiz / "clientes" / "acme" / "marca"
    d.mkdir(parents=True, exist_ok=True)
    (d / "marca.json").write_text(datos if isinstance(datos, str) else json.dumps(datos), encoding="utf-8")
    for nombre, contenido in (archivos or {}).items():
        (d / nombre).parent.mkdir(parents=True, exist_ok=True)
        (d / nombre).write_bytes(contenido)
    return d


# ── fuentes: lo que libass necesita ──────────────────────────────────────────
def test_metricas_de_la_montserrat_del_producto(cutkit_lib):
    _, marca, _ = cutkit_lib
    m = marca.metricas_fuente(FUENTES / "Montserrat-ExtraBold.ttf")
    # libass compara el Fontname del estilo con el name ID 1, no con la familia tipográfica (ID 16)
    assert m["familia"] == "Montserrat ExtraBold" and m["peso"] == 800 and not m["variable"]
    # el cuerpo de libass es winAscent + winDescent, más alto que el em: si se midiera con el em, las cajas de la QA
    # saldrían un 36 % más estrechas que el texto pintado
    assert m["upm"] == 1000 and m["alto_libass"] > m["upm"]


def test_metricas_detectan_fuentes_variables(cutkit_lib):
    _, marca, _ = cutkit_lib
    assert marca.metricas_fuente(FUENTES / "Montserrat[wght].ttf")["variable"] is True


@pytest.mark.parametrize("contenido, mensaje", [
    (b"wOF2" + b"\0" * 60, "WOFF"),
    (b"Copyright 2011 The Montserrat Project Authors", "no es una fuente"),
    (b"\x00\x01\x00\x00\x00\x09", "dañada"),
])
def test_metricas_de_archivos_que_no_sirven(cutkit_lib, tmp_path, contenido, mensaje):
    _, marca, _ = cutkit_lib
    f = tmp_path / "fuente.ttf"
    f.write_bytes(contenido)
    with pytest.raises(marca.MarcaInvalida, match=mensaje):
        marca.metricas_fuente(f)


# ── colores ──────────────────────────────────────────────────────────────────
def test_colores_ass_y_contraste(cutkit_lib):
    _, marca, _ = cutkit_lib
    assert marca.hex_valido("1d4ed8") == "#1D4ED8"
    assert marca.ass_color("#1D4ED8") == "&H00D84E1D"           # &HAABBGGRR
    assert marca.ass_color("#FFFFFF", 128) == "&H80FFFFFF"
    assert round(marca.contraste("#FFFFFF", "#000000"), 1) == 21.0
    with pytest.raises(marca.MarcaInvalida, match="#RRGGBB"):
        marca.hex_valido("azul")


# ── carga de la marca ────────────────────────────────────────────────────────
def test_sin_cliente_marca_neutra(cutkit_lib):
    _, marca, _ = cutkit_lib
    m = marca.cargar()
    assert m.nombre == "" and m.color("primario").startswith("#") and m.fuente("titulos").exists()
    assert m.datos["etiqueta_ia"] == "Contenido generado con IA" and not m.avisos


def test_cliente_sin_marca_avisa_y_usa_la_neutra(cutkit_lib):
    _, marca, _ = cutkit_lib
    m = marca.cargar("acme")
    assert m.nombre == "" and any("marca.json" in a for a in m.avisos)


def test_marca_del_cliente_se_fusiona_con_la_neutra(cutkit_lib):
    _, marca, raiz = cutkit_lib
    _marca_cliente(raiz, MARCA_ACME, {"logo.png": b"\x89PNG\r\n\x1a\n"})
    m = marca.cargar("acme")
    assert m.nombre == "Acme Automations" and m.color("primario") == "#1D4ED8"
    assert m.datos["cta_por_defecto"] == "Pide tu demo"
    assert m.sub("color") == "#FFFFFF"                           # de la neutra: el cliente no lo define
    assert m.logo() == raiz / "clientes" / "acme" / "marca" / "logo.png"
    assert m.fuente("titulos").name == "Montserrat-ExtraBold.ttf" and not m.avisos


def test_ruta_explicita_prevalece_y_debe_existir(cutkit_lib, tmp_path):
    _, marca, raiz = cutkit_lib
    _marca_cliente(raiz, MARCA_ACME)
    otra = tmp_path / "otra.json"
    otra.write_text(json.dumps({"nombre": "Nimbo"}), encoding="utf-8")
    assert marca.cargar("acme", ruta=otra).nombre == "Nimbo"
    with pytest.raises(marca.MarcaInvalida, match="no existe"):
        marca.cargar(ruta=tmp_path / "no-esta.json")


@pytest.mark.parametrize("contenido, mensaje", [
    ('{"nombre": "Acme",}', "no es JSON válido"),
    ("[1, 2]", "objeto JSON"),
    ({"colores": {"primario": "rojo"}}, "color no válido"),
    ({"subtitulos": {"resaltado": "#12"}}, "color no válido"),
])
def test_marca_invalida_dice_que_arreglar(cutkit_lib, contenido, mensaje):
    _, marca, raiz = cutkit_lib
    _marca_cliente(raiz, contenido)
    with pytest.raises(marca.MarcaInvalida, match=mensaje):
        marca.cargar("acme")


def test_contraste_bajo_avisa(cutkit_lib):
    _, marca, raiz = cutkit_lib
    _marca_cliente(raiz, {"colores": {"primario": "#FFE066", "texto_sobre_primario": "#FFFFFF"}})
    assert any("contraste bajo" in a for a in marca.cargar("acme").avisos)


def test_tipografia_del_cliente_y_sus_fallos(cutkit_lib):
    _, marca, raiz = cutkit_lib
    ttf = (FUENTES / "Montserrat-SemiBold.ttf").read_bytes()
    _marca_cliente(raiz, {"tipografias": {"titulos": {"archivo": "fuentes/Titulos.ttf"},
                                          "texto": {"archivo": "fuentes/web.woff2"}}},
                   {"fuentes/Titulos.ttf": ttf, "fuentes/web.woff2": b"wOF2" + b"\0" * 60})
    m = marca.cargar("acme")
    assert m.fuente("titulos") == raiz / "clientes" / "acme" / "marca" / "fuentes" / "Titulos.ttf"
    assert m.fuente("texto").name == "Montserrat-SemiBold.ttf"            # la WOFF2 no vale para vídeo
    assert any("WOFF" in a for a in m.avisos)
    m.fuente("texto")
    assert sum("WOFF" in a for a in m.avisos) == 1                         # el aviso no se repite


def test_tipografia_variable_avisa(cutkit_lib):
    _, marca, raiz = cutkit_lib
    _marca_cliente(raiz, {"tipografias": {"titulos": {"archivo": "Montserrat[wght].ttf"}}})
    m = marca.cargar("acme")
    assert m.fuente("titulos").name == "Montserrat[wght].ttf"
    assert any("variable" in a for a in m.avisos)


# ── rutas de proyecto ────────────────────────────────────────────────────────
def test_proyecto_en_creativos_del_cliente(cutkit_lib):
    paths, _, raiz = cutkit_lib
    (raiz / "clientes" / "acme").mkdir()
    d = paths.proyecto_dir("demo-crm", "acme", fecha="2026-11-09", crear=True)
    assert d == raiz / "clientes" / "acme" / "creativos" / "2026-11-09_demo-crm"
    assert paths.proyecto_dir("demo-crm") == d                              # sin cliente: lo busca
    assert paths.cliente_de("demo-crm") == "acme"
    assert paths.run_dir("demo-crm") == d / "edicion" and (d / "edicion" / "versions").is_dir()


def test_proyecto_de_cliente_inexistente_o_slug_raro(cutkit_lib):
    paths, _, _ = cutkit_lib
    with pytest.raises(paths.ProyectoNoEncontrado, match="cliente-nuevo"):
        paths.proyecto_dir("demo", "nimbo", crear=True)
    with pytest.raises(paths.ProyectoNoEncontrado):
        paths.proyecto_dir("no-existe")
    for malo in ("../fuera", "Demo", "a b", ""):
        with pytest.raises(ValueError):
            paths.marca_dir(malo) if malo else paths.proyecto_dir(malo)


def test_cargar_entorno_no_pisa_lo_que_ya_hay(cutkit_lib, monkeypatch):
    paths, _, raiz = cutkit_lib
    (raiz / ".env").write_text("# claves\nexport CK_PRUEBA_A='uno'\nCK_PRUEBA_B=dos\n", encoding="utf-8")
    monkeypatch.setenv("CK_PRUEBA_B", "ya-estaba")
    monkeypatch.delenv("CK_PRUEBA_A", raising=False)
    paths.cargar_entorno()
    import os
    assert os.environ["CK_PRUEBA_A"] == "uno" and os.environ["CK_PRUEBA_B"] == "ya-estaba"
    monkeypatch.delenv("CK_PRUEBA_A")
