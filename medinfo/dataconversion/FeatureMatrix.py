#!/usr/bin/python
"""
Abstract class for building raw feature matrices.
This class should take care of the business logic of interacting
with FeatureMatrixFactory and FeatureMatrixIO, allowing subclasses
to just worry about defining parameters for matrix construction.
"""

import os
import datetime

from medinfo.dataconversion.FeatureMatrixIO import FeatureMatrixIO

import LocalEnv
from medinfo.dataconversion.FeatureMatrixFactory import FeatureMatrixFactory
from medinfo.db import DBUtil
from Util import log

class FeatureMatrix:
    def __init__(self, variable, num_data_points, params=None):
        # Process arguments.
        self._var = variable
        self._num_rows = num_data_points
        if params is None:
            self._params = {}
        else:
            self._params = params

        # Initialize FeatureMatrixFactory.
        self._factory = FeatureMatrixFactory()

        # Initialize DB connection.
        self._connection = DBUtil.connection()

    def _query_patient_episodes(self, query, pat_id_col=None, index_time_col=None):
        # Initialize DB cursor.
        cursor = self._connection.cursor()

        # Fetch and return results.
        log.info('query: %s' % str(query))

        if isinstance(query, basestring):
            cursor.execute(query)
        else:
            log.info('query.params: %s' % str(query.params))
            cursor.execute(str(query), query.params)

        # Parse arguments.
        if pat_id_col is None:
            pat_id_col = 'pat_id'
        if index_time_col is None:
            index_time_col = 'index_time'

        self._factory.setPatientEpisodeInput(cursor, pat_id_col, index_time_col)
        num_episodes = self._factory.processPatientEpisodeInput()

        return num_episodes

    def _querystr_patient_episodes(self, querystr, pat_id_col=None, index_time_col=None):
        # Initialize DB cursor.
        cursor = self._connection.cursor()

        # Fetch and return results.
        log.info('query: %s' % querystr)
        cursor.execute(querystr)

        # Parse arguments.
        if pat_id_col is None:
            pat_id_col = 'pat_id'
        if index_time_col is None:
            index_time_col = 'index_time'

        self._factory.setPatientEpisodeInput(cursor, pat_id_col, index_time_col)
        num_episodes = self._factory.processPatientEpisodeInput()

        return num_episodes

    def _add_features(self, index_time_col=None):

        if LocalEnv.DATASET_SOURCE_NAME == 'STRIDE':
            self._add_time_features(index_time_col)
            self._add_demographic_features()
            self._add_treatment_team_features()
            self._add_comorbidity_features()
            self._add_flowsheet_features()
            self._add_lab_component_features()
        else:
        # elif LocalEnv.DATASET_SOURCE_NAME == 'UMich':
            self._add_time_features(index_time_col)
            self._add_demographic_features()
            self._add_comorbidity_features()
            self._add_lab_component_features()

            if LocalEnv.DATASET_SOURCE_NAME == 'UCSF':
                self._add_treatment_team_features()
                self._add_flowsheet_features()

    def _add_time_features(self, index_time_col=None):
        log.info('Adding admit date features...')
        # Add admission date.
        ADMIT_DX_CATEGORY_ID = 2

        if LocalEnv.DATASET_SOURCE_NAME == 'STRIDE':
            self._factory.addClinicalItemFeaturesByCategory([ADMIT_DX_CATEGORY_ID], \
                                                            dayBins=[], label='AdmitDxDate', features='pre')
        else:
        #elif LocalEnv.DATASET_SOURCE_NAME == 'UMich':
            self._factory.addClinicalItemFeaturesByCategory_UMich([ADMIT_DX_CATEGORY_ID], \
            dayBins=[], label='AdmitDxDate', features='pre', tableName='encounters')



        # Add time cycle features.
        log.info('Adding time cycle features...')
        if index_time_col is None:
            index_time_col = 'index_time'
        self._factory.addTimeCycleFeatures(index_time_col, 'month')
        self._factory.addTimeCycleFeatures(index_time_col, 'hour')

    def _add_demographic_features(self):
        log.info('Adding demographic features...')
        # Add birth and death.
        self._add_lifespan_features()
        # Add sex features.
        self._add_sex_features()
        # Add race features.
        self._add_race_features()

    def _add_lifespan_features(self):
        log.info('Adding lifespan features...')

        if LocalEnv.DATASET_SOURCE_NAME == 'STRIDE': # TODO
            self._factory.addClinicalItemFeatures(['Birth'], dayBins=[], features="pre")
            self._factory.addClinicalItemFeatures(['Death'], dayBins=[], features="post")
        else:
        #elif LocalEnv.DATASET_SOURCE_NAME == 'UMich':
            self._factory.addClinicalItemFeatures_UMich(['Birth'], dayBins=[], features="pre",
                                                        clinicalItemType=None, clinicalItemTime='Birth',
                                                        tableName='pt_info')

    def _add_sex_features(self):
        log.info('Adding sex features...')
        SEX_FEATURES = ["Male", "Female"]
        for feature in SEX_FEATURES:
            if LocalEnv.DATASET_SOURCE_NAME == 'STRIDE':  # TODO
                self._factory.addClinicalItemFeatures([feature], dayBins=[], features="pre")
            else:
            #elif LocalEnv.DATASET_SOURCE_NAME == 'UMich':
                self._factory.addClinicalItemFeatures_UMich([feature], dayBins=[], features="pre",
                                                   clinicalItemType='GenderName', clinicalItemTime=None, tableName="demographics")
    def _add_race_features(self):
        log.info('Adding race features...')
        for feature in self._factory.queryAllRaces():
            if LocalEnv.DATASET_SOURCE_NAME == 'STRIDE':  # TODO
                self._factory.addClinicalItemFeatures([feature], dayBins=[], features="pre")
            else:
            #elif LocalEnv.DATASET_SOURCE_NAME == 'UMich':
                self._factory.addClinicalItemFeatures_UMich([feature], dayBins=[], features="pre",
                                                  clinicalItemType='RaceName', clinicalItemTime=None, tableName='demographics')

    def _add_treatment_team_features(self):
        log.info('Adding treatment team features...')
        self._factory.addTreatmentTeamFeatures(features="pre")

    def _add_comorbidity_features(self):
        log.info('Adding comorbidity features...')
        self._factory.addCharlsonComorbidityFeatures(features='pre')

    def _add_flowsheet_features(self):
        log.info('Adding flowsheet features...')
        # Look at flowsheet results from the previous days
        FLOW_PRE_TIME_DELTAS = [ datetime.timedelta(-3) ]
        # Don't look into the future, otherwise cheating the prediction
        FLOW_POST_TIME_DELTA = datetime.timedelta(0)
        # Add flowsheet features for a variety of generally useful vitals.
        if LocalEnv.DATASET_SOURCE_NAME == 'STRIDE':
            BASIC_FLOWSHEET_FEATURES = [
                "BP_High_Systolic", "BP_Low_Diastolic", "FiO2",
                "Glasgow Coma Scale Score", "Pulse", "Resp", "Temp", "Urine"
            ]
        elif LocalEnv.DATASET_SOURCE_NAME == 'UCSF':
            BASIC_FLOWSHEET_FEATURES = [
                'SBP', 'DBP', 'FiO2', 'Pulse', 'Resp', 'Temp', 'o2flow'
            ]
        for pre_time_delta in FLOW_PRE_TIME_DELTAS:
            log.info('\t\tpreTimeDelta: %s' % pre_time_delta)
            self._factory.addFlowsheetFeatures(BASIC_FLOWSHEET_FEATURES, \
                pre_time_delta, FLOW_POST_TIME_DELTA)

    def _add_lab_component_features(self):
        # Look for lab data 90 days before each episode, but never after self.
        # Look at lab results from the previous days
        LAB_PRE_TIME_DELTAS = [ datetime.timedelta(-14) ]
        # Don't look into the future, otherwise cheating the prediction
        LAB_POST_TIME_DELTA = datetime.timedelta(0)

        # Add result features for a variety of generally useful components.
        if LocalEnv.DATASET_SOURCE_NAME == 'STRIDE':
            BASIC_LAB_COMPONENTS = [
                'WBC',  # White Blood Cell
                'HCT',  # Hematocrit
                'PLT',  # Platelet Count
                'NA',  # Sodium, Whole Blood
                'K',  # Potassium, Whole Blood
                'CO2',  # CO2, Serum/Plasma
                'BUN',  # Blood Urea Nitrogen
                'CR',  # Creatinine
                'TBIL',  # Total Bilirubin
                'ALB',  # Albumin
                'CA',  # Calcium
                'LAC',  # Lactic Acid
                'ESR',  # Erythrocyte Sedimentation Rate
                'CRP',  # C-Reactive Protein
                'TNI',  # Troponin I
                'PHA',  # Arterial pH
                'PO2A',  # Arterial pO2
                'PCO2A',  # Arterial pCO2
                'PHV',  # Venous pH
                'PO2V',  # Venous pO2
                'PCO2V'  # Venous pCO2
            ]
        elif LocalEnv.DATASET_SOURCE_NAME == 'UMich':
            BASIC_LAB_COMPONENTS = [
                'WBC',  # White Blood Cell
                'HCT',  # Hematocrit
                'PLT',  # Platelet Count
                'SOD',  # Sodium, Whole Blood
                'POT',  # Potassium, Whole Blood
                'CO2',  # CO2, Serum/Plasma
                'UN',  # Blood Urea Nitrogen
                'CREAT',  # Creatinine
                'TBIL',  # Total Bilirubin
                'ALB',  # Albumin
                'CAL',  # Calcium
                'LACTA',  # Lactic Acid; LACTA & LACTV are more frequent
                "WEST",  # Erythrocyte Sedimentation Rate
                'CRP',  # C-Reactive Protein
                'TROP',  # Troponin I
                'pHA',  # Arterial pH
                'PO2AA',  # Arterial pO2
                'PCOAA2',  # Arterial pCO2
                'pHV',  # Venous pH
                'pO2V',  # Venous pO2
                'pCO2V',  # Venous pCO2
            ]
        elif LocalEnv.DATASET_SOURCE_NAME == 'UCSF':
            BASIC_LAB_COMPONENTS = [
                'WBC',  # White Blood Cell
                'HCT',  # Hematocrit
                'PLT',  # Platelet Count
                'NAWB',  # Sodium, Whole Blood
                'K',  # Potassium, Whole Blood
                'CO2',  # CO2, Serum/Plasma
                'BUN',  # Blood Urea Nitrogen
                'CREAT',  # Creatinine
                'TBILI',  # Total Bilirubin
                'ALB',  # Albumin
                'CA',  # Calcium
                'LACTWB',  # Lactic Acid; LACTA & LACTV are more frequent
                "ESR",  # Erythrocyte Sedimentation Rate
                'CRP',  # C-Reactive Protein
                'TRPI',  # Troponin I
                'PH37',  # Arterial pH
                'PO2',  # Arterial pO2
                'PCO2'  # Arterial pCO2
                # 'pHV',  # Venous pH
                # 'pO2V',  # Venous pO2
                # 'pCO2V',  # Venous pCO2
            ]
        log.info('Adding lab component features...')
        for component in BASIC_LAB_COMPONENTS:
            log.info('\t%s' % component)
            for preTimeDelta in LAB_PRE_TIME_DELTAS:
                log.info('\t\t%s' % preTimeDelta)
                self._factory.addLabResultFeatures([component], False, preTimeDelta, LAB_POST_TIME_DELTA)

    def _build_matrix(self, header=None, dest_path=None):
        log.info('Building matrix...')
        self._factory.buildFeatureMatrix(header, dest_path)

    def write_matrix(self, dest_path, header=None):
        log.info('Writing matrix file...')
        fm_io = FeatureMatrixIO()
        # Get old matrix file.
        source_path = self._factory.getMatrixFileName()
        # Write to new matrix filee.
        matrix_file = open(dest_path, 'w')
        for line in header:
            matrix_file.write('# %s\n' % line)
        for line in open(source_path, 'r'):
            if line[0] != '#':
                matrix_file.write(line)
        # Delete old matrix file.
        os.remove(source_path)

    def _build_matrix_header(self, params=None):
        # params['include_lab_suffix_summary'] = True/False
        # params['include_clinical_item_suffix_summary'] = True/False
        # params['data_overview'] = str description.
        # params['field_summary'] = str description
        header = list()

        file_summary = self._build_file_summary(params['matrix_path'], \
            params['matrix_module'])
        header.extend(file_summary)
        header.extend([''])

        if params.get('data_overview'):
            header.extend(params['data_overview'])
            header.extend([''])
        if params.get('field_summary'):
            header.extend(params['field_summary'])
            header.extend([''])
        if params.get('include_clinical_item_suffix_summary'):
            ci_suffix_summary = self._build_clinical_item_suffix_summary()
            header.extend(ci_suffix_summary)
            header.extend([''])
        if params.get('include_lab_suffix_summary'):
            lab_suffix_summary = self._build_flowsheet_and_lab_result_suffix_summary()
            header.extend(lab_suffix_summary)
            header.extend([''])

        return header

    def _build_file_summary(self, matrix_path, matrix_module):
        summary = list()

        # <file_name.tab>
        matrix_name = matrix_path.split('/')[-1]
        summary.append(matrix_name)
        # Created: <timestamp>
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        summary.append('Created: %s' % timestamp)
        # Source: __name__
        module_name = matrix_module.split('/')[-1]
        summary.append('Source: %s' % module_name)
        # Command: Pipeline()
        class_name = module_name.split('.')[0]
        args = [self._var, str(self._num_rows)]
        for key, value in self._params:
            args.append('%s=%s' % (key, value))
        command = '%s(%s)' % (class_name, ', '.join(args))
        summary.append('Command: %s' % command)

        return summary

    def _build_clinical_item_suffix_summary(self):
        summary = list()
        #   [clinical_item] fields may have the following suffixes:
        summary.append('  [clinical_item] fields may have the following suffixes:')
        #       ___.pre - how many times has this occurred before order_time?
        summary.append('    ___.pre - how many times has this occurred before order_time?')
        #       ___.pre.Xd - how many times has this occurred within X days before index_time?
        summary.append('    ___.pre.Xd - how many times has this occurred within X days before index_time?')
        #       ___.preTimeDays - how many days before order_time was last occurrence?
        summary.append('    ___.preTimeDays - how many days before order_time was last occurrence?')

        return summary

    def _build_flowsheet_and_lab_result_suffix_summary(self):
        summary = list()
        #   [flowsheet] and [lab_result] fields may have the following suffixes:
        summary.append('  [flowsheet] and [lab_result] fields may have the following suffixes:')
        #       ___.X_Y.count - # of result values between X and Y days of index_time.
        summary.append('    ___.X_Y.count - # of result values between X and Y days of index_time.')
        #       ___.X_Y.countInRange - # of result values in normal range.
        summary.append('    ___.X_Y.countInRange - # of result values in normal range.')
        #       ___.X_Y.min - minimum result value.
        summary.append('    ___.X_Y.min - minimum result value.')
        #       ___.X_Y.max - maximum result value.
        summary.append('    ___.X_Y.max - maximum result value.')
        #       ___.X_Y.median - median result value.
        summary.append('    ___.X_Y.median - median result value.')
        #       ___.X_Y.std - standard deviation of result values.
        summary.append('    ___.X_Y.std - standard deviation of result values.')
        #       ___.X_Y.first - first result value.
        summary.append('    ___.X_Y.first - first result value.')
        #       ___.X_Y.last - last result value.
        summary.append('    ___.X_Y.last - last result value.')
        #       ___.X_Y.diff - difference between penultimate and proximate values.
        summary.append('    ___.X_Y.diff - difference between penultimate and proximate values.')
        #       ___.X_Y.slope - slope between penultimate and proximate values.
        summary.append('    ___.X_Y.slope - slope between penultimate and proximate values.')
        #       ___.X_Y.proximate - closest result value to order_time.
        summary.append('    ___.X_Y.proximate - closest result value to order_time.')
        #       ___.X_Y.firstTimeDays - time between first and order_time.
        summary.append('    ___.X_Y.firstTimeDays - time between first and order_time.')
        #       ___.X_Y.lastTimeDays - time between last and order_time.
        summary.append('    ___.X_Y.lastTimeDays - time between last and order_time.')
        #       ___.X_Y.proximateTimeDays - time between proximate and order_time.
        summary.append('    ___.X_Y.proximateTimeDays - time between proximate and order_time.')

        return summary
