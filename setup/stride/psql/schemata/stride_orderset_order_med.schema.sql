-- Table: stride_orderset_order_med
-- Description: Medications ordered from order sets.
-- Raw Files:
--  * orderset_medications.csv.gz
-- Clean Files:
--  * stride_orderset_order_med_2008_2014.csv.gz
-- CSV Fields:
--  * ORDER_MED_ID (e.g. 3000087)
--  * DESCRIPTION (e.g. SODIUM CHLORIDE 0.9 % 0.9 % IV SOLP)
--  * MEDICATION_ID (e.g. 2365)
--  * SS_SG_KEY (e.g. 17968)
--  * SECTION_NAME (e.g. HYPOGLYCEMIA CONTROL)
--  * SMART_GROUP (e.g. Antibiotics)
--  * ORDER_TYPE (e.g. Order Set)
--  * PROTOCOL_ID (e.g. 1841)
--  * PROTOCOL_NAME (e.g. IP SUR GENERAL ADMIT)

CREATE TABLE IF NOT EXISTS stride_orderset_order_med
(
  order_med_id BIGINT,
	description TEXT,
	medication_id INTEGER,
	ss_sg_key TEXT,
	section_name TEXT,
	smart_group TEXT,
	order_type TEXT,
	protocol_id BIGINT,
	protocol_name TEXT
);
