"""
Shell script to run several processes
"""
import sys,os;
import time;
from medinfo.common.Util import stdOpen, log, ProgressDots;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.db.Model import RowItemModel;
from medinfo.db.Model import RowItemFieldComparator, columnFromModelList;
from medinfo.db import DBUtil;

from medinfo.analysis.ConcatenateDataFiles import ConcatenateDataFiles;
from medinfo.analysis.SQLQueryDataFile import SQLQueryDataFile;
from medinfo.analysis.BatchTTests import BatchTTests;

BASE_RESULT_DIR = "results/byOrderSets/";
RESULT_DIRS = \
    [   BASE_RESULT_DIR+"01minutes/",
        BASE_RESULT_DIR+"30minutes/",
        BASE_RESULT_DIR+"60minutes/",
        BASE_RESULT_DIR+"120minutes/",
        BASE_RESULT_DIR+"240minutes/",
        BASE_RESULT_DIR+"480minutes/",
        BASE_RESULT_DIR+"960minutes/",
        BASE_RESULT_DIR+"1440minutes/",
        BASE_RESULT_DIR+"timeMatched/",
    ];
RESULT_BASENAME = "recClassification.byOrderSets";
FILELIST_FILENAME = "resultFileList.txt";
CONCATENATE_FILENAME = "concatenatedResults.tab.gz";
FILTERED_FILENAME = "filteredResults.tab.gz";   # Screen out rows with 0 verify / recommended items
TTEST_FILENAME = "ttests.tab.gz";

#DATA_QUERY = "select * from data where numQueryItems <> 0 and numVerifyItems <> 0 and numRecommendedItems <> 0";
# Add normalized precision calculations. Obtuse functions based on absolute values to simulate min / max functions for two input values
DATA_QUERY = """select *, 
    (tp+0.0) / ( ((numVerifyItems+numRecommendedItems) - abs(numVerifyItems-numRecommendedItems) ) / 2 ) as normalprecision
    from data 
    where numQueryItems <> 0 and numVerifyItems <> 0 and numRecommendedItems <> 0""";

LABEL_COLS = "_s,_m";  # Sort field separates methods. _m for topic model variant. Underscore instead of dash for SQL query filter accomodation
VALUE_COLS = "numqueryitems,numverifyitems,numrecommendeditems,tp,precision,recall,normalprecision,weightrecall,roc_auc";
MATCH_COLS = "patient_id,order_set_id";
BASE_LABELS = "None,None";

def main_concatenate(argv):
    mod = ConcatenateDataFiles();
    for resultDir in RESULT_DIRS:
        fileListFile = stdOpen(resultDir+FILELIST_FILENAME, "w");
        for filename in os.listdir(resultDir):
            if filename.startswith(RESULT_BASENAME):  
                print >> fileListFile, resultDir+filename;
        fileListFile.close();
        subargv = ["ConcatenateDataFiles.py","-o",resultDir+CONCATENATE_FILENAME];
        subargv.append(resultDir+FILELIST_FILENAME);
        mod.main(subargv);

def main_filter(argv):
    mod = SQLQueryDataFile();
    for resultDir in RESULT_DIRS:
        subargv = ["SQLQueryDataFile.py", "-q", DATA_QUERY];
        subargv.extend([resultDir+CONCATENATE_FILENAME, resultDir+FILTERED_FILENAME]);
        mod.main(subargv);

def main_ttests(argv):
    mod = BatchTTests();
    for resultDir in RESULT_DIRS:
        subargv = ["BatchTTests.py", "-l",LABEL_COLS, "-v",VALUE_COLS, "-m",MATCH_COLS, "-b", BASE_LABELS];
        subargv.extend([resultDir+FILTERED_FILENAME, resultDir+TTEST_FILENAME]);
        mod.main(subargv);

def main_mergeTTestResults(argv):
    mod = ConcatenateDataFiles();
    fileListFile = stdOpen(BASE_RESULT_DIR+FILELIST_FILENAME, "w");
    for resultDir in RESULT_DIRS:
        print >> fileListFile, resultDir+TTEST_FILENAME;
    fileListFile.close();
    subargv = ["ConcatenateDataFiles.py","-o", BASE_RESULT_DIR+CONCATENATE_FILENAME];
    subargv.append(BASE_RESULT_DIR+FILELIST_FILENAME);
    mod.main(subargv);

if __name__ == "__main__":
    main_concatenate(sys.argv);
    main_filter(sys.argv);
    main_ttests(sys.argv);
    main_mergeTTestResults(sys.argv);
