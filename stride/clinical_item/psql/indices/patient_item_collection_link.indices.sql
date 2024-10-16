-- Table: patient_item_collection_link

CREATE INDEX IF NOT EXISTS patient_item_collection_link_patient_item_id
                            ON patient_item_collection_link(patient_item_id);
CREATE INDEX IF NOT EXISTS patient_item_collection_link_item_collection_item_id
                            ON patient_item_collection_link(item_collection_item_id);
