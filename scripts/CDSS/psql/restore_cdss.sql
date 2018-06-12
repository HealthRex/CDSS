export DB_HOST=localhost
export DB_DSN=database
export DB_USER=user

gzip -d -c clinical_item_category.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c clinical_item.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c clinical_item_link.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c patient_item.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c backup_link_patient_item.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c clinical_item_assocation.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c item_collection.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c collection_type.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c item_collection_item.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c patient_item_collection_link.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
gzip -d -c order_result_stat.dump.sql.gz | psql -h $DB_HOST -U $DB_USER $DB_DSN
