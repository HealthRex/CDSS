#!/usr/bin/env python
"""Test case for respective module in application package, created by Muthu on April 4, 2016 to test DecayingWindows.py"""


import sys, os
from cStringIO import StringIO
from datetime import *
import unittest
import time

from Const import RUNNER_VERBOSITY;
from Util import log;

from medinfo.db.test.Util import DBTestCase;

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel;
from medinfo.cpoe.DecayingWindows import DecayingWindows, DecayAnalysisOptions;
#from medinfo.cpoe.ResetModel import ResetModel;
from medinfo.cpoe.DataManager import DataManager;

from medinfo.cpoe.AssociationAnalysis import AssociationAnalysis, AnalysisOptions;

TEMP_FILENAME = "DWTemp.txt";

class TestDecayingWindows(DBTestCase):
	def setUp(self):
		"""Prepare state for test cases"""
		DBTestCase.setUp(self);

		log.info("Populate the database with test data")

		self.clinicalItemCategoryIdStrList = list();
		headers = ["clinical_item_category_id","source_table"];
		dataModels = \
			[
				RowItemModel( [-1, "Labs"], headers ),
				RowItemModel( [-2, "Imaging"], headers ),
				RowItemModel( [-3, "Meds"], headers ),
				RowItemModel( [-4, "Nursing"], headers ),
				RowItemModel( [-5, "Problems"], headers ),
				RowItemModel( [-6, "Lab Results"], headers ),
			];
		for dataModel in dataModels:
			(dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item_category", dataModel );
			self.clinicalItemCategoryIdStrList.append( str(dataItemId) );

		headers = ["clinical_item_id","clinical_item_category_id","name","analysis_status"];
		dataModels = \
			[
				RowItemModel( [-1, -1, "CBC",1], headers ),
				RowItemModel( [-2, -1, "BMP",0], headers ), # Clear analysis status, so this will be ignored unless changed
				RowItemModel( [-3, -1, "Hepatic Panel",1], headers ),
				RowItemModel( [-4, -1, "Cardiac Enzymes",1], headers ),
				RowItemModel( [-5, -2, "CXR",1], headers ),
				RowItemModel( [-6, -2, "RUQ Ultrasound",1], headers ),
				RowItemModel( [-7, -2, "CT Abdomen/Pelvis",1], headers ),
				RowItemModel( [-8, -2, "CT PE Thorax",1], headers ),
				RowItemModel( [-9, -3, "Acetaminophen",1], headers ),
				RowItemModel( [-10, -3, "Carvedilol",1], headers ),
				RowItemModel( [-11, -3, "Enoxaparin",1], headers ),
				RowItemModel( [-12, -3, "Warfarin",1], headers ),
				RowItemModel( [-13, -3, "Ceftriaxone",1], headers ),
				RowItemModel( [-14, -4, "Foley Catheter",1], headers ),
				RowItemModel( [-15, -4, "Strict I&O",1], headers ),
				RowItemModel( [-16, -4, "Fall Precautions",1], headers ),
			];
		for dataModel in dataModels:
			(dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item", dataModel );

		headers = ["patient_item_id","encounter_id","patient_id","clinical_item_id","item_date"];
		dataModels = \
			[
				RowItemModel( [-1,  -111,   -11111, -4,  datetime(2000, 1, 1, 0)], headers ),
				RowItemModel( [-2,  -111,   -11111, -10, datetime(2000, 1, 1, 0)], headers ),
				RowItemModel( [-3,  -111,   -11111, -8,  datetime(2000, 1, 1, 2)], headers ),
				RowItemModel( [-4,  -112,   -11111, -10, datetime(2000, 1, 2, 0)], headers ),
				RowItemModel( [-5,  -112,   -11111, -12, datetime(2000, 2, 1, 0)], headers ),
				RowItemModel( [-10, -222,   -22222, -7,  datetime(2000, 1, 5, 0)], headers ),
				RowItemModel( [-12, -222,   -22222, -6,  datetime(2000, 1, 9, 0)], headers ),
				RowItemModel( [-13, -222,   -22222, -11, datetime(2000, 1, 9, 0)], headers ),
				RowItemModel( [-95, -222,   -22222, -9,  datetime(2000, 1,10, 0)], headers ),
				RowItemModel( [-94, -333,   -33333, -8,  datetime(2000, 1,10, 0)], headers ),	# In first window delta unit only
				RowItemModel( [-14, -333,   -33333, -6,  datetime(2000, 2, 9, 0)], headers ),
				RowItemModel( [-15, -333,   -33333, -2,  datetime(2000, 2,11, 0)], headers ),  # Will set clinical_item_link inheritances to this item to only record certain associations
				RowItemModel( [-16, -333,   -33333, -11, datetime(2000, 2,11, 0)], headers ),
			];
		for dataModel in dataModels:
			(dataItemId, isNew) = DBUtil.findOrInsertItem("patient_item", dataModel );


		headers = ["clinical_item_id","linked_item_id"];
		dataModels = \
			[   # Don't have direct, but instead demonstrate inherited relationship from 6 to 2 will still be recognized
				RowItemModel( [-6, -4], headers ),
				RowItemModel( [-4, -2], headers ),
			];
		for dataModel in dataModels:
			(dataItemId, isNew) = DBUtil.findOrInsertItem("clinical_item_link", dataModel );

		self.decayAnalyzer = DecayingWindows() # DecayingWindows instance to test on, *** remember to change database to medinfo_copy
		self.dataManager = DataManager();

	def tearDown(self):
		"""Restore state from any setUp or test steps"""
		log.info("Purge test records from the database")

		DBUtil.execute("delete from clinical_item_link where clinical_item_id < 0");
		DBUtil.execute("delete from clinical_item_association where clinical_item_id < 0");
		DBUtil.execute("delete from patient_item where patient_item_id < 0");
		DBUtil.execute("delete from clinical_item where clinical_item_id < 0");
		DBUtil.execute("delete from clinical_item_category where clinical_item_category_id in (%s)" % str.join(",", self.clinicalItemCategoryIdStrList) );

		# Purge temporary buffer files. May not match exact name if modified for other purpose
		for filename in os.listdir("."):
			if filename.startswith(TEMP_FILENAME):
				os.remove(filename);

		DBTestCase.tearDown(self);

	def test_decayingWindowsFromBuffer(self):

		associationQuery = \
			"""
			select
				clinical_item_id, subsequent_item_id,
				count_0, count_3600, count_86400, count_604800,
				count_2592000, count_7776000, count_31536000,
				count_any
			from
				clinical_item_association
			where
				clinical_item_id < 0
			order by
				clinical_item_id, subsequent_item_id
			""";

		decayAnalysisOptions = DecayAnalysisOptions()
		decayAnalysisOptions.startD = datetime(2000,1,9)
		decayAnalysisOptions.endD = datetime(2000,2,11)
		#decayAnalysisOptions.windowLength = 10
		decayAnalysisOptions.decay = 0.9
		decayAnalysisOptions.delta = timedelta(weeks=4)
		decayAnalysisOptions.patientIds = [-22222, -33333]
		decayAnalysisOptions.outputFile = TEMP_FILENAME;

		self.decayAnalyzer.decayAnalyzePatientItems(decayAnalysisOptions)

		expectedAssociationStats = \
			[
				[-11,-11,   1.9, 1.9, 1.9, 1.9, 1.9, 0, 0, 1.9],	# Note that decaying windows approach will not try to update counts for time periods longer than the delta period
				[-11, -9,   0.0, 0.0, 0.9, 0.9, 0.9, 0, 0, 0.9],
				[-11, -8,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0], 	# 8 not in same delta as other items so co-occurence not gettign counted. Consider future upgrade. Don't train on all time ever, but train on two deltas at a time, sliding / shifting window so do catch the overlap ranges
				[-11, -6,   0.9, 0.9, 0.9, 0.9, 0.9, 0, 0, 0.9],
				[ -9,-11,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0],
				[ -9, -9,   0.9, 0.9, 0.9, 0.9, 0.9, 0, 0, 0.9],
				[ -9, -8,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0],
				[ -9, -6,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0],
				[ -8,-11,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0], 	# 8 not in same delta as other items so co-occurence not gettign counted.
				[ -8, -9,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0], 	# 8 not in same delta as other items so co-occurence not gettign counted.
				[ -8, -8,   0.9, 0.9, 0.9, 0.9, 0.9, 0, 0, 0.9],
				[ -8, -6,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0], 	# 8 not in same delta as other items so co-occurence not gettign counted.
				[ -6,-11,   0.9, 0.9, 0.9, 1.9, 1.9, 0, 0, 1.9],
				[ -6, -9,   0.0, 0.0, 0.9, 0.9, 0.9, 0, 0, 0.9],
				[ -6, -8,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0], 	# 8 not in same delta as other items so co-occurence not gettign counted.
				[ -6, -6,   1.9, 1.9, 1.9, 1.9, 1.9, 0, 0, 1.9],
			];

		associationStats = DBUtil.execute(associationQuery);
		#for row in expectedAssociationStats:
		#	print >> sys.stderr, row;
		#print >> sys.stderr, "============"
		#for row in associationStats:
		#	print >> sys.stderr, row;
		#print >> sys.stderr, "============"
		self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 );

		expectedItemBaseCountById = \
			{
				-1: 0,
				-2: 0,
				-3: 0,
				-4: 0,
				-5: 0,
				-6: 1.9,
				-7: 0,
				-8: 0.9,
				-9: 0.9,
				-10: 0,
				-11: 1.9,
				-12: 0,
				-13: 0,
				-14: 0,
				-15: 0,
				-16: 0,
			}
		itemBaseCountById = self.dataManager.loadClinicalItemBaseCountByItemId();
		#print >> sys.stderr, itemBaseCountById;
		self.assertEqualDict(expectedItemBaseCountById, itemBaseCountById);


		######## Reset the model data and rerun with different decay parameters
		self.dataManager.resetAssociationModel()

		decayAnalysisOptions = DecayAnalysisOptions()
		decayAnalysisOptions.startD = datetime(2000,1,9)
		decayAnalysisOptions.endD = datetime(2000,2,11)
		decayAnalysisOptions.windowLength = 4;	# Just specify window length, then should calculate decay parameter
		#decayAnalysisOptions.decay = 0.9
		decayAnalysisOptions.delta = timedelta(weeks=4)
		decayAnalysisOptions.patientIds = [-22222, -33333]
		decayAnalysisOptions.outputFile = TEMP_FILENAME;

		self.decayAnalyzer.decayAnalyzePatientItems(decayAnalysisOptions)

		expectedAssociationStats = \
			[
				[-11,-11,   1.75, 1.75, 1.75, 1.75, 1.75, 0, 0, 1.75],
				[-11, -9,   0.0, 0.0, 0.75, 0.75, 0.75, 0, 0, 0.75],
				[-11, -8,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0],
				[-11, -6,   0.75, 0.75, 0.75, 0.75, 0.75, 0, 0, 0.75],
				[ -9,-11,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0],
				[ -9, -9,   0.75, 0.75, 0.75, 0.75, 0.75, 0, 0, 0.75],
				[ -9, -8,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0],
				[ -9, -6,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0],
				[ -8,-11,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0],
				[ -8, -9,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0],
				[ -8, -8,   0.75, 0.75, 0.75, 0.75, 0.75, 0, 0, 0.75],
				[ -8, -6,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0],
				[ -6,-11,   0.75, 0.75, 0.75, 1.75, 1.75, 0, 0, 1.75],
				[ -6, -9,   0.0, 0.0, 0.75, 0.75, 0.75, 0, 0, 0.75],
				[ -6, -8,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0],
				[ -6, -6,   1.75, 1.75, 1.75, 1.75, 1.75, 0, 0, 1.75],
			];

		associationStats = DBUtil.execute(associationQuery);
		#for row in expectedAssociationStats:
		#	print >> sys.stderr, row;
		#print >> sys.stderr, "============"
		#for row in associationStats:
		#	print >> sys.stderr, row;
		#print >> sys.stderr, "============"
		self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 );

		expectedItemBaseCountById = \
			{
				-1: 0,
				-2: 0,
				-3: 0,
				-4: 0,
				-5: 0,
				-6: 1.75,
				-7: 0,
				-8: 0.75,
				-9: 0.75,
				-10: 0,
				-11: 1.75,
				-12: 0,
				-13: 0,
				-14: 0,
				-15: 0,
				-16: 0,
			}
		itemBaseCountById = self.dataManager.loadClinicalItemBaseCountByItemId(acceptCache=False);	# Don't use cache, otherwise will get prior results
		#print >> sys.stderr, itemBaseCountById;
		self.assertEqualDict(expectedItemBaseCountById, itemBaseCountById);


	def test_decayingWindows(self):
		# Muthu's function to test DecayingWindows module

		associationQuery = \
			"""
			select
				clinical_item_id, subsequent_item_id,
				patient_count_0, patient_count_3600, patient_count_86400, patient_count_604800,
				patient_count_2592000, patient_count_7776000, patient_count_31536000,
				patient_count_any
			from
				clinical_item_association
			where
				clinical_item_id < 0
			order by
				clinical_item_id, subsequent_item_id
			""";


		decayAnalysisOptions = DecayAnalysisOptions()
		decayAnalysisOptions.startD = datetime(2000,1,9)
		decayAnalysisOptions.endD = datetime(2000,2,11)
		decayAnalysisOptions.windowLength = 10
		decayAnalysisOptions.decay = 0.9
		decayAnalysisOptions.delta = timedelta(weeks=4)
		decayAnalysisOptions.patientIds = [-22222, -33333]

		self.decayAnalyzer.decayAnalyzePatientItems (decayAnalysisOptions)

		expectedAssociationStats = \
			[
				[-11,-11,   1.9, 1.9, 1.9, 1.9, 1.9, 0, 0, 1.9],	# Note that decaying windows approach will not try to update counts for time periods longer than the delta period
				[-11, -9,   0.0, 0.0, 0.9, 0.9, 0.9, 0, 0, 0.9],
				[-11, -8,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0], 	# 8 not in same delta as other items so co-occurence not gettign counted. Consider future upgrade. Don't train on all time ever, but train on two deltas at a time, sliding / shifting window so do catch the overlap ranges. Problem here is buffer based algorithm, won't be recording analyze_dates as go, so will end up with duplicate counts of items each month?
				[-11, -6,   0.9, 0.9, 0.9, 0.9, 0.9, 0, 0, 0.9],
				[ -9,-11,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0],
				[ -9, -9,   0.9, 0.9, 0.9, 0.9, 0.9, 0, 0, 0.9],
				[ -9, -8,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0],
				[ -9, -6,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0],
				[ -8,-11,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0], 	# 8 not in same delta as other items so co-occurence not gettign counted.
				[ -8, -9,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0], 	# 8 not in same delta as other items so co-occurence not gettign counted.
				[ -8, -8,   0.9, 0.9, 0.9, 0.9, 0.9, 0, 0, 0.9],
				[ -8, -6,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0], 	# 8 not in same delta as other items so co-occurence not gettign counted.
				[ -6,-11,   0.9, 0.9, 0.9, 1.9, 1.9, 0, 0, 1.9],
				[ -6, -9,   0.0, 0.0, 0.9, 0.9, 0.9, 0, 0, 0.9],
				[ -6, -8,   0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0], 	# 8 not in same delta as other items so co-occurence not gettign counted.
				[ -6, -6,   1.9, 1.9, 1.9, 1.9, 1.9, 0, 0, 1.9],
			];

		associationStats = DBUtil.execute(associationQuery)
		self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 );

		#DBUtil.execute("delete from clinical_item_association")

		# Add another training period then should get a second decay multiplier for older data?
		# Weird in that incrementally building on prior data that is getting decayed, even though new training data actually occurred before chronologic time of data
		decayAnalysisOptions = DecayAnalysisOptions();
		decayAnalysisOptions.startD = datetime(2000,1,1)
		decayAnalysisOptions.endD = datetime(2000,2,12)
		decayAnalysisOptions.windowLength = 10
		decayAnalysisOptions.decay = 0.9
		decayAnalysisOptions.delta = timedelta(weeks=4)
		decayAnalysisOptions.patientIds = [-22222, -33333]

		self.decayAnalyzer.decayAnalyzePatientItems (decayAnalysisOptions)

		expectedAssociationStats = \
			[
				[-11L, -11L, 1.539, 1.539, 1.539, 1.539, 1.539, 0.0, 0.0, 1.539],
				[-11L, -9L, 0.0, 0.0, 0.729, 0.729, 0.729, 0.0, 0.0, 0.729],
				[-11L, -8L, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
				[-11L, -7L, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
				[-11L, -6L, 0.729, 0.729, 0.729, 0.729, 0.729, 0.0, 0.0, 0.729],
				[-9L, -11L, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
				[-9L, -9L, 0.729, 0.729, 0.729, 0.729, 0.729, 0.0, 0.0, 0.729],
				[-9L, -8L, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
				[-9L, -7L, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
				[-9L, -6L, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
				[-8L, -11L, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
				[-8L, -9L, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
				[-8L, -8L, 0.729, 0.729, 0.729, 0.729, 0.729, 0.0, 0.0, 0.729],
				[-8L, -6L, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
				[-7L, -11L, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.9],
				[-7L, -9L, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.9],
				[-7L, -7L, 0.9, 0.9, 0.9, 0.9, 0.9, 0.0, 0.0, 0.9],
				[-7L, -6L, 0.0, 0.0, 0.0, 0.9, 0.9, 0.0, 0.0, 0.9],
				[-6L, -11L, 0.729, 0.729, 0.729, 1.539, 1.539, 0.0, 0.0, 1.539],
				[-6L, -9L, 0.0, 0.0, 0.729, 0.729, 0.729, 0.0, 0.0, 0.729],
				[-6L, -8L, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
				[-6L, -7L, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
				[-6L, -6L, 1.539, 1.539, 1.539, 1.539, 1.539, 0.0, 0.0, 1.539],
			];

		associationStats = DBUtil.execute(associationQuery)
		#for row in expectedAssociationStats:
		#	print >> sys.stderr, row;
		#print >> sys.stderr, "============"
		#for row in associationStats:
		#	print >> sys.stderr, row;
		#print >> sys.stderr, "============"
		self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 );


	def test_resetModel(self):
		associationQuery = \
			"""
			select
				clinical_item_id, subsequent_item_id,
				patient_count_0, patient_count_3600, patient_count_86400, patient_count_604800,
				patient_count_2592000, patient_count_7776000, patient_count_31536000,
				patient_count_any
			from
				clinical_item_association
			where
				clinical_item_id < 0
			order by
				clinical_item_id, subsequent_item_id
			""";

		associationQueryDate = \
			"""
			select
				patient_item_id, analyze_date
			from
				patient_item
			where
				patient_item_id < 0
			order by
				patient_item_id
			""";

		# fill up the association table with something
		decayAnalysisOptions = DecayAnalysisOptions()
		decayAnalysisOptions.startD = datetime(2000,1,9)
		decayAnalysisOptions.endD = datetime(2000,2,11)
		decayAnalysisOptions.windowLength = 10
		decayAnalysisOptions.decay = 0.9
		decayAnalysisOptions.patientIds = [-22222, -33333]
		self.decayAnalyzer.decayAnalyzePatientItems (decayAnalysisOptions)

		# then clear the table
		self.dataManager.resetAssociationModel()

		expectedAssociationStats = \
			[
			];
		associationStats = DBUtil.execute(associationQuery)
		self.assertEqualTable(expectedAssociationStats, associationStats, precision=3 )

		# Set as NULL
		expectedAssociationStatsDate = \
			[[-95, None],[-94, None],[-16, None], [-15, None], [-14, None], [-13, None], [-12, None], [-10, None], [-5, None], [-4, None], [-3, None], [-2, None], [-1, None]
			];
		associationStatsDate = DBUtil.execute(associationQueryDate)
		#print >> sys.stderr, associationStatsDate
		self.assertEqualTable(expectedAssociationStatsDate, associationStatsDate)

def suite():
	"""Returns the suite of tests to run for this test class / module.
	Use unittest.makeSuite methods which simply extracts all of the
	methods for the given class whose name starts with "test"
	"""
	suite = unittest.TestSuite();
	#suite.addTest(TestDecayingWindows('test_decayingWindows'))
	#suite.addTest(TestDecayingWindows('test_decayingWindowsFromBuffer'))
	#suite.addTest(TestDecayingWindows('test_resetModel'))
	suite.addTest(unittest.makeSuite(TestDecayingWindows));

	return suite;

if __name__=="__main__":
	unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
