"""Piezas del montaje directo `ck anuncio` (perfil, subtítulos, silencios, maquetación y zona segura de Meta).

Se ejecutan con el Python de cutkit (NumPy, Pillow y PyYAML); no necesitan FFmpeg ni red.
"""
from __future__ import annotations

import pytest

from cutkit_apoyo import SRT_BRUTO


def test_perfil_anuncio_formatos_y_zonas_de_meta(py_cutkit):
    r = py_cutkit("""
        from cutkit.anuncio import _perfil
        q = _perfil("anuncio")["anuncio"]
        salida({f: {k: q["formatos"][f][k] for k in ("width", "height", "zona_segura")} for f in q["formatos"]}
               | {"hook": q["hook"], "formatos_lista": list(q["formatos"])})
    """)
    assert r["formatos_lista"] == ["9x16", "4x5"]
    assert (r["9x16"]["width"], r["9x16"]["height"], r["4x5"]["width"], r["4x5"]["height"]) == (1080, 1920, 1080, 1350)
    z = r["9x16"]["zona_segura"]
    # 14 % arriba, 35 % abajo y 6 % a los lados [OFFICIAL META]; franja de botones a la derecha en Reels
    assert (z["top"], z["bottom"], z["left"], z["right"]) == (269, 672, 65, 65)
    assert z["franja_derecha"]["desde_y"] >= 1100 and z["franja_derecha"]["x"] <= 1080 - 65
    assert r["hook"]["inicio_max"] <= 2.0


def test_perfil_inexistente_dice_cuales_hay(py_cutkit):
    r = py_cutkit("""
        from cutkit.anuncio import ErrorUsuario, _perfil
        try:
            _perfil("no-existe")
        except ErrorUsuario as e:
            salida(str(e))
    """)
    assert "anuncio" in r and "no existe" in r


def test_srt_a_palabras_con_tiempos(py_cutkit, tmp_path):
    f = tmp_path / "bruto.srt"
    f.write_text("﻿" + SRT_BRUTO.replace("\n", "\r\n"), encoding="utf-8")   # BOM y CRLF de Windows
    r = py_cutkit(f"""
        from pathlib import Path
        from cutkit.anuncio import leer_srt
        salida(leer_srt(Path({str(f)!r})))
    """)
    assert [w["text"] for w in r[:3]] == ["¿Tu", "CRM", "pierde"]
    assert r[0]["s"] == 0.3 and abs(r[3]["e"] - 1.6) < 0.01                 # la última palabra del cue acaba con él
    assert all(a["e"] <= b["s"] + 1e-6 for a, b in zip(r, r[1:]))
    assert r[-1]["text"] == "recupera." and abs(r[-1]["e"] - 5.6) < 0.01


@pytest.mark.parametrize("srt, mensaje", [
    ("1\nhola\n", "línea de tiempos"),
    ("1\n00:00:02,000 --> 00:00:01,000\nhola\n", "acaba antes de empezar"),
    ("1\n00:00:01,000 --> 00:00:02,000\n\n", "no tiene subtítulos"),
])
def test_srt_mal_formado(py_cutkit, tmp_path, srt, mensaje):
    f = tmp_path / "malo.srt"
    f.write_text(srt, encoding="utf-8")
    r = py_cutkit(f"""
        from pathlib import Path
        from cutkit.anuncio import ErrorUsuario, leer_srt
        try:
            leer_srt(Path({str(f)!r})); salida("sin error")
        except ErrorUsuario as e:
            salida(str(e))
    """)
    assert mensaje in r


def test_json_de_palabras_de_whisper(py_cutkit, tmp_path):
    f = tmp_path / "palabras.json"
    f.write_text('{"words": [{"word": " mundo", "start": 0.6, "end": 0.6}, {"text": "Hola", "s": 0.1, "e": 0.5}]}',
                 encoding="utf-8")
    r = py_cutkit(f"""
        from pathlib import Path
        from cutkit.anuncio import leer_palabras_json
        salida(leer_palabras_json(Path({str(f)!r})))
    """)
    assert [w["text"] for w in r] == ["Hola", "mundo"] and r[1]["e"] > r[1]["s"]     # ordenadas y sin duración 0


