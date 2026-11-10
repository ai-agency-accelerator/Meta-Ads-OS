"""Compilador: EditPlan (decisiones ancladas a palabras) → Timeline (segundos de programa) → render_spec → proyecto HF.

Determinista: mismas entradas → misma salida. El LLM nunca escribe tiempos; aquí se resuelven las anclas a fotograma.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import yaml

from . import captions as capmod
from . import clipcuts, textcase
from .analyze import load_index
from . import sistema
from .paths import FONTS, PERFILES, RAIZ, RECURSOS, cliente_de, run_dir, version_dir
from .spec import (ArollSegment, AssetManifest, AudioItem, Decision, EditPlan, MediaIndex, Timeline, TimelineItem)

MOTION_TOKENS = RECURSOS / "motion_tokens.yaml"

TRACK_OF = {"layout": "layout", "camera": "camera", "broll": "broll", "graphic": "graphic", "transition": "transition"}
DEFAULT_COMPONENT = {"layout": "layout.full_face", "camera": "camera.punch_in", "broll": "media.slot",
                     "transition": "transition.light_leak"}


# ───────────────────────────── utilidades ─────────────────────────────
def _has_text(it) -> bool:
    """¿La pieza enseña texto? Todo gráfico salvo media/escenas 3D/B-roll (para no cruzar dos textos en un relevo)."""
    comp = str(getattr(it, "component", "") or "")
    return getattr(it, "track", "") in ("graphic", "overlay") and not comp.startswith(("media.", "scene.", "layout.", "camera."))


def _is_real_media(it) -> bool:
    """¿Es una captura o un vídeo REAL (pista `broll`, `media.*`, `scene.*`)? 20-oct-2026 (fidelidad de un vídeo de prueba,
    BLOCK): una captura real entra y sale en corte seco (o fundiéndose con el fondo del panel), nunca en doble exposición
    con otra pieza: 2 f de una baldosa encima de la web real eran una captura alterada."""
    comp = str(getattr(it, "component", "") or "")
    return getattr(it, "track", "") == "broll" or comp.startswith(("media.", "scene."))


def _points_into(g, under) -> bool:
    """¿`g` es un señalador (`callout.*` con `target`) que empieza DENTRO de la captura real `under`? Entonces va encima
    de ella (su `target` está medido sobre esa imagen): no la releva ni la recorta. 20-oct-2026 (un vídeo de prueba,
    d021a): la flecha al ojo del grupo «06 · Color Grading» recortaba el panel Capas (d021f) y apuntaba a un panel vacío."""
    return (str(getattr(g, "component", "") or "").startswith("callout.") and "target" in (g.props or {})
            and _is_real_media(under) and under.t0 - 1e-3 <= g.t0 < under.t1 - 1e-3)


def snap(t: float, fps: int) -> float:
    return round(round(t * fps) / fps, 4)


def load_profile(fmt: str = "anuncio", outro_variant: str = "") -> dict:
    """Perfil de `recursos/perfiles/<fmt>.yaml` (anuncio | organico) con el cierre de la variante pedida."""
    p = PERFILES / f"{fmt}.yaml"
    if not p.exists():
        hay = ", ".join(sorted(x.stem for x in PERFILES.glob("*.yaml")))
        raise ValueError(f"no existe el perfil «{fmt}» (hay: {hay})")
    return with_outro(yaml.safe_load(p.read_text(encoding="utf-8")), outro_variant)


def with_outro(profile: dict, variant: str = "") -> dict:
    """El perfil con el cierre de la variante pedida (`plan.outro_variant`) o la por defecto del perfil.
    Un perfil puede declarar varios cierres en `outro.variants` (p. ej. uno para negocio y otro para comunidad)."""
    o = dict(profile.get("outro") or {})
    vs = o.get("variants") or {}
    key = variant or o.get("default", "")
    if variant and variant not in vs:
        raise ValueError(f"outro «{variant}» no existe en el perfil (hay: {', '.join(vs) or 'ninguno'})")
    if key in vs:
        o = {**o, **vs[key], "variant": key}
    return {**profile, "outro": o}


def load_plan(slug: str, vid: str) -> EditPlan:
    return EditPlan.model_validate_json((version_dir(slug, vid) / "plan.json").read_text())


def load_manifest(slug: str) -> AssetManifest:
    p = run_dir(slug) / "assets.json"
    return AssetManifest.model_validate_json(p.read_text()) if p.exists() else AssetManifest(slug=slug)


# ───────────────────────────── A-roll ─────────────────────────────
def build_aroll(mi: MediaIndex, plan: EditPlan, profile: dict, fps: int) -> list[ArollSegment]:
    """Segmentos de fuente que forman el programa. Respeta el corte del bruto; sólo aplica `aroll.cut` explícitos."""
    by_id = {w.id: w for w in mi.words}
    segs: list[ArollSegment] = []
    srcs = ["main"] + (["outro"] if plan.outro and profile.get("outro", {}).get("enabled") and
                       any(s.id == "outro" for s in mi.sources) else [])
    for sid in srcs:
        src = next(s for s in mi.sources if s.id == sid)
        ws = mi.words_of(sid)
        if sid == "outro":
            o = profile["outro"]
            a = min(o.get("trim_head", 0.0), max(0.0, ws[0].s - 0.05))
            b = min(src.duration, max(src.duration - o.get("trim_tail", 0.0), ws[-1].e + 0.15))
        else:
            a = max(0.0, ws[0].s - 0.12)
            b = min(src.duration, ws[-1].e + 0.30)
        cuts = []
        for d in plan.decisions:
            if d.type != "aroll.cut":
                continue
            w0, w1 = by_id.get(d.anchor.start), by_id.get(d.anchor.end or d.anchor.start)
            if w0 and w0.src == sid:
                # quita desde el final de la palabra anterior al tramo hasta el inicio de la palabra que sigue
                cuts.append((w0.s - d.params.get("pad_before", 0.02), w1.e + d.params.get("pad_after", 0.02)))
        cuts.sort()
        cur = a
        k = 0
        for c0, c1 in cuts:
            if c0 > cur:
                segs.append(ArollSegment(id=f"seg_{sid}_{k}", src=sid, src_in=snap(cur, fps), src_out=snap(c0, fps)))
                k += 1
            cur = max(cur, c1)
        if b > cur:
            segs.append(ArollSegment(id=f"seg_{sid}_{k}", src=sid, src_in=snap(cur, fps), src_out=snap(b, fps)))
    # respiración antes del outro: el último fotograma del contenido se congela un instante (sin él, «…ahí» y
    # «Por cierto» quedan a 133 ms y se pisan); la cama y la transición del outro cubren el hueco
    outro_first = next((k for k, s in enumerate(segs) if s.src == "outro"), None)
    if outro_first:
        segs[outro_first - 1].hold_after = snap(float((plan.tokens or {}).get("outro_gap_before",
                                                                   profile["outro"].get("gap_before", 0.3))), fps)
        # el vídeo no acaba en seco tras la última palabra: último fotograma (la CTA) congelado + cola de la música
        segs[-1].hold_after = snap(profile["outro"].get("hold_after", 0.0), fps)
    elif segs and float((plan.tokens or {}).get("end_hold", 0.0) or 0.0) > 0:
        # 19-oct-2026 (un vídeo de prueba, QA audio.music_tail_cut): SIN outro, el último fotograma se congela
        # `tokens.end_hold` s (≈0,5–0,6). Así la última palabra no la come el fundido del máster (la voz sigue hasta el
        # final real del wav y el congelado lleva ruido de sala) y el final propio de la música cae justo tras la última
        # palabra, en su downbeat, con la cola sonando entera en el congelado. Sin el token, todo queda como antes.
        segs[-1].hold_after = snap(float(plan.tokens["end_hold"]), fps)
    t = 0.0
    for s in segs:
        s.prog_in = round(t, 4)
        t += s.src_out - s.src_in + s.hold_after
        s.prog_out = round(t, 4)
    return segs


_DIMS: dict[str, tuple[int | None, int | None]] = {}


def media_dims(path: str) -> tuple[int | None, int | None]:
    """Ancho y alto reales de una imagen o vídeo (ffprobe; con caché en memoria)."""
    p = Path(path)
    if not p.is_absolute():
        p = RAIZ / p
    k = str(p)
    if k not in _DIMS:
        try:
            out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                  "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True).stdout.strip()
            w, h = (int(x) for x in out.split(",")[:2])
            _DIMS[k] = (w, h)
        except Exception:
            _DIMS[k] = (None, None)
    return _DIMS[k]


def clip_cuts_program(slug: str, mi: MediaIndex, segs: list[ArollSegment]) -> list[float]:
    """Cortes visibles de la cara en segundos de programa: saltos de toma dentro de cada segmento (detectados en la
    fuente) + las uniones entre segmentos (cortes de A-roll)."""
    try:
        by_src = clipcuts.for_sources(mi, run_dir(slug) / "media" / "clip_cuts.json")
    except Exception as e:              # sin ffmpeg/numpy: la regla no aplica, nunca rompe la compilación
        print(f"[clip_cuts] sin detección: {e}")
        return []
    out = []
    for k, s in enumerate(segs):
        if k:
            out.append(s.prog_in)
        for c in by_src.get(s.src, []):
            if s.src_in + 1e-3 < c < s.src_out - 1e-3:
                out.append(s.prog_in + (c - s.src_in))
    return sorted({round(t, 4) for t in out})


def src_to_prog(segs: list[ArollSegment], src: str, t: float) -> float | None:
    for s in segs:
        if s.src == src and s.src_in - 1e-6 <= t <= s.src_out + 1e-6:
            return s.prog_in + (t - s.src_in)
    return None


def word_times(mi: MediaIndex, segs: list[ArollSegment]) -> dict[str, tuple[float, float]]:
    out = {}
    for w in mi.words:
        s, e = src_to_prog(segs, w.src, w.s), src_to_prog(segs, w.src, w.e)
        if s is not None and e is None:
            seg = next(x for x in segs if x.src == w.src and x.src_in <= w.s <= x.src_out)
            e = seg.prog_out
        if s is not None and e is not None:
            out[w.id] = (round(s, 4), round(e, 4))
    return out


def normalize_layouts(items: list[TimelineItem], dur: float, fps: int) -> list[TimelineItem]:
    """Una sola capa de layout sin solapes: funde iguales contiguos, absorbe huecos < 0,6 s, rellena con cara."""
    lay = sorted([i for i in items if i.track == "layout"], key=lambda i: (i.t0, i.t1))
    rest = [i for i in items if i.track != "layout"]
    out: list[TimelineItem] = []
    # «igual» = mismo componente Y mismo lienzo/entrada: dos pantallas completas con fondos distintos son dos planos
    same = lambda a, b: a.component == b.component and {k: v for k, v in a.props.items() if k in ("panel_bg", "enter")} \
        == {k: v for k, v in b.props.items() if k in ("panel_bg", "enter")}
    for i in lay:
        if out and i.t0 < out[-1].t1:                      # solape
            if same(i, out[-1]):
                out[-1].t1 = max(out[-1].t1, i.t1)
                out[-1].decision_ids += [d for d in i.decision_ids if d not in out[-1].decision_ids]
                continue
            out[-1].t1 = i.t0                               # el nuevo manda desde su inicio
        if out and same(i, out[-1]) and i.t0 - out[-1].t1 < 0.6:
            out[-1].t1 = max(out[-1].t1, i.t1)
            out[-1].decision_ids += [d for d in i.decision_ids if d not in out[-1].decision_ids]
            continue
        out.append(i)
    filled: list[TimelineItem] = []
    cur, k = 0.0, 0
    for i in out:
        gap = i.t0 - cur
        if gap > 1 / fps:
            if gap < 0.6 and filled:                        # nada de destellos de cara de 6 fotogramas
                filled[-1].t1 = i.t0
            elif gap < 0.6:
                i.t0 = cur
            else:
                filled.append(TimelineItem(id=f"it_lay_default_{k}", track="layout", t0=snap(cur, fps), t1=i.t0,
                                           component="layout.full_face", z=1)); k += 1
        filled.append(i)
        cur = max(cur, i.t1)
    if dur - cur > 1 / fps:
        if dur - cur < 0.6 and filled:
            filled[-1].t1 = dur
        else:
            filled.append(TimelineItem(id=f"it_lay_default_{k}", track="layout", t0=snap(cur, fps), t1=dur,
                                       component="layout.full_face", z=1))
    filled = [i for i in filled if i.t1 - i.t0 > 1 / fps]
    # gráficos y B-roll que comparten slot: el anterior sale cuando entra el siguiente (+0,1 s de cruce). Los rótulos
    # «overlay» del registro (p. ej. label.mode_tag) van ENCIMA del clip: no compiten por el slot.
    from .motion.registry import COMPONENTS
    vis = sorted([i for i in rest if i.track in ("graphic", "broll")
                  and not (COMPONENTS.get(i.component or "") or {}).get("overlay")], key=lambda i: i.t0)
    # un señalador (callout.* con `target`) que empieza dentro de una captura real va encima de ella: no compite por el slot
    ptr = {id(g) for k, g in enumerate(vis) if any(_points_into(g, u) for u in vis[:k])}
    vis = [i for i in vis if id(i) not in ptr]
    for a, b in zip(vis, vis[1:]):
        if b.t0 < a.t1 and not (a.props.get("stack") or b.props.get("stack")):   # `stack`: se suman en el panel
            # una captura real nunca se cruza con otra pieza (ni 3 f): la anterior acaba donde entra la siguiente
            a.t1 = round(min(a.t1, b.t0 if (_is_real_media(a) or _is_real_media(b)) else b.t0 + 0.10), 4)
    return filled + rest


# ───────────────────────────── anclas ─────────────────────────────
def resolve_anchor(d: Decision, wt: dict, fps: int, dur: float) -> tuple[float, float] | None:
    a = d.anchor
    if a.start not in wt:
        return None
    s0 = wt[a.start][0 if a.start_edge == "s" else 1] + a.lead
    end_id = a.end or a.start
    if end_id not in wt:
        return None
    t1 = wt[end_id][1 if a.end_edge == "e" else 0] + a.tail
    if a.min_dur and t1 - s0 < a.min_dur:
        t1 = s0 + a.min_dur
    s0, t1 = max(0.0, snap(s0, fps)), min(dur, snap(t1, fps))
    return (s0, t1) if t1 > s0 else None


def resolve_cues(cues: dict[str, Any], wt: dict, lead: float = -0.12) -> dict[str, float]:
    out = {}
    for k, v in (cues or {}).items():
        if isinstance(v, (int, float)):
            out[k] = float(v)
        elif isinstance(v, str) and v in wt:
            out[k] = round(wt[v][0] + lead, 4)
        elif isinstance(v, dict) and v.get("word") in wt:
            out[k] = round(wt[v["word"]][0 if v.get("edge", "s") == "s" else 1] + v.get("offset", lead), 4)
    return out


# ───────────────────────────── outro ─────────────────────────────
def outro_decisions(profile: dict) -> list[Decision]:
    p = RAIZ / profile["outro"].get("plan", "")
    if not profile["outro"].get("plan") or not p.is_file():
        return []
    data = json.loads(p.read_text())
    return [Decision.model_validate(d) for d in data.get("decisions", [])]


# ───────────────────────────── compilación ─────────────────────────────
def compile_plan(slug: str, vid: str, build_html: bool = True) -> Timeline:
    mi = load_index(slug)
    plan = load_plan(slug, vid)
    profile = load_profile(plan.format, plan.outro_variant)
    man = load_manifest(slug)
    fps = profile["canvas"]["fps"]
    vd = version_dir(slug, vid)

    decisions = list(plan.decisions)
    if plan.outro and profile.get("outro", {}).get("enabled"):
        have = {d.id for d in decisions}
        decisions += [d for d in outro_decisions(profile) if d.id not in have]

    segs = build_aroll(mi, plan, profile, fps)
    dur = segs[-1].prog_out
    wt = word_times(mi, segs)
    items: list[TimelineItem] = []

    def asset_src(aid: str) -> dict | None:
        a = man.assets.get(aid)
        if not a:
            return None
        w, h = a.width, a.height
        if not (w and h) and (a.kind == "video" or Path(a.path).suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")):
            w, h = media_dims(a.path)               # sin medidas, cada worker de la captura las adivinaba a su manera
            #                                         (vídeo aún sin metadatos → 16:9) y la caja cambiaba de tamaño; los SVG no
        return {"id": f"m_{aid}", "kind": "video" if a.kind == "video" else "image", "src": f"media/{Path(a.path).name}",
                "path": a.path, "width": w, "height": h, "duration": a.duration}

    for d in decisions:
        if d.type not in TRACK_OF:
            continue
        rng = resolve_anchor(d, wt, fps, dur)
        if not rng:
            continue
        t0, t1 = rng
        props = textcase.props_titulo(dict(d.params.get("props", {})))   # rótulos en Title Case inteligente
        media = []
        for aid in d.params.get("assets", []):
            m = asset_src(aid)
            if m:
                m = dict(m, id=f"m_{aid}__{d.id}", asset=aid)     # id único por item (HF exige ids de media únicos)
                media.append(m)
        item = TimelineItem(id=f"it_{d.id}", track=TRACK_OF[d.type], t0=t0, t1=t1,
                            component=d.params.get("component") or DEFAULT_COMPONENT.get(d.type),
                            props=props, cues=resolve_cues(d.params.get("cues", {}), wt), decision_ids=[d.id],
                            z=d.params.get("z", {"layout": 1, "camera": 2, "broll": 5, "graphic": 20, "transition": 60}[d.type]))
        if media:
            item.props["_media"] = media
        for k in ("sfx", "hide_captions"):
            if k in d.params and k not in item.props:
                item.props[k] = d.params[k]
        items.append(item)

    PANEL_LAYOUTS = ("layout.split_top", "layout.broll_full")
    # nunca un panel vacío: si la primera cue de un gráfico llega >0,6 s después de su entrada, el gráfico (y el split
    # que lo contiene) arrancan en esa cue − 0,155 s; hasta entonces sigue el layout anterior (cara)
    for it in items:
        if it.track == "graphic" and it.cues and not it.props.get("keep_start"):
            first = min(it.cues.values())
            if first - it.t0 > 0.6:
                new_t0 = snap(first - 0.155, fps)
                for lay in items:
                    if lay.track == "layout" and lay.component in PANEL_LAYOUTS and abs(lay.t0 - it.t0) < 1.0:
                        lay.t0 = max(lay.t0, new_t0)
                it.t0 = new_t0
    # y el split nunca arranca antes que su primer contenido (gráfico o B-roll) por más de 0,3 s
    for lay in items:
        if lay.track == "layout" and lay.component in PANEL_LAYOUTS:
            inside = [i for i in items if i.track in ("graphic", "broll") and lay.t0 - 0.05 <= i.t0 < lay.t1]
            if inside:
                first = min(i.t0 for i in inside)
                if first - lay.t0 > 0.3:
                    lay.t0 = first
    # layouts: una sola capa continua, sin destellos; gráficos del mismo slot sin pisarse
    items = normalize_layouts(items, dur, fps)
    # pista de layout contigua: un hueco de < 0,25 s entre dos layouts no puede enseñar la cara cruda 1–7 fotogramas
    lays = sorted([i for i in items if i.track == "layout"], key=lambda i: i.t0)
    for a, b in zip(lays, lays[1:]):
        if 0 < b.t0 - a.t1 < 0.25:
            if a.component in PANEL_LAYOUTS:    # su contenido se alarga con él: nunca unos fotogramas de panel vacío
                for i in items:
                    if i.track in ("graphic", "broll") and a.t0 - 0.05 <= i.t0 < a.t1 and abs(i.t1 - a.t1) < 0.05:
                        i.t1 = b.t0
            a.t1 = b.t0
    # el último contenido de un panel llega hasta el final de su panel (si acaba < 0,35 s antes): nunca un panel vacío
    # entre que sale el gráfico y cambia el layout (normalize_layouts absorbe huecos y alarga el panel, no su contenido)
    for lay in lays:
        if lay.component in PANEL_LAYOUTS:
            inside = [i for i in items if i.track in ("graphic", "broll") and lay.t0 - 0.05 <= i.t0 < lay.t1]
            if inside:
                last = max(inside, key=lambda i: i.t1)
                if 0 < lay.t1 - last.t1 < 0.35:
                    last.t1 = lay.t1
    # cambios de layout pegados al corte del clip: si el bruto ya trae un corte (salto entre tomas) a ≤ 0,5 s de un
    # cambio de layout, el cambio cae EXACTAMENTE en ese corte; si no, se ven dos cortes seguidos a 3–4 fotogramas. Todo
    # lo que empieza o acaba en ese límite se mueve.
    # nunca dos cambios de plano seguidos: si un punch-in con corte entra < 0,8 s después de volver a la cara, la vuelta
    # a la cara se retrasa hasta ese corte (si no, la cara asoma un instante sin subtítulos y queda raro)
    lays = sorted([i for i in items if i.track == "layout"], key=lambda i: i.t0)
    for a, b in zip(lays, lays[1:]):
        if b.component != "layout.full_face" or a.component == "layout.full_face" or abs(a.t1 - b.t0) > 0.02:
            continue
        bnd = b.t0
        cams = [c for c in items if c.track == "camera" and c.props.get("cut") and bnd + 1e-3 < c.t0 <= bnd + 0.8]
        if not cams:
            continue
        c0 = min(c.t0 for c in cams)
        if b.t1 - c0 < 0.4:
            continue
        for i in items:
            if i.track in ("layout", "graphic", "broll") and abs(i.t1 - bnd) <= 0.02 and c0 - i.t0 >= 0.2:
                i.t1 = c0
        b.t0 = c0
    # cifras, logos y titulares a pantalla completa: centrados en la pantalla
    fulls = [l for l in items if l.track == "layout" and l.component == "layout.broll_full"]
    for g in items:
        if g.track == "graphic" and g.component in ("stat.big_number", "logo.reveal", "title.lockup_grid") \
                and any(l.t0 - 0.05 <= g.t0 < l.t1 for l in fulls):
            g.props.setdefault("band", "center")
            if g.component == "stat.big_number":
                g.props.setdefault("anchor", 0.5)
    pcuts = clip_cuts_program(slug, mi, segs)
    lays = sorted([i for i in items if i.track == "layout"], key=lambda i: i.t0)
    for a, b in zip(lays, lays[1:]):
        bnd = b.t0
        if abs(a.t1 - bnd) > 0.02 or not pcuts:
            continue
        c = min(pcuts, key=lambda x: abs(x - bnd))
        if not (0.5 / fps < abs(c - bnd) <= 0.5) or c - a.t0 < 0.4 or b.t1 - c < 0.4:
            continue
        for i in items:
            if i.track not in ("layout", "graphic", "broll", "camera"):
                continue
            if abs(i.t0 - bnd) <= 0.02 and i.t1 - c >= 0.2:
                i.t0 = c
            if abs(i.t1 - bnd) <= 0.02 and c - i.t0 >= 0.2:
                i.t1 = c
    # cortes de cámara pegados a un cambio de layout: caen EXACTAMENTE en ese cambio (si no, el punch-in se ve unos
    # fotogramas dentro del layout anterior —zoom raro en la mitad de abajo— y luego cambia el plano)
    lb = sorted({round(i.t0, 4) for i in items if i.track == "layout"} | {round(i.t1, 4) for i in items if i.track == "layout"})
    for cam in items:
        if cam.track == "camera" and cam.props.get("cut"):
            near = [b for b in lb if abs(b - cam.t0) <= 0.3]
            if near:
                b = min(near, key=lambda x: abs(x - cam.t0))
                if b < cam.t1 - 0.2:
                    cam.t0 = b
    # transiciones: el corte cae en el cambio de layout que tienen dentro (o en su centro)
    bounds = sorted({i.t0 for i in items if i.track == "layout"} | {i.t1 for i in items if i.track == "layout"})
    for it in items:
        if it.track == "transition" and "cut" not in it.cues:
            inside = [b for b in bounds if it.t0 - 0.25 <= b <= it.t1 + 0.25]
            it.cues["cut"] = round(min(inside, key=lambda b: abs(b - (it.t0 + it.t1) / 2)) if inside else (it.t0 + it.t1) / 2, 4)
            cut, w = it.cues["cut"], it.t1 - it.t0
            if not (it.t0 + 1 / fps <= cut <= it.t1 - 1 / fps):     # la ventana siempre contiene su corte (40 % antes)
                it.t0, it.t1 = snap(cut - 0.4 * w, fps), snap(cut + 0.6 * w, fps)
    # gráficos/B-roll seguidos en el mismo panel (< 2,5 s): el anterior acaba justo donde entra el siguiente, sin salida
    # (solo si los dos viven en la MISMA instancia de panel: nunca se alarga un gráfico por encima de un plano de cara)
    panels = [l for l in items if l.track == "layout" and l.component != "layout.full_face"]
    panel_of = lambda t: next((l for l in panels if l.t0 - 0.05 <= t < l.t1), None)
    from .motion.registry import COMPONENTS as _COMP    # los rótulos «overlay» van encima: no se encadenan
    vis = sorted([i for i in items if i.track in ("graphic", "broll")
                  and not (_COMP.get(i.component or "") or {}).get("overlay")], key=lambda i: i.t0)
    # 18-oct-2026 (críticas de un vídeo de prueba: «la composición desaparece en un fotograma y lo
    # siguiente empieza vacío»): dentro del MISMO panel no hay corte de plano que justifique una salida en seco. El
    # anterior sale con su salida animada corta (5 f, `exit: "fade"`, acelerando) y se cruza 2 f con la entrada del
    # siguiente: el panel nunca queda vacío ni cambia de golpe, y no hay más de 1 f con los dos textos legibles (tr.dirty_crossfade). En seco solo si el siguiente es la MISMA pieza que continúa su estado
    # (mismo componente: la rejilla con `carry`, un diagrama que sigue), si el plan ya trae `exit` o si no cabe el cruce
    # antes del final del panel. Cuando cambia el layout, el corte de plano lo pone html.py (`exit: "cut"` en su límite).
    xf = 2 / fps
    # un señalador sobre una captura real (callout.* con `target` que empieza dentro de ella) no entra en la cadena: la
    # captura sigue debajo hasta su final y el señalador solo se encadena con la pieza que llega después
    ptr = {id(g) for k, g in enumerate(vis)
           if any(_points_into(g, u) and panel_of(u.t0 + 0.02) is panel_of(g.t0 + 0.02) for u in vis[:k])}
    chain = [i for i in vis if id(i) not in ptr]
    pairs = list(zip(chain, chain[1:]))
    for g in vis:
        if id(g) in ptr:
            nxt = next((i for i in chain if i.t0 > g.t0 + 1e-3), None)
            if nxt is not None:
                pairs.append((g, nxt))
    for a, b in pairs:
        if a.props.get("stack") or b.props.get("stack"):   # se suman en el mismo panel (barra + cabeceras): no se recortan
            continue
        if 0 <= b.t0 - a.t1 < 2.5 or b.t0 < a.t1:
            pa, pb = panel_of(a.t0 + 0.02), panel_of(b.t0 + 0.02)
            if pa is not None and pa is pb:
                same_piece = a.component == b.component
                if "exit" in a.props or same_piece or b.t0 + xf > pa.t1 - 2 / fps:
                    a.t1 = b.t0
                    a.props.setdefault("exit", "cut")
                    # captura → captura en corte: la siguiente entra en corte también (si no, 8 f de fundido desde el
                    # panel vacío: d021 → d021f de un vídeo de prueba, el plan ya traía `exit: "cut"`)
                    if a.props.get("exit") == "cut" and _is_real_media(a) and str(b.component or "").startswith("media."):
                        b.props.setdefault("enter", "cut")
                elif _is_real_media(a) or _is_real_media(b):
                    # 20-oct-2026 (fidelidad de un vídeo de prueba, BLOCK: póster y panel Capas en doble exposición en
                    # 0:28,57 y 0:30,60; una baldosa 2 f sobre la web real en 1:01,40). Una captura o vídeo REAL
                    # no se cruza nunca con el plano anterior ni con el siguiente: sale en corte seco (o, si el plan pide
                    # `exit: "fade"`, fundiéndose con el fondo del panel en sus últimos 5 f, sin nada encima). Un gráfico
                    # que deja paso a una captura sale en sus 5 f y la captura entra al acabar (como dos textos). Entre dos
                    # capturas del mismo panel, corte seco también a la entrada (el cambio de recurso es un corte de montaje).
                    a.t1 = b.t0
                    a.props["exit"] = "cut" if _is_real_media(a) else "fade"
                    if _is_real_media(a) and str(b.component or "").startswith("media."):
                        b.props.setdefault("enter", "cut")
                elif _has_text(a) and _has_text(b):
                    # 18-oct (crítica de v007, BLOCK): dos piezas con texto NO se cruzan («Comenta» y «El Lead» se leían a la
                    # vez que el texto que salía): la anterior sale en sus 5 f y la siguiente empieza al acabar esa salida
                    a.t1 = b.t0
                    a.props["exit"] = "fade"
                else:
                    a.t1 = snap(b.t0 + xf, fps)
                    a.props["exit"] = "fade"
    # 28-oct-2026 (un vídeo de prueba, crítica de la v004: «destellos de blanco vacío de 2–3 f entre la
    # salida de un gráfico y la entrada del siguiente»): `overlap_in` (fotogramas, 1–6, opcional en el item) = la pieza
    # arranca N f ANTES de que acabe la salida de la anterior del MISMO panel (se adelanta su t0; el t1 de la anterior no
    # se toca). Pensado para cuando la anterior sale con `exit: "fade"`. Sin la prop, nada cambia
    _ov_done = set()
    for a, b in pairs:
        n = int(b.props.get("overlap_in") or 0)
        if n <= 0 or id(b) in _ov_done:
            continue
        pa, pb = panel_of(a.t0 + 0.02), panel_of(b.t0 + 0.02)
        if pa is None or pa is not pb or abs(a.t1 - b.t0) > 0.5 / fps:
            continue
        b.t0 = snap(max(a.t0 + 0.2, b.t0 - min(6, n) / fps), fps)
        _ov_done.add(id(b))
    for it in items:                               # props por defecto del perfil para cada layout
        for k, v in (profile.get("layout_defaults", {}).get(it.component or "", {}) or {}).items():
            it.props.setdefault(k, v)
    outro_seg = next((s for s in segs if s.src == "outro"), None)
    if outro_seg and profile["outro"].get("transition_in"):
        t = outro_seg.prog_in                          # el destello cubre la respiración congelada y cae en el corte
        hold = segs[segs.index(outro_seg) - 1].hold_after if segs.index(outro_seg) else 0.0
        ts = profile["outro"].get("transition_s")       # duración propia (p. ej. 0,3 s); si no, la de siempre
        ta, tb = (t - ts / 2, t + ts / 2) if ts else (t - max(0.2, hold), t + 0.2)
        items.append(TimelineItem(id="it_outro_transition", track="transition", t0=snap(ta, fps),
                                  t1=snap(tb, fps), component=profile["outro"]["transition_in"],
                                  props={"intensity": 0.8, **(profile["outro"].get("transition_props") or {})},
                                  cues={"cut": round(t, 4)}, z=60, decision_ids=["perfil.outro"]))

    # subtítulos
    hidden = []
    for d in decisions:
        if d.type == "caption.hide":
            r = resolve_anchor(d, wt, fps, dur)
            if r:
                hidden.append(r)
    for it in items:
        if it.props.get("hide_captions"):
            hidden.append((it.t0, it.t1))
    emph = {}
    for d in decisions:
        if d.type == "caption.emphasis":
            ids = [d.anchor.start] + ([d.anchor.end] if d.anchor.end else [])
            ids += d.params.get("words", [])
            for wid in ids:
                emph[wid] = d.params.get("treatment", "accent")
    pw = []
    order = [w for w in mi.words if w.id in wt]
    order.sort(key=lambda w: wt[w.id][0])
    for k, w in enumerate(order):
        s, e = wt[w.id]
        if any(a - 0.05 <= s <= b for a, b in hidden):
            continue
        nxt = wt[order[k + 1].id][0] if k + 1 < len(order) else dur
        pw.append({"id": w.id, "src": w.src, "text": w.text, "punct": w.punct_after, "s": s, "e": e, "gap": nxt - e})
    pages = capmod.group_pages(pw)
    wins = capmod.page_windows(pages, fps, dur)
    # una página que empieza o acaba a ≤2 fotogramas de un cambio de layout se pega al corte: si no, la palabra sale un
    # fotograma en la posición del layout anterior (cara ↔ junta) y se lee como un parpadeo
    lay_cuts = sorted({0.0} | {round(i.t0, 4) for i in items if i.track == "layout" and i.t0 > 0})
    tol = 2.5 / fps
    def _snap_cut(t):
        for L in lay_cuts:
            if abs(t - L) <= tol:
                return L
        return t
    wins = [(_snap_cut(a), _snap_cut(b)) for a, b in wins]
    for k, (pg, (a, b)) in enumerate(zip(pages, wins)):
        for (h0, h1) in hidden:            # recorta la página si un tramo oculto empieza antes de que acabe
            if a < h0 < b:
                b = h0
        if b - a < 0.15:
            continue
        hero = any(emph.get(w["id"]) == "hero" for w in pg)
        words = [{"id": w["id"], "text": w["text"] + ("" if not w["punct"] or w["punct"] in ".," else w["punct"].replace(",", "")),
                  "t0": round(max(w["s"], a), 4), "t1": round(w["e"], 4), "emphasis": emph.get(w["id"])} for w in pg]
        items.append(TimelineItem(id=f"cap_{k:03d}", track="caption", t0=snap(a, fps), t1=snap(b, fps),
                                  component="caption.lockup" if hero else "caption.rail",
                                  props={"words": words, "y": profile["captions"]["rail_y"]}, z=40,
                                  decision_ids=[f"caption.{w['id']}" for w in pg]))

    items.sort(key=lambda i: (i.t0, i.z))

    # audio
    audio: list[AudioItem] = []
    rd = run_dir(slug)
    voice_end: dict[str, float] = {}                   # fin real de la voz de cada segmento (en la fuente)
    for s in segs:
        src = next(x for x in mi.sources if x.id == s.src)
        voice = rd / "media" / f"voice_{s.src}.wav"
        vpath = voice if voice.exists() else Path(src.audio)
        src_end, fout = min(s.src_out, src.duration), (0.04 if s is segs[-1] else 0.008)
        if s.hold_after > 0:
            # antes de un congelado (el outro) la última palabra no se corta en el fin del vídeo: la voz sigue hasta el
            # final real del wav (sin pasar del congelado) con un fundido de 35 ms
            try:
                import soundfile as _sf
                src_end = min(max(src_end, _sf.info(str(vpath)).duration), s.src_out + s.hold_after)
            except Exception:                         # noqa: BLE001 — sin soundfile: el fin de la fuente
                pass
            fout = 0.035
        voice_end[s.id] = src_end
        audio.append(AudioItem(id=f"a_{s.id}", kind="voice", path=str(vpath),
                               t0=s.prog_in, media_start=s.src_in,
                               dur=round(src_end - s.src_in, 4),   # nunca más allá del wav
                               fade_in=0.008, fade_out=fout))
    # 27-oct-2026 (en un vídeo de prueba) · token opcional `voice_gain`: ventanas cortas de GANANCIA de voz
    #   (no es un reductor de ruido: solo baja el nivel en esa ventana, p. ej. un chasquido de boca entre dos palabras),
    #   ancladas a una palabra: [{"word": id, "edge": "s"|"e", "offset": s, "dur": s, "db": dB}], con rampas de 5 ms y
    #   solo dentro de un tramo de voz. Sin el token, nada cambia
    for vg in (plan.tokens or {}).get("voice_gain") or []:
        w = wt.get(str(vg.get("word")))
        if not w:
            print(f"[voz] voice_gain: palabra sin resolver ({vg.get('word')})")
            continue
        a = float(w[1] if vg.get("edge") == "e" else w[0]) + float(vg.get("offset", 0.0))
        b = a + max(0.005, min(0.5, float(vg.get("dur", 0.04))))
        db = max(-30.0, min(0.0, float(vg.get("db", -15.0))))
        for ai in audio:
            if ai.kind == "voice" and ai.id.startswith("a_") and ai.t0 <= a - 0.005 and b + 0.005 <= ai.t0 + (ai.dur or 0.0):
                ai.automation = sorted(list(ai.automation or []) + [(round(a - 0.005, 4), 0.0), (round(a, 4), db),
                                                                    (round(b, 4), db), (round(b + 0.005, 4), 0.0)])
    for s in segs:                                     # respiración congelada: ruido de sala de esa misma voz
        if s.hold_after > 0:
            src = next(x for x in mi.sources if x.id == s.src)
            voice = rd / "media" / f"voice_{s.src}.wav"
            end = s.prog_in + voice_end.get(s.id, min(s.src_out, src.duration)) - s.src_in
            audio.append(AudioItem(id=f"roomtone_{s.id}", kind="voice", path=str(voice if voice.exists() else src.audio),
                                   t0=round(end, 4), dur=round(s.prog_out - end, 4), gain_db=0.0))
    music = man.assets.get("music_bed")
    if music and profile["music"].get("enabled", True):
        # re-encaje sin coste (sale de la biblioteca): el final propio de la pista cae en el final del vídeo y ningún
        # empalme cae cerca de un momento clave (cues de gráficos y transiciones)
        try:
            from .audio import music as musicmod
            keys = sorted({round(c, 2) for i in items if i.track in ("graphic", "transition") for c in i.cues.values()})
            # el final propio de la pista cae justo tras la última palabra y su cola suena durante el fotograma congelado
            last_word = max((e for _, e in wt.values()), default=dur)
            end_at = min(dur - 0.03, last_word + 0.08) if segs[-1].hold_after > 0 else dur - profile["music"].get("end_before", 0.03)
            # pistas con cola larga: el plan puede adelantar su final para que la cola suene entera (QA audio.music_tail_cut)
            end_at += float((plan.tokens or {}).get("music_end_shift", 0.0))
            mres = musicmod.ensure(profile["music"].get("brief"), dur, rd / "media", allow_generate=False,
                                   end_at=round(end_at, 3), avoid_times=keys,
                                   track=(plan.tokens or {}).get("music_track"))
            music = type("M", (), {"path": str(mres.path)})()
        except Exception as e:                                    # sin re-encaje: la cama de `ck assets` tal cual
            print(f"[música] sin re-encaje ({e})")
        auto = [(0.0, profile["music"]["gain_lu"])]
        drops_win = []
        for d in decisions:
            if d.type == "music" and d.params.get("dropout"):
                r = resolve_anchor(d, wt, fps, dur)
                if r:
                    g = profile["music"]["gain_lu"]
                    auto += [(r[0] - 0.12, g), (r[0], -60.0), (r[1], -60.0), (r[1] + 0.25, g)]
                    drops_win.append((r[0] - 0.12, r[1] + 0.25))
        if outro_seg:
            g2 = profile["outro"].get("music", {}).get("gain_lu", -24.0)
            pre = outro_seg.prog_in - 0.3
            # dentro de un drop-out manda el drop-out (antes subía la cama sobre «sen-» y salía y entraba 3 veces)
            if not any(a <= pre <= b for a, b in drops_win):
                auto += [(pre, profile["music"]["gain_lu"])]
            auto += [(outro_seg.prog_in + 0.4, g2)]
        auto.sort()
        audio.append(AudioItem(id="a_music", kind="music", path=music.path, t0=0.0, dur=dur, gain_db=0.0,
                               fade_in=0.03, fade_out=0.05, automation=auto, decision_ids=["perfil.music"]))
    try:
        from .audio import sfxplan
        sfx_items = sfxplan.plan(decisions, items, wt, fps, dur, profile)
    except ImportError:
        sfx_items = plan_sfx(decisions, items, wt, fps, dur, profile)
    audio += sfx_items

    # el último plano llega al último fotograma: en un Short en bucle, 1 fotograma de otro layout se ve como un corte
    for it in items:
        if it.track in ("layout", "graphic") and dur - 0.15 < it.t1 < dur:
            it.t1 = dur
    tl = Timeline(slug=slug, version=vid, fps=fps, width=profile["canvas"]["width"], height=profile["canvas"]["height"],
                  duration=dur, aroll=segs, items=items, audio=audio, word_times=wt,
                  style={"profile": plan.style_profile or "firma"})
    (vd / "timeline.json").write_text(tl.model_dump_json(indent=1))
    spec = render_spec(tl, mi, plan, profile)
    (vd / "render_spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1))
    if build_html:
        build_program(tl, mi, vd)
        if any(s.id.endswith("_split") for s in mi.sources):      # el bruto trae también la versión 50/50
            build_program(tl, mi, vd, variant="split")
            spec["aroll"]["split_src"] = "media/program_split.mp4"
            spec["aroll"]["split_path"] = str(vd / "program_split.mp4")
            spec["aroll"]["split_seam"] = 960
            spec["aroll"]["split_sources"] = sorted(s.id[:-6] for s in mi.sources if s.id.endswith("_split"))
            spec["aroll"]["split_ranges"] = [[s.prog_in, s.prog_out] for s in tl.aroll
                                            if any(x.id == f"{s.src}_split" for x in mi.sources)]
            (vd / "render_spec.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1))
        from .motion.html import build_project
        build_project(spec, vd / "hf")
        # segunda pasada de SFX: cada efecto se alinea al instante VISUAL real (eventos que emiten los componentes)
        try:
            from .audio import sfxplan
            sfxplan.align_version(slug, vid)
            tl = Timeline.model_validate_json((vd / "timeline.json").read_text())
        except Exception as e:
            print(f"[sfx] sin alineación visual ({e}); se quedan en las cues de palabra")
    return tl


# ───────────────────────────── SFX ─────────────────────────────
def plan_sfx(decisions: list[Decision], items: list[TimelineItem], wt: dict, fps: int, dur: float, profile: dict) -> list[AudioItem]:
    """SFX explícitos (decisiones `sfx`) + eventos que declaran los componentes, con presupuesto de densidad."""
    try:
        from .audio import sfx as sfxmod
        from .motion.registry import COMPONENTS
    except Exception:
        return []
    cands = []
    for d in decisions:
        if d.type == "sfx":
            r = resolve_anchor(d, wt, fps, dur)
            if r:
                cands.append((r[0] + d.params.get("offset", 0.0), d.params["kind"], d.params.get("gain_db", 0.0), d.id, 10,
                              d.params.get("max_dur", 1.5)))
    for it in items:
        if it.track == "caption" or it.props.get("sfx") is False:
            continue
        spec = COMPONENTS.get(it.component or "", {})
        evs = spec.get("sfx", []) if isinstance(spec, dict) else getattr(spec, "sfx", [])
        for ev in evs or []:
            at = ev.get("at", "enter")
            t = (it.t0 if at == "enter" else it.t1 if at == "exit" else (it.t0 + it.t1) / 2 if at in ("cut", "mid")
                 else it.cues.get(at.split(":", 1)[-1]))
            if t is None:
                continue
            prio = 5 if it.track == "transition" else 3
            cands.append((t + ev.get("offset", 0.0), ev["kind"], ev.get("gain_db", 0.0), it.decision_ids[0] if it.decision_ids else it.id, prio,
                          0.9 if it.track == "transition" else max(0.25, it.t1 - t)))
    cands.sort()
    budget = max(1, int(profile["sfx"]["max_per_min"] * dur / 60))
    chosen, last_t = [], -9.0
    for c in sorted(cands, key=lambda c: -c[4]):          # prioridad: explícitos > transiciones > componentes
        if len(chosen) >= budget:
            break
        if any(abs(c[0] - x[0]) < 1.2 for x in chosen):   # nunca dos SFX en menos de 1,2 s
            continue
        chosen.append(c)
    chosen.sort()
    out = []
    picker = sfxmod.Picker(seed=hash(tuple(round(c[0], 2) for c in chosen)) % 9973) if hasattr(sfxmod, "Picker") else None
    for k, (t, kind, g, did, _, room) in enumerate(chosen):
        try:
            pick = picker.pick(kind) if picker else sfxmod.pick(kind, seed=k)
        except LookupError:
            continue
        fdur = pick.get("dur") or 1.5
        cap = 0.9 if kind not in ("riser", "riser_revelacion", "tension_tiempo") else 2.5
        sdur = round(max(0.15, min(fdur, cap, room)), 3)
        out.append(AudioItem(id=f"sfx_{k:02d}", kind="sfx", path=pick["path"], t0=round(t, 4),
                             media_start=pick.get("media_start", 0.0) or 0.0, dur=sdur, fade_out=min(0.08, sdur / 3),
                             gain_db=pick.get("mix_gain_db", 0.0) + g, sync_offset=pick.get("sync_offset", 0.0) or 0.0,
                             decision_ids=[did]))
    return out


# ───────────────────────────── render spec ─────────────────────────────
NEUTRAL_TOKENS = {"subject_color": "#60A5FA", "accent": "#FACC15"}   # sin marca del cliente: azul y amarillo legibles


def brand_tokens(cliente: str | None) -> dict:
    """Colores de la marca del cliente para los gráficos animados: `subject_color` ← primario, `accent` ← acento.
    Sin `marca.json` del cliente, una pareja neutra legible sobre fondo claro y oscuro. Las tipografías de marca se
    aplican en `ck anuncio`; los gráficos del montaje avanzado usan Montserrat, Inter y JetBrains Mono (incluidas)."""
    from .marca import MarcaInvalida, cargar
    try:
        m = cargar(cliente) if cliente else None
    except MarcaInvalida as e:
        print(f"[compile] marca de «{cliente}» no válida ({e}): uso colores neutros")
        m = None
    if m is None or m.carpeta is None:
        return dict(NEUTRAL_TOKENS)
    return {"subject_color": m.color("primario"), "accent": m.color("acento"),
            "brand": {"nombre": m.nombre, "colores": dict(m.datos.get("colores") or {})}}


def load_tokens(plan: EditPlan) -> dict:
    tk = {**brand_tokens(cliente_de(plan.slug)), "style_profile": plan.style_profile or "firma",
          "lockup_full_bottom": 1460}   # en cara completa el titular héroe va sobre el cuello/camiseta (bajo la UI real: 420 px)
    if MOTION_TOKENS.exists():
        try:
            tk["motion"] = yaml.safe_load(MOTION_TOKENS.read_text())
        except Exception:
            pass
    return tk | (plan.tokens or {})


def render_spec(tl: Timeline, mi: MediaIndex, plan: EditPlan, profile: dict) -> dict:
    faces = []
    for s in tl.aroll:
        for f in mi.faces.get(s.src, []):
            if s.src_in <= f.t <= s.src_out:
                faces.append([round(s.prog_in + f.t - s.src_in, 3), f.x, f.y, f.w, f.h])
    fonts = [
        {"family": "Montserrat", "file": str(FONTS / "Montserrat[wght].ttf"), "weight": "100 900", "style": "normal"},
        {"family": "Inter", "file": str(FONTS / "Inter[opsz,wght].ttf"), "weight": "100 900", "style": "normal"},
        {"family": "JetBrains Mono", "file": str(FONTS / "JetBrainsMono[wght].ttf"), "weight": "100 800", "style": "normal"},
    ]
    tokens = load_tokens(plan)
    tokens["safe"] = profile.get("safe_zone", {})
    if (profile.get("safe_zone") or {}).get("right_from_y") is not None:
        tokens["safe_right_from_y"] = profile["safe_zone"]["right_from_y"]
    if "lockup_full_bottom" not in (plan.tokens or {}) and (profile.get("safe_zone") or {}).get("bottom") is not None:
        # el titular héroe en cara completa se apoya en el límite inferior de la zona segura del perfil
        tokens["lockup_full_bottom"] = int(profile["canvas"]["height"]) - int(profile["safe_zone"]["bottom"])
    tokens["caption_y"] = profile["captions"]["rail_y"]
    # 20-oct-2026: un solo raíl en cara completa y gráficos a pantalla completa (perfil `captions.rail_*`; el plan puede
    # traer su propio `tokens.caption_rail`)
    cap = profile.get("captions") or {}
    rail = {k: cap[f"rail_{k}"] for k in ("shared", "y_full", "chin_gap", "max_px") if cap.get(f"rail_{k}") is not None}
    if rail:
        tokens.setdefault("caption_rail", rail)
    items = []
    for it in tl.items:
        d = {"id": it.id, "track": it.track, "t0": it.t0, "t1": it.t1, "component": it.component,
             "props": {k: v for k, v in it.props.items() if k != "_media"}, "cues": it.cues, "z": it.z}
        if "_media" in it.props:
            # `props.media_start`: un mismo clip puede partirse en subplanos que arrancan en distintos instantes
            ms = float(it.props.get("media_start", 0.0) or 0.0)
            # con sus medidas reales: sin ellas el runtime las leía del vídeo, que en algunos workers de la captura aún no
            # tenía metadatos (16:9 por defecto) → la caja del panel cambiaba de tamaño fotograma a fotograma
            d["media"] = [{k: m[k] for k in ("id", "kind", "src", "path", "asset", "width", "height") if m.get(k) is not None}
                          | {"media_start": ms} for m in it.props["_media"]]
            _line_media(it, d, tl.fps)
            _freeze_at_focus(tl, it, d, ms)
        items.append(d)
    return {"fps": tl.fps, "width": tl.width, "height": tl.height, "duration": tl.duration, "tokens": tokens,
            "fonts": fonts, "aroll": {"src": "media/program.mp4", "path": str(version_dir(tl.slug, tl.version) / "program.mp4"),
                                      "duration": tl.duration, "faces": faces},
            "items": items}


def _line_media(it: TimelineItem, d: dict, fps: int = 30) -> None:
    """`props.lines[].media` (title.lockup_grid: miniatura real por línea). 21-oct-2026 (un vídeo de prueba, d000): cada
    VÍDEO de una línea lleva su propia entrada en `d["media"]`: `media_start` y `loop` (`media_loop`) de SU línea y `start`
    = la cue de la línea (absoluta; sin cue, el t0 del item). html.py la pasa al <video> (data-start, data-duration =
    t1 − start, `loop`): HyperFrames reproduce el vídeo leyendo el HTML estático, no el componente. Antes todos los medios
    del item compartían `props.media_start` y arrancaban en t0, sin bucle. Las imágenes no cambian."""
    lines = it.props.get("lines")
    if not isinstance(lines, list) or not d.get("media"):
        return
    for ln in lines:
        if not isinstance(ln, dict) or not ln.get("media"):
            continue
        key = str(ln["media"])
        for m in d["media"]:
            if m.get("kind") != "video":
                continue
            if m.get("asset") != key and m.get("id") != key and not str(m.get("id", "")).startswith(f"m_{key}__"):
                continue
            cue = (it.cues or {}).get(str(ln.get("cue"))) if ln.get("cue") is not None else None
            start = float(cue) if isinstance(cue, (int, float)) else it.t0
            m["start"] = round(min(max(it.t0, start), it.t1 - 1 / fps), 4)
            if ln.get("media_start") is not None:
                m["media_start"] = max(0.0, float(ln["media_start"]))
            if ln.get("media_loop"):
                m["loop"] = True


def freeze_video(src: Path, at: float, hold: float, out_dir: Path, fps: int = 30) -> Path:
    """Copia de `src` idéntica hasta `at` (s de la fuente) y congelada en ese fotograma `hold` s más (CFR a `fps`).
    Caché por contenido en `out_dir` (misma fuente, instante y duración → mismo fichero)."""
    import hashlib
    st = src.stat()
    key = hashlib.sha1(f"{src.resolve()}|{st.st_size}|{st.st_mtime_ns}|{at:.4f}|{hold:.3f}|{fps}".encode()).hexdigest()[:12]
    out = out_dir / f"{src.stem}__freeze_{key}.mp4"
    if out.exists() and out.stat().st_size > 0:
        return out
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp.mp4")
    # el fotograma que se ve en `at` (rejilla de `fps` desde 0) es el último que entra; luego se repite `hold` s
    vf = f"fps={fps},trim=end={at + 0.5 / fps:.4f},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={hold:.3f}"
    subprocess.run([sistema.requiere("ffmpeg"), "-v", "error", "-y", "-i", str(src), "-an", "-vf", vf, "-c:v", "libx264",
                    "-preset", "medium", "-crf", "12", "-g", str(fps), "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    str(tmp)], check=True)
    tmp.replace(out)
    return out


def _freeze_at_focus(tl: Timeline, it: TimelineItem, d: dict, ms: float) -> None:
    """`props.freeze_at_focus` (media.ui_focus, 20-oct-2026; crítica visual 2 de un vídeo de prueba: la fuente de d032 hacía
    scroll en 46,5–46,9 y el anillo acababa enmarcando otra capa): el vídeo se congela en el fotograma de la cue `focus`.
    HyperFrames no sabe pausar un <video>, así que se monta una copia congelada y se usa en su lugar (mismo `media_start`)."""
    focus = (it.cues or {}).get("focus")
    if not it.props.get("freeze_at_focus") or focus is None or not d.get("media") or d["media"][0].get("kind") != "video":
        return
    m0 = d["media"][0]
    src = Path(m0.get("path") or "")
    if not src.is_absolute():
        src = RAIZ / src
    at = ms + max(0.0, float(focus) - it.t0)
    try:
        out = freeze_video(src, at, max(0.0, it.t1 - float(focus)) + 1.0, run_dir(tl.slug) / "media" / "frozen", tl.fps)
    except Exception as e:  # noqa: BLE001 — sin ffmpeg o sin fuente: el vídeo sigue sin congelar (y se dice)
        print(f"[compile] freeze_at_focus {it.id}: no se pudo congelar ({e}); sigue el vídeo original")
        return
    m0.update(path=str(out), src=f"media/{out.name}")
    d["props"]["_frozen_at"] = round(at, 3)


def build_program(tl: Timeline, mi: MediaIndex, vd: Path, variant: str = "") -> Path:
    """Concatena los tramos de A-roll (intermedios CFR 30 fps) en program.mp4, exacto al fotograma.

    `variant="split"`: program_split.mp4 con la versión 50/50 de la toma (fuente `<src>_split`, misma toma y
    mismos tiempos); los tramos sin versión 50/50 (p. ej. el outro) usan la fuente normal."""
    out = vd / ("program_split.mp4" if variant == "split" else "program.mp4")
    srcs = {s.id: s.mezzanine for s in mi.sources}
    if variant == "split":
        srcs = {sid: srcs.get(f"{sid}_split", path) for sid, path in srcs.items()}
    inputs, filters = [], []
    order = list(dict.fromkeys(s.src for s in tl.aroll))
    for sid in order:
        inputs += ["-i", srcs[sid]]
    for k, s in enumerate(tl.aroll):
        ii = order.index(s.src)
        f0, f1 = round(s.src_in * tl.fps), round(s.src_out * tl.fps)
        hold = f",tpad=stop_mode=clone:stop_duration={s.hold_after:.4f}" if s.hold_after > 0 else ""
        filters.append(f"[{ii}:v]trim=start_frame={f0}:end_frame={f1},setpts=PTS-STARTPTS{hold}[v{k}]")
    filters.append("".join(f"[v{k}]" for k in range(len(tl.aroll))) + f"concat=n={len(tl.aroll)}:v=1:a=0[out]")
    subprocess.run([sistema.requiere("ffmpeg"), "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filters),
                    "-map", "[out]", "-r", str(tl.fps), *sistema.codec_video("intermedio", tl.fps), str(out)], check=True)
    return out
