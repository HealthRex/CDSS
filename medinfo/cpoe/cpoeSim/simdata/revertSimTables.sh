export DB_HOST=localhost
export DB_PORT=5432
export DB_DSN=stride_inpatient_2008_2014
export DB_USER=jonc101

psql -U $DB_USER -d $DB_DSN -h $DB_HOST -p $DB_PORT -c "DROP TABLE IF EXISTS sim_user, sim_note, sim_note_type, sim_patient, sim_patient_order, sim_state_transition, sim_state, sim_patient_state, sim_result, sim_state_result, sim_order_result_map;"

# Drop the extra clinical items added, so they can be readded without conflict
psql -U $DB_USER -d $DB_DSN -h $DB_HOST -p $DB_PORT -c "DELETE FROM item_collection_item WHERE item_collection_item_id IN (-100);"
psql -U $DB_USER -d $DB_DSN -h $DB_HOST -p $DB_PORT -c "DELETE FROM item_collection WHERE item_collection_id IN (-100);"
psql -U $DB_USER -d $DB_DSN -h $DB_HOST -p $DB_PORT -c "DELETE FROM clinical_item_association WHERE clinical_item_association_id IN (-150,-160);"
psql -U $DB_USER -d $DB_DSN -h $DB_HOST -p $DB_PORT -c "DELETE FROM clinical_item WHERE clinical_item_id IN (-100);"
