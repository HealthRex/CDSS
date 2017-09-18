export DB_HOST=accesslog.cxkturzva06i.us-east-1.rds.amazonaws.com
export DB_DSN=emr_access
export DB_USER=jonc101

mysql -h $DB_HOST -u $DB_USER -p $DB_DSN < user.dump.sql
mysql -h $DB_HOST -u $DB_USER -p $DB_DSN < rotation.dump.sql
mysql -h $DB_HOST -u $DB_USER -p $DB_DSN < user_rotation.dump.sql
mysql -h $DB_HOST -u $DB_USER -p $DB_DSN < metric_group.dump.sql
mysql -h $DB_HOST -u $DB_USER -p $DB_DSN < metric.dump.sql
mysql -h $DB_HOST -u $DB_USER -p $DB_DSN < metric_line.dump.sql
mysql -h $DB_HOST -u $DB_USER -p $DB_DSN < access_log.dump.sql
