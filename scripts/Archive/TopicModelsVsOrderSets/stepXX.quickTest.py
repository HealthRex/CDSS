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

def main_quickTest(argv):
    modelFilename = argv[1];
    modeler = TopicModel();

    timer = time.time();
    (model, docCountByWordId) = modeler.loadModelAndDocCounts(modelFilename);
    timer = time.time() - timer;
    log.info("%.2f seconds to load",timer);
    
    timer = time.time();
    weightByItemIdByTopicId = modeler.generateWeightByItemIdByTopicId(model, 100);
    timer = time.time() - timer;
    log.info("%.2f seconds to generate weights",timer);

    for i in xrange(3):
        prog = ProgressDots();
        for (topicId, weightByItemId) in weightByItemIdByTopicId.iteritems():
            for (itemId, itemWeight) in weightByItemId.iteritems():
                prog.update();
        prog.printStatus();
    
    """
    for i in xrange(3):
        prog = ProgressDots();
        for (topicId, topicItems) in modeler.enumerateTopics(model, 100):
            for (itemId, itemScore) in topicItems:
                prog.update();
        prog.printStatus();
    """
   
if __name__ == "__main__":
    main_quickTest(sys.argv);
