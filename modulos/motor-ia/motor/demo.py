"""Prueba de referencia del motor (benchmark principal) con la empresa ficticia Nimbo (SaaS B2B).

Crea (o reutiliza) la marca, el producto con capturas REALES de una app web de ejemplo (`examples/nimbo_app/`), una
presentadora persistente, y produce un anuncio UGC de ~24 s en castellano: varias escenas, misma persona, diálogo con
lip-sync nativo, cambios de plano, B-roll, app real en el móvil, voz, subtítulos y CTA; después crea variantes baratas.

Es una ORDEN DE PAGO (≈4–6 $ con precios de 2026-10): `motor demo` pide confirmación al hook `motor_guard`.
Con `MOTOR_MOCK=1` recorre el mismo camino sin gastar.
"""

from __future__ import annotations

import time
from typing import Any, Callable

from .config import MODULE_ROOT
from .costs import summarize
from .models import Actor, BrandKit, Brief, Product
from .store import ctx

APP_FILE = MODULE_ROOT / "examples" / "nimbo_app" / "index.html"
BENCH_NAME = "benchmark-nimbo-es"

PRESENTADORA = dict(
    handle="@presentadora_01",
    appearance=("a 32-year-old Spanish woman with an ordinary, friendly face (not a model), light olive skin with visible "
                "pores and a few tiny freckles, shoulder-length straight dark brown hair tucked behind one ear, light natural "
                "makeup, average build"),
    persona="cercana, práctica y directa; habla rápido y natural, como a una compañera de trabajo",
    wardrobe="a plain navy crew-neck sweater",
    voice_hint="warm, confident 32-year-old woman from Spain, natural fast-paced delivery",
    location="a small, real home office: white desk with a laptop, a plant and a mug, soft daylight from a side window",
)


def ensure_brand_product(progress: Callable[[float, str], None]) -> tuple[BrandKit, Product]:
    c = ctx()
    brand = next((b for b in c.db.list(BrandKit) if b.name == "Nimbo"), None)
    if not brand:
        brand = BrandKit(name="Nimbo", colors={"primary": "#2F5BEA", "accent": "#12B76A", "text": "#FFFFFF"},
                         tone="cercano, práctico y concreto; nada corporativo",
                         ctas=["Pruébalo 14 días gratis"],
                         approved_claims=["responde a cada lead nuevo en menos de 5 minutos",
                                          "envía el enlace de reserva sin que nadie lo haga a mano",
                                          "avisa al comercial cuando hay una cita confirmada"],
                         dont_rules=["no prometer un número de clientes ni de ventas",
                                     "no inventar integraciones que no aparecen en la app"],
                         locales=["es-ES"], ai_label_policy="visible")
        c.db.put(brand)
    product = next((p for p in c.db.list(Product) if p.brand_id == brand.id and p.name == "Nimbo"), None)
    if not product:
        from .pipeline.product import capture_url

        progress(0.01, "Capturando pantallas REALES de la app de ejemplo (Playwright)")
        shots = [capture_url(f"{APP_FILE.as_uri()}?s={s}", wait_ms=300).id for s in ("home", "flujo", "informe")]
        product = Product(brand_id=brand.id, name="Nimbo", kind="app",
                          description="software que contesta y hace el seguimiento de los leads nuevos de forma automática",
                          benefits=["cada lead recibe respuesta en minutos, también de noche",
                                    "el enlace de reserva sale solo", "el comercial solo ve las citas confirmadas"],
                          proof_points=["panel con los leads del día y su estado", "resumen semanal de leads y citas"],
                          objections=["ya lo hacemos a mano", "configurarlo nos llevará semanas"],
                          screenshot_asset_ids=shots, visual_description="app web azul y blanca llamada Nimbo")
        c.db.put(product)
    return brand, product


def ensure_actor(progress: Callable[[float, str], None]) -> Actor:
    c = ctx()
    try:
        return c.db.find(Actor, PRESENTADORA["handle"])
    except KeyError:
        pass
    from .pipeline.actors import create_actor

    progress(0.02, f"Creando actor persistente {PRESENTADORA['handle']} (retrato maestro + hoja multivista + identidad)")
    return create_actor(PRESENTADORA["handle"], PRESENTADORA["appearance"], persona=PRESENTADORA["persona"],
                        wardrobe=PRESENTADORA["wardrobe"], voice_hint=PRESENTADORA["voice_hint"],
                        location_hint=PRESENTADORA["location"], locale="es-ES", gender="female")


def run_demo(duration: float = 24.0, use_vlm: bool = True, progress: Callable[[float, str], None] | None = None,
             variants: bool = True) -> dict[str, Any]:
    from . import orchestrator
    from .models import Project
    from .variants import make_variant

    prog = progress or (lambda p, m: None)
    t0 = time.time()
    brand, product = ensure_brand_product(prog)
    actor = ensure_actor(prog)
    brief = Brief(brand_id=brand.id, product_id=product.id, objective="pruebas gratuitas del software",
                  audience="dueños y responsables comerciales de pymes de servicios que pierden leads por contestar tarde",
                  key_messages=["cada lead recibe respuesta en minutos", "el comercial solo ve las citas confirmadas"],
                  locale="es-ES", duration_s=duration, platform="reels", actor_ids=[actor.id], n_angles=4,
                  style_notes="UGC grabado con el móvil en una oficina pequeña; presentadora cercana; nada de tono de anuncio")
    # reanuda un benchmark pausado (saldo o presupuesto) en vez de empezar otro: lo ya generado no se vuelve a pagar
    paused = [x for x in ctx().db.list(Project) if x.name == BENCH_NAME and x.status.startswith("paused")]
    p = paused[-1] if paused else orchestrator.create_project(brief, name=BENCH_NAME, talk_mode="native")
    res = orchestrator.run(p.id, prog, use_vlm=use_vlm)
    out: dict[str, Any] = {"master": res}
    if str(res.get("status", "")).startswith("paused"):
        out["note"] = "benchmark en pausa (ver master.reason); `motor demo` lo reanuda donde se quedó"
        out["total_cost"] = summarize()
        return out
    if variants:
        vs = []
        for kind, value in (("hook_text", "¿Cuánto tardas en contestar a un lead?"), ("aspect", "4:5"),
                            ("spoken_cta", "Pruébalo hoy, son catorce días gratis.")):
            try:
                prog(0.95, f"Variante {kind}")
                vs.append(make_variant(p.id, kind, value, use_vlm=False))
            except Exception as e:  # noqa: BLE001
                vs.append({"kind": kind, "error": str(e)[:200]})
        out["variants"] = vs
    out["total_cost"] = summarize()
    out["seconds"] = round(time.time() - t0, 1)
    out["actor"] = {"id": actor.id, "handle": actor.handle, "views": len(actor.sheet_asset_ids),
                    "identity_threshold": actor.identity.threshold, "self_similarity": actor.identity.self_similarity}
    return out


if __name__ == "__main__":  # pragma: no cover
    import json

    print(json.dumps(run_demo(progress=lambda p, m: print(f"{p * 100:5.1f}% {m}", flush=True)), indent=1, ensure_ascii=False))
