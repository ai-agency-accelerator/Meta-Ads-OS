"""Informe: veredicto (solo puertas: el juez no decide), resumen en español y `qa_summary.md`."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ..spec import QAIssue, QAReport
from .context import SEV_ORDER, QAContext, tc

LABELS = {
    "audio.true_peak": "pico verdadero por encima de −1 dBTP", "audio.loudness": "sonoridad fuera de −14 LUFS",
    "audio.vmr_word": "el fondo tapa la voz", "audio.vmr_integrated": "música demasiado alta",
    "audio.vmr_window": "voz justa sobre el fondo", "audio.voice_missing": "falta la voz", "audio.long_pause": "pausa larga",
    "audio.dropout": "hueco de audio", "audio.missing": "sin audio",
    "video.black": "parpadeo a negro", "video.freeze": "imagen congelada", "video.duration": "duración distinta de la timeline",
    "video.size": "resolución incorrecta", "video.av_duration": "audio y vídeo de distinta duración",
    "captions.sync": "subtítulos desincronizados", "captions.face_overlap": "subtítulo sobre la cara",
    "captions.min_duration": "subtítulo demasiado breve", "captions.coverage": "palabras sin subtítulo",
    "text.safe_zone": "texto fuera de la zona segura", "text.size": "texto pequeño", "text.clipped": "texto cortado",
    "ct.grounding": "afirmación sin respaldo", "ct.number_context": "cifra sin respaldo", "st.icon_source": "emoji",
    "pacing.dead_gap": "hueco visual", "pacing.hook": "gancho sin cambio visual", "pacing.over_edit": "sobre-edición",
    "ly.concurrent_text": "demasiado texto a la vez", "ly.breathing": "no respira", "sfx.density": "demasiados SFX",
    "sfx.cluster": "racimo de SFX", "sfx.repeat": "SFX repetido", "tr.mid_sentence": "transición a mitad de frase",
    "tr.rate": "demasiadas transiciones", "tr.only_on_block_change": "transición dentro del mismo layout",
    "mo.simultaneous_entries": "todo entra a la vez", "mo.camera_motion_ratio": "cámara siempre en movimiento",
    "mo.punch_dead_zone": "punch-in tibio", "camera.zoom_excess": "zoom excesivo", "sync.trigger_word": "gráfico sin palabra",
    "sync.entry_lead": "gráfico a destiempo", "rd.dwell": "texto que no da tiempo a leer", "mo.orphan_graphic": "gráfico huérfano",
    "logo.canonical": "logo que no es el canónico", "logo.unverified": "logo sin verificar", "ly.caption_rail_jump": "subtítulo que salta de altura",
    "tr.min_gap": "transiciones demasiado seguidas", "cam.punch_density": "demasiados punch-in", "mo.orphan_graphic": "gráfico huérfano",
    "ly.panel_empty": "panel superior vacío", "tr.too_long": "transición larga",
    "mo.ease_tokens": "eases sin sistema", "mo.overshoot_budget": "rebotes en todo", "mo.linear_spatial": "deriva lineal",
}


def label(check: str) -> str:
    return LABELS.get(check, check)


def verdict(issues: list[QAIssue]) -> str:
    gates = [i for i in issues if not i.check.startswith("judge.")]
    if any(i.severity == "block" for i in gates):
        return "fail"
    if any(i.severity == "warn" for i in gates):
        return "warn"
    return "pass"


# orden de importancia para el resumen (lo que más importa primero)
PRIORITY = ["ct.grounding", "logo.canonical", "ly.panel_empty", "audio.voice_missing", "video.black", "video.freeze", "video.duration", "audio.dropout",
            "captions.sync", "captions.face_overlap", "audio.vmr_word", "text.safe_zone", "pacing.hook", "tr.mid_sentence",
            "audio.true_peak", "audio.loudness", "audio.vmr_integrated", "text.size", "st.icon_source", "ct.number_context",
            "captions.coverage", "pacing.dead_gap", "ly.concurrent_text", "sfx.density", "mo.camera_motion_ratio"]
GLOBAL = {"audio.true_peak", "audio.loudness", "audio.vmr_integrated", "sfx.density", "mo.camera_motion_ratio",
          "pacing.over_edit", "tr.rate", "mo.ease_tokens", "mo.overshoot_budget", "video.duration", "video.size"}


def _prio(check: str) -> int:
    return PRIORITY.index(check) if check in PRIORITY else len(PRIORITY)


def summary_es(ctx: QAContext) -> str:
    """«La edición está bien excepto mm:ss–mm:ss (…); cambia estas N decisiones», por gravedad."""
    gates = [i for i in ctx.issues if not i.check.startswith("judge.") and i.severity in ("block", "warn")]
    if not gates:
        return "La edición está bien: pasa todas las puertas deterministas." + _judge_tail(ctx)
    dur = ctx.duration or 1
    by: dict[str, list[QAIssue]] = {}
    for i in gates:
        by.setdefault(i.check, []).append(i)
    order = sorted(by, key=lambda c: (min(SEV_ORDER[i.severity] for i in by[c]), _prio(c)))
    local, glob = [], []
    for c in order:
        lst = sorted(by[c], key=lambda i: (SEV_ORDER[i.severity], i.t0 if i.t0 is not None else 0))
        if c in GLOBAL or all(i.t0 is None or (i.t1 or 0) - i.t0 >= 0.8 * dur for i in lst):
            glob.append(label(c))
            continue
        if len(lst) <= 2:
            for i in sorted(lst, key=lambda i: i.t0 or 0):
                local.append(f"{tc(i.t0)}–{tc(i.t1)} ({label(c)})")
        else:
            secs = sum((i.t1 or i.t0 or 0) - (i.t0 or 0) for i in lst)
            local.append(f"{tc(lst[0].t0)}–{tc(lst[0].t1)} y {len(lst) - 1} tramos más (≈ {secs:.0f} s) ({label(c)})")
    local = list(dict.fromkeys(local))
    txt = "La edición está bien excepto " + "; ".join(local[:7]) if local else "La edición tiene problemas globales"
    if len(local) > 7:
        txt += f"; y {len(local) - 7} tipos de aviso menores"
    if glob:
        txt += ". En todo el vídeo: " + ", ".join(glob[:6])
    blocks = [i for i in gates if i.severity == "block"]
    blame = list(dict.fromkeys(d for i in sorted(blocks, key=lambda i: _prio(i.check)) for d in i.blame))
    blame_w = [d for d in dict.fromkeys(d for i in gates if i.severity == "warn" for d in i.blame) if d not in blame]
    if blame:
        txt += f". Cambia estas {len(blame)} decisiones: " + ", ".join(blame[:12]) + ("…" if len(blame) > 12 else "")
        if blame_w:
            txt += f" (y revisa {len(blame_w)} más con avisos)"
    elif blame_w:
        txt += f". Revisa estas {len(blame_w)} decisiones con avisos: " + ", ".join(blame_w[:10]) + ("…" if len(blame_w) > 10 else "")
    else:
        txt += ". La timeline no trae decision_ids: no hay decisiones culpables que cambiar automáticamente"
    nb = len(blocks)
    txt += f". ({nb} bloqueante{'s' if nb != 1 else ''}, {len(gates) - nb} aviso{'s' if len(gates) - nb != 1 else ''}.)"
    return txt + _judge_tail(ctx)


def _judge_tail(ctx: QAContext) -> str:
    j = ctx.metrics.get("judge", {})
    if j.get("status") == "ok":
        return f" El juez Gemini añade {j.get('issues', 0)} observaciones (ordenan, no deciden)."
    return ""


def build(ctx: QAContext) -> QAReport:
    ctx.issues.sort(key=lambda i: (SEV_ORDER[i.severity], i.check.startswith("judge."), i.t0 if i.t0 is not None else -1))
    for k, i in enumerate(ctx.issues):
        i.id = f"Q-{k + 1:04d}"
    return QAReport(slug=ctx.slug, version=ctx.vid, verdict=verdict(ctx.issues), summary_es=summary_es(ctx),
                    issues=ctx.issues, metrics=ctx.metrics)


def write_md(ctx: QAContext, rep: QAReport, sheets: list[Path]) -> Path:
    L = [f"# QA de `{rep.slug}/{rep.version}` — {rep.verdict.upper()}", "", rep.summary_es, ""]
    m = rep.metrics
    L += ["## Métricas", "",
          f"- Sonoridad: I = {m.get('lufs_i')} LUFS · LRA = {m.get('lra')} LU · pico verdadero = {m.get('true_peak_dbtp')} dBTP"
          + (f" · voz − fondo = {m.get('lrd_lu')} LU" if m.get("lrd_lu") is not None else ""),
          f"- Duración: render {m.get('render_duration_s')} s · timeline {m.get('timeline_duration_s')} s · {m.get('render_fps')} fps",
          f"- Subtítulos: {m.get('caption_pages', 0)} páginas · lead (fotogramas) {m.get('caption_lead_frames')} · sin subtítulo {m.get('words_without_caption')} palabras",
          f"- Texto: {m.get('text_boxes')} · zona segura {m.get('safe_zone')} · tamaños {m.get('text_px')}",
          f"- Ritmo: {m.get('pacing')}",
          f"- Motion: medidas {', '.join(m.get('motion_gates_measured', []))}",
          f"- Sin medir aún: {', '.join(m.get('motion_gates_skipped', [])) or '—'}", ""]
    j = m.get("judge") or {}
    if j.get("status") == "ok":
        L += ["## Juez Gemini (ordena, no decide)", "", f"- Modelo {j.get('model')} · puntuación ponderada de la rúbrica "
              f"{j.get('score_ponderado')} · {j.get('issues')} observaciones · {j.get('wall_s')} s", f"- {j.get('resumen')}", ""]
        noes = [r for r in j.get("rubrica", []) if not str(r.get("respuesta", "")).lower().startswith("s")]
        if noes:
            L += ["Preguntas con «no»: " + "; ".join(f"{r.get('id')} ({r.get('nota', '')[:90]})" for r in noes), ""]
    elif j:
        L += [f"Juez: {j.get('status')} — {j.get('reason', '')}", ""]
    L += ["## Issues", "", "| id | sev | check | tramo | qué pasa | culpables |", "|---|---|---|---|---|---|"]
    for i in rep.issues:
        tr = f"{tc(i.t0)}–{tc(i.t1)}" if i.t0 is not None else "global"
        msg = i.message.replace("|", "/")
        L.append(f"| {i.id} | {i.severity} | `{i.check}` | {tr} | {msg} | {', '.join(i.blame[:6]) or '—'} |")
    L += ["", "## Hojas de contacto", ""] + [f"- `{p.name}`" for p in sheets]
    if ctx.notes:
        L += ["", "## Notas", ""] + [f"- {n}" for n in ctx.notes]
    p = ctx.vdir / "qa_summary.md"
    p.write_text("\n".join(L) + "\n", encoding="utf-8")
    return p
