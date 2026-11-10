"""Tests de herramientas/editar_video.py: vídeos sintéticos de FFmpeg, sin red."""
from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys

import pytest

import editar_video as ev

RAIZ_PRODUCTO = pathlib.Path(__file__).resolve().parents[2]
HAY_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
requiere_ffmpeg = pytest.mark.skipif(not HAY_FFMPEG, reason="FFmpeg no está instalado")


def _hay_libass() -> bool:
    return HAY_FFMPEG and "ass" in ev._capacidades(shutil.which("ffmpeg"))["filtros"]


requiere_libass = pytest.mark.skipif(not _hay_libass(), reason="FFmpeg sin libass")

SRT = """1
00:00:00,000 --> 00:00:01,200
¿Tu agencia pierde leads cada noche?

2
00:00:01,200 --> 00:00:02,400
<i>Así</i> lo resolvimos en una semana
"""


def _sintetico(ruta: pathlib.Path, ancho: int = 320, alto: int = 180, dur: float = 2.0, audio: str = "seno") -> pathlib.Path:
    fuentes_audio = {
        "seno": f"sine=frequency=440:sample_rate=48000:duration={dur}",
        # voz (tono) en [0,1) [2,3) [4,5) y silencio en [1,2) [3,4)
        "pausas": f"aevalsrc='if(lt(mod(t\\,2)\\,1)\\,0.5*sin(2*PI*440*t)\\,0)':s=48000:d={dur}",
    }
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi",
           "-i", f"testsrc2=size={ancho}x{alto}:rate=30:duration={dur}"]
    if audio:
        cmd += ["-f", "lavfi", "-i", fuentes_audio[audio], "-shortest", "-c:a", "aac"]
    cmd += ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", str(ruta)]
    subprocess.run(cmd, check=True)
    return ruta


def _sondear(ruta: pathlib.Path) -> dict:
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                   "stream=codec_type,width,height,duration", "-of", "json", str(ruta)],
                                  capture_output=True, text=True, check=True).stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    return {"ancho": v["width"], "alto": v["height"], "duracion": float(v["duration"]),
            "audio": any(s["codec_type"] == "audio" for s in j["streams"])}


def _ejecutar(capsys, *args) -> tuple[int, dict]:
    codigo = ev.main([*map(str, args), "--json"])
    salida = capsys.readouterr().out.strip().splitlines()
    return codigo, (json.loads(salida[-1]) if salida else {})


@pytest.fixture(scope="module")
def horizontal(tmp_path_factory):
    if not HAY_FFMPEG:
        pytest.skip("FFmpeg no está instalado")
    return _sintetico(tmp_path_factory.mktemp("fuentes") / "horizontal.mp4", 640, 360, 2.0)


@pytest.fixture(scope="module")
def vertical(tmp_path_factory):
    if not HAY_FFMPEG:
        pytest.skip("FFmpeg no está instalado")
    return _sintetico(tmp_path_factory.mktemp("fuentes") / "vertical.mp4", 540, 960, 2.4)


# ─────────────────────────────── reformatear ───────────────────────────────

@requiere_ffmpeg
@pytest.mark.parametrize("formato", ["9x16", "4x5", "1x1"])
@pytest.mark.parametrize("modo", ["recorte", "relleno", "desenfoque"])
def test_reformatear_da_la_resolucion_exacta(horizontal, tmp_path, capsys, formato, modo):
    salida = tmp_path / f"{formato}_{modo}.mp4"
    codigo, res = _ejecutar(capsys, "reformatear", horizontal, "--formato", formato, "--modo", modo,
                            "--salida", salida, "--borrador")
    assert codigo == 0, res
    info = _sondear(salida)
    assert (info["ancho"], info["alto"]) == ev.FORMATOS[formato]
    assert res["formato"] == formato and info["audio"]
    assert abs(info["duracion"] - 2.0) <= 1 / 30 + 1e-6


@requiere_ffmpeg
def test_reformatear_avisa_de_recorte_y_ampliacion(horizontal, tmp_path, capsys):
    codigo, res = _ejecutar(capsys, "reformatear", horizontal, "--formato", "9x16", "--salida", tmp_path / "v.mp4",
                            "--borrador")
    assert codigo == 0
    assert any("Recortas el" in a for a in res["avisos"]) and any("se amplía" in a for a in res["avisos"])


