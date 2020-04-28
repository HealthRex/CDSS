import numpy as np
import collections
import datetime
from dateutil import parser
import pickle
import sys

# Create a master usage spreadsheet with columns
# Rotation, Role, Provider_ID, User-Day/Date, [Usage Per Relevant EHR Categories], Total Usage, 
# Number of EHR Actions, Number of EHR Actions Accessed Remotely, Number of Patient Records Accessed

access_logs = open("raw_resident_access_logs.csv", "rU")
access_logs.readline()

cutoff = 5 # minutes
role_map = 	{"R1":"PGY1", "R2":"PGY2+", "R3":"PGY2+"}

# 2 = General Medicine
# 5 = Night Team
# 22 = Emergency Medicine
# 27 = Intensive Care Unit
# note: only PGY2+ residents rotate through ICU
rotation_map = {"2":"General Medicine", "5":"Night Team", "22":"Emergency Medicine", "27":"Intensive Care Unit"}

# a user_day key is unique since a given user can presumably only assume one role for one rotation on one day 
patient_counter = {} # user-day: number of unique patients seen
action_counter = {} # user-day: number of ehr actions performed
remote_action_counter = {} # user-day: number of ehr actions accessed remotely (non-workstation)
role_tracker = {} # user-day: role
rotation_tracker = {} # user-day: rotation

# Extract all timestamps corresponding to a given user-day
action_histories = {} # indexed by user-day

# count = 0
# first pass through raw data
for line in access_logs:
	# count += 1
	# if (count % 10000 == 0):
		# print("{0} lines read...".format(count))
	line = line.strip().split(",")

	# extract relevant data fields
	role = role_map[line[0]]
	rotation = rotation_map[line[1]]
	patient_id = line[2]
	provider_id = line[4]
	workstation_id = line[7]
	metric_id = line[8]
	access_date = line[14].split(" ")[0]
	user_day = provider_id + "_" + access_date
	access_timestamp = line[14].split(" ")[1] # 15:15:56

	# update counters/trackers
	if (user_day not in patient_counter):
		patient_counter[user_day] = {}
	patient_counter[user_day][patient_id] = 1

	if (user_day not in action_counter):
		action_counter[user_day] = 0
	action_counter[user_day] += 1

	role_tracker[user_day] = role # although this same key will be updated many times, it will be updated with the same value - so we're ok!
	rotation_tracker[user_day] = rotation

	# If workstation_id == "GENERIC" or "", then remote login
	# Else --> workstation login from computer present in hospital
	if (workstation_id == "GENERIC" or workstation_id == ""): # remote access
		if (user_day not in remote_action_counter):
			remote_action_counter[user_day] = 0
		remote_action_counter[user_day] += 1

	# fill action history
	if (user_day not in action_histories):
		action_histories[user_day] = [(access_timestamp, metric_id)]
	else: # user_day already present
		action_histories[user_day].append( (access_timestamp, metric_id) )

# For each rotation and user-day, sort list of tuples by access_timestamp
for user_day in list(action_histories.keys()):
	action_histories[user_day] = sorted(action_histories[user_day], key=lambda x: x[0])

# Note: there are 551 different metric_ids (actions)
# load metric_id to ehr action category map
metric_inf = open("ehr_action_categories.csv", "rU")
metric_category_map = {}
for line in metric_inf:
	line = line.strip().split(",")
	metric_category_map[line[0]] = line[1]
metric_inf.close()

# Track time spent on each EHR category 
categories_of_interest = ["Chart Review", "Note Review", "Note Entry", "Order Entry", "Navigator", "Results Review"]
category_time_counter = {}
for category in categories_of_interest:
	category_time_counter[category] = {} # indexed by user-day

# Track time spent on EHR across all categories ("total")
total_time_counter = {} # indexed by user-day

