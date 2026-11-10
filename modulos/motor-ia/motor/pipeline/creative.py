"""Inteligencia creativa: ángulos de venta → guion por segmentos → storyboard por planos.

Principios (de la investigación):
  - El ángulo de venta es la unidad raíz (100ads, Motion): primero ideas, luego píxeles.
  - Formato PRESENTADOR, no testimonio, cuando el actor es sintético (FTC, UCPD, AI Act):
    nada de «lo he probado», «me cambió la vida»; sí «mira esto», «esto es lo que hace».
  - Guion para UGC nativo: frases cortas, registro hablado del locale, hook en <2 s, CTA explícita.
  - Voz primero: el guion fija la duración; el storyboard se ajusta a la voz.
  - Texto en pantalla compuesto con fuentes reales, nunca generado dentro del vídeo.
"""

from __future__ import annotations

import json
import re
from typing import Any

from ..costs import scope
from ..models import Actor, Angle, BrandKit, ContinuityBible, Product, Project, Script, ScriptSegment, Shot
from ..providers import registry

WORDS_PER_SECOND = {"es": 2.55, "en": 2.6, "de": 2.1, "fr": 2.5, "it": 2.5, "pt": 2.4, "ca": 2.5}
MAX_TALK_WORDS = {"es": 17, "en": 18, "de": 14, "fr": 17, "it": 17, "pt": 16, "ca": 17}  # por plano hablado de 8 s (modelos de vídeo con diálogo nativo)
TESTIMONIAL_PATTERNS = [
    r"\blo he probado\b", r"\bme ha cambiado\b", r"\bme cambió\b", r"\byo uso\b", r"\bllevo (?:\w+ )?(?:semanas|meses) usándol",
    r"\bmi piel\b", r"\bmi experiencia\b", r"\bI tried\b", r"\bchanged my\b", r"\bI've been using\b",
]

LOCALE_STYLE = {
    "es-ES": "español de España, coloquial y natural (vale, mira, la verdad, o sea, tío/tía solo si encaja), tuteo",
    "es-MX": "español de México, coloquial y natural (mira, la neta solo si encaja, oye), tuteo",
    "es-419": "español latino neutro, coloquial y natural, tuteo",
    "en-US": "casual American English, natural creator voice",
    "en-GB": "casual British English, natural creator voice",
    "de-DE": "lockeres, natürliches Deutsch wie eine Creatorin, duzen",
    "fr-FR": "français familier et naturel de créatrice, tutoiement",
    "it-IT": "italiano colloquiale e naturale da creator, dare del tu",
    "pt-PT": "português europeu coloquial e natural, tratar por tu",
    "pt-BR": "português brasileiro coloquial e natural, você",
    "ca-ES": "català col·loquial i natural, tuteig",
}


def _lang(locale: str) -> str:
    return locale.split("-")[0].lower()


# ───────────────────────────── Ángulos ─────────────────────────────

ANGLES_SCHEMA = {
    "type": "object",
    "properties": {
        "angles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "family": {"type": "string", "enum": ["pain", "desire", "mechanism", "social_proof", "objection", "offer", "novelty", "comparison"]},
                    "insight": {"type": "string"},
                    "promise": {"type": "string"},
                    "proof": {"type": "string"},
                    "hooks": {"type": "array", "items": {"type": "string"}},
                    "score": {"type": "number"},
                    "rationale": {"type": "string"},
                },
                "required": ["family", "insight", "promise", "hooks", "score", "rationale"],
            },
        }
    },
    "required": ["angles"],
}

STRATEGIST = (
    "Eres un estratega creativo de performance marketing especializado en anuncios UGC para TikTok, Reels y Meta. "
    "Piensas en ángulos de venta concretos, no en eslóganes. Solo usas afirmaciones que el brief permite. "
    "Puntúas cada ángulo de 0 a 10 según probabilidad de detener el scroll y vender a esta audiencia."
)


