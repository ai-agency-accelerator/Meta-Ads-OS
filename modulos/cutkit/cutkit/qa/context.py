"""Contexto del QA: lo que sabe el plan (Timeline, EditPlan, MediaIndex, render_spec) y el colector de issues.

Principio rector: QA que conoce el plan. Cada comprobación compara lo planificado con lo renderizado y cada
issue apunta a la decisión culpable (`TimelineItem.decision_ids` / `AudioItem.decision_ids`).
"""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from ..spec import EditPlan, MediaIndex, QAIssue, Timeline, TimelineItem
from .config import DEFAULTS, runs_root

SEV_ORDER = {"block": 0, "warn": 1, "info": 2}


def tc(t: float | None) -> str:
    """Segundos → mm:ss,d (timecode legible)."""
    if t is None:
        return "—"
    t = max(0.0, float(t))
    m, s = divmod(t, 60)
    return f"{int(m):02d}:{s:04.1f}".replace(".", ",")


def norm_word(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9%]", "", s)


def tokens(s: str) -> list[str]:
    return [w for w in (norm_word(x) for x in re.split(r"[\s/·|,;:()¿?¡!\"'«»…\-–—]+", s)) if w]


@dataclass
class TextBox:
    """Caja de texto visible en t (DOM de HyperFrames o OCR). Coordenadas en px del lienzo, origen arriba-izquierda."""
    t: float
    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    source: str = "ocr"            # dom | ocr
    item: str | None = None        # id del TimelineItem (DOM) o atribuido (OCR)
    role: str | None = None        # caption | key | headline | label | decorative …
    font_px: float | None = None
    opacity: float = 1.0
    conf: float = 1.0

    @property
    def h(self) -> float:
        return self.y1 - self.y0

    @property
    def w(self) -> float:
        return self.x1 - self.x0


