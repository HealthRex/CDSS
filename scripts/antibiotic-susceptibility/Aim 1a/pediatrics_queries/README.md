# ARM-Peds queries (in development)

Pediatric counterpart to ARMD — currently a collection of standalone SQL queries that adapt the adult cohort logic for patients under 18. Once stabilized, these will be packaged into a `ARM_Peds_pipeline/` sibling of `ARMD_pipeline/` with the same year-parameterized workflow.

## Status

**Work in progress.** Do not treat output of these queries as a finalized dataset. The cohort definition, antibiotic panels, and look-back windows may shift as the pediatric-specific design is finalized.

## How this differs from adult ARMD

- **Cohort**: patients `< 18` at culture order time (vs `>= 18` in adult ARMD's `01_cohort.sql`).
- **Antibiotic class/subtype mappings**: pediatric-specific dosing / approved-agent overrides will be applied here once finalized.
- **Comorbidities**: pediatric ICD-10 groupers (chromosomal disorders, prematurity, congenital anomalies) need to be added on top of the Elixhauser / AHRQ CCSR set used in the adult build.
- **Labs/vitals**: reference ranges differ by age band; quantile computations may need to be stratified.

## Contributing

If you're working on ARM-Peds, please:

1. Keep new queries here for now.
2. When the cohort definition stabilizes, lift them into a numbered `sql/` folder following the `ARMD_pipeline/sql/` pattern.
3. Update this README with a `legacy → pipeline` mapping table like the one in [`../legacy/README.md`](../legacy/README.md).
