"""Juez: fusiona señales deterministas y del VLM en veredictos por escena con acción de regeneración.

Reglas (investigación QA):
  - RECHAZO si hay un fallo determinista grave, o si el VLM reporta major/critical con confianza ≥0,7
    Y otra señal independiente lo apoya (determinista o una segunda pasada del VLM).
  - Un hallazgo del VLM sin apoyo queda como «revisar» (no gasta dinero regenerando).
  - Máximo de intentos por escena: lo controla el orquestador.
Salida tipo: «S04 rejected → identity_drift + hands → strengthen_identity: …».
"""

from __future__ import annotations

from collections import defaultdict

from ..models import Defect, Project, QAReport, RegenAction, SceneVerdict

ACTIONS = {
    "identity_drift": ("strengthen_identity", "regenerar con referencias de identidad reforzadas (modelo de imagen pro, 3 refs, plano más corto)"),
    "face_artifact": ("strengthen_identity", "regenerar fotograma clave y clip con referencias reforzadas"),
    "eyes_teeth": ("reroll_seed", "nueva toma con la misma especificación"),
    "hands": ("shorten_shot", "nueva toma más corta y con las manos fuera de cuadro o quietas"),
    "physics": ("shorten_shot", "nueva toma más corta con acción más simple"),
    "wardrobe_change": ("strengthen_identity", "regenerar con la referencia de vestuario del look de campaña"),
    "lip_sync": ("reroll_seed", "regenerar solo este tramo del A-roll"),
    "voice": ("reroll_seed", "regenerar el tramo hablado afectado"),
    "product_wrong": ("recompose_product", "sustituir por packshot/pantalla real compuesta"),
    "logo_text": ("recompose_product", "sustituir por composición con píxeles reales"),
    "flicker": ("reroll_seed", "nueva toma"),
    "continuity": ("strengthen_identity", "regenerar con la referencia de localización de la escena"),
    "freeze_black": ("reroll_seed", "nueva toma (el clip se congela o va a negro)"),
    "caption_error": ("fix_captions", "realinear subtítulos y re-renderizar (sin coste de generación)"),
    "audio": ("rerender_only", "re-mezclar y re-renderizar"),
    "ai_look": ("reroll_seed", "nueva toma con énfasis en realismo de móvil"),
    "duration": ("none", "ajustar guion en la siguiente iteración"),
    "extra_object": ("reroll_seed", "nueva toma: el móvil que graba no debe verse (manos vacías o con objetos de la escena)"),
    "silent_mouth": ("reroll_seed", "nueva toma con los labios cerrados (plano sin diálogo)"),
    "burned_text": ("reroll_seed", "nueva toma: el generador incrustó subtítulos o texto (se prohíbe en el prompt)"),
    "pacing": ("none", "nota creativa"),
}

HARD_DETERMINISTIC = {"identity_drift", "freeze_black", "voice", "silent_mouth", "extra_object", "burned_text"}
FAMILY = {"identity_drift": "face", "face_artifact": "face", "eyes_teeth": "face", "wardrobe_change": "look", "continuity": "look",
          "hands": "body", "physics": "body", "extra_object": "object", "product_wrong": "product", "logo_text": "product",
          "lip_sync": "speech", "voice": "speech", "silent_mouth": "speech"}


def decide(p: Project, det: list[Defect], vlm: list[Defect], checks: dict, version: int, *, vlm_raw: dict | None = None) -> QAReport:
    by_scene: dict[str | None, list[Defect]] = defaultdict(list)
    for d in det + vlm:
        by_scene[d.scene_id].append(d)
    verdicts: list[SceneVerdict] = []
    global_defects: list[Defect] = []
    review: list[str] = []
    for s in p.shots:
        ds = by_scene.get(s.id, [])
        reject_reasons: list[Defect] = []
        for d in ds:
            if d.source == "deterministic" and d.category in HARD_DETERMINISTIC and d.severity >= 0.6:
                reject_reasons.append(d)
            elif d.source == "deterministic" and d.category == "identity_drift":
                review.append(f"{s.id}: {d.evidence[:100]}")
            elif d.source.startswith("vlm") and d.severity >= 0.65 and d.confidence >= 0.7:
                # apoyo = la MISMA familia de defecto vista por otra señal (determinista o otra pasada), no cualquier cosa
                fam = FAMILY.get(d.category, d.category)
                support = [x for x in ds if x is not d and FAMILY.get(x.category, x.category) == fam
                           and (x.source != d.source or x.start != d.start)]
                if support or d.severity >= 0.9:
                    reject_reasons.append(d)
                else:
                    review.append(f"{s.id}: {d.category} ({d.evidence[:90]})")
        score = 1.0 - min(1.0, sum(d.severity * d.confidence for d in ds) / 2.5)
        if reject_reasons and s.shot_type not in ("graphic_card", "app_screen", "product_hero"):
            main = max(reject_reasons, key=lambda d: d.severity * d.confidence)
            kind, why = ACTIONS.get(main.category, ("reroll_seed", "nueva toma"))
            verdicts.append(SceneVerdict(scene_id=s.id, passed=False, score=round(score, 3), defects=ds,
                                         action=RegenAction(kind=kind, reason=why, params={"category": main.category})))  # type: ignore[arg-type]
        else:
            verdicts.append(SceneVerdict(scene_id=s.id, passed=True, score=round(score, 3), defects=ds))
    for d in by_scene.get(None, []):
        global_defects.append(d)
    rejected = [v for v in verdicts if not v.passed]
    hard_global = [d for d in global_defects if d.source == "deterministic" and d.severity >= 0.6]
    realism = None
    if vlm_raw:
        vals = [v.get("overall_realism") for v in vlm_raw.values() if isinstance(v, dict) and v.get("overall_realism") is not None]
        realism = round(sum(vals) / len(vals), 3) if vals else None
        ai = [v.get("looks_ai_generated") for v in vlm_raw.values() if isinstance(v, dict) and v.get("looks_ai_generated") is not None]
        checks["vlm_looks_ai"] = round(sum(ai) / len(ai), 3) if ai else None
    checks["vlm_realism"] = realism
    score = round(sum(v.score for v in verdicts) / max(len(verdicts), 1), 3)
    for d in global_defects:
        if d.category == "safety_compliance":
            review.append(f"cumplimiento: {d.evidence[:120]}")
    return QAReport(project_id=p.id, version=version, passed=not rejected and not hard_global, score=score, scenes=verdicts,
                    global_defects=global_defects, checks=checks, needs_review=review)


def summary_lines(r: QAReport) -> list[str]:
    head = {"approved": "APROBADO", "rejected": "RECHAZADO", "unreviewed": "SIN REVISIÓN VISUAL (no publicar sin mirar)",
            "needs_review": "REVISAR ANTES DE PUBLICAR"}[r.verdict]
    lines = [f"QA v{r.version}: {head} · score {r.score} · realismo VLM {r.checks.get('vlm_realism')}"
             f" · 'parece IA' {r.checks.get('vlm_looks_ai')}"]
    lines += [f"  revisar: {x}" for x in r.needs_review]
    for v in r.scenes:
        if not v.passed:
            lines.append("  " + v.summary())
    for d in r.global_defects:
        lines.append(f"  global: {d.category} ({d.source}) {d.evidence[:140]}")
    return lines
