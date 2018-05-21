-- Table: starr_preadmit_med
-- Description: Medications actively taken by pat_anon_id as of contact_date.
-- Raw Files:
--  * Chen_Active_Meds_At_Admit.csv.gz
-- Clean Files:
--  * starr_preadmit_meds_2014.csv.gz
-- CSV Fields:
--  * "PAT_ANON_ID" (e.g. 11577528280870)
--  * "CONTACT_DATE" (e.g. 04/21/2009)
--  * "MEDICATION_ID" (e.g. 1698)
--  * "DESCRIPTION" (e.g. "PLAVIX 75 MG PO TABS")
--  * "THERA_CLASS" (e.g. "CARDIOVASCULAR")
--  * "PHARM_CLASS" (e.g. "PROTON-PUMP INHIBITORS")
--  * "PHARM_SUBCLASS" (e.g. "Anticoagulants - Coumarin")

CREATE TABLE IF NOT EXISTS starr_preadmit_med
(
  pat_anon_id BIGINT,
  contact_date TIMESTAMP,
  medication_id INTEGER,
  description TEXT,
  thera_class TEXT,
  pharm_class TEXT,
  pharm_subclass TEXT
);
