"""Cama musical: pista del cliente o generada (Lyria, opcional) → análisis de pulso → ajuste a la duración en compás.

`ensure(brief, duration, out_dir)`:
  1. Candidatas, por este orden: la pista fijada (`track`: ruta de un archivo, nombre de un archivo de
     `clientes/<cliente>/marca/musica/` o hash de una pista generada en caché), las pistas del cliente en
     `clientes/<cliente>/marca/musica/` y las generadas en caché (`datos/biblioteca/musica/<hash>/`).
  2. Solo si no hay ninguna y `CK_MUSICA_IA=1` (de pago, ~0,08 $ por canción), genera una con Lyria (Gemini API:
     `lyria-3.5`, luego `lyria-3-pro-preview` y `lyria-3-clip-preview`) con `GEMINI_API_KEY` del `.env` de la raíz.
     Sin candidatas ni permiso para generar, lanza `SinMusica` (el vídeo sale sin cama; nunca hay pista sorpresa).
  3. Detecta tempo, pulsos y compases (flujo espectral + autocorrelación; sin librosa) y encaja la pista a la
     duración: recorte con fundido de salida, o bucle con fundido cruzado de potencia constante en un downbeat
     (elige el par de compases más parecidos para que el salto no se note).
  4. Registra procedencia y licencia (`registro.jsonl`) y devuelve un dict con `path` y un `asset` (spec.Asset).
En anuncios de Reels no se puede usar música con licencia comercial: usa pistas propias, libres de derechos para
publicidad o generadas. Nunca imprime la clave.
"""
from __future__ import annotations

import base64
import datetime as _dt
import hashlib
import json
import os
import re
from pathlib import Path

import numpy as np
from scipy import ndimage, signal

from ..paths import CLIENTES, LIBRARY as _BIBLIOTECA, RAIZ, all_timelines, cargar_entorno
from . import _dsp as d