def make_angles(p: Project, brand: BrandKit, product: Product) -> list[Angle]:
    b = p.brief
    llm = registry.llm("creative")
    prompt = f"""Genera {b.n_angles} ángulos de venta distintos para un anuncio en vídeo.

MARCA: {brand.name} · tono: {brand.tone}
PRODUCTO: {product.name} ({product.kind}) — {product.description}
BENEFICIOS: {json.dumps(product.benefits, ensure_ascii=False)}
PRUEBAS: {json.dumps(product.proof_points, ensure_ascii=False)}
OBJECIONES: {json.dumps(product.objections, ensure_ascii=False)}
PRECIO: {product.price or 'n/d'}
AFIRMACIONES APROBADAS (no inventes otras): {json.dumps(brand.approved_claims, ensure_ascii=False)}
PROHIBIDO: {json.dumps(brand.dont_rules, ensure_ascii=False)}
OBJETIVO: {b.objective} · AUDIENCIA: {b.audience}
MENSAJES CLAVE: {json.dumps(b.key_messages, ensure_ascii=False)}
IDIOMA: {b.locale} ({LOCALE_STYLE.get(b.locale, b.locale)}) · PLATAFORMA: {b.platform} · DURACIÓN: {b.duration_s:.0f}s

Cada ángulo: familia, insight de la audiencia, promesa, prueba, 3 hooks de máximo 9 palabras escritos como los diría un
creador real en el idioma pedido (patrón de interrupción, curiosidad o dolor concreto; nada de «¿Sabías que…?» genérico),
puntuación 0-10 y razón breve. Ángulos realmente distintos entre sí."""
    if llm.name == "mock":
        prompt += "<mock>" + json.dumps(_mock_angles(p, product)) + "</mock>"
    with scope(p.id):
        data = llm.json(STRATEGIST, prompt, ANGLES_SCHEMA, step="concept", temperature=0.9)
    out = []
    for a in data.get("angles", [])[: max(1, b.n_angles)]:
        out.append(Angle(family=a.get("family", "pain") if a.get("family") in Angle.model_fields["family"].annotation.__args__ else "pain",  # type: ignore[union-attr]
                         insight=a.get("insight", ""), promise=a.get("promise", ""), proof=a.get("proof", ""),
                         hooks=[h for h in a.get("hooks", []) if h][:3], score=float(a.get("score", 0) or 0), rationale=a.get("rationale", "")))
    out.sort(key=lambda x: -x.score)
    return out


def _mock_angles(p: Project, product: Product) -> dict[str, Any]:
    return {"angles": [
        {"family": "pain", "insight": f"La audiencia pierde tiempo sin {product.name}", "promise": product.benefits[0] if product.benefits else "resultado rápido",
         "proof": product.proof_points[0] if product.proof_points else "", "hooks": ["Deja de hacer esto ya", "Nadie te cuenta esto", "Mira lo que pasa"],
         "score": 8, "rationale": "dolor concreto"},
        {"family": "mechanism", "insight": "No entienden por qué funciona", "promise": "explicación simple", "proof": "",
         "hooks": ["Así funciona por dentro", "El truco está aquí", "Te lo explico en 20 segundos"], "score": 7, "rationale": "curiosidad"},
    ]}


# ───────────────────────────── Guion ─────────────────────────────

SCRIPT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "segments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "role": {"type": "string", "enum": ["hook", "problem", "agitate", "solution", "demo", "proof", "offer", "cta"]},
                    "text": {"type": "string"},
                    "on_screen_text": {"type": "string"},
                    "emotion": {"type": "string"},
                    "gesture": {"type": "string"},
                },
                "required": ["role", "text", "on_screen_text", "emotion"],
            },
        },
        "cta": {"type": "string"},
    },
    "required": ["title", "segments", "cta"],
}

SCRIPTWRITER = (
    "Eres guionista de anuncios UGC que parecen grabados por un creador real con el móvil, no por una marca. "
    "Escribes como se habla, no como se escribe: frases cortas, ritmo, pausas naturales, alguna muletilla del idioma "
    "con moderación, cero lenguaje corporativo, cero superlativos vacíos. Respetas estrictamente las afirmaciones aprobadas. "
    "El personaje es un PRESENTADOR (creador que enseña y recomienda), nunca un cliente que relata su experiencia personal "
    "de uso: no escribas testimonios en primera persona del tipo «lo he probado», «me cambió», «mi piel»."
)


