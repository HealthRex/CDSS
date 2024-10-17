-- Table: stride_patient

CREATE INDEX IF NOT EXISTS index_stride_patient_pat_id
                            ON stride_patient(SUBSTRING(pat_id, 1, 16));
