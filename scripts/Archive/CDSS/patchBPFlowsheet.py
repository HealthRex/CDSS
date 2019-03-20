from medinfo.common.Util import *;

ifs = stdOpen("JChenv3_BP_Table1.csv.gz")
ofs = stdOpen("JChenv3_BP_Table1.namepatch.csv.gz","w")

ifs.readline(); # Read and discard header, replacing with below to change BP_TYPE to FLOWSHEET_NAME for consistency with other flowsheet items
print >> ofs, '"PAT_ENC_CSN_ANON_ID","PAT_ANON_ID","FLO_MEAS_ID","FLOWSHEET_NAME","FLOWSHEET_VALUE","SHIFTED_DT_TM"';

prog = ProgressDots();
for line in ifs:
    ofs.write(line);
    prog.update();
prog.printStatus();