# ─────────────────────────────── cortar ───────────────────────────────

@requiere_ffmpeg
def test_cortar_por_tiempos(horizontal, tmp_path, capsys):
    salida = tmp_path / "corte.mp4"
    codigo, res = _ejecutar(capsys, "cortar", horizontal, "--desde", "0.5", "--hasta", "1.7", "--salida", salida,
                            "--borrador")
    assert codigo == 0, res
    assert abs(_sondear(salida)["duracion"] - 1.2) <= 1 / 30 + 1e-6


@requiere_ffmpeg
def test_cortar_tramo_imposible_es_error_del_usuario(horizontal, tmp_path, capsys):
    codigo, res = _ejecutar(capsys, "cortar", horizontal, "--desde", "1.5", "--hasta", "1.0",
                            "--salida", tmp_path / "x.mp4")
    assert codigo == 1 and not res["ok"]


@requiere_ffmpeg
def test_quitar_silencios_acorta_y_mantiene_la_voz(tmp_path, capsys):
    fuente = _sintetico(tmp_path / "pausas.mp4", 320, 180, 5.0, audio="pausas")
    salida = tmp_path / "sin_pausas.mp4"
    codigo, res = _ejecutar(capsys, "cortar", fuente, "--quitar-silencios", "--salida", salida, "--borrador")
    assert codigo == 0, res
    # 3 s de voz + 0,1 s de aire a cada lado de cada pausa interior → 3,4 s
    assert res["tramos"] == 3
    assert abs(_sondear(salida)["duracion"] - 3.4) <= 2 / 30


def test_tramos_con_voz_fusiona_y_ajusta_a_fotogramas():
    # la pausa corta (1,0–1,15) desaparece al dar 0,1 s de aire a cada lado: los dos primeros tramos se funden
    tramos = ev.tramos_con_voz([(1.0, 1.15), (3.0, 4.0)], dur=5.0, margen=0.1, fps=30)
    assert tramos == [(0.0, 3.1), (3.9, 5.0)]
    assert all(round(x * 30, 6).is_integer() for t in tramos for x in t)


# ─────────────────────────────── subtitular ───────────────────────────────

@requiere_libass
def test_subtitular_con_srt_valido(vertical, tmp_path, capsys):
    srt = tmp_path / "v.srt"
    srt.write_text(SRT, encoding="utf-8")
    salida = tmp_path / "subs.mp4"
    codigo, res = _ejecutar(capsys, "subtitular", vertical, "--srt", srt, "--formato", "9x16", "--salida", salida,
                            "--borrador")
    assert codigo == 0, res
    info = _sondear(salida)
    assert (info["ancho"], info["alto"]) == (540, 960) and info["audio"]
    assert abs(info["duracion"] - 2.4) <= 1 / 30 + 1e-6
    assert res["subtitulos"] == 2 and res["fuente"]


@requiere_ffmpeg
def test_subtitular_srt_roto_da_codigo_1(vertical, tmp_path, capsys):
    srt = tmp_path / "roto.srt"
    srt.write_text("1\n00:00:01 --> 00:00:02\nHola\n", encoding="utf-8")
    codigo, res = _ejecutar(capsys, "subtitular", vertical, "--srt", srt, "--salida", tmp_path / "x.mp4")
    assert codigo == 1 and "tiempo no válido" in res["error"]
    assert not (tmp_path / "x.mp4").exists()


@requiere_ffmpeg
def test_subtitular_formato_equivocado_da_codigo_1(horizontal, tmp_path, capsys):
    srt = tmp_path / "v.srt"
    srt.write_text(SRT, encoding="utf-8")
    codigo, res = _ejecutar(capsys, "subtitular", horizontal, "--srt", srt, "--formato", "9x16",
                            "--salida", tmp_path / "x.mp4")
    assert codigo == 1 and "reformatear" in res["arreglo"]


def test_leer_srt_tolera_bom_crlf_etiquetas_y_avisa_de_lo_corto():
    texto = "﻿1\r\n00:00:00,000 --> 00:00:00,300\r\n<b>Hola</b>\r\n\r\n00:00:01.000 --> 00:00:02.500\r\nSegundo\r\n"
    cues, avisos = ev.leer_srt(texto)
    assert cues == [(0.0, 0.3, "Hola"), (1.0, 2.5, "Segundo")]
    assert any("0,3 s" in a for a in avisos)
    with pytest.raises(ev.ErrorUsuario):
        ev.leer_srt("1\n00:00:02,000 --> 00:00:01,000\nAl revés\n")
    with pytest.raises(ev.ErrorUsuario):
        ev.leer_srt("")


