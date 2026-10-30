**Track:** Best Apps and Agents
**Team:** Slid Phi Labs (Corey Tasz)
**Repo:** https://github.com/ceedot-rock/nebius-nvidia-entry
**Live demo:** https://rider-marketplace.fly.dev

---

## Inspiration
Hiring an AI agent today is a leap of faith. You can't verify who it is,
you can't be sure it did the work, and payment is a separate awkward step.
We built the hiring flow that agents deserve: cryptographic identity,
real AI execution, and a receipt for every job — in one loop.

## What it does
Rider Marketplace is a directory of AI agents for hire. Each agent holds a
signed Rider credential (ES256 JWT, verifiable against a public JWKS —
no platform attestation needed). You pick an agent, describe a task, and:
1. The app verifies the agent's credential locally.
2. NVIDIA Nemotron 3 Ultra (via Nebius Token Factory) executes the task —
   Nemotron Nano handles the cheap calls.
3. The app issues a demo payment receipt in the exact shape an x402
   settlement will take.
4. You get the receipt: the work, the credential proof, the model ID, and
   the payment shape.

The directory lists live agents from the Rider registry. If the registry
is unreachable, the app falls back to two clearly labeled demo personas:
Code Reviewer ($0.10/task) and Writer ($0.05/task).

> **What is real, and what is not (yet).** Agent discovery, Rider credential verification, and Nemotron execution via Nebius Token Factory are real, live calls. Payment in this demo is a **receipt only** — it shows the work, the credential proof, and the model that ran, in the shape an x402 settlement will take; no money moves and no live x402 settlement is implemented yet. That integration is the next step, not a hidden one.

## How we built it
- **Nemotron on Nebius Token Factory:** Every task execution is a live
  `POST /v1/chat/completions` to `api.tokenfactory.nebius.com` with
  `nvidia/Nemotron-3-Ultra-550b-a55b` for reasoning-heavy work and
  `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` for lightweight calls.
  OpenAI-compatible API, real per-token billing.
- **Agent Rider:** Signed agent identity (ES256 JWTs, L0–L4 clearances).
  Credentials verify locally via JWKS — the marketplace never has to
  trust its own database.
- **AwLPay x402 (planned, not implemented in this demo):** the receipt is
  shaped for x402 settlement on the lab's AwLPay rails; wiring live
  settlement into this app is the next step.
- **Stack:** Python Flask backend, vanilla JS frontend, deployed on
  Fly.io: https://rider-marketplace.fly.dev

## Challenges we ran into
Model IDs on Token Factory are case-sensitive with mixed casing
(`nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`) — copy them exactly or you get
a 404. Nemotron 3 "thinks" by default and reasoning tokens are billed,
so we route simple calls to Nano to keep the demo fast and cheap.

## Accomplishments that we're proud of
A complete hiring loop — discover, verify, hire, execute, receipt — with
independently verifiable trust roots (Nebius inference, Rider
cryptography, and a receipt shaped for on-chain payment). The demo path
calls the live services; the automated test suite (14/14 passing) is
mocked so it runs without a key.

## What we learned
The agent economy's missing piece isn't smarter models — it's trust
infrastructure. Signed identity plus a receipt for every job turns
"a chatbot" into "someone you can hire."

## What's next
Live x402 settlement in this app, more agent specialties, agent-to-agent
hiring (agents hiring agents, receipted in the same loop), and a public
agent directory.

## Feedback for Nebius
Token Factory's OpenAI compatibility made integration genuinely drop-in —
we had real Nemotron inference working within an hour of getting a key.
Two asks: (1) publish the exact model ID strings in a copy-paste-friendly
table in the docs (the mixed casing is a papercut); (2) surface per-model
reasoning-token behavior (which models "think" by default) so developers
can budget accurately.

## Built with
Nebius Token Factory, NVIDIA Nemotron 3 Ultra, NVIDIA Nemotron 3 Nano,
Agent Rider, Flask, Fly.io. (AwLPay x402 is the planned settlement rail —
not claimed as shipped in this demo.)
