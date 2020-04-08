import pandas as pd
import scipy.stats
import math
####################
### Load in Data ###
####################

# Load in physician cohorts based on H&P notes
physician_hp = open("/Users/jwang/Desktop/Results/physician_patient_map_hp.csv", "rU")
cohorts_hp = {}
full_cohorts = {}

physician_hp.readline()
for line in physician_hp:
	line = line.strip().split(",")
	physician = line[0]
	if (physician in cohorts_hp):
		cohorts_hp[physician].append( (line[1], line[2], line[6]) ) # (patient_id, H&P note_time, encounter_id)
	else:
		cohorts_hp[physician] = [ (line[1], line[2], line[6]), ]

# Load in physician cohorts based on Discharge Summaries
physician_discharge = open("/Users/jwang/Desktop/Results/physician_patient_map_discharge.csv", "rU")
cohorts_discharge = {}

physician_discharge.readline()
for line in physician_discharge:
	line = line.strip().split(",")
	physician = line[0]
	if (physician in cohorts_discharge):
		cohorts_discharge[physician].append( (line[1], line[2], line[6]) ) # key = physician, value = (patient_id, discharge note_time, encounter_id)
	else:
		cohorts_discharge[physician] = [ (line[1], line[2], line[6]), ] 

# Combine to create unique list/cohort of patients per physician (union between H&P and discharge cohorts)
cohorts_full = {} # key = physician, value = list of patient ids
patient_lists = {} # key = physician, value = list of (patient_id, note_time) tuples

for physician, patients in cohorts_hp.items(): # corresponds to potential mortality
	cohort_list = []
	pat_list = [] 
	for (pat_id, note_time, encounter_id) in patients:
		cohort_list.append( (pat_id, note_time, encounter_id) )
		pat_list.append(pat_id)
	cohorts_full[physician] = cohort_list
	patient_lists[physician] = pat_list

for physician, patients in cohorts_discharge.items(): # corresponds to potential readmission
	if (physician not in full_cohorts):
		cohort_list = []
		pat_list = [] 
		for (pat_id, note_time, encounter_id) in patients:
			cohort_list.append( (pat_id, note_time, encounter_id) )
			pat_list.append(pat_id)
		cohorts_full[physician] = cohort_list
		patient_lists[physician] = pat_list

	else: # append additional unique patients
		for (pat_id, note_time, encounter_id) in patients:
			if (pat_id not in patient_lists[physician]): # not yet in physician's patient list
				cohorts_full[physician].append( (pat_id, note_time, encounter_id) )
				patient_lists[physician].append(pat_id) 
				#union = list(set(patients) | set(full_cohorts[physician])) # union between discharge and H&P cohorts

# Load in patients that died within 30 days of an admission order
mortality_30 = open("/Users/jwang/Desktop/Results/30_day_deaths.csv", "rU")
mortality_map = {} # key = patient_id, value = last recorded admission time
for line in mortality_30:
	line = line.strip().split(",")
	mortality_map[line[0]] = line[1] 

# Load in patient's that were readmitted within 30 days of a discharge order
readmission_30 = open("/Users/jwang/Desktop/Results/30_day_readmissions.csv", "rU")
readmission_map = {} # key = patient_id, value = (previous discharge time, previous encounter_id)
for line in readmission_30:
	line = line.strip().split(",")
	readmission_map[line[0]] = (line[1], line[2])

#########################################
### Observed Mortality OR Readmission ###
#########################################
# Compute observed mortality OR readmission = number of patients who died within 30 days of admission OR were readmitted within 30 days of a discharge/total patients seen based on H&P and Discharge Summary notes

#initialize map with all physician names
observed = {} # key = physician, value = (dead or readmitted patients/total patients seen)
for physician in list(cohorts_full.keys()):
	observed[physician] = (0, len(cohorts_full[physician]))

