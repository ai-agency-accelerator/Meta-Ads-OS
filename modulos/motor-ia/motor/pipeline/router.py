"""Model Router: decide la ruta más barata que mantiene la calidad para cada plano.

Regla de oro (investigación, rondas 3–4): no generar lo que se puede componer o reutilizar.
  - Texto, CTA, pantallas de app, producto con fotos reales → composición programática (coste ≈0)
  - Actor hablando → A-roll continuo con diálogo nativo (Omni) encadenado por extensiones
    (o banco + lip-sync de boca si hay proveedor de lip-sync)
  - Actor sin hablar → fotograma clave verificado + imagen→vídeo sin diálogo
  - B-roll sin personas → modelo barato (Veo Lite), con Omni como respaldo
Cada ruta lleva coste estimado y respaldos; el router respeta el tope de presupuesto del proyecto.
"""

from __future__ import annotations

from ..costs import price
from ..models import Product, Route, Shot
from ..providers import registry
from ..store import ctx


def _omni_cost(seconds: float, res: str = "720p") -> float:
    return price("gemini", "gemini-omni-1.1-flash", res, 0.101) * seconds


def _img_cost(n: int = 1) -> float:
    return price("gemini", "gemini-3.1-flash-image", "1k", 0.067) * n


def route_for(shot: Shot, product: Product | None, *, talk_mode: str, quality: str = "final") -> Route:
    has_fal_lipsync = registry.lipsync() is not None and not ctx().settings.mock
    res = "720p"
    if shot.shot_type == "graphic_card":
        return Route(pipeline="compose.cta", provider="local", est_cost_usd=0.0, reason="texto y CTA siempre programáticos")
    if shot.shot_type == "app_screen":
        if product and (product.screenshot_asset_ids or product.screen_recording_asset_ids):
            return Route(pipeline="compose.app_phone", provider="local", est_cost_usd=0.0,
                         reason="pantallas reales de la app en un móvil (cero UI inventada)",
                         fallbacks=[{"pipeline": "i2v", "model": "omni"}])
        return Route(pipeline="i2v", provider="gemini", model="gemini-omni-1.1-flash", est_cost_usd=_img_cost() + _omni_cost(shot.duration),
                     reason="sin capturas reales: plano de ambiente (nunca UI generada)")
    if shot.shot_type == "product_hero" and product and (product.packshot_asset_ids or product.footage_asset_ids):
        return Route(pipeline="compose.packshot", provider="local", est_cost_usd=0.0, reason="packshot/metraje real del producto")
    if shot.shot_type == "talking_head":
        if talk_mode == "lipsync" and has_fal_lipsync:
            return Route(pipeline="talking.bank_lipsync", provider="fal", model="kling-lipsync",
                         est_cost_usd=0.014 * max(5.0, shot.duration) * 1.5, reason="banco del actor + boca nueva")
        if talk_mode == "voiceover":
            return Route(pipeline="i2v", provider="gemini", model="gemini-omni-1.1-flash", params={"silent": True},
                         est_cost_usd=_img_cost() + _omni_cost(min(shot.duration, 6)), reason="voz en off: actor sin hablar")
        return Route(pipeline="talking.chain", provider="gemini", model="gemini-omni-1.1-flash",
                     est_cost_usd=_omni_cost(shot.duration + 1.0) * 1.4 + (_img_cost(2) if shot.index == 0 else 0),
                     reason="A-roll continuo con diálogo nativo (voz e identidad constantes por extensión)",
                     fallbacks=[{"pipeline": "talking.single", "model": "omni"}, {"pipeline": "voiceover"}])
    if shot.shot_type == "broll" and not shot.actor_id:
        return Route(pipeline="i2v", provider="gemini", model="veo-3.1-lite-generate-preview",
                     params={"duration": 4, "resolution": res},
                     est_cost_usd=_img_cost() + price("gemini", "veo-3.1-lite-generate-preview", "720p", 0.05) * 4 * 1.3,
                     reason="B-roll sin personas: modelo barato", fallbacks=[{"pipeline": "i2v", "model": "omni"}])
    # actor sin hablar / reacción / producto en mano / producto sin fotos reales
    dur = min(max(shot.duration, 3.0), 6.0)
    return Route(pipeline="i2v", provider="gemini", model="gemini-omni-1.1-flash", params={"silent": True},
                 est_cost_usd=(_img_cost(2 if shot.shot_type == "product_hand" else 1) + _omni_cost(dur) * 1.3),
                 reason="fotograma clave verificado + vídeo sin diálogo",
                 fallbacks=[{"pipeline": "i2v", "model": "veo-3.1-fast-generate-preview"}])


def plan_routes(shots: list[Shot], product: Product | None, *, talk_mode: str, quality: str = "final") -> float:
    total = 0.0
    for s in shots:
        s.route = route_for(s, product, talk_mode=talk_mode, quality=quality)
        total += s.route.est_cost_usd
    return round(total, 3)
