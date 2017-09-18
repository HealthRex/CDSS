rem For backup purposes, user simulation setup and recording data

set DB_HOST=localhost
set DB_PORT=5432
set DB_DSN=medinfo-5year-time
set DB_USER=jonc101

pg_dump -h %DB_HOST% -U %DB_USER% -t sim_user %DB_DSN% | gzip -c > sim_user.dump.sql.gz
pg_dump -h %DB_HOST% -U %DB_USER% -t sim_patient %DB_DSN% | gzip -c > sim_patient.dump.sql.gz
pg_dump -h %DB_HOST% -U %DB_USER% -t sim_state %DB_DSN% | gzip -c > sim_state.dump.sql.gz
pg_dump -h %DB_HOST% -U %DB_USER% -t sim_patient_state %DB_DSN% | gzip -c > sim_patient_state.dump.sql.gz
pg_dump -h %DB_HOST% -U %DB_USER% -t sim_state_transition %DB_DSN% | gzip -c > sim_state_transition.dump.sql.gz
pg_dump -h %DB_HOST% -U %DB_USER% -t sim_note_type %DB_DSN% | gzip -c > sim_note_type.dump.sql.gz
pg_dump -h %DB_HOST% -U %DB_USER% -t sim_note %DB_DSN% | gzip -c > sim_note.dump.sql.gz
pg_dump -h %DB_HOST% -U %DB_USER% -t sim_result %DB_DSN% | gzip -c > sim_result.dump.sql.gz
pg_dump -h %DB_HOST% -U %DB_USER% -t sim_state_result %DB_DSN% | gzip -c > sim_state_result.dump.sql.gz
pg_dump -h %DB_HOST% -U %DB_USER% -t sim_order_result_map %DB_DSN% | gzip -c > sim_order_result_map.dump.sql.gz
pg_dump -h %DB_HOST% -U %DB_USER% -t sim_patient_order %DB_DSN% | gzip -c > sim_patient_order.dump.sql.gz
