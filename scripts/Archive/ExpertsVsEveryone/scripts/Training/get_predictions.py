#!/usr/bin/env python
##########################################################################################
# Call ItemRecommender internally
##########################################################################################

import urlparse;
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

# import ItemRecommender
from medinfo.cpoe.ItemRecommender import ItemAssociationRecommender, RecommenderQuery

NUM_DIAGNOSES = 200 # max number of top diagnoses to iterate through
NUM_ASSOCIATIONS = 5000 # max number of top associations to print out

# Create item_id to description map
print("Creating clinical_item_id to description map")
id2description = {}
clinical_items = open('/Users/jwang/Desktop/Results/clinical_items.csv', "rU")
clinical_items.readline()
for line in clinical_items:
	line = line.strip().split(",")
	clinical_item_id = line[0]
	description = " ".join(line[1:])
	id2description[clinical_item_id] = description

# Reopen diagnoses, from the top of the file
diagnoses = open('/Users/jwang/Desktop/Results/diagnoses_to_test.csv', "rU")
diagnoses.readline()

baseQueryStr = "&targetItemIds=&excludeItemIds=71052,71046,71054,71083,71045,71047&excludeCategoryIds=1,58,4,2,160,161,59,13,159,163,23,62,18,11,46,2&timeDeltaMax=86400&sortField=P-YatesChi2-NegLog&sortReverse=True&filterField1=prevalence<:&filterField2=PPV<:&filterField3=RR<:&filterField4=sensitivity<:&filterField5=P-YatesChi2<:&resultCount=4000&invertQuery=false&showCounts=true&countPrefix=patient_&aggregationMethod=weighted&cacheTime=0"
recommender = ItemAssociationRecommender()

diagnosis_count = 0 
for line in diagnoses:
	line = line.strip().split(",")
	clinical_item_id = line[0]
	description = " ".join(line[1:])
	queryStr = "queryItemIds=" + str(clinical_item_id) + baseQueryStr
	print('Finding Top Associations for "{0}"'.format(description))

	# Build RecommenderQuery
	query = RecommenderQuery();
	paramDict = dict(urlparse.parse_qsl(queryStr,True));
	query.parseParams(paramDict);

	# Call ItemRecommender
	recommendations = recommender(query)

	# Output to csv file
	description = description.replace("/",";")
	fname = str(clinical_item_id) + " " + str(description) + ".csv"
	outfname = open("/Users/jwang/Desktop/Results/item_associations_expert_unmatched/" + fname, "w")
	outfname.write("clinical_item_id,description,score,PPV,OR,prevalence,RR,P-YatesChi2\n")

	association_count = 0 
	for rec in recommendations:
		recommender.populateDerivedStats(rec, ["PPV","OR","prevalence","RR","P-YatesChi2"])

		outfname.write("{0},{1},{2},{3},{4},{5},{6},{7}\n".format(rec["clinical_item_id"], id2description[str(rec["clinical_item_id"])], 
			rec["score"],rec["PPV"],rec["OR"],rec["prevalence"],rec["RR"],rec["P-YatesChi2"]))
		association_count += 1
		if (association_count == NUM_ASSOCIATIONS):
			break

	diagnosis_count += 1
	if (diagnosis_count == NUM_DIAGNOSES):
		break


# Add more stats: look at main function
# displayFields = query.getDisplayFields();
# self.populateDerivedStats(resultModel, displayFields);

