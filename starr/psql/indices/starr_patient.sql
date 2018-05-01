-- Table: starr_patient

CREATE INDEX IF NOT EXISTS index_patient_pat_id ON starr_patient(SUBSTRING(pat_id, 1, 16));
