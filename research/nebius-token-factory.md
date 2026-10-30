# Nebius Token Factory — Technical Brief
**Research date:** 2026-10-04 · For the Nebius x NVIDIA Global AI Hackathon (Devpost deadline Oct 30, 2026)

---

## 1. What is Nebius Token Factory?

Nebius Token Factory is Nebius's managed inference platform for open-source LLMs — a single OpenAI-compatible API in front of 60+ hosted open models (DeepSeek, Qwen, Llama, gpt-oss, and NVIDIA Nemotron). You get one API key, no model hosting, and per-token billing.

- **Docs:** https://docs.tokenfactory.nebius.com/
- **Console / playground:** https://tokenfactory.nebius.com/
- **Product page:** https://nebius.com/services/token-factory/enterprise-grade-inference
- **Official code samples / workshops:** https://github.com/nebius/token-factory-cookbook (includes a `models/nemotron/` dir with notebooks)

How it works: inference + fine-tuning over an OpenAI-compatible REST API; a web playground for testing prompts; third-party framework integrations (OpenHands, LangChain, etc.); **Token Factory Sandboxes** (VM-isolated code execution, beta) are a separate capability under the same account.

⚠️ **Do not confuse with the old Nebius AI Studio** (`api.studio.nebius.ai`) — Token Factory's host is `api.tokenfactory.nebius.com`. Also note a regional endpoint appears in some docs (`api.tokenfactory.us-central1.nebius.com/v1/`); prefer the global one unless the docs say otherwise.

---

## 2. Inference API — exact details

| Item | Value |
|---|---|
| **Base URL** | `https://api.tokenfactory.nebius.com/v1/` |
| **Chat endpoint** | `POST https://api.tokenfactory.nebius.com/v1/chat/completions` |
| **Model catalog** | `GET https://api.tokenfactory.nebius.com/v1/models?verbose=true` (returns IDs, context length, per-token prices — **auth required**) |
| **Auth** | `Authorization: Bearer <NEBIUS_API_KEY>` header |
| **Protocol** | OpenAI-compatible (drop-in for the OpenAI SDK; streaming, JSON mode, and tool/function calling supported) |

### Getting the API key
1. Go to **https://tokenfactory.nebius.com/** and sign in (Google or GitHub login works).
2. Click your profile → **API Keys** section → **Get API Key** → name it (e.g. `hackathon`).
3. Copy the key immediately — it is shown only once. Store it as `NEBIUS_API_KEY`.

The same key authenticates both inference calls and the `GET /v1/models` catalog.

### Working curl example (placeholder key)

```bash
curl -s https://api.tokenfactory.nebius.com/v1/chat/completions \
  -H "Authorization: Bearer $NEBIUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Reply with exactly: NEEM"}
    ],
    "max_tokens": 32,
    "temperature": 0
  }'
```

### Python example (OpenAI SDK)

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=os.environ["NEBIUS_API_KEY"],
)

resp = client.chat.completions.create(
    model="nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B",
    messages=[{"role": "user", "content": "Say hello in one sentence."}],
    max_tokens=64,
)
print(resp.choices[0].message.content)
```

### List the live model catalog (authenticated)

```bash
curl -s https://api.tokenfactory.nebius.com/v1/models?verbose=true \
  -H "Authorization: Bearer $NEBIUS_API_KEY" | python3 -m json.tool | head -60
```

### Nemotron gotchas reported by other hackathon teams (from their public feedback docs)
- **Model IDs are case-sensitive** — copy exact casing; a wrong case 404s. E.g. `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` vs `nvidia/nemotron-3-super-120b-a12b` (mixed casing is real).
- **Nemotron 3 thinks by default** and reasoning tokens are billed (and can crowd out `max_tokens`). If you get empty `content` with `finish_reason=length`, the answer may be in `reasoning_content`; control thinking via `chat_template_kwargs.enable_thinking`.
- If in doubt, resolve the ID at runtime from `GET /v1/models?verbose=true` instead of hardcoding.

---

## 3. Available NVIDIA Nemotron model IDs

Per Nebius's official cookbook (`models/nemotron/README.md`) and live use by other hackathon entries:

| Model | Exact model ID | Size / active | Context | Price (input/output per 1M tokens) |
|---|---|---|---|---|
| Nemotron 3 Nano 30B | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` | 30B / 3B | 262K | ~$0.06 / $0.24 |
| Nemotron 3 Super 120B | `nvidia/nemotron-3-super-120b-a12b` | 120B / 12B | 256K | ~$0.30 / $0.90 |
| Nemotron 3 Ultra 550B | `nvidia/Nemotron-3-Ultra-550b-a55b` | 550B / 55B | 1M | ~$1.00 / $3.00 |
| Nemotron 3.5 Lightning | `nvidia/Nemotron-3_5-Lightning` | 30B / 3B MoE | 1M | (check catalog) |

