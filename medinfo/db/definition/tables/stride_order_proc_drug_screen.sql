-- Drug Screen Results
-- 	Header row: Remove " marks and lower-case header lines
create table stride_order_proc_drug_screen
(
	order_proc_id bigint,
	pat_id text,
	pat_enc_csn_id bigint,
	ordering_date timestamp,
	proc_id integer,
	proc_code text,
	description text,
	quantity integer,
	order_status_c text,
	order_status text,
	reason_for_cancellation text,
	future_or_stand text,
	standing_exp_date timestamp,
	future_expected_compltn_date timestamp,
	standing_occurs integer,
	stand_orig_occur integer,
	rfl_priority text,
	order_priority text,
	stand_interval text,
	instantiated_time timestamp,
	ordering_mode text,
	is_pending_ord_yn text,
	proc_start_time timestamp,
	proc_end_time timestamp,
	id_of_replaced_order_proc_id bigint,
	patient_location text,
	login_department text,
	specimen_taken_time timestamp,
	specimen_recv_time timestamp,
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
