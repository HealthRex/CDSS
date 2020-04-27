#Association Analysis for 1 month
#Muthu Alagappan - March 23, 2016

import sys, os
import time
import psycopg2
from datetime import datetime
import logging

import unittest

from medinfo.common.Util import stdOpen
from medinfo.cpoe.Env import DATE_FORMAT
from medinfo.cpoe.test import TestAssociationAnalysis
from medinfo.cpoe import AssociationAnalysis
from medinfo.cpoe.test.Const import RUNNER_VERBOSITY


if __name__=="__main__":

	#####
	# Run Test Association - (if you run this, make sure to reset Util.numConnections to 0)
	#####
	#unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(TestAssociationAnalysis.suite()) #line from __main__ of TestAssociationAnalysis.py
	

	#####
	# Delete contents of Clinical_Item_Association, reset analyze_date column in patient_item, and create list of patient IDs
	#####
	conn = None
	try:
		conn = psycopg2.connect ("dbname=medinfo user=Muthu host=localhost") #connect to database
		print("Connected to database")    
		curs = conn.cursor()
		curs.execute("DELETE FROM clinical_item_association;") # clear the training table
		curs.execute("UPDATE patient_item SET analyze_date = null;") # reset the analyze_date column
		curs.execute("COPY (select distinct patient_id from patient_item where patient_id % 10 = 5) TO '/Users/Muthu/Desktop/JonathanChen/patientlist.txt'") #create a patient id list file
		conn.commit()
		curs.close()
		conn.close()
		print("Connection closed")	
	except psycopg2.DatabaseError as ex:
		print('I am unable to connect the database: ' + ex)
		sys.exit(1)
	

	#####
	# Run AssociationAnalysis.py on one month of data
	#####
	instance = AssociationAnalysis.AssociationAnalysis()
	analysisOptions = AssociationAnalysis.AnalysisOptions()

	#load and open the idFile, store it into patientIds (which is an object in analysisOptions)
	analysisOptions.patientIds = list()
	idFile = stdOpen("/Users/Muthu/Desktop/JonathanChen/patientlist.txt")
	for line in idFile:
		analysisOptions.patientIds.append(line.strip())

	#store start date
	timeTuple = time.strptime("2012-01-01", DATE_FORMAT)
	analysisOptions.startDate = datetime(*timeTuple[0:3])

	#store end date
	timeTuple = time.strptime("2012-01-30", DATE_FORMAT)
	analysisOptions.endDate = datetime(*timeTuple[0:3])

	instance.analyzePatientItems(analysisOptions)
	

	#####
	# Decay the clinical_item_association table
	#####
	conn=None
	decay = 0.99
	
	try:
		conn = psycopg2.connect ("dbname=medinfo user=Muthu host=localhost")
		print("connected to datbase")
		curs = conn.cursor()
	except psycopg2.DatabaseError as ex:
		print('I am unable to connect the database: ' + ex)
		sys.exit(1)

	prefixes = ['', 'patient_', 'encounter_']
	times = ['0', '3600', '7200', '21600', '43200', '86400', '172800', '345600', '604800', '1209600', '2592000', '7776000', '15552000', '31536000', '63072000', '126144000']
	
	fields = list()

	for prefix in prefixes:
		for time in times:
			fieldName = prefix + "count_" + str(time)
			fields.append(fieldName + '=' + fieldName + "*" + str(decay))
	
	for field in fields:
		sqlQuery = "UPDATE clinical_item_association SET " + field
		print(sqlQuery)
		curs.execute(sqlQuery)

		 
	conn.commit()
	curs.close()
	conn.close()
	print("Connection closed")





	