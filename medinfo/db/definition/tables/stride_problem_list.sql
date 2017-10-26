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
	noted_date timestamp,
	resolved_date timestamp,
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
