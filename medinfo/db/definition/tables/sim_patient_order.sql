-- Clinical item orders for patients, keyed with start and end dates
CREATE TABLE sim_patient_order
(
    sim_patient_order_id SERIAL NOT NULL,
    sim_user_id BIGINT NOT NULL,
    sim_patient_id BIGINT NOT NULL,
    clinical_item_id BIGINT NOT NULL,
    relative_time_start INTEGER NOT NULL,	-- Relative to base / zero time of simulated case that the order occurred / started
    relative_time_end INTEGER	-- Relative to base / zero time of simulated case that order concludes or was discontinued
);
ALTER TABLE sim_patient_order ADD CONSTRAINT sim_patient_order_pkey PRIMARY KEY (sim_patient_order_id);
ALTER TABLE sim_patient_order ADD CONSTRAINT sim_patient_order_sim_user_fkey FOREIGN KEY (sim_user_id) REFERENCES sim_user(sim_user_id);
ALTER TABLE sim_patient_order ADD CONSTRAINT sim_patient_order_sim_patient_fkey FOREIGN KEY (sim_patient_id) REFERENCES sim_patient(sim_patient_id);
ALTER TABLE sim_patient_order ADD CONSTRAINT sim_patient_order_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id);
CREATE INDEX index_sim_patient_order_sim_user_patient_date ON sim_patient_order(sim_user_id, sim_patient_id, relative_time_start);	-- Natural sorting option to order by user, patient, then in chronological order of clinical items
CREATE INDEX index_sim_patient_order_sim_clinical_item ON sim_patient_order(sim_patient_id, clinical_item_id);	-- Natural sorting option to order by patient, then in chronological order of clinical items
-- Record patient state at the time of the order.
-- Denormalized information that could be derived from sim_patient_state, but makes future joins a hassle using relative time information
ALTER TABLE sim_patient_order ADD COLUMN sim_state_id BIGINT NOT NULL DEFAULT 0;
ALTER TABLE sim_patient_order ADD CONSTRAINT sim_patient_order_state_fkey FOREIGN KEY (sim_state_id) REFERENCES sim_state(sim_state_id);
