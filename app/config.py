"""Configuration for the Rider Marketplace demo."""
import os

# Nebius Token Factory (Corey provides the key via NEBIUS_API_KEY env)
NEBIUS_API_KEY = os.environ.get("NEBIUS_API_KEY", "")
NEBIUS_BASE_URL = "https://api.tokenfactory.nebius.com/v1/"

# Model selection per track guidance (exact IDs, case-sensitive)
# Ultra for serious reasoning, Nano for fast everyday calls
NEMOTRON_REASONING = "nvidia/Nemotron-3-Ultra-550b-a55b"
NEMOTRON_FAST = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"
NEMOTRON_BALANCED = "nvidia/nemotron-3-super-120b-a12b"

# Rider
RIDER_BASE_URL = "https://agentrider.fly.dev"

# Tavily — default search for hired-agent research.
# Corey provides the key via TAVILY_API_KEY env (never committed).
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

# Demo mode: use Base Sepolia testnet for x402 payments
X402_NETWORK = "base-sepolia"
