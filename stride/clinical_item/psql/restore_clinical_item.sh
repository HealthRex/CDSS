#!/bin/sh -x
# Define constants for connecting to database from which to dump tables.
# For example, if dumping from local database named test_database and accessing
# as user test_user, you would use the following lines:
# export DB_HOST=localhost
# export DB_DSN=test_database
# export DB_USER=test_user
export DB_HOST=localhost
export DB_DSN=database
export DB_USER=user

# Pipe the uncompressed data from gzip to psql to load to database.
gzip -d -c clinical_item_category.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c clinical_item.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c clinical_item_link.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c patient_item.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c backup_link_patient_item.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c clinical_item_association.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c item_collection.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c collection_type.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c item_collection_item.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c patient_item_collection_link.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c order_result_stat.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c data_cache.schema.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN

# Existing PostgreSQL Table Level Dumps do not restore indexes (only table constraints)?
#	May need to add indexes and then recreate the table dumps
psql -h $DB_HOST -U $DB_USER -f indices/clinical_item.indices.sql $DB_DSN
psql -h $DB_HOST -U $DB_USER -f indices/clinical_item_association.indices.sql $DB_DSN
psql -h $DB_HOST -U $DB_USER -f indices/clinical_item_category.indices.sql $DB_DSN
psql -h $DB_HOST -U $DB_USER -f indices/item_collection_item.indices.sql $DB_DSN
psql -h $DB_HOST -U $DB_USER -f indices/patient_item.indices.sql $DB_DSN
psql -h $DB_HOST -U $DB_USER -f indices/patient_item_collection_link.indices.sql $DB_DSN
