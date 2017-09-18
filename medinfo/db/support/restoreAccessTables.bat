set DB_HOST=127.0.0.1
set DB_DSN=medinfo
set DB_USER=jonc101

mysql -h %DB_HOST% -u %DB_USER% -p %DB_DSN% < user.dump.sql
mysql -h %DB_HOST% -u %DB_USER% -p %DB_DSN% < rotation.dump.sql
mysql -h %DB_HOST% -u %DB_USER% -p %DB_DSN% < user_rotation.dump.sql
mysql -h %DB_HOST% -u %DB_USER% -p %DB_DSN% < metric_group.dump.sql
mysql -h %DB_HOST% -u %DB_USER% -p %DB_DSN% < metric.dump.sql
mysql -h %DB_HOST% -u %DB_USER% -p %DB_DSN% < metric_line.dump.sql
mysql -h %DB_HOST% -u %DB_USER% -p %DB_DSN% < access_log.dump.sql
