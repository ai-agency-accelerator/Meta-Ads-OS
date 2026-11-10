"""Orquestador extremo a extremo con regeneración selectiva.

brief → ángulos → guion → storyboard → rutas → fotogramas clave → A-roll continuo → cortes →
montaje → render → QA → regenerar SOLO lo rechazado → re-render → QA → exportar.

Cada etapa persiste el proyecto: si algo falla, `run(project_id)` reanuda desde donde se quedó
(los pasos ya hechos salen de caché y no cuestan dinero).
"""

from __future__ import annotations

import contextvars
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable

from .costs import BudgetExceeded, phase, scope, summarize
from .editing.render import render
from .models import Actor, BrandKit, Product, Project, QAReport, Shot
from .pipeline import creative, edit, scenes
from .pipeline.router import plan_routes
from .providers import registry
from .providers.base import ProviderError
from .qa import deterministic, judge, vlm
from .store import ctx

Progress = Callable[[float, str], None]

MAX_QA_ROUNDS = 2
MAX_SCENE_REGENS = 2


def _noop(_p: float, _m: str) -> None:
    pass


def _save(p: Project) -> None:
    ctx().db.put(p)


def _load_refs(p: Project) -> tuple[BrandKit, Product, Actor | None]:
    db = ctx().db
    brand = db.get(BrandKit, p.brief.brand_id)
    product = db.get(Product, p.brief.product_id)
    actor = db.find(Actor, p.brief.actor_ids[0]) if p.brief.actor_ids else None
    return brand, product, actor


def create_project(brief: Any, name: str = "", talk_mode: str = "native") -> Project:
    p = Project(name=name or f"{brief.platform}-{brief.locale}", brief=brief, variant_spec={"talk_mode": talk_mode})
    _save(p)
    return p


def plan(p: Project, progress: Progress = _noop) -> Project:
    brand, product, actor = _load_refs(p)
    if not p.angles:
        progress(0.04, "Generando ángulos de venta")
        p.angles = creative.make_angles(p, brand, product)
        p.chosen_angle_id = p.angles[0].id if p.angles else None
        _save(p)
    angle = next((a for a in p.angles if a.id == p.chosen_angle_id), p.angles[0])
    if not p.script:
        progress(0.08, f"Escribiendo guion (ángulo: {angle.family})")
        p.script = creative.write_script(p, brand, product, angle, actor)
        _save(p)
    if not p.shots:
        progress(0.12, "Storyboard y continuidad")
        talk_mode = p.variant_spec.get("talk_mode", "native")
        p.shots, p.continuity = creative.make_storyboard(p, p.script, actor, product, brand, talk_mode)
        est = plan_routes(p.shots, product, talk_mode=talk_mode, quality=p.brief.quality)
        p.variant_spec["estimated_cost_usd"] = est
        p.log.append(f"rutas planificadas · coste estimado {est:.2f} $")
        _save(p)
    return p


