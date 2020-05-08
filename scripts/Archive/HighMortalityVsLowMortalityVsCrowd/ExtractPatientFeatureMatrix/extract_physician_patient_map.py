#!/usr/bin/env python
##########################################################################################
# Extract all patients and their associated 
##########################################################################################
import sys, os
from io import StringIO
from datetime import datetime;

os.chdir('/Users/jwang/Desktop/ClinicalDecisionMaker/medinfo/db')
from Const import RUNNER_VERBOSITY;
from Util import log;
from Util import DBTestCase;

os.chdir('/Users/jwang/Desktop/ClinicalDecisionMaker')
from medinfo.common.test.Util import MedInfoTestCase;
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery;

# Create SCRIPT_FILE

# clinical_item_category_id = 13 (Discharge)
# clinical_item_category_id = 23 (Admission)

# H&P Note

SCRIPT_FILE = StringIO()
SCRIPT_FILE.write("psql stride jwang198")
DATA_QUERY = SQLQuery();

DATA_QUERY.addSelect("author_name")
DATA_QUERY.addSelect("pat_id")
DATA_QUERY.addSelect("note_date")
DATA_QUERY.addSelect("note_type")
DATA_QUERY.addSelect("provider_type")
DATA_QUERY.addSelect("specialty")
DATA_QUERY.addSelect("pat_enc_csn_id")

DATA_QUERY.addFrom("stride_note")
DATA_QUERY.addWhereEqual("note_type", "H&P")
DATA_QUERY.addOrderBy("author_name", dir="asc")
print(DATA_QUERY)

# Write out data to CSV
DBUtil.runDBScript(SCRIPT_FILE, False)
results = DBUtil.execute(DATA_QUERY);

output_hp = open("/Users/jwang/Desktop/Results/physician_patient_map_hp.csv", "w")
output_hp.write("clinician_name,patient_id,note_date,note_type,provider_type,specialty,encounter_id\n")

for line in results:
	if (line[4] == "Medical Student" or line[5] == "Medical Student"): #exclude medical students
		continue
	clinician_name = line[0].strip().split(",")
	clinician_name = "{0} {1}".format(clinician_name[1], clinician_name[0])
	output_hp.write("{0},{1},{2},{3},{4},{5},{6}\n".format(clinician_name,line[1],line[2],line[3],line[4],line[5],line[6]))

# Discharge Summary
SCRIPT_FILE = StringIO()
SCRIPT_FILE.write("psql stride jwang198")
DATA_QUERY = SQLQuery();

DATA_QUERY.addSelect("author_name")
DATA_QUERY.addSelect("pat_id")
DATA_QUERY.addSelect("note_date")
DATA_QUERY.addSelect("note_type")
DATA_QUERY.addSelect("provider_type")
DATA_QUERY.addSelect("specialty")
DATA_QUERY.addSelect("pat_enc_csn_id")

DATA_QUERY.addFrom("stride_note")
DATA_QUERY.addWhereEqual("note_type", "Discharge Summaries")
DATA_QUERY.addOrderBy("author_name", dir="asc")
print(DATA_QUERY)

# Write out data to CSV
DBUtil.runDBScript(SCRIPT_FILE, False)
results = DBUtil.execute(DATA_QUERY);

output_discharge = open("/Users/jwang/Desktop/Results/physician_patient_map_discharge.csv", "w")
output_discharge.write("clinician_name,patient_id,note_date,note_type,provider_type,specialty,encounter_id\n")

for line in results:
	if (line[4] == "Medical Student" or line[5] == "Medical Student"): #exclude medical students
		continue
	clinician_name = line[0].strip().split(",")
	clinician_name = "{0} {1}".format(clinician_name[1], clinician_name[0])
	output_discharge.write("{0},{1},{2},{3},{4},{5},{6}\n".format(clinician_name,line[1],line[2],line[3],line[4],line[5],line[6]))
