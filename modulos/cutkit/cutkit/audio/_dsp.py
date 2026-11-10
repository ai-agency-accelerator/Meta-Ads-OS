"""Utilidades de audio compartidas por voice/music/sfx/mix: E/S con ffmpeg, medida BS.1770 y análisis.

Todo trabaja en float32/float64 a 48 kHz con forma (muestras, canales). Las medidas siguen este criterio:
suelo = p5 del RMS en 50 ms, SNR = mediana del habla − suelo, LTAS por bandas
normalizado a 60 Hz–8 kHz, sibilancia = 5–9 kHz frente a 0,3–3 kHz (p95), cresta en el habla.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import numpy as np
import pyloudnorm as pyln
import soundfile as sf
from scipy import signal

SR = 48000

# Perfil tonal orientativo: mediana de 7 voces de referencia. Solo orientación de estilo: si el usuario da
# una voz de referencia propia, manda la suya.
LTAS_BANDS = [("60-125", 60, 125), ("125-250", 125, 250), ("250-500", 250, 500), ("500-1k", 500, 1000),
              ("1k-2k", 1000, 2000), ("2k-4k", 2000, 4000), ("4k-8k", 4000, 8000)]
_LTAS_REF_INVESTIGACION = {"60-125": -21.0, "125-250": -8.6, "250-500": -3.8, "500-1k": -5.1,
                           "1k-2k": -11.1, "2k-4k": -13.2, "4k-8k": -19.6}
# Calibración de método: la investigación midió una toma bruta con su propio script; este módulo mide el mismo fichero
# con otra máscara de habla y otra STFT. Desfase (este − investigación) por banda:
_DESFASE_METODO = {"60-125": 2.8, "125-250": 0.2, "250-500": 0.1, "500-1k": -0.7, "1k-2k": -1.5,
                   "2k-4k": 0.2, "4k-8k": 0.7}
LTAS_REFERENCIA = {k: round(v + _DESFASE_METODO[k], 1) for k, v in _LTAS_REF_INVESTIGACION.items()}
SIBILANCIA_REFERENCIA = 1.6 + 2.4      # 1,6 dB en la investigación; la toma bruta da 1,7 allí y 4,1 aquí


# ───────────────────────────── E/S ─────────────────────────────
def load(path: str | Path, channels: int = 1, sr: int = SR, start: float | None = None,
         dur: float | None = None) -> np.ndarray:
    """Decodifica cualquier fichero (wav/mp3/mp4…) con ffmpeg a float32 (n, channels) a `sr`."""
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin"]
    if start:
        cmd += ["-ss", f"{max(0.0, start):.6f}"]
    cmd += ["-i", str(path)]
    if dur is not None:
        cmd += ["-t", f"{max(0.0, dur):.6f}"]
    cmd += ["-vn", "-ac", str(channels), "-ar", str(sr), "-f", "f32le", "-acodec", "pcm_f32le", "-"]
    out = subprocess.run(cmd, capture_output=True, check=True).stdout
    x = np.frombuffer(out, dtype=np.float32).reshape(-1, channels)
    return x.copy()


def write(path: str | Path, x: np.ndarray, sr: int = SR, subtype: str = "PCM_24") -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), np.asarray(x, dtype=np.float32), sr, subtype=subtype)
    return path


def ffmpeg_filter(src: str | Path, dst: str | Path, af: str, channels: int = 1, sr: int = SR) -> Path:
    """Aplica una cadena -af de ffmpeg y escribe WAV de 24 bits."""
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y", "-i", str(src), "-vn",
           "-af", af, "-ac", str(channels), "-ar", str(sr), "-c:a", "pcm_s24le", str(dst)]
    subprocess.run(cmd, check=True, capture_output=True)
    return dst


# ───────────────────────────── loudness ─────────────────────────────
def db(x, floor: float = 1e-12):
    return 20.0 * np.log10(np.maximum(np.abs(x), floor))


def undb(g):
    return 10.0 ** (np.asarray(g) / 20.0)


def _as2d(x: np.ndarray) -> np.ndarray:
    return x[:, None] if x.ndim == 1 else x


def integrated_lufs(x: np.ndarray, sr: int = SR) -> float:
    """Loudness integrada BS.1770 (pyloudnorm). Rellena con ceros si dura < 0,4 s."""
    x = _as2d(x).astype(np.float64)
    if len(x) < int(0.45 * sr):
        x = np.vstack([x, np.zeros((int(0.45 * sr) - len(x), x.shape[1]))])
    v = pyln.Meter(sr).integrated_loudness(x)
    return float(v) if np.isfinite(v) else -70.0


def kweight(x: np.ndarray, sr: int = SR) -> np.ndarray:
    """Filtro K (estante agudo + paso alto RLB) de BS.1770, por canal."""
    x = _as2d(x).astype(np.float64)
    m = pyln.Meter(sr)
    y = x.copy()
    for f in m._filters.values():                      # high_shelf → high_pass (orden de pyloudnorm)
        y = signal.lfilter(f.b, f.a, y, axis=0)
    return y


def short_term(x: np.ndarray, sr: int = SR, win: float = 0.4, hop: float = 0.1) -> tuple[np.ndarray, np.ndarray]:
    """Loudness K-ponderada en ventanas deslizantes (0,4 s = momentánea; 3 s = corto plazo).

    Devuelve (tiempos del centro de cada ventana, LUFS). Vectorizado con suma acumulada.
    """
    y = kweight(x, sr)
    p = (y ** 2).sum(axis=1)                           # canales con peso 1 (L/R/mono)
    n, h = int(win * sr), int(hop * sr)
    if len(p) < n:
        p = np.concatenate([p, np.zeros(n - len(p))])
    c = np.concatenate([[0.0], np.cumsum(p)])
    starts = np.arange(0, len(p) - n + 1, h)
    ms = (c[starts + n] - c[starts]) / n
    lufs = -0.691 + 10 * np.log10(np.maximum(ms, 1e-12))
    return (starts + n / 2) / sr, lufs


def momentary_max(x: np.ndarray, sr: int = SR) -> float:
    """Máximo de loudness momentánea (400 ms): la referencia para calibrar SFX."""
    return float(np.max(short_term(x, sr, 0.4, 0.01)[1]))


def ebur128(path: str | Path) -> dict:
    """Mide con `ffmpeg ebur128=peak=true` (I, LRA, TP y máximos M/S). Es la medida de verdad del máster."""
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-nostdin", "-i", str(path), "-vn",
           "-af", "ebur128=peak=true:framelog=info", "-f", "null", "-"]
    err = subprocess.run(cmd, capture_output=True, text=True).stderr
    out: dict = {}
    summ = err[err.rfind("Summary:"):]
    for key, pat in {"I": r"I:\s+(-?[\d.]+|-inf) LUFS", "LRA": r"LRA:\s+(-?[\d.]+) LU",
                     "TP": r"Peak:\s+(-?[\d.]+|-inf) dBFS"}.items():
        mm = re.search(pat, summ)
        out[key] = float(mm.group(1)) if mm and mm.group(1) != "-inf" else None
    ms = [float(v) for v in re.findall(r"M:\s*(-?[\d.]+)", err[:err.rfind("Summary:")]) if v not in ("-inf",)]
    ss = [float(v) for v in re.findall(r"S:\s*(-?[\d.]+)", err[:err.rfind("Summary:")])]
    out["M_max"] = max(ms) if ms else None
    out["S_max"] = max(ss) if ss else None
    return out


def true_peak_db(x: np.ndarray, oversample: int = 4) -> float:
    x = _as2d(x)
    up = signal.resample_poly(x, oversample, 1, axis=0)
    return float(db(np.max(np.abs(up))))


# ───────────────────────────── análisis de voz ─────────────────────────────
def frame_rms_db(x: np.ndarray, sr: int = SR, win: float = 0.05, hop: float = 0.025) -> tuple[np.ndarray, np.ndarray]:
    m = _as2d(x).mean(axis=1).astype(np.float64)
    n, h = int(win * sr), int(hop * sr)
    if len(m) < n:
        m = np.concatenate([m, np.zeros(n - len(m))])
    c = np.concatenate([[0.0], np.cumsum(m ** 2)])
    st = np.arange(0, len(m) - n + 1, h)
    rms = np.sqrt(np.maximum((c[st + n] - c[st]) / n, 1e-14))
    return (st + n / 2) / sr, 20 * np.log10(rms)


def speech_mask(rms_db: np.ndarray, floor_db: float) -> np.ndarray:
    """Tramas con habla: por encima de máx(suelo + 12 dB, p95 − 30 dB). Sencillo y estable para voz de estudio."""
    thr = max(floor_db + 12.0, np.percentile(rms_db, 95) - 30.0)
    return rms_db > thr


def stft_db(x: np.ndarray, sr: int = SR, nfft: int = 2048, hop: int = 480):
    m = _as2d(x).mean(axis=1)
    f, t, Z = signal.stft(m, fs=sr, nperseg=nfft, noverlap=nfft - hop, boundary=None, padded=False)
    return f, t, (np.abs(Z) ** 2)


def voice_metrics(x: np.ndarray, sr: int = SR) -> dict:
    """Métricas de la voz (mono): loudness, LRA aprox., suelo, SNR, tipo de ruido, zumbido, LTAS, sibilancia,
    cresta, dispersión por frase y mejor tramo de room tone."""
    x = _as2d(x).mean(axis=1).astype(np.float64)
    t, r = frame_rms_db(x, sr)
    floor = float(np.percentile(r, 5))
    sp = speech_mask(r, floor)
    speech_med = float(np.median(r[sp])) if sp.any() else float(np.median(r))
    snr = speech_med - floor

    f, tt, P = stft_db(x, sr)
    # tramas STFT con habla (interpolando la máscara de 25 ms)
    sp_stft = np.interp(tt, t, sp.astype(float)) > 0.5
    quiet_stft = np.interp(tt, t, (r < floor + 6).astype(float)) > 0.5

    def band(lo, hi, cols):
        sel = (f >= lo) & (f < hi)
        return P[sel][:, cols].sum(axis=0)

    tot = band(60, 8000, sp_stft).sum() + 1e-20
    ltas = {name: round(float(10 * np.log10(band(lo, hi, sp_stft).sum() / tot + 1e-20)), 1)
            for name, lo, hi in LTAS_BANDS}

    sib = 10 * np.log10((band(5000, 9000, sp_stft) + 1e-20) / (band(300, 3000, sp_stft) + 1e-20))
    sib_p95 = float(np.percentile(sib, 95)) if sib.size else -40.0

    # tipo de ruido: dispersión temporal por banda en las tramas tranquilas (dB). <4 dB = estacionario
    noise_type, hum = "desconocido", []
    if quiet_stft.sum() >= 8:
        Q = 10 * np.log10(P[:, quiet_stft] + 1e-20)
        bands_idx = [(f >= lo) & (f < hi) for lo, hi in [(100, 300), (300, 1000), (1000, 3000), (3000, 8000)]]
        disp = float(np.mean([Q[b].mean(axis=0).std() for b in bands_idx]))
        noise_type = "estacionario" if disp < 4.0 else "no_estacionario"
        # zumbido: pico en 50·k Hz ≥ 10 dB sobre las bandas vecinas (red española a 50 Hz)
        qmask = np.repeat(r < floor + 6, int(0.025 * sr))[: len(x)]
        xq = x[: len(qmask)][qmask]
        if len(xq) < sr:
            xq = x
        _, Ph = signal.welch(xq, fs=sr, nperseg=sr)  # resolución de 1 Hz
        Ph_db = 10 * np.log10(Ph + 1e-20)
        for k in range(1, 6):
            h0 = 50 * k
            i0 = int(round(h0))
            neigh = np.r_[Ph_db[i0 - 12:i0 - 4], Ph_db[i0 + 4:i0 + 12]]
            if Ph_db[i0 - 1:i0 + 2].max() - np.median(neigh) >= 10:
                hum.append(h0)
    else:
        disp = None

    # cresta del habla (pico / RMS)
    spx = np.repeat(sp, int(0.025 * sr))[: len(x)]
    seg = x[: len(spx)][spx] if spx.any() else x
    crest = float(db(np.max(np.abs(seg))) - db(np.sqrt(np.mean(seg ** 2))))

    # dispersión por frase: p95 − p10 de la loudness de 400 ms en el habla
    ts, ls = short_term(x, sr, 0.4, 0.1)
    lsp = ls[np.interp(ts, t, sp.astype(float)) > 0.5]
    spread = float(np.percentile(lsp, 95) - np.percentile(lsp, 10)) if lsp.size > 5 else 0.0

    # room tone: el tramo de 1,5 s más tranquilo y estable
    room = best_room_tone(x, sr)

    ebu = _lra_from_short_term(x, sr)
    return {
        "integrated_lufs": round(integrated_lufs(x, sr), 2),
        "lra_lu": ebu,
        "peak_dbfs": round(float(db(np.max(np.abs(x)))), 2),
        "noise_floor_dbfs": round(floor, 1),
        "speech_rms_dbfs": round(speech_med, 1),
        "snr_db": round(snr, 1),
        "noise_type": noise_type,
        "noise_dispersion_db": None if disp is None else round(disp, 1),
        "hum_hz": hum,
        "ltas_rel_db": ltas,
        "sibilance_p95_db": round(sib_p95, 1),
        "crest_db": round(crest, 1),
        "phrase_spread_db": round(spread, 1),
        "speech_ratio": round(float(sp.mean()), 3),
        "room_tone": room,
    }


def _lra_from_short_term(x: np.ndarray, sr: int = SR) -> float:
    """LRA según EBU Tech 3342 (corto plazo 3 s, puerta absoluta −70 y relativa −20, p10–p95)."""
    _, s = short_term(x, sr, 3.0, 0.1)
    s = s[s > -70]
    if s.size < 3:
        return 0.0
    rel = 10 * np.log10(np.mean(10 ** (s / 10))) - 20
    s = s[s > rel]
    return round(float(np.percentile(s, 95) - np.percentile(s, 10)), 1)


def best_room_tone(x: np.ndarray, sr: int = SR, lengths=(1.5, 1.0, 0.6, 0.35)) -> dict:
    """Busca el tramo más tranquilo y estable para el room tone, del más largo al más corto: vale el primero
    cuyo nivel queda a ≤ 6 dB del suelo (p5). En Shorts con habla casi continua suele ser de 0,3–0,6 s."""
    t, r = frame_rms_db(x, sr, 0.05, 0.025)
    floor = float(np.percentile(r, 5))
    best = None
    for length in lengths:
        k = max(2, int(length / 0.025))
        if len(r) <= k:
            continue
        c1 = np.concatenate([[0], np.cumsum(r)])
        c2 = np.concatenate([[0], np.cumsum(r ** 2)])
        mu = (c1[k:] - c1[:-k]) / k
        sd = np.sqrt(np.maximum((c2[k:] - c2[:-k]) / k - mu ** 2, 0))
        i = int(np.argmin(mu + 2 * sd))
        s = max(0.0, float(t[i] - 0.025))
        cand = {"src_in": round(s, 3), "src_out": round(s + length, 3), "level_dbfs": round(float(mu[i]), 1),
                "length_s": length}
        if best is None or cand["level_dbfs"] < best["level_dbfs"]:
            best = cand
        if mu[i] <= floor + 6:
            return cand
    return best or {"src_in": 0.0, "src_out": min(len(x) / sr, 0.3), "level_dbfs": floor, "length_s": 0.3}


ROOM_LENGTHS = (1.5, 1.0, 0.6, 0.35, 0.2)           # ventanas reales que se prueban, de la más larga a la más corta
#                                                     (< 0,2 s, el bucle con fundidos ya se notaría: mejor sintético)


def room_tone(x: np.ndarray, sr: int = SR, words: list[tuple[float, float]] | None = None, length: float = 0.6,
              peak_max_dbfs: float = -45.0, margin_s: float = 0.15, seed: int = 7,
              energy_margin_s: float = 0.05) -> tuple[np.ndarray, dict]:
    """Ruido de sala LIMPIO de una voz para rellenar huecos (CTA congelada, respiraciones).

    1) Ventana REAL (la más larga posible: `length` y luego ROOM_LENGTHS hasta 0,2 s; quien la usa la repite con
       fundidos) con pico < `peak_max_dbfs`, ≥ `margin_s` de cualquier palabra (`words`, segundos de la fuente) y
       ≥ `energy_margin_s` de cualquier trama con habla o respiración (RMS > suelo + 12 dB, por si el ASR no ve
       chasquidos, colas ni inspiraciones). Antes solo se probaba `length` (3 s desde `mix`) con 0,15 s de
       margen también para la energía, así que en las tomas con silencios recortados siempre salía sintético.
    2) Si no hay ninguna (lo normal en una voz comprimida): ruido SINTÉTICO con el espectro medido del suelo de esa
       voz (Welch sobre las tramas tranquilas lejos de palabras) y su nivel RMS; determinista (`seed`).
    Devuelve (señal mono, info): la real mide lo que mida su ventana; la sintética, `length` s."""
    m = x if x.ndim == 1 else x.mean(axis=1)
    m = m.astype(np.float64)
    n = int(length * sr)
    t, r = frame_rms_db(m, sr, 0.05, 0.01)
    floor = float(np.percentile(r, 5))
    busy_e = r > floor + 12                                  # habla, chasquidos, colas e inspiraciones audibles
    busy_w = np.zeros(len(t), bool)
    if words:
        for s_, e_ in words:
            busy_w[(t >= s_ - 0.03) & (t <= e_ + 0.03)] = True
    ke, kw = int(round(energy_margin_s / 0.01)), int(round(margin_s / 0.01))
    busy = (np.convolve(busy_e.astype(float), np.ones(2 * ke + 1), mode="same") > 0) \
        | (np.convolve(busy_w.astype(float), np.ones(2 * kw + 1), mode="same") > 0)      # margen a cada lado
    free = ~busy
    # 1) ventana real: la más larga que exista; entre las de esa longitud, la más tranquila
    c = np.concatenate([[0], np.cumsum(free.astype(int))])
    for L in [length] + [v for v in ROOM_LENGTHS if v < length]:
        w, nL = max(1, int(round(L / 0.01))), int(L * sr)
        if free.sum() < w:
            continue
        best = None
        for i in np.where(c[w:] - c[:-w] == w)[0]:
            a = int(max(0.0, t[i] - 0.025) * sr)
            seg = m[a: a + nL]
            if len(seg) < nL:
                continue
            pk = float(db(np.max(np.abs(seg))))
            if pk < peak_max_dbfs:
                lvl = float(db(np.sqrt(np.mean(seg ** 2))))
                if best is None or lvl < best[0]:
                    best = (lvl, a, pk)
        if best is not None:
            lvl, a, pk = best
            return m[a: a + nL].copy(), {"mode": "real", "src_in": round(a / sr, 3), "src_out": round((a + nL) / sr, 3),
                                         "length_s": L, "level_dbfs": round(lvl, 1), "peak_dbfs": round(pk, 1),
                                         "floor_p5_dbfs": round(floor, 1)}
    # 2) sintético con el espectro del suelo: tramas fuera de palabras (sin exigir margen) y del 20 % más tranquilo;
    #    nivel = p10 de esas tramas, con tope para que el pico (≈ RMS + 12 dB) quede bajo `peak_max_dbfs`
    nonword = np.ones(len(t), bool)
    for s_, e_ in (words or []):
        nonword[(t >= s_ - 0.03) & (t <= e_ + 0.03)] = False
    nonword &= r <= floor + 12
    if nonword.sum() < 10:
        nonword = r <= np.percentile(r, 10)
    quiet = nonword & (r <= np.percentile(r[nonword], 20))
    if quiet.sum() < 5:
        quiet = nonword
    idx = np.where(quiet)[0]
    hop = int(0.01 * sr)
    chunks = [m[int(max(0.0, t[i] - 0.025) * sr): int(max(0.0, t[i] - 0.025) * sr) + hop] for i in idx]
    noise = np.concatenate(chunks) if chunks else m[: sr]
    target_db = min(float(np.percentile(r[nonword], 10)), peak_max_dbfs - 12.0)
    nper = 4096 if len(noise) >= 4096 else max(256, 2 ** int(np.log2(max(256, len(noise)))))
    f, P = signal.welch(noise, fs=sr, nperseg=min(nper, len(noise)))
    rng = np.random.default_rng(seed)
    nfft = 1 << int(np.ceil(np.log2(n + 1)))
    fr = np.fft.rfftfreq(nfft, 1 / sr)
    mag = np.sqrt(np.interp(fr, f, P))
    spec = mag * np.exp(1j * rng.uniform(0, 2 * np.pi, len(fr)))
    y = np.fft.irfft(spec, nfft)[:n]
    y *= undb(target_db) / (np.sqrt(np.mean(y ** 2)) + 1e-12)
    return y, {"mode": "sintetico", "level_dbfs": round(target_db, 1), "peak_dbfs": round(float(db(np.max(np.abs(y)))), 1),
               "frames": int(idx.size), "reason": f"ninguna ventana con pico < {peak_max_dbfs:g} dBFS y {margin_s:g} s de margen"}


# ───────────────────────────── filtros sencillos (numpy/scipy) ─────────────────────────────
def peaking_sos(f0: float, gain_db: float, q: float, sr: int = SR) -> np.ndarray:
    """Biquad de pico (RBJ) como SOS."""
    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / sr
    al = np.sin(w0) / (2 * q)
    b = np.array([1 + al * A, -2 * np.cos(w0), 1 - al * A])
    a = np.array([1 + al / A, -2 * np.cos(w0), 1 - al / A])
    return np.concatenate([b / a[0], a / a[0]])[None, :]


def shelf_sos(f0: float, gain_db: float, sr: int = SR, kind: str = "low", S: float = 1.0) -> np.ndarray:
    """Biquad de estante (RBJ) como SOS. `kind` = "low" | "high"."""
    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / sr
    al = np.sin(w0) / 2 * np.sqrt((A + 1 / A) * (1 / S - 1) + 2)
    c, sq = np.cos(w0), 2 * np.sqrt(A) * al
    if kind == "low":
        b = [A * ((A + 1) - (A - 1) * c + sq), 2 * A * ((A - 1) - (A + 1) * c), A * ((A + 1) - (A - 1) * c - sq)]
        a = [(A + 1) + (A - 1) * c + sq, -2 * ((A - 1) + (A + 1) * c), (A + 1) + (A - 1) * c - sq]
    else:
        b = [A * ((A + 1) + (A - 1) * c + sq), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - sq)]
        a = [(A + 1) - (A - 1) * c + sq, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - sq]
    b, a = np.asarray(b), np.asarray(a)
    return np.concatenate([b / a[0], a / a[0]])[None, :]


def pitch_shift(x: np.ndarray, semitones: float) -> np.ndarray:
    """Cambio de tono por remuestreo (varispeed, como una cinta): +1 st = 5,9 % más corto. Para variar SFX."""
    if abs(semitones) < 1e-3:
        return x
    from fractions import Fraction
    fr = Fraction(2 ** (semitones / 12)).limit_denominator(200)
    return signal.resample_poly(x, fr.denominator, fr.numerator, axis=0)


def to_json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o))
