"""`ck anuncio` de punta a punta con un bruto sintético de FFmpeg: 9:16 y 4:5 válidos para Meta, sin red ni gasto.

Necesita FFmpeg con libass y libx264 (si falta, se salta y dice qué instalar). Tarda unos 20–30 s.
"""
from __future__ import annotations

import json
import shutil

import pytest

from cutkit_apoyo import RAIZ_PRODUCTO, bruto_sintetico, entorno_limpio, ffmpeg_con, marca_acme, sondear


@pytest.fixture(scope="module")
def bruto(tmp_path_factory):
    """Un solo bruto para todo el módulo (generarlo cuesta más que los tests de error)."""
    motivo = ffmpeg_con("libass", "libx264")
    if motivo:
        pytest.skip(motivo)
    return bruto_sintetico(tmp_path_factory.mktemp("grabaciones"))


@pytest.fixture
def instancia_video(tmp_path, bruto):
    raiz = tmp_path / "os"
    marca_acme(raiz)
    plantilla = RAIZ_PRODUCTO / ".claude" / "skills" / "producir-video" / "plantilla-leeme.md"
    if plantilla.exists():                                  # el LEEME nuevo sale de la plantilla del producto
        destino = raiz / ".claude" / "skills" / "producir-video" / "plantilla-leeme.md"
        destino.parent.mkdir(parents=True)
        shutil.copy2(plantilla, destino)
    env = entorno_limpio(META_ADS_OS_RAIZ=str(raiz), CUTKIT_DATOS=str(tmp_path / "datos"))
    return raiz, bruto, env


def test_anuncio_9x16_y_4x5_listos_para_meta(uv_cutkit, instancia_video):
    raiz, bruto, env = instancia_video
    p = uv_cutkit(["ck", "anuncio", str(bruto), "--slug", "demo-crm", "--cliente", "acme",
                   "--hook", "¿Tu CRM pierde leads cada semana?", "--etiqueta-ia", "--fecha", "2026-11-09", "--json"],
                  env, timeout=600)
    assert p.returncode == 0, p.stderr[-3000:]
    res = json.loads(p.stdout)
    assert res["veredicto"] == "pass", res["qa"]
    proyecto = raiz / "clientes" / "acme" / "creativos" / "2026-11-09_demo-crm"
    assert res["proyecto"] == str(proyecto) and res["marca"] == "Acme Automations" and res["cta"] == "Pide tu demo"
    assert res["subtitulos"] == "bruto.srt" and res["silencios_quitados_s"] > 0.5

    esperado = {"9x16": (1080, 1920), "4x5": (1080, 1350)}
    for fmt, (w, h) in esperado.items():
        info = sondear(proyecto / f"demo-crm_{fmt}.mp4")
        v = next(s for s in info["streams"] if s["codec_type"] == "video")
        a = next(s for s in info["streams"] if s["codec_type"] == "audio")
        assert (v["width"], v["height"], v["codec_name"], v["pix_fmt"]) == (w, h, "h264", "yuv420p")
        assert (a["codec_name"], a["sample_rate"]) == ("aac", "48000")
        assert 4.0 < float(info["format"]["duration"]) < 6.5            # sin los silencios del bruto
    q = {x["formato"]: x for x in res["qa"]}
    assert set(q) == set(esperado) and all(x["issues"] == [] for x in q.values())
    assert all(abs(x["lufs"] + 14) <= 1.5 for x in q.values())
    hook = next(c for c in q["9x16"]["cajas"] if c["tipo"] == "hook")
    assert hook["t0"] == 0 and hook["lineas"] == 2

    assert (proyecto / "brutos" / "bruto.mp4").exists()                  # el bruto queda junto al proyecto
    srt = (proyecto / "demo-crm.srt").read_text(encoding="utf-8")
    assert "-->" in srt and "Acme" in srt
    leeme = (proyecto / "LEEME.md").read_text(encoding="utf-8")
    assert "<!-- cutkit:qa -->" in leeme and "1080×1920" in leeme and "−14,0 LUFS" in leeme
    # contrato de piezas: las dos líneas de formato fijo, la vía y una fila por formato
    assert "- **Estado:** borrador" in leeme and "- **Veredicto de políticas:** pendiente" in leeme
    assert "**Vía:** hibrido" in leeme and "**Cliente:** acme" in leeme
    assert "| demo-crm_9x16.mp4 | demo-crm | 9:16 | Reels, Stories |" in leeme
    assert "| demo-crm_4x5.mp4 | demo-crm | 4:5 | Feed |" in leeme and "| <nombre-base>_" not in leeme
    (proyecto / "LEEME.md").write_text(leeme.replace("Pendiente antes de publicar:", "Pendiente antes de publicar: "
                                                     "nota a mano"), encoding="utf-8")
    assert json.loads((proyecto / "qa_anuncio.json").read_text(encoding="utf-8"))["veredicto"] == "pass"

    # repetir el montaje actualiza el bloque de QA del LEEME, no lo duplica
    p2 = uv_cutkit(["ck", "anuncio", str(bruto), "--slug", "demo-crm", "--cliente", "acme", "--formatos", "9x16",
                    "--subtitulos", "no", "--json"], env, timeout=600)
    assert p2.returncode == 0, p2.stderr[-3000:]
    leeme2 = (proyecto / "LEEME.md").read_text(encoding="utf-8")
    assert leeme2.count("<!-- cutkit:qa -->") == 1 and "nota a mano" in leeme2


@pytest.mark.parametrize("args, codigo, mensaje", [
    (["/no/existe.mp4", "--slug", "demo", "--cliente", "acme"], 1, "no existe"),
    (["{bruto}", "--slug", "Demo Mal", "--cliente", "acme"], 1, "slug"),
    (["{bruto}", "--slug", "demo", "--cliente", "nimbo"], 1, "nimbo"),
    (["{bruto}", "--slug", "demo", "--cliente", "acme", "--formatos", "16x9"], 1, "16x9"),
    (["{bruto}", "--slug", "demo", "--cliente", "acme", "--perfil", "no-existe"], 1, "perfil"),
])
def test_errores_del_usuario_salen_con_codigo_1(uv_cutkit, instancia_video, args, codigo, mensaje):
    raiz, bruto, env = instancia_video
    p = uv_cutkit(["ck", "anuncio", *[a.replace("{bruto}", str(bruto)) for a in args]], env, timeout=300)
    assert p.returncode == codigo, (p.stdout[-1500:], p.stderr[-1500:])
    assert mensaje in (p.stdout + p.stderr)
    assert "Traceback" not in p.stderr
