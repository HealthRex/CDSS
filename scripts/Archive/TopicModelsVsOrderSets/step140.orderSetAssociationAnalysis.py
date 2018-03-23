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

from medinfo.cpoe.analysis.RecommendationClassificationAnalysis import RecommendationClassificationAnalysis;

RESULT_DIR = "results";

VALIDATE_FILENAME = "sourceData/first24hourOrderSets.2013.-12345.tab.gz";
#VALIDATE_FILENAME = "sourceData/first24hourOrderSets.2013.sample.tab.gz";

OUTPUT_BASENAME = "recClassification.byOrderSets";

def main_associationRec(argv):
    validateFilename = VALIDATE_FILENAME; # e.g., sourceData/first24hourItems.2013.-12345.tab.gz

    mod = RecommendationClassificationAnalysis();
    sortOptions = ["prevalence","PPV","OR","RR","P-YatesChi2-NegLog"];
    for sortOption in sortOptions:
        subargv = ["RecommendationClassificationAnalysis.py", "-P", validateFilename, "--numRecsByOrderSet", "-R", "ItemAssociationRecommender", "-a", "weighted", "-t", "86400", "-p", "patient_", 
                    "-s", sortOption, RESULT_DIR+"/%s.ItemAssociationRecommender.%s.tab.gz" % (OUTPUT_BASENAME, sortOption) ]
        mod.main(subargv);

if __name__ == "__main__":
    main_associationRec(sys.argv);
