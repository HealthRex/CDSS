-- Table: stride_order_result

CREATE INDEX IF NOT EXISTS index_stride_order_result_order_proc_id
                            ON stride_order_result(order_proc_id);
CREATE INDEX IF NOT EXISTS index_stride_order_result_base_name
                            ON stride_order_results(base_name);
