<<<<<<< .mine
export DB_HOST=localhost
export DB_DSN=medinfo
||||||| .r1798
export DB_HOST=medinfo-34567890.cxkturzva06i.us-east-1.rds.amazonaws.com
export DB_DSN=medinfo
=======
export DB_HOST=127.0.0.1
export DB_DSN=medinfo-5year-time
>>>>>>> .r1952
export DB_USER=shivaal

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
