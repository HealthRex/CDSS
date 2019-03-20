# Write out all patients that were readmitted within 30 days of a discharge
import pandas

threshold = pandas.to_timedelta("30 days 00:00:00") # 30 days

readmissions = open("/Users/jwang/Desktop/Results/30_day_readmissions.csv", "w")
lengths_of_stay = "/Users/jwang/Desktop/Results/lengths_of_stay.csv"

readmissions.write("patient_id,previous_discharge_time,previous_encounter_id,readmission_time,readmission_delta\n")

df = pandas.read_csv(lengths_of_stay, sep=",")
df = df.sort_values(['patient_id', 'admission_time', 'discharge_time'], ascending=[0,1,1])

cur_patient = ""
prev_discharge_time = ""
prev_encounter_id = ""
for index, row in df.iterrows():
	# new patient: store information and move on to subsequent recorded admission
	if (cur_patient != row["patient_id"]):
		cur_patient = row["patient_id"]
		prev_discharge_time = row["discharge_time"]
		prev_encounter_id = row["encounter_id"]

	# same patient: check if time between this admission and previous admission is <= 30 days
	else: # (cur_patient == row["patient_id"]):
		readmission_delta = pandas.to_datetime(row["admission_time"]) - pandas.to_datetime(prev_discharge_time)
		if (readmission_delta <= threshold): # readmission occurred within 30 days
			readmissions.write('{0},{1},{2},{3},{4}\n'.format(cur_patient, prev_discharge_time, prev_encounter_id, row["admission_time"], readmission_delta))

		# continue to subsequent admission
		prev_discharge_time = row["discharge_time"]
		prev_encounter_id = row["encounter_id"]

readmissions.close()