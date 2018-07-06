rem For backup purposes, core adapted tables (original raw tables from STRIDE separated)

set DB_HOST=localhost
set DB_PORT=5432
set DB_DSN=medinfo-5year-time
set DB_USER=jonc101

rem Initialization data on general patient simulation models, deposit into medinfo/db/definition/simdata
pg_dump -i -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -a -F p -x -O -t sim_note_type -f sim_note_type.dump.sql %DB_DSN%
pg_dump -i -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -a -F p -x -O -t sim_note -f sim_note.dump.sql %DB_DSN%
pg_dump -i -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -a -F p -x -O -t sim_result -f sim_result.dump.sql %DB_DSN%
pg_dump -i -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -a -F p -x -O -t sim_state_result -f sim_state_result.dump.sql %DB_DSN%
pg_dump -i -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -a -F p -x -O -t sim_order_result_map -f sim_order_result_map.dump.sql %DB_DSN%
pg_dump -i -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -a -F p -x -O -t sim_state_transition -f sim_state_transition.dump.sql %DB_DSN%
pg_dump -i -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -a -F p -x -O -t sim_state -f sim_state.dump.sql %DB_DSN%

rem Specific user records
pg_dump -i -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -a -F p -x -O -t sim_patient -f sim_patient.dump.sql %DB_DSN%
pg_dump -i -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -a -F p -x -O -t sim_patient_state -f sim_patient_state.dump.sql %DB_DSN%
pg_dump -i -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -a -F p -x -O -t sim_user -f sim_user.dump.sql %DB_DSN%
pg_dump -i -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -a -F p -x -O -t sim_patient_order -f sim_patient_order.dump.sql %DB_DSN%
