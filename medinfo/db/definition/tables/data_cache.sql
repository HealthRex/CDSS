-- Cache table to store results of common queries whose results infrequently
-- change
CREATE TABLE IF NOT EXISTS data_cache
(
	data_cache_id	SERIAL	NOT NULL,
	data_key	VARCHAR(255)	NOT NULL,	-- Must be VARCHAR fixed length to accomodate unique key index
	data_value	TEXT	NOT NULL,
	last_update	TIMESTAMP	NOT NULL,
	CONSTRAINT data_cache_pkey PRIMARY KEY (data_cache_id),
	CONSTRAINT data_cache_key UNIQUE (data_key)
);
-- ALTER TABLE data_cache MODIFY COLUMN data_cache_id BIGINT SIGNED NOT NULL AUTO_INCREMENT;
-- ALTER TABLE data_cache ADD CONSTRAINT data_cache_pkey PRIMARY KEY (data_cache_id);
-- ALTER TABLE data_cache ADD CONSTRAINT data_cache_key UNIQUE (data_key);
