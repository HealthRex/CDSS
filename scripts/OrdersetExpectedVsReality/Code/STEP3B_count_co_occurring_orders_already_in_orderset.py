"""
Find "A La Carte Orders": medications/procedures listed in order set that are more commonly ordered a la carte rather than with the order set
1) Find distinct orderset usage instances based on medication and procedure tables: result is a list of (patient_id, timestamp) "usage instances" for each orderset
2) Count co-occurring medications and procedures (e.g. labs) (BINARY, co-occur or not) that occur within a X minute window before/after the "usage instance" but NOT during; this requires counting from stride_order_med and stride_order_proc separately
3) Only include IDs that are already in the given order set in question
* To filter for just a la carte orders, we need to exclude all order_med_id/order_proc_ids that are from ordersets
"""
import glob
import sys, os
from cStringIO import StringIO
from datetime import datetime, timedelta
from dateutil import parser
import pickle as pkl
import time

os.chdir('/Users/jwang/Desktop/CDSS/medinfo/db')
from Const import RUNNER_VERBOSITY;
from Util import log;
from Util import DBTestCase;

os.chdir('/Users/jwang/Desktop/CDSS')
from medinfo.common.test.Util import MedInfoTestCase;
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery;
from medinfo.db.DBUtil import NUMBER, BOOLEAN, STRING, DATETIME;