def produce(p: Project, progress: Progress = _noop, *, parallel: int = 2) -> Project:
    brand, product, actor = _load_refs(p)
    talk_mode = p.variant_spec.get("talk_mode", "native")
    talking = [s for s in p.shots if s.shot_type == "talking_head"]
    cut = [s for s in p.shots if s.shot_type not in ("talking_head", "graphic_card")]
    location_ref = None
    # 1) A-roll
    if talking and talk_mode in ("native", "lipsync", "avatar") and actor:
        first = talking[0]
        if not first.keyframe_asset_id:
            progress(0.18, "Fotograma clave del actor (identidad verificada)")
            kf = scenes.make_keyframe(p, first, actor, p.continuity, product, n=2)
            first.keyframe_asset_id = kf.id
            _save(p)
        location_ref = ctx().db.get_asset(first.keyframe_asset_id)
        if not all(s.status == "ready" and s.clip_asset_id for s in talking):
            progress(0.25, f"A-roll: {len(talking)} tramos hablados ({'voz persistente + lip-sync' if talk_mode != 'native' else 'Omni + extensiones'})")
            scenes.generate_aroll(p, talking, actor, p.continuity, product, locale=p.brief.locale)
            _save(p)
    elif talking and talk_mode == "voiceover":
        for s in talking:
            s.shot_type = "reaction"
        cut = [s for s in p.shots if s.shot_type not in ("talking_head", "graphic_card")]
    # 2) planos de corte (en paralelo, cada uno con su propio contexto de costes)
    pending = [s for s in cut if not (s.status == "ready" and s.clip_asset_id) and s.status != "rejected"]  # retirados: no se rehacen
    if pending:
        progress(0.55, f"Planos de corte: {len(pending)} ({', '.join(s.shot_type for s in pending)})")

        def work(s: Shot) -> tuple[Shot, str | None]:
            try:
                scenes.generate_cutaway(p, s, actor, p.continuity, product, brand, location_ref=location_ref)
                return s, None
            except (ProviderError, ValueError) as e:
                if getattr(e, "billing", False):
                    raise
                return s, str(e)[:200]

        with ThreadPoolExecutor(max_workers=max(1, parallel)) as ex:
            futs = [ex.submit(contextvars.copy_context().run, work, s) for s in pending]
            for f in futs:
                s, err = f.result()
                if err:
                    p.log.append(f"{s.id} ({s.shot_type}) sin clip: {err} → se omite del montaje")
        _save(p)
    return p


def assemble_and_render(p: Project, progress: Progress = _noop, *, music: bool = True, out_name: str | None = None) -> Path:
    brand, product, actor = _load_refs(p)
    progress(0.72, "Montaje (timeline no destructiva) y render")
    with scope(p.id):
        tl = edit.build_timeline(p, brand, product, music=music)
        tl.version = (p.timeline.version + 1) if p.timeline else 1
        out = ctx().settings.exports_dir / p.id / (out_name or f"{p.id}_v{tl.version}.mp4")
        out.parent.mkdir(parents=True, exist_ok=True)
        render(tl, out, accent_hex=brand.colors.get("accent"))
    p.timeline = tl
    a = ctx().assets.ingest(out, source="render:final", meta={"project": p.id, "version": tl.version})
    p.render_asset_id = a.id
    # historial inmutable: la timeline de cada versión se guarda como asset (se puede volver a cualquiera)
    ta = ctx().assets.ingest_bytes(tl.model_dump_json().encode(), ".json", source="timeline", meta={"project": p.id, "version": tl.version})
    p.versions.append({"version": tl.version, "timeline_asset": ta.id, "render_asset": a.id, "ts": time.time(),
                       "takes": {s.id: s.clip_asset_id for s in p.shots}})
    _save(p)
    return out


def restore_version(project_id: str, version: int) -> dict[str, Any]:
    """«vuelve a la versión 2»: recupera timeline, vídeo y tomas de esa versión sin regenerar nada (0 $)."""
    from .models import Timeline

    p = ctx().db.get(Project, project_id)
    v = next((x for x in p.versions if x["version"] == int(version)), None)
    if v is None:
        raise KeyError(f"no existe la versión {version} (hay {[x['version'] for x in p.versions]})")
    tl = Timeline.model_validate_json(ctx().assets.abspath(v["timeline_asset"]).read_text(encoding="utf-8"))
    for s in p.shots:
        old = v.get("takes", {}).get(s.id)
        if old and old != s.clip_asset_id:
            s.takes.append({"clip": s.clip_asset_id, "revision": s.revision, "ts": time.time(), "note": "antes de restaurar"})
            s.clip_asset_id = old
    tl.version = max(x["version"] for x in p.versions) + 1
    p.timeline, p.render_asset_id = tl, v["render_asset"]
    p.versions.append({**v, "version": tl.version, "restored_from": int(version), "ts": time.time()})
    p.log.append(f"RESTAURADA la versión {version} como v{tl.version}")
    out = ctx().assets.abspath(v["render_asset"])
    export(p, out)
    _save(p)
    return {"project_id": p.id, "version": tl.version, "restored_from": int(version), "render": str(out), "cost_usd": 0.0}


