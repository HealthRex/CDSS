-- ------------------------------------------------- --
-- Computerized Physician Order Entry Stats Analysis --
-- ------------------------------------------------- --

-- List of clinical item categories to identify source tables that clinical item data is extracted from
CREATE TABLE clinical_item_category
(
    clinical_item_category_id SERIAL NOT NULL,
    source_table TEXT NOT NULL,	-- Name of the source table being extracted from
    description TEXT
);
-- ALTER TABLE clinical_item_category MODIFY COLUMN clinical_item_category_id BIGINT SIGNED NOT NULL AUTO_INCREMENT;	-- Use signed primary keys to facilitate unit tests
ALTER TABLE clinical_item_category ADD CONSTRAINT clinical_item_category_pkey PRIMARY KEY (clinical_item_category_id);

-- List of "clinical items" that will be included in analyses
--	Defines the "vocabulary" of "words" that can form part of clinical "documents"
--	At first, just use clinical orders, but eventually roll in other item types
--	to inform clinical contexts, such as problem list items, lab results, keywords extracted from notes, etc.
CREATE TABLE clinical_item
(
    clinical_item_id SERIAL NOT NULL,
    clinical_item_category_id BIGINT NOT NULL,
	external_id BIGINT,	-- ID number used in externally imported data.  May not always be available or unique
    name TEXT NOT NULL,
    description TEXT
);
-- ALTER TABLE clinical_item MODIFY COLUMN clinical_item_id BIGINT SIGNED NOT NULL AUTO_INCREMENT;
ALTER TABLE clinical_item ADD CONSTRAINT clinical_item_pkey PRIMARY KEY (clinical_item_id);
ALTER TABLE clinical_item ADD CONSTRAINT clinical_item_category_fkey FOREIGN KEY (clinical_item_category_id) REFERENCES clinical_item_category(clinical_item_category_id);
CREATE INDEX index_clinical_item_clinical_item_category ON clinical_item(clinical_item_category_id);
CREATE INDEX index_clinical_item_external_id ON clinical_item(external_id);

-- Clinical items linked to actual applications to individual patients, additional keyed by the date
--	of the item event (e.g., order entry or lab result)
CREATE TABLE patient_item
(
    patient_item_id SERIAL NOT NULL,
	external_id BIGINT,	-- ID number used from externally imported table
    patient_id BIGINT NOT NULL,
    clinical_item_id BIGINT NOT NULL,
    item_date TIMESTAMP NOT NULL,	-- Date that the clinical item occurred
    analyze_date TIMESTAMP			-- Date that the item was analyzed for association pre-computing. Should redesign this to separate table to allow for multiple models trained on same source data
);
-- ALTER TABLE patient_item MODIFY COLUMN patient_item_id BIGINT SIGNED NOT NULL AUTO_INCREMENT;
ALTER TABLE patient_item ADD CONSTRAINT patient_item_pkey PRIMARY KEY (patient_item_id);
ALTER TABLE patient_item ADD CONSTRAINT patient_item_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id);
CREATE INDEX index_patient_item_clinical_item_id_date ON patient_item(clinical_item_id, item_date); -- Strange that this is not implicitly created by foreign key constraint above?
-- ALTER TABLE patient_item ADD CONSTRAINT patient_item_patient_fkey FOREIGN KEY (patient_id) REFERENCES patient(patient_id);	-- No fixed patient (ID) table for now
CREATE INDEX index_patient_item_patient_id_date ON patient_item(patient_id, item_date);	-- Natural sorting option to order by patient, then in chronological order of clinical items
CREATE INDEX index_patient_item_external_id ON patient_item(external_id, clinical_item_id);

ALTER TABLE patient_item ADD COLUMN encounter_id BIGINT;	-- Option to track at the individual encounter level
CREATE INDEX index_patient_item_encounter_id_date ON patient_item(encounter_id, item_date);	-- Natural sorting option to order by patient encounter, then in chronological order of clinical items

-- ALTER IGNORE TABLE patient_item ADD UNIQUE INDEX patient_item_composite (patient_id, clinical_item_id, item_date);
ALTER TABLE patient_item ADD CONSTRAINT patient_item_composite UNIQUE (patient_id, clinical_item_id, item_date);