Older NVIDIA-served IDs seen in the wild: `nvidia/llama-3.1-nemotron-70b-instruct`, `nvidia/Llama-3_1-Nemotron-Ultra-253B-v1` (slower, avoid). There is also a multimodal Nano Omni variant (`nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`, image/video/audio input) — confirm via catalog.

**Prices are participant-verified (Sept 2026), not official-published — re-verify with `GET /v1/models?verbose=true` once Corey has a key.** The Devpost track guidance: *"Reach for Nemotron 3 Ultra when you need serious reasoning, and let Nano or Super handle the fast, everyday calls, so your credits stretch further."*

---

## 4. Signup, free tier, and pricing

**Signup — no account created by me (as instructed). Corey's steps:**
1. Register for the hackathon on Devpost: https://nebiusglobalaihackathon.devpost.com/
2. Sign up at https://tokenfactory.nebius.com/ (Google or GitHub OAuth — no credit card stated as required for signup).
3. Create an API key (profile → API Keys), save it as `NEBIUS_API_KEY`.
4. Claim hackathon credits (see below) and verify the balance in the console.

**Free / cheap access:**
- New accounts get **free promotional credits** on signup ("Start Free" model — no permanent free tier, but you can test the playground and API with the promo credits).
- **Hackathon credits:** the Devpost Resources page (https://nebiusglobalaihackathon.devpost.com/resources) offers
  1. **$25 in Token Factory credits** via a claim form using activation code **`NEBIUS-DEVPOST-GLOBAL26`**
  2. **Another $25** by joining the free **Nebius AI Builder Program** (https://dev.nebius.com — also advertises $400+ in partner credits/discounts: Tavily, LangChain, LangSmith, etc.)
- Promo codes are redeemed in the console at **Balance → Top up → With promo code**.
- Billing is pay-per-token against your org balance; the **Usage** tab shows per-project spend. At Nano's $0.06/$0.24 per 1M tokens, $50 of credit buys roughly ~400k full requests — plenty for a demo.

**Rate limits:** No public per-model RPM/RPD numbers found in the docs — quota is credit-based. Budget defensively: route hot paths through Nano, reserve Super/Ultra for the reasoning-heavy steps.

---

## 5. Hackathon-specific guidance

- **Devpost:** https://nebiusglobalaihackathon.devpost.com/ — the challenge, tracks, prizes, official rules.
- **Resources page (credits + Discord + events):** https://nebiusglobalaihackathon.devpost.com/resources
  - **Nebius Discord server** (invite linked on the Resources page — support channel, builder community).
  - **Builders & Brews: Hack Edition** in-person meetups (find events: luma.com link on the Resources page) — attendees can unlock extra Token Factory / AI Cloud / Tavily credits.
- **Official workshop:** the `token-factory-cookbook` repo has a full `workshops/token-factory-workshop` getting-started walkthrough (env setup, API keys, notebooks).
- **Kilo AI tutorial:** https://blog.kilo.ai/p/kilo-x-nebius — walks through grabbing a Token Factory key and pointing an agent harness at it.

### What the judges require (per the Devpost page)
1. Runs on **Token Factory or Nebius AI Cloud** AND uses **≥1 NVIDIA open-source model** — our Nemotron-over-Token-Factory path satisfies this directly.
2. Working project + demo URL + **≤3-min public YouTube video** + **public repo** with an open-source license (Apache 2.0 / MIT / MPL 2.0) visible on the repo page.
3. README must explain **where Nemotron was used and how Token Factory helped**.
4. **Feedback on Nebius Token Factory / NVIDIA tools is a required submission section** (there's even a "Most Valuable Feedback" $100 prize, 10 winners).
5. Prizes: $50k+ total — Grand Prize $20k, 2nd $10k, 3rd $6k, each track winner gets an NVIDIA Jetson Orin Nano, Best Use of Tavily $3k, City Winners $500 × 20.

**Recommended lane for us:** *Coding and Agentic Engineering* or *Best Apps and Agents* track — a working agent loop with live Nemotron calls, demo video, honest feedback section. Judging weights: technological implementation (effective use of Token Factory + Nemotron), design, potential impact, quality of idea.
