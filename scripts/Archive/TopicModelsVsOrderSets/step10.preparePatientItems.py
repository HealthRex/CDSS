"""
Shell script to run several processes
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

START_DATE_STR = "2013-01-01"
END_DATE_STR = "2014-01-01"
BASE_YEAR = 2013;

#QUERY_TIME = 14400;
#VERIFY_TIME = 86400;

QUERY_TIME = 14400;
#QUERY_TIME = 28800;
#QUERY_TIME = 57600;
#QUERY_TIME = 86400;
VERIFY_TIME = QUERY_TIME;

SOURCE_DATA_DIR = "sourceData";

def main_prepPatientItems(argv):
    prep = PreparePatientItems();
    for i in xrange(-9,10):
        prep.main(["PreparePatientItems","-S",START_DATE_STR, "-E",END_DATE_STR, "-p",str(DEMOGRAPHICS_CATEGORY_ID),"-c", str(ADMIT_DX_CATEGORY_ID), "-Q", str(QUERY_TIME), "-V", str(VERIFY_TIME), "-o", str(DEATH_ITEM_ID), "-t", "2592000", "%s/patientIds.5year.%s.tab.gz" % (SOURCE_DATA_DIR, i), "%s/firstItems.q%s.v%s.%s.%s.tab.gz" % (SOURCE_DATA_DIR, QUERY_TIME, VERIFY_TIME, BASE_YEAR, i)]);
    
    # Convert to (filtered) Bag of Words
    for i in xrange(-9,10):
        prep.main(["PreparePatientItems","-B","qvo","-X", EXCLUDE_CATEGORY_IDS_STR,"%s/firstItems.q%s.v%s.%s.%d.tab.gz" % (SOURCE_DATA_DIR,QUERY_TIME,VERIFY_TIME,BASE_YEAR,i),"%s/firstItems.q%s.v%s.%s.%d.filter.bow.gz" % (SOURCE_DATA_DIR,QUERY_TIME,VERIFY_TIME,BASE_YEAR,i)]);

    # Concatenate batch of files
    ofs = stdOpen("%s/firstItems.q%s.v%s.%s.1234567890.filter.bow.gz" % (SOURCE_DATA_DIR, QUERY_TIME, VERIFY_TIME, BASE_YEAR),"w");
    for i in [1,2,3,4,5,6,7,8,9,0]:
        ifs = stdOpen("%s/firstItems.q%s.v%s.%s.%d.filter.bow.gz" % (SOURCE_DATA_DIR,QUERY_TIME,VERIFY_TIME,BASE_YEAR,i) );
        ofs.write(ifs.read());
        ifs.close();
    ofs.close();
    
    # For comment and header row of csv files, drop repeats
    baseIds = [-1,-2,-3,-4,-5];
    ofs = stdOpen("%s/firstItems.q%s.v%s.%s.-12345.tab.gz" % (SOURCE_DATA_DIR,QUERY_TIME,VERIFY_TIME,BASE_YEAR),"w");
    isHeaderRowWritten = False;
    for baseId in baseIds:
        ifs = stdOpen("%s/firstItems.q%s.v%s.%s.%d.tab.gz" % (SOURCE_DATA_DIR,QUERY_TIME,VERIFY_TIME,BASE_YEAR,baseId) );
        for iLine, line in enumerate(ifs):
            if not line.startswith(COMMENT_TAG):    # Skip comment lines
                if line[0].isalpha():   # Starts with a letter/label, must be header row, not data
                    if isHeaderRowWritten:
                        continue;   # Skip text/header rows, except for the first one encountered
                    else:
                        isHeaderRowWritten = True;
                ofs.write(line);
        ifs.close();
    ofs.close();
 
if __name__ == "__main__":
    main_prepPatientItems(sys.argv);
