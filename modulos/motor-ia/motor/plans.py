"""Planes creativos hechos por agentes → proyectos del motor.

El estudio creativo multiagente (workflow `estudio-creativo` de Meta Ads OS, `.claude/workflows/estudio-creativo.js`) decide ángulo, guion, storyboard, look y
continuidad. Este módulo convierte ese plan en un `Project` listo para `orchestrator.run` (que se salta los pasos
creativos porque ya están hechos) y aplica las reglas del motor que un agente puede romper sin querer.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .models import Actor, Angle, BrandKit, Brief, ContinuityBible, Look, Product, Project, Script, ScriptSegment, Shot
from .pipeline.creative import MAX_TALK_WORDS, WORDS_PER_SECOND
from .pipeline.router import plan_routes
from .store import ctx

CUT_TYPES = {"product_hero", "product_hand", "broll", "actor_motion", "app_screen"}
FAMILIES = {"pain", "desire", "mechanism", "social_proof", "objection", "offer", "novelty", "comparison"}


def _words(t: str) -> int:
    return len(t.split())


def validate(plan: dict[str, Any], locale: str = "es-ES") -> list[str]:
    """Problemas que impedirían producir bien el plan (se corrigen solos cuando es posible en `to_project`)."""
    issues = []
    segs = plan.get("segments", [])
    lang = locale.split("-")[0]
    if not segs or segs[0].get("role") != "hook":
        issues.append("el primer segmento debe ser el hook")
    if segs and _words(segs[0]["text"]) > 10:
        issues.append(f"hook de {_words(segs[0]['text'])} palabras (>9)")
    for i, s in enumerate(segs):
        if _words(s["text"]) > MAX_TALK_WORDS.get(lang, 17) + 2:
            issues.append(f"segmento {i} ({s['role']}) con {_words(s['text'])} palabras")
        if re.search(r"\blo he probado\b|\bllevo (?:\w+ )?(?:semanas|meses)\b|\bme ha cambiado\b|\bdesde que la uso\b", s["text"], re.I):
            issues.append(f"segmento {i}: testimonio en primera persona (actriz sintética)")
    cuts = [s for s in plan.get("shots", []) if s["shot_type"] in CUT_TYPES]
    if len(cuts) > 3:
        issues.append(f"{len(cuts)} planos de corte (>3)")
    return issues


def to_project(plan: dict[str, Any], brand: BrandKit, product: Product, actor: Actor, *, locale: str = "es-ES",
               duration_s: float = 22, platform: str = "reels", angle: dict[str, Any] | None = None, name: str = "") -> Project:
    db = ctx().db
    lang = locale.split("-")[0]
    wps = WORDS_PER_SECOND.get(lang, 2.5)
    # ── guion ──
    segs = [ScriptSegment(role=s["role"], text=s["text"].strip(), on_screen_text=(s.get("on_screen_text") or "").strip(),  # type: ignore[arg-type]
                          emotion=s.get("emotion", "neutral"), gesture=s.get("gesture", ""),
                          est_duration=round(_words(s["text"]) / wps, 2), speaker=actor.id)
            for s in plan["segments"]]
    script = Script(locale=locale, title=plan.get("title", ""), angle_id=plan.get("angle_id"), segments=segs,
                    cta=(plan.get("cta_card") or (brand.ctas[0] if brand.ctas else "")).strip())
    # ── look y continuidad (el actor guarda el look: persiste para futuros anuncios) ──
    cont = plan.get("continuity", {})
    look = next((lk for lk in actor.looks if lk.wardrobe == cont.get("wardrobe_en")), None)
    if look is None:
        look = Look(name=plan.get("title", "look")[:40], wardrobe=cont.get("wardrobe_en", ""), hair_makeup=cont.get("hair_en", ""),
                    reference_asset_ids=[actor.master_portrait_id] if actor.master_portrait_id else [])
        actor.looks.append(look)
        db.put(actor)
    bible = ContinuityBible(actor_id=actor.id, look_id=look.id, location=cont.get("location_en", ""),
                            lighting=cont.get("lighting_en", ""), props=cont.get("props_en", []), time_of_day=cont.get("time_of_day", ""))
    # ── planos ──
    shots: list[Shot] = []
    used_talk: set[int] = set()
    last = len(segs) - 1
    for k, sh in enumerate(plan["shots"]):
        st = sh["shot_type"]
        idx = [i for i in sh.get("segment_indexes", []) if 0 <= i < len(segs)]
        if st == "talking_head":
            # reglas de la toma encadenada: hook solo; ≤17 palabras por tramo (si no, se parte)
            groups: list[list[int]] = []
            for i in idx:
                if i in used_talk:
                    continue
                if not groups or segs[i].role == "hook" or segs[groups[-1][0]].role == "hook" or \
                        sum(_words(segs[j].text) for j in groups[-1]) + _words(segs[i].text) > MAX_TALK_WORDS.get(lang, 17):
                    groups.append([i])
                else:
                    groups[-1].append(i)
                used_talk.add(i)
            for g in groups:
                dlg = " ".join(segs[j].text for j in g)
                shots.append(Shot(index=len(shots), shot_type="talking_head", segment_ids=[segs[j].id for j in g],
                                  duration=round(_words(dlg) / wps + 0.4, 2), dialogue=dlg, camera=sh.get("camera", "selfie_handheld"),
                                  description=sh.get("description_en", ""), location=bible.location, look_id=look.id,
                                  actor_id=actor.id, seed=1000 + len(shots) * 17, constraints={"emotion": segs[g[0]].emotion,
                                                                                               "gesture": segs[g[0]].gesture}))
        elif st in CUT_TYPES:
            # los cortes nunca tapan el hook ni la CTA: se mueven al segmento intermedio más cercano
            target = idx[0] if idx else 1
            if target == 0:
                target = 1
            if target >= last and last > 1:
                target = last - 1
            if product.kind != "app" and st == "app_screen":
                st = "product_hero"
            desc = sh.get("description_en", "")
            if st == "actor_motion" and "face" not in desc.lower():
                desc += ". Hands-only or over-the-shoulder framing; her face is out of frame."
            shots.append(Shot(index=len(shots), shot_type=st, segment_ids=[segs[target].id],  # type: ignore[arg-type]
                              duration=round(min(3.0, max(1.5, float(sh.get("duration", 2.0)))), 2), description=desc,
                              camera=sh.get("camera", "handheld_close"), location=bible.location, look_id=look.id,
                              actor_id=actor.id if st in ("actor_motion", "product_hand") else None,
                              uses_product=bool(sh.get("uses_product")) or st in ("product_hero", "product_hand"),
                              seed=2000 + len(shots) * 31))
    # segmentos hablados que el agente no asignó a ningún plano hablado → al tramo vecino (la voz no puede perderse)
    talking = [s for s in shots if s.shot_type == "talking_head"]
    for i, sg in enumerate(segs):
        if i not in used_talk and talking:
            tgt = min(talking, key=lambda t: min(abs(next(j for j, x in enumerate(segs) if x.id == sid) - i) for sid in t.segment_ids))
            tgt.segment_ids.append(sg.id)
            tgt.segment_ids.sort(key=lambda sid: next(j for j, x in enumerate(segs) if x.id == sid))
            tgt.dialogue = " ".join(x.text for x in segs if x.id in tgt.segment_ids)
    shots.append(Shot(index=len(shots), shot_type="graphic_card", duration=2.2, description="tarjeta final CTA"))
    brief = Brief(brand_id=brand.id, product_id=product.id, objective="ventas", audience=", ".join(plan.get("audience", []) or []),
                  key_messages=[s.text for s in segs if s.role in ("solution", "demo", "proof")][:3], locale=locale,
                  duration_s=duration_s, platform=platform, actor_ids=[actor.id], style_notes=plan.get("production_notes", ""))
    p = Project(name=name or plan.get("title", "plan de agentes"), brief=brief, script=script, continuity=bible, shots=shots,
                variant_spec={"talk_mode": "native", "source": "agentes", "plan": plan,
                              "hook_product_open": bool(plan.get("hook_product_overlay"))})
    if angle:
        fam = angle.get("family") if angle.get("family") in FAMILIES else "pain"
        ang = Angle(family=fam, insight=angle.get("insight", ""), promise=angle.get("promise", ""), proof=angle.get("demo_idea", ""),
                    hooks=angle.get("hooks", []), score=float(angle.get("score", 0)), rationale=angle.get("why_it_works", ""))
        p.angles, p.chosen_angle_id = [ang], ang.id
    est = plan_routes(p.shots, product, talk_mode="native", quality="final")
    p.variant_spec["estimated_cost_usd"] = est
    p.log.append(f"plan importado de agentes · {len(shots)} planos · coste estimado {est:.2f} $ · avisos: {validate(plan, locale)}")
    db.put(p)
    return p


def import_file(path: Path, brand_id: str, product_id: str, actor_handle: str, **kw: Any) -> list[Project]:
    """Fichero del estudio creativo ({"plans": [{"plan": …, "angle": …}], …}) o un plan suelto."""
    db = ctx().db
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    found, missing = [], []
    for what, ref, cmd, getter in (("marca", brand_id, "brand list", lambda: db.get(BrandKit, brand_id)),
                                   ("producto", product_id, "product list", lambda: db.get(Product, product_id)),
                                   ("actor", actor_handle, "actor list", lambda: db.find(Actor, actor_handle))):
        try:
            found.append(getter())
        except KeyError:
            missing.append(f"{what} «{ref}» (míralo con `motor {cmd}`)")
    if missing:
        raise ValueError("no existe en el motor: " + "; ".join(missing))
    brand, product, actor = found
    items = data.get("plans") if isinstance(data, dict) and "plans" in data else [{"plan": data}]
    return [to_project(it["plan"], brand, product, actor, angle=it.get("angle"), **kw) for it in items]
