"""Thin HTTP adapters for the supported LLM providers.

Each provider exposes two operations — text generation and listing available
models — over plain HTTP so we don't pull in three vendor SDKs.
"""
from __future__ import annotations

import httpx

from ..enums import LLMProvider

_TIMEOUT = httpx.Timeout(20.0)


def generate_text(provider: LLMProvider, api_key: str, model: str, prompt: str, system: str | None, max_tokens: int, temperature: float) -> str:
    if provider == LLMProvider.openai:
        return _openai_generate(api_key, model, prompt, system, max_tokens, temperature)
    if provider == LLMProvider.anthropic:
        return _anthropic_generate(api_key, model, prompt, system, max_tokens, temperature)
    return _gemini_generate(api_key, model, prompt, system, max_tokens, temperature)


def list_models(provider: LLMProvider, api_key: str) -> list[str]:
    if provider == LLMProvider.openai:
        return _openai_models(api_key)
    if provider == LLMProvider.anthropic:
        return _anthropic_models(api_key)
    return _gemini_models(api_key)


# --- OpenAI -----------------------------------------------------------------

def _openai_generate(api_key, model, prompt, system, max_tokens, temperature) -> str:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    # Current OpenAI models use `max_completion_tokens` (`max_tokens` is rejected by gpt-5.x).
    resp = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": model, "messages": messages, "max_completion_tokens": max_tokens, "temperature": temperature},
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _openai_models(api_key) -> list[str]:
    resp = httpx.get(
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    ids = [m["id"] for m in resp.json().get("data", [])]
    chat = sorted(i for i in ids if i.startswith("gpt-"))
    return chat or sorted(ids)


# --- Anthropic --------------------------------------------------------------

def _anthropic_headers(api_key) -> dict:
    return {"x-api-key": api_key, "anthropic-version": "2023-06-01"}


def _anthropic_generate(api_key, model, prompt, system, max_tokens, temperature) -> str:
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        payload["system"] = system
    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers=_anthropic_headers(api_key),
        json=payload,
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["content"][0]["text"].strip()


def _anthropic_models(api_key) -> list[str]:
    resp = httpx.get(
        "https://api.anthropic.com/v1/models",
        headers=_anthropic_headers(api_key),
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return [m["id"] for m in resp.json().get("data", [])]


# --- Gemini -----------------------------------------------------------------

def _gemini_generate(api_key, model, prompt, system, max_tokens, temperature) -> str:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature},
    }
    if system:
        payload["systemInstruction"] = {"parts": [{"text": system}]}
    resp = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        params={"key": api_key},
        json=payload,
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


def _gemini_models(api_key) -> list[str]:
    resp = httpx.get(
        "https://generativelanguage.googleapis.com/v1beta/models",
        params={"key": api_key},
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    models = []
    for m in resp.json().get("models", []):
        if "generateContent" in m.get("supportedGenerationMethods", []):
            models.append(m["name"].split("/")[-1])
    return models or [m["name"].split("/")[-1] for m in resp.json().get("models", [])]
