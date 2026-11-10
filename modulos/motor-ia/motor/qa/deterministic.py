"""Comprobaciones deterministas (baratas, reproducibles): son las únicas que pueden disparar una
regeneración por sí solas. El VLM confirma o escala (investigación QA: los VLM localizan errores
a la mitad del nivel humano).
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Any

from ..costs import record_local
from ..media import duration as media_duration, loudness, run_capture
from ..models import Actor, AssetKind, Defect, Project, Timeline
from ..pipeline import identity
from ..providers import registry
from ..providers.local_asr import cer_in, wer
from ..store import ctx
from . import objects, visual


def scene_at(tl: Timeline, t: float) -> str | None:
    for c in tl.clips:
        if c.start - 1e-3 <= t < c.start + c.duration:
            return c.scene_id
    return tl.clips[-1].scene_id if tl.clips else None


def freeze_black(path: str) -> list[dict[str, Any]]:
    err = run_capture(["-i", path, "-vf", "freezedetect=n=0.002:d=1.2,blackdetect=d=0.4:pix_th=0.06", "-an", "-f", "null", "-"])
    events = []
    for m in re.finditer(r"freeze_start: ([\d.]+).*?freeze_end: ([\d.]+)", err, re.S):
        events.append({"kind": "freeze", "start": float(m.group(1)), "end": float(m.group(2))})
    for m in re.finditer(r"black_start:([\d.]+) black_end:([\d.]+)", err):
        events.append({"kind": "black", "start": float(m.group(1)), "end": float(m.group(2))})
    return events


def run_checks(p: Project, tl: Timeline, render_path: str, actor: Actor | None) -> tuple[list[Defect], dict[str, Any]]:
    t0 = time.time()
    defects: list[Defect] = []
    checks: dict[str, Any] = {}
    # 1) duración
    dur = media_duration(render_path)
    checks["duration"] = round(dur, 2)
    target = p.brief.duration_s
    if dur < target * 0.7 or dur > target * 1.35:
        defects.append(Defect(category="duration", severity=0.4, evidence=f"duración {dur:.1f}s vs objetivo {target:.0f}s",
                              confidence=1.0))
    # 2) loudness
    lo = loudness(render_path)
    checks["loudness"] = lo
    if lo.get("lufs") is not None and not (-16.5 <= lo["lufs"] <= -11.5):
        defects.append(Defect(category="audio", severity=0.5, evidence=f"loudness {lo['lufs']} LUFS fuera de [-16.5,-11.5]",
                              confidence=1.0))
    if lo.get("true_peak") is not None and lo["true_peak"] > -0.3:
        defects.append(Defect(category="audio", severity=0.3, evidence=f"true peak {lo['true_peak']} dBTP", confidence=1.0))
    # 3) congelados y negros (fuera de la tarjeta CTA, que es casi estática a propósito)
    fb = freeze_black(render_path)
    checks["freeze_black"] = fb
    for ev in fb:
        sid = scene_at(tl, (ev["start"] + ev["end"]) / 2)
        shot = next((s for s in p.shots if s.id == sid), None)
        if shot and shot.shot_type == "graphic_card":
            continue
        if ev["end"] - ev["start"] >= 1.2 or ev["kind"] == "black":
            defects.append(Defect(scene_id=sid, category="freeze_black", severity=0.7, start=ev["start"], end=ev["end"],
                                  evidence=f"{ev['kind']} {ev['start']:.1f}–{ev['end']:.1f}s", confidence=0.95))
    # 4) identidad y objetos por ESCENA, medidos solo en los tramos que de verdad usa el montaje
    id_checks: dict[str, Any] = {}
    obj_checks: dict[str, Any] = {}
    by_scene: dict[str, list] = {}
    for c in tl.clips:
        by_scene.setdefault(c.scene_id, []).append(c)
    for s in p.shots:
        clips = by_scene.get(s.id, [])
        if not clips or s.shot_type in ("graphic_card", "app_screen", "broll", "product_hero"):
            continue
        meds, p10s, mins, spans, passed, twins, twin_risk = [], [], [], [], True, [], False
        phone_hits, phone_max = [], 0.0
        for c in clips:
            a = ctx().db.get_asset(c.asset_id)
            if a.kind != AssetKind.video:
                continue
            if actor and actor.identity.centroid:
                r = identity.video_identity(a, actor.identity, fps=2.0, start=c.src_in, dur=c.duration)
                if r.get("median") is not None:
                    meds.append(r["median"]); p10s.append(r["p10"]); mins.append(r["min"])
                    spans += [(round(c.start + x - c.src_in, 2), round(c.start + y - c.src_in, 2)) for x, y in r.get("drift_spans", [])]
                    passed = passed and r.get("passed") is not False
                    if r.get("reason"):
                        twins.append(r["reason"])
                    twin_risk = twin_risk or bool(r.get("twin_risk"))
            ob = objects.clip_has_phone(ctx().assets.abspath(a), c.src_in, c.duration, fps=0.5,
                                        tag=f"{p.id}_{s.id}_{c.start:.2f}") if s.shot_type == "talking_head" else {}
            if ob.get("available"):
                phone_hits += [round(c.start + t - c.src_in, 2) for t in ob["hits"]]
                phone_max = max(phone_max, ob["max"])
                if ob["phone"]:
                    defects.append(Defect(scene_id=s.id, category="extra_object", severity=0.7, start=c.start, end=c.start + c.duration,
                                          evidence=f"móvil en la mano (p={ob['max']:.2f}, s {[round(c.start + t - c.src_in, 1) for t in ob['hits']][:4]})",
                                          confidence=0.8))
        if meds:
            id_checks[s.id] = {"median": round(min(meds), 4), "p10": round(min(p10s), 4), "min": round(min(mins), 4),
                               "passed": passed, "drift_spans": spans, "twin": twins[:1], "twin_risk": twin_risk}
            if passed and twin_risk:
                defects.append(Defect(scene_id=s.id, category="identity_drift", severity=0.45, confidence=0.6,
                                      evidence="identidad correcta pero cerca de una «gemela» conocida: revisar a ojo"))
            if not passed:
                defects.append(Defect(scene_id=s.id, category="identity_drift", severity=0.8,
                                      evidence=f"SFace mediana {min(meds):.3f} p10 {min(p10s):.3f} tramos {spans[:3]} {twins[:1]}",
                                      confidence=0.9))
        obj_checks[s.id] = {"phone_hits": phone_hits[:6], "phone_max": round(phone_max, 3)}
    checks["identity"] = id_checks
    checks["objects"] = obj_checks
    # 4·) texto incrustado por el modelo de vídeo (subtítulos «fantasma» bajo los nuestros)
    txt_checks: dict[str, Any] = {}
    for s in p.shots:
        if s.shot_type in ("graphic_card", "app_screen", "product_hero"):
            continue
        for c in by_scene.get(s.id, []):
            a = ctx().db.get_asset(c.asset_id)
            if a.kind != AssetKind.video:
                continue
            bt = visual.burned_text(ctx().assets.abspath(a), c.src_in, c.duration, tag=f"{p.id}_{s.id}_{c.start:.2f}", n=2,
                                    expected=p.script.full_text() if p.script else "")
            if bt.get("burned"):
                txt_checks[s.id] = bt["hits"][:2]
                defects.append(Defect(scene_id=s.id, category="burned_text", severity=0.8, start=c.start, end=c.start + c.duration,
                                      evidence=f"texto incrustado por el generador: {bt['hits'][0]['text'][:60]}", confidence=0.85))
                break
    checks["burned_text"] = txt_checks
    # 4a) ritmo: microcortes y subtítulos solapados (lo que más delata un montaje automático)
    micro = [(round(c.start, 2), round(c.duration, 2)) for c in tl.clips if c.duration < 0.3]
    if micro:
        defects.append(Defect(category="pacing", severity=0.5, evidence=f"planos de menos de 0,3 s: {micro[:4]}", confidence=1.0))
    checks["micro_cuts"] = micro
    # 4a') afirmaciones: cifras, absolutos y temas vetados en guion, rótulos, CTA y pantallas reales mostradas
    try:
        from ..models import BrandKit, Product
        from . import compliance

        brand = ctx().db.get(BrandKit, p.brief.brand_id)
        product = ctx().db.get(Product, p.brief.product_id)
        issues = compliance.check_project(p, brand, product)
        checks["compliance"] = compliance.summary(issues)
        for it in issues[:6]:
            defects.append(Defect(category="safety_compliance", severity=0.5, evidence=it, confidence=0.8))
    except KeyError:
        pass
    # 4b) la etiqueta de IA tiene que verse TODO el vídeo (AI Act art. 50) — se comprueba en el píxel, no en la timeline
    checks["ai_label"] = _ai_label_presence(p, tl, render_path)
    if checks["ai_label"].get("missing_frac", 0) > 0.1:
        defects.append(Defect(category="safety_compliance", severity=0.9,
                              evidence=f"etiqueta de IA ausente en {checks['ai_label']['missing_frac']:.0%} de los fotogramas",
                              confidence=0.9))
    # 4b) boca que habla en planos que deben ir sin diálogo
    vis: dict[str, Any] = {}
    actor_types = ("actor_motion", "reaction", "product_hand")
    for i, c in enumerate(tl.clips):
        s = next((x for x in p.shots if x.id == c.scene_id), None)
        if not s or s.shot_type not in actor_types or not c.asset_id:
            continue
        src = ctx().assets.abspath(ctx().db.get_asset(c.asset_id))
        mo = visual.mouth_motion(src, c.src_in, c.duration, tag=f"{p.id}_{i}")
        if not mo.get("available"):
            continue
        vis[s.id] = {"jaw_std": mo.get("jaw_std"), "frames": mo.get("frames")}
        if mo.get("moving"):
            defects.append(Defect(scene_id=s.id, category="silent_mouth", severity=0.6, start=c.start, end=c.start + c.duration,
                                  evidence=f"la boca se mueve en un plano sin diálogo (jawOpen σ={mo.get('jaw_std')})",
                                  confidence=0.75))
    checks["visual"] = vis
    # 5) lo que se oye frente al guion (palabras corruptas, frases cortadas)
    tr = registry.transcriber()
    if p.script and hasattr(tr, "transcribe"):
        a = ctx().assets.ingest(render_path, source="render:final")
        if a.kind == AssetKind.video:
            text, _ = tr.transcribe(a, p.brief.locale)
            w = wer(p.script.full_text(), text)
            per_shot = {}
            for s in p.shots:
                if s.shot_type == "talking_head" and s.dialogue:
                    c = cer_in(text, s.dialogue)
                    per_shot[s.id] = round(c, 3)
                    if c > 0.12:  # la frase de ESTE tramo no se oye como en el guion → regenerar ese tramo
                        defects.append(Defect(scene_id=s.id, category="voice", severity=0.7 if c > 0.25 else 0.5,
                                              evidence=f"CER {c:.2f}: «{s.dialogue[:60]}» no se oye así en el render",
                                              confidence=0.9))
            checks["asr"] = {"wer": round(w, 3), "cer_by_scene": per_shot, "heard": text[:400]}
    record_local("qa", "deterministic", time.time() - t0)
    return defects, checks


def _ai_label_presence(p: Project, tl: Timeline, render_path: str) -> dict[str, Any]:
    """OCR 1 vez por segundo de la zona de la etiqueta de IA (si la política de marca la pide visible)."""
    lab = next((o for o in tl.overlays if o.w <= 0.35 and o.animation == "none" and o.start <= 0.05), None)
    if lab is None:
        return {"expected": False}
    from ..media import frame_at
    from ..pipeline.product import ocr_text

    from ..pipeline.edit import AI_LABEL

    expected = AI_LABEL.get(p.brief.locale.split("-")[0], "Made with AI")
    la = ctx().db.get_asset(lab.asset_id)
    H, W = tl.height, tl.width
    work = ctx().work("qa", f"label_{p.id}")
    missing, total = 0, 0
    t = 0.5
    while t < min(tl.duration, lab.start + lab.duration) - 0.2:
        f = frame_at(Path(render_path), t, work / f"l_{t:.1f}.png", width=W)
        from PIL import Image

        im = Image.open(f).convert("L")
        # recorte EXACTO de la píldora (geometría conocida del overlay) + inversión y umbral: sin el fondo alrededor,
        # Tesseract lee «Creado con IA» de forma fiable (con fondo de cocina fallaba aunque se viera perfecta)
        pw = W * lab.w
        ph = pw * (la.height or 52) / (la.width or 300)
        box = (int(W * lab.x - pw / 2 + 6), int(H * lab.y - ph / 2 + 4), int(W * lab.x + pw / 2 - 6), int(H * lab.y + ph / 2 - 4))
        crop = work / f"c_{t:.1f}.png"
        c = im.crop(box)
        c = c.resize((c.width * 3, c.height * 3)).point(lambda v: 0 if v > 150 else 255)
        c.save(crop)
        txt = ocr_text(crop, "spa+eng", psm="7")
        total += 1
        # se compara con el texto esperado por error de caracteres: el OCR confunde «IA» con «lA»
        if cer_in(txt, expected) > 0.35:
            missing += 1
        t += 1.0
    return {"expected": True, "checked": total, "missing": missing, "missing_frac": round(missing / total, 3) if total else 0.0}