ALTER TABLE patient_item ADD COLUMN source_id BIGINT;    -- Option to store reference to origin ID (e.g., order_proc_id to enable links between orders and lab results)
ALTER TABLE patient_item ADD COLUMN num_value DOUBLE PRECISION;	-- Option to store numerical data
ALTER TABLE patient_item ADD COLUMN text_value TEXT;	-- Option to store text/comment data
-- CREATE INDEX index_patient_item_id_num_value ON patient_item(num_value);
-- CREATE INDEX index_patient_item_text_value ON patient_item(text_value);



-- Core stat tracking table, record various association statistics,
--	mostly counting up the number of times one item / order follows another	within any patient's course.
-- DROP TABLE clinical_item_association;    -- If need to recreate from scratch with revised column types
CREATE TABLE clinical_item_association
(
    clinical_item_association_id SERIAL NOT NULL,
    clinical_item_id BIGINT NOT NULL,
    subsequent_item_id BIGINT NOT NULL
);
-- ALTER TABLE clinical_item_association MODIFY COLUMN clinical_item_association_id BIGINT SIGNED NOT NULL AUTO_INCREMENT;
ALTER TABLE clinical_item_association ADD CONSTRAINT clinical_item_association_pkey PRIMARY KEY (clinical_item_association_id);
ALTER TABLE clinical_item_association ADD CONSTRAINT clinical_item_association_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id);
ALTER TABLE clinical_item_association ADD CONSTRAINT clinical_item_association_subsequent_item_fkey FOREIGN KEY (subsequent_item_id) REFERENCES clinical_item(clinical_item_id);
ALTER TABLE clinical_item_association ADD CONSTRAINT clinical_item_association_composite_key UNIQUE (clinical_item_id, subsequent_item_id);
CREATE INDEX clinical_item_association_clinical_item_id ON clinical_item_association(clinical_item_id, subsequent_item_id);
CREATE INDEX clinical_item_association_subsequent_item_id ON clinical_item_association(subsequent_item_id, clinical_item_id);

-- Basic type of stats, counting up cooccurences.  Column names encoded by duration of seconds the counting timeframe represents
-- Use DOUBLE PRECISION / floating point values to allow for weighted pseudo-counts
ALTER TABLE clinical_item_association ADD COLUMN count_0 DOUBLE PRECISION DEFAULT 0;	-- Number of times the subsequent item follows the primary clinical item within 0 seconds of event TIMESTAMP
ALTER TABLE clinical_item_association ADD COLUMN count_3600 DOUBLE PRECISION DEFAULT 0;	-- 1 hour
ALTER TABLE clinical_item_association ADD COLUMN count_7200 DOUBLE PRECISION DEFAULT 0;	-- 2 hours
ALTER TABLE clinical_item_association ADD COLUMN count_21600 DOUBLE PRECISION DEFAULT 0;	-- 6 hours
ALTER TABLE clinical_item_association ADD COLUMN count_43200 DOUBLE PRECISION DEFAULT 0; -- 12 hours
ALTER TABLE clinical_item_association ADD COLUMN count_86400 DOUBLE PRECISION DEFAULT 0;  -- 1 day
ALTER TABLE clinical_item_association ADD COLUMN count_172800 DOUBLE PRECISION DEFAULT 0; -- 2 days
ALTER TABLE clinical_item_association ADD COLUMN count_345600 DOUBLE PRECISION DEFAULT 0; -- 4 days
ALTER TABLE clinical_item_association ADD COLUMN count_604800 DOUBLE PRECISION DEFAULT 0; -- 1 week
ALTER TABLE clinical_item_association ADD COLUMN count_1209600 DOUBLE PRECISION DEFAULT 0; -- 2 weeks
ALTER TABLE clinical_item_association ADD COLUMN count_2592000 DOUBLE PRECISION DEFAULT 0; -- 1 month (30 days)
ALTER TABLE clinical_item_association ADD COLUMN count_7776000 DOUBLE PRECISION DEFAULT 0; -- 3 months
ALTER TABLE clinical_item_association ADD COLUMN count_15552000 DOUBLE PRECISION DEFAULT 0; -- 6 months
ALTER TABLE clinical_item_association ADD COLUMN count_31536000 DOUBLE PRECISION DEFAULT 0; -- 1 year (365 days)
ALTER TABLE clinical_item_association ADD COLUMN count_63072000 DOUBLE PRECISION DEFAULT 0; -- 2 years
ALTER TABLE clinical_item_association ADD COLUMN count_126144000 DOUBLE PRECISION DEFAULT 0; -- 4 years
ALTER TABLE clinical_item_association ADD COLUMN count_any DOUBLE PRECISION DEFAULT 0; -- Number of times the subsequent item follows within any period of recorded time
ALTER TABLE clinical_item_association ADD COLUMN time_diff_sum DOUBLE PRECISION DEFAULT 0; -- Sum of differences in event times of subsequent vs. primary items, expressed in seconds.  This divided by count_any reflects the average time difference
ALTER TABLE clinical_item_association ADD COLUMN time_diff_sum_squares DOUBLE PRECISION DEFAULT 0; -- Sum of squared difference values as above.  Can be used with above to assess variance of time differences (var = (SumSquares - Sum^2) / count_any)

