-- Backup table for links overridden when merging clinical items that seem
-- related, but don't want to destroy the data completely
CREATE TABLE IF NOT EXISTS backup_link_patient_item
(
	backup_link_patient_item_id SERIAL NOT NULL,
	patient_item_id BIGINT NOT NULL,
	clinical_item_id BIGINT NOT NULL,
	CONSTRAINT backup_link_patient_item_pkey PRIMARY KEY (backup_link_patient_item_id),
	CONSTRAINT backup_link_patient_item_key UNIQUE (patient_item_id, clinical_item_id),
	CONSTRAINT backup_link_patient_item_patient_item_fkey FOREIGN KEY (patient_item_id) REFERENCES patient_item(patient_item_id),
	CONSTRAINT backup_link_patient_item_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id)
);
-- ALTER TABLE backup_link_patient_item MODIFY COLUMN backup_link_patient_item_id BIGINT SIGNED NOT NULL AUTO_INCREMENT;
-- ALTER TABLE backup_link_patient_item ADD CONSTRAINT backup_link_patient_item_pkey PRIMARY KEY (backup_link_patient_item_id);
-- ALTER TABLE backup_link_patient_item ADD CONSTRAINT backup_link_patient_item_key UNIQUE (patient_item_id, clinical_item_id);
-- ALTER TABLE backup_link_patient_item ADD CONSTRAINT backup_link_patient_item_patient_item_fkey FOREIGN KEY (patient_item_id) REFERENCES patient_item(patient_item_id);
-- ALTER TABLE backup_link_patient_item ADD CONSTRAINT backup_link_patient_item_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id);
