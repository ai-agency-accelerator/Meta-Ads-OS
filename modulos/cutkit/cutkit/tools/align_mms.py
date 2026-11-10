# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["torch==2.7.1", "torchaudio==2.7.1", "soundfile", "numpy<2.3"]
# ///
"""Alineación forzada palabra a palabra con MMS_FA (CTC multilingüe de torchaudio).

Uso: uv run --script cutkit/tools/align_mms.py <audio.wav> <words.json> <out.json>
  words.json = ["Hay", "un", "nuevo", ...]  (texto de cada palabra, en orden)
  out.json   = [[s, e, score], ...]  (segundos de la fuente; null si la palabra no se pudo alinear)
Whisper adelanta y agrupa los inicios (varias palabras con el mismo tiempo); esto da tiempos de ±20–40 ms.
"""
import json
import sys
import unicodedata

import numpy as np
import soundfile as sf
import torch
import torchaudio

NUM = {"0": "cero", "1": "uno", "2": "dos", "3": "tres", "4": "cuatro", "5": "cinco", "6": "seis", "7": "siete",
       "8": "ocho", "9": "nueve"}


def norm(w: str) -> str:
    w = unicodedata.normalize("NFKD", w.lower())
    w = "".join(c for c in w if not unicodedata.combining(c))
    w = "".join(NUM.get(c, c) for c in w)
    return "".join(c for c in w if "a" <= c <= "z" or c == "'")


def main() -> None:
    wav, words_p, out_p = sys.argv[1:4]
    words = json.load(open(words_p))
    y, sr = sf.read(wav, dtype="float32", always_2d=True)
    y = torch.from_numpy(y.mean(1)).unsqueeze(0)
    bundle = torchaudio.pipelines.MMS_FA
    if sr != bundle.sample_rate:
        y = torchaudio.functional.resample(y, sr, bundle.sample_rate)
    model = bundle.get_model(with_star=False).eval()
    tokenizer, aligner = bundle.get_tokenizer(), bundle.get_aligner()
    keep = [i for i, w in enumerate(words) if norm(w)]
    toks = [norm(words[i]) for i in keep]
    res: list = [None] * len(words)
    # por bloques de ~25 s con solape para no agotar memoria en brutos largos
    total = y.shape[1] / bundle.sample_rate
    with torch.inference_mode():
        emission, _ = model(y)
    ratio = y.shape[1] / emission.shape[1] / bundle.sample_rate
    spans = aligner(emission[0], tokenizer(toks))
    for k, sp in zip(keep, spans):
        s, e = sp[0].start * ratio, sp[-1].end * ratio
        score = float(np.mean([t.score for t in sp]))
        res[k] = [round(s, 3), round(min(e, total), 3), round(score, 3)]
    json.dump(res, open(out_p, "w"))
    print(f"alineadas {sum(r is not None for r in res)}/{len(words)} palabras")


if __name__ == "__main__":
    main()
