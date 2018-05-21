-- Table: starr_order_med

CREATE INDEX IF NOT EXISTS index_starr_order_med_pat_id
                            ON starr_order_med(pat_id);
