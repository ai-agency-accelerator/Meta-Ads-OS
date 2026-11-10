"""Estilo Flow y POV generalizados: recetas de ejemplo válidas, errores claros y recorrido simulado (0 $)."""
from __future__ import annotations

import json

import pytest

from motor_ia_apoyo import MODULO, cargar_script, entorno_limpio

flow = cargar_script("flow_style")
pov = cargar_script("pov_broll")


def test_ejemplos_validos():
    assert flow.validate_receta(flow.load_receta(MODULO / "examples" / "flow_receta_nimbo.json")) == []
    assert pov.validate_planos(json.loads((MODULO / "examples" / "pov_planos_ejemplo.json").read_text(encoding="utf-8"))) == []


def test_receta_rota_dice_que_arreglar(tmp_path):
    r = flow.load_receta(MODULO / "examples" / "flow_receta_nimbo.json")
    r["segmentos"][0]["rol"] = "demo"
    del r["luz_en"]
    errs = flow.validate_receta(r)
    assert "falta «luz_en»" in errs
    p = tmp_path / "mala.json"
    p.write_text("{ no es json", encoding="utf-8")
    with pytest.raises(flow.RecetaError, match="no es JSON válido"):
        flow.load_receta(p)


def test_subcomando_primero_para_que_motor_guard_lo_vea():
    with pytest.raises(SystemExit):
        flow.build_parser().parse_args(["--receta", "x.json", "keyframe"])
    a = flow.build_parser().parse_args(["keyframe", "--receta", "x.json", "--simular"])
    assert a.cmd == "keyframe" and a.simular


def test_recorrido_simulado_sin_proveedores_reales(uv_motor, tmp_path):
    """Los tests rápidos del módulo (Flow/POV, plan-import, configuración) prohíben instanciar Gemini y comprueban que
    todo sale de los proveedores simulados. El de extremo a extremo va aparte (`test_motor_ia_e2e.py`)."""
    env = entorno_limpio(MOTOR_MOCK="1", META_ADS_OS_RAIZ=str(tmp_path / "os"), MOTOR_DATA_DIR=str(tmp_path / "data"))
    rapidos = [str(MODULO / "tests" / f) for f in ("test_flow_style.py", "test_plans.py", "test_config.py")]
    p = uv_motor(["python", "-m", "pytest", "-q", "-p", "no:cacheprovider", *rapidos], env, timeout=600)
    assert p.returncode == 0, p.stdout[-3000:] + p.stderr[-2000:]


def test_plan_de_ejemplo_valido():
    """`examples/plan_ejemplo_nimbo.json` cumple las reglas de `plan-import` (validación en biblioteca estándar)."""
    plan = json.loads((MODULO / "examples" / "plan_ejemplo_nimbo.json").read_text(encoding="utf-8"))["plans"][0]["plan"]
    segs = plan["segments"]
    assert segs[0]["role"] == "hook" and len(segs[0]["text"].split()) <= 9 and segs[-1]["role"] == "cta"
    assert all(len(s["text"].split()) <= 17 for s in segs)
    cortes = [s for s in plan["shots"] if s["shot_type"] != "talking_head"]
    assert len(cortes) <= 3 and all(0 not in s.get("segment_indexes", []) for s in cortes)
