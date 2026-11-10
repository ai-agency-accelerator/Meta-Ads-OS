"""Proveedores mock: generan medios de prueba deterministas con FFmpeg (coste 0).

Sirven para tests de extremo a extremo sin red ni claves, y como red de seguridad cuando
un proveedor real no está configurado. NUNCA se presentan como resultados reales: todos
los assets llevan `source="mock:*"` y un rótulo visible "MOCK".
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from ..config import PACKAGE_ROOT
from ..media import duration as media_duration, filter_path, h264, run
from ..models import Asset, Word
from ..store import ctx
from .base import ImageRequest, TalkingRequest, TTSResult, VideoRequest

FONT = PACKAGE_ROOT / "assets" / "Montserrat-Bold.ttf"


def _color(seed_text: str) -> str:
    h = hashlib.md5(seed_text.encode()).hexdigest()
    return f"0x{h[:6]}"


def _esc(t: str) -> str:
    t = re.sub(r"[^\w\s.,!?¡¿áéíóúñÁÉÍÓÚÑ-]", "", t)[:60]
    return t.replace(":", " ").replace("'", " ")


def _size(aspect: str, base: int = 720) -> tuple[int, int]:
    return {"9:16": (base, int(base * 16 / 9)), "16:9": (int(base * 16 / 9), base), "1:1": (base, base), "4:5": (base, int(base * 5 / 4))}.get(
        aspect, (base, int(base * 16 / 9))
    )


class MockImage:
    name = "mock"

    def generate(self, req: ImageRequest) -> list[Asset]:
        out = []
        w, h = _size(req.aspect, 720)
        for i in range(req.n):
            p = ctx().work("mock") / f"img_{hashlib.md5((req.prompt + str(i) + str(req.seed)).encode()).hexdigest()[:10]}.png"
            run([
                "-f", "lavfi", "-i", f"color=c={_color(req.prompt + str(i))}:s={w}x{h}",
                "-vf", f"drawtext=fontfile={filter_path(FONT)}:text='MOCK {_esc(req.prompt)}':fontsize=28:fontcolor=white:x=(w-tw)/2:y=h/2:box=1:boxcolor=black@0.4",
                "-frames:v", 1, p,
            ])
            out.append(ctx().assets.ingest(p, source="mock:image", meta={"prompt": req.prompt}, move=True))
        return out


class MockVideo:
    name = "mock"

    def generate(self, req: VideoRequest) -> Asset:
        w, h = _size(req.aspect, 720)
        d = max(1.0, req.duration)
        p = ctx().work("mock") / f"vid_{hashlib.md5((req.prompt + str(req.seed) + str(d)).encode()).hexdigest()[:10]}.mp4"
        base = ["-f", "lavfi", "-i", f"color=c={_color(req.prompt)}:s={w}x{h}:r=30:d={d}"]
        if req.first_frame is not None:
            base = ["-loop", 1, "-t", d, "-i", ctx().assets.abspath(req.first_frame)]
        vf = (
            f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
            f"zoompan=z='min(zoom+0.0008,1.08)':d=1:s={w}x{h}:fps=30,"
            # rótulo de depuración ARRIBA y corto: en la franja de subtítulos con el diálogo, el detector de texto
            # incrustado (qa.visual.burned_text) lo rechazaría con razón, como a un vídeo real con subtítulos quemados
            f"drawtext=fontfile={filter_path(FONT)}:text='MOCK VIDEO {_esc(req.prompt[:4])}':fontsize=24:fontcolor=white:x=40:y=60:box=1:boxcolor=black@0.5"
        )
        run(base + ["-vf", vf, "-t", d, *h264(18), "-pix_fmt", "yuv420p", "-r", 30, p])
        return ctx().assets.ingest(p, source="mock:video", meta={"prompt": req.prompt}, move=True)


class MockTTS:
    """Voz del sistema en Mac (`say`) si existe; en Linux, Windows o si falla, tono sintético con la duración esperada."""

    name = "mock"
    VOICES = {"es-ES": "Eddy (Español (España))", "es-MX": "Eddy (Español (México))", "en-US": "Eddy (Inglés (EE. UU.))"}

    def speak(self, text: str, *, voice: str, locale: str, style: str = "", speed: float = 1.0) -> TTSResult:
        wd = ctx().work("mock")
        key = hashlib.md5((text + locale + voice).encode()).hexdigest()[:10]
        aiff = wd / f"tts_{key}.aiff"
        wav = wd / f"tts_{key}.wav"
        try:
            if sys.platform != "darwin" or not shutil.which("say") or os.environ.get("MOTOR_MOCK_TONO"):
                raise FileNotFoundError("sin voz del sistema")
            subprocess.run(["say", "-v", self.VOICES.get(locale, self.VOICES["es-ES"]), "-o", str(aiff), text], check=True, timeout=60, stdin=subprocess.DEVNULL)
            run(["-i", aiff, "-ac", 1, "-ar", 48000, wav])
        except Exception:
            secs = max(1.0, len(text.split()) / 2.6)
            run(["-f", "lavfi", "-i", f"sine=f=220:d={secs}", "-ac", 1, "-ar", 48000, wav])
        a = ctx().assets.ingest(wav, source="mock:tts", meta={"text": text, "locale": locale}, move=True)
        return TTSResult(audio=a, words=even_words(text, a.duration or media_duration(ctx().assets.abspath(a))))


def even_words(text: str, total: float, start: float = 0.0) -> list[Word]:
    toks = text.split()
    if not toks:
        return []
    weights = [max(len(t), 2) for t in toks]
    unit = total / sum(weights)
    out, t = [], start
    for tok, wgt in zip(toks, weights):
        d = wgt * unit
        out.append(Word(text=tok, start=round(t, 3), end=round(t + d * 0.92, 3)))
        t += d
    return out


class MockTalking:
    name = "mock"

    def generate(self, req: TalkingRequest) -> Asset:
        audio = req.audio
        if audio is None and req.dialogue:
            audio = MockTTS().speak(req.dialogue, voice="", locale=req.locale).audio
        dur = max(req.duration, (audio.duration or 0) + 0.6) if audio else req.duration
        v = MockVideo().generate(VideoRequest(prompt="TALK " + (req.dialogue or req.prompt), first_frame=req.portrait,
                                              duration=dur, aspect=req.aspect, seed=req.seed))
        if audio is None:
            return v
        req = TalkingRequest(prompt=req.prompt, portrait=req.portrait, audio=audio, dialogue=req.dialogue, locale=req.locale)
        out = ctx().work("mock") / f"talk_{v.id[:8]}_{req.audio.id[:8]}.mp4"
        run(["-i", ctx().assets.abspath(v), "-i", ctx().assets.abspath(req.audio), "-map", "0:v", "-map", "1:a",
             "-c:v", "copy", "-c:a", "aac", "-shortest", out])
        return ctx().assets.ingest(out, source="mock:talking", move=True)


class MockLipSync:
    name = "mock"

    def sync(self, video: Asset, audio: Asset) -> Asset:
        out = ctx().work("mock") / f"lips_{video.id[:8]}_{audio.id[:8]}.mp4"
        run(["-stream_loop", -1, "-i", ctx().assets.abspath(video), "-i", ctx().assets.abspath(audio), "-map", "0:v", "-map", "1:a",
             *h264(18), "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", out])
        return ctx().assets.ingest(out, source="mock:lipsync", move=True)


class MockMusic:
    name = "mock"

    def generate(self, prompt: str, duration: float) -> Asset:
        out = ctx().work("mock") / f"music_{hashlib.md5(prompt.encode()).hexdigest()[:8]}_{int(duration)}.wav"
        run(["-f", "lavfi", "-i", f"sine=f=110:d={duration}", "-f", "lavfi", "-i", f"sine=f=165:d={duration}",
             "-filter_complex", "amix=inputs=2,volume=0.3", "-ac", 2, "-ar", 48000, out])
        return ctx().assets.ingest(out, source="mock:music", move=True)


class MockTranscriber:
    name = "mock"

    def words(self, audio: Asset, locale: str, text_hint: str = "") -> list[Word]:
        d = audio.duration or media_duration(ctx().assets.abspath(audio))
        return even_words(text_hint or "", d)


class MockJudge:
    """Juez simulado con el MISMO esquema que el real. `MOTOR_MOCK_DEFECTS="extra_object@S2:critical,hands@S3"` inyecta
    defectos (una sola vez por escena y categoría) para probar el bucle rechazo → regeneración sin gastar."""

    name = "mock"
    _fired: set[str] = set()

    def review(self, video: Asset, prompt: str, schema: dict[str, Any], *, refs=None, fps: float = 2.0, step: str = "qa") -> Any:
        defects = []
        for item in filter(None, (os.environ.get("MOTOR_MOCK_DEFECTS") or "").split(",")):
            cat, _, rest = item.partition("@")
            label, _, sev = rest.partition(":")
            key = f"{cat}:{label}"  # una sola vez: tras regenerar, la escena debe pasar
            if cat and label and key not in MockJudge._fired and cat in prompt:
                MockJudge._fired.add(key)
                defects.append({"category": cat, "scene_label": label, "evidence": f"defecto inyectado ({cat})", "start_s": 0.0,
                                "end_s": 1.0, "severity": sev or "critical", "confidence": 0.95})
        return {"defects": defects, "overall_realism": 0.8, "looks_ai_generated": 0.2, "would_scroll_past": False,
                "summary": "juez simulado"}


class MockLLM:
    """Devuelve JSON plausible a partir de pistas del prompt. Solo para tests offline."""

    name = "mock"

    def json(self, system: str, prompt: str, schema: dict[str, Any] | None = None, *, images=None, step: str = "llm",
             temperature: float = 0.7, model: str | None = None) -> Any:
        m = re.search(r"<mock>(.*?)</mock>", prompt, re.S)
        if m:
            return json.loads(m.group(1))
        return {}

    def text(self, system: str, prompt: str, *, step: str = "llm", temperature: float = 0.7, model: str | None = None) -> str:
        return "mock"


def rng(seed: int) -> random.Random:
    return random.Random(seed)
