# SAGE Router – Clinical Question Routing API

This repository contains a small FastAPI service that routes primary-care eConsult questions to:

- The **top 3 specialties**, and  
- The **top 5 template conditions** (constrained to the top specialty),

using a **cached set of eConsult templates** and a **SecureGPT** deployment (Stanford APIM OpenAI endpoint).

It is designed for deployment by an engineer (e.g., on a GCP VM, Cloud Run, etc.) as a lightweight routing microservice for the SAGE project.

---

## 1. Repository Layout

Root directory (what you should see in this repo):

```text
.
├── api/
│   └── main.py
├── data/
│   ├── templates/
│   │   └── templates_combined.json
│   └── env.example.txt
├── environment.yml
├── README.md
├── results/
│   ├── cache_content.txt
│   ├── cache_metadata.json
│   └── specialty_condition_mapping.json
├── scripts/
│   ├── 01_load_templates.py
│   ├── 02_gpt_few_shot_predict.py
│   ├── 03_few_shot_evaluate.py
│   ├── debug_path.py
│   ├── fix_templates_full.py
│   └── upload_kv_cache.py
├── setup/
│   └── build_cache.py
└── utils/
    ├── __init__.py
    └── config.py
What each piece does
api/
api/main.py
The FastAPI app.
Defines the HTML UI at /
Defines the form endpoint /route
Defines the JSON API endpoint /api/route
Defines a healthcheck at /health
On startup, loads the cached template content and mappings from results/.
This is the main file used for deployment via uvicorn api.main:app.
data/
data/templates/templates_combined.json
Combined template JSON (all specialties & conditions). Used by the offline cache-building scripts.
data/env.example.txt
Example .env content (for reference) — safe to keep in the repo.
This directory is mainly useful if you want to rebuild the cache or reproduce the template-processing pipeline.
results/
Precomputed cache artifacts used by the running service:
results/specialty_condition_mapping.json
Mapping: specialty -> list of condition names.
Loaded into memory at startup and used to construct the system prompt.
results/cache_content.txt
Flattened text blob containing:
=== TEMPLATES === section with all templates (for grounding)
=== SPECIALTY MAPPINGS === section (for reference)
results/cache_metadata.json
Metadata (content hash, template counts, model info, etc.).
These three files are required for the router to start and route questions.
scripts/
Offline / experimental scripts. Not needed for day-to-day API serving, but included for reproducibility:
01_load_templates.py – loads raw templates and normalizes them.
02_gpt_few_shot_predict.py – runs few-shot routing predictions over test questions.
03_few_shot_evaluate.py – evaluates router performance offline.
debug_path.py – tiny helper to debug Python import paths.
fix_templates_full.py – fixes minor template formatting issues.
upload_kv_cache.py – uploads cache_content.txt into OpenAI's KV cache API and saves the KV cache ID.
These are optional. Keep them in the repo, but you don't need to run them to deploy the service.
setup/
setup/build_cache.py
Utility to rebuild all cache files in results/ from the templates in data/templates/.
Only needed when templates change or new specialties/templates are added.
utils/
utils/config.py
Central configuration helper. Reads environment variables (from .env if present) and exposes:
securegpt_url
securegpt_api_key
llm_model (e.g., gpt-5.1-mini)
path helpers like results_dir, data_dir, etc.
utils/init.py
Empty file that turns utils into a Python package so from utils.config import Config works.
This module is required by both api/main.py and the scripts.
What is essential for deployment?
For a deployment engineer, the minimal set is:
api/main.py
data/templates/ (and optionally data/templates_combined.json)
results/ (all three cache files)
utils/config.py and utils/__init__.py
environment.yml
.env (created locally from the example; not committed)
The rest (scripts/, setup/) are primarily for rebuilding the cache or reproducing experiments.
2. How It Works (High Level)
On startup, api/main.py:
Adds the project root to sys.path and imports Config from utils.config.
Loads:
results/specialty_condition_mapping.json → specialty_conditions (dict)
results/cache_content.txt → extracts the === TEMPLATES === section into templates_text
results/cache_metadata.json → cache_metadata (hash, counts, model)
When a question is submitted (via HTML form or /api/route):
It builds a system prompt that describes:
The routing task
The available specialties and their conditions
Constraints (e.g., all 5 conditions must come from the top specialty)
It builds a user prompt with:
The clinical question
The cached template text (templates_text) for grounding
It calls the SecureGPT endpoint (SECUREGPT_URL) with:
{
  "model": "<SAGE_ROUTER_MODEL>",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ]
}
It expects the model to return JSON of the form:
{
  "specialties": ["spec1", "spec2", "spec3"],
  "conditions": ["cond1", "cond2", "cond3", "cond4", "cond5"]
}
It parses that JSON, trims/pads the lists, and returns:
HTML (/route) for the UI, or
JSON (/api/route) for programmatic use.
The home page (/) is a simple HTML UI for manual testing. /health provides a basic health check.
3. Configuration
Configuration is centralized in utils/config.py, which reads environment variables and provides them to the rest of the code.
.env (local, not committed)
Create a .env file in the project root based on the example content:
# Example (do not commit)
SECUREGPT_URL=https://apim.stanfordhealthcare.org/openai-eastus2/deployments/<deployment>/chat/completions?api-version=2024-12-01-preview
SECUREGPT_API_KEY=your-key-here
SAGE_ROUTER_MODEL=gpt-5.1-mini
Keep .env out of version control (use .gitignore).
The repo may include data/env.example.txt or .env.example as documentation, but never real keys.
Important note for deployment (SecureGPT / networking)
The service assumes that the host machine can reach the SecureGPT APIM endpoint. Firewall rules, proxies, service accounts, and APIM access control are not handled in this repo.
For details on:
Which SECUREGPT_URL to use in each environment, and
How to correctly route SecureGPT traffic from a GCP VM,
please coordinate with Vishnu, who already knows how the SecureGPT API is configured in our infrastructure.
4. Environment Setup
This project is intended to run inside a Conda environment (or any Python 3.11+ virtual environment with equivalent packages).
4.1. Create and activate the Conda environment
From the project root:
conda env create -f environment.yml
conda activate sage-router    # or whatever name is in environment.yml
If the environment name inside environment.yml is different, use that name instead of sage-router.
4.2. Install extras (if needed)
environment.yml should already include all required libraries, but if needed:
pip install fastapi "uvicorn[standard]" python-dotenv requests openai
5. Running the Service Locally
Prerequisites:
Repo cloned.
Conda environment created and activated.
.env created with real SECUREGPT_URL and SECUREGPT_API_KEY.
results/ exists with the three cache files.
Then run:
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
You should see logs like:
DEBUG: project root = /path/to/sage-router
🔄 Loading routing cache...
✅ Loaded 23 specialties
✅ Loaded templates cache
✅ Cache meta
