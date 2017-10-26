-- Core stat tracking table, record various association statistics,
--	mostly counting up the number of times one item / order follows another	within any patient's course.
-- DROP TABLE clinical_item_association;    -- If need to recreate from scratch with revised column types
CREATE TABLE clinical_item_association
(
    clinical_item_association_id SERIAL NOT NULL,
    clinical_item_id BIGINT NOT NULL,
    subsequent_item_id BIGINT NOT NULL
);
-- ALTER TABLE clinical_item_association MODIFY COLUMN clinical_item_association_id BIGINT SIGNED NOT NULL AUTO_INCREMENT;
ALTER TABLE clinical_item_association ADD CONSTRAINT clinical_item_association_pkey PRIMARY KEY (clinical_item_association_id);
ALTER TABLE clinical_item_association ADD CONSTRAINT clinical_item_association_clinical_item_fkey FOREIGN KEY (clinical_item_id) REFERENCES clinical_item(clinical_item_id);
ALTER TABLE clinical_item_association ADD CONSTRAINT clinical_item_association_subsequent_item_fkey FOREIGN KEY (subsequent_item_id) REFERENCES clinical_item(clinical_item_id);
ALTER TABLE clinical_item_association ADD CONSTRAINT clinical_item_association_composite_key UNIQUE (clinical_item_id, subsequent_item_id);
CREATE INDEX clinical_item_association_clinical_item_id ON clinical_item_association(clinical_item_id, subsequent_item_id);
CREATE INDEX clinical_item_association_subsequent_item_id ON clinical_item_association(subsequent_item_id, clinical_item_id);

-- Basic type of stats, counting up cooccurences.  Column names encoded by duration of seconds the counting timeframe represents
-- Use DOUBLE PRECISION / floating point values to allow for weighted pseudo-counts
ALTER TABLE clinical_item_association ADD COLUMN count_0 DOUBLE PRECISION DEFAULT 0;	-- Number of times the subsequent item follows the primary clinical item within 0 seconds of event TIMESTAMP
ALTER TABLE clinical_item_association ADD COLUMN count_3600 DOUBLE PRECISION DEFAULT 0;	-- 1 hour
ALTER TABLE clinical_item_association ADD COLUMN count_7200 DOUBLE PRECISION DEFAULT 0;	-- 2 hours
ALTER TABLE clinical_item_association ADD COLUMN count_21600 DOUBLE PRECISION DEFAULT 0;	-- 6 hours
ALTER TABLE clinical_item_association ADD COLUMN count_43200 DOUBLE PRECISION DEFAULT 0; -- 12 hours
ALTER TABLE clinical_item_association ADD COLUMN count_86400 DOUBLE PRECISION DEFAULT 0;  -- 1 day
ALTER TABLE clinical_item_association ADD COLUMN count_172800 DOUBLE PRECISION DEFAULT 0; -- 2 days
ALTER TABLE clinical_item_association ADD COLUMN count_345600 DOUBLE PRECISION DEFAULT 0; -- 4 days
ALTER TABLE clinical_item_association ADD COLUMN count_604800 DOUBLE PRECISION DEFAULT 0; -- 1 week
ALTER TABLE clinical_item_association ADD COLUMN count_1209600 DOUBLE PRECISION DEFAULT 0; -- 2 weeks
ALTER TABLE clinical_item_association ADD COLUMN count_2592000 DOUBLE PRECISION DEFAULT 0; -- 1 month (30 days)
ALTER TABLE clinical_item_association ADD COLUMN count_7776000 DOUBLE PRECISION DEFAULT 0; -- 3 months
ALTER TABLE clinical_item_association ADD COLUMN count_15552000 DOUBLE PRECISION DEFAULT 0; -- 6 months
ALTER TABLE clinical_item_association ADD COLUMN count_31536000 DOUBLE PRECISION DEFAULT 0; -- 1 year (365 days)
ALTER TABLE clinical_item_association ADD COLUMN count_63072000 DOUBLE PRECISION DEFAULT 0; -- 2 years
ALTER TABLE clinical_item_association ADD COLUMN count_126144000 DOUBLE PRECISION DEFAULT 0; -- 4 years
ALTER TABLE clinical_item_association ADD COLUMN count_any DOUBLE PRECISION DEFAULT 0; -- Number of times the subsequent item follows within any period of recorded time
ALTER TABLE clinical_item_association ADD COLUMN time_diff_sum DOUBLE PRECISION DEFAULT 0; -- Sum of differences in event times of subsequent vs. primary items, expressed in seconds.  This divided by count_any reflects the average time difference
ALTER TABLE clinical_item_association ADD COLUMN time_diff_sum_squares DOUBLE PRECISION DEFAULT 0; -- Sum of squared difference values as above.  Can be used with above to assess variance of time differences (var = (SumSquares - Sum^2) / count_any)