def test_subtitulos_largos_se_parten_en_pantallas_de_dos_lineas():
    marca, _, _ = ev.cargar_marca()
    fuente = ev.elegir_fuente(marca, None)
    largo = " ".join(["automatización"] * 14)
    ass, avisos = ev.construir_ass_subtitulos([(0.0, 6.0, largo)], 1080, 1920, "9x16", marca, fuente)
    dialogos = [x for x in ass.splitlines() if x.startswith("Dialogue:")]
    assert len(dialogos) >= 2 and any("partido" in a for a in avisos)
    assert all(d.count("\\N") <= 1 for d in dialogos)
    # en 9:16 el texto acaba al 62,5 % del alto: dentro del tercio central y por encima del 35 % inferior
    estilo = next(x for x in ass.splitlines() if x.startswith("Style: Subtitulo"))
    assert estilo.split(",")[-2] == str(1920 - 1200)


# ─────────────────────────────── texto-hook ───────────────────────────────

@requiere_libass
def test_texto_hook_mantiene_duracion_y_resolucion(vertical, tmp_path, capsys):
    salida = tmp_path / "hook.mp4"
    codigo, res = _ejecutar(capsys, "texto-hook", vertical, "--texto", "¿Tu CRM pierde leads mientras duermes?",
                            "--salida", salida, "--borrador")
    assert codigo == 0, res
    info = _sondear(salida)
    assert (info["ancho"], info["alto"]) == (540, 960)
    assert abs(info["duracion"] - 2.4) <= 1 / 30 + 1e-6


@requiere_ffmpeg
def test_texto_hook_vacio_es_error(vertical, tmp_path, capsys):
    codigo, _ = _ejecutar(capsys, "texto-hook", vertical, "--texto", "  ", "--salida", tmp_path / "x.mp4")
    assert codigo == 1


def test_hook_queda_dentro_de_la_zona_segura_9x16():
    marca, _, _ = ev.cargar_marca()
    fuente = ev.elegir_fuente(marca, None)
    ass, _ = ev.construir_ass_hook("¿Tu CRM pierde leads mientras duermes?", 2, 1080, 1920, "9x16", "arriba",
                                   marca, fuente)
    campos = next(x for x in ass.splitlines() if x.startswith("Style: Hook")).split(",")
    cuerpo, relleno, margen_lat, margen_v = int(campos[2]), int(campos[16]), int(campos[19]), int(campos[21])
    assert margen_v - relleno >= 269  # la caja empieza por debajo del 14 % superior
    assert margen_lat - relleno >= 65  # y respeta el 6 % lateral
    lineas = ass.strip().splitlines()[-1].split("}", 1)[1].split("\\N")
    assert len(lineas) <= 3
    assert all(ev._ancho_texto(x, cuerpo, fuente) <= 1080 - 2 * margen_lat for x in lineas)


def test_metricas_de_la_fuente_por_defecto():
    fuente = ev.elegir_fuente(ev.cargar_marca()[0], None)
    if fuente["metricas"] is None:
        pytest.skip("Sin la fuente Montserrat del producto")
    assert "Montserrat" in fuente["familia"]
    assert fuente["metricas"].ancho("MMMM", 80) > fuente["metricas"].ancho("iiii", 80) > 0


# ─────────────────────────────── marca ───────────────────────────────

def test_marca_del_cliente_aplica_colores(instancia):
    carpeta = instancia / "clientes" / "acme" / "marca"
    carpeta.mkdir(parents=True)
    (carpeta / "marca.json").write_text(json.dumps({
        "nombre": "Acme Automations",
        "colores": {"primario": "#1F6FEB", "fondo": "#0B1F3A"},
        "subtitulos": {"color": "#FFD400", "contorno": "#101010", "mayusculas": True},
    }), encoding="utf-8")
    marca, base, avisos = ev.cargar_marca(cliente="acme")
    assert base == carpeta and not avisos
    fuente = ev.elegir_fuente(marca, base)
    hook, _ = ev.construir_ass_hook("Prueba", 2, 1080, 1920, "9x16", "arriba", marca, fuente)
    estilo = next(x for x in hook.splitlines() if x.startswith("Style: Hook")).split(",")
    assert estilo[5] == "&H00EB6F1F"  # caja (OutlineColour con BorderStyle 3): primario en BGR
    assert estilo[3] == "&H00FFFFFF"  # texto blanco por contraste sobre el azul
    subs, _ = ev.construir_ass_subtitulos([(0, 1, "hola")], 1080, 1920, "9x16", marca, fuente,
                                          mayusculas=marca["subtitulos"]["mayusculas"])
    estilo = next(x for x in subs.splitlines() if x.startswith("Style: Subtitulo")).split(",")
    assert estilo[3] == "&H0000D4FF" and estilo[5] == "&H00101010"
    assert subs.strip().endswith("HOLA")


