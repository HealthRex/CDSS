`train_models.py` is used to train and test the machine learning model. It utilizes cohorts, datasets, evaluators, extractors, featurizers, models, and trainers files from the `healthrex_ml` directory. Through this file, one can define a data cohort, extract the desired feature values (ex. lab results, diagnoses, etc), and train/test a machine learning model. The code contains definitions for a Random Forest model and LightGBM model but other desired model configurations can be added as well. 

`__init__.py`, `cosmos.py`, and `deploy.py` are utilized to generate real-time model estimates. Real-time feature vectors are populated using FHIR-based Epic API calls and fed into the model (developed above) to generate real-time inferences. These values are stored in the Azure Cosmos database and can be accessed through function calls listed in `cosmos.py`. 

`generateEmail.py`, `orderInfo.py`, and `order_action.py` are used to gather prospective estimates from the ordering physicians. FHIR-based Epic API calls are used to extract additional information (such as recent WBC results or demographic information) regarding a specific order that was placed. This code can autogenerate an email containg all this information that is sent to the ordering physicians. 

Some classes and functions are imported from healthrex_ml and referenced in `train_model.py`. The source code for healthrex_ml can be found at https://github.com/HealthRex/deployr-dev.


Code contributors: Grace Y.E. Kim, Conor K. Corbin, Robert Maclay, Aakash Acharya, Sreedevi Mony, Soumya Punnathanam, Sajjad Fouladvand. 
