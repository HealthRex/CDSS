export DB_HOST=localhost
export DB_DSN=test_db
export DB_USER=mrlsdvd

psql -U $DB_USER -d $DB_DSN -h $DB_HOST -c "DROP TABLE IF EXISTS sim_user, sim_note, sim_note_type, sim_patient, sim_patient_order, sim_state_transition, sim_state, sim_patient_state, sim_result, sim_state_result, sim_order_result_map;"

# ./restoreSimTables.sh
