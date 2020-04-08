import numpy as np
import pandas as pd

dataset_flag = "10-13"
# dataset_flag = "8-9"

full_dataset = "N/A"
if (dataset_flag == "10-13"):
	full_dataset = open("/Users/jwang/Desktop/Results/2010-2013_patient_feature_matrix_reordered.csv", "rU")
else:
	full_dataset = open("/Users/jwang/Desktop/Results/2008-2009_patient_feature_matrix_reordered.csv", "rU")

header = full_dataset.readline()
header = header.strip().split(",")

# Read in last recorded admission diagnoses
last_recorded_diagnoses = {}
last_recorded_diagnoses_f = "N/A"
if (dataset_flag == "10-13"):
	last_recorded_diagnoses_f = "/Users/jwang/Desktop/Results/last_recorded_admission_diagnosis_10_13.csv"
else: 
	last_recorded_diagnoses_f = "/Users/jwang/Desktop/Results/last_recorded_admission_diagnosis_8_9.csv"

df = pd.read_csv(last_recorded_diagnoses_f, sep=",")
df = df[["patient_id","clinical_item_id"]]
df = pd.get_dummies(df, columns=["clinical_item_id"])
admission_header = list(df)[1:]

for index, row in df.iterrows():
	row = list(map(str,list(row)))
	last_recorded_diagnoses[row[0]] = ",".join(row[1:])
	
# Read in death data (7 day mortalities)
death_data_7 = open("/Users/jwang/Desktop/Results/7_day_deaths.csv", "rU")
id_to_death_7 = {}
death_data_7.readline()
for line in death_data_7:
	line = line.strip().split(",")
	# if (line[1] == "None"): # survived
	# 	id_to_death[line[0]] = "survived"
	# else: # died
	# 	id_to_death[line[0]] = "died"
	id_to_death_7[line[0]] = 1

# Read in death data (30 day mortalities)
death_data_30 = open("/Users/jwang/Desktop/Results/30_day_deaths.csv", "rU")
id_to_death_30 = {}
death_data_30.readline()
for line in death_data_30:
	line = line.strip().split(",")
	id_to_death_30[line[0]] = 1

# Read in death data (90 day mortalities)
death_data_90 = open("/Users/jwang/Desktop/Results/90_day_deaths.csv", "rU")
id_to_death_90 = {}
death_data_90.readline()
for line in death_data_90:
	line = line.strip().split(",")
	id_to_death_90[line[0]] = 1

# Read in 30 day readmission data
readmission_data_30 = open("/Users/jwang/Desktop/Results/30_day_readmissions.csv", "rU")
id_to_readmission_30 = {}
readmission_data_30.readline()
for line in readmission_data_30:
	line = line.strip().split(",")
	id_to_readmission_30[line[0]] = 1

# Read in lengths of stay (not necessary?)

# Read in income data
income_data = open("/Users/jwang/Desktop/Results/income_based_on_zip.csv", "rU")
id_to_income = {}
income_data.readline()
for line in income_data:
	line = line.strip().split(",")
	income_bin = "None"
	if (line[1] == ">200000"):
		income_bin = 20
	elif (line[1] == "<20000"):
		income_bin = 1
	elif (len(line[1]) > 1):
		income_range = line[1].strip().split("-")
		income_floor = int(income_range[0])
		income_bin = income_floor//10000
	id_to_income[line[0]] = str(income_bin)

# Read in age data
age_data = open("/Users/jwang/Desktop/Results/ages.csv", "rU")
id_to_age = {}
age_data.readline()
for line in age_data:
	line = line.strip().split(",")
	# age_bin = "None"
	if (line[1] != "None"):
		age = int(line[1])
		# if (age < 18):
		# 	age_bin = 0
		# elif (age < 26):
		# 	age_bin = 1
		# elif (age < 36):
		# 	age_bin = 2
		# elif (age < 46):
		# 	age_bin = 3
		# elif (age < 56):
		# 	age_bin = 4
		# elif (age < 66):
		# 	age_bin = 5
		# else: # age >= 66
		# 	age_bin = 6
	
	# id_to_age[line[0]] = str(age_bin)
	id_to_age[line[0]] = str(age)

