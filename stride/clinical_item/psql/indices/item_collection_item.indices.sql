-- Table: item_collection_item

CREATE INDEX IF NOT EXISTS item_collection_item_collection_id
                            ON item_collection_item(item_collection_id);
CREATE INDEX IF NOT EXISTS item_collection_item_clinical_item_id
                            ON item_collection_item(clinical_item_id);
CREATE INDEX IF NOT EXISTS item_collection_item_type_id
                            ON item_collection_item(collection_type_id);
