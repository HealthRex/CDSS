#!/usr/bin/env python
##########################################################################################
# Extract out treatment groups per patient
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

# Load in Treatment Group Aggregations
treatment_aggregations = open("/Users/jwang/Desktop/ClinicalDecisionMaker/medinfo/dataconversion/mapdata/TreatmentTeamGroups.tab", "rU")
treatment_aggregation_map = {}
treatment_aggregations.readline()
treatment_aggregations.readline()
for line in treatment_aggregations:
	line = line.strip().split("\t")
	treatment_aggregation_map[line[0]] = line[1]
print(treatment_aggregation_map)

# Create SCRIPT_FILE
SCRIPT_FILE = StringIO()
SCRIPT_FILE.write("psql stride jwang198")

# Find all clinical_item_ids associated with each patient_id
# SELECT * FROM clinical_item WHERE clinical_item_category_id = 161;

DATA_QUERY = SQLQuery();
DATA_QUERY.addSelect("clinical_item_id")
DATA_QUERY.addSelect("description")
DATA_QUERY.addSelect("clinical_item_category_id")
DATA_QUERY.addWhereEqual("clinical_item_category_id", "161")
DATA_QUERY.addFrom("clinical_item")

print(DATA_QUERY)

# Write out data to CSV
DBUtil.runDBScript(SCRIPT_FILE, False)
results = DBUtil.execute(DATA_QUERY);

output = open("/Users/jwang/Desktop/Results/treatment_teams.csv", "w")
output.write("clinical_item_id,description,clinical_item_category_id,treatment_team\n")

for line in results:
	treatment_team = "Unclassified"
	if line[1] in treatment_aggregation_map:
		treatment_team = treatment_aggregation_map[line[1]]
	output.write("{0},{1},{2},{3}\n".format(line[0],line[1],line[2],treatment_team))

	