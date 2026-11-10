import json
import pathlib
import subprocess

import pytest

import transcribir as tr

VTT = """WEBVTT
Kind: captions
Language: es

00:00:00.000 --> 00:00:02.000
<c>¿Pierdes</c> 10 horas a la semana

00:00:01.500 --> 00:00:03.000
¿Pierdes 10 horas a la semana

2
00:00:03.000 --> 00:00:05.000
respondiendo <00:00:03.500>emails?
"""


def test_limpiar_vtt():
    assert tr.limpiar_vtt(VTT) == "¿Pierdes 10 horas a la semana respondiendo emails?"


def test_tramos_vtt_con_tiempos():
    tramos = tr.tramos_vtt(VTT)
    assert [(x["inicio"], x["texto"]) for x in tramos] == [(0.0, "¿Pierdes 10 horas a la semana"),
                                                          (3.0, "respondiendo emails?")]
    assert " ".join(x["texto"] for x in tramos) == tr.limpiar_vtt(VTT)
    assert tr.texto_con_tiempos(tramos) == "[00:00] ¿Pierdes 10 horas a la semana\n[00:03] respondiendo emails?"
    assert tr.srt(tramos).startswith("1\n00:00:00,000 --> 00:00:02,000\n¿Pierdes")
    assert tr._marca(3725.5) == "1:02:05" and tr._marca(3725.5, srt=True) == "01:02:05,500"


def test_elegir_subtitulo():
    archivos = [pathlib.Path(n) for n in ("v.en.vtt", "v.es-orig.vtt", "v.es.vtt")]
    assert tr.elegir_subtitulo(archivos, ["es", "en"]) == (pathlib.Path("v.es.vtt"), "es")
    assert tr.elegir_subtitulo(archivos, ["fr", "en"]) == (pathlib.Path("v.en.vtt"), "en")
    assert tr.elegir_subtitulo([pathlib.Path("v.de.vtt")], ["es"]) == (pathlib.Path("v.de.vtt"), "?")
    assert tr.elegir_subtitulo([], ["es"]) is None


@pytest.mark.parametrize("url,esperado", [
    ("https://www.youtube.com/watch?v=abc123XYZ_-&t=10", "abc123XYZ_-"),
    ("https://www.instagram.com/reel/C0dEfGh/", "C0dEfGh"), ("https://example.com", "video"),
])
def test_identificador(url, esperado):
    assert tr.identificador(url) == esperado


def test_orden_ytdlp(monkeypatch):
    disponibles = {"uv"}
    monkeypatch.setattr(tr.shutil, "which", lambda x: x if x in disponibles else None)
    assert tr.orden_ytdlp() == ["uv", "tool", "run", "yt-dlp"]
    disponibles.add("uvx")
    assert tr.orden_ytdlp() == ["uvx", "yt-dlp"]
    disponibles.add("yt-dlp")
    assert tr.orden_ytdlp() == ["yt-dlp"]
    disponibles.clear()
    assert tr.orden_ytdlp() is None


@pytest.fixture
def ytdlp(monkeypatch):
    """yt-dlp simulado: escribe los subtítulos que toquen en la carpeta de -o."""
    estado = {"subs": {"v.es.vtt": VTT}, "orden": None}

    def run(cmd, **kw):
        estado["orden"] = cmd
        destino = pathlib.Path(cmd[cmd.index("-o") + 1]).parent
        for nombre, texto in estado["subs"].items():
            (destino / nombre).write_text(texto, encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0, "", "ERROR: no subtitles" if not estado["subs"] else "")

    monkeypatch.setattr(tr, "orden_ytdlp", lambda: ["yt-dlp"])
    monkeypatch.setattr(tr.subprocess, "run", run)
    return estado


def test_main_con_cliente(instancia, ytdlp, capsys):
    url = "https://www.youtube.com/watch?v=abc123"
    assert tr.main([url, "--cliente", "acme", "--json"]) == 0
    r = json.loads(capsys.readouterr().out)
    assert r["idioma"] == "es" and r["texto"].startswith("¿Pierdes")
    destino = pathlib.Path(r["guardado"])
    assert destino.parent == instancia / "clientes" / "acme" / "investigacion" / "transcripciones"
    assert destino.name.endswith("_abc123.txt") and destino.read_text(encoding="utf-8").startswith(f"# {url}")
    orden = ytdlp["orden"]
    assert "--skip-download" in orden and orden[-2:] == ["--", url] and orden[orden.index("--sub-langs") + 1] == "es,en"


def test_main_salida_y_texto(instancia, ytdlp, tmp_path, capsys):
    assert tr.main(["https://example.com/v/1", "--salida", str(tmp_path / "t.txt")]) == 0
    assert capsys.readouterr().out.strip().endswith("emails?") and (tmp_path / "t.txt").exists()


def test_main_con_tiempos(instancia, ytdlp, capsys):
    assert tr.main(["https://www.youtube.com/watch?v=abc123", "--cliente", "acme", "--tiempos", "--json"]) == 0
    r = json.loads(capsys.readouterr().out)
    txt, srt = pathlib.Path(r["guardado"]), pathlib.Path(r["guardado_srt"])
    assert srt == txt.with_suffix(".srt") and "00:00:03,000 --> 00:00:05,000" in srt.read_text(encoding="utf-8")
    assert "[00:03] respondiendo emails?" in txt.read_text(encoding="utf-8") and len(r["tramos"]) == 2
    assert tr.main(["https://example.com/v/1", "--tiempos"]) == 0
    assert capsys.readouterr().out.startswith("[00:00] ¿Pierdes")
    assert tr.main(["https://example.com/v/1", "--json"]) == 0
    assert "tramos" not in json.loads(capsys.readouterr().out)  # sin --tiempos, la salida de siempre


def test_main_errores(instancia, ytdlp, monkeypatch, capsys):
    assert tr.main(["www.youtube.com/watch?v=x"]) == 1
    assert tr.main(["https://x.example/v", "--idiomas", "es;rm -rf"]) == 1
    assert tr.main(["https://x.example/v", "--cliente", "nadie"]) == 2
    ytdlp["subs"] = {}
    assert tr.main(["https://x.example/v"]) == 1
    assert "Sin subtítulos" in capsys.readouterr().err
    monkeypatch.setattr(tr, "orden_ytdlp", lambda: None)
    assert tr.main(["https://x.example/v"]) == 2
    assert "uv tool install yt-dlp" in capsys.readouterr().err

    def lento(cmd, **kw):
        raise subprocess.TimeoutExpired(cmd, 300)
    monkeypatch.setattr(tr, "orden_ytdlp", lambda: ["yt-dlp"])
    monkeypatch.setattr(tr.subprocess, "run", lento)
    assert tr.main(["https://x.example/v"]) == 1
