import pandas as pd
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve
import pickle
import seaborn as sns
from sklearn.metrics import roc_curve, auc as roc_auc_score

# Set Seaborn style to 'white' which has no grid by default
sns.set_style("white")


# Load the test data and predictions for RF, LR, and XGB
test_rf = pd.read_csv("feature_matrix/test_set_sep4_2023_standard_rf.csv")
test_lr = pd.read_csv("feature_matrix/test_set_sep4_2023_standard_lr.csv")
test_xgb = pd.read_csv("feature_matrix/test_set_sep4_2023_standard_xgb.csv")


# Load the RF, LR, and XGB models
with open("saved_classical_ml_models/rf_model.pkl", "rb") as rf_model_file:
    rf_model = pickle.load(rf_model_file)

with open("saved_classical_ml_models/lr_model.pkl", "rb") as lr_model_file:
    lr_model = pickle.load(lr_model_file)

with open("saved_classical_ml_models/xgb_model.pkl", "rb") as xgb_model_file:
    xgb_model = pickle.load(xgb_model_file)

# Extract true labels from the test data
true_labels_rf = test_rf["outcome"]
true_labels_lr = test_lr["outcome"]
true_labels_xgb = test_xgb["outcome"]

non_feature_list = [
    "person_id",
    "drug_exposure_start_DATE",
    "TreatmentDuration",
    "outcome",
]

# Make predictions using the RF, LR, and XGB models
prob_rf = rf_model.predict_proba(test_rf.drop(columns=non_feature_list))[:, 1]
prob_lr = lr_model.predict_proba(test_lr.drop(columns=non_feature_list))[:, 1]
prob_xgb = xgb_model.predict_proba(test_xgb.drop(columns=non_feature_list))[:, 1]


# Calculate ROC curves for RF, LR, and XGB
fpr_rf, tpr_rf, _ = roc_curve(true_labels_rf, prob_rf)
roc_auc_rf = roc_auc_score(fpr_rf, tpr_rf)

fpr_lr, tpr_lr, _ = roc_curve(true_labels_lr, prob_lr)
roc_auc_lr = roc_auc_score(fpr_lr, tpr_lr)

fpr_xgb, tpr_xgb, _ = roc_curve(true_labels_xgb, prob_xgb)
roc_auc_xgb = roc_auc_score(fpr_xgb, tpr_xgb)


# Calculate calibration curves for RF, LR, and XGB
fraction_of_positives_rf, mean_predicted_value_rf = calibration_curve(
    true_labels_rf, prob_rf, n_bins=10
)
fraction_of_positives_lr, mean_predicted_value_lr = calibration_curve(
    true_labels_lr, prob_lr, n_bins=10
)
fraction_of_positives_xgb, mean_predicted_value_xgb = calibration_curve(
    true_labels_xgb, prob_xgb, n_bins=10
)

# Load clinicians' data and prepare it
latest_data = pd.read_excel("models/results.xlsx") #read clinicians result (saved as 0/1 with percentage)
latest_data = latest_data.rename(columns={"treatment_duration ": "treatment_duration"})
latest_data["true_label"] = (latest_data["treatment_duration"] <= 180).astype(int)
latest_data["percent"] = pd.to_numeric(latest_data["percent"], errors="coerce")

# Extract necessary columns for clinicians' analysis
true_labels_clinicians = latest_data["true_label"]
prediction_probabilities_clinicians = (
    latest_data["percent"] / 100
)  # Convert percentages to probabilities

# Calculate ROC curve for clinicians
fpr_clinicians, tpr_clinicians, _ = roc_curve(
    true_labels_clinicians, prediction_probabilities_clinicians
)
roc_auc_clinicians = roc_auc_score(fpr_clinicians, tpr_clinicians)

# Calculate calibration curve for clinicians
prob_true_clinicians, mean_pred_clinicians = calibration_curve(
    true_labels_clinicians, prediction_probabilities_clinicians, n_bins=10
)


# Set font sizes for the plots
plt.rcParams["font.size"] = 18  # Base font size
plt.rcParams["axes.labelsize"] = 20  # Font size for X and Y labels
plt.rcParams["axes.titlesize"] = 20  # Font size for the title
plt.rcParams["legend.fontsize"] = 20  # Font size for legends

# Define colors for each model
colors = {"Clinicians": "green", "XGB": "blue", "RF": "red", "LR": "lightgrey"}

# Plot both ROC and calibration curves side by side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))

# Plot ROC curves with consistent colors and styles
# Note: The order of plotting determines the order in the legend
ax1.plot(
    fpr_clinicians,
    tpr_clinicians,
    label=f"Clinicians (AUC = {roc_auc_clinicians:.2f})",
    color=colors["Clinicians"],
    lw=3,
)
ax1.plot(
    fpr_xgb,
    tpr_xgb,
    label=f"XGBoost (AUC = {roc_auc_xgb:.2f})",
    color=colors["XGB"],
    lw=2,
)
ax1.plot(
    fpr_rf,
    tpr_rf,
    label=f"Random Forest (AUC = {roc_auc_rf:.2f})",
    color=colors["RF"],
    lw=2,
)
ax1.plot(
    fpr_lr,
    tpr_lr,
    label=f"Logistic Regression (AUC = {roc_auc_lr:.2f})",
    color=colors["LR"],
    linestyle="dashed",
    lw=2,
)
ax1.plot([0, 1], [0, 1], color="gray", linestyle="--", lw=2)
ax1.set_xlabel("False Positive Rate")
ax1.set_ylabel("True Positive Rate")
ax1.set_title("ROC Curves for Clinicians, XGBoost, RF, and LR")
ax1.legend(loc="lower right", fontsize=20)

#  Set black outer border for ROC curve plot
for spine in ax1.spines.values():
    spine.set_edgecolor("black")

# Set black legend border for ROC curve plot
legend = ax1.legend(loc="lower right", fontsize=20)
legend.get_frame().set_edgecolor("black")


# Plot calibration curves with consistent colors and styles
ax2.plot(
    mean_pred_clinicians,
    prob_true_clinicians,
    marker="v",
    label="Clinicians",
    color=colors["Clinicians"],
    lw=2,
)
ax2.plot(
    mean_predicted_value_xgb,
    fraction_of_positives_xgb,
    marker="^",
    label="XGB",
    color=colors["XGB"],
    lw=2,
)
ax2.plot(
    mean_predicted_value_rf,
    fraction_of_positives_rf,
    marker="o",
    label="RF",
    color=colors["RF"],
    lw=2,
)
ax2.plot(
    mean_predicted_value_lr,
    fraction_of_positives_lr,
    marker="s",
    label="LR",
    color=colors["LR"],
    lw=2,
)
ax2.plot([0, 1], [0, 1], linestyle="--", color="gray", lw=2)
ax2.set_xlabel("Mean Predicted Value")
ax2.set_ylabel("Fraction of Positives")
ax2.set_title("Calibration Curves for Clinicians, XGBoost, RF, and LR")
ax2.legend(loc="lower right", fontsize=20)


# Set black outer border for calibration curve plot
for spine in ax2.spines.values():
    spine.set_edgecolor("black")

# Set black legend border for calibration curve plot
legend = ax2.legend(loc="lower right", fontsize=20)
legend.get_frame().set_edgecolor("black")

plt.tight_layout()

# Save the figure in high quality
plt.savefig("combined_roc_calibration_curves.png", format="png", dpi=600)

plt.show()
