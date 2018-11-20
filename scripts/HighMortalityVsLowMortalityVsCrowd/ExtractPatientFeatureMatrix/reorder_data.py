import pandas as pd

# Goal: to ensure that only the last recorded admission's data is used for a given patient id
# Note: the raw patient feature tables include data recorded from ALL encounters; we only want to consider the LAST encounter

# 2008-2009 data
dataset_8_9 = "/Users/jwang/Desktop/Results/2008-2009_patient_feature_matrix.tab"
df_8_9 = pd.read_csv(dataset_8_9, sep="\t")
df_8_9 = df_8_9.sort_values(['patient_id', 'edAdmitTime', 'dischargeTime'], ascending=[0,0,0])

df_8_9.to_csv("/Users/jwang/Desktop/Results/2008-2009_patient_feature_matrix_reordered.csv", sep=",", index=False)

# 2010-2013 data
dataset_10_13 = "/Users/jwang/Desktop/Results/2010-2013_patient_feature_matrix.tab"
df_10_13 = pd.read_csv(dataset_10_13, sep="\t")
df_10_13 = df_10_13.sort_values(['patient_id', 'edAdmitTime', 'dischargeTime'], ascending=[0,0,0])

df_10_13.to_csv("/Users/jwang/Desktop/Results/2010-2013_patient_feature_matrix_reordered.csv", sep=",", index=False)