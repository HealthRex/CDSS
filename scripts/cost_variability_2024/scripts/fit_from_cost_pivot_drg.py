from google.cloud import bigquery
from google.cloud.bigquery import dbapi
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/grolleau/Desktop/github repos/Cost variability/json_credentials/grolleau_application_default_credentials.json'
os.environ['GCLOUD_PROJECT'] = 'som-nero-phi-jonc101'

# Instantiate a client object so you can make queries
client = bigquery.Client()

# Create a connexion to that client
conn = dbapi.connect(client)

pivot_drg_query = f"""
SELECT * FROM `som-nero-phi-jonc101.francois_db.cost_pivot_drg`
"""

df = pd.read_sql_query(pivot_drg_query, conn)

# explore missing values
no_drg = (df.iloc[:, 5:].apply(lambda x: (~x.isna()).sum(), axis=1) <= 0)
df[no_drg] # 7 observations have no DRG

# Fill zeros when DRG is NaN
df.iloc[:, 5:] = df.iloc[:, 5:].fillna(0)

X_imputed = np.array(df.iloc[:, 5:])

# Normalize the features
#X_imputed = (X_imputed - X_imputed.mean(axis=0)) / X_imputed.std(axis=0) Divivded by zero gives inf here

# Keep only the target
Y_name = "Cost_Total_Scaled"
Y = np.array(df[Y_name])

# Normalize the target
Y = (Y - Y.mean()) / Y.std()

##### FITTING THE MODEL #####

# Fit a Random Forest model
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
from sklearn.model_selection import cross_val_score
from scipy.stats import linregress

# Instantiate the Random Forest model
rf = RandomForestRegressor(n_estimators=1,  
                                   min_samples_split=2,  
                                   min_samples_leaf=1, 
                                   max_depth=None,  
                                   max_features='sqrt') 

#from sklearn.linear_model import LinearRegression
#rf = LinearRegression()

#from sklearn.linear_model import Lasso, LassoCV
#lasso_cv = LassoCV(alphas=[0.1, 0.01, 0.001, 0.0005, 0.0001], cv=5)
#lasso_cv.fit(X_imputed, Y)
#rf = lasso_model = Lasso(alpha=lasso_cv.alpha_)

# Fit the model to your data
rf.fit(X_imputed, Y)

# Predict on the training set
Y_pred = rf.predict(X_imputed)

# Calculate R^2 on the training set
r2_ori = r2_score(Y, Y_pred)

### Calibration plot

# Predict values using the model on the training dataset
Y_pred = rf.predict(X_imputed)

# Define the quantiles
quantiles = np.linspace(0, 1, 11)  # For quintiles

# Determine the bin edges based on quantiles of Y_pred
bin_edges = np.quantile(Y_pred, quantiles)[1:]

# Use digitize to assign each Y_pred to a bin
bins = np.digitize(Y_pred, bin_edges, right=True)

# Initialize lists for plotting
mean_predicted_ori = []
mean_actual_ori = []

# Calulate slope and intercept for the in-sample calibration curve
slope_ori, intercept_ori, _, _, _ = linregress(Y_pred, Y)

# Calculate mean actual and predicted values for each bin
for i in range(1, len(bin_edges)):
    bin_indices = bins == i
    if np.any(bin_indices):
        mean_predicted_ori.append(Y_pred[bin_indices].mean())
        mean_actual_ori.append(Y[bin_indices].mean())

# Plotting
plt.figure(figsize=(10, 10))

# Plot the perfect prediction line
plt.plot([min(mean_actual_ori), max(mean_actual_ori)],
         [min(mean_actual_ori), max(mean_actual_ori)], 
         color='red', linestyle='--', label='Perfect Calibration')

###
from sklearn.model_selection import KFold
kf = KFold(n_splits=10, shuffle=True, random_state=42)  # No. of folds here

r2_cv = []
slope_cv = []
intercept_cv = []

# Loop over each fold
for fold_i, (train_index, test_index) in enumerate(kf.split(X_imputed)):
    X_train, X_test = X_imputed[train_index], X_imputed[test_index]
    Y_train, Y_test = Y[train_index], Y[test_index]
    
    # Fit the model
    rf.fit(X_train, Y_train)
    
    # Predict on the test set
    Y_pred = rf.predict(X_test)
    
    # Calculate R^2 for the current fold
    r2 = r2_score(Y_test, Y_pred)
    r2_cv.append(r2)
    
    # Calulate slope and intercept for the cv calibration curves
    slope, intercept, _, _, _ = linregress(Y_pred, Y_test)
    slope_cv.append(slope)
    intercept_cv.append(intercept)
    
    # Use digitize to assign each Y_pred to a bin
    bins = np.digitize(Y_pred, bin_edges, right=True)
    
    mean_predicted = []
    mean_actual = []
    
    # Calculate mean actual and predicted values for each bin
    for i in range(1, len(bin_edges) + 1):
        bin_indices = bins == i
        if np.any(bin_indices):
            mean_predicted.append(Y_pred[bin_indices].mean())
            mean_actual.append(Y_test[bin_indices].mean())
    
    # Plot the calibration curve for the current fold
    plt.plot(mean_predicted, mean_actual, linestyle='-', color='gray', alpha=0.5)

# Plot the in-sample calibration curve
plt.plot(mean_predicted_ori, mean_actual_ori, color='blue', label='In sample', marker='o')

# Add labels for the legend
plt.plot([], [], linestyle='-', color='gray', alpha=0.5, label='CV Folds')

# Add text for the metric values
plt.text(x=0.02, y=0.875, s=f'In-sample', transform=plt.gca().transAxes, fontsize=12)
plt.text(x=0.03, y=0.85, s=f'$R^2$: {100*r2_ori:.1f}%', transform=plt.gca().transAxes, fontsize=12)
plt.text(x=0.03, y=0.825, s=f'Intercept: {intercept_ori:.2f}', transform=plt.gca().transAxes, fontsize=12)
plt.text(x=0.03, y=0.8, s=f'Slope: {slope_ori:.2f}', transform=plt.gca().transAxes, fontsize=12)

plt.text(x=0.02, y=0.75, s=f'CV', transform=plt.gca().transAxes, fontsize=12)
plt.text(x=0.03, y=0.725, s=f'$R^2$: {100*np.mean(r2_cv):.2f}%', transform=plt.gca().transAxes, fontsize=12)
plt.text(x=0.03, y=0.7, s=f'Intercept: {np.mean(intercept_cv):.2f}', transform=plt.gca().transAxes, fontsize=12)
plt.text(x=0.03, y=0.675, s=f'Slope: {np.mean(slope_cv):.2f}', transform=plt.gca().transAxes, fontsize=12)

plt.xlim([min(mean_actual_ori), max(mean_actual_ori)])
plt.ylim([min(mean_actual_ori), max(mean_actual_ori)])
plt.title(f"Predicting {Y_name} from DRGs in all hospitalizations (n={X_imputed.shape[0]})\nCross-Validated Calibration ({rf.__class__.__name__} model)")
plt.xlabel('Mean Predicted Cost')
plt.ylabel('Mean Observed Cost')
plt.legend()
plt.show()