-- Patient problem lists
--	Header: Lower-case and remove " marks
--	Remove comments with quote marks ("cartilage","gastritis",""Nonocclusive...","Stanford Psych...,"Depression/anxiety...) confounded with comma delimiters
CREATE TABLE IF NOT EXISTS stride_problem_list
(
	problem_list_id BIGINT,
	pat_id TEXT,
	dx_id BIGINT,
	dx_name TEXT,
	dx_group TEXT,
	ref_bill_code TEXT,
	description TEXT,
	noted_date TIMESTAMP,
	resolved_date TIMESTAMP,
	problem_cmt TEXT,
	chronic_yn TEXT,
	principal_pl_yn TEXT
);
CREATE INDEX IF NOT EXISTS index_stride_problem_list_problem_list_id ON stride_problem_list(problem_list_id);
CREATE INDEX IF NOT EXISTS index_stride_problem_list_pat_id ON stride_problem_list(SUBSTRING(pat_id, 1, 16));
CREATE INDEX IF NOT EXISTS index_stride_problem_list_dx_id ON stride_problem_list(dx_id);
CREATE INDEX IF NOT EXISTS index_stride_problem_list_dx_name ON stride_problem_list(SUBSTRING(dx_name, 1, 16));
CREATE INDEX IF NOT EXISTS index_stride_problem_list_noted_date ON stride_problem_list(noted_date);

ALTER TABLE stride_problem_list ADD COLUMN IF NOT EXISTS base_bill_code TEXT;
CREATE INDEX IF NOT EXISTS index_stride_problem_list_ref_bill_code ON stride_problem_list(SUBSTRING(ref_bill_code, 1, 16));
CREATE INDEX IF NOT EXISTS index_stride_problem_list_base_bill_code ON stride_problem_list(SUBSTRING(base_bill_code, 1, 16));
