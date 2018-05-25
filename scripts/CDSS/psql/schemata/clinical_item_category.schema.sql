-- Table: clinical_item_category
-- Description: Categories of clinical items derived from STRIDE dataset.

CREATE TABLE IF NOT EXISTS clinical_item_category
(
  clinical_item_category_id SERIAL NOT NULL,
  source_table TEXT NOT NULL, -- source for clinical item (e.g. stride_patient)
  description TEXT,
  default_recommend INTEGER DEFAULT 1,
  CONSTRAINT clinical_item_category_pkey PRIMARY KEY (clinical_item_category_id)
);
