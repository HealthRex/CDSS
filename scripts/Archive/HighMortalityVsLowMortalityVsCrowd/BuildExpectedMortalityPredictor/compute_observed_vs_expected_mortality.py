import pandas as pd
import scipy.stats
import math
##########################
### Observed Mortality ###
##########################

# Load in physician cohorts based on H&P notes
physician_hp = open("/Users/jwang/Desktop/Results/physician_patient_map_hp.csv", "rU")
physician_cohorts = {}

physician_hp.readline()
for line in physician_hp:
	line = line.strip().split(",")
	physician = line[0]
	if (physician in physician_cohorts):
		physician_cohorts[physician].append( (line[1], line[2]) ) # (patient_id, H&P note_time)
	else:
		physician_cohorts[physician] = [ (line[1], line[2]), ]

# Load in patient's that died within 30 days of an admission order
mortality_30 = open("/Users/jwang/Desktop/Results/30_day_deaths.csv", "rU")
mortality_map = {}
for line in mortality_30:
	line = line.strip().split(",")
	mortality_map[line[0]] = line[1] # key = patient_id, value = last recorded admission time

# Compute observed mortality = number of patients who died within 30 days of admission/total patients seen based on H&P notes

#initialize map with all physician ids
observed_mortality = {}
for physician in physician_cohorts.keys():
	observed_mortality[physician] = (0, len(physician_cohorts[physician]))

for physician, patients in physician_cohorts.iteritems():
	for (pat_id, note_time) in patients:

		if (pat_id in mortality_map):
			delta = pd.to_datetime(note_time) - pd.to_datetime(mortality_map[pat_id])
			if (delta >= pd.to_timedelta("0 days 00:00:00")): # this physician was responsible for this patient right before death
				#print(pat_id)
				#num_patients += 1
				observed_mortality[physician] = (observed_mortality[physician][0]+1, observed_mortality[physician][1])

# perform division (save number of observed mortalities)
observed_mortalities = {}
for physician, (dead, total) in observed_mortality.iteritems():
	observed_mortality[physician] = float(dead)/total
	observed_mortalities[physician] = int(dead)
#print(observed_mortality)

##########################
### Expected Mortality ###
##########################

# Expected mortality = average probability of patients in physician cohort dying within 30 days of an admission

# Initialize map with physician ids
expected_mortality = {}
for physician in physician_cohorts.keys():
	expected_mortality[physician] = (0, len(physician_cohorts[physician]))

# Read in sickness metrics (expected mortality probability)
mortality_probs = {} # key = patient_id, value = probability of dying within 30 days
mortality_probs_f = open("/Users/jwang/Desktop/Results/mortality_probs_remapped.csv", "rU")
mortality_probs_f.readline()
for line in mortality_probs_f:
	line = line.strip().split(",")
	mortality_probs[line[0]] = float(line[1])

# Find average probability of 30 day mortality for patients in cohort
for physician, patients in physician_cohorts.iteritems():
	for (pat_id, note_time) in patients:
		if (pat_id not in mortality_probs):
			continue # assume patient without probability of death maintains same as average probability for the physician

		if (physician in expected_mortality):
			expected_mortality[physician] = (float(expected_mortality[physician][0])+mortality_probs[pat_id], expected_mortality[physician][1]+1)
		else: # not yet in the dictionary
			expected_mortality[physician] = (mortality_probs[pat_id], 1)

# Perform division
for physician, (prob_sum, total) in expected_mortality.iteritems():
	expected_mortality[physician] = float(prob_sum)/total
#print(expected_mortality)

############################
### Print/Compute Scores ###
############################

# Write out observed and expected probabilities to CSV
outf = open("/Users/jwang/Desktop/Results/mortality_observed_vs_expected.csv", "w")
outf.write("physician,observed_mortality_rate,expected_mortality_rate,total_patients,observed_dead,observed_survived,expected_dead,expected_survived,p-value,score,observed_over_expected\n")
for physician in physician_cohorts.keys():

	# Compute Fisher Exact Test
	cohort_size = len(physician_cohorts[physician])
	observed_dead = observed_mortalities[physician]
	observed_survived = cohort_size - observed_dead
	expected_dead = round(expected_mortality[physician]*cohort_size)
	expected_survived = cohort_size - expected_dead
	contingency_table = [ [observed_dead, observed_survived], [expected_dead, expected_survived] ]
	odds_ratio, p_value = scipy.stats.fisher_exact(contingency_table, alternative="two-sided") # observed dead, observed survived | expected dead, expected_survived
	if (expected_mortality[physician] == 0):
		observed_over_expected = None
	else:
		observed_over_expected = float(observed_mortality[physician])/expected_mortality[physician]

	# Two-Sided
	score = -1*math.log10(p_value) # base 10 logarithm
	if (observed_dead > expected_dead): # more patients died than were expected
		score = -1*score

	outf.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10}\n".format(physician,observed_mortality[physician],expected_mortality[physician],len(physician_cohorts[physician]),
		observed_dead,observed_survived,expected_dead,expected_survived,p_value,score,observed_over_expected))
outf.close()

