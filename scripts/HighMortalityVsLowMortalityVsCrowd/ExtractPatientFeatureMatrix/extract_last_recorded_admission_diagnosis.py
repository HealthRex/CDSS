#!/usr/bin/env python
##########################################################################################
# Extract out each patient's last recored admission diagnosis (within 2008-2009 OR 2010-2013)
##########################################################################################
import sys, os
from cStringIO import StringIO
from datetime import datetime

os.chdir('/Users/jwang/Desktop/ClinicalDecisionMaker/medinfo/db')
from Const import RUNNER_VERBOSITY;
from Util import log;
from Util import DBTestCase;

os.chdir('/Users/jwang/Desktop/ClinicalDecisionMaker')
from medinfo.common.test.Util import MedInfoTestCase;
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery;
from medinfo.db.DBUtil import NUMBER, BOOLEAN, STRING, DATETIME;

# Create SCRIPT_FILE
SCRIPT_FILE = StringIO()
SCRIPT_FILE.write("psql stride jwang198")

# Load in top patient count diagnoses (we will only include these as binary covariates)
# select *
# from clinical_item
# where clinical_item_category_id = 2
# order by patient_count desc
DATA_QUERY = SQLQuery()
DATA_QUERY.addSelect("clinical_item_id")
DATA_QUERY.addSelect("name")
DATA_QUERY.addSelect("description")
DATA_QUERY.addSelect("patient_count")
DATA_QUERY.addFrom("clinical_item")
DATA_QUERY.addWhereEqual("patient_count > 0 and clinical_item_category_id", 2)
top_admission_diagnoses_f = open("/Users/jwang/Desktop/Results/top_admission_diagnoses.csv", "w")
top_admission_diagnoses = {}
top_admission_diagnoses_string = []

DBUtil.runDBScript(SCRIPT_FILE, False)
results = DBUtil.execute(DATA_QUERY);
top_admission_diagnoses_f.write("clinical_item_id,name,description,patient_count\n")
for line in results:
	top_admission_diagnoses_f.write("{0},{1},{2},{3}\n".format(line[0],line[1],line[2],line[3]))
	top_admission_diagnoses[line[0]] = line[2]
	top_admission_diagnoses_string.append(str(line[0]))
top_admission_diagnoses_f.close()
top_admission_diagnoses_string = ",".join(top_admission_diagnoses_string)
top_admission_diagnoses_string = "(" + top_admission_diagnoses_string + ")"
#print(top_admission_diagnoses)
#print(top_admission_diagnoses_string)

# Find admission diagnosis for all patients associated with last recorded admission: 2008-2009 dataset
dataset_8_9 = open("/Users/jwang/Desktop/Results/2008-2009_patient_feature_matrix_reordered.csv", "rU")
last_recorded_admission_diagnosis_8_9 = open("/Users/jwang/Desktop/Results/last_recorded_admission_diagnosis_8_9.csv", "w")
last_recorded_admission_diagnosis_8_9.write("patient_id,clinical_item_id,encounter_id,item_date\n")
header = dataset_8_9.readline()
patient_ids = {} # ensure uniqueness