def use_previous_take(project_id: str, scene: str | int, progress: Progress = _noop) -> dict[str, Any]:
    """«usa la toma anterior de la escena 3»: vuelve a la toma previa de esa escena y re-monta (sin generar)."""
    p = ctx().db.get(Project, project_id)
    s = resolve_scene(p, scene)
    if not s.takes:
        raise ValueError(f"la escena {scene} no tiene tomas anteriores")
    prev = s.takes.pop()
    s.takes.append({"clip": s.clip_asset_id, "revision": s.revision, "ts": time.time(), "note": "sustituida por la anterior"})
    s.clip_asset_id = prev["clip"]
    if s.shot_type == "talking_head":
        for t in p.shots:
            if t.shot_type == "talking_head":
                t.clip_asset_id = prev["clip"]
    out = assemble_and_render(p, progress)
    rep = quality_check(p, out, progress)
    export(p, out)
    _save(p)
    return {"project_id": p.id, "scene": s.id, "render": str(out), "qa_verdict": rep.verdict, "cost_usd": 0.0}


def quality_check(p: Project, out: Path, progress: Progress = _noop, *, use_vlm: bool = True):
    brand, product, actor = _load_refs(p)
    progress(0.82, "QA: comprobaciones deterministas (identidad, ASR, congelados, loudness)")
    with scope(p.id):
        det, checks = deterministic.run_checks(p, p.timeline, str(out), actor)  # type: ignore[arg-type]
        vlm_defects: list = []
        raw: dict = {}
        visual = "missing"
        # el juez simulado solo cuenta como revisión en pruebas (MOTOR_MOCK_JUDGE=1); nunca en producción
        if use_vlm and (registry.judge().name != "mock" or os.environ.get("MOTOR_MOCK_JUDGE")):
            progress(0.88, "QA: revisión multimodal (3 pasadas)")
            try:
                vlm_defects, raw = vlm.review(p, p.timeline, out, actor)  # type: ignore[arg-type]
                visual = "done"
            except Exception as e:  # noqa: BLE001
                p.log.append(f"VLM QA no disponible: {str(e)[:160]} → el anuncio queda SIN REVISIÓN VISUAL")
    report = judge.decide(p, det, vlm_defects, checks, version=p.timeline.version if p.timeline else 1, vlm_raw=raw)
    report.visual_review = visual
    p.qa_reports.append(report)
    for line in judge.summary_lines(report):
        p.log.append(line)
    _save(p)
    return report


def regenerate(p: Project, report, progress: Progress = _noop) -> list[str]:
    """Aplica las acciones del QA SOLO a las escenas rechazadas (gasto etiquetado como «regeneration»)."""
    with phase("regeneration"):
        return _regenerate(p, report, progress)