LIBRARY = _BIBLIOTECA / "musica"
EXT_AUDIO = (".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".aif", ".aiff")


class SinMusica(RuntimeError):
    """No hay pista que usar (ni del cliente, ni en caché, ni permiso para generarla)."""


def musica_ia_activa() -> bool:
    return os.environ.get("CK_MUSICA_IA", "").strip().lower() in ("1", "true", "si", "sí", "yes")


PROMPT_VERSION = "p1"
FIT_VERSION = "14"                    # súbelo si cambia el algoritmo de encaje (invalida los fit_*.wav)
#                                       14 (20-oct): con ≥ 1 s de programa tras el último golpe, la cola que no cabe se
#                                       funde en 0,5–0,6 s sin tocar los 0,5 s que siguen al golpe (antes 0,12 s); el
#                                       encaje cuenta cuántas veces suena cada compás de la fuente (`max_bar_plays`)
#                                       13 (20-oct): el estirado de tempo ya no rellena con ceros el final del cuerpo
#                                       (hueco de 70 ms antes del último golpe en un vídeo de prueba) y la cola cortada
#                                       se funde en 0,12 s, no en 0,3 s
COST_USD = {"lyria-3.5": 0.08, "lyria-3-pro-preview": 0.08, "lyria-3-clip-preview": 0.04}
# 20-oct (crítica de un vídeo de prueba: c70e06abd14cee3c sonaba por sexta vez seguida): una pista que ya sonó en los
# últimos RECENT_SHORTS Shorts (otros slugs) paga RECENT_PENALTY por cada uno (lo mismo que no pasar el control), así
# que solo repite si las demás encajan mucho peor. `tokens.music_track` del plan fija la pista y no paga nada.
RECENT_SHORTS = 5
RECENT_PENALTY = 1.0

DEFAULT_BRIEF: dict = {
    "use": "shorts_tech",
    "genre": "minimal modern electronic",
    "bpm": [95, 110],
    "mood": "focused, modern, quietly optimistic, tech",
    "instruments": "soft analog synth pulse, muted plucks, warm round sub bass, tight clean drums with soft kick "
                   "and light hi-hats, subtle airy texture",
    "energy": "constant medium energy, steady groove from start to end",
    "dropout": True,
    "avoid": "no vocals, no vocal chops, no lead melody, no big drops, no risers, no build-ups, nothing that "
             "competes with a spoken voice in the 1-4 kHz range",
    "model": "lyria-3.5",
}


# ───────────────────────────── brief y caché ─────────────────────────────
def _brief(brief: dict | None) -> dict:
    b = dict(DEFAULT_BRIEF)
    b.update({k: v for k, v in (brief or {}).items() if v is not None})
    return b


def brief_hash(brief: dict) -> str:
    b = _brief(brief)
    blob = json.dumps({**b, "_pv": PROMPT_VERSION}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def _fmt(t: float) -> str:
    t = int(round(t))
    return f"{t // 60}:{t % 60:02d}"


def build_prompt(brief: dict, duration: float) -> str:
    """Prompt en inglés con estructura por marcas de tiempo (la doc de Lyria 3.5 lo recomienda para la duración)."""
    b = _brief(brief)
    lo, hi = (b["bpm"] if isinstance(b["bpm"], (list, tuple)) else (b["bpm"], b["bpm"]))
    total = float(np.clip(duration + 10, 60, 180))
    mid = total * 0.5
    sections = [
        "[0:00 - 0:04] Intro: the groove starts almost immediately, drums and pulse in by 0:04.",
        f"[0:04 - {_fmt(mid)}] Main groove: steady and hypnotic, same {b['energy']}.",
    ]
    if b.get("dropout"):
        sections.append(f"[{_fmt(mid)} - {_fmt(mid + 4)}] Short breakdown: drums drop out for one bar, pads and "
                        f"pulse continue, then the groove returns on the downbeat.")
        sections.append(f"[{_fmt(mid + 4)} - {_fmt(total - 4)}] Main groove continues, same energy, no build-up.")
    else:
        sections.append(f"[{_fmt(mid)} - {_fmt(total - 4)}] Main groove continues, same energy.")
    sections.append(f"[{_fmt(total - 4)} - {_fmt(total)}] Clean ending on the last bar.")
    return (
        f"Instrumental background music bed for a short tech explainer video with a voice-over. "
        f"Genre: {b['genre']}. Tempo: {int(round((lo + hi) / 2))} BPM (between {lo} and {hi} BPM), 4/4, "
        f"steady grid. Mood: {b['mood']}. Instruments: {b['instruments']}. "
        f"Mix: understated and spacious, leave room for a spoken voice, controlled low end. "
        f"Instrumental only, no vocals. Avoid: {b['avoid']}. "
        f"Total length about {_fmt(total)} ({int(total)} seconds).\n" + "\n".join(sections)
    )


# ───────────────────────────── generación ─────────────────────────────
def _api_key() -> str | None:
    cargar_entorno()
    return os.environ.get("GEMINI_API_KEY") or None


def _ext_for(data: bytes, mime: str | None) -> str:
    if data[:4] == b"RIFF":
        return ".wav"
    if data[:3] == b"ID3" or data[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"):
        return ".mp3"
    if mime and "wav" in mime:
        return ".wav"
    return ".mp3"


def _generate(model: str, prompt: str, out_base: Path) -> tuple[Path, dict]:
    """Llama a Lyria y escribe el audio. Devuelve (ruta, info con el texto/estructura devuelto)."""
    from google import genai
    key = _api_key()
    if not key:
        raise RuntimeError("falta GEMINI_API_KEY en el .env de la raíz")
    client = genai.Client(api_key=key)
    data, mime, text, api = None, None, [], None
    if model == "lyria-3.5":
        api = "interactions.create"
        it = client.interactions.create(model=model, input=prompt, response_format={"type": "audio"})
        for step in getattr(it, "steps", None) or []:
            if getattr(step, "type", None) == "model_output":
                for c in step.content or []:
                    if c.type == "audio" and data is None:
                        data = c.data
                        mime = getattr(c, "mime_type", None)
                    elif c.type == "text":
                        text.append(c.text)
        if data is None and getattr(it, "output_audio", None) is not None:
            data = it.output_audio.data
    else:
        from google.genai import types
        api = "models.generate_content"
        resp = client.models.generate_content(
            model=model, contents=prompt,
            config=types.GenerateContentConfig(response_modalities=["AUDIO", "TEXT"]))
        for cand in resp.candidates or []:
            for part in (cand.content.parts if cand.content else []) or []:
                if part.inline_data is not None and data is None:
                    data, mime = part.inline_data.data, part.inline_data.mime_type
                elif part.text:
                    text.append(part.text)
    if data is None:
        raise RuntimeError(f"{model}: la respuesta no trae audio")
    raw = base64.b64decode(data) if isinstance(data, str) else bytes(data)
    path = out_base.with_suffix(_ext_for(raw, mime))
    path.write_bytes(raw)
    return path, {"api": api, "mime": mime, "text": "\n".join(t for t in text if t)[:4000]}


# ───────────────────────────── pulso y compases ─────────────────────────────
def analyze_beats(x: np.ndarray, sr: int = d.SR, bpm_hint: float = 102.0) -> dict:
    """Tempo, pulsos y downbeats con flujo espectral + autocorrelación (suficiente para música electrónica de
    rejilla fija). `confidence` < 0,5 → no cortar a ritmo con confianza."""
    m = x.mean(axis=1) if x.ndim == 2 else x
    hop, nfft = 512, 2048
    f, t, Z = signal.stft(m, fs=sr, nperseg=nfft, noverlap=nfft - hop, boundary=None, padded=False)
    S = np.log1p(100 * np.abs(Z))
    flux = np.maximum(np.diff(S, axis=1), 0)
    env = flux.sum(axis=0)
    low = flux[f < 150].sum(axis=0)
    env = env - ndimage.uniform_filter1d(env, 32)
    env = np.maximum(env, 0)
    fps = sr / hop
    # tempo: autocorrelación con prior log-normal alrededor de bpm_hint
    ac = np.correlate(env - env.mean(), env - env.mean(), mode="full")[len(env) - 1:]
    lags = np.arange(len(ac))
    bpms = 60 * fps / np.maximum(lags, 1)
    sel = (bpms >= 60) & (bpms <= 190)
    prior = np.exp(-0.5 * (np.log2(bpms / bpm_hint) / 0.35) ** 2)
    score = np.where(sel, ac * prior, -np.inf)
    lag = int(np.argmax(score))
    # refino el periodo con interpolación parabólica
    if 1 <= lag < len(ac) - 1:
        a, b_, c = ac[lag - 1], ac[lag], ac[lag + 1]
        den = a - 2 * b_ + c
        lag_f = lag + (0.5 * (a - c) / den if den != 0 else 0.0)
    else:
        lag_f = float(lag)
    bpm = 60 * fps / lag_f
    conf = float(ac[lag] / (ac[0] + 1e-12))
    # fase: la que maximiza la suma de la envolvente en la rejilla
    P = lag_f
    phases = np.arange(int(np.ceil(P)))
    sums = [env[np.round(np.arange(p, len(env), P)).astype(int).clip(0, len(env) - 1)].sum() for p in phases]
    ph = phases[int(np.argmax(sums))]
    grid = np.arange(ph, len(env), P)
    # pequeño ajuste local (±6 % del periodo) a máximos de la envolvente
    beats = []
    w = max(1, int(0.06 * P))
    for g in grid:
        g = int(round(g))
        lo, hi = max(0, g - w), min(len(env), g + w + 1)
        beats.append(lo + int(np.argmax(env[lo:hi])) if hi > lo else g)
    beats = np.asarray(beats)
    bt = (beats + 1) * hop / sr + (nfft / 2) / sr - hop / sr   # centro de trama del flujo
    # downbeat: fase (de 4) con más energía de bombo
    k = [low[beats[i::4]].mean() if len(beats[i::4]) else 0 for i in range(4)]
    db0 = int(np.argmax(k))
    downs = bt[db0::4]
    ibi = np.diff(bt)
    stability = float(1 - np.std(ibi) / (np.mean(ibi) + 1e-9)) if len(ibi) > 2 else 0.0
    return {"bpm": round(float(bpm), 2), "beats": [round(float(v), 4) for v in bt],
            "downbeats": [round(float(v), 4) for v in downs], "bar_s": round(4 * 60 / bpm, 4),
            "confidence": round(min(1.0, max(0.0, conf * 2)) * stability, 3), "acf_peak": round(conf, 3)}


def _bar_features(x: np.ndarray, sr: int, starts: list[float], bar_s: float = 0.0,
                  ends: list[float] | None = None) -> np.ndarray:
    """Huella espectral por compás (energía log10 en 24 bandas) para comparar compases al empalmar."""
    m = x.mean(axis=1) if x.ndim == 2 else x
    edges = np.geomspace(40, 16000, 25)
    feats = []
    for k, s in enumerate(starts):
        e = ends[k] if ends is not None else s + bar_s
        seg = m[int(s * sr): int(e * sr)]
        if len(seg) < 1024:
            feats.append(np.zeros(24)); continue
        F = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2
        fr = np.fft.rfftfreq(len(seg), 1 / sr)
        feats.append(np.log10([F[(fr >= lo) & (fr < hi)].sum() + 1e-9 for lo, hi in zip(edges[:-1], edges[1:])]))
    return np.asarray(feats)


# ───────────────────────────── compases: densidad, arranque, final ─────────────────────────────
SPARSE_LU = 12.0            # ventana de 400 ms «dispersa»: M < I − 12 (I = integrada de la pista)
SPARSE_MAX = 0.10           # el tramo usado no puede tener más de un 10 % de ventanas dispersas
BAR_SPARSE = 0.25           # un compás con > 25 % de ventanas dispersas se salta (breakdown, intro, final)
SPLICE_MAX_DIST = 0.10      # distancia de huella máxima en un empalme
SPLICE_MIN_GAP_S = 1.0      # ningún empalme a < 1 s de una cue visual o palabra clave (`avoid_times`)
SPLICE_MIN_XF_S = 0.25      # cruce mínimo (y al menos 1 tiempo)
HOOK_S = 3.0                # gancho: ningún hueco > 150 ms en los primeros 3 s…
HOOK_GAP_S = 0.15
HOOK_GAP_LU = 18.0          # …entendido como ventanas de 50 ms a > 18 LU por debajo de la integrada de la pista
MAX_STRETCH = 0.03          # ajuste de tempo máximo (rubberband) para arrancar en un downbeat
STRETCH_PAD_S = 0.5         # el estirado lleva detrás 0,5 s de lo que sigue en la fuente (rubberband pierde ~70 ms al final)
STRETCH_XF_S = 0.01         # cruce de 10 ms del cuerpo estirado a la cola original, justo tras el último downbeat
TAIL_CUT_MAX_S = 0.3        # QA: no se recortan más de 0,3 s audibles de la cola del final
TAIL_FADE_S = 0.12          # fundido de la cola si no cabe entera (antes 0,3 s: se comía lo que quedaba de cola; el
#                             máster pone después su propio fundido de 0,15 s)
# 20-oct (crítica de audio de un vídeo de prueba): con el golpe final justo tras la última palabra y la CTA congelada
# ≥ 1 s, lo que no cabe de la cola se funde LARGO (como mucho 0,6 s, dejando intactos los 0,5 s que siguen al golpe):
# así no acaba en seco y la QA `audio.music_tail_cut` lo acepta (fundido ≥ 0,5 s tras la última palabra)
TAIL_ROOM_LONG_S = 1.0      # programa mínimo tras el golpe final para el fundido largo
TAIL_HIT_KEEP_S = 0.5       # lo que suena intacto tras el golpe
TAIL_FADE_LONG_S = 0.6      # fundido largo máximo
TAIL_FADE_OK_S = 0.5        # fundido mínimo para que la QA no lo cuente como corte en seco
# 20-oct: ningún compás de la fuente puede sonar más de MAX_BAR_PLAYS veces en el encaje (bucle audible). `ensure`
# descarta esas pistas en la elección automática; una pista fijada a mano (`tokens.music_track`) se respeta con aviso
MAX_BAR_PLAYS = 2


def hook_gaps(y: np.ndarray, sr: int = d.SR, t1: float = HOOK_S, ref_lufs: float | None = None,
              drop_lu: float = HOOK_GAP_LU, min_s: float = HOOK_GAP_S, bridge_s: float = 0.0) -> list[list[float]]:
    """Huecos (> `min_s`) en los primeros `t1` s: loudness K de 50 ms (salto 10 ms) por debajo de `ref − drop_lu`.
    `bridge_s` > 0: dos huecos que solo separa un repunte de ≤ `bridge_s` cuentan como uno."""
    seg = y[: int(t1 * sr)]
    if len(seg) < int(0.06 * sr):
        return []
    ref = ref_lufs if ref_lufs is not None else d.integrated_lufs(seg, sr)
    t, L = d.short_term(seg, sr, 0.05, 0.01)
    low = L < ref - drop_lu
    nb = int(round(bridge_s / 0.01))
    if nb > 0 and low.any():                      # rellena los repuntes cortos entre dos tramos bajos
        idx = np.where(low)[0]
        for a_, b_ in zip(idx, idx[1:]):
            if 1 < b_ - a_ <= nb + 1:
                low[a_:b_] = True
    out, st = [], None
    for i, v in enumerate(np.append(low, False)):
        if v and st is None:
            st = i
        elif not v and st is not None:
            if (i - st) * 0.01 >= min_s:
                out.append([round(float(t[st]) - 0.025, 3), round(float(t[i - 1]) + 0.025, 3)])
            st = None
    return out


def find_gaps(y: np.ndarray, sr: int, t0: float, t1: float, ref_lufs: float, drop_lu: float = HOOK_GAP_LU,
              min_s: float = HOOK_GAP_S, bridge_s: float = 0.0) -> list[list[float]]:
    """Huecos (> `min_s`, loudness K de 50 ms bajo `ref − drop_lu`) entre t0 y t1, en tiempo absoluto."""
    a = max(0, int(t0 * sr))
    return [[round(g0 + a / sr, 3), round(g1 + a / sr, 3)]
            for g0, g1 in hook_gaps(y[a: int(t1 * sr)], sr, t1 - a / sr, ref_lufs, drop_lu, min_s, bridge_s)]


def patch_gaps(y: np.ndarray, sr: int, gaps: list, bar_prog_s: float, ref_lufs: float,
               min_s: float = HOOK_GAP_S, bridge_s: float = 0.0) -> tuple[np.ndarray, list[dict]]:
    """Rellena cada hueco con el MISMO tramo del compás vecino (±1, ±2 compases) si ese tramo no tiene hueco (con el
    mismo criterio con que se buscó: `min_s`, `bridge_s`); cruces de 20 ms. Las paradas rítmicas del tema solo caen
    cada 2 compases, así que el vecino suele estar lleno."""
    y = y.copy()
    patches = []
    xf = int(0.02 * sr)
    for g0, g1 in gaps:
        a, b = max(0, int((g0 - 0.04) * sr)), min(len(y), int((g1 + 0.04) * sr))
        done = None
        for k in (1, -1, 2, -2):
            off = int(round(k * bar_prog_s * sr))
            if a + off < 0 or b + off > len(y) or b - a <= 2 * xf:
                continue
            rep = y[a + off: b + off]
            if hook_gaps(rep, sr, (b - a) / sr + 0.01, ref_lufs, min_s=min_s, bridge_s=bridge_s):
                continue
            w = np.ones((b - a, 1))
            w[:xf, 0] = np.linspace(0, 1, xf)
            w[-xf:, 0] = np.linspace(1, 0, xf)
            y[a:b] = y[a:b] * (1 - w) + rep * w
            done = k
            break
        patches.append({"gap": [g0, g1], "from_bar_offset": done})
    return y, patches


def patch_hook_gaps(y: np.ndarray, sr: int, until_s: float, bar_prog_s: float, ref_lufs: float) -> tuple[np.ndarray, list[dict]]:
    """Rellena los huecos (> 150 ms, ventanas de 50 ms) del gancho [0, until_s] con el MISMO tramo del compás vecino
    (±1 o ±2 compases: el tema repite el groove y solo para cada 2 compases), con cruces de 20 ms. No toca el
    camino ni el fraseo; solo quita las paradas rítmicas del tema antes de la primera salida de la música."""
    # también los huecos que EMPIEZAN antes del límite aunque acaben después (cruzan la primera salida)
    gaps = [g for g in find_gaps(y, sr, 0.0, min(len(y) / sr, until_s + 0.4), ref_lufs) if g[0] < until_s]
    return patch_gaps(y, sr, gaps, bar_prog_s, ref_lufs)


def _stretch(y: np.ndarray, tempo: float, sr: int = d.SR) -> np.ndarray:
    """Cambio de tempo sin cambiar el tono (ffmpeg rubberband)."""
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        a, b = Path(td) / "in.wav", Path(td) / "out.wav"
        d.write(a, y, sr, subtype="FLOAT")
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(a),
                        "-af", f"rubberband=tempo={tempo:.6f}", "-c:a", "pcm_f32le", str(b)], check=True)
        return d.load(b, channels=y.shape[1], sr=sr)


def bar_table(x: np.ndarray, beats: dict, sr: int = d.SR) -> dict:
    """Tabla por compás (downbeat → downbeat): p10 de la loudness momentánea, fracción de ventanas dispersas,
    densidad y huella. Es la base de arranque, final, empalmes y control de calidad."""
    D = list(beats.get("downbeats", []))
    t, M = d.short_term(x, sr, 0.4, 0.05)
    I = d.integrated_lufs(x, sr)
    bars = []
    for k, (a, b) in enumerate(zip(D, D[1:])):
        w = (t >= a) & (t < b)
        mw = M[w] if w.any() else np.array([-70.0])
        bars.append({"i": k, "s": float(a), "e": float(b), "p10": round(float(np.percentile(mw, 10)), 2),
                     "sparse": round(float((mw < I - SPARSE_LU).mean()), 3)})
    med = float(np.median([bb["p10"] for bb in bars])) if bars else -70.0
    for bb in bars:
        bb["dense"] = bool(bb["sparse"] <= BAR_SPARSE and bb["p10"] >= med - 10)
    feats = _bar_features(x, sr, [bb["s"] for bb in bars], ends=[bb["e"] for bb in bars]) if bars else np.zeros((0, 24))
    return {"bars": bars, "feats": feats, "I": I, "p10_median": med}


def _groove_bar(tb: dict, max_s: float = 45.0) -> int | None:
    """Primer compás con groove: él y el siguiente con ≤ 10 % de ventanas dispersas y p10 ≥ mediana − 8 dB."""
    bars, med = tb["bars"], tb["p10_median"]
    for k in range(len(bars) - 1):
        a, b = bars[k], bars[k + 1]
        if a["s"] > max_s:
            break
        if all(z["sparse"] <= SPARSE_MAX and z["p10"] >= med - 8 for z in (a, b)):
            return k
    return None


def groove_start(x: np.ndarray, beats: dict, sr: int = d.SR, max_s: float = 45.0, table: dict | None = None) -> float:
    """Downbeat en que arranca el groove (p10 momentáneo por compás, no la integrada). En Shorts la cama tiene que
    estar desde el primer fotograma: se salta la intro escasa que traen los temas generados."""
    if beats.get("confidence", 0) < 0.3:
        return 0.0
    tb = table or bar_table(x, beats, sr)
    k = _groove_bar(tb, max_s)
    return float(tb["bars"][k]["s"]) if k is not None else 0.0


def _last_dense(tb: dict) -> int:
    bars = tb["bars"]
    k = len(bars) - 1
    while k > 0 and not bars[k]["dense"]:
        k -= 1
    return k


def breakdowns(x: np.ndarray, beats: dict, sr: int = d.SR, table: dict | None = None) -> list[list[float]]:
    """Tramos de compases dispersos tras el groove (breakdowns y final), en tiempos de la fuente."""
    tb = table or bar_table(x, beats, sr)
    g = _groove_bar(tb) or 0
    out: list[list[float]] = []
    for bb in tb["bars"][g:]:
        if not bb["dense"]:
            if out and abs(out[-1][1] - bb["s"]) < 0.05:
                out[-1][1] = bb["e"]
            else:
                out.append([bb["s"], bb["e"]])
    return [[round(a, 3), round(b, 3)] for a, b in out]


# ───────────────────────────── camino por compases ─────────────────────────────
def _greedy_path(tb: dict, start: int, n: int, last: int, rem: float, avoid: list[float]) -> tuple[list[int], list[dict]]:
    """`n` compases desde `start` siguiendo la pista; salta compases dispersos y, al acabarse, vuelve atrás.
    Cada salto elige (compás de salida, compás de entrada) minimizando la distancia entre el compás que se deja y
    el ANTERIOR al de entrada (así la entrada suena a continuación natural), con fraseo de 4 compases y lejos de
    `avoid` (≥ 1 s)."""
    bars, F = tb["bars"], tb["feats"]
    dense = {bb["i"] for bb in bars if bb["dense"] and bb["i"] <= last}
    seq, splices, since = [start], [], 1          # `since`: compases añadidos desde el último empalme

    def prog_len(sq):
        return rem + sum(bars[b]["e"] - bars[b]["s"] for b in sq)

    guard = 0
    while len(seq) < n and guard < 4 * n:
        guard += 1
        cur = seq[-1]
        if cur + 1 in dense:
            seq.append(cur + 1); since += 1
            continue
        best = None
        for back in range(0, min(8, since - 1) + 1):      # salir hasta 8 compases antes (zonas densas en cues)
            leave = seq[-1 - back]
            ps = prog_len(seq[: len(seq) - back])          # instante de programa del empalme
            clash = any(abs(ps - a) < SPLICE_MIN_GAP_S for a in avoid)
            ahead = any(c2 > leave + 1 for c2 in dense)          # ¿queda pista por delante?
            for c in sorted(dense):
                # el destino tiene que dejar atrás el obstáculo (c > cur + 1) o ser un bucle real (c < leave − 3)
                if c - 1 not in dense or not (c > cur + 1 or c < leave - 3):
                    continue
                dist = float(((F[leave] - F[c - 1]) ** 2).mean())
                # fuera de fraseo = suspenso; cada compás denso que se pierde (al salir antes o saltar) obliga a
                # repetir más tarde; avanzar antes que repetir
                skipped = sum(1 for z in range(leave + 1, c) if z in dense) if c > leave else 0
                cost = dist + (0.0 if (c - leave - 1) % 4 == 0 else 1.0) + 0.015 * back + (5.0 if clash else 0.0)
                cost += (0.06 if c < leave and ahead else 0.0) + 0.015 * skipped
                if best is None or cost < best[0]:
                    best = (cost, back, leave, c, dist, ps, clash)
        if best is None:
            break
        _, back, leave, c, dist, ps, clash = best
        if back:
            del seq[-back:]
        seq.append(c)
        since = 1
        splices.append({"prog_s": round(ps, 3), "from_bar_src_s": round(bars[leave]["e"], 3),
                        "to_bar_src_s": round(bars[c]["s"], 3), "dist": round(dist, 4),
                        "phrase_ok": (c - leave - 1) % 4 == 0, "near_avoid": clash})
    return seq, splices


def _render_path(x: np.ndarray, tb: dict, seq: list[int], rem: float, sr: int, xf_s: float) -> np.ndarray:
    """Concatena los compases; en cada empalme cruza (coseno, igual ganancia) la cola del compás saliente con la
    preparación del entrante y TERMINA el cruce en el downbeat entrante (su transitorio queda intacto)."""
    bars = tb["bars"]
    xf = int(xf_s * sr)
    a0 = max(0, int((bars[seq[0]]["s"] - rem) * sr))
    chunks, cur_end = [x[a0: int(bars[seq[0]]["e"] * sr)]], int(bars[seq[0]]["e"] * sr)
    for prev, b in zip(seq, seq[1:]):
        s, e = int(bars[b]["s"] * sr), int(bars[b]["e"] * sr)
        if b == prev + 1:
            chunks.append(x[cur_end: e])
        else:
            n = min(xf, s, len(chunks[-1]))
            tail = chunks[-1][-n:]
            head = x[s - n: s]
            w = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, n))[:, None]
            chunks[-1] = chunks[-1][:-n]
            chunks.append(tail * (1 - w) + head * w)
            chunks.append(x[s: e])
        cur_end = e
    return np.concatenate(chunks)