# For each rotation and user-day, compute action deltas (proxy for interaction time)
for user_day, history in action_histories.items():
	time_start = ""
	metric_id = ""
	metric_category = ""
	for tup in history:
		if (time_start == ""): # first time in sequence
			time_start = parser.parse(tup[0])
			metric_id = tup[1]
			if (metric_id in metric_category_map): # action of interest
				metric_category = metric_category_map[metric_id]
			else:
				metric_category = ""
		else: 
			# compute difference between timestamps
			time_delta = parser.parse(tup[0]) - time_start
			if (time_delta <= datetime.timedelta(minutes=cutoff)): # enforce idle cutoff (e.g. consider only inter-access time intervals < 5 minutes or else assume inactivity)
				if (user_day not in list(total_time_counter.keys())):
					total_time_counter[user_day] = datetime.timedelta(minutes=0)
				total_time_counter[user_day] += time_delta

				# based on metric_category, add to corresponding time_counter
				if (metric_category in categories_of_interest):
					if (user_day not in list(category_time_counter[metric_category].keys())):
						category_time_counter[metric_category][user_day] = datetime.timedelta(minutes=0)
					category_time_counter[metric_category][user_day] += time_delta

			# update variables
			time_start = parser.parse(tup[0])
			metric_id = tup[1]
			if (metric_id in metric_category_map): # action of interest
				metric_category = metric_category_map[metric_id]
			else:
				metric_category = ""

# Output results to master spreadsheet
outf_spreadsheet = open("usage_spreadsheet.csv", "w")
outf_spreadsheet.write("Rotation,Role,Provider_ID,Date,Chart_Review_Time,Note_Review_Time,Note_Entry_Time,Order_Entry_Time,Navigator_Time,Results_Review_Time,Total_Time,Number_EHR_Actions,Number_EHR_Actions_Accessed_Remotely,Number_Unique_Patient_Records_Accessed\n")
for user_day in list(total_time_counter.keys()):
	provider_id = user_day.split("_")[0]
	access_date = user_day.split("_")[1]

	# ehr action-specific usage times
	chart_review_time = datetime.timedelta(minutes=0)
	note_review_time = datetime.timedelta(minutes=0)
	note_entry_time = datetime.timedelta(minutes=0)
	order_entry_time = datetime.timedelta(minutes=0)
	navigator_time = datetime.timedelta(minutes=0)
	results_review_time = datetime.timedelta(minutes=0)
	total_time = datetime.timedelta(minutes=0)
	if (user_day in category_time_counter["Chart Review"]):
		chart_review_time = category_time_counter["Chart Review"][user_day]
	if (user_day in category_time_counter["Note Review"]):
		note_review_time = category_time_counter["Note Review"][user_day]
	if (user_day in category_time_counter["Note Entry"]):
		note_entry_time = category_time_counter["Note Entry"][user_day]
	if (user_day in category_time_counter["Order Entry"]):
		order_entry_time = category_time_counter["Order Entry"][user_day]
	if (user_day in category_time_counter["Navigator"]):
		navigator_time = category_time_counter["Navigator"][user_day]
	if (user_day in category_time_counter["Results Review"]):
		results_review_time = category_time_counter["Results Review"][user_day]
	if (user_day in total_time_counter):
		total_time = total_time_counter[user_day]

	# counters
	num_actions = 0
	num_remote_actions = 0
	num_patients = 0
	if (user_day in action_counter):
		num_actions = action_counter[user_day]
	if (user_day in remote_action_counter):
		num_remote_actions = remote_action_counter[user_day]
	if (user_day in patient_counter):
		num_patients = len(patient_counter[user_day]) # number of unique patients

	outf_spreadsheet.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13}\n".format(rotation_tracker[user_day],role_tracker[user_day],
		provider_id,access_date,chart_review_time,note_review_time,note_entry_time,order_entry_time,navigator_time,results_review_time,total_time,
		num_actions,num_remote_actions,num_patients))
outf_spreadsheet.close()