@dataclass
class QAContext:
    slug: str
    vid: str
    vdir: Path
    timeline: Timeline
    render: Path
    plan: EditPlan | None = None
    media_index: MediaIndex | None = None
    render_spec: dict[str, Any] = field(default_factory=dict)
    cfg: dict[str, Any] = field(default_factory=lambda: DEFAULTS)
    work: Path | None = None                       # carpeta de trabajo (frames, caché)
    probe: dict[str, Any] = field(default_factory=dict)
    issues: list[QAIssue] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    boxes: list[TextBox] = field(default_factory=list)
    boxes_source: str = ""
    faces: list[tuple[float, float, float, float, float]] = field(default_factory=list)  # (t, x, y, w, h) norm.
    frames_full: list[tuple[float, Path]] = field(default_factory=list)   # fotogramas 1080p para OCR/caras
    frames_sheet: list[tuple[float, Path]] = field(default_factory=list)  # 270 px para hojas de contacto
    tweens: list[dict[str, Any]] = field(default_factory=list)            # GSAP (si se pudo leer el HF)
    cam_rects: list[tuple[float, float, float, float, float, float]] = field(default_factory=list)  # (t, x, y, w, h, opacidad) del A-roll en pantalla (DOM)
    panel_occ: list[tuple[float, float]] = field(default_factory=list)    # (t, ocupación 0..1 del panel superior)
    render_faces: list[tuple[float, tuple, tuple]] = field(default_factory=list)  # (t, caja ojos, caja boca) en px del RENDER (detector de caras)

    # ─────────────── utilidades sobre el plan
    @property
    def fps(self) -> int:
        return self.timeline.fps or 30

    @property
    def duration(self) -> float:
        return float(self.timeline.duration or self.probe.get("duration") or 0.0)

    @property
    def is_short(self) -> bool:
        return self.timeline.height > self.timeline.width and self.duration <= 180

    def decisions(self) -> dict[str, Any]:
        return {d.id: d for d in (self.plan.decisions if self.plan else [])}

    def items(self, tracks: Iterable[str] | None = None) -> list[TimelineItem]:
        tr = set(tracks) if tracks else None
        return [i for i in self.timeline.items if tr is None or i.track in tr]

    def active(self, t0: float, t1: float | None = None, tracks: Iterable[str] | None = None) -> list[TimelineItem]:
        t1 = t0 if t1 is None else t1
        return [i for i in self.items(tracks) if i.t0 <= t1 + 1e-6 and i.t1 >= t0 - 1e-6]

    def blame(self, t0: float, t1: float | None = None, tracks: Iterable[str] | None = None,
              audio_kinds: Iterable[str] | None = None) -> list[str]:
        """Decisiones de los ítems (y del audio) activos en el tramo."""
        out: list[str] = []
        for it in self.active(t0, t1, tracks):
            out += it.decision_ids
        if audio_kinds:
            t1 = t0 if t1 is None else t1
            ak = set(audio_kinds)
            for a in self.timeline.audio:
                end = a.t0 + (a.dur or 0.0)
                if a.kind in ak and a.t0 <= t1 and end >= t0:
                    out += a.decision_ids
        return list(dict.fromkeys(out))

    def word_text(self) -> dict[str, str]:
        """id de palabra → texto (MediaIndex); vacío si no hay índice."""
        if not self.media_index:
            return {}
        return {w.id: w.text for w in self.media_index.words}

    def word_punct(self) -> dict[str, str]:
        if not self.media_index:
            return {}
        return {w.id: w.punct_after for w in self.media_index.words}

    def words_sorted(self) -> list[tuple[str, float, float]]:
        return sorted(((k, float(v[0]), float(v[1])) for k, v in self.timeline.word_times.items()), key=lambda x: x[1])

    def contention_spans(self) -> list[tuple[float, float]]:
        """Tramos justificados como contención (motivo `contencion` en el plan o `hold_reason` en el ítem)."""
        dec = self.decisions()
        spans = []
        for it in self.timeline.items:
            if it.props.get("hold_reason") or it.props.get("contencion"):
                spans.append((it.t0, it.t1))
                continue
            for d in it.decision_ids:
                if d in dec and dec[d].motive.code == "contencion":
                    spans.append((it.t0, it.t1))
                    break
        # decisiones de contención sin ítem: se resuelven por sus palabras ancla
        wt = self.timeline.word_times
        for d in dec.values():
            if d.motive.code == "contencion" and d.anchor.start in wt:
                s = wt[d.anchor.start][0]
                e = wt.get(d.anchor.end or d.anchor.start, wt[d.anchor.start])[1]
                spans.append((s, e))
        return spans

    # ─────────────── colector de issues
    def add(self, check: str, severity: str, message: str, t0: float | None = None, t1: float | None = None,
            evidence: dict[str, Any] | None = None, blame: list[str] | None = None,
            fix: list[dict[str, Any]] | None = None) -> QAIssue:
        iss = QAIssue(id=f"Q-{len(self.issues) + 1:04d}", check=check, severity=severity,
                      t0=None if t0 is None else round(float(t0), 3), t1=None if t1 is None else round(float(t1), 3),
                      message=message, evidence=evidence or {}, blame=list(dict.fromkeys(blame or [])), fix=fix or [])
        self.issues.append(iss)
        return iss


# ───────────────────────────── carga
def _load_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def version_dir(slug: str, vid: str) -> Path:
    from ..paths import run_dir
    return run_dir(slug) / "versions" / vid