def write_script(p: Project, brand: BrandKit, product: Product, angle: Angle, actor: Actor | None) -> Script:
    b = p.brief
    lang = _lang(b.locale)
    wps = WORDS_PER_SECOND.get(lang, 2.5)
    speak_seconds = max(8.0, b.duration_s - 2.5)  # deja ~2,5 s para tarjeta CTA / respiración
    target_words = int(speak_seconds * wps)
    llm = registry.llm("creative")
    prompt = f"""Escribe el guion de un anuncio UGC de {b.duration_s:.0f} segundos para {b.platform}.

ÁNGULO: {angle.family} — insight: {angle.insight} — promesa: {angle.promise} — prueba: {angle.proof}
HOOKS CANDIDATOS: {json.dumps(angle.hooks, ensure_ascii=False)}
PRODUCTO: {product.name} — {product.description}
BENEFICIOS: {json.dumps(product.benefits, ensure_ascii=False)}
AFIRMACIONES APROBADAS: {json.dumps(brand.approved_claims, ensure_ascii=False)}
PROHIBIDO: {json.dumps(brand.dont_rules, ensure_ascii=False)}
CTA PREFERIDAS: {json.dumps(brand.ctas, ensure_ascii=False)}
PRESENTADOR: {actor.persona if actor else 'creador/a de contenido cercano/a'}
IDIOMA Y REGISTRO: {b.locale} — {LOCALE_STYLE.get(b.locale, b.locale)}
NOTAS DE ESTILO: {b.style_notes or '—'}

Reglas duras:
- Entre {int(target_words * 0.85)} y {target_words} palabras habladas EN TOTAL (es lo que cabe en {speak_seconds:.0f}s).
- 4 a 6 segmentos. El primero es el hook (≤9 palabras, se entiende sin sonido gracias al texto en pantalla).
- Cada segmento hablado ≤ {MAX_TALK_WORDS.get(lang, 17)} palabras.
- on_screen_text: texto corto para pantalla (≤6 palabras) o cadena vacía. Solo el hook y la CTA suelen llevarlo.
- El último segmento es la CTA ({b.objective}).
- Formato presentador: describe lo que hace el producto y por qué importa; no inventes experiencias personales de uso.
- Números y marcas escritos como se pronuncian si hay duda."""
    if llm.name == "mock":
        prompt += "<mock>" + json.dumps(_mock_script(b.locale, product, angle)) + "</mock>"
    with scope(p.id):
        data = llm.json(SCRIPTWRITER, prompt, SCRIPT_SCHEMA, step="script", temperature=0.8)
    script = _to_script(data, b.locale, angle.id, actor, wps)
    issues = script_issues(script, b.locale, target_words, synthetic=(actor.synthetic if actor else True))
    from ..qa import compliance

    issues += compliance.check_project(p.model_copy(update={"script": script}), brand, product, screens=False)
    if issues and llm.name != "mock":
        fix = (prompt + "\n\nTu versión anterior incumple estas reglas: " + "; ".join(issues) +
               "\nVersión anterior: " + json.dumps(data, ensure_ascii=False) + "\nReescríbela cumpliendo TODAS las reglas.")
        with scope(p.id):
            data = llm.json(SCRIPTWRITER, fix, SCRIPT_SCHEMA, step="script", temperature=0.6)
        script = _to_script(data, b.locale, angle.id, actor, wps)
    return script


def _to_script(data: dict[str, Any], locale: str, angle_id: str, actor: Actor | None, wps: float) -> Script:
    segs = []
    for s in data.get("segments", []):
        text = re.sub(r"\s+", " ", (s.get("text") or "").strip())
        segs.append(ScriptSegment(role=s.get("role", "solution"), speaker=actor.id if actor and text else None, text=text,
                                  on_screen_text=(s.get("on_screen_text") or "").strip(), emotion=s.get("emotion", "neutral"),
                                  gesture=s.get("gesture", ""), est_duration=round(max(1.2, len(text.split()) / wps + 0.25), 2)))
    return Script(locale=locale, title=data.get("title", ""), angle_id=angle_id, segments=segs, cta=data.get("cta", ""))


def script_issues(s: Script, locale: str, target_words: int, synthetic: bool = True) -> list[str]:
    issues = []
    total = sum(len(x.text.split()) for x in s.segments)
    if total > target_words * 1.08:
        issues.append(f"demasiadas palabras ({total} > {target_words})")
    if total < target_words * 0.6:
        issues.append(f"demasiado corto ({total} palabras, objetivo ~{target_words})")
    lang = _lang(locale)
    for seg in s.segments:
        if len(seg.text.split()) > MAX_TALK_WORDS.get(lang, 17) + 2:
            issues.append(f"segmento '{seg.role}' demasiado largo ({len(seg.text.split())} palabras)")
    if s.segments and s.segments[0].role != "hook":
        issues.append("el primer segmento debe ser el hook")
    if s.segments and len(s.segments[0].text.split()) > 10:
        issues.append("hook de más de 9 palabras")
    if synthetic:
        full = s.full_text()
        for pat in TESTIMONIAL_PATTERNS:
            if re.search(pat, full, re.I):
                issues.append(f"testimonio en primera persona no permitido para actor sintético ('{pat}')")
    return issues


