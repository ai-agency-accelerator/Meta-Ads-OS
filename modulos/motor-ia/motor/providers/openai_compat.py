"""Cerebro alternativo vía OpenAI (Responses/Chat Completions). Se usa solo si no hay GEMINI_API_KEY."""

from __future__ import annotations

import json
from typing import Any

import httpx

from ..costs import cache_get, cache_key, cache_put, meter, record_cached, token_cost
from ..models import Asset
from ..store import ctx
from .base import ProviderError

MODEL = "gpt-5-mini"


class OpenAILLM:
    name = "openai"

    def __init__(self, model: str = MODEL):
        self.model = model

    def _chat(self, system: str, prompt: str, *, json_mode: bool, step: str, temperature: float, model: str | None) -> str:
        m = model or self.model
        k = cache_key("oai", m, system, prompt, json_mode, temperature)
        hit = cache_get(k)
        if hit:
            record_cached(step, "openai", m)
            return hit["text"]
        body: dict[str, Any] = {"model": m, "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}]}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        with meter(step, "openai", m, est_usd=0.01) as mt:
            r = httpx.post("https://api.openai.com/v1/chat/completions", json=body, timeout=180,
                           headers={"Authorization": f"Bearer {ctx().settings.key('OPENAI_API_KEY')}"})
            if r.status_code >= 400:
                raise ProviderError(f"OpenAI {r.status_code}: {r.text[:300]}", retryable=r.status_code in (429, 500, 503))
            j = r.json()
            u = j.get("usage", {})
            mt.set_usd(token_cost("openai", m, u.get("prompt_tokens", 0), u.get("completion_tokens", 0)), unit="tokens",
                       quantity=u.get("total_tokens", 0))
        text = j["choices"][0]["message"]["content"]
        cache_put(k, {"text": text})
        return text

    def json(self, system: str, prompt: str, schema: dict[str, Any] | None = None, *, images: list[Asset] | None = None,
             step: str = "llm", temperature: float = 0.7, model: str | None = None) -> Any:
        sys2 = system + "\nResponde SOLO con JSON válido" + (f" que cumpla este esquema: {json.dumps(schema)}" if schema else ".")
        return json.loads(self._chat(sys2, prompt, json_mode=True, step=step, temperature=temperature, model=model))

    def text(self, system: str, prompt: str, *, step: str = "llm", temperature: float = 0.7, model: str | None = None) -> str:
        return self._chat(system, prompt, json_mode=False, step=step, temperature=temperature, model=model)
