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

from medinfo.cpoe.TopicModel import TopicModel;
from medinfo.cpoe.analysis.TopicModelAnalysis import TopicModelAnalysis;
from medinfo.cpoe.analysis.PreparePatientItems import PreparePatientItems;
from medinfo.cpoe.analysis.RecommendationClassificationAnalysis import RecommendationClassificationAnalysis;

numTopicsOptions = [0,2,4,8,16,32,64,128,256,512,1024,2048];
#numTopicsOptions = [16,32,64];

RESULT_DIR = "results";

BASE_MODEL_FILENAMES = ["models/topicModel.first24hourItems.2013.1234567890.filter.bow.gz.%sTopic.model"];
VALIDATE_FILENAMES = ["sourceData/first24hourOrderSets.2013.-12345.tab.gz"];

""" # Time matched model alternative
BASE_MODEL_FILENAMES = \
    [   "models/topicModel.firstItems.q14400.v14400.2013.1234567890.filter.bow.gz.%sTopic.model",
        "models/topicModel.firstItems.q28800.v28800.2013.1234567890.filter.bow.gz.%sTopic.model",
        "models/topicModel.firstItems.q57600.v57600.2013.1234567890.filter.bow.gz.%sTopic.model",
        "models/topicModel.firstItems.q86400.v86400.2013.1234567890.filter.bow.gz.%sTopic.model",
    ];
VALIDATE_FILENAMES = \
    [   "sourceData/first24hourOrderSets.2013.q86400.v14400.-12345.tab.gz",
        "sourceData/first24hourOrderSets.2013.q86400.v28800.-12345.tab.gz",
        "sourceData/first24hourOrderSets.2013.q86400.v57600.-12345.tab.gz",
        "sourceData/first24hourOrderSets.2013.q86400.v86400.-12345.tab.gz",
    ];
"""

#BASE_MODEL_FILENAME = "D:\Box Sync\SecureFiles\CDSS\models/topicModel.first24hourItems.2013.1234567890.filter.bow.gz.%sTopic.model";
#VALIDATE_FILENAME = "sourceData/first24hourOrderSets.2013.sample.tab.gz";

OUTPUT_BASENAME = "recClassification.byOrderSets";

def main_topicModelAnalysis(argv):
    instance = TopicModelAnalysis();

    for baseModelFilename, validateFilename in zip(BASE_MODEL_FILENAMES, VALIDATE_FILENAMES):

        for numTopics in numTopicsOptions:
            modelFilename = baseModelFilename % numTopics;
            argv = ["TopicModelAnalysis.py", "-M",modelFilename, "--numRecsByOrderSet", "-s","tf", validateFilename, RESULT_DIR+"/%s.tf.%s.%s" % (OUTPUT_BASENAME, os.path.basename(modelFilename),os.path.basename(validateFilename))];
            instance.main(argv);

            # Again with TF*IDF score weights
            #argv = ["TopicModelAnalysis.py", "-M",modelFilename, "--numRecsByOrderSet", "-s","tfidf", validateFilename, RESULT_DIR+"/%s.tfidf.%s.%s" % (OUTPUT_BASENAME, os.path.basename(modelFilename),os.path.basename(validateFilename))];
            #instance.main(argv);

if __name__ == "__main__":
    main_topicModelAnalysis(sys.argv);