-- Similar stats, but don't count duplicates within the timeframes, only incrementing counts for the first subsequent item encountered
-- Expand time windows for counting. Should always meet or exceed dataset timeframe so easy to upscale without full recalc
-- More stats, but now count simply by the existence of a patient with the combination and only count once per patient
ALTER TABLE clinical_item_association ADD COLUMN patient_count_0 DOUBLE PRECISION DEFAULT 0;
ALTER TABLE clinical_item_association ADD COLUMN patient_count_3600 DOUBLE PRECISION DEFAULT 0;	-- 1 hour
ALTER TABLE clinical_item_association ADD COLUMN patient_count_7200 DOUBLE PRECISION DEFAULT 0;	-- 2 hours
ALTER TABLE clinical_item_association ADD COLUMN patient_count_21600 DOUBLE PRECISION DEFAULT 0;	-- 6 hours
ALTER TABLE clinical_item_association ADD COLUMN patient_count_43200 DOUBLE PRECISION DEFAULT 0; -- 12 hours
ALTER TABLE clinical_item_association ADD COLUMN patient_count_86400 DOUBLE PRECISION DEFAULT 0;  -- 1 day
ALTER TABLE clinical_item_association ADD COLUMN patient_count_172800 DOUBLE PRECISION DEFAULT 0; -- 2 days
ALTER TABLE clinical_item_association ADD COLUMN patient_count_345600 DOUBLE PRECISION DEFAULT 0; -- 4 days
ALTER TABLE clinical_item_association ADD COLUMN patient_count_604800 DOUBLE PRECISION DEFAULT 0; -- 1 week
ALTER TABLE clinical_item_association ADD COLUMN patient_count_1209600 DOUBLE PRECISION DEFAULT 0; -- 2 weeks
ALTER TABLE clinical_item_association ADD COLUMN patient_count_2592000 DOUBLE PRECISION DEFAULT 0; -- 1 month (30 days)
ALTER TABLE clinical_item_association ADD COLUMN patient_count_7776000 DOUBLE PRECISION DEFAULT 0; -- 3 months
ALTER TABLE clinical_item_association ADD COLUMN patient_count_15552000 DOUBLE PRECISION DEFAULT 0; -- 6 months
ALTER TABLE clinical_item_association ADD COLUMN patient_count_31536000 DOUBLE PRECISION DEFAULT 0; -- 1 year (365 days)
ALTER TABLE clinical_item_association ADD COLUMN patient_count_63072000 DOUBLE PRECISION DEFAULT 0; -- 2 years
ALTER TABLE clinical_item_association ADD COLUMN patient_count_126144000 DOUBLE PRECISION DEFAULT 0; -- 4 years
ALTER TABLE clinical_item_association ADD COLUMN patient_count_any DOUBLE PRECISION DEFAULT 0;
ALTER TABLE clinical_item_association ADD COLUMN patient_time_diff_sum DOUBLE PRECISION DEFAULT 0;
ALTER TABLE clinical_item_association ADD COLUMN patient_time_diff_sum_squares DOUBLE PRECISION DEFAULT 0;

