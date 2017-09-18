# For backup purposes, core adapted tables (original raw tables from STRIDE separated)

export DB_HOST=accesslog.cxkturzva06i.us-east-1.rds.amazonaws.com
export DB_PORT=3306
export DB_DSN=emr_access
export DB_USER=jonc101

mysqldump -h $DB_HOST -u $DB_USER -p $DB_DSN user > user.dump.sql
mysqldump -h $DB_HOST -u $DB_USER -p $DB_DSN rotation > rotation.dump.sql
mysqldump -h $DB_HOST -u $DB_USER -p $DB_DSN user_rotation > user_rotation.dump.sql
mysqldump -h $DB_HOST -u $DB_USER -p $DB_DSN metric_group > metric_group.dump.sql
mysqldump -h $DB_HOST -u $DB_USER -p $DB_DSN metric > metric.dump.sql
mysqldump -h $DB_HOST -u $DB_USER -p $DB_DSN metric_line > metric_line.dump.sql
mysqldump -h $DB_HOST -u $DB_USER -p $DB_DSN access_log > access_log.dump.sql
