-- Mapping Table for Medications to Common Active Ingredients
CREATE TABLE IF NOT EXISTS stride_mapped_meds
(
	medication_id INTEGER,
	medication_name TEXT,
	rxcui INTEGER,
	active_ingredient TEXT
);
CREATE INDEX IF NOT EXISTS index_stride_mapped_meds_medication_id ON stride_mapped_meds(medication_id);
ALTER TABLE stride_mapped_meds ADD COLUMN IF NOT EXISTS analysis_status INTEGER DEFAULT 1;
ALTER TABLE stride_mapped_meds ADD COLUMN IF NOT EXISTS morphine_po_equivalent FLOAT;
