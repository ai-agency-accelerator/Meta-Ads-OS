"""Puertas de motion medibles (`recursos/qa_motion_gates.yaml`): se miden sobre la timeline, el plan,
el audio planificado y los tweens GSAP del proyecto HF. Las que piden píxeles finos (contraste, estrobo, márgenes)
quedan para una iteración posterior y se listan en `metrics.motion_gates_skipped`.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict

from .config import gate_severity, motion_gates, motion_thresholds
from .context import QAContext, cam_kind, item_texts, tc

ENTRY_TRACKS = ("graphic", "broll", "overlay")
SENT_END = (".", "?", "!", "…")


def _src(wid: str) -> str:
    """Fuente de una palabra por su id (main_w0001 → main)."""
    return wid.rsplit("_w", 1)[0] if "_w" in wid else ""


def _all_decisions(ctx: QAContext) -> dict:
    """Decisiones del plan + las del cierre del perfil que el plan no copia (`outro.plan` del perfil y sus variantes)."""
    if getattr(ctx, "_dec_all", None) is None:
        import json

        from ..paths import RAIZ
        from ..spec import Decision

        dec = dict(ctx.decisions())
        try:
            from ..compile import load_profile
            o = load_profile(ctx.plan.format if ctx.plan else "anuncio").get("outro") or {}
            planes = [o.get("plan")] + [v.get("plan") for v in (o.get("variants") or {}).values()]
        except Exception:                                   # noqa: BLE001 — sin perfil: solo las del plan
            planes = []
        for p in [RAIZ / x for x in planes if x and (RAIZ / x).is_file()]:
            try:
                for d in json.loads(p.read_text(encoding="utf-8")).get("decisions", []):
                    if d.get("id") not in dec:
                        try:
                            dec[d["id"]] = Decision.model_validate(d)
                        except Exception:
                            pass
            except Exception:
                pass
        ctx._dec_all = dec  # type: ignore[attr-defined]
    return ctx._dec_all  # type: ignore[attr-defined]


def _anchor_time(ctx: QAContext, it) -> tuple[str, float] | None:
    dec = _all_decisions(ctx)
    wt = ctx.timeline.word_times
    for d in it.decision_ids:
        if d in dec and dec[d].anchor.start in wt:
            w = dec[d].anchor.start
            return w, float(wt[w][0] if dec[d].anchor.start_edge == "s" else wt[w][1])
    return None


def _sentence_end_after(ctx: QAContext, t: float) -> float | None:
    punct = ctx.word_punct()
    for wid, s, e in ctx.words_sorted():
        if s >= t - 0.05 and punct.get(wid, "").strip()[-1:] in SENT_END:
            return e
    return None


def _aroll_width(ctx: QAContext) -> int:
    """Ancho real del A-roll que usa el render (hf/<aroll.src>); si no, el de las fuentes del MediaIndex."""
    src = (ctx.render_spec.get("aroll") or {}).get("src")
    if src and (ctx.vdir / "hf" / src).exists():
        try:
            from .media import probe

            w = probe(ctx.vdir / "hf" / src).get("width")
            if w:
                return int(w)
        except Exception:
            pass
    return max((s.width for s in (ctx.media_index.sources if ctx.media_index else [])), default=ctx.timeline.width)


def run(ctx: QAContext) -> None:
    th = motion_thresholds()
    ctx.cfg["motion"] = th
    dur = ctx.duration or 1.0
    measured, skipped = [], []

    # ─── mo.simultaneous_entries
    ents = sorted((i for i in ctx.items(ENTRY_TRACKS) if not i.props.get("stagger_group")), key=lambda i: i.t0)
    win = th["simultaneous_window_s"]
    flagged = set()
    for k, it in enumerate(ents):
        grp = [x for x in ents[k:] if x.t0 - it.t0 <= win]
        if len(grp) > th["simultaneous_max"] and it.id not in flagged:
            flagged.update(x.id for x in grp)
            ctx.add("mo.simultaneous_entries", gate_severity("mo.simultaneous_entries"),
                    f"{len(grp)} elementos entran a la vez en {tc(it.t0)} (máx. {th['simultaneous_max']} en {win * 1000:.0f} ms).",
                    it.t0, it.t0 + win, {"items": [x.id for x in grp], "componentes": [x.component for x in grp]},
                    [d for x in grp for d in x.decision_ids], [{"op": "stagger", "items": [x.id for x in grp], "follow": "words"}])
    measured.append("mo.simultaneous_entries")

    # ─── sfx.density (+ sfx.repeat, sfx.cluster) y sfx.silent_block: en GESTOS desde el 18-oct-2026 (checks_audio)
    from .checks_audio import check_sfx_density, check_sfx_silent_blocks, check_sfx_visual_sync_px
    got = check_sfx_density(ctx, th)
    if got:
        measured += got
    else:
        skipped.append("sfx.density (sin SFX en timeline.audio)")
    measured += check_sfx_silent_blocks(ctx, th)
    try:                                               # sincronía por píxeles (necesita el render y las cajas del DOM)
        measured += check_sfx_visual_sync_px(ctx)
    except Exception as exc:                           # noqa: BLE001
        ctx.notes.append(f"sfx.visual_sync por píxeles sin medir: {type(exc).__name__}: {str(exc)[:160]}")

    # ─── transiciones: tr.rate, tr.mid_sentence, tr.only_on_block_change
    trs = sorted(ctx.items(["transition"]), key=lambda i: i.t0)
    lim = th["tr_per_min_short"] if ctx.is_short else th["tr_per_min_long"]
    tpm = len(trs) / dur * 60
    ctx.metrics["transitions_per_min"] = round(tpm, 2)
    if tpm > lim:
        ctx.add("tr.rate", gate_severity("tr.rate"), f"{tpm:.1f} transiciones con efecto por minuto (máx. {lim}).", 0, dur,
                {"n": len(trs), "por_min": round(tpm, 2), "umbral": lim}, [d for t in trs for d in t.decision_ids],
                [{"op": "replace_transition", "with": "corte_seco", "where": "dentro del mismo layout"}])
    words = ctx.words_sorted()
    punct = ctx.word_punct()
    layouts = [i.t0 for i in ctx.items(["layout"])]
    wt_text = ctx.word_text()

    def _inside_sentence(t: float) -> tuple[str, str, float] | None:
        """¿El instante t cae dentro de una frase? (entre dos palabras con pausa corta y sin fin de frase, o dentro de
        una palabra que no cierra frase). Devuelve (palabra antes, palabra después, pausa)."""
        for k, (wid, s, e) in enumerate(words):
            if s < t < e and punct.get(wid, "").strip()[-1:] not in SENT_END and k + 1 < len(words) \
                    and _src(wid) == _src(words[k + 1][0]):
                return wid, words[k + 1][0], 0.0
        prev = [w for w in words if w[2] <= t]
        nxt = [w for w in words if w[1] >= t]
        if prev and nxt and nxt[0][1] - prev[-1][2] < th["tr_mid_sentence_pause_s"] \
                and punct.get(prev[-1][0], "").strip()[-1:] not in SENT_END \
                and _src(prev[-1][0]) == _src(nxt[0][0]):          # main → outro es cambio de bloque válido
            return prev[-1][0], nxt[0][0], nxt[0][1] - prev[-1][2]
        return None
    for tr in trs:
        mid = (tr.t0 + tr.t1) / 2
        cut = float(tr.cues.get("cut", mid))           # el instante del corte (cues.cut), no la ventana del efecto
        hit = _inside_sentence(cut)
        if hit:
            a, b, pause = hit
            ctx.add("tr.mid_sentence", gate_severity("tr.mid_sentence"),
                    f"Transición {tr.component or ''} a mitad de frase en {tc(tr.t0)}–{tc(tr.t1)} "
                    f"(«{wt_text.get(a, a)} | {wt_text.get(b, b)}»).",
                    tr.t0, tr.t1, {"entre": [a, b], "pausa_s": round(pause, 3), "item": tr.id},
                    tr.decision_ids, [{"op": "move_transition", "item": tr.id, "to": "fin_de_frase"}])
        if layouts and not any(abs(l - mid) <= 0.35 for l in layouts):
            ctx.add("tr.only_on_block_change", gate_severity("tr.only_on_block_change"),
                    f"Transición con efecto en {tc(tr.t0)} sin cambio de layout: dentro del layout, corte seco.",
                    tr.t0, tr.t1, {"item": tr.id}, tr.decision_ids, [{"op": "replace_transition", "item": tr.id, "with": "corte_seco"}])
    measured += ["tr.rate", "tr.mid_sentence" if punct else "tr.mid_sentence(sin puntuación: solo pausa)", "tr.only_on_block_change"]

    # ─── presupuesto de transiciones y densidad de punch (motion/camara_transiciones.yaml)
    for a, b in zip(trs, trs[1:]):
        if b.t0 - a.t0 < 2.5:
            ctx.add("tr.min_gap", "warn", f"Dos transiciones con efecto separadas {b.t0 - a.t0:.1f} s ({tc(a.t0)} y {tc(b.t0)}; mín. 2,5 s).",
                    a.t0, b.t1, {"sep_s": round(b.t0 - a.t0, 2)}, a.decision_ids + b.decision_ids,
                    [{"op": "replace_transition", "item": b.id, "with": "corte_seco"}])
    for tr in trs:
        if tr.t1 - tr.t0 > 0.4 + 1e-3 and not tr.props.get("riser"):
            ctx.add("tr.too_long", "info", f"Transición de {tr.t1 - tr.t0:.2f} s en {tc(tr.t0)} (máx. 0,4 s salvo riser).",
                    tr.t0, tr.t1, {"dur_s": round(tr.t1 - tr.t0, 2)}, tr.decision_ids, [{"op": "retime", "item": tr.id, "dur_s": 0.3}])
    punches = sorted(c.t0 for c in ctx.items(["camera"]) if cam_kind(c).startswith("punch"))
    dense = [(a, b) for a, b in zip(punches, punches[1:]) if b - a < 2.0]
    if len(dense) >= 2:
        ctx.add("cam.punch_density", "warn", f"{len(dense)} pares de punch-in a menos de 2 s (máx. 1 punch cada 2 s).",
                dense[0][0], dense[-1][1], {"pares": [[round(a, 2), round(b, 2)] for a, b in dense[:10]]},
                ctx.blame(dense[0][0], dense[-1][1], ["camera"])[:10], [{"op": "remove_punch", "keep": "los de énfasis"}])
    measured += ["tr.min_gap", "cam.punch_density"]

    # ─── cámara: mo.camera_motion_ratio, mo.punch_dead_zone, zoom excesivo
    cams = sorted(ctx.items(["camera"]), key=lambda i: i.t0)
    moving = [c for c in cams if cam_kind(c) in ("slow_push", "push", "zoom", "drift", "ken_burns", "pan", "zoom_out")]
    mov_s = sum(c.t1 - c.t0 for c in moving)
    pct = 100 * mov_s / dur
    ctx.metrics["camera_motion_pct"] = round(pct, 1)
    if pct > th["camera_motion_pct_max"]:
        ctx.add("mo.camera_motion_ratio", gate_severity("mo.camera_motion_ratio"),
                f"La cámara virtual se mueve el {pct:.0f} % del tiempo (máx. {th['camera_motion_pct_max']} %).", 0, dur,
                {"pct": round(pct, 1)}, [d for c in moving for d in c.decision_ids][:30],
                [{"op": "set_camera", "kind": "hold", "where": "planos sin énfasis"}])
    prev_scale, prev_end = 1.0, None
    srcw = _aroll_width(ctx)
    dz = th["punch_dead_zone"]
    for c in cams:
        sc = c.props.get("scale")
        if not isinstance(sc, (int, float)) or cam_kind(c) in [cam_kind(m) for m in moving]:
            continue   # solo estados discretos (punch/reframe/hold); los movimientos continuos no son «saltos»
        if prev_end is not None and prev_end <= c.t0 + 1e-3:
            prev_scale = 1.0        # el punch anterior ya volvió a ×1 (out: cut/ease)
        ratio = max(sc, prev_scale) / max(1e-6, min(sc, prev_scale))
        if cam_kind(c).startswith("punch") and dz[0] <= ratio <= dz[1]:
            ctx.add("mo.punch_dead_zone", gate_severity("mo.punch_dead_zone"),
                    f"Punch-in tibio de {100 * (ratio - 1):.0f} % en {tc(c.t0)}: o 0 % o ≥ 12 %.", c.t0, c.t0 + 0.3,
                    {"ratio": round(ratio, 3), "zona_prohibida": list(dz)}, c.decision_ids,
                    [{"op": "set_camera", "item": c.id, "scale": round(prev_scale * 1.15, 3)}])
        eff = sc * ctx.timeline.width / max(1, srcw)
        if eff > th["zoom_warn"]:
            ctx.add("camera.zoom_excess", "block" if eff > th["zoom_block"] else "warn",
                    f"Zoom efectivo {eff:.2f}× sobre la resolución de origen en {tc(c.t0)} (se nota la ampliación).",
                    c.t0, c.t1, {"scale": sc, "src_width": srcw, "efectivo": round(eff, 2)}, c.decision_ids,
                    [{"op": "limit_scale", "item": c.id, "max": round(srcw / ctx.timeline.width * th["zoom_warn"], 2)}])
        prev_scale, prev_end = sc, (c.t1 if c.props.get("out", "cut") != "hold" else None)
    measured += ["mo.camera_motion_ratio", "mo.punch_dead_zone", "camera.zoom_excess"]

    # ─── sincronía con la voz: sync.trigger_word, sync.entry_lead
    lo, hi = th["entry_lead_ms"]
    leads = []
    for it in ctx.items(["graphic", "broll"]):
        if not it.decision_ids:
            ctx.add("sync.trigger_word", gate_severity("sync.trigger_word", "block"),
                    f"El ítem {it.id} ({it.component}, {tc(it.t0)}) no apunta a ninguna decisión: sin palabra disparadora ni porqué.",
                    it.t0, it.t1, {"item": it.id}, [], [{"op": "remove_component", "item": it.id}])
            continue
        if not ctx.plan:
            continue
        at = _anchor_time(ctx, it)
        if at is None:
            ctx.add("sync.trigger_word", gate_severity("sync.trigger_word", "block"),
                    f"La decisión de {it.id} ({tc(it.t0)}) no ancla a una palabra que sobreviva al corte.",
                    it.t0, it.t1, {"item": it.id}, it.decision_ids, [{"op": "replan", "reason": "anclar a palabra"}])
            continue
        ms = (it.t0 - at[1]) * 1000
        leads.append((it, at[0], ms))
    if leads:
        ok = [x for x in leads if lo <= x[2] <= hi + th["entry_late_tol_ms"]]   # rango + tolerancia tarde
        pct_ok = 100 * len(ok) / len(leads)
        ctx.metrics["entry_lead"] = {"n": len(leads), "pct_en_rango": round(pct_ok, 1),
                                     "p50_ms": round(sorted(x[2] for x in leads)[len(leads) // 2])}
        for it, w, ms in leads:
            if ms > hi + th["entry_late_tol_ms"] or ms < lo - 250:
                ctx.add("sync.entry_lead", gate_severity("sync.entry_lead"),
                        f"{it.id} entra {abs(ms):.0f} ms {'después' if ms > 0 else 'antes'} de su palabra {w} ({tc(it.t0)}); "
                        f"objetivo {-hi:.0f}–{-lo:.0f} ms antes.",
                        it.t0, it.t0 + 0.3, {"lead_ms": round(ms), "rango_ms": [lo, hi], "palabra": w}, it.decision_ids,
                        [{"op": "retime", "item": it.id, "lead_ms": -155}])
        if pct_ok < th["entry_pct_min"]:
            ctx.add("sync.entry_lead", "info", f"Solo el {pct_ok:.0f} % de los recursos entra en la ventana de antelación (mín. {th['entry_pct_min']} %).",
                    evidence={"pct": round(pct_ok, 1)})
    measured += ["sync.trigger_word", "sync.entry_lead" if ctx.plan else "sync.entry_lead(sin plan)"]

    # ─── ct.no_cover_up (warn, 17-oct-2026): un gráfico de pantalla completa no existe solo para tapar un jump cut.
    #     Cortes del EDL = saltos dentro de una misma fuente entre tramos de A-roll. Pantalla completa = layout
    #     broll_full activo en su entrada, o el gráfico pinta su propio lienzo. Salta si entra a ±2 f de un corte y su
    #     decisión es «eliminar_pausa_o_error» o no tiene palabra disparadora en su entrada (−0,25…+0,6 s).
    fr = 1.0 / (ctx.fps or 30)
    segs = sorted(ctx.timeline.aroll, key=lambda s: s.prog_in)
    jumps = [b.prog_in for a, b in zip(segs, segs[1:]) if a.src == b.src and abs(b.src_in - a.src_out) > fr]
    # + saltos de toma DENTRO de la fuente (el bruto puede llegar ya cortado): la caché de `clipcuts` que deja compile
    try:
        import json as _json
        cc = _json.loads((ctx.vdir.parent.parent / "media" / "clip_cuts.json").read_text())
        for s in segs:
            for c in (cc.get(s.src) or {}).get("cuts", []):
                if s.src_in + 1e-3 < c < s.src_out - 1e-3:
                    jumps.append(s.prog_in + (c - s.src_in))
    except Exception:                                                  # noqa: BLE001 — sin caché: solo los del EDL
        pass
    lays = sorted(ctx.items(["layout"]), key=lambda i: i.t0)

    # ─── mo.abrupt_exit (warn, 18-oct-2026; antes «sin medir»): un gráfico que sale en seco (`exit: "cut"`: desaparece
    #     en 1 fotograma) solo vale si ese fotograma es un corte de plano: cambio de layout, transición o salto del A-roll
    #     (±1 f), o si le sigue la MISMA pieza que continúa su estado (mismo componente a ±1 f en el mismo panel: la
    #     rejilla con `carry`, un diagrama que sigue). Dentro de un panel, compile.py ya da salida animada corta (5 f).
    cuts_ab = sorted({round(l.t0, 4) for l in lays} | {round(l.t1, 4) for l in lays}
                     | {round(t.t0, 4) for t in ctx.items(["transition"])} | {round(t.t1, 4) for t in ctx.items(["transition"])}
                     | {round(c, 4) for c in jumps} | {round(ctx.duration, 4)})
    vis_ab = sorted(ctx.items(["graphic", "broll", "overlay"]), key=lambda i: i.t0)
    # 20-oct-2026: una captura o vídeo REAL (pista broll, media.*, scene.*) sale en corte seco a propósito (compile.py:
    # nunca se cruza con otra pieza), y entrar en una captura real también es un corte de plano: ninguno es «brusco»
    real = lambda i: i.track == "broll" or str(i.component or "").startswith(("media.", "scene."))
    abrupt = []
    for it in vis_ab:
        if (it.props or {}).get("exit") != "cut":
            continue
        if any(abs(it.t1 - c) <= fr + 1e-3 for c in cuts_ab):
            continue
        if real(it) or any(o is not it and real(o) and abs(o.t0 - it.t1) <= fr + 1e-3 for o in vis_ab):
            continue
        # continúa en la pieza siguiente: mismo componente, o una que nace de su geometría (`from`: title.header desde el
        # héroe de logo.reveal) o arrastra su estado (`carry`/`carry_from`)
        if any(o is not it and abs(o.t0 - it.t1) <= fr + 1e-3 and (o.component == it.component or isinstance((o.props or {}).get("from"), dict)
               or (o.props or {}).get("carry") or (o.props or {}).get("carry_from") is not None) for o in vis_ab):
            continue
        abrupt.append(it)
    for it in abrupt:
        ctx.add("mo.abrupt_exit", gate_severity("mo.abrupt_exit", "warn"),
                f"{it.id} ({it.component}) desaparece en un fotograma en {tc(it.t1)} sin corte de plano ni salida animada.",
                max(0.0, it.t1 - 0.2), it.t1 + 0.2, {"exit": "cut", "t1": round(it.t1, 3)}, it.decision_ids,
                [{"op": "set_prop", "item": it.id, "exit": "fade", "reason": "salida animada corta (5 f) dentro del panel"}])
    ctx.metrics["abrupt_exit"] = {"n": len(abrupt), "items": [i.id for i in abrupt][:20]}
    measured.append("mo.abrupt_exit")

    decs_all = _all_decisions(ctx) if ctx.plan else {}
    for it in ctx.items(["graphic", "broll"]):
        cut = next((c for c in jumps if abs(it.t0 - c) <= 2 * fr + 1e-6), None)
        if cut is None:
            continue
        lay = [l for l in lays if l.t0 <= it.t0 + 1e-3 < l.t1]
        full = (lay and lay[-1].component == "layout.broll_full") or it.track == "broll" \
            or (it.props.get("backdrop") not in (None, "none", "auto")) or bool(it.props.get("paint_canvas"))
        if not full:
            continue
        codes = {getattr(getattr(decs_all.get(d), "motive", None), "code", None) for d in it.decision_ids}
        at = _anchor_time(ctx, it) if ctx.plan else None
        trig = at is not None and -0.25 <= at[1] - it.t0 <= 0.6
        if "eliminar_pausa_o_error" in codes or not trig:
            ctx.add("ct.no_cover_up", gate_severity("ct.no_cover_up", "warn"),
                    f"{it.id} ({it.component}) entra a pantalla completa justo en un corte del A-roll ({tc(cut)})"
                    + (" con el porqué «eliminar pausa o error»" if "eliminar_pausa_o_error" in codes
                       else " sin palabra que lo dispare en su entrada") + ": parece que tapa el corte.",
                    it.t0, min(it.t1, it.t0 + 0.6), {"corte": round(cut, 3), "palabra": at[0] if at else None,
                                                      "palabra_t": round(at[1], 3) if at else None},
                    it.decision_ids, [{"op": "retime", "item": it.id, "to": "palabra disparadora"}])
    measured.append("ct.no_cover_up" if ctx.plan else "ct.no_cover_up(sin plan)")

    # ─── rd.dwell, mo.orphan_graphic, mo.component_repeat
    reps = Counter()
    for it in ctx.items(["graphic"]):
        txt = " ".join(item_texts(it))
        need = max(th["dwell_min_s"], len(txt) / th["dwell_chars_per_s"] + th["dwell_extra_s"]) if txt else 0
        if txt and it.t1 - it.t0 < need:
            ctx.add("rd.dwell", gate_severity("rd.dwell"),
                    f"{it.id} dura {it.t1 - it.t0:.2f} s y su texto ({len(txt)} caracteres) necesita {need:.2f} s para leerse.",
                    it.t0, it.t1, {"dur_s": round(it.t1 - it.t0, 2), "necesita_s": round(need, 2), "texto": txt[:80]},
                    it.decision_ids, [{"op": "extend", "item": it.id, "to_s": round(need, 2)}, {"op": "shorten_text", "item": it.id}])
        reps[(it.component, str(it.props.get("preset") or it.props.get("enter") or ""))] += 1
        if ctx.plan and not it.props.get("hold") and not it.props.get("sostener"):
            at = _anchor_time(ctx, it)
            if at:
                end = _sentence_end_after(ctx, at[1])
                if end is not None and it.t1 > end + th["orphan_after_s"]:
                    nxt_words = [w for w in words if end < w[1] < it.t1]
                    if nxt_words:
                        ctx.add("mo.orphan_graphic", gate_severity("mo.orphan_graphic"),
                                f"{it.id} sigue en pantalla {it.t1 - end:.1f} s después de acabar su frase ({tc(end)}).",
                                end, it.t1, {"fin_frase": round(end, 2), "t1": it.t1}, it.decision_ids,
                                [{"op": "trim", "item": it.id, "t1": round(end + 0.3, 2)}])
    for (comp, preset), n in reps.items():
        if comp and n > th["component_repeat_max_short"] and ctx.is_short:
            ctx.add("mo.component_repeat", gate_severity("mo.component_repeat", "info"),
                    f"El componente {comp} se repite {n} veces con la misma animación.", evidence={"n": n, "preset": preset})
    measured += ["rd.dwell", "mo.component_repeat", "mo.orphan_graphic" if ctx.plan else "mo.orphan_graphic(sin plan)"]

    # ─── mo.text_entry (block): TODO texto entra animado (regla de estilo). Dos pruebas:
    #     plan → `enter: "cut"` en un componente de texto; DOM (20-oct-2026, kit v14) → hoja de texto nueva en los 8
    #     primeros fotogramas del bloque o de su cue que llega al 90 % de su meseta en < 5 f Y se mueve < 20 px
    #     (boxes._entry_probe; con el bloque en t = 0, lo visible en el primer fotograma también cuenta)
    sev_te = gate_severity("mo.text_entry", "block")
    no_text = ("media.", "layout.", "camera.", "transition", "caption", "scene.capture3d")
    for it in ctx.items(["graphic", "overlay"]):
        if it.props.get("enter") == "cut" and it.component and not str(it.component).startswith(no_text):
            ctx.add("mo.text_entry", sev_te,
                    f"{it.id} ({it.component}) lleva `enter: \"cut\"`: prohibido en texto, el texto tiene que entrar animado.",
                    it.t0, min(it.t1, it.t0 + 0.5), {"enter": "cut"}, it.decision_ids,
                    [{"op": "set", "item": it.id, "path": "params.props.enter", "value": None}])
    te_cases = ctx.metrics.pop("_text_entry", None)
    if te_cases is not None:
        by_item: dict[str, list] = {}
        for c in te_cases:
            by_item.setdefault(c["item"], []).append(c)
        for iid, cs in by_item.items():
            c0 = cs[0]
            txt = " · ".join(sorted({c["texto"] for c in cs}))[:120]
            ctx.add("mo.text_entry", sev_te,
                    f"Texto sin animación de entrada en {iid}: «{txt}» aparece casi de golpe"
                    + (" (en su palabra" if c0["en_cue"] else " (al empezar el bloque") + f", {tc(c0['t'])})"
                    + (f"; {c0['prueba']}" if c0.get("prueba") else "") + ".",
                    c0["t"], c0["t"] + 0.5, {"casos": cs[:6]}, c0["decision_ids"],
                    [{"op": "component_fix", "reason": "el texto entra con gx.textIn (8 f: subida de 32 px y opacidad "
                      "≈ power2.out, o máscara yPercent 110 → 0): ≥ 5 f hasta el 90 % o ≥ 20 px de recorrido"}])
        measured.append("mo.text_entry")
    else:
        measured.append("mo.text_entry(solo plan: sin DOM)")

    # ─── ly.line_parity (warn; regla de estilo: si dos rótulos paralelos tienen 2 líneas, el tercero también):
    #     en un grupo de rótulos paralelos (marcados por gx.lineParity), todos con el mismo número de líneas en pantalla
    lp = ctx.metrics.pop("_line_parity", None)
    if lp is not None:
        for c in lp.get("fallos", []):
            desc = ", ".join(f"«{x['text']}» {x['lines']}" for x in c["rotulos"])
            ctx.add("ly.line_parity", gate_severity("ly.line_parity", "warn"),
                    f"Rótulos paralelos de {c['item']} ({c['grupo']}) con distinto número de líneas: {desc}.",
                    c["t"], c["t"] + 0.5, {"rotulos": c["rotulos"]}, c["decision_ids"],
                    [{"op": "component_fix", "reason": "todos en una línea, o todos partidos en dos de forma equilibrada (gx.lineParity)"}])
        ctx.metrics["line_parity"] = {"grupos": lp.get("grupos", 0), "fallos": len(lp.get("fallos", []))}
        measured.append("ly.line_parity")
    else:
        skipped.append("ly.line_parity (sin DOM)")

    # ─── ly.breathing: al menos un tramo limpio de ≥ 2 s cada 20 s
    busy = sorted((i.t0, i.t1) for i in ctx.items(["graphic", "broll"]))
    every, clean = th["breathing_every_s"], th["breathing_clean_s"]
    if busy:
        t = 0.0
        while t < dur - 1.0:
            w1 = min(dur, t + every)
            free, cur, best = [], t, 0.0
            for s, e in busy:
                if e <= t or s >= w1:
                    continue
                best = max(best, s - cur)
                cur = max(cur, e)
            best = max(best, w1 - cur)
            if best < clean and w1 - t >= every * 0.75:
                ctx.add("ly.breathing", gate_severity("ly.breathing"),
                        f"Entre {tc(t)} y {tc(w1)} no hay ningún tramo de {clean:.0f} s sin gráficos (máx. limpio {best:.1f} s).",
                        t, w1, {"max_limpio_s": round(best, 2)}, ctx.blame(t, w1, ["graphic", "broll"])[:12],
                        [{"op": "remove_component", "reason": "dejar respirar: cara sola en la frase clave"}])
            t += every
    measured.append("ly.breathing")

    # ─── tweens GSAP: mo.ease_tokens, mo.overshoot_budget, mo.linear_spatial
    if ctx.tweens:
        tw = [t for t in ctx.tweens if t.get("dur", 0) > 0]
        # el lineal con papel declarado (progress, typing, scroll, path: una velocidad constante, no una curva) no cuenta
        # como ease del sistema (18-oct-2026; el runtime cierra el resto a los 4 tokens: enter, exit, move, pop)
        roles_lin = ("scroll", "progress", "typing", "path")
        eases = Counter(t["ease"] for t in tw if not (t["ease"] in ("none", "linear", "power0") and (t.get("role") or "") in roles_lin))
        spatial = {"x", "y", "scale", "scaleX", "scaleY", "rotation", "xPercent", "yPercent"}
        over = [t for t in tw if re.match(r"(back|elastic|bounce)", t["ease"])]
        params = sorted({float(m.group(1)) for t in over if (m := re.search(r"\(([\d.]+)", t["ease"]))})
        lin = [t for t in tw if t["ease"] in ("none", "linear", "power0") and set(t["props"]) & spatial
               and (t.get("role") or "") not in roles_lin]
        ctx.metrics["tweens"] = {"n": len(tw), "eases_distintos": len(eases), "overshoot_pct": round(100 * len(over) / max(1, len(tw)), 1),
                                 "overshoot_valores": params, "lineales_espaciales": len(lin), "top_eases": eases.most_common(6)}
        if len(eases) > th["eases_max"]:
            ctx.add("mo.ease_tokens", gate_severity("mo.ease_tokens"),
                    f"{len(eases)} eases distintos (máx. {th['eases_max']}): el movimiento no tiene un sistema.",
                    evidence={"eases": dict(eases.most_common(12))}, fix=[{"op": "map_eases_to_tokens"}])
        if over and (100 * len(over) / len(tw) > th["overshoot_pct_max"] or len(params) > 1
                     or any(p > th["overshoot_param_max"] for p in params) or any(t["ease"].startswith(("elastic", "bounce")) for t in over)):
            ctx.add("mo.overshoot_budget", gate_severity("mo.overshoot_budget"),
                    f"Rebotes en {len(over)}/{len(tw)} tweens ({100 * len(over) / len(tw):.0f} %), con {len(params)} sobreimpulsos distintos "
                    f"{params[:8]} (máx. {th['overshoot_pct_max']} %, un único valor ≤ {th['overshoot_param_max']}).",
                    evidence={"n": len(over), "valores": params}, fix=[{"op": "map_eases_to_tokens", "overshoot": "solo foco del beat"}])
        if lin:
            t0 = min(t["start"] for t in lin)
            ctx.add("mo.linear_spatial", gate_severity("mo.linear_spatial"),
                    f"{len(lin)} tweens lineales de posición/escala (deriva mecánica), el primero en {tc(t0)}.",
                    t0, None, {"n": len(lin), "ejemplos": [{"t": round(t['start'], 2), "props": t['props'], "targets": t['targets']} for t in lin[:6]]},
                    ctx.blame(t0, t0 + 0.5, ["camera"]), [{"op": "map_eases_to_tokens"}])
        measured += ["mo.ease_tokens", "mo.overshoot_budget", "mo.linear_spatial"]
    else:
        skipped.append("mo.ease_tokens/overshoot/linear (sin tweens GSAP legibles)")

    all_ids = [g.get("id") for g in motion_gates().get("gates", []) or []]
    done = {m.split("(")[0] for m in measured} | {"rd.safe_zone", "rd.text_size", "ly.concurrent_text", "ly.caption_rail_jump", "ct.grounding",
                                                    "ct.number_context", "st.icon_source"}
    ctx.metrics["motion_gates_measured"] = sorted(done & set(all_ids)) if all_ids else sorted(done)
    ctx.metrics["motion_gates_skipped"] = sorted(set(all_ids) - done) + skipped
