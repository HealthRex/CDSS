# Compute summary statistics across rotations and roles

import numpy as np
import datetime
from dateutil import parser
import sys
from scipy.stats import ttest_ind

# exclude vacation days
threshold = 1*3600 # 1 hour vacation threshold (in seconds)

total_time_map = {"General Medicine":{"PGY1":[], "PGY2+":[]}, "Night Team":{"PGY1":[], "PGY2+":[]}, "Emergency Medicine":{"PGY1":[], "PGY2+":[]}, "Intensive Care Unit":{"PGY2+":[]}}
chart_review_map = {"General Medicine":{"PGY1":[], "PGY2+":[]}, "Night Team":{"PGY1":[], "PGY2+":[]}, "Emergency Medicine":{"PGY1":[], "PGY2+":[]}, "Intensive Care Unit":{"PGY2+":[]}}
note_review_map = {"General Medicine":{"PGY1":[], "PGY2+":[]}, "Night Team":{"PGY1":[], "PGY2+":[]}, "Emergency Medicine":{"PGY1":[], "PGY2+":[]}, "Intensive Care Unit":{"PGY2+":[]}}
note_entry_map = {"General Medicine":{"PGY1":[], "PGY2+":[]}, "Night Team":{"PGY1":[], "PGY2+":[]}, "Emergency Medicine":{"PGY1":[], "PGY2+":[]}, "Intensive Care Unit":{"PGY2+":[]}}
order_entry_map = {"General Medicine":{"PGY1":[], "PGY2+":[]}, "Night Team":{"PGY1":[], "PGY2+":[]}, "Emergency Medicine":{"PGY1":[], "PGY2+":[]}, "Intensive Care Unit":{"PGY2+":[]}}
navigator_map = {"General Medicine":{"PGY1":[], "PGY2+":[]}, "Night Team":{"PGY1":[], "PGY2+":[]}, "Emergency Medicine":{"PGY1":[], "PGY2+":[]}, "Intensive Care Unit":{"PGY2+":[]}}
results_review_map = {"General Medicine":{"PGY1":[], "PGY2+":[]}, "Night Team":{"PGY1":[], "PGY2+":[]}, "Emergency Medicine":{"PGY1":[], "PGY2+":[]}, "Intensive Care Unit":{"PGY2+":[]}}
num_actions_map = {"General Medicine":{"PGY1":[], "PGY2+":[]}, "Night Team":{"PGY1":[], "PGY2+":[]}, "Emergency Medicine":{"PGY1":[], "PGY2+":[]}, "Intensive Care Unit":{"PGY2+":[]}}
num_remote_actions_map = {"General Medicine":{"PGY1":[], "PGY2+":[]}, "Night Team":{"PGY1":[], "PGY2+":[]}, "Emergency Medicine":{"PGY1":[], "PGY2+":[]}, "Intensive Care Unit":{"PGY2+":[]}}
num_patients_map = {"General Medicine":{"PGY1":[], "PGY2+":[]}, "Night Team":{"PGY1":[], "PGY2+":[]}, "Emergency Medicine":{"PGY1":[], "PGY2+":[]}, "Intensive Care Unit":{"PGY2+":[]}}

inf = open("usage_spreadsheet.csv", "rU")
inf.readline()
for line in inf:
	line = line.strip().split(",")

	total_time = parser.parse(line[10]) 
	total_time = 3600*total_time.hour + 60*total_time.minute + total_time.second # convert to seconds

	if (total_time < threshold):
		continue

	rotation = line[0]
	role = line[1]

	num_actions_map[rotation][role].append(int(line[11]))
	num_remote_actions_map[rotation][role].append(int(line[12]))
	num_patients_map[rotation][role].append(int(line[13]))

	# add to total_time_map
	total_time_map[rotation][role].append(total_time/3600.0)

	# identify section-specific times
	chart_review = parser.parse(line[4])
	chart_review = 3600*chart_review.hour + 60*chart_review.minute + chart_review.second # convert to seconds
	chart_review_map[rotation][role].append(chart_review/3600.0)

	note_review = parser.parse(line[5])
	note_review = 3600*note_review.hour + 60*note_review.minute + note_review.second # convert to seconds
	note_review_map[rotation][role].append(note_review/3600.0)

	note_entry = parser.parse(line[6])
	note_entry = 3600*note_entry.hour + 60*note_entry.minute + note_entry.second # convert to seconds
	note_entry_map[rotation][role].append(note_entry/3600.0)

	order_entry = parser.parse(line[7])
	order_entry = 3600*order_entry.hour + 60*order_entry.minute + order_entry.second # convert to seconds
	order_entry_map[rotation][role].append(order_entry/3600.0)

	navigator = parser.parse(line[8])
	navigator = 3600*navigator.hour + 60*navigator.minute + navigator.second # convert to seconds
	navigator_map[rotation][role].append(navigator/3600.0)

	results_review = parser.parse(line[9])
	results_review = 3600*results_review.hour + 60*results_review.minute + results_review.second # convert to seconds
	results_review_map[rotation][role].append(results_review/3600.0)


