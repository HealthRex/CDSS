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

SOURCE_DATA_DIR = "sourceData/";
#MODEL_DIR = "D:\Box Sync\SecureFiles\CDSS\models";
MODEL_DIR = "D:/Documents/tempModels";

#INPUT_FILENAME = "first24HourItems.2013.1.filter.bow.gz";
INPUT_FILENAME = "first24HourItems.2013.1234567890.filter.bow.gz";
#INPUT_FILENAME = "firstItems.q14400.v14400.2013.1234567890.filter.bow.gz";
#INPUT_FILENAME = "firstItems.q28800.v28800.2013.1234567890.filter.bow.gz";
#INPUT_FILENAME = "firstItems.q57600.v57600.2013.1234567890.filter.bow.gz";
#INPUT_FILENAME = "firstItems.q86400.v86400.2013.1234567890.filter.bow.gz";

#numTopicsOptions = [0,2,4,8,16,32,64,128,256,512,1024,2048];
numTopicsOptions = [2,4,8,16,32,64,128,256,512,1024,2048];

def main_buildTopicModel(argv):
    bowInputFilename = SOURCE_DATA_DIR+INPUT_FILENAME;

    mod = TopicModel();
    for numTopics in numTopicsOptions:
        subargv = ["TopicModel", "-n", str(numTopics)];
        subargv.extend([bowInputFilename, MODEL_DIR+"/topicModel."+os.path.basename(bowInputFilename)+".%dTopic.model" % (numTopics), ]);
        mod.main(subargv);
    return mod.model;

if __name__ == "__main__":
    model = main_buildTopicModel(sys.argv);