-- More stats, but now count by the existence of a patient encounter with the combination and only count once per encounter
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_0 DOUBLE PRECISION DEFAULT 0;
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_3600 DOUBLE PRECISION DEFAULT 0;	-- 1 hour
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_7200 DOUBLE PRECISION DEFAULT 0;	-- 2 hours
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_21600 DOUBLE PRECISION DEFAULT 0;	-- 6 hours
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_43200 DOUBLE PRECISION DEFAULT 0; -- 12 hours
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_86400 DOUBLE PRECISION DEFAULT 0;  -- 1 day
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_172800 DOUBLE PRECISION DEFAULT 0; -- 2 days
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_345600 DOUBLE PRECISION DEFAULT 0; -- 4 days
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_604800 DOUBLE PRECISION DEFAULT 0; -- 1 week
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_1209600 DOUBLE PRECISION DEFAULT 0; -- 2 weeks
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_2592000 DOUBLE PRECISION DEFAULT 0; -- 1 month (30 days)
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_7776000 DOUBLE PRECISION DEFAULT 0; -- 3 months
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_15552000 DOUBLE PRECISION DEFAULT 0; -- 6 months
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_31536000 DOUBLE PRECISION DEFAULT 0; -- 1 year (365 days)
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_63072000 DOUBLE PRECISION DEFAULT 0; -- 2 years
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_126144000 DOUBLE PRECISION DEFAULT 0; -- 4 years
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_any DOUBLE PRECISION DEFAULT 0;
ALTER TABLE clinical_item_association ADD COLUMN encounter_time_diff_sum DOUBLE PRECISION DEFAULT 0;
ALTER TABLE clinical_item_association ADD COLUMN encounter_time_diff_sum_squares DOUBLE PRECISION DEFAULT 0;

-- Default to including all options in recommendations, but allow customizations to specify some for exclusion
ALTER TABLE clinical_item_category ADD COLUMN default_recommend INTEGER DEFAULT 1;	
ALTER TABLE clinical_item ADD COLUMN default_recommend INTEGER DEFAULT 1;	

-- Denormalize child record count to facilitate rapid query times
ALTER TABLE clinical_item ADD COLUMN item_count INTEGER;
ALTER TABLE clinical_item ADD COLUMN patient_count INTEGER;
ALTER TABLE clinical_item ADD COLUMN encounter_count INTEGER;
-- Drop the integer counts and use floating point instead to allow for weighted pseudo-counts
ALTER TABLE clinical_item DROP COLUMN item_count;
ALTER TABLE clinical_item DROP COLUMN patient_count;
ALTER TABLE clinical_item DROP COLUMN encounter_count;

ALTER TABLE clinical_item ADD COLUMN item_count DOUBLE PRECISION;
ALTER TABLE clinical_item ADD COLUMN patient_count DOUBLE PRECISION;
ALTER TABLE clinical_item ADD COLUMN encounter_count DOUBLE PRECISION;

-- Allow specification of items that should or should not bother to be included in association analysis
ALTER TABLE clinical_item ADD COLUMN analysis_status INTEGER DEFAULT 1;

-- Highlight items that may be of interest as outcome measures
ALTER TABLE clinical_item ADD COLUMN outcome_interest INTEGER DEFAULT 0;

-- Stats on order (lab) results to help track distributions
CREATE TABLE order_result_stat
(
	order_result_stat_id SERIAL NOT NULL,
	base_name TEXT NOT NULL,
	value_count INTEGER DEFAULT 0,
	value_sum DOUBLE PRECISION DEFAULT 0,
	value_sum_squares DOUBLE PRECISION DEFAULT 0
);
ALTER TABLE order_result_stat ADD CONSTRAINT order_result_stat_pkey PRIMARY KEY (order_result_stat_id);
ALTER TABLE order_result_stat ADD CONSTRAINT order_result_stat_key UNIQUE (base_name);

ALTER TABLE order_result_stat ADD COLUMN max_result_flag TEXT;
ALTER TABLE order_result_stat ADD COLUMN max_result_in_range TEXT;

