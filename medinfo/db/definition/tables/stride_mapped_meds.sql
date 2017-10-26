-- Mapping Table for Medications to Common Active Ingredients
create table stride_mapped_meds
(
	medication_id integer,
	medication_name text,
	rxcui integer,
	active_ingredient text
);
CREATE INDEX index_stride_mapped_meds_medication_id ON stride_mapped_meds(medication_id);
ALTER TABLE stride_mapped_meds ADD COLUMN analysis_status INTEGER DEFAULT 1;
ALTER TABLE stride_mapped_meds ADD COLUMN morphine_po_equivalent FLOAT;
