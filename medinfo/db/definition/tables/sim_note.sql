-- Patient Notes
CREATE TABLE sim_note
(
	sim_note_id SERIAL NOT NULL,
	sim_state_id BIGINT NOT NULL,
	note_type_id INTEGER,
	author_type_id INTEGER,
	service_type_id INTEGER,
	relative_state_time INTEGER NOT NULL, -- Seconds relative to the simulated patient state's relative_time_start
	content TEXT NOT NULL
);
ALTER TABLE sim_note ADD CONSTRAINT sim_note_pkey PRIMARY KEY (sim_note_id);
ALTER TABLE sim_note ADD CONSTRAINT sim_note_state_fkey FOREIGN KEY (sim_state_id) REFERENCES sim_state(sim_state_id);
ALTER TABLE sim_note ADD CONSTRAINT sim_note_note_type_fkey FOREIGN KEY (note_type_id) REFERENCES sim_note_type(sim_note_type_id);
ALTER TABLE sim_note ADD CONSTRAINT sim_note_author_type_fkey FOREIGN KEY (author_type_id) REFERENCES sim_note_type(sim_note_type_id);
ALTER TABLE sim_note ADD CONSTRAINT sim_note_service_type_fkey FOREIGN KEY (service_type_id) REFERENCES sim_note_type(sim_note_type_id);
CREATE INDEX index_sim_note_state ON sim_note(sim_state_id,relative_state_time);
