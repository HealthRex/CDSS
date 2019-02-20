-- Mapping Table for Medications to Common Active Ingredients
create table stride_mapped_meds
(
	medication_id integer,
	medication_name text,
	rxcui integer,
	active_ingredient text
);
CREATE INDEX index_stride_mapped_meds_medication_id ON stride_mapped_meds(medication_id);
ALTER TABLE stride_mapped_meds ADD COLUMN analysis_status INTEGER DEFAULT 1;
ALTER TABLE stride_mapped_meds ADD COLUMN morphine_po_equivalent FLOAT;

-- Medication Order Data Table.  Source headers need " removed, lower-case, and make sure refills column is numeric
-- 	Remove " marks and lower-case header lines
--	(Refills should be numeric 0 not char o.  Just swap "o" for "0")  (Entry 436981419... refills should be numeric, not "prn")
create table stride_order_med
(
	order_med_id bigint not null,
	pat_id text,
	pat_enc_csn_id bigint,
	ordering_datetime datetime,
	hosp_admsn_time datetime,
	hosp_dischrg_time datetime,
	order_class text,
	medication_id integer,
	description text,
	sig text,
	quantity text,
	refills integer,
	start_date datetime,
	end_date datetime,
	dispense_as_written_yn text,
	reason_for_discontinuation text,
	enc_type_c integer,
	encounter_type text,
	patient_location text,
	login_department text,
	display_name text,
	hv_hospitalist_yn text,
	med_route text,
	discontinue_time datetime,
	changed_from_order_med_id bigint,
	reason_pended_med_refused text,
	hv_discr_freq_id bigint,
	discr_freq_name text,
	discr_freq_display_name text,
	discr_freq_type text,
	discr_freq_number_of_times integer,
	freq_time_unit text,
	prn_yn text,
	freq_duplicate_dose_interval integer,
	freq_missed_dose_interval integer,
	freqency_or_period text,
	hv_discrete_dose text,
	hv_dose_unit text,
	non_formulary_yn text,
	order_status text,
	min_discrete_dose float,
	max_discrete_dose float,
	dose_unit text,
	is_pending_ord_yn text,
	modify_track text,
	med_comments text,
	usr_select_medicn_id integer,
	lastdose text,
	amb_med_disp_name text,
	refills_remaining integer,
	rule_based_order_transmittl_yn text,
	outpat_orderstat_before_admsn text,
	last_dose_time text,
	pend_approve_flag text,
	prn_comment text,
	med_dis_disp_qty integer,
	med_dis_disp_unit text
);
ALTER TABLE stride_order_med ADD CONSTRAINT stride_order_med_pkey PRIMARY KEY (order_med_id);
CREATE INDEX index_stride_order_med_pat_id ON stride_order_med(pat_id (16));
CREATE INDEX index_stride_order_med_ordering_datetime ON stride_order_med(ordering_datetime);
CREATE INDEX index_stride_order_med_pat_enc_csn_id ON stride_order_med(pat_enc_csn_id);
CREATE INDEX index_stride_order_med_medication_id ON stride_order_med(medication_id);


-- Drug Screen Results
-- 	Header row: Remove " marks and lower-case header lines
create table stride_order_proc_drug_screen
(
	order_proc_id bigint,
	pat_id text,
	pat_enc_csn_id bigint,
	ordering_date datetime,
	proc_id integer,
	proc_code text,
	description text,
	quantity integer,
	order_status_c text,
	order_status text,
	reason_for_cancellation text,
	future_or_stand text,
	standing_exp_date datetime,
	future_expected_compltn_date datetime,
	standing_occurs integer,
	stand_orig_occur integer,
	rfl_priority text,
	order_priority text,
	stand_interval text,
	instantiated_time datetime,
	ordering_mode text,
	is_pending_ord_yn text,
	proc_start_time datetime,
	proc_end_time datetime,
	id_of_replaced_order_proc_id bigint,
	patient_location text,
	login_department text,
	specimen_taken_time datetime,
	specimen_recv_time datetime,
	result_line integer,
	component_id integer,
	component_name text,
	ord_value text,
	ref_normal_vals text
);
CREATE INDEX index_stride_order_proc_drug_screen_compkey ON stride_order_proc_drug_screen(order_proc_id, result_line);
CREATE INDEX index_stride_order_proc_drug_screen_pat_id ON stride_order_proc_drug_screen(pat_id (16));
CREATE INDEX index_stride_order_proc_drug_screen_pat_enc_csn_id ON stride_order_proc_drug_screen(pat_enc_csn_id);
CREATE INDEX index_stride_order_proc_drug_screen_component_id ON stride_order_proc_drug_screen(component_id);

-- Patient ID list with birth date, gender, race
-- 	Header: Lower-case
create table stride_patient
(
	pat_id text,
	pat_mrn_id bigint,
	birth_date datetime,
	gender text,
	primary_race text
);
CREATE INDEX index_patient_pat_id ON stride_patient(pat_id (16));
CREATE INDEX index_patient_pat_mrn_id ON stride_patient(pat_mrn_id);
-- Get rid of identifying information
ALTER TABLE stride_patient ADD COLUMN birth_year INTEGER;
UPDATE stride_patient SET birth_year = YEAR(birth_date);
ALTER TABLE stride_patient DROP COLUMN birth_date;
ALTER TABLE stride_patient DROP COLUMN pat_mrn_id;

