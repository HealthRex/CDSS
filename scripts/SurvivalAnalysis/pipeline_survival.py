import os
import numpy as np
import pandas as pd
import copy
import warnings
import matplotlib.pyplot as plt


from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sksurv.ensemble import RandomSurvivalForest
from sksurv.linear_model import CoxPHSurvivalAnalysis, CoxnetSurvivalAnalysis
import xgboost as xgboost
from sksurv.metrics import concordance_index_censored
import shap
from matplotlib.pyplot import axis

from sklearn.model_selection import train_test_split
from sklearn.model_selection import GroupKFold, StratifiedGroupKFold
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline


# Specify the path to your CSV file
csv_file_path = "synthetic_survival_data.csv"

# Read the CSV file into a Pandas DataFrame
df = pd.read_csv(csv_file_path)


# from column_mapping import column_mapping

# # Load your  dataset
# your_data = load_data('your_data.csv')

# # Map the specific columns using the column_mapping dictionary
# your_data.rename(columns=column_mapping, inplace=True)

# df = your_data


# Rename the columns as needed
df.rename(columns={"Duration_Days": "time", "Status": "status"}, inplace=True)


# Create X and y
X = df.drop(
    ["time", "status", "Patient_ID"], axis=1
)  # Exclude 'Duration_Days' and 'Status' from X
print("X shape:", X.shape)
y = df[["time", "status"]]  # Use 'Duration_Days' and 'Status' as y
print(y)


# check for missing values, from most missing to least missing columns:
s = X.isna().sum()
s = s[s != 0].sort_values(ascending=False)
print(s)  # should be an empty list


df["time"] = df["time"].astype(int)


# Divide the features into continuous and categorical
scaling_cols = [c for c in X.columns if X[c].dtype.kind in ["i", "f"]]
cat_cols = [c for c in X.columns if X[c].dtype.kind not in ["i", "f"]]


preprocessor = ColumnTransformer(
    [
        ("cat-preprocessor", OrdinalEncoder(), cat_cols),
        ("standard-scaler", StandardScaler(), scaling_cols),
    ],
    remainder="passthrough",
    sparse_threshold=0,
)

# Define the number of splits and create a GroupKFold object
n_splits = 5
group_kfold = GroupKFold(n_splits=n_splits)
groups = df["Patient_ID"]


# Define functions for each model pipeline
def coxph_model(X, y, groups):
    c_index = []

    for train_index, test_index in group_kfold.split(X, y, groups=groups):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

        # Create the CoxPHSurvivalAnalysis pipeline with preprocessing
        cox = make_pipeline(preprocessor, CoxPHSurvivalAnalysis(alpha=0.01))

        # Combine 'status' and 'time' into a structured array
        y_train = np.array(
            [(s, t) for s, t in zip(y_train["status"].astype(bool), y_train["time"])],
            dtype=[("status", bool), ("time", "float32")],
        )

        # Fit the CoxPH model
        cox.fit(X_train, y_train)

        # Predict on the test set
        y_pred = cox.predict(X_test)

        # Calculate the concordance index
        c_index.append(
            concordance_index_censored(
                y_test["status"].astype("bool"), y_test["time"], y_pred
            )[0]
        )

    return c_index


def rsf_model(X, y, groups):
    c_index = []

    for train_index, test_index in group_kfold.split(X, y, groups=groups):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

        # Create the RandomSurvivalForest pipeline with preprocessing
        rsf = make_pipeline(preprocessor, RandomSurvivalForest(random_state=42))

        # Combine 'status' and 'time' into a structured array
        y_train = np.array(
            [(s, t) for s, t in zip(y_train["status"].astype(bool), y_train["time"])],
            dtype=[("status", bool), ("time", "float32")],
        )

        # Fit the RSF model
        rsf.fit(X_train, y_train)

        # Predict on the test set
        y_pred = rsf.predict(X_test)

        # Calculate the concordance index
        c_index.append(
            concordance_index_censored(
                y_test["status"].astype("bool"), y_test["time"], y_pred
            )[0]
        )

    return c_index


def survival_xgboost_model(X, y, groups):
    c_index = []

    for train_index, test_index in group_kfold.split(X, y, groups=groups):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        y_train_xgb = np.where(y_train["status"] == 1, y_train["time"], -y_train["time"])
        y_test_xgb = np.where(y_test["status"] == 1, y_test["time"], -y_test["time"])
        xgb_train = xgboost.DMatrix(X_train, label=y_train_xgb)
        xgb_test = xgboost.DMatrix(X_test, label=y_test_xgb)

        params = {
            "eta": 0.002,
            "max_depth": 3,
            "objective": "survival:cox",
            "subsample": 0.5,
        }

        def c_statistic_harrell(pred, labels):
            total = 0
            matches = 0
            for i in range(len(labels)):
                for j in range(len(labels)):
                    if labels[j] > 0 and abs(labels[i]) > labels[j]:
                        total += 1
                        if pred[j] > pred[i]:
                            matches += 1

            # Check if total is zero to avoid division by zero
            if total == 0:
                return 0.0

            return matches / total

        xgb_model = xgboost.train(
            params, xgb_train, 5000, evals=[(xgb_test, "test")], verbose_eval=500
        )
        y_pred = xgb_model.predict(xgb_test, ntree_limit=5000)

        c_index.append(c_statistic_harrell(np.array(y_pred), y_test_xgb))

    return c_index


# Call each model function and store the results
coxph_results = coxph_model(X, y, groups)
rsf_results = rsf_model(X, y, groups)
xgboost_results = survival_xgboost_model(X, y, groups)

# Print or save the results for each model
print("CoxPH Results:", coxph_results)
print("Random Survival Forest Results:", rsf_results)
print("Survival XGBoost Results:", xgboost_results)

# Calculate and print the average c-index for each model
coxph_average_c_index = np.array(coxph_results).mean()
rsf_average_c_index = np.array(rsf_results).mean()
xgboost_average_c_index = np.array(xgboost_results).mean()

print("Average c-index (CoxPH):", coxph_average_c_index)
print("Average c-index (Random Survival Forest):", rsf_average_c_index)
print("Average c-index (XGBoost):", xgboost_average_c_index)