num (remote) actions, num patients
for rotation in num_actions_map.keys():
	for role, values in num_actions_map[rotation].iteritems():
		print("# Actions", rotation, role)
		print("{0} median with IQR {1}-{2}".format(np.median(np.array(values)), np.percentile(np.array(values), 25), np.percentile(np.array(values), 75)))

for rotation in num_remote_actions_map.keys():
	for role, values in num_remote_actions_map[rotation].iteritems():
		print("# Remote Actions", rotation, role)
		print("{0} median with IQR {1}-{2}".format(np.median(np.array(values)), np.percentile(np.array(values), 25), np.percentile(np.array(values), 75)))

for rotation in num_patients_map.keys():
	for role, values in num_patients_map[rotation].iteritems():
		print("# Patients", rotation, role)
		print("{0} median with IQR {1}-{2}".format(np.median(np.array(values)), np.percentile(np.array(values), 25), np.percentile(np.array(values), 75)))


time spent on each ehr action
for rotation in chart_review_map.keys():
	for role, values in chart_review_map[rotation].iteritems():
		print("Chart Review", rotation, role)
		print("{0} mean with stdev {1}".format(np.mean(np.array(values)), np.std(np.array(values))))

for rotation in note_review_map.keys():
	for role, values in note_review_map[rotation].iteritems():
		print("Note Review", rotation, role)
		print("{0} mean with stdev {1}".format(np.mean(np.array(values)), np.std(np.array(values))))

for rotation in note_entry_map.keys():
	for role, values in note_entry_map[rotation].iteritems():
		print("Note Entry", rotation, role)
		print("{0} mean with stdev {1}".format(np.mean(np.array(values)), np.std(np.array(values))))

for rotation in order_entry_map.keys():
	for role, values in order_entry_map[rotation].iteritems():
		print("Order Entry", rotation, role)
		print("{0} mean with stdev {1}".format(np.mean(np.array(values)), np.std(np.array(values))))

for rotation in navigator_map.keys():
	for role, values in navigator_map[rotation].iteritems():
		print("Navigator", rotation, role)
		print("{0} mean with stdev {1}".format(np.mean(np.array(values)), np.std(np.array(values))))

for rotation in results_review_map.keys():
	for role, values in results_review_map[rotation].iteritems():
		print("Results Review", rotation, role)
		print("{0} mean with stdev {1}".format(np.mean(np.array(values)), np.std(np.array(values))))

total time in aggregate and by role
agg = [] # aggregate across all rotations and roles
pgy1 = []
pgy2plus = []
for rotation in total_time_map.keys():
	for role, values in total_time_map[rotation].iteritems():
		agg.extend(values)
		if (role == "PGY1"):
			pgy1.extend(values)
		else: # role == "PGY2+"
			pgy2plus.extend(values)
print("All rotations/roles")
print("{0} mean with stdev {1}".format(np.mean(np.array(agg)), np.std(np.array(agg))))
print("{0} median with IQR {1}-{2}".format(np.median(np.array(agg)), np.percentile(np.array(agg), 25), np.percentile(np.array(agg), 75)))

print("PGY1")
print("{0} mean with stdev {1}".format(np.mean(np.array(pgy1)), np.std(np.array(pgy1))))
print("{0} median with IQR {1}-{2}".format(np.median(np.array(pgy1)), np.percentile(np.array(pgy1), 25), np.percentile(np.array(pgy1), 75)))

print("PGY2+")
print("{0} mean with stdev {1}".format(np.mean(np.array(pgy2plus)), np.std(np.array(pgy2plus))))
print("{0} median with IQR {1}-{2}".format(np.median(np.array(pgy2plus)), np.percentile(np.array(pgy2plus), 25), np.percentile(np.array(pgy2plus), 75)))

total time by rotation and role
for rotation in total_time_map.keys():
	for role, values in total_time_map[rotation].iteritems():
		print(rotation, role)
		print("{0} mean with stdev {1}".format(np.mean(np.array(values)), np.std(np.array(values))))
		print("{0} median with IQR {1}-{2}".format(np.median(np.array(values)), np.percentile(np.array(values), 25), np.percentile(np.array(values), 75)))
n