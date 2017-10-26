-- Patient ID list with birth date, gender, race
-- 	Header: Lower-case
create table stride_patient
(
	pat_id text,
	pat_mrn_id bigint,
	birth_date datetime,
	gender text,
	primary_race text
);
CREATE INDEX index_patient_pat_id ON stride_patient(pat_id (16));
CREATE INDEX index_patient_pat_mrn_id ON stride_patient(pat_mrn_id);
-- Get rid of identifying information
ALTER TABLE stride_patient ADD COLUMN birth_year INTEGER;
UPDATE stride_patient SET birth_year = YEAR(birth_date);
ALTER TABLE stride_patient DROP COLUMN birth_date;
ALTER TABLE stride_patient DROP COLUMN pat_mrn_id;

-- Populate oncology label based on patient_possible_onco.csv
ALTER TABLE stride_patient ADD COLUMN possible_oncology INTEGER DEFAULT 0;
