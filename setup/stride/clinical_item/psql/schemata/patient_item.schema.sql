-- Table: patient_item
-- Description: Clinical items linked to actual applications to individual
-- patients, additionally keyed by the date of the item event (e.g., order
-- entry or lab result).

CREATE TABLE IF NOT EXISTS patient_item
(
    patient_item_id SERIAL NOT NULL,
	external_id BIGINT,	-- ID used from external source (e.g. RXCUI)
    patient_id BIGINT NOT NULL,
    clinical_item_id BIGINT NOT NULL,
    item_date TIMESTAMP NOT NULL,	-- date that clinical item occurred
    analyze_date TIMESTAMP,			-- date that item was analyzed for association
                                -- pre-computing. Should redesign this to
                                -- separate table to allow for multiple models
                                -- trained on same source data.
    encounter_id BIGINT, -- option to track at the individual encounter level
    text_value TEXT, -- option to store text/comment data
    num_value FLOAT, -- option to store numerical data
    source_id BIGINT, -- ID from source table
    item_date_utc TIMESTAMP,        -- date that clinical item occurred in UTC timezone, None if it's a date
    CONSTRAINT patient_item_pkey PRIMARY KEY (patient_item_id),
    CONSTRAINT patient_item_clinical_item_fkey FOREIGN KEY (clinical_item_id)
                  REFERENCES clinical_item(clinical_item_id),
    CONSTRAINT patient_item_composite UNIQUE (patient_id, clinical_item_id, item_date)
);
