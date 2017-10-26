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
