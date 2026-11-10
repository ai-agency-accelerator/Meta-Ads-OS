"""Puertas de audio: sonoridad integrada, pico verdadero, relación voz/fondo (stems) y silencios inesperados.

- Sonoridad y pico verdadero se miden SOBRE EL MP4 FINAL (el AAC añade sobrepico).
- Los silencios se buscan en la VOZ (stem), nunca en la mezcla con música (`silencedetect` no ve nada).
- La relación voz/fondo usa los stems de `versions/<vid>/audio/` con ponderación K (pyloudnorm), integrada, por
  ventana de 3 s y por palabra.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from . import media
from .context import QAContext, tc

SR = 48000


def _stems(ctx: QAContext) -> dict[str, list[Path]]:
    d = ctx.vdir / "audio"
    out: dict[str, list[Path]] = {"voice": [], "music": [], "sfx": []}
    if not d.is_dir():
        return out
    for p in sorted(d.rglob("*")):                      # `mix.render` deja los stems en audio/stems/
        if not p.is_file() or p.suffix.lower() not in (".wav", ".flac", ".aif", ".aiff", ".mp3", ".m4a"):
            continue
        n = p.stem.lower()
        if n.startswith(("mix", "master", "final")):
            continue
        if "voice" in n or "voz" in n or "dialog" in n:
            out["voice"].append(p)
        elif "music" in n or "musica" in n or "música" in n or "bed" in n:
            out["music"].append(p)
        elif "sfx" in n or "fx" in n:
            out["sfx"].append(p)
    return out


def _load_sum(paths: list[Path], n: int) -> np.ndarray:
    acc = np.zeros(n)
    for p in paths:
        x = media.decode_audio(p, SR)[:n]
        acc[: len(x)] += x
    return acc


def check_loudness(ctx: QAContext) -> None:
    a = ctx.cfg["audio"]
    if not ctx.probe.get("audio"):
        ctx.add("audio.missing", "block", "El render no tiene pista de audio.", blame=ctx.blame(0, ctx.duration, audio_kinds=["voice"]))
        return
    r = media.ebur128(ctx.render)
    ctx.metrics.update({"lufs_i": r["I"], "lra": r["LRA"], "true_peak_dbtp": r["TP"]})
    ctx._momentary = r["momentary"]  # type: ignore[attr-defined]
    I, TP = r["I"], r["TP"]
    mix_dec = ctx.blame(0, ctx.duration, tracks=[], audio_kinds=["music"])
    if I is not None and abs(I - a["lufs_target"]) > a["lufs_tol"]:
        ctx.add("audio.loudness", "block",
                f"Sonoridad integrada {I:.1f} LUFS fuera de {a['lufs_target']:.0f} ± {a['lufs_tol']:.0f} LUFS.",
                0, ctx.duration, {"lufs_i": I, "umbral": [a["lufs_target"] - a["lufs_tol"], a["lufs_target"] + a["lufs_tol"]],
                                  "fuente": "ebur128 sobre el MP4 final"},
                mix_dec, [{"op": "gain", "db": round(a["lufs_target"] - I, 1), "then": "limiter(-1.5 dBTP)+remux"}])
    if TP is not None and TP > a["tp_max_dbtp"]:
        over = [(round(t - 0.1, 2), round(p, 2)) for t, p in r.get("ftpk", []) if p > a["tp_max_dbtp"]]
        t0, t1 = (over[0][0], over[-1][0] + 0.1) if over else (0, ctx.duration)
        ctx.add("audio.true_peak", "block",
                f"Pico verdadero {TP:.1f} dBTP en el MP4 final (máximo {a['tp_max_dbtp']:.1f}); {len(over)} bloque(s) de "
                f"100 ms lo superan. El limitador va antes del AAC y el códec añade sobrepico: limitar a −1,5 dBTP y "
                f"volver a medir sobre el MP4.",
                t0, t1, {"true_peak_dbtp": TP, "umbral_dbtp": a["tp_max_dbtp"], "bloques_sobre_umbral": over[:20],
                         "fuente": "ebur128 peak=true (AES TD1008)"},
                mix_dec, [{"op": "limiter", "ceiling_dbtp": -1.5}, {"op": "remux"}])


def _rms_db(x: np.ndarray, hop: int) -> np.ndarray:
    n = len(x) // hop
    if n == 0:
        return np.array([])
    fr = x[: n * hop].reshape(n, hop)
    return 10 * np.log10(np.mean(fr ** 2, axis=1) + 1e-12)


def _runs(mask: np.ndarray, hop_s: float, min_s: float) -> list[tuple[float, float]]:
    out, start = [], None
    for i, m in enumerate(np.append(mask, False)):
        if m and start is None:
            start = i
        elif not m and start is not None:
            if (i - start) * hop_s >= min_s:
                out.append((start * hop_s, i * hop_s))
            start = None
    return out


def check_silences(ctx: QAContext, stems: dict[str, list[Path]], voice: np.ndarray | None) -> None:
    a = ctx.cfg["audio"]
    hop = int(0.01 * SR)
    words = ctx.words_sorted()
    cont = ctx.contention_spans()
    # 1) silencio total en la mezcla (voz y música por debajo de −60 dBFS) fuera de transiciones
    mix = media.decode_audio(ctx.render, SR)
    db = _rms_db(mix, hop)
    total = _runs(db < a["total_silence_db"], 0.01, a["total_silence_min_s"])
    trans = [(i.t0 - 0.1, i.t1 + 0.1) for i in ctx.items(["transition"])]
    for s, e in total:
        if s < 0.05 and e - s < 0.5 or e > ctx.duration - 0.05:   # arranque/cola de códec
            continue
        if any(ts <= s and e <= te for ts, te in trans):
            continue
        ctx.add("audio.dropout", "block", f"Silencio total de {e - s:.2f} s en la mezcla ({tc(s)}–{tc(e)}) que el plan no declara.",
                s, e, {"rms_dbfs_max": float(db[int(s * 100):int(e * 100)].max()), "umbral_dbfs": a["total_silence_db"]},
                ctx.blame(s, e, audio_kinds=["voice", "music"]), [{"op": "replan", "reason": "hueco de audio"}])
    # 2) voz que falta donde la timeline dice que se habla (stem de voz)
    if voice is not None and len(voice):
        vdb = _rms_db(voice, hop)
        sil = _runs(vdb < a["voice_silence_db"], 0.01, a["voice_silence_min_s"])
        missing = []
        for s, e in sil:
            inside = [w for w in words if w[1] >= s - 0.02 and w[2] <= e + 0.02 and (w[2] - w[1]) >= 0.12]
            if inside:
                missing.append((s, e, [w[0] for w in inside]))
        for s, e, ws in missing:
            ctx.add("audio.voice_missing", "block",
                    f"No se oye la voz en {tc(s)}–{tc(e)} aunque la timeline coloca ahí {len(ws)} palabra(s).",
                    s, e, {"palabras": ws[:12], "voz_rms_umbral_dbfs": a["voice_silence_db"]},
                    ctx.blame(s, e, tracks=["caption"], audio_kinds=["voice"]),
                    [{"op": "check_aroll_sync"}])
        ctx.metrics["voice_silences_s"] = round(sum(e - s for s, e in sil), 2)
    # 3) huecos entre palabras más largos de lo normal y sin justificación (plan)
    gaps = []
    for (w0, s0, e0), (w1, s1, e1) in zip(words, words[1:]):
        g = s1 - e0
        if g >= a["pause_warn_s"] and not any(cs <= e0 + 0.2 and s1 - 0.2 <= ce for cs, ce in cont):
            gaps.append((e0, s1, w0, w1))
    for e0, s1, w0, w1 in gaps:
        ctx.add("audio.long_pause", "warn",
                f"Pausa de {s1 - e0:.2f} s sin justificar entre {w0} y {w1} ({tc(e0)}–{tc(s1)}).",
                e0, s1, {"pausa_s": round(s1 - e0, 2), "umbral_s": a["pause_warn_s"], "fuente": "word_times"},
                ctx.blame(e0, s1, tracks=["layout", "camera"]),
                [{"op": "set_pause", "class": "dramatica|fin_frase", "max_s": 0.6}])


def check_vmr(ctx: QAContext, stems: dict[str, list[Path]]) -> np.ndarray | None:
    """Relación voz/fondo con stems y ponderación K. Devuelve la voz (para los silencios)."""
    a = ctx.cfg["audio"]
    if not stems["voice"]:
        ctx.notes.append("Sin stems en audio/: la relación voz/música no se mide (haría falta Demucs).")
        return None
    import pyloudnorm as pyln

    n = int((ctx.duration or ctx.probe.get("duration", 0)) * SR) + SR
    voice = _load_sum(stems["voice"], n)
    back = _load_sum(stems["music"] + stems["sfx"], n)
    music = _load_sum(stems["music"], n)
    if not (stems["music"] or stems["sfx"]):
        ctx.notes.append("Stems sin música ni SFX: relación voz/fondo no aplicable.")
        return voice
    meter = pyln.Meter(SR)

    def integ(x: np.ndarray) -> float:
        try:
            v = meter.integrated_loudness(x)
            return float(v) if np.isfinite(v) else -120.0
        except Exception:
            return -120.0
    lrd = integ(voice) - integ(back)
    ctx.metrics["lrd_lu"] = round(lrd, 1)
    ctx.metrics["voice_lufs_stem"] = round(integ(voice), 1)
    ctx.metrics["background_lufs_stem"] = round(integ(back), 1)

    def kf(x: np.ndarray) -> np.ndarray:
        y = x.copy()
        for f in meter._filters.values():   # filtros K de pyloudnorm (shelf + high-pass)
            y = f.apply_filter(y)
        return y
    vk, bk, mk = kf(voice), kf(back), kf(music)
    ldb = lambda x: 10 * np.log10(np.mean(x ** 2) + 1e-12)  # noqa: E731
    music_dec = ctx.blame(0, ctx.duration, tracks=[], audio_kinds=["music"])
    if lrd < a["lrd_warn_lu"]:
        sev = "block" if lrd < a["lrd_block_lu"] else "warn"
        ctx.add("audio.vmr_integrated", sev, f"La voz queda solo {lrd:.1f} LU por encima del fondo (mínimo {a['lrd_warn_lu']:.0f} LU).",
                0, ctx.duration, {"lrd_lu": round(lrd, 1), "umbral_warn": a["lrd_warn_lu"], "umbral_block": a["lrd_block_lu"],
                                  "fuente": "stems, ponderación K (Torcoli 2019)"},
                music_dec, [{"op": "gain", "track": "music", "db": round(lrd - a["lrd_warn_lu"] - 1, 1)}])
    # ventanas de 3 s con voz
    words = ctx.words_sorted()
    low_w = []
    for k in np.arange(0, max(0.0, ctx.duration - 1.0), 3.0):
        s, e = int(k * SR), int(min(ctx.duration, k + 3) * SR)
        if not any(k <= w[1] < k + 3 for w in words):
            continue
        d = ldb(vk[s:e]) - ldb(bk[s:e])
        if d < a["win3_warn_db"]:
            low_w.append((float(k), float(min(ctx.duration, k + 3)), round(float(d), 1)))
    ctx.metrics["vmr_win3_min_db"] = min((x[2] for x in low_w), default=None)
    # por palabra: se agrupan las palabras contiguas con VMR bajo en un único issue
    wt = ctx.word_text()
    # por palabra, solo en los tramos de 10 ms con voz activa (los tiempos del ASR van en rejilla de 80 ms y estiran
    # los finales: medir la palabra entera mezclaría la pausa y daría falsos «la música tapa la voz»)
    hop = int(0.01 * SR)
    nf = min(len(vk), len(bk)) // hop
    ve = np.mean(vk[: nf * hop].reshape(nf, hop) ** 2, axis=1)
    be = np.mean(bk[: nf * hop].reshape(nf, hop) ** 2, axis=1)
    me = np.mean(mk[: nf * hop].reshape(nf, hop) ** 2, axis=1)
    # la máscara de una palabra se mide en 1–4 kHz (consonantes, lo que oye el móvil). En banda
    # completa los graves de la voz tapaban 9 palabras con fondo a < 6 dB en esa banda
    from scipy import signal as _sg
    bp = _sg.butter(4, [1000, 4000], "bandpass", fs=SR, output="sos")
    def _band_e(x):
        y = _sg.sosfiltfilt(bp, x[: nf * hop])
        return np.mean(y.reshape(nf, hop) ** 2, axis=1)
    vbe, bbe, mbe = _band_e(voice), _band_e(back), _band_e(music)
    floor = 10 ** (-50 / 10)
    rows = []
    for wid, s, e in words:
        f0, f1 = int(s * 100), int(max(e, s + 0.12) * 100)
        if f1 <= f0 or f1 > nf:
            continue
        seg = ve[f0:f1]
        act = (seg > seg.max() * 10 ** (-15 / 10)) & (seg > floor)
        if act.sum() < 3:
            continue   # sin voz medible dentro de la palabra: es un problema de tiempos, no de mezcla
        d_full = 10 * np.log10(seg[act].sum() / (be[f0:f1][act].sum() + 1e-12))
        d = 10 * np.log10(vbe[f0:f1][act].sum() / (bbe[f0:f1][act].sum() + 1e-12))      # 1–4 kHz
        dm = 10 * np.log10(vbe[f0:f1][act].sum() / (mbe[f0:f1][act].sum() + 1e-12))
        lvl = 10 * np.log10(seg[act].mean() + 1e-12)
        rows.append((wid, s, e, float(d), float(dm), float(lvl), float(d_full)))
    if rows:
        # palabra con la voz > 15 dB por debajo de la mediana: el ASR la sitúa mal (no es la mezcla) → fuera
        med = float(np.median([r[5] for r in rows]))
        rows = [r for r in rows if r[5] >= med - 15]
    if rows:
        arr = np.array([r[3] for r in rows])
        ctx.metrics["vmr_word_p5_db"] = round(float(np.percentile(arr, 5)), 1)          # banda de 1–4 kHz
        ctx.metrics["vmr_word_p50_db"] = round(float(np.median(arr)), 1)
        ctx.metrics["words_vmr_lt_6db"] = int((arr < a["word_warn_db"]).sum())
        full = np.array([r[6] for r in rows])
        ctx.metrics["vmr_word_fullband"] = {"p5_db": round(float(np.percentile(full, 5)), 1),
                                            "lt_6db": int((full < a["word_warn_db"]).sum())}
        ctx.metrics["vmr_word_banda"] = "1–4 kHz"
    bad = [r for r in rows if r[3] < a["word_warn_db"]]
    groups: list[list[tuple]] = []
    for r in bad:
        if groups and r[1] - groups[-1][-1][2] < 0.6:
            groups[-1].append(r)
        else:
            groups.append([r])
    for g in groups:
        s, e = g[0][1], g[-1][2]
        worst = min(x[3] for x in g)
        sfx_guilty = any(x[4] - x[3] > 3 for x in g)   # contra la música sola la palabra se oye: lo tapan los SFX
        kinds = ["sfx"] if sfx_guilty else ["music", "sfx"]
        txt = " ".join(wt.get(x[0], x[0]) for x in g)
        ctx.add("audio.vmr_word", "warn",
                f"{'Los SFX tapan' if sfx_guilty else 'El fondo tapa'} la voz en «{txt}» ({tc(s)}–{tc(e)}): "
                f"voz − fondo = {worst:.1f} dB en 1–4 kHz (mínimo {a['word_warn_db']:.0f} dB).",
                s, e, {"vmr_db": {x[0]: round(x[3], 1) for x in g}, "vmr_vs_music_only_db": {x[0]: round(x[4], 1) for x in g},
                       "umbral_warn_db": a["word_warn_db"], "nota": "sin prueba ASR voz/mezcla no se bloquea"},
                ctx.blame(s - 0.3, e + 0.3, tracks=[], audio_kinds=kinds),
                [{"op": "duck", "track": "sfx" if sfx_guilty else "music", "gain_db": -8, "t0": round(s - 0.3, 2), "t1": round(e + 0.3, 2)},
                 {"op": "shift_events", "track": "sfx", "into": "word_gaps"}] if sfx_guilty else
                [{"op": "duck", "track": "music", "gain_db": -6, "t0": round(s - 0.3, 2), "t1": round(e + 0.3, 2)}])
    for s, e, d in low_w:
        if any(g[0][1] < e and g[-1][2] > s for g in groups):
            continue   # ya cubierto por un issue por palabra
        ctx.add("audio.vmr_window", "info", f"Ventana {tc(s)}–{tc(e)} con voz − fondo = {d:.1f} dB (< {a['win3_warn_db']:.0f} dB).",
                s, e, {"vmr_db": d, "umbral_db": a["win3_warn_db"]}, ctx.blame(s, e, tracks=[], audio_kinds=["music", "sfx"]))
    return voice


def check_sfx_visual_sync(ctx: QAContext, max_ms: float = 40.0) -> None:
    """`sfx.visual_sync`: cada SFX debe sonar a ≤ 40 ms del evento VISUAL real de su item (`events.json`, que
    `cutkit.audio.events` lee de `window.__ckEvents`). Se compara el instante de sincronía del SFX (`t0` de su
    `AudioItem`) con el evento más cercano del mismo item (por `decision_ids`); sin evento, se informa.
    Si `sfx_plan.json` trae el PRIMER FOTOGRAMA VISIBLE del evento (`event_ref.t_visible` = arranque del tween +
    `retardo_ms` de la paleta), se mide contra él y no contra el arranque del tween (un trazo que empieza
    a verse 90 ms después de arrancar sonaba antes que la tinta)."""
    import json
    p = ctx.vdir / "events.json"
    sfx = [a for a in ctx.timeline.audio if a.kind == "sfx"]
    if not sfx:
        return
    if not p.exists():
        ctx.notes.append("Sin events.json: la sincronía SFX ↔ evento visual no se mide (cutkit.audio.events).")
        return
    try:
        evs = [e for e in json.loads(p.read_text()).get("events", [])
               if not str(e.get("kind", "")).startswith(("layout.", "lockup.", "camera."))]
    except Exception:                                     # noqa: BLE001
        ctx.notes.append("events.json ilegible: sincronía SFX no medida.")
        return
    moved, target, on_cue, layered = set(), {}, set(), set()
    sp = ctx.vdir / "sfx_plan.json"
    if sp.exists():
        try:
            chosen = json.loads(sp.read_text()).get("chosen", [])
            moved = {c["id"] for c in chosen if c.get("moved_for_word")}
            target = {c["id"]: c["event_ref"] for c in chosen if c.get("event_ref")}   # evento al que se alineó
            on_cue = {c["id"] for c in chosen if c.get("sync_src") == "cue" and not c.get("event_ref")}
            # capas y texturas de un gesto («sfx_07.c1», «.t2») van desplazadas a propósito (el aire de
            # `juntar` −0,20 s, el reloj en la palabra siguiente): se mide su golpe principal y cada golpe de escalera
            layered = {c["id"] for c in chosen if "." in str(c["id"]) and not c.get("escalera")}
        except Exception:                                 # noqa: BLE001
            moved = set()
    items_by_dec: dict[str, set[str]] = {}
    for it in ctx.timeline.items:
        for did in it.decision_ids:
            items_by_dec.setdefault(did, set()).add(it.id)
    deltas, bad, unmatched = [], [], []
    for a in sfx:
        if a.id in layered:
            continue
        if a.id in on_cue:                                # alineado a su cue (el componente no emite ese evento)
            unmatched.append(a.id)
            continue
        ids = set().union(*(items_by_dec.get(d, set()) for d in a.decision_ids)) if a.decision_ids else set()
        cand = [e for e in evs if e.get("item") in ids and abs(float(e["t"]) - a.t0) <= 1.0]
        if a.id in target and abs(float(target[a.id]["t"]) - a.t0) <= 1.0:
            cand = [target[a.id]]
        if not cand:
            unmatched.append(a.id)
            continue
        e = min(cand, key=lambda e: abs(float(e["t"]) - a.t0))
        dms = (a.t0 - float(e.get("t_visible", e["t"]))) * 1000
        deltas.append(dms)
        if abs(dms) > max_ms and a.id not in moved:
            bad.append((a, e, dms))
    ctx.metrics["sfx_visual_sync"] = {"medidos": len(deltas), "sin_evento": unmatched,
                                      "max_abs_ms": round(max((abs(x) for x in deltas), default=0.0), 1)}
    for a, e, dms in bad:
        ctx.add("sfx.visual_sync", "block",
                f"El SFX {a.id} suena {dms:+.0f} ms respecto a su evento visual «{e.get('kind')}» ({tc(float(e['t']))}"
                + (", primer fotograma visible" if e.get("t_visible") is not None else "") + "); "
                f"máximo ±{max_ms:.0f} ms.",
                a.t0, a.t0 + 0.1, {"sfx_t0": round(a.t0, 3), "evento": e, "delta_ms": round(dms, 1), "umbral_ms": max_ms},
                ctx.blame(a.t0 - 0.1, a.t0 + 0.1, tracks=[], audio_kinds=["sfx"]),
                [{"op": "move_sfx", "id": a.id, "t0": round(float(e.get("t_visible", e["t"])) - 0.02, 3)}])
    if unmatched:
        ctx.add("sfx.visual_sync_unmatched", "info",
                f"{len(unmatched)} SFX sin evento visual en su item (alineados a cues de palabra): {', '.join(unmatched[:12])}.",
                None, None, {"sfx": unmatched})


PX_W, PX_H = 135, 240                                     # fotogramas en miniatura para la sincronía por píxeles


def _px_frames(ctx: QAContext) -> tuple[np.ndarray, float] | None:
    """El render entero a 135×240 en gris y a su fps (una pasada de ffmpeg; ~130 MB para 2 min 15 s). En caché."""
    import subprocess
    if getattr(ctx, "_px", None) is not None:
        return ctx._px  # type: ignore[attr-defined]
    src = ctx.render if ctx.render and Path(ctx.render).exists() else None
    if src is None:
        return None
    fps = float((ctx.probe or {}).get("fps") or media.probe(src).get("fps") or 30.0)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-an", "-vf", f"scale={PX_W}:{PX_H}:flags=area,format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8)
    fr = fr[: fr.size // (PX_W * PX_H) * PX_W * PX_H].reshape(-1, PX_H, PX_W)
    ctx._px = (fr, fps)  # type: ignore[attr-defined]
    return ctx._px  # type: ignore[attr-defined]


def check_sfx_visual_sync_px(ctx: QAContext, max_ms: float = 40.0, win_s: float = 0.1) -> list[str]:
    """`sfx.visual_sync` contra los PÍXELES: `t_visible` es lo que el componente dice;
    esto mira lo que se ve. Para cada golpe de SFX (el principal de cada gesto y cada golpe de escalera; no las capas
    ni las texturas, que van desplazadas a propósito) se busca, a ±`win_s` (3 f) de su `t_visible`, el fotograma en
    que empieza a cambiar la imagen en la zona de su item: cajas de texto del item en el DOM si las hay; si no, el
    panel del layout (mitad de arriba en un split, pantalla entera si no), sin los subtítulos. «Empieza a cambiar» =
    el número de píxeles que cambian > 10 niveles pasa de 2 × su mediana + 3. Salta (warn) si el SFX queda a más de
    ±`max_ms` de ese fotograma; sin cambio en la ventana, se informa. Necesita el render: se llama tras
    `boxes.collect`. Sin cajas del DOM, la zona es el panel entero y otra animación cercana (la salida del gráfico
    anterior) puede adelantar el cambio: por eso avisa, no bloquea."""
    import json
    from .config import gate_severity  # noqa: F401
    sp = ctx.vdir / "sfx_plan.json"
    if not sp.exists():
        return []
    try:
        chosen = {c["id"]: c for c in json.loads(sp.read_text()).get("chosen", [])}
    except Exception:                                     # noqa: BLE001
        return []
    got = _px_frames(ctx)
    if got is None:
        ctx.notes.append("Sin render: la sincronía SFX ↔ píxeles no se mide.")
        return []
    fr, fps = got
    sx, sy = PX_W / 1080.0, PX_H / 1920.0
    caps = [b for b in ctx.boxes if (b.role or "") == "caption"]
    rows, bad, nomatch = [], [], []
    for a in sorted((a for a in ctx.timeline.audio if a.kind == "sfx"), key=lambda a: a.t0):
        c = chosen.get(a.id)
        if c is None or (("." in a.id) and not c.get("escalera")):
            continue                                       # capas y texturas: desplazadas a propósito
        ref = c.get("event_ref") or {}
        tv = ref.get("t_visible", ref.get("t"))
        if tv is None:
            continue
        item = c.get("item_id")
        k0, k1 = max(1, int((float(tv) - win_s) * fps)), min(len(fr) - 1, int((float(tv) + win_s) * fps) + 1)
        if k1 - k0 < 3:
            continue
        # zona: cajas del item en el DOM (±1 s) o el panel de su layout
        bx = [b for b in ctx.boxes if b.item == item and abs(b.t - float(tv)) <= 1.0]
        mask = np.zeros((PX_H, PX_W), bool)
        if bx:
            for b in bx:
                mask[max(0, int(b.y0 * sy) - 2): int(b.y1 * sy) + 3, max(0, int(b.x0 * sx) - 2): int(b.x1 * sx) + 3] = True
        else:
            lay = next((l for l in ctx.active(float(tv), tracks=["layout"])), None)
            split = lay is not None and "split" in str(lay.component or "")
            mask[: int((900 if split else 1920) * sy), :] = True
        for b in caps:                                     # sin los subtítulos (cambian en cada palabra)
            if abs(b.t - float(tv)) <= 0.6:
                mask[max(0, int(b.y0 * sy) - 2): int(b.y1 * sy) + 3, max(0, int(b.x0 * sx) - 2): int(b.x1 * sx) + 3] = False
        if mask.sum() < 20:
            continue
        seg = fr[k0 - 1: k1 + 1].astype(np.int16)
        # píxeles que cambian entre fotogramas (> 10 niveles): una raya fina de rotulador también cuenta
        cnt = np.array([int((np.abs(seg[i] - seg[i - 1])[mask] > 10).sum()) for i in range(1, len(seg))])
        if not len(cnt):
            continue
        thr = max(4.0, 2 * float(np.median(cnt)) + 3)
        edges = [i for i in range(len(cnt)) if cnt[i] >= thr and (i == 0 or cnt[i - 1] < thr)]
        if not edges:
            nomatch.append(a.id)
            continue
        ts = [(k0 + i) / fps for i in edges]               # fotograma (k0 + i) es el primero distinto del anterior
        t_px = min(ts, key=lambda t: abs(t - float(tv)))
        dms = (a.t0 - t_px) * 1000
        rows.append(dms)
        if abs(dms) > max_ms + 1e-3:
            bad.append((a, t_px, dms, item))
    ctx.metrics["sfx_visual_sync_px"] = {"medidos": len(rows), "sin_cambio_visible": nomatch,
                                         "max_abs_ms": round(max((abs(x) for x in rows), default=0.0), 1),
                                         "fuera_de_tolerancia": len(bad)}
    for a, t_px, dms, item in bad:
        ctx.add("sfx.visual_sync", "warn",
                f"Por píxeles, el SFX {a.id} suena {dms:+.0f} ms respecto al fotograma en que cambia su item "
                f"({item}, {tc(t_px)}); máximo ±{max_ms:.0f} ms.",
                a.t0, a.t0 + 0.1, {"sfx_t0": round(a.t0, 3), "t_pixeles": round(t_px, 3), "delta_ms": round(dms, 1),
                                   "fuente": "píxeles (diferencia entre fotogramas en la zona del item)"},
                ctx.blame(a.t0 - 0.1, a.t0 + 0.1, tracks=[], audio_kinds=["sfx"]),
                [{"op": "move_sfx", "id": a.id, "t0": round(t_px - 0.02, 3)}])
    return ["sfx.visual_sync(px)"]


def sfx_gestures(audio) -> list[list]:
    """SFX agrupados en GESTOS: un gesto es un sonido con sus capas y su escalera. Con los ids de
    `sfxplan` («sfx_07», capas «sfx_07.c1», golpes de escalera «sfx_07.e2») por el prefijo, con el principal primero;
    con ids antiguos, los AudioItem con el mismo t0 (±5 ms)."""
    sfx = sorted((a for a in audio if a.kind == "sfx"), key=lambda a: a.t0)
    if any("." in a.id for a in sfx):
        by: dict[str, list] = {}
        for a in sfx:
            by.setdefault(a.id.split(".")[0], []).append(a)
        groups = [sorted(g, key=lambda a: ("." in a.id, a.t0)) for g in by.values()]
        return sorted(groups, key=lambda g: g[0].t0)
    out: list[list] = []
    for a in sfx:
        if out and abs(a.t0 - out[-1][0].t0) < 0.005:
            out[-1].append(a)
        else:
            out.append([a])
    return out


def _sfx_plan(ctx: QAContext) -> list[dict]:
    import json
    p = ctx.vdir / "sfx_plan.json"
    try:
        return json.loads(p.read_text()).get("chosen", []) if p.exists() else []
    except Exception:                                     # noqa: BLE001
        return []


def _firma_ids(ctx: QAContext) -> set[str]:
    """AudioItems de la firma DECLARADA (paleta con `firma: true` o grupo `firma:` en sfx_plan.json): su repetición
    es la firma, no un SFX repetido."""
    try:
        from ..audio.sfxplan import _anim_map
        firmas = {k for k, v in (_anim_map().get("paletas") or {}).items() if v.get("firma")}
    except Exception:                                     # noqa: BLE001
        firmas = set()
    return {c["id"] for c in _sfx_plan(ctx) if c.get("firma") or c.get("palette") in firmas
            or str(c.get("group") or "").startswith("firma:")}


def check_sfx_density(ctx: QAContext, th: dict) -> list[str]:
    """`sfx.density`, `sfx.repeat` y `sfx.cluster` contando GESTOS (un sonido con sus capas = 1; antes
    cada fichero, así que la capa de brillo de la firma contaba como otro SFX). `sfx.repeat` cuenta el fichero
    PRINCIPAL de cada gesto (las copias procesadas cuentan como su original; el click de papel bajo un sello es timbre,
    no otra muestra) y no cuenta la firma declarada."""
    from .config import gate_severity
    dur = ctx.duration or 1.0
    sfx = sorted((a for a in ctx.timeline.audio if a.kind == "sfx"), key=lambda a: a.t0)
    if not sfx:
        return []
    gest = sfx_gestures(sfx)
    rate = len(gest) / dur
    ts = [g[0].t0 for g in gest]
    holes = [b - a for a, b in zip([0.0] + ts, ts + [dur])]
    ctx.metrics["sfx"] = {"n": len(sfx), "gestos": len(gest), "por_s": round(rate, 3), "por_min": round(rate * 60, 2),
                          "hueco_max_s": round(max(holes), 2) if holes else None}
    if rate > th["sfx_per_s_max"]:
        ctx.add("sfx.density", gate_severity("sfx.density"),
                f"{len(gest)} gestos de SFX en {dur:.0f} s = {rate:.2f}/s (máx. {th['sfx_per_s_max']}/s; un gesto es un "
                f"sonido con sus capas).", 0, dur,
                {"gestos": len(gest), "audio_items": len(sfx), "por_s": round(rate, 3), "umbral": th["sfx_per_s_max"]},
                [d for g in gest for a in g for d in a.decision_ids][:40],
                [{"op": "remove_sfx", "keep": "primeros de bloque, firma y acentos; quitar internos de los tramos densos"}])
    firma = _firma_ids(ctx)
    by_file: dict[str, list] = {}
    for g in gest:                                       # por GESTO: su fichero principal (las capas son su timbre)
        a = g[0]
        if a.id in firma:
            continue
        name = Path(a.path).stem.split("__", 1)[0]       # copia procesada (`<id>__hp250…`) = su original
        by_file.setdefault(name, []).append(a)
    # ventana DESLIZANTE de 60 s (antes por minuto natural: 4 al final de un minuto y 4 al
    # principio del siguiente no saltaban), entre paletas (por fichero)
    for name, lst in by_file.items():
        lst.sort(key=lambda a: a.t0)
        worst, k0 = [], 0
        for k in range(len(lst)):
            while lst[k].t0 - lst[k0].t0 >= 60.0:
                k0 += 1
            if k - k0 + 1 > len(worst):
                worst = lst[k0:k + 1]
        if len(worst) > th["sfx_same_per_min_max"]:
            ctx.add("sfx.repeat", gate_severity("sfx.density"),
                    f"La muestra «{name}» suena {len(worst)} veces en 60 s ({tc(worst[0].t0)}–{tc(worst[-1].t0)}; "
                    f"máx. {th['sfx_same_per_min_max']}; la firma declarada no cuenta).",
                    worst[0].t0, worst[-1].t0 + (worst[-1].dur or 0.3), {"muestra": name, "n": len(worst)},
                    [d for a in worst for d in a.decision_ids], [{"op": "vary_sfx", "sample": name}])
    k = 0
    while k < len(gest):
        grp = [g for g in gest[k:] if g[0].t0 - gest[k][0].t0 <= 1.0]
        if len(grp) > th["sfx_cluster_1s_max"]:
            ctx.add("sfx.cluster", gate_severity("sfx.density"),
                    f"Racimo de {len(grp)} gestos de SFX en 1 s ({tc(grp[0][0].t0)}).", grp[0][0].t0,
                    grp[-1][0].t0 + (grp[-1][0].dur or 0.3),
                    {"gestos": len(grp), "muestras": [Path(g[0].path).stem.split('__', 1)[0] for g in grp]},
                    [d for g in grp for a in g for d in a.decision_ids], [{"op": "remove_sfx", "keep": 1}])
            k += len(grp)
        else:
            k += 1
    return ["sfx.density"]


def check_sfx_silent_blocks(ctx: QAContext, th: dict) -> list[str]:
    """`sfx.silent_block` (warn): bloque (gráfico o B-roll) de ≥ `sfx_silent_min_s` con animación visible
    (eventos de events.json que no son layout, cámara, lockup ni salida) y sin ningún SFX: ni suyo (sus decisiones o
    su item en sfx_plan.json) ni de otro item a ±`sfx_silent_win_s` de alguna de sus animaciones.
    Caso típico: el director deja mudos varios bloques con `props.sfx: false` para cuadrar el tope."""
    import json
    from .config import gate_severity
    p = ctx.vdir / "events.json"
    if not p.exists():
        ctx.notes.append("Sin events.json: sfx.silent_block no se mide (cutkit.audio.events).")
        return []
    try:
        evs = json.loads(p.read_text()).get("events", [])
    except Exception:                                     # noqa: BLE001
        return []
    by_item: dict[str, list[dict]] = {}
    for e in evs:
        k = str(e.get("kind", ""))
        if k.startswith(("layout.", "camera.", "lockup.", "transition.")) or k in ("exit", "leave"):
            continue
        by_item.setdefault(str(e.get("item")), []).append(e)
    sfx = [a for a in ctx.timeline.audio if a.kind == "sfx"]
    gest_t = [g[0].t0 for g in sfx_gestures(sfx)]
    plan_item = {c["id"]: c.get("item_id") for c in _sfx_plan(ctx)}
    own_items = {plan_item.get(a.id) for a in sfx} - {None}
    own_decs = {d for a in sfx for d in a.decision_ids}
    win, dmin = float(th.get("sfx_silent_win_s", 0.25)), float(th.get("sfx_silent_min_s", 2.5))
    # un gráfico SIN eventos (p. ej. el marcador completo de keyword.highlight no emitía ninguno y quedaba
    # mudo sin que saltara la puerta) cuenta como animado si su componente suena en el mapa o el registro;
    # su animación es su entrada (t0)
    try:
        from ..audio.sfxplan import _anim_map
        from ..motion.registry import COMPONENTS
        emap = _anim_map().get("eventos") or {}
    except Exception:                                     # noqa: BLE001
        emap, COMPONENTS = {}, {}

    def _sounds(comp: str) -> bool:
        spec = COMPONENTS.get(comp) or {}
        reg = spec.get("sfx") if isinstance(spec, dict) else getattr(spec, "sfx", None)
        return bool(reg) or any(k == comp or k.startswith(comp + "@") for k in emap)
    mute = []
    for it in ctx.items(["graphic", "broll"]):
        if it.t1 - it.t0 < dmin - 1e-6:
            continue
        no_ev = not by_item.get(it.id)
        if no_ev and not _sounds(it.component or ""):
            continue
        if it.id in own_items or set(it.decision_ids) & own_decs:
            continue
        ets = [float(e["t"]) for e in by_item[it.id]] if not no_ev else [float(it.t0)]
        if any(abs(t - te) <= win for t in gest_t for te in ets):
            continue
        mute.append(it)
        muted_by = (it.props or {}).get("sfx") is False
        ctx.add("sfx.silent_block", gate_severity("sfx.silent_block"),
                f"Bloque animado mudo: {it.component} {tc(it.t0)}–{tc(it.t1)} "
                + ("(el componente no emite eventos y no suena)" if no_ev else f"({len(ets)} animaciones y ningún SFX)")
                + (" — lo silencia `props.sfx: false` (prohibido en un bloque animado: usa `sfx_skip`)." if muted_by else "."),
                it.t0, it.t1, {"item": it.id, "componente": it.component, "dur_s": round(it.t1 - it.t0, 2),
                               "animaciones": sorted({str(e.get('kind')) for e in by_item.get(it.id, [])}), "sin_eventos": no_ev,
                               "props_sfx_false": muted_by},
                it.decision_ids,
                [{"op": "unset_prop", "item": it.id, "prop": "sfx"}] if muted_by else
                [{"op": "emit_events" if no_ev else "map_sfx", "component": it.component,
                  "events": sorted({str(e.get('kind')) for e in by_item.get(it.id, [])})}])
    ctx.metrics["sfx_silent_blocks"] = [m.id for m in mute]
    return ["sfx.silent_block"]


def check_music_tail(ctx: QAContext, max_cut_s: float = 0.3, fade_ok_s: float = 0.5, room_ok_s: float = 1.0,
                     max_bar_plays: int = 2) -> None:
    """`audio.music_tail_cut`: el final propio de la cama no puede perder más de 0,3 s AUDIBLES de cola al acabar
    el vídeo (lo mide `music.fit_to_duration` y lo deja en el sidecar `<pista>.json`).
    NO es un corte en seco si el golpe final (`end_at`) cae
    después de la última palabra, quedan ≥ `room_ok_s` de programa tras él y lo que no cabe de la cola se funde en
    ≥ `fade_ok_s` (`tail_fade_s`, FIT_VERSION 14): lo que se pierde es el final de la reverberación, ya 15–25 dB bajo la
    cama (medido: 11789620de70ef16 con 1,26 s tras el golpe pierde 0,36 s de cola a −55…−60 dBFS). Entonces se informa.
    `audio.music_loop` (warn): el encaje repite un compás de la fuente más de `max_bar_plays` veces (bucle audible;
    `music.ensure` ya no lo elige solo, pero `tokens.music_track` puede fijarlo)."""
    import json
    for a in ctx.timeline.audio:
        if a.kind != "music":
            continue
        sc = Path(a.path).with_suffix(".json")
        if not sc.exists():
            continue
        try:
            fit = json.loads(sc.read_text()).get("fit", {})
        except Exception:                                 # noqa: BLE001
            continue
        cut = fit.get("tail_cut_s")
        ctx.metrics["music_tail_cut_s"] = cut
        plays = fit.get("max_bar_plays")
        ctx.metrics["music_max_bar_plays"] = plays
        if plays is not None and int(plays) > max_bar_plays:
            ctx.add("audio.music_loop", "warn",
                    f"La cama repite un mismo compás de la pista {plays} veces (bucle audible; máximo {max_bar_plays}): "
                    f"quitar `tokens.music_track` para que `music.ensure` elija una pista sin bucle, o una pista nueva.",
                    0, ctx.duration, {"max_bar_plays": plays, "repeated_bars": fit.get("repeated_bars"),
                                      "umbral": max_bar_plays},
                    ctx.blame(0, ctx.duration, tracks=[], audio_kinds=["music"]), [{"op": "music_track", "track": None}])
        words = ctx.words_sorted()
        last_w = words[-1][2] if words else None
        end_at, fade = fit.get("end_at"), fit.get("tail_fade_s")
        faded = (cut is not None and cut > max_cut_s and end_at is not None and fade is not None and last_w is not None
                 and float(fade) >= fade_ok_s - 1e-3 and float(end_at) >= last_w - 0.02
                 and float(ctx.duration) - float(end_at) >= room_ok_s - 1e-3)
        if faded:
            ctx.metrics["music_tail_faded"] = {"tail_cut_s": cut, "tail_fade_s": fade, "end_at": end_at,
                                               "last_word_end_s": round(last_w, 3)}
            ctx.add("audio.music_tail_cut", "info",
                    f"La cola de la música pierde {cut:.2f} s al acabar, pero el golpe final cae tras la última palabra "
                    f"({end_at:.2f} s), suena {float(ctx.duration) - float(end_at):.2f} s después y se funde en "
                    f"{float(fade):.2f} s: no es un corte en seco.",
                    fit.get("end_at"), ctx.duration, {"tail_cut_s": cut, "tail_fade_s": fade, "end_at": end_at,
                                                      "umbral_fundido_s": fade_ok_s})
            continue
        if cut is not None and cut > max_cut_s:
            ctx.add("audio.music_tail_cut", "block",
                    f"Se recortan {cut:.2f} s audibles de la cola final de la música (máximo {max_cut_s:.1f} s): "
                    f"adelantar `end_at` o alargar el final del vídeo.",
                    fit.get("end_at"), ctx.duration, {"tail_audible_s": fit.get("tail_audible_s"), "tail_cut_s": cut,
                                                      "end_at": fit.get("end_at"), "umbral_s": max_cut_s},
                    ctx.blame(ctx.duration - 1.0, ctx.duration, tracks=[], audio_kinds=["music"]),
                    [{"op": "music_end_at", "end_at": round((fit.get("end_at") or ctx.duration) - (cut - max_cut_s), 3)}])


def check_music_dropouts(ctx: QAContext, stems: dict[str, list[Path]], max_db: float = -40.0) -> None:
    """`audio.music_dropout`: dentro de cada caída de la cama (automatización a −60) la música tiene que estar a
    ≤ −40 dBFS (stem de música). Antes un punto del outro la subía en mitad de la caída, encima de la última palabra."""
    if not stems.get("music"):
        return
    wins = []
    for a in ctx.timeline.audio:
        if a.kind != "music":
            continue
        auto = sorted((float(p[0]), float(p[1])) for p in (a.automation or []))
        for (u0, g0), (u1, g1) in zip(auto, auto[1:]):
            if g0 <= -59 and g1 <= -59 and u1 - u0 > 0.08:
                wins.append((a.t0 + u0, a.t0 + u1))
    if not wins:
        return
    try:
        import soundfile as sf
        x, sr = sf.read(str(stems["music"][0]), always_2d=True)
    except Exception as e:                                # noqa: BLE001
        ctx.notes.append(f"Caídas de música sin medir ({e}).")
        return
    mono = x.mean(axis=1)
    res = []
    for a, b in wins:
        s, e = int((a + 0.03) * sr), int((b - 0.03) * sr)
        if e <= s or s >= len(mono):
            continue
        db = float(20 * np.log10(np.sqrt(np.mean(mono[s:e] ** 2)) + 1e-12))
        res.append({"t0": round(a, 3), "t1": round(b, 3), "dbfs": round(db, 1)})
        if db > max_db:
            ctx.add("audio.music_dropout", "block",
                    f"La música suena a {db:.1f} dBFS dentro de su caída {a:.2f}–{b:.2f} s (máximo {max_db:.0f} dBFS).",
                    a, b, {"dbfs": round(db, 1), "umbral_dbfs": max_db},
                    ctx.blame(a, b, tracks=[], audio_kinds=["music"]), [])
    ctx.metrics["music_dropouts"] = res


def run(ctx: QAContext) -> None:
    check_loudness(ctx)
    check_sfx_visual_sync(ctx)
    check_music_tail(ctx)
    stems = _stems(ctx)
    ctx.metrics["stems"] = {k: [p.name for p in v] for k, v in stems.items()}
    check_music_dropouts(ctx, stems)
    voice = check_vmr(ctx, stems)
    check_silences(ctx, stems, voice)
