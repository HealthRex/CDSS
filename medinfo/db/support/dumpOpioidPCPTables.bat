rem For backup purposes, core adapted tables (original raw tables from STRIDE separated)

set DB_HOST=localhost
set DB_PORT=5432
set DB_DSN=opioidrx
set DB_USER=jonc101

mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% stride_icd9_cm > stride_icd9_cm.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% stride_mapped_meds > stride_mapped_meds.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% stride_order_med > stride_order_med.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% stride_order_proc_drug_screen > stride_order_proc_drug_screen.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% stride_order_proc_referrals_n_consults > stride_order_proc_referrals_n_consults.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% stride_pat_enc > stride_pat_enc.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% stride_patient > stride_patient.dump.sql
mysqldump -h %DB_HOST% -u %DB_USER% -p %DB_DSN% stride_problem_list > stride_problem_list.dump.sql

rem pg_dump -i -h %DB_HOST% -p %DB_PORT% -U %DB_USER% -a -F p -x -O -t clinical_item_category -f clinical_item_category.dump.sql %DB_DSN%
