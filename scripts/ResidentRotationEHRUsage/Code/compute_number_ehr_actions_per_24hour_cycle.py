# Goal: compute average number of EHR actions logged per user day in half hour increments over 24 hour cycle for different inpatient rotations
import numpy as np

# Change flag to compute for PGY1 or PGY2+
# ROLE = "PGY1"
ROLE = "PGY2+"

if (ROLE == "PGY1"):
	role_filter = ["R1"]
else:
	role_filter = ["R2","R3"]

access_logs = open("raw_resident_access_logs.csv", "rU")
access_logs.readline()

# For each rotation, we split 24 hours into 48 half-hour buckets; we then keep count of number of actions
def bucket(access_timestamp):
	hours = access_timestamp[0]
	minutes = access_timestamp[1]
	bucket_id = hours*2

	if (minutes > 30):
		bucket_id += 1
	return(bucket_id)

action_counter = {'2':{}, '5':{}, '22':{}, '27':{}}
for line in access_logs:
	line = line.strip().split(",")
	role = line[0]
	if (role in role_filter):
		# print(role)
		rotation_id = line[1]
		access_date = line[14].split(" ")[0]
		access_timestamp = list(map(int, line[14].split(" ")[1].split(":")[:-1]))
		bucket_id = bucket(access_timestamp)
		provider_id = line[4]

		user_day = provider_id + "_" + access_date
		if (user_day not in action_counter[rotation_id]):
			action_counter[rotation_id][user_day] = [0]*48
			action_counter[rotation_id][user_day][bucket_id] += 1
		else: # user_day already present
			action_counter[rotation_id][user_day][bucket_id] += 1

# For each rotation, compute average number of actions per user-day
averaged_timeseries = {'2':np.zeros(48), '5':np.zeros(48), '22':np.zeros(48), '27':np.zeros(48)}
for rotation_id in list(action_counter.keys()):
	num_user_days = 0
	for user_day, action_ts in action_counter[rotation_id].items(): # for each timeseries
		num_user_days += 1
		averaged_timeseries[rotation_id] = averaged_timeseries[rotation_id] + np.array(action_ts)
	if (num_user_days == 0): # e.g. for PGY1 interns in ICU since first years do not do ICU rotation
		averaged_timeseries[rotation_id] = averaged_timeseries[rotation_id] # no division
	else:
		averaged_timeseries[rotation_id] = averaged_timeseries[rotation_id] / num_user_days

# Output results
outf = open("average_number_actions_per_userday_24_hour_cycle_{0}.csv".format(ROLE), "w")
outf.write("rotation,{0}\n".format(",".join(map(str, list(np.array(list(range(0,48)))/2.0)))))
for k, v in averaged_timeseries.items():
	if (int(k) == 2):
		outf.write("General Medicine,")
	elif (int(k) == 5):
		outf.write("Medicine Night Team,")
	elif (int(k) == 22):
		outf.write("Emergency Department,")
	elif (int(k) == 27):
		outf.write("Intensive Care Unit,")
	else:
		print("unrecognized rotation_id...")
	outf.write("{0}\n".format(",".join(map(str, list(v)))))
outf.close()

