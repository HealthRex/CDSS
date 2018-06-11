-- Table: item_collection
-- Description: Track manually specified collections of clinical items and
--              their relative relationships. For example, pre-existing
--              order sets.

CREATE TABLE IF NOT EXISTS item_collection
(
    item_collection_id SERIAL NOT NULL,
    section VARCHAR(1024), -- Allow indexing values up to 400 characters
    name VARCHAR(1024) NOT NULL,
    description TEXT,
    external_id BIGINT, -- Map to order set protocol ID
    subgroup VARCHAR(1024), -- Map to order set "Smart Group"
    CONSTRAINT item_collection_pkey PRIMARY KEY (item_collection_id)
);
