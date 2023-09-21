import numpy as np
import pandas as pd

# Set random seed for reproducibility
np.random.seed(0)

# Number of patients
num_patients = 1000

# Generate synthetic patient IDs
patient_ids = np.arange(1, num_patients + 1)

# Generate random demographic data
age = np.random.randint(18, 90, size=num_patients)

# Generate gender features as binary values (0 or 1)
gender_F = np.random.randint(0, 2, size=num_patients)
gender_M = 1 - gender_F  # Complement to ensure either F or M

# Generate random race features as binary values (0 or 1) for each patient
num_races = 12
race_columns = [f"Race{i}" for i in range(1, num_races + 1)]
race_data = np.zeros((num_patients, num_races))

# Assign a random race to each patient
for i in range(num_patients):
    random_race_index = np.random.randint(0, num_races)
    race_data[i, random_race_index] = 1

# Generate 189 random numeric features
num_features = 189
numeric_features = np.random.randn(num_patients, num_features)

# Calculate the duration and status based on the condition you provided
duration = np.random.randint(
    1, 365, size=num_patients
)  # Random duration between 1 and 364 days
status = np.where(duration > 180, 0, 1)

# Create a DataFrame
data = pd.DataFrame(
    {
        "Patient_ID": patient_ids,
        "Age": age,
        "Gender_F": gender_F,
        "Gender_M": gender_M,
        **{race_column: race_data[:, i] for i, race_column in enumerate(race_columns)},
        **{str(i): numeric_features[:, i - 3] for i in range(3, num_features + 3)},
        "Duration_Days": duration,
        "Status": status,
    }
)

# Save the data to the specified CSV file path
data.to_csv("synthetic_survival_data.csv", index=False)
