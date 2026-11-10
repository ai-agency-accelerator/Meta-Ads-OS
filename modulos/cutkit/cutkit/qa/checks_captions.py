"""Puertas de subtítulos (ítems `caption.*`): sincronía con `word_times`, duración mínima, cobertura y que no tapen
ni la boca ni los ojos (`render_spec.aroll.faces`).

Sincronía: cada página entra entre 0 y 2 fotogramas ANTES de su primera palabra (lead = t_palabra − t0).
Bloquea si el subtítulo llega > 150 ms tarde o > 300 ms antes (ITU-R BT.1359).
"""
from __future__ import annotations

from .context import QAContext, caption_words, item_texts, tc, tokens
from .geometry import face_screen, layout_at

# zonas de la cara (fracciones de la caja de la cara): ojos y boca
EYES = (0.15, 0.22, 0.85, 0.50)
MOUTH = (0.22, 0.62, 0.78, 0.95)


def _caption_items(ctx: QAContext):
    return sorted([i for i in ctx.items(["caption"]) if (i.component or "caption").startswith("caption")], key=lambda i: i.t0)


def _first_word(ctx: QAContext, it) -> tuple[str, float] | None:
    """Primera palabra de la página: ids del compilador (props.words[].id / decisiones caption.<id>), luego los tiempos
    propios de props.words[].t0, y como último recurso la ventana [t0 − 1 fotograma, t1)."""
    wt = ctx.timeline.word_times
    ids = caption_words(it, wt)
    if ids:
        w = min(ids, key=lambda x: wt[x][0])
        return w, float(wt[w][0])
    ws = [x for x in (it.props.get("words") or []) if isinstance(x, dict) and isinstance(x.get("t0"), (int, float))]
    if ws:
        w = min(ws, key=lambda x: x["t0"])
        return str(w.get("text", "?")), float(w["t0"])
    f = 1.0 / ctx.fps
    cands = [(k, float(v[0])) for k, v in wt.items() if it.t0 - f - 1e-6 <= v[0] < it.t1]
    return min(cands, key=lambda x: x[1]) if cands else None


def _hidden_spans(ctx: QAContext) -> list[tuple[float, float]]:
    """Tramos donde el plan oculta el raíl (`caption.hide`) o un gráfico declara que ya dice el texto."""
    out = []
    dec = ctx.decisions()
    for it in ctx.timeline.items:
        if it.props.get("hides_captions") or it.props.get("hide_captions") or it.component == "caption.hide":
            out.append((it.t0, it.t1))
        elif any(d in dec and dec[d].type == "caption.hide" for d in it.decision_ids):
            out.append((it.t0, it.t1))
    wt = ctx.timeline.word_times
    for d in dec.values():
        if d.type == "caption.hide" and d.anchor.start in wt:
            out.append((wt[d.anchor.start][0] + d.anchor.lead, wt.get(d.anchor.end or d.anchor.start, wt[d.anchor.start])[1]))
    return out


