# Antibiotic Susceptibility — Aim 1a

Code for building the **Antibiotic Resistance Microbiology Dataset (ARMD)** from Stanford's STARR via Google BigQuery.

ARMD is publicly available on [Dryad](https://doi.org/10.5061/DRYAD.JQ2BVQ8KP) and described in:

> Nateghi Haredasht, F. et al. *Antibiotic Resistance Microbiology Dataset (ARMD): A Resource for Antimicrobial Resistance from EHRs.* Scientific Data (2025). [doi:10.1038/s41597-025-05649-7](https://doi.org/10.1038/s41597-025-05649-7)

---

## Folder map

- **[`ARMD_pipeline/`](./ARMD_pipeline)** — the active, reproducible adult pipeline. One-command year-versioned builds (`python run_pipeline.py --year 2025`). This is what you want for any new refresh of adult ARMD.
- **[`pediatrics_queries/`](./pediatrics_queries)** — queries for **ARM-Peds**, an upcoming pediatric counterpart to ARMD. Active development; not yet packaged as a pipeline.
- **[`legacy/`](./legacy)** — the original standalone adult SQL queries that the published ARMD release was built from. Kept for reference; superseded by `ARMD_pipeline/`.

## Year-versioned ARMD builds

The pipeline produces one self-contained BigQuery dataset per STARR refresh year:

```
som-nero-phi-jonc101.ARMD_2024.*    ← built from shc_core_2024
som-nero-phi-jonc101.ARMD_2025.*    ← built from shc_core_2025
```

Each dataset contains 16 ARMD feature tables (cohort, demographics, ward info, labs, vitals, antibiotic exposures, comorbidities, etc.) plus 3 reference lookup tables.

## Annual refresh — one-line workflow

When STARR publishes a new year of data:

```bash
cd ARMD_pipeline
python run_pipeline.py --year 2026
```

The runner creates `ARMD_2026`, uploads reference CSVs, runs all 17 SQL steps, and drops staging tables at the end. See [`ARMD_pipeline/README.md`](./ARMD_pipeline/README.md) for full usage, dependency graph, and validation tests.

## Citation

```bibtex
@article{nateghi2025armd,
  title={Antibiotic Resistance Microbiology Dataset (ARMD): A Resource for Antimicrobial Resistance from EHRs},
  author={Nateghi Haredasht, Fateme and others},
  journal={Scientific Data},
  volume={12},
  pages={1299},
  year={2025},
  doi={10.1038/s41597-025-05649-7}
}
```

## Contact

**Fateme Nateghi Haredasht, PhD** — [fnateghi@stanford.edu](mailto:fnateghi@stanford.edu)