-- Cache table to store results of common queries whose results infrequently change
CREATE TABLE data_cache
(
	data_cache_id	SERIAL	NOT NULL,
	data_key	VARCHAR(255)	NOT NULL,	-- Must be VARCHAR fixed length to accomodate unique key index
	data_value	TEXT	NOT NULL,
	last_update	TIMESTAMP	NOT NULL
);
-- ALTER TABLE data_cache MODIFY COLUMN data_cache_id BIGINT SIGNED NOT NULL AUTO_INCREMENT;
ALTER TABLE data_cache ADD CONSTRAINT data_cache_pkey PRIMARY KEY (data_cache_id);
ALTER TABLE data_cache ADD CONSTRAINT data_cache_key UNIQUE (data_key);


-- Backup table for links overridden when merging clinical items that seem related, but don't want to destroy the data completely
CREATE TABLE backup_link_patient_item
(
	backup_link_patient_item_id SERIAL NOT NULL,
	patient_item_id BIGINT NOT NULL,
	clinical_item_id BIGINT NOT NULL
);
-- ALTER TABLE backup_link_patient_item MODIFY COLUMN backup_link_patient_item_id BIGINT SIGNED NOT NULL AUTO_INCREMENT;
ALTER TABLE backup_link_patient_item ADD CONSTRAINT backup_link_patient_item_pkey PRIMARY KEY (backup_link_patient_item_id);
ALTER TABLE backup_link_patient_item ADD CONSTRAINT backup_link_patient_item_key UNIQUE (patient_item_id, clinical_item_id);
ALTER TABLE backup_link_patient_item ADD CONSTRAINT backup_link_patient_item_patient_item_fkey FOREIGN KEY (patient_item_id) REFERENCES patient_item(patient_item_id);
ALTER TABLE backup_link_patient_item ADD CONSTRAINT backup_link_patient_item_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id);


-- Table to track links between clinical items that should not have association stats calculated
--	probably because they have a specific firm relation (e.g., component clinical item of a composite one)
CREATE TABLE clinical_item_link
(
	clinical_item_link_id SERIAL NOT NULL,
	clinical_item_id BIGINT NOT NULL,
	linked_item_id BIGINT NOT NULL
);
-- ALTER TABLE clinical_item_link MODIFY COLUMN clinical_item_link_id BIGINT SIGNED NOT NULL AUTO_INCREMENT;
ALTER TABLE clinical_item_link ADD CONSTRAINT clinical_item_link_pkey PRIMARY KEY (clinical_item_link_id);
ALTER TABLE clinical_item_link ADD CONSTRAINT clinical_item_link_key UNIQUE (clinical_item_id, linked_item_id);
ALTER TABLE clinical_item_link ADD CONSTRAINT clinical_item_link_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id);
ALTER TABLE clinical_item_link ADD CONSTRAINT clinical_item_link_linked_item_fkey FOREIGN KEY (linked_item_id) REFERENCES clinical_item(clinical_item_id);




-- Tables to track manually specified collections of clinical items and their relative relationships
-- For example, use to track pre-existing order sets
CREATE TABLE item_collection
(
	item_collection_id SERIAL NOT NULL,
    subject VARCHAR(255) NOT NULL,	-- VARCHAR to allow indexing
    name VARCHAR(255) NOT NULL,	-- VARCHAR to allow indexing
    description TEXT
);
-- ALTER TABLE item_collection MODIFY COLUMN item_collection_id BIGINT SIGNED NOT NULL AUTO_INCREMENT;
ALTER TABLE item_collection ADD CONSTRAINT item_collection_pkey PRIMARY KEY (item_collection_id);

ALTER TABLE item_collection ADD COLUMN external_id BIGINT;		-- Map to order set protocol ID
--ALTER TABLE item_collection RENAME COLUMN name TO name; 		-- Map to order set protocol name
ALTER TABLE item_collection RENAME COLUMN subject TO section;	-- Map to order set section_name
ALTER TABLE item_collection ADD COLUMN subgroup VARCHAR(255);	-- Map to order set "Smart Group"

-- Longer expected length to allow for long protocol names that are up to 400 characters
ALTER TABLE item_collection ALTER COLUMN section DROP NOT NULL;
ALTER TABLE item_collection ALTER COLUMN section TYPE VARCHAR(1024);
ALTER TABLE item_collection ALTER COLUMN subgroup TYPE VARCHAR(1024);
ALTER TABLE item_collection ALTER COLUMN name TYPE VARCHAR(1024);


