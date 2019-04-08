export DB_HOST=localhost
export DB_PORT=5432
export DB_DSN=medinfo-5year-time
export DB_USER=jonc101

psql -U $DB_USER -d $DB_DSN -h $DB_HOST -p $DB_PORT -c "DROP TABLE IF EXISTS sim_user, sim_note, sim_note_type, sim_patient, sim_patient_order, sim_state_transition, sim_state, sim_patient_state, sim_result, sim_state_result, sim_order_result_map;"

# ./restoreSimTables.sh
