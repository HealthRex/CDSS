export DB_HOST=localhost
export DB_PORT=5432
export DB_DSN=medinfo-5year-time
export DB_USER=jonc101

# Prepare schema of empty tables ready to receive data
psql -f cpoeSim.sql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_DSN

# Add mock clinical_item values for simulated recommender
psql -f extraClinicalItems.sql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_DSN

# Restore the prior dumps of data table contents
# Core simulation infrastructure
psql -f sim_note_type.dump.sql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_DSN
psql -f sim_result.dump.sql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_DSN
psql -f sim_order_result_map.dump.sql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_DSN
# Case specific data
psql -f sim_state.dump.sql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_DSN
psql -f sim_note.dump.sql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_DSN
# Though there are "default" state results that are more of a core simulation infrastructure results
psql -f sim_state_result.dump.sql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_DSN
psql -f sim_state_transition.dump.sql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_DSN

# Individual test user interaction behavior (but some default ones are necessary for infrastructure)
psql -f sim_user.dump.sql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_DSN
psql -f sim_patient.dump.sql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_DSN
psql -f sim_patient_order.dump.sql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_DSN
psql -f sim_patient_state.dump.sql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_DSN
