-- Table: stride_patient_encounter

CREATE INDEX IF NOT EXISTS index_stride_patient_encounter_encounter_id
                            ON stride_patient_encounter(pat_enc_csn_id);
