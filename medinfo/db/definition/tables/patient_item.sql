-- Clinical items linked to actual applications to individual patients, additional keyed by the date
--	of the item event (e.g., order entry or lab result)
CREATE TABLE IF NOT EXISTS patient_item
(
    patient_item_id SERIAL NOT NULL,
	  external_id BIGINT,	-- ID number used from externally imported table
    patient_id BIGINT NOT NULL,
    clinical_item_id BIGINT NOT NULL,
    item_date TIMESTAMP NOT NULL,	-- Date that the clinical item occurred
    analyze_date TIMESTAMP,			-- Date that the item was analyzed for association pre-computing. Should redesign this to separate table to allow for multiple models trained on same source data
    CONSTRAINT patient_item_pkey PRIMARY KEY (patient_item_id),
    CONSTRAINT patient_item_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id)
);
-- ALTER TABLE patient_item MODIFY COLUMN patient_item_id BIGINT SIGNED NOT NULL AUTO_INCREMENT;
-- ALTER TABLE patient_item ADD CONSTRAINT patient_item_pkey PRIMARY KEY (patient_item_id);
-- ALTER TABLE patient_item ADD CONSTRAINT patient_item_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id);
CREATE INDEX IF NOT EXISTS index_patient_item_clinical_item_id_date ON patient_item(clinical_item_id, item_date); -- Strange that this is not implicitly created by foreign key constraint above?
-- ALTER TABLE patient_item ADD CONSTRAINT patient_item_patient_fkey FOREIGN KEY (patient_id) REFERENCES patient(patient_id);	-- No fixed patient (ID) table for now
CREATE INDEX IF NOT EXISTS index_patient_item_patient_id_date ON patient_item(patient_id, item_date);	-- Natural sorting option to order by patient, then in chronological order of clinical items
CREATE INDEX IF NOT EXISTS index_patient_item_external_id ON patient_item(external_id, clinical_item_id);

ALTER TABLE patient_item ADD COLUMN IF NOT EXISTS encounter_id BIGINT;	-- Option to track at the individual encounter level
CREATE INDEX IF NOT EXISTS index_patient_item_encounter_id_date ON patient_item(encounter_id, item_date);	-- Natural sorting option to order by patient encounter, then in chronological order of clinical items

-- ALTER IGNORE TABLE patient_item ADD UNIQUE INDEX patient_item_composite (patient_id, clinical_item_id, item_date);
-- Need this DO $$ construction in order to get the "IF NOT EXISTS" effect.
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT constraint_name
    FROM information_schema.constraint_column_usage
    WHERE table_name = 'patient_item' AND constraint_name = 'patient_item_composite'
  )
  THEN
    ALTER TABLE patient_item ADD CONSTRAINT patient_item_composite UNIQUE (patient_id, clinical_item_id, item_date);
  END IF;
END$$;

ALTER TABLE patient_item ADD COLUMN IF NOT EXISTS source_id BIGINT;    -- Option to store reference to origin ID (e.g., order_proc_id to enable links between orders and lab results)
ALTER TABLE patient_item ADD COLUMN IF NOT EXISTS num_value DOUBLE PRECISION;	-- Option to store numerical data
ALTER TABLE patient_item ADD COLUMN IF NOT EXISTS text_value TEXT;	-- Option to store text/comment data
-- CREATE INDEX index_patient_item_id_num_value ON patient_item(num_value);
-- CREATE INDEX index_patient_item_text_value ON patient_item(text_value);