def sparse_fraction(y: np.ndarray, t0: float = 0.0, t1: float | None = None, sr: int = d.SR) -> float:
    """Fracción de ventanas de 400 ms con M < I − 12 en [t0, t1] (I del propio tramo)."""
    a, b = int(t0 * sr), int((t1 if t1 is not None else len(y) / sr) * sr)
    seg = y[a:b]
    if len(seg) < sr:
        return 0.0
    I = d.integrated_lufs(seg, sr)
    _, M = d.short_term(seg, sr, 0.4, 0.1)
    return round(float((M < I - SPARSE_LU).mean()), 4)


def _prog_beats(tb: dict, beats: dict, seq: list[int], rem: float, duration: float,
                tail_from: int | None = None) -> tuple[list[float], list[float]]:
    """Pulsos y downbeats del encaje en TIEMPO DE PROGRAMA (para encajar reentradas y cortes al pulso)."""
    bars = tb["bars"]
    src = np.asarray(beats.get("beats", []), dtype=float)
    out, downs = [], []
    s0 = bars[seq[0]]["s"]
    pre = src[(src >= s0 - rem) & (src < s0)]
    out += list(pre - (s0 - rem))
    p = rem
    for b in seq:
        a, e = bars[b]["s"], bars[b]["e"]
        downs.append(p)
        out += list(src[(src >= a) & (src < e)] - a + p)
        p += e - a
    if tail_from is not None:
        a = bars[tail_from]["e"]
        downs.append(p)
        out += list(src[src >= a] - a + p)
    keep = lambda v: [round(float(t), 4) for t in v if 0 <= t <= duration]          # noqa: E731
    return keep(sorted(out)), keep(downs)


