# Aggregate co_occurrence results to create master spreadsheet with columns:
# procedure_code/medication_id, description, orderset_X, yes_co_occurrence_with_orderset_X_usage, no_co_occurrence_with_orderset_X_usage, yes_co_occurrence_with_any_orderset_usage, no_co_occurrence_with_any_orderset_usage, orderset_X_usage_count, co_occurring_probability_orderset_X, co_occurring_probability_any_orderset, p_value
import glob
import sys, os
from cStringIO import StringIO
from datetime import datetime, timedelta
from dateutil import parser
import numpy as np
import scipy.stats as stats

year_intervals = [(2014, 2017)]
for tup in year_intervals:
	start_year = tup[0]
	end_year = tup[1]

	# windows = [10, 60, 120] # minutes
	windows = [10]
	for window in windows:
		# initialize data structures; store four counts for contingency table
		co_occurrence_for_orderset_X_tracker = {} # first key = orderset X > second key = medication_id/proc_code, value = [yes, no] within co_occurrence window of specific orderset X usage instance
		co_occurrence_for_any_orderset_tracker = {} # key = medication_id/proc_code, value = yes, within co_occurrence window of any orderset usage instance  
		orderset_usage_instances = {} # key = orderset X, value = orderset X usage instances
		descriptions = {} # key = medication_id/proc_code, value = description
		order_types = {} # key = medication_id/proc_code, value = order_type

		DATADIR = "/Users/jwang/Desktop/Chen/OrderSetOptimization/Results/{0}-{1}".format(start_year, end_year)

		# MEDICATIONS
		for medication_co_occurrence_file in glob.glob("{0}/co_occurring_orders_MEDICATIONS/{1}/*".format(DATADIR, window)):
			orderset = medication_co_occurrence_file.split("/")[-1].split(".csv")[0]

			inf = open(medication_co_occurrence_file, "rU")
			inf.readline()
			for line in inf:
				line = line.strip().split(",")
				medication_id = int(line[0])
				description = line[1]
				order_type = line[2]
				co_occurrence_count = int(line[3])
				orderset_usage_count = int(line[4])

				orderset_usage_instances[orderset] = orderset_usage_count
				descriptions[medication_id] = description
				order_types[medication_id] = order_type

				# update counts for orderset X tracker
				if (orderset not in co_occurrence_for_orderset_X_tracker):
					co_occurrence_for_orderset_X_tracker[orderset] = {}
				if (medication_id not in co_occurrence_for_orderset_X_tracker[orderset]):
					co_occurrence_for_orderset_X_tracker[orderset][medication_id] = [0,0]
				co_occurrence_for_orderset_X_tracker[orderset][medication_id][0] = co_occurrence_count # yes, medication co-occurred with orderset X
				co_occurrence_for_orderset_X_tracker[orderset][medication_id][1] = orderset_usage_count - co_occurrence_count # no, medication did no co-occur with orderset X

				# update counts for all orderset tracker
				if (medication_id not in co_occurrence_for_any_orderset_tracker):
					co_occurrence_for_any_orderset_tracker[medication_id] = 0
				co_occurrence_for_any_orderset_tracker[medication_id] += co_occurrence_count # yes, medication co-occurred with orderset X 
			inf.close()

		# PROCEDURES
		for procedure_co_occurrence_file in glob.glob("{0}/co_occurring_orders_PROCEDURES/{1}/*".format(DATADIR, window)):
			orderset = procedure_co_occurrence_file.split("/")[-1].split(".csv")[0]

			inf = open(procedure_co_occurrence_file, "rU")
			inf.readline()
			for line in inf:
				line = line.strip().split(",")
				procedure_code = line[0]
				description = line[1]
				order_type = line[2]
				co_occurrence_count = int(line[3])
				orderset_usage_count = int(line[4])

				orderset_usage_instances[orderset] = orderset_usage_count
				descriptions[procedure_code] = description
				order_types[procedure_code] = order_type

				# update counts for orderset X tracker
				if (orderset not in co_occurrence_for_orderset_X_tracker):
					co_occurrence_for_orderset_X_tracker[orderset] = {}
				if (procedure_code not in co_occurrence_for_orderset_X_tracker[orderset]):
					co_occurrence_for_orderset_X_tracker[orderset][procedure_code] = [0,0]
				co_occurrence_for_orderset_X_tracker[orderset][procedure_code][0] = co_occurrence_count # yes, procedure co-occurred with orderset X
				co_occurrence_for_orderset_X_tracker[orderset][procedure_code][1] = orderset_usage_count - co_occurrence_count # no, procedure did no co-occur with orderset X

				# update counts for all orderset tracker
				if (procedure_code not in co_occurrence_for_any_orderset_tracker):
					co_occurrence_for_any_orderset_tracker[procedure_code] = 0
				co_occurrence_for_any_orderset_tracker[procedure_code] += co_occurrence_count # yes, procedure co-occurred with orderset X 
			inf.close()

		# compute total orderset usage instances
		total_order_set_usage_instances = np.sum(np.array(orderset_usage_instances.values()))

		# output files
		for orderset, co_occurrence_map in co_occurrence_for_orderset_X_tracker.iteritems():
			outf = open("{0}/co_occurring_orders_MASTER/{1}/{2}.csv".format(DATADIR, window, orderset), "w")
			outf.write("id_or_code,description,order_type,orderset_X,yes_co_occurrence_with_orderset_X_usage,no_co_occurrence_with_orderset_X_usage,yes_co_occurrence_with_any_orderset_usage,no_co_occurrence_with_any_orderset_usage,orderset_X_usage_count,co_occurring_probability_orderset_X,co_occurring_probability_any_orderset,p_value\n")

			for id_or_code, co_occurrence_counts in co_occurrence_map.iteritems():
				yes_orderset_X = co_occurrence_for_orderset_X_tracker[orderset][id_or_code][0] # medication co-occurred within window of orderset X usage instance
				no_orderset_X = co_occurrence_for_orderset_X_tracker[orderset][id_or_code][1] # medication did not co-occur within window of orderset X usage instance
				yes_any_orderset = co_occurrence_for_any_orderset_tracker[id_or_code] # medication co-occurred within window of any orderset usage instance
				no_any_orderset = total_order_set_usage_instances - co_occurrence_for_any_orderset_tracker[id_or_code] # medication did not co-occur within window of any orderset usage instance

				# compute P-value
				oddsratio, pvalue = stats.fisher_exact([[yes_orderset_X, no_orderset_X], [yes_any_orderset, no_any_orderset]])

				outf.write("{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11}\n".format(
					id_or_code, descriptions[id_or_code], order_types[id_or_code], orderset, yes_orderset_X, no_orderset_X, yes_any_orderset,
					no_any_orderset, orderset_usage_instances[orderset], float(yes_orderset_X)/(yes_orderset_X + no_orderset_X), 
					float(yes_any_orderset)/(yes_any_orderset+no_any_orderset), pvalue))
			outf.close()

