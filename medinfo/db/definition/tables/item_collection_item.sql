CREATE TABLE IF NOT EXISTS item_collection_item
(
	item_collection_item_id SERIAL NOT NULL,
	item_collection_id BIGINT NOT NULL,
	clinical_item_id BIGINT,	-- Allow null for references to actions not available as an existing clinical_item
	collection_type_id INTEGER,
	value DECIMAL(9,3),	-- Precision values, but allow decimal values, not just integers
	priority INTEGER,
	comment TEXT,
	CONSTRAINT item_collection_item_pkey PRIMARY KEY (item_collection_item_id),
	CONSTRAINT item_collection_item_collection_fkey FOREIGN KEY (item_collection_id) REFERENCES item_collection(item_collection_id)
);
-- ALTER TABLE item_collection_item MODIFY COLUMN item_collection_item_id BIGINT SIGNED NOT NULL AUTO_INCREMENT;
-- ALTER TABLE item_collection_item ADD CONSTRAINT item_collection_item_pkey PRIMARY KEY (item_collection_item_id);
-- ALTER TABLE item_collection_item ADD CONSTRAINT item_collection_item_collection_fkey FOREIGN KEY (item_collection_id) REFERENCES item_collection(item_collection_id);
CREATE INDEX IF NOT EXISTS item_collection_item_collection_id ON item_collection_item(item_collection_id);


-- ALTER TABLE item_collection_item ADD CONSTRAINT item_collection_item_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id);
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT constraint_name
    FROM information_schema.table_constraints
    WHERE table_name = 'item_collection_item' AND constraint_name = 'item_collection_item_item_fkey'
  )
  THEN
    ALTER TABLE item_collection_item ADD CONSTRAINT item_collection_item_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id);
  END IF;
END$$;

CREATE INDEX IF NOT EXISTS item_collection_item_clinical_item_id ON item_collection_item(clinical_item_id);

-- ALTER TABLE item_collection_item ADD CONSTRAINT item_collection_item_type_fkey FOREIGN KEY (collection_type_id) REFERENCES collection_type(collection_type_id);
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT constraint_name
    FROM information_schema.table_constraints
    WHERE table_name = 'item_collection_item' AND constraint_name = 'item_collection_item_type_fkey'
  )
  THEN
    ALTER TABLE item_collection_item ADD CONSTRAINT item_collection_item_type_fkey FOREIGN KEY (collection_type_id) REFERENCES collection_type(collection_type_id);
  END IF;
END$$;
--CREATE INDEX item_collection_item_type_id ON item_collection_item(collection_type_id);
