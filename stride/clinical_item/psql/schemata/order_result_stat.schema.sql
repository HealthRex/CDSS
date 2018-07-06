-- Table: order_result_stat
-- Description: Stats on order (lab) results to help track distributions.

CREATE TABLE IF NOT EXISTS order_result_stat
(
	order_result_stat_id SERIAL NOT NULL,
	base_name TEXT NOT NULL,
	value_count INTEGER DEFAULT 0,
	value_sum FLOAT DEFAULT 0,
	value_sum_squares FLOAT DEFAULT 0,
	max_result_flag TEXT,
	max_result_in_range TEXT,
	CONSTRAINT order_result_stat_pkey PRIMARY KEY (order_result_stat_id),
	CONSTRAINT order_result_stat_key UNIQUE (base_name)
);
