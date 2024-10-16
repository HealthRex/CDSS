-- Table: stride_order_proc

CREATE INDEX IF NOT EXISTS index_stride_order_proc_pat_id_bigint
                            ON stride_order_proc(CAST(pat_id AS BIGINT));
CREATE INDEX IF NOT EXISTS index_stride_order_proc_pat_id_str
                            ON stride_order_proc(pat_id);
CREATE INDEX IF NOT EXISTS index_stride_order_proc_order_proc_id
                            ON stride_order_proc(order_proc_id);
CREATE INDEX IF NOT EXISTS index_stride_order_proc_proc_code
                            ON stride_order_proc(proc_code);
CREATE INDEX IF NOT EXISTS index_stride_order_proc_order_proc_id_proc_code
                            ON stride_order_proc(proc_code, order_proc_id);
