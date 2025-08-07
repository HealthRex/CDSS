AIM2: Real-Time Deployment of Antimicrobial Susceptibility Prediction Model
Objective
Deploy machine learning models for predicting antimicrobial susceptibility in real time using hospital EHR data, within the Stanford Health Care (SHC) infrastructure.

Infrastructure & Deployment Requirements
 Security & Compliance
You must be connected to the SHC VPN at all times when working on this deployment.


All work must be conducted under an active IRB due to the presence of Protected Health Information (PHI).


Coordinate closely with the Stanford SHC infrastructure team for permissions and approvals.
Model Deployment via Azure Functions
Key Notes
Azure Functions are used for real-time inference.


You cannot create a new Azure Function environment independently — this must be provisioned by the SHC infrastructure team.


Deployment Process
Request Environment Creation


Contact the SHC team.


Provide a description of:


Project purpose


Project scope


Required access level


AIM2 Environment Setup


The SHC team has provisioned the Azure Function environment named: **SmartAlert**.


Associated cosmosdb is also created under **machinelearningdb** named smartaler. For generating new containers ensure you use the same partition key path  as you need to retrieve your records otherwise you will miss your saved records.
Forexample you can simply use /PartionKey for all the containers. 

Container Creation Limitation


We've encountered a container quota limit within machinelearningdb.


This issue has been reported to SHC and is under resolution — follow up regularly with them for updates. Ask soumya and sree for updates.




Summary of Infrastructure: Current Status
Azure Function Environment Created:
 The environment SmartAlert has been successfully provisioned.


Credentials Provided:
 Environment variables and credentials are available — refer to the shared Box folder.


Database and Container Provisioned:
 The Azure storage database and container have been created.


Container Throughput Issue:
 The container has reached its throughput limit. The SHC team is actively working to resolve this.


Deployment:


Feature Extraction:
Labs (over the past 14 days) , Vitals (over the past 48 hours), Demographics (including Age, Gender), medication (over the past 180 days), patient location has been extracted. 
Comorbidity components are extracted but essentially with a real-time model we did not incorporate. 
Historical microbial resistance (under development all susceptibility and resistant to abx needs further debugging and exploring of API)
Access to Nursing home visit, ADI score iis not provided. 
Inference: 
local testing of your model needs to be completed you should ensure it runs without errors.
Once validated, submit a request to the SHC team for:


Deployment URL


Databricks access token






 FHIR API Access:
 All required EPIC FHIR API access has been granted for this project.


Code overview:
pipeline consists of two main modules and one supporting module:


Supporting Modules
utils.py – Utility Functions
This module includes helper functions used throughout the pipeline.
 Key functionality includes:
Extracting patient identifiers such as FHIR ID, MRN, and encounter ID from the input data.


Validating or formatting inputs before inference or logging.
cosmos.py – CosmosDB Integration
This module handles all interactions with Azure CosmosDB, including:
Writing and updating patient records (e.g., inference results, error logs).


Inserting failed inference attempts into the Model_APIErrors container.


Ensuring correct partition keys and container IDs are used for writing data.
 Note: Be sure to update the partition key and container ID as required by recent SHC infrastructure changes.

1. TimeTriggerActivePopulation Module
This is a time-triggered Azure Function that initiates the pipeline on a scheduled basis.
Trigger Frequency:
 By default, the function runs every 24 hours.


Local Testing:
 For development or debugging, you can change the schedule to run every 10 minutes by updating the function.json file:

 json
CopyEdit
{
  "schedule": "0 */10 * * * *" // Every 10 minutes
}
Function Behavior (__init__.py):


Every 10 minutes, the function loops through 8 hospital units used for silent deployment (similar to deployerdb).


For each unit, it queries all current inpatients and retrieves:


FHIR_id


Encounter ID


MRN (Medical Record Number)


Gender


Date of birth


Current bedding unit


Parallel Processing:


The function uses 20 threads for faster data processing.


For debugging purposes, you can reduce this to a single thread by modifying the thread pool size in the config.


Inference and Error Handling:


Each patient's data is sent for inference up to 5 times (retry mechanism).


If inference consistently fails, the record is added to the Model_APIErrors container in CosmosDB.


Important Notes for Deployment:


Be sure to update the partition key as the SHC infrastructure is currently being changed.


You will also need to update the container ID if there are any schema or naming changes in CosmosDB.
Make sure you log your code for the real-time deployment logging information will be available for 24 hours.

2. HttpTriggerInference Module
This is an HTTP-triggered Azure Function that produces antibiotic resistance scores for individual patients.
 It can be executed via the function URL, either locally or through the deployed Azure URL.
__init__.py – Main Inference Logic
This script orchestrates the full inference pipeline:


Retrieves patient clinical data by calling the FHIR Epic REST API.


Constructs a feature vector using the patient’s medical history.


Passes the features through the model to generate a resistance score.


Writes the score to the appropriate container in CosmosDB for persistence.


feature_engineering.py – Feature Construction
This module defines a class that extracts and processes structured EHR data for each patient.
 The extracted features include:


Demographics (e.g., age, gender)


Lab results


Vital signs


Comorbidities


Prior antibiotic exposures


Antibiotic class and subtype


Note:
 Sections related to prior microbial resistance and organism identification are still under development.
 These must be debugged and completed before full production deployment
Empricabx.py – Antibiotic Resistance Prediction
This module contains the logic to generate antibiotic-specific resistance scores.


It can use a model deployed via Azure Databricks, or fallback to a locally loaded model.


The output includes resistance probabilities for each antibiotic.


Note:
 This module requires further debugging and testing, as it depends on finalized feature engineering, which is not yet completed.
List of prior antibiotics is the same as Aim1_1a
The Comorbidity Components is the same as Aim_1a
Model : is the inpatient model we developed for Aim1_b


  