def run(ctx: QAContext) -> None:
    c = ctx.cfg["captions"]
    fps = ctx.fps
    caps = _caption_items(ctx)
    ctx.metrics["caption_pages"] = len(caps)
    if not caps:
        if ctx.timeline.word_times:
            ctx.add("captions.missing", "warn", "La timeline no tiene páginas de subtítulo (caption.*).", 0, ctx.duration)
        return
    lo, hi = c["lead_frames"]
    leads, bad = [], []
    for it in caps:
        fw = _first_word(ctx, it)
        if fw is None:
            continue
        wid, ws = fw
        lead_f = (ws - it.t0) * fps
        leads.append(lead_f)
        if not (lo - 0.5 <= lead_f <= hi + 0.5):     # ±0,5 fotograma por el encaje a la rejilla
            bad.append((it, wid, ws, lead_f))
        dur = it.t1 - it.t0
        if dur < c["min_dur_s"] - 1e-3:     # tolerancia de coma flotante (0,2999… = 0,3)
            sev = "block" if dur * fps < c["min_dur_block_frames"] else "warn"
            ctx.add("captions.min_duration", sev, f"Página de subtítulo de {dur:.2f} s en {tc(it.t0)} (mínimo {c['min_dur_s']} s).",
                    it.t0, it.t1, {"dur_s": round(dur, 3), "umbral_s": c["min_dur_s"], "item": it.id},
                    it.decision_ids, [{"op": "merge_caption_page", "item": it.id}])
    if leads:
        import numpy as np
        arr = np.array(leads)
        ctx.metrics["caption_lead_frames"] = {"p5": round(float(np.percentile(arr, 5)), 2), "p50": round(float(np.median(arr)), 2),
                                              "p95": round(float(np.percentile(arr, 95)), 2),
                                              "pct_en_rango": round(100 * float(((arr >= lo - 0.5) & (arr <= hi + 0.5)).mean()), 1)}
    # agrupar páginas desfasadas contiguas en un issue por tramo
    groups: list[list] = []
    for b in bad:
        if groups and b[0].t0 - groups[-1][-1][0].t1 < 1.0 and (b[3] < lo) == (groups[-1][-1][3] < lo):
            groups[-1].append(b)
        else:
            groups.append([b])
    for g in groups:
        late = g[0][3] < lo
        worst_ms = max(abs(x[3]) for x in g) / fps * 1000
        worst_signed = min(x[3] for x in g) if late else max(x[3] for x in g)
        ms = abs(worst_signed) / fps * 1000
        block = (late and ms > c["late_block_ms"]) or ((not late) and ms > c["early_block_ms"])
        msg = (f"{len(g)} página(s) de subtítulo {'entran DESPUÉS de su palabra' if late else 'entran demasiado pronto'} "
               f"({tc(g[0][0].t0)}–{tc(g[-1][0].t1)}; peor {worst_signed:+.1f} fotogramas = {ms:.0f} ms; objetivo 0–2 antes).")
        ctx.add("captions.sync", "block" if block else "warn", msg, g[0][0].t0, g[-1][0].t1,
                {"paginas": [{"item": x[0].id, "palabra": x[1], "t_palabra": round(x[2], 3), "t0": round(x[0].t0, 3),
                              "lead_frames": round(x[3], 2)} for x in g[:12]],
                 "umbral_frames": [lo, hi], "peor_ms": round(worst_ms)},
                [d for x in g for d in x[0].decision_ids],
                [{"op": "retime_captions", "items": [x[0].id for x in g], "lead_frames": 1}])
    # cobertura: palabras dichas fuera de toda página y fuera de las ventanas ocultas
    hidden = _hidden_spans(ctx)
    spans = [(i.t0 - 0.05, i.t1 + 0.05) for i in caps]
    wt_txt = ctx.word_text()
    # palabras que escribe en pantalla un lockup, un CTA o un gráfico que oculta el raíl → cubiertas
    written = [(i.t0 - 0.3, i.t1 + 0.3, set(tokens(" ".join(item_texts(i)))))
               for i in ctx.items(["graphic", "overlay", "caption"]) if item_texts(i)]

    def covered(w: str, s: float) -> bool:
        if any(a <= s <= b for a, b in spans):
            return True
        tk = set(tokens(wt_txt.get(w, "")))
        return bool(tk) and any(a <= s <= b and tk <= toks for a, b, toks in written)
    unc_all = [(w, s) for w, s, e in ctx.words_sorted() if not covered(w, s)]
    # dentro de una ventana oculta a propósito se toleran ≤ 4 palabras sin escribir
    unc = []
    for w, s in unc_all:
        if any(a <= s <= b for a, b in hidden):
            n_in = sum(1 for w2, s2 in unc_all if any(a <= s2 <= b and a <= s <= b for a, b in hidden))
            if n_in <= 4:
                continue
        unc.append((w, s))
    ctx.metrics["words_without_caption"] = len(unc)
    if unc:
        wt = ctx.word_text()
        runs: list[list] = []
        for w, s in unc:
            if runs and s - runs[-1][-1][1] < 1.0:
                runs[-1].append((w, s))
            else:
                runs.append([(w, s)])
        for r in runs:
            if len(r) < 2:
                continue
            txt = " ".join(wt.get(w, w) for w, _ in r)
            ctx.add("captions.coverage", "warn", f"{len(r)} palabras sin subtítulo en {tc(r[0][1])}–{tc(r[-1][1])}: «{txt[:80]}».",
                    r[0][1], r[-1][1] + 0.3, {"palabras": [w for w, _ in r][:20]},
                    ctx.blame(r[0][1], r[-1][1], ["graphic", "layout"]), [{"op": "replan", "reason": "ventana sin subtítulo"}])
    _face_overlap(ctx, caps)


def _overlap_frac(box: tuple[float, float, float, float], reg: tuple[float, float, float, float]) -> float:
    ix = max(0.0, min(box[2], reg[2]) - max(box[0], reg[0]))
    iy = max(0.0, min(box[3], reg[3]) - max(box[1], reg[1]))
    area = max(1e-6, (reg[2] - reg[0]) * (reg[3] - reg[1]))
    return ix * iy / area


