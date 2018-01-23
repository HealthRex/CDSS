-- Referrals and Consults, includes patient location and login department (lots of inpatient data too)
--	Header: Lower-case, remove " marks
--	Look for rfl_priority is not null and ordering_mode = 'Outpatient' to isolate relevant referrals
CREATE TABLE IF NOT EXISTS stride_order_proc_referrals_n_consults
(
	order_proc_id BIGINT,
	pat_id TEXT,
	pat_enc_csn_id BIGINT,
	ordering_date TIMESTAMP,
	proc_id BIGINT,
	proc_code TEXT,
	description TEXT,
	quantity INTEGER,
	order_status_c INTEGER,
	order_status TEXT,
	reason_for_cancellation TEXT,
	future_or_stand TEXT,
	standing_exp_date TIMESTAMP,
	future_expected_compltn_date TIMESTAMP,
	standing_occurs INTEGER,
	stand_orig_occur INTEGER,
	rfl_priority TEXT,
	hv_hospitalist_yn TEXT,
	prov_status TEXT,
	order_priority TEXT,
	stand_interval TEXT,
	instantiated_time TIMESTAMP,
	ordering_mode TEXT,
	is_pending_ord_yn TEXT,
	proc_start_time TIMESTAMP,
	proc_ending_time TIMESTAMP,
	id_of_replaced_order_proc_id BIGINT,
	patient_location TEXT,
	login_department TEXT,
	requested_provider_specialty TEXT,
	reason_for_rferral TEXT,
	num_visits_authorized_by_rfl INTEGER,
	requested_department_specialty TEXT
);
CREATE INDEX IF NOT EXISTS index_stride_order_proc_referrals_n_consults_order_proc_id ON stride_order_proc_referrals_n_consults(order_proc_id);
CREATE INDEX IF NOT EXISTS index_stride_order_proc_referrals_n_consults_pat_id ON stride_order_proc_referrals_n_consults(SUBSTRING(pat_id, 1 ,16));
CREATE INDEX IF NOT EXISTS index_stride_order_proc_referrals_n_consults_pat_enc_csn_id ON stride_order_proc_referrals_n_consults(pat_enc_csn_id);
CREATE INDEX IF NOT EXISTS index_stride_order_proc_referrals_n_consults_proc_id ON stride_order_proc_referrals_n_consults(proc_id);
