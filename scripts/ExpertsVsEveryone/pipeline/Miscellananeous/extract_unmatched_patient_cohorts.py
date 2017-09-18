#!/usr/bin/env python
##########################################################################################
# Extract patient_ids based on expert v.s. everyone provider type
##########################################################################################
import sys, os
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
from medinfo.db.DBUtil import NUMBER, BOOLEAN, STRING, DATETIME;

# Create SCRIPT_FILE
SCRIPT_FILE = StringIO()
SCRIPT_FILE.write("psql medinfo jwang198")

# Find all clinical_item_ids associated with each patient_id
# SELECT * FROM clinical_item WHERE clinical_item_category_id = 161;

DATA_QUERY = SQLQuery();

# From patient_item or clinical_item
DATA_QUERY.addSelect("patient_id")
DATA_QUERY.addSelect("clinical_item_category_id")
DATA_QUERY.addSelect('name')
DATA_QUERY.addSelect("description")

# Join
DATA_QUERY.addFrom("patient_item")
DATA_QUERY.addJoin("clinical_item", "patient_item.clinical_item_id = clinical_item.clinical_item_id", joinType="INNER")
DATA_QUERY.addWhereEqual("clinical_item_category_id = 161 AND description", "Tt Med Univ (Primary)") # Everyone
#DATA_QUERY.addWhereEqual("clinical_item_category_id = 161 AND description", "Tt Pamf Med (Primary)") # Expert

DATA_QUERY.addOrderBy("patient_id", dir="ASC")

print(DATA_QUERY)

# Write out data to CSV
DBUtil.runDBScript(SCRIPT_FILE, False)
results = DBUtil.execute(DATA_QUERY);

unique_patient_ids = {}

# output = open("/Users/jwang/Desktop/expert.csv", "w")
# outlist = open("/Users/jwang/Desktop/expert_list.csv", "w")
output = open("/Users/jwang/Desktop/everyone.csv", "w") #includes experts + trainees who are providing patient care
outlist = open("/Users/jwang/Desktop/everyone_list.csv", "w")

output.write("patient_id,clinical_item_category_id,name,description\n")

#count = 0
for line in results:
    if (line[0] not in unique_patient_ids.keys()): # only consider unique patient_ids
        unique_patient_ids[line[0]] = 1
        output.write("{0},{1},{2},{3}\n".format(line[0],line[1],line[2],line[3]))
        outlist.write(str(line[0])+"\n")
        # count += 1 # get 1000 unique patient_ids
        # if (count == 1000):
        #     break
    else:
        pass
