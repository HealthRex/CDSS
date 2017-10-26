-- Stats on order (lab) results to help track distributions
CREATE TABLE order_result_stat
(
	order_result_stat_id SERIAL NOT NULL,
	base_name TEXT NOT NULL,
	value_count INTEGER DEFAULT 0,
	value_sum DOUBLE PRECISION DEFAULT 0,
	value_sum_squares DOUBLE PRECISION DEFAULT 0
);
ALTER TABLE order_result_stat ADD CONSTRAINT order_result_stat_pkey PRIMARY KEY (order_result_stat_id);
ALTER TABLE order_result_stat ADD CONSTRAINT order_result_stat_key UNIQUE (base_name);

ALTER TABLE order_result_stat ADD COLUMN max_result_flag TEXT;
ALTER TABLE order_result_stat ADD COLUMN max_result_in_range TEXT;
