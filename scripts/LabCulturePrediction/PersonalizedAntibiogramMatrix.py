#!/usr/bin/python
"""
Class for generating PersonalizedAntibiogramMatrix.
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

import pdb
class PersonalizedAntibiogramMatrix(FeatureMatrix):
    def __init__(self, lab_panel, lab_features, num_episodes, random_state=None):
        FeatureMatrix.__init__(self, lab_panel, num_episodes)

        # Parse arguments.
        self._lab_panel = lab_panel
        self._lab_features = lab_features

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


    def _query_patient_episodes(self):
        log.info('Querying patient episodes...')
        # Initialize DB cursor.
        cursor = self._connection.cursor()

        # Build parameters for query.
        
        query = """SELECT
                    pat_anon_id as pat_id,
                    pat_enc_csn_anon_id,
                    shifted_order_time,
                    order_proc_anon_id,
                    organism_name,
                    proc_code,
                    
                    MAX(CASE WHEN antibiotic_name = 'Ampicillin' and suseptibility in ('Positive', 'Susceptible') then 1 else 0 end) as ampicillin_susc,
                    MAX(CASE WHEN antibiotic_name = 'Ampicillin/Sulbactam' and suseptibility in ('Positive', 'Susceptible') then 1 else 0 end) as ampicillin_sulbactam_susc,
                    MAX(CASE WHEN antibiotic_name = 'Piperacillin/Tazobactam' and suseptibility in ('Positive', 'Susceptible') then 1 else 0 end) as piperacillin_tazobactam_susc,

                    MAX(CASE WHEN antibiotic_name in ('Cefazolin', 'Cefazolin..') and suseptibility in ('Positive', 'Susceptible') then 1 else 0 end) as cefazolin_susc,
                    MAX(CASE WHEN antibiotic_name in ('Ceftriaxone', 'Ceftriaxone.') and suseptibility in ('Positive', 'Susceptible') then 1 else 0 end) as ceftriaxone_susc,
                    MAX(CASE WHEN antibiotic_name = 'Cefepime' and suseptibility in ('Positive', 'Susceptible') then 1 else 0 end) as cefepime_susc,

                    MAX(CASE WHEN antibiotic_name in ('Aztreonam', 'Aztreonam.') and suseptibility in ('Positive', 'Susceptible') then 1 else 0 end) as aztreonam_susc,
                    MAX(CASE WHEN antibiotic_name = 'Imipenem' and suseptibility in ('Positive', 'Susceptible') then 1 else 0 end) as imipenem_susc,
                    MAX(CASE WHEN antibiotic_name = 'Meropenem' and suseptibility in ('Positive', 'Susceptible') then 1 else 0 end) as meropenem_susc,

                    MAX(CASE WHEN antibiotic_name = 'Gentamicin' and suseptibility in ('Positive', 'Susceptible') then 1 else 0 end) as gentamicin_susc,
                    MAX(CASE WHEN antibiotic_name = 'Tobramycin' and suseptibility in ('Positive', 'Susceptible') then 1 else 0 end) as tobramycin_susc,
                    MAX(CASE WHEN antibiotic_name = 'Amikacin' and suseptibility in ('Positive', 'Susceptible') then 1 else 0 end) as amikacin_susc,

                    MAX(CASE WHEN antibiotic_name = 'Ciprofloxacin' and suseptibility in ('Positive', 'Susceptible') then 1 else 0 end) as ciprofloxacin_susc,
                    MAX(CASE WHEN antibiotic_name = 'Levofloxacin' and suseptibility in ('Positive', 'Susceptible') then 1 else 0 end) as levofloxacin_susc,
                    MAX(CASE WHEN antibiotic_name = 'Trimethoprim/Sulfamethoxazole.' and suseptibility in ('Positive', 'Susceptible') then 1 else 0 end) as trimethoprim_sulfamethoxazole_susc,

                    MAX(CASE WHEN antibiotic_name = 'Nitrofurantoin' and suseptibility in ('Positive', 'Susceptible') then 1 else 0 end) as nitrofurantoin_susc,

                    MAX(CASE WHEN antibiotic_name = 'Ampicillin' then 1 else 0 end) as ampicillin_tested,
                    MAX(CASE WHEN antibiotic_name = 'Ampicillin/Sulbactam' then 1 else 0 end) as ampicillin_sulbactam_tested,
                    MAX(CASE WHEN antibiotic_name = 'Piperacillin/Tazobactam' then 1 else 0 end) as piperacillin_tazobactam_tested,

                    MAX(CASE WHEN antibiotic_name in ('Cefazolin', 'Cefazolin..') then 1 else 0 end) as cefazolin_tested,
                    MAX(CASE WHEN antibiotic_name in ('Ceftriaxone', 'Ceftriaxone.') then 1 else 0 end) as ceftriaxone_tested,
                    MAX(CASE WHEN antibiotic_name = 'Cefepime' then 1 else 0 end) as cefepime_tested,

                    MAX(CASE WHEN antibiotic_name in ('Aztreonam', 'Aztreonam.') then 1 else 0 end) as aztreonam_tested,
                    MAX(CASE WHEN antibiotic_name = 'Imipenem' then 1 else 0 end) as imipenem_tested,
                    MAX(CASE WHEN antibiotic_name = 'Meropenem' then 1 else 0 end) as meropenem_tested,

                    MAX(CASE WHEN antibiotic_name = 'Gentamicin' then 1 else 0 end) as gentamicin_tested,
                    MAX(CASE WHEN antibiotic_name = 'Tobramycin' then 1 else 0 end) as tobramycin_tested,
                    MAX(CASE WHEN antibiotic_name = 'Amikacin' then 1 else 0 end) as amikacin_tested,

                    MAX(CASE WHEN antibiotic_name = 'Ciprofloxacin' then 1 else 0 end) as ciprofloxacin_tested,
                    MAX(CASE WHEN antibiotic_name = 'Levofloxacin' then 1 else 0 end) as levofloxacin_tested,
                    MAX(CASE WHEN antibiotic_name = 'Trimethoprim/Sulfamethoxazole.' then 1 else 0 end) as trimethoprim_sulfamethoxazole_tested,

                    MAX(CASE WHEN antibiotic_name = 'Nitrofurantoin' then 1 else 0 end) as nitrofurantoin_tested
                FROM 
                    stride_culture_micro
                WHERE
                    antibiotic_name in ('Ampicillin', 'Ampicillin/Sulbactam', 'Piperacillin/Tazobactam', 'Cefazolin', 'Cefazolin..',
                                       'Ceftriaxone', 'Ceftriaxone.', 'Cefepime', 'Aztreonam', 'Aztreonam.', 'Imipenem', 'Meropenem',
                                       'Gentamicin', 'Tobramycin', 'Amikacin', 'Ciprofloxacin', 'Levofloxacin', 'Trimethoprim/Sulfamethoxazole.',
                                       'Nitrofurantoin')
                    AND
                    organism_name in ('ESCHERICHIA COLI', 'KLEBSIELLA PNEUMONIAE', 'PSEUDOMONAS AERUGINOSA', 'PROTEUS MIRABILIS')
                GROUP BY pat_id, pat_enc_csn_anon_id, shifted_order_time, order_proc_anon_id, organism_name, proc_code
                ORDER BY pat_id, pat_enc_csn_anon_id, shifted_order_times
                """
        self._num_reported_episodes = FeatureMatrix._query_patient_episodes(self, query, pat_id_col='pat_id', index_time_col='shifted_order_time')

    def _add_features(self):
        # # Add past susceptibility readings
        self._add_susc_features()

        # # Add past antibiotic use as features
        self._add_med_features()

        # # Add lab panel order features.
        for panel in self._lab_features:
            self._factory.addClinicalItemFeatures([panel], features="pre")
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
        # line = 'Also included %s panel components: %s' % (','.join(self._lab_panel), self._lab_components)
        # summary.append(line

        return summary

if __name__ == "__main__":
    log.level = logging.DEBUG
    start_time = time.time()
    # Initialize lab test matrix.
    ltm = LabCultureMatrix("LABBLC", 5)
    # Output lab test matrix.
    elapsed_time = numpy.ceil(time.time() - start_time)
    ltm.write_matrix("LABBLC-panel-5-episodes-%s-sec.tab" % str(elapsed_time))