def test_silencios_y_tiempo_de_programa(py_cutkit):
    r = py_cutkit("""
        import numpy as np
        from cutkit.anuncio import SR, a_programa, tramos_con_voz
        t = np.arange(int(SR * 6)) / SR
        voz = ((t > 0.5) & (t < 2.0)) | ((t > 3.0) & (t < 3.2)) | ((t > 3.4) & (t < 5.0))
        y = (0.3 * np.sin(2 * np.pi * 220 * t) * voz + 0.0005 * np.random.default_rng(1).standard_normal(len(t)))
        tr = tramos_con_voz(y.astype("float32"), -35, 0.35, 0.08)
        salida({"tramos": tr, "p": [a_programa(x, tr) for x in (0.0, 0.6, 2.5, 3.5)]})
    """)
    tr = r["tramos"]
    # el silencio inicial (0,5 s) y el de 2,0–3,0 se quitan; la pausa de 0,2 s (< 0,35 s) se respeta
    assert len(tr) == 2
    assert abs(tr[0][0] - 0.42) < 0.03 and abs(tr[0][1] - 2.08) < 0.03
    assert abs(tr[1][0] - 2.92) < 0.03 and abs(tr[1][1] - 5.08) < 0.03
    assert r["p"][0] is None and r["p"][2] is None                          # caen en silencios quitados
    assert abs(r["p"][1] - 0.18) < 0.03 and abs(r["p"][3] - (tr[0][1] - tr[0][0] + 0.58)) < 0.03


def test_paginas_de_subtitulos_cortas(py_cutkit, tmp_path):
    f = tmp_path / "bruto.srt"
    f.write_text(SRT_BRUTO, encoding="utf-8")
    r = py_cutkit(f"""
        from pathlib import Path
        from cutkit.anuncio import leer_srt, paginas
        salida(paginas(leer_srt(Path({str(f)!r})), 6.0))
    """)
    assert r and all(1 <= len(p["palabras"]) <= 3 for p in r)
    assert all(p["t1"] > p["t0"] for p in r) and all(a["t1"] <= b["t0"] + 1e-6 for a, b in zip(r, r[1:]))
    assert " ".join(w["text"] for p in r for w in p["palabras"]).startswith("¿Tu CRM pierde leads cada semana?")


def test_hook_en_lineas_equilibradas(py_cutkit):
    r = py_cutkit("""
        from cutkit.anuncio import _Medidor, _ajustar
        from cutkit.paths import FUENTES
        med = _Medidor(FUENTES / "Montserrat-ExtraBold.ttf")
        out = {}
        for k, texto in enumerate(("¿Tu CRM pierde leads cada semana?", "Corto",
                                   "Automatiza el seguimiento de cada lead sin contratar a nadie más este mismo "
                                   "trimestre", "Automatiza el seguimiento de cada lead sin contratar a nadie más "
                                   "este trimestre y deja de perder oportunidades por contestar tarde")):
            size, lineas = _ajustar(med, texto, 96, 62, 950 - 36, 3)
            out[k] = {"size": size, "lineas": lineas, "anchos": [med.ancho(x, size) for x in lineas]}
        salida(out)
    """)
    h = r["0"]
    assert h["size"] == 96 and len(h["lineas"]) == 2
    assert min(h["anchos"]) / max(h["anchos"]) > 0.6                         # nada de una palabra suelta abajo
    assert r["1"]["lineas"] == ["Corto"]
    largo = r["2"]                                                            # no cabe en 3 líneas a 96: baja el cuerpo
    assert len(largo["lineas"]) == 3 and max(largo["anchos"]) <= 950 - 36 and 62 <= largo["size"] < 96
    assert min(largo["anchos"]) / max(largo["anchos"]) > 0.6
    # demasiado largo incluso al mínimo: se queda en el mínimo y la QA avisa (hook.texto_largo)
    assert r["3"]["size"] == 62 and len(r["3"]["lineas"]) > 3


