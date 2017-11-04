#!/usr/bin/python
"""
Class for generating LabTestMatrix.
"""

import datetime
import os
import time
import numpy
from medinfo.dataconversion.FeatureMatrixFactory import FeatureMatrixFactory
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery

class LabTestMatrix:
    def __init__(self, labTests, numPatientEpisodes):
        self.factory = FeatureMatrixFactory()
        self.labTests = labTests
        self.numPatients = 1
        self.numPatientEpisodes = numPatientEpisodes
        # Initialize DB connection.
        self.connection = DBUtil.connection()
        self._queryPatientEpisodes()

        # Look for lab data 90 days before each episode, but never afterself.
        preTimeDelta = datetime.timedelta(-90)
        postTimeDelta = datetime.timedelta(0)
        # Add lab features.
        self.factory.addLabResultFeatures(self.labTests, False, preTimeDelta, postTimeDelta)
        # Build matrix.
        self.factory.buildFeatureMatrix()

        return

    def _getAverageOrdersPerPatient(self):
        # Initialize DB cursor.
        cursor = self.connection.cursor()

        # Get average number of results for this lab test per patient.
        query = "SELECT AVG(num_orders) \
        FROM ( \
            SELECT pat_id, COUNT(sor.order_proc_id) AS num_orders \
            FROM stride_order_proc AS sop, stride_order_results AS sor \
            WHERE sop.order_proc_id = sor.order_proc_id AND base_name IN ('%s') \
            GROUP BY pat_id \
        ) AS num_orders_per_patient" % ("', '".join(self.labTests))

        cursor.execute(query)
        avgOrdersPerPatient = cursor.fetchone()[0]

        return avgOrdersPerPatient

    def _getRandomPatientList(self, numPatientsToQuery):
        # Initialize DB cursor.
        cursor = self.connection.cursor()

        # Get numPatientsToQuery random patients who have gotten test.
        # TODO(sbala): Have option to feed in a seed for the randomness.
        query = "SELECT pat_id \
        FROM stride_order_proc AS sop, stride_order_results AS sor \
        WHERE sop.order_proc_id = sor.order_proc_id AND \
        base_name IN ('%s') \
        ORDER BY RANDOM() \
        LIMIT %d;" % ("', '".join(self.labTests), numPatientsToQuery)

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
        query = "SELECT CAST(pat_id AS bigint), \
            sop.order_proc_id AS order_proc_id, proc_code, order_time, \
            COUNT(CASE result_in_range_yn WHEN 'Y' THEN 1 ELSE null END) AS normal_results \
            FROM stride_order_proc AS sop, stride_order_results AS sor \
            WHERE sop.order_proc_id = sor.order_proc_id \
            AND base_name IN ('%s') \
            AND CAST(pat_id AS BIGINT) IN (%s) \
            GROUP BY pat_id, sop.order_proc_id, proc_code, order_time \
            ORDER BY pat_id, sop.order_proc_id, proc_code, order_time;" % ("', '".join(self.labTests), patientListStr)

        cursor.execute(query)

        # Set and process patientEpisodeInput.
        self.factory.setPatientEpisodeInput(cursor, "pat_id", "order_time")
        self.factory.processPatientEpisodeInput()

    def writeLabTestMatrix(self, destPath):
        labMatrixFile = open(destPath, "w")
        sourcePath = self.factory.getMatrixFileName()
        os.rename(sourcePath, destPath)

if __name__ == "__main__":
    start_time = time.time()
    # Initialize lab test matrix.
    ltm = LabTestMatrix(["BUN"], 10)
    # Output lab test matrix.
    elapsed_time = numpy.ceil(time.time() - start_time)
    ltm.writeLabTestMatrix("RBC-test-RBC-NA-K-10-episodes-%s-sec.tab" % str(elapsed_time))
