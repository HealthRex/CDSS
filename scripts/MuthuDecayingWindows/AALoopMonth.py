#Association Analysis for looping months
#Muthu Alagappan - March 24, 2016

import sys, os
import time
import psycopg2
from datetime import *
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
		print "Connected to database"    
		curs = conn.cursor()
		curs.execute("DELETE FROM clinical_item_association;") # clear the training table
		curs.execute("UPDATE patient_item SET analyze_date = null;") # reset the analyze_date column
		curs.execute("COPY (select distinct patient_id from patient_item where patient_id % 10 = 5) TO '/Users/Muthu/Desktop/JonathanChen/patientlist.txt'") #create a patient id list file
		conn.commit()
		curs.close()
		conn.close()
		print "Connection closed"	
	except psycopg2.DatabaseError, ex:
		print 'I am unable to connect the database: '
		print ex
		sys.exit(1)
	


	
	#####
	# Loop one month at a time until end date
	#####

	#set start and end dates, item length (delta), and decay rate
	startD = datetime.strptime("2012-01-01", DATE_FORMAT) #makes a datetime object for the start and end date
	endD = datetime.strptime("2012-03-05", DATE_FORMAT)
	delta = timedelta(weeks=4) #length of one decay item
	window = 36 #how many months in your window
	decay = 1-(1.0/window) #decay rate = (1 - (1/c)), where c = window length

	currentItemStart = startD #start and end for first iteration
	currentItemEnd = startD + delta

	#load and open the idFile, store it into patientIds (which is an object in analysisOptions)
	patientIdsList = list()
	idFile = stdOpen("/Users/Muthu/Desktop/JonathanChen/patientlist.txt")
	for line in idFile:
		patientIdsList.append(line.strip())

	
	#set sql statement constants
	prefixes = ['', 'patient_', 'encounter_']
	times = ['0', '3600', '7200', '21600', '43200', '86400', '172800', '345600', '604800', '1209600', '2592000', '7776000', '15552000', '31536000', '63072000', '126144000']
	firstIteration = 1

	#Keep running the Analysis until you reach the end date
	while currentItemEnd <= endD:

		print currentItemStart
		print currentItemEnd


		# Decay database, except at first iteration
		if firstIteration != 1:
			conn = None
			try:
				conn = psycopg2.connect ("dbname=medinfo user=Muthu host=localhost")
				print "connected to datbase"
				curs = conn.cursor()
			except psycopg2.DatabaseError, ex:
				print 'I am unable to connect the database: ' 
				print ex
				sys.exit(1)

			fields = list()

			for prefix in prefixes:
				for time in times:
					fieldName = prefix + "count_" + str(time)
					fields.append(fieldName + '=' + fieldName + "*" + str(decay))

			sqlQuery = "UPDATE clinical_item_association SET " + str.join(',', fields) + ";"
			print sqlQuery
			curs.execute(sqlQuery)

			conn.commit()
			curs.close()
			conn.close()
			print "Connection closed"

			''' Test code for only updating one column one time
			for field in fields:
				if c == 0:
					sqlQuery = "UPDATE clinical_item_association SET " + field
					print sqlQuery
					curs.execute(sqlQuery)
					c=1
				else:
					break 
			'''
		else:
			firstIteration = 0


		
		#Add in a new month worth of training
		instance = AssociationAnalysis.AssociationAnalysis()
		analysisOptions = AssociationAnalysis.AnalysisOptions()

		analysisOptions.patientIds = patientIdsList
		analysisOptions.startDate = currentItemStart
		analysisOptions.endDate = currentItemEnd

		instance.analyzePatientItems(analysisOptions)
		

		#Increment dates to next month
		currentItemStart = currentItemEnd + timedelta(days=1) #increment for next loop
		currentItemEnd = currentItemStart + delta
	





	