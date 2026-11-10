"""Revisión multimodal con Gemini sobre un proxy con timecode y número de escena quemados.

Técnicas que mejoran la localización (investigación QA):
  - una pasada por familia de defectos (mejor que una pasada genérica),
  - identificar y localizar en la MISMA llamada, pidiendo evidencia antes de los tiempos,
  - numeración visual de fotogramas/escenas (NumPro) y ~5 fps,
  - referencias del actor para juzgar identidad, guion para juzgar lo que se oye.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..media import filter_path, h264, run
from ..models import Actor, Asset, Defect, Project, Timeline
from ..providers import registry
from ..store import ctx

DEFECT_SCHEMA = {
    "type": "object",
    "properties": {
        "defects": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "scene_label": {"type": "string"},
                    "evidence": {"type": "string"},
                    "start_s": {"type": "number"},
                    "end_s": {"type": "number"},
                    "severity": {"type": "string", "enum": ["minor", "major", "critical"]},
                    "confidence": {"type": "number"},
                },
                "required": ["category", "evidence", "start_s", "end_s", "severity", "confidence"],
            },
        },
        "overall_realism": {"type": "number"},
        "looks_ai_generated": {"type": "number"},
        "would_scroll_past": {"type": "boolean"},
        "summary": {"type": "string"},
    },
    "required": ["defects", "overall_realism", "looks_ai_generated", "summary"],
}

PASSES = {
    "people": ("Personas: deriva de identidad entre planos (¿es SIEMPRE la misma persona que en las referencias?), caras "
               "extrañas, ojos o mirada antinaturales, dientes que cambian, labios desincronizados con la voz, manos o dedos "
               "deformes, cambios de ropa o pelo entre planos, movimientos corporales imposibles.",
               ["identity_drift", "face_artifact", "eyes_teeth", "lip_sync", "hands", "wardrobe_change", "physics"]),
    "scene": ("Escena y producto: objetos que aparecen/desaparecen o se deforman, fondo que se deforma, parpadeo (flicker), "
              "física imposible, producto o logotipo incorrecto o deformado, texto ilegible o inventado dentro de la imagen "
              "(los subtítulos y rótulos superpuestos son correctos por diseño), continuidad de localización/luz entre planos. "
              "En planos selfie, el móvil que graba NUNCA debe verse: un segundo teléfono en la mano es un defecto "
              "(extra_object); el móvil con la app real en pantalla completa sí es correcto.",
              ["physics", "flicker", "product_wrong", "logo_text", "continuity", "extra_object"]),
    "gestalt": ("Sensación global: ¿parece un anuncio hecho con IA o un vídeo real de un creador? Ritmo y montaje, "
                "naturalidad de la voz (¿demasiado limpia, robótica, cambia de voz?), audio (clics, cortes, música que tapa), "
                "subtítulos (errores, desfase con la voz), cualquier señal que delate generación artificial.",
                ["ai_look", "voice", "audio", "caption_error", "pacing"]),
}


def _order(tl: Timeline) -> list[str]:
    seen: list[str] = []
    for c in sorted(tl.clips, key=lambda c: c.start):
        if c.scene_id not in seen:
            seen.append(c.scene_id)
    return seen


def make_proxy(tl: Timeline, render: Path, out: Path) -> Path:
    """540×960 a fps constante con timecode (abajo dcha.) y número de ESCENA (arriba izq.; el mismo que ve el usuario)."""
    font = filter_path(Path(__file__).resolve().parent.parent / "assets" / "Montserrat-Bold.ttf")
    labels = []
    order = _order(tl)
    for c in sorted(tl.clips, key=lambda c: c.start):
        labels.append(
            f"drawtext=fontfile={font}:text='S{order.index(c.scene_id) + 1}':x=14:y=14:fontsize=30:fontcolor=white:box=1:boxcolor=black@0.85:"
            f"enable='between(t,{c.start:.3f},{c.start + c.duration - 0.001:.3f})'"
        )
    tc = (f"drawtext=fontfile={font}:text='%{{pts\\:hms}}':x=w-tw-14:y=h-th-14:fontsize=26:fontcolor=white:box=1:"
          f"boxcolor=black@0.85")
    vf = f"fps=25,setpts=PTS-STARTPTS,scale=540:960," + ",".join(labels + [tc])
    run(["-i", render, "-vf", vf, *h264(26), "-c:a", "aac", "-b:a", "96k", out])
    return out


def scene_labels(tl: Timeline) -> dict[str, str]:
    return {f"S{i + 1}": sid for i, sid in enumerate(_order(tl))}


def review(p: Project, tl: Timeline, render: Path, actor: Actor | None, passes: list[str] | None = None) -> tuple[list[Defect], dict[str, Any]]:
    judge = registry.judge()
    proxy = make_proxy(tl, render, ctx().work("qa", p.id) / f"proxy_v{tl.version}.mp4")
    proxy_asset: Asset = ctx().assets.ingest(proxy, source="render:qa_proxy")
    refs = []
    if actor and actor.master_portrait_id:
        refs = [ctx().db.get_asset(actor.master_portrait_id)]
    labels = scene_labels(tl)
    script = p.script.full_text() if p.script else ""
    defects: list[Defect] = []
    raw: dict[str, Any] = {}
    for name in passes or list(PASSES):
        focus, cats = PASSES[name]
        prompt = (
            "Eres el control de calidad de una productora de anuncios UGC verticales. Revisa este vídeo como lo haría un "
            "espectador exigente en TikTok. Cada fotograma lleva arriba a la izquierda el número de escena (S1, S2…) y abajo "
            "a la derecha el tiempo. La imagen de referencia es la persona protagonista.\n"
            f"FOCO DE ESTA PASADA: {focus}\n"
            f"Categorías válidas: {', '.join(cats)}.\n"
            f"Guion que se debe oír: «{script}»\n"
            "Reglas: reporta SOLO defectos que veas claramente; para cada uno da primero la evidencia concreta (qué se ve/oye), "
            "luego la escena (S#) y el intervalo exacto leído del timecode (no marques el vídeo entero). Usa 'critical' solo si "
            "un espectador normal lo notaría sin buscarlo. confidence entre 0 y 1. overall_realism (0-1) y "
            "looks_ai_generated (0-1) para todo el vídeo. La etiqueta «Creado con IA» es obligatoria por ley: no es un defecto "
            "ni cuenta para looks_ai_generated. Responde en español."
        )
        data = judge.review(proxy_asset, prompt, DEFECT_SCHEMA, refs=refs, fps=5.0, step="qa")
        raw[name] = data
        for d in data.get("defects", []) or []:
            cat = d.get("category", "other")
            if cat not in cats:
                cat = "other"  # nunca reinterpretar (un «extra_object» no debe disparar strengthen_identity)
            sev = {"minor": 0.3, "major": 0.65, "critical": 0.9}.get(d.get("severity", "minor"), 0.3)
            label = (d.get("scene_label") or "").strip().upper()
            scene_id = labels.get(label)
            if not scene_id:
                from .deterministic import scene_at

                scene_id = scene_at(tl, (float(d.get("start_s", 0)) + float(d.get("end_s", 0))) / 2)
            ev = (d.get("evidence") or "").lower()
            if "creado con ia" in ev or "made with ai" in ev or ("etiqueta" in ev and " ia" in ev):
                continue  # la etiqueta de IA es OBLIGATORIA (AI Act art. 50): nunca es un defecto de «parece IA»
            span = float(d.get("end_s", 0)) - float(d.get("start_s", 0))
            conf = float(d.get("confidence", 0.5))
            if span > 0.6 * max(tl.duration, 1) and span > 3:  # marca el vídeo entero → poco fiable
                conf *= 0.5
            defects.append(Defect(scene_id=scene_id, category=cat, severity=sev, start=d.get("start_s"), end=d.get("end_s"),
                                  evidence=d.get("evidence", ""), source=f"vlm:{getattr(judge, 'model', judge.name)}:{name}",
                                  confidence=round(conf, 3)))
    return defects, raw
