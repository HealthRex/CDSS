-- Table: stride_order_results

CREATE INDEX IF NOT EXISTS index_stride_order_results_order_proc_id
                            ON stride_order_results(order_proc_id);
CREATE INDEX IF NOT EXISTS index_stride_order_results_base_name
                            ON stride_order_results(base_name);
