"""Transcripción local con marcas de tiempo por palabra (faster-whisper, MIT) + alineado al guion.

Se usa para:
  - subtítulos palabra a palabra exactos (el texto sale del guion; los tiempos, del audio),
  - QA: WER entre lo que se oye y lo que dice el guion (palabras corruptas, frases cortadas).
Coste: CPU local (≈1–2× tiempo real en un portátil reciente con el modelo `small` int8).
"""

from __future__ import annotations

import difflib
import re
import time
import unicodedata
from functools import lru_cache

from ..costs import record_local
from ..models import Asset, Word
from ..store import ctx

MODEL_SIZE = "small"


@lru_cache(maxsize=1)
def _model():
    from faster_whisper import WhisperModel

    # usa la caché estándar de Hugging Face (el modelo puede estar ya descargado por otras herramientas)
    return WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")


def norm(w: str) -> str:
    w = unicodedata.normalize("NFKD", w.lower())
    w = "".join(c for c in w if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9ñ]+", "", w)


def _chars(text: str) -> str:
    return "".join(norm(x) for x in text.split())


def cer_in(hyp: str, ref: str) -> float:
    """Error por caracteres de `ref` dentro de `hyp` (alineamiento local: el inicio y el final en `hyp` son libres).

    Insensible a cómo el ASR segmenta las palabras («bájatela» ↔ «bájate la») y a la puntuación, pero estricto con
    el contenido: cambiar una palabra de 6 letras en una frase de 90 caracteres ≈ 0,07.
    """
    r, h = _chars(ref), _chars(hyp)
    if not r:
        return 0.0
    if not h:
        return 1.0
    prev = [0] * (len(h) + 1)  # empezar en cualquier punto de h no cuesta
    for i in range(1, len(r) + 1):
        cur = [i] + [0] * len(h)
        ri = r[i - 1]
        for j in range(1, len(h) + 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ri != h[j - 1]))
        prev = cur
    return min(prev) / len(r)  # terminar en cualquier punto de h no cuesta


def wer(ref: str, hyp: str) -> float:
    r = [norm(x) for x in ref.split() if norm(x)]
    h = [norm(x) for x in hyp.split() if norm(x)]
    if not r:
        return 0.0 if not h else 1.0
    d = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]
    for i in range(len(r) + 1):
        d[i][0] = i
    for j in range(len(h) + 1):
        d[0][j] = j
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (0 if r[i - 1] == h[j - 1] else 1))
    return d[len(r)][len(h)] / len(r)


def repeated_spans(phrases: list[tuple[float, float, list[Word]]], script_text: str, min_words: int = 2) -> list[tuple[float, float]]:
    """Repeticiones que mete el modelo de vídeo y el guion no tiene («por la mañana… por la mañana»): el principio de
    una frase copia el final de la anterior. Devuelve el tramo a quitar: la frase entera si solo es la repetición, o
    su arranque hasta la primera palabra nueva. Una mala transcripción («las acudes» por «la sacudes») no cuenta."""
    script = " ".join(norm(t) for t in script_text.split())
    out = []
    for (_s0, _e0, w0), (s1, e1, w1) in zip(phrases, phrases[1:]):
        t0, t1 = [norm(w.text) for w in w0], [norm(w.text) for w in w1]
        for k in range(min(len(t0), len(t1)), min_words - 1, -1):
            if difflib.SequenceMatcher(a="".join(t0[-k:]), b="".join(t1[:k]), autojunk=False).ratio() < 0.8:
                continue
            if " ".join(t0[-k:] + t1[:k]) not in script:  # el guion no repite a propósito
                out.append((s1, e1 if k == len(w1) else max(s1, w1[k].start - 0.03)))
            break
    return out


def align(script_text: str, asr_words: list[Word]) -> list[Word]:
    """Pone los tiempos del ASR sobre las palabras exactas del guion (difflib + interpolación)."""
    toks = script_text.split()
    if not toks:
        return []
    if not asr_words:
        return []
    a = [norm(t) for t in toks]
    b = [norm(w.text) for w in asr_words]
    times: list[tuple[float, float] | None] = [None] * len(toks)
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            w = asr_words[blk.b + k]
            times[blk.a + k] = (w.start, w.end)
    # interpolar huecos
    total_end = asr_words[-1].end
    i = 0
    while i < len(toks):
        if times[i] is not None:
            i += 1
            continue
        j = i
        while j < len(toks) and times[j] is None:
            j += 1
        left = times[i - 1][1] if i > 0 and times[i - 1] else (asr_words[0].start if i == 0 else 0.0)
        right = times[j][0] if j < len(toks) and times[j] else total_end
        n = j - i
        span = max(right - left, 0.05 * n)
        for k in range(n):
            s = left + span * k / n
            times[i + k] = (s, s + span / n * 0.9)
        i = j
    return [Word(text=t, start=round(st, 3), end=round(max(en, st + 0.05), 3)) for t, (st, en) in zip(toks, times)]  # type: ignore[misc]


