"""Afirmaciones (`ct.grounding`, block): todo ítem `graphic` cuyo texto no sale de la transcripción debe tener
`source` en su decisión del plan. También cifras sin respaldo (`ct.number_context`) y emojis (`st.icon_source`).

Respaldo por transcripción: ≥ 60 % de los tokens de contenido de cada cadena aparecen en las palabras dichas en
±10 s (texto de `media_index.json`, tiempos de `Timeline.word_times`). Los números tienen que aparecer tal cual.
"""
from __future__ import annotations

import re

from .config import gate_severity
from .context import QAContext, item_texts, tc, tokens

STOP = set("""a al algo con como de del el ella en era es esta este esto ha han hay la las le lo los mas me mi muy no o
para pero por que se si sin su sus te tu un una uno y ya the of and to for is in on with your you it this that""".split())
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF\U0001F900-\U0001F9FF]")
NUM = re.compile(r"\d+(?:[.,]\d+)?")


# siglas que suelen decirse desarrolladas (respaldo si se dicen todas sus partes)
ALIASES = {"llm": ("modelo", "lenguaje"), "llms": ("modelo", "lenguaje"), "ia": ("inteligencia", "artificial"),
           "ai": ("inteligencia", "artificial"), "api": ("api",), "ok": ("vale",)}


def _stem(t: str) -> str:
    """Lematización ligera para español: los 5 primeros caracteres (funciona/funcionan, responde/responder)."""
    return t[:5] if len(t) > 5 else t


def _covered(tok: str, said: set[str], said_st: set[str]) -> bool:
    if tok in said or _stem(tok) in said_st:
        return True
    parts = ALIASES.get(tok)
    return bool(parts) and all(_stem(p) in said_st for p in parts)


def _said_tokens(ctx: QAContext, t0: float, t1: float, win: float) -> set[str]:
    wt = ctx.word_text()
    out: set[str] = set()
    for wid, (s, e) in ctx.timeline.word_times.items():
        if t0 - win <= s <= t1 + win and wid in wt:
            out.update(tokens(wt[wid]))
    return out


def run(ctx: QAContext) -> None:
    c = ctx.cfg["claims"]
    dec = ctx.decisions()
    have_text = bool(ctx.word_text())
    if not have_text:
        ctx.notes.append("Sin media_index.json (texto de palabras): el respaldo de afirmaciones solo mira `source`.")
    n_checked = n_bad = 0
    for it in ctx.items(["graphic"]):
        texts = item_texts(it)
        if not texts:
            continue
        n_checked += 1
        said = _said_tokens(ctx, it.t0, it.t1, c["window_s"]) if have_text else set()
        sources = [dec[d].source for d in it.decision_ids if d in dec and dec[d].source]
        unsupported, nums = [], []
        for s in texts:
            toks = [t for t in tokens(s) if t not in STOP and not t.isdigit()]
            said_st = {_stem(x) for x in said}
            cov = (sum(1 for t in toks if _covered(t, said, said_st)) / len(toks)) if toks else 1.0
            if toks and cov < c["coverage_min"]:
                unsupported.append({"texto": s, "cobertura": round(cov, 2),
                                    "sin_respaldo": [t for t in toks if not _covered(t, said, said_st)][:8]})
            for n in NUM.findall(s):
                if re.sub(r"\D", "", n) not in said:   # tokens() ya quita puntos y comas
                    nums.append({"texto": s, "cifra": n})
            if EMOJI.search(s):
                ctx.add("st.icon_source", "block", f"Emoji en el gráfico {it.id} ({tc(it.t0)}): «{s[:40]}».",
                        it.t0, it.t1, {"texto": s, "item": it.id}, it.decision_ids,
                        [{"op": "remove_emoji", "item": it.id}])
        if (unsupported or nums) and not sources:
            n_bad += 1
            plan_note = "" if ctx.plan else " (no hay plan.json: no se puede ver si la decisión trae `source`)"
            # etiquetas de interfaz o ejemplos ilustrativos declarados en el plan: aviso, no bloqueo
            soft = str(it.props.get("text_role", "")).lower() in ("ui", "interfaz", "ejemplo", "example", "decorative", "decorativo")
            if unsupported:
                ctx.add("ct.grounding", "warn" if soft else gate_severity("ct.grounding", "block"),
                        f"El gráfico {it.id} ({tc(it.t0)}–{tc(it.t1)}) dice algo que no se dice en el audio y su decisión no tiene "
                        f"`source`: «{unsupported[0]['texto'][:60]}»{plan_note}.",
                        it.t0, it.t1, {"cadenas": unsupported[:6], "umbral_cobertura": c["coverage_min"],
                                       "ventana_s": c["window_s"], "item": it.id, "component": it.component},
                        it.decision_ids, [{"op": "remove_component", "item": it.id},
                                          {"op": "replan", "reason": "anclar el texto a lo dicho o añadir source"}])
            if nums:
                ctx.add("ct.number_context", gate_severity("ct.number_context", "warn"),
                        f"Cifra(s) en pantalla que no se dicen ni tienen fuente en {it.id} ({tc(it.t0)}): "
                        f"{', '.join(n['cifra'] for n in nums[:5])}.",
                        it.t0, it.t1, {"cifras": nums[:8], "item": it.id}, it.decision_ids,
                        [{"op": "remove_component", "item": it.id}])
        elif (unsupported or nums) and sources:
            ctx.add("ct.sourced", "info", f"{it.id} afirma algo que no se dice pero cita fuente: {sources[0][:80]}.",
                    it.t0, it.t1, {"source": sources, "cadenas": unsupported[:3]}, it.decision_ids)
    ctx.metrics["claims"] = {"graficos_con_texto": n_checked, "sin_respaldo": n_bad}
