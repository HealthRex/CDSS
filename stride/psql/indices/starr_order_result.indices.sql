-- Table: starr_order_result

CREATE INDEX IF NOT EXISTS index_starr_order_result_order_proc_id
                            ON starr_order_result(order_proc_id);
CREATE INDEX IF NOT EXISTS index_starr_order_result_base_name
                            ON starr_order_results(base_name);
