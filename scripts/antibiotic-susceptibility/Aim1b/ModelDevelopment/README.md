Here is the file for model developments:
For inpatients we used XGv=boost classifier trained and test on inpatients.

Outpatient Antimicrobial Susceptibility Model Development: 
Notebook: Aim_1b_ModelDevelopment_Outpatients.ipynb
This notebook contains code for developing machine learning models to predict antimicrobial susceptibility for outpatient data.

Notes and Guidelines
Outpatient susceptibility prediction is more challenging due to data sparsity and lower resistance prevalence. 

Please Consider:

1. Filter Antibiotics by Prevalence

Include only antibiotics with resistance prevalence ≥ 5% or ≤ 95%.

2. Minimum Sample Size (Exclude antibiotics with fewer than 1,000 records).

3. Model Selection

Compare XGBoost and LightGBM models.

Use the model with higher performance for evaluation.

In most cases, performance differences are minimal.

4. Handling Low-Performance or Sparse Antibiotics:

For antibiotics with low model performance or high missingness:

Train on a combined dataset (inpatient + outpatient).

Evaluate performance only on outpatient data.

5. Deployment Consideration:

Exclude respiratory cultures for real-time model deployment.