def _max_plays(seq: list[int]) -> int:
    """Veces que suena el compás de la fuente que más se repite en el encaje (1 = sin bucle)."""
    if not seq:
        return 0
    return int(max(seq.count(b) for b in set(seq)))


def fit_to_duration(x: np.ndarray, duration: float, beats: dict, sr: int = d.SR, *, end_at: float | None = None,
                    avoid_times: list[float] | tuple = (), skip_intro: bool = True, fade_out_s: float = 1.5,
                    table: dict | None = None, hook_until: float | None = None) -> tuple[np.ndarray, dict]:
    """Encaja la pista a `duration` caminando por compases DENSOS (salta intro escasa y breakdowns).

    - `end_at`: el último downbeat del «clean ending» propio de la pista cae en ese instante de programa y su cola
      suena después, sin rampa (p. ej. final del bloque principal antes del outro).
    - `avoid_times`: instantes (cues, palabras clave) a ≥ 1 s de cualquier empalme.
    Empalmes: distancia < 0,1, fraseo de 4 compases, cruce de 1 tiempo (≥ 250 ms) que acaba en el downbeat.
    `info["ok"]` es False si el tramo usado tiene > 10 % de ventanas dispersas o algún empalme pasa de 0,1.
    """
    N = int(round(duration * sr))
    tb = table or bar_table(x, beats, sr)
    bars = tb["bars"]
    info: dict = {"method": "", "splices": [], "start_s": 0.0, "warnings": []}
    if beats.get("confidence", 0) < 0.3 or len(bars) < 8:
        y = x[:N] if len(x) >= N else np.vstack([x, np.zeros((N - len(x), x.shape[1]))])
        info.update({"method": "recorte_sin_rejilla", "ok": False})
        info["warnings"].append("rejilla de pulso poco fiable: sin encaje por compases")
        nf = min(int(fade_out_s * sr), len(y)); y = y.copy(); y[-nf:] *= np.cos(np.linspace(0, np.pi / 2, nf))[:, None]
        return y.astype(np.float32), info
    start = (_groove_bar(tb) if skip_intro else 0) or 0
    last = _last_dense(tb)
    bar_s = float(np.median([bb["e"] - bb["s"] for bb in bars]))
    beat_s = bar_s / 4
    xf_s = max(SPLICE_MIN_XF_S, beat_s)
    avoid = sorted(float(a) for a in (avoid_times or []))
    info["start_s"] = round(bars[start]["s"], 3)

    if end_at is not None:
        # n compases completos hasta `end_at`; lo que sobra es preparación antes del primer downbeat.
        # Camino codicioso de n compases y, sobre él, el mejor punto m para saltar a los últimos compases
        # (c' … last), cuyo final es el último downbeat de la pista.
        F = tb["feats"]
        blen = lambda sq: sum(bars[b]["e"] - bars[b]["s"] for b in sq)      # noqa: E731
        tm, Mm = d.short_term(x, sr, 0.4, 0.05)
        hook_cache: dict = {}

        def preroll_dense(s0: float, rem: float) -> bool:
            """La preparación (antes del primer downbeat) tiene que ser densa: ≤ 10 % de ventanas dispersas."""
            if rem < 0.05:
                return True
            w = (tm >= s0 - rem) & (tm <= s0)
            return (not w.any()) or float((Mm[w] < tb["I"] - SPARSE_LU).mean()) <= SPARSE_MAX

        def hook_bad(seq: list[int], rem: float) -> bool:
            """Puerta del gancho sobre el audio real del arranque: ningún hueco > 150 ms en 0–3 s (ventanas de
            50 ms; la loudness de 400 ms no ve las paradas rítmicas del tema)."""
            key = (tuple(seq[:3]), round(rem, 3))
            if key not in hook_cache:
                y0 = _render_path(x, tb, seq[:3], rem, sr, xf_s)
                hook_cache[key] = bool(hook_gaps(y0, sr, HOOK_S, tb["I"]))
            return hook_cache[key]

        best = None
        n0 = int(end_at // bar_s)
        for st in range(start, start + 8):                 # arrancar más tarde si el gancho cae en la intro o en una parada
          for n in (n0, n0 - 1, n0 + 1):
            if n < 2 or st >= last:
                continue
            rem0 = end_at - n * bar_s
            P, splP = _greedy_path(tb, st, n, last, max(rem0, 0.0), avoid)
            if len(P) < n:
                continue
            for m in range(1, n + 1):
                cp = last + 1 - (n - m)
                if m < n and (cp <= P[m - 1] or not all(bars[k]["dense"] for k in range(cp, last + 1))):
                    continue
                if m == n and P[-1] != last:
                    continue
                seq = P[:m] + list(range(cp, last + 1)) if m < n else list(P)
                L = blen(seq)
                rem = end_at - L
                # (a) natural: preparación de hasta 1 compás (o empezar ≤ 0,3 s dentro del primer compás);
                # (b) ajuste de tempo ≤ 3 % (rubberband) para arrancar EN el downbeat, sin preparación
                opts = []
                if -0.3 <= rem <= bars[seq[0]]["s"] and preroll_dense(bars[seq[0]]["s"], rem):
                    opts.append((rem, 1.0, 0.0 if not hook_bad(seq, rem) else 10.0))
                f = end_at / L
                if abs(f - 1) <= MAX_STRETCH:
                    opts.append((0.0, f, 0.3 + 5 * abs(f - 1) + (0.0 if not hook_bad(seq, 0.0) else 10.0)))
                if not opts:
                    continue
                rem_o, f_o, extra = min(opts, key=lambda o: o[2])
                scale = (end_at - rem_o) / L if f_o != 1.0 else 1.0       # programa = fuente × escala (tempo)
                spl = [dict(sp, prog_s=round(rem_o + (sp["prog_s"] - max(rem0, 0.0)) * scale, 3)) for sp in splP
                       if sp["prog_s"] - max(rem0, 0.0) < blen(P[:m]) - 0.01]
                if m < n and cp != P[m - 1] + 1:
                    dist = float(((F[P[m - 1]] - F[cp - 1]) ** 2).mean())
                    spl.append({"prog_s": round(rem_o + blen(P[:m]) * scale, 3), "from_bar_src_s": round(bars[P[m - 1]]["e"], 3),
                                "to_bar_src_s": round(bars[cp]["s"], 3), "dist": round(dist, 4),
                                "phrase_ok": (cp - P[m - 1] - 1) % 4 == 0})
                for sp in spl:
                    sp["near_avoid"] = any(abs(sp["prog_s"] - a_) < SPLICE_MIN_GAP_S for a_ in avoid)
                cost = sum(sp["dist"] + (0 if sp["phrase_ok"] else 1.0) + (5 if sp["near_avoid"] else 0)
                           + (1 if sp["dist"] >= SPLICE_MAX_DIST else 0) for sp in spl) + 0.05 * len(spl) \
                    + 0.1 * (len(seq) - len(set(seq))) + extra
                if best is None or cost < best[0]:
                    best = (cost, seq, spl, rem_o, last - cp + 1 if m < n else 0, f_o, extra >= 10)
            if best is not None and best[0] < 0.5:
                break
        if best is None:
            info["warnings"].append("end_at imposible con esta pista: encaje sin final propio")
            end_at = None
        else:
            _, seq, spl, rem, t, f_o, hook_fail = best
            body = _render_path(x, tb, seq, rem, sr, xf_s)
            L = blen(seq)
            tail = x[int(bars[last]["e"] * sr):]                  # el «clean ending» y su cola, sin rampa
            if f_o != 1.0:
                # 20-oct: rubberband pierde ~50–80 ms al final de lo que estira y antes se rellenaba con CEROS (hueco
                # de 70 ms justo antes del último golpe: un vídeo de prueba, 102,10 s). Se estira el cuerpo con lo que
                # le sigue en la fuente (STRETCH_PAD_S del final propio), se corta en `end_at` y se cruza en 10 ms del
                # audio estirado a la cola original (es el mismo audio, ±3 % de tempo): el último golpe queda intacto.
                st_ = _stretch(np.vstack([body, tail[: int(STRETCH_PAD_S * sr)]]), L / end_at, sr)   # tempo > 1 acelera
                ne, nx = int(round(end_at * sr)), int(STRETCH_XF_S * sr)
                if len(st_) >= ne + nx and len(tail) >= nx:
                    w = (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, nx)))[:, None]
                    y = np.concatenate([st_[:ne], st_[ne: ne + nx] * (1 - w) + tail[:nx] * w, tail[nx:]])
                else:
                    info["warnings"].append("el estirado de tempo salió corto: cola pegada sin cruce")
                    body = st_[:ne] if len(st_) >= ne else np.vstack([st_, np.zeros((ne - len(st_), st_.shape[1]))])
                    y = np.concatenate([body, tail])
            else:
                y = np.concatenate([body, tail])
            info.update({"method": "camino_por_compases+final_propio" + ("+tempo" if f_o != 1.0 else ""),
                         "end_at": round(end_at, 3), "final_downbeat_src_s": round(bars[last]["e"], 3), "ending_bars": t,
                         "preroll_s": round(rem, 3), "tail_s": round(len(tail) / sr, 3),
                         "tempo_factor": round(L / end_at, 4) if f_o != 1.0 else 1.0})
            info["splices"] = spl
            info["repeated_bars"] = len(seq) - len(set(seq))
            info["max_bar_plays"] = _max_plays(seq)
            info["start_s"] = round(bars[seq[0]]["s"], 3)
            info["preroll_src_s"] = [round(bars[seq[0]]["s"] - rem, 3), round(bars[seq[0]]["s"], 3)]
            bp, dp = _prog_beats(tb, beats, seq, rem, duration + 10, tail_from=last)
            if f_o != 1.0:                                    # pulsos en el tiempo ya ajustado
                k = end_at / L
                mapb = lambda v: [round(u * k if u <= L + 1e-6 else end_at + (u - L), 4) for u in v]     # noqa: E731
                bp, dp = mapb(bp), mapb(dp)
            info["beats_prog_s"] = [u for u in bp if u <= duration]
            info["downbeats_prog_s"] = [u for u in dp if u <= duration]
            # cola audible (hasta I − 45) frente a lo que queda de programa tras `end_at`
            tt, rr = d.frame_rms_db(tail, sr, 0.05, 0.01) if len(tail) > sr * 0.06 else (np.array([0.0]), np.array([-140.0]))
            loud = np.where(rr > tb["I"] - 45)[0]
            info["tail_audible_s"] = round(float(tt[loud[-1]]) if loud.size else 0.0, 3)
            info["tail_cut_s"] = round(max(0.0, info["tail_audible_s"] - (duration - end_at)), 3)
            if len(y) >= N:
                y = y[:N].copy()
                room = duration - end_at                     # programa que queda tras el golpe final
                fade_s = TAIL_FADE_S if room < TAIL_ROOM_LONG_S else min(TAIL_FADE_LONG_S, room - TAIL_HIT_KEEP_S)
                nf = min(int(fade_s * sr), len(y))
                y[-nf:] *= np.cos(np.linspace(0, np.pi / 2, nf))[:, None]
                info["tail_fade_s"] = round(nf / sr, 3)
                if info["tail_cut_s"] > TAIL_CUT_MAX_S:
                    info["warnings"].append(f"se recortan {info['tail_cut_s']} s audibles de la cola del final"
                                            + (f" (con fundido de {nf / sr:.2f} s)" if nf / sr >= TAIL_FADE_OK_S else ""))
            else:
                y = np.vstack([y, np.zeros((N - len(y), y.shape[1]))])
            used_end = end_at
            if hook_fail:
                info["warnings"].append("ningún arranque cumple la puerta del gancho (hueco > 150 ms en 0–3 s)")
    if end_at is None:
        n = int(np.ceil(duration / bar_s)) + 1
        seq, spl = _greedy_path(tb, start, n, last, 0.0, avoid)
        y = _render_path(x, tb, seq, 0.0, sr, xf_s)
        if len(y) < N:
            y = np.vstack([y, np.zeros((N - len(y), y.shape[1]))])
            info["warnings"].append("la pista no da para toda la duración")
        y = y[:N].copy()
        nf = min(int(fade_out_s * sr), len(y))
        y[-nf:] *= np.cos(np.linspace(0, np.pi / 2, nf))[:, None]
        info.update({"method": "camino_por_compases", "splices": spl, "repeated_bars": len(seq) - len(set(seq)),
                     "max_bar_plays": _max_plays(seq)})
        info["beats_prog_s"], info["downbeats_prog_s"] = _prog_beats(tb, beats, seq, 0.0, duration)
        used_end = duration - fade_out_s
    # gancho hasta la primera salida de la música: sin paradas (> 150 ms) → relleno con el compás vecino
    hu = max(HOOK_S, float(hook_until or 0.0))
    bar_prog = bar_s * (1.0 / info.get("tempo_factor", 1.0) if info.get("tempo_factor") else 1.0)
    y, info["hook_patches"] = patch_hook_gaps(y, sr, min(hu, len(y) / sr), bar_prog, tb["I"])
    info["hook_until_s"] = round(hu, 3)
    y[: int(0.01 * sr)] *= np.linspace(0, 1, int(0.01 * sr))[:, None]
    info["xfade_s"] = round(xf_s, 3)
    info["sparse_frac"] = sparse_fraction(y, 0.0, used_end, sr)            # el gancho cuenta: desde 0 s
    info["sparse_frac_hook_0_3s"] = sparse_fraction(y, 0.0, 3.0, sr) if len(y) > 3 * sr else None
    info["hook_gaps"] = hook_gaps(y, sr, hu, tb["I"])
    bad = [sp for sp in info["splices"] if sp["dist"] >= SPLICE_MAX_DIST or sp["near_avoid"] or not sp["phrase_ok"]]
    loops = int(info.get("max_bar_plays") or 1) > MAX_BAR_PLAYS
    info["ok"] = info["sparse_frac"] <= SPARSE_MAX and not bad and not info["hook_gaps"] and not loops
    if loops:
        info["warnings"].append(f"bucle audible: un compás de la fuente suena {info['max_bar_plays']} veces "
                                f"(máx. {MAX_BAR_PLAYS})")
    if info["hook_gaps"]:
        info["warnings"].append(f"huecos en el gancho (0–{hu:.1f} s): {info['hook_gaps']}")
    if info["sparse_frac"] > SPARSE_MAX:
        info["warnings"].append(f"tramo usado con {info['sparse_frac']:.0%} de ventanas dispersas (> 10 %)")
    for sp in bad:
        info["warnings"].append(f"empalme en {sp['prog_s']} s con distancia {sp['dist']}"
                                + (" junto a una cue" if sp["near_avoid"] else "")
                                + ("" if sp["phrase_ok"] else " fuera de fraseo"))
    return y.astype(np.float32), info


