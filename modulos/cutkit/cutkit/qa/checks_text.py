"""Zonas seguras de Meta (Reels y Stories) y tamaño de texto (cajas del DOM de HF o del OCR).

Zona segura (1080×1920): 269 arriba, 672 abajo, 65 a cada lado y 227 a la derecha por debajo de y=1152 (franja de
botones de Reels); se escala con el lienzo (`cfg["safe"]`).
Tamaño: texto clave (subtítulos, titulares) ≥ 44 px; texto que se lee ≥ 30 px; < 24 px bloquea si viene del DOM y
no es decorativo (con OCR no se distingue lo decorativo ni el texto quemado en una captura: aviso).
También mide `ly.concurrent_text` (bloques simultáneos fuera del subtítulo) y texto cortado en el borde.
"""
from __future__ import annotations

from collections import defaultdict

from .config import gate_severity
from .context import QAContext, TextBox, norm_word, tc

KEY_ROLES = {"caption", "key", "headline", "title", "hero", "stat"}


def _zone(ctx: QAContext) -> tuple[float, float, float, float]:
    s = ctx.cfg["safe"]
    W, H = ctx.timeline.width, ctx.timeline.height
    sx, sy = W / s["ref_w"], H / s["ref_h"]
    return s["left"] * sx, s["top"] * sy, W - s["right"] * sx, H - s["bottom"] * sy


def _key(b: TextBox, ctx: QAContext | None = None) -> str:
    """Clave de agrupación: el raíl de subtítulos es UNO; un gráfico, su ítem; el OCR sin atribuir, el gráfico o
    B-roll activo en ese instante (así un panel con 10 etiquetas da un issue, no diez)."""
    if (b.role or "") == "caption":
        return "caption-rail"
    if b.item:
        return b.item
    if ctx is not None:
        act = ctx.active(b.t, b.t, ["graphic", "broll", "overlay"])
        if act:
            return "en:" + max(act, key=lambda i: (i.z, i.t0)).id
    return f"ocr:{norm_word(b.text)[:24]}"


def _spans(samples: list[TextBox], step: float, gap_s: float = 1.5) -> list[list[TextBox]]:
    out: list[list[TextBox]] = []
    for b in sorted(samples, key=lambda x: x.t):
        if out and b.t - out[-1][-1].t <= max(step * 1.6, gap_s):
            out[-1].append(b)
        else:
            out.append([b])
    return out


