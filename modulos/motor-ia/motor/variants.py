"""Variantes: «generar una vez, variar cien».

Una variante es un proyecto hijo que REUTILIZA los clips aprobados del padre y solo cambia lo mínimo:

  coste ≈0 (solo re-render, segmentos en caché):
    hook_text      → otro texto de hook en pantalla
    cta            → otro texto/botón de CTA en la tarjeta final
    captions       → otro estilo de subtítulos
    aspect         → 4:5 o 1:1 (recorte del mismo material)
    music          → otra música / sin música
  coste bajo (se regenera solo una pieza):
    spoken_cta     → re-extiende SOLO el último tramo del A-roll con otra CTA hablada
    rewrite_line   → cambia una frase hablada (p. ej. el hook): A-roll desde ese tramo, cortes reutilizados
    language       → nuevo A-roll en otro idioma; B-roll, producto y app se reutilizan
"""

from __future__ import annotations

import copy
from typing import Any

from .costs import phase, scope, summarize
from .editing.render import render
from .models import Project, ScriptSegment
from .orchestrator import _load_refs, _save, export, quality_check
from .pipeline import creative, edit, scenes
from .providers import registry
from .store import ctx

CHEAP = {"hook_text", "cta", "captions", "aspect", "music"}


def _child(parent: Project, spec: dict[str, Any]) -> Project:
    child = copy.deepcopy(parent)
    from .models import new_id

    child.id = new_id("var")
    child.parent_id = parent.id
    child.variant_spec = {**parent.variant_spec, **spec, "parent": parent.id}
    child.qa_reports = []
    child.timeline = None
    child.render_asset_id = None
    child.log = [f"variante de {parent.id}: {spec}"]
    child.name = f"{parent.name} · {spec.get('kind')}"
    return child


def make_variant(parent_id: str, kind: str, value: Any = None, *, qa: bool = True, use_vlm: bool = False) -> dict[str, Any]:
    with phase("variant"):
        return _make_variant(parent_id, kind, value, qa=qa, use_vlm=use_vlm)


