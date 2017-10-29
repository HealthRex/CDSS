-- Tables to track manually specified collections of clinical items and their relative relationships
-- For example, use to track pre-existing order sets
CREATE TABLE IF NOT EXISTS item_collection
(
	item_collection_id SERIAL NOT NULL,
    section VARCHAR(255) NOT NULL,	-- VARCHAR to allow indexing
    name VARCHAR(255) NOT NULL,	-- VARCHAR to allow indexing
    description TEXT,
		CONSTRAINT item_collection_pkey PRIMARY KEY (item_collection_id)
);
-- ALTER TABLE item_collection MODIFY COLUMN item_collection_id BIGINT SIGNED NOT NULL AUTO_INCREMENT;
-- ALTER TABLE item_collection ADD CONSTRAINT item_collection_pkey PRIMARY KEY (item_collection_id);

ALTER TABLE item_collection ADD COLUMN IF NOT EXISTS external_id BIGINT;		-- Map to order set protocol ID
--ALTER TABLE item_collection RENAME COLUMN name TO name; 		-- Map to order set protocol name

DO $$
BEGIN
	IF EXISTS (
		SELECT column_name
		FROM information_schema.columns
		WHERE table_name = 'item_collection' AND column_name = 'subject'
	)
	THEN
		ALTER TABLE item_collection RENAME COLUMN subject TO section;	-- Map to order set section_name
	END IF;
END$$;

ALTER TABLE item_collection ADD COLUMN IF NOT EXISTS subgroup VARCHAR(255);	-- Map to order set "Smart Group"

-- Longer expected length to allow for long protocol names that are up to 400 characters
ALTER TABLE item_collection ALTER COLUMN section DROP NOT NULL;
ALTER TABLE item_collection ALTER COLUMN section TYPE VARCHAR(1024);
ALTER TABLE item_collection ALTER COLUMN subgroup TYPE VARCHAR(1024);
ALTER TABLE item_collection ALTER COLUMN name TYPE VARCHAR(1024);
