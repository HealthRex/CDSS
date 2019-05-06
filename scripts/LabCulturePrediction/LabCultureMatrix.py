#!/usr/bin/python
"""
Class for generating LabCultureMatrix.
"""

import datetime
import inspect
import logging
import os
import sys
import time
import numpy
import pandas as pd

from medinfo.common.Util import log
from medinfo.dataconversion.FeatureMatrixFactory import FeatureMatrixFactory
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery
from medinfo.dataconversion.FeatureMatrix import FeatureMatrix

class LabCultureMatrix(FeatureMatrix):
    def __init__(self, lab_panel, num_episodes, random_state=None):
        FeatureMatrix.__init__(self, lab_panel, num_episodes)

        # Parse arguments.
        self._lab_panel = lab_panel.split()

        self._med_panel = [['Cefepime (Oral)', 'Cefepime (Intravenous)'],
                            ['Cefazolin (Oral)', 'Cefazolin (Intravenous)'],
                            ['Ceftriaxone (Oral)', 'Ceftriaxone (Intravenous)'],
                            ['Meropenem (Oral)', 'Meropenem (Intravenous)'],
                            ['Vancomycin (Oral)', 'Vancomycin (Intravenous)'],
                            ['Linezolid (Oral)', 'Linezolid (Intravenous)'],
                            ['Daptomycin (Oral)', 'Daptomycin (Intravenous)'],
                            ['Levofloxacin (Oral)', 'Levofloxacin (Intravenous)'],
                            ['Ciprofloxacin (Oral)', 'Ciprofloxacin (Intravenous)'],
                            ['Ampicillin (Oral)', 'Ampicillin (Intravenous)'],
                            ['Metronidazole (Oral)', 'Metronidazole (Intravenous)'],
                            ['Caspofungin (Oral)', 'Caspofungin (Intravenous)']]
        # susceptibility_df = pd.read_csv('/Users/conorcorbin/repos/CDSS/scripts/LabCulturePrediction/Susceptibility_Feature_Names.csv')
        susceptibility_df = pd.read_csv('/home/ec2-user/CDSS/scripts/LabCulturePrediction/Susceptibility_Feature_Names.csv')
        self._susceptibility_names = susceptibility_df['name'].values        
        self._num_requested_episodes = num_episodes
        self._num_reported_episodes = 0

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
        # Initialize DB connection.
        cursor = self._connection.cursor()

        # Doing a single query results in a sequential scan through
        # stride_order_results. To avoid this, break up the query in two.

        # First, get all the order_proc_ids for proc_code.
        query = SQLQuery()
        query.addSelect('order_proc_id')
        query.addFrom('stride_order_proc')
        query.addWhereIn('proc_code', self._lab_panel)
        query.addGroupBy('order_proc_id')
        log.debug('Querying order_proc_ids for... %s' % ','.join(self._lab_panel))
        results = DBUtil.execute(query)
        lab_order_ids = [row[0] for row in results]

        # Second, get all base_names from those orders.
        query = SQLQuery()
        query.addSelect('base_name')
        query.addFrom('stride_order_results')
        query.addWhereIn('order_proc_id', lab_order_ids)
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
        query.addSelect('pat_id')
        query.addSelect('COUNT(sop.order_proc_id) AS num_orders')
        query.addFrom('stride_order_proc AS sop')
        query.addFrom('stride_order_results AS sor')
        query.addWhere('sop.order_proc_id = sor.order_proc_id')
        query.addWhereIn("proc_code", self._lab_panel)
        components = self._get_components_in_lab_panel()
        query.addWhereIn("base_name", components)
        query.addGroupBy('pat_id')
        log.debug('Querying median orders per patient...')
        results = DBUtil.execute(query)
        order_counts = [ row[1] for row in results ]
        if len(order_counts) == 0:
            error_msg = '0 orders for lab panel %s' % ','.join(self._lab_panel)
            log.critical(error_msg)
            sys.exit('[ERROR] %s' % error_msg)
        else:
            return numpy.median(order_counts)

    def _get_random_patient_list(self):
        # Initialize DB cursor.
        cursor = self._connection.cursor()

        # Get average number of results for this lab test per patient.
        avg_orders_per_patient = self._get_average_orders_per_patient()
        log.info('avg_orders_per_patient: %s' % avg_orders_per_patient)
        # Based on average # of results, figure out how many patients we'd
        # need to get for a feature matrix of requested size.
        self._num_patients = int(numpy.max([self._num_requested_episodes / \
            avg_orders_per_patient, 1]))

        # Get numPatientsToQuery random patients who have gotten test.
        # TODO(sbala): Have option to feed in a seed for the randomness.
        query = SQLQuery()
        query.addSelect('pat_id')
        query.addFrom('stride_order_proc AS sop')
        query.addWhereIn('proc_code', self._lab_panel)
        query.addGroupBy('pat_id') # this should be a unique list of patients
        query.addOrderBy('RANDOM()')
        query.setLimit(self._num_patients)
        log.debug('Querying random patient list...')
        results = DBUtil.execute(query)

        # Get patient list.
        random_patient_list = [ row[0] for row in results ]

        return random_patient_list

    def _query_patient_episodes(self):
        log.info('Querying patient episodes...')
        # Initialize DB cursor.
        cursor = self._connection.cursor()

        # Build parameters for query.
        self._lab_components = self._get_components_in_lab_panel()
        random_patient_list = self._get_random_patient_list()

        #print("RANDOM PATIENT LIST", random_patient_list)

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
        query = SQLQuery()
        query.addSelect('CAST(pat_anon_id AS BIGINT) AS pat_id')
        query.addSelect('CAST(shifted_order_time AS TIMESTAMP)')
        query.addSelect('stride_culture_micro.proc_code')
        query.addSelect('organism_name') #one for the result

        # Experimenting
        susceptibility_flags = ['Trimethoprim/Sulfamethoxazole', 'Vancomycin', 'Penicillin', 'Levofloxacin',
                                'Clindamycin', 'Ceftriaxone', 'Erythromycin', 'Ampicillin',
                                'Meropenem', 'Ciprofloxacin', 'Cefepime', 'Aztreonam',
                                'Ampicillin/Sulbactam', 'Piperacillin/Tazobactam',
                                'Linezolid', 'Oxacillin.', 'Cefazolin', 'Daptomycin']

        for med in susceptibility_flags:

            query.addSelect(("MAX(CASE WHEN antibiotic_name = '%s' AND (suseptibility = 'Susceptible' OR suseptibility = 'Positive') THEN 1 ELSE 0 END) AS %s_Susc" % (med, med)).replace('/','_').replace('.', ''))
            query.addSelect(("MAX(CASE WHEN antibiotic_name = '%s' THEN 1 ELSE 0 END) as %s_tested" % (med, med)).replace('/', '_').replace('.', ''))


        # Let us look at top 10 commonly occuring bacteria
        query.addSelect("CASE WHEN organism_name IS NULL THEN 0 ELSE 1 END AS BACTERIA_PRESENT")
        query.addSelect("CASE WHEN organism_name = 'ESCHERICHIA COLI' THEN 1 ELSE 0 END AS ESCHERICHIA_COLI")
        query.addSelect("CASE WHEN organism_name = 'STAPHYLOCOCCUS AUREUS' THEN 1 ELSE 0 END AS STAPHYLOCOCCUS_AUREUS")
        query.addSelect("CASE WHEN organism_name = 'ENTEROCOCCUS SPECIES' THEN 1 ELSE 0 END AS ENTEROCOCCUS_SPECIES")
        query.addSelect("CASE WHEN organism_name = 'KLEBSIELLA PNEUMONIAE' THEN 1 ELSE 0 END AS KLEBSIELLA_PNEUMONIAE")
        query.addSelect("CASE WHEN organism_name = 'PSEUDOMONAS AERUGINOSA' THEN 1 ELSE 0 END AS PSEUDOMONAS_AERUGINOSA")
        query.addSelect("CASE WHEN organism_name = 'COAG NEGATIVE STAPHYLOCOCCUS' THEN 1 ELSE 0 END AS COAG_NEGATIVE_STAPHYLOCOCCUS")
        query.addSelect("CASE WHEN organism_name = 'ENTEROCOCCUS FAECALIS' THEN 1 ELSE 0 END AS ENTEROCOCCUS_FAECALIS")
        query.addSelect("CASE WHEN organism_name = 'PROTEUS MIRABILIS' THEN 1 ELSE 0 END AS PROTEUS_MIRABILIS")
        query.addSelect("CASE WHEN organism_name = 'CANDIDA ALBICANS' THEN 1 ELSE 0 END AS CANDIDA_ALBICANS")
        
        query.addFrom('stride_culture_micro')
 
        query.addWhereIn("stride_culture_micro.proc_code", self._lab_panel)
        query.addWhereIn("pat_anon_id", random_patient_list)
        query.addGroupBy('pat_anon_id')
        query.addGroupBy('shifted_order_time')
        query.addGroupBy('stride_culture_micro.proc_code')
        query.addGroupBy('organism_name')
        query.addOrderBy('pat_anon_id')
        query.addOrderBy('shifted_order_time')
        query.addOrderBy('stride_culture_micro.proc_code')
        query.addOrderBy('organism_name')
        query.setLimit(self._num_requested_episodes)

        self._num_reported_episodes = FeatureMatrix._query_patient_episodes(self, query, pat_id_col='pat_id', index_time_col='shifted_order_time')

    def _add_features(self):
        # Add past susceptibility readings
        self._add_susc_features()

        # Add past antibiotic use as features
        self._add_med_features()

        # Add lab panel order features.
        self._factory.addClinicalItemFeatures(self._lab_panel, features="pre")

        # Add lab component result features, for a variety of time deltas.
        LAB_PRE_TIME_DELTAS = [datetime.timedelta(-14)]
        LAB_POST_TIME_DELTA = datetime.timedelta(0)
        log.info('Adding lab component features...')
        for pre_time_delta in LAB_PRE_TIME_DELTAS:
            log.info('\t%s' % pre_time_delta)
            self._factory.addLabResultFeatures(self._lab_components, False, pre_time_delta, LAB_POST_TIME_DELTA)

        FeatureMatrix._add_features(self, index_time_col='shifted_order_time')

    def _add_susc_features(self):
        for susc_name in self._susceptibility_names:
            log.debug('Adding %s feature...' % susc_name)
            self._factory.addClinicalItemFeatures([susc_name], column='name',
                                                  label=susc_name, features="pre")

    def _add_med_features(self):
        # Adds all prior antibiotic use as features
        for med_set in self._med_panel:
            med_label = med_set[0].split()[0] # Takes name of antibiotic
            log.debug('Adding %s medication features...' % med_label)
            self._factory.addClinicalItemFeatures(med_set, column="description",
                                                  label="Med." + med_label, features="pre")


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
        line = 'the %s lab panel across %s inpatients from Stanford hospital.' % (','.join(self._lab_panel), self._num_patients)
        overview.append(line)
        # Each row contains columns summarizing the patient's demographics,
        line = "Each row contains columns summarizing the patient's demographics,"
        overview.append(line)
        # inpatient admit date, prior vitals, prior lab panel orders, and
        line = 'inpatient admit date, prior vitals, prior lab panel orders, and'
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
        line = '%s.[clinical_item] - orders of the lab panel of interest.' % ','.join(self._lab_panel)
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
        line = 'Also included %s panel components: %s' % (','.join(self._lab_panel), self._lab_components)
        summary.append(line)

        return summary

if __name__ == "__main__":
    log.level = logging.DEBUG
    start_time = time.time()
    # Initialize lab test matrix.
    ltm = LabCultureMatrix("LABBLC", 5)
    # Output lab test matrix.
    elapsed_time = numpy.ceil(time.time() - start_time)
    ltm.write_matrix("LABBLC-panel-5-episodes-%s-sec.tab" % str(elapsed_time))
