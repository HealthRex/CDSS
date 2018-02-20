-- ICD9 mapping
CREATE TABLE IF NOT EXISTS stride_icd9_cm
(
	cui	TEXT,
	ispref TEXT,
	aui	TEXT,
	tty	TEXT,
	code TEXT,
	str	TEXT,
	suppress	TEXT
);
CREATE INDEX IF NOT EXISTS index_stride_icd9_cm_code ON stride_icd9_cm(SUBSTRING(code, 1, 16));
