"""
Shell script to run several processes
"""
import sys,os;
import time;
import json;
from cStringIO import StringIO;
from medinfo.common.Const import COMMENT_TAG;
from medinfo.common.Util import stdOpen, log, ProgressDots;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.db.Model import RowItemModel;
from medinfo.db.Model import RowItemFieldComparator, columnFromModelList;
from medinfo.db import DBUtil;

from medinfo.analysis.ConcatenateDataFiles import ConcatenateDataFiles;
from medinfo.analysis.SQLQueryDataFile import SQLQueryDataFile;
from medinfo.analysis.BatchTTests import BatchTTests;

BASE_RESULT_DIR = "results/byOrderSets/";
RESULT_BASENAME = "recClassification.byOrderSets";
FILELIST_FILENAME = "resultFileList.txt";
CONCATENATE_FILENAME = "concatenatedResults.tab.gz";
FILTERED_FILENAME = "filteredResults.tab.gz";   # Simplified results format for easier interpretation / visualization
SORTED_FILENAME = "sortedResults.tab.gz";   # Should be able to copy these results into Excel to make PivotTables / PivotCharts of results

DATA_QUERY = "select * from data order by SortType, TopicCount, VerifyTime";

def main_formatMergedTTests(argv):
    ifs = stdOpen(BASE_RESULT_DIR+CONCATENATE_FILENAME);
    ofs = stdOpen(BASE_RESULT_DIR+FILTERED_FILENAME, "w");

    summaryData = {"argv": argv};
    print >> ofs, COMMENT_TAG, json.dumps(summaryData);

    outputCols = ["SortType","TopicCount","VerifyTime","Group1.precision.mean","Group1.recall.mean","Group1.normalprecision.mean","Group1.weightrecall.mean","Group1.roc_auc.mean","ttest_rel.precision","ttest_rel.recall","ttest_rel.weightrecall","ttest_rel.roc_auc","Group1.numqueryitems.mean","Group1.numverifyitems.mean","Group1.numrecommendeditems.mean","Group1.tp.mean"];
    formatter = TextResultsFormatter(ofs);
    formatter.formatTuple(outputCols);  # Output header row

    reader = TabDictReader(ifs);
    for row in reader:
        row["SortType"] = row["Group1._s"];

        # Extract out numerical data from filename text parameters
        row["TopicCount"] = None;
        if row["Group1._m"] != 'None':
            # Expecting model name strings of the form: "models/topicModel.first24hourItems.2013.1234567890.filter.bow.gz.64Topic.model"
            topicChunk = row["Group1._m"].split(".")[-2];   # Expect second to last period-delimited chunk to contain topic count
            topicChunk = topicChunk[:topicChunk.find("Topic")]; # Remove trailing Topic text
            row["TopicCount"] = int(topicChunk);

        # Expecting result file name argument of the form: "results/byOrderSets/01minutes/filteredResults.tab.gz"
        timeChunk = row["args[0]"].split("/")[-2];
        timeChunk = timeChunk[:timeChunk.find("minutes")];
        row["VerifyTime"] = int(timeChunk);

        formatter.formatResultDict(row, outputCols);

    ifs.close();
    ofs.close();

def main_sortResults(argv):
    mod = SQLQueryDataFile();
    subargv = ["SQLQueryDataFile.py", "-q", DATA_QUERY];
    subargv.extend([BASE_RESULT_DIR+FILTERED_FILENAME, BASE_RESULT_DIR+SORTED_FILENAME]);
    mod.main(subargv);

if __name__ == "__main__":
    main_formatMergedTTests(sys.argv);
    main_sortResults(sys.argv);
