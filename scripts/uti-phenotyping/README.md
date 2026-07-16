# Aim 3 — LLM-Based UTI Phenotyping

Use large language models to phenotype **urinary tract infection (UTI)** from free-text
clinical notes and benchmark them against physician adjudication. For each note the model
reproduces the two-reviewer protocol — it labels **10 UTI symptoms** and answers **4 clinical
assessments**, each with supporting evidence — and we score agreement against the adjudicated
ground truth.

> Clinical protocol: `Instructions - UTI Phenotyping.pdf`.
>
> **Taking this project over?** Start with **`HANDOFF.md`** — orientation, where the data lives
> (Stanford Medicine Box), and what file holds what result. This README is the how-to-run reference.

---

## TL;DR — clone and run

```bash
cd scripts/uti-phenotyping

# 1. Environment
python3 -m venv uti_phenotyping_env
source uti_phenotyping_env/bin/activate
pip install -r requirements.txt

# 2. Auth — your OWN Google Cloud credentials (ADC); no API keys, no .env needed
gcloud auth application-default login
gcloud auth application-default set-quota-project som-nero-phi-jonc101-secure
#   + Stanford full-traffic VPN must be ON (PHI projects use VPC Service Controls)

# 3. Confirm you can reach the models
./verify_vertex_access.py                         # expect Gemini/Claude/Llama [OK]

# 4. Put your adjudication sheet at the default path (see "Data setup")
#    data/input/adjudication.csv                  (or pass --input <path>)

# 5. Run the pipeline (every script is executable)
./build_curated_dataset.py                        # Stage 1: sheet -> BigQuery -> curated notes
./run_phenotyping.py --model gemini-2.5-pro       # Stage 2: notes -> LLM -> predictions
./evaluate.py --model gemini-2.5-pro              # Stage 3: predictions vs ground truth -> metrics
./symptom_feature_analysis.py --model gemini-2.5-pro   # optional: symptom studies + charts
```

The repo ships **no PHI** — notes are pulled live from BigQuery with your own credentials,
and every LLM call authenticates as *you* via ADC (see "No-PHI handoff").

---

## The LLM stack — Vertex AI (Stanford Nero, PHI-safe)

All models run on **Stanford's PHI-safe Vertex AI** in the Nero **secure** project
(`som-nero-phi-jonc101-secure`). Authentication is **per-user Application Default
Credentials (ADC)** — there are **no shared API keys**. (This replaces the retired
SecureGPT / `apim.stanfordhealthcare.org` gateway.)

`src/phi_safe_llm.py` exposes one interface — `PHISafeLLM(model_name).generate(prompt,
system_prompt=...)` — and dispatches to the right SDK per family:

| Model (code name) | Family / SDK | Region | Notes |
|---|---|---|---|
| `gemini-2.5-pro` *(default)* | `google.genai` | `us-central1` | keeps "thinking" on; large output budget |
| `gemini-2.5-flash` | `google.genai` | `us-central1` | `thinking_budget=0`; cheap/fast |
| `claude-opus-4-7` | `anthropic.AnthropicVertex` | `global` | no `temperature` (deprecated) |
| `claude-sonnet-4-6` | `anthropic.AnthropicVertex` | `us-east5` | |
| `claude-haiku-4-5` | `anthropic.AnthropicVertex` | `us-east5` | dated slug `@20251001` |
| `llama-4-maverick`, `llama-4-scout` | OpenAI-compatible | `us-east5` | ADC token, refreshed as needed |

Key constraints (from `vertex_ai_reference.md`):
- **GA / BAA-covered models only for PHI** — no `-preview` slugs.
- **No OpenAI/GPT** — there is no Stanford BAA for OpenAI, so GPT models cannot touch PHI
  (this is why the old `gpt-5` default was removed).
- **Gemini 2.5 Pro rejects `thinking_budget=0`** (HTTP 400); the client leaves it unset for Pro
  and disables thinking only for Flash.
- **Project override:** set `VERTEX_PROJECT` to change the Vertex project (default
  `som-nero-phi-jonc101-secure`, where the models are enabled).
