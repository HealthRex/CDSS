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
            'psql_table': 'starr_patient_encounter'
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
            'psql_table': 'starr_patient_encounter'
        },
        'Chen_Insurance_Info_Yrs6_8.csv.gz': {
            'clean_file': 'starr_insurance_2014_2017.csv.gz',
            'psql_table': 'starr_patient_encounter'
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
        'Chen_Treatment_Team_Yrs6.patchHeader.csv.gz': {
            'clean_file': 'starr_treatment_team_year_6.csv.gz',
            'psql_table': 'starr_treatment_team'
        },
        'Chen_Treatment_Team_Yrs7.patchHeader.csv.gz': {
            'clean_file': 'starr_treatment_team_year_7.csv.gz',
            'psql_table': 'starr_treatment_team'
        },
        'Chen_Treatment_Team_Yrs8.patchHeader.csv.gz': {
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
        'JChenv3_BP_Table1.patchHeader.csv.gz': {
            'clean_file': 'starr_flow_bp_2008_2014.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_HRate_Table2.patchHeader.csv.gz': {
            'clean_file': 'starr_flow_hr_2008_2014.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_Resp_Table3.patchHeader.csv.gz': {
            'clean_file': 'starr_flow_resp_2008_2014.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_fio2_Table4.patchHeader.csv.gz': {
            'clean_file': 'starr_flow_fio2_2008_2014.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_pulse_Table5.patchHeader.csv.gz': {
            'clean_file': 'starr_flow_pulse_2008_2014.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_temp_Table6.patchHeader.csv.gz': {
            'clean_file': 'starr_flow_temp_2008_2014.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_urine_Table7.patchHeader.csv.gz': {
            'clean_file': 'starr_flow_urine_2008_2014.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_GCS_Table8.patchHeader.csv.gz': {
            'clean_file': 'starr_flow_gcs_2008_2014.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_BP_Table11.patchHeader.csv.gz': {
            'clean_file': 'starr_flow_bp_2014_2017_11.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_BP_Table12.patchHeader.csv.gz': {
            'clean_file': 'starr_flow_bp_2014_2017_12.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_BP_Table13.patchHeader.csv.gz': {
            'clean_file': 'starr_flow_bp_2014_2017_13.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_BP_Table14.patchHeader.csv.gz': {
            'clean_file': 'starr_flow_bp_2014_2017_14.csv.gz',
            'psql_table': 'starr_flowsheet'
        },
        'JChenv3_BP_Table15.patchHeader.csv.gz': {
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
        },
        'export_ICD-9-CM_2013.csv.gz': {
            'clean_file': 'icd9_cm_2013.csv.gz',
            'psql_table': 'icd9_cm'
        },
        'JChenv3_ADTTable10.csv.gz': {
            'clean_file': 'starr_adt_2008_2014.csv.gz',
            'psql_table': 'starr_adt'
        },
        'JChenv3_ADTTable56.csv.gz': {
            'clean_file': 'starr_adt_2014_2017.csv.gz',
            'psql_table': 'starr_adt'
        },
        'ChargeMaster.Stanford.2014.csv.gz': {
            'clean_file': 'stanford_chargemaster_2014.csv.gz',
            'psql_table': 'stanford_chargemaster'
        },
        'Chen_Order_Med_5Yr.patchQuotes.csv.gz': {
            'clean_file': 'starr_order_med_2008_2014.csv.gz',
            'psql_table': 'starr_order_med'
        },
        'Chen_Order_Med_Yrs6_8.patchHeader.csv.gz': {
            'clean_file': 'starr_order_med_2014_2017.csv.gz',
            'psql_table': 'starr_order_med'
        }
        'orderset_procedures.csv.gz': {
            'clean_file': 'starr_orderset_order_proc_2008_2014.csv.gz',
            'psql_table': 'starr_orderset_order_proc'
        },
        'Chen_OrderSets_Proc_Yrs6_8.csv.gz': {
            'clean_file': 'starr_orderset_order_proc_2014_2017.csv.gz',
            'psql_table': 'starr_orderset_order_proc'
        },
        'orderset_medications.csv.gz': {
            'clean_file': 'starr_orderset_order_med_2008_2014.csv.gz',
            'psql_table': 'starr_orderset_order_med'
        },
        'Chen_OrderSets_Med_Yrs6_8.csv.gz': {
            'clean_file': 'starr_orderset_order_med_2014_2017.csv.gz',
            'psql_table': 'starr_orderset_order_med'
        },
        'JChen_cult_micro_7yr.patchIds.csv.gz': {
            'clean_file': 'starr_culture_micro_7_year.csv.gz',
            'psql_table': 'starr_culture_micro'
        }
        'export_ICD-10-CM_2016.csv.gz': {
            'clean_file': 'icd10_cm_2016.csv.gz',
            'psql_table': 'icd10_cm'
        },
        'JChenv3_Admits_Table58.csv.gz': {
            'clean_file': 'starr_admit_2014_2017.csv.gz',
            'psql_table': 'starr_admit'
        },
        'JChenv3_DRG_Table57.csv.gz': {
            'clean_file': 'starr_drg_7_year.csv.gz',
            'psql_table': 'starr_drg'
        }
    }

    @staticmethod
    def fetch_starr_dir():
        # CDSS/starr/
        return os.path.join(PATH_TO_CDSS, 'starr')

    @staticmethod
    def fetch_core_dir():
        # CDSS/core/
        return os.path.join(PATH_TO_CDSS, 'core')

    @staticmethod
    def fetch_data_dir():
        # CDSS/starr/data/
        starr_dir = StarrLoader.fetch_starr_dir()
        return os.path.join(starr_dir, 'data')

    @staticmethod
    def fetch_clean_data_dir():
        data_dir = StarrLoader.fetch_data_dir()
        return os.path.join(data_dir, 'clean')

    @staticmethod
    def fetch_raw_data_dir():
        data_dir = StarrLoader.fetch_data_dir()
        return os.path.join(data_dir, 'raw')

    @staticmethod
    def fetch_psql_dir():
        # CDSS/starr/data/
        starr_dir = StarrLoader.fetch_starr_dir()
        return os.path.join(starr_dir, 'psql')

    @staticmethod
    def fetch_psql_schemata_dir():
        # CDSS/starr/schemata/
        psql_dir = StarrLoader.fetch_psql_dir()
        return os.path.join(psql_dir, 'schemata')

    @staticmethod
    def download_starr_data():
        data_dir = StarrLoader.fetch_data_dir()

        # Remote folder ID defined in LocalEnv.
        box = BoxClient()
        box.download_folder(BOX_STARR_FOLDER_ID, data_dir)

    @staticmethod
    def build_clean_data_file(source_path, dest_path):
        # Force pandas to read certain fields as an object.
        # This both makes read_csv faster and reduces parsing errors.
        # Fields that look like integers should be read as objects so that
        # missing data doesn't force pandas to read as a float.
        # http://pandas.pydata.org/pandas-docs/stable/gotchas.html#support-for-integer-na
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
        elif 'fio2' in raw_file_name:
            # TODO(sbala): Find a way to capture the PEEP value in our schema.
            # FiO2 is sometimes recorded as a FiO2/PEEP value, which cannot
            # be stored as a floating point number. Given <5% of values include
            # a PEEP value (Positive End Expiratory-Pressure), it's OK to lose
            # this information. e.g. "0.50/8-10" ==> "0.50"
            float_value = raw_data['flowsheet_value'].str.split('/', \
                                                                expand=True)[0]
            raw_data['flowsheet_value'] = float_value


        # Write to csv.
        raw_data.to_csv(path_or_buf=dest_path, compression='gzip', index=False)

    @staticmethod
    def build_starr_psql_schemata():
        schemata_dir = StarrLoader.fetch_psql_schemata_dir()
        for params in StarrLoader.STARR_FILE_PARAMS.values():
            psql_table = params['psql_table']

            log.debug('loading %s schema...' % psql_table)

            # Open file, feed to DBUtil, and close file.
            schema_file_name = '.'.join([psql_table, 'schema.sql'])
            schema_file_path = os.path.join(schemata_dir, schema_file_name)
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
            raw_path = os.path.join(raw_data_dir, raw_file)
            clean_path = os.path.join(clean_data_dir, clean_file)
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

        # Build starr_patient_encounter based on starr_admit_vital
        # and stride_insurance.
        starr_patient_encounter_query = \
            """
            SELECT
                si.pat_id, si.pat_enc_csn_id,
                payor_name, title,
                bp_systolic, bp_diastolic,
                temperature, pulse, respirations
            INTO TABLE
                stride_patient_encounter
            FROM
                stride_insurance AS si
            JOIN
                stride_admit_vital AS sav
            ON
                si.pat_enc_csn_id=sav.pat_enc_csn_id;
            """
        DBUtil.execute(starr_patient_encounter_query)

if __name__=='__main__':
    # StarrLoader.download_starr_data()
    log.level = logging.DEBUG
    StarrLoader.load_starr_to_psql()
