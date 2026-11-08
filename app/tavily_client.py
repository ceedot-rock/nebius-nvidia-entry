"""Tavily web search — default search provider for hired-agent research.

Hired agents research through here: fresh web context keyed by the
TAVILY_API_KEY environment secret. Fail-closed with a Corey-readable
hint when the key is absent. No key is ever committed. Only stdlib +
requests (already a dependency).
"""
import os
import re

import requests

from config import TAVILY_API_KEY as CONFIG_KEY

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


class TavilyError(Exception):
    """Any Tavily search failure."""


RESEARCH_SIGNALS = re.compile(
    r"\b(research|latest|current|news|compar|versus|\bvs\b|"
    r"what (is|are|was|were)|who (is|are|was|were)|trend|"
    r"how (much|many)|summariz|state of|price of)\b",
    re.IGNORECASE,
)


def looks_like_research(task):
    """True when the task reads like research (default-on signal)."""
    return bool(task and RESEARCH_SIGNALS.search(task))


def _key():
    """Live env first (rotation-friendly), config constant as fallback."""
    return os.environ.get("TAVILY_API_KEY", "").strip() or (CONFIG_KEY or "").strip()


def search(query, max_results=3, search_depth="basic", timeout=30):
    """Run one Tavily search. Returns a list of title/url/content/score.

    Raises TavilyError on any failure (missing key, auth, transport,
    unexpected shape). Cost control: basic depth unless advanced is
    asked for, max_results clamped to 1..10.
    """
    q = (query or "").strip()
    if not q:
        raise TavilyError("empty query — nothing to search.")
    key = _key()
    if not key:
        raise TavilyError(
            "TAVILY_API_KEY is not set. "
            "Corey: copy a key from https://app.tavily.com/home "
            "and export TAVILY_API_KEY."
        )
    try:
        n = max(1, min(10, int(max_results or 3)))
    except (TypeError, ValueError):
        n = 3
    depth = "advanced" if search_depth == "advanced" else "basic"
    try:
        r = requests.post(
            TAVILY_SEARCH_URL,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"query": q, "search_depth": depth, "max_results": n},
            timeout=timeout,
        )
    except requests.RequestException as e:
        raise TavilyError(f"request failed: {e}")
    if r.status_code == 401:
        raise TavilyError("401 Unauthorized — check TAVILY_API_KEY.")
    if r.status_code == 429:
        raise TavilyError("429 rate limited — slow down or check credits.")
    if r.status_code != 200:
        raise TavilyError(f"HTTP {r.status_code}: {r.text[:300]}")
    try:
        results = r.json()["results"]
        if not isinstance(results, list):
            raise ValueError("results is not a list")
    except (KeyError, ValueError) as e:
        raise TavilyError(f"unexpected response shape: {e}; body: {r.text[:300]}")
    out = []
    for h in results[:n]:
        if not isinstance(h, dict):
            continue
        out.append(
            {
                "title": str(h.get("title") or "")[:200],
                "url": str(h.get("url") or "")[:500],
                "content": str(h.get("content") or "")[:1500],
                "score": h.get("score"),
            }
        )
    return out


def format_context(hits, limit_chars=3000):
    """One prompt-ready context block, hard-capped so context stays bounded."""
    if not hits:
        return ""
    try:
        cap = max(1, int(limit_chars or 3000))
    except (TypeError, ValueError):
        cap = 3000
    lines = ["Fresh web sources (Tavily default search):"]
    for i, h in enumerate(hits, 1):
        lines.append(f"{i}. {h.get('title') or 'untitled'} — {h.get('url') or 'no url'}")
        if h.get("content"):
            lines.append(f"   {h['content'][:400]}")
    return "\n".join(lines)[:cap]
