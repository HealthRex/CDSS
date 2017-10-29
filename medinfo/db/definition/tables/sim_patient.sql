-- Basic simulated patient information
CREATE TABLE IF NOT EXISTS sim_patient
(
	sim_patient_id SERIAL NOT NULL,
	name TEXT NOT NULL,
	age_years INTEGER NOT NULL,
	gender TEXT NOT NULL,
	CONSTRAINT sim_patient_pkey PRIMARY KEY (sim_patient_id)
);
-- ALTER TABLE sim_patient ADD CONSTRAINT sim_patient_pkey PRIMARY KEY (sim_patient_id);
