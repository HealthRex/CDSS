set DATA_DIR="C:\Box Sync\SecureFiles\CDSS\inpatient5year"

python -m medinfo.db.DBUtil -d , -i %DATA_DIR%/Chen_Demographics.csv.gz -t stride_patient -f death_date
python -m medinfo.db.DBUtil -d , -i %DATA_DIR%/Chen_DX_List_5Yr.csv.gz -t stride_dx_list -f noted_date,resolved_date

python -m medinfo.db.DBUtil -d , -x -i %DATA_DIR%/Chen_Order_Med_5Yr.csv.gz -t stride_order_med  -f ordering_date,start_taking_time,order_end_time,end_taking_time,discon_time
python -m medinfo.db.DBUtil -d , -x -i %DATA_DIR%/Chen_Order_MedMixInfo_5Yr.csv.gz -t stride_order_medmixinfo

python -m medinfo.db.DBUtil -d , -x -i %DATA_DIR%/Chen_Order_Proc_Yr1.csv.gz -t stride_order_proc -f ordering_date,order_inst,instantiated_time,order_time,proc_start_time,proc_ending_time,result_time,last_stand_perf_dt,last_stand_perf_tm,proc_end_time,standing_exp_date,proc_bgn_time
python -m medinfo.db.DBUtil -d , -x -i %DATA_DIR%/Chen_Order_Proc_Yr2.csv.gz -t stride_order_proc -f ordering_date,order_inst,instantiated_time,order_time,proc_start_time,proc_ending_time,result_time,last_stand_perf_dt,last_stand_perf_tm,proc_end_time,standing_exp_date,proc_bgn_time
python -m medinfo.db.DBUtil -d , -x -i %DATA_DIR%/Chen_Order_Proc_Yr3.csv.gz -t stride_order_proc -f ordering_date,order_inst,instantiated_time,order_time,proc_start_time,proc_ending_time,result_time,last_stand_perf_dt,last_stand_perf_tm,proc_end_time,standing_exp_date,proc_bgn_time
python -m medinfo.db.DBUtil -d , -x -i %DATA_DIR%/Chen_Order_Proc_Yr4.csv.gz -t stride_order_proc -f ordering_date,order_inst,instantiated_time,order_time,proc_start_time,proc_ending_time,result_time,last_stand_perf_dt,last_stand_perf_tm,proc_end_time,standing_exp_date,proc_bgn_time
python -m medinfo.db.DBUtil -d , -x -i %DATA_DIR%/Chen_Order_Proc_Yr5.csv.gz -t stride_order_proc -f ordering_date,order_inst,instantiated_time,order_time,proc_start_time,proc_ending_time,result_time,last_stand_perf_dt,last_stand_perf_tm,proc_end_time,standing_exp_date,proc_bgn_time

python -m medinfo.db.DBUtil -d , -x -i %DATA_DIR%/Chen_Order_Result_Yr1.csv.gz -t stride_order_results  -f result_date,result_time
python -m medinfo.db.DBUtil -d , -x -i %DATA_DIR%/Chen_Order_Result_Yr2.csv.gz -t stride_order_results  -f result_date,result_time
python -m medinfo.db.DBUtil -d , -x -i %DATA_DIR%/Chen_Order_Result_Yr3.csv.gz -t stride_order_results  -f result_date,result_time
python -m medinfo.db.DBUtil -d , -x -i %DATA_DIR%/Chen_Order_Result_Yr4.csv.gz -t stride_order_results  -f result_date,result_time
python -m medinfo.db.DBUtil -d , -x -i %DATA_DIR%/Chen_Order_Result_Yr5.csv.gz -t stride_order_results  -f result_date,result_time

rem Support / Data Lookup Tables
python -m medinfo.db.DBUtil -d \t -i %DATA_DIR%/mapped_meds_5yr_20150508.txt.gz -t stride_mapped_meds 
python -m medinfo.db.DBUtil -d , -i %DATA_DIR%/export_ICD-9-CM_2013.csv.gz -t stride_icd9_cm

rem Order Set Usage
python -m medinfo.db.DBUtil -d , -i %DATA_DIR%/orderset_procedures.csv.gz -t stride_orderset_order_proc
python -m medinfo.db.DBUtil -d , -i %DATA_DIR%/orderset_medications.csv.gz -t stride_orderset_order_med

rem Treatment Team assignments
python -m medinfo.db.DBUtil -d , -x -i %DATA_DIR%/Chen_TreatmentTeam_Yr1.csv.gz -t stride_treatment_team  -f trtmnt_tm_begin_date,trtmnt_tm_end_date
python -m medinfo.db.DBUtil -d , -x -i %DATA_DIR%/Chen_TreatmentTeam_Yr2.csv.gz -t stride_treatment_team  -f trtmnt_tm_begin_date,trtmnt_tm_end_date
python -m medinfo.db.DBUtil -d , -x -i %DATA_DIR%/Chen_TreatmentTeam_Yr3.csv.gz -t stride_treatment_team  -f trtmnt_tm_begin_date,trtmnt_tm_end_date
python -m medinfo.db.DBUtil -d , -x -i %DATA_DIR%/Chen_TreatmentTeam_Yr4.csv.gz -t stride_treatment_team  -f trtmnt_tm_begin_date,trtmnt_tm_end_date
python -m medinfo.db.DBUtil -d , -x -i %DATA_DIR%/Chen_TreatmentTeam_Yr5.csv.gz -t stride_treatment_team  -f trtmnt_tm_begin_date,trtmnt_tm_end_date

