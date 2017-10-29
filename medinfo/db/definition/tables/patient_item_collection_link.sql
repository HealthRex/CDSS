-- Link table between patient items and (order set) collections they belong to or are derived from
CREATE TABLE IF NOT EXISTS patient_item_collection_link
(
	patient_item_collection_link_id SERIAL NOT NULL,
	patient_item_id BIGINT NOT NULL,
	item_collection_item_id BIGINT NOT NULL,
	CONSTRAINT patient_item_collection_link_pkey PRIMARY KEY (patient_item_collection_link_id),
	CONSTRAINT patient_item_collection_link_patient_fkey FOREIGN KEY (patient_item_id) REFERENCES patient_item(patient_item_id)
);
-- ALTER TABLE patient_item_collection_link ADD CONSTRAINT patient_item_collection_link_pkey PRIMARY KEY (patient_item_collection_link_id);
-- ALTER TABLE patient_item_collection_link ADD CONSTRAINT patient_item_collection_link_patient_fkey FOREIGN KEY (patient_item_id) REFERENCES patient_item(patient_item_id);
CREATE INDEX IF NOT EXISTS patient_item_collection_link_patient_item_id ON patient_item_collection_link(patient_item_id);

-- ALTER TABLE patient_item_collection_link ADD CONSTRAINT patient_item_collection_link_item_fkey FOREIGN KEY (item_collection_item_id) REFERENCES item_collection_item(item_collection_item_id);
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT constraint_name
    FROM information_schema.table_constraints
    WHERE table_name = 'patient_item_collection_link' AND constraint_name = 'patient_item_collection_link_item_fkey'
  )
  THEN
    ALTER TABLE patient_item_collection_link ADD CONSTRAINT patient_item_collection_link_item_fkey FOREIGN KEY (item_collection_item_id) REFERENCES item_collection_item(item_collection_item_id);
  END IF;
END$$;

CREATE INDEX IF NOT EXISTS patient_item_collection_link_item_collection_item_id ON patient_item_collection_link(item_collection_item_id);