# ───────────────────────────── API ─────────────────────────────
class MusicResult(dict):
    """dict con acceso por atributo (y campos de `spec.Asset`): sirve a `mix`/tests (dict) y al resolver de assets
    (`a.path`, `a.license`, `a.notes`, `a.origin`, `a.source_url`, `a.model_dump()`)."""

    def __getattr__(self, k):
        if k in self:
            return self[k]
        asset = dict.get(self, "asset") or {}
        if k in asset:
            return asset[k]
        if k in ("source_url", "sha256", "width", "height"):
            return asset.get(k)
        raise AttributeError(k)

    def model_dump(self) -> dict:
        from cutkit.spec import Asset
        return Asset(**self["asset"]).model_dump()


def _register(entry: dict) -> None:
    LIBRARY.mkdir(parents=True, exist_ok=True)
    with open(LIBRARY / "registro.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _license_text(model: str, date: str) -> str:
    return (f"Generada con Google Lyria ({model}) vía Gemini API el {date}; lleva marca de agua SynthID inaudible; "
            f"sujeta a los términos de la Gemini API y a su política de uso del contenido generado. "
            f"Pista única por brief; prompt y respuesta guardados en meta.json.")


def _parse_brief(brief) -> dict:
    if brief is None:
        return {}
    if isinstance(brief, dict):
        return dict(brief)
    s = str(brief).strip()
    if s.startswith("{"):
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            pass
    return {"mood": s} if s else {}


def _new_track(b: dict, h: str, duration: float, models, warnings: list[str]) -> dict | None:
    """Genera con Lyria (lyria-3.5 → pro → clip) y guarda meta + registro. None si todo falla."""
    cdir = LIBRARY / h
    cdir.mkdir(parents=True, exist_ok=True)
    prompt = build_prompt(b, duration)
    today = _dt.date.today().isoformat()
    for model in dict.fromkeys(models or (b.get("model", "lyria-3.5"), "lyria-3-pro-preview", "lyria-3-clip-preview")):
        try:
            src, info = _generate(model, prompt, cdir / f"source_{model.replace('.', '_')}")
        except Exception as e:                       # noqa: BLE001 — registro y siguiente modelo
            warnings.append(f"{model} falló: {type(e).__name__}: {str(e)[:300]}")
            continue
        meta = {"hash": h, "brief": b, "prompt": prompt, "model": model, "origin": "music_gen",
                "source": str(src), "created": _dt.datetime.now().isoformat(timespec="seconds"),
                "license": _license_text(model, today), "license_verified": True,
                "synthid": True, "response": info, "cost_usd": COST_USD.get(model, 0.08)}
        _analyze_meta(meta, b)
        (cdir / "meta.json").write_text(d.to_json(meta))
        _register({k: meta[k] for k in ("hash", "model", "origin", "source", "created", "license",
                                        "license_verified", "cost_usd")} | {"brief_use": b.get("use")})
        return meta
    return None


def _analyze_meta(meta: dict, b: dict | None = None) -> dict:
    xs = d.load(meta["source"], channels=2)
    meta["source_duration_s"] = round(len(xs) / d.SR, 3)
    if "beats" not in meta:
        bb = (b or meta.get("brief") or {}).get("bpm", 102)
        hint = float(np.mean(bb)) if isinstance(bb, (list, tuple)) else float(bb)
        meta["beats"] = analyze_beats(xs, bpm_hint=hint)
    meta["source_lufs"] = round(d.integrated_lufs(xs), 2)
    tb = bar_table(xs, meta["beats"])
    meta["groove_start_s"] = groove_start(xs, meta["beats"], table=tb)
    meta["breakdowns_src_s"] = breakdowns(xs, meta["beats"], table=tb)
    meta["dense_bars"] = int(sum(bb["dense"] for bb in tb["bars"]))
    meta["analysis_version"] = FIT_VERSION
    return meta


def _load_meta(h: str) -> dict | None:
    p = LIBRARY / h / "meta.json"
    if not p.exists():
        return None
    meta = json.loads(p.read_text())
    src = Path(meta.get("source", ""))
    if not src.exists():
        # la carpeta del producto se movió (rutas absolutas viejas): la fuente vive junto a meta.json
        local = p.parent / src.name
        if not (src.name and local.exists()):
            return None
        meta["source"] = str(local)
        p.write_text(d.to_json(meta))
    if meta.get("analysis_version") != FIT_VERSION:
        _analyze_meta(meta)
        p.write_text(d.to_json(meta))
    return meta


def _fit_track(meta: dict, duration: float, end_at, avoid, out_dir: Path, hook_until: float | None = None) -> tuple[Path, dict]:
    key = hashlib.sha1(json.dumps([round(end_at, 3) if end_at is not None else None,
                                   [round(a, 2) for a in sorted(avoid or [])],
                                   round(hook_until, 3) if hook_until else None]).encode()).hexdigest()[:8]
    tag = f"fit{FIT_VERSION}_{duration:.2f}s_{key}.wav"
    fit_p = (LIBRARY / meta["hash"] / tag) if meta["origin"] == "music_gen" else out_dir / f"library_{tag}"
    if fit_p.exists() and fit_p.with_suffix(".json").exists():
        return fit_p, json.loads(fit_p.with_suffix(".json").read_text())
    xs = d.load(meta["source"], channels=2)
    y, info = fit_to_duration(xs, duration, meta["beats"], end_at=end_at, avoid_times=avoid or [], hook_until=hook_until)
    d.write(fit_p, y)
    fit_p.with_suffix(".json").write_text(d.to_json(info))
    return fit_p, info


def _score(info: dict) -> float:
    """Menor es mejor: dispersión + peor empalme + 0,05 por empalme + 0,1 por compás de la fuente que se repite
    (bucle audible) + 1 si no pasa el control."""
    worst = max([sp["dist"] for sp in info.get("splices", [])] or [0.0])
    return (info.get("sparse_frac", 1.0) + worst + 0.05 * len(info.get("splices", []))
            + 0.1 * info.get("repeated_bars", 0) + (0 if info.get("ok") else 1.0))


_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}_")


