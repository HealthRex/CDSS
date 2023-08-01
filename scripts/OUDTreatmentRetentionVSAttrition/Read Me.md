This code is still under construction, optimization, documentation and revisions. 

<h1 style="font-size:60px;">1. Input data format</h1>

Please copy your data under the "feature_matrix" directory. You'd need to create train data (```train_set.csv```) and test data(```test_set.csv```). Each row in your data represent one encounter. Columns include patient ID (person_id), predictors (a list of concept IDs and demographic features), and meta-data related columns (such as drug exposure start date and etc.). Remember to list your meta-data features in "non_feature_list" variable within the "main_ml_model.py". Here, the assumption is that the treatment duration is in a column labeled as "TreatmentDuration". 


<h1 style="font-size:60px;">1. Input data format</h1>

Run the following command to train ML models using your train data:

```
python3 main_ml_models.py --ml_model lr
```

Note, ```ml_model``` argumant helps you define what ML model to choose. Options are: lr (for logistic regression), rf (for random forest), and xgb (for xgboost). 
