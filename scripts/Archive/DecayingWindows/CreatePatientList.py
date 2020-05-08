#Quick script to generate a random patient list
#Muthu Alagappan - March 29, 2016
# How to call it from command line:
# "python .../CreatePatientList.py 1 2 3 4 5 6 7 8 9 0" >> basically, you feed as arguments all the numbers of the files you want to create, then it creates one file for each number with the prefix "PatientIDs..."
# Then run StitchIDFiles.py to stitch it all together

import sys, os
import psycopg2
import logging

import unittest

from medinfo.common.Util import stdOpen
from medinfo.cpoe.test import TestAssociationAnalysis
from medinfo.cpoe import AssociationAnalysis
from medinfo.cpoe.test.Const import RUNNER_VERBOSITY

def getPatientList(idFile):
	conn = None
	try:
		conn = psycopg2.connect ("dbname=medinfo user=Muthu host=localhost") #connect to database
		print("Connected to database")    
		curs = conn.cursor()
		patientNumbers = sys.argv[1:]
		for number in patientNumbers:
			fileName = idFile[:-4] + str(number) + ".txt"
			fileNameQuery = "COPY (select distinct patient_id from patient_item where patient_id % 10 = " + str(number) +") TO '" + str(fileName) + "';"
			curs.execute(fileNameQuery)
			print("Patient ID file created to: " + fileName)
		conn.commit()
		curs.close()
		conn.close()
		print("Connection closed")	
	except psycopg2.DatabaseError as ex:
		print('I am unable to connect the database: ')
		print(ex)
		sys.exit(1)

# Does the same as above, except for the negative numbers
def getPatientListNegative(idFile):
	conn = None
	try:
		conn = psycopg2.connect ("dbname=medinfo user=Muthu host=localhost") #connect to database
		print("Connected to database")    
		curs = conn.cursor()
		patientNumbers = sys.argv[1:]
		for number in patientNumbers:
			fileName = idFile[:-4] + "Neg" + str(number) + ".txt"
			fileNameQuery = "COPY (select distinct patient_id from patient_item where patient_id % 10 = " + "-" + str(number) +") TO '" + str(fileName) + "';"
			curs.execute(fileNameQuery)
			print("Patient ID file created to: " + fileName)
		conn.commit()
		curs.close()
		conn.close()
		print("Connection closed")	
	except psycopg2.DatabaseError as ex:
		print('I am unable to connect the database: ')
		print(ex)
		sys.exit(1)

#getPatientList("/Users/Muthu/Desktop/JonathanChen/CDSS_checkedout/MuthuAnalysis/PatientIDFiles/patientIDs.txt")
getPatientListNegative("/Users/Muthu/Desktop/JonathanChen/CDSS_checkedout/MuthuAnalysis/PatientIDFiles/patientIDs.txt")