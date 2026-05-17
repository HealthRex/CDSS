# Legacy queries (archived)

These are the **original standalone SQL queries** that produced the first published ARMD release (Dryad, May 2025). They were built from `shc_core_2023` against the now-deprecated dataset name `antimicrobial_stewardship`.

## Status

**Superseded.** All of these queries have been incorporated, bug-fixed, and year-parameterized in [`../ARMD_pipeline/sql/`](../ARMD_pipeline/sql). Do not use the queries in this folder for new refreshes — use the pipeline instead.

## Mapping legacy → pipeline

The pipeline's numbered SQL files correspond to these originals:

| Legacy file | Pipeline equivalent |
|---|---|
| `microbiology_cultures_cohort_query.sql` | `sql/01_cohort.sql` |
| `microbiology_cultures_demographics.sql` | `sql/02_demographics.sql` |
| `microbiology_cultures_ward_info.sql` | `sql/03_ward_info.sql` |
| `Labs.sql` | `sql/04_labs.sql` |
| `Vitals.sql` | `sql/05_vitals.sql` |
| `prior_abx_class_subtype_lookup.sql` | `sql/06_abx_class_subtype_lookup.sql` |
| `time-to-event-augmented-queries/medication_exposure.sql` | `sql/07_prior_medications.sql` |
| `time-to-event-augmented-queries/antibiotic_class_exposure.sql` | `sql/08_antibiotic_class_exposure.sql` |
| `time-to-event-augmented-queries/antibiotic_subtype_exposure.sql` | `sql/09_antibiotic_subtype_exposure.sql` |
| `time-to-event-augmented-queries/microbial_resistance.sql` | `sql/10_microbial_resistance.sql` |
| `time-to-event-augmented-queries/previous_infecting_organisms.sql` | `sql/11_prior_infecting_organism.sql` |
| `time-to-event-augmented-queries/comorbidities.sql` | `sql/12_comorbidities.sql` |
| `time-to-event-augmented-queries/prior_procedures.sql` | `sql/13_prior_procedures.sql` |
| `microbiology_cultures_adi_scores.sql` | `sql/14_adi_scores.sql` |
| `time-to-event-augmented-queries/nursing_home_visits.sql` | `sql/15_nursing_home_visits.sql` |
| `time-to-event-augmented-queries/Implied-susceptibility.sql` | `sql/16_implied_susceptibility.sql` |

## Bug fixes applied during migration

The pipeline corrects several bugs preserved from these originals — see [`../ARMD_pipeline/README.md`](../ARMD_pipeline/README.md) for the full list. Highlights:

- `Labs.sql`: `last_wbc` was computed with `FIRST_VALUE`; `first/last_lymphocytes`, `first/last_hgb`, `first/last_plt` all read from the `neutrophils` source column; `Period_Day` was hardcoded to 14 across all three look-back windows.
- `Vitals.sql`: `Q25_diasbp` was computed from `sysbp`; `median_sysbp` was missing entirely; `LAST_VALUE` calls lacked the unbounded frame, so every `last_*` column equaled the current row's value.
- `prior_abx_class_subtype_lookup.sql`: `INSERT INTO` targeted a personal sandbox dataset (`fateme_db`) so the lookup table ended up empty.
- `time-to-event-augmented-queries/prior_procedures.sql`: unclosed `where (` and a trailing comma — both produced parse errors.
- `time-to-event-augmented-queries/microbial_resistance.sql`: column name typos (`resistsant`).
- `time-to-event-augmented-queries/previous_infecting_organisms.sql`: missing project prefix on `CREATE TABLE`; typo `culutre` → `culture`.
- `01_cohort.sql` (pipeline only): added `SELECT DISTINCT` to dedupe source-level duplicate rows in `culture_sensitivity` that were inflating row counts by ~50%.

## Why keep these around?

For reproducibility of the published Dryad release. Anyone reading the Scientific Data paper can match the published methodology back to these exact queries. The pipeline produces a slightly different (deduplicated, bug-corrected) dataset, which is documented in its README.
