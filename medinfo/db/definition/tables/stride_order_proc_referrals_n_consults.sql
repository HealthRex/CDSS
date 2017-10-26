-- Referrals and Consults, includes patient location and login department (lots of inpatient data too)
--	Header: Lower-case, remove " marks
--	Look for rfl_priority is not null and ordering_mode = 'Outpatient' to isolate relevant referrals
CREATE TABLE stride_order_proc_referrals_n_consults
(
	order_proc_id bigint,
	pat_id text,
	pat_enc_csn_id bigint,
	ordering_date timestamp,
	proc_id bigint,
	proc_code text,
	description text,
	quantity integer,
	order_status_c integer,
	order_status text,
	reason_for_cancellation text,
	future_or_stand text,
	standing_exp_date timestamp,
	future_expected_compltn_date timestamp,
	standing_occurs integer,
	stand_orig_occur integer,
	rfl_priority text,
	hv_hospitalist_yn text,
	prov_status text,
	order_priority text,
	stand_interval text,
	instantiated_time timestamp,
	ordering_mode text,
	is_pending_ord_yn text,
	proc_start_time timestamp,
	proc_ending_time timestamp,
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
