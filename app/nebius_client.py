"""Nebius Token Factory client — real Nemotron inference, no mocks.

Uses the OpenAI-compatible chat completions API at
https://api.tokenfactory.nebius.com/v1/chat/completions
with Bearer auth. Model IDs are case-sensitive.
"""
import requests

from config import NEBIUS_API_KEY, NEBIUS_BASE_URL


class NebiusError(Exception):
    """Any Nebius API failure."""


def chat(model, messages, max_tokens=1024, temperature=0.7, timeout=120):
    """Send a chat completion request. Returns the assistant's text.

    messages: list of {"role": ..., "content": ...} dicts.
    Raises NebiusError on any failure (auth, rate limit, model error).
    """
    if not NEBIUS_API_KEY:
        raise NebiusError(
            "NEBIUS_API_KEY is not set. "
            "Corey: create a key at https://tokenfactory.nebius.com "
            "and export NEBIUS_API_KEY."
        )
    url = NEBIUS_BASE_URL.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {NEBIUS_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=timeout)
    except requests.RequestException as e:
        raise NebiusError(f"request failed: {e}")
    if r.status_code == 401:
        raise NebiusError("401 Unauthorized — check NEBIUS_API_KEY.")
    if r.status_code == 429:
        raise NebiusError("429 rate limited — slow down or check credits.")
    if r.status_code != 200:
        raise NebiusError(f"HTTP {r.status_code}: {r.text[:300]}")
    try:
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, ValueError) as e:
        raise NebiusError(f"unexpected response shape: {e}; body: {r.text[:300]}")


def list_models(timeout=30):
    """Return the live model catalog (requires auth)."""
    if not NEBIUS_API_KEY:
        raise NebiusError("NEBIUS_API_KEY is not set.")
    url = NEBIUS_BASE_URL.rstrip("/") + "/models?verbose=true"
    headers = {"Authorization": f"Bearer {NEBIUS_API_KEY}"}
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json()
