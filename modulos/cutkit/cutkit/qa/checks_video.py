"""Puertas de vídeo: negros y congelados no planificados, y duración del render igual a la de la timeline.

`blackdetect` con d = 0,03 s (el valor por defecto de 2 s no ve parpadeos) y `freezedetect` n = −60 dB, d = 0,5 s.
Un negro o congelado es intencionado si la timeline lo declara: transición `dip_to_black`/`fade_black`, o un ítem
con `props.intent` en {black, freeze, hold, still} o `props.static = true` (tarjeta fija, captura quieta).
"""
from __future__ import annotations

from typing import Any

from .context import QAContext, tc

BLACK_INTENTS = {"dip_to_black", "fade_black", "black", "fade_to_black", "dip"}
FREEZE_INTENTS = {"freeze", "hold", "still", "static", "freeze_frame"}


def _planned(ctx: QAContext, s: float, e: float, kinds: set[str]) -> bool:
    # congelados que declara el propio A-roll: `hold_after` de un segmento (respiración antes del outro, CTA final quieta
    # del perfil): el tramo [prog_out − hold_after, prog_out] es un fotograma congelado a propósito
    if kinds is FREEZE_INTENTS:
        for seg in getattr(ctx.timeline, "aroll", None) or []:
            h = float(getattr(seg, "hold_after", 0.0) or 0.0)
            if h <= 0:
                continue
            h0, h1 = float(seg.prog_out) - h - 0.1, float(seg.prog_out) + 0.1
            if s >= h0 - 0.05 and e <= h1 + 0.1:
                return True
    for it in ctx.timeline.items:
        if it.t1 < s - 0.05 or it.t0 > e + 0.05:
            continue
        label = {str(it.props.get("intent", "")), str(it.props.get("kind", "")), str(it.component or "").split(".")[-1]}
        if label & kinds or (kinds is FREEZE_INTENTS and it.props.get("static") is True):
            # el ítem debe cubrir la mayor parte del tramo
            if min(e, it.t1) - max(s, it.t0) >= 0.6 * (e - s):
                return True
    return False


def run(ctx: QAContext, dec: dict[str, Any]) -> None:
    fps = ctx.fps
    # ─── duración
    p = ctx.probe
    tl_d = float(ctx.timeline.duration or 0.0)
    rd = float(p.get("duration") or 0.0)
    ctx.metrics.update({"render_duration_s": rd, "timeline_duration_s": tl_d, "render_fps": p.get("fps"),
                        "render_size": [p.get("width"), p.get("height")]})
    tol = ctx.cfg["video"]["dur_tol_frames"] / fps + 1e-3
    if tl_d and abs(rd - tl_d) > tol:
        ctx.add("video.duration", "block",
                f"El render dura {rd:.3f} s y la timeline {tl_d:.3f} s (Δ {rd - tl_d:+.3f} s = {round((rd - tl_d) * fps):+d} fotogramas).",
                min(rd, tl_d), max(rd, tl_d), {"render_s": rd, "timeline_s": tl_d, "tolerancia_s": round(tol, 3)},
                [], [{"op": "rerender", "reason": "duración distinta de la timeline"}])
    if p.get("audio_duration") and abs(p["audio_duration"] - rd) > 0.1:
        ctx.add("video.av_duration", "warn", f"Audio ({p['audio_duration']:.2f} s) y vídeo ({rd:.2f} s) no duran lo mismo.",
                None, None, {"audio_s": p["audio_duration"], "video_s": rd}, [], [{"op": "remux"}])
    if (p.get("width"), p.get("height")) != (ctx.timeline.width, ctx.timeline.height):
        ctx.add("video.size", "block", f"Resolución {p.get('width')}×{p.get('height')} ≠ {ctx.timeline.width}×{ctx.timeline.height} de la timeline.",
                evidence={"render": [p.get("width"), p.get("height")]}, fix=[{"op": "rerender"}])
    if p.get("fps") and abs(float(p["fps"]) - fps) > 0.01:
        ctx.add("video.fps", "warn", f"El render va a {p['fps']} fps y la timeline a {fps} fps.", evidence={"render_fps": p["fps"]})
    # ─── negros
    nb = 0
    dom = ctx.boxes_source.startswith("dom")
    for s, e in dec.get("black", []):
        if _planned(ctx, s, e, BLACK_INTENTS):
            continue
        if dom and any(s - 0.05 <= b.t <= e + 0.05 for b in ctx.boxes):
            continue    # el DOM tiene texto visible: es una tarjeta sobre negro, no un parpadeo
        nb += 1
        nfr = max(1, round((e - s) * fps))
        ctx.add("video.black", "block",
                f"{nfr} fotograma(s) en negro no planificados en {tc(s)}–{tc(e)} (se lee como un parpadeo).",
                s, e, {"black_s": round(e - s, 3), "frames": nfr, "detector": "blackdetect d=0.03 pix_th=0.10 pic_th=0.98"},
                ctx.blame(s - 1 / fps, e + 1 / fps, ["layout", "transition", "overlay", "graphic", "broll"]),
                [{"op": "overlap", "frames": max(6, nfr + 2), "at": round(s, 3), "reason": "solapar el plano siguiente o fundir"}])
    # ─── congelados (medidos solo en la franja del A-roll; sin A-roll visible no cuentan)
    from .geometry import aroll_visible

    nf = 0
    for s, e in dec.get("freeze", []):
        e = e if e is not None else ctx.duration
        if _planned(ctx, s, e, FREEZE_INTENTS):
            continue
        vis = [aroll_visible(ctx, s + k * (e - s) / 6) for k in range(7)]
        if sum(vis) < 4:
            continue    # tarjeta, B-roll a pantalla completa: la cara no se ve, no es un congelado del A-roll
        nf += 1
        ctx.add("video.freeze", "block", f"Imagen congelada {e - s:.2f} s en {tc(s)}–{tc(e)} sin que el plan lo declare.",
                s, e, {"freeze_s": round(e - s, 2), "detector": "freezedetect n=-60dB d=0.5"},
                ctx.blame(s, e), [{"op": "replan", "reason": "plano congelado no planificado"}])
    ctx.metrics.update({"black_events": nb, "freeze_events": nf})


