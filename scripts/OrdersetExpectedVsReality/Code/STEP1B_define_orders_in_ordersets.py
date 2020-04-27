"""
Find orders associated with each given orderset; output as a pickled map
"""
import glob
import sys, os
from io import StringIO
from datetime import datetime, timedelta
from dateutil import parser
import pickle as pkl

DATADIR = "/Users/jwang/Desktop/Chen/OrderSetOptimization/Results/2014-2017"

# Find medication_ids and proc_codes associated with a given orderset; these cannot be counted as "co-occurring" items
orderset_orders = {} # key: orderset_id, value: medication_id/proc_code

for medication_instances_file in glob.glob("{0}/orderset_order_pairings_MEDICATIONS/*".format(DATADIR)):
	inf = open(medication_instances_file, "rU")
	inf.readline()
	for line in inf:
		line = line.strip().split(",")
		medication_id = int(line[2])
		orderset_id = int(line[3])
		orderset_name = "_".join(line[4].strip().split())
		orderset = "{0}_{1}".format(orderset_id, orderset_name)

		if (orderset not in orderset_orders):
			orderset_orders[orderset] = {medication_id:1,} # initialize map data structure
		else:
			orderset_orders[orderset][medication_id] = 1

for procedure_instances_file in glob.glob("{0}/orderset_order_pairings_PROCEDURES/*".format(DATADIR)):
	# if (procedure_instances_file.strip().split("/")[-1] not in ordersets_of_interest):
	# 	continue

	inf = open(procedure_instances_file, "rU")
	inf.readline()
	for line in inf:
		line = line.strip().split(",")
		procedure_code = line[2]
		orderset_id = int(line[3])
		orderset_name = "_".join(line[4].strip().split())
		orderset = "{0}_{1}".format(orderset_id, orderset_name)

		if (orderset not in orderset_orders):
			orderset_orders[orderset] = {procedure_code:1,} # initialize map data structure
		else:
			orderset_orders[orderset][procedure_code] = 1

# Output pickle file
# print(orderset_orders)
pkl.dump(orderset_orders, open("{0}/orderset_orders.pkl".format(DATADIR), "wb"))

	