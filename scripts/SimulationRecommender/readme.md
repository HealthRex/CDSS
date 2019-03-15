
#### \dt List of Tables from psql (David M.)  

- backup_link_patient_item
- clinical_item
- clinical_item_association
- clinical_item_category
- clinical_item_link
- collection_type
- data_cache
- item_collection
- item_collection_item
- order_result_stat
- patient_item
- patient_item_collection_link
- sim_note
- sim_note_type
- sim_order_result_map
- sim_patient
- sim_patient_order
- sim_patient_state
- sim_result
- sim_state_result
- sim_state_transition
- sim_user 

#### Shell Script to Dump DataTables (Jonathan Chen) 
#### # !/bin/sh -x
#### Define constants for connecting to database from which to dump tables.
#### For example, if dumping from local database named test_database and accessing
#### as user test_user, you would use the following lines:
#### export DB_HOST=localhost
#### export DB_DSN=test_database
#### export DB_USER=test_user
export DB_HOST=localhost
export DB_DSN=database
export DB_USER=user

#### Pipe the uncompressed data from gzip to psql to load to database.
gzip -d -c clinical_item_category.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c clinical_item.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c clinical_item_link.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c patient_item.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c backup_link_patient_item.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c clinical_item_association.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c item_collection.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c collection_type.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c item_collection_item.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c patient_item_collection_link.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c order_result_stat.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
gzip -d -c data_cache.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN <br />
