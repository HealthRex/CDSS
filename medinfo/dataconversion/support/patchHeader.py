"""
# Utility to assist in modifying just the first line of a file to patch header row issues.  Specific issue addressed
#   Came up as below example:
#
#   Patch header rows (older 1 year data.  Does not appear necessary for 5 year data, but retaining notes on method)
#           order_proc.txt (Had a | header separator instead of tab)
#           order_med (remove rx. prefixes from headers)
#
#   Method (avoid creating large copy of data file) outlined in Unix below, or use this patchHeader.py
#       1. Extract header line
#       2. Edit header line in editor and copy contents
#       3. Delete old header line from file
#       4. Merge patched header back into data file

## Equivalent Unix commands?
head -n 1 ../data/STRIDE/order_proc1yr.txt > header.proc.txt
vi header.proc.txt
sed -i '1 d' ../data/STRIDE/order_proc1yr.txt
cat header.proc.txt ../data/STRIDE/order_proc1yr.txt > ../data/STRIDE/order_proc1yr.patch.txt
sed -i '1 i order_proc_id\tpat_id\tpat_enc_csn_id\tordering_date\torder_type\tproc_id\tproc_code\tdescription\tdisplay_name\tcpt_code\tproc_cat_name\torder_class\tauthrzing_prov_id\tabnormal_yn\tlab_status\torder_status\tquantity\tfuture_or_stand\tstanding_exp_date\tstanding_occurs\tstand_orig_occur\tradiology_status\tproc_bgn_time\tproc_end_time\torder_inst\tstand_interval\tdiscrete_interval\tinstantiated_time\torder_time\tresult_time\tproc_start_time\tproblem_list_id\tproc_ending_time\tchng_order_proc_id\tlast_stand_perf_dt\tlast_stand_perf_tm\tparent_ce_order_id\tordering_mode' ../data/STRIDE/order_proc1yr.txt

## Example Usage:
python patchHeader.py originalFile.txt headerFile.txt
<<<Manually Edit headerFile.txt to desired header>>>
python patchHeader.py originalFile.txt patchedFile.txt headerFile.txt
"""

import sys;
from medinfo.common.Util import ProgressDots, stdOpen;

oldDataFile = stdOpen(sys.argv[1]);
newDataFile = stdOpen(sys.argv[2],"w");
replaceHeaderFile = None;
if len(sys.argv) > 3:
    replaceHeaderFile = stdOpen(sys.argv[3]);

oldHeaderLine = oldDataFile.readline()

if replaceHeaderFile is None:
    # Don't have the header file to replace, so just extract the header line from the data file for manual editing
    newDataFile.write(oldHeaderLine);

else:
    # Have the replacement header to populate into a new data file
    newHeaderLine = replaceHeaderFile.readline();
    newDataFile.write(newHeaderLine);
    
    progress = ProgressDots();
    for line in oldDataFile:
        newDataFile.write(line);
        progress.update();
    progress.printStatus();
        
newDataFile.close();
