# Stanford Cosmos Environment: Onboarding Guide

## Eligibility

- Access is restricted to Stanford Medicine researchers.
- You will need:
  - **SID** (Stanford ID)  
  - **Epic UserWeb account**
  - Review and follow Cosmos "rules of the road" ([more info](https://galaxy.epic.com/Redirect.aspx?DocumentID=4024320&PrefDocID=113401))
- When publishing Cosmos-enabled findings, you must acknowledge Cosmos in your publication and, twice a year, provide the Governing Council with a list of your citations and any other works referencing your Cosmos-based research (per Section 2.3.1 of the Cosmos Terms).

## Sign Up Steps

1. **SID Request:**  
   Have someone with an SID request one for you: [Stanford SID Request](https://stanfordhc.service-now.com/esc)  
   - In the form, choose:  
     - In-person  
     - Epic
2. **Epic UserWeb Account:**  
   Create an account at [Epic UserWeb](http://userweb.epic.com/) (select Stanford Health Care).
3. **Cosmos Access Request:**  
   Complete the [Stanford Cosmos Access Request form](https://redcap.stanford.edu/surveys/?s=DAEFTNLWRFXTCNNK).
4. **Training:**  
   Complete applicable Epic Cosmos trainings. Sign up at [Epic Training Catalog](https://training.epic.com/CourseCatalog#/?LocationID=1&VersionID=1277&ViewID=train-tracks) (search "cosmos" under 'all applications').

## Access Levels

- **Aggregate-level access:**  
  Use Slicer Dicer in the Cosmos Portal for cohort discovery and feasibility analysis.
- **DSVM & Line-level access:**  
  - DSVM access: Requires Epic COS 500 (data scientist certification) for SQL/R/Python queries.
  - Line-level data: Requires Epic COS 550 (data architect certification).

## Getting Started

- After approval, log in to the Cosmos Portal with your Stanford credentials.
- **Slicer Dicer:**  
  Explore cohorts, diagnoses, medications, and outcomes with built-in filters and visualizations.
- **DSVM:**  
  Use R, Python, or SQL for advanced analysis and data mart creation.  
  Data marts can be exported as SQL tables, CSV, or parquet files.

## Data Structure & Handling

- Cosmos includes demographics, diagnoses, labs, medications, procedures, SDOH, and more.
- Dates are shifted per patient; ages may be truncated (all birthdays set to Jan 1).
- No direct identifiers; LDS excludes direct dates and other PHI.

## Workflow Overview

- Define your study or project.
- Use Slicer Dicer for feasibility, then request a data mart from a Stanford data architect for complex analysis (contact Kameron Black, kb633@stanford.edu, if needed).
- Notify Epic of your publication intent.
- Import data marts directly into R/Python via SQL connection for analysis.
- Validate, analyze, and publish results per Stanford and Epic guidelines.

## Support

- For questions or issues, contact: kb633@stanford.edu.

## Cosmos Publication Checklist

- Before publishing, clearly define your base population using recommended filters (e.g., "Has any encounters?" and "Base Patient") and avoid drawing conclusions from random samples ("Sneak Peek" mode).
- Review known data limitations, biases, and data quality issues for all relevant domains (see Cosmos Data Science White Papers and Data Encyclopedia).
- When ready to publish or share, mask small counts (<11), request file transfer via your Cosmos representative, notify Epic of your publication or presentation (CosmosPublications@epic.com), and include required Cosmos attribution.  
  For externally funded studies, submit your publication, presentation, or an abstract to the Cosmos community, ensuring transparency regardless of publication outcome.  
  [More info](https://galaxy.epic.com/?#Browse/page=1!68!50!100130418&from=Galaxy-Redirect)
