rem For backup purposes, core adapted tables (original raw tables from STRIDE separated)

set DB_HOST=localhost
set DB_PORT=5432
set DB_DSN=medinfo
set DB_USER=jonc101

mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% clinical_item_category > clinical_item_category.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% clinical_item > clinical_item.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% patient_item > patient_item.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% clinical_item_link > clinical_item_link.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% backup_link_patient_item > backup_link_patient_item.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% clinical_item_association > clinical_item_association.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% item_collection > item_collection.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% collection_type > collection_type.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% item_collection_item > item_collection_item.dump.sql

rem pg_dump -i -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -a -F p -x -O -t clinical_item_category -f clinical_item_category.dump.sql %DB_DSN%