def _slug_of(out_dir: Path) -> str | None:
    """`<proyecto>/edicion/media` (o `<CUTKIT_RUNS>/<slug>/edit/media`) → slug, sin la fecha del proyecto."""
    p = Path(out_dir).resolve()
    if p.parent.name in ("edicion", "edit") and len(p.parents) > 1:
        return _FECHA.sub("", p.parents[1].name)
    return None


def _cliente_de(out_dir: Path) -> str | None:
    """`clientes/<cliente>/creativos/<proyecto>/edicion/media` → cliente."""
    try:
        rel = Path(out_dir).resolve().relative_to(CLIENTES.resolve())
    except ValueError:
        return None
    return rel.parts[0] if len(rel.parts) > 2 and rel.parts[1] == "creativos" else None


def recent_tracks(exclude_slug: str | None = None, n: int = RECENT_SHORTS, timelines=None) -> list[dict]:
    """Pista de la cama de los últimos `n` vídeos montados (otros slugs), del más reciente al más antiguo: la del ítem
    `a_music` de la timeline más reciente de cada proyecto (`<proyecto>/edicion/versions/<vid>/timeline.json`),
    ordenadas por la fecha de esa timeline (a igualdad, por slug). [{slug, version, hash, mtime}]."""
    rx = re.compile(r"^music_(.+)_\d+(?:\.\d+)?s\.wav$")
    last: dict[str, tuple[float, str, str]] = {}
    for tl in (timelines if timelines is not None else all_timelines()):
        slug = _FECHA.sub("", tl.parents[3].name)
        if slug == exclude_slug:
            continue
        try:
            mt = tl.stat().st_mtime
            if slug in last and last[slug][0] >= mt:
                continue
            audio = json.loads(tl.read_text()).get("audio") or []
        except Exception:                              # noqa: BLE001 — timeline a medio escribir o rota
            continue
        m = next((rx.match(Path(a.get("path", "")).name) for a in audio if a.get("kind") == "music"), None)
        if m:
            last[slug] = (mt, tl.parent.name, m.group(1))
    order = sorted(last.items(), key=lambda kv: (-kv[1][0], kv[0]))[: max(0, n)]
    return [{"slug": s, "version": v, "hash": h, "mtime": round(mt, 1)} for s, (mt, v, h) in order]


