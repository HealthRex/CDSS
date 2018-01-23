#!/usr/bin/env python
"""
Given a large relational data table of matching data, calculate paired t-tests between statistics
"""

import sys, os;
import time;
import json;
from optparse import OptionParser
from cStringIO import StringIO;

import numpy as np;
from scipy.stats import ttest_rel, ttest_ind;

from medinfo.db.Model import columnFromModelList;
from medinfo.db.Model import RowItemFieldComparator;
from medinfo.common.Const import COMMENT_TAG;
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.db.Model import RowItemModel;
from Util import log;

from BaseAnalysis import BaseAnalysis;

# Summary stats to report (more for sanity checking)
def percentile25(x):
    return np.percentile(x,25);
def percentile75(x):
    return np.percentile(x,75);
SUMMARY_FUNCTIONS = [len, np.mean, np.std, np.median, percentile25, percentile75];

# Use to determine which tests to run
COMPARISON_TESTS = [ttest_ind, ttest_rel];

class BatchTTests(BaseAnalysis):
    def __init__(self):
        BaseAnalysis.__init__(self);
        self.labelCols = None;
        self.valueCols = None;
        self.matchCols = None;
        self.baseLabels = None;

    def __call__(self, inputFile, labelCols, valueCols, matchCols, baseLabels=None):
        prog = ProgressDots();

        self.labelCols = labelCols;
        self.valueCols = valueCols;
        self.matchCols = matchCols;
        self.baseLabels = baseLabels;

        labelModelByLabelKey = dict();
        dataByLabelKey = dict();

        reader = TabDictReader(inputFile);
        for rowModel in reader:
            labelKey = list();
            labelModel = dict();
            for labelCol in self.labelCols:
                labelModel[labelCol] = rowModel[labelCol];
                labelKey.append(rowModel[labelCol]);
            labelKey = tuple(labelKey); # Change to immutable object that can be hashed

            # Copy just items of interest
            valueModel = {};
            if self.matchCols:
                for matchCol in self.matchCols:
                    valueModel[matchCol] = rowModel[matchCol];
            for valueCol in self.valueCols:
                try:
                    valueModel[valueCol] = float(rowModel[valueCol]);
                except ValueError:  # Maybe None string, could not parse into a number
                    valueModel[valueCol] = None;

            if labelKey not in dataByLabelKey:
                labelModelByLabelKey[labelKey] = labelModel;
                dataByLabelKey[labelKey] = list();
            dataByLabelKey[labelKey].append(valueModel);

            prog.update();

        # prog.printStatus();

        # Another pass to ensure data is consistently sorted in each group to allow later paired t-tests
        if self.matchCols:
            for labelKey, data in dataByLabelKey.iteritems():
                data.sort( RowItemFieldComparator(self.matchCols) );

        # See if looking for only one set of base labeled data to compare the rest against
        baseLabelKey = None;
        if self.baseLabels is not None:
            baseLabelKey = tuple(self.baseLabels);

        # Result pass to compare all group pair-wise combinations
        prog = ProgressDots();
        for labelKey0, data0 in dataByLabelKey.iteritems():
            prefix0 = "Group0.";
            labelModel0 = labelModelByLabelKey[labelKey0];

            if baseLabelKey is not None and labelKey0 != baseLabelKey:
                continue;   # Skip entries where the base label does not match specified key

            for labelKey1, data1 in dataByLabelKey.iteritems():
                prefix1 = "Group1.";
                labelModel1 = labelModelByLabelKey[labelKey1];

                result = dict();
                for labelCol in self.labelCols:
                    result[prefix0+labelCol] = labelModel0[labelCol];
                    result[prefix1+labelCol] = labelModel1[labelCol];

                for valueCol in self.valueCols:
                    # Pull out value column for each data group.  Previous, sort by match col to allow paired t-testing
                    # Skip any value pairs if non-numeric / None value
                    values0 = list();
                    values1 = list();
                    for dataItem0, dataItem1 in zip(data0, data1):
                        if dataItem0[valueCol] is not None and dataItem1[valueCol] is not None:
                            values0.append(dataItem0[valueCol]);
                            values1.append(dataItem1[valueCol]);

                    for summaryFunction in SUMMARY_FUNCTIONS:
                        result[prefix0 +valueCol+"."+ summaryFunction.__name__] = summaryFunction(values0);
                        result[prefix1 +valueCol+"."+ summaryFunction.__name__] = summaryFunction(values1);

                    for compTest in COMPARISON_TESTS:
                        (t, p) = compTest(values0,values1);
                        if np.isnan(p):
                            p = None;   # Use more generic expression for NaN / null value
                        result[compTest.__name__+"."+valueCol] = p;

                yield result;

                prog.update();
        # prog.printStatus();

    def resultHeaders(self, labelCols, valueCols, matchCol):
        headers = list();
        prefixes = ["Group0.","Group1."];
        for labelCol in labelCols:
            for prefix in prefixes:
                headers.append(prefix+labelCol);

        for valueCol in valueCols:
            for summaryFunction in SUMMARY_FUNCTIONS:
                for prefix in prefixes:
                    headers.append(prefix +valueCol+"."+ summaryFunction.__name__);

        compTests = COMPARISON_TESTS;
        for compTest in compTests:
            for valueCol in valueCols:
                headers.append(compTest.__name__ +"."+valueCol);

        return headers;

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <inputFile> <outputFile>\n"+\
                    "   <inputFile>    Tab-delimited file of data\n"+\
                    "   <ouputFile>    Tab-delimited file with relational table of t-test p-values for each sub-group pair.  Specify \"-\" to send to stdout.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-l", "--labelCols",  dest="labelCols",  help="Comma-separated list of the column headers to label data rows as belonging to different subgroups");
        parser.add_option("-v", "--valueCols",  dest="valueCols",  help="Comma-separated list of the column headers for data values want to calculate statistics for");
        parser.add_option("-m", "--matchCols",  dest="matchCols",  help="Comma-separated list of the column headers to match groups on, like row identifiers.  If not exists, then do independent t-tests rather than paired.");
        parser.add_option("-b", "--baseLabels", dest="baseLabels", help="Comma-separated list of values that the labelCols should have to represent which base method to compare all other methods to as a reference (otherwise do a full n^2 cartesian product of all combinations).");
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) > 1:
            inputFile = stdOpen(args[0]);
            outputFile = stdOpen(args[1],"w");

            labelCols = options.labelCols.split(",");
            valueCols = options.valueCols.split(",");
            matchCols = None;
            if options.matchCols:
                matchCols = options.matchCols.split(",");
            baseLabels = None;
            if options.baseLabels:
                baseLabels = options.baseLabels.split(",");

            # Print comment line with arguments to allow for deconstruction later as well as extra results
            summaryData = {"argv": argv};
            print >> outputFile, COMMENT_TAG, json.dumps(summaryData);

            # Tab-delimited output formatting
            formatter = TextResultsFormatter(outputFile);

            # Prep generator first, so will be able to extract out relevant header columns
            rowGenerator = self(inputFile, labelCols, valueCols, matchCols, baseLabels);

            # Insert a mock record to get a header / label row
            colNames = self.resultHeaders(labelCols, valueCols, matchCols);
            formatter.formatResultDict(RowItemModel(colNames,colNames), colNames);

            # Stream the concatenated data rows to the output to avoid storing all in memory
            for outputDict in rowGenerator:
                formatter.formatResultDict(outputDict, colNames);

        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = BatchTTests();
    instance.main(sys.argv);