def _regenerate(p: Project, report, progress: Progress = _noop) -> list[str]:
    brand, product, actor = _load_refs(p)
    done: list[str] = []
    talking = [s for s in p.shots if s.shot_type == "talking_head"]
    for v in report.scenes:
        if v.passed:
            continue
        s = next((x for x in p.shots if x.id == v.scene_id), None)
        if not s:
            continue
        regens = s.constraints.get("regens", 0)
        if regens >= MAX_SCENE_REGENS:
            p.log.append(f"{s.id}: límite de regeneraciones alcanzado → se mantiene la mejor toma")
            continue
        # no destructivo: si la regeneración falla, se restaura la toma anterior tal cual
        chained = p.variant_spec.get("talk_mode", "native") == "native"
        affected = (talking[talking.index(s):] if chained else [s]) if s.shot_type == "talking_head" else [s]
        import copy as _copy

        snap = {t.id: (t.status, t.clip_asset_id, t.constraints.get("chunk_asset"), t.route, t.duration, t.keyframe_asset_id,
                       _copy.deepcopy(t.constraints)) for t in affected}
        s.constraints["regens"] = regens + 1
        if s.clip_asset_id:
            s.takes.append({"clip": s.clip_asset_id, "revision": s.revision, "ts": time.time(), "reason": v.summary()[:160]})
        kind = v.action.kind
        s.revision += 1
        cats = {d.category for d in v.defects}
        if "extra_object" in cats:
            # en positivo (negar el objeto lo ceba) + fotograma clave nuevo: la causa suele venir de la imagen inicial
            s.constraints["keyframe_extra"] = "Both of her hands are empty; one rests on the counter, the other gestures naturally."
            s.constraints["motion_extra"] = "Her hands stay empty the whole time."
            s.keyframe_asset_id = None
        if "silent_mouth" in cats:
            s.constraints["motion_extra"] = (s.constraints.get("motion_extra", "") + " Her lips stay closed the whole time; she does "
                                             "not speak, whisper or mouth any words.").strip()
        if kind == "strengthen_identity":
            s.constraints["strong_identity"] = True
            if s.shot_type != "talking_head" or s is talking[0]:
                s.keyframe_asset_id = None  # el fotograma clave se rehace con modelo pro y referencias reforzadas
        elif kind == "shorten_shot":
            s.duration = max(1.5, round(s.duration * 0.75, 2))
            s.constraints["keyframe_extra"] = "Hands are still and mostly out of frame; simple calm action."
        elif kind == "recompose_product" and product and (product.packshot_asset_ids or product.screenshot_asset_ids):
            from .models import Route

            s.route = Route(pipeline="compose.app_phone" if product.kind == "app" else "compose.packshot", provider="local",
                            reason="QA: producto generado incorrecto → píxeles reales")
        elif kind in ("fix_captions", "rerender_only", "none"):
            continue
        progress(0.9, f"Regenerando {s.id} ({s.shot_type}) → {kind}")
        p.log.append(f"REGEN {v.summary()}")
        try:
            if s.shot_type == "talking_head":
                for t in affected:  # toma encadenada: desde este tramo; lip-sync: solo este tramo
                    t.status, t.clip_asset_id = "planned", None
                    t.constraints.pop("chunk_asset", None)
                # se regenera desde este tramo (los anteriores se conservan en la cadena)
                scenes.generate_aroll(p, talking, actor, p.continuity, product, locale=p.brief.locale)  # type: ignore[arg-type]
            else:
                s.status, s.clip_asset_id = "planned", None
                loc = ctx().db.get_asset(talking[0].keyframe_asset_id) if talking and talking[0].keyframe_asset_id else None
                scenes.generate_cutaway(p, s, actor, p.continuity, product, brand, location_ref=loc)
            done.append(s.id)
        except Exception as e:  # noqa: BLE001
            for t in affected:
                t.status, t.clip_asset_id, _chunk, t.route, t.duration, t.keyframe_asset_id, t.constraints = snap[t.id]
            s.constraints["regens"] = regens + 1  # el intento fallido cuenta (evita bucles)
            p.log.append(f"{s.id}: regeneración fallida ({type(e).__name__}: {str(e)[:140]}) → se conserva la toma anterior")
            if getattr(e, "billing", False) or isinstance(e, BudgetExceeded) or not isinstance(e, (ProviderError, ValueError)):
                _save(p)
                raise
    _save(p)
    return done


def resolve_scene(p: Project, scene: str | int):
    """Acepta id de plano ('shot_…'), número humano ('3' = tercera escena) o 'S3'."""
    key = str(scene).strip().upper().lstrip("S")
    if key.isdigit():
        order = p.scene_order()  # misma numeración que ve el usuario en el vídeo y en la UI
        i = int(key) - 1
        if not 0 <= i < len(order):
            raise KeyError(f"escena {scene} fuera de rango (1–{len(order)})")
        return p.shot(order[i])
    return p.shot(str(scene))


