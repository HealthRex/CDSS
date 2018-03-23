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

from medinfo.cpoe.TopicModel import TopicModel;
from medinfo.cpoe.analysis.TopicModelAnalysis import TopicModelAnalysis;
from medinfo.cpoe.analysis.PreparePatientItems import PreparePatientItems;
from medinfo.cpoe.analysis.RecommendationClassificationAnalysis import RecommendationClassificationAnalysis;

NUM_RECOMMENDATIONS = 10;

#numTopicsOptions = [0,2,4,8,16,32,64,128,256,512];
numTopicsOptions = [512,1024,2048,4096];

RESULT_DIR = "results";

def main_topicModelAnalysis(argv):
    baseModelFilename = argv[1];    # e.g., models/topicModel.first24hourItems.2013.1234567890.filter.bow.gz.%sTopic.model
    validateFilename = argv[2]; # e.g., sourceData/first24hourItems.2013.-12345.tab.gz

    instance = TopicModelAnalysis();

    for numTopics in numTopicsOptions:
        modelFilename = baseModelFilename % numTopics;
        argv = ["TopicModelAnalysis.py", "-M",modelFilename, "-r",str(NUM_RECOMMENDATIONS), "-s","tf", validateFilename, RESULT_DIR+"/recClassification.tf.%s.%s" % (os.path.basename(modelFilename),os.path.basename(validateFilename))];
        instance.main(argv);

        # Again with TF*IDF score weights
        argv = ["TopicModelAnalysis.py", "-M",modelFilename, "-r",str(NUM_RECOMMENDATIONS), "-s","tfidf", validateFilename, RESULT_DIR+"/recClassification.tfidf.%s.%s" % (os.path.basename(modelFilename),os.path.basename(validateFilename))];
        instance.main(argv);

if __name__ == "__main__":
    main_topicModelAnalysis(sys.argv);
