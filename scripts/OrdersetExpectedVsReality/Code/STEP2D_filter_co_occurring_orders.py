# Filter co-occurring orders to only consider ones with co-occurring probability > median ordering probability of associated order set
# And P-value (from Fisher Exact Test) < p_threshold defined below
# Aggregate all results in one master spreadsheet

import pickle as pkl
import glob
import sys, os
from cStringIO import StringIO
from datetime import datetime, timedelta
from dateutil import parser

# Counter (to obtain Bonferroni Correction denominator)
# denominator = 0 

# Load in median ordering probabilities
median_ordering_probabilities = pkl.load(open("median_ordering_probabilities.pkl", "rb"))
p_threshold = 0.05/114017 # Bonferroni Correction
print("Bonferroni Correction: P < {0}".format(p_threshold))

year_intervals = [(2014, 2017)]
for tup in year_intervals:
	start_year = tup[0]
	end_year = tup[1]

	# windows = [10, 60, 120] # minutes
	windows = [10]
	for window in windows:

		DATADIR = "/Users/jwang/Desktop/Chen/OrderSetOptimization/Results/{0}-{1}".format(start_year, end_year)
		outf = open("{0}/co_occurring_orders_FINAL/{1}/co_occurring_orders_filtered.csv".format(DATADIR, window), "w")
		outf.write("id_or_code,description,order_type,orderset_X,yes_co_occurrence_with_orderset_X_usage,no_co_occurrence_with_orderset_X_usage,yes_co_occurrence_with_any_orderset_usage,no_co_occurrence_with_any_orderset_usage,orderset_X_usage_count,co_occurring_probability_orderset_X,co_occurring_probability_any_orderset,p_value\n")

		# Iterate over intermediate co-occurrence statistics file
		for co_occurrence_file in glob.glob("{0}/co_occurring_orders_MASTER/{1}/*".format(DATADIR, window)):
			orderset_id = int(co_occurrence_file.split("/")[-1].split(".csv")[0].split("_")[0])

			if (orderset_id not in median_ordering_probabilities):
				continue # skip
			median_ordering_prob = median_ordering_probabilities[orderset_id]
			
			inf = open(co_occurrence_file, "rU")
			header = inf.readline()
			for raw_line in inf:
				line = raw_line.strip().split(",")
				p_value = float(line[-1])
				co_occurring_prob = float(line[-3])

				# denominator += 1

				if (co_occurring_prob > median_ordering_prob and p_value < p_threshold): # filter
					outf.write(raw_line)
		outf.close()
# print(denominator)