def regen_scene(project_id: str, scene: str | int, action: str = "reroll_seed", progress: Progress = _noop,
                note: str = "manual") -> dict[str, Any]:
    """Regenera SOLO una escena (versión nueva de la timeline; el resto sale de caché) y vuelve a exportar."""
    from .models import RegenAction, SceneVerdict

    p = ctx().db.get(Project, project_id)
    s = resolve_scene(p, scene)
    s.constraints["regens"] = 0
    rep = QAReport(project_id=p.id, scenes=[SceneVerdict(scene_id=s.id, passed=False,
                                                         action=RegenAction(kind=action, reason=note))])  # type: ignore[arg-type]
    before = summarize(p.id)["total_usd"]
    try:
        done = regenerate(p, rep, progress)
    except (ProviderError, BudgetExceeded) as e:
        why = "presupuesto del motor alcanzado" if isinstance(e, BudgetExceeded) else "saldo del proveedor agotado"
        return {"project_id": p.id, "scene": s.id, "status": "paused_billing" if getattr(e, "billing", False) else "paused_budget",
                "reason": f"{why}: {str(e)[:200]}", "regenerated": [], "render": None,
                "note": "la toma anterior se conserva; repite la orden cuando haya saldo"}
    out = assemble_and_render(p, progress)
    report = quality_check(p, out, progress, use_vlm=False)
    export(p, out)
    _save(p)
    return {"project_id": p.id, "scene": s.id, "regenerated": done, "render": str(out), "version": p.timeline.version if p.timeline else None,
            "qa_passed": report.passed, "cost_usd": round(summarize(p.id)["total_usd"] - before, 4)}


def _drop_failed_cutaways(p: Project, report) -> list[str]:
    dropped = []
    for v in report.scenes:
        s = next((x for x in p.shots if x.id == v.scene_id), None)
        if (s is None or v.passed or s.shot_type in ("talking_head", "graphic_card") or s.constraints.get("opener")
                or s.constraints.get("regens", 0) < MAX_SCENE_REGENS):
            continue
        if s.clip_asset_id:
            s.takes.append({"clip": s.clip_asset_id, "revision": s.revision, "ts": time.time(), "reason": "retirado: " + v.summary()[:120]})
        s.clip_asset_id, s.status = None, "rejected"
        p.log.append(f"{s.id} ({s.shot_type}) RETIRADO del montaje tras {MAX_SCENE_REGENS} regeneraciones: {v.summary()[:140]}")
        dropped.append(s.id)
    if dropped:
        _save(p)
    return dropped


def run(project_id: str, progress: Progress = _noop, *, use_vlm: bool = True, music: bool = True,
        max_rounds: int = MAX_QA_ROUNDS) -> dict[str, Any]:
    t_start = time.time()
    p = ctx().db.get(Project, project_id)
    p.status = "running"
    _save(p)
    try:
        plan(p, progress)
        produce(p, progress)
        out = assemble_and_render(p, progress, music=music)
        report = quality_check(p, out, progress, use_vlm=use_vlm)
        rounds = 0
        while not report.passed and rounds < max_rounds:
            rounds += 1
            changed = regenerate(p, report, progress)
            if not changed and all(v.action.kind not in ("fix_captions", "rerender_only") for v in report.scenes if not v.passed):
                break
            out = assemble_and_render(p, progress, music=music)
            report = quality_check(p, out, progress, use_vlm=use_vlm)
        # último recurso: un plano de corte que sigue rechazado tras sus regeneraciones SE QUITA (mejor un short sin ese
        # plano que publicarlo con 3 manos); la voz continúa sobre la toma de la actriz
        dropped = _drop_failed_cutaways(p, report)
        if dropped:
            out = assemble_and_render(p, progress, music=music)
            report = quality_check(p, out, progress, use_vlm=use_vlm)
        export_dir = export(p, out)
        p.status = {"approved": "done", "unreviewed": "done_unreviewed", "needs_review": "needs_review"}.get(report.verdict,
                                                                                                         "done_with_warnings")
        progress(1.0, "Terminado")
    except (ProviderError, BudgetExceeded) as e:
        if not (getattr(e, "billing", False) or isinstance(e, BudgetExceeded)):
            p.status = "failed"
            p.log.append(f"ERROR: {type(e).__name__}: {str(e)[:300]}")
            _save(p)
            raise
        # pausa reanudable: todo lo generado queda guardado y `motor run <id>` continúa desde aquí
        p.status = "paused_budget" if isinstance(e, BudgetExceeded) else "paused_billing"
        why = "presupuesto del motor alcanzado" if isinstance(e, BudgetExceeded) else "saldo del proveedor agotado"
        p.log.append(f"PAUSA: {why}: {str(e)[:200]} → recarga/ajusta y ejecuta `motor run {p.id}` para reanudar")
        _save(p)
        progress(1.0, f"En pausa: {why}")
        return {"project_id": p.id, "status": p.status, "reason": str(e)[:300], "render": None, "export_dir": None,
                "qa_passed": None, "cost": summarize(p.id), "seconds": round(time.time() - t_start, 1)}
    except Exception as e:  # noqa: BLE001
        p.status = "failed"
        p.log.append(f"ERROR: {type(e).__name__}: {str(e)[:300]}")
        _save(p)
        raise
    _save(p)
    costs = summarize(p.id)
    return {"project_id": p.id, "status": p.status, "render": str(out), "export_dir": str(export_dir),
            "qa_passed": report.passed, "qa_verdict": report.verdict, "qa_score": report.score, "cost": costs, "seconds": round(time.time() - t_start, 1)}


