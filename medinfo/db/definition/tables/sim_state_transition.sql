-- State transition triggers
CREATE TABLE IF NOT EXISTS sim_state_transition
(
	sim_state_transition_id SERIAL NOT NULL,
	pre_state_id BIGINT NOT NULL,
	post_state_id BIGINT NOT NULL,
	clinical_item_id BIGINT, -- Clinical Item that occurs in pre-state to trigger transition to post-state
	time_trigger INTEGER,	-- Alternatively, amount of time (seconds) to pass before triggering state transition
	description TEXT,
	CONSTRAINT sim_state_transition_pkey PRIMARY KEY (sim_state_transition_id),
	CONSTRAINT sim_state_transition_unique_key UNIQUE (pre_state_id, clinical_item_id),
	CONSTRAINT sim_state_transition_pre_state_fkey FOREIGN KEY (pre_state_id) REFERENCES sim_state(sim_state_id),
	CONSTRAINT sim_state_transition_post_state_fkey FOREIGN KEY (post_state_id) REFERENCES sim_state(sim_state_id),
	CONSTRAINT sim_state_transition_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id)
);
-- ALTER TABLE sim_state_transition ADD CONSTRAINT sim_state_transition_pkey PRIMARY KEY (sim_state_transition_id);
-- ALTER TABLE sim_state_transition ADD CONSTRAINT sim_state_transition_unique_key UNIQUE (pre_state_id, clinical_item_id);
-- ALTER TABLE sim_state_transition ADD CONSTRAINT sim_state_transition_pre_state_fkey FOREIGN KEY (pre_state_id) REFERENCES sim_state(sim_state_id);
-- ALTER TABLE sim_state_transition ADD CONSTRAINT sim_state_transition_post_state_fkey FOREIGN KEY (post_state_id) REFERENCES sim_state(sim_state_id);
-- ALTER TABLE sim_state_transition ADD CONSTRAINT sim_state_transition_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id);
CREATE INDEX IF NOT EXISTS index_sim_state_transition_pre_state ON sim_state_transition(pre_state_id,clinical_item_id);	-- Should be created implicitly by UNIQUE constraint
CREATE INDEX IF NOT EXISTS index_sim_state_transition_post_state ON sim_state_transition(post_state_id,clinical_item_id);
