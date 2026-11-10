"""Ritmo: intervalos entre cambios visuales (inicios de ítems layout/broll/graphic/transition y punch-in de cámara)
frente a la distribución del perfil (`perfil_estilo.yaml → estilo.ritmo`).

- Hueco visual muerto: intervalo > p90 del perfil sin justificación de contención → warn (alta si es el gancho).
- Sobre-edición: cambios por minuto > p90 del perfil (`cortes_por_min`) → warn.
- Gancho: el primer cambio visual llega después de `hook_first_change_s`.
Siempre avisos (las referencias no son el estilo del usuario; se usa un perfil de referencia como distribución hasta que
haya ediciones aprobadas por el usuario).
"""
from __future__ import annotations

import numpy as np

from .config import rhythm_profile
from .context import QAContext, cam_kind, tc

VISUAL_TRACKS = ("layout", "broll", "graphic", "transition")


def visual_changes(ctx: QAContext) -> list[float]:
    ts = [i.t0 for i in ctx.items(VISUAL_TRACKS)]
    ts += [i.t0 for i in ctx.items(["camera"]) if cam_kind(i).startswith(("punch", "reframe"))]
    ts += [i.t1 for i in ctx.items(["graphic", "broll"]) if i.t1 < ctx.duration - 0.2]   # la salida también cambia el plano
    # tiempos internos de los componentes (cada elemento de una lista, cada paso de un diagrama) también son cambios
    ts += [float(v) for i in ctx.items(["graphic", "broll", "overlay"]) for v in i.cues.values()
           if isinstance(v, (int, float)) and i.t0 <= v <= i.t1]
    ts = sorted(t for t in ts if 0 <= t < ctx.duration)
    out: list[float] = []
    for t in ts:
        if not out or t - out[-1] > 0.10:
            out.append(round(t, 3))
    return out


ALIVE = ("media.scroll", "viz.", "flow.", "chart.", "progress.", "timeline.steps", "media.video", "media.screen")


def alive_spans(ctx: QAContext) -> list[tuple[float, float]]:
    """Tramos con animación interna continua (scroll, diagrama que se dibuja, vídeo): no son huecos muertos."""
    out = []
    for i in ctx.items(["graphic", "broll", "overlay"]):
        comp = i.component or ""
        if comp.startswith(ALIVE) or i.props.get("speed") or i.props.get("scroll") or i.props.get("animated"):
            out.append((i.t0, i.t1))
    return out


def run(ctx: QAContext) -> None:
    prof_name = ctx.plan.style_profile if ctx.plan and ctx.plan.style_profile else ctx.timeline.style.get("style_profile")
    name, ritmo = rhythm_profile(prof_name)
    ev = visual_changes(ctx)
    dur = ctx.duration
    if dur <= 0:
        return
    gaps = np.diff([0.0] + ev + [dur])
    per_min = len(ev) / dur * 60
    ctx.metrics["pacing"] = {"perfil": name or None, "perfil_es_propio": bool(prof_name) and prof_name == name,
                             "cambios": len(ev), "cambios_por_min": round(per_min, 1),
                             "intervalo_s": {"p10": round(float(np.percentile(gaps, 10)), 2), "p50": round(float(np.median(gaps)), 2),
                                             "p90": round(float(np.percentile(gaps, 90)), 2), "max": round(float(gaps.max()), 2)}}
    if not ritmo:
        ctx.notes.append("Sin perfil de ritmo: no se compara la densidad.")
        return
    iv = ritmo.get("intervalo_cambio_visual_s", {})
    cpm = ritmo.get("cortes_por_min", {})
    p90_gap = float(iv.get("p90", 2.8))
    ref = f"perfil {name}" + ("" if prof_name == name else " (referencia; no es el estilo del usuario: certeza baja)")
    cont = ctx.contention_spans() + alive_spans(ctx)
    bounds = [0.0] + ev + [dur]
    for a, b in zip(bounds, bounds[1:]):
        if b - a <= p90_gap:
            continue
        covered = sum(max(0.0, min(b, ce) - max(a, cs)) for cs, ce in cont)
        if covered >= 0.6 * (b - a):
            continue
        hook = a < 3.0
        ctx.add("pacing.dead_gap", "warn",
                f"{'Gancho' if hook else 'Hueco visual'} de {b - a:.1f} s sin cambio visual ({tc(a)}–{tc(b)}); p90 del {ref} = {p90_gap:.1f} s.",
                a, b, {"hueco_s": round(b - a, 2), "p90_perfil_s": p90_gap, "max_perfil_s": iv.get("max"), "perfil": name,
                       "prioridad": "alta" if hook else "media", "contencion_cubre_s": round(covered, 2)},
                ctx.blame(a, b, ["layout", "camera", "broll", "graphic"]),
                [{"op": "replan", "reason": "añadir un evento anclado a una palabra de énfasis o declarar contención",
                  "span": [round(a, 2), round(b, 2)]}])
    if cpm and per_min > float(cpm.get("p90", 50)):
        ctx.add("pacing.over_edit", "warn",
                f"Sobre-edición: {per_min:.0f} cambios visuales por minuto (p90 del {ref} = {cpm.get('p90')}).",
                0, dur, {"cambios_por_min": round(per_min, 1), "p90_perfil": cpm.get("p90"), "perfil": name},
                [], [{"op": "replan", "reason": "restar: quitar los cambios de ritmo puro sin causa semántica"}])
    first = ev[0] if ev else dur
    lim = ctx.cfg["pacing"]["hook_first_change_s"]
    if first > lim:
        ctx.add("pacing.hook", "warn", f"El primer cambio visual llega a {first:.1f} s (gancho: antes de {lim:.1f} s).",
                0, first, {"primer_cambio_s": round(first, 2), "umbral_s": lim, "perfil_primer_corte": ritmo.get("primer_corte_s")},
                ctx.blame(0, first, ["layout", "camera"]), [{"op": "replan", "reason": "evento visual antes de 1 s en el gancho"}])