@pytest.mark.parametrize("fmt", ["9x16", "4x5"])
def test_maquetacion_dentro_de_la_zona_segura(py_cutkit, fmt):
    """Hook, subtítulos, CTA y etiqueta de IA largos, en mayúsculas: ninguna caja pisa la interfaz de Meta."""
    r = py_cutkit(f"""
        from cutkit.anuncio import _fuera_de_zona, _perfil, maquetar
        from cutkit.marca import cargar
        q = _perfil("anuncio")["anuncio"]
        cfg = dict(q["formatos"]["{fmt}"], _hook=q["hook"], _cta=q["cta"])
        pags = [{{"palabras": [{{"text": "AUTOMATIZACIONES", "s": 0.2, "e": 0.9}}, {{"text": "INMEDIATAS", "s": 0.9,
                 "e": 1.6}}], "t0": 0.2, "t1": 1.6}}]
        ass, cajas = maquetar("{fmt}", cfg, cargar(), "¿Cuántos leads pierdes cada semana por contestar tarde?",
                              "Reserva tu llamada de diagnóstico gratis", pags, 12.0, "Contenido generado con IA", True)
        salida({{"ass": ass, "cajas": cajas, "fuera": [_fuera_de_zona(c["caja"], cfg["zona_segura"], cfg["width"],
                cfg["height"]) for c in cajas]}})
    """)
    assert {c["tipo"] for c in r["cajas"]} == {"hook", "subtitulo", "cta", "etiqueta_ia"}
    assert r["fuera"] == [{}] * len(r["cajas"]), r["cajas"]
    hook = next(c for c in r["cajas"] if c["tipo"] == "hook")
    assert hook["t0"] == 0 and hook["t1"] <= 2.5
    # el estilo usa la familia del name ID 1 (si no, libass cae en otra fuente del sistema)
    assert "Style: Hook,Montserrat ExtraBold," in r["ass"] and "Style: Ia,Montserrat SemiBold," in r["ass"]


def test_numeros_en_espanol(py_cutkit):
    r = py_cutkit("""
        from cutkit.anuncio import _n
        salida([_n(-14.0), _n(9.25, 2), _n(2.7)])
    """)
    assert r == ["−14,0", "9,25", "2,7"]


def test_brutos_no_se_pisan_ni_se_confunden(py_cutkit, tmp_path):
    a, b = tmp_path / "dia1" / "toma.mp4", tmp_path / "dia2" / "toma.mp4"
    for f, contenido in ((a, b"primera toma"), (b, b"segunda toma, distinta")):
        f.parent.mkdir()
        f.write_bytes(contenido)
    proyecto = tmp_path / "proyecto"
    r = py_cutkit(f"""
        from pathlib import Path
        from cutkit.anuncio import _guardar_bruto
        p = Path({str(proyecto)!r})
        uno = _guardar_bruto(Path({str(a)!r}), p)
        otra_vez = _guardar_bruto(Path({str(a)!r}), p)
        dos = _guardar_bruto(Path({str(b)!r}), p)
        dentro = _guardar_bruto(uno, p)
        salida([str(x.relative_to(p.resolve())) for x in (uno, otra_vez, dos, dentro)] + [dos.read_bytes().decode()])
    """)
    assert r == ["brutos/toma.mp4", "brutos/toma.mp4", "brutos/toma-2.mp4", "brutos/toma.mp4", "segunda toma, distinta"]


def test_leeme_sin_plantilla_cumple_el_contrato(py_cutkit, tmp_path):
    """Fuera del producto (sin la plantilla de `producir-video`), el LEEME nuevo lleva igualmente Estado y Veredicto."""
    r = py_cutkit("""
        from pathlib import Path
        from cutkit.anuncio import Opciones, PLANTILLA_LEEME, _leeme_nuevo
        op = Opciones(entrada=Path("x.mp4"), slug="demo", cliente="acme", hook="¿Hola?")
        res = {"veredicto": "warn", "archivos": ["/p/demo_9x16.mp4", "/p/demo.srt"]}
        salida({"hay_plantilla": PLANTILLA_LEEME.exists(), "txt": _leeme_nuevo("demo", res, op, "<!-- cutkit:qa -->")})
    """, META_ADS_OS_RAIZ=str(tmp_path))
    assert not r["hay_plantilla"]
    txt = r["txt"]
    assert "- **Estado:** borrador" in txt and "- **Veredicto de políticas:** pendiente" in txt
    assert "| demo_9x16.mp4 | demo | 9:16 | Reels, Stories | «¿Hola?» |" in txt and "demo.srt |" not in txt
