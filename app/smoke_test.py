"""Smoke test: verify Nebius Token Factory connectivity and Nemotron inference.

Usage:
    export NEBIUS_API_KEY=your-key-here
    python smoke_test.py

Exits 0 on success, 1 on any failure. Prints exactly what it checked.
"""
import sys

sys.path.insert(0, ".")

from config import NEMOTRON_FAST
from nebius_client import chat, NebiusError


def main():
    print("Nebius Token Factory smoke test")
    print("=" * 40)

    # 1. Key present
    from config import NEBIUS_API_KEY
    if not NEBIUS_API_KEY:
        print("FAIL: NEBIUS_API_KEY is not set")
        return 1
    print("ok: API key is set")

    # 2. Real inference call to Nemotron Nano (cheap)
    print(f"calling {NEMOTRON_FAST} ...")
    try:
        out = chat(
            NEMOTRON_FAST,
            [{"role": "user", "content": "Reply with exactly: SMOKE OK"}],
            max_tokens=32,
            temperature=0.0,
        )
    except NebiusError as e:
        print(f"FAIL: inference error: {e}")
        return 1
    print(f"ok: got response: {out.strip()[:60]!r}")

    # 3. Response is non-empty
    if not out.strip():
        print("FAIL: empty response")
        return 1
    print("ok: non-empty response")

    print("=" * 40)
    print("SMOKE TEST PASSED — real Nemotron inference via Nebius Token Factory")
    return 0


if __name__ == "__main__":
    sys.exit(main())
