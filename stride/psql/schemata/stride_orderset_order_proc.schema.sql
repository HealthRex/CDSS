-- Table: stride_orderset_order_proc
-- Description: Procedures ordered from order sets.
-- Raw Files:
--  * orderset_procedures.csv.gz
-- Clean Files:
--  * stride_orderset_order_proc_2008_2014.csv.gz
-- CSV Fields:
--  * ORDER_PROC_ID (e.g. 32163106)
--  * PROC_CODE (e.g. NUR1940)
--  * PROC_ID (e.g. 473044)
--  * SS_SG_KEY (e.g. 15012)
--  * SECTION_NAME (e.g. LABORATORY)
--  * SMART_GROUP (e.g. Chemistry)
--  * ORDER_TYPE (e.g. Order Set)
--  * PROTOCOL_ID (e.g. 1595)
--  * PROTOCOL_NAME (e.g. IP INTERAGENCY DISCHARGE ORDERS)

CREATE TABLE IF NOT EXISTS stride_orderset_order_proc
(
	order_proc_id BIGINT,
	proc_code TEXT,
	proc_id BIGINT,
	ss_sg_key TEXT,
	section_name TEXT,
	smart_group TEXT,
	order_type TEXT,
	protocol_id BIGINT,
	protocol_name TEXT
);
