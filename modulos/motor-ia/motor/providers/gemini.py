"""Adaptadores Google Gemini API: LLM, imagen (Nano Banana), vídeo (Veo 3.1 / Omni), voz (TTS),
música (Lyria), transcripción y revisión de vídeo (QA).

Todas las llamadas pasan por `meter()` (coste real) y por caché de contenido cuando el resultado
es determinista para la misma petición (mismo prompt, refs, semilla y modelo).
"""

from __future__ import annotations

import json
import mimetypes
import time
from pathlib import Path
from typing import Any

from ..costs import cache_get, cache_key, cache_put, meter, price, record_cached, token_cost
from ..media import pcm_to_wav, run
from ..models import Asset, Word
from ..locales import LOCALE_NAMES
from ..store import ctx
from .base import ImageRequest, ProviderError, TalkingRequest, TTSResult, VideoRequest, is_billing
from .retry import SAFE_RETRY_MARKERS, with_retries

DEFAULT_LLM = "gemini-3.8-flash"
CREATIVE_LLM = "gemini-3.1-pro-preview"
IMAGE_MODEL = "gemini-3.1-flash-image"
IMAGE_MODEL_PRO = "gemini-3-pro-image"
VEO_LITE = "veo-3.1-lite-generate-preview"
VEO_FAST = "veo-3.1-fast-generate-preview"
VEO_STD = "veo-3.1-generate-preview"
OMNI = "gemini-omni-1.1-flash"
TTS_MODEL = "gemini-3.8-flash-tts"
MUSIC_MODEL = "lyria-3-clip-preview"
JUDGE_MODEL = "gemini-3.8-flash"
TRANSCRIBE_MODEL = "gemini-3.5-transcribe"

_client = None


def client():
    global _client
    if _client is None:
        from google import genai

        key = ctx().settings.key("GEMINI_API_KEY")
        if not key:
            raise ProviderError("GEMINI_API_KEY no configurada")
        _client = genai.Client(api_key=key)
    return _client


def _types():
    from google.genai import types

    return types


def _image_part(a: Asset):
    t = _types()
    p = ctx().assets.abspath(a)
    mime = a.mime or mimetypes.guess_type(p.name)[0] or "image/png"
    return t.Part.from_bytes(data=p.read_bytes(), mime_type=mime)


def _usage(resp) -> tuple[int, int]:
    u = getattr(resp, "usage_metadata", None)
    if not u:
        return 0, 0
    prompt = int(getattr(u, "prompt_token_count", 0) or 0)
    out = int(getattr(u, "candidates_token_count", 0) or 0) + int(getattr(u, "thoughts_token_count", 0) or 0)
    return prompt, out


def _video_tokens(resp) -> int:
    u = getattr(resp, "usage_metadata", None)
    total = 0
    for d in (getattr(u, "prompt_tokens_details", None) or []):
        if str(getattr(d, "modality", "")).upper().endswith("VIDEO"):
            total += int(getattr(d, "token_count", 0) or 0)
    return total


def _wrap(e: Exception) -> Exception:
    s = str(e)
    moderation = any(k in s.lower() for k in ("safety", "blocked", "prohibited", "policy", "person", "celebrity", "raimedia"))
    retry = any(k in s for k in ("429", "500", "503", "504", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "INTERNAL", "DEADLINE"))
    code = getattr(e, "code", None) if isinstance(getattr(e, "code", None), int) else None
    return ProviderError(f"Gemini: {s[:600]}", retryable=retry, moderation=moderation, billing=is_billing(e), status_code=code)


# ───────────────────────────── LLM ─────────────────────────────


