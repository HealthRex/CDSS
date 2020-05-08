"""Association Analysis for decaying windows class
Muthu Alagappan - March 28, 2016

Based on Decaying Windows concept from Mining of Massive Datasets textbook
http://infolab.stanford.edu/~ullman/mmds/ch4.pdf

Given a timeline of many years of data to analyze with AssociationAnalysis (co-occurrence counter),
learn the stats (count co-occurrences) just one chunk (delta, e.g., month) at a time.
After each delta learned, decay all of the stats/counts learned by a specified decay factor.
This has the effect of exponentially shrinking older data relevance compared to newer data.

Terms defined:
- Counts/Stats/Co-occurrences: Number of occurrences and co-occurrences of items and pairs of items in timeline
- Delta: Time period intervals to run AssociationAnalysis one at a time
- Decay: Scalar to decay all values learned each delta by, should be a value in (0.0,1.0)
- Window: Number of delta intervals to pass before expect counts to be decayed down to 1/e (~0.37). 
	Can use this to calculate decay factor = 1 - (1/window)
	Corresponds to T = Mean lifetime of the data relevance
	t(1/2) = Half-life of data relevance = T * ln(2)

Consider future upgrade. Don't train on total timeline, but train on two deltas at a time, 
sliding / shifting window so do catch the overlap ranges. 
Problem here is buffer based algorithm, won't be recording analyze_dates as go, 
so will end up with duplicate counts of items each month? Would have to keep analyzed patient_item_ids 
in buffer memory as well so know not to duplicate them.
"""


import sys, os
import time
import json
import psycopg2
from datetime import *
import logging

import unittest

from optparse import OptionParser
from medinfo.common.Util import stdOpen
from medinfo.cpoe.Env import DATE_FORMAT
from medinfo.db import DBUtil
from medinfo.cpoe.test import TestAssociationAnalysis
from medinfo.cpoe import AssociationAnalysis
from medinfo.cpoe.test.Const import RUNNER_VERBOSITY
from medinfo.cpoe.Const import DELTA_NAME_BY_SECONDS, SECONDS_PER_DAY;
from .Util import log;

class DecayAnalysisOptions:
	"""Simple struct to pass filter parameters on which records to do analysis on"""
	def __init__(self):
		self.startD = None
		self.endD = None
		self.windowLength = None
		self.patientIds = None
		self.decay = None
		self.delta = timedelta(weeks=4)
		self.associationsPerCommit = None
		self.itemsPerUpdate = None
		self.outputFile = None
		self.skipLargerCountWindows = True;	# If set, then won't try to update association count fields longer than the given delta time, since will never be a different number than the next largest interval count and just consumes extra memory


