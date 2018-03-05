"""
Shell script to run several processes
"""
import sys,os;
import time;
from scipy.stats import ttest_rel, ttest_ind;
from numpy import mean;
from medinfo.common.Util import stdOpen, log, ProgressDots;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.db.Model import RowItemModel;
from medinfo.db.Model import RowItemFieldComparator, columnFromModelList;
from medinfo.db import DBUtil;

from medinfo.cpoe.analysis.OrderSetRecommenderClassificationAnalysis import OrderSetRecommenderClassificationAnalysis;
from medinfo.cpoe.analysis.OrderSetUsageAnalysis import OrderSetUsageAnalysis;

NUM_RECOMMENDATIONS = 10;
RESULT_DIR = "results";

def main_associationRec(argv):
    validateFilename = argv[1]; # e.g., sourceData/first24hourItems.2013.-12345.tab.gz

    mod = OrderSetRecommenderClassificationAnalysis();
    sortOptions = ["tf","tfidf"];
    for sortOption in sortOptions:
        subargv = ["OrderSetRecommenderClassificationAnalysis.py", "-r", str(NUM_RECOMMENDATIONS), "-s", sortOption, 
                    validateFilename, RESULT_DIR+"/recClassification.OrderSetRecommender.%s.tab.gz" % sortOption]
        mod.main(subargv);

    mod = OrderSetUsageAnalysis();
    numRecsOptions = [0,NUM_RECOMMENDATIONS];
    sortFieldOptions = ["patient_count","name"];
    #numRecsOptions = [0];
    #sortFieldOptions = ["name"];
    #for numRecsOption in numRecsOptions:
    #    for sortField in sortFieldOptions:
    #        subargv = ["OrderSetUsageAnalysis.py", "-r", str(numRecsOption), "-s", sortField];
    #        subargv.extend([validateFilename, RESULT_DIR+"/recClassification.OrderSetUsage.%sRecs.%s.tab.gz" % (numRecsOption,sortField)]);
    #        mod.main(subargv);

if __name__ == "__main__":
    main_associationRec(sys.argv);
