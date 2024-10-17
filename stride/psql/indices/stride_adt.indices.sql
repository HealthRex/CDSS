-- Table: stride_adt

CREATE INDEX IF NOT EXISTS index_stride_adt_patient_date
                            ON stride_adt(pat_anon_id, shifted_transf_in_dt_tm,
                                          shifted_transf_out_dt_tm);
CREATE INDEX IF NOT EXISTS index_stride_adt_department
                            ON stride_adt(department_in, event_in, event_out,
                                          shifted_transf_in_dt_tm,
                                          shifted_transf_out_dt_tm);
