#!/bin/sh -x
# Define constants for connecting to database from which to dump tables.
# For example, if dumping from local database named test_database and accessing
# as user test_user, you would use the following lines:
# export DB_HOST=localhost
# export DB_DSN=test_database
# export DB_USER=test_user
export DB_HOST=database_host_name
export DB_DSN=database_source_name
export DB_USER=database_user_name

# pg_dump automatically dumps the contents of a database to standard output.
# Pipe these results to gzip, which writes to a compressed file.
pg_dump -h $DB_HOST -U $DB_USER -t stride_patient_encounter $DB_DSN | gzip -c > stride_patient_encounter.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_admit $DB_DSN | gzip -c > stride_admit.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_adt $DB_DSN | gzip -c > stride_adt.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_chargemaster $DB_DSN | gzip -c > stride_chargemaster.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_culture_micro $DB_DSN | gzip -c > stride_culture_micro.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_drg $DB_DSN | gzip -c > stride_drg.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_dx_list $DB_DSN | gzip -c > stride_dx_list.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_flowsheet $DB_DSN | gzip -c > stride_flowsheet.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_icd9_cm $DB_DSN | gzip -c > stride_icd9_cm.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_icd10_cm $DB_DSN | gzip -c > stride_icd10_cm.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_income $DB_DSN | gzip -c > stride_income.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_io_flowsheet $DB_DSN | gzip -c > stride_io_flowsheet.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_mapped_meds $DB_DSN | gzip -c > stride_mapped_meds.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_medication_mpi $DB_DSN | gzip -c > stride_medication_mpi.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_note $DB_DSN | gzip -c > stride_note.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_order_med $DB_DSN | gzip -c > stride_order_med.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_order_medmixinfo $DB_DSN | gzip -c > stride_order_medmixinfo.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_order_results $DB_DSN | gzip -c > stride_order_results.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_orderset_order_med $DB_DSN | gzip -c > stride_orderset_order_med.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_orderset_order_proc $DB_DSN | gzip -c > stride_orderset_order_proc.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_patient_encounter $DB_DSN | gzip -c > stride_patient_encounter.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_patient $DB_DSN | gzip -c > stride_patient.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_preadmit_med $DB_DSN | gzip -c > stride_preadmit_med.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t stride_treatment_team $DB_DSN | gzip -c > stride_treatment_team.dump.sql.gz
