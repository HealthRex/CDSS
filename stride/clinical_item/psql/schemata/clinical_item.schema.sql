-- Table: clinical_item
-- Description: List of "clinical items" that will be included in analyses.
--              Defines the "vocabulary" of "words" that can form part of
--              clinical "documents."

CREATE TABLE IF NOT EXISTS clinical_item
(
    clinical_item_id SERIAL NOT NULL,
    clinical_item_category_id BIGINT NOT NULL,
    external_id BIGINT,	-- ID from externally imported data (e.g. RXCUI)
    name TEXT NOT NULL, -- e.g. MED540151
    description TEXT,   -- e.g. Warfarin
    default_recommend INTEGER DEFAULT 1, -- whether to recommend in CDSS
    item_count DOUBLE PRECISION, -- summary statistic of # occurrences ()
    patient_count DOUBLE PRECISION, -- summary statistic of # of unique patients
    encounter_count DOUBLE PRECISION, -- summary statistic of # of unique encounters
    analysis_status INTEGER DEFAULT 1, -- should be in assocation analysis?
    outcome_interest INTEGER DEFAULT 0, -- could be outcome measure?
    CONSTRAINT clinical_item_pkey PRIMARY KEY (clinical_item_id),
    CONSTRAINT clinical_item_category_fkey FOREIGN KEY
                (clinical_item_category_id) REFERENCES
                clinical_item_category(clinical_item_category_id)
);