# ───────────────────────────── ly.panel_empty
PANEL_BG = {"ink": (18, 16, 22), "navy": (7, 26, 41), "paper": (236, 232, 225), "white": (246, 246, 244)}


def panel_empty(ctx: QAContext, dec: dict[str, Any]) -> None:
    """La mitad superior de un `layout.split_top` sin contenido más de 0,3 s (block): ocupación de píxeles que no son
    el fondo del panel, medida en el render a 10 fps dentro del slot (0–874 px)."""
    import numpy as np

    pn = ctx.cfg["panel"]
    arr = dec.get("panel")
    splits = [i for i in ctx.items(["layout"]) if i.component == "layout.split_top"]
    if arr is None or not splits:
        if splits:
            ctx.notes.append("ly.panel_empty: no se pudo decodificar el panel superior.")
        return
    fps = dec.get("panel_fps", pn["fps"])
    occ_all = []
    for lay in splits:
        bg = PANEL_BG.get(str(lay.props.get("panel_bg") or "ink"))
        k0, k1 = int(np.ceil((lay.t0 + 0.30) * fps)), int(np.floor(lay.t1 * fps))   # sin el deslizamiento de entrada
        empty: list[float] = []
        for k in range(max(0, k0), min(len(arr), k1)):
            fr = arr[k].astype(np.int16)
            ref = np.array(bg if bg is not None else np.median(fr[2:6].reshape(-1, 3), axis=0), dtype=np.int16)
            occ = float((np.abs(fr - ref).max(axis=2) > pn["diff"]).mean())
            t = k / fps
            occ_all.append((round(t, 2), round(occ, 4)))
            if occ < pn["occ_min"]:
                empty.append(t)
        runs: list[list[float]] = []
        for t in empty:
            if runs and t - runs[-1][-1] <= 1.5 / fps:
                runs[-1].append(t)
            else:
                runs.append([t])
        for r in runs:
            t0, t1 = r[0], r[-1] + 1 / fps
            if t1 - t0 <= pn["empty_min_s"]:
                continue
            ctx.add("ly.panel_empty", "block",
                    f"El panel superior del split está vacío {t1 - t0:.1f} s ({tc(t0)}–{tc(t1)}): media pantalla muerta.",
                    t0, t1, {"ocupacion_max": max((o for t, o in occ_all if t0 <= t <= t1), default=0.0),
                             "umbral_ocupacion": pn["occ_min"], "slot_px": [0, pn["slot_h"]], "layout_item": lay.id},
                    lay.decision_ids + ctx.blame(t0, t1, ["graphic", "broll"]),
                    [{"op": "replan", "reason": "llenar el panel (recurso anclado a la frase) o pasar a full_face", "span": [round(t0, 2), round(t1, 2)]}])
    ctx.panel_occ = occ_all
    if occ_all:
        ctx.metrics["panel_occupancy"] = {"muestras": len(occ_all), "pct_vacio": round(100 * sum(o < pn["occ_min"] for _, o in occ_all) / len(occ_all), 1)}
