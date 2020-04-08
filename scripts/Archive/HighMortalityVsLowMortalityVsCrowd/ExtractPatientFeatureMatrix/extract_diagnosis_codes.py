#!/usr/bin/env python
##########################################################################################
# Extract all diagnoses sorted by item_count
##########################################################################################
import sys, os
from io import StringIO
from datetime import datetime;

os.chdir('/Users/jwang/Desktop/CDSS/medinfo/db')
from Const import RUNNER_VERBOSITY;
from Util import log;
from Util import DBTestCase;

os.chdir('/Users/jwang/Desktop/CDSS')
from medinfo.common.test.Util import MedInfoTestCase;
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery;

# Create SCRIPT_FILE
SCRIPT_FILE = StringIO()
SCRIPT_FILE.write("psql medinfo_2008_2014_patch_2014_2017 jwang198")
DATA_QUERY = SQLQuery();

# From patient_item or clinical_item
DATA_QUERY.addSelect("clinical_item_id")
# DATA_QUERY.addSelect("clinical_item_category_id")
DATA_QUERY.addSelect("description")
DATA_QUERY.addSelect('name')
# DATA_QUERY.addSelect("item_count")

# Join
DATA_QUERY.addFrom("clinical_item")
DATA_QUERY.addWhereEqual("clinical_item_category_id", "2") 

DATA_QUERY.addOrderBy("item_count", dir="DESC")

print(DATA_QUERY)

# Write out data to CSV
DBUtil.runDBScript(SCRIPT_FILE, False)
results = DBUtil.execute(DATA_QUERY);

unique_patient_ids = {}

output = open("/Users/jwang/Desktop/Chen/Top_vs_Bottom_Study/Results/patient_feature_matrix/diagnoses.csv", "w")
# output.write("clinical_item_id,clinical_item_category_id,name,description,item_count\n")
output.write("clinical_item_id,description\n")

for line in results:
    # output.write("{0},{1},{2},{3},{4}\n".format(line[0],line[1],line[2],line[3],line[4]))
    output.write("{0},{1},{2}\n".format(line[0],line[1],line[2]))
