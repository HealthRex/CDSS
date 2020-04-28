# 1) Extract all patients associated with top and bottom performing clinician cohorts
# 2) Create csv feature matrices for unmatched patient cohorts in preparation for matching

# Extract clinician cohorts (top, bottom, everyone)
print("Assembling top and bottom physician cohorts...")
performance_scores = open("/Users/jwang/Desktop/Results/mortality_observed_vs_expected.csv", "rU")
header = performance_scores.readline()
top_clinicians = {} 
bottom_clinicians = {}
all_clinicians = {}

for physician in performance_scores:
	physician = physician.strip().split(",")
	score = float(physician[9])
	if (score > 0): # high performer
		top_clinicians[physician[0]] = score
	elif (score < 0): # low performer
		bottom_clinicians[physician[0]] = score

	# all clinicians are included regardless of score in the "everyone" cohort
	all_clinicians[physician[0]] = score
performance_scores.close()
print(len(top_clinicians), len(bottom_clinicians))

# Load in physician-patient map
physician_specialties = {}
print("Assembling top and bottom patient cohorts...")
physician_patient_map = open("/Users/jwang/Desktop/Results/physician_patient_map_hp.csv", "rU")
physician_patient_map.readline()
top_cohort = {} 
bottom_cohort = {}
all_cohort = {}
# Identify patients associated with top, bottom, and everyone clinician cohorts 
for line in physician_patient_map:
	line = line.strip().split(",")
	physician = line[0]
	physician_specialties[physician] = line[5]
	if (physician in top_clinicians):
		top_cohort[line[1]] = 1
	elif (physician in bottom_clinicians):
		bottom_cohort[line[1]] = 1

	# all clinicians (and associated patients) are considered in "everyone" cohort
	all_cohort[line[1]] = 1
physician_patient_map.close()
print(len(top_cohort), len(bottom_cohort), len(all_cohort))

# Assemble feature matrices for top and bottom patient cohorts
# Note: this only keeps patients seen in 2010-2013
print("Writing out top and bottom patient feature matrices...")
feature_matrix = open("/Users/jwang/Desktop/Results/2010-2013_patient_feature_matrix.csv", "rU")
top_matrix = open("/Users/jwang/Desktop/Results/2010-2013_unmatched_patient_feature_matrix_top_performing.csv", "w")
bottom_matrix = open("/Users/jwang/Desktop/Results/2010-2013_unmatched_patient_feature_matrix_bottom_performing.csv", "w")
all_cohort_f = open("/Users/jwang/Desktop/Results/all_patients.csv", "w")

header = feature_matrix.readline()
top_matrix.write(header)
bottom_matrix.write(header)

top_count = 0
bottom_count = 0
overlap = {}
for patient in feature_matrix:
	line = patient # raw line
	patient = patient.strip().split(",")
	patient_id = patient[1]

	if (patient_id in all_cohort):
		all_cohort_f.write(patient_id + "\n")

	# exclude overlapping patients; keep only patients uniquely associated wtih one cohort
	if (patient_id in top_cohort and patient_id in bottom_cohort):
		overlap[patient_id] = 1
		continue
	elif (patient_id in top_cohort):
		top_matrix.write(line)
		top_count += 1
	elif (patient_id in bottom_cohort):
		bottom_matrix.write(line)
		bottom_count += 1

feature_matrix.close()
top_matrix.close()
bottom_matrix.close()
all_cohort_f.close()
print(top_count, bottom_count)
print(len(overlap))

# Analyze patients that are duplicate/overlapping
print("Analyzing duplicate/overlap patients between top and bottom patient cohorts...")
overlap_map_top = {} # key = patient_id, value = array of physicians that wrote a H&P note in top cohort
overlap_map_bottom = {} # key = patient_id, value = array of physicians that wrote a H&P note in bottom cohort

physician_patient_map = open("/Users/jwang/Desktop/Results/physician_patient_map_hp.csv", "rU")
physician_patient_map.readline()
for line in physician_patient_map:
	line = line.strip().split(",")
	physician = line[0]
	patient_id = line[1]
	if (patient_id in overlap): 
		if (physician in top_clinicians):

			if (patient_id not in overlap_map_top): # not yet in overlap_map
				overlap_map_top[patient_id] = [physician]
			else: # already in overlap_map_top
				overlap_map_top[patient_id].append(physician)

		elif (physician in bottom_clinicians):

			if (patient_id not in overlap_map_bottom): # not yet in overlap_map
				overlap_map_bottom[patient_id] = [physician]
			else: # already in overlap_map_bottom
				overlap_map_bottom[patient_id].append(physician)

overlap_outf = open("/Users/jwang/Desktop/Results/duplicate_patients.csv", "w")
overlap_outf.write("patient_id,physician,physician speciality,physician cohort\n")
# iterate through all duplicate patients
for patient_id, top_physicians in overlap_map_top.items():
	for physician in top_physicians:
		overlap_outf.write("{0},{1},{2},top\n".format(patient_id,physician,physician_specialties[physician]))
	for physician in overlap_map_bottom[patient_id]:
		overlap_outf.write("{0},{1},{2},bottom\n".format(patient_id,physician,physician_specialties[physician]))
overlap_outf.close()
