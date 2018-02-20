-- Code Table to record note type information.  For brevity, also track author and service types (Treatment Team?) here
CREATE TABLE IF NOT EXISTS sim_note_type
(
	sim_note_type_id INTEGER NOT NULL,
	name TEXT NOT NULL,
	priority INTEGER,
	description TEXT,
	CONSTRAINT sim_note_type_pkey PRIMARY KEY (sim_note_type_id)
);
-- ALTER TABLE sim_note_type ADD CONSTRAINT sim_note_type_pkey PRIMARY KEY (sim_note_type_id);