-- Populate oncology label based on patient_possible_onco.csv
ALTER TABLE stride_patient ADD COLUMN possible_oncology INTEGER DEFAULT 0;



-- Referrals and Consults, includes patient location and login department (lots of inpatient data too)
--	Header: Lower-case, remove " marks
--	Look for rfl_priority is not null and ordering_mode = 'Outpatient' to isolate relevant referrals
CREATE TABLE stride_order_proc_referrals_n_consults
(
	order_proc_id bigint,
	pat_id text,
	pat_enc_csn_id bigint,
	ordering_date datetime,
	proc_id bigint,
	proc_code text,
	description text,
	quantity integer,
	order_status_c integer,
	order_status text,
	reason_for_cancellation text,
	future_or_stand text,
	standing_exp_date datetime,
	future_expected_compltn_date datetime,
	standing_occurs integer,
	stand_orig_occur integer,
	rfl_priority text,
	hv_hospitalist_yn text,
	prov_status text,
	order_priority text,
	stand_interval text,
	instantiated_time datetime,
	ordering_mode text,
	is_pending_ord_yn text,
	proc_start_time datetime,
	proc_ending_time datetime,
	id_of_replaced_order_proc_id bigint,
	patient_location text,
	login_department text,
	requested_provider_specialty text,
	reason_for_rferral text,
	num_visits_authorized_by_rfl integer,
	requested_department_specialty text
);
CREATE INDEX index_stride_order_proc_referrals_n_consults_order_proc_id ON stride_order_proc_referrals_n_consults(order_proc_id);
CREATE INDEX index_stride_order_proc_referrals_n_consults_pat_id ON stride_order_proc_referrals_n_consults(pat_id (16));
CREATE INDEX index_stride_order_proc_referrals_n_consults_pat_enc_csn_id ON stride_order_proc_referrals_n_consults(pat_enc_csn_id);
CREATE INDEX index_stride_order_proc_referrals_n_consults_proc_id ON stride_order_proc_referrals_n_consults(proc_id);


-- Encounter dates, types, department.  Lots of inpatient data
--	Header: Lower-case and remove " marks
CREATE TABLE stride_pat_enc
(
	pat_id text,
	pat_enc_csn_id bigint,
	contact_date datetime,
	enc_type text,
	department_name text,
	appt_status text,
	visit_type text,
	cancel_reason text,
	hosp_admdn_type text,
	surgical_service text,
	phone_reminder_status text,
	appt_time datetime,
	er_arrival_time datetime,
	hosp_admsn_time datetime,
	hosp_dischrg_time datetime,
	adm_for_surg_yn text,
	outgoing_call_yn text,
	is_walk_in_yn text,
	cancel_reason_cmt text,
	admission_confirmation_status text,
	discharge_confirmation_status text,
	inpatient_data_id bigint
);
CREATE INDEX index_stride_pat_enc_pat_id ON stride_pat_enc(pat_id (16));
CREATE INDEX index_stride_pat_enc_pat_enc_csn_id ON stride_pat_enc(pat_enc_csn_id);
CREATE INDEX index_stride_pat_enc_contact_date ON stride_pat_enc(contact_date);
CREATE INDEX index_stride_pat_enc_inpatient_data_id ON stride_pat_enc(inpatient_data_id);

-- Patient problem lists
--	Header: Lower-case and remove " marks
--	Remove comments with quote marks ("cartilage","gastritis",""Nonocclusive...","Stanford Psych...,"Depression/anxiety...) confounded with comma delimiters
CREATE TABLE stride_problem_list
(
	problem_list_id bigint,
	pat_id text,
	dx_id bigint,
	dx_name text,
	dx_group text,
	ref_bill_code text,
	description text,
	noted_date datetime,
	resolved_date datetime,
	problem_cmt text,
	chronic_yn text,
	principal_pl_yn text
);
CREATE INDEX index_stride_problem_list_problem_list_id ON stride_problem_list(problem_list_id);
CREATE INDEX index_stride_problem_list_pat_id ON stride_problem_list(pat_id (16));
CREATE INDEX index_stride_problem_list_dx_id ON stride_problem_list(dx_id);
CREATE INDEX index_stride_problem_list_dx_name ON stride_problem_list(dx_name (16));
CREATE INDEX index_stride_problem_list_noted_date ON stride_problem_list(noted_date);

ALTER TABLE stride_problem_list ADD COLUMN base_bill_code TEXT;
CREATE INDEX index_stride_problem_list_ref_bill_code ON stride_problem_list(ref_bill_code (16));
CREATE INDEX index_stride_problem_list_base_bill_code ON stride_problem_list(base_bill_code (16));


-- pat_enc_dx.csv -- Encounter diagnoses (may be multiple per encounter)
-- pat_enc_profee_dx_px.csv -- Encounter procedures and linked diagnosis and department
-- pat_enc_dept.csv -- Encounter department (redundant with pat_enc)


-- Hospital account encounter data
-- pat_enc_hsp_acct_cpt_codes.csv
-- pat_enc_hsp_acct_dx.csv
-- pat_enc_hsp_acct_icd_px.csv



-- ICD9 mapping
CREATE TABLE stride_icd9_cm
(
	cui	TEXT,
	ispref TEXT,
	aui	TEXT,
	tty	TEXT,
	code TEXT,
	str	TEXT,
	suppress	TEXT
);
CREATE INDEX index_stride_icd9_cm_code ON stride_icd9_cm(code (16));