def run(ctx: QAContext) -> None:
    if not ctx.boxes:
        ctx.notes.append("Sin cajas de texto: no se comprueban zonas seguras ni tamaños.")
        return
    s = ctx.cfg["safe"]
    zx0, zy0, zx1, zy1 = _zone(ctx)
    is_ocr = ctx.boxes_source.startswith("ocr")
    step = 1.0 / (ctx.cfg["sampling"]["ocr_fps"] if is_ocr else ctx.cfg["sampling"]["boxes_fps"])
    tol = s["ocr_tol_px"] if is_ocr else 0.5      # estrictamente fuera (<, no ≤), con medio píxel de redondeo
    W, H = ctx.timeline.width, ctx.timeline.height
    items = {i.id: i for i in ctx.timeline.items}

    # ventanas en movimiento: transiciones (barridos/luces desplazan todo el plano) y entradas deslizadas de los split
    trans = [(i.t0 - 1 / ctx.fps, i.t1 + 1 / ctx.fps) for i in ctx.timeline.items if i.track == "transition"]
    slides = [(i.t0, i.t0 + 12 / ctx.fps) for i in ctx.timeline.items
              if i.track == "layout" and (i.props or {}).get("enter") == "slide"]

    def moving(b: TextBox) -> bool:
        """Muestra tomada durante el desplazamiento de entrada (≈12 f) o de salida (≈8 f) de su ítem, durante una
        transición o durante la entrada deslizada de un split (el contenido cae con el panel)."""
        if any(a <= b.t <= z for a, z in trans + slides):
            return True
        it = items.get(b.item or "")
        if it is None:
            return False
        return b.t - it.t0 < 12 / ctx.fps or it.t1 - b.t < 8 / ctx.fps

    # ─── zona segura
    out_by: dict[str, list[tuple[TextBox, dict[str, float]]]] = defaultdict(list)
    times_out: set[float] = set()
    zx1_top = W - (zx0)   # la franja de botones está en la parte baja: por encima, margen simétrico (65 px)
    split_y = H * float(s.get("right_from_y", 1152)) / s["ref_h"]
    for b in ctx.boxes:
        right = zx1 if b.y1 > split_y else zx1_top     # misma regla que el runtime (ctx.safeAt con tokens.safe_right_from_y)
        intr = {"arriba": zy0 - b.y0, "abajo": b.y1 - zy1, "izquierda": zx0 - b.x0, "derecha": b.x1 - right}
        intr = {k: round(v, 1) for k, v in intr.items() if v > tol}
        if intr and moving(b):
            continue
        if intr:
            out_by[_key(b, ctx)].append((b, intr))
            times_out.add(round(b.t, 3))
    n_t = len({round(b.t, 3) for b in ctx.boxes}) or 1
    ctx.metrics["safe_zone"] = {"zona_px": [round(zx0), round(zy0), round(zx1), round(zy1)],
                                "muestras_con_texto_fuera_pct": round(100 * len(times_out) / n_t, 1),
                                "segundos_fuera_aprox": round(len(times_out) * step, 1)}
    rail = out_by.pop("caption-rail", None)
    if rail:
        sps = _spans([h[0] for h in rail], step, 3.0)
        worst: dict[str, float] = {}
        for _, intr in rail:
            for k, v in intr.items():
                worst[k] = max(worst.get(k, 0), v)
        secs = sum(sp[-1].t + step - sp[0].t for sp in sps)
        b = max(rail, key=lambda h: max(h[1].values()))[0]
        blame = list(dict.fromkeys(d for h in rail for d in (items[h[0].item].decision_ids if h[0].item in items else [])))
        lados = ", ".join(f"{k} {v:.0f} px" for k, v in sorted(worst.items(), key=lambda kv: -kv[1]))
        ctx.add("text.safe_zone", gate_severity("rd.safe_zone", "block") if max(worst.values()) >= 8 else "warn",
                f"El raíl de subtítulos sale de la zona segura en {len(sps)} tramo(s) (≈ {secs:.0f} s; peor {lados}): "
                f"súbelo por encima de y = {round(zy1)} px o fíjalo por layout.",
                sps[0][0].t, sps[-1][-1].t + step,
                {"tramos": [[round(sp[0].t, 2), round(sp[-1].t + step, 2)] for sp in sps][:40], "intrusion_px": worst,
                 "ejemplo": b.text, "zona_px": [round(zx0), round(zy0), round(zx1), round(zy1)], "fuente": b.source},
                blame or ctx.blame(sps[0][0].t, sps[-1][-1].t, ["layout"])[:10],
                [{"op": "move_caption_rail", "max_y_px": round(zy1) - 20}])
    for key, hits in out_by.items():
        for sp in _spans([h[0] for h in hits], step, 1.5):
            t0, t1 = sp[0].t, sp[-1].t + step
            hh = [h for h in hits if t0 - 1e-6 <= h[0].t <= t1]
            worst: dict[str, float] = {}
            for _, intr in hh:
                for k, v in intr.items():
                    worst[k] = max(worst.get(k, 0), v)
            b = max(hh, key=lambda h: max(h[1].values()))[0]
            attributed = b.source == "dom" or b.item is not None
            sev = gate_severity("rd.safe_zone", "block") if attributed and max(worst.values()) >= 8 else "warn"   # < 8 px: aviso
            it = items.get(b.item or "")
            blame = (it.decision_ids if it else []) or ctx.blame(t0, t1, ["graphic", "broll", "layout", "caption"])
            lados = ", ".join(f"{k} {v:.0f} px" for k, v in sorted(worst.items(), key=lambda kv: -kv[1]))
            quien = "El raíl de subtítulos queda" if key == "caption-rail" else (
                f"Texto de {key.split(':')[-1]} queda" if key.startswith("en:") or key in items else "Texto")
            if key == "caption-rail":
                blame = list(dict.fromkeys(d for h in hh for d in (items[h[0].item].decision_ids if h[0].item in items else [])))
                blame = blame or ctx.blame(t0, t1, ["layout"])
            ctx.add("text.safe_zone", sev,
                    f"{quien} fuera de la zona segura en {tc(t0)}–{tc(t1)} ({len({round(h[0].t, 2) for h in hh})} muestras; "
                    f"peor: «{b.text[:40]}», {lados})"
                    + ("" if attributed else " [OCR sin atribuir: puede ser texto de una captura]") + ".",
                    t0, t1, {"texto": b.text, "caja": [round(b.x0), round(b.y0), round(b.x1), round(b.y1)],
                             "intrusion_px": worst, "zona_px": [round(zx0), round(zy0), round(zx1), round(zy1)],
                             "item": b.item, "fuente": b.source, "muestras": len(hh)},
                    blame, [{"op": "reflow_component", "item": b.item, "safe_profile": "shorts_9x16"}] if b.item else
                    [{"op": "replan", "reason": "layout fuera de zona segura"}])

    # ─── tamaño mínimo
    small_by: dict[str, list[TextBox]] = defaultdict(list)
    for b in ctx.boxes:
        size = b.font_px if b.font_px else b.h
        is_key = (b.role or "") in KEY_ROLES
        if (b.role or "") in ("decorative", "caption"):
            continue      # el raíl de subtítulos se mide aparte, con su tamaño típico
        if size < (s["key_min_px"] if is_key else s["min_px"]):
            small_by[_key(b, ctx)].append(b)
    # raíl de subtítulos: el alto de caja OCR depende de las letras («una» no tiene ascendentes), así que se
    # compara el p75 de todas sus cajas (o el font_px del DOM) con el mínimo de texto clave
    cap = [b for b in ctx.boxes if (b.role or "") == "caption"]
    if cap:
        import numpy as np
        hs = np.array([b.font_px or b.h for b in cap])
        typ = float(np.percentile(hs, 75 if is_ocr else 50))
        ctx.metrics["caption_px"] = {"p25": round(float(np.percentile(hs, 25)), 1), "tipico": round(typ, 1), "n": len(cap)}
        if typ < s["key_min_px"]:
            ctx.add("text.size", "block" if not is_ocr else "warn",
                    f"Subtítulos de ~{typ:.0f} px (mínimo {s['key_min_px']} px para texto clave{'; alto de caja OCR p75' if is_ocr else ''}).",
                    0, ctx.duration, {"px_tipico": round(typ, 1), "umbral_px": s["key_min_px"], "fuente": ctx.boxes_source},
                    [], [{"op": "scale_text", "track": "caption", "min_px": s["key_min_px"]}])
    for key, bs in small_by.items():
        for sp in _spans(bs, step):
            b = min(sp, key=lambda x: x.font_px or x.h)
            size = b.font_px or b.h
            is_key = (b.role or "") in KEY_ROLES
            if size < s["tiny_px"]:
                sev = "block" if b.source == "dom" or b.item else "warn"
            elif is_key:
                sev = "block" if b.source == "dom" else "warn"    # alto de caja OCR ≠ cuerpo de letra: aviso
            else:
                sev = "warn"
            if len(sp) < 2 and sev == "warn" and b.source == "ocr":
                continue        # una sola muestra OCR: ruido probable
            t0, t1 = sp[0].t, sp[-1].t + step
            it = items.get(b.item or "")
            n_txt = len({norm_word(x.text) for x in sp})
            ctx.add("text.size", sev,
                    f"{'Subtítulos' if key == 'caption-rail' else 'Texto clave' if is_key else 'Texto'} de {size:.0f} px en "
                    f"{tc(t0)}–{tc(t1)} ({n_txt} textos; el menor «{b.text[:30]}») "
                    f"(mínimo {s['key_min_px'] if is_key else s['min_px']} px{'; caja OCR' if b.source == 'ocr' else ''}).",
                    t0, t1, {"px": round(size, 1), "medida": "font_px" if b.font_px else "alto_caja", "texto": b.text,
                             "rol": b.role, "item": b.item, "fuente": b.source,
                             "umbral_px": s["key_min_px"] if is_key else s["min_px"]},
                    (it.decision_ids if it else []) or ctx.blame(t0, t1, ["graphic", "broll"]),
                    [{"op": "scale_text", "item": b.item, "min_px": s["key_min_px"] if is_key else s["min_px"]}])
    sizes = sorted((b.font_px or b.h) for b in ctx.boxes)
    if sizes:
        ctx.metrics["text_px"] = {"p10": round(sizes[len(sizes) // 10], 1), "p50": round(sizes[len(sizes) // 2], 1),
                                  "pct_lt_24": round(100 * sum(x < 24 for x in sizes) / len(sizes), 1)}

    # ─── ly.caption_rail_jump: el subtítulo salta de altura sin cambio de layout
    cy: dict[float, float] = {}
    for b in ctx.boxes:
        if (b.role or "") == "caption":
            cy[round(b.t, 3)] = max(cy.get(round(b.t, 3), 0.0), (b.y0 + b.y1) / 2)
    lay = [i.t0 for i in ctx.items(["layout"])]
    jumps = []
    ts = sorted(cy)
    for a, b2 in zip(ts, ts[1:]):
        if b2 - a <= 2.5 * step and abs(cy[b2] - cy[a]) > 0.03 * H and not any(a - 0.5 <= l <= b2 + 0.5 for l in lay):
            jumps.append((a, b2, cy[a], cy[b2]))
    if jumps:
        ctx.add("ly.caption_rail_jump", gate_severity("ly.caption_rail_jump"),
                f"El subtítulo cambia de altura {len(jumps)} vez/veces sin cambio de layout (p. ej. {tc(jumps[0][0])}: "
                f"y {jumps[0][2]:.0f} → {jumps[0][3]:.0f} px).",
                jumps[0][0], jumps[-1][1], {"saltos": [[round(a, 2), round(y0), round(y1)] for a, _, y0, y1 in jumps][:20]},
                ctx.blame(jumps[0][0], jumps[-1][1], ["layout"])[:8], [{"op": "fix_caption_rail_per_layout"}])

    # ─── texto cortado en el borde del lienzo
    edge = [b for b in ctx.boxes if (b.x0 <= 4 or b.y0 <= 4 or b.x1 >= W - 4 or b.y1 >= H - 4) and not moving(b)]
    for sp in _spans(edge, step):
        if len(sp) < 2 and is_ocr:
            continue
        b = sp[0]
        ctx.add("text.clipped", "block" if b.source == "dom" else "warn",
                f"Texto que toca el borde del lienzo (posible corte) en {tc(sp[0].t)}: «{b.text[:40]}».",
                sp[0].t, sp[-1].t + step, {"caja": [round(b.x0), round(b.y0), round(b.x1), round(b.y1)], "fuente": b.source},
                ctx.blame(sp[0].t, sp[-1].t, ["graphic", "broll", "camera"]), [{"op": "reflow_component", "item": b.item}])

    # ─── ly.concurrent_text: bloques simultáneos fuera del subtítulo
    th = ctx.cfg["motion"]
    by_t: dict[float, list[TextBox]] = defaultdict(list)
    for b in ctx.boxes:
        if (b.role or "") not in ("caption", "lockup"):
            by_t[round(b.t, 3)].append(b)
    heavy = []
    for t, bs in sorted(by_t.items()):
        blocks = {_key(b, ctx) for b in bs} if not is_ocr else _ocr_blocks(bs)
        words = sum(len(b.text.split()) for b in bs)
        if len(blocks) > th["concurrent_blocks_max"] + (1 if is_ocr else 0):     # cuenta bloques (ítems), no palabras
            heavy.append((t, len(blocks), words))
    for sp in _spans([TextBox(t=t, text="", x0=0, y0=0, x1=0, y1=0) for t, _, _ in heavy], step):
        if len(sp) < 2:
            continue
        t0, t1 = sp[0].t, sp[-1].t + step
        hv = [h for h in heavy if t0 <= h[0] <= t1]
        ctx.add("ly.concurrent_text", gate_severity("ly.concurrent_text"),
                f"Demasiado texto compitiendo en {tc(t0)}–{tc(t1)}: hasta {max(h[1] for h in hv)} bloques y "
                f"{max(h[2] for h in hv)} palabras fuera del subtítulo (máx. {th['concurrent_blocks_max']} y {th['concurrent_words_max']}).",
                t0, t1, {"bloques_max": max(h[1] for h in hv), "palabras_max": max(h[2] for h in hv), "fuente": ctx.boxes_source},
                ctx.blame(t0, t1, ["graphic", "broll"]), [{"op": "remove_component", "reason": "un único foco"}])


def _ocr_blocks(bs: list[TextBox]) -> list[tuple[float, float]]:
    """Agrupa líneas OCR cercanas en bloques (párrafos/tarjetas)."""
    blocks: list[list[TextBox]] = []
    for b in sorted(bs, key=lambda x: x.y0):
        for bl in blocks:
            last = bl[-1]
            if b.y0 - last.y1 < 1.2 * max(last.h, b.h) and min(b.x1, last.x1) - max(b.x0, last.x0) > -40:
                bl.append(b)
                break
        else:
            blocks.append([b])
    return [(bl[0].x0, bl[0].y0) for bl in blocks]
