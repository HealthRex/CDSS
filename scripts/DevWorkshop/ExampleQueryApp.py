#!/usr/bin/env python
"""
Example app module to run queries against the processed clincal database, 
more as fodder to test management of driver scripts to manage this.
"""
import sys, os
import time;
from optparse import OptionParser;
import json;
import urlparse;
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

    def queryPatientItems(self, options, outputFile):
        """Query for all patient item records that fulfill the options criteria
        and then send the results as tab-delimited output to the outputFile.
        """
        pauseSeconds = float(options.pauseSeconds);

        query = SQLQuery();
        query.addSelect("pi.patient_id, cic.description, ci.clinical_item_id, ci.name, ci.description, pi.item_date");
        query.addFrom("clinical_item_category as cic");
        query.addFrom("clinical_item as ci");
        query.addFrom("patient_item as pi");
        query.addWhere("cic.clinical_item_category_id = ci.clinical_item_category_id");
        query.addWhere("ci.clinical_item_id = pi.clinical_item_id");
        if options.startDate:
            query.addWhereOp("pi.item_date",">=", DBUtil.parseDateValue(options.startDate) );
        if options.endDate:
            query.addWhereOp("pi.item_date","<", DBUtil.parseDateValue(options.endDate) );
        if options.categoryIds:
            query.addWhereIn("cic.clinical_item_category_id", options.categoryIds.split(",") );
        query.addOrderBy("pi.patient_id, pi.item_date, ci.clinical_item_id");

        formatter = TextResultsFormatter(outputFile);
        
        prog = ProgressDots();
        for row in DBUtil.execute(query, includeColumnNames=True, connFactory=self.connFactory):
            formatter.formatTuple(row);
            time.sleep(pauseSeconds);
            prog.update();
        prog.printStatus();

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "Query for the patient_item records that exist with the specified criteria\n"+\
                    "usage: %prog [options] [<outputFile>]\n"+\
                    "   <outputFile>    Results file. Leave blank or specify \"-\" to send to stdout.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-s", "--startDate",  dest="startDate", help="Query start of date range.");
        parser.add_option("-e", "--endDate",  dest="endDate", help="Query end of date range.");
        parser.add_option("-c", "--categoryIds",  dest="categoryIds", help="Comma separated list of clinical_item_category_ids to look for.");
        parser.add_option("-p", "--pauseSeconds",  dest="pauseSeconds", default="0", help="Number of seconds to pause between processing each record.");
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) > 0:
            outputFile = stdOpen(args[0],"w");

            # Print comment line with arguments to allow for deconstruction later as well as extra results
            summaryData = {"argv": argv};
            print >> outputFile, COMMENT_TAG, json.dumps(summaryData);

            self.queryPatientItems(options, outputFile);

        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);


if __name__ == "__main__":
    instance = ExampleQueryApp();
    instance.main(sys.argv);
