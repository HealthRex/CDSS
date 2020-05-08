#!/usr/bin/env python
"""
Example app module to run queries against the processed clincal database, 
more as fodder to test management of driver scripts to manage this.
"""
import sys, os
import time;
from optparse import OptionParser;
import json;
import urllib.parse;
import math;
from datetime import datetime, timedelta;
from medinfo.common.Const import COMMENT_TAG;
from medinfo.common.Util import stdOpen, ProgressDots, log;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel;
from medinfo.db.Model import modelListFromTable, modelDictFromList;
from medinfo.db.ResultsFormatter import TextResultsFormatter;

class ExampleQueryApp:
    def __init__(self):
        self.connFactory = DBUtil.ConnectionFactory();  # Default connection source

    def queryItems(self, options, outputFile):
        """Query for all clinical item records that fulfill the options criteria
        and then send the results as tab-delimited output to the outputFile.
        """
        pauseSeconds = float(options.pauseSeconds);

        query = SQLQuery();
        query.addSelect("cic.description, ci.clinical_item_id, ci.name, ci.description");
        query.addFrom("clinical_item_category as cic");
        query.addFrom("clinical_item as ci");
        query.addWhere("cic.clinical_item_category_id = ci.clinical_item_category_id");
        if options.itemPrefix:
            query.addWhereOp("ci.description","like", options.itemPrefix+"%%");    # Add wildcard to enabe prefix search
        if options.categoryNames:
            query.addWhereIn("cic.description", options.categoryNames.split(",") );
        query.addOrderBy("cic.description, ci.name, ci.description, ci.clinical_item_id");

        formatter = TextResultsFormatter(outputFile);
        
        prog = ProgressDots();
        for row in DBUtil.execute(query, includeColumnNames=True, connFactory=self.connFactory):
            formatter.formatTuple(row);
            time.sleep(pauseSeconds);
            prog.update();
        prog.printStatus();

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "Query for the clinical_item records that exist with the specified criteria\n"+\
                    "usage: %prog [options] [<outputFile>]\n"+\
                    "   <outputFile>    Results file. Leave blank or specify \"-\" to send to stdout.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-i", "--itemPrefix",  dest="itemPrefix", help="Look for clinical_items whose description starts with this prefix.");
        parser.add_option("-c", "--categoryNames",  dest="categoryNames", help="Comma separated list of clinical_item_category.descriptions to look for.");
        parser.add_option("-p", "--pauseSeconds",  dest="pauseSeconds", default="0", help="Number of seconds to pause between processing each record.");
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) > 0:
            outputFile = stdOpen(args[0],"w");

            # Print comment line with arguments to allow for deconstruction later as well as extra results
            summaryData = {"argv": argv};
            print(COMMENT_TAG, json.dumps(summaryData), file=outputFile);

            self.queryItems(options, outputFile);

        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = ExampleQueryApp();
    instance.main(sys.argv);
