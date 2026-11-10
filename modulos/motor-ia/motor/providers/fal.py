"""Adaptadores fal.ai (cola REST). Se activan solos cuando existe FAL_KEY.

Endpoints y parámetros verificados en la documentación de fal el 2026-10-04 (pueden cambiar; revisa fal.ai/models):
  - fal-ai/kling-video/lipsync/audio-to-video   video_url, audio_url · 0,014 $ por bloque de 5 s · vídeo 2–10 s
  - fal-ai/kling-video/ai-avatar/v2/standard    image_url, audio_url, prompt · 0,0562 $/s
  - fal-ai/kling-video/v3/standard/image-to-video  start_image_url, prompt, end_image_url, elements, generate_audio(def true!)
  - minimax/h3-max/lip-sync/image-to-video      image_url, audio_url (≥5 s), resolution 768P · 0,08 $/s
  - bytedance/seedream/v5/lite/edit             prompt, image_urls (≤10) · 0,035 $/imagen
  - fal-ai/bytedance-upscaler/upscale/video     video_url, target_resolution · 0,0072 $/s a 1080p
Patrón: POST https://queue.fal.run/<id> (Authorization: Key …) → usar status_url/response_url devueltos.
Las URLs de salida son públicas y caducan: se descargan al momento.
"""

from __future__ import annotations

import math
import time
from typing import Any

import httpx

from ..costs import cache_get, cache_key, cache_put, meter, price, record_cached
from ..media import duration as media_duration
from ..models import Asset
from ..store import ctx
from .base import ImageRequest, ProviderError, TalkingRequest, VideoRequest

QUEUE = "https://queue.fal.run"


def _headers() -> dict[str, str]:
    key = ctx().settings.key("FAL_KEY")
    if not key:
        raise ProviderError("FAL_KEY no configurada")
    return {"Authorization": f"Key {key}", "Content-Type": "application/json"}


def upload(a: Asset) -> str:
    """Sube un asset a fal storage y devuelve URL pública (cacheada por id de asset)."""
    k = cache_key("fal_upload", a.id)
    hit = cache_get(k)
    if hit and time.time() - hit.get("ts", 0) < 6 * 24 * 3600:  # las URLs de subida caducan: se renuevan a los 6 días
        return hit["url"]
    import fal_client

    # la clave viene de la configuración del motor (no de os.environ, que fal_client leería por defecto)
    url = fal_client.SyncClient(key=ctx().settings.key("FAL_KEY")).upload_file(str(ctx().assets.abspath(a)))
    cache_put(k, {"url": url, "ts": time.time()})
    return url


def run(endpoint: str, body: dict[str, Any], *, timeout: float = 1200) -> dict[str, Any]:
    r = httpx.post(f"{QUEUE}/{endpoint}", json=body, headers=_headers(), timeout=60)
    if r.status_code >= 400:
        billing = r.status_code == 402 or (r.status_code == 403 and "balance" in r.text.lower())
        raise ProviderError(f"fal {endpoint} {r.status_code}: {r.text[:400]}", retryable=r.status_code in (429, 503),
                            moderation=r.status_code == 422, billing=billing)
    sub = r.json()
    status_url, response_url = sub["status_url"], sub["response_url"]
    ctx().db.cache_put(f"pending_gen:fal:{sub.get('request_id')}", {"provider": "fal", "endpoint": endpoint, "status_url": status_url,
                                                                   "response_url": response_url, "ts": time.time()})
    deadline = time.time() + timeout
    while True:
        if time.time() > deadline:
            raise ProviderError(f"fal {endpoint}: timeout", retryable=False)
        try:
            st = httpx.get(status_url, headers=_headers(), timeout=60).json()
        except Exception:  # noqa: BLE001  (el trabajo YA está aceptado: se sigue sondeando, no se reenvía)
            time.sleep(8)
            continue
        if st.get("status") == "COMPLETED":
            break
        time.sleep(4)
    res = httpx.get(response_url, headers=_headers(), timeout=120)
    if res.status_code >= 400:
        raise ProviderError(f"fal {endpoint} resultado {res.status_code}: {res.text[:400]}", moderation=res.status_code == 422)
    return res.json()


def _download(url: str, ext: str, meta: dict[str, Any]) -> Asset:
    r = httpx.get(url, timeout=300, follow_redirects=True)
    if r.status_code >= 400 or len(r.content) < 1000:
        raise ProviderError(f"fal: descarga fallida ({r.status_code}, {len(r.content)} bytes)", accepted=True)
    data = r.content
    return ctx().assets.ingest_bytes(data, ext, source=f"fal:{meta.get('endpoint', '')}", meta=meta)


def _video_url(res: dict[str, Any]) -> str:
    v = res.get("video") or (res.get("videos") or [{}])[0]
    if isinstance(v, dict) and v.get("url"):
        return v["url"]
    raise ProviderError(f"fal: respuesta sin vídeo: {str(res)[:200]}")


