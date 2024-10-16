-- Table: stride_flowsheet

CREATE INDEX IF NOT EXISTS index_stride_flowsheet_pat_enc
                            ON stride_flowsheet(pat_anon_id,pat_enc_csn_anon_id);
CREATE INDEX IF NOT EXISTS index_stride_flowsheet_measure
                            ON stride_flowsheet(flo_meas_id,flowsheet_name);
CREATE INDEX IF NOT EXISTS index_stride_flowsheet_pat_anon_id
                            ON stride_flowsheet(pat_anon_id);
CREATE INDEX IF NOT EXISTS index_stride_flowsheet_flowsheet_name
                            ON stride_flowsheet(flowsheet_name);
