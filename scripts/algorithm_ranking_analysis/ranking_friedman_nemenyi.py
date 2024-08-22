######################### Import Necessary Libraries ########################
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon, friedmanchisquare, rankdata
from Orange.evaluation import compute_CD, graph_ranks
import matplotlib.pyplot as plt

########################### Load and Preprocess Data #########################
# Load your data from a CSV file. Replace 'AUC.csv' with your file path.
# The data should contain columns for the dataset identifier and performance metrics.
# The first column should be the dataset names and the other columns should be algorithm performances.

file_path = "your_file.csv"  # Update this path
performances = pd.read_csv(file_path)

# Extract algorithm names (assuming the first column is 'Dataset')
algorithms_names = performances.columns[1:]

############################## Perform Friedman Test #########################
# Rank the performances for each dataset
ranks = performances.drop('Dataset', axis=1).apply(rankdata, axis=1)

# Compute the average ranks for each algorithm
average_ranks = ranks.mean(axis=0)

# Perform Friedman test
statistic, p_value = friedmanchisquare(*performances.drop('Dataset', axis=1).values.T)

print(f"Friedman statistic: {statistic}")
print(f"P-value: {p_value}")

########################## Nemenyi Post-Hoc Test #############################
# Compute critical difference (CD) for Nemenyi test
# Set n to the number of datasets and alpha to your significance level (0.05 or 0.1)
n_datasets = len(performances)
cd = compute_CD(average_ranks, n=n_datasets, alpha="0.1", test="nemenyi")

# Generate and save the plot
graph_ranks(average_ranks, names=algorithms_names, cd=cd, width=8, textspace=1.5)
plt.savefig("ranking.pdf")  # Save the plot as a PDF file

print(f"Critical Difference (CD): {cd}")
