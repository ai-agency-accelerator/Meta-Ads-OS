"""Prueba extremo a extremo en modo simulado (sin red, coste 0): valida la integración de todos los módulos.

Usa la empresa ficticia Nimbo (SaaS B2B). Tarda 1–3 min (render real con FFmpeg): marca `lento`.
Desde la raíz: `MOTOR_MOCK=1 uv run --project modulos/motor-ia python -m pytest modulos/motor-ia/tests -q`.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path

import pytest


def _setup(tmp: Path):
    os.environ["MOTOR_MOCK"] = "1"
    os.environ["MOTOR_DATA_DIR"] = str(tmp)
    # el juez simulado cuenta como revisión SOLO aquí, e inyecta un defecto grave en la escena 2 de la primera versión:
    # así se ejecuta de verdad el bucle rechazo → regeneración selectiva → nueva versión → QA
    os.environ["MOTOR_MOCK_JUDGE"] = "1"
    os.environ["MOTOR_MOCK_DEFECTS"] = "hands@S2:critical"
    from motor import config, store
    from motor.providers import registry

    config.reset_settings()
    store.set_ctx(None)
    registry.reset()
    models = Path(__file__).resolve().parent.parent / "data" / "models"
    if models.exists():
        (tmp / "models").mkdir(parents=True, exist_ok=True)
        for sub in ("face", "tessdata", "clip"):
            if (models / sub).exists() and not (tmp / "models" / sub).exists():
                shutil.copytree(models / sub, tmp / "models" / sub)


@pytest.mark.lento
def test_e2e_mock():
    tmp = Path(tempfile.mkdtemp(prefix="motor_e2e_"))
    if not os.environ.get("MOTOR_KEEP_TMP"):
        import atexit
        import shutil

        atexit.register(shutil.rmtree, tmp, True)  # ~150 MB por ejecución: no se deja basura en $TMPDIR
    _setup(tmp)
    from motor import orchestrator
    from motor.models import Actor, BrandKit, Brief, Product
    from motor.providers.mock import MockImage
    from motor.providers.base import ImageRequest
    from motor.store import ctx

    c = ctx()
    brand = BrandKit(name="Nimbo", colors={"primary": "#2F5BEA", "accent": "#12B76A", "text": "#FFFFFF"},
                     ctas=["Pruébalo 14 días gratis"], approved_claims=["responde a cada lead nuevo en menos de 5 minutos"])
    c.db.put(brand)
    shots = MockImage().generate(ImageRequest(prompt="pantalla app", n=2))
    product = Product(brand_id=brand.id, name="Nimbo", kind="app", description="software de seguimiento automático de leads",
                      benefits=["respuesta a cada lead en minutos", "enlace de reserva automático"],
                      screenshot_asset_ids=[a.id for a in shots])
    c.db.put(product)
    portrait = MockImage().generate(ImageRequest(prompt="retrato actor"))[0]
    actor = Actor(handle="@actor_test", appearance="mujer de 29 años", master_portrait_id=portrait.id)
    c.db.put(actor)
    brief = Brief(brand_id=brand.id, product_id=product.id, objective="pruebas gratuitas", audience="pymes de servicios",
                  locale="es-ES", duration_s=20, actor_ids=[actor.id], n_angles=2)
    p = orchestrator.create_project(brief, name="e2e-mock")
    res = orchestrator.run(p.id, use_vlm=True, music=True, max_rounds=1)
    print(json.dumps(res, indent=1, ensure_ascii=False)[:1500])
    pr = c.db.get(type(p), p.id)
    first = pr.qa_reports[0]
    assert not first.passed and any(not v.passed for v in first.scenes), "el defecto inyectado debía rechazar la escena 2"
    assert any(line.startswith("REGEN") for line in pr.log), "debía regenerarse SOLO la escena rechazada"
    assert len(pr.qa_reports) >= 2 and pr.timeline.version >= 2
    print("bucle QA:", [r.verdict for r in pr.qa_reports], [ln for ln in pr.log if ln.startswith("REGEN")])
    assert Path(res["render"]).exists()
    assert (Path(res["export_dir"]) / "manifest.json").exists()
    from motor.media import probe

    info = probe(res["render"])
    kinds = {s["codec_type"] for s in info["streams"]}
    assert {"video", "audio"} <= kinds
    assert res["cost"]["total_usd"] < 0.01  # solo CPU local, ninguna llamada de pago

    # ── edición no destructiva: órdenes en lenguaje natural ──
    from motor.commands import apply

    v0 = c.db.get(type(p), p.id).timeline.version
    r = apply(p.id, "regenera únicamente la escena 2", confirm=True)
    p2 = c.db.get(type(p), p.id)
    assert r["op"]["op"] == "regen_scene" and p2.timeline.version > v0, r
    for order in ("cambia el texto del hook a «¿Cuánto tardas en contestar?»", "versión 4:5", "que diga al final «Pruébalo hoy»",
                  "hook: ¿Otro lead sin contestar?", "hazlo en inglés"):
        r = apply(p.id, order, confirm=True)
        print(order, "→", r["op"], r.get("variant_id"), r.get("qa_verdict"), r.get("estimate_usd"))
        assert Path(r["render"]).exists(), order
    parent = c.db.get(type(p), p.id)
    assert len(parent.variants) == 5
    en = c.db.get(type(p), parent.variants[-1]["id"])
    assert en.brief.locale == "en-US" and en.script.locale == "en-US"

    # una orden de pago SIN confirmar no ejecuta nada y devuelve el coste estimado
    pend = apply(p.id, "hazlo en alemán")
    assert pend["status"] == "needs_confirmation" and pend["estimate_usd"] > 0.05, pend
    # edición acumulativa: el 4:5 se conserva al cambiar después el hook de la variante 4:5
    v45 = next(v["id"] for v in parent.variants if v["kind"] == "aspect")
    r = apply(v45, "cambia el texto del hook a «Contesta antes»", confirm=True)
    assert c.db.get(type(p), r["variant_id"]).timeline.height == 1350, "la variante de la variante debía seguir en 4:5"

    # ── API interna ──
    from fastapi.testclient import TestClient

    from motor.api.server import app

    cl = TestClient(app)
    assert "Motor de anuncios" in cl.get("/").text
    assert cl.get("/api/status").status_code == 200
    d = cl.get(f"/api/projects/{p.id}").json()
    assert d["render_asset_id"] and len(d["variants"]) == 5
    assert cl.get(f"/api/assets/{d['render_asset_id']}").status_code == 200
    # seguridad: ids con path traversal y hosts ajenos se rechazan
    assert cl.get("/api/projects/..%2F..%2Fmodels/export").status_code in (400, 404)
    assert cl.get("/api/projects/proj_x/export").status_code == 400
    assert cl.get("/api/status", headers={"host": "evil.example"}).status_code == 400
    assert cl.get(f"/api/assets/{d['render_asset_id']}").headers.get("x-content-type-options") == "nosniff"


if __name__ == "__main__":
    test_e2e_mock()
