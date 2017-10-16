#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
from datetime import datetime;
import unittest

from Const import LOGGER_LEVEL, RUNNER_VERBOSITY;
from Util import log;

from medinfo.db.test.Util import DBTestCase;

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel;

from medinfo.cpoe.AssociationAnalysis import AssociationAnalysis, AnalysisOptions;

class TestAssociationAnalysis(DBTestCase):
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
				RowItemModel( [-14, -333,   -33333, -6,  datetime(2000, 2, 9, 0)], headers ),
				RowItemModel( [-15, -333,   -33333, -2,  datetime(2000, 2,11, 0)], headers ),  # Will set clinical_item_link inheritances to this item to only record certain associations
				RowItemModel( [-16, -333,   -33333, -11,  datetime(2000, 2,11, 0)], headers ),
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

		# Temp filename for data buffer
		self.bufferFilename = "updateBufferTemp.txt"

		self.analyzer = AssociationAnalysis();  # Instance to test on

	def tearDown(self):
		"""Restore state from any setUp or test steps"""
		log.info("Purge test records from the database")

		DBUtil.execute("delete from clinical_item_link where clinical_item_id < 0");
		DBUtil.execute("delete from clinical_item_association where clinical_item_id < 0");
		DBUtil.execute("delete from patient_item where patient_item_id < 0");
		DBUtil.execute("delete from clinical_item where clinical_item_id < 0");
		DBUtil.execute("delete from clinical_item_category where clinical_item_category_id in (%s)" % str.join(",", self.clinicalItemCategoryIdStrList) );

		# Deletes any temp bufferFile
		dirname = os.path.dirname(self.bufferFilename);
		if dirname == "": dirname = ".";
		for filename in os.listdir(dirname):
			if filename.startswith(self.bufferFilename):
				os.remove(os.path.join(dirname,filename));

		DBTestCase.tearDown(self);

	def test_analyzePatientItems_commandLine_bufferFile(self):
		# Run the association analysis, save to a file, and update from the file to the database, all command-line control
		associationQuery = \
			"""
			select
				clinical_item_id, subsequent_item_id,
				patient_count_0, patient_count_3600, patient_count_86400, patient_count_604800,
				patient_count_2592000, patient_count_7776000, patient_count_31536000,
				patient_count_any,
				patient_time_diff_sum, patient_time_diff_sum_squares
			from
				clinical_item_association
			where
				clinical_item_id < 0
			order by
				clinical_item_id, subsequent_item_id
			""";

		log.debug("Use incremental update, including date filters to start.");
		self.analyzer.main(["AssociationAnalysis.py","-s","2000-01-09","-e","2000-02-11","-b",self.bufferFilename,"-p","1",  "0,-22222,-33333"]);
		self.analyzer.main(["AssociationAnalysis.py","-b",self.bufferFilename]);

		expectedAssociationStats = \
			[
				[-11,-11,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[-11, -6,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[ -6,-11,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[ -6, -6,   2, 2, 2, 2, 2, 2, 2, 2,  0.0, 0.0],
			];

		associationStats = DBUtil.execute(associationQuery)
		self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 )



		log.debug("Use incremental update, only doing the update based on a part of the data.");
		self.analyzer.main(["AssociationAnalysis.py","-b",self.bufferFilename,"0,-22222,-33333"]);
		self.analyzer.main(["AssociationAnalysis.py","-b",self.bufferFilename]);

		expectedAssociationStats = \
			[
				[-11,-11,   2, 2, 2, 2, 2, 2, 2, 2,  0.0, 0.0],
				[-11, -7,   0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[-11, -6,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[ -7,-11,   0, 0, 0, 1, 1, 1, 1, 1,  345600.0, 119439360000.0],
				[ -7, -7,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[ -7, -6,   0, 0, 0, 1, 1, 1, 1, 1,  345600.0, 119439360000.0],

				[ -6,-11,   1, 1, 1, 2, 2, 2, 2, 2, 172800.0, 29859840000.0],
				[ -6, -7,   0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[ -6, -6,   2, 2, 2, 2, 2, 2, 2, 2,  0.0, 0.0],
			];

		associationStats = DBUtil.execute(associationQuery);
		self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 );

	def test_analyzePatientItemsFromBuffer(self):
		# Run the association analysis, save to a file, and update from the file to the database
		associationQuery = \
			"""
			select
				clinical_item_id, subsequent_item_id,
				patient_count_0, patient_count_3600, patient_count_86400, patient_count_604800,
				patient_count_2592000, patient_count_7776000, patient_count_31536000,
				patient_count_any,
				patient_time_diff_sum, patient_time_diff_sum_squares
			from
				clinical_item_association
			where
				clinical_item_id < 0
			order by
				clinical_item_id, subsequent_item_id
			""";

		log.debug("Use incremental update, including date filters to start.");
		analysisOptions = AnalysisOptions();
		analysisOptions.patientIds = [-22222, -33333];
		analysisOptions.startDate = datetime(2000,1,9);
		analysisOptions.endDate = datetime(2000,2,11);
		analysisOptions.bufferFile = self.bufferFilename;

		self.analyzer.analyzePatientItems(analysisOptions)
		self.analyzer.commitUpdateBufferFromFile(self.bufferFilename)

		expectedAssociationStats = \
			[
				[-11,-11,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[-11, -6,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[ -6,-11,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[ -6, -6,   2, 2, 2, 2, 2, 2, 2, 2,  0.0, 0.0],
			];

		associationStats = DBUtil.execute(associationQuery)
		self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 )



		log.debug("Use incremental update, only doing the update based on a part of the data.");
		analysisOptions = AnalysisOptions();
		analysisOptions.patientIds = [-22222, -33333];
		analysisOptions.bufferFile = self.bufferFilename;

		self.analyzer.analyzePatientItems( analysisOptions );
		self.analyzer.commitUpdateBufferFromFile(self.bufferFilename)

		expectedAssociationStats = \
			[
				[-11,-11,   2, 2, 2, 2, 2, 2, 2, 2,  0.0, 0.0],
				[-11, -7,   0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[-11, -6,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[ -7,-11,   0, 0, 0, 1, 1, 1, 1, 1,  345600.0, 119439360000.0],
				[ -7, -7,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[ -7, -6,   0, 0, 0, 1, 1, 1, 1, 1,  345600.0, 119439360000.0],

				[ -6,-11,   1, 1, 1, 2, 2, 2, 2, 2, 172800.0, 29859840000.0],
				[ -6, -7,   0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[ -6, -6,   2, 2, 2, 2, 2, 2, 2, 2,  0.0, 0.0],
			];

		associationStats = DBUtil.execute(associationQuery);
		self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 );

	def test_analyzePatientItems(self):
		# Run the association analysis against the mock test data above and verify
		#   expected stats afterwards.

		associationQuery = \
			"""
			select
				clinical_item_id, subsequent_item_id,
				patient_count_0, patient_count_3600, patient_count_86400, patient_count_604800,
				patient_count_2592000, patient_count_7776000, patient_count_31536000,
				patient_count_any,
				patient_time_diff_sum, patient_time_diff_sum_squares
			from
				clinical_item_association
			where
				clinical_item_id < 0
			order by
				clinical_item_id, subsequent_item_id
			""";


		log.debug("Use incremental update, including date filters to start.");
		analysisOptions = AnalysisOptions();
		analysisOptions.patientIds = [-22222, -33333];
		analysisOptions.startDate = datetime(2000,1,9);
		analysisOptions.endDate = datetime(2000,2,11);
		self.analyzer.analyzePatientItems( analysisOptions );

		expectedAssociationStats = \
			[
				[-11,-11,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[-11, -6,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[ -6,-11,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[ -6, -6,   2, 2, 2, 2, 2, 2, 2, 2,  0.0, 0.0],
			];

		associationStats = DBUtil.execute(associationQuery);
		self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 );


		log.debug("Use incremental update, only doing the update based on a part of the data.");
		analysisOptions = AnalysisOptions();
		analysisOptions.patientIds = [-22222, -33333];
		self.analyzer.analyzePatientItems( analysisOptions );

		expectedAssociationStats = \
			[
				[-11,-11,   2, 2, 2, 2, 2, 2, 2, 2,  0.0, 0.0],
				[-11, -7,   0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[-11, -6,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[ -7,-11,   0, 0, 0, 1, 1, 1, 1, 1,  345600.0, 119439360000.0],
				[ -7, -7,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[ -7, -6,   0, 0, 0, 1, 1, 1, 1, 1,  345600.0, 119439360000.0],

				[ -6,-11,   1, 1, 1, 2, 2, 2, 2, 2, 172800.0, 29859840000.0],
				[ -6, -7,   0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[ -6, -6,   2, 2, 2, 2, 2, 2, 2, 2,  0.0, 0.0],
			];

		associationStats = DBUtil.execute(associationQuery);
		self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 );

		log.debug("Expand incremental update, by now including additional clinical items whose analysis status previously excluded them.");
		DBUtil.updateRow("clinical_item",{"analysis_status":1},-2);
		analysisOptions.patientIds = [-22222, -33333];
		self.analyzer.analyzePatientItems( analysisOptions );

		expectedAssociationStats = \
			[
				[-11,-11,   2, 2, 2, 2, 2, 2, 2, 2,  0.0, 0.0],
				[-11, -7,   0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[-11, -6,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[-11, -2,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[ -7,-11,   0, 0, 0, 1, 1, 1, 1, 1,  345600.0, 119439360000.0],
				[ -7, -7,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[ -7, -6,   0, 0, 0, 1, 1, 1, 1, 1,  345600.0, 119439360000.0],

				[ -6,-11,   1, 1, 1, 2, 2, 2, 2, 2, 172800.0, 29859840000.0],
				[ -6, -7,   0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[ -6, -6,   2, 2, 2, 2, 2, 2, 2, 2,  0.0, 0.0],

				[ -2,-11,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[ -2, -2,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
			];

		associationStats = DBUtil.execute(associationQuery);
		self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 );


		log.debug("Incremental update that includes a single patient data being split, so have to account for all of those dependencies");

		headers = ["patient_item_id","encounter_id","patient_id","clinical_item_id","item_date"];
		dataModels = \
			[
				RowItemModel( [-1111, -334, -33333, -3,  datetime(2000, 2,11, 8)], headers ),
			];
		for dataModel in dataModels:
			(dataItemId, isNew) = DBUtil.findOrInsertItem("patient_item", dataModel );

		analysisOptions.patientIds = [-22222, -33333];
		self.analyzer.analyzePatientItems( analysisOptions );

		expectedAssociationStats = \
			[
				[-11,-11,   2, 2, 2, 2, 2, 2, 2, 2,  0.0, 0.0],
				[-11, -7,   0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[-11, -6,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[-11, -3,   0, 0, 1, 1, 1, 1, 1, 1,  28800.0, 829440000.0],
				[-11, -2,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[ -7,-11,   0, 0, 0, 1, 1, 1, 1, 1,  345600.0, 119439360000.0],
				[ -7, -7,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[ -7, -6,   0, 0, 0, 1, 1, 1, 1, 1,  345600.0, 119439360000.0],

				[ -6,-11,   1, 1, 1, 2, 2, 2, 2, 2,  172800.0, 29859840000.0],
				[ -6, -7,   0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[ -6, -6,   2, 2, 2, 2, 2, 2, 2, 2,  0.0, 0.0],
				[ -6, -3,   0, 0, 0, 1, 1, 1, 1, 1,  201600.0, 40642560000.0],

				[ -3,-11,   0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[ -3, -6,   0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[ -3, -3,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[ -3, -2,   0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],

				[ -2,-11,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[ -2, -3,   0, 0, 1, 1, 1, 1, 1, 1,  28800.0, 829440000.0],
				[ -2, -2,   1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
			];
		associationStats = DBUtil.execute(associationQuery);
		self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 );

		log.debug("Negative test case, repeating analysis should not change any results");
		analysisOptions.patientIds = [-22222, -33333];
		self.analyzer.analyzePatientItems( analysisOptions );
		associationStats = DBUtil.execute(associationQuery);
		self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 );

		log.debug("Complete the remaining incremental update");
		analysisOptions.patientIds = [-11111, -22222, -33333];
		self.analyzer.analyzePatientItems( analysisOptions );

		expectedAssociationStats = \
			[   # Note that sum-squares in particular gets rounded off due to large values
				[-12, -12, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				[-12, -10, 0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[-12,  -8, 0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[-12,  -4, 0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[-11, -11, 2, 2, 2, 2, 2, 2, 2, 2,  0.0, 0.0],
				[-11,  -7, 0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[-11,  -6, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				[-11,  -3, 0, 0, 1, 1, 1, 1, 1, 1,  28800.0, 829440000.0],
				[-11,  -2, 1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[-10, -12, 0, 0, 0, 0, 0, 1, 1, 1, 2678400.0, 7173830000000.0],    # Longer time diff?
				[-10, -10, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				[-10,  -8, 0, 0, 1, 1, 1, 1, 1, 1, 7200.0, 51840000.0],
				[-10,  -4, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				[ -8, -12, 0, 0, 0, 0, 0, 1, 1, 1, 2671200.0, 7135310000000.0],     # Longer diff
				[ -8, -10, 0, 0, 1, 1, 1, 1, 1, 1, 79200.0, 6272640000.0],
				[ -8,  -8, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				[ -8,  -4, 0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[ -7, -11, 0, 0, 0, 1, 1, 1, 1, 1, 345600.0, 119439000000.0],
				[ -7,  -7, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				[ -7,  -6, 0, 0, 0, 1, 1, 1, 1, 1, 345600.0, 119439000000.0],
				[ -6, -11, 1, 1, 1, 2, 2, 2, 2, 2, 172800.0, 29859840000.0],
				[ -6,  -7, 0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[ -6,  -6, 2, 2, 2, 2, 2, 2, 2, 2, 0.0, 0.0],
				[ -6,  -3, 0, 0, 0, 1, 1, 1, 1, 1, 201600.0, 40642600000.0],
				[ -4, -12, 0, 0, 0, 0, 0, 1, 1, 1, 2678400.0, 7173830000000.0], # ???
				[ -4, -10, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				[ -4,  -8, 0, 0, 1, 1, 1, 1, 1, 1, 7200.0, 51840000.0],
				[ -4,  -4, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				[ -3, -11, 0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[ -3,  -6, 0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[ -3,  -3, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				[ -3,  -2, 0, 0, 0, 0, 0, 0, 0, 0,  0.0, 0.0],
				[ -2, -11, 1, 1, 1, 1, 1, 1, 1, 1,  0.0, 0.0],
				[ -2,  -3, 0, 0, 1, 1, 1, 1, 1, 1, 28800.0, 829440000.0],
				[ -2,  -2, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0]
			];

		associationStats = DBUtil.execute(associationQuery);
		self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 );

		# Check the association stats for non-unique counts as well (allowing for repeats)
		nonUniqueAssociationQuery = \
			"""
			select
				clinical_item_id, subsequent_item_id,
				count_0, count_3600, count_86400, count_604800,
				count_2592000, count_7776000, count_31536000, count_126144000,
				count_any,
				time_diff_sum, time_diff_sum_squares
			from
				clinical_item_association
			where
				clinical_item_id < 0
			order by
				clinical_item_id, subsequent_item_id
			""";
		expectedAssociationStats = \
			[   # Note that sum-squares in particular gets rounded off due to large values
				 [-12, -12, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [-12, -10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [-12,  -8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [-12,  -4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [-11, -11, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0.0, 0.0],
				 [-11,  -7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [-11,  -6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [-11,  -3, 0, 0, 1, 1, 1, 1, 1, 1, 1, 28800.0, 829440000.0],
				 [-11,  -2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [-10, -12, 0, 0, 0, 0, 1, 2, 2, 2, 2, 5270400.0, 13892300000000.0],
				 [-10, -10, 2, 2, 3, 3, 3, 3, 3, 3, 3, 86400.0, 7464960000.0],
				 [-10,  -8, 0, 0, 1, 1, 1, 1, 1, 1, 1, 7200.0, 51840000.0],
				 [-10,  -4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [ -8, -12, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2671200.0, 7135310000000.0],
				 [ -8, -10, 0, 0, 1, 1, 1, 1, 1, 1, 1, 79200.0, 6272640000.0],
				 [ -8,  -8, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [ -8,  -4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [ -7, -11, 0, 0, 0, 1, 1, 1, 1, 1, 1, 345600.0, 119439000000.0],
				 [ -7,  -7, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [ -7,  -6, 0, 0, 0, 1, 1, 1, 1, 1, 1, 345600.0, 119439000000.0],
				 [ -6, -11, 1, 1, 1, 2, 2, 2, 2, 2, 2, 172800.0, 29859800000.0],
				 [ -6,  -7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [ -6,  -6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0.0, 0.0],
				 [ -6,  -3, 0, 0, 0, 1, 1, 1, 1, 1, 1, 201600.0, 40642600000.0],
				 [ -4, -12, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2678400.0, 7173830000000.0],
				 [ -4, -10, 1, 1, 2, 2, 2, 2, 2, 2, 2, 86400.0, 7464960000.0],
				 [ -4,  -8, 0, 0, 1, 1, 1, 1, 1, 1, 1, 7200.0, 51840000.0],
				 [ -4,  -4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [ -3, -11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [ -3,  -6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [ -3,  -3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [ -3,  -2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [ -2, -11, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [ -2,  -3, 0, 0, 1, 1, 1, 1, 1, 1, 1, 28800.0, 829440000.0],
				 [ -2,  -2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
			];
		associationStats = DBUtil.execute(nonUniqueAssociationQuery);
		self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 );


		# Again for patient level counts
		patientAssociationQuery = \
			"""
			select
				clinical_item_id, subsequent_item_id,
				patient_count_0, patient_count_3600, patient_count_86400, patient_count_604800,
				patient_count_2592000, patient_count_7776000, patient_count_31536000, patient_count_126144000,
				patient_count_any,
				patient_time_diff_sum, patient_time_diff_sum_squares
			from
				clinical_item_association
			where
				clinical_item_id < 0
			order by
				clinical_item_id, subsequent_item_id
			""";
		expectedAssociationStats = \
			[   # Note that sum-squares in particular gets rounded off due to large values
				 [-12, -12, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [-12, -10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [-12,  -8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [-12,  -4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [-11, -11, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0.0, 0.0],
				 [-11,  -7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [-11,  -6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [-11,  -3, 0, 0, 1, 1, 1, 1, 1, 1, 1, 28800.0, 829440000.0],
				 [-11,  -2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [-10, -12, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2678400.0, 2678400.0*2678400.0],    # Main difference.  Duplicates within a single patient, only count once
				 [-10, -10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],   # Don't count duplicates
				 [-10,  -8, 0, 0, 1, 1, 1, 1, 1, 1, 1, 7200.0, 51840000.0],
				 [-10,  -4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [ -8, -12, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2671200.0, 7135310000000.0],
				 [ -8, -10, 0, 0, 1, 1, 1, 1, 1, 1, 1, 79200.0, 6272640000.0],
				 [ -8,  -8, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [ -8,  -4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [ -7, -11, 0, 0, 0, 1, 1, 1, 1, 1, 1, 345600.0, 119439000000.0],
				 [ -7,  -7, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [ -7,  -6, 0, 0, 0, 1, 1, 1, 1, 1, 1, 345600.0, 119439000000.0],
				 [ -6, -11, 1, 1, 1, 2, 2, 2, 2, 2, 2, 172800.0, 29859800000.0],
				 [ -6,  -7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [ -6,  -6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0.0, 0.0],
				 [ -6,  -3, 0, 0, 0, 1, 1, 1, 1, 1, 1, 201600.0, 40642600000.0],
				 [ -4, -12, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2678400.0, 7173830000000.0],
				 [ -4, -10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],  # Don't count repeats
				 [ -4,  -8, 0, 0, 1, 1, 1, 1, 1, 1, 1, 7200.0, 51840000.0],
				 [ -4,  -4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [ -3, -11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [ -3,  -6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [ -3,  -3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [ -3,  -2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [ -2, -11, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [ -2,  -3, 0, 0, 1, 1, 1, 1, 1, 1, 1, 28800.0, 829440000.0],
				 [ -2,  -2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
			];
		associationStats = DBUtil.execute(patientAssociationQuery);
		self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 );


		# Again for encounter level counts
		encounterAssociationQuery = \
			"""
			select
				clinical_item_id, subsequent_item_id,
				encounter_count_0, encounter_count_3600, encounter_count_86400, encounter_count_604800,
				encounter_count_2592000, encounter_count_7776000, encounter_count_31536000, encounter_count_126144000,
				encounter_count_any,
				encounter_time_diff_sum, encounter_time_diff_sum_squares
			from
				clinical_item_association
			where
				clinical_item_id < 0
			order by
				clinical_item_id, subsequent_item_id
			""";
		expectedAssociationStats = \
			[   # Note that sum-squares in particular gets rounded off due to large values
				 [-12, -12, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [-12, -10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [-12,  -8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [-12,  -4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [-11, -11, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0.0, 0.0],
				 [-11,  -7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [-11,  -6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [-11,  -3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],   # No longer related in separate encounters
				 [-11,  -2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [-10, -12, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2592000.0, 2592000.0*2592000.0],    # Only count the relation within a common encounter
				 [-10, -10, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0.0, 0.0],   # Now count for separate encounters
				 [-10,  -8, 0, 0, 1, 1, 1, 1, 1, 1, 1, 7200.0, 51840000.0],
				 [-10,  -4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [ -8, -12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0], # No longer related in separate encounters
				 [ -8, -10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],  # No longer related in separate encounters
				 [ -8,  -8, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [ -8,  -4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [ -7, -11, 0, 0, 0, 1, 1, 1, 1, 1, 1, 345600.0, 119439000000.0],
				 [ -7,  -7, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [ -7,  -6, 0, 0, 0, 1, 1, 1, 1, 1, 1, 345600.0, 119439000000.0],
				 [ -6, -11, 1, 1, 1, 2, 2, 2, 2, 2, 2, 172800.0, 29859800000.0],
				 [ -6,  -7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [ -6,  -6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0.0, 0.0],
				 [ -6,  -3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],   # No longer related in separate encounters
				 [ -4, -12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0], # No longer related in separate encounters
				 [ -4, -10, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [ -4,  -8, 0, 0, 1, 1, 1, 1, 1, 1, 1, 7200.0, 51840000.0],
				 [ -4,  -4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [ -3, -11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [ -3,  -6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [ -3,  -3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [ -3,  -2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],
				 [ -2, -11, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
				 [ -2,  -3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0, 0.0],   # No longer related in separate encounters
				 [ -2,  -2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.0, 0.0],
			];
		associationStats = DBUtil.execute(encounterAssociationQuery);
		self.assertEqualTable( expectedAssociationStats, associationStats, precision=3 );

def suite():
	"""Returns the suite of tests to run for this test class / module.
	Use unittest.makeSuite methods which simply extracts all of the
	methods for the given class whose name starts with "test"
	"""
	suite = unittest.TestSuite();
	#suite.addTest(TestAssociationAnalysis("test_incColNamesAndTypeCodes"));
	#suite.addTest(TestAssociationAnalysis("test_insertFile_skipErrors"));
	#suite.addTest(TestAssociationAnalysis('test_executeIterator'));
	#suite.addTest(TestAssociationAnalysis('test_findOrInsertItem'));
	#suite.addTest(TestAssociationAnalysis('test_analyzePatientItems_commandLine_bufferFile'))
	suite.addTest(unittest.makeSuite(TestAssociationAnalysis));

	return suite;

if __name__=="__main__":
	log.setLevel(LOGGER_LEVEL)

	unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
