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
