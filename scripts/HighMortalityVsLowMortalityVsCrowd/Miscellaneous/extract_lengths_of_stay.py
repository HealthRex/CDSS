import pandas 

def compute_delta(admission_time, discharge_time):
	# Stride time syntax: 2012-04-12 11:09:00
	return (pandas.to_datetime(discharge_time) - pandas.to_datetime(admission_time))

def main():
	flowtable = "/Users/jwang/Desktop/Results/admission_discharge_flow.csv"
	length_of_stay = open("/Users/jwang/Desktop/Results/lengths_of_stay.csv", "w")

	df = pandas.read_csv(flowtable, sep=",")
	df = df.sort_values(['patient_id', 'admission_time', 'discharge_time'], ascending=[0,1,1])

	df.to_csv("/Users/jwang/Desktop/Results/pandas_temp.csv", sep=",")

	length_of_stay.write("patient_id,admission_time,discharge_time,length_of_stay,encounter_id\n")

	# Variables
	cur_patient = ""
	cur_admission_time = ""
	cur_encounter_id = ""
	first_admission_found = False # to ensure that admission/discharge order times between patients are not mixed up

	# For each admission order, find closest discharge order; this constitutes a patient encounter/length of stay
	for index, row in df.iterrows():
		#print(index)

		# start of new patient: look for first discharge
		if (cur_patient != row["patient_id"] or not first_admission_found):
			cur_patient = row["patient_id"]
			first_admission_found = False

			if (row["admission"] == "Admission"):
				cur_admission_time = row["admission_time"]
				cur_encounter_id = row["encounter_id"] # encounter_id holds for a patient's entire stay from initial admission to final discharge
				first_admission_found = True

				if (row["discharge"] == "Discharge"):

					# Compute length of stay
					time_delta = compute_delta(cur_admission_time, row["discharge_time"])
					length_of_stay.write("{0},{1},{2},{3},{4}\n".format(cur_patient, cur_admission_time, row["discharge_time"], time_delta, cur_encounter_id))

			else: # continue until you found first admission order for the new patient
				continue	

		# same patient
		else: # cur_patient == row["patient_id"]:

			if (row["admission"] == "Admission"): # restart: look for next discharge
				cur_admission_time = row["admission_time"]
				cur_encounter_id = row["encounter_id"]

			if (row["discharge"] == "Discharge"):

				# Compute length of stay
				time_delta = compute_delta(cur_admission_time, row["discharge_time"])
				length_of_stay.write("{0},{1},{2},{3},{4}\n".format(cur_patient, cur_admission_time, row["discharge_time"], time_delta, cur_encounter_id))
	length_of_stay.close()

if __name__ == "main":
	main()

# Script
main()