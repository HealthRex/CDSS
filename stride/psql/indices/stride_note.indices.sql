-- Table: stride_note

CREATE INDEX IF NOT EXISTS index_stride_note_pat_enc
                            ON stride_note(pat_id,pat_enc_csn_id);
CREATE INDEX IF NOT EXISTS index_stride_note_provider_type
                            ON stride_note(provider_type);
CREATE INDEX IF NOT EXISTS index_stride_note_service_type
                            ON stride_note(hospital_service,note_type);
