-- Table: stride_chargemaster
-- Description: Charges in Stanford hospital (not price/cost).
--              Publicly available at http://www.oshpd.ca.gov/chargemaster/
-- Raw Files:
--  * ChargeMaster.Stanford.2014.csv.gz
-- Clean Files:
--  * stride_chargemaster_2014.csv.gz
-- CSV Fields:
--  * service_code (e.g. 33178377)
--  * description (e.g. "HC TRANSFUSION BLOOD-1 HR")
--  * price (e.g. 2125.00)

CREATE TABLE IF NOT EXISTS stride_chargemaster
(
	service_code INTEGER,
	description TEXT,
	price FLOAT
);
