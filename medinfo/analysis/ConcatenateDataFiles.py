#!/usr/bin/env python
"""
Given a collection of data files / tables, produce a single combined / concatenated data file / table.
Look for argv in comments in the header of the data files (or explicitly specified by the user)
to identify data generation parameters, and add those values as columns to the concatenated file
to allow for a denormalized relational means to distinguish the data sources.
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

class ConcatenateDataFiles(BaseAnalysis):
    def __init__(self):
        BaseAnalysis.__init__(self);
        self.colNames = None; # Keep track of column headers identified in parsing

    def resultHeaders(self):
        return tuple(self.colNames);

    def __call__(self, inputFiles):
        """Return generator over dictionary objects representing
        the concatenated contents of the input files after adding and accounting for argv parameter columns.
        """
        # Consolidate a master set of all column headers to use
        self.colNames = list(); # Keep track of consistent order found
        colSet = set(); # Keep track of unique items

        # Pull out any header comments that may represent an argv list to parse
        # Pull out header row with column labels for each input file
        argvDicts = list(); # Dictionary for each input file keyed by argv parameter name with respective value
        readers = list();    # TabDictReader from which header columns can be accessed as fieldnames
        for inputFile in inputFiles:
            reader = TabDictReader(inputFile);
            readers.append(reader);
            for col in reader.fieldnames:
                if col not in colSet:
                    colSet.add(col);
                    self.colNames.append(col);

            argvDict = self.extract_argvDict(reader.commentLines);  # Must be called after reader.fieldnames so initial text parsing will start
            argvDicts.append(argvDict);
            for col in argvDict.iterkeys():
                if col not in colSet:
                    colSet.add(col);
                    self.colNames.append(col);

        prog = ProgressDots(50,1,"Files");

        # Now generate each file in succession, but "outer-joined" to include the master column header list
        for argvDict, reader in zip(argvDicts, readers):
            for resultDict in reader:
                resultDict.update(argvDict);
                for col in self.colNames:
                    if col not in resultDict:
                        resultDict[col] = None;
                yield resultDict;
            prog.update();
        # prog.printStatus()

    def extract_argvDict(self, commentLines):
        argvDict = dict();
        for line in commentLines:
            if "argv[0]" not in argvDict:    # Only use the first one found
                commentStr = line[1:].strip(); # Remove comment tag and any flanking whitespace
                try:
                    jsonData = json.loads(commentStr);
                    argv = jsonData;
                    if type(jsonData) == dict:
                        argv = jsonData["argv"];

                    # Simple parse through argv to turn into dictionary of key-value pairs
                    lastKey = None;
                    iArg = 0;
                    for i in xrange(len(argv)):
                        if i == 0:
                            argvDict["argv[0]"] = argv[i];
                        else:
                            if lastKey is not None:
                                # Already have an option key, see if next item is option value, or another option and last was just set/present or not
                                if argv[i].startswith("-"):
                                    # Two option keys in a row, the former was apparently a set/present or not option
                                    argvDict[lastKey] = lastKey;
                                    lastKey = argv[i];
                                else:
                                    argvDict[lastKey] = argv[i];
                                    lastKey = None;
                            else:
                                if argv[i].startswith("-"):
                                    lastKey = argv[i];
                                else:   # Moved on to general arguments
                                    argvDict["args[%d]" % iArg] = argv[i];
                                    iArg += 1;

                except ValueError, exc:
                    # Not a JSON parsable string, ignore it then
                    log.debug(exc);
                    pass;

        return argvDict;


    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <inputFile1> <inputFile2> ... <inputFileN>\n"+\
                    "   <inputFileX>    Tab-delimited file of data.  Initial comment lines will be scanned for list of argv parameters to add as data columns.\n"+\
                    "                   If only a single input is given, interpret this as an index file which lists the names of the other files to concatenate (e.g., obtained with dir * /b or ls).\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-o", "--outputFile",  dest="outputFile",  help="Tab-delimited file matching concatenated contents of input files.  Specify \"-\" to send to stdout.");
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) > 0:
            inputFiles = list();
            if len(args) > 1:
                for inputFilename in args:
                    inputFiles.append(stdOpen(inputFilename));
            else: # len(argvs) == 1, Single index file rather than list of all files on command-line
                indexFile = stdOpen(args[0]);
                for line in indexFile:
                    inputFilename = line.strip();
                    inputFiles.append(stdOpen(inputFilename));

            # Format the results for output
            outputFile = stdOpen(options.outputFile,"w");

            # Print comment line with arguments to allow for deconstruction later as well as extra results
            summaryData = {"argv": argv};
            print >> outputFile, COMMENT_TAG, json.dumps(summaryData);

            # Tab-delimited output formatting
            formatter = TextResultsFormatter(outputFile);

            # Begin the file parsing so can at least get the total list of column headers
            rowGenerator = self(inputFiles);
            firstRow = rowGenerator.next();

            # Insert a mock record to get a header / label row
            colNames = self.resultHeaders();
            formatter.formatTuple(colNames);

            # Stream the concatenated data rows to the output to avoid storing all in memory
            formatter.formatResultDict(firstRow, colNames);
            for outputDict in rowGenerator:
                formatter.formatResultDict(outputDict, colNames);

        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = ConcatenateDataFiles();
    instance.main(sys.argv);
