-- Encounter dates, types, department.  Lots of inpatient data
--	Header: Lower-case and remove " marks
CREATE TABLE IF NOT EXISTS stride_pat_enc
(
	pat_id TEXT,
	pat_enc_csn_id BIGINT,
	contact_date TIMESTAMP,
	enc_type TEXT,
	department_name TEXT,
	appt_status TEXT,
	visit_type TEXT,
	cancel_reason TEXT,
	hosp_admdn_type TEXT,
	surgical_service TEXT,
	phone_reminder_status TEXT,
	appt_time TIMESTAMP,
	er_arrival_time TIMESTAMP,
	hosp_admsn_time TIMESTAMP,
	hosp_dischrg_time TIMESTAMP,
	adm_for_surg_yn TEXT,
	outgoing_call_yn TEXT,
	is_walk_in_yn TEXT,
	cancel_reason_cmt TEXT,
	admission_confirmation_status TEXT,
	discharge_confirmation_status TEXT,
	inpatient_data_id BIGINT
);
CREATE INDEX IF NOT EXISTS index_stride_pat_enc_pat_id ON stride_pat_enc(SUBSTRING(pat_id, 1, 16));
CREATE INDEX IF NOT EXISTS index_stride_pat_enc_pat_enc_csn_id ON stride_pat_enc(pat_enc_csn_id);
CREATE INDEX IF NOT EXISTS index_stride_pat_enc_contact_date ON stride_pat_enc(contact_date);
CREATE INDEX IF NOT EXISTS index_stride_pat_enc_inpatient_data_id ON stride_pat_enc(inpatient_data_id);

-- pat_enc_dx.csv -- Encounter diagnoses (may be multiple per encounter)
-- pat_enc_profee_dx_px.csv -- Encounter procedures and linked diagnosis and department
-- pat_enc_dept.csv -- Encounter department (redundant with pat_enc)

-- Hospital account encounter data
-- pat_enc_hsp_acct_cpt_codes.csv
-- pat_enc_hsp_acct_dx.csv
-- pat_enc_hsp_acct_icd_px.csv
