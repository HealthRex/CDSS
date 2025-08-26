import os
from dotenv import load_dotenv

load_dotenv()

LLM_O3_MINI_API_URL = os.getenv("LLM_O3_MINI_API_URL")
LLM_API_KEY = os.getenv("HEALTHREX_API_KEY")