class FalKlingLipSync:
    """Boca nueva sobre una toma existente (banco del actor). Vídeo de entrada 2–10 s."""

    name = "fal"
    endpoint = "fal-ai/kling-video/lipsync/audio-to-video"
    model = endpoint

    def sync(self, video: Asset, audio: Asset) -> Asset:
        k = cache_key("fal_lipsync", self.endpoint, video.id, audio.id)
        hit = cache_get(k)
        if hit:
            record_cached("lipsync", "fal", self.endpoint)
            return ctx().db.get_asset(hit["asset"])
        d = video.duration or media_duration(ctx().assets.abspath(video))
        blocks = math.ceil(max(d, 2) / 5)
        unit = price("fal", self.endpoint, None, 0.014)
        with meter("lipsync", "fal", self.endpoint, est_usd=blocks * unit * 5) as m:
            res = run(self.endpoint, {"video_url": upload(video), "audio_url": upload(audio)})
            m.set("5s_block", blocks, unit * 5)
        a = _download(_video_url(res), ".mp4", {"endpoint": self.endpoint, "video": video.id, "audio": audio.id})
        cache_put(k, {"asset": a.id})
        return a


class FalKlingAvatar:
    """Retrato + audio (nuestra voz TTS persistente) → plano hablado. Para el banco y hooks."""

    name = "fal"
    endpoint = "fal-ai/kling-video/ai-avatar/v2/standard"
    model = endpoint

    def generate(self, req: TalkingRequest) -> Asset:
        if req.audio is None or req.portrait is None:
            raise ProviderError("Kling Avatar necesita retrato y audio")
        k = cache_key("fal_avatar", self.endpoint, req.portrait.id, req.audio.id, req.prompt)
        hit = cache_get(k)
        if hit:
            record_cached("video", "fal", self.endpoint)
            return ctx().db.get_asset(hit["asset"])
        d = req.audio.duration or 6
        unit = price("fal", self.endpoint, None, 0.0562)
        with meter("video", "fal", self.endpoint, est_usd=unit * d) as m:
            res = run(self.endpoint, {"image_url": upload(req.portrait), "audio_url": upload(req.audio), "prompt": req.prompt[:500]})
            m.set("second", d, unit)
        a = _download(_video_url(res), ".mp4", {"endpoint": self.endpoint})
        cache_put(k, {"asset": a.id})
        return a


class FalVideo:
    """Imagen→vídeo en fal (Kling 3.0 std por defecto; audio desactivado explícitamente)."""

    name = "fal"
    ENDPOINTS = {
        "kling-3": ("fal-ai/kling-video/v3/standard/image-to-video", 0.084),
        "minimax": ("minimax/h3/image-to-video", 0.06),
        "wan": ("fal-ai/wan/v3/image-to-video", 0.10),
    }

    def __init__(self, which: str = "kling-3"):
        self.endpoint, self.unit = self.ENDPOINTS.get(which, self.ENDPOINTS["kling-3"])
        self.model = self.endpoint

    def generate(self, req: VideoRequest) -> Asset:
        if req.first_frame is None:
            raise ProviderError("fal I2V necesita fotograma inicial")
        dur = int(min(10, max(3, round(req.duration))))
        k = cache_key("fal_i2v", self.endpoint, req.prompt, req.first_frame.id, dur, req.seed)
        hit = cache_get(k)
        if hit:
            record_cached("video", "fal", self.endpoint)
            return ctx().db.get_asset(hit["asset"])
        body: dict[str, Any] = {"prompt": req.prompt[:2400], "duration": str(dur), "generate_audio": False}
        if "kling" in self.endpoint:
            body["start_image_url"] = upload(req.first_frame)
            if req.negative_prompt:
                body["negative_prompt"] = req.negative_prompt
        else:
            body["image_url"] = upload(req.first_frame)
            body["resolution"] = "768P" if "minimax" in self.endpoint else "720p"
        with meter("video", "fal", self.endpoint, est_usd=self.unit * dur) as m:
            res = run(self.endpoint, body)
            m.set("second", dur, self.unit)
        a = _download(_video_url(res), ".mp4", {"endpoint": self.endpoint, "prompt": req.prompt})
        cache_put(k, {"asset": a.id})
        return a


class FalSeedreamEdit:
    name = "fal"
    endpoint = "bytedance/seedream/v5/lite/edit"
    model = endpoint

    def generate(self, req: ImageRequest) -> list[Asset]:
        out = []
        for i in range(max(1, req.n)):
            k = cache_key("fal_seedream", self.endpoint, req.prompt, [r.id for r in req.refs], req.seed, i)
            hit = cache_get(k)
            if hit:
                record_cached("image", "fal", self.endpoint)
                out.append(ctx().db.get_asset(hit["asset"]))
                continue
            unit = price("fal", self.endpoint, None, 0.035)
            with meter("image", "fal", self.endpoint, est_usd=unit) as m:
                res = run(self.endpoint, {"prompt": req.prompt, "image_urls": [upload(r) for r in req.refs][:10],
                                          "image_size": "portrait_16_9" if req.aspect == "9:16" else "square_hd"})
                m.set("image", 1, unit)
            img = (res.get("images") or [{}])[0].get("url")
            if not img:
                raise ProviderError("Seedream: sin imagen")
            a = _download(img, ".png", {"endpoint": self.endpoint, "prompt": req.prompt})
            cache_put(k, {"asset": a.id})
            out.append(a)
        return out


class FalUpscaler:
    name = "fal"
    endpoint = "fal-ai/bytedance-upscaler/upscale/video"
    model = endpoint

    def upscale(self, video: Asset, width: int, height: int) -> Asset:
        d = video.duration or 10
        unit = price("fal", self.endpoint, None, 0.0072)
        with meter("upscale", "fal", self.endpoint, est_usd=unit * d) as m:
            res = run(self.endpoint, {"video_url": upload(video), "target_resolution": "1080p"})
            m.set("second", d, unit)
        return _download(_video_url(res), ".mp4", {"endpoint": self.endpoint})