def _mock_script(locale: str, product: Product, angle: Angle) -> dict[str, Any]:
    return {"title": f"{product.name} · {angle.family}", "cta": "Pruébalo hoy", "segments": [
        {"role": "hook", "text": angle.hooks[0] if angle.hooks else "Mira esto", "on_screen_text": angle.hooks[0] if angle.hooks else "Mira esto", "emotion": "sorpresa"},
        {"role": "problem", "text": "Casi todo el mundo pierde tiempo con esto cada día.", "on_screen_text": "", "emotion": "empatía"},
        {"role": "solution", "text": f"Con {product.name} lo resuelves en un momento, sin complicarte.", "on_screen_text": "", "emotion": "entusiasmo"},
        {"role": "demo", "text": "Fíjate, lo abres, eliges lo que quieres y listo.", "on_screen_text": "", "emotion": "neutral"},
        {"role": "cta", "text": "Si te pasa, pruébalo hoy desde el enlace.", "on_screen_text": "Pruébalo hoy", "emotion": "cercano"},
    ]}


# ───────────────────────────── Storyboard ─────────────────────────────

STORYBOARD_SCHEMA = {
    "type": "object",
    "properties": {
        "continuity": {
            "type": "object",
            "properties": {"location": {"type": "string"}, "lighting": {"type": "string"}, "time_of_day": {"type": "string"},
                           "props": {"type": "array", "items": {"type": "string"}}},
            "required": ["location", "lighting", "time_of_day"],
        },
        "cutaways": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "segment_index": {"type": "integer"},
                    "shot_type": {"type": "string", "enum": ["actor_motion", "product_hand", "product_hero", "app_screen", "broll"]},
                    "description": {"type": "string"},
                    "camera": {"type": "string"},
                    "duration": {"type": "number"},
                },
                "required": ["segment_index", "shot_type", "description", "camera", "duration"],
            },
        },
        "talking_framing": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["continuity", "cutaways", "talking_framing"],
}

DIRECTOR = (
    "Eres director de anuncios UGC grabados con móvil. Planificas planos simples y creíbles: una sola localización "
    "realista, luz natural, cámara en mano o selfie. Evitas todo lo que delata a la IA: manos manipulando objetos "
    "pequeños con precisión, texto dentro de la imagen, varias personas, física compleja, planos de cine."
)


