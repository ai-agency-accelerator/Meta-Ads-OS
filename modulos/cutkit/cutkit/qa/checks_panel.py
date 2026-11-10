"""Panel del split vacío: la mitad superior de `layout.split_top` sin contenido más de 0,3 s.

Medida sobre el render (no sobre el plan): fotogramas en gris a 10 fps y 135×240 (área), región del panel desde
y=170 px (bajo la UI de Shorts) hasta la junta − degradado (≈ 874 px). Un fotograma está «vacío» si la región es
casi uniforme: desviación típica de luma < `std_max` y < `edge_frac_max` de píxeles con gradiente apreciable (el grano
del panel, a esta resolución, se promedia y no cuenta). Tramos vacíos > `min_s` → warn con la decisión del layout
y de lo que debería llenar el panel (broll/graphic activos).
"""
from __future__ import annotations

import numpy as np

from . import media
from .context import QAContext, tc

FPS = 10
W, H = 135, 240
CFG = {"min_s": 0.3, "std_max": 6.0, "edge_frac_max": 0.004, "edge_th": 10.0, "top_px": 170, "skip_edges_s": 0.12}


def _empty_flags(frames: np.ndarray, y0: int, y1: int) -> np.ndarray:
    reg = frames[:, y0:y1, 4:-4]
    std = reg.reshape(len(reg), -1).std(axis=1)
    gy = np.abs(np.diff(reg, axis=1))
    gx = np.abs(np.diff(reg, axis=2))
    edges = ((gy[:, :, :-1] > CFG["edge_th"]) | (gx[:, :-1, :] > CFG["edge_th"])).reshape(len(reg), -1).mean(axis=1)
    return (std < CFG["std_max"]) & (edges < CFG["edge_frac_max"])


def run(ctx: QAContext) -> None:
    splits = [i for i in ctx.items(["layout"]) if i.component == "layout.split_top"]
    if not splits or not ctx.render or not ctx.render.exists():
        return
    frames = media.lowres_gray(ctx.render, fps=FPS, w=W, h=H)
    n = len(frames)
    sy = H / float(ctx.timeline.height or 1920)
    found, checked = [], 0.0
    for it in splits:
        J = int(it.props.get("junction_y", 1008))
        feather = int(it.props.get("feather", 110))
        y0, y1 = int(CFG["top_px"] * sy), int((J - feather - 24) * sy)
        if y1 - y0 < 8:
            continue
        a = int(np.ceil((it.t0 + CFG["skip_edges_s"]) * FPS))
        b = min(n, int(np.floor((it.t1 - CFG["skip_edges_s"]) * FPS)))
        if b <= a:
            continue
        checked += (b - a) / FPS
        flags = _empty_flags(frames[a:b], y0, y1)
        k = 0
        while k < len(flags):
            if not flags[k]:
                k += 1
                continue
            j = k
            while j < len(flags) and flags[j]:
                j += 1
            s0, s1 = (a + k) / FPS, (a + j) / FPS
            if s1 - s0 > CFG["min_s"]:
                found.append((s0, s1, it))
            k = j
    ctx.metrics["panel"] = {"split_s_revisados": round(checked, 1), "tramos_vacios": len(found),
                            "s_vacios": round(sum(b - a for a, b, _ in found), 2)}
    for s0, s1, it in found:
        blame = list(it.decision_ids) + ctx.blame(s0, s1, ["broll", "graphic"])
        ctx.add("panel.split_vacio", "warn",
                f"La mitad superior del split está vacía {s1 - s0:.1f} s ({tc(s0)}–{tc(s1)}): falta recurso o el gráfico "
                "sale antes del corte del layout.",
                t0=s0, t1=s1, evidence={"layout_item": it.id, "umbral_s": CFG["min_s"]}, blame=blame,
                fix=[{"op": "extend_or_add_broll", "t0": round(s0, 3), "t1": round(s1, 3)},
                     {"op": "shorten_layout", "item": it.id, "to": round(s0, 3)}])
