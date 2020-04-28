#!/usr/bin/env python
##########################################################################################
# Extract age out of stride database
##########################################################################################
import sys, os
from io import StringIO
from datetime import datetime

os.chdir('/Users/jwang/Desktop/ClinicalDecisionMaker/medinfo/db')
from Const import RUNNER_VERBOSITY;
from Util import log;
from Util import DBTestCase;

os.chdir('/Users/jwang/Desktop/ClinicalDecisionMaker')
from medinfo.common.test.Util import MedInfoTestCase;
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery;

# Create SCRIPT_FILE
SCRIPT_FILE = StringIO()
SCRIPT_FILE.write("psql stride jwang198")

# Find all clinical_item_ids associated with each patient_id
# SELECT * FROM clinical_item WHERE clinical_item_category_id = 161;

DATA_QUERY = SQLQuery();
DATA_QUERY.addSelect("pat_id")
DATA_QUERY.addSelect("birth_year")
DATA_QUERY.addFrom("stride_patient")

print(DATA_QUERY)

# Write out data to CSV
DBUtil.runDBScript(SCRIPT_FILE, False)
results = DBUtil.execute(DATA_QUERY);

output = open("/Users/jwang/Desktop/ages.csv", "w")
output.write("patient_id,age\n")

for line in results:
	age = None
	if (line[1] != None):
		age = 2017 - int(line[1])
	output.write("{0},{1}\n".format(line[0],age))