def _parse_json(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
        raise ProviderError(f"respuesta no JSON: {text[:300]}", retryable=True)


class GeminiLLM:
    name = "gemini"

    def __init__(self, model: str = DEFAULT_LLM):
        self.model = model

    def _call(self, system: str, prompt: str, *, schema: dict | None, images: list[Asset] | None, step: str,
              temperature: float, model: str | None) -> tuple[str, str]:
        t = _types()
        m = model or self.model
        contents: list[Any] = [_image_part(a) for a in (images or [])] + [prompt]
        cfg: dict[str, Any] = {"system_instruction": system, "temperature": temperature}
        if schema is not None:
            cfg["response_mime_type"] = "application/json"
            cfg["response_json_schema"] = schema
        key = cache_key("llm", m, system, prompt, schema, [a.id for a in images or []], temperature)
        hit = cache_get(key)
        if hit is not None:
            record_cached(step, "gemini", m)
            return hit["text"], m
        est = token_cost("gemini", m, len(prompt) // 3 + 2000, 4000)
        with meter(step, "gemini", m, est_usd=est) as mt:
            def go():
                try:
                    return client().models.generate_content(model=m, contents=contents, config=t.GenerateContentConfig(**cfg))
                except Exception as e:  # noqa: BLE001
                    raise _wrap(e) from e

            resp = with_retries(go)
            pi, po = _usage(resp)
            mt.set_usd(token_cost("gemini", m, pi, po), unit="tokens", quantity=pi + po, note=f"in={pi} out={po}")
        text = resp.text or ""
        if schema is not None:
            try:
                _parse_json(text)
            except ProviderError:
                return text, m  # respuesta rota: NO se cachea (si no, el proyecto quedaría atascado con ella para siempre)
        if text.strip():
            cache_put(key, {"text": text})
        return text, m

    def json(self, system: str, prompt: str, schema: dict[str, Any] | None = None, *, images: list[Asset] | None = None,
             step: str = "llm", temperature: float = 0.7, model: str | None = None) -> Any:
        text, _ = self._call(system, prompt, schema=schema or {"type": "object"}, images=images, step=step,
                             temperature=temperature, model=model)
        return _parse_json(text)

    def text(self, system: str, prompt: str, *, step: str = "llm", temperature: float = 0.7, model: str | None = None) -> str:
        text, _ = self._call(system, prompt, schema=None, images=None, step=step, temperature=temperature, model=model)
        return text


# ───────────────────────────── Imagen ─────────────────────────────


class GeminiImage:
    name = "gemini"

    def __init__(self, model: str = IMAGE_MODEL):
        self.model = model

    def generate(self, req: ImageRequest) -> list[Asset]:
        t = _types()
        size = {"0.5k": "512", "1k": "1K", "2k": "2K", "4k": "4K"}.get(req.size.lower(), "1K")
        unit = price("gemini", self.model, req.size.lower(), price("gemini", self.model, "1k", 0.07))
        out: list[Asset] = []
        for i in range(max(1, req.n)):
            key = cache_key("img", self.model, req.prompt, [a.id for a in req.refs], req.ref_roles, req.aspect, size, req.seed, i)
            hit = cache_get(key)
            if hit:
                record_cached("image", "gemini", self.model)
                out.append(ctx().db.get_asset(hit["asset"]))
                continue
            parts: list[Any] = []
            for a, role in zip(req.refs, req.ref_roles + [""] * len(req.refs)):
                if role:
                    parts.append(f"[Reference image — {role}]")
                parts.append(_image_part(a))
            parts.append(req.prompt)
            cfg = t.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=t.ImageConfig(aspect_ratio=req.aspect, image_size=size),
                seed=(req.seed + i) if req.seed is not None else None,
            )
            with meter("image", "gemini", self.model, est_usd=unit) as mt:
                def go():
                    try:
                        return client().models.generate_content(model=self.model, contents=parts, config=cfg)
                    except Exception as e:  # noqa: BLE001
                        raise _wrap(e) from e

                resp = with_retries(go)
                img_bytes, mime = None, "image/png"
                for cand in resp.candidates or []:
                    for p in (cand.content.parts if cand.content else []) or []:
                        if getattr(p, "inline_data", None) and p.inline_data.data:
                            img_bytes, mime = p.inline_data.data, p.inline_data.mime_type or mime
                if img_bytes is None:
                    reason = getattr(resp.candidates[0], "finish_reason", "?") if resp.candidates else "sin candidatos"
                    mt.set_usd(0.0, note=f"sin imagen: {reason}")
                    raise ProviderError(f"Gemini image: sin imagen ({reason}). {(resp.text or '')[:200]}", moderation=True)
                mt.set("image", 1, unit)
            ext = mimetypes.guess_extension(mime) or ".png"
            a = ctx().assets.ingest_bytes(img_bytes, ext, source=f"gemini:{self.model}",
                                          meta={"prompt": req.prompt, "refs": [r.id for r in req.refs], "seed": req.seed})
            cache_put(key, {"asset": a.id})
            out.append(a)
        return out


# ───────────────────────────── Vídeo: Veo 3.1 ─────────────────────────────


def _gimage(a: Asset):
    t = _types()
    p = ctx().assets.abspath(a)
    mime = a.mime or mimetypes.guess_type(p.name)[0] or "image/png"
    return t.Image(image_bytes=p.read_bytes(), mime_type=mime)


def _veo_duration(d: float) -> int:
    # Veo 3.1 admite 4, 6 u 8 segundos
    for allowed in (4, 6, 8):
        if d <= allowed + 0.25:
            return allowed
    return 8


class GeminiVeo:
    """Veo 3.1 (Lite/Fast/Standard). Imagen→vídeo con primer fotograma, último fotograma y referencias."""

    name = "gemini"

    def __init__(self, model: str = VEO_LITE):
        self.model = model

    def generate(self, req: VideoRequest) -> Asset:
        t = _types()
        dur = _veo_duration(req.duration)
        res = req.resolution if req.resolution in ("720p", "1080p", "4k") else "720p"
        key = cache_key("veo", self.model, req.prompt, req.first_frame.id if req.first_frame else None,
                        req.last_frame.id if req.last_frame else None, [r.id for r in req.refs], dur, res, req.aspect,
                        req.audio, req.negative_prompt, req.seed)
        hit = cache_get(key)
        if hit:
            record_cached("video", "gemini", self.model)
            return ctx().db.get_asset(hit["asset"])
        unit = price("gemini", self.model, res, 0.4)
        cfg: dict[str, Any] = {
            "aspect_ratio": req.aspect if req.aspect in ("9:16", "16:9") else "9:16",
            "duration_seconds": dur,
            "resolution": res,
            "person_generation": "allow_adult",
            "number_of_videos": 1,
        }
        if req.negative_prompt:
            cfg["negative_prompt"] = req.negative_prompt
        if req.seed is not None:
            cfg["seed"] = int(req.seed) % 4294967295
        if req.last_frame is not None:
            cfg["last_frame"] = _gimage(req.last_frame)
        if req.refs and req.first_frame is None:
            cfg["reference_images"] = [t.VideoGenerationReferenceImage(image=_gimage(r), reference_type="ASSET") for r in req.refs[:3]]
        # `generate_audio` solo existe en Vertex/Enterprise: con clave de la API de desarrollador el SDK lo rechaza aunque
        # sea False. No se envía: el audio de los cortes se silencia igualmente en el montaje.
        with meter("video", "gemini", self.model, est_usd=unit * dur) as mt:
            video_bytes = self._run(req, cfg)
            mt.set("second", dur, unit, note=f"{res} audio={req.audio}")
        a = ctx().assets.ingest_bytes(video_bytes, ".mp4", source=f"gemini:{self.model}",
                                      meta={"prompt": req.prompt, "duration": dur, "resolution": res, "seed": req.seed})
        cache_put(key, {"asset": a.id})
        return a

    def _run(self, req: VideoRequest, cfg: dict[str, Any]) -> bytes:
        t = _types()
        c = client()

        def submit(conf: dict[str, Any]):
            try:
                return c.models.generate_videos(
                    model=self.model,
                    prompt=req.prompt,
                    image=_gimage(req.first_frame) if req.first_frame is not None else None,
                    config=t.GenerateVideosConfig(**conf),
                )
            except Exception as e:  # noqa: BLE001
                raise _wrap(e) from e

        conf = dict(cfg)
        for _round in range(4):
            try:
                op = with_retries(lambda: submit(conf), attempts=3, base=20, markers=SAFE_RETRY_MARKERS)
                break
            except ProviderError as e:
                if e.billing or _round == 3:
                    raise
                # algunos parámetros no existen en todas las variantes/modos: se quitan los que el error menciona
                msg = str(e).lower().replace("_", "")
                drop = [k for k in ("generate_audio", "seed", "negative_prompt", "person_generation", "reference_images", "last_frame")
                        if k in conf and (k.replace("_", "") in msg or "not supported" in msg or "invalid" in msg)]
                if not drop:
                    raise
                for k in drop:
                    conf.pop(k)
        deadline = time.time() + 900
        while not op.done:
            if time.time() > deadline:
                raise ProviderError("Veo: timeout esperando la operación", retryable=True)
            time.sleep(8)
            op = c.operations.get(op)
        if getattr(op, "error", None):
            raise _wrap(Exception(str(op.error)))
        resp = op.response or getattr(op, "result", None)
        vids = getattr(resp, "generated_videos", None) or []
        if not vids:
            reasons = getattr(resp, "rai_media_filtered_reasons", None)
            raise ProviderError(f"Veo: sin vídeo (filtrado: {reasons})", moderation=True)
        v = vids[0].video
        data = getattr(v, "video_bytes", None)
        if not data:
            c.files.download(file=v)
            data = v.video_bytes
        if not data:
            raise ProviderError("Veo: vídeo vacío")
        return data


class GeminiVeoTalking:
    """Plano hablado con diálogo nativo de Veo (labios generados con el propio vídeo).

    La voz nativa varía entre planos: el pipeline la sustituye por la voz canónica del actor
    (TTS) solo si hay lip-sync disponible; si no, conserva la nativa y unifica tono/sala en post.
    """

    name = "gemini"

    def __init__(self, model: str = VEO_FAST):
        self.veo = GeminiVeo(model)

    def generate(self, req: TalkingRequest) -> Asset:
        prompt = req.prompt
        if req.dialogue:
            lang = {"es-ES": "Spanish from Spain (Castilian accent)", "es-MX": "Mexican Spanish", "en-US": "American English"}.get(
                req.locale, req.locale)
            prompt += f' She speaks directly to camera in {lang}, natural casual delivery: "{req.dialogue}"'
            if req.voice_hint:
                prompt += f" Voice: {req.voice_hint}."
        return self.veo.generate(VideoRequest(prompt=prompt, first_frame=req.portrait, duration=req.duration, aspect=req.aspect,
                                              resolution=req.resolution, audio=True, seed=req.seed,
                                              negative_prompt="subtitles, captions, text on screen, music, distorted mouth, extra fingers"))


# ───────────────────────────── Voz ─────────────────────────────


class GeminiTTS:
    """TTS Gemini 3.8 vía Interactions API. `voice` es un id del catálogo (p.ej. es-es-commercial-3),
    un nombre de voz de estudio (Kore, Aoede…) o una voz diseñada propia (voice_…)."""

    name = "gemini"

    def __init__(self, model: str = TTS_MODEL):
        self.model = model

    def speak(self, text: str, *, voice: str, locale: str, style: str = "", speed: float = 1.0) -> TTSResult:
        key = cache_key("tts2", self.model, text, voice, locale, style, speed)
        hit = cache_get(key)
        if hit:
            record_cached("voice", "gemini", self.model)
            a = ctx().db.get_asset(hit["asset"])
            return TTSResult(audio=a, words=[Word(**w) for w in hit.get("words", [])])
        content: dict[str, Any] = {"type": "text", "text": text}
        if style:
            content["annotations"] = [{"type": "speech_metadata", "style": style}]
        body = dict(model=self.model, input=[{"type": "user_input", "content": [content]}],
                    response_format={"type": "audio"}, generation_config={"speech_config": [{"voice": voice}]})
        est = token_cost("gemini", self.model, 900, int(len(text.split()) / 2.4 * 32), audio_out=True)
        with meter("voice", "gemini", self.model, est_usd=est) as mt:
            it = with_retries(lambda: _interaction(body))
            data, mime = _interaction_media(it, "audio")
            if not data:
                raise ProviderError("Gemini TTS: sin audio")
            pi, po = _interaction_usage(it)
            mt.set_usd(token_cost("gemini", self.model, pi, po, audio_out=True), unit="tokens", quantity=pi + po,
                       note=f"in={pi} out={po} voice={voice}")
        raw = ctx().work("tts") / f"{key[:16]}.src{mimetypes.guess_extension(mime or 'audio/wav') or '.wav'}"
        if (mime or "").startswith("audio/l16"):
            pcm_to_wav(data, raw, rate=24000)
        else:
            raw.write_bytes(data)
        wav48 = ctx().work("tts") / f"{key[:16]}.wav"
        run(["-i", raw, "-ac", 1, "-ar", 48000, wav48])
        raw.unlink(missing_ok=True)
        a = ctx().assets.ingest(wav48, source=f"gemini:{self.model}", meta={"text": text, "voice": voice, "locale": locale}, move=True)
        cache_put(key, {"asset": a.id, "words": []})
        return TTSResult(audio=a, words=[])


def list_voices(language_code: str | None = None, **filters: str) -> list[dict[str, Any]]:
    """Catálogo de voces (gratis). Filtros: language_code, gender, persona, context, type, search."""
    import httpx

    params: dict[str, Any] = {"page_size": 500}
    if language_code:
        params["language_code"] = language_code
    params.update(filters)
    r = httpx.get("https://generativelanguage.googleapis.com/v1beta/voices", params=params,
                  headers={"x-goog-api-key": ctx().settings.key("GEMINI_API_KEY") or ""}, timeout=30)
    r.raise_for_status()
    return r.json().get("voices", [])


def design_voice(display_name: str, description: str, *, language_code: str = "es-ES", gender: str = "female",
                 model: str = TTS_MODEL) -> dict[str, Any]:
    """Diseña una voz propia persistente (voice_…) a partir de una descripción. Devuelve id + muestra WAV."""
    import base64

    import httpx

    body = {"model": model, "display_name": display_name, "gender": gender, "language_code": language_code,
            "type": "prompted", "prompted": {"input": description}, "store": True}
    with meter("voice", "gemini", f"{model}:voice-design", est_usd=0.0) as mt:
        r = httpx.post("https://generativelanguage.googleapis.com/v1beta/voices", json=body,
                       headers={"x-goog-api-key": ctx().settings.key("GEMINI_API_KEY") or ""}, timeout=120)
        if r.status_code >= 400:
            raise ProviderError(f"voice design: {r.status_code} {r.text[:400]}")
        j = r.json()
        mt.set_usd(0.0, note="voice design")
    sample = None
    if j.get("sample_audio") or j.get("sampleAudio"):
        data = base64.b64decode(j.get("sample_audio") or j.get("sampleAudio"))
        sample = ctx().assets.ingest_bytes(data, ".wav", source="gemini:voice-design", meta={"voice": j.get("id") or j.get("name")})
    return {"id": j.get("id") or j.get("name"), "raw": {k: v for k, v in j.items() if "audio" not in k.lower()},
            "sample_asset_id": sample.id if sample else None}


# ───────────────────────────── Interactions API (Omni, TTS) ─────────────────────────────


API_BASE = "https://generativelanguage.googleapis.com/v1beta"


def _rest(method: str, path: str, *, json_body: dict[str, Any] | None = None, timeout: float = 120) -> dict[str, Any]:
    """REST directo (el SDK 2.28 envía la clave por duplicado al consultar interacciones)."""
    import httpx

    r = httpx.request(method, f"{API_BASE}/{path}", json=json_body, timeout=timeout,
                      headers={"x-goog-api-key": ctx().settings.key("GEMINI_API_KEY") or "", "Content-Type": "application/json"})
    if r.status_code >= 400:
        txt = r.text[:800]
        raise ProviderError(f"Gemini REST {r.status_code}: {txt}", retryable=r.status_code in (429, 503), status_code=r.status_code,
                            moderation=any(k in txt.lower() for k in ("safety", "blocked", "prohibited", "policy")),
                            billing=r.status_code == 402 or is_billing(Exception(txt)))
    return r.json()


def _mark_pending(iid: str, body: dict[str, Any]) -> None:
    """Registra en disco una generación ACEPTADA por el proveedor antes de recibir el resultado.

    Si el proceso o la red mueren a mitad, queda constancia (id remoto, modelo, hora) para conciliar el gasto y no
    relanzar a ciegas. Se borra al recibir el resultado completo.
    """
    try:
        ctx().db.cache_put(f"pending_gen:{iid}", {"provider": "gemini", "model": body.get("model"), "remote_id": iid,
                                                  "ts": time.time(), "status": "accepted"})
    except Exception:  # noqa: BLE001
        pass


def _clear_pending(iid: str | None) -> None:
    if iid:
        try:
            ctx().db.conn().execute("DELETE FROM cache WHERE key=?", (f"pending_gen:{iid}",))
            ctx().db.conn().commit()
        except Exception:  # noqa: BLE001
            pass


def _interaction(body: dict[str, Any], *, background: bool = False, timeout: float = 900) -> dict[str, Any]:
    """Crea una interacción y espera el resultado.

    Usa streaming SSE (`stream: true`): el endpoint GET /interactions/{id} devuelve hoy un error de
    autenticación con claves de API («Multiple authentication credentials»), así que no se sondea.
    El resultado se reconstruye a partir de los eventos (interacción final o deltas de contenido).
    Si la conexión se pierde DESPUÉS de que la interacción tenga id, el error se marca `accepted` (no se reintenta:
    se cobraría dos veces) y la generación queda registrada como pendiente.
    """
    import httpx

    payload = dict(body)
    payload.pop("background", None)
    payload["stream"] = True
    st: dict[str, Any] = {"final": None, "iid": None, "status": None, "error": None, "usage": None}
    steps: dict[int, dict[str, Any]] = {}
    event_types: list[str] = []
    try:
        with httpx.stream("POST", f"{API_BASE}/interactions?alt=sse", json=payload, timeout=httpx.Timeout(timeout, connect=30),
                          headers={"x-goog-api-key": ctx().settings.key("GEMINI_API_KEY") or "", "Content-Type": "application/json"}) as r:
            if r.status_code >= 400:
                txt = r.read().decode(errors="ignore")[:800]
                raise ProviderError(f"Gemini REST {r.status_code}: {txt}", retryable=r.status_code in (429, 503), status_code=r.status_code,
                                    moderation=any(k in txt.lower() for k in ("safety", "blocked", "prohibited", "policy")),
                                    billing=r.status_code == 402 or is_billing(Exception(txt)))
            buf = ""
            for line in r.iter_lines():
                if line.startswith("data:"):
                    buf += line[5:].strip()
                    continue
                if line.strip() == "" and buf:
                    try:
                        ev = json.loads(buf)
                    except json.JSONDecodeError:
                        buf = ""
                        continue
                    buf = ""
                    _sse_event(ev, st, steps, event_types, body)
    except ProviderError:
        raise
    except Exception as e:  # noqa: BLE001  (corte de red, timeout…)
        acc = st["iid"]
        raise ProviderError(f"Interactions: conexión perdida {'tras aceptar ' + acc if acc else 'antes de aceptar'}: "
                            f"{type(e).__name__}: {str(e)[:200]}", retryable=not acc, accepted=bool(acc), remote_id=acc) from e
    iid, final, usage, error = st["iid"], st["final"], st["usage"], st["error"]
    if iid:
        _LAST_INTERACTIONS.append(iid)
    if final and final.get("steps"):
        out = final
    else:
        out = {"id": iid, "status": st["status"] or "completed", "usage": usage,
               "steps": [{"type": v["type"] or "model_output", "content": list(v["content"].values())} for _, v in sorted(steps.items())]}
    if usage and not out.get("usage"):
        out["usage"] = usage
    out["_events"] = event_types[-30:]
    if error or (out.get("status") in ("failed", "cancelled")):
        _clear_pending(iid)
        raise ProviderError(f"Interactions: {out.get('status')} id={iid} {str(error)[:400]}", remote_id=iid,
                            moderation="safety" in str(error).lower() or "block" in str(error).lower())
    return out


def _sse_event(ev: dict[str, Any], st: dict[str, Any], steps: dict[int, dict[str, Any]], event_types: list[str],
               body: dict[str, Any]) -> None:
    et = ev.get("event_type", "")
    event_types.append(et)
    if "interaction" in ev and isinstance(ev["interaction"], dict):
        it = ev["interaction"]
        if it.get("id") and not st["iid"]:
            st["iid"] = it["id"]
            _mark_pending(it["id"], body)
        if it.get("steps") or it.get("status") in ("completed", "failed", "cancelled"):
            st["final"] = it
        if it.get("usage"):
            st["usage"] = it["usage"]
        st["status"] = it.get("status") or st["status"]
    if ev.get("status"):
        st["status"] = ev["status"]
    if ev.get("error"):
        st["error"] = ev["error"]
    if ev.get("usage"):
        st["usage"] = ev["usage"]
    if et in ("step.start",) and isinstance(ev.get("step"), dict):
        steps.setdefault(int(ev.get("index", 0)), {"type": ev["step"].get("type"), "content": {}})
    if et in ("step.delta", "content.delta") and isinstance(ev.get("delta"), dict):
        d = ev["delta"]
        stp = steps.setdefault(int(ev.get("index", 0)), {"type": "model_output", "content": {}})
        kind = d.get("type") or ("text" if "text" in d else None)
        if kind in ("video", "audio", "image", "text"):
            cur = stp["content"].setdefault(kind, {"type": kind, "data_parts": [], "mime_type": "", "uri": None, "text": ""})
            if d.get("data"):
                cur["data_parts"].append(d["data"])
            if d.get("mime_type"):
                cur["mime_type"] = d["mime_type"]
            if d.get("uri"):
                cur["uri"] = d["uri"]
            if d.get("text"):
                cur["text"] += d["text"]


_LAST_INTERACTIONS: list[str] = []


def _interaction_media(d: dict[str, Any], kind: str) -> tuple[bytes | None, str]:
    import base64

    items = []
    for st in d.get("steps") or []:
        if st.get("type") == "model_output":
            for cc in st.get("content") or []:
                if cc.get("type") == kind:
                    items.append(cc)
    out_key = f"output_{kind}"
    if not items and d.get(out_key):
        items = [d[out_key]]
    if not items:
        return None, ""
    it = items[-1]
    mime = it.get("mime_type") or ""
    if it.get("data_parts"):
        # cada delta SSE es base64 independiente (con su relleno «=»): concatenar el texto truncaría el fichero
        return b"".join(base64.b64decode(x) for x in it["data_parts"]), mime
    if it.get("data"):
        return base64.b64decode(it["data"]), mime
    uri = it.get("uri")
    if uri:
        return _download_file(uri), mime
    return None, mime


def _download_file(uri: str) -> bytes:
    import httpx

    c = client()
    name = uri.split("/v1beta/")[-1].split("?")[0] if "/v1beta/" in uri else uri
    if name.startswith("files/"):
        deadline = time.time() + 300
        while True:
            f = c.files.get(name=name.split(":")[0])
            state = getattr(f.state, "name", str(f.state))
            if state == "ACTIVE" or time.time() > deadline:
                break
            time.sleep(3)
        url = f"https://generativelanguage.googleapis.com/v1beta/{name.split(':')[0]}:download?alt=media"
    else:
        url = uri
    r = httpx.get(url, headers={"x-goog-api-key": ctx().settings.key("GEMINI_API_KEY") or ""}, timeout=300, follow_redirects=True)
    r.raise_for_status()
    return r.content


def _interaction_usage(d: dict[str, Any]) -> tuple[int, int]:
    u = d.get("usage") or {}
    pi = int(u.get("total_input_tokens") or 0)
    po = int(u.get("total_output_tokens") or 0) + int(u.get("total_thought_tokens") or 0)
    return pi, po


def _interaction_video_tokens(d: dict[str, Any]) -> int:
    u = d.get("usage") or {}
    return sum(int(x.get("tokens") or 0) for x in (u.get("output_tokens_by_modality") or []) if x.get("modality") == "video")


def _b64_image(a: Asset) -> dict[str, Any]:
    import base64

    p = ctx().assets.abspath(a)
    mime = a.mime or mimetypes.guess_type(p.name)[0] or "image/png"
    return {"type": "image", "data": base64.b64encode(p.read_bytes()).decode(), "mime_type": mime}


NO_TEXT = "No subtitles, no captions and no on-screen text of any kind (the editor adds them later)."


class GeminiOmni:
    """Gemini Omni 1.1 Flash: imagen→vídeo con primer fotograma + referencias de identidad (Interactions API).

    - Plano continuo forzado por prompt (por defecto Omni mete cortes).
    - Sin diálogo salvo que se pida: «No dialogue, lips closed».
    - Guarda el id de interacción (store=True) para poder EXTENDER el vídeo generado (permitido en el EEE).
    """

    name = "gemini"
    model = OMNI

    def __init__(self, model: str = OMNI):
        self.model = model

    def _price_per_s(self, res: str) -> float:
        return price("gemini", self.model, res, 0.101)

    def _call(self, inputs: list[dict[str, Any]], prompt: str, *, res: str, aspect: str, duration: float, task: str,
              previous_id: str | None = None, step: str = "video", key_parts: tuple = ()) -> Asset:
        key = cache_key("omni", self.model, prompt, key_parts, res, aspect, round(duration), task, previous_id)
        hit = cache_get(key)
        if hit:
            record_cached(step, "gemini", self.model)
            return ctx().db.get_asset(hit["asset"])
        rf: dict[str, Any] = {"type": "video", "aspect_ratio": aspect if aspect in ("9:16", "16:9") else "9:16",
                              "resolution": res, "delivery": "inline"}
        body: dict[str, Any] = {"model": self.model, "input": inputs + [{"type": "text", "text": prompt}],
                                "response_format": rf, "store": True}
        if task and not previous_id:
            body["generation_config"] = {"video_config": {"task": task}}
        if previous_id:
            body["previous_interaction_id"] = previous_id
            # con tarea de vídeo y conversación previa, la API exige un turno de usuario explícito
            body["input"] = [{"type": "user_input", "content": inputs + [{"type": "text", "text": prompt}]}]
        unit = self._price_per_s(res)
        with meter(step, "gemini", self.model, est_usd=unit * max(duration, 3) + 0.01) as mt:
            def go():
                try:
                    return _interaction(body, background=True)
                except ProviderError as e:
                    if "duration" in str(e).lower() or "response_format" in str(e).lower():
                        raise
                    raise
            d = with_retries(go, attempts=3, base=20, markers=SAFE_RETRY_MARKERS)
            data, mime = _interaction_media(d, "video")
            pi, po = _interaction_usage(d)
            vt = _interaction_video_tokens(d)
            usd = (pi * price("gemini", self.model, "input_per_m", 1.5) + (po - vt) * price("gemini", self.model, "output_per_m", 9.0)
                   + vt * price("gemini", self.model, "video_output_per_m", 17.5)) / 1_000_000
            if not data:
                mt.set_usd(usd, unit="tokens", quantity=pi + po, note="sin vídeo")
                raise ProviderError(f"Omni: sin vídeo. {str(d.get('output_text') or '')[:200]}", moderation=True)
            mt.set_usd(usd, unit="tokens", quantity=pi + po, note=f"video_tokens={vt} in={pi} out={po} res={res}")
        a = ctx().assets.ingest_bytes(data, ".mp4", source=f"gemini:{self.model}",
                                      meta={"prompt": prompt, "interaction_id": d.get("id"), "task": task, "resolution": res})
        cache_put(key, {"asset": a.id, "interaction_id": d.get("id")})
        _clear_pending(d.get("id"))
        return a

    def generate(self, req: VideoRequest) -> Asset:
        inputs: list[dict[str, Any]] = []
        tags = []
        n = 0
        if req.first_frame is not None:
            n += 1
            inputs.append(_b64_image(req.first_frame))
            tags.append(f"[# Sources <FIRST_FRAME>@Image{n}]")
        refs = []
        for i, r in enumerate(req.refs[:4]):
            n += 1
            inputs.append(_b64_image(r))
            refs.append(f"<IMAGE_REF_{i}>@Image{n}")
        if refs:
            tags.append(f"[# References {' '.join(refs)}]")
        speech = "" if req.audio else " No dialogue, the person does not speak, lips stay closed. No music, only quiet natural room tone."
        guide = ""
        if req.first_frame is not None:
            guide += " Use Image1 as the exact starting frame."
        if refs:
            guide += " Use the reference images only to keep the same person's identity (face, hair, skin, body); do not use them as literal frames."
        dur = max(3, min(10, int(round(req.duration))))
        prompt = (f"{' '.join(tags)} A single continuous {dur}-second shot with no scene cuts and no transitions. {req.prompt}"
                  f"{speech}{guide}").strip()
        task = "image_to_video" if req.first_frame is not None and not refs else ("reference_to_video" if refs and req.first_frame is None else "")
        res = req.resolution if req.resolution in ("360p", "720p", "1080p", "4k") else "720p"
        return self._call(inputs, prompt, res=res, aspect=req.aspect, duration=dur, task=task,
                          key_parts=(req.first_frame.id if req.first_frame else None, [r.id for r in req.refs[:4]], req.seed, req.audio))

    def extend(self, video: Asset, prompt: str, duration: float = 6, res: str = "720p", aspect: str = "9:16",
               take: int = 0) -> Asset:
        """Continúa la MISMA toma (misma voz y sala). `take` distingue regeneraciones (si no, la caché devuelve la anterior)."""
        prev = video.meta.get("interaction_id")
        if not prev:
            raise ProviderError("Omni extend: el vídeo no tiene interaction_id (solo se pueden extender vídeos generados)")
        dur = max(3, min(10, int(round(duration))))
        # sin la cláusula de texto, Omni incrusta subtítulos en las extensiones (comprobado en tomas reales)
        p = (f"Continue this exact video seamlessly for {dur} more seconds, same continuous shot, same person, same voice and room. "
             f"{prompt} {NO_TEXT}")
        return self._call([], p, res=res, aspect=aspect, duration=dur, task="extend", previous_id=prev, step="video",
                          key_parts=(video.id, take))


class GeminiOmniTalking:
    """Plano hablado con diálogo nativo de Omni (labios generados con el vídeo; voz propia del modelo)."""

    name = "gemini"

    def __init__(self, model: str = OMNI):
        self.omni = GeminiOmni(model)
        self.model = model

    def generate(self, req: TalkingRequest) -> Asset:
        lang = LOCALE_NAMES.get(req.locale, req.locale)
        voice = f" Voice: {req.voice_hint}." if req.voice_hint else ""
        prompt = (f"{req.prompt} The person speaks directly to the phone camera in {lang}, natural casual delivery with "
                  f"realistic pauses and breathing, and says exactly: «{req.dialogue}».{voice} Only this person speaks. "
                  f"No music, no background voices. {NO_TEXT}")
        return self.omni.generate(VideoRequest(prompt=prompt, first_frame=req.portrait, refs=req.refs, duration=req.duration,
                                               aspect=req.aspect, resolution=req.resolution, audio=True, seed=req.seed))


# ───────────────────────────── Música ─────────────────────────────


class GeminiMusic:
    name = "gemini"

    def __init__(self, model: str = MUSIC_MODEL):
        self.model = model

    def generate(self, prompt: str, duration: float) -> Asset:
        t = _types()
        key = cache_key("music", self.model, prompt, round(duration))
        hit = cache_get(key)
        if hit:
            record_cached("music", "gemini", self.model)
            return ctx().db.get_asset(hit["asset"])
        unit = price("gemini", self.model, None, 0.04)
        with meter("music", "gemini", self.model, est_usd=unit) as mt:
            def go():
                try:
                    return client().models.generate_content(
                        model=self.model, contents=prompt, config=t.GenerateContentConfig(response_modalities=["AUDIO"]))
                except Exception as e:  # noqa: BLE001
                    raise _wrap(e) from e

            resp = with_retries(go)
            data, mime = None, "audio/mpeg"
            for cand in resp.candidates or []:
                for p in (cand.content.parts if cand.content else []) or []:
                    if getattr(p, "inline_data", None) and p.inline_data.data:
                        data, mime = p.inline_data.data, p.inline_data.mime_type or mime
            if not data:
                raise ProviderError("Lyria: sin audio")
            mt.set("request", 1, unit, note=mime)
        if "L16" in mime or "pcm" in mime.lower():
            tmp = ctx().work("music") / f"{key[:12]}.wav"
            pcm_to_wav(data, tmp, rate=48000, channels=2)
            a = ctx().assets.ingest(tmp, source=f"gemini:{self.model}", meta={"prompt": prompt}, move=True)
        else:
            ext = mimetypes.guess_extension(mime) or ".mp3"
            a = ctx().assets.ingest_bytes(data, ext, source=f"gemini:{self.model}", meta={"prompt": prompt})
        cache_put(key, {"asset": a.id})
        return a


# ───────────────────────────── Revisión de vídeo (QA) ─────────────────────────────


class GeminiJudge:
    name = "gemini"

    def __init__(self, model: str = JUDGE_MODEL):
        self.model = model

    def review(self, video: Asset, prompt: str, schema: dict[str, Any], *, refs: list[Asset] | None = None,
               fps: float = 2.0, step: str = "qa") -> Any:
        t = _types()
        key = cache_key("judge", self.model, video.id, prompt, schema, [r.id for r in refs or []], fps)
        hit = cache_get(key)
        if hit is not None:
            record_cached(step, "gemini", self.model)
            return hit
        c = client()
        path = ctx().assets.abspath(video)
        dur = video.duration or 30
        est = token_cost("gemini", self.model, int(dur * fps * 280 + dur * 32 + 3000), 3000, video_in_tokens=int(dur * fps * 280))
        with meter(step, "gemini", self.model, est_usd=est) as mt:
            def upload():
                try:
                    f = c.files.upload(file=str(path), config={"mime_type": "video/mp4"})
                    deadline = time.time() + 300
                    while getattr(f.state, "name", str(f.state)) == "PROCESSING":
                        if time.time() > deadline:
                            raise ProviderError("Files API: procesamiento demasiado lento", retryable=True)
                        time.sleep(3)
                        f = c.files.get(name=f.name)
                    if getattr(f.state, "name", str(f.state)) == "FAILED":
                        raise ProviderError("Files API: procesamiento fallido")
                    return f
                except ProviderError:
                    raise
                except Exception as e:  # noqa: BLE001
                    raise _wrap(e) from e

            f = with_retries(upload)
            try:
                parts: list[Any] = [t.Part(file_data=t.FileData(file_uri=f.uri, mime_type="video/mp4"),
                                           video_metadata=t.VideoMetadata(fps=fps))]
                for i, r in enumerate(refs or []):
                    parts.append(f"[Reference image {i + 1}]")
                    parts.append(_image_part(r))
                parts.append(prompt)
                cfg = t.GenerateContentConfig(response_mime_type="application/json", response_json_schema=schema, temperature=0.2)

                def go():
                    try:
                        return c.models.generate_content(model=self.model, contents=parts, config=cfg)
                    except Exception as e:  # noqa: BLE001
                        raise _wrap(e) from e

                resp = with_retries(go)
            finally:
                try:
                    c.files.delete(name=f.name)
                except Exception:
                    pass
            pi, po = _usage(resp)
            vt = _video_tokens(resp)
            mt.set_usd(token_cost("gemini", self.model, pi, po, video_in_tokens=vt), unit="tokens", quantity=pi + po,
                       note=f"in={pi} (video {vt}) out={po} fps={fps}")
        data = _parse_json(resp.text or "")  # sin JSON válido → error (el QA quedará «sin revisión visual», nunca aprobado)
        if data:
            cache_put(key, data)
        return data
