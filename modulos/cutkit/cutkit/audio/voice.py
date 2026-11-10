"""Cadena de voz ADAPTATIVA: mide → decide → aplica → vuelve a medir.

Orden: restar antes que sumar, nivelar después de filtrar, techo al final.
  A (ffmpeg)  paso alto (+ estante) · notch de zumbido · SIN reductor de ruido
  B (numpy)   nivelador por frase (±6 dB) si la dispersión pasa de 10 dB
  C (ffmpeg)  compresor ~2,5:1 · expansor calibrado con el suelo tras comprimir (la SNR no debe caer > 3 dB)
  D           EQ correctiva parcial (ffmpeg; 50 % / ±3 dB, o 60 % / ±4 dB con voz de referencia) · de-esser (numpy)
  E (ffmpeg)  ganancia estática · limitador −3 dBFS
Nunca `loudnorm` (ni dinámico ni lineal): la normalización final la hace `mix` con ganancia fija + limitador.
Los de-esser de ffmpeg (`deesser`, `adynamicequalizer`) no dieron una reducción medible y controlada en las voces
probadas (0 dB o −10 dB), por eso el de-esser y el nivelador van en numpy, con parámetros escritos en el informe.
"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import numpy as np
from scipy import ndimage, signal

from . import _dsp as d

VOICE_PREMIX_LUFS = -16.5          # voz antes de mezclar (targets.voice_lufs_premix)
LIMIT_DBFS = -3.0                  # limitador de seguridad de la voz


# ───────────────────────────── pasos en numpy ─────────────────────────────
def phrase_leveler(x: np.ndarray, sr: int = d.SR, max_gain_db: float = 6.0, tol_db: float = 1.0,
                   ramp_s: float = 0.04) -> tuple[np.ndarray, dict]:
    """Ganancia de clip por frase: lleva cada frase a ±1 LU de la mediana, con tope de ±6 dB y rampas de 40 ms.
    Las frases salen del RMS (habla separada por pausas ≥ 250 ms); en las pausas la ganancia se interpola."""
    t, r = d.frame_rms_db(x, sr, 0.05, 0.025)
    floor = float(np.percentile(r, 5))
    sp = d.speech_mask(r, floor)
    sp = ndimage.binary_closing(sp, structure=np.ones(int(0.25 / 0.025)))  # une huecos < 250 ms
    lab, n = ndimage.label(sp)
    segs = []
    for k in range(1, n + 1):
        idx = np.where(lab == k)[0]
        s0, s1 = int(t[idx[0]] * sr - 0.025 * sr), int(t[idx[-1]] * sr + 0.025 * sr)
        s0, s1 = max(0, s0), min(len(x), s1)
        if s1 - s0 >= int(0.4 * sr):
            segs.append((s0, s1, d.integrated_lufs(x[s0:s1], sr)))
    if len(segs) < 2:
        return x, {"phrases": len(segs), "applied": False}
    med = float(np.median([s[2] for s in segs]))
    pts_t, pts_g = [], []
    for s0, s1, L in segs:
        diff = med - L
        g = 0.0 if abs(diff) <= tol_db else float(np.clip(diff - np.sign(diff) * tol_db, -max_gain_db, max_gain_db))
        pts_t += [s0 / sr + ramp_s, s1 / sr - ramp_s]
        pts_g += [g, g]
    order = np.argsort(pts_t)
    tt = np.arange(len(x)) / sr
    curve = np.interp(tt, np.asarray(pts_t)[order], np.asarray(pts_g)[order])
    y = x * d.undb(curve)[:, None] if x.ndim == 2 else x * d.undb(curve)
    gains = [round(med - s[2], 1) for s in segs]
    return y, {"phrases": len(segs), "median_lufs": round(med, 1), "applied": True,
               "max_gain_db": round(float(np.max(np.abs(curve))), 1),
               "spread_before_db": round(float(np.percentile(gains, 95) - np.percentile(gains, 5)), 1)}


def split_band_deesser(x: np.ndarray, sr: int = d.SR, f_split: float = 4500.0, thr_db: float = 3.0,
                       max_gr_db: float = 5.0, attack_ms: float = 2.0, release_ms: float = 60.0) -> tuple[np.ndarray, dict]:
    """De-esser de banda partida: solo atenúa la banda > `f_split` cuando la relación 5–9 kHz / 0,3–3 kHz pasa de
    `thr_db`. Banda alta con filtro de fase cero, así `x − alta` es exactamente complementaria (sin coloración)."""
    m = x if x.ndim == 1 else x.mean(axis=1)
    hi = signal.sosfiltfilt(signal.butter(4, f_split, "highpass", fs=sr, output="sos"), m)
    lo = m - hi
    sib = signal.sosfilt(signal.butter(2, [5000, 9000], "bandpass", fs=sr, output="sos"), m)
    body = signal.sosfilt(signal.butter(2, [300, 3000], "bandpass", fs=sr, output="sos"), m)
    w = int(0.005 * sr)
    e_s = ndimage.uniform_filter1d(sib ** 2, w)
    e_b = ndimage.uniform_filter1d(body ** 2, w)
    ratio = 10 * np.log10((e_s + 1e-12) / (e_b + 1e-12))
    # solo donde la banda sibilante está claramente por encima del ruido
    lvl = 10 * np.log10(e_s + 1e-14)
    gate = lvl > np.percentile(lvl, 50)
    gr = np.where(gate, np.clip((ratio - thr_db) * 0.8, 0.0, max_gr_db), 0.0)
    gr = ndimage.maximum_filter1d(gr, int(release_ms / 1000 * sr), origin=-(int(release_ms / 1000 * sr) // 2) + 1)
    gr = ndimage.uniform_filter1d(gr, max(1, int(attack_ms / 1000 * sr)))
    y = lo + hi * d.undb(-gr)
    active = float((gr > 0.5).mean())
    out = y if x.ndim == 1 else np.repeat(y[:, None], x.shape[1], axis=1)
    return out.astype(np.float32), {"f_split_hz": f_split, "thr_db": thr_db, "max_gr_db": max_gr_db,
                                    "active_ratio": round(active, 3), "mean_gr_db_when_active":
                                    round(float(gr[gr > 0.5].mean()), 2) if active > 0 else 0.0}


# ───────────────────────────── decisiones ─────────────────────────────
def _targets(ref: str | Path | None) -> tuple[dict, float, float, float, str]:
    """Perfil tonal objetivo, fuerza de la igualación, tope y sibilancia de referencia."""
    if ref:
        rm = d.voice_metrics(d.load(ref))
        return rm["ltas_rel_db"], 0.6, 4.0, rm["sibilance_p95_db"], f"voz de referencia del usuario ({Path(ref).name})"
    return dict(d.LTAS_REFERENCIA), 0.5, 3.0, d.SIBILANCIA_REFERENCIA, \
        "mediana de voces de referencia (solo orientación; falta una voz de referencia del usuario)"


def _eq_moves(ltas: dict, target: dict, strength: float, cap: float) -> tuple[list[dict], list[str]]:
    """EQ correctiva moderada: compara bandas (suavizado de 3), corrige solo el `strength` de la diferencia y con
    tope `cap`; ignora diferencias ≤ 2 dB. La banda 60–125 Hz la resuelve el paso alto."""
    names = [b[0] for b in d.LTAS_BANDS]
    diff = np.array([ltas[n] - target[n] for n in names])
    sm = np.convolve(np.pad(diff, 1, mode="edge"), np.ones(3) / 3, mode="valid")
    centers = {"125-250": 180, "250-500": 350, "500-1k": 700, "1k-2k": 1400, "2k-4k": 3000, "4k-8k": 6000}
    moves, warns = [], []
    for i, n in enumerate(names):
        if n == "60-125":
            continue
        dv = 0.5 * diff[i] + 0.5 * sm[i]            # mezcla banda propia y vecinas
        if abs(diff[i]) > 6:
            warns.append(f"banda {n} a {diff[i]:+.1f} dB del objetivo: probable problema de toma (micro/sala)")
        if abs(dv) <= 2.0:
            continue
        g = float(np.clip(-strength * dv, -cap, cap))
        if abs(g) < 0.75:
            continue
        moves.append({"fx": "peaking", "hz": centers[n], "gain_db": round(g, 1), "q": 1.2,
                      "reason": f"{n} a {diff[i]:+.1f} dB del objetivo → corrige {int(strength * 100)} % con tope ±{cap:g} dB"})
    return moves, warns


def _chain_a(m: dict, target: dict, strength: float, cap: float) -> tuple[list[dict], list[str]]:
    steps, warns = [], []
    low = m["ltas_rel_db"]["60-125"] - target["60-125"]
    hp = 90 if low > 4 else 80
    steps.append({"fx": "highpass", "hz": hp, "poles": 2, "slope_db_oct": 12,
                  "reason": f"60–125 Hz a {low:+.1f} dB del objetivo" if low > 4 else "limpieza de graves por defecto"})
    if low > 6:
        steps.append({"fx": "lowshelf", "hz": 150, "gain_db": -2.5,
                      "reason": f"grave sobrante ({low:+.1f} dB) tras el paso alto"})
    for h in m["hum_hz"]:
        steps.append({"fx": "notch", "hz": h, "q": 30, "reason": "zumbido de red detectado en las pausas"})
    # SIN reductor de ruido (en la prueba A/B se prefirió la toma sin él). `afftdn` daba un timbre metálico tipo autotune en las colas y retrasaba la voz 25 ms
    # respecto a la imagen. El ruido de las pausas lo baja el expansor de C; si la toma es muy ruidosa, se avisa al usuario.
    snr = m["snr_db"]
    if snr < 15:
        warns.append(f"SNR {snr} dB < 15: AVISAR AL USUARIO — toma muy ruidosa (sin reductor de ruido por criterio de estilo): repetir o aislador")
    elif snr < 25:
        warns.append(f"SNR {snr} dB (15–25): ruido de fondo audible; sin reductor de ruido por criterio de estilo, revisar a oído")
    return steps, warns


def _af(steps: list[dict]) -> str:
    parts = []
    for s in steps:
        fx = s["fx"]
        if fx == "highpass":
            parts.append(f"highpass=f={s['hz']}:poles={s['poles']}")
        elif fx == "lowshelf":
            parts.append(f"lowshelf=f={s['hz']}:g={s['gain_db']}:t=q:w=0.7")
        elif fx == "notch":
            parts.append(f"equalizer=f={s['hz']}:t=q:w={s['q']}:g=-25")
        elif fx == "afftdn":
            parts.append(f"afftdn=nr={s['nr']}:nf={s['nf']}:tn={s['tn']}")
        elif fx == "peaking":
            parts.append(f"equalizer=f={s['hz']}:t=q:w={s['q']}:g={s['gain_db']}")
        elif fx == "compressor":
            parts.append(f"acompressor=threshold={d.undb(s['threshold_db']):.6f}:ratio={s['ratio']}:attack={s['attack_ms']}"
                         f":release={s['release_ms']}:knee=2.8:makeup=1:detection=rms")
        elif fx == "expander":
            parts.append(f"agate=mode=downward:range={d.undb(s['range_db']):.4f}:threshold={d.undb(s['threshold_dbfs']):.6f}"
                         f":ratio={s['ratio']}:attack={s['attack_ms']}:release={s['release_ms']}:detection=rms")
        elif fx == "gain":
            parts.append(f"volume={s['db']:.2f}dB")
        elif fx == "limiter":
            parts.append(f"alimiter=limit={d.undb(s['ceiling_dbfs']):.4f}:attack=5:release=50:level=disabled:asc=1")
    return ",".join(parts) if parts else "anull"


# ───────────────────────────── API ─────────────────────────────
def analyze(src: str | Path) -> dict:
    """Solo mide (sin procesar)."""
    return d.voice_metrics(d.load(src))


def process(src_wav: str | Path, out_wav: str | Path, ref: str | Path | None = None) -> dict:
    """Procesa la voz de `src_wav` (wav/mp4/… → mono 48 kHz) y escribe `out_wav` (WAV 24 bits).

    Etapas: A limpieza (ffmpeg) → B nivelador (numpy) → C compresor + expansor (ffmpeg) → D EQ correctiva y
    de-esser decididos midiendo DESPUÉS de comprimir (la compresión sube consonantes y sibilancia) → E ganancia
    estática + limitador. Devuelve {"in", "out", "chain", "ffmpeg", "checks", "warnings", "out_wav"}.
    Reintenta (≤ 3 pasadas) si la cresta baja de 12 dB o si la SNR cae más de 3 dB.
    """
    out_wav = Path(out_wav)
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="ck_voice_"))
    try:
        x = d.load(src_wav)                                  # (n, 1)
        src = d.write(tmp / "in.wav", x)
        m_in = d.voice_metrics(x)
        target, strength, cap, sib_ref, target_src = _targets(ref)

        # A · limpieza (paso alto, zumbido, ruido) en ffmpeg; la EQ tonal va en D
        steps_a, warns = _chain_a(m_in, target, strength, cap)
        a = d.ffmpeg_filter(src, tmp / "a.wav", _af(steps_a))
        xa = d.load(a)
        ma = d.voice_metrics(xa)

        # B · nivelador por frase (numpy)
        steps_b = []
        if ma["phrase_spread_db"] > 10:
            y, info = phrase_leveler(xa[:, 0])
            xa = y[:, None]
            steps_b.append({"fx": "leveler", "max_gain_db": 6, "ramp_ms": 40, **info,
                            "reason": f"dispersión por frase {ma['phrase_spread_db']} dB > 10"})
        b = d.write(tmp / "b.wav", xa)
        mb = d.voice_metrics(xa) if steps_b else ma

        ratio, thr_off, exp_ratio, exp_off = 2.5, -5.0, 3, 12.0
        attempt, snr_drop = 0, 0.0
        while True:
            attempt += 1
            # C · compresor; el expansor se calibra con el suelo medido tras comprimir
            comp = {"fx": "compressor", "ratio": ratio, "threshold_db": round(mb["speech_rms_dbfs"] + thr_off, 1),
                    "attack_ms": 15, "release_ms": 100,
                    "reason": f"habla a {mb['speech_rms_dbfs']} dBFS RMS → umbral {thr_off:+g} dB (~3–6 dB de reducción)"}
            c0 = d.ffmpeg_filter(b, tmp / "c0.wav", _af([comp]))
            mc0 = d.voice_metrics(d.load(c0))
            snr_c = ma["snr_db"] - mc0["snr_db"]
            steps_c = [comp]
            if snr_c > 1.0:
                steps_c.append({"fx": "expander", "ratio": exp_ratio, "range_db": -8,
                                "threshold_dbfs": round(mc0["noise_floor_dbfs"] + exp_off, 1), "attack_ms": 5, "release_ms": 150,
                                "reason": f"el compresor sube el suelo {snr_c:.1f} dB respecto al habla: expansor suave (−8 dB máx.)"})
            c = d.ffmpeg_filter(b, tmp / "c.wav", _af(steps_c))
            xc = d.load(c)
            mc = d.voice_metrics(xc)

            # D · EQ correctiva (ffmpeg) y de-esser (numpy) medidos sobre la voz ya comprimida
            eq, w_eq = _eq_moves(mc["ltas_rel_db"], target, strength, cap)
            dd = d.ffmpeg_filter(c, tmp / "d.wav", _af(eq)) if eq else c
            xd = d.load(dd)
            md = d.voice_metrics(xd) if eq else mc
            steps_d = list(eq)
            sib_excess = md["sibilance_p95_db"] - sib_ref
            if sib_excess > 3.0:
                gr = float(np.clip(sib_excess, 3, 6))
                xd, info = split_band_deesser(xd, thr_db=sib_ref, max_gr_db=gr)
                steps_d.append({"fx": "deesser", "hz": 6500, **info,
                                "reason": f"sibilancia p95 {md['sibilance_p95_db']} dB, {sib_excess:+.1f} sobre la referencia"})
            d2 = d.write(tmp / "d2.wav", xd)

            # E · ganancia estática + limitador (nunca loudnorm)
            L = d.integrated_lufs(xd)
            gain = {"fx": "gain", "db": round(VOICE_PREMIX_LUFS - L, 2),
                    "reason": f"ganancia estática a {VOICE_PREMIX_LUFS} LUFS (sin loudnorm)"}
            lim = {"fx": "limiter", "ceiling_dbfs": LIMIT_DBFS, "reason": "techo de seguridad de la voz"}
            d.ffmpeg_filter(d2, tmp / "e.wav", _af([gain, lim]))
            mo = d.voice_metrics(d.load(tmp / "e.wav"))
            snr_drop = m_in["snr_db"] - mo["snr_db"]
            if attempt >= 3:
                break
            redo = False
            if mo["crest_db"] < 12 and ratio > 2.0:
                ratio, thr_off, redo = 2.0, thr_off + 2, True
                warns.append(f"cresta {mo['crest_db']} dB < 12: bajo el compresor a 2:1 y repito")
            if snr_drop > 3:
                exp_ratio, exp_off, redo = 4, exp_off + 3, True
                warns.append(f"la SNR cae {snr_drop:.1f} dB: expansor más firme y repito")
            if not redo:
                break
        steps_e = [gain, lim]
        m_out = mo
        warns += w_eq
        shutil.copy(tmp / "e.wav", out_wav)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    names = [b[0] for b in d.LTAS_BANDS][1:]
    ltas_dev = {n: round(m_out["ltas_rel_db"][n] - target[n], 1) for n in names}
    checks = {
        "snr_drop_db": {"value": round(snr_drop, 1), "max": 3.0, "ok": snr_drop <= 3.0},
        "crest_db": {"value": m_out["crest_db"], "min": 12.0, "ok": m_out["crest_db"] >= 12.0},
        "sibilance_vs_ref_db": {"value": round(m_out["sibilance_p95_db"] - sib_ref, 1), "max_abs": 3.0,
                                "ok": abs(m_out["sibilance_p95_db"] - sib_ref) <= 3.0},
        "ltas_dev_db": {"value": ltas_dev, "max_abs": 3.0,
                        "ok": max(abs(v) for v in ltas_dev.values()) <= 3.0},
        "integrated_lufs": {"value": m_out["integrated_lufs"], "target": VOICE_PREMIX_LUFS,
                            "ok": abs(m_out["integrated_lufs"] - VOICE_PREMIX_LUFS) <= 1.0},
    }
    for k, c in checks.items():
        if c["ok"] is False:
            warns.append(f"comprobación {k} fuera de rango: {c['value']}")
    chain = steps_a + steps_b + steps_c + steps_d + steps_e
    return {"out_wav": str(out_wav), "in": m_in, "out": m_out,
            "target": {"source": target_src, "ltas": target, "sibilance_p95_db": sib_ref},
            "chain": chain, "ffmpeg": {"A": _af(steps_a), "C": _af(steps_c), "D": _af([s for s in steps_d if s["fx"] == "peaking"]),
                                       "E": _af(steps_e)},
            "checks": checks, "warnings": warns, "passes": attempt}
