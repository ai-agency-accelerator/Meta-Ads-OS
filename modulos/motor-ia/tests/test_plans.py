"""Planes del estudio creativo → proyectos del motor (`motor plan-import`), en simulado: 0 $, sin red ni FFmpeg."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parent.parent
PLAN = MODULE / "examples" / "plan_ejemplo_nimbo.json"


def _plan() -> dict:
    return json.loads(PLAN.read_text(encoding="utf-8"))["plans"][0]["plan"]


def test_el_plan_de_ejemplo_cumple_las_reglas():
    from motor.plans import validate

    assert validate(_plan()) == []


@pytest.mark.parametrize("cambio,aviso", [
    (lambda p: p["segments"].pop(0), "primer segmento"),
    (lambda p: p["segments"][0].update(text="una dos tres cuatro cinco seis siete ocho nueve diez once"), "hook de 11"),
    (lambda p: p["segments"][2].update(text="Lo he probado y me ha cambiado la semana"), "testimonio"),
    (lambda p: p["shots"].extend([{"shot_type": "broll", "segment_indexes": [2]}] * 3), "planos de corte"),
])
def test_avisos_del_plan(cambio, aviso):
    from motor.plans import validate

    p = copy.deepcopy(_plan())
    cambio(p)
    assert any(aviso in v for v in validate(p)), validate(p)


def _entidades():
    from motor.models import Actor, BrandKit, Product
    from motor.providers.base import ImageRequest
    from motor.providers.mock import MockImage
    from motor.store import ctx

    db = ctx().db
    brand = BrandKit(name="Nimbo", ctas=["Pruébalo 14 días gratis"],
                     approved_claims=["responde a cada lead nuevo en menos de 5 minutos"])
    db.put(brand)
    shot = MockImage().generate(ImageRequest(prompt="pantalla de Nimbo"))[0]
    product = Product(brand_id=brand.id, name="Nimbo", kind="app", screenshot_asset_ids=[shot.id])
    db.put(product)
    portrait = MockImage().generate(ImageRequest(prompt="retrato"))[0]
    db.put(Actor(handle="@presentadora_01", appearance="mujer de 32 años", master_portrait_id=portrait.id))
    return brand, product


def test_importar_plan_crea_el_proyecto(motor_simulado):
    from motor.plans import import_file

    brand, product = _entidades()
    (p,) = import_file(PLAN, brand.id, product.id, "@presentadora_01", duration_s=20, locale="es-ES")
    tipos = [s.shot_type for s in p.shots]
    assert tipos[-1] == "graphic_card" and "app_screen" in tipos
    hook_id = p.script.segments[0].id
    cortes = [s for s in p.shots if s.shot_type == "app_screen"]
    assert all(hook_id not in s.segment_ids for s in cortes)  # un corte nunca tapa el hook
    habladas = [sid for s in p.shots if s.shot_type == "talking_head" for sid in s.segment_ids]
    assert sorted(habladas) == sorted(sg.id for sg in p.script.segments)  # ninguna frase se pierde
    assert p.brief.platform == "reels" and p.variant_spec["estimated_cost_usd"] > 0


def test_importar_con_ids_inexistentes_explica_que_falta(motor_simulado):
    from motor.plans import import_file

    brand, _product = _entidades()
    with pytest.raises(ValueError, match=r"producto «prod_x».*product list.*actor «@nadie»"):
        import_file(PLAN, brand.id, "prod_x", "@nadie")