rem Prior to Admission Medications
python -m medinfo.db.DBUtil -d , -i %DATA_DIR%/Chen_Active_Meds_At_Admit.csv.gz -t stride_preadmit_med  -f contact_date

rem Encounter Info (Insurance, Admit Vitals)
python -m medinfo.db.DBUtil -i %DATA_DIR%/Chen_Insurance_Info_5Yr.csv.gz -t stride_patient_encounter -d ,
python -m medinfo.db.DBUtil -i %DATA_DIR%/Chen_Admit_Vitals.csv.gz -t stride_patient_encounter -d ,

rem Notes data (metadata not actual note content)
python -m medinfo.db.DBUtil -d , -i %DATA_DIR%/Chen_Clinical_Notes_Yr1.csv.gz -t stride_note -f note_date
python -m medinfo.db.DBUtil -d , -i %DATA_DIR%/Chen_Clinical_Notes_Yr2.csv.gz -t stride_note -f note_date
python -m medinfo.db.DBUtil -d , -i %DATA_DIR%/Chen_Clinical_Notes_Yr3.csv.gz -t stride_note -f note_date
python -m medinfo.db.DBUtil -d , -i %DATA_DIR%/Chen_Clinical_Notes_Yr4.csv.gz -t stride_note -f note_date
python -m medinfo.db.DBUtil -d , -i %DATA_DIR%/Chen_Clinical_Notes_Yr5.csv.gz -t stride_note -f note_date

rem Medication to MPI mapping
python -m medinfo.db.DBUtil -d , -i %DATA_DIR%/Chen_MedicationID_to_MPI.csv.gz -t stride_medication_mpi

rem Public chargemaster
python -m medinfo.db.DBUtil -d , -x -i %DATA_DIR%/ChargeMaster.Stanford.2014.csv.gz -t chargemaster

rem ADT (Location) Data
python -m medinfo.db.DBUtil -d , -i %DATA_DIR%/JChenv3_ADTTable10.csv.gz -t stride_adt -f SHIFTED_TRANSF_IN_DT_TM,SHIFTED_TRANSF_OUT_DT_TM

rem Flowsheet data (e.g., Vitals).  May need -e to skip errors for FiO2/PEEP Scale Standard whose values cannot be parsed as simple floats
python -m medinfo.db.DBUtil -i %DATA_DIR%/JChenv3_fio2_Table4.csv.gz -d , -t STRIDE_FLOWSHEET -f SHIFTED_RECORD_DT_TM -e
python -m medinfo.db.DBUtil -i %DATA_DIR%/JChenv3_BP_Table1.namepatch.csv.gz -d , -t STRIDE_FLOWSHEET -f SHIFTED_RECORD_DT_TM
python -m medinfo.db.DBUtil -i %DATA_DIR%/JChenv3_GCS_Table8.csv.gz -d , -t STRIDE_FLOWSHEET -f SHIFTED_RECORD_DT_TM
python -m medinfo.db.DBUtil -i %DATA_DIR%/JChenv3_HRate_Table2.csv.gz -d , -t STRIDE_FLOWSHEET -f SHIFTED_RECORD_DT_TM
python -m medinfo.db.DBUtil -i %DATA_DIR%/JChenv3_pulse_Table5.csv.gz -d , -t STRIDE_FLOWSHEET -f SHIFTED_RECORD_DT_TM
python -m medinfo.db.DBUtil -i %DATA_DIR%/JChenv3_Resp_Table3.csv.gz -d , -t STRIDE_FLOWSHEET -f SHIFTED_RECORD_DT_TM
python -m medinfo.db.DBUtil -i %DATA_DIR%/JChenv3_temp_Table6.csv.gz -d , -t STRIDE_FLOWSHEET -f SHIFTED_RECORD_DT_TM
python -m medinfo.db.DBUtil -i %DATA_DIR%/JChenv3_urine_Table7.csv.gz -d , -t STRIDE_FLOWSHEET -f SHIFTED_RECORD_DT_TM



rem Input / Output Flowsheet Data
python -m medinfo.db.DBUtil -d , -i %DATA_DIR%/Jchen_Inpu_output_data1.csv.gz -t stride_io_flowsheet -f SHIFTED_TRANSF_IN_DT_TM
python -m medinfo.db.DBUtil -d , -i %DATA_DIR%/Jchen_Inpu_output_data2.csv.gz -t stride_io_flowsheet -f SHIFTED_TRANSF_IN_DT_TM
python -m medinfo.db.DBUtil -d , -i %DATA_DIR%/Jchen_Inpu_output_data3.csv.gz -t stride_io_flowsheet -f SHIFTED_TRANSF_IN_DT_TM
python -m medinfo.db.DBUtil -d , -i %DATA_DIR%/Jchen_Inpu_output_data4.csv.gz -t stride_io_flowsheet -f SHIFTED_TRANSF_IN_DT_TM
python -m medinfo.db.DBUtil -d , -i %DATA_DIR%/Jchen_Inpu_output_data5.csv.gz -t stride_io_flowsheet -f SHIFTED_TRANSF_IN_DT_TM
