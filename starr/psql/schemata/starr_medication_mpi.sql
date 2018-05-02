-- Table: starr_medication_mpi
-- Description: Mapping from starr medication ID (based on Epic) to Medicare
-- Provider Inventory (MPI).
-- Original Files:
--	* Chen_MedicationID_to_MPI.csv.gz
-- Clean Files:
--	* starr_medication_mpi.csv.gz
-- CSV Fields:
--  * "MEDICATION_ID" (e.g. 127722)
--  * "MED_NAME" (e.g. "AMOXICILLIN-POT CLAVULANATE 875-125 MG PO TABS")
--  * "MPI_ID_VAL" (e.g. "0033")

CREATE TABLE IF NOT EXISTS starr_medication_mpi
(
	medication_id INTEGER,
	med_name TEXT,
	mpi_id_val TEXT
);