CREATE TABLE collection_type
(
	collection_type_id INTEGER NOT NULL, -- SIGNED option for MySQL
	name VARCHAR(255) NOT NULL,
	description TEXT
);
ALTER TABLE collection_type ADD CONSTRAINT collection_type_pkey PRIMARY KEY (collection_type_id);
ALTER TABLE collection_type ADD CONSTRAINT collection_type_key UNIQUE (name);
-- Insert base collection types expected
INSERT INTO collection_type (collection_type_id, name, description) VALUES
	(1, 'Recommendation', 'Recommendation Level - For example, 1=Generally agreed recommendation, 2=Moderate or conflicting support for recommendation, 2.1=Recommendation default without quantification, 2.5=Conflicting support, favor not recommending, or highly conditional, 3=Generally agreed against'),
	(2, 'Evidence', 'Evidence Level - For example, 1=(a) Strong evidence, 2=(b) Moderate evidence, 3=(c) Weak evidence'),
	(3, 'Reference','Reference Level - For example, 1=Explicitly referenced in collection, 2=Implied use in collection, 2.5=Consistent with properties of collection, but may be highly conditional or secondary choice, 3=Referenced *against* use');
INSERT INTO collection_type (collection_type_id, name, description) VALUES
	(4, 'OrderSet', '1=Default-selected, 2=Available, 2.5=Available under sub-menu');
INSERT INTO collection_type (collection_type_id, name, description) VALUES
	(5, 'DiagnosisLink', 'Link an (admission) diagnosis designated by clinical_item_id to the item collection (value = 3: reference guidelines or value = 4: order set collections).');

 	
CREATE TABLE item_collection_item
(
	item_collection_item_id SERIAL NOT NULL,
	item_collection_id BIGINT NOT NULL,
	clinical_item_id BIGINT,	-- Allow null for references to actions not available as an existing clinical_item
	collection_type_id INTEGER,
	value DECIMAL(9,3),	-- Precision values, but allow decimal values, not just integers
	priority INTEGER,
	comment TEXT
);
-- ALTER TABLE item_collection_item MODIFY COLUMN item_collection_item_id BIGINT SIGNED NOT NULL AUTO_INCREMENT;
ALTER TABLE item_collection_item ADD CONSTRAINT item_collection_item_pkey PRIMARY KEY (item_collection_item_id);
ALTER TABLE item_collection_item ADD CONSTRAINT item_collection_item_collection_fkey FOREIGN KEY (item_collection_id) REFERENCES item_collection(item_collection_id);
CREATE INDEX item_collection_item_collection_id ON item_collection_item(item_collection_id);
ALTER TABLE item_collection_item ADD CONSTRAINT item_collection_item_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id);
CREATE INDEX item_collection_item_clinical_item_id ON item_collection_item(clinical_item_id);
ALTER TABLE item_collection_item ADD CONSTRAINT item_collection_item_type_fkey FOREIGN KEY (collection_type_id) REFERENCES collection_type(collection_type_id);
--CREATE INDEX item_collection_item_type_id ON item_collection_item(collection_type_id);


-- Link table between patient items and (order set) collections they belong to or are derived from
CREATE TABLE patient_item_collection_link
(
	patient_item_collection_link_id SERIAL NOT NULL,
	patient_item_id BIGINT NOT NULL,
	item_collection_item_id BIGINT NOT NULL
);
ALTER TABLE patient_item_collection_link ADD CONSTRAINT patient_item_collection_link_pkey PRIMARY KEY (patient_item_collection_link_id);
ALTER TABLE patient_item_collection_link ADD CONSTRAINT patient_item_collection_link_patient_fkey FOREIGN KEY (patient_item_id) REFERENCES patient_item(patient_item_id);
CREATE INDEX patient_item_collection_link_patient_item_id ON patient_item_collection_link(patient_item_id);
ALTER TABLE patient_item_collection_link ADD CONSTRAINT patient_item_collection_link_item_fkey FOREIGN KEY (item_collection_item_id) REFERENCES item_collection_item(item_collection_item_id);
CREATE INDEX patient_item_collection_link_item_collection_item_id ON patient_item_collection_link(item_collection_item_id);
