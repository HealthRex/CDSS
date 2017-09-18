# For backup purposes, core adapted tables (original raw tables from STRIDE separated)

export DB_HOST=medinfo-5year-time.cxkturzva06i.us-east-1.rds.amazonaws.com
export DB_PORT=5432
export DB_DSN=medinfo
export DB_USER=jonc101

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



#mysqldump -h $DB_HOST -u $DB_USER -p $DB_DSN clinical_item_category > clinical_item_category.dump.sql
#mysqldump -h $DB_HOST -u $DB_USER -p $DB_DSN clinical_item > clinical_item.dump.sql
#mysqldump -h $DB_HOST -u $DB_USER -p $DB_DSN clinical_item_link > clinical_item_link.dump.sql
#mysqldump -h $DB_HOST -u $DB_USER -p $DB_DSN patient_item > patient_item.dump.sql
#mysqldump -h $DB_HOST -u $DB_USER -p $DB_DSN backup_link_patient_item > backup_link_patient_item.dump.sql
#mysqldump -h $DB_HOST -u $DB_USER -p $DB_DSN clinical_item_association > clinical_item_association.dump.sql
#mysqldump -h $DB_HOST -u $DB_USER -p $DB_DSN item_collection > item_collection.dump.sql
#mysqldump -h $DB_HOST -u $DB_USER -p $DB_DSN collection_type > collection_type.dump.sql
#mysqldump -h $DB_HOST -u $DB_USER -p $DB_DSN item_collection_item > item_collection_item.dump.sql
