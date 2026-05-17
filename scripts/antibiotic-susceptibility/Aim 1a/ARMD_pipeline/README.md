# ARMD Pipeline

A reproducible data extraction and validation pipeline for the **Antibiotic Resistance Microbiology Dataset (ARMD)** — a de-identified resource derived from electronic health records (EHR) at Stanford Health Care.

ARMD is publicly available on [Dryad](https://doi.org/10.5061/DRYAD.JQ2BVQ8KP) and described in:

> Nateghi Haredasht, F. et al. *Antibiotic Resistance Microbiology Dataset (ARMD): A Resource for Antimicrobial Resistance from EHRs.* Scientific Data (2025). [doi:10.1038/s41597-025-05649-7](https://doi.org/10.1038/s41597-025-05649-7)

---

## Overview

This pipeline extracts 16 feature tables from the [STAnford medicine Research data Repository (STARR)](https://starr.stanford.edu/) via Google BigQuery, producing the complete ARMD dataset. It includes a comprehensive validation test suite to ensure data quality after each run.

### Year-versioned builds

Each run produces a self-contained BigQuery dataset named **`ARMD_<year>`** (e.g. `ARMD_2024`, `ARMD_2025`) built from the matching STARR source dataset **`shc_core_<year>`**. The two datasets live side by side in the same project so you can compare or migrate between refreshes without disrupting downstream consumers.

```
som-nero-phi-jonc101.ARMD_2024.microbiology_cultures_cohort
som-nero-phi-jonc101.ARMD_2024.microbiology_cultures_demographics
…
som-nero-phi-jonc101.ARMD_2025.microbiology_cultures_cohort
som-nero-phi-jonc101.ARMD_2025.microbiology_cultures_demographics
```

Each `ARMD_<year>` dataset also contains the three reference tables uploaded by the pipeline (`temp_antibiotics`, `prior_antibiotics_list`, `CPT_ICD10PCS_mapping`) so the dataset is fully self-contained.

### Dataset at a Glance

| Metric | Value (2024 release) |
|---|---|
| Culture records | ~751,000 |
| Unique patients | ~283,000 |
| Culture types | Urine (50%), Blood (39%), Respiratory (11%) |
| Antibiotics tested | 55 |
| Time span | 1999–2024 |
| Source | Stanford Health Care EHR (Epic → STARR) |

---

## Project Structure

```
ARMD_pipeline/
├── config.py                     # BigQuery project, dataset resolution, reference stats
├── run_pipeline.py               # Pipeline runner (takes --year)
├── requirements.txt              # Python dependencies
├── pytest.ini                    # Test configuration
├── CPT_ICD10PCS_mapping.csv      # Procedure code mapping reference (also at repo root)
├── sql/                          # SQL queries (numbered by execution order)
│   ├── 01_cohort.sql             # Base cohort: cultures, organisms, susceptibility
│   ├── 02_demographics.sql       # Age, gender
│   ├── 03_ward_info.sql          # IP/OP/ER/ICU indicators
│   ├── 04_labs.sql               # Lab quantiles + first/last over 14/30/180-day windows
│   ├── 05_vitals.sql             # Vital sign quantiles + first/last
│   ├── 06_abx_class_subtype_lookup.sql  # Antibiotic classification reference
│   ├── 07_prior_medications.sql  # Prior antibiotic exposure with time-to-event
│   ├── 08_antibiotic_class_exposure.sql  # Class-level exposure
│   ├── 09_antibiotic_subtype_exposure.sql # Subtype-level exposure
│   ├── 10_microbial_resistance.sql       # Prior resistance history
│   ├── 11_prior_infecting_organism.sql   # Previous infecting organisms
│   ├── 12_comorbidities.sql      # Elixhauser & AHRQ CCSR comorbidities
│   ├── 13_prior_procedures.sql   # Dialysis, CVC, mech. ventilation, etc.
│   ├── 14_adi_scores.sql         # Area Deprivation Index scores
│   ├── 15_nursing_home_visits.sql # Nursing home visit history
│   └── 16_implied_susceptibility.sql # Inferred susceptibility rules
└── tests/
    ├── conftest.py               # Pytest fixtures (year-aware)
    └── test_armd_validation.py   # 60+ validation tests
```

### How year parameterization works

Each SQL file under `sql/` keeps two literal dataset names so it remains independently runnable in the BigQuery UI:

```
som-nero-phi-jonc101.shc_core_2023             ← source placeholder
som-nero-phi-jonc101.antimicrobial_stewardship  ← destination placeholder
```

At runtime, `run_pipeline.py` rewrites those literals to `shc_core_<year>` and `ARMD_<year>` before sending each statement to BigQuery. To run a SQL file standalone in the BigQuery console for debugging, just change the source dataset name in your copy.

---

## Setup

### Prerequisites

- Python 3.9+
- Access to Stanford's STARR BigQuery environment (via VPN)
- Google Cloud authentication configured (`gcloud auth application-default login`)

### Install Dependencies

```bash
cd ARMD_pipeline
pip install -r requirements.txt
```

---

## Usage

### Build a specific year's ARMD dataset

```bash
# Build ARMD_2024 from shc_core_2024
python run_pipeline.py --year 2024

# Build ARMD_2025 from shc_core_2025
python run_pipeline.py --year 2025
```

The runner will:

1. Create the destination dataset `ARMD_<year>` if it doesn't exist.
2. Upload the three reference CSVs (`temp_antibiotics.csv`, `prior_antibiotics_list.csv`, `CPT_ICD10PCS_mapping.csv`) into that dataset.
3. Execute the 16 SQL steps in order, rewriting `shc_core_2023` → `shc_core_<year>` and `antimicrobial_stewardship` → `ARMD_<year>` for each statement.

### Run a Single Step

```bash
python run_pipeline.py --year 2025 --step 01_cohort
```

### Resume from a Specific Step

```bash
python run_pipeline.py --year 2025 --from 07_prior_medications
```

### Dry Run (Preview Without Executing)

```bash
python run_pipeline.py --year 2025 --dry-run
```

### Skip the Setup Step

If the reference CSVs are already uploaded and you just want to re-run the SQL:

```bash
python run_pipeline.py --year 2025 --skip-setup
```

### Export Tables to CSV

```bash
python run_pipeline.py --year 2025 --export ./output_2025/
```

---

## Validation Tests

The test suite validates the dataset against the published ARMD paper statistics and clinical expectations. Tests run directly against BigQuery.

### Run All Tests for a Specific Year

```bash
cd ARMD_pipeline
pytest tests/ -v --year 2025
```

### Run Tests for a Specific Table

```bash
pytest tests/ -v --year 2025 -k "test_cohort"          # Cohort table only
pytest tests/ -v --year 2025 -k "TestDemographics"     # Demographics only
pytest tests/ -v --year 2025 -k "TestLabs"             # Labs only
```

### Test Categories

| Category | # Tests | What It Checks |
|---|---|---|
| **Schema** | 16 | Required columns exist in each table |
| **Referential integrity** | 10 | All feature records link back to cohort |
| **Domain constraints** | 8 | Only valid categorical values |
| **Row count & distributions** | 7 | Totals and proportions match paper (±30% tolerance) |
| **Temporal consistency** | 5 | Time-to-event values point in correct direction |
| **Clinical plausibility** | 4 | Lab/vital values in physiological ranges |
| **Cross-table consistency** | 5 | Tables agree with each other |
| **Logical checks** | 5+ | Positive cultures have organisms, adults only |

### Updating Reference Statistics

After each refresh, update the expected values in `config.py`:

```python
REFERENCE_STATS = {
    "total_culture_records": 751_075,
    "unique_patients": 283_715,
    "row_count_tolerance_pct": 30,
    ...
}
```

---

## SQL Query Dependency Graph

```
00_setup (CSV uploads: temp_antibiotics, prior_antibiotics_list, CPT mapping)
   │
01_cohort ──────────┬──► 02_demographics
                    ├──► 03_ward_info
                    ├──► 04_labs
                    ├──► 05_vitals
                    ├──► 06_abx_lookup ──► 07_prior_medications ──┬──► 08_class_exposure
                    │                                              └──► 09_subtype_exposure
                    ├──► 10_microbial_resistance (uses prior_antibiotics_list)
                    ├──► 11_prior_infecting_organism
                    ├──► 12_comorbidities
                    ├──► 13_prior_procedures (uses CPT_ICD10PCS_mapping)
                    ├──► 14_adi_scores
                    ├──► 15_nursing_home_visits
                    └──► 16_implied_susceptibility
```

---

## Bug fixes vs. original queries (May 2026 refactor)

This pipeline incorporates several corrections to the original queries that were preserved verbatim from the master scripts folder. If you compare with the older `Labs.sql`, `Vitals.sql`, or `prior_abx_class_subtype_lookup.sql`, expect these differences:

- **`04_labs.sql`**: `last_wbc` was computed with `FIRST_VALUE` instead of `LAST_VALUE`. `first/last_lymphocytes`, `first/last_hgb`, `first/last_plt` were all reading the `neutrophils` source column. `Period_Day` was hardcoded to 14 in all three look-back windows; now correctly emits 14 / 30 / 180.
- **`05_vitals.sql`**: `Q25_diasbp` was computed from `sysbp`. `median_sysbp` was missing entirely. `LAST_VALUE` calls lacked `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`, causing every `last_*` column to equal the current row's value.
- **`06_abx_class_subtype_lookup.sql`**: `INSERT INTO` targeted a personal sandbox dataset (`fateme_db`). Now points at the pipeline destination.
- **`10_microbial_resistance.sql`**: Column names `recorded_resistsant_time` and `resistsant_time_to_cultureTime` carried a misspelling. Renamed to `recorded_resistant_time` and `resistant_time_to_culturetime`.
- **`11_prior_infecting_organism.sql`**: `CREATE TABLE` reference was missing the project prefix. Also `prior_infecting_organism_days_to_culutre` renamed to `..._days_to_culture`.
- **`13_prior_procedures.sql`**: Unclosed `where (` and trailing comma — both produced SQL parse errors. Column `procedure_days_culture` renamed to `procedure_time_to_culturetime` for consistency with sibling tables.

---

## Output Tables

Each SQL step produces a BigQuery table under `som-nero-phi-jonc101.ARMD_<year>`:

| Step | Output Table | ARMD CSV File |
|---|---|---|
| 01 | `microbiology_cultures_cohort` | `microbiology_cultures_cohort.csv` |
| 02 | `microbiology_cultures_demographics` | `microbiology_cultures_demographics.csv` |
| 03 | `microbiology_cultures_ward_info` | `microbiology_cultures_ward_info.csv` |
| 04 | `microbiology_Labs` | `microbiology_cultures_labs.csv` |
| 05 | `microbiology_Vitals` | `microbiology_cultures_vitals.csv` |
| 06 | `class_subtype_lookup` | *(reference table)* |
| 07 | `microbiology_cultures_medication_exposure` | `microbiology_cultures_prior_med.csv` |
| 08 | `microbiology_cultures_antibiotic_class_exposure` | `microbiology_cultures_antibiotic_class_exposure.csv` |
| 09 | `microbiology_cultures_antibiotic_subtype_exposure` | `microbiology_cultures_antibiotic_subtype_exposure.csv` |
| 10 | `microbiology_microbial_resistance_augmented` | `microbiology_cultures_microbial_resistance.csv` |
| 11 | `microbiology_culture_prior_infecting_organism_augmented` | `microbiology_culture_prior_infecting_organism.csv` |
| 12 | `microbiology_comorbidity_augmented` | `microbiology_cultures_comorbidity.csv` |
| 13 | `microbiology_cultures_priorprocedures_augmented` | `microbiology_cultures_priorprocedures.csv` |
| 14 | `microbiology_cultures_adi_scores` | `microbiology_cultures_adi_scores.csv` |
| 15 | `microbiology_cultures_nursing_home_visits_augmented` | `microbiology_cultures_nursing_home_visits.csv` |
| 16 | `microbiology_implied_susceptibility` | `microbiology_cultures_implied_susceptibility.csv` |

Tables are linked using: `anon_id`, `pat_enc_csn_id_coded`, `order_proc_id_coded`.

---

## Data Sources

All data is extracted from [STARR](https://starr.stanford.edu/) (Stanford Medicine Research Data Repository):

- **Source dataset:** `som-nero-phi-jonc101.shc_core_<year>` (e.g. `shc_core_2024`, `shc_core_2025`)
- **Core tables used:** `order_proc`, `lab_result`, `culture_sensitivity`, `demographic`, `flowsheet`, `adt`, `order_med`, `mapped_meds`, `diagnosis`, `procedure`, `encounter`, `zip`
- **Reference tables (shared):** `mapdata.ADI_data_CA`, `mapdata.ahrq_ccsr_diagnosis`, `mapdata.elixhauser-comorbidity-components`
- **Reference tables (uploaded per build):** `temp_antibiotics`, `prior_antibiotics_list`, `CPT_ICD10PCS_mapping`

---

## De-identification

The dataset produced by this pipeline keeps raw values (raw age, raw gender, zip codes, raw timestamps). For Dryad release, an additional de-id pass is applied:

- Patient IDs are anonymized (`anon_id`)
- Ages are binned (18–24, 25–34, ..., 90+)
- Gender is binary-coded (0/1)
- All timestamps are jittered at the patient level
- ZIP codes are removed

That de-id pass is **not** part of this pipeline.

---

## Citation

```bibtex
@article{nateghi2025armd,
  title={Antibiotic Resistance Microbiology Dataset (ARMD): A Resource for Antimicrobial Resistance from EHRs},
  author={Nateghi Haredasht, Fateme and Amrollahi, Fatemeh and Maddali, Manoj V. and Marshall, Nicholas and Ma, Stephen P. and Cooper, Lauren N. and Johnson, Andrew O. and Wei, Ziming and Medford, Richard J. and Kanjilal, Sanjat and Banaei, Niaz and Deresinski, Stanley and Goldstein, Mary K. and Asch, Steven M. and Chang, Amy and Chen, Jonathan H.},
  journal={Scientific Data},
  volume={12},
  pages={1299},
  year={2025},
  doi={10.1038/s41597-025-05649-7}
}
```

---

## License

This project was developed under Stanford University IRB approval (eProtocol #70466). The ARMD dataset on Dryad is licensed under [CC BY-NC-ND 4.0](http://creativecommons.org/licenses/by-nc-nd/4.0/).

## Contact

**Fateme Nateghi Haredasht, PhD**
Stanford University
[fnateghi@stanford.edu](mailto:fnateghi@stanford.edu)
