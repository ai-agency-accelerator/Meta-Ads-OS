"""Orquestación de `ck qa`: carga el plan, decodifica una vez, ejecuta las puertas (de barato a caro), el juez en
paralelo y escribe `qa.json`, `qa_sheet_*.jpg` y `qa_summary.md` en `versions/<vid>/`."""
from __future__ import annotations

import shutil
import threading
import time
from typing import Any

from ..spec import QAReport
from . import boxes, checks_audio, checks_captions, checks_claims, checks_logo, checks_motion, checks_pacing, checks_text, checks_video
from . import judge as judge_mod
from . import media, report, sheets
from .context import QAContext, load_context


def _step(ctx: QAContext, name: str, fn, *a: Any) -> None:
    t = time.time()
    try:
        fn(ctx, *a)
    except Exception as exc:   # una puerta rota no tumba el QA: queda como nota e issue info
        import traceback

        ctx.notes.append(f"La comprobación «{name}» falló: {type(exc).__name__}: {str(exc)[:200]}")
        ctx.add(f"qa.error.{name}", "info", f"No se pudo ejecutar {name}: {type(exc).__name__}",
                evidence={"traceback": traceback.format_exc()[-800:]})
    ctx.metrics.setdefault("timings_s", {})[name] = round(time.time() - t, 1)


def run(slug: str, vid: str, judge: bool = True, keep_frames: bool = False) -> QAReport:
    t_all = time.time()
    ctx = load_context(slug, vid)
    ctx.work = ctx.vdir / "qa_work"
    ctx.work.mkdir(parents=True, exist_ok=True)
    ctx.probe = media.probe(ctx.render)
    if not ctx.timeline.duration:
        ctx.notes.append("La timeline no trae duración: se usa la del render.")

    # juez en paralelo (subida + inferencia tardan; no depende de las puertas)
    jres: dict[str, Any] = {}
    jth = None
    if judge:
        def _j() -> None:
            try:
                jres.update(judge_mod.run(ctx))
            except Exception as exc:
                jres.update({"status": "error", "reason": f"{type(exc).__name__}: {str(exc)[:300]}"})
        jth = threading.Thread(target=_j, daemon=True)
        jth.start()

    t = time.time()
    dec = media.shared_decode(ctx.render, ctx.work, ctx.cfg)
    ctx.frames_full, ctx.frames_sheet = dec["full"], dec["sheet"]
    ctx.metrics.setdefault("timings_s", {})["decode"] = round(time.time() - t, 1)
    if not dec["ok"]:
        ctx.notes.append("FFmpeg devolvió error en la decodificación compartida: " + dec["stderr_tail"][-200:])

    _step(ctx, "audio", checks_audio.run)
    _step(ctx, "boxes", boxes.collect)              # antes que vídeo: el DOM y la cámara afinan negros y congelados
    _step(ctx, "video", checks_video.run, dec)
    _step(ctx, "panel", checks_video.panel_empty, dec)
    _step(ctx, "captions", checks_captions.run)
    _step(ctx, "motion", checks_motion.run)          # antes que texto: fija los umbrales de motion del YAML
    _step(ctx, "text", checks_text.run)
    _step(ctx, "claims", checks_claims.run)
    _step(ctx, "logos", checks_logo.run)
    _step(ctx, "pacing", checks_pacing.run)
    try:                                              # respaldo del panel del split si ly.panel_empty no pudo medir
        from . import checks_panel
        if "panel_occupancy" not in ctx.metrics:
            _step(ctx, "panel_fallback", checks_panel.run)
    except Exception as exc:  # noqa: BLE001
        ctx.notes.append(f"checks_panel no disponible: {type(exc).__name__}: {str(exc)[:160]}")

    if jth is not None:
        jth.join(timeout=900)
        ctx.metrics["judge"] = jres or {"status": "timeout"}
        if jres.get("status") not in ("ok", None):
            ctx.notes.append(f"Juez: {jres.get('status')} — {jres.get('reason', '')}")
    else:
        ctx.metrics["judge"] = {"status": "skip", "reason": "--no-judge"}

    rep = report.build(ctx)
    sh = sheets.build(ctx)
    ctx.metrics["sheets"] = [p.name for p in sh]
    ctx.metrics["notes"] = ctx.notes
    ctx.metrics["timings_s"]["total"] = round(time.time() - t_all, 1)
    rep.metrics = ctx.metrics
    (ctx.vdir / "qa.json").write_text(rep.model_dump_json(indent=1), encoding="utf-8")
    report.write_md(ctx, rep, sh)
    if not keep_frames:
        shutil.rmtree(ctx.work, ignore_errors=True)
    return rep
