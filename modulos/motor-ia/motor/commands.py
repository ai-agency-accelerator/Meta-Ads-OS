"""Órdenes de edición en lenguaje natural sobre un anuncio ya generado.

    «regenera únicamente la escena 3»          → regen_scene (versión nueva, resto en caché)
    «la escena 2 tiene las manos raras»        → regen_scene con acción shorten_shot
    «cambia el hook» / «hook: ¿Otra vez pizza?» → rewrite_line del hook (A-roll desde ese tramo)
    «cambia el texto del hook a …»             → hook_text (≈0 $)
    «hazlo en alemán»                          → language de-DE (solo A-roll nuevo)
    «CTA: Descárgala ya» / «que diga …al final» → cta (tarjeta, ≈0 $) / spoken_cta
    «versión 4:5», «sin música», «subtítulos limpios»

Primero un analizador determinista (gratis, sin red); si no entiende la orden, un LLM barato la traduce a una
operación del mismo esquema. Las operaciones de texto/idioma crean variantes (proyectos hijos): el máster no se toca.
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable

from .costs import scope
from .models import Project
from .store import ctx

LOCALES = {
    "alemán": "de-DE", "aleman": "de-DE", "german": "de-DE", "inglés": "en-US", "ingles": "en-US", "english": "en-US",
    "británico": "en-GB", "britanico": "en-GB", "francés": "fr-FR", "frances": "fr-FR", "french": "fr-FR",
    "italiano": "it-IT", "italian": "it-IT", "portugués": "pt-PT", "portugues": "pt-PT", "brasileño": "pt-BR",
    "brasileno": "pt-BR", "mexicano": "es-MX", "latino": "es-MX", "latam": "es-MX", "castellano": "es-ES",
    "español de españa": "es-ES", "catalán": "ca-ES", "catalan": "ca-ES",
}
ACTIONS = {"reroll_seed", "strengthen_identity", "shorten_shot", "recompose_product"}
OP_SCHEMA = {
    "type": "object",
    "properties": {
        "op": {"type": "string", "enum": ["regen_scene", "rewrite_line", "hook_text", "cta", "spoken_cta", "language",
                                          "aspect", "captions", "music", "rerender", "restore", "previous_take", "unknown"]},
        "scene": {"type": "string", "description": "número de escena humano (1 = primera) si aplica"},
        "role": {"type": "string", "description": "rol del segmento del guion a reescribir (hook, problem, solution, demo, proof, offer, cta)"},
        "action": {"type": "string", "enum": sorted(ACTIONS)},
        "value": {"type": "string", "description": "texto nuevo, locale (de-DE…), formato (4:5) o estilo"},
    },
    "required": ["op"],
}


def _quoted(text: str) -> str | None:
    m = re.search(r"[«\"“'](.+?)[»\"”']", text) or re.search(r":\s*(.+)$", text)
    return m.group(1).strip() if m else None


def parse(instruction: str) -> dict[str, Any] | None:
    t = instruction.lower().strip()
    q = _quoted(instruction)
    if "subtítulo" in t or "subtitulo" in t or "captions" in t:
        if any(re.search(rf"\b{name}\b", t) for name in LOCALES):
            return {"op": "unsupported", "value": "subtítulos en otro idioma con la voz original todavía no; ¿querías «hazlo en …» (doblaje completo)?"}
        if re.search(r"mal|error|corrige|arregla", t):
            return {"op": "rerender", "value": "subtítulos"}  # realinear y re-renderizar: gratis
        style = "tiktok_bold" if re.search(r"llamativ|tiktok|karaoke|amarill|grande", t) else (
            "brand" if "marca" in t or "brand" in t else "clean")
        return {"op": "captions", "value": style}
    mv = re.search(r"(?:vuelve|volver|restaura|recupera)\w*\s+(?:a\s+)?(?:la\s+)?versi[oó]n\s*(\d+)|\bv(\d+)\b", t)
    if mv and re.search(r"vuelve|volver|restaura|recupera", t):
        return {"op": "restore", "value": next(g for g in mv.groups() if g)}
    mt = re.search(r"toma anterior.*escena\s*(\d+)|escena\s*(\d+).*toma anterior", t)
    if mt:
        return {"op": "previous_take", "scene": next(g for g in mt.groups() if g)}
    m = re.search(r"escena\s*(?:n[ºo.]?\s*)?(\d+)|\bs(\d+)\b|scene\s*(\d+)", t)
    if m and re.search(r"regenera|rehaz|repite|otra toma|cambia|arregla|mal|raro|rar[ao]s|fallo|deforma|no se parece|redo|regenerate", t):
        scene = next(g for g in m.groups() if g)
        action = "reroll_seed"
        if re.search(r"no se parece|cara|identidad|otra persona|face", t):
            action = "strengthen_identity"
        elif re.search(r"mano|dedo|hand|movimiento raro|deforma", t):
            action = "shorten_shot"
        elif re.search(r"producto|app|pantalla|etiqueta|logo|packshot", t):
            action = "recompose_product"
        return {"op": "regen_scene", "scene": scene, "action": action}
    for name, loc in LOCALES.items():
        if re.search(rf"\b{name}\b", t) and re.search(r"hazlo|haz una versión|haz la versión|tradu|dóbla|dobla|versión en|version en|"
                                                        r"make it|translate|in (english|german|french|italian|portuguese)", t):
            return {"op": "language", "value": loc}
    if re.search(r"\b(4:5|1:1|16:9)\b", t):
        return {"op": "aspect", "value": re.search(r"\b(4:5|1:1|16:9)\b", t).group(1)}  # type: ignore[union-attr]
    if re.search(r"sin música|sin musica|quita la música|no music", t):
        return {"op": "music", "value": ""}
    if "hook" in t or "gancho" in t:
        if re.search(r"texto|en pantalla|rótulo|rotulo|on-screen|sticker", t):
            return {"op": "hook_text", "value": q} if q else None
        return {"op": "rewrite_line", "role": "hook", "value": q or ""}
    if "cta" in t or "llamada a la acción" in t or "al final" in t:
        if re.search(r"di[gc]a|habla|hablad|dice|spoken|voz", t):
            return {"op": "spoken_cta", "value": q} if q else None
        return {"op": "cta", "value": q} if q else None
    return None


def _llm_parse(p: Project, instruction: str) -> dict[str, Any]:
    from .providers import registry

    llm = registry.llm("fast")
    shots = [f"S{i + 1}: {s.shot_type} · {(s.dialogue or s.description)[:70]}" for i, s in enumerate(p.shots)]
    prompt = (f"Traduce la orden del usuario sobre un anuncio de vídeo a UNA operación.\nEscenas:\n" + "\n".join(shots) +
              f"\nOrden: {instruction}")
    if llm.name == "mock":
        prompt += "<mock>" + json.dumps({"op": "unknown"}) + "</mock>"
    with scope(p.id):
        return llm.json("Eres el editor de un motor de anuncios. Devuelve solo la operación.", prompt, OP_SCHEMA,
                        step="edit_command", temperature=0.0)


def _next_hook(p: Project) -> str:
    """Si piden «cambia el hook» sin texto: el mejor hook alternativo de los ángulos ya generados."""
    used = p.script.segments[0].text.strip().lower() if p.script and p.script.segments else ""
    chosen = next((a for a in p.angles if a.id == p.chosen_angle_id), None)
    pool = (chosen.hooks if chosen else []) + [h for a in sorted(p.angles, key=lambda a: -a.score) for h in a.hooks]
    for h in pool:
        if h.strip().lower() != used:
            return h
    raise ValueError("no hay hooks alternativos: indica el texto («hook: …»)")


CONFIRM_ABOVE_USD = 0.05
OMNI_USD_S = 0.104  # medido: Omni 1.1 Flash 720p (libro de costes)


def _split(instruction: str) -> list[str]:
    """«versión 4:5 y sin música» → dos órdenes (solo si cada parte se entiende por separado)."""
    parts = [x.strip() for x in re.split(r"\s*(?:;|\by además\b|\by también\b|,\s*y\s+|\s+y\s+)\s*", instruction) if x.strip()]
    if len(parts) > 1 and all(parse(x) for x in parts):
        return parts
    return [instruction]


def _talk_seconds(shots) -> float:
    return sum(min(10.0, max(3.0, len(s.dialogue.split()) / 2.7 + 0.6)) for s in shots)


def estimate(p: Project, op: dict[str, Any]) -> float:
    """Coste estimado de una orden con precios MEDIDOS (las extensiones también cobran el vídeo previo como entrada)."""
    from .orchestrator import resolve_scene

    talking = [s for s in p.shots if s.shot_type == "talking_head"]
    kind = op.get("op")
    if kind in ("hook_text", "cta", "aspect", "captions", "music", "rerender", "unsupported", "restore", "previous_take"):
        return 0.0005
    if kind == "language":
        return round(_talk_seconds(talking) * OMNI_USD_S * 1.1 + 0.05, 3)
    if kind in ("spoken_cta",):
        return round(_talk_seconds(talking[-1:]) * OMNI_USD_S * 1.1, 3)
    if kind == "rewrite_line":
        role = op.get("role", "hook")
        seg = next((x for x in (p.script.segments if p.script else []) if x.role == role), None)
        k = next((i for i, t in enumerate(talking) if seg and seg.id in t.segment_ids), 0)
        return round(_talk_seconds(talking[k:]) * OMNI_USD_S * 1.1, 3)
    if kind == "regen_scene":
        try:
            s = resolve_scene(p, op["scene"])
        except KeyError:
            return 0.0
        if s.shot_type == "talking_head":
            return round(_talk_seconds(talking[talking.index(s):]) * OMNI_USD_S * 1.1 + 0.07, 3)
        if s.route and s.route.pipeline.startswith("compose"):
            return 0.0005
        return round(max(3.0, s.duration) * OMNI_USD_S + 0.07, 3)
    return 0.0


def plan(project_id: str, instruction: str) -> dict[str, Any]:
    p = ctx().db.get(Project, project_id)
    ops = [parse(x) or _llm_parse(p, x) for x in _split(instruction)]
    est = round(sum(estimate(p, o) for o in ops), 4)
    return {"ops": ops, "estimate_usd": est, "needs_confirmation": est > CONFIRM_ABOVE_USD}


def apply(project_id: str, instruction: str, progress: Callable[[float, str], None] | None = None, *,
          confirm: bool = False) -> dict[str, Any]:
    """Ejecuta la orden. Si cuesta más de CONFIRM_ABOVE_USD y no viene `confirm`, devuelve el plan con el coste."""
    pl = plan(project_id, instruction)
    if pl["needs_confirmation"] and not confirm:
        return {**pl, "status": "needs_confirmation",
                "message": f"Esta orden cuesta ≈{pl['estimate_usd']:.2f} $: confírmala para ejecutarla."}
    results = []
    target = project_id
    for op in pl["ops"]:
        r = _apply_one(target, op, instruction, progress)
        results.append(r)
        if r.get("variant_id"):
            target = r["variant_id"]  # la siguiente orden se aplica sobre la variante recién creada (edición acumulativa)
    out = dict(results[-1])
    out["op"] = pl["ops"][-1] if len(pl["ops"]) == 1 else pl["ops"]
    out["estimate_usd"] = pl["estimate_usd"]
    if len(results) > 1:
        out["steps"] = results
    return out


def _apply_one(project_id: str, op: dict[str, Any], instruction: str,
               progress: Callable[[float, str], None] | None = None) -> dict[str, Any]:
    from .orchestrator import regen_scene
    from .variants import make_variant

    prog = progress or (lambda f, m: None)
    p = ctx().db.get(Project, project_id)
    p.log.append(f"ORDEN «{instruction}» → {op}")
    ctx().db.put(p)
    kind = op.get("op")
    if kind == "unsupported":
        raise ValueError(op.get("value") or "orden no soportada")
    if kind == "restore":
        from .orchestrator import restore_version

        return {"op": op, **restore_version(project_id, int(op["value"]))}
    if kind == "previous_take":
        from .orchestrator import use_previous_take

        return {"op": op, **use_previous_take(project_id, op["scene"], prog)}
    if kind == "rerender":
        from .orchestrator import assemble_and_render, export, quality_check

        out = assemble_and_render(p, prog)
        rep = quality_check(p, out, prog)
        export(p, out)
        return {"op": op, "render": str(out), "qa_verdict": rep.verdict}
    if kind == "regen_scene":
        action = op.get("action") if op.get("action") in ACTIONS else "reroll_seed"
        return {"op": op, **regen_scene(project_id, op["scene"], action, prog, note=f"orden: {instruction}")}
    if kind == "rewrite_line":
        text = op.get("value") or (_next_hook(p) if op.get("role", "hook") == "hook" else "")
        if not text:
            raise ValueError("falta el texto nuevo")
        return {"op": op, **make_variant(project_id, "rewrite_line", {"role": op.get("role", "hook"), "text": text})}
    if kind in ("hook_text", "cta", "spoken_cta", "language", "aspect", "captions", "music"):
        value: Any = op.get("value")
        if kind == "music":
            value = False
        return {"op": op, **make_variant(project_id, kind, value)}
    raise ValueError(f"no entiendo la orden: «{instruction}»")