for line in dataset_8_9:
	line = line.strip().split(",")
	if (line[0] not in patient_ids): # note that the first occurrence of the patient_id will denote the last recorded admission diagnosis as the input file is ordered in that fashion
		patient_ids[line[0]] = 1

		encounter_id = line[5]

		# Example Query
		# SELECT patient_id , clinical_item_id , encounter_id , item_date
		# FROM patient_item
		# WHERE clinical_item_id in (41802,41808,41798,41791,41806,41788,41797,41796,41787,41807,41795,41873,41801,41871,41792,41786,41794,41805,41803,41785,41804,41872,41878,42225,42312,41776,41759,41764,41774,41835,41760,41765,41831,41838,41754,41762,41833,41837,41820,41836,41839,41784,41779,41834,41772,41758,41783,41832,41809,41814,41763,41778,41822,41766,41781,41823,41769,41775,41773,41821,41830,41882,41889,41929,41921,41847,41860,41846,41883,41892,41890,41922,41841,41856,41869,41943,41844,41956,41957,41884,41865,41894,41857,41909,41891,41912,41864,41854,41855,41867,41881,41866,41870,41868,41946,41908,41916,41887,41880,41886,41917,41958,41885,41989,42019,41968,41975,41998,41997,42078,41980,41969,41982,41965,42081,42017,42016,41960,41987,42018,42033,41990,42038,42028,41964,42058,41973,42072,41963,42002,42031,42085,41959,42073,41983,42040,41974,41981,42099,42111,42127,42130,42151,42149,42091,42128,42143,42112,42150,42147,42096,42116,42090,42121,42122,42098,42140,42113,42102,42186,42187,42197,42233,42242,42226,42175,42202,42212,42243,42181,42194,42223,42219,42208,42173,42184,42185,42229,42222,42302,42276,42310,42336,42305,42253,42321,42246,42330,42260,42322,42329,42335,42415,42364,42431,42432,42440,42488,42551,42680,42815,42777,42062,42535,42108,41777,41852,42334,42297,42097,42433,42434,42211,41770,42042,42188,41949,42779,41771,42668,42883,42392,41903,42224,42068,42701,42594,42426) and encounter_id = %s ;
		DATA_QUERY = SQLQuery()
		DATA_QUERY.addSelect("patient_id")
		DATA_QUERY.addSelect("clinical_item_id")
		DATA_QUERY.addSelect("encounter_id")
		DATA_QUERY.addSelect('item_date')
		DATA_QUERY.addFrom("patient_item")
		DATA_QUERY.addWhereEqual("clinical_item_id in {0} and encounter_id".format(top_admission_diagnoses_string), int(line[5]))
		DBUtil.runDBScript(SCRIPT_FILE, False)
		results = DBUtil.execute(DATA_QUERY);
		#print(DATA_QUERY)

		for line in results:
			last_recorded_admission_diagnosis_8_9.write("{0},{1},{2},{3}\n".format(line[0],line[1],line[2],line[3]))

dataset_8_9.close()
last_recorded_admission_diagnosis_8_9.close()

# Find admission diagnosis for all patients associated with last recorded admission: 2010-2013 dataset
dataset_10_13 = open("/Users/jwang/Desktop/Results/2010-2013_patient_feature_matrix_reordered.csv", "rU")
last_recorded_admission_diagnosis_10_13 = open("/Users/jwang/Desktop/Results/last_recorded_admission_diagnosis_10_13.csv", "w")
last_recorded_admission_diagnosis_10_13.write("patient_id,clinical_item_id,encounter_id,item_date\n")
header = dataset_10_13.readline()
patient_ids = {} # ensure uniqueness

for line in dataset_10_13:
	line = line.strip().split(",")
	if (line[0] not in patient_ids): # note that the first occurrence of the patient_id will denote the last recorded admission diagnosis as the input file is ordered in that fashion
		patient_ids[line[0]] = 1

		encounter_id = line[5]

		DATA_QUERY = SQLQuery()
		DATA_QUERY.addSelect("patient_id")
		DATA_QUERY.addSelect("clinical_item_id")
		DATA_QUERY.addSelect("encounter_id")
		DATA_QUERY.addSelect('item_date')
		DATA_QUERY.addFrom("patient_item")
		DATA_QUERY.addWhereEqual("clinical_item_id in {0} and encounter_id".format(top_admission_diagnoses_string), int(line[5]))
		DBUtil.runDBScript(SCRIPT_FILE, False)
		results = DBUtil.execute(DATA_QUERY);
		#print(DATA_QUERY)

		for line in results:
			last_recorded_admission_diagnosis_10_13.write("{0},{1},{2},{3}\n".format(line[0],line[1],line[2],line[3]))

dataset_10_13.close()
last_recorded_admission_diagnosis_10_13.close()

	