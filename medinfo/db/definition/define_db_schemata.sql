-- Wrapper script to define all DB schema.
-- Note that the order in which schema are defined may be significant,
-- as some schema definitions reference previous schema.

-- CPOE Statistics
\i medinfo/db/definition/tables/clinical_item_category.sql
\i medinfo/db/definition/tables/clinical_item.sql
\i medinfo/db/definition/tables/patient_item.sql
\i medinfo/db/definition/tables/clinical_item_association.sql
\i medinfo/db/definition/tables/order_result_stat.sql
\i medinfo/db/definition/tables/data_cache.sql
\i medinfo/db/definition/tables/backup_link_patient_item.sql
\i medinfo/db/definition/tables/clinical_item_link.sql
\i medinfo/db/definition/tables/item_collection.sql
\i medinfo/db/definition/tables/collection_type.sql
\i medinfo/db/definition/tables/item_collection_item.sql
\i medinfo/db/definition/tables/patient_item_collection_link.sql

-- CPOE Simultation
\i medinfo/db/definition/tables/sim_user.sql
\i medinfo/db/definition/tables/sim_patient.sql
\i medinfo/db/definition/tables/sim_state.sql
\i medinfo/db/definition/tables/sim_patient_state.sql
\i medinfo/db/definition/tables/sim_state_transition.sql
\i medinfo/db/definition/tables/sim_note_type.sql
\i medinfo/db/definition/tables/sim_note.sql
\i medinfo/db/definition/tables/sim_result.sql
\i medinfo/db/definition/tables/sim_state_result.sql
\i medinfo/db/definition/tables/sim_order_result_map.sql
\i medinfo/db/definition/tables/sim_patient_order.sql

-- Opioid RX
\i medinfo/db/definition/tables/stride_mapped_meds.sql
\i medinfo/db/definition/tables/stride_order_med.sql
\i medinfo/db/definition/tables/stride_order_proc_drug_screen.sql
\i medinfo/db/definition/tables/stride_patient.sql
\i medinfo/db/definition/tables/stride_order_proc_referrals_n_consults.sql
\i medinfo/db/definition/tables/stride_pat_enc.sql
\i medinfo/db/definition/tables/stride_problem_list.sql
\i medinfo/db/definition/tables/stride_icd9_cm.sql

-- STRIDE Data
-- \i medinfo/db/definition/tables/stride_order_proc.sql
-- \i medinfo/db/definition/tables/stride_order_instantiated.sql

