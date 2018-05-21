"""
Parameters to be used by StrideLoader.

Defines the mappings between raw_stride_file ==> clean_stride_file
and clean_stride_file ==> psql_table. If other data is added in the future,
(e.g. names of MySQL tables), should be added here.
"""

# For backwards compatibility with the application code throughout the
# database which originally calls starr.
TABLE_PREFIX = 'starr'

STRIDE_LOADER_PARAMS = {
    'Chen_Demographics.csv.gz': {
        'clean_file': '%s_demographics_2008_2014.csv.gz',
        'psql_table': '%s_patient'
    },
    'Chen_Demographics_Yr6_8.csv.gz': {
        'clean_file': '%s_demographics_2014_2017.csv.gz',
        'psql_table': '%s_patient'
    },
    'Chen_Active_Meds_At_Admit.csv.gz': {
        'clean_file': '%s_preadmit_meds_2008_2014.csv.gz',
        'psql_table': '%s_preadmit_med'
    },
    'Chen_Admit_Vitals.csv.gz': {
        'clean_file': '%s_admit_vitals_2008_2014.csv.gz',
        'psql_table': '%s_patient_encounter'
    },
    'Chen_Clinical_Notes_Yr1.csv.gz': {
        'clean_file': '%s_clinical_notes_year_1.csv.gz',
        'psql_table': '%s_note'
    },
    'Chen_Clinical_Notes_Yr2.csv.gz': {
        'clean_file': '%s_clinical_notes_year_2.csv.gz',
        'psql_table': '%s_note'
    },
    'Chen_Clinical_Notes_Yr3.csv.gz': {
        'clean_file': '%s_clinical_notes_year_3.csv.gz',
        'psql_table': '%s_note'
    },
    'Chen_Clinical_Notes_Yr4.csv.gz': {
        'clean_file': '%s_clinical_notes_year_4.csv.gz',
        'psql_table': '%s_note'
    },
    'Chen_Clinical_Notes_Yr5.csv.gz': {
        'clean_file': '%s_clinical_notes_year_5.csv.gz',
        'psql_table': '%s_note'
    },
    'Chen_Clinical_Notes_Yr6.csv.gz': {
        'clean_file': '%s_clinical_notes_year_6.csv.gz',
        'psql_table': '%s_note'
    },
    'Chen_Clinical_Notes_Yr7.csv.gz': {
        'clean_file': '%s_clinical_notes_year_7.csv.gz',
        'psql_table': '%s_note'
    },
    'Chen_Clinical_Notes_Yr8.csv.gz': {
        'clean_file': '%s_clinical_notes_year_8.csv.gz',
        'psql_table': '%s_note'
    },
    'Chen_DX_List_5Yr.csv.gz': {
        'clean_file': '%s_dx_2008_2014.csv.gz',
        'psql_table': '%s_dx'
    },
    'Chen_Dx_List_Yrs6_8.csv.gz': {
        'clean_file': '%s_dx_2014_2017.csv.gz',
        'psql_table': '%s_dx'
    },
    'Chen_Insurance_Info_5Yr.csv.gz': {
        'clean_file': '%s_insurance_2008_2014.csv.gz',
        'psql_table': '%s_patient_encounter'
    },
    'Chen_Insurance_Info_Yrs6_8.csv.gz': {
        'clean_file': '%s_insurance_2014_2017.csv.gz',
        'psql_table': '%s_patient_encounter'
    },
    'Chen_Mapped_Meds_5Yr.csv.gz': {
        'clean_file': '%s_medication_2008_2014.csv.gz',
        'psql_table': '%s_medication'
    },
    'Chen_Mapped_Meds_Yrs6_8.csv.gz': {
        'clean_file': '%s_medication_2014_2017.csv.gz',
        'psql_table': '%s_medication'
    },
    'Chen_MedicationID_to_MPI.csv.gz': {
        'clean_file': '%s_medication_mpi.csv.gz',
        'psql_table': '%s_medication_mpi'
    },
    'Chen_Order_MedMixInfo_5Yr.csv.gz': {
        'clean_file': '%s_medication_mix_2008_2014.csv.gz',
        'psql_table': '%s_medication_mix'
    },
    'Chen_MedMixInfo_Yrs6_8.patchHeader.csv.gz': {
        'clean_file': '%s_medication_mix_2014_2017.csv.gz',
        'psql_table': '%s_medication_mix'
    },
    'Chen_Order_Proc_Yr1.patchcommas.csv.gz': {
        'clean_file': '%s_order_proc_year_1.csv.gz',
        'psql_table': '%s_order_proc'
    },
    'Chen_Order_Proc_Yr2.patchcommas.csv.gz': {
        'clean_file': '%s_order_proc_year_2.csv.gz',
        'psql_table': '%s_order_proc'
    },
    'Chen_Order_Proc_Yr3.patchcommas.csv.gz': {
        'clean_file': '%s_order_proc_year_3.csv.gz',
        'psql_table': '%s_order_proc'
    },
    'Chen_Order_Proc_Yr4.patchcommas.csv.gz': {
        'clean_file': '%s_order_proc_year_4.csv.gz',
        'psql_table': '%s_order_proc'
    },
    'Chen_Order_Proc_Yr5.patchcommas.csv.gz': {
        'clean_file': '%s_order_proc_year_5.csv.gz',
        'psql_table': '%s_order_proc'
    },
    'Chen_Order_Proc_Yr6.patchcommas.csv.gz': {
        'clean_file': '%s_order_proc_year_6.csv.gz',
        'psql_table': '%s_order_proc'
    },
    'Chen_Order_Proc_Yr7.patchcommas.csv.gz': {
        'clean_file': '%s_order_proc_year_7.csv.gz',
        'psql_table': '%s_order_proc'
    },
    'Chen_Order_Proc_Yr8.patchcommas.csv.gz': {
        'clean_file': '%s_order_proc_year_8.csv.gz',
        'psql_table': '%s_order_proc'
    },
    'Chen_Order_Result_Yr1.csv.gz': {
        'clean_file': '%s_order_result_year_1.csv.gz',
        'psql_table': '%s_order_result'
    },
    'Chen_Order_Result_Yr2.csv.gz': {
        'clean_file': '%s_order_result_year_2.csv.gz',
        'psql_table': '%s_order_result'
    },
    'Chen_Order_Result_Yr3.csv.gz': {
        'clean_file': '%s_order_result_year_3.csv.gz',
        'psql_table': '%s_order_result'
    },
    'Chen_Order_Result_Yr4.csv.gz': {
        'clean_file': '%s_order_result_year_4.csv.gz',
        'psql_table': '%s_order_result'
    },
    'Chen_Order_Result_Yr5.csv.gz': {
        'clean_file': '%s_order_result_year_5.csv.gz',
        'psql_table': '%s_order_result'
    },
    'Chen_Order_Res_Yr6.csv.gz': {
        'clean_file': '%s_order_result_year_6.csv.gz',
        'psql_table': '%s_order_result'
    },
    'Chen_Order_Res_Yr7.csv.gz': {
        'clean_file': '%s_order_result_year_7.csv.gz',
        'psql_table': '%s_order_result'
    },
    'Chen_Order_Res_Yr8.csv.gz': {
        'clean_file': '%s_order_result_year_8.csv.gz',
        'psql_table': '%s_order_result'
    },
    'Chen_TreatmentTeam_Yr1.csv.gz': {
        'clean_file': '%s_treatment_team_year_1.csv.gz',
        'psql_table': '%s_treatment_team'
    },
    'Chen_TreatmentTeam_Yr2.csv.gz': {
        'clean_file': '%s_treatment_team_year_2.csv.gz',
        'psql_table': '%s_treatment_team'
    },
    'Chen_TreatmentTeam_Yr3.csv.gz': {
        'clean_file': '%s_treatment_team_year_3.csv.gz',
        'psql_table': '%s_treatment_team'
    },
    'Chen_TreatmentTeam_Yr4.csv.gz': {
        'clean_file': '%s_treatment_team_year_4.csv.gz',
        'psql_table': '%s_treatment_team'
    },
    'Chen_TreatmentTeam_Yr5.csv.gz': {
        'clean_file': '%s_treatment_team_year_5.csv.gz',
        'psql_table': '%s_treatment_team'
    },
    'Chen_Treatment_Team_Yrs6.patchHeader.csv.gz': {
        'clean_file': '%s_treatment_team_year_6.csv.gz',
        'psql_table': '%s_treatment_team'
    },
    'Chen_Treatment_Team_Yrs7.patchHeader.csv.gz': {
        'clean_file': '%s_treatment_team_year_7.csv.gz',
        'psql_table': '%s_treatment_team'
    },
    'Chen_Treatment_Team_Yrs8.patchHeader.csv.gz': {
        'clean_file': '%s_treatment_team_year_8.csv.gz',
        'psql_table': '%s_treatment_team'
    },
    'Chen_income_vs_zip.csv.gz': {
        'clean_file': '%s_income_2008_2014.csv.gz',
        'psql_table': '%s_income'
    },
    'Chen_income_vs_zip_Yrs6_8.csv.gz': {
        'clean_file': '%s_income_2014_2017.csv.gz',
        'psql_table': '%s_income'
    },
    'JChenv3_BP_Table1.patchHeader.csv.gz': {
        'clean_file': '%s_flow_bp_2008_2014.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_HRate_Table2.patchHeader.csv.gz': {
        'clean_file': '%s_flow_hr_2008_2014.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_Resp_Table3.patchHeader.csv.gz': {
        'clean_file': '%s_flow_resp_2008_2014.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_fio2_Table4.patchHeader.csv.gz': {
        'clean_file': '%s_flow_fio2_2008_2014.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_pulse_Table5.patchHeader.csv.gz': {
        'clean_file': '%s_flow_pulse_2008_2014.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_temp_Table6.patchHeader.csv.gz': {
        'clean_file': '%s_flow_temp_2008_2014.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_urine_Table7.patchHeader.csv.gz': {
        'clean_file': '%s_flow_urine_2008_2014.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_GCS_Table8.patchHeader.csv.gz': {
        'clean_file': '%s_flow_gcs_2008_2014.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_BP_Table11.patchHeader.csv.gz': {
        'clean_file': '%s_flow_bp_2014_2017_11.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_BP_Table12.patchHeader.csv.gz': {
        'clean_file': '%s_flow_bp_2014_2017_12.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_BP_Table13.patchHeader.csv.gz': {
        'clean_file': '%s_flow_bp_2014_2017_13.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_BP_Table14.patchHeader.csv.gz': {
        'clean_file': '%s_flow_bp_2014_2017_14.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_BP_Table15.patchHeader.csv.gz': {
        'clean_file': '%s_flow_bp_2014_2017_15.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_Heartrate_Table16.csv.gz': {
        'clean_file': '%s_flow_hr_2014_2017_16.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_Heartrate_Table17.csv.gz': {
        'clean_file': '%s_flow_hr_2014_2017_17.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_Heartrate_Table18.csv.gz': {
        'clean_file': '%s_flow_hr_2014_2017_18.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_Heartrate_Table19.csv.gz': {
        'clean_file': '%s_flow_hr_2014_2017_19.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_Heartrate_Table20.csv.gz': {
        'clean_file': '%s_flow_hr_2014_2017_20.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_Heartrate_Table20.csv.gz': {
        'clean_file': '%s_flow_hr_2014_2017_20.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_Resp_Table21.csv.gz': {
        'clean_file': '%s_flow_resp_2014_2017_21.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_Resp_Table22.csv.gz': {
        'clean_file': '%s_flow_resp_2014_2017_22.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_Resp_Table23.csv.gz': {
        'clean_file': '%s_flow_resp_2014_2017_23.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_Resp_Table24.csv.gz': {
        'clean_file': '%s_flow_resp_2014_2017_24.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_Resp_Table25.csv.gz': {
        'clean_file': '%s_flow_resp_2014_2017_25.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_temp_Table26.csv.gz': {
        'clean_file': '%s_flow_temp_2014_2017_26.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_temp_Table27.csv.gz': {
        'clean_file': '%s_flow_temp_2014_2017_27.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_temp_Table28.csv.gz': {
        'clean_file': '%s_flow_temp_2014_2017_28.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_temp_Table29.csv.gz': {
        'clean_file': '%s_flow_temp_2014_2017_29.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_temp_Table30.csv.gz': {
        'clean_file': '%s_flow_temp_2014_2017_30.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_fio2_Table31.csv.gz': {
        'clean_file': '%s_flow_fio2_2014_2017_31.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_fio2_Table32.csv.gz': {
        'clean_file': '%s_flow_fio2_2014_2017_32.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_fio2_Table33.csv.gz': {
        'clean_file': '%s_flow_fio2_2014_2017_33.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_fio2_Table34.csv.gz': {
        'clean_file': '%s_flow_fio2_2014_2017_34.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_fio2_Table35.csv.gz': {
        'clean_file': '%s_flow_fio2_2014_2017_35.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_pulse_Table36.csv.gz': {
        'clean_file': '%s_flow_pulse_2014_2017_36.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_pulse_Table37.csv.gz': {
        'clean_file': '%s_flow_pulse_2014_2017_37.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_pulse_Table38.csv.gz': {
        'clean_file': '%s_flow_pulse_2014_2017_38.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_pulse_Table39.csv.gz': {
        'clean_file': '%s_flow_pulse_2014_2017_39.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_pulse_Table40.csv.gz': {
        'clean_file': '%s_flow_pulse_2014_2017_40.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_urine_Table41.csv.gz': {
        'clean_file': '%s_flow_urine_2014_2017_41.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_urine_Table42.csv.gz': {
        'clean_file': '%s_flow_urine_2014_2017_42.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_urine_Table43.csv.gz': {
        'clean_file': '%s_flow_urine_2014_2017_43.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_urine_Table44.csv.gz': {
        'clean_file': '%s_flow_urine_2014_2017_44.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_urine_Table45.csv.gz': {
        'clean_file': '%s_flow_urine_2014_2017_45.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_GCS_Table46.csv.gz': {
        'clean_file': '%s_flow_gcs_2014_2017_46.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_GCS_Table47.csv.gz': {
        'clean_file': '%s_flow_gcs_2014_2017_47.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_GCS_Table48.csv.gz': {
        'clean_file': '%s_flow_gcs_2014_2017_48.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_GCS_Table49.csv.gz': {
        'clean_file': '%s_flow_gcs_2014_2017_49.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_GCS_Table50.csv.gz': {
        'clean_file': '%s_flow_gcs_2014_2017_50.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_sp02_Table51.csv.gz': {
        'clean_file': '%s_flow_spo2_2014_2017_51.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_sp02_Table52.csv.gz': {
        'clean_file': '%s_flow_spo2_2014_2017_52.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_sp02_Table53.csv.gz': {
        'clean_file': '%s_flow_spo2_2014_2017_53.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_sp02_Table54.csv.gz': {
        'clean_file': '%s_flow_spo2_2014_2017_54.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChenv3_sp02_Table55.csv.gz': {
        'clean_file': '%s_flow_spo2_2014_2017_55.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChen_Flwst_Height_Yr8.csv.gz': {
        'clean_file': '%s_flow_height_2008_2017.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'JChen_Flwst_Weight_Yr8.csv.gz': {
        'clean_file': '%s_flow_weight_2008_2017.csv.gz',
        'psql_table': '%s_flowsheet'
    },
    'Jchen_Inpu_output_data1.csv.gz': {
        'clean_file': '%s_io_flowsheet_1.csv.gz',
        'psql_table': '%s_io_flowsheet'
    },
    'Jchen_Inpu_output_data2.csv.gz': {
        'clean_file': '%s_io_flowsheet_2.csv.gz',
        'psql_table': '%s_io_flowsheet'
    },
    'Jchen_Inpu_output_data3.csv.gz': {
        'clean_file': '%s_io_flowsheet_3.csv.gz',
        'psql_table': '%s_io_flowsheet'
    },
    'Jchen_Inpu_output_data4.csv.gz': {
        'clean_file': '%s_io_flowsheet_4.csv.gz',
        'psql_table': '%s_io_flowsheet'
    },
    'Jchen_Inpu_output_data5.csv.gz': {
        'clean_file': '%s_io_flowsheet_5.csv.gz',
        'psql_table': '%s_io_flowsheet'
    },
    'Jchen_Inpu_output_update_11.csv.gz': {
        'clean_file': '%s_io_flowsheet_11.csv.gz',
        'psql_table': '%s_io_flowsheet'
    },
    'Jchen_Inpu_output_update_12.csv.gz': {
        'clean_file': '%s_io_flowsheet_12.csv.gz',
        'psql_table': '%s_io_flowsheet'
    },
    'Jchen_Inpu_output_update_13.csv.gz': {
        'clean_file': '%s_io_flowsheet_13.csv.gz',
        'psql_table': '%s_io_flowsheet'
    },
    'Jchen_Inpu_output_update_14.csv.gz': {
        'clean_file': '%s_io_flowsheet_14.csv.gz',
        'psql_table': '%s_io_flowsheet'
    },
    'Jchen_Inpu_output_update_15.csv.gz': {
        'clean_file': '%s_io_flowsheet_15.csv.gz',
        'psql_table': '%s_io_flowsheet'
    },
    'Jchen_Inpu_output_update_16.csv.gz': {
        'clean_file': '%s_io_flowsheet_16.csv.gz',
        'psql_table': '%s_io_flowsheet'
    },
    'Jchen_Inpu_output_update_17.csv.gz': {
        'clean_file': '%s_io_flowsheet_17.csv.gz',
        'psql_table': '%s_io_flowsheet'
    },
    'Jchen_Inpu_output_update_18.csv.gz': {
        'clean_file': '%s_io_flowsheet_18.csv.gz',
        'psql_table': '%s_io_flowsheet'
    },
    'Jchen_Inpu_output_update_19.csv.gz': {
        'clean_file': '%s_io_flowsheet_19.csv.gz',
        'psql_table': '%s_io_flowsheet'
    },
    'Jchen_Inpu_output_update_20.csv.gz': {
        'clean_file': '%s_io_flowsheet_20.csv.gz',
        'psql_table': '%s_io_flowsheet'
    },
    'export_ICD-9-CM_2013.csv.gz': {
        'clean_file': 'icd9_cm_2013.csv.gz',
        'psql_table': 'icd9_cm'
    },
    'JChenv3_ADTTable10.csv.gz': {
        'clean_file': '%s_adt_2008_2014.csv.gz',
        'psql_table': '%s_adt'
    },
    'JChenv3_ADTTable56.csv.gz': {
        'clean_file': '%s_adt_2014_2017.csv.gz',
        'psql_table': '%s_adt'
    },
    'ChargeMaster.Stanford.2014.csv.gz': {
        'clean_file': 'stanford_chargemaster_2014.csv.gz',
        'psql_table': 'stanford_chargemaster'
    },
    'Chen_Order_Med_5Yr.patchQuotes.csv.gz': {
        'clean_file': '%s_order_med_2008_2014.csv.gz',
        'psql_table': '%s_order_med'
    },
    'Chen_Order_Med_Yrs6_8.patchHeader.csv.gz': {
        'clean_file': '%s_order_med_2014_2017.csv.gz',
        'psql_table': '%s_order_med'
    },
    'orderset_procedures.csv.gz': {
        'clean_file': '%s_orderset_order_proc_2008_2014.csv.gz',
        'psql_table': '%s_orderset_order_proc'
    },
    'Chen_OrderSets_Proc_Yrs6_8.csv.gz': {
        'clean_file': '%s_orderset_order_proc_2014_2017.csv.gz',
        'psql_table': '%s_orderset_order_proc'
    },
    'orderset_medications.csv.gz': {
        'clean_file': '%s_orderset_order_med_2008_2014.csv.gz',
        'psql_table': '%s_orderset_order_med'
    },
    'Chen_OrderSets_Med_Yrs6_8.csv.gz': {
        'clean_file': '%s_orderset_order_med_2014_2017.csv.gz',
        'psql_table': '%s_orderset_order_med'
    },
    'JChen_cult_micro_7yr.patchIds.csv.gz': {
        'clean_file': '%s_culture_micro_7_year.csv.gz',
        'psql_table': '%s_culture_micro'
    },
    'export_ICD-10-CM_2016.csv.gz': {
        'clean_file': 'icd10_cm_2016.csv.gz',
        'psql_table': 'icd10_cm'
    },
    'JChenv3_Admits_Table58.csv.gz': {
        'clean_file': '%s_admit_2014_2017.csv.gz',
        'psql_table': '%s_admit'
    },
    'JChenv3_DRG_Table57.csv.gz': {
        'clean_file': '%s_drg_7_year.csv.gz',
        'psql_table': '%s_drg'
    }
}
