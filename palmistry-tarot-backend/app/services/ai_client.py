"""Thin wrapper around the OpenAI chat completions API.

Every failure mode here — no API key configured, network error, timeout,
rate limit, or a response that isn't valid JSON — is normalized into a
single `AIUnavailable` exception. Callers (see `insights.py`) catch that
one exception type and fall back to the deterministic, rule-based
interpreter, so a third-party outage never breaks a reading for the user.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache

from openai import APIConnectionError, APIError, APITimeoutError, OpenAI

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TIMEOUT_SECONDS = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "20"))


class AIUnavailable(Exception):
    """Raised for any condition where the caller should use the deterministic fallback."""


@lru_cache
def _client() -> OpenAI:
    # lru_cache means we only build the client once per process, and only
    # the first time it's actually needed — not at import time. That way
    # a deployment with no OPENAI_API_KEY set still boots and serves
    # deterministic readings; it just never reaches this function's happy path.
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise AIUnavailable("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key, timeout=OPENAI_TIMEOUT_SECONDS, max_retries=1)


def is_configured() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def chat_json(system_prompt: str, user_prompt: str) -> dict:
    """Call the model and parse a JSON object response.

    Raises AIUnavailable on any failure — missing key, network/timeout
    error, or a non-JSON response — so callers can catch one exception
    type and fall back safely.
    """
    try:
        client = _client()
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=700,
        )
    except AIUnavailable:
        raise
    except (APITimeoutError, APIConnectionError, APIError) as exc:
        raise AIUnavailable(f"OpenAI API call failed: {exc}") from exc
    except Exception as exc:  # noqa: BLE001 — an LLM outage must never break a reading
        raise AIUnavailable(f"Unexpected AI client error: {exc}") from exc

    choice = completion.choices[0] if completion.choices else None
    raw = choice.message.content if choice and choice.message else None
    if not raw:
        raise AIUnavailable("Empty response from model.")

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AIUnavailable(f"Model did not return valid JSON: {exc}") from exc