- **Billing labels:** `user_id` / `experiment` (override via `VERTEX_LABEL_USER` /
  `VERTEX_LABEL_EXPERIMENT`, default `your_name` / `uti-phenotyping`) attach to **Gemini and
  Llama** calls; Vertex's Anthropic endpoint rejects a `labels` field, so **Claude** calls carry none.

Verify access anytime with **`./verify_vertex_access.py`** (sends a generic, non-PHI prompt to
each model and prints `[OK]`/`[FAIL]`).

---

## Prerequisites

- **Python 3.9+** (3.10+ recommended; 3.9 works with `FutureWarning`s).
- **Google Cloud access** to `som-nero-phi-jonc101-secure` (Vertex models) and
  `som-nero-phi-jonc101` (+ `-secure`) for BigQuery, via
  `gcloud auth application-default login`. Each user authenticates as themselves.
- **Stanford full-traffic VPN** on for every call (VPC Service Controls).
- No API keys. Optional env overrides: `VERTEX_PROJECT` (LLM project),
  `GOOGLE_CLOUD_PROJECT` (BigQuery billing project, default `som-nero-phi-jonc101`).

## Data setup (no PHI ships with the repo)

The repo is **code only**. `data/` is git-ignored and starts empty on a fresh clone.

- **Input:** place your adjudication sheet at **`data/input/adjudication.csv`** (the default),
  or point any script at another file with `--input <path>`. New sheets are expected to use the
  **same schema** (see "Input schema"). PHI input files are shared via Stanford Medicine Box
  (link in `HANDOFF.md`) — never through git.
- **Notes:** you don't obtain note text separately. A new sheet has only MRNs + timestamps;
  Stage 1 fetches the de-identified note text from BigQuery using **your** credentials.
- **Results / prior outputs:** everything under `data/output/` (curated dataset, per-model
  predictions, metrics, and the `analysis/` figures behind the deck) is shared via **Box**, not git.
  Copy the Box `data/output/` in to reuse prior results, or regenerate with the pipeline.
  See `HANDOFF.md` → "What file contains what result."

## No-PHI handoff

- The repo never stores PHI: `data/`, `logs/`, and `.env` are git-ignored; notebooks were
  removed in favor of scripts (they had embedded identifiers).
- Every LLM call and BigQuery query runs under the operator's **own** ADC — nothing is shared.
- The recipient regenerates data from their own access rather than receiving note data.

---

## Scripts (all executable — `./name.py --help` for options)

| Script | Stage | Reads | Writes |
|---|---|---|---|
| `verify_vertex_access.py` | check | Vertex (generic prompt) | prints `[OK]`/`[FAIL]` per model |
| `build_curated_dataset.py` | 1 — data mapping | adjudication sheet + **BigQuery** | `data/output/curated_dataset.csv`, `mapping_summary.csv` |
| `run_phenotyping.py` | 2 — inference | sheet + `curated_dataset.csv` + **Vertex** | `data/output/<prefix>_results.jsonl`, `<prefix>_summary.csv` |
| `evaluate.py` | 3 — evaluation | sheet + `<prefix>_summary.csv` | `data/output/<prefix>_metrics.json` (+ printed tables) |
| `symptom_feature_analysis.py` | analysis | sheet + `<prefix>_summary.csv` | `data/output/analysis/<model>/*.png` + `*.csv` |

Common flags: `--input <adjudication.csv>` (default `data/input/adjudication.csv`),
`--model <name>`, `--limit N` (Stage 2 quick test), `--no-resume` (Stage 2).

**Run on a new sheet (full regenerate — curate → predict → evaluate → analyze):** save it as
`data/input/adjudication.csv` and run the five TL;DR commands in order; each stage writes to
`data/output/` and the next reads it. For a sheet at a different path, pass `--input <path>` to
Stage 1, Stage 2, `evaluate.py`, and `symptom_feature_analysis.py`.

### Ground-truth behavior (for new, possibly-unlabeled inputs)

