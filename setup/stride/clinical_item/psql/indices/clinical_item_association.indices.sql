-- Table: clinical_item_association

CREATE INDEX IF NOT EXISTS clinical_item_association_clinical_item_id
                            ON clinical_item_association(clinical_item_id, subsequent_item_id);
CREATE INDEX IF NOT EXISTS clinical_item_association_subsequent_item_id
                            ON clinical_item_association(subsequent_item_id, clinical_item_id);
