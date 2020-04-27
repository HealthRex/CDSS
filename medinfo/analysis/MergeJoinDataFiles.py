#!/usr/bin/env python
"""
Given a collection of data files / tables with a common column, produce a single combined data file / table
with merged columns based on a common specified key column.
Basically like a SQL (outer join) on specified key column.
"""

import sys, os;
import time;
import json;
import numpy as np;
from optparse import OptionParser
from io import StringIO;
import pandas as pd;    # Take advantage of existing framework for DataFrame manipulation
from medinfo.common.Const import COMMENT_TAG, VALUE_DELIM;
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from .Util import log;

from .BaseAnalysis import BaseAnalysis;

class MergeJoinDataFiles(BaseAnalysis):
    def __init__(self):
        BaseAnalysis.__init__(self);
        self.na_rep = np.nan;

    def __call__(self, inputFiles, keys, suffixList, outFile):
        """Merges the DataFrame contents of the inputFiles by respective keys and saves back to outFile,
        with non-key data element column labels extended with specified suffixes.
        """
        mergeFrame = None;
        lastSuffix = None;
        for (inputFile, nextSuffix) in zip(inputFiles, suffixList):
            inputFrame = pd.read_table(inputFile, comment=COMMENT_TAG);

            # Ensure non-key columns will have suffixes added (may not happen automatically if no name clashes)
            nextCols = set(inputFrame.columns.tolist()) - set(keys);
            nextColsWithSuffixByNonSuffix = dict();
            for col in nextCols:
                nextColsWithSuffixByNonSuffix[col] = col+nextSuffix;

            if mergeFrame is None:
                mergeFrame = inputFrame;
            else:
                # Primary merge-join operation by Pandas implementation
                mergeFrame = mergeFrame.merge(inputFrame, how="outer", on=keys, suffixes=[lastSuffix,nextSuffix], copy=False);

            # Apply column renaming to ensure non-key columns have suffixes added
            mergeFrame.rename( columns=nextColsWithSuffixByNonSuffix, inplace=True );

            lastSuffix = nextSuffix;

        mergeFrame.to_csv(outFile, sep="\t", na_rep=self.na_rep, index=False);

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <inputFile1> <inputFile2> ... <inputFileN>\n"+\
                    "   <inputFileX>    Tab-delimited files of data, should have a key column with a unique identifier to merge across files.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-c", "--keyList",  dest="keyList",  help="Comma-separated list of column identifiers to find in the input files to know what to merge on.");
        parser.add_option("-s", "--suffixList",  dest="suffixList",  help="Comma-separated list of suffixes to add to non-key column names in common across merged files");
        parser.add_option("-o", "--outputFile",  dest="outputFile",  help="Tab-delimited file containing merged contents of input files.  Specify \"-\" to send to stdout.");
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting %s: %s" % (os.getpid(), str.join(" ", argv)) );
        timer = time.time();
        if len(args) > 1:
            inputFiles = list();
            for inputFilename in args:
                inputFiles.append(stdOpen(inputFilename));

            keyList = options.keyList.split(",");
            suffixList = options.suffixList.split(",");
            
            # Format the results for output
            outputFile = stdOpen(options.outputFile,"w");

            # Print comment line with arguments to allow for deconstruction later as well as extra results
            summaryData = {"argv": argv};
            print(COMMENT_TAG, json.dumps(summaryData), file=outputFile);

            self(inputFiles, keyList, suffixList, outputFile);

        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = MergeJoinDataFiles();
    instance.main(sys.argv);
