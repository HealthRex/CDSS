#!/usr/bin/env python
"""
Given a relational data table input,
output a derivative based on SQL query syntax,
using a generic tablename "data."
Equivalent function to SQL where clause.
"""

import sys, os;
import time;
import json;
from optparse import OptionParser
from cStringIO import StringIO;

from medinfo.db.Model import columnFromModelList;
from medinfo.db.Model import RowItemFieldComparator;
from medinfo.common.Const import COMMENT_TAG;
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db.Model import RowItemModel;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.db.ResultsFormatter import pandas_read_table, pandas_write_table;
from medinfo.db.ResultsFormatter import pandas_to_sqlconn, pandas_read_sql_query;
from Util import log;

from BaseAnalysis import BaseAnalysis;

DEFAULT_TABLENAME = 'data';

class SQLQueryDataFile(BaseAnalysis):
    def __init__(self):
        BaseAnalysis.__init__(self);

    def __call__(self, sqlQuery, inputFile, outputFile):
        # Load inputFile into dataFrame
        inputDF = pandas_read_table(inputFile);
        # In memory SQL DB instance of data
        conn = pandas_to_sqlconn(inputDF, tableName=DEFAULT_TABLENAME);
        # Run SQL query to generate an output result dataFrame
        outputDF = pandas_read_sql_query(sqlQuery, conn);
        # Send the results to text output
        pandas_write_table(outputDF, outputFile);
    
    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <inputFile> <outputFile>\n"+\
                    "   <inputFile>    Tab-delimited file of relational data. Specify \"-\" to read from stdin.\n"+\
                    "   <ouputFile>    Tab-delimited file relational query data results.  Specify \"-\" to send to stdout.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-q", "--sqlQuery",  dest="sqlQuery",  help="SQL Query to execute on the input data file/table. Use default tablename '%s' in query." % DEFAULT_TABLENAME);
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) > 1:
            inputFile = stdOpen(args[0]);
            outputFile = stdOpen(args[1],"w");
            sqlQuery = options.sqlQuery;

            # Print comment line with arguments to allow for deconstruction later as well as extra results
            summaryData = {"argv": argv};
            print >> outputFile, COMMENT_TAG, json.dumps(summaryData);

            # Primary execution to load inputFile, run query, then drop results into outputFile
            dataFrame = self(sqlQuery, inputFile, outputFile);
        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = SQLQueryDataFile();
    instance.main(sys.argv);
