import os
from dotenv import load_dotenv

# Load .env next to your project root; adjust path if needed
load_dotenv()

def _require(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return v

LLM_API_KEY = _require("HEALTHREX_API_KEY")
LLM_O3_MINI_API_URL = _require("LLM_O3_MINI_API_URL")
LLM_GPT5_API_URL = _require("LLM_GPT5_API_URL")

__all__ = ["LLM_API_KEY", "LLM_O3_MINI_API_URL", "LLM_GPT5_API_URL"]
