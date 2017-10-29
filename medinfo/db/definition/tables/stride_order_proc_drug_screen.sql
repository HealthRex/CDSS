-- Drug Screen Results
-- 	Header row: Remove " marks and lower-case header lines
CREATE TABLE IF NOT EXISTS stride_order_proc_drug_screen
(
	order_proc_id BIGINT,
	pat_id TEXT,
	pat_enc_csn_id BIGINT,
	ordering_date TIMESTAMP,
	proc_id INTEGER,
	proc_code TEXT,
	description TEXT,
	quantity INTEGER,
	order_status_c TEXT,
	order_status TEXT,
	reason_for_cancellation TEXT,
	future_or_stand TEXT,
	standing_exp_date TIMESTAMP,
	future_expected_compltn_date TIMESTAMP,
	standing_occurs INTEGER,
	stand_orig_occur INTEGER,
	rfl_priority TEXT,
	order_priority TEXT,
	stand_interval TEXT,
	instantiated_time TIMESTAMP,
	ordering_mode TEXT,
	is_pending_ord_yn TEXT,
	proc_start_time TIMESTAMP,
	proc_end_time TIMESTAMP,
	id_of_replaced_order_proc_id BIGINT,
	patient_location TEXT,
	login_department TEXT,
	specimen_taken_time TIMESTAMP,
	specimen_recv_time TIMESTAMP,
	result_line INTEGER,
	component_id INTEGER,
	component_name TEXT,
	ord_value TEXT,
	ref_normal_vals TEXT
);
CREATE INDEX IF NOT EXISTS index_stride_order_proc_drug_screen_compkey ON stride_order_proc_drug_screen(order_proc_id, result_line);
CREATE INDEX IF NOT EXISTS index_stride_order_proc_drug_screen_pat_id ON stride_order_proc_drug_screen(SUBSTRING(pat_id, 1, 16));
CREATE INDEX IF NOT EXISTS index_stride_order_proc_drug_screen_pat_enc_csn_id ON stride_order_proc_drug_screen(pat_enc_csn_id);
CREATE INDEX IF NOT EXISTS index_stride_order_proc_drug_screen_component_id ON stride_order_proc_drug_screen(component_id);
