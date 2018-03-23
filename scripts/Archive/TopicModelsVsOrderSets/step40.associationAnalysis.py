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

from medinfo.cpoe.analysis.RecommendationClassificationAnalysis import RecommendationClassificationAnalysis;

NUM_RECOMMENDATIONS = 10;
RESULT_DIR = "results";

def main_associationRec(argv):
    validateFilename = argv[1]; # e.g., sourceData/first24hourItems.2013.-12345.tab.gz

    mod = RecommendationClassificationAnalysis();
    sortOptions = ["prevalence","PPV","OR","RR","P-YatesChi2-NegLog"];
    for sortOption in sortOptions:
        subargv = ["RecommendationClassificationAnalysis.py", "-P", validateFilename, "-r", str(NUM_RECOMMENDATIONS), "-R", "ItemAssociationRecommender", "-a", "weighted", "-t", "86400", "-p", "patient_", 
                    "-s", sortOption, RESULT_DIR+"/recClassification.ItemAssociationRecommender.%s.tab.gz" % sortOption]
        mod.main(subargv);

if __name__ == "__main__":
    main_associationRec(sys.argv);
