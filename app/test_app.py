"""Tests for Rider Marketplace. No external calls — all mocked.

Run: python3 -m pytest test_app.py -v
"""
import sys
from unittest.mock import patch

sys.path.insert(0, ".")

import pytest

import main

FAKE_LIVE = [
    {
        "id": "abc123",
        "name": "TestCoder",
        "skills": ["python"],
        "trust_score": 42,
        "tasks_completed": 7,
        "price_usd": 0.10,
        "system_prompt": "You are a test coder.",
        "fallback": False,
    }
]

TEST_API_KEY = "test-entry-secret"


@pytest.fixture
def authed(monkeypatch):
    """Set the hire-gate secret and return the matching request headers."""
    monkeypatch.setenv("NEBIUS_ENTRY_API_KEY", TEST_API_KEY)
    return {"X-API-Key": TEST_API_KEY}


@pytest.fixture
def client():
    main.app.config["TESTING"] = True
    with main.app.test_client() as c:
        yield c


def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.get_json()["ok"] is True


def test_index_loads(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"Rider Marketplace" in r.data


def test_list_agents_live(client):
    with patch.object(main, "search_agents", return_value=[
        {"id": "abc123", "name": "TestCoder", "capabilities": ["python"],
         "trust_score": 42, "tasks_completed": 7}
    ]):
        r = client.get("/api/agents")
    assert r.status_code == 200
    d = r.get_json()
    assert d["source"] == "live"
    assert len(d["agents"]) == 1
    assert d["agents"][0]["name"] == "TestCoder"
    assert d["agents"][0]["trust_score"] == 42


def test_list_agents_fallback(client):
    with patch.object(main, "search_agents", side_effect=main.RiderError("down")):
        r = client.get("/api/agents")
    assert r.status_code == 200
    d = r.get_json()
    assert d["source"] == "fallback"
    assert len(d["agents"]) == 2


def test_verify_missing_token(client):
    r = client.post("/api/verify", json={})
    assert r.status_code == 400


def test_verify_ok(client):
    with patch.object(main, "verify_credential",
                       return_value=(True, {"agent_id": "abc", "level": "L1"})):
        r = client.post("/api/verify", json={"rider": "fake.jwt.here"})
    assert r.status_code == 200
    d = r.get_json()
    assert d["valid"] is True
    assert d["rider"]["level"] == "L1"


def test_hire_no_key_401(client, monkeypatch):
    monkeypatch.setenv("NEBIUS_ENTRY_API_KEY", TEST_API_KEY)
    r = client.post("/api/hire", json={"agent_id": "abc123", "task": "hi"})
    assert r.status_code == 401


def test_hire_wrong_key_401(client, monkeypatch):
    monkeypatch.setenv("NEBIUS_ENTRY_API_KEY", TEST_API_KEY)
    r = client.post(
        "/api/hire",
        json={"agent_id": "abc123", "task": "hi"},
        headers={"X-API-Key": "wrong-secret"},
    )
    assert r.status_code == 401


def test_hire_key_unset_401(client, monkeypatch):
    # No env var at all: the endpoint must stay closed, not silently open.
    monkeypatch.delenv("NEBIUS_ENTRY_API_KEY", raising=False)
    r = client.post(
        "/api/hire",
        json={"agent_id": "abc123", "task": "hi"},
        headers={"X-API-Key": "anything"},
    )
    assert r.status_code == 401


def test_hire_right_key_passes_through(client, authed):
    fake_result = "MOCKED: pass-through works."
    with patch.object(main, "_agents_for_display", return_value=(FAKE_LIVE, "live")), \
         patch.object(main, "chat", return_value=fake_result):
        r = client.post(
            "/api/hire",
            json={"agent_id": "abc123", "task": "hi"},
            headers=authed,
        )
    assert r.status_code == 200
    d = r.get_json()
    assert d["result"] == fake_result
    assert d["payment"]["status"] == "demo_receipt"


def test_hire_unknown_agent(client, authed):
    with patch.object(main, "_agents_for_display", return_value=(FAKE_LIVE, "live")):
        r = client.post("/api/hire", json={"agent_id": "nope", "task": "hi"},
                        headers=authed)
    assert r.status_code == 404


def test_hire_empty_task(client, authed):
    with patch.object(main, "_agents_for_display", return_value=(FAKE_LIVE, "live")):
        r = client.post("/api/hire", json={"agent_id": "abc123", "task": "  "},
                        headers=authed)
    assert r.status_code == 400


def test_hire_success_mocked(client, authed):
    fake_result = "MOCKED: here is your code review."
    with patch.object(main, "_agents_for_display", return_value=(FAKE_LIVE, "live")), \
         patch.object(main, "chat", return_value=fake_result) as m:
        r = client.post(
            "/api/hire",
            json={"agent_id": "abc123", "task": "review: def f(x): return x"},
            headers=authed,
        )
    assert r.status_code == 200
    d = r.get_json()
    assert d["result"] == fake_result
    assert d["agent"] == "TestCoder"
    assert d["agent_source"] == "live"
    assert "Nemotron" in d["model"]
    assert m.call_args[0][0] == main.NEMOTRON_REASONING
    msgs = m.call_args[0][1]
    assert msgs[0]["role"] == "system"
    assert msgs[1]["content"] == "review: def f(x): return x"


def test_hire_nebius_failure(client, authed):
    with patch.object(main, "_agents_for_display", return_value=(FAKE_LIVE, "live")), \
         patch.object(main, "chat", side_effect=main.NebiusError("down")):
        r = client.post(
            "/api/hire", json={"agent_id": "abc123", "task": "write haiku"},
            headers=authed,
        )
    assert r.status_code == 502
    assert "Nemotron" in r.get_json()["error"]