def _make_variant(parent_id: str, kind: str, value: Any = None, *, qa: bool = True, use_vlm: bool = False) -> dict[str, Any]:
    parent = ctx().db.get(Project, parent_id)
    child = _child(parent, {"kind": kind, "value": value})
    brand, product, actor = _load_refs(child)
    assert child.script is not None
    # edición ACUMULATIVA: formato, subtítulos y música del padre se mantienen salvo que esta orden los cambie
    look = dict(parent.variant_spec.get("look", {}))
    if kind == "aspect":
        look["aspect"] = str(value or "4:5")
    elif kind == "captions":
        look["caption_style"] = value or "clean"
    elif kind == "music":
        look["music"] = bool(value)
    child.variant_spec["look"] = look
    child.variant_spec["edits"] = parent.variant_spec.get("edits", []) + [{"kind": kind, "value": value}]
    _save(child)  # guardada ANTES de gastar: el presupuesto y los costes quedan asociados a la variante
    music = look.get("music", True)
    parent_music = next((a.asset_id for a in (parent.timeline.audio if parent.timeline else []) if a.role == "music"), None)
    talking = [s for s in child.shots if s.shot_type == "talking_head"]
    if kind == "hook_text":
        child.script.segments[0].on_screen_text = str(value)
    elif kind == "cta":
        child.script.cta = str(value)
        brand = brand.model_copy(update={"ctas": [str(value)] + brand.ctas})
    elif kind in ("captions", "music", "aspect"):
        pass
    elif kind in ("spoken_cta", "rewrite_line"):
        spec = value if isinstance(value, dict) else {"role": "cta", "text": str(value)}
        if talking:
            _rewrite_spoken(child, spec.get("role", "cta"), str(spec["text"]), actor, product)
        else:  # modo voz en off: basta con cambiar el texto (la voz TTS se regenera al montar, céntimos)
            seg = next((x for x in child.script.segments if x.role == spec.get("role", "cta")), None)
            if seg is None:
                seg = ScriptSegment(role=spec.get("role", "cta"), text=str(spec["text"]))  # type: ignore[arg-type]
                child.script.segments.append(seg)
            seg.text = str(spec["text"])
            if seg.role == "cta":
                child.script.cta = seg.text
    elif kind == "language":
        locale = str(value)
        child.brief = child.brief.model_copy(update={"locale": locale})
        llm = registry.llm("creative")
        segs = [{"role": s.role, "text": s.text, "on_screen_text": s.on_screen_text} for s in child.script.segments]
        prompt = (f"Transcrea este guion de anuncio UGC al locale {locale} ({creative.LOCALE_STYLE.get(locale, locale)}). "
                  f"Mantén la duración aproximada (mismo número de palabras ±10%), el registro hablado nativo y las afirmaciones. "
                  f"No traduzcas literalmente: adapta. Guion: {segs}")
        if llm.name == "mock":
            import json

            # simulación: frases de relleno en el idioma destino (el modo real transcrea con Gemini)
            filler = {"en": "This is part {n} of the ad and it is really simple.", "de": "Das ist Teil {n} der Anzeige und ganz einfach.",
                      "fr": "Voici la partie {n} de la pub, c'est très simple.", "it": "Questa è la parte {n} dello spot, è semplicissimo.",
                      "pt": "Esta é a parte {n} do anúncio e é muito simples."}.get(locale.split("-")[0])
            mock_segs = [{**sg, "text": filler.format(n=i + 1)} if filler else sg for i, sg in enumerate(segs)]
            prompt += "<mock>" + json.dumps({"segments": mock_segs, "cta": child.script.cta, "title": child.script.title}) + "</mock>"
        schema = {"type": "object", "properties": {"title": {"type": "string"}, "cta": {"type": "string"}, "segments": creative.SCRIPT_SCHEMA["properties"]["segments"]},
                  "required": ["segments", "cta"]}
        with scope(child.id):
            data = llm.json(creative.SCRIPTWRITER, prompt, schema, step="script", temperature=0.5)
        for seg, new in zip(child.script.segments, data.get("segments", [])):
            seg.text = new.get("text", seg.text)
            seg.on_screen_text = new.get("on_screen_text", seg.on_screen_text)
        child.script.locale = locale
        child.script.cta = data.get("cta", child.script.cta)
        for s in talking:
            s.dialogue = " ".join(x.text for x in child.script.segments if x.id in s.segment_ids)
            s.status, s.clip_asset_id = "planned", None
            s.constraints.pop("chunk_asset", None)
            s.revision += 1
        if talking:
            scenes.generate_aroll(child, talking, actor, child.continuity, product, locale=locale)  # type: ignore[arg-type]
        # en voz en off no hay A-roll: la voz TTS del nuevo idioma se genera al montar
    else:
        raise ValueError(f"tipo de variante desconocido: {kind}")

    _save(child)
    with scope(child.id):
        tl = edit.build_timeline(child, brand, product, music=music,
                                 music_asset=parent_music if child.brief.duration_s == parent.brief.duration_s else None)
        if look.get("caption_style"):
            tl.captions.style = look["caption_style"]
        if look.get("aspect"):
            w, h = {"4:5": (1080, 1350), "1:1": (1080, 1080), "16:9": (1920, 1080)}.get(look["aspect"], (1080, 1350))
            tl.width, tl.height = w, h
            tl.captions.position_y = 0.80
            for ov in tl.overlays:
                ov.y = min(ov.y, 0.9)
            # la app, el producto y la tarjeta se recomponen al formato (sin recortar cabecera ni botón)
            fixed = {s.id for s in child.shots if s.shot_type in ("app_screen", "product_hero", "graphic_card")} | {"cta"}
            for c in tl.clips:
                if c.scene_id in fixed:
                    c.fit = "contain"
        out = ctx().settings.exports_dir / child.id / f"{child.id}.mp4"
        out.parent.mkdir(parents=True, exist_ok=True)
        render(tl, out, accent_hex=brand.colors.get("accent"))
    child.timeline = tl
    child.render_asset_id = ctx().assets.ingest(out, source="render:variant").id
    report = None
    if qa:
        report = quality_check(child, out, use_vlm=use_vlm)
    export(child, out)
    _save(child)
    parent = ctx().db.get(Project, parent_id)  # releer: otra variante pudo guardarse mientras tanto (sin perder entradas)
    parent.variants.append({"id": child.id, "kind": kind, "value": value, "render": str(out), "asset": child.render_asset_id})
    _save(parent)
    return {"variant_id": child.id, "kind": kind, "render": str(out), "cost": summarize(child.id),
            "qa_passed": report.passed if report else None, "qa_verdict": report.verdict if report else None}


def _rewrite_spoken(child: Project, role: str, text: str, actor, product) -> None:
    """Cambia una frase hablada y regenera el A-roll SOLO desde el tramo que la contiene.

    Los tramos anteriores se conservan; los posteriores se re-extienden porque cada extensión continúa la anterior
    (misma voz, misma toma). Cambiar la CTA = 1 tramo; cambiar el hook = todo el A-roll (los cortes se reutilizan).
    """
    assert child.script is not None
    talking = [s for s in child.shots if s.shot_type == "talking_head"]
    seg = next((x for x in child.script.segments if x.role == role and any(x.id in t.segment_ids for t in talking)), None)
    if seg is None:
        seg = ScriptSegment(role=role, text=text)  # type: ignore[arg-type]
        if role == "hook":
            child.script.segments.insert(0, seg)
            talking[0].segment_ids.insert(0, seg.id)
        else:
            child.script.segments.append(seg)
            talking[-1].segment_ids.append(seg.id)
    seg.text = text
    if role == "hook":
        seg.on_screen_text = text if len(text.split()) <= 8 else None
    if role == "cta":
        child.script.cta = text
    k = next(i for i, t in enumerate(talking) if seg.id in t.segment_ids)
    chained = child.variant_spec.get("talk_mode", "native") == "native"  # en lip-sync cada tramo es independiente
    for t in (talking[k:] if chained else [talking[k]]):
        t.dialogue = " ".join(x.text for x in child.script.segments if x.id in t.segment_ids).strip()
        t.status, t.clip_asset_id = "planned", None
        t.constraints.pop("chunk_asset", None)
        t.revision += 1
    scenes.generate_aroll(child, talking, actor, child.continuity, product, locale=child.brief.locale)  # type: ignore[arg-type]