for physician, patients in cohorts_full.items():
	for (pat_id, note_time, encounter_id) in patients: # iterate through all patients that physician is responsible for based on H&P or discharge note

		if (pat_id in mortality_map): # patient died within 30 days of an admission; found from H&P note

			# Q: Is this physician responsible? If this physician signed the H&P note associated with patient's last admission
			delta = pd.to_datetime(note_time) - pd.to_datetime(mortality_map[pat_id])
			if (delta >= pd.to_timedelta("0 days 00:00:00")): # this physician was responsible for this patient right before death
				observed[physician] = (observed[physician][0]+1,observed[physician][1])

		elif (pat_id in readmission_map): # patient was readmitted within 30 days of a discharge; found from Discharge Summary note

			# Q: Is this physician responsible? If physician signed discharge summary associated with patient's discharge before subsequent readmission
			#delta = pd.to_datetime(note_time) - pd.to_datetime(readmission_map[pat_id])
			#past_threshold = pd.to_timedelta("-1 days 00:00:00")
			#future_threshold = pd.to_timedelta("1 days 00:00:00")
			#if (delta >= past_threshold and delta <= future_threshold): # signed within 24 hours of patient's official discharge order or if encounter ids match

			patient_encounter_id = readmission_map[pat_id][1]
			if (encounter_id == patient_encounter_id): # physician's encounter id associated with discharge summary matches patient's encounter id associated with their discharge right before the <= 30 day readmission
				observed[physician] = (observed[physician][0]+1,observed[physician][1])

# perform division (save number of observed mortalities)
# NOTE: dead_or_re = "dead or readmitted"
observed_number = {}
for physician, (dead_or_re, total) in observed.items():
	observed[physician] = float(dead_or_re)/total
	observed_number[physician] = int(dead_or_re)

##########################
### Expected Mortality ###
##########################

# Expected mortality or readmission = average probability of patients in physician cohort dying within 30 days of an admission or being readmitted within 30 days of a discharge

#initialize map with all physician names
expected = {} # key = physician, value = (dead or readmitted patients/total patients seen)
for physician in list(cohorts_full.keys()):
	expected[physician] = (0, len(cohorts_full[physician]))

# Read in expected mortality/readmission union probability 
dead_or_re_probs = {} # key = patient_id, value = probability of dying within 30 days
dead_or_re_probs_f = open("/Users/jwang/Desktop/Results/mortality_or_readmission_probs_remapped.csv", "rU")
dead_or_re_probs_f.readline()
for line in dead_or_re_probs_f:
	line = line.strip().split(",")
	dead_or_re_probs[line[0]] = float(line[1])

# Find average probability of 30 day mortality/readmission for patients in cohort
for physician, patients in cohorts_full.items():
	for (pat_id, note_time, encounter_id) in patients:
		if (pat_id not in dead_or_re_probs):
			continue # assume patient without missing probability of death/readmission maintains same as average probability for physician's cohort

		if (physician in expected):
			expected[physician] = (float(expected[physician][0])+dead_or_re_probs[pat_id], expected[physician][1]+1)
		else: # not yet in the dictionary
			expected[physician] = (dead_or_re_probs[pat_id], 1)

# Perform division
for physician, (prob_sum, total) in expected.items():
	expected[physician] = float(prob_sum)/total

############################
### Print/Compute Scores ###
############################

# Write out observed and expected probabilities to CSV
outf = open("/Users/jwang/Desktop/Results/mortalityORreadmission_observed_vs_expected.csv", "w")
outf.write("physician,observed_combined_rate,expected_combined_rate,total_patients,observed_deadORreadmitted,observed_healthy,expected_deadORreadmitted,expected_healthy,p-value,score\n")
for physician in list(cohorts_full.keys()):

	# Compute Fisher Exact Test
	cohort_size = len(cohorts_full[physician])
	observed_deadORreadmitted = observed_number[physician]
	observed_healthy = cohort_size - observed_deadORreadmitted
	expected_deadORreadmitted = round(expected[physician]*cohort_size)
	expected_healthy = cohort_size - expected_deadORreadmitted
	contingency_table = [ [observed_deadORreadmitted, observed_healthy], [expected_deadORreadmitted, expected_healthy] ]
	odds_ratio, p_value = scipy.stats.fisher_exact(contingency_table, alternative="two-sided") # observed_deadORreadmitted, observed_healthy | expected_deadORreadmitted, expected_healthy

	# Two-Sided
	score = -1*math.log10(p_value) # base 10 logarithm
	if (observed_deadORreadmitted > expected_deadORreadmitted): # more patients died than were expected
		score = -1*score

	outf.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}\n".format(physician,observed[physician],expected[physician],cohort_size,
		observed_deadORreadmitted,observed_healthy,expected_deadORreadmitted,expected_healthy,p_value,score))
outf.close()
