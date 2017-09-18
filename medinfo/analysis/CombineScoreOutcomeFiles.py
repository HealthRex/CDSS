#!/usr/bin/env python
"""
Combine a score file with an outcome file that can then be fed into ROC / prediction analyses.
"""

import sys, os;
import time;
import json;
from optparse import OptionParser
from cStringIO import StringIO;
from medinfo.db.Model import columnFromModelList;
from medinfo.common.Const import COMMENT_TAG;
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.db.Model import RowItemModel;
from Util import log;

from Const import OUTCOME_ABSENT, OUTCOME_PRESENT;

from BaseAnalysis import BaseAnalysis;

class CombineScoreOutcomeFiles(BaseAnalysis):
    def __init__(self):
        BaseAnalysis.__init__(self);

    def __call__(self, scoreFile, outcomeFile, linkCol, outcomeLabel, valueMin, valueMax, generateHeader=False):
        """Return generator over dictionary objects representing
        the same contents as the scoreFile, but with added entry / column
        to reflect the outcome information in the outcomeFile, named outcomeLabel.
        Link the two together based on a common linkCol.
        Look for values in the outcomeFile, any whose value column is within [valueMin,valueMax]
        will be labeled with a positive outcome of +1, all else labeled 0.
        """
        scoreReader = TabDictReader(scoreFile);
        outcomeReader = TabDictReader(outcomeFile);
        
        # Find positive outcome labels by presence in outcome reader.  
        #   If multiple exist for a link item ID will count any being positive as overall positive.
        outcomeByLinkId = dict();
        for outcomeDict in outcomeReader:
            linkId = outcomeDict[linkCol];
            value = float(outcomeDict["value"]);
            if valueMin <= value and value <= valueMax:
                outcomeByLinkId[linkId] = OUTCOME_PRESENT;
        
        # Now copy through core score data, but adding outcome column
        for scoreDict in scoreReader:
            linkId = scoreDict[linkCol];
            scoreDict[outcomeLabel] = OUTCOME_ABSENT;
            if linkId in outcomeByLinkId:
                scoreDict[outcomeLabel] = OUTCOME_PRESENT;
            
            if generateHeader:
                headerDict = RowItemModel(scoreDict.keys(),scoreDict.keys());
                yield headerDict;
                generateHeader = False; # Only need first row
            yield scoreDict;

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <scoreFile> <outcomeFile> [<outputFile>]\n"+\
                    "   <scoreFile>     Tab-delimited file containing item IDs as well as column(s) for some score that will be used to relate to outcomes\n"+\
                    "   <outcomeFile>   Tab-delimited file containing item IDs as well as value column to assess for outcome labeling\n"+\
                    "   <outputFile>    Tab-delimited file matching score file with extra outcome column\n"+\
                    "                       Leave blank or specify \"-\" to send to stdout.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-c", "--linkCol",  dest="linkCol",  help="Name of column to link score and outcome file");
        parser.add_option("-o", "--outcomeLabel",  dest="outcomeLabel",  help="Label to set for new outcome column");
        parser.add_option("-v", "--valueMin",  dest="valueMin", help="Minimum value to treat as a positive outcome");
        parser.add_option("-V", "--valueMax",  dest="valueMax", help="Maximum value to treat as a positive outcome");
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) > 1:
            scoreFile = stdOpen(args[0]);
            outcomeFile = stdOpen(args[1]);

            valueMin = float(options.valueMin);
            valueMax = float(options.valueMax);
            
            # Run the actual analysis
            outputDicts = self(scoreFile, outcomeFile, options.linkCol, options.outcomeLabel, valueMin, valueMax, generateHeader=True);

            # Format the results for output
            outputFilename = None;
            if len(args) > 2:
                outputFilename = args[2];
            outputFile = stdOpen(outputFilename,"w");
            
            # Print comment line with arguments to allow for deconstruction later as well as extra results
            summaryData = {"argv": argv};
            print >> outputFile, COMMENT_TAG, json.dumps(summaryData);

            formatter = TextResultsFormatter(outputFile);
            formatter.formatResultDicts(outputDicts);
        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = CombineScoreOutcomeFiles();
    instance.main(sys.argv);
