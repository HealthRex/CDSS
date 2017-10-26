-- Model patient states with transition options
CREATE TABLE sim_state
(
 	sim_state_id SERIAL NOT NULL,
 	name TEXT NOT NULL,
 	description TEXT
);
ALTER TABLE sim_state ADD CONSTRAINT sim_state_pkey PRIMARY KEY (sim_state_id);
-- INSERT INTO sim_state(sim_state_id,name, description) VALUES (0,'Default','Default State Info');