- **Stage 2 `run_phenotyping.py`** tolerates missing labels: with no `*_ground_truth` columns it
  prints a **warning**, still runs the LLM, and writes predictions (skips the accuracy line).
- **Stage 3 `evaluate.py` and `symptom_feature_analysis.py`** *require* ground truth — they
  **raise an error** if labels are absent.

---

## The phenotyping task

**10 symptoms** — each `Yes` / `Negation` (explicitly denied) / `No` (not mentioned), with a
verbatim supporting quote for Yes/Negation: `dysuria`, `subjective_fever`, `urinary_urgency`,
`urinary_frequency`, `suprapubic_pain_tenderness`, `flank_cva_pain_tenderness`,
`perineal_pain_painful_prostate_exam`, `urinary_incontinence`, `macroscopic_hematuria`,
`ability_to_perceive_symptoms`.

**4 assessments** — each `Yes` / `No` / `Unclear` with reasoning: `UTI?`,
`Is any infection present?`, `Presumed Infection Plausible?`, `Prophylactic Antibiotics Appropriate?`.

Model input is the note-text column **`deid_note_text`**; the headline label is
**`UTI?_ground_truth`** (see `src/uti_phenotyper.py`, `src/evaluation.py`).

## Input schema

The adjudication sheet is **~75 cases across ~50 urine cultures**, **75 columns**:

- **5 identifiers:** `patient_MRN`, `Urine Culture_Order Date & Time(taken time)`, `Note Type`,
  `Note Date/Time (Collins)`, `Note Date/Time (Lee)`.
- **14 fields × 5 columns each** (10 symptoms + 4 assessments): `<Field>_P1 (Collins)`,
  `<Field> Support_P1 (Collins)`, `<Field>_P2 (Lee)`, `<Field> Support_P2 (Lee)`,
  `<Field>_ground_truth`.

Phenotyping is **per note**, not per culture: a culture with multiple adjudicated notes yields
multiple predictions. (During Stage-1 mapping, note records within ±1 h of the same adjudicated
timestamp are concatenated with `---NOTE SEPARATOR---`; that is same-timestamp merging, not
per-culture pooling. See `config/table_mappings.yaml`.)

## Directory layout

```
uti-phenotyping/
├── README.md
├── vertex_ai_reference.md                 # Stanford Vertex AI cookbook (models, regions, BAA)
├── Instructions - UTI Phenotyping.pdf     # clinician reviewer protocol
├── presentation/  aim3_prelim_reseach_plan.pptx, aim3_progress_scaleup.pptx   # result + scale-up decks
├── requirements.txt
├── .env.example                           # optional env overrides (no keys needed)
├── verify_vertex_access.py                # smoke-test Vertex model access
├── build_curated_dataset.py               # Stage 1 (BigQuery)
├── run_phenotyping.py                     # Stage 2 (Vertex LLM inference)
├── evaluate.py                            # Stage 3 (metrics vs ground truth)
├── symptom_feature_analysis.py            # symptom studies + charts
├── config/  settings.py, table_mappings.yaml
├── src/     bigquery_client.py, data_mapper.py, phi_safe_llm.py, uti_phenotyper.py, evaluation.py
└── data/    (git-ignored)  input/  output/    <- your PHI lives here, never committed
```

## Known limitations / next steps

- Stage-1 time matching uses a fixed **−7 h UTC→Pacific** offset (no DST) and ±1 h / ±1 min
  tolerances (`src/data_mapper.py`); unmatched cases show as 0-match rows in `mapping_summary.csv`.
- If Gemini 2.5 Pro ever returns empty output, its "thinking" consumed the token budget — raise
  `max_output_tokens` (or bound `thinking_budget`) in `src/phi_safe_llm.py` (`_GEMINI`).
- Claude/Llama are enabled on `-secure`; confirm BAA/GA status in `vertex_ai_reference.md` before
  using a new model on PHI.
- Decide before scaling whether you want **per-note** (current) or **per-culture** phenotyping.
```