def pistas_cliente(cliente: str | None) -> list[Path]:
    """Pistas del cliente (`clientes/<cliente>/marca/musica/`), por nombre."""
    if not cliente:
        return []
    carpeta = CLIENTES / cliente / "marca" / "musica"
    return sorted(p for p in carpeta.glob("*") if p.suffix.lower() in EXT_AUDIO and p.is_file()) if carpeta.is_dir() else []


def _resolver_pista(track: str, cliente: str | None) -> Path | None:
    """`track` como archivo: ruta absoluta, relativa a la raíz del producto o nombre dentro de `marca/musica/`."""
    cands = [Path(track).expanduser(), RAIZ / track]
    if cliente:
        cands.append(CLIENTES / cliente / "marca" / "musica" / track)
    return next((c for c in cands if c.suffix.lower() in EXT_AUDIO and c.is_file()), None)


def _licencia_archivo(ruta: Path) -> tuple[str, bool]:
    """Licencia de una pista propia: `<pista>.licencia.txt` o `LICENCIA.txt` de su carpeta (primera línea)."""
    for f in (ruta.with_suffix(ruta.suffix + ".licencia.txt"), ruta.with_name("LICENCIA.txt")):
        if f.exists():
            txt = f.read_text(encoding="utf-8", errors="ignore").strip()
            if txt:
                return txt.splitlines()[0][:300], True
    return ("Pista aportada por el usuario SIN licencia documentada: antes de publicar, confirma que permite usarla en "
            "publicidad (en anuncios de Reels no vale música con licencia comercial) y documenta su origen en "
            f"{ruta.name}.licencia.txt."), False


def _meta_archivo(ruta: Path, b: dict) -> dict:
    """Meta de una pista de archivo (cliente o `track`), cacheada por ruta + tamaño + fecha de modificación."""
    st = ruta.stat()
    h = "lib_" + hashlib.sha1(f"{ruta.resolve()}|{st.st_size}|{st.st_mtime_ns}".encode()).hexdigest()[:10]
    cache = LIBRARY / h / "meta.json"
    if cache.exists():
        meta = json.loads(cache.read_text())
        if meta.get("analysis_version") == FIT_VERSION:
            return meta
    lic, ok = _licencia_archivo(ruta)
    meta = {"hash": h, "brief": b, "prompt": None, "model": None, "origin": "library", "source": str(ruta),
            "created": _dt.datetime.now().isoformat(timespec="seconds"), "license": lic, "license_verified": ok,
            "synthid": False, "cost_usd": 0.0}
    _analyze_meta(meta, b)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(d.to_json(meta))
    _register({k: meta[k] for k in ("hash", "model", "origin", "source", "created", "license",
                                    "license_verified", "cost_usd")} | {"brief_use": b.get("use")})
    return meta


def library_tracks(use: str | None = None) -> list[str]:
    """Hashes de pistas generadas en caché (opcionalmente del mismo `use`)."""
    out = []
    for p in sorted(LIBRARY.glob("*/meta.json")):
        try:
            m = json.loads(p.read_text())
        except Exception:                              # noqa: BLE001
            continue
        if m.get("origin") == "music_gen" and (use is None or (m.get("brief") or {}).get("use") == use):
            out.append(m["hash"])
    return out


