# Compute median ordering probabilities for each orderset
# Can derive these thresholds from order set utilization spreadsheet (From Ron Li)
# Output as pickle array

import numpy as np
import pickle as pkl

median_ordering_probabilities = {} # key = orderset ID, value = median
ordering_probabilities = {} # key = orderset ID, value = array of ordering probabilities
inf = open("orderset_ordering_probabilities.csv", "rU")
inf.readline()

for line in inf:
	line = line.strip().split(",")
	orderset_id = int(line[1])
	if ("NA" in line[-1]):
		continue
	ordering_prob = float(line[-1])

	if (orderset_id not in ordering_probabilities):
		ordering_probabilities[orderset_id] = []
	ordering_probabilities[orderset_id].append(ordering_prob)
inf.close()

# compute median ordering probabilities
for orderset_id, ordering_prob_array in ordering_probabilities.iteritems():
	median_ordering_probabilities[orderset_id] = np.median(np.array(ordering_prob_array))

# print(median_ordering_probabilities)
pkl.dump(median_ordering_probabilities, open("median_ordering_probabilities.pkl", "wb"))