year_intervals = [(2014, 2017)]
for tup in year_intervals:
	start_year = tup[0]
	end_year = tup[1]

	DATADIR = "/Users/jwang/Desktop/Chen/OrderSetOptimization/Results/{0}-{1}/".format(start_year, end_year)
	# ordersets_of_interest = ["625_ANE_PACU_(INPATIENT)_usage_instances.csv", "698_IP_MED_GENERAL__ADMIT_usage_instances.csv", "2457_IP_GEN_HEPARIN_PROTOCOLS_usage_instances.csv"] # use these as sanity check

	#######################################################################
	#                                                                     # 
	#    Load in Distinct Order Set Usage Instances and Orderset Orders   # 
	#                                                                     # 
	#######################################################################

	# Load distinct order set usage instances from medication and procedure tables
	orderset_instances = {} # key: orderset, value: instance = (patient_id, timestamp)

	# Load orderset order ids; need to explicitly exclude these in our co-occurrence counting
	orderset_order_med_ids = pkl.load(open("{0}/orderset_order_med_ids.pkl".format(DATADIR), "rb")) # key: patient_id, second_key: order_med_id associated with having been ordered from an orderset
	orderset_order_proc_ids = pkl.load(open("{0}/orderset_order_proc_ids.pkl".format(DATADIR), "rb")) # key: patient_id, second_key: order_proc_id associated with having been ordered from an orderset

	orderset_usage_instances_inf = open("{0}/orderset_usage_instances.csv".format(DATADIR), "rU")
	orderset_usage_instances_inf.readline()
	for line in orderset_usage_instances_inf:
		line = line.strip().split(",")
		orderset_id = int(line[0])
		orderset_name = "_".join(line[1].strip().split())
		orderset = "{0}_{1}".format(orderset_id, orderset_name)
		patient_id = line[2]
		timestamp = line[3]
		instance = (patient_id, timestamp)

		if (orderset not in orderset_instances):
			orderset_instances[orderset] = {instance:1,} # initialize map data structure
		else: 
			orderset_instances[orderset][instance] = 1

	# Load medication_ids and proc_codes associated with a given orderset; only these can be counted as "a la carte" items
	orderset_orders = pkl.load(open("{0}/orderset_orders.pkl".format(DATADIR), "rb")) # key: orderset_id, value: medication_id/proc_code

	#############################
	#                           # 
	#    Count Co-Occurrences   # 
	#                           # 
	#############################

	windows = [10, 60, 120] # minutes
	for window in windows:
		print("Starting a la carte counts counts for {0}-minute window...".format(window))
		order_description_map = {} # key: medication_id/proc_code, value: description

		for orderset in orderset_instances.keys():
			instances = orderset_instances[orderset].keys()
			num_instances = len(instances)
			
			co_occurrence_medication_counts = {} 
			print("Querying medication a la carte counts for orderset {0}...".format(orderset))
			instances_queried = 0

			for instance in instances:
				instances_queried += 1
				if (instances_queried % 1000 == 0):
					print(instances_queried)

				try:
					pat_id = int(instance[0])
					timestamp = parser.parse(instance[1])
				except:
					print("Unexpected error... skipping...")
					continue
				window_upper = timestamp + timedelta(minutes=window)
				window_lower = timestamp - timedelta(minutes=window)

				order_med_id_str = ""
				if (pat_id in orderset_order_med_ids.keys()):
					for order_med_id in orderset_order_med_ids[pat_id].keys():
						order_med_id_str += "'{0}', ".format(order_med_id)
					order_med_id_str = order_med_id_str[:-2]

				"""
				SELECT
					pat_id,
					medication_id,
					description,
					COUNT(*) as medication_co_occurrence
				FROM
					stride_order_med
				WHERE
					pat_id = {0} AND
					ordering_date > {1}-Xmin AND
					ordering_date < {1}+Xmin
				GROUP BY
					pat_id, medication_id, description
				"""
				DATA_QUERY = SQLQuery();
				DATA_QUERY.addSelect("pat_id")
				DATA_QUERY.addSelect("medication_id")
				DATA_QUERY.addSelect("description")
				DATA_QUERY.addSelect("COUNT(*) as medication_co_occurrence")

				DATA_QUERY.addFrom("stride_order_med")
				DATA_QUERY.addWhere("pat_id = '{0}'".format(pat_id))
				DATA_QUERY.addWhere("ordering_date >= '{0}'".format(window_lower))
				DATA_QUERY.addWhere("ordering_date <= '{0}'".format(window_upper))
				if (pat_id in orderset_order_med_ids.keys()):
					DATA_QUERY.addWhere("order_med_id NOT IN ({0})".format(order_med_id_str)) # do not count order instances ordered with an order set; we only want a la carte instances

				DATA_QUERY.addGroupBy("pat_id")
				DATA_QUERY.addGroupBy("medication_id")
				DATA_QUERY.addGroupBy("description")

				# print(DATA_QUERY)
				results = DBUtil.execute(DATA_QUERY);
				for line in results:
					medication = int(line[1])
					description = line[2]
					count = int(line[3])

					order_description_map[medication] = description.replace(",", ";")

					# consider only orders already in orderset
					if (orderset in orderset_orders and medication in orderset_orders[orderset].keys()): # medication is in order set
						if (medication not in co_occurrence_medication_counts):
							co_occurrence_medication_counts[medication] = 1 # binary, consider whether the order occurred in the given time window or not
						else:
							co_occurrence_medication_counts[medication] += 1

			outf = open("{0}/a_la_carte_orders_MEDICATIONS/{1}/{2}.csv".format(DATADIR, window, orderset.replace(" ", "_").replace("/", "_")), "w")
			outf.write("medication,description,order_type,a_la_carte_count,orderset_usage_count,ratio\n")

			for medication, co_occurrence in co_occurrence_medication_counts.iteritems():
				outf.write("{0},{1},medication,{2},{3},{4}\n".format(medication, order_description_map[medication], co_occurrence, num_instances, float(co_occurrence)/num_instances))
			outf.close()

		for orderset in orderset_instances.keys():
			instances = orderset_instances[orderset].keys()
			num_instances = len(instances)

			co_occurrence_procedure_counts = {}
			print("Querying procedure a la carte counts for orderset {0}...".format(orderset))
			instances_queried = 0

			for instance in instances:
				instances_queried += 1
				if (instances_queried % 1000 == 0):
					print(instances_queried)

				try:
					pat_id = int(instance[0])
					timestamp = parser.parse(instance[1])
				except:
					print("Unexpected error... skipping...")
					continue
				window_upper = timestamp + timedelta(minutes=window)
				window_lower = timestamp - timedelta(minutes=window)

				order_proc_id_str = ""
				if (pat_id in orderset_order_proc_ids.keys()):
					for order_proc_id in orderset_order_proc_ids[pat_id].keys():
						order_proc_id_str += "'{0}', ".format(order_proc_id)
					order_proc_id_str = order_proc_id_str[:-2]

				"""
				SELECT
					pat_id,
					proc_id,
					description,
					COUNT(*) as procedure_co_occurrence
				FROM
					stride_order_proc
				WHERE
					pat_id = {0} AND
					order_time >= {1}-Xmin AND
					order_time <= {1}+Xmin AND
					order_type IN ('Imaging', 'Blood Bank', 'Lab Panel', 'Microbiology', 'HIV Lab Restricted', 'Lab Only', 'Lab', 'Microbiology Culture', 'Point of Care Testing', 'ECHO')
				GROUP BY
					pat_id, proc_id, description
				"""
				DATA_QUERY = SQLQuery();
				DATA_QUERY.addSelect("pat_id")
				# DATA_QUERY.addSelect("proc_id")
				DATA_QUERY.addSelect("proc_code")
				DATA_QUERY.addSelect("description")
				DATA_QUERY.addSelect("order_type")
				DATA_QUERY.addSelect("COUNT(*) as procedure_co_occurrence")

				DATA_QUERY.addFrom("stride_order_proc")
				DATA_QUERY.addWhere("pat_id = '{0}'".format(pat_id))
				DATA_QUERY.addWhere("order_time >= '{0}'".format(window_lower))
				DATA_QUERY.addWhere("order_time <= '{0}'".format(window_upper))
				DATA_QUERY.addWhere("order_type IN  ('Imaging', 'Blood Bank', 'Lab Panel', 'Microbiology', 'HIV Lab Restricted', 'Lab Only', 'Lab', 'Microbiology Culture', 'Point of Care Testing', 'ECHO')")
				if (pat_id in orderset_order_proc_ids.keys()):
					DATA_QUERY.addWhere("order_proc_id NOT IN ({0})".format(order_proc_id_str)) # do not count order instances ordered with an order set

				DATA_QUERY.addGroupBy("pat_id")
				DATA_QUERY.addGroupBy("proc_code")
				DATA_QUERY.addGroupBy("description")
				DATA_QUERY.addGroupBy("order_type")

				# print(DATA_QUERY)
				results = DBUtil.execute(DATA_QUERY);
				for line in results:
					procedure = line[1]
					description = line[2].replace(",", ";")
					order_type = line[3]
					count = int(line[4])

					# if (order_type == "Blood Bank" and procedure not in ["LABBBPCRY", "LABBBPFFP", "LABBBPPLT", "LABBBPRBC"]): # filter irrelevant blood bank orders (e.g. nursing orders)
					# 	continue 

					order_description_map[procedure] = description

					# consider only orders already in orderset
					if (orderset in orderset_orders and procedure in orderset_orders[orderset].keys()): # procedure is in order set
						if (procedure not in co_occurrence_procedure_counts):
							co_occurrence_procedure_counts[procedure] = 1
						else:
							co_occurrence_procedure_counts[procedure] += 1

			outf = open("{0}/a_la_carte_orders_PROCEDURES/{1}/{2}.csv".format(DATADIR, window, orderset.replace(" ", "_").replace("/", "_")), "w")
			outf.write("procedure,description,order_type,a_la_carte_count,orderset_usage_count,ratio\n")

			for procedure, co_occurrence in co_occurrence_procedure_counts.iteritems():
				outf.write("{0},{1},{2},{3},{4},{5}\n".format(procedure, order_description_map[procedure], order_type, co_occurrence, num_instances, float(co_occurrence)/num_instances))
			outf.close()

