"""Rider client — real Agent Rider integration.

All endpoints live at https://agentrider.fly.dev (verified 2026-10-04).
Free paths used by the demo: /api/registry, /api/rider/verify.
"""
import requests

from config import RIDER_BASE_URL


class RiderError(Exception):
    """Any Rider API failure."""


def search_agents(query="", limit=10, timeout=30):
    """Search the live agent registry. Returns list of agent dicts."""
    url = f"{RIDER_BASE_URL}/api/registry"
    params = {"limit": limit}
    if query:
        params["q"] = query
    try:
        r = requests.get(url, params=params, timeout=timeout)
    except requests.RequestException as e:
        raise RiderError(f"registry request failed: {e}")
    if r.status_code != 200:
        raise RiderError(f"registry HTTP {r.status_code}: {r.text[:200]}")
    try:
        data = r.json()
    except ValueError as e:
        raise RiderError(f"registry bad JSON: {e}")
    # Response shape: list or {"agents": [...]} — handle both
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("agents", "results", "items"):
            if key in data and isinstance(data[key], list):
                return data[key]
    raise RiderError(f"unexpected registry shape: {str(data)[:200]}")


def verify_credential(jwt_token, timeout=30):
    """Verify a rider JWT via the free /api/rider/verify endpoint.

    Returns (valid: bool, details: dict).
    """
    url = f"{RIDER_BASE_URL}/api/rider/verify"
    try:
        r = requests.post(url, json={"rider": jwt_token}, timeout=timeout)
    except requests.RequestException as e:
        raise RiderError(f"verify request failed: {e}")
    if r.status_code != 200:
        raise RiderError(f"verify HTTP {r.status_code}: {r.text[:200]}")
    try:
        data = r.json()
    except ValueError as e:
        raise RiderError(f"verify bad JSON: {e}")
    return bool(data.get("valid")), data.get("rider", {})
