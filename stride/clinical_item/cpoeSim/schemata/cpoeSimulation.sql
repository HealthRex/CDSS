-- Basic simultation user tracking information
CREATE TABLE sim_user
(
	sim_user_id SERIAL NOT NULL,
	name TEXT NOT NULL
--How many years since you received your medical degree (MD/DO)?
--What is your primary area / specialty of clinical practice?
--List your current or prior medical training and board certifications:
--What percentage of your time in the past year has been spent practicing outpatient / clinic medicine?
--What percentage of your time in the past year has been spent practicing inpatient / hospital medicine?
--Approximately how many patients have you admitted to an inpatient hospital service in the past year?

);
ALTER TABLE sim_user ADD CONSTRAINT sim_user_pkey PRIMARY KEY (sim_user_id);
-- INSERT INTO sim_user(sim_user_id,name) VALUES (0,'Default User');

-- Basic simulated patient information
CREATE TABLE sim_patient
(
	sim_patient_id SERIAL NOT NULL,
	name TEXT NOT NULL,
	age_years INTEGER NOT NULL,
	gender TEXT NOT NULL
);
ALTER TABLE sim_patient ADD CONSTRAINT sim_patient_pkey PRIMARY KEY (sim_patient_id);

-- Model patient states with transition options
CREATE TABLE sim_state
(
 	sim_state_id SERIAL NOT NULL,
 	name TEXT NOT NULL,
 	description TEXT
);
ALTER TABLE sim_state ADD CONSTRAINT sim_state_pkey PRIMARY KEY (sim_state_id);
-- INSERT INTO sim_state(sim_state_id,name, description) VALUES (0,'Default','Default State Info');

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

-- State transition triggers
CREATE TABLE sim_state_transition
(
	sim_state_transition_id SERIAL NOT NULL,
	pre_state_id BIGINT NOT NULL,
	post_state_id BIGINT NOT NULL,
	clinical_item_id BIGINT, -- Clinical Item that occurs in pre-state to trigger transition to post-state
	time_trigger INTEGER,	-- Alternatively, amount of time (seconds) to pass before triggering state transition
	description TEXT
);
ALTER TABLE sim_state_transition ADD CONSTRAINT sim_state_transition_pkey PRIMARY KEY (sim_state_transition_id);
ALTER TABLE sim_state_transition ADD CONSTRAINT sim_state_transition_unique_key UNIQUE (pre_state_id, clinical_item_id);
ALTER TABLE sim_state_transition ADD CONSTRAINT sim_state_transition_pre_state_fkey FOREIGN KEY (pre_state_id) REFERENCES sim_state(sim_state_id);
ALTER TABLE sim_state_transition ADD CONSTRAINT sim_state_transition_post_state_fkey FOREIGN KEY (post_state_id) REFERENCES sim_state(sim_state_id);
ALTER TABLE sim_state_transition ADD CONSTRAINT sim_state_transition_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id);
CREATE INDEX index_sim_state_transition_pre_state ON sim_state_transition(pre_state_id,clinical_item_id);	-- Should be created implicitly by UNIQUE constraint
CREATE INDEX index_sim_state_transition_post_state ON sim_state_transition(post_state_id,clinical_item_id);

-- Code Table to record note type information.  For brevity, also track author and service types (Treatment Team?) here
CREATE TABLE sim_note_type
(
	sim_note_type_id INTEGER NOT NULL,
	name TEXT NOT NULL,
	priority INTEGER,
	description TEXT
);
ALTER TABLE sim_note_type ADD CONSTRAINT sim_note_type_pkey PRIMARY KEY (sim_note_type_id);

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

-- Result data, primarily labs and imaging, with either numeric or text values.  Lookup / code table to organize types of results
-- Format group_string as cascading categories necessary for sorting and subgrouping (e.g., Labs>Hematology>Automated Blood Count)
-- Use priority as master sorting index rather than sorting by each category grouping, as alphabetical may not always be desired sort option
CREATE TABLE sim_result
(
	sim_result_id SERIAL NOT NULL,
	name TEXT NOT NULL,
	description TEXT,
	group_string TEXT,
	priority INTEGER
);
ALTER TABLE sim_result ADD CONSTRAINT sim_result_pkey PRIMARY KEY (sim_result_id);

