-- Table: stride_mapped_meds
-- Description: Medication mapped to RxNorm Concept Unique Identifier (RxCUI).
-- Original Files:
--	* Chen_Mapped_Meds_5Yr.csv.gz
--  * Chen_Mapped_Meds_Yrs6_8.patchHeader.csv.gz
-- Clean Files:
--	* stride_medication_2008_2014.csv.gz
--  * stride_medication_2014_2017.patchHeader.csv.gz
-- CSV Fields:
--  * "MEDICATION_ID" (e.g. 127722)
--  * "NAME" (e.g. "MAGNESIUM OXIDE 400 MG PO CAPS")
--  * "RXCUI" (e.g. "733")
--  * "GENERIC_NAME" (e.g. "LORazepam 1 mg tablet")
--  * active_ingredient (e.g. azatadine) (this field imputed via RxNorm API)

CREATE TABLE IF NOT EXISTS stride_mapped_meds
(
  medication_id INTEGER,
  name TEXT,
  rxcui INTEGER,
  generic_name TEXT,
  active_ingredient TEXT
);
