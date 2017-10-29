-- Patient ID list with birth date, gender, race
-- 	Header: Lower-case
CREATE TABLE IF NOT EXISTS stride_patient
(
	pat_id TEXT,
	-- pat_mrn_id BIGINT,
	birth_date TIMESTAMP,
	gender TEXT,
	primary_race TEXT
);
CREATE INDEX IF NOT EXISTS index_patient_pat_id ON stride_patient(SUBSTRING(pat_id, 1, 16));
-- CREATE INDEX IF NOT EXISTS index_patient_pat_mrn_id ON stride_patient(pat_mrn_id);
-- Get rid of identifying information
ALTER TABLE stride_patient ADD COLUMN IF NOT EXISTS birth_year INTEGER;

-- UPDATE stride_patient SET birth_year = YEAR(birth_date);
DO $$
BEGIN
	IF EXISTS (
		SELECT column_name
		FROM information_schema.columns
		WHERE table_name = 'stride_patient' AND column_name = 'birth_date'
	)
	THEN
		UPDATE stride_patient SET birth_year = EXTRACT(isoyear FROM birth_date);
	END IF;
END$$;

ALTER TABLE stride_patient DROP COLUMN IF EXISTS birth_date;
-- ALTER TABLE stride_patient DROP COLUMN IF EXISTS pat_mrn_id;

-- Populate oncology label based on patient_possible_onco.csv
ALTER TABLE stride_patient ADD COLUMN IF NOT EXISTS possible_oncology INTEGER DEFAULT 0;
