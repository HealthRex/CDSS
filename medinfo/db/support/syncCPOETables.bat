rem For backup purposes, core reagent models and rules should be dumped
rem    from a common central development server (since only developers should edit that content).

set SOURCE_COMPUTER=easyv1.ics.uci.edu
set SOURCE_PORT=6002
set SOURCE_DATABASE=reactiondev
set SOURCE_USERNAME=chenjh
set SOURCE_PASSWORD=ChemDB#2008

set TARGET_COMPUTER=easyv1.ics.uci.edu
set TARGET_PORT=6002
set TARGET_DATABASE=reaction_tutorial
set TARGET_USERNAME=chenjh
set TARGET_PASSWORD=ChemDB#2008

set TARGET_COMPUTER=localhost
set TARGET_PORT=5432
set TARGET_DATABASE=rex_update_20111123
set TARGET_USERNAME=jonc101
set TARGET_PASSWORD=1234

set SYNC_COMMAND=python ../codebase/medinfo/db/support/syncDatabaseTable.py -c %SOURCE_COMPUTER% -o %SOURCE_PORT% -d %SOURCE_DATABASE% -u %SOURCE_USERNAME% -p %SOURCE_PASSWORD% -C %TARGET_COMPUTER% -O %TARGET_PORT% -D %TARGET_DATABASE% -U %TARGET_USERNAME% -P %TARGET_PASSWORD% 

%SYNC_COMMAND% clinical_item_category
%SYNC_COMMAND% clinical_item
%SYNC_COMMAND% patient_item
%SYNC_COMMAND% clinical_item_association