def test_cliente_sin_marca_usa_la_neutra_y_avisa(instancia):
    marca, base, avisos = ev.cargar_marca(cliente="acme")
    assert base is None and avisos and marca["colores"]["primario"] == "#FFFFFF"


def test_marca_mal_formada_es_error_del_usuario(instancia):
    carpeta = instancia / "clientes" / "acme" / "marca"
    carpeta.mkdir(parents=True)
    (carpeta / "marca.json").write_text("{ no es json", encoding="utf-8")
    with pytest.raises(ev.ErrorUsuario):
        ev.cargar_marca(cliente="acme")
    (carpeta / "marca.json").write_text(json.dumps({"colores": {"primario": "azul"}}), encoding="utf-8")
    marca, base, _ = ev.cargar_marca(cliente="acme")
    with pytest.raises(ev.ErrorUsuario):
        ev.construir_ass_hook("x", 2, 1080, 1920, "9x16", "arriba", marca, ev.elegir_fuente(marca, base))
    with pytest.raises(ev.ErrorUsuario):
        ev.cargar_marca(cliente="../fuera")


@requiere_libass
def test_texto_hook_con_cliente_de_punta_a_punta(instancia, vertical, tmp_path, capsys):
    carpeta = instancia / "clientes" / "acme" / "marca"
    carpeta.mkdir(parents=True)
    (carpeta / "marca.json").write_text(json.dumps({"colores": {"primario": "#1F6FEB"}}), encoding="utf-8")
    codigo, res = _ejecutar(capsys, "texto-hook", vertical, "--texto", "Deja de perder leads", "--cliente", "acme",
                            "--salida", tmp_path / "hook_acme.mp4", "--borrador")
    assert codigo == 0, res
    assert not any("uso la neutra" in a for a in res["avisos"])


# ─────────────────────────────── CLI y configuración ───────────────────────────────

def test_sin_ffmpeg_da_codigo_2(monkeypatch, tmp_path, capsys):
    video = tmp_path / "x.mp4"
    video.write_bytes(b"\x00")
    monkeypatch.setattr(ev.shutil, "which", lambda _nombre: None)
    codigo, res = _ejecutar(capsys, "info", video)
    assert codigo == 2 and "brew install ffmpeg" in res["arreglo"]


@requiere_ffmpeg
def test_no_sobrescribe_ni_pisa_la_entrada(horizontal, tmp_path, capsys):
    existente = tmp_path / "ya.mp4"
    existente.write_bytes(b"no tocar")
    codigo, res = _ejecutar(capsys, "cortar", horizontal, "--salida", existente)
    assert codigo == 1 and "--sobrescribir" in res["arreglo"]
    assert existente.read_bytes() == b"no tocar"
    codigo, _ = _ejecutar(capsys, "cortar", horizontal, "--salida", horizontal, "--sobrescribir")
    assert codigo == 1


def test_argumentos_invalidos_dan_codigo_1(capsys):
    assert ev.main(["reformatear", "x.mp4", "--formato", "2x3"]) == 1
    assert ev.main(["subcomando-que-no-existe"]) == 1
    capsys.readouterr()


@requiere_ffmpeg
def test_info_por_linea_de_ordenes_aislada(vertical):
    r = subprocess.run([sys.executable, "-I", str(RAIZ_PRODUCTO / "herramientas" / "editar_video.py"), "info",
                        str(vertical), "--json"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    res = json.loads(r.stdout)
    assert res["formato"] == "9x16" and res["audio"] and res["ancho"] == 540
    assert any("Resolución baja" in a for a in res["avisos"])
