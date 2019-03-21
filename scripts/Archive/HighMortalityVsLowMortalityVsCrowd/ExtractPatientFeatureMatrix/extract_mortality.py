#!/usr/bin/env python
##########################################################################################
# Extract death clinical item occurrence per patient
##########################################################################################
import sys, os
import pandas
from cStringIO import StringIO
from datetime import datetime;

os.chdir('/Users/jwang/Desktop/ClinicalDecisionMaker/medinfo/db')
from Const import RUNNER_VERBOSITY;
from Util import log;
from Util import DBTestCase;

os.chdir('/Users/jwang/Desktop/ClinicalDecisionMaker')
from medinfo.common.test.Util import MedInfoTestCase;
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery;

# Load in patient encounters map
patient_encounters = {}
pat_enc_f = open("/Users/jwang/Desktop/Results/lengths_of_stay.csv", "rU")
pat_enc_f.readline()
for line in pat_enc_f:
	line = line.strip().split(",")
	if (line[0] not in patient_encounters):
		patient_encounters[line[0]] = [pandas.to_datetime(line[1]),] # patient id: list of admission times
	else:
		patient_encounters[line[0]].append(pandas.to_datetime(line[1]))

# print(patient_encounters)

# Create SCRIPT_FILE
SCRIPT_FILE = StringIO()
SCRIPT_FILE.write("psql stride jwang198")
DATA_QUERY = SQLQuery();

DATA_QUERY.addSelect("pat_id")
DATA_QUERY.addSelect("death_date")
DATA_QUERY.addFrom("stride_patient")
print(DATA_QUERY)

# Write out data to CSV
DBUtil.runDBScript(SCRIPT_FILE, False)
results = DBUtil.execute(DATA_QUERY);
#print(len(results))

output_7 = open("/Users/jwang/Desktop/Results/7_day_deaths.csv", "w")
output_30 = open("/Users/jwang/Desktop/Results/30_day_deaths.csv", "w")
output_90 = open("/Users/jwang/Desktop/Results/90_day_deaths.csv", "w")

output_7.write("patient_id,prev_admission_time,death_time,delta\n")
output_30.write("patient_id,prev_admission_time,death_time,delta\n")
output_90.write("patient_id,prev_admission_time,death_time,delta\n")

delta_7 = pandas.to_timedelta("7 days 00:00:00")
delta_30 = pandas.to_timedelta("30 days 00:00:00")
delta_90 = pandas.to_timedelta("90 days 00:00:00")
for line in results:
	if (line[1] is None):
		continue # patient survived, recorded as None
	
	pat_id = line[0]
	death_time = pandas.to_datetime(line[1])

	if (pat_id not in patient_encounters): # patient_id not included in admit-discharge table
		continue

	for admission_time in patient_encounters[pat_id]:
		delta = pandas.to_timedelta(death_time - admission_time)
		if (delta <= delta_90):
			output_90.write("{0},{1},{2},{3}\n".format(pat_id,admission_time,death_time,delta))
			if (delta <= delta_30):
				output_30.write("{0},{1},{2},{3}\n".format(pat_id,admission_time,death_time,delta))
				if (delta <= delta_7):
					output_7.write("{0},{1},{2},{3}\n".format(pat_id,admission_time,death_time,delta))

output_7.close()
output_30.close()
output_90.close()
