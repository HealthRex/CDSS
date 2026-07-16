# Vertex AI on Stanford Nero — full reference cookbook

Project-agnostic working reference for calling LLMs on Stanford's PHI-safe
Vertex AI projects. Copy-paste patterns for each model family, BAA
constraints called out, production patterns from real runs, and the
gotchas you'd otherwise lose time on.

**Scope:** any Stanford project under the Nero PHI-safe environment
(`som-nero-*` billing). Replace `<YOUR_PROJECT_ID>` with your project's ID
throughout.

**Last updated:** 2026-06-07. BAA status changes; recheck before using a
new model on PHI data.

---

## Table of contents

1. [What lives where](#1-what-lives-where) — quick reference table
2. [PHI / BAA constraints](#2-phi--baa-constraints) — **READ FIRST for PHI projects**
3. [One-time setup](#3-one-time-setup) — auth, env, packages
4. [Smoke test all models](#4-smoke-test-all-models) — copy-paste verification script
5. [Claude (Anthropic)](#5-claude-anthropic) — Opus / Sonnet / Haiku
6. [Gemini (Google)](#6-gemini-google) — Pro / Flash
7. [Llama (Meta)](#7-llama-meta) — Scout / Maverick
8. [Embeddings](#8-embeddings) — text-embedding-005
9. [Structured JSON output](#9-structured-json-output) — schemas, fence stripping, thinking budgets
10. [Production patterns](#10-production-patterns) — threading, checkpointing, retries
11. [Cost reference + how to budget](#11-cost-reference--how-to-budget)
12. [Reading the bill](#12-reading-the-bill) — what each line means
13. [Troubleshooting](#13-troubleshooting) — common errors decoded
14. [Templates](#14-templates) — full scripts for common patterns

---

## 1. What lives where

The single most useful table. Every cell has bitten somebody.

| Family | Model ID (slug) | Region | SDK | BAA-covered for PHI? |
|---|---|---|---|---|
| Anthropic | `claude-opus-4-7@default` | `global` | `anthropic.AnthropicVertex` | ✅ yes (stable) |
| Anthropic | `claude-sonnet-4-6@default` | `us-east5` | `anthropic.AnthropicVertex` | ✅ yes (stable) |
| Anthropic | `claude-haiku-4-5@20251001` | `us-east5` | `anthropic.AnthropicVertex` | ✅ yes (stable, dated slug required) |
| Google | `gemini-2.5-pro` | `us-central1` | `google.genai` | ✅ yes (stable, GA) |
| Google | `gemini-2.5-flash` | `us-central1` | `google.genai` | ✅ yes (stable, GA) |
| Google | `gemini-3-pro-preview` | `global` | `google.genai` | ❌ **PREVIEW — not BAA-covered** |
| Google | `gemini-3.5-flash` | `global` | `google.genai` | ✅ yes (BAA-confirmed by SRCC 2026-06-08) |
| Google | `text-embedding-005` | `us-central1` | `google.genai` | ✅ yes (stable) |
| Meta | `meta/llama-4-maverick-17b-128e-instruct-maas` | `us-east5` | OpenAI-compatible | ✅ yes (stable, Vertex MaaS) |
| Meta | `meta/llama-4-scout-17b-16e-instruct-maas` | `us-east5` | OpenAI-compatible | ✅ yes |

Pricing in [§11](#11-cost-reference--how-to-budget). Quotas in [§13 / Troubleshooting](#13-troubleshooting).

> **The 3 things this table hides:**
> 1. **Different SDKs per family.** Calling Claude via the genai SDK 404s with a confusing "publisher google" error. The SDK has to match the family.
> 2. **Region matters.** Calling Claude Opus on `us-east5` 404s — it's only on `global` and `us` multi-region. Calling Gemini Flash on `global` works; on `us-central1` also works. Defaults in this doc are what's been tested.
> 3. **OpenAI doesn't have a Stanford BAA.** OpenAI models (GPT-5/4o/etc.) cannot be used on PHI under Stanford's agreements, even via Vertex.

---

## 2. PHI / BAA constraints

**The rule that matters most for PHI/EHR work:**

> Stanford's BAA with GCP covers **GA / stable models** only. **Preview models are explicitly excluded.** Patient data going through a preview model = BAA violation = IRB issue.

### Why this trips people up

Vertex's Model Garden shows preview models alongside GA ones with no obvious distinction. The UI happily lets you call them. The SDK doesn't refuse. The model returns reasonable answers. **Only the BAA paperwork says "no."**

Real examples we've hit:
- **Gemini 3 Pro Preview** — released 2025-11-18, shows in Model Garden, accessible via the SDK, looks production-ready. NOT BAA-covered (preview stage).
- **Gemini 3.5 Flash** — accessible in `global` region. **BAA-covered (GA), confirmed by SRCC 2026-06-08.** The "no Preview label in Model Garden = GA" convention held up; SRCC confirmed.

### How to check before using a model on PHI

1. **Vertex Model Garden card** — look for "GA" or "Preview" tag, and the "Release stage" field
2. **Vertex AI docs** — search the model name; the official Google docs page says "Preview" or "GA"
3. **When in doubt, ask SRCC** (`srcc-support@stanford.edu`) — they'll confirm BAA status

### What stable looks like (as of 2026-06)

| ✅ GA / BAA-covered for PHI | ❌ Preview / NOT BAA-covered |
|---|---|
| Claude Opus 4.7, Sonnet 4.6, Haiku 4.5 | Anything with `-preview` in the slug |
| Gemini 2.5 Pro, 2.5 Flash | Gemini 3 Pro Preview, 3.1 Pro Preview |
| text-embedding-005 | Gemini 3.5 Flash (verify) |
| Llama 4 Maverick, Scout (Vertex MaaS) | Most Google "Image"/"Video" preview models |

**No OpenAI BAA at Stanford as of 2026-06.** Don't send PHI to OpenAI, period.

### What if you want to use a preview model on PHI?

You don't. Use a stable model now and re-run on the preview model once it goes GA. The cost of "we tested with model X" → "wait, that was preview" is far higher than running on a slightly older stable model.

---

## 3. One-time setup

### gcloud CLI

```bash
# Skip if already installed
brew install --cask google-cloud-sdk
gcloud --version
```

### Authentication — Application Default Credentials (ADC)

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project <YOUR_PROJECT_ID>
gcloud config set project <YOUR_PROJECT_ID>
```

This writes a refresh token to `~/.config/gcloud/application_default_credentials.json` that all the Python SDKs auto-discover. The standard ADC flow — works for `google.genai`, `anthropic.AnthropicVertex`, `google.cloud.bigquery`, etc.

### VPN

Stanford full-traffic VPN must be active before any call. PHI-safe projects have VPC Service Controls enabled — without VPN you'll get cryptic 403s.

### Python env

Python 3.10+ recommended (3.9 works but is past end-of-life; you'll get FutureWarnings).

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade \
    google-cloud-aiplatform \
    google-cloud-bigquery \
    google-genai \
    google-auth \
    "anthropic[vertex]" \
    openai \
    pandas pyarrow
```

`openai` is for the Llama-on-Vertex endpoint (Vertex exposes Llama via an OpenAI-compatible API).

### Verify access — smoke test (§4)

Run the smoke test before doing anything else. If a model errors, fix that before writing pipeline code.

---

## 4. Smoke test all models

Save as `verify_vertex_access.py`. One file, every family, calls each model once, reports OK/FAIL with a snippet.

```python
"""Smoke-test every Vertex AI model. Run after gcloud auth + VPN."""
import google.auth
import google.auth.transport.requests
from anthropic import AnthropicVertex
from openai import OpenAI
from google import genai
from google.genai import types

PROJECT_ID = "<YOUR_PROJECT_ID>"
PROMPT = "In one sentence, what is hypertension?"


def test_claude(model, region):
    client = AnthropicVertex(project_id=PROJECT_ID, region=region)
    msg = client.messages.create(
        model=model,
        max_tokens=200,
        messages=[{"role": "user", "content": PROMPT}],
    )
    return msg.content[0].text.strip()


def test_llama(model):
    creds, _ = google.auth.default()
    creds.refresh(google.auth.transport.requests.Request())
    client = OpenAI(
        base_url=(
            f"https://us-east5-aiplatform.googleapis.com/v1beta1/"
            f"projects/{PROJECT_ID}/locations/us-east5/endpoints/openapi"
        ),
        api_key=creds.token,
    )
    resp = client.chat.completions.create(
        model=model,
        max_tokens=200,
        messages=[{"role": "user", "content": PROMPT}],
    )
    return resp.choices[0].message.content.strip()


def test_gemini(model, location="us-central1"):
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=location)
    resp = client.models.generate_content(
        model=model,
        contents=PROMPT,
        config=types.GenerateContentConfig(max_output_tokens=200),
    )
    return (resp.text or "").strip()


if __name__ == "__main__":
    tests = [
        ("Claude Opus 4.7",  lambda: test_claude("claude-opus-4-7@default",   "global")),
        ("Claude Sonnet 4.6",lambda: test_claude("claude-sonnet-4-6@default", "us-east5")),
        ("Claude Haiku 4.5", lambda: test_claude("claude-haiku-4-5@20251001", "us-east5")),
        ("Llama 4 Maverick", lambda: test_llama("meta/llama-4-maverick-17b-128e-instruct-maas")),
        ("Llama 4 Scout",    lambda: test_llama("meta/llama-4-scout-17b-16e-instruct-maas")),
        ("Gemini 2.5 Pro",   lambda: test_gemini("gemini-2.5-pro")),
        ("Gemini 2.5 Flash", lambda: test_gemini("gemini-2.5-flash")),
    ]
    for name, fn in tests:
        try:
            print(f"[OK]    {name:22s}: {fn()[:80]}")
        except Exception as e:
            print(f"[FAIL]  {name:22s}: {type(e).__name__}: {e}")
```

Expected: 7/7 OK on a properly enabled project. If any FAIL, see [§13 Troubleshooting](#13-troubleshooting).

---

## 5. Claude (Anthropic)

### Minimal call

```python
from anthropic import AnthropicVertex

client = AnthropicVertex(
    project_id="<YOUR_PROJECT_ID>",
    region="global",   # Opus is global; Sonnet & Haiku are us-east5
)

msg = client.messages.create(
    model="claude-opus-4-7@default",
    max_tokens=2000,
    system="You are a clinical reasoning assistant.",
    messages=[{"role": "user", "content": "What's the differential for chest pain in a 55F?"}],
    # NB: temperature is deprecated on Opus 4.7+ — calling with temperature=... returns HTTP 400
)
print(msg.content[0].text)
```

### Quirks to know

- **`temperature` is deprecated on Opus 4.7+.** Don't pass it. Use the model's default (effectively low temperature for clinical tasks).
- **Haiku uses a dated slug.** `claude-haiku-4-5@default` is not published — pin to `@20251001` (or the date Stanford has).
- **Opus is on `global` only.** Sonnet and Haiku are on `us-east5`. Mixing these wrong returns 404.
- **No `response_schema` parameter.** Claude doesn't have native structured-output forcing on Vertex. Use prompt-driven JSON + parse with fence stripping (see [§9](#9-structured-json-output)).
- **Pricing tiers differ by 5x.** Opus ≈ 5× Sonnet ≈ 5× Haiku. For high-volume work, Haiku/Sonnet is almost always the right call.

### When to use each

| Task | Recommended |
|---|---|
| Top-tier reasoning, hard clinical judgment | **Opus 4.7** |
| Standard production classification / labeling | **Sonnet 4.6** |
| Bulk LLM-as-judge with simple rubrics | **Haiku 4.5** |

---

## 6. Gemini (Google)

### Minimal call

```python
from google import genai
from google.genai import types

client = genai.Client(
    vertexai=True,
    project="<YOUR_PROJECT_ID>",
    location="us-central1",   # 2.5 Pro/Flash live here
)

resp = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="What's the differential for chest pain in a 55F?",
    config=types.GenerateContentConfig(
        system_instruction="You are a clinical reasoning assistant.",
        max_output_tokens=2000,
        temperature=0.0,
        # IMPORTANT: see thinking_budget below
    ),
)
print(resp.text)
```

### Quirks to know

- **Gemini 2.5 Pro uses thinking by default.** It silently consumes from your `max_output_tokens` budget for reasoning before producing visible output. Symptom: `resp.text` comes back empty. Fix:
  ```python
  config=types.GenerateContentConfig(
      ...,
      thinking_config=types.ThinkingConfig(thinking_budget=0),  # disable thinking
  )
  ```
- **`thought_signature` warning is harmless.** Gemini 3.5 Flash (and 3.x Pro variants) emit a `thought_signature` content-part on every response, even with `thinking_budget=0`. The SDK prints:
  > `Warning: there are non-text parts in the response: ['thought_signature'], returning concatenated text result from text parts.`
  Your `resp.text` and `json.loads(resp.text)` still work correctly — just ignore the warning. If it's noisy, suppress with `warnings.filterwarnings("ignore", message=".*thought_signature.*")`.
- **`response_mime_type="application/json"` works** and is preferred over prompt-driven JSON for Gemini.
- **`response_schema` accepts a plain JSON-schema dict.** Validates output.
- **`location="global"` for newer previews, `us-central1` for stable Pro/Flash.** Don't assume — check the Model Garden card.

### Structured JSON pattern (use this every time you want a labeled output)

```python
SCHEMA = {
    "type": "object",
    "properties": {
        "category": {"type": "string", "enum": ["medication", "scheduling", "lab", "other"]},
        "confidence": {"type": "number"},
        "rationale": {"type": "string"},
    },
    "required": ["category", "confidence", "rationale"],
}

resp = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=user_message,
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        response_mime_type="application/json",
        response_schema=SCHEMA,
        max_output_tokens=1024,
        thinking_config=types.ThinkingConfig(thinking_budget=0),  # Flash needs this too
    ),
)
labels = json.loads(resp.text)
```

### When to use each

| Task | Recommended |
|---|---|
| Heavy reasoning, long context | **Gemini 2.5 Pro** (with `thinking_budget=N>0`) |
| High-volume classification / labeling | **Gemini 2.5 Flash** (`thinking_budget=0`, ~10× cheaper than Pro) |
| Document chunking / summarization at scale | **Flash** |

---

## 7. Llama (Meta)

Vertex exposes Llama via an OpenAI-compatible endpoint. The auth is GCP, but the SDK and API shape are OpenAI's.

### Minimal call

```python
import google.auth
import google.auth.transport.requests
from openai import OpenAI

PROJECT_ID = "<YOUR_PROJECT_ID>"
LOCATION = "us-east5"

creds, _ = google.auth.default()
creds.refresh(google.auth.transport.requests.Request())

client = OpenAI(
    base_url=(
        f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/"
        f"projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/openapi"
    ),
    api_key=creds.token,
)

resp = client.chat.completions.create(
    model="meta/llama-4-maverick-17b-128e-instruct-maas",
    max_tokens=2000,
    messages=[
        {"role": "system", "content": "You are a clinical assistant."},
        {"role": "user", "content": "What's the differential for chest pain in a 55F?"},
    ],
)
print(resp.choices[0].message.content)
```

### Quirks to know

- **The credential expires.** `creds.refresh(...)` is required before every burst of calls. For long runs, refresh once per ~50 minutes.
- **Vertex MaaS is BAA-covered** — yes, Llama on Vertex MaaS counts as Vertex AI, covered.
- **No native structured-output forcing.** Use prompt-driven JSON + parse.
- **Tokenization differs from Claude/Gemini.** Per-prompt cost estimates need Llama-specific tokenization (use `tiktoken` with a Llama tokenizer or just budget loosely).

### When to use each

| Task | Recommended |
|---|---|
| Open-weights baseline for benchmarks | **Llama 4 Maverick** (the bigger, ~128B-equivalent) |
| Cost-sensitive eval at scale | **Llama 4 Scout** (~17B-effective) |

---

## 8. Embeddings

### text-embedding-005

```python
from google import genai
from google.genai import types

client = genai.Client(
    vertexai=True,
    project="<YOUR_PROJECT_ID>",
    location="us-central1",
)

resp = client.models.embed_content(
    model="text-embedding-005",
    contents=["First text", "Second text", "Third text"],
    config=types.EmbedContentConfig(task_type="CLUSTERING"),
)
vectors = [e.values for e in resp.embeddings]   # each is 768-dim
```

### Quirks to know

- **`task_type` matters.** The model produces *different* vectors for different task types. Pick once at the start of the project and never mix.
  - `CLUSTERING` — for UMAP/HDBSCAN, similarity grouping
  - `RETRIEVAL_DOCUMENT` / `RETRIEVAL_QUERY` — for RAG (different per side)
  - `SEMANTIC_SIMILARITY` — for pairwise comparison
  - `CLASSIFICATION` — for downstream classifier features
- **Batch up to ~100 texts per request.** Beyond ~250 you hit limits. The model handles batches in parallel internally.
- **Output is always 768-dim.** Store as `ARRAY<FLOAT64>` in BigQuery or as `list[float]` in Parquet.
- **Cost is negligible** (~$0.025 per million tokens). Embedding 50K patient questions ≈ $3.

---

## 9. Structured JSON output

The most common production pattern: get back a typed object, not free-form prose.

### Pattern A — Gemini with `response_schema` (preferred when you have the choice)

Native validation; if the model can't match the schema, you get a 400 instead of mystery garbage. See [§6](#6-gemini-google).

### Pattern B — Claude / Llama with prompt-driven JSON + fence stripping

These don't have native schema enforcement. You instruct the model to emit JSON and parse it. The catch: models sometimes wrap output in ` ```json ... ``` ` fences even when told not to.

```python
import json
import re

_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$")

def parse_json_response(raw: str) -> dict:
    """Strip markdown fences and parse JSON. Returns dict or raises."""
    cleaned = _FENCE_RE.sub("", raw).strip()
    return json.loads(cleaned)
```

### Pattern C — JSON with thinking budget (Gemini 2.5 Pro/Flash)

If `resp.text` comes back empty and you're requesting JSON, the model burned its `max_output_tokens` on thinking. Two fixes:

```python
# Option 1: disable thinking entirely (good for classification)
thinking_config=types.ThinkingConfig(thinking_budget=0)

# Option 2: bump max_tokens to account for thinking + JSON
max_output_tokens=4000   # 2K for thinking, 2K for the JSON
```

### Pattern D — Defensive parsing wrapper

For long production runs, always log the raw text on first parse failure so you can debug what shape the model actually emitted:

```python
_PRINTED_RAW = False

def safe_parse(raw: str) -> dict:
    global _PRINTED_RAW
    cleaned = _FENCE_RE.sub("", raw).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        if not _PRINTED_RAW:
            _PRINTED_RAW = True
            print(f"--- RAW (first parse failure) ---\n{raw[:1500]!r}\n--- END ---")
        raise
```

---

## 10. Production patterns

Patterns that survived a real ~50K-row labeling run on Opus. Use these any time you're labeling more than a few hundred rows.

### Threaded concurrency

Vertex doesn't expose a native batch API for Claude. For Gemini, batch exists but is a 24-hour async path. For sync-with-decent-throughput, use Python threads with a bounded `ThreadPoolExecutor`:

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def process(row):
    try:
        return ("ok", call_model(row["question"]))
    except Exception as e:
        return ("err", f"{type(e).__name__}: {e}")

with ThreadPoolExecutor(max_workers=8) as ex:
    futures = [ex.submit(process, row) for row in rows]
    for fut in as_completed(futures):
        status, result = fut.result()
        ...
```

**Empirical concurrency limits** (Stanford Nero project, June 2026):
- Claude Opus 4.7: **8 concurrent works well**, ~4.5 req/sec sustained (rate-limit-bounded)
- Claude Sonnet 4.6: 8–16 concurrent, faster
- Gemini 2.5 Flash: 8–16, very fast (~8 req/sec)
- Gemini 3.5 Flash (`global`): **10 concurrent → 5.4 req/sec sustained** on a 10-call structured-JSON smoke test (verified 2026-06-08)
- Llama Vertex MaaS: 8, modest

Higher concurrency hits `RateLimitError` → adds wait time, doesn't help throughput. Start at 8 and tune.

### Retry with exponential backoff

```python
from anthropic import RateLimitError, APIError
import time, random

def call_with_retry(client, *args, max_retries=4, **kwargs):
    for attempt in range(max_retries + 1):
        try:
            return client.messages.create(*args, **kwargs)
        except (RateLimitError, APIError) as e:
            if attempt == max_retries:
                raise
            # 2, 4, 8, 16 seconds + jitter
            time.sleep((2 ** (attempt + 1)) + random.uniform(0, 1))
```

For Gemini, retry on `google.api_core.exceptions.ResourceExhausted` and `google.genai.errors.ClientError`.

### Checkpoint / resume

A multi-hour run **will** hit a network blip, VPN drop, or laptop sleep. Plan for it. Pattern: write each result to a local JSONL as it completes, on resume read the file and skip already-done IDs.

```python
import json, threading, pathlib

CHECKPOINT = pathlib.Path("out/labels.jsonl")
_WRITE_LOCK = threading.Lock()

def append_jsonl(row):
    """Thread-safe append. JSON lines < PIPE_BUF are atomic on POSIX."""
    line = json.dumps(row, default=str) + "\n"
    with _WRITE_LOCK:
        with open(CHECKPOINT, "a") as f:
            f.write(line)

def load_done_ids() -> set:
    if not CHECKPOINT.exists():
        return set()
    ids = set()
    with open(CHECKPOINT) as f:
        for line in f:
            try:
                ids.add(int(json.loads(line)["id"]))
            except (json.JSONDecodeError, KeyError):
                pass  # tolerate one half-written line on crash
    return ids

# At start: pending = [row for row in all_rows if row["id"] not in load_done_ids()]
# At each successful label: append_jsonl({"id": row["id"], **labels})
# Re-run the same command after any crash; it picks up where it left off.
```

After labeling completes, bulk-load the JSONL into BigQuery (or Parquet) with an explicit schema:

```python
from google.cloud import bigquery

bq = bigquery.Client(project="<YOUR_PROJECT_ID>")
schema = [
    bigquery.SchemaField("id", "INT64", mode="REQUIRED"),
    bigquery.SchemaField("score", "INT64"),
    bigquery.SchemaField("justification", "STRING"),
]
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    schema=schema,
    write_disposition="WRITE_TRUNCATE",
    ignore_unknown_values=True,
)
with open("out/labels.jsonl", "rb") as f:
    bq.load_table_from_file(f, "<YOUR_PROJECT_ID>.<DATASET>.labels", job_config=job_config).result()
```

### Run from a stable terminal

For runs > 30 minutes:

```bash
screen -S mylongrun
python run.py
# Ctrl+A then D to detach
# screen -r mylongrun to reattach later
```

Closing the terminal in `screen` doesn't kill the process. `tmux` works the same way.

---

## 11. Cost reference + how to budget

Pricing on Vertex with Stanford's ~15% discount, as of 2026-06. Recheck on the Vertex pricing page for current rates.

| Model | Input ($/M tokens) | Output ($/M tokens) | Labeling 50K rows (≈) |
|---|---|---|---|
| **Claude Opus 4.7** | $12.75 | $63.75 | **~$600** ¹ |
| **Claude Sonnet 4.6** | $2.55 | $12.75 | **~$120** |
| **Claude Haiku 4.5** | $0.68 | $3.40 | **~$30** |
| **Gemini 2.5 Pro** | $1.06 | $4.25 | ~$50 |
| **Gemini 2.5 Flash** | $0.0638 | $0.255 | **~$3** |
| **Llama 4 Maverick** | ~$0.20 | ~$0.60 | ~$10 |
| **text-embedding-005** | $0.021 | n/a | ~$3 |

¹ Empirical from a real ~50K Opus run with ~1.5K input + ~150 output tokens per row.

### Pre-flight budget check

Before kicking off a long run, do this math out loud:

```
cost ≈ N_rows × (input_tokens × input_price + output_tokens × output_price) × 0.85
```

Where `0.85` is the Stanford discount. Round up generously — token counts vary.

### Set a budget alert (do this once per billing account)

```
GCP Console → Billing → Budgets & alerts → Create budget
  Scope:     <YOUR_PROJECT_ID>
  Amount:    e.g. $500/month
  Alerts:    50% / 90% / 100%
```

This doesn't cap spending — it emails you when thresholds hit. The cap behavior is via separate quotas (more aggressive setup).

### Pre-confirm large runs

**Stanford norm:** for any single planned spend > $1,000 in a Healthrex/Nero project, confirm with the PI (e.g., Jon Chen) by email *before* kicking off. The estimate matters even if the run comes in cheaper.

---

## 12. Reading the bill

`som-nero-*` projects bill into the **`Nero-General`** billing account (rolls up many researchers' projects).

### Line items you'll see

| Bill line | What it includes |
|---|---|
| **Vertex AI** | Google-native: Gemini Pro / Flash / text-embedding-005, Vertex platform fees, embeddings, anything via `google.genai` |
| **Claude Opus 4.7** | Anthropic Opus only — separate SKU even though accessed through Vertex |
| **Claude Sonnet 4.6** | Anthropic Sonnet only — separate SKU |
| **Claude Haiku 4.5** | Anthropic Haiku only — separate SKU |
| **Cloud Storage / Networking / BigQuery** | Storage and query infrastructure |
| **Compute Engine** | VMs (typically not yours unless you spun one up) |

**Anthropic Claude lines are NOT included in the "Vertex AI" total.** They appear as their own lines. So when accounting for your spend, sum the Claude lines plus your share of "Vertex AI."

### Why your number might not match what you ran

The billing account aggregates **multiple users and multiple projects.** A $3K "Vertex AI" line could be 1 person's heavy Gemini run, or 5 people's combined work. To disambiguate:

- Filter Billing Reports by `Project: <YOUR_PROJECT_ID>` to scope to just your project
- Filter by `Time Range` to a single day to see who was running what when
- Cross-reference with collaborator timelines ("Ivan ran his judge on June 6")

### Daily granularity

Billing Reports → switch the chart to **daily** instead of monthly. Spikes correlate with individual jobs and make it easy to see "this $1.5K spike was the day I ran the filter pass."

### Lag

GCP billing has a **24–48 hour lag.** Today's calls show up tomorrow afternoon.

---

## 13. Troubleshooting

### `404 NOT_FOUND - Publisher Model ... was not found`

The cryptic-but-common one. Four sub-causes:

| Error fragment | Likely cause | Fix |
|---|---|---|
| `publishers/google/models/claude-...` | Wrong SDK (genai instead of AnthropicVertex) | Use `AnthropicVertex` for any `claude-*` model |
| `publishers/anthropic/models/claude-...-NOT_THIS_SLUG` | Wrong slug — `@default` not published for some models | Try the dated version, e.g. `claude-haiku-4-5@20251001` |
| `your project does not have access to it` | Project-level enablement gate | Contact `srcc-support@stanford.edu` or the project PI |
| `gemini-3-pro-preview` | Preview model, not enabled for project | Per [§2](#2-phi--baa-constraints), don't use preview on PHI; use 2.5 Pro instead |

### `403 PERMISSION_DENIED` or `VPC Service Controls`

VPN issue. Connect Stanford full-traffic VPN.

### `temperature is deprecated for this model`

Claude Opus 4.7+. Remove `temperature=...` from the call. Use the model's default.

### `Empty response.text` from Gemini

Thinking budget ate the output. Either:
- Disable thinking: `thinking_config=types.ThinkingConfig(thinking_budget=0)`
- Or bump `max_output_tokens` (4000+ for Pro)

### `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`

The model returned empty content. Causes:
- (Gemini) Thinking ate the budget — see above
- (Claude) Content moderation hit, model declined to respond — rare; skip the row
- (Any) Token limit cut before any output — increase `max_tokens`

### `RateLimitError` (Claude) / `ResourceExhausted` (Gemini)

You're past the per-minute quota. Reduce concurrency or add exponential backoff (see [§10](#10-production-patterns)).

### Sonnet returns nonsense for structured-output tasks

Known calibration issue we hit: Sonnet sometimes mis-classifies bool fields and emits values outside the documented 1–5 range on classification tasks where Opus is fine. **For high-stakes classification, use Opus.** For high-volume cost-sensitive judging, validate Sonnet on a calibration set before committing.

### Llama: `Unauthorized` after running for a while

Credentials expired. Refresh:
```python
creds.refresh(google.auth.transport.requests.Request())
```
Wrap your long-running loop to refresh every ~50 minutes.

---

## 14. Templates

Three copy-paste starting points. Adjust to your task.

### Template A — Smoke test on a small sample

For when you're calibrating a new prompt. Cost: pennies. Time: 1–5 min.

```python
"""Sanity-check a prompt on 25 rows before committing to a full run."""
from anthropic import AnthropicVertex
import json, re

PROJECT_ID = "<YOUR_PROJECT_ID>"
SYSTEM = "<YOUR_PROMPT>"

client = AnthropicVertex(project_id=PROJECT_ID, region="global")
rows = fetch_25_rows()  # however you do it — BQ query, parquet, etc.

_FENCE = re.compile(r"^\s*```(?:json)?\s*|\s*```\s*$")
for row in rows:
    msg = client.messages.create(
        model="claude-opus-4-7@default",
        max_tokens=2000,
        system=SYSTEM,
        messages=[{"role": "user", "content": row["text"]}],
    )
    raw = msg.content[0].text
    try:
        labels = json.loads(_FENCE.sub("", raw).strip())
    except json.JSONDecodeError:
        print(f"PARSE FAIL on {row['id']}: {raw[:200]!r}")
        continue
    print(f"{row['id']}: {labels}")
```

### Template B — Production run with checkpointing

The full pattern from [§10](#10-production-patterns). Use any time you're labeling more than ~500 rows.

See `04_filter_at_scale.py` in the MyChatBench repo for the full implementation — it's the production-quality version of this pattern with retries, JSONL checkpoint, threaded concurrency, BQ upload, CLI flags for `--limit / --concurrency / --upload-only / --no-upload`.

### Template C — Embedding job

```python
"""Embed all rows in a BQ table, write back to BQ + a Parquet for sharing."""
from google import genai
from google.genai import types
from google.cloud import bigquery
import pandas as pd

PROJECT_ID = "<YOUR_PROJECT_ID>"
SOURCE_TABLE = "<YOUR_DATASET>.<YOUR_TABLE>"
TEXT_COLUMN = "text"
ID_COLUMN = "id"
TARGET_TABLE = "<YOUR_DATASET>.embeddings"

bq = bigquery.Client(project=PROJECT_ID)
emb = genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")

df = bq.query(f"SELECT {ID_COLUMN}, {TEXT_COLUMN} FROM `{SOURCE_TABLE}`").to_dataframe()

BATCH = 100
embeddings = []
for i in range(0, len(df), BATCH):
    batch_texts = df[TEXT_COLUMN].iloc[i:i+BATCH].tolist()
    resp = emb.models.embed_content(
        model="text-embedding-005",
        contents=batch_texts,
        config=types.EmbedContentConfig(task_type="CLUSTERING"),
    )
    embeddings.extend(e.values for e in resp.embeddings)
    if (i // BATCH) % 10 == 0:
        print(f"  {i+BATCH}/{len(df)}")

out = pd.DataFrame({
    ID_COLUMN: df[ID_COLUMN],
    "embedding": embeddings,
})

# To BQ
out.to_gbq(TARGET_TABLE, project_id=PROJECT_ID, if_exists="replace")

# To Parquet for sharing (e.g., via Box for collaborators without GCP access)
out.to_parquet("out/embeddings.parquet", index=False)
```

---

## Appendix: when to ask SRCC vs your PI

| Issue | Who to contact |
|---|---|
| New model access / enablement | `srcc-support@stanford.edu` |
| BAA / PHI compliance question | `srcc-support@stanford.edu` |
| Quota raise for a specific model | `srcc-support@stanford.edu` |
| Budget over the project's PI threshold | Your PI (e.g., Jon Chen for Healthrex) |
| Billing visibility / Billing Account Viewer role | Your PI |
| Project creation / new GCP project | Your PI + SRCC |

**Process tip:** SRCC tickets work best as fresh emails (not replies to old threads). Include: project ID, exact model ID, exact error message (paste verbatim), what you've tried.
