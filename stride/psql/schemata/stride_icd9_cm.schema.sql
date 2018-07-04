-- Table: stride_icd9_cm
-- Description: ICD-9 CM (International Classification of Diseases, Ninth
--              Revision, Clinical Modification)
-- Original Files:
--  * export_ICD-9-CM_2013.csv.gz
-- Clean Files:
--  * stride_icd9_cm_2013.csv.gz
-- CSV Fields:
--  * CUI (concept unique identifier, e.g. C0005684)
--  * ISPREF (is preferred label for disease, e.g. Y)
--  * AUI (atom unique identifier, e.g. A8343293)
--  * TTY (term type, e.g. PT = preferred term, HT = hierarchical term)
--  * CODE (e.g. 010.86)
--  * STR (e.g. "2nd deg burn upper arm")
--  * SUPPRESS (e.g. Y)

CREATE TABLE IF NOT EXISTS stride_icd9_cm
(
  cui TEXT,
  ispref TEXT,
  aui TEXT,
  tty TEXT,
  code TEXT,
  str TEXT,
  suppress TEXT
);