def ensure(brief: dict | str | None, duration: float, out_dir: str | Path, *, allow_generate: bool = True,
           models: tuple[str, ...] | None = None, end_at: float | None = None,
           avoid_times: list[float] | None = None, track: str | None = None, max_new: int = 1,
           library_pick: bool = True, hook_until: float | None = None, slug: str | None = None,
           recent_n: int = RECENT_SHORTS, cliente: str | None = None) -> MusicResult:
    """Devuelve la cama musical encajada a `duration` (WAV 48 kHz estéreo en `out_dir`).

    Selección: `track` (o `brief["track"]`; en el plan, `tokens.music_track`) fuerza una pista: un archivo (ruta, o
    nombre dentro de `clientes/<cliente>/marca/musica/`) o el hash de una pista generada en caché. Si no, compiten las
    pistas del cliente, la del brief si ya está en caché y, con `library_pick` (por defecto), las demás generadas del
    mismo `use`; gana la de mejor puntuación (dispersión + peor empalme + nº de empalmes; la del brief con −0,02) más
    RECENT_PENALTY por cada uno de los últimos `recent_n` vídeos (otros slugs) en que ya sonó. Solo con
    `CK_MUSICA_IA=1` (y `allow_generate`) se genera con Lyria la pista del brief si no hay ninguna candidata, o hasta
    `max_new` variante(s) si ninguna pasa el control (> 10 % disperso o empalme ≥ 0,1). Sin candidatas: `SinMusica`.
    `cliente` y `slug` salen de `out_dir` (`clientes/<c>/creativos/<proyecto>/edicion/media`) si no se dan.
    `end_at`, `avoid_times` y `hook_until` (primera salida de la música: hasta ahí, ninguna parada > 150 ms) se pasan
    a `fit_to_duration`. Resultado: dict con acceso por atributo (ver MusicResult).
    """
    b = _brief(_parse_brief(brief))
    track = track or b.pop("track", None)
    h = brief_hash(b)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cliente = cliente or _cliente_de(out_dir)
    allow_generate = allow_generate and musica_ia_activa()
    warnings: list[str] = []
    cost, cache_hit, tried = 0.0, True, []
    slug = slug or _slug_of(out_dir)
    try:
        recent = recent_tracks(slug, recent_n) if recent_n > 0 else []
    except Exception:                                  # noqa: BLE001 — sin historial: sin penalización
        recent = []
    uses = {}
    for r in recent:
        uses.setdefault(r["hash"], []).append(r["slug"])

    def penalty(meta) -> float:
        return RECENT_PENALTY * len(uses.get(meta["hash"], []))

    def evaluate(meta):
        fp, inf = _fit_track(meta, duration, end_at, avoid_times, out_dir, hook_until)
        tried.append({"hash": meta["hash"], "ok": inf.get("ok"), "sparse_frac": inf.get("sparse_frac"),
                      "splices": len(inf.get("splices", [])), "score": round(_score(inf), 4),
                      "max_bar_plays": inf.get("max_bar_plays"),
                      "recent_uses": uses.get(meta["hash"], []), "recent_penalty": penalty(meta)})
        return (meta, fp, inf)

    chosen = None
    if track:
        archivo = _resolver_pista(str(track), cliente)
        meta = _meta_archivo(archivo, b) if archivo else _load_meta(str(track))
        if meta is None:
            raise SinMusica(f"no encuentro la pista «{track}» (ni como archivo ni en la caché {LIBRARY})")
        chosen = evaluate(meta)
        if int(chosen[2].get("max_bar_plays") or 1) > MAX_BAR_PLAYS:
            warnings.append(f"la pista fijada {track} sonaría en bucle (un compás {chosen[2]['max_bar_plays']} veces, "
                            f"máx. {MAX_BAR_PLAYS}): se respeta porque la fija el plan; quita `tokens.music_track` "
                            f"para que se elija una sin bucle")
    else:
        propias = []
        for p in pistas_cliente(cliente):
            try:
                propias.append(evaluate(_meta_archivo(p, b)))
            except Exception as e:                     # noqa: BLE001 — archivo ilegible: aviso y siguiente
                warnings.append(f"no puedo leer la pista {p.name}: {type(e).__name__}: {str(e)[:200]}")
        meta = _load_meta(h)
        if meta is None and allow_generate and not propias:
            cache_hit = False
            meta = _new_track(b, h, duration, models, warnings)
            cost += (meta or {}).get("cost_usd", 0.0)
        cands = propias + ([evaluate(meta)] if meta else [])
        if library_pick or not (cands and cands[0][2].get("ok")):
            for oh in library_tracks(b.get("use")):
                if oh != h and (om := _load_meta(oh)) is not None:
                    if om.get("source_duration_s", 0) < 0.5 * duration:     # demasiado corta: bucle audible
                        tried.append({"hash": oh, "ok": False, "why": "fuente < 0,5 × duración"})
                        continue
                    cands.append(evaluate(om))
            n_new = 0
            while allow_generate and n_new < max_new and not any(c[2].get("ok") for c in cands):
                n_new += 1
                vb = {**b, "_variant": n_new}
                vh = brief_hash(vb)
                vm = _load_meta(vh)
                if vm is None:
                    vm = _new_track(vb, vh, duration, models, warnings)
                    if vm is None:
                        break
                    cost += vm.get("cost_usd", 0.0)
                cands.append(evaluate(vm))
        if len(cands) > 1:
            cands = [c for c in cands if c[0].get("source_duration_s", 0) >= 0.5 * duration] or cands
        # 20-oct: guarda de BUCLE real (no solo la duración de la fuente: una pista de 114 s con 62 s de compases densos
        # sonaba 4 veces el mismo tramo de 8 compases en 102 s). Ninguna pista cuyo encaje haga sonar un compás más de
        # MAX_BAR_PLAYS veces, por mucha penalización de repetición que pague otra; si todas lo harían, la que menos
        loopy = [c for c in cands if int(c[2].get("max_bar_plays") or 1) > MAX_BAR_PLAYS]
        if loopy and len(loopy) < len(cands):
            for c in loopy:
                warnings.append(f"descarto {c[0]['hash']}: sonaría en bucle (un compás {c[2]['max_bar_plays']} veces)")
            cands = [c for c in cands if c not in loopy]
        elif loopy:
            least = min(int(c[2].get("max_bar_plays") or 1) for c in cands)
            cands = [c for c in cands if int(c[2].get("max_bar_plays") or 1) == least]
            warnings.append(f"todas las pistas sonarían en bucle (mínimo {least} veces un compás): hace falta una pista "
                            f"nueva más larga")
        if cands:
            # la del brief tiene una ventaja pequeña (estabilidad); si otra de la biblioteca encaja mejor, gana esa.
            # + RECENT_PENALTY por cada vídeo reciente (otro slug) en que ya sonó
            chosen = min(cands, key=lambda c: _score(c[2]) + penalty(c[0]) - (0.02 if c[0]["hash"] == h else 0.0))
            if chosen[0]["hash"] != h:
                warnings.append(f"uso la pista {Path(chosen[0]['source']).name if chosen[0]['origin'] == 'library' else chosen[0]['hash']}"
                                " (la que mejor encaja)")
            if uses.get(chosen[0]["hash"]):
                warnings.append(f"la pista {chosen[0]['hash']} ya sonó en {len(uses[chosen[0]['hash']])} de los últimos "
                                f"{len(recent)} vídeos ({', '.join(uses[chosen[0]['hash']])}): las demás encajan peor; "
                                f"para otra, `tokens.music_track` en el plan")
    if chosen is None:
        donde = f"clientes/{cliente}/marca/musica/" if cliente else "clientes/<cliente>/marca/musica/"
        motivo = (" | ".join(warnings) if warnings else
                  "pon una pista con licencia para publicidad en " + donde + ", fíjala con `tokens.music_track` (o "
                  "`--musica` en `ck anuncio`) o activa la generación con Lyria (de pago) con CK_MUSICA_IA=1")
        raise SinMusica(motivo)
    meta, fit_p, fit_info = chosen
    warnings += fit_info.get("warnings", [])
    beats = meta["beats"]
    if beats.get("confidence", 0) < 0.3:
        warnings.append(f"rejilla de pulso con confianza baja ({beats.get('confidence')}): no cortar imagen a ritmo")
    final = out_dir / f"music_{meta['hash']}_{duration:.2f}s.wav"
    if final.resolve() != fit_p.resolve():
        final.write_bytes(fit_p.read_bytes())
    # sidecar: `mix` lee de aquí los pulsos en tiempo de programa (reentradas de drop-outs al pulso)
    final.with_suffix(".json").write_text(d.to_json({"hash": meta["hash"], "bpm": beats.get("bpm"), "fit": fit_info}))
    lufs = d.integrated_lufs(d.load(final, channels=2))
    sha = hashlib.sha256(final.read_bytes()).hexdigest()
    asset = {"id": f"music_{meta['hash']}", "kind": "audio", "path": str(final), "sha256": sha,
             "origin": "music_gen" if meta["origin"] == "music_gen" else "library",
             "license": meta["license"], "duration": round(duration, 3),
             "notes": f"{meta.get('model') or 'biblioteca'} · {beats.get('bpm')} BPM · {fit_info.get('method')}"
                      f" · {len(fit_info.get('splices', []))} empalmes · disperso {fit_info.get('sparse_frac')}"}
    return MusicResult({
        "path": str(final), "source": meta["source"], "origin": meta["origin"], "license": meta["license"],
        "license_verified": meta["license_verified"], "model": meta.get("model"), "prompt": meta.get("prompt"),
        "hash": meta["hash"], "brief_hash": h, "bpm": beats.get("bpm"), "bar_s": beats.get("bar_s"),
        "downbeats": beats.get("downbeats"), "beat_confidence": beats.get("confidence"),
        "source_duration_s": meta.get("source_duration_s"), "fit": fit_info, "lufs": round(lufs, 2),
        "candidates": tried, "recent": recent, "cache_hit": cache_hit, "cost_usd": cost, "warnings": warnings,
        "asset": asset})
