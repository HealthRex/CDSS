# Filter a la carte orders; orders associated with order sets such that:
# Co-occuring probability a la carte > ordering probability with order set
import pickle as pkl
import glob
import sys, os
from io import StringIO
from datetime import datetime, timedelta
from dateutil import parser
import scipy.stats as stats

# Load in order set ordering probabilities
ordering_probabilities = {} # key = orderset ID, second_key = medication_id/order_proc, value = ordering probability
ordering_counts = {} # key = orderset ID, second_key = medication_id/order_proc, value = order count (from orderset)
orderset_usage_counts = {} # key = orderset ID, value = orderset usage count
orderset_names = {} # key = orderset id, value = orderset name

inf = open("orderset_ordering_probabilities.csv", "rU")
inf.readline()

for line in inf:
	line = line.strip().split(",")
	orderset_id = int(line[1])
	id_or_code = line[3].strip() # string
	if ("NA" in line[-1]):
		continue
	ordering_prob = float(line[-1])
	orderset_usage_count = int(line[-2])
	ordering_count = int(line[-3])

	if (orderset_id not in ordering_probabilities):
		ordering_probabilities[orderset_id] = {}
	ordering_probabilities[orderset_id][id_or_code] = ordering_prob

	if (orderset_id not in ordering_counts):
		ordering_counts[orderset_id] = {}
	ordering_counts[orderset_id][id_or_code] = ordering_count

	orderset_usage_counts[orderset_id] = orderset_usage_count

	orderset_names[orderset_id] = line[2]
inf.close()
# print(ordering_probabilities[832].values())

# Filter a la carte output
year_intervals = [(2014, 2017)]
for tup in year_intervals:
	start_year = tup[0]
	end_year = tup[1]

	windows = [10, 60, 120] # minutes
	for window in windows:

		DATADIR = "/Users/jwang/Desktop/Chen/OrderSetOptimization/Results/{0}-{1}".format(start_year, end_year)
		outf = open("{0}/a_la_carte_orders_FINAL/{1}/a_la_carte_orders_filtered.csv".format(DATADIR, window), "w")
		outf.write("orderset_id,orderset_name,id_or_code,description,order_type,a_la_carte_count,orderset_usage_count,a_la_carte_prob,ordering_count_from_orderset,ordering_prob_from_orderset,p_value\n")

		# Iterate over intermediate co-occurrence statistics file
		for a_la_carte_file in glob.glob("{0}/a_la_carte_orders_MEDICATIONS/{1}/*".format(DATADIR, window)) + glob.glob("{0}/a_la_carte_orders_PROCEDURES/{1}/*".format(DATADIR, window)):
			orderset_id = int(a_la_carte_file.split("/")[-1].split(".csv")[0].split("_")[0])

			if (orderset_id not in ordering_probabilities):
				continue # skip
			
			inf = open(a_la_carte_file, "rU")
			# print(a_la_carte_file)
			header = inf.readline()
			for raw_line in inf:
				line = raw_line.strip().split(",")
				id_or_code = str(line[0].strip())
				if (id_or_code not in ordering_probabilities[orderset_id]):
					continue
				ordering_count = int(ordering_counts[orderset_id][id_or_code])
				a_la_carte_count = int(line[-3])
				orderset_usage_count = int(orderset_usage_counts[orderset_id])
				a_la_carte_prob = float(line[-1])
				ordering_prob = float(ordering_probabilities[orderset_id][id_or_code])

				if (a_la_carte_prob > ordering_prob): # filter
					# compute P-value
					# print([[a_la_carte_count, ordering_count], [orderset_usage_count - a_la_carte_count, orderset_usage_count - ordering_count]])
					odds_ratio, p_value = stats.fisher_exact([[a_la_carte_count, ordering_count], [orderset_usage_count - a_la_carte_count, orderset_usage_count - ordering_count]])

					outf.write("{0},{1},{2},{3},{4},{5}\n".format(orderset_id, orderset_names[orderset_id], raw_line[:-1], ordering_count, ordering_prob, p_value))
		outf.close()