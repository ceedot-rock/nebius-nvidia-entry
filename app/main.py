"""Rider Marketplace — hire a verified AI agent powered by Nemotron.

Demo app for the Nebius x NVIDIA Global AI Hackathon.
Track: Best Apps and Agents.

Flow: discover agents (live Rider registry) -> verify credential ->
hire -> Nemotron executes -> demo payment receipt (no live x402
settlement; the AwLPay x402 wiring is planned, not implemented).
"""
import hmac
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, render_template, request

from config import NEMOTRON_REASONING, RIDER_BASE_URL
from nebius_client import chat, NebiusError
from rider_client import search_agents, verify_credential, RiderError

app = Flask(__name__)

# Fallback personas if the live registry is unreachable. Each maps to a
# Nemotron system prompt specialty. These are clearly labeled as fallback.
FALLBACK_AGENTS = [
    {
        "id": "fallback-code-reviewer",
        "name": "Code Reviewer (demo)",
        "skills": ["Python", "JavaScript", "security review"],
        "price_usd": 0.10,
        "system_prompt": (
            "You are an expert code reviewer. Review the user's code for "
            "bugs, security issues, and style. Be specific and actionable."
        ),
        "fallback": True,
    },
    {
        "id": "fallback-writer",
        "name": "Writer (demo)",
        "skills": ["copywriting", "editing", "summarization"],
        "price_usd": 0.05,
        "system_prompt": (
            "You are a professional writer and editor. Help the user write "
            "clear, compelling text. Match their tone."
        ),
        "fallback": True,
    },
]


def _agents_for_display():
    """Live registry agents, or fallback personas if unreachable."""
    try:
        live = search_agents(limit=6)
        agents = []
        for a in live:
            agents.append(
                {
                    "id": str(a.get("id") or a.get("agent_id")),
                    "name": a.get("name", "Unnamed agent"),
                    "skills": a.get("capabilities", []) or [],
                    "trust_score": a.get("trust_score"),
                    "tasks_completed": a.get("tasks_completed", 0),
                    "price_usd": 0.10,
                    "system_prompt": (
                        "You are a helpful AI agent hired for a task. "
                        f"Your listed skills are: {', '.join(a.get('capabilities', []) or ['general'])}. "
                        "Complete the user's task thoroughly."
                    ),
                    "fallback": False,
                }
            )
        return agents, "live"
    except RiderError:
        return FALLBACK_AGENTS, "fallback"


@app.route("/")
def index():
    return render_template(
        "index.html", api_key=os.environ.get("NEBIUS_ENTRY_API_KEY", "")
    )


def _require_api_key():
    """Shared-secret gate for /api/hire (each call spends Nebius credits).

    Compares the X-API-Key header against NEBIUS_ENTRY_API_KEY in
    constant time. Refuses with 401 when the env var is unset or the
    header is missing/mismatched — the endpoint is never open.
    """
    expected = os.environ.get("NEBIUS_ENTRY_API_KEY", "")
    provided = request.headers.get("X-API-Key", "")
    if not expected or not hmac.compare_digest(provided, expected):
        return jsonify({"error": "invalid or missing X-API-Key"}), 401
    return None


@app.route("/api/agents")
def list_agents():
    """Live agent directory from the Rider registry."""
    agents, source = _agents_for_display()
    return jsonify(
        {"agents": agents, "source": source, "rider_base": RIDER_BASE_URL}
    )


@app.route("/api/verify", methods=["POST"])
def verify():
    """Verify a rider JWT credential. Free, no auth needed."""
    data = request.get_json(force=True)
    token = (data.get("rider") or "").strip()
    if not token:
        return jsonify({"error": "rider JWT is required"}), 400
    try:
        valid, details = verify_credential(token)
    except RiderError as e:
        return jsonify({"error": f"Rider verify failed: {e}"}), 502
    return jsonify({"valid": valid, "rider": details})


@app.route("/api/hire", methods=["POST"])
def hire():
    """Hire an agent: run Nemotron on the task, return result + receipt."""
    auth_error = _require_api_key()
    if auth_error:
        return auth_error
    data = request.get_json(force=True)
    agent_id = data.get("agent_id")
    task = (data.get("task") or "").strip()
    if not agent_id:
        return jsonify({"error": "agent_id is required"}), 400
    if not task:
        return jsonify({"error": "task is required"}), 400

    agents, source = _agents_for_display()
    agent = next((a for a in agents if a["id"] == agent_id), None)
    if not agent:
        return jsonify({"error": f"unknown agent: {agent_id}"}), 404

    # Execute the task with Nemotron 3 Ultra (reasoning model)
    try:
        result = chat(
            NEMOTRON_REASONING,
            [
                {"role": "system", "content": agent["system_prompt"]},
                {"role": "user", "content": task},
            ],
            max_tokens=2048,
        )
    except NebiusError as e:
        return jsonify({"error": f"Nemotron inference failed: {e}"}), 502

    # Demo payment receipt. No on-chain x402 settlement happens here:
    # the AwLPay x402 wiring is planned, not implemented. This only shows
    # the receipt shape (status "demo_receipt").
    payment = {
        "status": "demo_receipt",
        "amount_usd": agent["price_usd"],
        "network": "base-sepolia",
        "note": "Demo receipt only — no live x402 settlement (AwLPay integration planned)",
    }

    return jsonify(
        {
            "agent": agent["name"],
            "agent_source": source,
            "model": NEMOTRON_REASONING,
            "result": result,
            "payment": payment,
        }
    )


@app.route("/healthz")
def healthz():
    return jsonify({"ok": True, "service": "rider-marketplace"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
