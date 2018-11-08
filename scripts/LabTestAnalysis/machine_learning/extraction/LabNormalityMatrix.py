#!/usr/bin/python
"""
Class for generating UMichNormalityMatrix.
"""

import datetime
import inspect
import logging
import os
import sys
import time
import numpy
from optparse import OptionParser

from medinfo.common.Util import log
from medinfo.dataconversion.FeatureMatrixFactory import FeatureMatrixFactory
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery
from medinfo.dataconversion.FeatureMatrix import FeatureMatrix

import LocalEnv

class LabNormalityMatrix(FeatureMatrix):
    def __init__(self, lab_var, num_episodes, random_state=None, isLabPanel=True, timeLimit=None):
        FeatureMatrix.__init__(self, lab_var, num_episodes)

        self._isLabPanel = isLabPanel
        if isLabPanel:
            self._varTypeInTable = 'proc_code'
        else:
            self._varTypeInTable = 'base_name'

        # Parse arguments.
        self._lab_var = lab_var
        self._num_requested_episodes = num_episodes
        self._num_reported_episodes = 0
        # SQLite's random() function does not support a seed value.
        if random_state and LocalEnv.DATABASE_CONNECTOR_NAME == 'psycopg2':
            query = SQLQuery()
            query.addSelect('setseed(%d);' % random_state)
            DBUtil.execute(query)
            self._random_state = random_state

        self._time_limit = timeLimit

        # Query patient episodes.
        self._query_patient_episodes()
        episodes = self._factory.getPatientEpisodeIterator()
        patients = set()
        for episode in episodes:
            patient_id = int(episode[self._factory.patientEpisodeIdColumn])
            patients.add(patient_id)
        self._num_patients = len(patients)

        # Add features.
        self._add_features()

        # Build matrix.
        FeatureMatrix._build_matrix(self)

    def _get_components_in_lab_panel(self):
        if not self._isLabPanel:
            return [self._lab_var]

        # Initialize DB connection.
        cursor = self._connection.cursor()

        if LocalEnv.DATASET_SOURCE_NAME == 'STRIDE':
        # Doing a single query results in a sequential scan through
        # stride_order_results. To avoid this, break up the query in two.

        # First, get all the order_proc_ids for proc_code.

            query = SQLQuery()
            query.addSelect('order_proc_id')
            query.addFrom('stride_order_proc')
            query.addWhereIn('proc_code', [self._lab_var])
            query.addGroupBy('order_proc_id')
            log.debug('Querying order_proc_ids for %s...' % self._lab_var)
            results = DBUtil.execute(query)
            lab_order_ids = [row[0] for row in results]

            # Second, get all base_names from those orders.
            query = SQLQuery()
            query.addSelect('base_name')
            query.addFrom('stride_order_results')
            query.addWhereIn('order_proc_id', lab_order_ids)
            query.addGroupBy('base_name')

        else:
        # elif LocalEnv.DATASET_SOURCE_NAME == 'UMich':
            query = SQLQuery()
            query.addSelect('base_name')
            query.addFrom('labs')
            query.addWhereIn('proc_code', [self._lab_var])
            query.addGroupBy('base_name')

        log.debug('Querying base_names for order_proc_ids...')
        results = DBUtil.execute(query)
        components = [row[0] for row in results]

        return components

    def _get_average_orders_per_patient(self):
        # Initialize DB cursor.
        cursor = self._connection.cursor()

        # Get average number of results for this lab test per patient.
        query = SQLQuery()
        if LocalEnv.DATASET_SOURCE_NAME == 'STRIDE':
            query.addSelect('CAST(pat_id AS BIGINT) AS pat_id')
            query.addSelect('COUNT(sop.order_proc_id) AS num_orders')
            query.addFrom('stride_order_proc AS sop')
            query.addFrom('stride_order_results AS sor')

            query.addWhere('sop.order_proc_id = sor.order_proc_id')
            query.addWhereIn(self._varTypeInTable, [self._lab_var])
            components = self._get_components_in_lab_panel()
            query.addWhereIn("base_name", components)
            query.addGroupBy('pat_id')

        else:
        #elif LocalEnv.DATASET_SOURCE_NAME == 'UMich':
            query.addSelect('CAST(pat_id AS BIGINT) AS pat_id')
            query.addSelect('COUNT(order_proc_id) AS num_orders')
            query.addFrom('labs')
            query.addWhereIn(self._varTypeInTable, [self._lab_var])
            components = self._get_components_in_lab_panel()
            query.addWhereIn("base_name", components)
            query.addGroupBy('pat_id')
        log.debug('Querying median orders per patient...')
        results = DBUtil.execute(query)

        order_counts = [ row[1] for row in results ]
        if len(order_counts) == 0:
            error_msg = '0 orders for lab "%s."' % self._lab_var
            log.critical(error_msg)
            sys.exit('[ERROR] %s' % error_msg)
        else:
            return numpy.median(order_counts)

    def _get_random_patient_list(self):
        # Initialize DB cursor.
        cursor = self._connection.cursor()

        query = SQLQuery()
        query.addSelect('CAST(pat_id AS BIGINT) AS pat_id')


        if LocalEnv.DATASET_SOURCE_NAME == 'STRIDE':
            if self._isLabPanel:
                query.addSelect('COUNT(sop.order_proc_id) AS num_orders')
                query.addFrom('stride_order_proc AS sop')
                query.addFrom('stride_order_results AS sor')

                if self._time_limit:
                    if self._time_limit[0]:
                        query.addWhere("sop.order_time > '%s'" % self._time_limit[0])
                    if self._time_limit[1]:
                        query.addWhere("sop.order_time < '%s'" % self._time_limit[1])

                query.addWhere('sop.order_proc_id = sor.order_proc_id')
                query.addWhereIn('proc_code', [self._lab_var])

                '''
                sbala: Technically it's possible for someone to get a lab ordered without getting results
                '''
                query.addWhereIn("base_name", self._lab_components)

            else:
                query.addSelect('COUNT(sor.order_proc_id) AS num_orders')
                query.addFrom('stride_order_proc AS sop')
                query.addFrom('stride_order_results AS sor')
                query.addWhere('sop.order_proc_id = sor.order_proc_id')
            ##
                query.addWhereIn("base_name", [self._lab_var])
        else:
            query.addSelect('COUNT(order_proc_id) AS num_orders')
            query.addFrom('labs')
            if self._isLabPanel:
                query.addWhereIn("proc_id", [self._lab_var]) # TODO
                query.addWhereIn("base_name", self._lab_components)
            else:
                query.addWhereIn("base_name", [self._lab_var])

        query.addGroupBy('pat_id')

        log.debug('Querying the number of orders per patient...')

        results = DBUtil.execute(query)

        order_counts = [row[1] for row in results]

        if len(results) == 0:
            error_msg = '0 orders for component "%s."' % self._lab_var  # sx
            log.critical(error_msg)
            sys.exit('[ERROR] %s' % error_msg)
        else:
            avg_orders_per_patient = numpy.median(order_counts)
            log.info('avg_orders_per_patient: %s' % avg_orders_per_patient)
            # Based on average # of results, figure out how many patients we'd
            # need to get for a feature matrix of requested size.
            self._num_patients = int(numpy.max([self._num_requested_episodes / \
                                                avg_orders_per_patient, 1]))

            # Some components may have fewer associated patients than the required sample size
            patient_number_chosen = min([len(results), self._num_patients])  #

            '''
            Set seed to ensure re-producibility of patient episodes.
            Recover int random_state here, since numpy requires int while sql requires [-1,1]
            '''
            numpy.random.seed(int(self._random_state*float(sys.maxint)))
            inds_random_patients = numpy.random.choice(len(results), size=patient_number_chosen, replace=False)

            pat_IDs_random_patients = [results[ind][0] for ind in inds_random_patients]

            return pat_IDs_random_patients

    def _query_patient_episodes(self):
        log.info('Querying patient episodes...')
        # Initialize DB cursor.
        cursor = self._connection.cursor()

        # Build parameters for query.
        self._lab_components = self._get_components_in_lab_panel()
        random_patient_list = self._get_random_patient_list()

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

        if LocalEnv.DATASET_SOURCE_NAME=='STRIDE':

            query = SQLQuery()

            '''
            pat_id: hashed patient id
            '''
            query.addSelect('CAST(pat_id AS BIGINT) as pat_id')

            '''
            order_proc_id: unique identifier for an episode
            '''
            if self._isLabPanel:
                query.addSelect('sop.order_proc_id AS order_proc_id')
            else:
                query.addSelect('sor.order_proc_id AS order_proc_id')

            '''
            self._varTypeInTable: usually proc_code or base_name, the column of the lab to be queried
            '''
            query.addSelect(self._varTypeInTable)


            '''
            order_time: The time of the order. Note that sor table does not have this info. 
            '''
            query.addSelect('order_time')


            '''
            y-labels related columns, choose one to predict (for now, use all_components_normal to predict). 
            '''
            if self._isLabPanel:
                # query.addSelect("CASE WHEN abnormal_yn = 'Y' THEN 1 ELSE 0 END AS abnormal_panel")  #
                query.addSelect(
                    "SUM(CASE WHEN result_flag IN ('High', 'Low', 'High Panic', 'Low Panic', '*', 'Abnormal') OR result_flag IS NULL THEN 1 ELSE 0 END) AS num_components")  # sx
                query.addSelect("SUM(CASE WHEN result_flag IS NULL THEN 1 ELSE 0 END) AS num_normal_components")  # sx
                query.addSelect(
                    "CAST(SUM(CASE WHEN result_flag IN ('High', 'Low', 'High Panic', 'Low Panic', '*', 'Abnormal') THEN 1 ELSE 0 END) = 0 AS INT) AS all_components_normal")  # sx
            else:
                query.addSelect(
                    "CASE WHEN result_flag IN ('High', 'Low', 'High Panic', 'Low Panic', '*', 'Abnormal') THEN 0 ELSE 1 END AS component_normal")


            '''
            Relevant tables. Note that sor table does not have patient_id info; need to join sop to obtain it.  
            '''
            query.addFrom('stride_order_proc AS sop')
            query.addFrom('stride_order_results AS sor')
            query.addWhere('sop.order_proc_id = sor.order_proc_id')

            '''
            Condition: self._time_limit[0] < order_time < self._time_limit[1]
            '''
            if self._time_limit:
                if self._time_limit[0]:
                    query.addWhere("sop.order_time > '%s'" % self._time_limit[0])
                if self._time_limit[1]:
                    query.addWhere("sop.order_time < '%s'" % self._time_limit[1])


            query.addWhere("(result_flag in ('High', 'Low', 'High Panic', 'Low Panic', '*', 'Abnormal') OR result_flag IS NULL)")
            query.addWhereIn(self._varTypeInTable, [self._lab_var])  # sx
            query.addWhereIn("pat_id", random_patient_list)

            query.addGroupBy('pat_id')
            query.addGroupBy('sop.order_proc_id')
            query.addGroupBy(self._varTypeInTable)
            query.addGroupBy('order_time')

            # query.addGroupBy('abnormal_yn')  #

            query.addOrderBy('pat_id')
            query.addOrderBy('sop.order_proc_id')
            query.addOrderBy(self._varTypeInTable)
            query.addOrderBy('order_time')

            query.setLimit(self._num_requested_episodes)

            self._num_reported_episodes = FeatureMatrix._query_patient_episodes(self, query,
                                                                                index_time_col='order_time')

        else:

            '''
            Sqlite3 has an interesting limit for the total number of place_holders in a query, 
            and this limit varies across platforms/operating systems (500-99999 on mac, 999 by defaulty). 
            
            To avoid this problem when querying 1000-10000 patient ids, use string queries instead of the
            default (convenient) routine in DBUtil.  
            '''

            query_str = "SELECT CAST(pat_id AS BIGINT) AS pat_id, order_proc_id, base_name, order_time, "
            query_str += "CASE WHEN result_in_range_yn = 'Y' THEN 1 ELSE 0 END AS component_normal "
            query_str += "FROM labs "
            query_str += "WHERE base_name = '%s' " % self._lab_var
            query_str += "AND pat_id IN "
            pat_list_str = "("
            for pat_id in random_patient_list:
                pat_list_str += str(pat_id) + ","
            pat_list_str = pat_list_str[:-1] + ") "
            query_str += pat_list_str
            query_str += "GROUP BY pat_id, order_proc_id, base_name, order_time "
            query_str += "ORDER BY pat_id, order_proc_id, base_name, order_time "
            query_str += "LIMIT %d" % self._num_requested_episodes

            self._num_reported_episodes = FeatureMatrix._query_patient_episodes(self, query_str, index_time_col='order_time')

    def _add_features(self):
        # Add lab panel order features.
        if LocalEnv.DATASET_SOURCE_NAME == 'STRIDE':
            self._factory.addClinicalItemFeatures([self._lab_var], features="pre", isLabPanel=self._isLabPanel)
        else:
            # TODO: naming
            self._factory.addClinicalItemFeatures_UMich([self._lab_var], features="pre",
                                                        clinicalItemType=self._varTypeInTable,
                                                        clinicalItemTime='order_time',
                                                        tableName='labs') #sx

        # Add lab component result features, for a variety of time deltas.
        LAB_PRE_TIME_DELTAS = [datetime.timedelta(-14)]
        LAB_POST_TIME_DELTA = datetime.timedelta(0)
        log.info('Adding lab component features...')
        for pre_time_delta in LAB_PRE_TIME_DELTAS:
            log.info('\t%s' % pre_time_delta)
            self._factory.addLabResultFeatures(self._lab_components, False, pre_time_delta, LAB_POST_TIME_DELTA)

        FeatureMatrix._add_features(self, index_time_col='order_time')

    def write_matrix(self, dest_path):
        log.info('Writing %s...' % dest_path)
        header = self._build_matrix_header(dest_path)
        FeatureMatrix.write_matrix(self, dest_path, header)

    def _build_matrix_header(self, matrix_path):
        params = {}

        params['matrix_path'] = matrix_path
        params['matrix_module'] = inspect.getfile(inspect.currentframe())
        params['data_overview'] = self._build_data_overview()
        params['field_summary'] = self._build_field_summary()
        params['include_lab_suffix_summary'] = True
        params['include_clinical_item_suffix_summary'] = True

        return FeatureMatrix._build_matrix_header(self, params)

    def _build_data_overview(self):
        overview = list()
        # Overview:\n\
        line = 'Overview:'
        overview.append(line)
        # This file contains %s data rows, representing %s unique orders of
        line = 'This file contains %s data rows, representing %s unique orders of' % (self._num_reported_episodes, self._num_reported_episodes)
        overview.append(line)
        # the %s lab panel across %s inpatients from Stanford hospital.
        line = 'the %s lab across %s inpatients from Stanford hospital.' % (self._lab_var, self._num_patients)
        overview.append(line)
        # Each row contains columns summarizing the patient's demographics,
        line = "Each row contains columns summarizing the patient's demographics,"
        overview.append(line)
        # inpatient admit date, prior vitals, prior lab panel orders, and
        line = 'inpatient admit date, prior vitals, prior lab orders, and'
        overview.append(line)
        # prior lab component results. Note the distinction between a lab
        line = 'prior lab component results. NOte the distinction between a lab'
        overview.append(line)
        # panel (e.g. LABMETB) and a lab component within a panel (e.g. Na, RBC).
        line = 'panel (e.g. LABMETB) and a lab component within a panel (e.g. Na).'
        overview.append(line)
        # Most cells in matrix represent a count statistic for an event's
        line = "Most cells in matrix represent a count statistic for ran event's"
        overview.append(line)
        # occurrence or the difference between an event's time and order_time.
        line = "occurrence or the difference between an event's time and order_time."
        overview.append(line)

        return overview

    def _build_field_summary(self):
        summary = list()

        # Fields:
        line = 'Fields:'
        summary.append(line)
        #   pat_id - ID # for patient in the STRIDE data set. \n\
        line = 'pat_id - ID # for patient in the STRIDE data set.'
        summary.append(line)
        #   order_proc_id - ID # for clinical order. \n\
        line = 'order_proc_id - ID # for clinical order.'
        summary.append(line)
        #   proc_code - code representing ordered lab panel. \n\
        line = 'proc_code - code representing ordered lab panel.'
        summary.append(line)
        #   order_time - time at which lab panel was ordered. \n\
        line = 'order_time - time at which lab panel was ordered.'
        summary.append(line)
        #   abnormal_panel - were any components in panel abnormal (binary)? \n\
        line = 'abnormal_panel - were any components in panel abnoral (binary)?'
        summary.append(line)
        #   num_components - # of unique components in lab panel. \n\
        line = 'num_components - # of unique components in lab panel.'
        summary.append(line)
        #   num_normal_components - # of normal component results in panel. \n\
        line = 'num_normal_components - # of normal component results in panel.'
        summary.append(line)
        #   all_components_normal - inverse of abnormal_panel (binary). \n\
        line = 'all_components_normal - inverse of abnormal_panel (binary).'
        summary.append(line)
        #   AdmitDxDate.[clinical_item] - admit diagnosis, pegged to admit date.\n\
        line = 'AdmitDxDate.[clinical_item] - admit diagnosis, pegged to admit date.'
        summary.append(line)
        #   order_time.[month|hour] - when was the lab panel ordered? \n\
        line = 'order_time.[month|hour] - when was the lab panel ordered?'
        summary.append(line)
        #   Birth.preTimeDays - patient's age in days.\n\
        line = "Birth.preTimeDays - patient's age in days."
        summary.append(line)
        #   [Male|Female].pre - is patient male/female (binary)?\n\
        line = '[Male|Female].pre - is patient male/female (binary)?'
        summary.append(line)
        #   [RaceX].pre - is patient race [X]?\n\
        line = '[RaceX].pre - is patient race [X]?'
        summary.append(line)
        #   Team.[specialty].[clinical_item] - specialist added to treatment team.\n\
        line = 'Team.[specialty].[clinical_item] - specialist added to treatment team.'
        summary.append(line)
        #   Comorbidity.[disease].[clinical_item] - disease added to problem list.\n\
        line = 'Comorbidity.[disease].[clinical_item] - disease added to problem list.'
        summary.append(line)
        #   ___.[flowsheet] - measurements for flowsheet biometrics.\n\
        line = '___.[flowsheet] - measurements for flowsheet biometrics.'
        summary.append(line)
        #       Includes BP_High_Systolic, BP_Low_Diastolic, FiO2,\n\
        line = '    Includes BP_High_Systolic, BP_Low_Diastolic, FiO2,'
        summary.append(line)
        #           Glasgow Coma Scale Score, Pulse, Resp, Temp, and Urine.\n\
        line = '        Glasgow Coma Scale Score, Pulse, Resp, Temp, and Urine.'
        summary.append(line)
        #   %s.[clinical_item] - orders of the lab panel of interest.\n\
        line = '%s.[clinical_item] - orders of the lab panel of interest.' % self._lab_var
        summary.append(line)
        #   ___.[lab_result] - lab component results.\n\
        line = '__.[lab_result] - lab component results.'
        summary.append(line)
        #       Included standard components: WBC, HCT, PLT, NA, K, CO2, BUN,\n\
        line = '    Included standard components: WBC, HCT, PLT, NA, K, CO2, BUN,'
        summary.append(line)
        #           CR, TBIL, ALB, CA, LAC, ESR, CRP, TNI, PHA, PO2A, PCO2A,\n\
        line = '        CR, TBIL, ALB, CA, LAC, ESR, CRP, TNI, PHA, PO2A, PCO2A,'
        summary.append(line)
        #           PHV, PO2V, PCO2V\n\
        line = '        PHV, PO2V, PCO2V'
        summary.append(line)
        #       Also included %s panel components: %s\n\
        line = 'Also included %s panel components: %s' % (self._lab_var, self._lab_components)
        summary.append(line)

        return summary

if __name__ == "__main__":
    """Main method, callable from command line"""
    usageStr =  "usage: %prog [options]\n"

    parser = OptionParser(usage=usageStr)

    parser.add_option('-n', '--numRows', dest='numRows', metavar="<numRows>", help='The number of rows in resulting matrix')
    parser.add_option('-l', '--labCode', dest='lab', metavar='<lab>', help='proc_code for lab of interest')
    parser.add_option('-r', '--randomState', dest='randomState', metavar='<randomState>', help='Random state for consistent results')

    (options, args) = parser.parse_args(sys.argv[1:])

    log.info("Starting: "+str.join(" ", sys.argv))
    start_time = time.time()

    ltm = LabNormalityMatrix(options.lab, options.numRows, options.randomState)

    elapsed_time = numpy.ceil(time.time() - start_time)
    file_name = '%s-panel-%s-episodes-%s-sec.tab' % (options.lab, options.numRows, elapsed_time)
    ltm.write_matrix(file_name)

    timer = time.time() - timer
    log.info("%.3f seconds to complete",timer);