def _record_storage(p: Project) -> None:
    """Coste de almacenamiento de los assets NUEVOS de este proyecto (1 mes en R2). Se registra una vez por versión."""
    from .costs import record_storage

    ids = {x for s in p.shots for x in (s.keyframe_asset_id, s.clip_asset_id, s.constraints.get("chunk_asset")) if x}
    ids |= {c.asset_id for c in (p.timeline.clips if p.timeline else []) if c.asset_id}
    if p.render_asset_id:
        ids.add(p.render_asset_id)
    seen = set(p.variant_spec.get("_stored_assets", []))
    new = ids - seen
    total = 0
    for i in new:
        try:
            total += ctx().db.get_asset(i).bytes
        except KeyError:
            continue
    if total:
        with scope(p.id):
            record_storage(total, note=f"{len(new)} assets nuevos, {total / 1e6:.1f} MB × 1 mes")
    p.variant_spec["_stored_assets"] = sorted(seen | ids)


def export(p: Project, out: Path) -> Path:
    """Exporta MP4 + miniatura + manifiesto («genoma creativo» + procedencia + costes + QA)."""
    from .media import frame_at

    d = ctx().settings.exports_dir / p.id
    d.mkdir(parents=True, exist_ok=True)
    thumb = frame_at(out, 1.0, d / "thumbnail.jpg", width=540)
    brand, product, actor = _load_refs(p)
    angle = next((a for a in p.angles if a.id == p.chosen_angle_id), None)
    last_qa = p.qa_reports[-1] if p.qa_reports else None
    _record_storage(p)
    manifest = {
        "project": p.id, "name": p.name, "parent": p.parent_id, "variant_spec": p.variant_spec,
        "genome": {
            "angle": angle.model_dump() if angle else None,
            "hook": p.script.segments[0].text if p.script and p.script.segments else None,
            "cta": p.script.cta if p.script else None, "actor": actor.handle if actor else None,
            "look": p.continuity.look_id, "locale": p.brief.locale, "platform": p.brief.platform,
            "talk_mode": p.variant_spec.get("talk_mode", "native"),
            "shots": [{"id": s.id, "type": s.shot_type, "route": s.route.pipeline if s.route else None,
                       "model": s.route.model if s.route else None, "attempts": s.attempts} for s in p.shots],
        },
        "script": p.script.model_dump() if p.script else None,
        "qa": {"passed": last_qa.passed, "score": last_qa.score, "lines": judge.summary_lines(last_qa)} if last_qa else None,
        "cost": summarize(p.id),
        "cost_note": ("Coste registrado en ESTE proyecto. Los clips reutilizados de otro proyecto (padre de una variante, "
                      "banco del actor) se pagaron y contabilizaron allí. El almacenamiento se valora a precio de R2 aunque hoy "
                      "esté en disco local."),
        "qa_verdict": last_qa.verdict if last_qa else None,
        "provenance": {
            "ai_generated": True,
            "label_policy": brand.ai_label_policy,
            "note": ("Contiene personas y escenas generadas con IA (Gemini Omni/Veo/Imagen: llevan SynthID). Etiqueta visible "
                     "según política de marca. Firmar C2PA con c2patool antes de publicar (ver docs/RUNBOOK.md)."),
        },
        "files": {"video": out.name, "thumbnail": thumb.name},
    }
    (d / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    if Path(out).resolve().parent != d.resolve():
        import shutil

        shutil.copy2(out, d / out.name)
    return d
