import shap
import numpy as np
import pandas as pd
import matplotlib
from sklearn.datasets import load_diabetes
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Load the Diabetes Dataset
diabetes = load_diabetes()
X = pd.DataFrame(diabetes.data, columns=diabetes.feature_names)
y = pd.Series(diabetes.target, name='target')

# Split the Data into Training and Testing Sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a RandomForest Regressor
reg = RandomForestRegressor(n_estimators=100, random_state=42)
reg.fit(X_train, y_train)

# Initialize JavaScript visualization code for SHAP
shap.initjs()

# Explain the Model's Predictions using SHAP values
explainer = shap.TreeExplainer(reg)
shap_values = explainer.shap_values(X_test)

# Visualize the SHAP values for a Single Prediction
shap.force_plot(explainer.expected_value, shap_values[0], X_test.iloc[0])

# Visualize the SHAP values for All Features against All Samples
shap.summary_plot(shap_values, X_test)