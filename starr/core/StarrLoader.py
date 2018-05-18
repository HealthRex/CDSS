#!/usr/bin/python
"""
Simple wrapper around BoxClient for downloading STARR data from Box.

Class for extracting, transforming, and loading raw STARR files as delivered by
Stanford into a proper format that can be analyzed (psql, R, etc).

All knowledge about the oddities of the STARR dataset should be confined
to this file. It will try to solve a number of problems, including:
* Inconsistencies in column names (e.g. pat_id vs. pat_anon_id)
* Inconsistencies in using quotes (e.g. pat_id vs. "pat_id" for headers)
* Inconsistencies in capitalization
* Quotes which prevent logical data types (e.g. "1980" vs. 1980 for timestamps)
"""

import inspect
import logging
import os
import gzip
import shutil
import pandas as pd
import numpy as np

from LocalEnv import BOX_STARR_FOLDER_ID, PATH_TO_CDSS, LOCAL_PROD_DB_PARAM
from starr.box.BoxClient import BoxClient
from medinfo.db import DBUtil
from medinfo.common.Util import log
from starr.rxnorm.RxNormClient import RxNormClient

class StarrLoader:
    STARR_FILE_PARAMS = {
        'Chen_Demographics.csv.gz': {
            'clean_file': 'starr_demographics_2008_2014.csv.gz',
            'psql_table': 'starr_patient'
        },
        'Chen_Demographics_Yr6_8.csv.gz': {
            'clean_file': 'starr_demographics_2014_2017.csv.gz',
            'psql_table': 'starr_patient'
        },
        'Chen_Active_Meds_At_Admit.csv.gz': {
            'clean_file': 'starr_preadmit_meds_2008_2014.csv.gz',
            'psql_table': 'starr_preadmit_med'
        },
        'Chen_Admit_Vitals.csv.gz': {
            'clean_file': 'starr_admit_vitals_2008_2014.csv.gz',
            'psql_table': 'starr_admit_vital'
        },
        'Chen_Clinical_Notes_Yr1.csv.gz': {
            'clean_file': 'starr_clinical_notes_year_1.csv.gz',
            'psql_table': 'starr_note'
        },
        'Chen_Clinical_Notes_Yr2.csv.gz': {
            'clean_file': 'starr_clinical_notes_year_2.csv.gz',
            'psql_table': 'starr_note'
        },
        'Chen_Clinical_Notes_Yr3.csv.gz': {
            'clean_file': 'starr_clinical_notes_year_3.csv.gz',
            'psql_table': 'starr_note'
        },
        'Chen_Clinical_Notes_Yr4.csv.gz': {
            'clean_file': 'starr_clinical_notes_year_4.csv.gz',
            'psql_table': 'starr_note'
        },
        'Chen_Clinical_Notes_Yr5.csv.gz': {
            'clean_file': 'starr_clinical_notes_year_5.csv.gz',
            'psql_table': 'starr_note'
        },
        'Chen_Clinical_Notes_Yr6.csv.gz': {
            'clean_file': 'starr_clinical_notes_year_6.csv.gz',
            'psql_table': 'starr_note'
        },
        'Chen_Clinical_Notes_Yr7.csv.gz': {
            'clean_file': 'starr_clinical_notes_year_7.csv.gz',
            'psql_table': 'starr_note'
        },
        'Chen_Clinical_Notes_Yr8.csv.gz': {
            'clean_file': 'starr_clinical_notes_year_8.csv.gz',
            'psql_table': 'starr_note'
        },
        'Chen_DX_List_5Yr.csv.gz': {
            'clean_file': 'starr_dx_2008_2014.csv.gz',
            'psql_table': 'starr_dx'
        },
        'Chen_Dx_List_Yrs6_8.csv.gz': {
            'clean_file': 'starr_dx_2014_2017.csv.gz',
            'psql_table': 'starr_dx'
        },
        'Chen_Insurance_Info_5Yr.csv.gz': {
            'clean_file': 'starr_insurance_2008_2014.csv.gz',
            'psql_table': 'starr_insurance'
        },
        'Chen_Insurance_Info_Yrs6_8.csv.gz': {
            'clean_file': 'starr_insurance_2014_2017.csv.gz',
            'psql_table': 'starr_insurance'
        },
        'Chen_Mapped_Meds_5Yr.csv.gz': {
            'clean_file': 'starr_medication_2008_2014.csv.gz',
            'psql_table': 'starr_medication'
        },
        'Chen_Mapped_Meds_Yrs6_8.csv.gz': {
            'clean_file': 'starr_medication_2014_2017.csv.gz',
            'psql_table': 'starr_medication'
        },
        'Chen_MedicationID_to_MPI.csv.gz': {
            'clean_file': 'starr_medication_mpi.csv.gz',
            'psql_table': 'starr_medication_mpi'
        },
        'Chen_Order_MedMixInfo_5Yr.csv.gz': {
            'clean_file': 'starr_medication_mix_2008_2014.csv.gz',
            'psql_table': 'starr_medication_mix'
        },
        'Chen_MedMixInfo_Yrs6_8.patchHeader.csv.gz': {
            'clean_file': 'starr_medication_mix_2014_2017.csv.gz',
            'psql_table': 'starr_medication_mix'
        },
        'Chen_Order_Proc_Yr1.patchcommas.csv.gz': {
            'clean_file': 'starr_order_proc_year_1.csv.gz',
            'psql_table': 'starr_order_proc'
        },
        'Chen_Order_Proc_Yr2.patchcommas.csv.gz': {
            'clean_file': 'starr_order_proc_year_2.csv.gz',
            'psql_table': 'starr_order_proc'
        },
        'Chen_Order_Proc_Yr3.patchcommas.csv.gz': {
            'clean_file': 'starr_order_proc_year_3.csv.gz',
            'psql_table': 'starr_order_proc'
        },
        'Chen_Order_Proc_Yr4.patchcommas.csv.gz': {
            'clean_file': 'starr_order_proc_year_4.csv.gz',
            'psql_table': 'starr_order_proc'
        },
        'Chen_Order_Proc_Yr5.patchcommas.csv.gz': {
            'clean_file': 'starr_order_proc_year_5.csv.gz',
            'psql_table': 'starr_order_proc'
        },
        'Chen_Order_Proc_Yr6.patchcommas.csv.gz': {
            'clean_file': 'starr_order_proc_year_6.csv.gz',
            'psql_table': 'starr_order_proc'
        },
        'Chen_Order_Proc_Yr7.patchcommas.csv.gz': {
            'clean_file': 'starr_order_proc_year_7.csv.gz',
            'psql_table': 'starr_order_proc'
        },
        'Chen_Order_Proc_Yr8.patchcommas.csv.gz': {
            'clean_file': 'starr_order_proc_year_8.csv.gz',
            'psql_table': 'starr_order_proc'
        },
        'Chen_Order_Result_Yr1.csv.gz': {
            'clean_file': 'starr_order_result_year_1.csv.gz',
            'psql_table': 'starr_order_result'
        },
        'Chen_Order_Result_Yr2.csv.gz': {
            'clean_file': 'starr_order_result_year_2.csv.gz',
            'psql_table': 'starr_order_result'
        },
        'Chen_Order_Result_Yr3.csv.gz': {
            'clean_file': 'starr_order_result_year_3.csv.gz',
            'psql_table': 'starr_order_result'
        },
        'Chen_Order_Result_Yr4.csv.gz': {
            'clean_file': 'starr_order_result_year_4.csv.gz',
            'psql_table': 'starr_order_result'
        },
        'Chen_Order_Result_Yr5.csv.gz': {
            'clean_file': 'starr_order_result_year_5.csv.gz',
            'psql_table': 'starr_order_result'
        },
        'Chen_Order_Res_Yr6.csv.gz': {
            'clean_file': 'starr_order_result_year_6.csv.gz',
            'psql_table': 'starr_order_result'
        },
        'Chen_Order_Res_Yr7.csv.gz': {
            'clean_file': 'starr_order_result_year_7.csv.gz',
            'psql_table': 'starr_order_result'
        },
        'Chen_Order_Res_Yr8.csv.gz': {
            'clean_file': 'starr_order_result_year_8.csv.gz',
            'psql_table': 'starr_order_result'
        },
        'Chen_TreatmentTeam_Yr1.csv.gz': {
            'clean_file': 'starr_treatment_team_year_1.csv.gz',
            'psql_table': 'starr_treatment_team'
        },
        'Chen_TreatmentTeam_Yr2.csv.gz': {
            'clean_file': 'starr_treatment_team_year_2.csv.gz',
            'psql_table': 'starr_treatment_team'
        },
        'Chen_TreatmentTeam_Yr3.csv.gz': {
            'clean_file': 'starr_treatment_team_year_3.csv.gz',
            'psql_table': 'starr_treatment_team'
        },
        'Chen_TreatmentTeam_Yr4.csv.gz': {
            'clean_file': 'starr_treatment_team_year_4.csv.gz',
            'psql_table': 'starr_treatment_team'
        },
        'Chen_TreatmentTeam_Yr5.csv.gz': {
            'clean_file': 'starr_treatment_team_year_5.csv.gz',
            'psql_table': 'starr_treatment_team'
        },
        'Chen_TreatmentTeam_Yr6.patchHeader.csv.gz': {
            'clean_file': 'starr_treatment_team_year_6.csv.gz',
            'psql_table': 'starr_treatment_team'
        },
        'Chen_TreatmentTeam_Yr7.patchHeader.csv.gz': {
            'clean_file': 'starr_treatment_team_year_7.csv.gz',
            'psql_table': 'starr_treatment_team'
        },
        'Chen_TreatmentTeam_Yr8.patchHeader.csv.gz': {
            'clean_file': 'starr_treatment_team_year_8.csv.gz',
            'psql_table': 'starr_treatment_team'
        },
        'Chen_income_vs_zip.csv.gz': {
            'clean_file': 'starr_income_2008_2014.csv.gz',
            'psql_table': 'starr_income'
        },
        'Chen_income_vs_zip_Yrs6_8.csv.gz': {
            'clean_file': 'starr_income_2014_2017.csv.gz',
            'psql_table': 'starr_income'
        },
        'JChenv3_BP_Table1.namepatch.csv.gz': {
            'clean_file': 'starr_flow_bp_2008_2014.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_HRate_Table2.csv.gz': {
            'clean_file': 'starr_flow_hr_2008_2014.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_Resp_Table3.csv.gz': {
            'clean_file': 'starr_flow_resp_2008_2014.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_fio2_Table4.csv.gz': {
            'clean_file': 'starr_flow_fio2_2008_2014.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_pulse_Table5.csv.gz': {
            'clean_file': 'starr_flow_pulse_2008_2014.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_temp_Table6.csv.gz': {
            'clean_file': 'starr_flow_temp_2008_2014.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_urine_Table7.csv.gz': {
            'clean_file': 'starr_flow_urine_2008_2014.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_GCS_Table8.csv.gz': {
            'clean_file': 'starr_flow_gcs_2008_2014.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_BP_Table11.csv.gz': {
            'clean_file': 'starr_flow_bp_2014_2017_11.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_BP_Table12.csv.gz': {
            'clean_file': 'starr_flow_bp_2014_2017_12.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_BP_Table13.csv.gz': {
            'clean_file': 'starr_flow_bp_2014_2017_13.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_BP_Table14.csv.gz': {
            'clean_file': 'starr_flow_bp_2014_2017_14.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_BP_Table15.csv.gz': {
            'clean_file': 'starr_flow_bp_2014_2017_15.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_Heartrate_Table16.csv.gz': {
            'clean_file': 'starr_flow_hr_2014_2017_16.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_Heartrate_Table17.csv.gz': {
            'clean_file': 'starr_flow_hr_2014_2017_17.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_Heartrate_Table18.csv.gz': {
            'clean_file': 'starr_flow_hr_2014_2017_18.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_Heartrate_Table19.csv.gz': {
            'clean_file': 'starr_flow_hr_2014_2017_19.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_Heartrate_Table20.csv.gz': {
            'clean_file': 'starr_flow_hr_2014_2017_20.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_Heartrate_Table20.csv.gz': {
            'clean_file': 'starr_flow_hr_2014_2017_20.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_Resp_Table21.csv.gz': {
            'clean_file': 'starr_flow_resp_2014_2017_21.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_Resp_Table22.csv.gz': {
            'clean_file': 'starr_flow_resp_2014_2017_22.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_Resp_Table23.csv.gz': {
            'clean_file': 'starr_flow_resp_2014_2017_23.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_Resp_Table24.csv.gz': {
            'clean_file': 'starr_flow_resp_2014_2017_24.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_Resp_Table25.csv.gz': {
            'clean_file': 'starr_flow_resp_2014_2017_25.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_temp_Table26.csv.gz': {
            'clean_file': 'starr_flow_temp_2014_2017_26.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_temp_Table27.csv.gz': {
            'clean_file': 'starr_flow_temp_2014_2017_27.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_temp_Table28.csv.gz': {
            'clean_file': 'starr_flow_temp_2014_2017_28.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_temp_Table29.csv.gz': {
            'clean_file': 'starr_flow_temp_2014_2017_29.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_temp_Table30.csv.gz': {
            'clean_file': 'starr_flow_temp_2014_2017_30.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_fio2_Table31.csv.gz': {
            'clean_file': 'starr_flow_fio2_2014_2017_31.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_fio2_Table32.csv.gz': {
            'clean_file': 'starr_flow_fio2_2014_2017_32.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_fio2_Table33.csv.gz': {
            'clean_file': 'starr_flow_fio2_2014_2017_33.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_fio2_Table34.csv.gz': {
            'clean_file': 'starr_flow_fio2_2014_2017_34.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_fio2_Table35.csv.gz': {
            'clean_file': 'starr_flow_fio2_2014_2017_35.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_pulse_Table36.csv.gz': {
            'clean_file': 'starr_flow_pulse_2014_2017_36.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_pulse_Table37.csv.gz': {
            'clean_file': 'starr_flow_pulse_2014_2017_37.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_pulse_Table38.csv.gz': {
            'clean_file': 'starr_flow_pulse_2014_2017_38.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_pulse_Table39.csv.gz': {
            'clean_file': 'starr_flow_pulse_2014_2017_39.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_pulse_Table40.csv.gz': {
            'clean_file': 'starr_flow_pulse_2014_2017_40.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_urine_Table41.csv.gz': {
            'clean_file': 'starr_flow_urine_2014_2017_41.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_urine_Table42.csv.gz': {
            'clean_file': 'starr_flow_urine_2014_2017_42.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_urine_Table43.csv.gz': {
            'clean_file': 'starr_flow_urine_2014_2017_43.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_urine_Table44.csv.gz': {
            'clean_file': 'starr_flow_urine_2014_2017_44.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_urine_Table45.csv.gz': {
            'clean_file': 'starr_flow_urine_2014_2017_45.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_GCS_Table46.csv.gz': {
            'clean_file': 'starr_flow_gcs_2014_2017_46.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_GCS_Table47.csv.gz': {
            'clean_file': 'starr_flow_gcs_2014_2017_47.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_GCS_Table48.csv.gz': {
            'clean_file': 'starr_flow_gcs_2014_2017_48.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_GCS_Table49.csv.gz': {
            'clean_file': 'starr_flow_gcs_2014_2017_49.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_GCS_Table50.csv.gz': {
            'clean_file': 'starr_flow_gcs_2014_2017_50.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_sp02_Table51.csv.gz': {
            'clean_file': 'starr_flow_spo2_2014_2017_51.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_sp02_Table52.csv.gz': {
            'clean_file': 'starr_flow_spo2_2014_2017_52.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_sp02_Table53.csv.gz': {
            'clean_file': 'starr_flow_spo2_2014_2017_53.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_sp02_Table54.csv.gz': {
            'clean_file': 'starr_flow_spo2_2014_2017_54.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_sp02_Table55.csv.gz': {
            'clean_file': 'starr_flow_spo2_2014_2017_55.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChen_Flwst_Height_Yr8.csv.gz': {
            'clean_file': 'starr_flow_height_2008_2017.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChen_Flwst_Weight_Yr8.csv.gz': {
            'clean_file': 'starr_flow_weight_2008_2017.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'Jchen_Inpu_output_data1.csv.gz': {
            'clean_file': 'starr_io_flowsheet_1.csv.gz',
            'psql_table': 'starr_io_flowsheet'
        },
        'Jchen_Inpu_output_data2.csv.gz': {
            'clean_file': 'starr_io_flowsheet_2.csv.gz',
            'psql_table': 'starr_io_flowsheet'
        },
        'Jchen_Inpu_output_data3.csv.gz': {
            'clean_file': 'starr_io_flowsheet_3.csv.gz',
            'psql_table': 'starr_io_flowsheet'
        },
        'Jchen_Inpu_output_data4.csv.gz': {
            'clean_file': 'starr_io_flowsheet_4.csv.gz',
            'psql_table': 'starr_io_flowsheet'
        },
        'Jchen_Inpu_output_data5.csv.gz': {
            'clean_file': 'starr_io_flowsheet_5.csv.gz',
            'psql_table': 'starr_io_flowsheet'
        },
        'Jchen_Inpu_output_update_11.csv.gz': {
            'clean_file': 'starr_io_flowsheet_11.csv.gz',
            'psql_table': 'starr_io_flowsheet'
        },
        'Jchen_Inpu_output_update_12.csv.gz': {
            'clean_file': 'starr_io_flowsheet_12.csv.gz',
            'psql_table': 'starr_io_flowsheet'
        },
        'Jchen_Inpu_output_update_13.csv.gz': {
            'clean_file': 'starr_io_flowsheet_13.csv.gz',
            'psql_table': 'starr_io_flowsheet'
        },
        'Jchen_Inpu_output_update_14.csv.gz': {
            'clean_file': 'starr_io_flowsheet_14.csv.gz',
            'psql_table': 'starr_io_flowsheet'
        },
        'Jchen_Inpu_output_update_15.csv.gz': {
            'clean_file': 'starr_io_flowsheet_15.csv.gz',
            'psql_table': 'starr_io_flowsheet'
        },
        'Jchen_Inpu_output_update_16.csv.gz': {
            'clean_file': 'starr_io_flowsheet_16.csv.gz',
            'psql_table': 'starr_io_flowsheet'
        },
        'Jchen_Inpu_output_update_17.csv.gz': {
            'clean_file': 'starr_io_flowsheet_17.csv.gz',
            'psql_table': 'starr_io_flowsheet'
        },
        'Jchen_Inpu_output_update_18.csv.gz': {
            'clean_file': 'starr_io_flowsheet_18.csv.gz',
            'psql_table': 'starr_io_flowsheet'
        },
        'Jchen_Inpu_output_update_19.csv.gz': {
            'clean_file': 'starr_io_flowsheet_19.csv.gz',
            'psql_table': 'starr_io_flowsheet'
        },
        'Jchen_Inpu_output_update_20.csv.gz': {
            'clean_file': 'starr_io_flowsheet_20.csv.gz',
            'psql_table': 'starr_io_flowsheet'
        }
    }

    @staticmethod
    def fetch_starr_dir():
        # CDSS/starr/
        return PATH_TO_CDSS + 'starr/'

    @staticmethod
    def fetch_core_dir():
        # CDSS/core/
        return PATH_TO_CDSS + 'core/'

    @staticmethod
    def fetch_data_dir():
        # CDSS/starr/data/
        starr_dir = StarrLoader.fetch_starr_dir()
        return starr_dir + 'data/'

    @staticmethod
    def fetch_clean_data_dir():
        data_dir = StarrLoader.fetch_data_dir()
        return data_dir + 'clean/'

    @staticmethod
    def fetch_raw_data_dir():
        data_dir = StarrLoader.fetch_data_dir()
        return data_dir + 'raw/'

    @staticmethod
    def fetch_psql_dir():
        # CDSS/starr/data/
        starr_dir = StarrLoader.fetch_starr_dir()
        return starr_dir + 'psql/'

    @staticmethod
    def fetch_psql_schemata_dir():
        # CDSS/starr/schemata/
        psql_dir = StarrLoader.fetch_psql_dir()
        return psql_dir + 'schemata/'

    @staticmethod
    def download_starr_data():
        data_dir = StarrLoader.fetch_data_dir()

        # Remote folder ID defined in LocalEnv.
        box = BoxClient()
        box.download_folder(BOX_STARR_FOLDER_ID, data_dir)

    @staticmethod
    def build_clean_data_file(source_path, dest_path):
        # Force pandas to read certain fields as a given data type.
        # This both makes read_csv faster and reduces parsing errors.
        # Fields that look like integers should be read as objects so that
        # missing data doesn't force pandas to read as a float.
        # http://pandas.pydata.org/pandas-docs/stable/gotchas.html#support-for-integer-na
        data_types = {
            # 0_integer and 1_integer only encountered in test cases.
            '0_integer': object,
            '1_INTEGER': object,
            'abnormal_yn': object,
            'act_order_c': object,
            'active_order': object,
            'admin_dose_unit': object,
            'admin_dose_unit_c': object,
            'admin_min_dose': object,
            'admin_max_dose': object,
            'amb_med_disp_name': object,
            'AUTHOR_NAME': object,
            'authrzing_prov_id': object,
            'base_name': object,
            'BED': object,
            'BED_STATUS': object,
            'BIRTH_YEAR': object,
            'BP_DIASTOLIC': object,
            'BP_SYSTOLIC': object,
            'calc_dose_unit': object,
            'calc_dose_unit_c': object,
            'CALC_DOSE_UNIT_C': object,
            'calc_min_dose': object,
            'calc_max_dose': object,
            'calc_volume_yn': object,
            'chng_order_med_id': object,
            'chng_order_proc_id': object,
            'common_name': object,
            'component_name': object,
            'CONTACT_DATE': object,
            'COSIGNER_NAME': object,
            'cpt_code': object,
            'data_source': object,
            'DEATH_DATE': object,
            'DEPARTMENT': object,
            'DEPARTMENT_IN': object,
            'department_name': object,
            'description': object,
            'DESCRIPTION': object,
            'discon_time': object,
            'discrete_frequency': object,
            'discrete_interval': object,
            'dispense_unit': object,
            'display_name': object,
            'dose_calc_info': object,
            'DOSE_CALC_INFO': object,
            'dose_unit': object,
            'dose_unit_c': object,
            'DOSE_UNIT_C': object,
            'doses_remaining': object,
            'duration_unit_name': object,
            'dx_icd9_code': object,
            'dx_icd9_code_list': object,
            'end_taking_time': object,
            'ETHNICITY': object,
            'EVENT_IN': object,
            'EVENT_OUT': object,
            'FLO_MEAS_ID': object,
            'freq_name': object,
            'future_or_stand': object,
            'G1_DISP_NAME': object,
            'G2_DISP_NAME': object,
            'GENDER': object,
            'GENERIC_NAME': object,
            'HOSPITAL_SERVICE': object,
            'hv_discr_freq_id': object,
            'hv_discrete_dose': object,
            'hv_dose_unit': object,
            'hv_dose_unit_c': object,
            'INCOME_RANGE': object,
            'ingredient_type': object,
            'ingredient_type_c': object,
            'instantiated_time': object,
            'lab_status': object,
            'lastdose': object,
            'last_stand_perf_dt': object,
            'last_stand_perf_tm': object,
            'line': object,
            'LINE': object,
            'medication_id': object,
            'MEDICATION_ID': object,
            'medication_name': object,
            'MED_NAME': object,
            'MAX_CALC_DOSE_AMT': object,
            'max_calc_dose_amt': object,
            'max_discrete_dose': object,
            'max_dose_amount': object,
            'max_duration': object,
            'max_rate': object,
            'max_volume': object,
            'MEAS_VALUE': object,
            'med_dis_disp_qty': object,
            'med_dis_disp_unit_c': object,
            'med_duration_unit_c': object,
            'med_presc_prov_id': object,
            'med_route': object,
            'med_route_c': object,
            'medication_id': object,
            'MIN_CALC_DOSE_AMT': object,
            'min_calc_dose_amt': object,
            'min_discrete_dose': object,
            'min_dose_amount': object,
            'min_duration': object,
            'min_rate': object,
            'min_volume': object,
            'modify_track': object,
            'modify_track_c': object,
            'MPI_ID_VAL': object,
            'NAME': object,
            'nonformulary_yn': object,
            'NOTE_DATE': object,
            'noted_date': object,
            'NOTE_TYPE': object,
            'number_of_doses': object,
            'ord_date_real': object,
            'ord_num_value': object,
            'ord_prov_id': object,
            'order_class': object,
            'order_class_c': object,
            'order_class_name': object,
            'order_end_time': object,
            'order_inst': object,
            'order_med_id': object,
            'order_priority': object,
            'order_priority_c': object,
            'order_proc_id': object,
            'order_status': object,
            'order_status_c': object,
            'order_time': object,
            'order_type': object,
            'ordering_date': object,
            'ordering_id': object,
            'ordering_mode': object,
            'ordering_mode_c': object,
            'parent_ce_order_id': object,
            'PAT_ANON_ID': object,
            'pat_id': object,
            'PAT_ID': object,
            'pat_enc_csn_id': object,
            'PAT_ENC_CSN_ANON_ID': object,
            'PAT_ENC_CSN_ID': object,
            'pat_loc_id': object,
            'PATIENT_CLASS': object,
            'PAYOR_NAME': object,
            'PHARM_CLASS': object,
            'PHARM_SUBCLASS': object,
            'problem_list_id': object,
            'proc_bgn_time': object,
            'proc_cat_name': object,
            'proc_code': object,
            'proc_end_time': object,
            'proc_ending_time': object,
            'proc_id': object,
            'proc_start_time': object,
            'PROV_NAME': object,
            'PROVIDER_TYPE': object,
            'PULSE': object,
            'quantity': object,
            'RACE': object,
            'radiology_status': object,
            'rate_unit': object,
            'rate_unit_c': object,
            'reference_unit': object,
            'refills': object,
            'refills_remaining': object,
            'resolved_date': object,
            'RESPIRATIONS': object,
            'result_date': object,
            'result_in_range_yn': object,
            'result_status': object,
            'result_time': object,
            'resume_status': object,
            'resume_status_c': object,
            'RN': object,
            'rsn_for_discon': object,
            'rsn_for_discon_c': object,
            'RXCUI': object,
            'selection': object,
            'SELECTION': object,
            'SEQ_NUM_IN_BED_MIN': object,
            'SEQ_NUM_IN_ENC': object,
            'SHIFTED_TRANSF_IN_DT_TM': object,
            'SHIFTED_TRANSF_OUT_DT_TM': object,
            'SPECIALTY': object,
            'standing_exp_date': object,
            'standing_occurs': object,
            'stand_interval': object,
            'stand_orig_occur': object,
            'start_taking_time': object,
            'STATUS': object,
            'TEMPERATURE': float,
            'THERA_CLASS': object,
            'TITLE': object,
            'TREATMENT_TEAM': object,
            'TRTMNT_TM_BEGIN_DATE': object,
            'TRTMNT_TM_END_DATE': object,
            'value_normalized': object,
            'volume_unit': object,
            'volume_unit_c': object
        }

        raw_data = pd.read_csv(source_path, compression='gzip', \
                                dtype=object, skipinitialspace=True,
                                error_bad_lines=False, warn_bad_lines=True)

        # Make header column all lowercase.
        raw_data.columns = [column.lower() for column in raw_data.columns]

        # Make custom patches to the data values. Any parsing errors should
        # be fixed offline, but any data oddities should be fixed here.
        raw_file_name = os.path.split(source_path)[-1]
        # If generating a starr_mapped_meds file, append active_ingredient.
        if 'Chen_Mapped_Meds' in raw_file_name:
            rxnorm = RxNormClient()
            name_function = rxnorm.fetch_name_by_rxcui
            raw_data['active_ingredient'] = raw_data['rxcui'].map(name_function)
        # elif 'Chen_Order_Proc_Yr7' in raw_file_name:
        #     # Chen_Order_Proc_Yr7['quantity'] has >3500 rows with the value 'S'
        #     # for quantity. These are standing orders, for which 'quantity'
        #     # does not make clinical sense. Because 'quantity' must be an
        #     # integer, however, force this value to None.
        #     raw_data['quantity'].replace(to_replace='S', value=np.nan, \
        #                                     inplace=True)
        #     # Chen_Order_Proc_Yr7['standing_exp_date'] has a number of token
        #     # values which seem to represent a non-existent expiration date.
        #     # Includes: 99999, 99993, and 1
        #     raw_data['standing_exp_date'].replace(to_replace='99999', \
        #                                             value=np.nan, inplace=True)
        #     raw_data['standing_exp_date'].replace(to_replace='99993', \
        #                                             value=np.nan, inplace=True)
        #     raw_data['standing_exp_date'].replace(to_replace='1', \
        #                                             value=np.nan, inplace=True)
        #     raw_data['standing_exp_date'].replace(to_replace='0', \
        #                                             value=np.nan, inplace=True)
        #     raw_data['standing_exp_date'].replace(to_replace=99999.0, \
        #                                             value=np.nan, inplace=True)
        #     # Chen_Order_Proc_Yr7['order_inst'] is 'PRN' (meaning the order
        #     # is on a "pro re nata" or "as needed" basis). This field is
        #     # a datetime, so represent as nan.
        #     raw_data['order_inst'].replace(to_replace='PRN', value=np.nan, \
        #                                     inplace=True)
        #     # Chen_Order_Proc_Yr7['parent_ce_order_id'] is 'Inpatient' for
        #     # >3500 rows, so replace with NaN.
        #     raw_data['parent_ce_order_id'].replace(to_replace='Inpatient', \
        #                                             value=np.nan, inplace=True)

        # Write to csv.
        raw_data.to_csv(path_or_buf=dest_path, compression='gzip', index=False)

    @staticmethod
    def build_starr_psql_schemata():
        schemata_dir = StarrLoader.fetch_psql_schemata_dir()
        for params in StarrLoader.STARR_FILE_PARAMS.values():
            psql_table = params['psql_table']

            # Open file, feed to DBUtil, and close file.
            schema_file_name = '.'.join([psql_table, 'sql'])
            schema_file_path = schemata_dir + schema_file_name
            schema_file = open(schema_file_path, 'r')
            DBUtil.runDBScript(schema_file)
            schema_file.close()

    @staticmethod
    def clear_starr_psql_tables():
        log.info('Clearing starr psql tables...')
        for params in StarrLoader.STARR_FILE_PARAMS.values():
            psql_table = params['psql_table']
            log.debug('dropping table %s...' % psql_table)
            # load_starr_to_psql is not itempotent, so in case schema already
            # existed, clear table (avoid duplicate data).
            # existence_query = "SELECT EXISTS(SELECT 1 FROM pg_tables WHERE tablename = '%s')"
            # table_exists = DBUtil.execute(existence_query % psql_table)[0][0]
            # if table_exists:
            #     DBUtil.execute("DELETE FROM %s;" % psql_table)
            DBUtil.execute("DROP TABLE IF EXISTS %s CASCADE;" % psql_table)

    @staticmethod
    def load_starr_to_psql():
        # Clear any old data.
        StarrLoader.clear_starr_psql_tables()
        # Build schemata.
        StarrLoader.build_starr_psql_schemata()

        # Build paths to clean data files.
        raw_data_dir = StarrLoader.fetch_raw_data_dir()
        clean_data_dir = StarrLoader.fetch_clean_data_dir()
        for raw_file in sorted(StarrLoader.STARR_FILE_PARAMS.keys()):
            params = StarrLoader.STARR_FILE_PARAMS[raw_file]

            # Build clean data file.
            clean_file = params['clean_file']
            log.info('loading %s...' % clean_file)
            raw_path = '/'.join([raw_data_dir, raw_file])
            clean_path = '/'.join([clean_data_dir, clean_file])
            log.debug('starr/data/[raw/%s] ==> [clean/%s]' % (raw_file, clean_file))
            # Building the clean file is the slowest part of setup, so only
            # do it if absolutely necessary. This means that users must be
            # aware of issues like a stale cache.
            if not os.path.exists(clean_path):
                StarrLoader.build_clean_data_file(raw_path, clean_path)

            # Uncompress data file.
            unzipped_clean_path = clean_path[:-3]
            with gzip.open(clean_path, 'rb') as f_in, open(unzipped_clean_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

            # psql COPY data from clean files into DB.
            psql_table = params['psql_table']
            log.debug('starr/data/clean/%s ==> %s' % (clean_file, psql_table))
            # In some cases, two files going to the same table will have
            # non-identical column names. Pass these explicitly so that
            # psql knows which columns to try to fill from file.
            # Strip the newline character.
            with open(unzipped_clean_path, 'r') as f_in:
                columns = f_in.readline()[:-1]
            command = "COPY %s (%s) FROM '%s' WITH (FORMAT csv, HEADER);" % (psql_table, columns, unzipped_clean_path)
            DBUtil.execute(command)

            # Delete unzipped_clean_path.
            os.remove(unzipped_clean_path)

if __name__=='__main__':
    # StarrLoader.download_starr_data()
    log.level = logging.INFO
    StarrLoader.load_starr_to_psql()
