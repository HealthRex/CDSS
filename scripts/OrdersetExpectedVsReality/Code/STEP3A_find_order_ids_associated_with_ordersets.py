# An a la carte order cannot be ordered from an order set although the order is present in the orderset; an orderset cannot be triggered
# Extract all order_med_ids/order_proc_ids associated with a given patient_id
# Output a pickled map that we can use to filter orders ordere from order sets
import glob
import sys, os
from cStringIO import StringIO
from datetime import datetime, timedelta
from dateutil import parser
import pickle as pkl

os.chdir('/Users/jwang/Desktop/CDSS/medinfo/db')
from Const import RUNNER_VERBOSITY;
from Util import log;
from Util import DBTestCase;

os.chdir('/Users/jwang/Desktop/CDSS')
from medinfo.common.test.Util import MedInfoTestCase;
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery;
from medinfo.db.DBUtil import NUMBER, BOOLEAN, STRING, DATETIME;

# Medications
orderset_order_med_ids = {} # key: patient_id, second_key: order_med_id associated with having been ordered from an orderset

DATA_QUERY = """
SELECT  
	soom.order_med_id,
	som.pat_id
FROM 
	stride_order_med AS som 
	JOIN 
		stride_orderset_order_med AS soom 
	ON 
		som.order_med_id = soom.order_med_id
WHERE 
	som.ordering_date::DATE > DATE '2014-01-01'
	AND NOT section_name = 'Ad-hoc Orders'
"""
print(DATA_QUERY)
DATADIR = "/Users/jwang/Desktop/Chen/OrderSetOptimization/Results/2014-2017"

results = DBUtil.execute(DATA_QUERY);
for line in results:
	order_med_id = int(line[0])
	patient_id = int(line[1])
	# if (patient_id == 7072283518095):
	# 	print(patient_id, order_med_id)
	if (patient_id not in orderset_order_med_ids.keys()):
		orderset_order_med_ids[patient_id] = {}
	orderset_order_med_ids[patient_id][order_med_id] = 1

pkl.dump(orderset_order_med_ids, open("{0}/orderset_order_med_ids.pkl".format(DATADIR), "wb"))

print(orderset_order_med_ids)
# sanity check
# for patient_id, order_med_id_arr in orderset_order_med_ids.iteritems():
# 	if (len(order_med_id_arr) > 1):
# 		print(patient_id, len(order_med_id_arr))

# Procedures
orderset_order_proc_ids = {} # key: patient_id, second_key: order_proc_id associated with having been ordered from an orderset

DATA_QUERY = """ 
SELECT  
	soop.order_proc_id, 
	sop.pat_id
FROM 
	stride_orderset_order_proc AS soop
	JOIN 
		stride_order_proc AS sop 
	ON 
		soop.order_proc_id = sop.order_proc_id
WHERE 
	sop.ordering_date::DATE > DATE '2014-01-01'
	AND NOT section_name = 'Ad-hoc Orders'
;
"""
print(DATA_QUERY)

results = DBUtil.execute(DATA_QUERY);
for line in results:
	order_proc_id = int(line[0])
	patient_id = int(line[1])
	if (patient_id not in orderset_order_proc_ids.keys()):
		orderset_order_proc_ids[patient_id] = {}
	orderset_order_proc_ids[patient_id][order_proc_id] = 1

pkl.dump(orderset_order_proc_ids, open("{0}/orderset_order_proc_ids.pkl".format(DATADIR), "wb"))

print(orderset_order_proc_ids)