-- Specific values for individual patient states, map to clinical_items reflecting laboratory results
-- Include flowsheet (vitals) through here as well and just separate out by result group_strings
CREATE TABLE sim_state_result
(
	sim_state_result_id SERIAL NOT NULL,
	sim_state_id INTEGER NOT NULL,  -- Simulated Patient State identifier that this result should be available for.  Don't assign to specific patients, assign patients to a state that these reflect
	sim_result_id BIGINT NOT NULL,
	clinical_item_id BIGINT, -- Map to clinical_items reflecting (laboratory) results
	num_value FLOAT,
	num_value_noise FLOAT, -- Option to add +/- noise to reported value in case of repeated testing
	text_value TEXT,
	result_flag TEXT
);
ALTER TABLE sim_state_result ADD CONSTRAINT sim_state_result_pkey PRIMARY KEY (sim_state_result_id);
ALTER TABLE sim_state_result ADD CONSTRAINT sim_state_result_state_fkey FOREIGN KEY (sim_state_id) REFERENCES sim_state(sim_state_id);
ALTER TABLE sim_state_result ADD CONSTRAINT sim_state_result_sim_result_fkey FOREIGN KEY (sim_result_id) REFERENCES sim_result(sim_result_id);
ALTER TABLE sim_state_result ADD CONSTRAINT sim_state_result_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id);
CREATE INDEX index_sim_state_result_state ON sim_state_result(sim_state_id);
CREATE INDEX index_sim_state_result_sim_result ON sim_state_result(sim_result_id,num_value);
CREATE INDEX index_sim_state_result_clinical_item ON sim_state_result(clinical_item_id);

-- Many-to-Many mapping to indicate which (lab) orders (referenced as clinical_item_ids) can trigger which results
--	That way can prespecify what lab results are expected for a simulated patient, but do not release
--	that information until user orders a respective laboratory test.
CREATE TABLE sim_order_result_map
(
	sim_order_result_map_id SERIAL NOT NULL,
	clinical_item_id BIGINT NOT NULL, -- Precedent item / Triggering order
	sim_result_id BIGINT NOT NULL,
	turnaround_time INTEGER	-- Seconds from the order time until expect to have/release the result
);
ALTER TABLE sim_order_result_map ADD CONSTRAINT sim_order_result_map_pkey PRIMARY KEY (sim_order_result_map_id);
ALTER TABLE sim_order_result_map ADD CONSTRAINT sim_order_result_map_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id);
ALTER TABLE sim_order_result_map ADD CONSTRAINT sim_order_result_map_sim_result_fkey FOREIGN KEY (sim_result_id) REFERENCES sim_result(sim_result_id);
CREATE INDEX index_sim_order_result_map_sim_result ON sim_order_result_map(sim_result_id);
CREATE INDEX index_sim_order_result_map_clinical_item ON sim_order_result_map(clinical_item_id);

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


-- Populate sim_order_result_map and sim_result with existing data based on queries like below

-- select 
--    sop.proc_cat_name, sop.proc_id, sop.proc_code, sop.description,
--    sor.base_name, sor.component_name,
--    count(ord_num_value) as countValue,
--    sum(ord_num_value) as sumValue,
--    sum(ord_num_value*ord_num_value) as sumSquaresValue,
--    count(extract(epoch from sop.result_time-proc_start_time)) countTurnaround,
--    sum(extract(epoch from sop.result_time-proc_start_time)) sumTurnaround, 
--    sum( extract(epoch from sop.result_time-proc_start_time) ^2 ) sumSquaresTurnaround
-- from stride_order_proc as sop, stride_order_results as sor
-- where sop.order_proc_id = sor.order_proc_id
-- group by
--    sop.proc_cat_name, sop.proc_id, sop.proc_code, sop.description,
--    sor.base_name, sor.component_name

-- select 
--    flo_meas_id, flowsheet_name, 
--    count(flowsheet_value) as countValue, sum(flowsheet_value) as sumValue, sum(flowsheet_value^2) as sumSquaresValue
-- from stride_flowsheet
-- group by 
--    flo_meas_id, flowsheet_name 
--

-- Calculate result distribution summary statistics
-- python scripts\CDSS\populateOrderResultStats.py
