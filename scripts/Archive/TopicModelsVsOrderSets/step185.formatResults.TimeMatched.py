"""
Shell script to run several processes.
Different layout for Time Matched experiment series. Won't have an order set reference to compare against?
"""
import sys,os;
import time;
import json;
from io import StringIO;
from medinfo.common.Const import COMMENT_TAG;
from medinfo.common.Util import stdOpen, log, ProgressDots;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.db.Model import RowItemModel;
from medinfo.db.Model import RowItemFieldComparator, columnFromModelList;
from medinfo.db import DBUtil;

from medinfo.analysis.ConcatenateDataFiles import ConcatenateDataFiles;
from medinfo.analysis.SQLQueryDataFile import SQLQueryDataFile;
from medinfo.analysis.BatchTTests import BatchTTests;

BASE_RESULT_DIR = "results/byOrderSets/timeMatched/";
FILTERED_FILENAME = "filteredResults.tab.gz";   # Previously filtered already, now format and sort results
FORMATTED_FILENAME = "formattedResults.tab.gz";
SORTED_FILENAME = "sortedResults.tab.gz";

DATA_QUERY = \
"""select SortType, TopicCount, TrainTime, VerifyTime, 
   avg(precision) as precision_mean, avg(recall) as recall_mean, avg(normalprecision) as normalprecision_mean, avg(weightrecall) as weightrecall_mean, avg(roc_auc) as roc_auc_mean 
from data
group by SortType, TopicCount, TrainTime, VerifyTime
order by SortType, TopicCount, TrainTime, VerifyTime
""";

def main_formatResults(argv):
    ifs = stdOpen(BASE_RESULT_DIR+FILTERED_FILENAME);
    ofs = stdOpen(BASE_RESULT_DIR+FORMATTED_FILENAME, "w");

    summaryData = {"argv": argv};
    print(COMMENT_TAG, json.dumps(summaryData), file=ofs);

    outputCols = ["SortType","TopicCount","TrainTime","VerifyTime","precision","recall","normalprecision","weightrecall","roc_auc"];
    formatter = TextResultsFormatter(ofs);
    formatter.formatTuple(outputCols);  # Output header row

    reader = TabDictReader(ifs);
    for row in reader:
        row["SortType"] = row["_s"];

        # Extract out numerical data from filename text parameters
        row["TopicCount"] = None;
        row["TrainTime"] = None;
        if row["_m"] != 'None':
            # Expecting model name strings of the form: "models/topicModel.firstItems.q14400.v14400.2013.1234567890.filter.bow.gz.16Topic.model"
            chunks = row["_m"].split(".");
            topicChunk = chunks[-2];   # Expect second to last period-delimited chunk to contain topic count
            topicChunk = topicChunk[:topicChunk.find("Topic")]; # Remove trailing Topic text
            row["TopicCount"] = int(topicChunk);

            for chunk in chunks:
                if chunk[0] == "q" and chunk[-1].isdigit(): # This should be the query time in seconds
                    queryTimeSeconds = int(chunk[1:]);
                    queryTimeMinutes = queryTimeSeconds / 60;
                    row["TrainTime"] = queryTimeMinutes;

        # Expecting training file name argument of the form: "sourceData/first24hourOrderSets.2013.q86400.v14400.-12345.tab.gz"
        row["VerifyTime"] = None;
        for chunk in row["args_0_"].split("."):
            if chunk[0] == "v" and chunk[-1].isdigit(): # This should be the verify time in seconds
                verifyTimeSeconds = int(chunk[1:]);
                verifyTimeMinutes = verifyTimeSeconds / 60;
                row["VerifyTime"] = verifyTimeMinutes;

        formatter.formatResultDict(row, outputCols);

    ifs.close();
    ofs.close();

def main_sortResults(argv):
    mod = SQLQueryDataFile();
    subargv = ["SQLQueryDataFile.py", "-q", DATA_QUERY];
    subargv.extend([BASE_RESULT_DIR+FORMATTED_FILENAME, BASE_RESULT_DIR+SORTED_FILENAME]);
    mod.main(subargv);

if __name__ == "__main__":
    main_formatResults(sys.argv);
    main_sortResults(sys.argv);
