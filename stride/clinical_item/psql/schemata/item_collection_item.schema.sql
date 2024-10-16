-- Table: item_collection_item
-- Description: Individual items in each item collection.

CREATE TABLE IF NOT EXISTS item_collection_item
(
	item_collection_item_id SERIAL NOT NULL,
	item_collection_id BIGINT NOT NULL,
	clinical_item_id BIGINT,	-- Allow null for reference to non-existent items
	collection_type_id INTEGER,
	value DECIMAL(9,3),	-- Precision values, but allow decimals, not just integers
	priority INTEGER,
	comment TEXT,
  CONSTRAINT item_collection_item_pkey PRIMARY KEY (item_collection_item_id),
  CONSTRAINT item_collection_item_collection_fkey FOREIGN KEY (item_collection_id) REFERENCES item_collection(item_collection_id),
  CONSTRAINT item_collection_item_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id),
  CONSTRAINT item_collection_item_type_fkey FOREIGN KEY (collection_type_id) REFERENCES collection_type(collection_type_id)
);
