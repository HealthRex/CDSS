#!/usr/bin/env python
"""
Example app module to run queries against a GCP BigQuery database, 
more as fodder to test management of driver scripts to manage this.
"""
import sys, os
import time;
from optparse import OptionParser;
import json;
from medinfo.common.Const import COMMENT_TAG;
from medinfo.common.Util import stdOpen, ProgressDots, log;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery;
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
        query.addSelect("count(order_med_id_coded) as nOrders");
        query.addSelect("om.med_route, om.medication_id, om.med_description");
        query.addFrom("starr_datalake2018.order_med as om");
        if options.descriptionPrefix:
            query.addWhereOp("om.med_description","like", options.descriptionPrefix+"%%");    # Add wildcard to enabe prefix search
        if options.medRoutes:
            query.addWhereIn("om.med_route", options.medRoutes.split(",") );
        query.addGroupBy("om.medication_id, om.med_description, om.med_route");
        query.addOrderBy("nOrders desc, om.med_description");

        formatter = TextResultsFormatter(outputFile);
        
        prog = ProgressDots();
        for row in DBUtil.execute(query, includeColumnNames=True, connFactory=self.connFactory):
            formatter.formatTuple(row);
            time.sleep(pauseSeconds);
            prog.update();
        prog.printStatus();

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "Query for order_med record counts that exist with the specified criteria\n"+\
                    "usage: %prog [options] [<outputFile>]\n"+\
                    "   <outputFile>    Results file. Specify \"-\" to send to stdout.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-d", "--descriptionPrefix",  dest="descriptionPrefix", help="Look for medication orders whose description starts with this prefix.");
        parser.add_option("-r", "--medRoutes",  dest="medRoutes", help="Comma separated list of medication routes to consider (e.g., Intravenous, Oral).");
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