def make_storyboard(p: Project, script: Script, actor: Actor | None, product: Product, brand: BrandKit,
                    talk_mode: str) -> tuple[list[Shot], ContinuityBible]:
    """talk_mode: 'native' (diálogo nativo a cámara + cutaways), 'voiceover' (VO sobre planos), 'lipsync' (banco + boca)."""
    llm = registry.llm("default")
    has_app = product.kind == "app" and bool(product.screenshot_asset_ids or product.screen_recording_asset_ids)
    has_product_media = bool(product.packshot_asset_ids or product.footage_asset_ids)
    segs = [{"i": i, "role": s.role, "text": s.text, "emotion": s.emotion} for i, s in enumerate(script.segments)]
    prompt = f"""Planifica los planos de corte (cutaways) para este anuncio UGC vertical 9:16.

GUION (segmentos): {json.dumps(segs, ensure_ascii=False)}
ACTOR: {actor.appearance if actor else 'sin actor'}
PRODUCTO: {product.name} ({product.kind}) — aspecto: {product.visual_description or product.description}
¿Hay capturas reales de la app?: {has_app} · ¿Hay fotos/vídeo reales del producto?: {has_product_media}
MODO: {talk_mode}

Devuelve:
- continuity: una localización concreta y realista (ej. «cocina pequeña de piso en Madrid, encimera blanca»), luz, hora y atrezo.
- cutaways: 2–4 planos de corte de 1.5–3 s que ilustran segmentos concretos (no el hook ni la CTA). Van BAJO LA VOZ: nunca
  muestres la cara del actor de frente (parecería que habla sin mover la boca). Usa 'app_screen' si es una app con capturas
  reales, 'product_hero' para enseñar el producto real, 'broll' para ambiente o detalle, 'actor_motion' SOLO con encuadre de
  manos o por encima del hombro (cara fuera de cuadro). Prefiere planos que no requieran manos precisas.
- talking_framing: encuadre de cada segmento hablado (ej. «selfie plano medio», «primer plano», «plano medio apoyada en encimera»)."""
    if llm.name == "mock":
        prompt += "<mock>" + json.dumps(_mock_storyboard(len(script.segments), has_app)) + "</mock>"
    with scope(p.id):
        data = llm.json(DIRECTOR, prompt, STORYBOARD_SCHEMA, step="storyboard", temperature=0.6)
    cont = data.get("continuity", {}) or {}
    bible = ContinuityBible(actor_id=actor.id if actor else None, look_id=(actor.looks[0].id if actor and actor.looks else None),
                            location=cont.get("location", ""), lighting=cont.get("lighting", "luz natural de ventana"),
                            time_of_day=cont.get("time_of_day", "día"), props=cont.get("props", []) or [])
    framings = data.get("talking_framing", []) or []
    shots: list[Shot] = []
    lang = _lang(script.locale)
    wps = WORDS_PER_SECOND.get(lang, 2.5)
    # A-roll: planos hablados (agrupa segmentos hasta llenar ~7.5 s de habla por plano)
    group: list[ScriptSegment] = []
    groups: list[list[ScriptSegment]] = []
    for seg in script.segments:
        words = len(seg.text.split())
        cur = sum(len(x.text.split()) for x in group)
        if group and (cur + words > MAX_TALK_WORDS.get(lang, 17) or seg.role == "hook" or group[0].role == "hook"):
            groups.append(group)
            group = []
        group.append(seg)
    if group:
        groups.append(group)
    for gi, g in enumerate(groups):
        text = " ".join(s.text for s in g).strip()
        framing = framings[min(gi, len(framings) - 1)] if framings else "selfie plano medio"
        st = "talking_head" if talk_mode in ("native", "lipsync") else "reaction"
        dur = round(min(8.0, max(2.5, len(text.split()) / wps + 0.6)), 2)
        shots.append(Shot(index=len(shots), shot_type=st, segment_ids=[s.id for s in g], duration=dur, description=framing,
                          camera="selfie_handheld" if "selfie" in framing.lower() else "handheld_medium",
                          location=bible.location, look_id=bible.look_id, actor_id=actor.id if actor else None, dialogue=text,
                          constraints={"emotion": g[0].emotion, "gesture": g[0].gesture, "role": g[0].role}))
    # B-roll / cutaways
    for c in data.get("cutaways", [])[:4]:
        si = int(c.get("segment_index", 0))
        if si <= 0 or si >= len(script.segments):
            continue
        st = c.get("shot_type", "broll")
        desc = c.get("description", "")
        if st == "reaction":  # gesto mudo de frente bajo la voz = «doblaje roto»: se convierte en plano sin cara
            st = "actor_motion"
        if st == "app_screen" and not has_app:
            st = "product_hero" if has_product_media else "broll"
        if st == "product_hero" and not has_product_media:
            # nunca se inventa el producto: en una app es su pantalla real; sin fotos de un físico, ambiente
            st = "app_screen" if has_app else "broll"
        if st == "actor_motion":
            desc = (desc + ". Hands-only or over-the-shoulder framing; her face is out of frame.").strip(". ")
        shots.append(Shot(index=len(shots), shot_type=st, segment_ids=[script.segments[si].id],
                          duration=round(min(3.0, max(1.5, float(c.get("duration", 2.0)))), 2),
                          description=desc, camera=c.get("camera", "handheld"), location=bible.location,
                          look_id=bible.look_id, actor_id=actor.id if actor and st in ("reaction", "actor_motion", "product_hand") else None,
                          uses_product=st in ("product_hand", "product_hero", "app_screen")))
    # Tarjeta final de CTA (siempre programática)
    cta_seg = next((s for s in script.segments if s.role == "cta"), None)
    shots.append(Shot(index=len(shots), shot_type="graphic_card", segment_ids=[cta_seg.id] if cta_seg else [], duration=2.2,
                      description="tarjeta final CTA", camera="static"))
    return shots, bible


def _mock_storyboard(n: int, has_app: bool) -> dict[str, Any]:
    return {"continuity": {"location": "salón luminoso de piso en Madrid, sofá gris", "lighting": "luz natural de ventana lateral",
                           "time_of_day": "mañana", "props": ["taza de café"]},
            "cutaways": [{"segment_index": 2, "shot_type": "app_screen" if has_app else "product_hero", "description": "enseña el producto",
                          "camera": "handheld close", "duration": 2.5},
                         {"segment_index": 1, "shot_type": "broll", "description": "detalle del ambiente", "camera": "handheld", "duration": 2.0}],
            "talking_framing": ["selfie primer plano", "selfie plano medio", "plano medio", "selfie plano medio"]}
