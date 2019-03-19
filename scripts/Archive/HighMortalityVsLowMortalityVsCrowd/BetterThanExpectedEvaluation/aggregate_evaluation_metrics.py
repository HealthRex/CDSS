import pickle
import sys
import numpy as np
"""
Understanding evaluation metrics:
1) Recall = Sensitivity = TP/(TP + FN)
2) Precision = PPV (Positive Predictive Value) = TP/(TP + FP)
3) F1-Score = (2 * precision * recall)/(precision + recall)
4) AU-ROC (c-statistic) = area under the ROC curve
"""

BASE_DIR = "/Users/jwang/Desktop/Chen/Top_vs_Bottom_Study/Results_Revisions/Analysis_Better_Than_Expected"
def parse_association_model_evaluation_output(inf, cohort):
	# Set up arrays to be pickled
	recall_arr = []
	precision_arr = []
	f1_arr = []
	auroc_arr = []

	inf.readline()
	inf.readline()

	auroc = None
	f1_score = None
	precision = None
	recall = None
	for line in inf:
		line = line.strip().split("\t")
		if (line[-3] != "None"):
			auroc = float(line[-3])
			auroc_arr.append(auroc)
		if (line[-9] != "None"):
			f1_score = float(line[-9])
			f1_arr.append(f1_score)
		if (line[-10] != "None"):
			precision = float(line[-10])
			precision_arr.append(precision)
		if (line[-11] != "None"):
			recall = float(line[-11])
			recall_arr.append(recall)

	# Output pickle arrays
	OUTPUT_DIR = "{0}/{1}_evaluation".format(BASE_DIR, cohort)

	pickle.dump(np.array(recall_arr), open("{0}/recall_arr.pkl".format(OUTPUT_DIR), "wb"))
	pickle.dump(np.array(precision_arr), open("{0}/precision_arr.pkl".format(OUTPUT_DIR), "wb"))
	pickle.dump(np.array(f1_arr), open("{0}/f1_arr.pkl".format(OUTPUT_DIR), "wb"))
	pickle.dump(np.array(auroc_arr), open("{0}/auroc_arr.pkl".format(OUTPUT_DIR), "wb"))

def parse_orderset_evaluation_output(inf, cohort="orderset"):
	# Set up arrays to be pickled
	recall_arr = []
	precision_arr = []
	f1_arr = []
	auroc_arr = []

	inf.readline()
	inf.readline()

	auroc = None
	f1_score = None
	precision = None
	recall = None
	for line in inf:
		line = line.strip().split("\t")
		if (line[-13] != "None"):
			auroc = float(line[-13])
			auroc_arr.append(auroc)
		if (line[-19] != "None"):
			f1_score = float(line[-19])
			f1_arr.append(f1_score)
		if (line[-20] != "None"):
			precision = float(line[-20])
			precision_arr.append(precision)
		if (line[-21] != "None"):
			recall = float(line[-21])
			recall_arr.append(recall)

	# Output pickle arrays
	OUTPUT_DIR = "{0}/{1}_evaluation".format(BASE_DIR, cohort)

	pickle.dump(np.array(recall_arr), open("{0}/recall_arr.pkl".format(OUTPUT_DIR), "wb"))
	pickle.dump(np.array(precision_arr), open("{0}/precision_arr.pkl".format(OUTPUT_DIR), "wb"))
	pickle.dump(np.array(f1_arr), open("{0}/f1_arr.pkl".format(OUTPUT_DIR), "wb"))
	pickle.dump(np.array(auroc_arr), open("{0}/auroc_arr.pkl".format(OUTPUT_DIR), "wb"))

crowd_inf = open("{0}/crowd_evaluation/recClassification.byOrderSets.ItemAssociationRecommender.PPV.tab".format(BASE_DIR), "rU")
parse_association_model_evaluation_output(crowd_inf, "crowd")

low_mortality_inf = open("{0}/low_mortality_evaluation/recClassification.byOrderSets.ItemAssociationRecommender.PPV.tab".format(BASE_DIR), "rU")
parse_association_model_evaluation_output(low_mortality_inf, "low_mortality")

high_mortality_inf = open("{0}/high_mortality_evaluation/recClassification.byOrderSets.ItemAssociationRecommender.PPV.tab".format(BASE_DIR), "rU")
parse_association_model_evaluation_output(high_mortality_inf, "high_mortality")

orderset_inf = open("{0}/orderset_evaluation/recClassification.byOrderSets.OrderSetUsage.tab".format(BASE_DIR), "rU")
parse_orderset_evaluation_output(orderset_inf, "orderset")
