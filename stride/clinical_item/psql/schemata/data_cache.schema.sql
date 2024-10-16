-- Table: data_cache
-- Description: Store results of common queries which infrequently change.

CREATE TABLE IF NOT EXISTS data_cache
(
	data_cache_id	SERIAL	NOT NULL,
	data_key	VARCHAR(255)	NOT NULL,	-- VARCHAR fixed length to accomodate unique key index
	data_value	TEXT	NOT NULL,
	last_update	TIMESTAMP	NOT NULL,
  CONSTRAINT data_cache_pkey PRIMARY KEY (data_cache_id),
  CONSTRAINT data_cache_key UNIQUE (data_key)
);
