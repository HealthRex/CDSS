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

from medinfo.cpoe.analysis.OrderSetRecommenderClassificationAnalysis import OrderSetRecommenderClassificationAnalysis;
from medinfo.cpoe.analysis.OrderSetUsageAnalysis import OrderSetUsageAnalysis;

RESULT_DIR = "results";
VALIDATE_FILENAME = "sourceData/first24hourOrderSets.2013.-12345.tab.gz";
#VALIDATE_FILENAME = "sourceData/first24hourOrderSets.2013.sample.tab.gz";
OUTPUT_BASENAME = "recClassification.byOrderSets";

def main_associationRec(argv):
    validateFilename = VALIDATE_FILENAME; # e.g., sourceData/first24hourItems.2013.-12345.tab.gz

    mod = OrderSetUsageAnalysis();
    subargv = ["OrderSetUsageAnalysis.py", "--numRecsByOrderSet"];
    subargv.extend([validateFilename, RESULT_DIR+"/%s.OrderSetUsage.tab.gz" % (OUTPUT_BASENAME)]);
    mod.main(subargv);

if __name__ == "__main__":
    main_associationRec(sys.argv);
