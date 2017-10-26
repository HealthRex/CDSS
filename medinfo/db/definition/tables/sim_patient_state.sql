-- Record when a patient enters a given state
CREATE TABLE sim_patient_state
(
	sim_patient_state_id SERIAL NOT NULL,
	sim_patient_id BIGINT NOT NULL,
	sim_state_id BIGINT NOT NULL,
	relative_time_start INTEGER NOT NULL,
	relative_time_end INTEGER -- Redundant to store end-time when can infer from start time of next record, but having both recorded makes for easier retrieval queries
);
ALTER TABLE sim_patient_state ADD CONSTRAINT sim_patient_state_pkey PRIMARY KEY (sim_patient_state_id);
ALTER TABLE sim_patient_state ADD CONSTRAINT sim_patient_state_patient_fkey FOREIGN KEY (sim_patient_id) REFERENCES sim_patient(sim_patient_id);
ALTER TABLE sim_patient_state ADD CONSTRAINT sim_patient_state_state_fkey FOREIGN KEY (sim_state_id) REFERENCES sim_state(sim_state_id);
CREATE INDEX index_sim_patient_state_patient ON sim_patient_state(sim_patient_id,relative_time_start,relative_time_end);
CREATE INDEX index_sim_patient_state_state ON sim_patient_state(sim_state_id);
