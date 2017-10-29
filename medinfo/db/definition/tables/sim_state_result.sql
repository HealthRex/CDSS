-- Specific values for individual patient states, map to clinical_items reflecting laboratory results
-- Include flowsheet (vitals) through here as well and just separate out by result group_strings
CREATE TABLE IF NOT EXISTS sim_state_result
(
	sim_state_result_id SERIAL NOT NULL,
	sim_state_id INTEGER NOT NULL,  -- Simulated Patient State identifier that this result should be available for.  Don't assign to specific patients, assign patients to a state that these reflect
	sim_result_id BIGINT NOT NULL,
	clinical_item_id BIGINT, -- Map to clinical_items reflecting (laboratory) results
	num_value FLOAT,
	num_value_noise FLOAT, -- Option to add +/- noise to reported value in case of repeated testing
	text_value TEXT,
	result_flag TEXT,
	CONSTRAINT sim_state_result_pkey PRIMARY KEY (sim_state_result_id),
	CONSTRAINT sim_state_result_state_fkey FOREIGN KEY (sim_state_id) REFERENCES sim_state(sim_state_id),
	CONSTRAINT sim_state_result_sim_result_fkey FOREIGN KEY (sim_result_id) REFERENCES sim_result(sim_result_id),
	CONSTRAINT sim_state_result_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id)
);
-- ALTER TABLE sim_state_result ADD CONSTRAINT sim_state_result_pkey PRIMARY KEY (sim_state_result_id);
-- ALTER TABLE sim_state_result ADD CONSTRAINT sim_state_result_state_fkey FOREIGN KEY (sim_state_id) REFERENCES sim_state(sim_state_id);
-- ALTER TABLE sim_state_result ADD CONSTRAINT sim_state_result_sim_result_fkey FOREIGN KEY (sim_result_id) REFERENCES sim_result(sim_result_id);
-- ALTER TABLE sim_state_result ADD CONSTRAINT sim_state_result_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id);
CREATE INDEX IF NOT EXISTS index_sim_state_result_state ON sim_state_result(sim_state_id);
CREATE INDEX IF NOT EXISTS index_sim_state_result_sim_result ON sim_state_result(sim_result_id,num_value);
CREATE INDEX IF NOT EXISTS index_sim_state_result_clinical_item ON sim_state_result(clinical_item_id);
