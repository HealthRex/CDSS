"""
Extract order set usage instances, items leading up to the instance to query trained association model, and items after the instance for evaluation
"""
import sys,os;
import time;
from medinfo.common.Const import COMMENT_TAG;
from medinfo.common.Util import stdOpen, log, ProgressDots;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.db.Model import RowItemModel;
from medinfo.db.Model import RowItemFieldComparator, columnFromModelList;
from medinfo.db import DBUtil;

from medinfo.cpoe.analysis.PreparePatientItems import PreparePatientItems;

EXCLUDE_CATEGORY_DESCRIPTIONS = ['Nursing','Discharge','Transfer','BB Call Slip','Transport','Admission','Pharmacy Supplies','Diet Communication'];
EXCLUDE_CATEGORY_IDS = [4,5,11,13,18,23,46,66];    # From 5 year data set
EXCLUDE_CATEGORY_IDS_STR = str.join(',', [str(catId) for catId in EXCLUDE_CATEGORY_IDS] );   # Concatenate into string form

ADMIT_DX_CATEGORY_ID = 2;
DEATH_ITEM_ID = 72416;
DEMOGRAPHICS_CATEGORY_ID = 159;

# 2010-2013 data range
START_DATE_STR = "2010-01-01"
END_DATE_STR = "2014-01-01"

SOURCE_DATA_DIR = "/Users/jwang/Desktop/Chen/Top_vs_Bottom_Study/Results_Revisions/Analysis_Better_Than_Expected";

EVAL_TIMESPAN = 86400; # query window to extract model predictions (24 hours)
VERIFY_TIMESPAN = 86400 # evaluation window for items to validate model predictions

BASE_OUTPUT_NAME = "OrdersetItems.2010-2013.q%d.v%d" % (EVAL_TIMESPAN, VERIFY_TIMESPAN);

def main_prepPatientItems(argv):
    prep = PreparePatientItems();
    # for i in xrange(-9,10):
    prep.main(["PreparePatientItems","-S",START_DATE_STR, "-E",END_DATE_STR, "-O", "-p",str(DEMOGRAPHICS_CATEGORY_ID),"-c", str(ADMIT_DX_CATEGORY_ID), "-Q", str(EVAL_TIMESPAN), "-V", str(VERIFY_TIMESPAN), "%s/better_than_expected_patients.csv" % (SOURCE_DATA_DIR), "%s/%s.tab.gz" % (SOURCE_DATA_DIR, BASE_OUTPUT_NAME)]);
    
    # # Convert to (filtered) Bag of Words
    # for i in xrange(-9,10):
    #     prep.main(["PreparePatientItems","-B","qvo","-X", EXCLUDE_CATEGORY_IDS_STR,"%s/%s.%s.tab.gz" % (SOURCE_DATA_DIR,BASE_OUTPUT_NAME,i),"%s/%s.%s.filter.bow.gz" % (SOURCE_DATA_DIR,BASE_OUTPUT_NAME,i)]);

    # Concatenate batch of files
    # ofs = stdOpen("%s/%s.1234567890.filter.bow.gz" % (SOURCE_DATA_DIR, BASE_OUTPUT_NAME),"w");
    # for i in [1,2,3,4,5,6,7,8,9,0]:
    #     ifs = stdOpen("%s/%s.%d.filter.bow.gz" % (SOURCE_DATA_DIR, BASE_OUTPUT_NAME, i) );
    #     ofs.write(ifs.read());
    #     ifs.close();
    # ofs.close();
    
    # # For comment and header row of csv files, drop repeats
    # baseIds = [-1,-2,-3,-4,-5];
    # ofs = stdOpen("%s/%s.-12345.tab.gz" % (SOURCE_DATA_DIR,BASE_OUTPUT_NAME),"w");
    # isHeaderRowWritten = False;
    # for baseId in baseIds:
    #     ifs = stdOpen("%s/%s.%d.tab.gz" % (SOURCE_DATA_DIR,BASE_OUTPUT_NAME,baseId) );
    #     for iLine, line in enumerate(ifs):
    #         if not line.startswith(COMMENT_TAG):    # Skip comment lines
    #             if line[0].isalpha():   # Starts with a letter/label, must be header row, not data
    #                 if isHeaderRowWritten:
    #                     continue;   # Skip text/header rows, except for the first one encountered
    #                 else:
    #                     isHeaderRowWritten = True;
    #             ofs.write(line);
    #     ifs.close();
    # ofs.close();
 
if __name__ == "__main__":
    main_prepPatientItems(sys.argv);
