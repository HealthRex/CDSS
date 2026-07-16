# data/input — where your adjudication sheet goes

This directory is **git-ignored** (it holds PHI). Nothing here is committed except this README.

## What to put here
Place your adjudication sheet as the default path:

    data/input/adjudication.csv

It must follow the schema documented in the top-level `README.md` ("Input schema"):
75 columns = 5 identifiers + 14 fields × (P1, P1 support, P2, P2 support, ground_truth).

Or keep any filename and point the scripts at it:

    ./build_curated_dataset.py --input data/input/my_sheet.csv
    ./run_phenotyping.py       --input data/input/my_sheet.csv --model gpt-5

## Where the data comes from
PHI input files are shared **separately** (e.g. Stanford Medicine Box) — never through git.
You do **not** need note text here: Stage 1 (`build_curated_dataset.py`) fetches the
de-identified notes from BigQuery using your own GCP credentials.

## Outputs
Generated files land in `../output/` (also git-ignored): `curated_dataset.csv`,
`mapping_summary.csv`, `llm_phenotyping_<model>_summary.csv`, and `analysis/`.
