-- List of clinical item categories to identify source tables that clinical item data is extracted from
CREATE TABLE clinical_item_category
(
    clinical_item_category_id SERIAL NOT NULL,
    source_table TEXT NOT NULL,	-- Name of the source table being extracted from
    description TEXT
);
-- ALTER TABLE clinical_item_category MODIFY COLUMN clinical_item_category_id BIGINT SIGNED NOT NULL AUTO_INCREMENT;	-- Use signed primary keys to facilitate unit tests
ALTER TABLE clinical_item_category ADD CONSTRAINT clinical_item_category_pkey PRIMARY KEY (clinical_item_category_id);

-- Default to including all options in recommendations, but allow customizations to specify some for exclusion
ALTER TABLE clinical_item_category ADD COLUMN default_recommend INTEGER DEFAULT 1;
