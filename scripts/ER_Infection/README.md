# Personalized Antibiograms for Machine Learning DrivenAntibiotic Selection

### Abstract
The Centers for Disease Control and Prevention identify improving antibiotic prescribing stewardship as the most important action to combat the spread of resistant bacteria. Clinicians balance broad empiric antibiotic coverage ensuring activity against serious infections vs. precision coverage targeting only the most likely pathogens. In this retrospective multi-site study, we trained machine learning models to predict which antibiotics infections would be susceptible to (personalized antibiograms) using electronic health record data of 8,342 infection treated at Stanford emergency departments between 2009 to 2019 and 15,806 uncomplicated urinary tract infections from Massachusetts General Hospital and Brigham Women’s Hospital in Boston between 2007 and 2016. We assessed the trade-off of broad-spectrum vs. precise antibiotic prescribing using a novel optimization procedure for antibiotic selection. In the Stanford dataset, personalized antibiograms reallocated existing distributions of empiric antibiotics while achieving a coverage rate (fraction of infections covered by treatment selection) of 85.9%; similar to clinician performance (84.3% p=0.11). In the Boston dataset, personalized antibiograms achieved a coverage rate of 90.4%; a significant improvement over clinician(88.1% p<0.0001) prescribing. Antibiotic selection driven by personalized antibiograms achieved similar coverage rates as seen in actual clinical practice with substantially narrower antibiotics. In the Stanford dataset, personalized antibiograms maintained clinician coverage rates while narrowing 69% of empiric vancomycin+piperacillin/tazobactam prescriptions to piperacillin/tazobactam monotherapy, and 40% of piperacillin/tazobactam prescriptions to cefazolin. In the Boston dataset, personalized antibiograms maintained clinical coverage rates while narrowing 48% of ciprofloxacin to trimethoprim/sulfamethoxazole. Precision empiric antibiotic prescribing supported by personalized antibiogram prediction models could improve patient safety and antibiotic stewardship by reducing unnecessary use of broad spectrum antibiotics that breed a growing tide of resistant organisms.

### Data Availability Statement
The Stanford cohort was derived from data made available through [STARR](https://starr.stanford.edu/), STAnford medicine Research data Repository. The Boston cohort has been made [publicly available](https://physionet.org/content/antimicrobial-resistance-uti/1.0.0/) through Physionet. 

### Demo
A demo of the software used for the analysis of this manuscript has been been made publicly available in a jupyter notebook [here](https://github.com/HealthRex/CDSS/blob/master/scripts/ER_Infection/notebooks/demo/Demo%20Personalized%20Antibiogram%20Linear%20Programming.ipynb). 

### Directory Descriptions

#### /ER_Infection/SQL/
 Contains the set of SQL queries used to derive the Stanford cohort.

####  /ER_Infection/notebooks/decision_alg/
Contains python code for the linear programming optimizer

####  /ER_Infection/notebooks/eda/
Contains notebooks with exploratory data analysis

####  /ER_Infection/notebooks/featurizing/
Contains code used to construct a feature matrix for our personalized antibiogram models

####  /ER_Infection/notebooks/figures_and_tabels/
Contains code used to construct figures and tables seen in the manuscript and supplement

####  /ER_Infection/notebooks/labelling/
Contains code used to label observations in the stanford dataset

####  /ER_Infection/notebooks/mit_data_analysis/
Contains code used for analysis of the Boston cohort

####  /ER_Infection/notebooks/modeling/
Contains code used to train personalized antibiogram models


