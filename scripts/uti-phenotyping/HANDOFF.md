# UTI Phenotyping — Handoff Guide

Orientation for the next owner. **For step-by-step run instructions, see `README.md`.**
This guide covers what the project is, where the data lives, and **what file holds what result**.

---

## 1. What this is
LLM-based **UTI phenotyping** from clinical notes, benchmarked against physician adjudication.
Two stages + evaluation + analysis:
1. **`build_curated_dataset.py`** — map each labeled case (MRN + timestamps) to its de-identified
   note text via BigQuery → `curated_dataset.csv`.
2. **`run_phenotyping.py`** — run a PHI-safe **Vertex AI** LLM over each note → per-note labels
   (10 symptoms + 4 assessments).
3. **`evaluate.py`** — accuracy / Cohen's κ vs ground truth.
4. **`symptom_feature_analysis.py`** — symptom studies + charts.

## 2. Before you start
- **Google Cloud access** (your own): Vertex models on `som-nero-phi-jonc101-secure`; BigQuery on
  `som-nero-phi-jonc101` (+ `-secure`). Auth via `gcloud auth application-default login`; Stanford
  full-traffic **VPN on**. No API keys. See `README.md` → "Prerequisites."
- **Python env**: `README.md` → "TL;DR."
- **Sanity check**: `./verify_vertex_access.py` should show the models `[OK]`.

## 3. Getting the data (it is NOT in git)
The repo is **code only**; `data/` is git-ignored. The data (the input sheet + the whole
`data/output/`) lives in **Stanford Medicine Box**:

> https://stanfordmedicine.box.com/s/wepikvold08em34o3b5cscozvqr56g7s
> *(access is Box-permission-gated — request access if it doesn't open)*

After cloning:
- Put the adjudication sheet at **`data/input/adjudication.csv`** (or use `--input <path>`).
- To reuse prior results instead of regenerating, copy the Box **`data/output/`** into
  `data/output/`. Otherwise regenerate with the pipeline (needs BigQuery + Vertex).

## 4. What file contains what result

| File (under `data/output/`) | Contents | Produced by |
|---|---|---|
| `curated_dataset.csv` | de-identified note text joined per case (`deid_note_text`) | `build_curated_dataset.py` (Stage 1) |
| `mapping_summary.csv` | per-case MRN→anon_id mapping + matched-row counts (0-match rows = dropped) | `build_curated_dataset.py` |
| `llm_phenotyping_<model>_summary.csv` | per-note LLM predictions **+ ground-truth columns** (self-contained) | `run_phenotyping.py` (Stage 2) |
| `llm_phenotyping_<model>_results.jsonl` | raw per-note LLM records | `run_phenotyping.py` |
| `llm_phenotyping_<model>_metrics.json` | accuracy / κ / classification report per field | `evaluate.py` (Stage 3) |
| `analysis/<model>/missingness_uncertainty.csv` + `.png` | P(UTI \| symptom absent) — **deck "Missingness Insight"** | `symptom_feature_analysis.py` |
| `analysis/<model>/mismatch_importance.csv` + `.png` | symptom-mismatch → LLM-error correlation — **deck "Feature-Level Error Drivers"** | `symptom_feature_analysis.py` |
| `analysis/<model>/diagnostic_vs_frequency.csv` + `.png` | diagnostic power vs documentation frequency | `symptom_feature_analysis.py` |

The **prelim-results slides** (`presentation/aim3_prelim_reseach_plan.pptx`, committed) come from the
`analysis/<model>/` files (insights) and `llm_phenotyping_<model>_summary.csv` (accuracy). The Box
`data/output/` files use the old model names (`gpt-5`, `claude-3_7-sonnet`, `gemini-2_5-pro`);
re-runs use current Vertex names (e.g. `gemini-2.5-pro`; note `gpt-5` is retired — no OpenAI BAA).

## 5. How to run — end to end (summary; details in `README.md`)
Save your sheet as `data/input/adjudication.csv`, then run **in order** (each stage writes to
`data/output/` and the next one reads it):
```bash
./verify_vertex_access.py                          # confirm Vertex access
./build_curated_dataset.py                         # Stage 1: sheet -> BigQuery -> curated_dataset.csv
./run_phenotyping.py --model gemini-2.5-pro        # Stage 2: notes -> Vertex LLM -> *_summary.csv
./evaluate.py --model gemini-2.5-pro               # Stage 3: predictions vs ground truth -> metrics
./symptom_feature_analysis.py --model gemini-2.5-pro   # symptom studies + charts
```
**New CSV at a different path?** Pass `--input <path>` to Stage 1, Stage 2, `evaluate.py`, and
`symptom_feature_analysis.py` (Stage 1's default output feeds Stage 2's default `--curated`). This
is the full regenerate-from-scratch path: curate → predict → evaluate → analyze.

## 6. Key things to know
- **LLMs run on Vertex AI** (ADC, no keys). `gpt-5` is gone (no Stanford OpenAI BAA); default is
  `gemini-2.5-pro`. All models are enabled on `som-nero-phi-jonc101-secure`.
- **Phenotyping is per note, not per culture** — a urine culture with several notes yields several
  predictions (no roll-up). Decide if you want per-culture aggregation before scaling.
- **Counts you'll see:** ~**75 cases map** (MRN→anon_id) but ~**66 get phenotyped** — the gap is note-
  timestamp matching (Stage 1 keys note time off the *Collins* column only; Stage 2 falls back to
  *Lee*). See `README.md` → "Known limitations."
- **Ground truth:** `run_phenotyping.py` warns + runs without labels; `evaluate.py` /
  `symptom_feature_analysis.py` require labels (error if absent).
- **New input CSVs:** same 75-column schema; drop at `data/input/adjudication.csv` (or `--input`).
  A new sheet has only MRNs + timestamps → Stage 1 refetches notes from BigQuery with your creds.

## 7. What's next (scale-up)
Full adjudicated gold set, calibrated per-field metrics, and hybrid (rule + LLM) phenotyping.
See `presentation/aim3_progress_scaleup.pptx`.
