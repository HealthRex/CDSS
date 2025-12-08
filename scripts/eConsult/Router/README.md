# SAGE Router – Clinical Question Routing API

This repo contains a small FastAPI service that routes **primary-care eConsult questions** to:

- The **top specialties** (ranked by relevance), and  
- The **top template “conditions”** within the best specialty,

using a pre-computed cache of SAGE eConsult templates and an LLM call through **SecureGPT**.

The UI is an HTML form. The same logic is available via a JSON API (`/api/route`) for integration into other services.

---

## 1. Repository Layout

```text
sage-router/
├── api/
│   └── main.py                  # FastAPI app + HTML UI + routing logic
│
├── data/
│   ├── templates/               # Individual template JSONs (one per condition)
│   └── templates_combined.json  # Optional merged templates file
│
├── results/
│   ├── cache_content.txt        # Prompt-optimized concatenation of templates + mappings
│   ├── cache_metadata.json      # Metadata: hash, counts, timestamp, model, etc.
│   └── specialty_condition_mapping.json  # {specialty: [condition1, condition2, ...]}
│
├── scripts/
│   ├── 01_load_templates.py
│   ├── 02_gpt_few_shot_predict.py
│   ├── 03_few_shot_evalute.py
│   ├── debug_path.py
│   ├── fix_templates_full.py
│   └── upload_kv_cache.py       # (Optional) Upload cache_content.txt as KV cache to OpenAI
│
├── setup/
│   └── build_cache.py           # Builds results/cache_* files from data/templates/
│
├── utils/
│   ├── __init__.py              # Empty; marks utils as a package
│   └── config.py                # Central configuration (reads .env and paths)
│
├── environment.yml              # Conda environment
├── .env.example                 # Example env vars (no secrets)
└── README.md
