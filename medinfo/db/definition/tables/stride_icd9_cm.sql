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
