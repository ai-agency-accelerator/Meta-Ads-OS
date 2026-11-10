"""Benchmark de REPRODUCCIÓN con píxeles reales (sin llamadas de pago).

Monta un anuncio con clips REALES de Omni que ya tengas en tu motor (una toma hablada de ~6 s, la misma toma extendida
a ~12 s y un plano de acción sin diálogo), pantallas REALES de la app de ejemplo de Nimbo (Playwright) y la tarjeta
CTA, y ejecuta todo lo que no necesita API: alineado ASR, montaje no destructivo, render, QA determinista (identidad,
diálogo, boca en planos mudos, congelados, loudness), regeneración de escena (comprueba que pide confirmación),
variantes baratas y exportación con costes.

Uso (ids de assets de tu `data/assets`, por ejemplo de un `motor run` anterior):
  uv run --project modulos/motor-ia --extra local python modulos/motor-ia/tests/bench_replay.py \
      --retrato <id> --toma <id> --toma-completa <id> --muda <id> --hook "…" --demo "…"
No se ejecuta con pytest (no empieza por `test_`).
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from motor import orchestrator
from motor.costs import summarize
from motor.demo import ensure_brand_product
from motor.models import Actor, Brief, Project, Route, Script, ScriptSegment, Shot
from motor.pipeline import identity
from motor.store import ctx

ACTOR = "@replay_v0"


def ensure_actor_v0(portrait_id: str) -> Actor:
    db = ctx().db
    try:
        return db.find(Actor, ACTOR)
    except KeyError:
        pass
    portrait = db.get_asset(portrait_id)
    a = Actor(handle=ACTOR, name=ACTOR.lstrip("@"), appearance="a 32-year-old Spanish woman", gender="female",
              master_portrait_id=portrait.id)
    a.identity = identity.build_profile([portrait])
    db.put(a)
    return a


def main(portrait: str, take_1: str, take_full: str, silent: str, hook_text: str, demo_text: str) -> dict:
    TAKE_1, TAKE_FULL, SILENT = take_1, take_full, silent
    t0 = time.time()
    c = ctx()
    prog = lambda f, m: print(f"{f * 100:5.1f}% {m}", flush=True)  # noqa: E731
    brand, product = ensure_brand_product(prog)
    actor = ensure_actor_v0(portrait)
    brief = Brief(brand_id=brand.id, product_id=product.id, objective="pruebas gratuitas", audience="pymes de servicios",
                  locale="es-ES", duration_s=15, platform="reels", actor_ids=[actor.id])
    p = orchestrator.create_project(brief, name="replay-real-pixels", talk_mode="native")
    hook = ScriptSegment(role="hook", text=hook_text, on_screen_text=" ".join(hook_text.split()[:5]))
    demo = ScriptSegment(role="demo", text=demo_text, on_screen_text="")
    p.script = Script(title="replay", locale="es-ES", segments=[hook, demo], cta="Pruébalo 14 días gratis")
    # fotograma de la toma real como referencia de localización (fondo de las pantallas de la app)
    from motor.media import frame_at

    kf_path = frame_at(c.assets.abspath(c.db.get_asset(TAKE_1)), 0.5, c.work("replay", p.id) / "kf.jpg", width=720)
    kf = c.assets.ingest(kf_path, source="frame:replay")
    talk1 = Shot(shot_type="talking_head", segment_ids=[hook.id], duration=6, dialogue=hook.text, keyframe_asset_id=kf.id,
                 clip_asset_id=TAKE_FULL, status="ready", constraints={"chunk_asset": TAKE_1},
                 route=Route(pipeline="talking.chain", provider="gemini", model="gemini-omni-1.1-flash", reason="clip real"))
    talk2 = Shot(shot_type="talking_head", segment_ids=[demo.id], duration=6, dialogue=demo.text, clip_asset_id=TAKE_FULL,
                 status="ready", constraints={"chunk_asset": TAKE_FULL},
                 route=Route(pipeline="talking.chain", provider="gemini", model="gemini-omni-1.1-flash", reason="clip real (extend)"))
    action = Shot(shot_type="actor_motion", segment_ids=[hook.id], duration=2.0, description="mira algo en la mesa y sonríe",
                  clip_asset_id=SILENT, status="ready",
                  route=Route(pipeline="i2v", provider="gemini", model="gemini-omni-1.1-flash", reason="clip real"))
    app1 = Shot(shot_type="app_screen", segment_ids=[demo.id], duration=2.2, description="leads de hoy", uses_product=True,
                route=Route(pipeline="compose.app_phone", provider="local", reason="pantallas reales"))
    app2 = Shot(shot_type="app_screen", segment_ids=[demo.id], duration=2.0, description="flujo de seguimiento", uses_product=True,
                route=Route(pipeline="compose.app_phone", provider="local", reason="pantallas reales"))
    card = Shot(shot_type="graphic_card", duration=2.2, route=Route(pipeline="compose.cta", provider="local", reason="CTA"))
    p.shots = [talk1, talk2, action, app1, app2, card]
    p.continuity.actor_id = actor.id
    c.db.put(p)

    # producción: solo lo que falta (pantallas de la app, locales y gratis) — los clips reales ya están «ready»
    orchestrator.produce(p, prog)
    out = orchestrator.assemble_and_render(p, prog, music=True)
    report = orchestrator.quality_check(p, out, prog, use_vlm=True)  # el juez Gemini fallará con 402 → solo determinista
    export_dir = orchestrator.export(p, out)
    p.status = "done" if report.passed else "done_with_warnings"
    c.db.put(p)

    # edición no destructiva sin coste: variantes baratas
    from motor.commands import apply

    variants = []
    for order in ("cambia el texto del hook a «¿Cuánto tardas en contestar?»", "versión 4:5", "subtítulos limpios"):
        r = apply(p.id, order)
        variants.append({"order": order, "variant": r.get("variant_id"), "render": r.get("render"), "qa": r.get("qa_passed"),
                         "cost": r["cost"]["total_usd"]})
    # regeneración de una escena con IA → sin saldo: debe quedar en pausa reanudable, sin romper nada
    try:
        regen = apply(p.id, "regenera únicamente la escena 3")
    except Exception as e:  # noqa: BLE001
        regen = {"error": f"{type(e).__name__}: {str(e)[:160]}"}
    p = c.db.get(Project, p.id)
    last = p.qa_reports[-1] if p.qa_reports else None
    res = {
        "project": p.id, "render": str(out), "export_dir": str(export_dir), "duration_s": p.timeline.duration if p.timeline else None,
        "qa_passed": report.passed, "qa_lines": [ln for ln in (last and orchestrator.judge.summary_lines(last)) or []],
        "qa_checks": {k: v for k, v in (report.checks or {}).items() if k != "freeze_black"},
        "variants": variants, "regen_scene_3": regen, "cost_master": summarize(p.id),
        "seconds": round(time.time() - t0, 1), "log_tail": p.log[-12:],
    }
    Path(export_dir, "bench_replay.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str))
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--retrato", required=True, help="asset del retrato maestro con el que se generaron los clips")
    ap.add_argument("--toma", required=True, help="toma hablada de ~6 s")
    ap.add_argument("--toma-completa", required=True, help="la misma toma extendida a ~12 s")
    ap.add_argument("--muda", required=True, help="plano de acción sin diálogo")
    ap.add_argument("--hook", required=True, help="lo que dice la primera toma (texto exacto)")
    ap.add_argument("--demo", required=True, help="lo que dice la extensión (texto exacto)")
    a = ap.parse_args()
    print(json.dumps(main(a.retrato, a.toma, a.toma_completa, a.muda, a.hook, a.demo), indent=1, ensure_ascii=False,
                     default=str))