# Identify relevant data columns
ignore = ['IVAntibiotic.pre', 'BloodCulture.pre', 'RespViralPanel.pre', 'AnyICULifeSupport.pre', 'AnyDNR.pre', 'AnyVasoactive.pre', 'AnyCRRT.pre', 'AnyVentilator.pre', 'ComfortCare.pre', 'PalliativeConsult.pre', "TBIL.first", "ALB.first", "LAC.first", "ESR.first", "CRP.first", "TNI.first", "PHA.first", "PO2A.first", "PCO2A.first", "PHV.first", "PO2V.first", "PCO2V.first", "Birth.pre", "Death.pre"]
relevant_cols = ["patient_id", "dischargeTime", "edAdmitTime", "encounter_id"]
for col in header:
	#if ("first" in col or "pre" in col) and "preTime" not in col and "TT" not in col and col not in ignore: 
	if ("first" in col or "pre" in col) and "preTime" not in col and col not in ignore: # include treatment team
		relevant_cols.append(col) 

relevant_indices = []
for col in relevant_cols:
	relevant_indices.append(header.index(col))
relevant_cols.append("income_level")
relevant_cols.append("age")
relevant_cols.extend(admission_header)

# outcomes
relevant_cols.append("death_7")
relevant_cols.append("death_30")
relevant_cols.append("death_90")
relevant_cols.append("readmission_30")
relevant_cols.append("readmission_or_death_30")

# Print out to csv format
output = "N/A"
if (dataset_flag == "10-13"):
	output = open("/Users/jwang/Desktop/Results/2010-2013_patient_feature_matrix.csv", "w")
else:
	output = open("/Users/jwang/Desktop/Results/2008-2009_patient_feature_matrix.csv", "w")
patient_ids = {} # ensure uniqueness

# NOTE: we are reading in data associated with the first time we see a patient_id; this, by design, is the last recorded encounter

output.write("normalized_patient_id,")
output.write(",".join(relevant_cols))
output.write("\n")

normalized_patient_id = 1
for line in full_dataset:
	line = line.strip().split(",")
	admit_year = line[4][:4]
	discharge_year = line[3][:4]

	year_range = []
	if (dataset_flag == "10-13"):
		year_range = ["2010","2011","2012","2013"]
	else: # 2008-2009
		year_range = ["2008","2009"]
	# if (line[0] not in patient_ids) and (admit_year in ["2010","2011","2012","2013"] or discharge_year in ["2010","2011","2012","2013"]):
	# if (line[0] not in patient_ids) and (admit_year in ["2008","2009"] or discharge_year in ["2008","2009"]):
	if (line[0] not in patient_ids) and (admit_year in year_range or discharge_year in year_range):

		patient_ids[line[0]] = 1
		line = np.array(line)
		output.write(str(normalized_patient_id)+",")
		output.write(",".join(list(line[relevant_indices])))

		output.write("," + id_to_income[line[0]])
		output.write("," + id_to_age[line[0]])

		if (line[0] in last_recorded_diagnoses):
			output.write("," + last_recorded_diagnoses[line[0]])
		else:
			output.write("," + "0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")

		if (line[0] in id_to_death_7):
			output.write("," + "died")
		else:
			output.write("," + "survived")

		if (line[0] in id_to_death_30):
			output.write("," + "died")
		else:
			output.write("," + "survived")

		if (line[0] in id_to_death_90):
			output.write("," + "died")
		else:
			output.write("," + "survived")

		if (line[0] in id_to_readmission_30):
			output.write("," + "yes")
		else:
			output.write("," + "no")

		if (line[0] in id_to_readmission_30 or line[0] in id_to_death_30):
			output.write("," + "yes")
		else:
			output.write("," + "no")

		output.write("\n")
		normalized_patient_id += 1

	else:
		pass
