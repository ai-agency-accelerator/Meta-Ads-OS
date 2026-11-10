"""Mezcla y máster de una `Timeline` (voz + room tone + música + SFX) a 48 kHz estéreo.

Convenciones de `AudioItem` (cutkit/spec.py):
- `t0`: segundos de programa en que suena el PUNTO DE SINCRONÍA; el fichero arranca en `t0 − sync_offset`.
  En SFX, si `sync_offset == 0` y el fichero está en el catálogo, se usa su `punto_sincronia_ms` (o el del recorte);
  para un ataque en la primera muestra, `sfxplan` escribe 1e-4. `pitch` (semitonos) se aplica por remuestreo y el
  punto de sincronía escala con la velocidad.
- `gain_db`: en VOZ es ganancia de clip absoluta; en MÚSICA y SFX es un DESPLAZAMIENTO sobre el nivel calibrado
  (cama a `bed_lu_rel_voice` de la voz; SFX a su `rel_voice_lu` respecto a la voz a corto plazo alrededor de t0).
- `automation`: [(t programa, dB)] interpolado en dB (drop-outs de música, respiraciones…).
- `duck`: la música baja `duck_db` bajo la voz (anticipación 150 ms, ataque 100, mantenimiento 300, relajación 500)
  y se «talla» 2,5 dB en 2,5 kHz solo mientras hay voz.
Perfil: `PROFILE` ← `timeline.style["audio"]` ← argumento `profile`.

Voz: ítems contiguos (los cortes del A-roll) → fundido cruzado SOLAPADO de potencia constante de 10 ms con manijas
de la fuente y ajuste a cruce por cero (±2 ms); huecos → room tone en bucle (nunca silencio digital).
Máster: ganancia estática a −14 LUFS + limitador de true peak (×4, anticipación 5 ms, relajación 80 ms) a −1,5 dBTP,
iterado hasta ±0,1 LU. Nunca `loudnorm`. Escribe `mix.wav`, `stems/{voice,music,sfx}.wav` y `mix_report.json`.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from scipy import ndimage, signal

from . import _dsp as d
from . import sfx as sfxlib

SR = d.SR
PROFILE: dict = {
    "format": "anuncio",
    "target_lufs": -14.0,
    "tp_dbtp": -1.5,
    "bed_lu_rel_voice": -18.0,          # Shorts −18 (−15…−23); largos −20/−24
    "bed_no_voice_lu_rel_voice": -12.0,  # música sola (montajes, cierre)
    "duck_db": 3.0,                      # Shorts 0–3 dB extra; largos 4–8
    # Una cama plana quedaba −21,8 LU bajo la voz en 400 Hz–6 kHz y con el 72 % de su energía bajo 300 Hz: en el móvil
    # no se oía. Ducking SIEMPRE 3 dB: la calibración se mide durante el
    # habla (ya agachada), así que bajo la voz sigue a −18 LU y en los huecos sube a −15
    "duck_all": True,
    "music_presence_hz": 2000.0, "music_presence_db": 3.0, "music_presence_q": 1.0,   # presencia en el bus de la cama
    "music_lift_ramp_s": 0.30,           # rampa de `tokens.music_lift` del plan: [{start, end, lu}] sube la cama en un tramo
    # Evita un último golpe flojo y la cola fundida bajo la CTA congelada. Tras
    # la ÚLTIMA palabra (si quedan ≤ `end_window_s` de programa) ya no hay voz que proteger: la cama suelta el ducking y
    # el tallado en `end_duck_release_s` y sube hasta el nivel de «cierre» (`end_bed_lu_rel_voice`, por defecto
    # `bed_no_voice_lu_rel_voice` = −12 LU: música sola, cierre) con una rampa de `end_ramp_s`. Así suena la cola de la
    # música que promete el perfil (outro.hold_after: «suena la cola de la música, no acaba en seco»)
    "end_window_s": 2.0, "end_bed_lu_rel_voice": None, "end_ramp_s": 0.08, "end_duck_release_s": 0.06,
    "end_after_word_s": 0.03,            # la rampa arranca 30 ms tras el final de la última palabra (su fundido es de 35 ms)
    # paradas propias del tema dentro de una pausa de voz: desde 100 ms y uniendo las que separa un repunte ≤ 80 ms
    # (un golpe de charles entre dos caídas: tras el EQ de bus el repunte dura unos 60 ms)
    "pause_gap_min_s": 0.10, "pause_gap_bridge_s": 0.08,
    "duck_lookahead_s": 0.15, "duck_attack_s": 0.10, "duck_hold_s": 0.30, "duck_release_s": 0.50,
    "carve_db": 2.5, "carve_hz": 2500.0, "carve_q": 0.8,
    "calib_highpass_hz": 0.0,            # la cama se calibra en BANDA COMPLETA a bed_lu_rel_voice (−18 LU); con
                                         # > 0 (antes 300) se calibraría con voz y música filtradas por encima de ese corte…
    "bed_fullband_max_lu_rel_voice": -15.0,   # …sin que la banda completa pase de −15 LU respecto a la voz
    "reentry_ramp_s": 0.02,              # los drop-outs vuelven secos (≤ 20 ms) en el pulso siguiente a su palabra
    "music_highpass_hz": 115.0,          # EQ de bus de la cama ANTES de calibrar: paso alto 12 dB/oct (115 Hz; antes 80)…
    "music_lowshelf_hz": 150.0, "music_lowshelf_db": -3.0,   # …y estante −3 dB (que el bajo no pise la voz)
    "voice_xfade_s": 0.010, "zero_cross_s": 0.002,
    "roomtone_xfade_s": 0.08,
    "sfx_highpass_hz": 120.0,
    "sfx_rel_voice_lu": dict(sfxlib.REL_VOICE_LU),
    "sfx_max_per_min": 24.0,             # GESTOS por minuto (un sonido con sus capas = 1), como los perfiles anuncio y organico y la QA sfx.density (≤ 0,40/s); antes se contaba cada fichero (14)
    "limiter_lookahead_s": 0.005, "limiter_release_s": 0.08,
    "master_fade_out_s": 0.15,           # fundido a −∞ al final del programa (en el máster)
}


# ───────────────────────────── utilidades ─────────────────────────────
class _Cache:
    def __init__(self):
        self.files: dict[tuple[str, int], np.ndarray] = {}

    def get(self, path: str, ch: int) -> np.ndarray:
        k = (str(path), ch)
        if k not in self.files:
            self.files[k] = d.load(path, channels=ch)
        return self.files[k]


def _add(bus: np.ndarray, x: np.ndarray, pos: int) -> None:
    """Suma `x` en `bus` a partir de la muestra `pos` (recorta por los bordes)."""
    a, b = max(0, pos), min(len(bus), pos + len(x))
    if b > a:
        bus[a:b] += x[a - pos: b - pos]


def _automation_curve(points, t: np.ndarray) -> np.ndarray:
    if not points:
        return np.zeros_like(t)
    pts = sorted((float(a), float(b)) for a, b in points)
    return np.interp(t, [p[0] for p in pts], [p[1] for p in pts])


def _fade(x: np.ndarray, n_in: int, n_out: int, shape: str = "eqp") -> np.ndarray:
    """Fundidos de potencia constante (sin/cos) al principio y al final."""
    x = x.copy()
    if n_in > 0:
        n_in = min(n_in, len(x))
        c = np.sin(np.linspace(0, np.pi / 2, n_in)) if shape == "eqp" else np.linspace(0, 1, n_in)
        x[:n_in] *= c[:, None] if x.ndim == 2 else c
    if n_out > 0:
        n_out = min(n_out, len(x))
        c = np.cos(np.linspace(0, np.pi / 2, n_out)) if shape == "eqp" else np.linspace(1, 0, n_out)
        x[-n_out:] *= c[:, None] if x.ndim == 2 else c
    return x


def _zero_cross(src: np.ndarray, i: int, win: int) -> int:
    """Cruce por cero más cercano a `i` dentro de ±win muestras (mono)."""
    a, b = max(1, i - win), min(len(src) - 1, i + win)
    if b <= a:
        return i
    seg = src[a - 1:b]
    zc = np.where(np.signbit(seg[:-1]) != np.signbit(seg[1:]))[0] + a
    return int(zc[np.argmin(np.abs(zc - i))]) if zc.size else i


def _power_mean_lufs(vals: np.ndarray) -> float:
    vals = vals[np.isfinite(vals) & (vals > -70)]
    return float(10 * np.log10(np.mean(10 ** (vals / 10)))) if vals.size else -70.0


# ───────────────────────────── limitador de true peak ─────────────────────────────
def _tp_envelope(x: np.ndarray, oversample: int = 4, chunk: int = SR * 10, pad: int = 256) -> np.ndarray:
    """Pico verdadero por muestra (máx. de las 4 submuestras y canales), por bloques para no gastar memoria."""
    n = len(x)
    out = np.empty(n, dtype=np.float64)
    for s in range(0, n, chunk):
        a, b = max(0, s - pad), min(n, s + chunk + pad)
        up = signal.resample_poly(x[a:b].astype(np.float64), oversample, 1, axis=0)
        pk = np.abs(up).max(axis=1)[: (b - a) * oversample].reshape(b - a, oversample).max(axis=1)
        e = min(n, s + chunk)
        out[s:e] = pk[s - a: s - a + (e - s)]
    return np.maximum(out, np.abs(x).max(axis=1))


def tp_limiter(x: np.ndarray, ceiling_dbtp: float, lookahead_s: float = 0.005, release_s: float = 0.08,
               oversample: int = 4) -> tuple[np.ndarray, dict]:
    """Limitador con anticipación sobre el pico verdadero (×4).

    gr = techo / pico → mínimo hacia delante (anticipación) → relajación exponencial a 1 ms de resolución →
    mínimo hacia delante + media hacia atrás de la misma ventana (rampa de ataque que garantiza g ≤ gr en el pico).
    """
    ceil = d.undb(ceiling_dbtp)
    pk = _tp_envelope(x, oversample)
    gr = np.minimum(1.0, ceil / np.maximum(pk, 1e-12))
    m = max(1, int(lookahead_s * SR) // 2)
    L = 2 * m + 1
    g_min = ndimage.minimum_filter1d(gr, size=L, origin=-m)               # min(gr[i … i+2m])
    B = 48                                                                # bloques de 1 ms
    nb = math.ceil(len(g_min) / B)
    padv = np.pad(g_min, (0, nb * B - len(g_min)), constant_values=1.0)
    need = padv.reshape(nb, B).min(axis=1)
    rel = 1 - math.exp(-1.0 / (release_s * 1000))
    env = np.empty(nb)
    e = 1.0
    for i in range(nb):                                                   # ~1e5 iteraciones: rápido
        e = min(need[i], e + (1 - e) * rel)
        env[i] = e
    env_s = np.repeat(env, B)[: len(x)]
    h = ndimage.minimum_filter1d(env_s, size=L, origin=-m)
    g = ndimage.uniform_filter1d(h, size=L, origin=m)                     # media de h[i−2m … i]
    g = np.minimum(g, 1.0)
    y = x * g[:, None]
    return y.astype(np.float32), {"max_gr_db": round(float(-d.db(g.min())), 2),
                                  "gr_active_ratio": round(float((g < 0.999).mean()), 4)}


# ───────────────────────────── pistas ─────────────────────────────
def _is_roomtone(it) -> bool:
    return it.id.startswith("roomtone") or str(it.path).endswith("#roomtone")


def _source_words(slug: str | None) -> dict[str, list[tuple[float, float]]]:
    """Palabras (segundos de la FUENTE) por ruta de audio de voz, desde `media_index.json` del run."""
    import json as _json
    out: dict[str, list[tuple[float, float]]] = {}
    if not slug:
        return out
    try:
        from cutkit.paths import run_dir
        mi = _json.loads((run_dir(slug) / "media_index.json").read_text())
    except Exception:                                    # noqa: BLE001
        return out
    by_src: dict[str, list[tuple[float, float]]] = {}
    for w in mi.get("words", []):
        by_src.setdefault(w["src"], []).append((float(w["s"]), float(w["e"])))
    for srcd in mi.get("sources", []):
        ws = by_src.get(srcd["id"], [])
        for p in (srcd.get("audio"), str(run_dir(slug) / "media" / f"voice_{srcd['id']}.wav")):
            if p:
                out[str(Path(p).resolve())] = ws
    return out


def _voice_bus(items, N, prof, cache, report, words_src: dict | None = None):
    bus = np.zeros(N, dtype=np.float64)
    rt_items = [it for it in items if _is_roomtone(it)]      # relleno explícito con el ruido de sala de su fuente
    items = sorted([it for it in items if not _is_roomtone(it)], key=lambda a: a.t0)
    h = int(round(prof["voice_xfade_s"] / 2 * SR))
    zc = int(round(prof["zero_cross_s"] * SR))
    spans, joins = [], 0
    for k, it in enumerate(items):
        src = cache.get(it.path, 1)[:, 0]
        dur = it.dur if it.dur is not None else len(src) / SR - it.media_start
        dur = max(0.0, min(dur, len(src) / SR - it.media_start))      # nunca más allá de la fuente
        prev_c = k > 0 and abs(items[k - 1].t0 + (items[k - 1].dur or 0) - it.t0) < 0.002
        next_c = k + 1 < len(items) and abs(it.t0 + dur - items[k + 1].t0) < 0.002
        i0 = _zero_cross(src, int(round(it.media_start * SR)), zc)
        i1 = _zero_cross(src, int(round((it.media_start + dur) * SR)), zc)
        hin = min(h, i0) if prev_c else 0
        hout = min(h, len(src) - i1) if next_c else 0
        seg = src[i0 - hin: i1 + hout].astype(np.float64)
        n_in = 2 * hin if prev_c else int(max(it.fade_in, 0.010) * SR)
        n_out = 2 * hout if next_c else int(max(it.fade_out, 0.010) * SR)
        seg = _fade(seg, n_in, n_out)
        pos = int(round(it.t0 * SR)) - hin
        t = (pos + np.arange(len(seg))) / SR
        gdb = it.gain_db + _automation_curve(it.automation, t)
        _add(bus, seg * d.undb(gdb), pos)
        spans.append((it.t0, it.t0 + dur, it.path))
        joins += int(prev_c)
    # room tone en los huecos (y antes de la primera palabra si el programa empieza en silencio)
    gaps = []
    for (s0, e0, p0), (s1, e1, p1) in zip(spans, spans[1:]):
        if s1 - e0 > 0.002:
            gaps.append((e0, s1, p0))
    if spans and spans[0][0] > 0.03:
        gaps.insert(0, (0.0, spans[0][0], spans[0][2]))
    if spans and N / SR - spans[-1][1] > 0.03:
        gaps.append((spans[-1][1], N / SR, spans[-1][2]))
    # los rellenos explícitos mandan sobre los automáticos que pisan
    explicit = [(it.t0, it.t0 + (it.dur or 0.0), str(it.path).replace("#roomtone", ""), it.gain_db) for it in rt_items]
    gaps = [(g0, g1, p, 0.0) for g0, g1, p in gaps if not any(a < g1 and b > g0 for a, b, _, _ in explicit)] + explicit
    rt_info = {}
    for g0, g1, path, gdb in gaps:
        if path not in rt_info:
            # ventana real limpia (pico < −45 dBFS, ≥ 150 ms de cualquier palabra) o ruido sintético con el espectro
            # del suelo de esa voz: nunca colas de palabras ni chasquidos
            src = cache.get(path, 1)[:, 0]
            ws = (words_src or {}).get(str(Path(path).resolve()), [])
            tone, rt = d.room_tone(src, SR, words=ws, length=3.0)
            rt_info[path] = (tone, rt)
        tone, rt = rt_info[path]
        ov = 0.02
        need = int((g1 - g0 + 2 * ov) * SR)
        x = _loop(tone, need, int(prof["roomtone_xfade_s"] * SR))
        x = _fade(x, int(ov * 2 * SR), int(ov * 2 * SR))
        _add(bus, x * d.undb(gdb), int((g0 - ov) * SR))
    report["voice"] = {"items": len(items), "joins_xfaded": joins, "xfade_ms": prof["voice_xfade_s"] * 1000,
                       "roomtone_gaps": len(gaps), "roomtone_explicit": len(explicit),
                       "roomtone_s": round(sum(g[1] - g[0] for g in gaps), 3),
                       "roomtone_src": [v[1] for v in rt_info.values()]}
    return bus, spans


def _loop(tone: np.ndarray, n: int, xf: int) -> np.ndarray:
    if len(tone) == 0:
        return np.zeros(n)
    xf = max(8, min(xf, len(tone) // 3))
    out = tone.copy()
    while len(out) < n:
        th = np.linspace(0, np.pi / 2, xf)
        mid = out[-xf:] * np.cos(th) + tone[:xf] * np.sin(th)
        out = np.concatenate([out[:-xf], mid, tone[xf:]])
    return out[:n]


def _activity(voice: np.ndarray, word_times: dict, N: int, prof: dict) -> np.ndarray:
    """Actividad de voz 0/1 a 100 Hz (palabras de la timeline si las hay; si no, RMS)."""
    fr = 100
    nf = int(math.ceil(N / SR * fr))
    act = np.zeros(nf, dtype=bool)
    if word_times:
        for s, e in word_times.values():
            act[max(0, int(s * fr)): min(nf, int(math.ceil(e * fr)))] = True
    else:
        t, r = d.frame_rms_db(voice, SR, 0.03, 0.01)
        sp = d.speech_mask(r, float(np.percentile(r, 5)))
        idx = np.clip((t * fr).astype(int), 0, nf - 1)
        act[idx[sp]] = True
    # une huecos menores que el mantenimiento
    act = ndimage.binary_closing(act, structure=np.ones(max(1, int(prof["duck_hold_s"] * fr))))
    return act


def _duck_env(act: np.ndarray, N: int, prof: dict) -> np.ndarray:
    """Envolvente 0..1 de ducking a 100 Hz → interpolada a muestras. Anticipación + ataque + mantenimiento + relajación."""
    fr = 100
    a = act.copy()
    la = int(prof["duck_lookahead_s"] * fr)
    if la > 0:                                          # empieza `lookahead` antes de la voz
        a = a | np.r_[a[la:], np.zeros(la, bool)]
    hold = int(prof["duck_hold_s"] * fr)
    hold = max(1, hold)
    a = ndimage.maximum_filter1d(a.astype(float), size=hold, origin=(hold - 1) // 2) > 0.5   # mantiene tras la voz
    ka = 1 - math.exp(-1 / (prof["duck_attack_s"] * fr))
    kr = 1 - math.exp(-1 / (prof["duck_release_s"] * fr))
    env = np.empty(len(a))
    e = 0.0
    for i, v in enumerate(a):
        e += (1.0 - e) * ka if v else -e * kr
        env[i] = e
    t = np.arange(N) / SR
    return np.interp(t, np.arange(len(env)) / fr, env)


def _music_beats(it) -> list[float]:
    """Pulsos del encaje en tiempo de programa (sidecar `<pista>.json` que escribe `music.ensure`)."""
    import json as _json
    p = Path(it.path).with_suffix(".json")
    if not p.exists():
        return []
    try:
        fit = _json.loads(p.read_text()).get("fit", {})
    except Exception:                                    # noqa: BLE001
        return []
    off = (it.t0 - it.sync_offset) - it.media_start
    return [b + off for b in fit.get("beats_prog_s", [])]


def _low_hits(mono: np.ndarray, t_from: float, t_to: float) -> list[float]:
    """Ataques de golpes graves (bombo/bajo, < 150 Hz) entre `t_from` y `t_to` (segundos de programa): el instante en
    que la envolvente de 5 ms sube del 30 % de su pico. La rejilla de pulsos no ve los golpes a contratiempo."""
    a, b = max(0, int((t_from - 0.3) * SR)), min(len(mono), int((t_to + 0.3) * SR))
    if b - a < int(0.05 * SR):
        return []
    lo = signal.sosfilt(signal.butter(4, 150, "lowpass", fs=SR, output="sos"), mono[a:b])
    env = np.sqrt(np.convolve(lo ** 2, np.ones(240) / 240, mode="same"))
    if env.max() <= 1e-6:
        return []
    pk, _ = signal.find_peaks(env, height=env.max() * 0.35, prominence=env.max() * 0.2, distance=int(0.12 * SR))
    out = []
    for k in pk:
        j = k
        while j > 0 and env[j] > 0.3 * env[k]:
            j -= 1
        t = (a + j) / SR
        if t_from <= t <= t_to:
            out.append(round(t, 4))
    return out


def _quiet_runs(voice: np.ndarray | None, t0: float, t1: float, drop_db: float = 25.0) -> list[tuple[float, float]]:
    """Tramos en que la voz cae `drop_db` bajo su máximo local (energía de 20 ms, salto 10 ms) entre t0 y t1."""
    if voice is None:
        return []
    a, b = int(max(0.0, t0) * SR), int(t1 * SR)
    seg = voice[a:b]
    hop, win = int(0.01 * SR), int(0.02 * SR)
    n = (len(seg) - win) // hop
    if n <= 3:
        return []
    lv = np.array([20 * np.log10(np.sqrt(np.mean(seg[i * hop: i * hop + win] ** 2)) + 1e-12) for i in range(n)])
    quiet = lv < max(lv.max() - drop_db, -55.0)
    runs, st = [], None
    for i, q in enumerate(np.append(quiet, False)):
        if q and st is None:
            st = i
        elif not q and st is not None:
            c0 = max(0.0, t0) + st * hop / SR + win / SR / 2 - hop / SR / 2
            c1 = max(0.0, t0) + (i - 1) * hop / SR + win / SR / 2 + hop / SR / 2
            runs.append((c0, c1))
            st = None
    return runs


def _exit_in_voice_gap(t1: float, words, hits_at, beats, exit_ramp: float, guard: float,
                       voice: np.ndarray | None = None) -> tuple[float, float] | None:
    """Salida de la cama en un hueco de voz ANTES de su palabra ancla (la primera que empieza tras la rampa
    planificada), dentro de [ancla − 0,6, ancla]. Huecos = silencio entre palabras del ASR y tramos en que la voz real
    cae 25 dB (el ASR estira los finales). Del más tardío al más temprano: la rampa acaba en el hueco, 10 ms antes del
    golpe vecino si lo hay, y no pisa ningún golpe; puede empezar hasta 40 ms antes del hueco. None si no cabe."""
    starts = sorted(s_ for s_, _ in words)
    anchor = next((s0 for s0 in starts if s0 >= t1 - 0.05), None)
    if anchor is None or anchor - t1 > 1.0:
        return None
    lo = anchor - 0.6
    prev_end = max((e for s_, e in words if e <= anchor - 0.005), default=-1.0)
    runs = _quiet_runs(voice, lo, anchor)
    if anchor - 0.005 - max(prev_end, lo) >= 0.03:
        runs.append((max(prev_end, lo), anchor - 0.005))
    hs = sorted(set([float(b) for b in beats if lo - 0.2 <= b <= anchor + 0.05] + hits_at(lo - 0.2, anchor + 0.05)))
    for r0, r1 in sorted(runs, key=lambda r: -r[1]):
        fe = r1
        near = [h for h in hs if r0 < h <= r1 + 0.04]
        if near:
            fe = near[0] - guard
        for _ in range(4):
            inside = [h for h in hs if fe - exit_ramp < h <= fe]
            if not inside:
                break
            fe = inside[0] - guard
        fs = max(r0 - 0.04, fe - exit_ramp)
        if fe - fs >= 0.015 and fe <= anchor and fs >= lo:
            return fs, fe
    return None


def _music_downbeats(it) -> list[float]:
    """Downbeats del encaje en tiempo de programa (sidecar `<pista>.json`)."""
    import json as _json
    p = Path(it.path).with_suffix(".json")
    try:
        fit = _json.loads(p.read_text()).get("fit", {}) if p.exists() else {}
    except Exception:                                    # noqa: BLE001
        fit = {}
    off = (it.t0 - it.sync_offset) - it.media_start
    return [b + off for b in fit.get("downbeats_prog_s", [])]


def _snap_reentries(points, beats: list[float], ramp: float, exit_ramp: float = 0.06,
                    exit_guard: float = 0.010, hits=None, words=None,
                    voice: np.ndarray | None = None) -> tuple[list[tuple[float, float]], list[dict]]:
    """Encaja los drop-outs al pulso.
    - SALIDA (de > −40 dB a ≤ −40 dB): en el hueco de voz antes de su palabra ancla ([ancla − 0,6, ancla]), lo más
      tarde posible y 10 ms antes del golpe junto a la palabra; si no hay hueco y la rampa pisa un golpe (pulso de
      la rejilla o ataque grave medido entre su inicio − 30 ms y su final),
      se adelanta para que ACABE `exit_guard` antes de ese pulso (rampa `exit_ramp`): el golpe no suena cortado.
    - VUELTA (de ≤ −40 dB a > −40 dB): SECA (`ramp`) y acaba en el primer pulso tras el final del hueco."""
    pts = sorted((float(a), float(b)) for a, b in points)
    if not beats or len(pts) < 2:
        return pts, []
    bt = np.asarray(beats)
    moves: list[dict] = []
    # salidas
    res = list(pts)
    for i in range(len(res) - 1):
        (t0, v0), (t1, v1) = res[i], res[i + 1]
        if v0 > -40 >= v1 and words:
            gap = _exit_in_voice_gap(t1, words, hits or (lambda a_, b_: []), bt, exit_ramp, exit_guard, voice)
            if gap is not None:
                s1, e1 = gap
                # la meseta (−60) tiene que seguir: la salida no puede pasar del siguiente punto
                if i + 2 >= len(res) or e1 < res[i + 2][0]:
                    res[i], res[i + 1] = (s1, v0), (e1, v1)
                    moves.append({"exit_from": [round(t0, 3), round(t1, 3)], "exit_to": [round(s1, 3), round(e1, 3)],
                                  "voice_gap": True})
                    continue
        if v0 > -40 >= v1:
            # golpe que la rampa cortaría a medias: pulso de la rejilla o ataque grave medido (contratiempos)
            cand = sorted(set([float(v) for v in bt[(bt >= t0 - 0.03) & (bt < t1)]] + (hits(t0 - 0.03, t1) if hits else [])))
            if cand:
                b = cand[0]
                e1 = b - exit_guard
                s1 = max(e1 - exit_ramp, res[i - 1][0] + 1e-3 if i > 0 else 0.0)
                res[i], res[i + 1] = (s1, v0), (e1, v1)
                moves.append({"exit_from": [round(t0, 3), round(t1, 3)], "exit_to": [round(s1, 3), round(e1, 3)],
                              "beat": round(b, 3)})
    pts = sorted(res)
    out, i = [], 0
    while i < len(pts):
        t, v = pts[i]
        if i + 1 < len(pts) and v <= -40 < pts[i + 1][1]:
            nxt = bt[bt >= t - 1e-3]
            if nxt.size and nxt[0] - t <= 1.0:
                b = float(nxt[0])
                hi = pts[i + 1][1]
                out += [(max(t, b - ramp), v), (b, hi)]
                moves.append({"from": [round(t, 3), round(pts[i + 1][0], 3)], "to_beat": round(b, 3)})
                # descarta puntos que quedarían antes de la nueva vuelta
                j = i + 2
                while j < len(pts) and pts[j][0] <= b:
                    j += 1
                i = j
                continue
        out.append((t, v))
        i += 1
    return out, moves


def _music_bus(items, N, prof, cache, voice, act, report, words=None):
    bus = np.zeros((N, 2), dtype=np.float64)
    if not items:
        report["music"] = {"items": 0}
        return bus
    env = _duck_env(act, N, prof)
    # final: tras la última palabra la cama suelta el ducking enseguida (no 0,3 s de mantenimiento + 0,5 s de
    # relajación: el último golpe caía agachado) y luego sube al nivel de cierre (más abajo, tras calibrar)
    t_all = np.arange(N) / SR
    last_w = max((float(e) for _, e in (words or [])), default=None)
    end_t0 = None
    if last_w is not None and 0.0 < N / SR - last_w <= float(prof.get("end_window_s", 2.0)):
        end_t0 = last_w + float(prof.get("end_after_word_s", 0.03))
        rel_ = max(1e-3, float(prof.get("end_duck_release_s", 0.06)))
        env = env * np.clip(1.0 - (t_all - end_t0) / rel_, 0.0, 1.0)
    carve_sos = d.peaking_sos(prof["carve_hz"], -abs(prof["carve_db"]), prof["carve_q"]) if prof["carve_db"] else None
    bus_eq = []
    if prof.get("music_highpass_hz"):
        bus_eq.append(signal.butter(2, prof["music_highpass_hz"], "highpass", fs=SR, output="sos"))
    if prof.get("music_lowshelf_db"):
        bus_eq.append(d.shelf_sos(prof["music_lowshelf_hz"], prof["music_lowshelf_db"], SR, "low"))
    if prof.get("music_presence_db"):                    # que la cama asome en el altavoz del móvil
        bus_eq.append(d.peaking_sos(prof["music_presence_hz"], prof["music_presence_db"], prof.get("music_presence_q", 1.0)))
    # loudness de la voz en ventanas de 400 ms y actividad por ventana (para calibrar «durante el habla»)
    tv, lv = d.short_term(voice, SR, 0.4, 0.1)
    act_w = act[np.clip((tv * 100).astype(int), 0, len(act) - 1)]
    L_voice_speech = _power_mean_lufs(lv[act_w])
    L_voice = d.integrated_lufs(voice)
    hp_cal = signal.butter(4, prof["calib_highpass_hz"], "highpass", fs=SR, output="sos") if prof.get("calib_highpass_hz") else None
    if hp_cal is not None:
        _, lv_hp = d.short_term(signal.sosfilt(hp_cal, voice, axis=0), SR, 0.4, 0.1)
        L_voice_speech_hp = _power_mean_lufs(lv_hp[act_w])
    if L_voice <= -60:                                   # sin voz (montaje): la cama manda; el máster pone el nivel
        L_voice = L_voice_speech = prof["target_lufs"] - prof["bed_no_voice_lu_rel_voice"]
        hp_cal = None
    info = []
    for it in items:
        src = cache.get(it.path, 2)
        a = int(round(it.media_start * SR))
        dur = it.dur if it.dur is not None else len(src) / SR - it.media_start
        seg = src[a: a + int(round(dur * SR))].astype(np.float64)
        for sos in bus_eq:                               # EQ de bus antes de calibrar
            seg = signal.sosfilt(sos, seg, axis=0)
        seg = _fade(seg, int(max(it.fade_in, 0.01) * SR), int(max(it.fade_out, 0.01) * SR), shape="eqp")
        pos = int(round((it.t0 - it.sync_offset) * SR))
        tmp = np.zeros((N, 2))
        _add(tmp, seg, pos)
        t = np.arange(N) / SR
        mono = tmp.mean(axis=1)
        auto, moves = _snap_reentries(it.automation, _music_beats(it), prof.get("reentry_ramp_s", 0.02),
                                      hits=lambda a_, b_: _low_hits(mono, a_, b_), words=words,
                                      voice=voice.mean(axis=1) if voice is not None and voice.ndim == 2 else voice)
        # paradas propias del tema (> 150 ms): se rellenan con el mismo tramo del compás vecino
        #  - en el gancho, hasta la primera salida YA encajada (también la que cruza ese límite);
        #  - y en cualquier pausa de voz > 150 ms (ahí la parada se oye sola), salvo dentro de un drop-out
        first_exit = next((float(b[0]) for a, b in zip(auto, auto[1:]) if a[1] > -40 >= b[1]), N / SR)
        dbs = _music_downbeats(it)
        hook_patch, pause_patch = [], []
        if len(dbs) >= 2:
            from .music import find_gaps, patch_gaps
            bar = float(np.median(np.diff(dbs)))
            ref = d.integrated_lufs(seg)
            hook = [g for g in find_gaps(tmp, SR, 0.0, min(N / SR, first_exit + 0.4), ref) if g[0] < first_exit]
            tmp, hook_patch = patch_gaps(tmp, SR, hook, bar, ref)
            ws = sorted(words or [])
            pauses = [(e0, s1) for (s0, e0), (s1, e1) in zip(ws, ws[1:]) if s1 - e0 >= 0.15]
            # tras la última palabra no se rellena: ahí suena el final propio de la pista (un parche reiniciaría un compás)
            # en una pausa de voz la parada se oye sola desde 100 ms, y dos paradas que separa un repunte de
            # ≤ 80 ms son una (caso típico en el outro: dos caídas de 0,1 s
            # con un golpe de charles en medio que la búsqueda de > 150 ms no veía y quedaban casi en silencio)
            pmin, pbr = float(prof.get("pause_gap_min_s", 0.10)), float(prof.get("pause_gap_bridge_s", 0.08))
            cand = []
            for g0, g1 in find_gaps(tmp, SR, first_exit, N / SR, ref, min_s=pmin, bridge_s=pbr):
                in_drop = _automation_curve(auto, np.array([(g0 + g1) / 2]))[0] <= -40
                if not in_drop and any(min(g1, p1) - max(g0, p0) >= 0.1 for p0, p1 in pauses):
                    cand.append([g0, g1])
            tmp, pause_patch = patch_gaps(tmp, SR, cand, bar, ref, min_s=pmin, bridge_s=pbr)
        g = _automation_curve(auto, t)
        if it.duck or prof.get("duck_all", False):
            g = g - prof["duck_db"] * env
            if carve_sos is not None:
                carved = signal.sosfilt(carve_sos, tmp, axis=0)
                tmp = tmp * (1 - env[:, None]) + carved * env[:, None]
        tmp *= d.undb(g)[:, None]
        # calibración: nivel de la cama durante el habla = voz + bed_lu_rel_voice (+ gain_db del ítem)
        s0, s1 = max(0, pos), min(N, pos + len(seg))
        tm, lm = d.short_term(tmp, SR, 0.4, 0.1)
        inside = (tm * SR >= s0) & (tm * SR <= s1)
        act_m = act[np.clip((tm * 100).astype(int), 0, len(act) - 1)]
        use = inside & act_m & (lm > -70)
        cal = {}
        if use.sum() >= 10:
            L_m = _power_mean_lufs(lm[use])
            target = L_voice_speech + prof["bed_lu_rel_voice"]
            mode = "durante_habla"
            gain = target - L_m
            if hp_cal is not None:
                # lo que se oye en un móvil: voz y cama por encima de 300 Hz a `bed_lu_rel_voice`…
                _, lm_hp = d.short_term(signal.sosfilt(hp_cal, tmp, axis=0), SR, 0.4, 0.1)
                L_m_hp = _power_mean_lufs(lm_hp[use])
                g_hp = (L_voice_speech_hp + prof["bed_lu_rel_voice"]) - L_m_hp
                # …con tope: la banda completa no pasa de `bed_fullband_max_lu_rel_voice`
                g_cap = (L_voice_speech + prof["bed_fullband_max_lu_rel_voice"]) - L_m
                gain = min(g_hp, g_cap)
                mode = "durante_habla_>300Hz" + ("_tope_banda_completa" if g_cap < g_hp else "")
                cal = {"gain_300hz_db": round(g_hp, 2), "gain_cap_fullband_db": round(g_cap, 2),
                       "gain_fullband_ref_db": round(target - L_m, 2)}
        else:
            L_m = _power_mean_lufs(lm[inside])
            target = L_voice + prof["bed_no_voice_lu_rel_voice"]
            mode = "sin_voz"
            gain = target - L_m
        gain += it.gain_db
        bus += tmp * d.undb(gain)
        info.append({"id": it.id, "calibration": mode, "gain_db": round(gain, 2), "target_lufs": round(target, 2),
                     "duck": bool(it.duck), "automation_points": len(it.automation), "reentries_on_beat": moves,
                     "hook_until_s": round(first_exit, 3), "hook_patches": hook_patch, "pause_patches": pause_patch, **cal})
    # `tokens.music_lift` del plan ([{start, end, lu}]): sube la cama +lu en ese tramo (rampas de 0,3 s)
    lifts = []
    for x in prof.get("music_lift") or []:
        try:
            a_, b_, lu_ = float(x["start"]), float(x["end"]), float(x.get("lu", 2.0))
        except (KeyError, TypeError, ValueError):
            continue
        if b_ > a_:
            r_ = min(float(prof.get("music_lift_ramp_s", 0.3)), (b_ - a_) / 2)
            tt = np.arange(N) / SR
            up = np.clip(np.minimum((tt - (a_ - r_)) / r_, ((b_ + r_) - tt) / r_), 0.0, 1.0)
            bus *= d.undb(lu_ * up)[:, None]
            lifts.append({"start": a_, "end": b_, "lu": lu_})
    ducked = any(it.duck for it in items) or prof.get("duck_all", False)
    # cierre. Tras la última palabra (ducking ya suelto arriba) la cama sube al nivel de «música sola» con una
    # rampa corta: de −18 LU bajo la voz (−15 sin ducking) a `end_bed_lu_rel_voice` (−12 por defecto)
    end_info = None
    if end_t0 is not None and end_t0 < N / SR:
        tgt = prof.get("end_bed_lu_rel_voice")
        tgt = float(prof["bed_no_voice_lu_rel_voice"] if tgt is None else tgt)
        lift = tgt - float(prof["bed_lu_rel_voice"]) - (float(prof["duck_db"]) if ducked else 0.0)
        r_ = max(1e-3, float(prof.get("end_ramp_s", 0.08)))
        if lift > 0:
            bus *= d.undb(lift * np.clip((t_all - end_t0) / r_, 0.0, 1.0))[:, None]
        tail = bus[int(end_t0 * SR):]
        m_end = d.momentary_max(np.vstack([tail, np.zeros((SR // 2, 2))])) if len(tail) > SR // 50 else None
        # la subida teórica no cuenta con la pista (el golpe final se quedaba a −14,2 LU con objetivo −12): se mide lo que
        # llega y se corrige, con la subida total ≤ +6 dB
        lift_max = float(prof.get("end_lift_max_db", 6.0))
        if m_end is not None and np.isfinite(m_end):
            extra = min(tgt - (m_end - L_voice_speech), lift_max - max(lift, 0.0))
            if extra > 0.5:
                bus *= d.undb(extra * np.clip((t_all - end_t0) / r_, 0.0, 1.0))[:, None]
                lift = max(lift, 0.0) + extra
                tail = bus[int(end_t0 * SR):]
                m_end = d.momentary_max(np.vstack([tail, np.zeros((SR // 2, 2))]))
        end_info = {"last_word_end_s": round(last_w, 3), "from_s": round(end_t0, 3), "lift_db": round(max(lift, 0.0), 2),
                    "duck_release_s": prof.get("end_duck_release_s"), "target_lu_rel_voice": tgt,
                    "music_m_max_lu_rel_voice": None if m_end is None else round(m_end - L_voice_speech, 2)}
    report["music"] = {"items": len(items), "detail": info, "voice_speech_lufs": round(L_voice_speech, 2),
                       "lift": lifts, "end": end_info,
                       "presence": [prof.get("music_presence_hz"), prof.get("music_presence_db")],
                       "duck_db": prof["duck_db"] if ducked else "inactivo",
                       "carve_db": prof["carve_db"] if (ducked and prof["carve_db"]) else "inactivo",
                       "bus_eq": {"highpass_hz": prof.get("music_highpass_hz"),
                                  "lowshelf": [prof.get("music_lowshelf_hz"), prof.get("music_lowshelf_db")]}}
    return bus


def _chain_keys(timeline) -> dict[str, str]:
    """SFX → cadena (item de su decisión; una transición, el item que entra en su corte)."""
    items = list(getattr(timeline, "items", []) or [])
    by_dec: dict[str, list] = {}
    for it in items:
        for dd in it.decision_ids:
            by_dec.setdefault(dd, []).append(it)
    out = {}
    for a in getattr(timeline, "audio", []) or []:
        if a.kind != "sfx" or not a.decision_ids:
            continue
        its = by_dec.get(a.decision_ids[0], [])
        if not its:                                       # decisión sin item propio: el gráfico activo en ese instante
            its = [j for j in items if j.track in ("graphic", "broll") and j.t0 - 0.05 <= a.t0 <= j.t1]
        if not its:
            continue
        it = its[0]
        key = it.id
        if it.track == "transition":
            cut = float(it.cues.get("cut", (it.t0 + it.t1) / 2))
            nxt = [j for j in items if j.track in ("graphic", "broll") and abs(j.t0 - cut) <= 0.25]
            if nxt:
                key = nxt[0].id
        out[a.id] = key
    return out


def _protected_sfx(timeline, out_dir: Path) -> set[str]:
    """Ids de los AudioItems de SFX que son ACENTOS PROTEGIDOS (`acento_protegido` en `sfx_plan.json` de la versión,
    que escribe `sfxplan.align_version` junto a `audio/`), comprobando también su t0 (±5 ms) por si el fichero es de
    una compilación anterior. Sin `sfx_plan.json`: ninguno."""
    import json as _json
    p = Path(out_dir).parent / "sfx_plan.json"
    if not p.exists():
        return set()
    try:
        chosen = _json.loads(p.read_text()).get("chosen", [])
    except Exception:                                    # noqa: BLE001
        return set()
    want = {str(c["id"]): float(c.get("t0", -1.0)) for c in chosen if c.get("acento_protegido")}
    return {a.id for a in getattr(timeline, "audio", []) or []
            if a.kind == "sfx" and a.id in want and abs(float(a.t0) - want[a.id]) <= 0.005}


def _sfx_bus(items, N, prof, cache, voice, act, report, chain_keys: dict | None = None,
             protected: set[str] | None = None):
    """Bus de SFX. Devuelve (bus, prot): `prot` es la parte del bus que forman los acentos protegidos (ya incluida en
    `bus`), para que la guarda de palabra los trate aparte."""
    bus = np.zeros((N, 2), dtype=np.float64)
    prot = np.zeros((N, 2), dtype=np.float64) if protected else None
    tv, lv3 = d.short_term(voice, SR, 3.0, 0.1)
    L_voice = d.integrated_lufs(voice)
    if L_voice <= -60:                                   # sin voz: referencia = nivel de entrega
        L_voice = prof["target_lufs"]
    hp = signal.butter(2, prof["sfx_highpass_hz"], "highpass", fs=SR, output="sos")
    placed = []
    for it in sorted(items, key=lambda a: a.t0):
        entry = sfxlib.lookup(it.path)
        kind = (entry or {}).get("kind") or "pop"
        src = cache.get(it.path, 2)
        # tramo y punto de sincronía
        ms = it.media_start
        dur = it.dur
        sync = it.sync_offset
        if entry is not None:
            if dur is None and entry.get("duracion_util_ms"):
                u0, u1 = entry["duracion_util_ms"]
                if ms == 0.0:
                    ms = u0 / 1000
                dur = u1 / 1000 - ms
            if sync == 0.0:
                rec = [r for r in entry.get("recortes") or [] if r["inicio_ms"] / 1000 - 0.005 <= ms <= r["fin_ms"] / 1000]
                if rec:
                    sync = rec[0]["sync_ms"] / 1000 - ms
                else:
                    sync = max(0.0, float(entry.get("punto_sincronia_ms") or 0) / 1000 - ms)
        if dur is None:
            dur = len(src) / SR - ms
        a = int(round(ms * SR))
        seg = src[a: a + int(round(dur * SR))].astype(np.float64)
        if len(seg) == 0:
            continue
        pitch = float(getattr(it, "pitch", 0.0) or 0.0)
        if pitch:
            seg = d.pitch_shift(seg, pitch)
            sync = sync / (2 ** (pitch / 12))
        if kind != "impact":
            seg = signal.sosfilt(hp, seg, axis=0)
        seg = _fade(seg, int(max(it.fade_in, 0.002) * SR), int(max(it.fade_out, 0.015) * SR), shape="lin")
        # nivel: M máx. del tramo → voz a corto plazo alrededor de t0 + rel
        m_max = d.momentary_max(np.vstack([seg, np.zeros((SR // 2, 2))]))
        win = (tv >= it.t0 - 1.5) & (tv <= it.t0 + 1.5)
        act_w = act[np.clip((tv * 100).astype(int), 0, len(act) - 1)]
        L_loc = _power_mean_lufs(lv3[win & act_w]) if (win & act_w).any() else L_voice
        rel = prof["sfx_rel_voice_lu"].get(kind, -14.0)
        gain = (L_loc + rel + it.gain_db) - m_max
        pos = int(round((it.t0 - sync) * SR))
        t = (pos + np.arange(len(seg))) / SR
        g = gain + _automation_curve(it.automation, t)
        _add(bus, seg * d.undb(g)[:, None], pos)
        if prot is not None and it.id in protected:
            _add(prot, seg * d.undb(g)[:, None], pos)
        placed.append({"id": it.id, "file": Path(it.path).name, "catalog_id": (entry or {}).get("id"), "kind": kind,
                       "t0": round(it.t0, 3), "file_start_prog": round(pos / SR, 3), "sync_offset": round(sync, 4),
                       "media_start": round(ms, 4), "dur": round(len(seg) / SR, 3), "pitch": pitch,
                       "gain_db": round(gain, 2),
                       "rel_voice_lu": rel + it.gain_db, "voice_local_lufs": round(L_loc, 2),
                       "src_m_max": round(m_max, 2)})
    # densidad en «gestos»: sin tecleo ni click; una firma de plantilla (mismo fichero, tono ascendente, < 10 s
    # entre apariciones) cuenta como uno; dos capas en el mismo instante (impacto sub + media) cuentan como uno
    # (además: SFX suaves ≤ −18 LU no cuentan; los de una misma cadena — un componente, o la transición que entra en
    # él — a < 1,2 s cuentan uno, como en sfxplan.count_gestures)
    chain_of = chain_keys or {}
    gestures, chains = 0, {}
    last = None
    for p in placed:
        if p["kind"] in ("type", "click") or p["rel_voice_lu"] <= -18.0:
            continue
        fid = p.get("catalog_id") or p["file"]               # las copias procesadas cuentan como su original
        ch = chains.get(fid)
        if ch and p["t0"] - ch[0] <= 10.0 and p["pitch"] > ch[1]:
            chains[fid] = (p["t0"], p["pitch"])
            continue
        chains[fid] = (p["t0"], p["pitch"])
        key = chain_of.get(p["id"])
        if last is not None and (abs(p["t0"] - last[0]) < 0.05 or (key and key == last[1] and p["t0"] - last[0] < 0.6)):
            last = (p["t0"], key)
            continue
        gestures += 1
        last = (p["t0"], key)
    # con la norma «cada animación» las entradas (≤ −14 LU) no gastan presupuesto: la puerta mira los acentos
    acc, last2 = 0, None
    for p in placed:
        if p["kind"] in ("type", "click") or p["rel_voice_lu"] <= -14.0:
            continue
        key = chain_of.get(p["id"])
        if last2 is not None and (abs(p["t0"] - last2[0]) < 0.05 or (key and key == last2[1] and p["t0"] - last2[0] < 0.6)):
            last2 = (p["t0"], key)
            continue
        acc += 1
        last2 = (p["t0"], key)
    dur_min = N / SR / 60
    # la puerta cuenta GESTOS, igual que sfxplan y la QA: un sonido con sus capas y su escalera. Con los ids
    # de sfxplan («sfx_07», «sfx_07.c1», «sfx_07.e2») por el prefijo; con ids antiguos, por t0 (±5 ms)
    if any("." in p["id"] for p in placed):
        n_sounds = len({p["id"].split(".")[0] for p in placed})
    else:
        n_sounds, last_t = 0, None
        for p in sorted(placed, key=lambda p: p["t0"]):
            if last_t is None or p["t0"] - last_t >= 0.005:
                n_sounds += 1
            last_t = p["t0"]
    report["sfx"] = {"items": len(placed), "gestures": gestures, "accent_gestures": acc, "sounds": n_sounds,
                     "per_min": round(n_sounds / dur_min, 2) if dur_min else 0,
                     "files_per_min": round(len(placed) / dur_min, 2) if dur_min else 0,
                     "accent_per_min": round(acc / dur_min, 2) if dur_min else 0,
                     "gestures_total_per_min": round(gestures / dur_min, 2) if dur_min else 0, "placed": placed,
                     "acentos_protegidos": sorted(protected or [])}
    return bus, prot


def _db_x(own: float, room: float, cap: float) -> float:
    """dB que hay que bajar `own` para que quepa en `room` (energías), como mucho `cap`."""
    if own <= 0:
        return 0.0
    return cap if room <= 0 else min(cap, max(0.0, 10 * np.log10(own / room)))


def _word_mask_guard(sfx, music, voice_st, word_times, prof, report, prot=None):
    """Guarda voz − fondo por PALABRA en 1–4 kHz (la QA `audio.vmr_word` mide en esa banda):
    donde una palabra queda a menos de `word_guard_db` (6 + 2 dB de margen) del fondo en esa banda, baja lo justo el bus
    que más tapa (SFX o cama, como mucho `word_guard_max_db` y `word_guard_music_max_db`) durante esa palabra, con
    rampas de 15 ms sin retraso. El ataque del SFX, que cae en el hueco antes de la palabra, no se toca.
    Sin esta protección, un acento sobre una palabra bajaba −9,9 dB en banda completa y quedaba a −19,9 LU, con el ataque
    a −24,9 dBFS en vez de −15,0. `prot` = la parte del bus de SFX que son ACENTOS PROTEGIDOS
    (`sfxplan._is_protected_accent`). Primero baja el resto de SFX; si no basta, al acento solo se le recorta la banda
    1–4 kHz (la que tapa la palabra) como mucho `word_guard_max_db`, sin perder más de `word_guard_protect_max_db` (4 dB)
    de energía total, y desde 10 ms antes de la palabra (no 30: el ataque queda entero); si aun así falta, baja la cama
    (como mucho `word_guard_music_max_db`). Sin acentos protegidos, todo queda como antes.
    Devuelve (sfx, music)."""
    if not word_times:
        report["sfx_word_guard"] = {"palabras": 0}
        return sfx, music
    bp = signal.butter(4, [1000, 4000], "bandpass", fs=SR, output="sos")
    hop = int(0.01 * SR)
    nf = len(sfx) // hop
    has_prot = prot is not None and bool(np.any(prot))

    def be(x):
        y = signal.sosfiltfilt(bp, x[: nf * hop].mean(axis=1) if x.ndim == 2 else x[: nf * hop])
        return np.mean(y.reshape(nf, hop) ** 2, axis=1)

    def fe(x):                                           # energía en banda completa por trama de 10 ms
        y = x[: nf * hop].mean(axis=1) if x.ndim == 2 else x[: nf * hop]
        return np.mean(y.reshape(nf, hop) ** 2, axis=1)
    rest = sfx - prot if has_prot else sfx
    ve, se, me = be(voice_st), be(rest), be(music)
    pe, pfull = (be(prot), fe(prot)) if has_prot else (np.zeros(nf), np.zeros(nf))
    target = float(prof.get("word_guard_db", 8.0))
    caps = {"sfx": float(prof.get("word_guard_max_db", 10.0)), "music": float(prof.get("word_guard_music_max_db", 6.0))}
    prot_max = float(prof.get("word_guard_protect_max_db", 4.0))
    gains = {"sfx": np.zeros(nf), "music": np.zeros(nf), "prot_band": np.zeros(nf)}   # dB por trama de 10 ms (≤ 0)
    hits = []
    for s0, e0 in sorted(tuple(v) for v in word_times.values()):
        f0, f1 = int(s0 * 100), int(max(e0, s0 + 0.12) * 100)
        if f1 <= f0 or f1 > nf:
            continue
        seg = ve[f0:f1]
        act = (seg > seg.max() * 10 ** (-1.5)) & (seg > 1e-9)
        if act.sum() < 3:
            continue
        v, sb, mb = seg[act].sum(), se[f0:f1][act].sum(), me[f0:f1][act].sum()
        pb = pe[f0:f1][act].sum()
        if sb + pb + mb <= 0 or 10 * np.log10(v / (sb + pb + mb + 1e-18)) >= target:
            continue
        room = v / 10 ** (target / 10)                   # energía de fondo que cabe en la banda
        if pb < 0.05 * (sb + pb + mb):                   # sin acento protegido (o despreciable): como siempre
            bus, own, other = ("sfx", sb, mb) if sb >= mb else ("music", mb, sb)
            x = _db_x(own, room - other - pb, caps[bus])
            if x > 0.1:
                g = gains[bus]
                g[max(0, f0 - 3): f1 + 3] = np.minimum(g[max(0, f0 - 3): f1 + 3], -x)
                hits.append({"t0": round(s0, 2), "t1": round(e0, 2), "bus": bus, "db": round(-x, 1)})
            continue
        if mb > sb + pb:                                 # la cama es la que tapa: como siempre (el acento no se toca)
            x = _db_x(mb, room - sb - pb, caps["music"])
            if x > 0.1:
                g = gains["music"]
                g[max(0, f0 - 3): f1 + 3] = np.minimum(g[max(0, f0 - 3): f1 + 3], -x)
                hits.append({"t0": round(s0, 2), "t1": round(e0, 2), "bus": "music", "db": round(-x, 1)})
            continue
        hit = {"t0": round(s0, 2), "t1": round(e0, 2), "bus": "sfx+acento"}
        xs = _db_x(sb, room - pb - mb, caps["sfx"])      # 1) el resto de SFX
        sb2 = sb * 10 ** (-xs / 10)
        # 2) el acento: solo su banda 1–4 kHz, sin perder más de `prot_max` dB de energía total en la palabra
        frac = min(1.0, pb / max(pfull[f0:f1][act].sum(), 1e-18))
        floor_g = (10 ** (-prot_max / 10) - (1 - frac)) / frac if frac > 0 else 0.0
        cap_p = caps["sfx"] if floor_g <= 0 else min(caps["sfx"], -10 * np.log10(min(1.0, floor_g)))
        xp = _db_x(pb, room - sb2 - mb, cap_p)
        pb2 = pb * 10 ** (-xp / 10)
        xm = _db_x(mb, room - sb2 - pb2, caps["music"]) if mb > 0 else 0.0     # 3) la cama, si aún falta
        for key, x, a in (("sfx", xs, 3), ("prot_band", xp, 0), ("music", xm, 3)):
            if x > 0.1:
                g = gains[key]
                g[max(0, f0 - a): f1 + 3] = np.minimum(g[max(0, f0 - a): f1 + 3], -x)
        hit.update({"db": round(-xs, 1), "acento_banda_db": round(-xp, 1), "acento_total_db": round(
            10 * np.log10(max(1e-12, 1 - frac + frac * 10 ** (-xp / 10))), 1), "cama_db": round(-xm, 1),
            "voz_fondo_db": round(10 * np.log10(v / (sb2 + pb2 + mb * 10 ** (-xm / 10) + 1e-18)), 1)})
        if xs > 0.1 or xp > 0.1 or xm > 0.1:
            hits.append(hit)
    k = 1 - math.exp(-1 / (0.015 * 100))                # rampas de ~15 ms, sin retraso (ida y vuelta)

    def smooth(gain):
        g = ndimage.minimum_filter1d(gain, size=3)
        sm = np.empty_like(g)
        acc = 0.0
        for i, v in enumerate(g):
            acc += (v - acc) * k
            sm[i] = acc
        acc = 0.0
        for i in range(len(sm) - 1, -1, -1):
            acc += (g[i] - acc) * k
            sm[i] = min(sm[i], acc)
        return sm
    out = {"sfx": rest, "music": music}
    for bus in ("sfx", "music"):
        if np.any(gains[bus]):
            curve = np.interp(np.arange(len(out[bus])) / SR, np.arange(nf) / 100.0, smooth(gains[bus]))
            out[bus] = out[bus] * d.undb(curve)[:, None]
    if has_prot:
        p_out = prot
        if np.any(gains["prot_band"]):
            # recorte SOLO de la banda 1–4 kHz: banda (fase cero) × curva + resto (complementario exacto)
            band = signal.sosfiltfilt(bp, prot, axis=0)
            curve = np.interp(np.arange(len(prot)) / SR, np.arange(nf) / 100.0, smooth(gains["prot_band"]))
            p_out = (prot - band) + band * d.undb(curve)[:, None]
        out["sfx"] = out["sfx"] + p_out
    report["sfx_word_guard"] = {"palabras": len(hits), "detalle": hits[:40]}
    return out["sfx"], out["music"]


# ───────────────────────────── API ─────────────────────────────
def render(timeline, out_dir: str | Path, profile: dict | None = None) -> dict:
    """Mezcla la timeline y escribe `mix.wav` + stems. Devuelve métricas (LUFS, TP, LRA, voz/música) y detalle."""
    prof = {**PROFILE, **((timeline.style or {}).get("audio") or {}), **(profile or {})}
    if "music_lift" not in prof:                         # tramos de cama más alta, de `tokens` del plan
        try:
            from cutkit.compile import load_plan
            prof["music_lift"] = (load_plan(timeline.slug, timeline.version).tokens or {}).get("music_lift") or []
        except Exception:                                # noqa: BLE001 — sin plan (banco de pruebas): sin tramos
            prof["music_lift"] = []
    out_dir = Path(out_dir)
    (out_dir / "stems").mkdir(parents=True, exist_ok=True)
    dur = timeline.duration or max((a.t0 + (a.dur or 0)) for a in timeline.audio)
    N = int(math.ceil(dur * SR))
    cache = _Cache()
    report: dict = {"profile": prof, "duration_s": round(dur, 3), "sample_rate": SR}
    by = {k: [a for a in timeline.audio if a.kind == k] for k in ("voice", "music", "sfx")}

    voice, _ = _voice_bus(by["voice"], N, prof, cache, report, words_src=_source_words(getattr(timeline, "slug", None)))
    act = _activity(voice, timeline.word_times, N, prof)
    voice_st = np.repeat(voice[:, None], 2, axis=1)      # centrada: L = R (así se mide y así suena)
    music = _music_bus(by["music"], N, prof, cache, voice_st, act, report,
                       words=[tuple(v) for v in (timeline.word_times or {}).values()])
    sfx, prot = _sfx_bus(by["sfx"], N, prof, cache, voice_st, act, report, chain_keys=_chain_keys(timeline),
                         protected=_protected_sfx(timeline, out_dir))
    if prof.get("word_guard", True):                     # voz − fondo ≥ 6 dB por palabra en 1–4 kHz
        sfx, music = _word_mask_guard(sfx, music, voice_st, timeline.word_times, prof, report, prot=prot)
    premix = voice_st + music + sfx

    # máster: ganancia estática + limitador de true peak, iterando hasta ±0,1 LU del objetivo
    L0 = d.integrated_lufs(premix)
    g = prof["target_lufs"] - L0
    ceiling = prof["tp_dbtp"] - 0.1
    for it_n in range(6):
        y, lim = tp_limiter(premix * d.undb(g), ceiling, prof["limiter_lookahead_s"], prof["limiter_release_s"])
        L = d.integrated_lufs(y)
        tp = d.true_peak_db(y)
        if tp > prof["tp_dbtp"]:
            ceiling -= (tp - prof["tp_dbtp"]) + 0.05
            continue
        if abs(L - prof["target_lufs"]) <= 0.1:
            break
        g += prof["target_lufs"] - L
    nf = min(int(prof.get("master_fade_out_s", 0.15) * SR), len(y))      # el vídeo acaba en silencio (−∞), sin corte
    if nf > 0:
        y = y.copy()
        y[-nf:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, nf)))[:, None].astype(np.float32)
    master = {"premix_lufs": round(L0, 2), "static_gain_db": round(g, 2), "ceiling_dbtp": round(ceiling, 2),
              "iterations": it_n + 1, "fade_out_s": prof.get("master_fade_out_s", 0.15), **lim}
    mix_p = d.write(out_dir / "mix.wav", y)
    stems = {}
    for name, x in (("voice", voice_st), ("music", music), ("sfx", sfx)):
        stems[name] = str(d.write(out_dir / "stems" / f"{name}.wav", x * d.undb(g)))

    # medidas finales
    ebu = d.ebur128(mix_p)
    tv, lv = d.short_term(voice_st * d.undb(g), SR, 0.4, 0.1)
    _, lm = d.short_term(music * d.undb(g), SR, 0.4, 0.1)
    act_w = act[np.clip((tv * 100).astype(int), 0, len(act) - 1)]
    ok = act_w & (lm > -70) & (lv > -70)
    v_over_m = float(np.median(lv[ok] - lm[ok])) if ok.any() else None
    Lv, Lm = d.integrated_lufs(voice_st * d.undb(g)), d.integrated_lufs(music * d.undb(g))
    v_over_m_hp = None
    if by["music"] and prof.get("calib_highpass_hz"):
        hp = signal.butter(4, prof["calib_highpass_hz"], "highpass", fs=SR, output="sos")
        _, lvh = d.short_term(signal.sosfilt(hp, voice_st, axis=0), SR, 0.4, 0.1)
        _, lmh = d.short_term(signal.sosfilt(hp, music, axis=0), SR, 0.4, 0.1)
        okh = act_w & (lmh > -70) & (lvh > -70)
        v_over_m_hp = round(float(np.median(lvh[okh] - lmh[okh])), 2) if okh.any() else None
    metrics = {
        "integrated_lufs_ebur128": ebu["I"], "lra_lu": ebu["LRA"], "true_peak_dbtp_ebur128": ebu["TP"],
        "integrated_lufs_pyloudnorm": round(d.integrated_lufs(y), 2), "true_peak_dbtp_x4": round(d.true_peak_db(y), 2),
        "voice_lufs": round(Lv, 2), "music_lufs": round(Lm, 2) if by["music"] else None,
        "music_rel_voice_lu": round(Lm - Lv, 2) if by["music"] else None,
        "voice_over_music_during_speech_db": None if v_over_m is None else round(v_over_m, 2),
        "voice_over_music_300hz_db": v_over_m_hp,
        "sfx_per_min": report["sfx"]["per_min"],                       # GESTOS/min (sonido + capas = 1), como la QA
        "sfx_gestures_total_per_min": report["sfx"]["gestures_total_per_min"],   # todo lo que suena (entradas incl.)
    }
    tail_cut, fit_ = None, {}
    for it in by["music"]:
        sc = Path(it.path).with_suffix(".json")
        if sc.exists():
            import json as _json
            try:
                fit_ = _json.loads(sc.read_text()).get("fit", {}) or {}
                tail_cut = fit_.get("tail_cut_s")
            except Exception:                            # noqa: BLE001
                pass
    metrics["music_tail_cut_s"] = tail_cut
    # como la QA `audio.music_tail_cut`, no es corte en seco si el golpe final cae tras la última palabra, suena
    # ≥ 1 s después y la cola se funde en ≥ 0,5 s (FIT_VERSION 14)
    last_w_ = max((float(e) for _, e in (timeline.word_times or {}).values()), default=None)
    tail_faded = bool(tail_cut is not None and fit_.get("end_at") is not None and last_w_ is not None
                      and float(fit_.get("tail_fade_s") or 0.0) >= 0.5 - 1e-3 and float(fit_["end_at"]) >= last_w_ - 0.02
                      and dur - float(fit_["end_at"]) >= 1.0 - 1e-3)
    metrics["music_tail_faded"] = tail_faded
    checks = {
        "integrated_lufs": {"value": metrics["integrated_lufs_ebur128"], "target": prof["target_lufs"], "tol": 0.5,
                            "ok": metrics["integrated_lufs_ebur128"] is not None
                            and abs(metrics["integrated_lufs_ebur128"] - prof["target_lufs"]) <= 0.5},
        "true_peak_dbtp": {"value": metrics["true_peak_dbtp_ebur128"], "max": prof["tp_dbtp"],
                           "ok": metrics["true_peak_dbtp_ebur128"] is not None
                           and metrics["true_peak_dbtp_ebur128"] <= prof["tp_dbtp"] + 0.05},
        # lo que oye un móvil: voz − cama por encima de 300 Hz durante el habla (la banda completa queda como dato)
        "voice_over_music_db": {"value": v_over_m_hp if v_over_m_hp is not None else metrics["voice_over_music_during_speech_db"],
                                "min": 15.0, "band": ">300 Hz" if v_over_m_hp is not None else "completa",
                                "ok": (v_over_m_hp if v_over_m_hp is not None else (v_over_m if v_over_m is not None else 99)) >= 15.0},
        "lra_lu": {"value": metrics["lra_lu"], "max": 4.0 if prof["format"] != "long" else 8.0,
                   "ok": metrics["lra_lu"] is not None and metrics["lra_lu"] <= (4.0 if prof["format"] != "long" else 8.0)},
        "music_tail_cut_s": {"value": tail_cut, "max": 0.3, "fundido": tail_faded,
                             "ok": tail_cut is None or tail_cut <= 0.3 or tail_faded},
        "sfx_per_min": {"value": metrics["sfx_per_min"], "max": prof["sfx_max_per_min"] if prof["format"] != "long" else 3.0,
                        "ok": metrics["sfx_per_min"] <= (prof["sfx_max_per_min"] if prof["format"] != "long" else 3.0)},
    }
    out = {"mix": str(mix_p), "stems": stems, "lufs": metrics["integrated_lufs_ebur128"],
           "tp": metrics["true_peak_dbtp_ebur128"], "lra": metrics["lra_lu"], "metrics": metrics, "checks": checks,
           "master": master, **{k: report[k] for k in ("voice", "music", "sfx")},
           "sfx_word_guard": report.get("sfx_word_guard"),
           "profile": prof, "duration_s": report["duration_s"]}
    (out_dir / "mix_report.json").write_text(d.to_json(out))
    return out
