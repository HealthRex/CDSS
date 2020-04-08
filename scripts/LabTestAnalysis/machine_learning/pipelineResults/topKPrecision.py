# Go through the top predicted rows for an input data frame file and report the
#","precision (positive predictive value = % correct-normal), as sorted by each prediction method used

import sys, os;
import time;
from io import StringIO;
from datetime import datetime, timedelta;
import json;

import pandas as pd;
from medinfo.common.Util import stdOpen, log, ProgressDots;
from medinfo.common.Const import COMMENT_TAG, NULL_STRING;


# Anything that is not a label of result (Y) column, assume is a predicted value/score column
#     to yield "normal" results (not "abnormal" which should = "all_result_normal" but some labs not labeled)
labelCols = ["patient_id","encounter_id","order_proc_id","proc_code","order_time"];
resultCols = ["normal","abnormal","result_normal_count","result_total_count","all_result_normal"];
outcomeCol = "normal";

def main(argv):
    timer = time.time();

    infile = stdOpen(argv[1]);
    outfile = stdOpen(argv[2],"w");
    
    summaryData = {"argv": argv};
    print(COMMENT_TAG, json.dumps(summaryData), file=outfile);

    df = pd.read_csv(infile, na_values=[NULL_STRING]);
    df["normal"] = 1-df["abnormal"];    # Use not-abnormal as output of interest. Should be same as all_result_normal, but some labs not labeled

    # Prepare output dataframe skeleton
    resultDF = pd.DataFrame();
    nRows = len(df);
    floatNRows = float(nRows);  # Facilitate subsequent floating point division
    for iRow in range(nRows):
        topK = iRow+1;    # Top K items considered
        topKPercent = topK/ floatNRows; # Top Percentage of all items considered
        resultDF.set_value(iRow,"iRow", iRow);
        resultDF.set_value(iRow,"Top K", topK);
        resultDF.set_value(iRow,"Top K %", topKPercent);

    for col in df.columns:
        if col not in labelCols and col not in resultCols:
            # Any leftover should be a predicted test result / score, correlated with the outcome column
            scoreCol = col;
            print(scoreCol, file=sys.stderr);
            scoreResultCol = scoreCol #+".precisionAtK";
            if scoreResultCol.startswith("predictedTest."):
                scoreResultCol = scoreResultCol[len("predictedTest."):];    # Clean up (trim off) name prefixes
            df.sort(scoreCol, ascending=False, inplace=True);    # Descending sort by the score column

            countNormal = 0.0;
            countAll = 0;
            iRow = 0;
            for index, row in df.iterrows():
                countAll += 1;
                countNormal += row[outcomeCol];
                precisionAtK = countNormal / countAll;
                #print >> sys.stderr, precisionAtK, row[[outcomeCol,scoreCol]];
                resultDF.set_value(iRow,scoreResultCol, precisionAtK);
                iRow += 1;

    print("output", file=sys.stderr)
    resultDF.to_csv(outfile);

    return df;


if __name__ == "__main__":
    df = main(sys.argv);
