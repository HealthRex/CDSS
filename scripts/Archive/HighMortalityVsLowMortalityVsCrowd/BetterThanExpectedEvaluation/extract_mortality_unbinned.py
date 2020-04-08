#!/usr/bin/env python
##########################################################################################
# Extract death clinical item occurrence per patient
##########################################################################################
import sys, os
import pandas
from io import StringIO
from datetime import datetime;

from Const import RUNNER_VERBOSITY;
from Util import log;
from Util import DBTestCase;

from medinfo.common.test.Util import MedInfoTestCase;
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery;

# Load in patient encounters map
patient_encounters = {}
pat_enc_f = open("/Users/jwang/Desktop/Chen/Top_vs_Bottom_Study/Results/lengths_of_stay.csv", "rU")
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

output = open("/Users/jwang/Desktop/Chen/Top_vs_Bottom_Study/Submission_JBI_Major_Revisions/Analysis_Better_Than_Expected/mortality_days_after_last_admission.csv", "w")
output.write("pat_id,admission_time,death_time,delta\n")
for line in results:
	if (line[1] is None):
		continue # patient survived, recorded as None
	
	pat_id = line[0]
	death_time = pandas.to_datetime(line[1])

	if (pat_id not in patient_encounters): # patient_id not included in admit-discharge table
		continue

	for admission_time in patient_encounters[pat_id]:
		delta = pandas.to_timedelta(death_time - admission_time)
		output.write("{0},{1},{2},{3}\n".format(pat_id,admission_time,death_time,delta))

output.close()
