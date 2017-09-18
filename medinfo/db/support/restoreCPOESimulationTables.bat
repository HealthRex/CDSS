set DB_HOST=127.0.0.1
set DB_DSN=medinfo-5year-time
set DB_USER=jonc101

gzip -d -c sim_user.dump.sql.gz | psql -h %DB_HOST% -U %DB_USER% %DB_DSN% 
gzip -d -c sim_patient.dump.sql.gz | psql -h %DB_HOST% -U %DB_USER% %DB_DSN% 
gzip -d -c sim_state.dump.sql.gz | psql -h %DB_HOST% -U %DB_USER% %DB_DSN% 
gzip -d -c sim_patient_state.dump.sql.gz | psql -h %DB_HOST% -U %DB_USER% %DB_DSN% 
gzip -d -c sim_state_transition.dump.sql.gz | psql -h %DB_HOST% -U %DB_USER% %DB_DSN% 
gzip -d -c sim_note_type.dump.sql.gz | psql -h %DB_HOST% -U %DB_USER% %DB_DSN% 
gzip -d -c sim_note.dump.sql.gz | psql -h %DB_HOST% -U %DB_USER% %DB_DSN% 
gzip -d -c sim_result.dump.sql.gz | psql -h %DB_HOST% -U %DB_USER% %DB_DSN% 
gzip -d -c sim_state_result.dump.sql.gz | psql -h %DB_HOST% -U %DB_USER% %DB_DSN% 
gzip -d -c sim_order_result_map.dump.sql.gz | psql -h %DB_HOST% -U %DB_USER% %DB_DSN% 
gzip -d -c sim_patient_order.dump.sql.gz | psql -h %DB_HOST% -U %DB_USER% %DB_DSN% 
