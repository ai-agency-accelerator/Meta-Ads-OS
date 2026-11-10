"""Dónde está la cara de la persona en cámara EN PANTALLA en cada instante.

`render_spec.aroll.faces` está en coordenadas del A-roll crudo (normalizadas 0..1). El runtime de cutkit/motion lo
mueve por layout (split: cara bajada ~470 px; full_face: reencuadre ×1,12–1,22 anclado abajo) y por cámara
(punch_in / slow_push). Dos fuentes, en este orden:
1. DOM: el rectángulo del <video> del A-roll tras el seek (exacto: incluye layout, cámara y animaciones de entrada).
2. Respaldo en Python que replica `components/layout.js` y `camera.js` (aproximado).
Sin A-roll visible (`layout.broll_full`, `layout.card_float`, opacidad de la cámara < 0,5) → None.
"""
from __future__ import annotations

import bisect
from typing import Any

from .context import QAContext, face_at

HIDDEN_LAYOUTS = {"layout.broll_full", "layout.card_float"}
SPLIT = {"J": 1008, "shift": 470, "eyes_y": 1250}
FULL = {"rail_max": 1214, "cap_top": 28, "gap": 22, "s_max": 1.22, "chin_pad": 0.035}


def layout_at(ctx: QAContext, t: float):
    """Ítem de layout activo en t (None = full_face implícito)."""
    cur = None
    for it in sorted(ctx.items(["layout"]), key=lambda i: i.t0):
        if it.t0 <= t + 1e-6 and t < it.t1 - 1e-6:
            cur = it
    return cur


def aroll_visible(ctx: QAContext, t: float) -> bool:
    lay = layout_at(ctx, t)
    if lay is not None and lay.component in HIDDEN_LAYOUTS and lay.props.get("aroll") != "behind":
        return False
    rect = _cam_rect(ctx, t)
    return rect is None or rect[4] >= 0.5


def _cam_rect(ctx: QAContext, t: float) -> tuple[float, float, float, float, float] | None:
    cr = ctx.cam_rects
    if not cr:
        return None
    ts = [c[0] for c in cr]
    k = bisect.bisect_left(ts, t)
    best = min((c for c in cr[max(0, k - 1):k + 1]), key=lambda c: abs(c[0] - t))
    return best[1:] if abs(best[0] - t) <= 0.2 else None


def _median_face(ctx: QAContext, t0: float, t1: float) -> tuple[float, float, float, float] | None:
    sel = [f for f in ctx.faces if t0 - 0.05 <= f[0] <= t1 + 0.05]
    if not sel:
        return face_at(ctx, (t0 + t1) / 2, max_dt=5.0)
    med = lambda k: sorted(f[k] for f in sel)[len(sel) // 2]  # noqa: E731
    return med(1), med(2), med(3), med(4)


def _layout_cam(ctx: QAContext, lay, t: float) -> tuple[float, float, float] | None:
    """(x, y, s) del contenedor de cámara del layout (transformOrigin 0 0), como layout.js."""
    W, H = ctx.timeline.width, ctx.timeline.height
    t0, t1 = (lay.t0, lay.t1) if lay is not None else (t - 1, t + 1)
    p: dict[str, Any] = lay.props if lay is not None else {}
    f = _median_face(ctx, t0, t1)
    name = lay.component if lay is not None else "layout.full_face"
    if name in HIDDEN_LAYOUTS:
        return None
    if name == "layout.split_top":
        if p.get("face_shift") is not None:
            dy = float(p["face_shift"])
        elif f is None:
            dy = SPLIT["shift"]
        else:
            eyes_src = (f[1] + f[3] * 0.40) * H
            dy = min(620.0, max(300.0, round(float(p.get("eyes_y", SPLIT["eyes_y"])) - eyes_src)))
        return 0.0, dy, 1.0
    if f is None:
        return 0.0, 0.0, 1.0
    c = min(0.95, max(0.3, f[1] + f[3] + float(p.get("chin_pad", FULL["chin_pad"]))))
    target = (FULL["rail_max"] - FULL["cap_top"] - FULL["gap"]) / H
    s = 1.0
    if p.get("reframe") is not False and c > target:
        s = min(float(p.get("max_scale", FULL["s_max"])), max(1.0, (1 - target) / (1 - c)))
    cx = (f[0] + f[2] / 2) * W
    x = round(min(0.0, max(W * (1 - s), cx * (1 - s))))
    return float(x), float(round(H * (1 - s))), s


def _camera_move(ctx: QAContext, lay, t: float) -> tuple[float, float, float]:
    """punch_in (ck-cam-move) activo en t, con su punto de anclaje como camera.js."""
    W, H = ctx.timeline.width, ctx.timeline.height
    for c in ctx.items(["camera"]):
        if not (c.t0 <= t < c.t1) or c.component not in ("camera.punch_in",):
            continue
        s = min(2.0, max(1.0, float(c.props.get("scale", 1.3))))
        if 1.0 < s < 1.12:
            s = 1.12
        f = _median_face(ctx, c.t0, c.t1)
        if f is None:
            continue
        focus = c.props.get("focus")
        rail_below = lay is None or lay.component != "layout.split_top"
        if focus == "chin" or (focus != "eyes" and rail_below):
            P = ((f[0] + f[2] / 2) * W, min(H, (f[1] + f[3] + 0.035) * H))
        else:
            P = ((f[0] + f[2] / 2) * W, (f[1] + f[3] * 0.40) * H)
        return round(P[0] * (1 - s)), round(P[1] * (1 - s)), s
    return 0.0, 0.0, 1.0


def face_screen(ctx: QAContext, t: float) -> tuple[float, float, float, float] | None:
    """Caja de la cara en px del lienzo (x0, y0, x1, y1) o None si el A-roll no se ve."""
    f = face_at(ctx, t)
    if f is None or not aroll_visible(ctx, t):
        return None
    W, H = ctx.timeline.width, ctx.timeline.height
    rect = _cam_rect(ctx, t)
    if rect is not None:
        rx, ry, rw, rh, _ = rect
        return rx + f[0] * rw, ry + f[1] * rh, rx + (f[0] + f[2]) * rw, ry + (f[1] + f[3]) * rh
    lay = layout_at(ctx, t)
    lc = _layout_cam(ctx, lay, t)
    if lc is None:
        return None
    mx, my, ms = _camera_move(ctx, lay, t)
    lx, ly, ls = lc

    def tr(px: float, py: float) -> tuple[float, float]:
        px, py = px * ms + mx, py * ms + my          # #ck-cam-move (punch)
        return px * ls + lx, py * ls + ly            # #ck-cam (layout)
    x0, y0 = tr(f[0] * W, f[1] * H)
    x1, y1 = tr((f[0] + f[2]) * W, (f[1] + f[3]) * H)
    return x0, y0, x1, y1