def _regions(ctx: QAContext, t: float) -> dict[str, tuple] | None:
    """Zonas de ojos y boca en pantalla: del render (detector de caras, si las cajas son de OCR) o del plan (layout + cámara)."""
    if ctx.render_faces:
        best = min(ctx.render_faces, key=lambda r: abs(r[0] - t))
        if abs(best[0] - t) <= 0.3:
            return {"ojos": best[1], "boca": best[2]}
        # el detector de caras falla en primerísimos planos (cara cortada por el punch): plan, solo si el render está al día
        if any(i.check == "qa.stale_render" for i in ctx.issues):
            return None
    fb = face_screen(ctx, t)
    if fb is None:
        return None
    fx0, fy0, fx1, fy1 = fb
    fw, fh = fx1 - fx0, fy1 - fy0
    return {"ojos": (fx0 + EYES[0] * fw, fy0 + EYES[1] * fh, fx0 + EYES[2] * fw, fy0 + EYES[3] * fh),
            "boca": (fx0 + MOUTH[0] * fw, fy0 + MOUTH[1] * fh, fx0 + MOUTH[2] * fw, fy0 + MOUTH[3] * fh)}


def _face_overlap(ctx: QAContext, caps) -> None:
    """Texto (subtítulo, lockup o gráfico) sobre los ojos o la boca, con la cara situada EN PANTALLA
    (layout + cámara: geometry.face_screen). Sin A-roll visible no se mide."""
    if not ctx.faces and not ctx.render_faces:
        ctx.notes.append("Sin caras (render_spec.aroll.faces ni detección en el render): no se comprueba si el texto tapa boca u ojos.")
        return
    cap_ids = {i.id: i for i in caps}
    items = {i.id: i for i in ctx.timeline.items}
    thr = ctx.cfg["captions"]["face_overlap_block"]
    hits: list[tuple[float, str, float, object, str]] = []
    cache: dict[float, object] = {}
    for b in ctx.boxes:
        it = items.get(b.item or "")
        kind = "caption" if (b.role in ("caption",) or (it is not None and it.component == "caption.rail")) else \
            "lockup" if (b.role == "lockup" or (it is not None and it.component == "caption.lockup")) else \
            "graphic" if (it is not None and it.track in ("graphic", "overlay", "broll")) else None
        if kind is None:
            continue
        if b.t not in cache:
            cache[b.t] = _regions(ctx, b.t)
        regs = cache[b.t]
        if regs is None:
            continue
        for name, reg in regs.items():
            fr = _overlap_frac((b.x0, b.y0, b.x1, b.y1), reg)
            if fr >= thr:
                hits.append((b.t, name, fr, b, kind))
    # agrupar por tipo de texto y continuidad temporal (un issue por tramo, no por palabra)
    step = 1.0 / max(1e-6, ctx.cfg["sampling"]["boxes_fps"] if ctx.boxes_source.startswith("dom") else ctx.cfg["sampling"]["ocr_fps"])
    groups: list[list] = []
    for h in sorted(hits, key=lambda h: (h[4], h[0])):
        if groups and groups[-1][-1][4] == h[4] and h[0] - groups[-1][-1][0] <= 2.5 * step:
            groups[-1].append(h)
        else:
            groups.append([h])
    ctx.metrics["face_overlap_samples"] = len(hits)
    for g in groups:
        t0, t1 = g[0][0], g[-1][0] + step
        parts = sorted({h[1] for h in g})
        worst = max(h[2] for h in g)
        b = max(g, key=lambda h: h[2])[3]
        kind = g[0][4]
        quien = {"caption": "El subtítulo", "lockup": "El lockup", "graphic": "El gráfico"}[kind]
        blame = list(dict.fromkeys(d for h in g for d in (items[h[3].item].decision_ids if h[3].item in items else [])))
        lay = layout_at(ctx, t0)
        ctx.add("captions.face_overlap", "block",
                f"{quien} tapa {' y '.join(parts)} en {tc(t0)}–{tc(t1)} ({worst:.0%} de la zona; «{b.text[:30]}»).",
                t0, t1, {"zona": parts, "fraccion_max": round(worst, 2), "caja": [round(b.x0), round(b.y0), round(b.x1), round(b.y1)],
                         "texto": b.text, "tipo": kind, "layout": lay.component if lay else "layout.full_face (implícito)",
                         "fuente_caja": b.source, "fuente_cara": "render(caras)" if ctx.render_faces else ("dom+render_spec" if ctx.cam_rects else "render_spec+layout(py)")},
                blame or ctx.blame(t0, t1, ["caption", "layout", "graphic"]),
                [{"op": "move_caption_rail" if kind == "caption" else "reflow_component", "item": b.item, "avoid": parts}])
