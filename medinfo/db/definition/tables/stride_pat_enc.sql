-- Encounter dates, types, department.  Lots of inpatient data
--	Header: Lower-case and remove " marks
CREATE TABLE stride_pat_enc
(
	pat_id text,
	pat_enc_csn_id bigint,
	contact_date timestamp,
	enc_type text,
	department_name text,
	appt_status text,
	visit_type text,
	cancel_reason text,
	hosp_admdn_type text,
	surgical_service text,
	phone_reminder_status text,
	appt_time timestamp,
	er_arrival_time timestamp,
	hosp_admsn_time timestamp,
	hosp_dischrg_time timestamp,
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

-- pat_enc_dx.csv -- Encounter diagnoses (may be multiple per encounter)
-- pat_enc_profee_dx_px.csv -- Encounter procedures and linked diagnosis and department
-- pat_enc_dept.csv -- Encounter department (redundant with pat_enc)

-- Hospital account encounter data
-- pat_enc_hsp_acct_cpt_codes.csv
-- pat_enc_hsp_acct_dx.csv
-- pat_enc_hsp_acct_icd_px.csv
