#!/usr/bin/python
"""
Utility class for constructing feature matrix that summarizes mortality
outcomes for patients who have a specified condition or disease.
"""

import datetime
import inspect
import os

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery
from medinfo.dataconversion.FeatureMatrix import FeatureMatrix
from medinfo.dataconversion.FeatureMatrixFactory import FeatureMatrixFactory
from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO
from medinfo.common.Util import log

class ConditionMortalityMatrix(FeatureMatrix):
    def __init__(self, condition, num_patients, params=None):
        # params['icd_list'] = list of ICD codes for condition.
        FeatureMatrix.__init__(self, condition, num_patients)

        # Initialize DB connection.
        self._connection = DBUtil.connection()

        # If client doesn't supply icd_list, try to get it.
        self._condition = condition
        if params is not None and params.get('icd_list'):
            icd_list = params['icd_list']
        else:
            icd_list = self._get_icd_list()
        # If still haven't found anything, abort.
        if icd_list is None:
            raise ValueError('Unrecognized condition.')
        self._icd_list = icd_list
        log.info('%s ICDs: %s' % (self._condition, self._icd_list))

        # Query patient episodes.
        self._num_patients = num_patients
        self._query_patient_episodes()

        # Add features.
        FeatureMatrix._add_features(self)

        # Build matrix.
        FeatureMatrix._build_matrix(self)

    def icd_list(self):
        return self._icd_list

    def _get_icd_list(self):
        # Build query.
        # Try to optimistically find any related ICD codes.
        #
        # SELECT
        #   name AS icd
        # FROM
        #   clinical_item
        # WHERE
        #   clinical_item_category_id = 1 AND ## PROBLEM_LIST
        #   (
        #       description LIKE '%condition.lower()%' OR
        #       description LIKE '%condition.upper()%' OR
        #       description LIKE '%condition.capitalize()%'
        #   ) AND
        #   (
        #       NOT description LIKE ICD_CODES_TO_IGNORE
        #   )
        # GROUP BY
        #   icd
        #
        # TODO(sbala): Ignore certain ICD codes.
        # ICD_CODES_TO_IGNORE = [
        #     # Personal and family history, as these are not present condition.
        #     'V10', 'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18', 'V19'
        # ]
        query = SQLQuery()
        query.addSelect('name AS icd')
        query.addFrom('clinical_item')
        query.addWhereEqual('clinical_item_category_id', 1)
        query.openWhereOrClause()
        query.addWhereLike('description', '%%%s%%' % self._condition.lower())
        query.addWhereLike('description', '%%%s%%' % self._condition.upper())
        query.addWhereLike('description', '%%%s%%' % self._condition.capitalize())
        query.closeWhereOrClause()
        query.addGroupBy('icd')

        # Execute query and fetch results.
        results = DBUtil.execute(query)
        icd_list = [result[0] for result in results]

        return icd_list

    def _get_random_patient_list(self):
        # Build query.
        # We're interested in all clinical decision moments for all patients
        # who have 'condition' in their problem list.
        #
        # The full set of 'decision moments' is captured by stride_order_proc.
        #
        # For most patients, information will vary across time points.
        # For example, if physician orders A1C lab panel, there will an episode
        # before and after results, one with and without that information.
        # For learning, it's fine to treat these as independent events, and
        # trust the algorithms to learn whether A1C is helpful.
        #
        # SELECT
        #   CAST(pi.patient_id AS bigint)
        # FROM
        #   patient_item AS pi,
        #   clinical_item AS ci,
        #   clinical_item_category AS cic
        # WHERE
        #   pi.clinical_item_id = ci.clinical_item_id AND
        #   ci.clinical_item_category_id = cic.clinical_item_category_id AND
        #   clinical_item_category = 1 AND ## (PROBLEM_LIST)
        #   ci.name in (icd_list)
        # LIMIT
        #   self._num_patients
        query = SQLQuery()
        query.addSelect('CAST(pi.patient_id AS bigint)')
        query.addFrom('patient_item AS pi')
        query.addFrom('clinical_item AS ci')
        query.addFrom('clinical_item_category AS cic')
        query.addWhere('pi.clinical_item_id = ci.clinical_item_id')
        query.addWhere('ci.clinical_item_category_id = cic.clinical_item_category_id')
        query.addWhereEqual('cic.clinical_item_category_id', 1)
        query.addWhereIn('ci.name', self._icd_list)
        query.setLimit(self._num_patients)

        # Fetch and return results.
        results = DBUtil.execute(query)
        patient_list = [result[0] for result in results]

        return patient_list

    def _query_patient_episodes(self):
        log.info('Querying patient episodes...')
        # Initialize DB cursor.
        cursor = self._connection.cursor()

        # Get random list of self._num_patients patients to query.
        random_patient_list = self._get_random_patient_list()

        # Build query.
        # SELECT
        #   CAST(sop.pat_id AS bigint),
        #   sop.order_time AS index_time,
        #   sp.death_date AS death_date
        # FROM
        #   stride_order_proc AS sop,
        #   stride_patient AS sp
        # WHERE
        #   sop.pat_id = sp.pat_id AND
        #   sop.pat_id IN random_patient_list
        # GROUP BY
        #   pat_id,
        #   index_time,
        #   death_date
        # ORDER BY
        #   pat_id,
        #   index_time,
        #   death_date
        #
        # TODO(sbala): Investigate whether it's possible to get a timestamp
        # for the death, not just the death date. Both stride_patient and
        # patient_item only have death date, but stride_order_proc might.
        # Haven't been able to find the corresponding order_proc_id.
        DECISION_ORDER_TYPES = ['Lab', 'ECHO', 'Pharmacy Consult',
            'Point of Care Testing']
        query = SQLQuery()
        query.addSelect('CAST(sop.pat_id AS bigint)')
        query.addSelect('sop.order_time AS index_time')
        query.addSelect('sp.death_date AS death_date')
        query.addFrom('stride_order_proc AS sop')
        query.addFrom('stride_patient AS sp')
        query.addWhere('sop.pat_id = sp.pat_id')
        query.addWhereEqual('order_class', 'Normal')
        query.addWhere('NOT sop.order_time IS NULL')
        query.addWhereIn('CAST(sop.pat_id AS bigint)', random_patient_list)
        query.addGroupBy('sop.pat_id')
        query.addGroupBy('index_time')
        query.addGroupBy('death_date')
        query.addOrderBy('sop.pat_id')
        query.addOrderBy('index_time')
        query.addOrderBy('death_date')

        FeatureMatrix._query_patient_episodes(self, query)

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

        # Overview:
        overview.append('Overview:')
        # This file contains ___ data rows, representing ___ unique inpatients
        line = 'This file contains %s data rows, representing %s unique inpatients' % (self._factory.getNumRows(), self._num_patients)
        overview.append(line)
        # from Stanford hospital, all of which had ___ in their problem list.
        line = 'from Stanford hospital, all of which had %s in their problem list.' % self._condition
        overview.append(line)
        # ___ is defined by the following ICD codes:
        line = '%s is defined by the following ICD codes:'
        overview.append(line)
        #   ICD9.X, ICD.Y, ICD.Z
        line = '  %s' % ', '.join(self._icd_list)
        overview.append(line)
        # Each row represents a decision point (proxied by clinical order).
        line = 'Each row represents a decision point (proxied by clinical order).'
        overview.append(line)
        # Each row contains fields summarizing the patient's demographics,
        line = "Each row contains fields summarizing the patient's demographics"
        overview.append(line)
        # inpatient admit date, prior vitals, and prior lab results.
        line = 'inpatient admit date, prior vitals, and prior lab results.'
        overview.append(line)
        # Most cells in matrix represent a count statistic for an event's
        line = "Most cells in matrix represent a count statistic for an event's"
        overview.append(line)
        # occurrence or a difference between an event's time and index_time.
        line = "occurrence or a difference between an event's time and index_time."
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
        #   index_time - time at which clinical decision was made.
        summary.append('index_time - time at which clinical decision was made.')
        #   death_date - if patient died, date on which they died.
        summary.append('death_date - if patient died, date on which they died.')
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

        return summary

if __name__ == "__main__":
    dest_path = 'pneumonia-morbidity-10-epi.tab'
    pneumonia = ConditionMortalityMatrix('pneumonia', 10, dest_path)
