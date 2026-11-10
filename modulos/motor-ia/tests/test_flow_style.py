"""Estilo Flow y POV generalizados: validación de recetas y recorrido completo en simulado (0 $, sin red)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parent.parent
EXAMPLE = MODULE / "examples" / "flow_receta_nimbo.json"
POV = MODULE / "examples" / "pov_planos_ejemplo.json"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"_{name}", MODULE / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


flow = _load("flow_style")
pov = _load("pov_broll")


def test_la_receta_de_ejemplo_es_valida():
    assert flow.validate_receta(flow.load_receta(EXAMPLE)) == []


@pytest.mark.parametrize("cambio,mensaje", [
    (lambda r: r.pop("producto_en"), "falta «producto_en»"),
    (lambda r: r["segmentos"][0].update(rol="demo"), "primer segmento"),
    (lambda r: r["segmentos"][0].update(texto="una dos tres cuatro cinco seis siete ocho nueve diez"), "más de 9 palabras"),
    (lambda r: r["segmentos"][1].update(texto="Lo he probado y funciona"), "testimonio"),
    (lambda r: r["generaciones"]["a"]["planos"][0].update(dice=42), "no existe"),
    (lambda r: r["referencias_producto"].update(foto="no-existe.png"), "no existe no-existe.png"),
    (lambda r: r["referencias_producto"].update(mala="producto:logo:0"), "no vale"),
    (lambda r: r["generaciones"]["b"]["planos"].pop(), "no lo dice ningún plano"),
    (lambda r: r.update(nombre="Con Espacios"), "minúsculas"),
])
def test_validacion_con_mensajes_claros(cambio, mensaje):
    r = flow.load_receta(EXAMPLE)
    cambio(r)
    errs = flow.validate_receta(r)
    assert any(mensaje in e for e in errs), errs


def test_prompts_y_estimacion_sin_red():
    r = flow.load_receta(EXAMPLE)
    p = flow.gen_prompt(r, "a", 3)
    assert p.startswith("[# Sources <FIRST_FRAME>@Image1] [# References <IMAGE_REF_0>@Image2 <IMAGE_REF_1>@Image3]")
    assert "«¿Cuánto tardas en contestar a un lead nuevo?»" in p and "It starts exactly on Image1" in p
    assert "continuation" in flow.gen_prompt(r, "b", 0)
    est = flow.estimate(r)
    assert est["total"] > 0 and set(est) >= {"keyframe", "gen_a", "gen_b", "stills", "animate:escritorio"}


def test_pov_ejemplo_valido_y_detecta_personas():
    assert pov.validate_planos(json.loads(POV.read_text(encoding="utf-8"))) == []
    malo = {"nombre": "x-y", "planos": {"p": {"segundos": 5, "fotograma_en": "a woman smiling", "movimiento_en": "walks"}}}
    assert any("personas" in e for e in pov.validate_planos(malo))


def _main(mod, *args, capsys) -> dict:
    assert mod.main(list(args)) == 0
    return json.loads(capsys.readouterr().out)


def test_flow_completo_en_simulado(motor_simulado, capsys):
    from motor.costs import summarize
    from motor.models import Actor, BrandKit, Product
    from motor.providers.base import ImageRequest
    from motor.providers.mock import MockImage
    from motor.store import ctx

    c = ctx()
    brand = BrandKit(name="Nimbo", ctas=["Pruébalo 14 días gratis"])
    c.db.put(brand)
    shot = MockImage().generate(ImageRequest(prompt="pantalla de Nimbo"))[0]
    product = Product(brand_id=brand.id, name="Nimbo", kind="app", screenshot_asset_ids=[shot.id])
    c.db.put(product)
    portrait = MockImage().generate(ImageRequest(prompt="retrato"))[0]
    c.db.put(Actor(handle="@presentadora_01", appearance="mujer de 32 años", master_portrait_id=portrait.id))
    receta = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    receta.update(marca_id=brand.id, producto_id=product.id)
    rp = motor_simulado / "receta.json"
    rp.write_text(json.dumps(receta), encoding="utf-8")

    assert _main(flow, "validar", "--receta", str(rp), capsys=capsys)["valida"] is True
    assert _main(flow, "plan", "--receta", str(rp), capsys=capsys)["coste_estimado_usd"]["total"] > 0
    assert _main(flow, "setup", "--receta", str(rp), capsys=capsys)["proyecto"].startswith("proj_")
    kf = _main(flow, "keyframe", "--receta", str(rp), "--n", "2", capsys=capsys)
    assert kf["simulado"] is True and len(kf["fotogramas"]) == 2
    a = _main(flow, "gen_a", "--receta", str(rp), kf["fotogramas"][0], capsys=capsys)["toma"]
    b = _main(flow, "gen_b", "--receta", str(rp), a, capsys=capsys)["toma"]
    st = _main(flow, "stills", "--receta", str(rp), "--n", "1", capsys=capsys)
    clip = _main(flow, "animate", "--receta", str(rp), "escritorio", st["escritorio"][0], capsys=capsys)["clip"]
    for aid in (a, b, clip, *kf["fotogramas"]):
        assert c.db.get_asset(aid).source.startswith("mock:")
    state = json.loads((c.settings.work_dir / "flow" / "nimbo-escritorio" / "state.json").read_text(encoding="utf-8"))
    assert state["gen_a"] == [a] and state["gen_b"] == [b] and state["refs"]["panel"] == shot.id
    chk = _main(flow, "check", "--receta", str(rp), a, capsys=capsys)
    assert "dur" in chk
    assert summarize()["total_usd"] < 0.01

    pv = _main(pov, "keyframe", "--planos", str(POV), "llegada", "--n", "1", capsys=capsys)
    vid = _main(pov, "gen", "--planos", str(POV), "llegada", pv["fotogramas"][0], capsys=capsys)
    assert pv["simulado"] and c.db.get_asset(vid["video"]).source.startswith("mock:")
    assert _main(pov, "list", "--planos", str(POV), capsys=capsys)["llegada"]["videos"] == [vid["video"]]


def test_el_subcomando_va_primero():
    """`motor_guard` reconoce `flow_style.py <subcomando>`: con la receta antes del subcomando, argparse se niega."""
    with pytest.raises(SystemExit):
        flow.build_parser().parse_args(["--receta", "x.json", "keyframe"])
