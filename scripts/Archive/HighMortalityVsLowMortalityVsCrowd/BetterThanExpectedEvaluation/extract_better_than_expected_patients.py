import sys
from datetime import datetime
import pandas
from dateutil import parser
###########################################################################################################################################
# Extract "better than expected" patient cases that are not included in balanced patient cohorts inputted for association model training  #
###########################################################################################################################################

# Exclude patients inputted in association model training
low_mortality_patients = open("/Users/jwang/Desktop/Chen/Top_vs_Bottom_Study/Results_Preliminary/Results/top_patients_matched_remapped.csv", "rU")
high_mortality_patients = open("/Users/jwang/Desktop/Chen/Top_vs_Bottom_Study/Results_Preliminary/Results/bottom_patients_matched_remapped.csv", "rU")
crowd_patients = open("/Users/jwang/Desktop/Chen/Top_vs_Bottom_Study/Results_Preliminary/Results/everyone_patients_matched_remapped.csv", "rU")

exclude_patients = {}
for line in low_mortality_patients:
	patient_id = int(line.strip())
	exclude_patients[patient_id] = 1
low_mortality_patients.close()

for line in high_mortality_patients:
	patient_id = int(line.strip())
	exclude_patients[patient_id] = 1
high_mortality_patients.close()

for line in crowd_patients:
	patient_id = int(line.strip())
	exclude_patients[patient_id] = 1
crowd_patients.close()

# print(len(exclude_patients.keys()))

# Identify patients that turned out "better than expected" based on pre-defined thresholds
# Better than expected patient case: mortality prob > threshold (high risk) but mortality delta > threshold (good outcome)
prob_threshold = 0.50
delta_threshold = 30 # pandas.Timedelta(days=30)

inf = open("joined_probs_mortality_delta_spreadsheet.csv", "rU")
inf.readline()

better_than_expected_patients = {}
for line in inf:
	line = line.strip().split(",")
	delta = line[2]
	if (delta == "N/A"):
		continue # no mortality data
	else:
		delta = int(delta.strip().split(" ")[0]) # extract days
	patient_id = int(line[0])
	mortality_prob = float(line[1])

	if (mortality_prob > prob_threshold and delta > delta_threshold):
		# exclude patients from balanced patient cohorts inputted into association models
		if (patient_id not in list(exclude_patients.keys())):
			better_than_expected_patients[patient_id] = 1
inf.close()

print("Better than expected patient cases: {0}".format(len(list(better_than_expected_patients.keys()))))

# Output better than expected patient list
outf = open("better_than_expected_patients.csv", "w")
for patient_id in list(better_than_expected_patients.keys()):
	outf.write("{0}\n".format(patient_id))
outf.close()



