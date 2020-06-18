-- Table: stride_medication_mpi

CREATE INDEX IF NOT EXISTS index_stride_medication_mpi_medication_id
                            ON stride_medication_mpi(medication_id,mpi_id_val);
CREATE INDEX IF NOT EXISTS index_stride_medication_mpi_med_name
                            ON stride_medication_mpi(med_name);
CREATE INDEX IF NOT EXISTS index_stride_medication_mpi_mpi_id
                            ON stride_medication_mpi(mpi_id_val,medication_id);
