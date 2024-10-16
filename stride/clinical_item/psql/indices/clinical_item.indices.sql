-- Table: clinical_item

CREATE INDEX IF NOT EXISTS index_clinical_item_clinical_item_category
                            ON clinical_item(clinical_item_category_id);
CREATE INDEX IF NOT EXISTS index_clinical_item_external_id
                            ON clinical_item(external_id);
