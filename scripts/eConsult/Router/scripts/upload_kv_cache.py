import sys
from pathlib import Path

# ----------------------------------------------------
# ADD PROJECT ROOT TO PYTHON PATH (bulletproof version)
# ----------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

print("DEBUG: project root =", PROJECT_ROOT)
print("DEBUG: first sys.path entries =", sys.path[:5])

from utils.config import Config
from openai import OpenAI
import os
import re
import json

cfg = Config()
client = OpenAI(api_key=cfg.securegpt_api_key)

cache_file = cfg.results_dir / "cache_content.txt"

print(f"📄 Uploading KV cache from: {cache_file}")

with open(cache_file, "r") as f:
    cache_text = f.read()

response = client.cached_inputs.create(
    display_name="sage_templates_cache",
    input=[{"role": "system", "content": cache_text}]
)

print("✅ KV Cache created!")
print(f"📌 Cache ID: {response.id}")

# Save it for API
(cache_file.parent / "kv_cache_id.txt").write_text(response.id)
