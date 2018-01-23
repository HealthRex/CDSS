-- Basic simultation user tracking information
CREATE TABLE IF NOT EXISTS sim_user
(
	sim_user_id SERIAL NOT NULL,
	name TEXT NOT NULL,
	CONSTRAINT sim_user_pkey PRIMARY KEY (sim_user_id)
--How many years since you received your medical degree (MD/DO)?
--What is your primary area / specialty of clinical practice?
--List your current or prior medical training and board certifications:
--What percentage of your time in the past year has been spent practicing outpatient / clinic medicine?
--What percentage of your time in the past year has been spent practicing inpatient / hospital medicine?
--Approximately how many patients have you admitted to an inpatient hospital service in the past year?
);
-- ALTER TABLE sim_user ADD CONSTRAINT sim_user_pkey PRIMARY KEY (sim_user_id);
-- INSERT INTO sim_user(sim_user_id,name) VALUES (0,'Default User');
