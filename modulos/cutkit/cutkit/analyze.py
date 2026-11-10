"""Análisis determinista de las fuentes → MediaIndex.

- Transcripción verbatim con tiempos por palabra + glosario (`recursos/glosario.yaml` del producto y, si existe,
  `clientes/<cliente>/marca/glosario.yaml`) aplicado palabra a palabra, y ajuste de los inicios de palabra al ataque
  real de la voz (el ASR adelanta ~150 ms).
  Motor de transcripción (`CK_ASR`): `local` (por defecto, whisper.cpp, gratis) u `openai` (whisper-1, ≈0,006 $/min
  con tu OPENAI_API_KEY; solo si lo pides). Nunca se cambia de uno a otro sin pedirlo: así no hay gasto sorpresa.
- Pausas medidas en la señal (no con los tiempos del ASR) y clasificadas por la puntuación que las precede.
- Caras a 10 fps sobre el intermedio (reencuadres, pantalla partida y QA de subtítulos): Apple Vision en Mac si está
  instalado el extra `mac`; en el resto, OpenCV (clasificador Haar incluido en opencv).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import yaml

from . import sistema
from .paths import CLIENTES, DATOS, PAQUETE, MODULO, RECURSOS, cargar_entorno, marca_dir, run_dir
from .spec import FaceSample, MediaIndex, Pause, Source, Word

GLOSARIO = RECURSOS / "glosario.yaml"
WHISPER_MODELO = "ggml-large-v3-turbo-q5_0.bin"


# ───────────────────────────── transcripción ─────────────────────────────
def _whisper(wav48: str, prompt: str, idioma: str = "es") -> dict:
    """whisper-1 de OpenAI (de pago, ≈0,006 $/min). Necesita OPENAI_API_KEY en el .env de la raíz y el extra `ia`."""
    cargar_entorno()
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("falta OPENAI_API_KEY en el .env de la raíz (o usa CK_ASR=local con whisper.cpp)")
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("falta el paquete openai: `uv sync --project modulos/cutkit --extra ia`") from None
    tmp = Path(wav48).with_suffix(".16k.mp3")
    subprocess.run([sistema.requiere("ffmpeg"), "-v", "error", "-y", "-i", wav48, "-ac", "1", "-ar", "16000", "-b:a", "64k",
                    str(tmp)], check=True)
    try:
        with tmp.open("rb") as fh:
            r = OpenAI().audio.transcriptions.create(model="whisper-1", file=fh, language=idioma,
                                                     response_format="verbose_json",
                                                     timestamp_granularities=["word", "segment"], prompt=prompt)
    finally:
        tmp.unlink(missing_ok=True)
    return r.model_dump()


def modelo_whisper_local() -> Path:
    """Modelo de whisper.cpp: `CK_WHISPER_MODELO`, `modulos/cutkit/datos/modelos/` o la caché habitual del usuario."""
    env = os.environ.get("CK_WHISPER_MODELO")
    for c in ([Path(env)] if env else []) + [DATOS / "modelos" / WHISPER_MODELO,
                                              Path.home() / ".cache" / "whisper-cpp" / WHISPER_MODELO]:
        if c.exists():
            return c
    raise RuntimeError(f"no encuentro el modelo de whisper.cpp ({WHISPER_MODELO}): descárgalo con `ck instalar --whisper` "
                       "o indica su ruta en CK_WHISPER_MODELO")


def _whisper_local(wav48: str, prompt: str, idioma: str = "es") -> dict:
    """whisper.cpp con la misma forma que whisper-1: `words` con tiempos y `segments` con su texto.
    Un segmento por palabra (`-ml 1 -sow`): el texto lleva la puntuación pegada, que _seg_punct recupera."""
    cli = shutil.which("whisper-cli") or shutil.which("whisper-cpp")
    if not cli:
        raise RuntimeError(f"falta whisper.cpp ({sistema.arreglo('whisper-cli')})")
    modelo = modelo_whisper_local()
    tmp = Path(wav48).with_suffix(".16k.wav")
    subprocess.run([sistema.requiere("ffmpeg"), "-v", "error", "-y", "-i", wav48, "-ac", "1", "-ar", "16000", str(tmp)],
                   check=True)
    out = tmp.parent / f"{tmp.stem}.asr"   # whisper-cli añade «.json»
    salida = Path(f"{out}.json")
    args = [cli, "-m", str(modelo), "-f", str(tmp), "-l", idioma, "-ml", "1", "-sow", "-oj", "-of", str(out), "-np",
            "-t", str(max(1, min(8, (os.cpu_count() or 4) - 1)))]
    if prompt:
        args += ["--prompt", prompt]
    try:
        subprocess.run(args, check=True, capture_output=True)
        js = json.loads(salida.read_text(encoding="utf-8"))
    finally:
        tmp.unlink(missing_ok=True)
        salida.unlink(missing_ok=True)
    words, segments = [], []
    for s in js.get("transcription", []):
        txt = s["text"].strip()
        palabra = re.sub(r"^[¿¡\"«]+|[.,;:?!…\"»]+$", "", txt)
        if not palabra:
            if segments:   # puntuación suelta: va con la palabra anterior
                segments[-1]["text"] += txt
            continue
        a, b = s["offsets"]["from"] / 1000, s["offsets"]["to"] / 1000
        words.append({"word": palabra, "start": a, "end": b})
        segments.append({"text": txt, "start": a, "end": b})
    return {"text": " ".join(x["text"] for x in segments), "words": words, "segments": segments, "asr": "whisper.cpp"}


def asr(wav48: str, prompt: str = "", modo: str | None = None, idioma: str | None = None) -> dict:
    """Transcribe con el motor pedido (`modo` o `CK_ASR`; por defecto `local`). No cambia de motor por su cuenta."""
    modo = (modo or os.environ.get("CK_ASR") or "local").lower()
    idioma = idioma or os.environ.get("CK_IDIOMA") or "es"
    if modo == "openai":
        print("[asr] transcripción con whisper-1 de OpenAI (de pago, ≈0,006 $/min)")
        return _whisper(wav48, prompt, idioma)
    if modo != "local":
        raise RuntimeError(f"CK_ASR={modo!r} no válido (local | openai)")
    return _whisper_local(wav48, prompt, idioma)


_asr = asr  # nombre antiguo


def _glossary(cliente: str | None = None) -> list[tuple[re.Pattern, str]]:
    """Glosario del producto + el del cliente (`clientes/<cliente>/marca/glosario.yaml`, que manda)."""
    palabras: dict = {}
    for f in (GLOSARIO, (marca_dir(cliente) / "glosario.yaml") if cliente else None):
        if f is not None and f.exists():
            palabras.update((yaml.safe_load(f.read_text(encoding="utf-8")) or {}).get("palabras") or {})
    return [(re.compile(rf"^(?:{k})$", re.I), v) for k, v in palabras.items()]


def _seg_punct(segments: list[dict], words: list[dict]) -> list[str]:
    """Puntuación tras cada palabra, reconstruida desde el texto de los segmentos de whisper."""
    out = [""] * len(words)
    text = " ".join(s["text"].strip() for s in segments)
    toks = re.findall(r"[\wáéíóúüñÁÉÍÓÚÜÑ'%$€\-]+|[.,;:?!¿¡…]", text)
    wi = 0
    for i, t in enumerate(toks):
        if re.match(r"[.,;:?!…]", t):
            if wi > 0:
                out[wi - 1] += t
            continue
        if re.match(r"[¿¡]", t):
            continue
        if wi < len(words):
            wi += 1
    return out


def _envelope(wav: str, hop: float = 0.01) -> tuple[np.ndarray, float]:
    y, sr = sf.read(wav, dtype="float32", always_2d=False)
    if y.ndim > 1:
        y = y.mean(1)
    h = int(sr * hop)
    n = len(y) // h
    rms = np.sqrt((y[: n * h].reshape(n, h) ** 2).mean(1) + 1e-12)
    return 20 * np.log10(rms + 1e-9), hop


def _voiced(db: np.ndarray) -> np.ndarray:
    speech_lvl = np.percentile(db, 80)
    return db > speech_lvl - 24


def _cliente_de_ruta(p: Path) -> str | None:
    """Cliente dueño de una carpeta de trabajo (`clientes/<cliente>/creativos/…`); None fuera del producto."""
    try:
        return p.resolve().relative_to(CLIENTES.resolve()).parts[0]
    except (ValueError, IndexError):
        return None


def transcribe_source(src: Source, prompt: str) -> list[Word]:
    rd = Path(src.mezzanine).parent
    cache = rd / f"asr_{src.id}.json"
    j = json.loads(cache.read_text()) if cache.exists() else asr(src.audio, prompt)
    cache.write_text(json.dumps(j, ensure_ascii=False))
    raw = j.get("words") or []
    punct = _seg_punct(j.get("segments") or [], raw)
    gl = _glossary(_cliente_de_ruta(rd))
    db, hop = _envelope(src.audio)
    voiced = _voiced(db)
    words: list[Word] = []
    for i, w in enumerate(raw):
        t = w["word"].strip()
        txt = t
        for pat, rep in gl:
            if pat.match(t):
                txt = rep
                break
        s, e = float(w["start"]), float(w["end"])
        # ajustar el inicio al ataque de voz más cercano (±0,2 s) si hay un silencio justo antes
        k = int(s / hop)
        lo, hi = max(1, k - 20), min(len(voiced) - 1, k + 8)
        for j2 in range(lo, hi):
            if not voiced[j2 - 1] and voiced[j2]:
                if abs(j2 - k) <= 20:
                    s = j2 * hop
                    break
        if e <= s:
            e = s + 0.08
        words.append(Word(id=f"{src.id}_w{i:04d}", src=src.id, text=txt, raw=t if txt != t else None, s=round(s, 3),
                          e=round(e, 3), punct_after=punct[i] if i < len(punct) else ""))
    return words


def measure_pauses(src: Source, words: list[Word]) -> list[Pause]:
    db, hop = _envelope(src.audio)
    voiced = _voiced(db)
    pauses: list[Pause] = []
    for a, b in zip(words, words[1:]):
        lo, hi = int(a.e / hop) - 15, int(b.s / hop) + 15
        lo, hi = max(lo, 0), min(hi, len(voiced))
        seg = voiced[lo:hi]
        # tramo de silencio más largo entre las dos palabras
        best, cur, start, bs = 0, 0, 0, 0
        for i, v in enumerate(seg):
            if not v:
                if cur == 0:
                    start = i
                cur += 1
                if cur > best:
                    best, bs = cur, start
            else:
                cur = 0
        if best * hop >= 0.12:
            s = (lo + bs) * hop
            e = s + best * hop
            p = a.punct_after
            kind = ("aire_muerto" if e - s > 1.0 else "fin_frase" if re.search(r"[.?!…]", p) else
                    "coma" if re.search(r"[,;:]", p) else "interna")
            pauses.append(Pause(src=src.id, s=round(s, 3), e=round(e, 3), kind=kind))
    return pauses


# ───────────────────────────── caras ─────────────────────────────
def _detector_caras():
    """Función gris (H×W uint8) → [(x, y, w, h) normalizados, origen arriba-izquierda], de mayor a menor área.

    Apple Vision en Mac (extra `mac`); OpenCV con el clasificador Haar que trae opencv en el resto (o si Vision falta)."""
    import cv2

    if sys.platform == "darwin" and os.environ.get("CK_CARAS", "auto") != "opencv":
        try:
            import Vision  # pyobjc (extra `mac`)
            from Foundation import NSData

            def vision(fr):
                ok, buf = cv2.imencode(".png", fr)
                data = NSData.dataWithBytes_length_(buf.tobytes(), len(buf))
                req = Vision.VNDetectFaceRectanglesRequest.alloc().init()
                Vision.VNImageRequestHandler.alloc().initWithData_options_(data, None).performRequests_error_([req], None)
                res = sorted(req.results() or [], key=lambda r: -r.boundingBox().size.width * r.boundingBox().size.height)
                return [(bb.origin.x, 1 - bb.origin.y - bb.size.height, bb.size.width, bb.size.height)
                        for bb in (r.boundingBox() for r in res)]
            return vision
        except ImportError:
            pass
    casc = cv2.CascadeClassifier(str(Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"))

    def haar(fr):
        h, w = fr.shape[:2]
        caras = casc.detectMultiScale(fr, scaleFactor=1.1, minNeighbors=6, minSize=(max(24, w // 12), max(24, w // 12)))
        caras = sorted(caras, key=lambda c: -c[2] * c[3])
        return [(x / w, y / h, cw / w, ch / h) for x, y, cw, ch in caras]
    return haar


def track_faces(src: Source, fps: float = 10.0) -> list[FaceSample]:
    W, H = 360, 640
    raw = subprocess.run([sistema.requiere("ffmpeg"), "-v", "error", "-i", src.mezzanine, "-vf", f"fps={fps},scale={W}:{H}",
                          "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
    frames = np.frombuffer(raw, np.uint8)
    n = frames.size // (W * H)
    frames = frames[: n * W * H].reshape(n, H, W)
    detectar = _detector_caras()
    out: list[FaceSample] = []
    last = None
    for i, fr in enumerate(frames):
        res = detectar(fr)
        if res:
            last = res[0]
        elif last is None:
            continue
        x, y, w, h = last
        out.append(FaceSample(t=round(i / fps, 3), x=round(x, 4), y=round(y, 4), w=round(w, 4), h=round(h, 4)))
    # suavizado (media móvil de 5 muestras) para que los reencuadres no tiemblen
    if len(out) > 5:
        arr = np.array([[f.x, f.y, f.w, f.h] for f in out])
        k = np.ones(5) / 5
        sm = np.stack([np.convolve(np.pad(arr[:, c], 2, mode="edge"), k, mode="valid") for c in range(4)], 1)
        for f, (x, y, w, h) in zip(out, sm):
            f.x, f.y, f.w, f.h = round(float(x), 4), round(float(y), 4), round(float(w), 4), round(float(h), 4)
    return out


# ───────────────────────────── orquestación ─────────────────────────────
def analyze(slug: str, sources: list[Source], prompt: str = "", faces: bool = True) -> MediaIndex:
    rd = run_dir(slug)
    words, pauses, face_map = [], [], {}
    for src in sources:
        ws = transcribe_source(src, prompt)
        words += ws
        pauses += measure_pauses(src, ws)
        if faces:
            face_map[src.id] = track_faces(src)
    mi = MediaIndex(slug=slug, sources=sources, words=words, pauses=pauses, faces=face_map)
    (rd / "media_index.json").write_text(mi.model_dump_json(indent=1))
    return mi


def align(slug: str, mi: MediaIndex | None = None) -> MediaIndex:
    """Alineación forzada MMS (CTC) palabra a palabra; corrige los tiempos gruesos de whisper (±20–40 ms).

    Corre en un entorno aislado (`uv run --script modulos/cutkit/cutkit/tools/align_mms.py`, torch fijado) para no
    engordar el proyecto. Si una palabra no se alinea o el resultado es incoherente, conserva el tiempo de whisper.
    LICENCIA: el modelo MMS_FA se publica bajo CC-BY-NC 4.0 (uso no comercial). Por eso está apagado por defecto y
    solo se usa con `CK_ALINEAR=mms`; no lo actives para piezas comerciales (anuncios de clientes). Ver LICENCIAS.md.
    """
    rd = run_dir(slug)
    mi = mi or load_index(slug)
    script = PAQUETE / "tools" / "align_mms.py"
    for src in mi.sources:
        ws = mi.words_of(src.id)
        if not ws:                                   # fuentes sin transcripción propia (versión 50/50 de la misma toma)
            continue
        wj, aj = rd / "media" / f"words_{src.id}.json", rd / "media" / f"align_{src.id}.json"
        new_words = json.dumps([w.text for w in ws], ensure_ascii=False)
        # 27-10-2026 (en un vídeo de prueba): la caché solo vale para la MISMA lista de palabras. Al repetir el
        # ASR (otro prompt, otro motor) cambia el número de palabras y la alineación vieja desplazaba todos los tiempos.
        stale = aj.exists() and (not wj.exists() or wj.read_text() != new_words)
        wj.write_text(new_words)
        if stale:
            aj.rename(aj.with_name(f"align_{src.id}.viejo.json"))
        if not aj.exists():
            subprocess.run(["uv", "run", "--quiet", "--script", str(script), src.audio, str(wj), str(aj)], check=True,
                           cwd=MODULO, capture_output=True)
        res = json.loads(aj.read_text())
        for w, r in zip(ws, res):
            if r and r[1] > r[0] and abs(r[0] - w.s) < 1.0:
                w.s, w.e = r[0], max(r[1], r[0] + 0.06)
        # monotonía: ninguna palabra empieza antes de que acabe la anterior
        for a, b in zip(ws, ws[1:]):
            if b.s < a.s:
                b.s = a.s + 0.02
            if a.e > b.s:
                a.e = b.s
    mi.pauses = []
    for src in mi.sources:
        mi.pauses += measure_pauses(src, mi.words_of(src.id))
    (rd / "media_index.json").write_text(mi.model_dump_json(indent=1))
    return mi


def load_index(slug: str) -> MediaIndex:
    return MediaIndex.model_validate_json((run_dir(slug) / "media_index.json").read_text())


def transcript_md(mi: MediaIndex) -> str:
    """Transcripción legible con ids para el director (una línea por frase)."""
    lines, cur, src = [], [], None
    for w in mi.words:
        if src != w.src:
            if cur:
                lines.append(" ".join(cur))
                cur = []
            lines.append(f"\n## Fuente `{w.src}`")
            src = w.src
        cur.append(f"{w.text}{w.punct_after}⟨{w.id.split('_w')[1]}·{w.s:.2f}⟩")
        if re.search(r"[.?!…]", w.punct_after):
            lines.append(" ".join(cur))
            cur = []
    if cur:
        lines.append(" ".join(cur))
    return "\n".join(lines)