-- -- Another? connection table for instantiated / spawned child orders off initial parent orders
-- create table stride_stand_hov_inst_ord
-- (
--     parent_order_proc_id bigint not null,
--     line               integer not null,
--     child_order_proc_id bigint
-- );
--
-- -- Order Results / Lab Results generated from orders
-- create table stride_order_results (
--     order_proc_id bigint not null,
--     line          integer not null,
--     ord_date_real  float,
--     result_date date,
--     result_time timestamp,
--     component_name text,
--     base_name      text,
--     common_name    text,
--     ord_num_value float,
--     reference_unit     text,
--     result_in_range_yn text,
--     result_flag        text,
--     result_status      text,
--     lab_status         text,
--     value_normalized   text
--   );
--
--
--
--
--
-- -- Medication Sub-Table to Itemize Mixture Components
-- create table stride_order_medmixinfo
-- (
-- 	order_med_id bigint,	-- link to parent order medication entry
-- 	line integer,
-- 	medication_id integer,	-- core id number for this medication component
-- 	medication_name text,	-- text description of the medication
-- 	ingredient_type_c integer,
-- 	ingredient_type text,
-- 	min_dose_amount float,
-- 	max_dose_amount float,
-- 	dose_unit_c integer,
-- 	dose_unit text,
-- 	nonformulary_yn text,
-- 	selection integer,
-- 	min_calc_dose_amt float,
-- 	max_calc_dose_amt float,
-- 	calc_dose_unit_c integer,
-- 	calc_dose_unit text,
-- 	dose_calc_info text
--   );
--
--
-- -- Mapping Table for Medications to Common Active Ingredients
-- create table stride_mapped_meds
-- (
-- 	medication_id integer,
-- 	medication_name text,
-- 	rxcui integer,
-- 	active_ingredient text
-- );
--
-- -- Prior to Admission Medications.  Not ordered during stay, but documenting previously taking
-- create table stride_preadmit_med
-- (
-- 	stride_preadmit_med_id SERIAL,
-- 	pat_anon_id bigint,
-- 	contact_date timestamp,
-- 	medication_id integer,
-- 	description text,
-- 	thera_class text,
-- 	pharm_class text,
-- 	pharm_subclass text
-- );
--
-- alter table stride_mapped_meds add column thera_class text;
-- alter table stride_mapped_meds add column pharm_class text;
-- alter table stride_mapped_meds add column pharm_subclass text;
--
--
-- -- Diagnosis / Problem List codes
-- create table stride_dx_list
-- (
--     pat_id         text,
--     pat_enc_csn_id bigint,
--     noted_date date,
--     resolved_date date,
--     dx_icd9_code text,
--     data_source text
-- );
-- ALTER TABLE stride_dx_list ADD COLUMN dx_icd9_code_list TEXT;
--
-- -- ICD9 Translation Table
-- create table stride_icd9_cm
-- (
-- 	CUI	text,
-- 	ISPREF text,
-- 	AUI	text,
-- 	TTY	text,
-- 	CODE text,
-- 	STR	text,
-- 	SUPPRESS	text
-- );
--
--
--
-- create table STRIDE_ORDERSET_ORDER_PROC
-- (
-- 	ORDER_PROC_ID bigint,
-- 	PROC_CODE text,
-- 	PROC_ID bigint,
-- 	SS_SG_KEY text,
-- 	SECTION_NAME text,
-- 	SMART_GROUP text,
-- 	ORDER_TYPE text,
-- 	PROTOCOL_ID bigint,
-- 	PROTOCOL_NAME text
-- );
--
-- create table STRIDE_ORDERSET_ORDER_MED
-- (
-- 	ORDER_MED_ID bigint,
-- 	DESCRIPTION text,
-- 	MEDICATION_ID integer,
-- 	SS_SG_KEY text,
-- 	SECTION_NAME text,
-- 	SMART_GROUP text,
-- 	ORDER_TYPE text,
-- 	PROTOCOL_ID bigint,
-- 	PROTOCOL_NAME text
-- );
--
--
-- create table STRIDE_TREATMENT_TEAM
-- (
-- 	STRIDE_TREATMENT_TEAM_ID serial,
-- 	PAT_ID text,
-- 	PAT_ENC_CSN_ID bigint,
-- 	LINE integer,
-- 	TRTMNT_TM_BEGIN_DATE timestamp,
-- 	TRTMNT_TM_END_DATE timestamp,
-- 	TREATMENT_TEAM text,
-- 	PROV_NAME text
-- );
--
-- create table STRIDE_PATIENT_ENCOUNTER
-- (
-- 	PAT_ENC_CSN_ID bigint,
-- 	PAT_ID bigint,
--
-- 	PAYOR_NAME text,
-- 	TITLE text,
--
-- 	BP_SYSTOLIC integer,
-- 	BP_DIASTOLIC integer,
-- 	TEMPERATURE float,
-- 	PULSE integer,
-- 	RESPIRATIONS integer
-- );
--
--
-- create table STRIDE_FLOWSHEET
-- (
-- 	PAT_ENC_CSN_ANON_ID bigint,
-- 	PAT_ANON_ID bigint,
-- 	FLO_MEAS_ID int,
-- 	FLOWSHEET_NAME text,
-- 	FLOWSHEET_VALUE float,
-- 	SHIFTED_RECORD_DT_TM timestamp
-- );
--
-- -- Metadat about patient notes, but not the actual note content (keeps things deidentified)
-- create table STRIDE_NOTE
-- (
-- 	PAT_ID bigint,
-- 	PAT_ENC_CSN_ID bigint,
-- 	NOTE_DATE timestamp,
-- 	NOTE_TYPE text,
-- 	AUTHOR_NAME text,
-- 	PROVIDER_TYPE text,
-- 	HOSPITAL_SERVICE text,
-- 	DEPARTMENT text,
-- 	SPECIALTY text,
-- 	COSIGNER_NAME text,
-- 	STATUS text
-- );
--
-- create table STRIDE_ADT
-- (
-- 	PAT_ANON_ID bigint,
-- 	PAT_ENC_CSN_ANON_ID bigint,
-- 	SEQ_NUM_IN_BED_MIN integer,
-- 	SEQ_NUM_IN_ENC integer,
-- 	PATIENT_CLASS text,
-- 	BED text,
-- 	BED_STATUS text,
-- 	SHIFTED_TRANSF_IN_DT_TM timestamp,
-- 	DEPARTMENT_IN text,
-- 	EVENT_IN text,
-- 	SHIFTED_TRANSF_OUT_DT_TM timestamp,
-- 	EVENT_OUT text
-- );
--
-- create table STRIDE_MEDICATION_MPI
-- (
-- 	MEDICATION_ID integer,
-- 	MED_NAME text,
-- 	MPI_ID_VAL text,
-- 	STATUS text
-- );
--
-- -- Not from STRIDE. Public content retrievable from http://www.oshpd.ca.gov/chargemaster/
-- -- Consider adding columns to delineate multiple years and sources of data
-- create table CHARGEMASTER
-- (
-- 	SERVICE_CODE integer,
-- 	DESCRIPTION text,
-- 	PRICE float
-- );
--
-- create table STRIDE_IO_FLOWSHEET
-- (
-- 	PAT_ANON_ID bigint,
-- 	PAT_ENC_CSN_ANON_ID bigint,
-- 	FLO_MEAS_ID bigint,
-- 	G1_DISP_NAME text,
-- 	G2_DISP_NAME text,
-- 	SHIFTED_TRANSF_IN_DT_TM timestamp,
-- 	MEAS_VALUE text,
-- 	RN bigint
-- );
