import numpy as np

full_dataset = open("expert_matching_dataset_full.tab", "rU")
header = full_dataset.readline()
header = header.strip().split("\t")

# Read in income data
income_data = open("income_based_on_zip.csv", "rU")
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
age_data = open("ages.csv", "rU")
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
	if ("first" in col or "pre" in col) and "preTime" not in col and "TT" not in col and col not in ignore: 
		relevant_cols.append(col)

relevant_indices = []
for col in relevant_cols:
	relevant_indices.append(header.index(col))
relevant_cols.append("income_level")
relevant_cols.append("age")

# Print out to csv format
output = open("expert_2013only.csv", "w")
patient_ids = {} # ensure uniqueness

output.write("normalized_patient_id,")
output.write(",".join(relevant_cols))
output.write("\n")

normalized_patient_id = 1
for line in full_dataset:
	line = line.strip().split("\t")
	admit_year = line[4][:4]
	discharge_year = line[3][:4]
	if (line[0] not in patient_ids) and (admit_year == "2013" or discharge_year == "2013"):
		patient_ids[line[0]] = 1
		line = np.array(line)
		output.write(str(normalized_patient_id)+",")
		output.write(",".join(list(line[relevant_indices])))

		output.write("," + id_to_income[line[0]])
		output.write("," + id_to_age[line[0]])
		output.write("\n")

		normalized_patient_id += 1

	else:
		pass
