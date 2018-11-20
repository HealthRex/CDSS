### Goal

The goal of this project is to predict the result of blood culture lab results. As a corollary,
we also seek to predict the susceptibility/resistance of certain cultures to certain antibiotics.

### Motivation

Understanding accurate predictors of blood culture labs could reduce the need to 
perform certain lab tests thereby reducing waste. Additionally, it is becoming more imperative
to minimize the use of broad spectrum antibiotics as bacteria develop resistance. 


### Data
The core data for this project is in the stride_culture_micro table. This table provides a series of blood
culture tests.
Note: we create a new column in our matrix for our presence/absence label  using
the organism_name column from stride_culture_micro. See LabCultureMatrix for code sample.


### ML Tasks and corresponding code
1. Determine presence of infection
    * Binary classification
2. What strain of bacteria
    * Binary classification
See LabCulturePredictionPipeline for code (only blood culture - LABBLC - was used).


Results of the above tasks are reproducible by running the current LabCulturePredictionPipeline script.


### Directions this project could go
This project could benefit from including indications of previous cultures such as:
* Whether the patient has previously grown a certain bacteria
* Whether the patient has previously been given a certain antibiotic


### Suggested Readings
* https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5632149/
* https://www.sciencedirect.com/science/article/pii/S1532046418301291
* https://www.shmabstracts.com/abstract/predicting-bacteremia-in-hospitalized-patients-an-analysis-of-electronic-health-record-data/
* https://bmcmedinformdecismak.biomedcentral.com/articles/10.1186/s12911-017-0550-1
* https://www.sciencedirect.com/science/article/pii/S0924857907003445?via%3Dihub
* https://www.ncbi.nlm.nih.gov/pubmed/28268133
* https://academic.oup.com/cid/article/65/10/1607/3950071
* https://journals.lww.com/co-infectiousdiseases/Citation/2017/12000/Machine_learning___novel_bioinformatics_approaches.2.aspx
