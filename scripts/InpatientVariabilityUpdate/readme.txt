-------------------------------------------------
Project summary 
-------------------------------------------------
Biomedical informatics PhD program rotation project to analyze reasons for variation in Stanford Health Care hospitalization costs (initially among hospitalizations with DRG for major bowel procedures). Overall goal is to hopefully identify ways that SHC can control costs
Author: Selina Pi
Date: Winter Quarter (Jan-Mar) 2023

-------------------------------------------------
Code 
-------------------------------------------------
0. Explorations
- Purpose: Collection of SQL BigQuery pulls to explore SHC clinical and cost data

1. Master file.ipynb 
- Purpose: Connects to lab's BigQuery clinical and cost databases to run cohort selection, feature extraction, visualizations, and regression models.
- Environment: healthrex_ml environment with setup steps described in the readme file here: https://github.com/HealthRex/healthrex_ml
- Terminal commands to open file in Jupyter Notebook:
  % conda activate healthrex_ml 
  % jupyter notebook

-------------------------------------------------
Data access and troubleshooting
-------------------------------------------------
- Steps for BigQuery access: https://github.com/HealthRex/CDSS/blob/master/scripts/DevWorkshop/ReadMe.GoogleCloud-BigQuery-VPC.txt 
- Python version: 3.11.0
- pip version: 22.3.1
- Google Cloud CLI version: 413.0.0
- My operating system: macOS Ventura 13.2
- You can ignore this warning in Terminal/Jupyter Notebook: "WARNING:  
Cannot add the project "som-nero-phi-jonc101" to ADC as the quota project because the account in ADC does not have the "serviceusage.services.use" permission on this project. You might receive a "quota_exceeded" or "API not enabled" error. Run $ gcloud auth application-default set-quota-project to add a quota project."
- Some issues go away when you reimport the python package or restart the kernel...
