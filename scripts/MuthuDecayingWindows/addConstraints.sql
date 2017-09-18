-- ALTER TABLE patient_item MODIFY COLUMN patient_item_id BIGINT SIGNED NOT NULL AUTO_INCREMENT;
ALTER TABLE patient_item ADD CONSTRAINT patient_item_pkey PRIMARY KEY (patient_item_id);
ALTER TABLE patient_item ADD CONSTRAINT patient_item_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id);
CREATE INDEX index_patient_item_clinical_item_id_date ON patient_item(clinical_item_id, item_date); -- Strange that this is not implicitly created by foreign key constraint above?
-- ALTER TABLE patient_item ADD CONSTRAINT patient_item_patient_fkey FOREIGN KEY (patient_id) REFERENCES patient(patient_id);	-- No fixed patient (ID) table for now
CREATE INDEX index_patient_item_patient_id_date ON patient_item(patient_id, item_date);	-- Natural sorting option to order by patient, then in chronological order of clinical items
CREATE INDEX index_patient_item_external_id ON patient_item(external_id, clinical_item_id);

ALTER TABLE patient_item ADD COLUMN encounter_id BIGINT;	-- Option to track at the individual encounter level
CREATE INDEX index_patient_item_encounter_id_date ON patient_item(encounter_id, item_date);	-- Natural sorting option to order by patient encounter, then in chronological order of clinical items

-- ALTER IGNORE TABLE patient_item ADD UNIQUE INDEX patient_item_composite (patient_id, clinical_item_id, item_date);
ALTER TABLE patient_item ADD CONSTRAINT patient_item_composite UNIQUE (patient_id, clinical_item_id, item_date);