class DecayingWindows:
	"Class which implements AssociationAnalysis (i.e. builds clinical_item_association table) in a decaying windows manner, by taking in the appropriate parameters"

	def __init__(self):
		"Default constructor"
		self.connFactory = DBUtil.ConnectionFactory();  # Default connection source
		self.decayCount = 0

	def standardDecay (self, decayAnalysisOptions):
		conn = self.connFactory.connection()
		prefixes = ['', 'patient_', 'encounter_']
		times = ['0', '3600', '7200', '21600', '43200', '86400', '172800', '345600', '604800', '1209600', '2592000', '7776000', '15552000', '31536000', '63072000', '126144000', 'any']
		try:
			log.debug("Connected to datbase");
			curs = conn.cursor()

			fields = list()
			for prefix in prefixes:
				for time in times:
					fieldName = prefix + "count_" + str(time)
					fields.append(fieldName + '=' + fieldName + "*" + str(decayAnalysisOptions.decay))

			"""log.debug("starting to drop indices");
			sqlQuery = "ALTER TABLE clinical_item_association drop CONSTRAINT clinical_item_association_pkey;"
			curs.execute(sqlQuery)
			sqlQuery = "ALTER TABLE clinical_item_association drop CONSTRAINT clinical_item_association_clinical_item_fkey;"
			curs.execute(sqlQuery)
			sqlQuery = "ALTER TABLE clinical_item_association drop CONSTRAINT clinical_item_association_subsequent_item_fkey;"
			curs.execute(sqlQuery)
			sqlQuery = "ALTER TABLE clinical_item_association drop CONSTRAINT clinical_item_association_composite_key;"
			curs.execute(sqlQuery)
			sqlQuery = "DROP INDEX clinical_item_association_clinical_item_id;"
			curs.execute(sqlQuery)
			sqlQuery = "DROP INDEX clinical_item_association_subsequent_item_id;"
			curs.execute(sqlQuery)
			log.debug( "finished dropping indices" );
			"""

			log.debug("starting decay");
			sqlQuery = "UPDATE clinical_item_association SET " + str.join(',', fields) + ";"
			curs.execute(sqlQuery)
			log.debug("finished decay");

			"""log.debug("starting to add indices");
			sqlQuery = "ALTER TABLE clinical_item_association ADD CONSTRAINT clinical_item_association_pkey PRIMARY KEY (clinical_item_association_id);"
			curs.execute(sqlQuery)
			sqlQuery = "ALTER TABLE clinical_item_association ADD CONSTRAINT clinical_item_association_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id);"
			curs.execute(sqlQuery)
			sqlQuery = "ALTER TABLE clinical_item_association ADD CONSTRAINT clinical_item_association_subsequent_item_fkey FOREIGN KEY (subsequent_item_id) REFERENCES clinical_item(clinical_item_id);"
			curs.execute(sqlQuery)
			sqlQuery = "ALTER TABLE clinical_item_association ADD CONSTRAINT clinical_item_association_composite_key UNIQUE (clinical_item_id, subsequent_item_id);"
			curs.execute(sqlQuery)
			sqlQuery = "CREATE INDEX clinical_item_association_clinical_item_id ON clinical_item_association(clinical_item_id, subsequent_item_id);"
			curs.execute(sqlQuery)
			sqlQuery = "CREATE INDEX clinical_item_association_subsequent_item_id ON clinical_item_association(subsequent_item_id, clinical_item_id);"
			curs.execute(sqlQuery)
			log.debug("finished adding indices");
			"""

			conn.commit()
			log.debug("finished commit");
		finally:
			curs.close()
			conn.close()

	def decayAnalyzePatientItems(self, decayAnalysisOptions):
		log.debug("delta = %s" % decayAnalysisOptions.delta);

		# Derive decay scalar based on window length if not directly set
		if decayAnalysisOptions.decay is None:
			decayAnalysisOptions.decay = 1-(1.0/decayAnalysisOptions.windowLength) #decay rate = (1 - (1/c)), where c = window length

		currentBuffer = None;	# In memory buffer if using temp files. Otherwise, use the database as the data cache
		if decayAnalysisOptions.outputFile is not None:
			currentBuffer = dict();

		#####
		# Step one delta (e.g., month) at a time until end date
		#####
		currentItemStart = decayAnalysisOptions.startD 
		currentItemEnd = currentItemStart + decayAnalysisOptions.delta
		
		#Keep running the Analysis until you reach the end date
		while currentItemStart < decayAnalysisOptions.endD:

			log.debug(currentItemStart);
			log.debug(currentItemEnd);

			instance = AssociationAnalysis.AssociationAnalysis()
			analysisOptions = AssociationAnalysis.AnalysisOptions()

			if decayAnalysisOptions.outputFile is not None:
				analysisOptions.bufferFile = decayAnalysisOptions.outputFile

			# Decay any existing stats before learn new ones to increment
			if currentBuffer is None:
				self.standardDecay(decayAnalysisOptions)
			else:
				log.debug("buffer decay");
				currentBuffer = instance.bufferDecay(currentBuffer, decayAnalysisOptions.decay)
			self.decayCount +=1

			#Add in a new delta worth of training
			instance.associationsPerCommit = decayAnalysisOptions.associationsPerCommit
			instance.itemsPerUpdate = decayAnalysisOptions.itemsPerUpdate
			log.debug(instance.associationsPerCommit);
			log.debug(instance.itemsPerUpdate);

			analysisOptions.patientIds = decayAnalysisOptions.patientIds
			analysisOptions.startDate = currentItemStart;
			analysisOptions.endDate = currentItemEnd

			# Decide which count fields to update
			if decayAnalysisOptions.skipLargerCountWindows:
				deltaSeconds = decayAnalysisOptions.delta.total_seconds();
				
				# Look for smallest value that is still larger than the given delta.
				smallestLargerDeltaOption = sys.maxsize;	
				for secondsOption in DELTA_NAME_BY_SECONDS.keys():
					if secondsOption > deltaSeconds:
						smallestLargerDeltaOption = min(secondsOption, smallestLargerDeltaOption);

				# Tell the AssociationAnalysis to only accrue data for time ranges within the size of the delta period specified
				analysisOptions.deltaSecondsOptions = list();
				for secondsOption in DELTA_NAME_BY_SECONDS.keys():
					if secondsOption <= smallestLargerDeltaOption:
						analysisOptions.deltaSecondsOptions.append(secondsOption);

			log.debug("starting new delta");
			log.debug(analysisOptions.startDate);
			log.debug(analysisOptions.endDate);
			instance.analyzePatientItems(analysisOptions) #if an outputFile has been set, it will automatically output buffer to the file
			log.debug("finished new delta");

			# if you have been doing everything in memory, then load the latest buffer from Analysis Options and merge it with your current buffer
			if currentBuffer is not None:
				bufferOneDelta = instance.loadUpdateBufferFromFile(decayAnalysisOptions.outputFile)
				currentBuffer = instance.mergeBuffers(currentBuffer, bufferOneDelta)
				log.debug("finished merge");

			#Increment dates to next four weeks
			currentItemStart = currentItemEnd
			currentItemEnd = currentItemStart + decayAnalysisOptions.delta

		log.debug("Total number of decays: " + str(self.decayCount) );
		
		# Commit to database if have been doing everything in memory. (If not, then have already been commiting to database incrementally)
		if currentBuffer is not None:
			finalCommitBufferFileName = "finalCommitBuffer.txt"

			if os.path.exists(decayAnalysisOptions.outputFile):
				os.remove(decayAnalysisOptions.outputFile)

			instance.saveBufferToFile(finalCommitBufferFileName, currentBuffer)
			del currentBuffer #deleting the buffer to save memory, because commitUpdateBufferFromFile will need the memory equivalent of one new buffer
			instance.commitUpdateBufferFromFile(str(finalCommitBufferFileName))

			# Comment out if want the file to remain so can commit separetely or for debugging
			if os.path.exists(finalCommitBufferFileName):
				os.remove(finalCommitBufferFileName)

		log.debug("finished process");

	def main (self, argv):
		"""Main method, callable from command line"""
		usageStr =  "usage: %prog [options] <patientIds>\n"+\
					"   <patientIds>    Comma-separated list of patient IDs to run the analysis on, or use option to specify a file.\n"
		parser = OptionParser(usage=usageStr)
		parser.add_option("-i", "--idFile", dest="idFile", help="If provided, look for patient IDs in then named file, one ID per line, in the format '/Users/Muthu/Desktop/JonathanChen/patientlist.txt'")
		parser.add_option("-s", "--startDate", dest="startDate", metavar="<startDate>",  help="Date string (e.g., 2011-12-15), must be provided, will start analysis on items occuring on or after this date.");
		parser.add_option("-e", "--endDate", dest="endDate", metavar="<endDate>",  help="Date string (e.g., 2011-12-15), must be provided, will stop analysis on items occuring before this date.");
		parser.add_option("-w", "--window", type="int", dest="window", metavar="<window>",  help="Window integer (e.g., 36), (unit is deltas, i.e. a window of 36 and a delta of 4 weeks means that after 36 x4 weeks, the data is decayed ~1/e ~ 0.37). More precisely, the window x delta is how long it will take for the data to decay to 38 percent of its original worth. Higher delta means it takes longer to decay. This number must be provided.");
		parser.add_option("-d", "--delta", type="int", dest="delta", metavar="<delta>",  help="Delta integer (e.g., 4), (unit of time is weeks, defaults to 4 weeks), define in what increments do you want to read in the data. After each increment/delta, it performs a decay.");
		parser.add_option("-a", "--associationsPerCommit", type="int", dest="associationsPerCommit", help="If provided, will commit incremental analysis results to the database when accrue this many association items.  Can help to avoid allowing accrual of too much buffered items whose runtime memory will exceed the 32bit 2GB program limit.")
		parser.add_option("-u", "--itemsPerUpdate", type="int", dest="itemsPerUpdate", help="If provided, when updating patient_item analyze_dates, will only update this many items at a time to avoid overloading MySQL query.")
		parser.add_option("-o", "--outputFile", dest="outputFile", help="If provided, send buffer to output file rather than commiting to database")
		(options, args) = parser.parse_args(argv[1:])

		decayAnalysisOptions = DecayAnalysisOptions()

		log.debug("starting process");

		#set start and end dates, item length (delta), and decay rate
		decayAnalysisOptions.startD = datetime.strptime(options.startDate, DATE_FORMAT) #makes a datetime object for the start and end date
		decayAnalysisOptions.endD = datetime.strptime(options.endDate, DATE_FORMAT)
		decayAnalysisOptions.windowLength = options.window #how many deltas in your window
		decayAnalysisOptions.delta = timedelta(weeks=options.delta)
		if options.associationsPerCommit is not None:
			decayAnalysisOptions.associationsPerCommit = options.associationsPerCommit
		if options.itemsPerUpdate is not None:	
			decayAnalysisOptions.itemsPerUpdate = options.itemsPerUpdate

		if options.delta != None:
			decayAnalysisOptions.delta = timedelta(weeks=(options.delta)) #length of one decay item

		if options.outputFile is not None:
			decayAnalysisOptions.outputFile = options.outputFile

		#set patientIds based on either a file input or args
		decayAnalysisOptions.patientIds = list()
		if len(args) > 0:
			decayAnalysisOptions.patientIds.extend(args[0].split(","))
		if options.idFile is not None:
			idFile = stdOpen(options.idFile)
			for line in idFile:
				decayAnalysisOptions.patientIds.append(line.strip())
		

		#quit if invalid parameters
		if decayAnalysisOptions.startD is None or decayAnalysisOptions.endD is None or options.window is None or options.window == 0 or decayAnalysisOptions.patientIds is None:
			parser.print_help()
			sys.exit(0)


		log.debug("global start and end date");
		log.debug(decayAnalysisOptions.startD, decayAnalysisOptions.endD, decayAnalysisOptions.windowLength);
		self.decayAnalyzePatientItems(decayAnalysisOptions)


if __name__== "__main__":

	instance = DecayingWindows()
	instance.main(sys.argv)
	