class WhisperTranscriber:
    name = "faster-whisper"
    model = MODEL_SIZE

    def __init__(self):
        import faster_whisper  # noqa: F401  (falla pronto si no está instalado)

    def transcribe(self, audio: Asset, locale: str, hint: str | None = None) -> tuple[str, list[Word]]:
        """`hint` = texto esperado como contexto de decodificación (segunda escucha; ver scenes.verify_line)."""
        t0 = time.time()
        lang = (locale or "es").split("-")[0]
        # se decodifica con ffmpeg a numpy (faster-whisper falla con PyAV ≥19 al abrir ficheros)
        from ..media import read_wav_mono

        pcm = read_wav_mono(ctx().assets.abspath(audio), rate=16000)
        if pcm.size < 1600:
            return "", []
        # clip casi en silencio: Whisper «oye» frases inventadas («¡Suscríbete!» en un plano a −67 dB). El VAD de
        # faster-whisper lo evita pero empeora las frases cortas (probado), así que se usa un umbral de energía.
        import numpy as np

        hop = 1600  # 100 ms
        n = pcm.size // hop
        peak_db = 20 * np.log10(np.sqrt((pcm[: n * hop].reshape(n, hop).astype(np.float32) ** 2).mean(axis=1)).max() + 1e-9) if n else -120
        if peak_db < -40:
            return "", []
        segs, _info = _model().transcribe(pcm, language=lang, word_timestamps=True, vad_filter=False, beam_size=5,
                                          initial_prompt=hint or None)
        words: list[Word] = []
        texts = []
        for s in segs:
            texts.append(s.text)
            for w in s.words or []:
                words.append(Word(text=w.word.strip(), start=float(w.start), end=float(w.end)))
        record_local("asr", f"faster-whisper-{MODEL_SIZE}", time.time() - t0)
        return " ".join(t.strip() for t in texts), words

    def phrases(self, audio: Asset, locale: str, min_gap: float = 0.12, pad: float = 0.06) -> list[tuple[float, float, list[Word]]]:
        """Transcribe frase a frase, partiendo por los silencios. Con la toma entera Whisper se «come» las repeticiones
        («por la mañana… por la mañana» sale una sola vez, comprobado); con frases cortas no."""
        import numpy as np

        from ..media import read_wav_mono

        lang = (locale or "es").split("-")[0]
        sr, hop = 16000, 160  # 10 ms
        pcm = read_wav_mono(ctx().assets.abspath(audio), rate=sr)
        n = pcm.size // hop
        if n < 30:
            return []
        db = 20 * np.log10(np.sqrt((pcm[: n * hop].reshape(n, hop).astype(np.float32) ** 2).mean(axis=1)) + 1e-9)
        idx = np.flatnonzero(db > max(np.percentile(db, 10) + 12, db.max() - 45))
        spans: list[list[int]] = []
        for k in idx:
            if spans and k - spans[-1][1] <= int(min_gap * 100):
                spans[-1][1] = int(k)
            else:
                spans.append([int(k), int(k)])
        t0 = time.time()
        out = []
        for a, b in spans:
            if b - a < 15:  # <0,15 s: respiración o chasquido
                continue
            s, e = max(0.0, a / 100 - pad), min(n / 100, (b + 1) / 100 + pad)
            segs, _ = _model().transcribe(pcm[int(s * sr): int(e * sr)], language=lang, word_timestamps=True,
                                          vad_filter=False, beam_size=5)
            ws = [Word(text=w.word.strip(), start=s + float(w.start), end=s + float(w.end)) for sg in segs for w in sg.words or []]
            if ws:
                out.append((round(s, 3), round(e, 3), ws))
        record_local("asr", f"faster-whisper-{MODEL_SIZE}", time.time() - t0)
        return out

    def words(self, audio: Asset, locale: str, text_hint: str = "") -> list[Word]:
        _, words = self.transcribe(audio, locale)
        return align(text_hint, words) if text_hint else words
