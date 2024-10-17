#!/bin/sh -x
# Define constants for connecting to database from which to dump tables.
# For example, if dumping from local database named test_database and accessing
# as user test_user, you would use the following lines:
# export DB_HOST=localhost
# export DB_DSN=test_database
# export DB_USER=test_user
export DB_HOST=host
export DB_DSN=database
export DB_USER=user

# Alternatively, if just want to dump data as CSV file without schema, meta-data, etc.
# psql -U <user> -d <database> -c "\copy clinical_item TO 'clinical_item.csv' with (format csv,header true, delimiter ',');"

# pg_dump automatically dumps the contents of a database to standard output.
# Pipe these results to gzip, which writes to a compressed file.
pg_dump -h $DB_HOST -U $DB_USER -t  clinical_item_category $DB_DSN | gzip -c > clinical_item_category.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t  clinical_item $DB_DSN | gzip -c > clinical_item.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t  clinical_item_link $DB_DSN | gzip -c > clinical_item_link.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t  patient_item $DB_DSN | gzip -c > patient_item.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t  backup_link_patient_item $DB_DSN | gzip -c > backup_link_patient_item.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t  clinical_item_association $DB_DSN | gzip -c > clinical_item_association.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t  item_collection $DB_DSN | gzip -c > item_collection.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t  collection_type $DB_DSN | gzip -c > collection_type.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t  item_collection_item $DB_DSN | gzip -c > item_collection_item.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t  patient_item_collection_link $DB_DSN | gzip -c > patient_item_collection_link.dump.sql.gz
pg_dump -h $DB_HOST -U $DB_USER -t  order_result_stat $DB_DSN | gzip -c > order_result_stat.dump.sql.gz
