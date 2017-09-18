rem For backup purposes, core adapted tables 

set DB_HOST=localhost
set DB_PORT=5432
set DB_DSN=emr_access
set DB_USER=jonc101

mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% user > user.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% rotation > rotation.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% user_rotation > user_rotation.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% metric_group > metric_group.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% metric > metric.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% metric_line > metric_line.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% access_log > access_log.dump.sql