def load_context(slug: str, vid: str) -> QAContext:
    vdir = version_dir(slug, vid)
    tl_path = vdir / "timeline.json"
    if not tl_path.exists():
        raise FileNotFoundError(f"No existe {tl_path}")
    timeline = Timeline.model_validate(_load_json(tl_path))
    render = vdir / "render.mp4"
    if not render.exists():
        raise FileNotFoundError(f"No existe el render {render}")
    ctx = QAContext(slug=slug, vid=vid, vdir=vdir, timeline=timeline, render=render)
    plan_p = vdir / "plan.json"
    if plan_p.exists():
        try:
            ctx.plan = EditPlan.model_validate(_load_json(plan_p))
        except Exception as exc:
            ctx.notes.append(f"plan.json no válido ({type(exc).__name__}): se ignora")
    mi_p = vdir.parent.parent / "media_index.json"
    if mi_p.exists():
        try:
            ctx.media_index = MediaIndex.model_validate(_load_json(mi_p))
        except Exception as exc:
            ctx.notes.append(f"media_index.json no válido ({type(exc).__name__}): se ignora")
    for p in (vdir / "render_spec.json", vdir / "hf" / "render_spec.json"):
        if p.exists():
            try:
                ctx.render_spec = _load_json(p)
                break
            except Exception:
                pass
    faces = (ctx.render_spec.get("aroll", {}) or {}).get("faces") or timeline.style.get("faces") or []
    ctx.faces = [tuple(map(float, f[:5])) for f in faces if len(f) >= 5]
    if not ctx.faces and ctx.media_index and ctx.media_index.faces:
        ctx.faces = _faces_from_index(ctx)
    return ctx


def _faces_from_index(ctx: QAContext) -> list[tuple[float, float, float, float, float]]:
    """Caras del MediaIndex (tiempo de fuente) → tiempo de programa vía los segmentos de A-roll."""
    out = []
    for seg in ctx.timeline.aroll:
        for f in ctx.media_index.faces.get(seg.src, []):
            if seg.src_in <= f.t < seg.src_out:
                out.append((seg.prog_in + (f.t - seg.src_in), f.x, f.y, f.w, f.h))
    return sorted(out)


def face_at(ctx: QAContext, t: float, max_dt: float = 0.6) -> tuple[float, float, float, float] | None:
    if not ctx.faces:
        return None
    best = min(ctx.faces, key=lambda f: abs(f[0] - t))
    return best[1:] if abs(best[0] - t) <= max_dt else None


def item_texts(it: TimelineItem) -> list[str]:
    """Cadenas de texto visibles que declara un ítem en sus props (recorrido recursivo de claves de texto)."""
    keys = {"text", "title", "subtitle", "label", "labels", "lines", "items", "headline", "caption", "value", "kicker",
            "body", "name", "words", "bullets", "steps", "stat", "unit", "quote"}
    out: list[str] = []

    def walk(v: Any, k: str | None) -> None:
        if isinstance(v, str):
            if k in keys and v.strip() and not v.startswith(("media/", "http", "#")) and not re.fullmatch(r"w_\d+", v):
                out.append(v.strip())
        elif isinstance(v, dict):
            for kk, vv in v.items():
                if kk in ("src", "asset", "path", "color", "font", "ease", "id"):
                    continue
                walk(vv, kk if kk in keys else (k if k in keys and kk in ("t", "text", "label") else kk))
        elif isinstance(v, list):
            for x in v:
                walk(x, k)

    walk(it.props, None)
    return list(dict.fromkeys(out))


def caption_words(it: TimelineItem, word_times: dict[str, Any] | None = None) -> list[str]:
    """Ids de palabra de una página de subtítulo: props.words[].id (compilador), props.word_ids, o las decisiones
    `caption.<id>`. Con `word_times` se aceptan solo ids que existen en la timeline."""
    raw: list[str] = []
    for x in (it.props.get("word_ids") or []) + (it.props.get("words") or []):
        if isinstance(x, str):
            raw.append(x)
        elif isinstance(x, dict) and isinstance(x.get("id"), str):
            raw.append(x["id"])
    if not raw:
        raw = [d.split(".", 1)[1] for d in it.decision_ids if d.startswith("caption.")]
    if word_times is not None:
        return [w for w in raw if w in word_times]
    return [w for w in raw if re.fullmatch(r"[\w-]*w_?\d{1,6}", w)]


def cam_kind(it: TimelineItem) -> str:
    """Tipo de un ítem de cámara/transición: props.kind o la última parte del componente (camera.punch_in → punch_in)."""
    return str(it.props.get("kind") or (it.component or "").split(".")[-1])
