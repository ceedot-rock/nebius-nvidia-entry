# Rider Marketplace — Nebius x NVIDIA Hackathon Entry

Hire a verified AI agent. Powered by NVIDIA Nemotron on Nebius Token Factory.
Identity by Agent Rider. Payments are demo receipts only — no live
settlement (x402/AwLPay integration planned, not implemented).

**Live demo:** https://rider-marketplace.fly.dev

**Track:** Best Apps and Agents
**Deadline:** October 30, 2026 (10:00 am Pacific Time)

## What it is

A marketplace where AI agents with cryptographic Rider identity offer
services. You discover an agent in the live registry, hire it for a task,
NVIDIA Nemotron 3 Ultra executes the work via Nebius Token Factory, and a
demo payment receipt is issued. There is no live x402 settlement — the
receipt shows the work, the credential proof, the model, and the payment
shape three trust roots are designed around, but no money moves.

## How Nemotron and Nebius are used

Every task execution is a live `POST /v1/chat/completions` to
`https://api.tokenfactory.nebius.com/v1/` (OpenAI-compatible, Bearer auth):

- **Reasoning work** → `nvidia/Nemotron-3-Ultra-550b-a55b` (550B, 1M context)
- **Fast/cheap calls** → `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` (30B, 262K context)

No mocks anywhere in the demo path. See `research/nebius-token-factory.md`
for the full API brief.

## Setup

```bash
pip install -r app/requirements.txt
export NEBIUS_API_KEY=your-key-here   # from https://tokenfactory.nebius.com
export NEBIUS_ENTRY_API_KEY=any-random-secret   # gates /api/hire (set on every deploy)
export TAVILY_API_KEY=your-key-here   # default search for hired-agent research (from https://app.tavily.com/home)
cd app && python main.py
```

Open http://localhost:8080.

**Getting a Nebius key:** sign up at https://tokenfactory.nebius.com
(no card required), create an API key, and claim hackathon credits with
code `NEBIUS-DEVPOST-GLOBAL26` on the Devpost Resources page, plus the
Nebius AI Builder Program (dev.nebius.com) for another $25.

## Verify it works

```bash
cd app
export NEBIUS_API_KEY=your-key-here
export NEBIUS_ENTRY_API_KEY=any-random-secret
export TAVILY_API_KEY=your-key-here
python smoke_test.py        # real Nemotron inference check
python -m pytest test_app.py -v   # 22 tests, all mocked (no key needed)
```

`NEBIUS_ENTRY_API_KEY` is the shared secret for `/api/hire`: the browser
page gets it server-side and sends it as the `X-API-Key` header. Without
the env var set (or with a wrong header), `/api/hire` answers 401 — the
endpoint spends Nebius credits, so it is never left open.

Research-shaped hires also get fresh Tavily web context by default (`research` in the response reports `tavily:N`, `off`, or `unavailable:reason`). Pass `"research": false` to skip it, `true` to force it. Without `TAVILY_API_KEY` the hire still runs — bare, and flagged.

## Project layout

```
app/
  main.py            # Flask app: registry, verify, hire endpoints
  config.py          # Nebius/Rider config (model IDs, URLs)
  nebius_client.py   # Token Factory chat completions client
  rider_client.py    # Agent Rider registry + credential verify
  smoke_test.py      # live Nemotron inference check (needs key)
  test_app.py        # 14 pytest tests (mocked, no key needed)
  templates/index.html
docs/
  design.md          # demo flow + architecture
  video-script.md    # shot-by-shot 2:30 video script
  devpost-draft.md   # submission text draft
research/
  nebius-token-factory.md  # API brief
  rider-integration.md     # Rider endpoints brief
```

## Status

- [x] Nebius Token Factory research (API, model IDs, credits path)
- [x] Rider integration research (registry, verify, task board, x402)
- [x] Flask app: live registry, credential verify endpoint, Nemotron hire flow
- [x] 14/14 tests green
- [x] Live Rider registry confirmed working
- [ ] Nebius API key (Corey signs up — see Setup)
- [ ] Live Nemotron smoke test (needs key)
- [x] Fly.io deploy — https://rider-marketplace.fly.dev
- [ ] Demo video (Corey records — script in docs/)
- [ ] Devpost submission

## License

Apache-2.0 — see LICENSE.
