"""
Configuration loader for the pipeline.
Loads all settings from environment variables via .env file.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ---------- API Key ----------
LLM_API_KEY = os.getenv("HEALTHREX_API_KEY")

# ---------- Model API URLs ----------
# OpenAI/Azure models
LLM_GPT5_API_URL = os.getenv("LLM_GPT5_API_URL")
LLM_O3_MINI_API_URL = os.getenv("LLM_O3_MINI_API_URL")

# Claude (AWS Bedrock)
LLM_CLAUDE_API_URL = os.getenv("LLM_CLAUDE_API_URL")

# Gemini models
LLM_GEMINI_25_PRO_API_URL = os.getenv("LLM_GEMINI_25_PRO_API_URL")
LLM_GEMINI_20_FLASH_API_URL = os.getenv("LLM_GEMINI_20_FLASH_API_URL")

# ---------- Default Settings ----------
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-5")
