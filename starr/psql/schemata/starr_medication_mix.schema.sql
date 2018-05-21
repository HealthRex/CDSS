-- Table: starr_medication_mix
-- Description: 1-to-many mapping from order order_med_id to medication(s)
-- in order (identified by medication_id). Note both min_dose_amount (nominal
-- prescribed amount) vs min_calc_dose_amt (calculated amount based on
-- concentration of ingredient).
-- Original Files:
--	* Chen_MedicationID_to_MPI.csv.gz
-- Clean Files:
--	* starr_medication_mpi.csv.gz
-- CSV Fields:
--  * order_med_id (e.g. 11192203)
--  * line (1-indexed line counter of medications in order_med_id, e.g. 2)
--  * medication_id (e.g. 210379)
--  * medication_name (e.g. "SODIUM CHLORIDE 0.9 % 0.9 % IV SOLP")
--  * ingredient_type_c (ingredient category number, e.g. 1)
--  * ingredient_type (maps to ingredient_type_c, e.g. "Base" for 1)
--  * min_dose_amount (e.g. 1000)
--  * max_dose_amount (e.g. 5000)
--  * dose_unit_c (dose unit category number, e.g. 1.0)
--  * dose_unit (maps to dose_unit_c, e.g. "mL" for 1)
--  * nonformulary_yn (e.e. Y)
--  * selection (e.g. 3)
--  * min_calc_dose_amt (e.g. 10)
--  * max_calc_dose_amt (e.g. 50)
--  * calc_dose_unit_c (e.g. 8)
--  * calc_dose_unit (maps to calc_dose_unit_c, e.g. "mcg" for 8)
--  * dose_calc_info (formula for min_dose_amount -> min_calc_dose_amt, e.g.
--                    "50 mg ? 1 mL/25 mg = 2 mL ? 25,000 mcg/mL = 50,000 mcg")

CREATE TABLE IF NOT EXISTS starr_medication_mix
(
  order_med_id BIGINT,
  line INTEGER,
  medication_id INTEGER,
  medication_name TEXT,
  ingredient_type_c INTEGER,
  ingredient_type TEXT,
  min_dose_amount FLOAT,
  max_dose_amount FLOAT,
  dose_unit_c INTEGER,
  dose_unit TEXT,
  nonformulary_yn TEXT,
  selection INTEGER,
  min_calc_dose_amt FLOAT,
  max_calc_dose_amt FLOAT,
  calc_dose_unit_c INTEGER,
  calc_dose_unit TEXT,
  dose_calc_info TEXT
);
