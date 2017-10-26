-- Basic simulated patient information
CREATE TABLE sim_patient
(
	sim_patient_id SERIAL NOT NULL,
	name TEXT NOT NULL,
	age_years INTEGER NOT NULL,
	gender TEXT NOT NULL
);
ALTER TABLE sim_patient ADD CONSTRAINT sim_patient_pkey PRIMARY KEY (sim_patient_id);
