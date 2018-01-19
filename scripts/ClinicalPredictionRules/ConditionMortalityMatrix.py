#!/usr/bin/python
"""
Utility class for constructing feature matrix that summarizes mortality
outcomes for patients who have a specified condition or disease.
"""

import datetime
import os

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery
from medinfo.dataconversion.FeatureMatrixFactory import FeatureMatrixFactory
from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO

class ConditionMortalityMatrix:
    def __init__(self, condition, num_patients, dest_path, icd_list=None):
        # Initialize FeatureMatrixFactory.
        self.factory = FeatureMatrixFactory()

        # Initialize DB connection.
        self._connection = DBUtil.connection()

        # If client doesn't supply icd_list, try to get it.
        self._condition = condition
        if icd_list is None:
            icd_list = self._get_icd_list()
            # If still haven't found anything, abort.
            if icd_list is None:
                raise ValueError('Unrecognized condition.')
        self._icd_list = icd_list

        # Query patient episodes.
        print 'Querying patient episodes...'
        self._num_patients = num_patients
        patient_list = self._get_random_patient_list()
        self._query_patient_episodes()

        # Add time features.
        print 'Adding time features...'
        self._add_time_features()
        # Add demographic features.
        print 'Adding demographic features...'
        self._add_demographic_features()
        # Add treatment team features.
        print 'Adding treatment team features...'
        self.factory.addTreatmentTeamFeatures(features="pre")
        # Add Charlson Comorbidity features.
        print 'Adding comorbidity features...'
        self.factory.addCharlsonComorbidityFeatures(features="pre")
        # Add flowsheet vitals features.
        print 'Adding flowsheet features...'
        self._add_flowsheet_features()
        # Add lab panel order and component result features.
        print 'Adding lab component features...'
        self._add_lab_component_features()
        # Build matrix.
        print 'Building feature matrix...'
        self._dest_path = dest_path
        header = self._build_matrix_header()
        self.factory.buildFeatureMatrix(header, self._dest_path)

    def icd_list(self):
        return self._icd_list

    def _get_icd_list(self):
        # Initialize DB cursor.
        cursor = self._connection.cursor()

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
        self._icd_list = icd_list

        return icd_list

    def _get_random_patient_list(self):
        # Initialize DB cursor.
        cursor = self._connection.cursor()

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

        # Fetch and return results.
        cursor.execute(str(query), query.params)
        self.factory.setPatientEpisodeInput(cursor, 'pat_id', 'index_time')
        self.factory.processPatientEpisodeInput()

    def _build_matrix_header(self):
        # FeatureMatrixFactory and FeatureMatrixIO expect a list of strings.
        # Each comment below represents the line in the comment.
        header = list()

        # <file_name.tab>
        file_name = self._dest_path.split('/')[-1]
        header.append(file_name)
        # Created: <timestamp>
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        header.append('Created: %s' % timestamp)
        # Source: __name__
        header.append('Source: %s' % __name__)
        # Command: ConditionMortalityMatrix().write_matrix(file_name)
        command = 'ConditionMortalityMatrix(%s, %s).write_matrix(%s)' % \
            (self._condition, self._num_patients, file_name)
        header.append('Command: %s' % command)
        #
        header.append('')
        # Overview:
        header.append('Overview:')
        # This file contains ___ data rows, representing ___ unique inpatients
        line = 'This file contains %s data rows, representing %s unique inpatients' % (self.factory.getNumRows(), self._num_patients)
        header.append(line)
        # from Stanford hospital, all of which had ___ in their problem list.
        line = 'from Stanford hospital, all of which had %s in their problem list.' % self._condition
        header.append(line)
        # ___ is defined by the following ICD codes:
        line = '%s is defined by the following ICD codes:'
        header.append(line)
        #   ICD9.X, ICD.Y, ICD.Z
        line = '  %s' % ', '.join(self._icd_list)
        # Each row represents a decision point (proxied by clinical order).
        line = 'Each row represents a decision point (proxied by clinical order).'
        header.append(line)
        # Each row contains fields summarizing the patient's demographics,
        line = "Each row contains fields summarizing the patient's demographics"
        header.append(line)
        # inpatient admit date, prior vitals, and prior lab results.
        line = 'inpatient admit date, prior vitals, and prior lab results.'
        header.append(line)
        # Most cells in matrix represent a count statistic for an event's
        line = "Most cells in matrix represent a count statistic for an event's"
        header.append(line)
        # occurrence or a difference between an event's time and index_time.
        line = "occurrence or a difference between an event's time and index_time."
        header.append(line)
        #
        header.append('')
        # Fields:
        header.append('Fields:')
        #   pat_id - ID # for patient in the STRIDE data set.
        header.append('  pat_id - ID # for patient in the STRIDE data set.')
        #   index_time - time at which clinical decision was made.
        header.append('  index_time - time at which clinical decision was made.')
        #   death_date - if patient died, date on which they died.
        header.append('  death_date - if patient died, date on which they died.')
        #   AdmitDxDate.[clinical_item] - admit diagnosis, pegged to admit date.
        header.append('  AdmitDxDate.[clinical_item] - admit diagnosis, pegged to admit date.')
        #   Birth.preTimeDays - patient's age in days.
        header.append("  Birth.preTimeDays - patient's age in days.")
        #   [Male|Female].pre - is patient male/female (binary)?
        header.append('  [Male|Female].pre - is patient male/female (binary)?')
        #   [RaceX].pre - is patient race [X]?
        header.append('  [RaceX].pre - is patient race [X]?')
        #   Team.[specialty].[clinical_item] - specialist added to treatment team.
        header.append('  Team.[specialty].[clinical_item] - specialist added to treatment team.')
        #   Comorbidity.[disease].[clinical_item] - disease added to problem list.
        header.append('  Comorbidity.[disease].[clinical_item] - disease added to problem list.')
        #   ___.[flowsheet] - measurements for flowsheet biometrics.
        header.append('  ___.[flowsheet] - measurements for flowsheet biometrics.')
        #       Includes BP_High_Systolic, BP_Low_Diastolic, FiO2,
        header.append('    Includes BP_High_Systolic, BP_Low_Diastolic, FiO2,')
        #           Glasgow Coma Scale Score, Pulse, Resp, Temp, and Urine.
        header.append('      Glasgow Coma Scale Score, Pulse, Resp, Temp, and Urine.')
        #   ___.[lab_result] - lab component results.
        header.append('  ___.[lab_result] - lab component results.')
        #       Included standard components: WBC, HCT, PLT, NA, K, CO2, BUN,
        header.append('    Included standard components: WBC, HCT, PLT, NA, K, CO2, BUN,')
        #           CR, TBIL, ALB, CA, LAC, ESR, CRP, TNI, PHA, PO2A, PCO2A,
        header.append('      CR, TBIL, ALB, CA, LAC, ESR, CRP, TNI, PHA, PO2A, PCO2A,')
        #           PHV, PO2V, PCO2V
        header.append('      PHV, PO2V, PCO2V')
        #
        header.append('')
        #   [clinical_item] fields may have the following suffixes:
        header.append('  [clinical_item] fields may have the following suffixes:')
        #       ___.pre - how many times has this occurred before order_time?
        header.append('    ___.pre - how many times has this occurred before order_time?')
        #       ___.pre.Xd - how many times has this occurred within X days before index_time?
        header.append('    ___.pre.Xd - how many times has this occurred within X days before index_time?')
        #       ___.preTimeDays - how many days before order_time was last occurrence?
        header.append('    ___.preTimeDays - how many days before order_time was last occurrence?')
        #
        header.append('')
        #   [flowsheet] and [lab_result] fields may have the following suffixes:
        header.append('  [flowsheet] and [lab_result] fields may have the following suffixes:')
        #       ___.X_Y.count - # of result values between X and Y days of index_time.
        header.append('    ___.X_Y.count - # of result values between X and Y days of index_time.')
        #       ___.X_Y.countInRange - # of result values in normal range.
        header.append('    ___.X_Y.countInRange - # of result values in normal range.')
        #       ___.X_Y.min - minimum result value.
        header.append('    ___.X_Y.min - minimum result value.')
        #       ___.X_Y.max - maximum result value.
        header.append('    ___.X_Y.max - maximum result value.')
        #       ___.X_Y.median - median result value.
        header.append('    ___.X_Y.median - median result value.')
        #       ___.X_Y.std - standard deviation of result values.
        header.append('    ___.X_Y.std - standard deviation of result values.')
        #       ___.X_Y.first - first result value.
        header.append('    ___.X_Y.first - first result value.')
        #       ___.X_Y.last - last result value.
        header.append('    ___.X_Y.last - last result value.')
        #       ___.X_Y.diff - difference between penultimate and proximate values.
        header.append('    ___.X_Y.diff - difference between penultimate and proximate values.')
        #       ___.X_Y.slope - slope between penultimate and proximate values.
        header.append('    ___.X_Y.slope - slope between penultimate and proximate values.')
        #       ___.X_Y.proximate - closest result value to order_time.
        header.append('    ___.X_Y.proximate - closest result value to order_time.')
        #       ___.X_Y.firstTimeDays - time between first and order_time.
        header.append('    ___.X_Y.firstTimeDays - time between first and order_time.')
        #       ___.X_Y.lastTimeDays - time between last and order_time.
        header.append('    ___.X_Y.lastTimeDays - time between last and order_time.')
        #       ___.X_Y.proximateTimeDays - time between proximate and order_time.
        header.append('    ___.X_Y.proximateTimeDays - time between proximate and order_time.')

        return header

    def _add_time_features(self):
        # Add admission date.
        ADMIT_DX_CATEGORY_ID = 2
        self.factory.addClinicalItemFeaturesByCategory([ADMIT_DX_CATEGORY_ID], \
            dayBins=[], label="AdmitDxDate", features="pre")

        # Add time cycle features.
        self.factory.addTimeCycleFeatures("index_time", "month")
        self.factory.addTimeCycleFeatures("index_time", "hour")

    def _add_demographic_features(self):
        self.factory.addClinicalItemFeatures(['Birth'], dayBins=[], features="pre")
        self.factory.addClinicalItemFeatures(['Death'], dayBins=[], features="post")
        self.factory.addSexFeatures()
        self.factory.addRaceFeatures()

    def _add_flowsheet_features(self):
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

    def _add_lab_component_features(self):
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

if __name__ == "__main__":
    dest_path = 'pneumonia-morbidity-10-epi.tab'
    pneumonia = ConditionMortalityMatrix('pneumonia', 10, dest_path)