-- Similar stats, but don't count duplicates within the timeframes, only incrementing counts for the first subsequent item encountered
-- Expand time windows for counting. Should always meet or exceed dataset timeframe so easy to upscale without full recalc
-- More stats, but now count simply by the existence of a patient with the combination and only count once per patient
ALTER TABLE clinical_item_association ADD COLUMN patient_count_0 DOUBLE PRECISION DEFAULT 0;
ALTER TABLE clinical_item_association ADD COLUMN patient_count_3600 DOUBLE PRECISION DEFAULT 0;	-- 1 hour
ALTER TABLE clinical_item_association ADD COLUMN patient_count_7200 DOUBLE PRECISION DEFAULT 0;	-- 2 hours
ALTER TABLE clinical_item_association ADD COLUMN patient_count_21600 DOUBLE PRECISION DEFAULT 0;	-- 6 hours
ALTER TABLE clinical_item_association ADD COLUMN patient_count_43200 DOUBLE PRECISION DEFAULT 0; -- 12 hours
ALTER TABLE clinical_item_association ADD COLUMN patient_count_86400 DOUBLE PRECISION DEFAULT 0;  -- 1 day
ALTER TABLE clinical_item_association ADD COLUMN patient_count_172800 DOUBLE PRECISION DEFAULT 0; -- 2 days
ALTER TABLE clinical_item_association ADD COLUMN patient_count_345600 DOUBLE PRECISION DEFAULT 0; -- 4 days
ALTER TABLE clinical_item_association ADD COLUMN patient_count_604800 DOUBLE PRECISION DEFAULT 0; -- 1 week
ALTER TABLE clinical_item_association ADD COLUMN patient_count_1209600 DOUBLE PRECISION DEFAULT 0; -- 2 weeks
ALTER TABLE clinical_item_association ADD COLUMN patient_count_2592000 DOUBLE PRECISION DEFAULT 0; -- 1 month (30 days)
ALTER TABLE clinical_item_association ADD COLUMN patient_count_7776000 DOUBLE PRECISION DEFAULT 0; -- 3 months
ALTER TABLE clinical_item_association ADD COLUMN patient_count_15552000 DOUBLE PRECISION DEFAULT 0; -- 6 months
ALTER TABLE clinical_item_association ADD COLUMN patient_count_31536000 DOUBLE PRECISION DEFAULT 0; -- 1 year (365 days)
ALTER TABLE clinical_item_association ADD COLUMN patient_count_63072000 DOUBLE PRECISION DEFAULT 0; -- 2 years
ALTER TABLE clinical_item_association ADD COLUMN patient_count_126144000 DOUBLE PRECISION DEFAULT 0; -- 4 years
ALTER TABLE clinical_item_association ADD COLUMN patient_count_any DOUBLE PRECISION DEFAULT 0;
ALTER TABLE clinical_item_association ADD COLUMN patient_time_diff_sum DOUBLE PRECISION DEFAULT 0;
ALTER TABLE clinical_item_association ADD COLUMN patient_time_diff_sum_squares DOUBLE PRECISION DEFAULT 0;

-- More stats, but now count by the existence of a patient encounter with the combination and only count once per encounter
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_0 DOUBLE PRECISION DEFAULT 0;
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_3600 DOUBLE PRECISION DEFAULT 0;	-- 1 hour
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_7200 DOUBLE PRECISION DEFAULT 0;	-- 2 hours
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_21600 DOUBLE PRECISION DEFAULT 0;	-- 6 hours
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_43200 DOUBLE PRECISION DEFAULT 0; -- 12 hours
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_86400 DOUBLE PRECISION DEFAULT 0;  -- 1 day
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_172800 DOUBLE PRECISION DEFAULT 0; -- 2 days
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_345600 DOUBLE PRECISION DEFAULT 0; -- 4 days
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_604800 DOUBLE PRECISION DEFAULT 0; -- 1 week
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_1209600 DOUBLE PRECISION DEFAULT 0; -- 2 weeks
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_2592000 DOUBLE PRECISION DEFAULT 0; -- 1 month (30 days)
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_7776000 DOUBLE PRECISION DEFAULT 0; -- 3 months
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_15552000 DOUBLE PRECISION DEFAULT 0; -- 6 months
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_31536000 DOUBLE PRECISION DEFAULT 0; -- 1 year (365 days)
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_63072000 DOUBLE PRECISION DEFAULT 0; -- 2 years
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_126144000 DOUBLE PRECISION DEFAULT 0; -- 4 years
ALTER TABLE clinical_item_association ADD COLUMN encounter_count_any DOUBLE PRECISION DEFAULT 0;
ALTER TABLE clinical_item_association ADD COLUMN encounter_time_diff_sum DOUBLE PRECISION DEFAULT 0;
ALTER TABLE clinical_item_association ADD COLUMN encounter_time_diff_sum_squares DOUBLE PRECISION DEFAULT 0;
