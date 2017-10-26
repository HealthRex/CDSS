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

-- Default to including all options in recommendations, but allow customizations to specify some for exclusion
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
