-- Table: patient_item

CREATE INDEX IF NOT EXISTS index_patient_item_clinical_item_id_date
                            ON patient_item(clinical_item_id, item_date);
-- Natural to sort by patient, then in chronological order of clinical items
CREATE INDEX IF NOT EXISTS index_patient_item_patient_id_date
                            ON patient_item(patient_id, item_date);
CREATE INDEX IF NOT EXISTS index_patient_item_external_id
                            ON patient_item(external_id, clinical_item_id);
-- Natural to sort by patient encounter, then chronologically
CREATE INDEX IF NOT EXISTS index_patient_item_encounter_id_date
                            ON patient_item(encounter_id, item_date);
CREATE INDEX IF NOT EXISTS index_patient_item_id_num_value
                            ON patient_item(num_value);
CREATE INDEX IF NOT EXISTS index_patient_item_text_value
                            ON patient_item(text_value);
