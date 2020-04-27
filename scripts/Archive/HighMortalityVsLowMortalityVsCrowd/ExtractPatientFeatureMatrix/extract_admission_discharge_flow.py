#!/usr/bin/env python
##########################################################################################
# Extract admission and discharge orders for all patients
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

SCRIPT_FILE = StringIO()
SCRIPT_FILE.write("psql stride jwang198")
DATA_QUERY = SQLQuery();

DATA_QUERY.addSelect("pat_anon_id")
DATA_QUERY.addSelect("shifted_transf_in_dt_tm")
DATA_QUERY.addSelect("department_in")
DATA_QUERY.addSelect("event_in")
DATA_QUERY.addSelect("shifted_transf_out_dt_tm")
DATA_QUERY.addSelect("event_out")
DATA_QUERY.addSelect("pat_enc_csn_anon_id")
DATA_QUERY.addWhereEqual("event_out = 'Discharge' OR event_in", 'Admission')

DATA_QUERY.addFrom("stride_adt")
print(DATA_QUERY)

# Write out data to CSV
DBUtil.runDBScript(SCRIPT_FILE, False)
results = DBUtil.execute(DATA_QUERY);

output = open("/Users/jwang/Desktop/Results/admission_discharge_flow.csv", "w")
output.write("patient_id,admission_time,department,admission,discharge_time,discharge,encounter_id\n")

for line in results:
    output.write("{0},{1},{2},{3},{4},{5},{6}\n".format(line[0],line[1],line[2],line[3],line[4],line[5],line[6]))
