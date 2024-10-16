-- Table: clinical_item_link
-- Description: Track links between clinical items that should not have
--              association stats calculated, probably because they have a
--              specific firm relation (e.g. component clinical item of a
--              composite one).

CREATE TABLE IF NOT EXISTS clinical_item_link
(
	clinical_item_link_id SERIAL NOT NULL,
	clinical_item_id BIGINT NOT NULL,
	linked_item_id BIGINT NOT NULL,
  CONSTRAINT clinical_item_link_pkey PRIMARY KEY (clinical_item_link_id),
  CONSTRAINT clinical_item_link_key UNIQUE (clinical_item_id, linked_item_id),
  CONSTRAINT clinical_item_link_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id),
  CONSTRAINT clinical_item_link_linked_item_fkey FOREIGN KEY (linked_item_id) REFERENCES clinical_item(clinical_item_id)
);
