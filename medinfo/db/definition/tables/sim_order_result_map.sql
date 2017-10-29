-- Many-to-Many mapping to indicate which (lab) orders (referenced as clinical_item_ids) can trigger which results
--	That way can prespecify what lab results are expected for a simulated patient, but do not release
--	that information until user orders a respective laboratory test.
CREATE TABLE IF NOT EXISTS sim_order_result_map
(
	sim_order_result_map_id SERIAL NOT NULL,
	clinical_item_id BIGINT NOT NULL, -- Precedent item / Triggering order
	sim_result_id BIGINT NOT NULL,
	turnaround_time INTEGER,	-- Seconds from the order time until expect to have/release the result
	CONSTRAINT sim_order_result_map_pkey PRIMARY KEY (sim_order_result_map_id),
	CONSTRAINT sim_order_result_map_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id),
	CONSTRAINT sim_order_result_map_sim_result_fkey FOREIGN KEY (sim_result_id) REFERENCES sim_result(sim_result_id)
);
-- ALTER TABLE sim_order_result_map ADD CONSTRAINT sim_order_result_map_pkey PRIMARY KEY (sim_order_result_map_id);
-- ALTER TABLE sim_order_result_map ADD CONSTRAINT sim_order_result_map_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id);
-- ALTER TABLE sim_order_result_map ADD CONSTRAINT sim_order_result_map_sim_result_fkey FOREIGN KEY (sim_result_id) REFERENCES sim_result(sim_result_id);
CREATE INDEX IF NOT EXISTS index_sim_order_result_map_sim_result ON sim_order_result_map(sim_result_id);
CREATE INDEX IF NOT EXISTS index_sim_order_result_map_clinical_item ON sim_order_result_map(clinical_item_id);
