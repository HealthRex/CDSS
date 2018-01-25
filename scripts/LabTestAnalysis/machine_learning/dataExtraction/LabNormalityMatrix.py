#!/usr/bin/python
"""
Class for generating LabNormalityMatrix.
"""

import datetime
import os
import sys
import time
import numpy

from scripts.Util import log
from medinfo.dataconversion.FeatureMatrixFactory import FeatureMatrixFactory
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery

class LabNormalityMatrix:
    def __init__(self, labPanel, numPatientEpisodes):
        self.factory = FeatureMatrixFactory()
        self.labPanel = labPanel
        self.labComponents = self._getComponentsInLabPanel(labPanel)
        self.numPatients = 1
        self.numRequestedEpisodes = numPatientEpisodes
        self.numPatientEpisodes = numPatientEpisodes

        # Initialize DB connection.
        self.connection = DBUtil.connection()
        print "Querying patient episodes..."
        self._queryPatientEpisodes()

        # Add time features.
        print 'Adding time features...'
        self._addTimeFeatures()
        # Add demographic features.
        print 'Adding demographic features...'
        self._addDemographicFeatures()
        # Add treatment team features.
        print 'Adding treatment team features...'
        self.factory.addTreatmentTeamFeatures(features="pre")
        # Add Charlson Comorbidity features.
        print 'Adding comorbidity features...'
        self.factory.addCharlsonComorbidityFeatures(features="pre")
        # Add flowsheet vitals features.
        print 'Adding flowsheet features...'
        self._addFlowsheetFeatures()
        # Add lab panel order and component result features.
        print 'Adding lab test features...'
        self._addLabTestFeatures()

        # Build matrix.
        print 'Building matrix...'
        self.factory.buildFeatureMatrix()

        return

    def _getComponentsInLabPanel(self, labPanel):
        # Initialize DB connection.
        connection = DBUtil.connection()
        cursor = connection.cursor()

        # Build query to get component names for panel.
        query = SQLQuery()
        query.addSelect("base_name")
        query.addFrom("stride_order_proc AS sop")
        query.addFrom("stride_order_results AS sor")
        query.addWhere("sop.order_proc_id = sor.order_proc_id")
        query.addWhere("proc_code = '%s'" % labPanel)
        query.addGroupBy("base_name")

        # Return component names in list.
        cursor.execute(str(query))
        return [ row[0] for row in cursor.fetchall() ]

    def _getAverageOrdersPerPatient(self):
        # Initialize DB cursor.
        cursor = self.connection.cursor()

        # Get average number of results for this lab test per patient.
        query = "SELECT AVG(num_orders) \
        FROM ( \
            SELECT pat_id, COUNT(sop.order_proc_id) AS num_orders \
            FROM stride_order_proc AS sop, stride_order_results AS sor \
            WHERE sop.order_proc_id = sor.order_proc_id AND proc_code IN ('%s') \
            GROUP BY pat_id \
        ) AS num_orders_per_patient" % (self.labPanel)

        cursor.execute(query)
        avgOrdersPerPatient = cursor.fetchone()[0]

        if avgOrdersPerPatient is None:
            error_msg = '0 orders for lab panel "%s."' % self.labPanel
            log.critical(error_msg)
            sys.exit('[ERROR] %s' % error_msg)

        return avgOrdersPerPatient

    def _getRandomPatientList(self, numPatientsToQuery):
        # Initialize DB cursor.
        cursor = self.connection.cursor()

        # Get numPatientsToQuery random patients who have gotten test.
        # TODO(sbala): Have option to feed in a seed for the randomness.
        query = "SELECT pat_id \
        FROM stride_order_proc AS sop, stride_order_results AS sor \
        WHERE sop.order_proc_id = sor.order_proc_id AND \
        proc_code IN ('%s') \
        ORDER BY RANDOM() \
        LIMIT %d;" % (self.labPanel, numPatientsToQuery)

        cursor.execute(query)

        # Get patient list.
        randomPatientList = list()
        for row in cursor.fetchall():
            randomPatientList.append(row[0])

        return randomPatientList

    def _queryPatientEpisodes(self):
        # Initialize DB cursor.
        cursor = self.connection.cursor()

        # Get average number of results for this lab test per patient.
        avgOrdersPerPatient = self._getAverageOrdersPerPatient()

        # Based on average # of results, figure out how many patients we'd
        # need to get for a feature matrix of requested size.
        numPatientsToQuery = int(numpy.max([self.numPatientEpisodes / avgOrdersPerPatient, 1]))
        self.numPatients = numPatientsToQuery
        randomPatientList = self._getRandomPatientList(numPatientsToQuery)
        patientListStr = ", ".join(randomPatientList)

        # Build SQL query for list of patient episodes.
        # Note that for 2008-2014 data, result_flag can take on any of the
        # following values:  High, Low, High Panic, Low Panic,
        # Low Off-Scale, Negative, Positive, Resistant, Susceptible, Abnormal, *
        # (NONE): Only 27 lab components can have this flag. None has this
        #           value for more than 5 results, so ignore it.
        # *: Only 10 lab components can have this flag. Only 6 have it for
        #           >10 tests, and each of them is a microbiology test for which
        #           a flag is less meaningful, e.g. Gram Stain, AFB culture.
        # Susceptible: Only 15 lab components can have this flag. All of those
        #           only have this value for 2 results, so ignore it.
        # Resistant: Only 1 lab component can have this flag. Only two results
        #           have this value, so ignore it.
        # Abnormal: 1462 lab components can have this flag. Many (e.g. UBLOOD)
        #           have this value for thousands of results, so include it.
        # Negative: Only 10 lab components can have this flag, and all for
        #           less than 5 results, so ignore it.
        # Positive: Only 3 lab components can have this flag, and all for
        #           only 1 result, so ignore it.
        # Low Off-Scale: Only 1 lab component can have this flag, and only for
        #           3 results, so ignore it.
        # Low Panic: 1401 lab components can have this flag, many core
        #           metabolic components. Include it.
        # High Panic: 8084 lab components can have this flag, many core
        #           metabolic components. Include it.


        query = "SELECT CAST(pat_id AS BIGINT), \
            sop.order_proc_id AS order_proc_id, proc_code, order_time, \
            CASE WHEN abnormal_yn = 'Y' THEN 1 ELSE 0 END AS abnormal_panel, \
            COUNT(result_flag in ('High', 'Low', 'High Panic', 'Low Panic', NULL)) AS num_components, \
            COUNT(CASE result_flag WHEN NULL THEN 1 ELSE NULL END) AS num_normal_components, \
            CAST(COUNT(CASE WHEN result_flag IN ('High', 'Low', 'High Panic', 'Low Panic') THEN 1 ELSE NULL END) = 0 AS INT) AS all_components_normal \
            FROM stride_order_proc AS sop, stride_order_results AS sor \
            WHERE sop.order_proc_id = sor.order_proc_id \
            AND result_flag in ('High', 'Low', 'High Panic', 'Low Panic', NULL)\
            AND proc_code IN ('%s') \
            AND CAST(pat_id AS BIGINT) IN (%s) \
            GROUP BY pat_id, sop.order_proc_id, proc_code, order_time, abnormal_yn \
            ORDER BY pat_id, sop.order_proc_id, proc_code, order_time;" % (self.labPanel, patientListStr)

        cursor.execute(query)

        # Set and process patientEpisodeInput.
        self.factory.setPatientEpisodeInput(cursor, "pat_id", "order_time")
        self.factory.processPatientEpisodeInput()

        # Update numPatientEpisodes.
        self.numPatientEpisodes = 0
        episodes = self.factory.getPatientEpisodeIterator()
        for episode in episodes:
            self.numPatientEpisodes += 1

    def _addTimeFeatures(self):
        # Add admission date.
        ADMIT_DX_CATEGORY_ID = 2
        self.factory.addClinicalItemFeaturesByCategory([ADMIT_DX_CATEGORY_ID], \
            dayBins=[], label="AdmitDxDate", features="pre")

        # Add time cycle features.
        self.factory.addTimeCycleFeatures("order_time", "month")
        self.factory.addTimeCycleFeatures("order_time", "hour")

    def _addDemographicFeatures(self):
        BIRTH_FEATURE = "Birth"
        self.factory.addClinicalItemFeatures([BIRTH_FEATURE], dayBins=[], features="pre")
        self._addSexFeatures()
        self._addRaceFeatures()

    def _addSexFeatures(self):
        SEX_FEATURES = ["Male", "Female"]
        for feature in SEX_FEATURES:
            self.factory.addClinicalItemFeatures([feature], dayBins=[], \
                features="pre")

    def _addRaceFeatures(self):
        RACE_FEATURES = ["RaceWhiteHispanicLatino", "RaceWhiteNonHispanicLatino",
                    "RaceHispanicLatino", "RaceBlack", "RaceAsian",
                    "RacePacificIslander", "RaceNativeAmerican",
                    "RaceOther", "RaceUnknown"]
        for feature in RACE_FEATURES:
            self.factory.addClinicalItemFeatures([feature], dayBins=[], \
                features="pre")

    def _addFlowsheetFeatures(self):
        # Look at flowsheet results from the previous days
        FLOW_PRE_TIME_DELTAS = [ datetime.timedelta(-1), datetime.timedelta(-3),
            datetime.timedelta(-7), datetime.timedelta(-30),
            datetime.timedelta(-90) ]
        # Don't look into the future, otherwise cheating the prediction
        FLOW_POST_TIME_DELTA = datetime.timedelta(0)

        # Add flowsheet features for a variety of generally useful vitals.
        BASIC_FLOWSHEET_FEATURES = [
            "BP_High_Systolic", "BP_Low_Diastolic", "FiO2",
            "Glasgow Coma Scale Score", "Pulse", "Resp", "Temp", "Urine"
        ]
        print "\tBASIC_FLOWSHEET_FEATURES"
        for preTimeDelta in FLOW_PRE_TIME_DELTAS:
            print "\t\t%s" % preTimeDelta
            self.factory.addFlowsheetFeatures(BASIC_FLOWSHEET_FEATURES, preTimeDelta, \
                    FLOW_POST_TIME_DELTA)

    def _addLabTestFeatures(self):
        # Add lab panel order features.
        self.factory.addClinicalItemFeatures([self.labPanel], features="pre")

        # Look for lab data 90 days before each episode, but never after self.
        # Look at lab results from the previous days
        LAB_PRE_TIME_DELTAS = [ datetime.timedelta(-1), datetime.timedelta(-3),
            datetime.timedelta(-7), datetime.timedelta(-30),
            datetime.timedelta(-90) ]
        # Don't look into the future, otherwise cheating the prediction
        LAB_POST_TIME_DELTA = datetime.timedelta(0)

        # Add result features for a variety of generally useful components.
        BASIC_LAB_COMPONENTS = [
            'WBC',      # White Blood Cell
            'HCT',      # Hematocrit
            'PLT',      # Platelet Count
            'NA',       # Sodium, Whole Blood
            'K',        # Potassium, Whole Blood
            'CO2',      # CO2, Serum/Plasma
            'BUN',      # Blood Urea Nitrogen
            'CR',       # Creatinine
            'TBIL',     # Total Bilirubin
            'ALB',      # Albumin
            'CA',       # Calcium
            'LAC',      # Lactic Acid
            'ESR',      # Erythrocyte Sedimentation Rate
            'CRP',      # C-Reactive Protein
            'TNI',      # Troponin I
            'PHA',      # Arterial pH
            'PO2A',     # Arterial pO2
            'PCO2A',    # Arterial pCO2
            'PHV',      # Venous pH
            'PO2V',     # Venous pO2
            'PCO2V'     # Venous pCO2
        ]
        for component in BASIC_LAB_COMPONENTS:
            print "\t%s" % component
            for preTimeDelta in LAB_PRE_TIME_DELTAS:
                print "\t\t%s" % preTimeDelta
                self.factory.addLabResultFeatures([component], False, preTimeDelta, LAB_POST_TIME_DELTA)

        # Add labPanel component result features, for a variety of time deltas.
        print "\tlabComponents"
        for preTimeDelta in LAB_PRE_TIME_DELTAS:
            print "\t\t%s" % preTimeDelta
            self.factory.addLabResultFeatures(self.labComponents, False, preTimeDelta, LAB_POST_TIME_DELTA)

    def write_matrix(self, destPath):
        print 'Writing final matrix file...'
        # Get old matrix file.
        sourcePath = self.factory.getMatrixFileName()
        # Write to new matrix file.
        labMatrixFile = open(destPath, "w")
        self._writeMatrixHeader(destPath, labMatrixFile)
        for line in open(sourcePath, "r"):
            labMatrixFile.write(line)
        # Delete old matrix file.
        os.remove(sourcePath)

    def _writeMatrixHeader(self, matrixFileName, matrixFile):
        created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        source = __name__
        command = "LabNormalityMatrix('%s', %s).writeMatrixFile('%s')" % (self.labPanel, \
            self.numRequestedEpisodes, matrixFileName)

        header = """\
# %s\n\
# Created: %s\n\
# Source: %s \n\
# Command: %s\n\
# \n\
# Overview:\n\
# This file contains %s data rows, representing %s unique orders of \n\
# the %s lab panel across %s inpatients from the Stanford hospital.\n\
# Each row contains columns summarizing the patient's demographics, \n\
# inpatient admit date, prior vitals, prior lab panel orders, and \n\
# prior lab component results. Note the distinction between a lab\n\
# panel (e.g. LABMETB) and a lab component within a panel (e.g. Na, RBC). \n\
# Most cells in matrix represent a count statistic for an event's \n\
# occurrence or the difference between an event's time and order_time.\n\
# \n\
# Fields: \n\
#   pat_id - ID # for patient in the STRIDE data set. \n\
#   order_proc_id - ID # for clinical order. \n\
#   proc_code - code representing ordered lab panel. \n\
#   order_time - time at which lab panel was ordered. \n\
#   abnormal_panel - were any components in panel abnormal (binary)? \n\
#   num_components - # of unique components in lab panel. \n\
#   num_normal_components - # of normal component results in panel. \n\
#   all_components_normal - inverse of abnormal_panel (binary). \n\
#   AdmitDxDate.[clinical_item] - admit diagnosis, pegged to admit date.\n\
#   order_time.[month|hour] - when was the lab panel ordered? \n\
#   Birth.preTimeDays - patient's age in days.\n\
#   [Male|Female].pre - is patient male/female (binary)?\n\
#   [RaceX].pre - is patient race [X]?\n\
#   Team.[specialty].[clinical_item] - specialist added to treatment team.\n\
#   Comorbidity.[disease].[clinical_item] - disease added to problem list.\n\
#   ___.[flowsheet] - measurements for flowsheet biometrics.\n\
#       Includes BP_High_Systolic, BP_Low_Diastolic, FiO2,\n\
#           Glasgow Coma Scale Score, Pulse, Resp, Temp, and Urine.\n\
#   %s.[clinical_item] - orders of the lab panel of interest.\n\
#   ___.[lab_result] - lab component results.\n\
#       Included standard components: WBC, HCT, PLT, NA, K, CO2, BUN,\n\
#           CR, TBIL, ALB, CA, LAC, ESR, CRP, TNI, PHA, PO2A, PCO2A,\n\
#           PHV, PO2V, PCO2V\n\
#       Also included %s panel components: %s\n\
#   \n\
#   [clinical_item] fields may have the following suffixes:\n\
#       ___.pre - how many times has this occurred before order_time?\n\
#       ___.pre.Xd - how many times has this occurred within X days before order_time?\n\
#       ___.preTimeDays - how many days before order_time was last occurrence?\n\
#   \n\
#   [flowsheet] and [lab_result] fields may have the following suffixes:\n\
#       ___.X_Y.count - # of result values between X and Y days of order_time.\n\
#       ___.X_Y.countInRange - # of result values in normal range.\n\
#       ___.X_Y.min - minimum result value.\n\
#       ___.X_Y.max - maximum result value.\n\
#       ___.X_Y.median - median result value.\n\
#       ___.X_Y.std - standard deviation of result values.\n\
#       ___.X_Y.first - first result value.\n\
#       ___.X_Y.last - last result value.\n\
#       ___.X_Y.diff - difference between penultimate and proximate values.\n\
#       ___.X_Y.slope - slope between penultimate and proximate values.\n\
#       ___.X_Y.proximate - closest result value to order_time.\n\
#       ___.X_Y.firstTimeDays - time between first and order_time.\n\
#       ___.X_Y.lastTimeDays - time between last and order_time.\n\
#       ___.X_Y.proximateTimeDays - time between proximate and order_time.\n\
#\n""" % \
            (matrixFileName, created, source, command, \
            self.numPatientEpisodes, self.numPatientEpisodes, self.labPanel, \
            self.numPatients, self.labPanel, self.labPanel, self.labComponents)

        matrixFile.write(header)

if __name__ == "__main__":
    start_time = time.time()
    # Initialize lab test matrix.
    ltm = LabNormalityMatrix("LABABG", 10)
    # Output lab test matrix.
    elapsed_time = numpy.ceil(time.time() - start_time)
    ltm.write_matrix("LABABG-panel-10-episodes-%s-sec.tab" % str(elapsed_time))
