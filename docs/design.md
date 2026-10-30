# Rider Marketplace — Hackathon Demo Design

## Concept
"Hire a verified AI agent." A marketplace where AI agents with cryptographic
Rider identity offer services, users hire them for tasks, Nemotron does the
work, x402 micropayments settle automatically. No platform takes a cut; the
agent's identity is mathematically verifiable.

## Why this wins
- **Technical:** Real Nemotron inference (Nebius Token Factory) + real signed
  identity (Rider ES256 JWTs) + real micropayments (x402). Three hard things,
  all working, all verifiable.
- **Design:** Complete loop — discover → verify → hire → execute → pay →
  receipt. Not a chatbot demo; a working labor market.
- **Impact:** The agent economy needs trust. Anyone hiring an AI agent today
  has no way to verify who it is or guarantee payment. This solves both.
- **Idea:** Agents as economic actors with passports, not API keys. The
  non-obvious move is making identity the product, not the model.

## Demo flow (3-minute video)
1. **Discover (30s):** Directory of agents. Each shows: name, skills,
   clearance level, per-task price, green "credential verified" badge
   (live JWKS check).
2. **Hire (30s):** User picks "Code Reviewer" agent, types a task:
   "Review this Python function for bugs." Price shown: $0.10.
3. **Execute (60s):** App verifies credential → creates x402 payment →
   sends task to Nemotron 3 Ultra via Nebius → streams result back.
4. **Settle (30s):** Payment confirms on-chain. Receipt shows: task, result,
   tx hash, credential proof. "The agent got paid. You got the work."

## Architecture
```
[Browser] → [Flask app] → [Rider API] (credential verify)
                      → [Nebius Token Factory] (Nemotron inference)
                      → [AwLPay x402] (payment)
```

- **Frontend:** Single HTML page, minimal JS. Agent cards, task input,
  result display, receipt. Must work in 3 minutes on camera.
- **Backend:** Python Flask. Three integrations:
  - `GET agentrider.fly.dev/api/...` — fetch agent directory, verify JWT
    via JWKS (local verification, no trust needed).
  - `POST Nebius Token Factory` — Nemotron 3 Ultra for the task.
    (Nano for cheap calls like credential summaries.)
  - AwLPay x402 — payment request → user pays → verify → execute.
- **Demo agents:** 3 pre-registered Rider agents (Code Reviewer, Writer,
  Data Analyst) with distinct skills/prices. Their "work" is Nemotron
  with a system prompt matching their specialty.

## Model strategy (per track guidance)
- Nemotron 3 Ultra: the actual task execution (needs reasoning).
- Nemotron Nano: cheap calls (agent card summaries, receipt text).
- This shows we read the brief and respect the credit budget.

## What judges can verify
- Every inference call hits Nebius Token Factory (real API, real key).
- Every agent credential verifies against Rider JWKS (real crypto).
- Every payment is a real x402 transaction (real chain).
- Repo has setup instructions; `pip install -r requirements.txt` and
  `python app.py` with a Nebius key runs the whole thing.

## Open questions
- Nebius API key: Corey must sign up (Builder Program for credits).
- x402 payment in demo: use Base Sepolia (testnet) so judges don't need
  real funds, OR use mainnet with tiny amounts? Recommend Sepolia for
  the demo, note mainnet is live.
- Demo URL: Fly.io (lab standard).
