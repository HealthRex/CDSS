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

# Limit query to a subset of Patient IDs so the it won't take forever to run
# Makes the test example a bit too specific, but just for testing/workshop purposes for now
SAMPLE_PATIENT_IDS = \
    [   8964988988145,-11778919967000,1644524778271,-1627153119971,9923828241050,-5505734464236,-8296233665981,2645846033211,4012879741993,-619085030152,-8899507533651,-8847205751993,2285364981542,11681768930454,11237047079533,11791338997183,2629785819499,-4317483268249,-10560244594508,4075456796837,-12062784624707,-9962190379122,10289612886477,4041156778190,6330402647868,9113630299220,-2754652568957,10689309033926,3868658223235,9918201424648,
        -8901765389230,-4794658653950,8912988390527,-10438876782272,10296121737922,6667901215721,-4838043793686,6424149980463,768294002186,-2884643689156,11531207483718,-8077552655778,-6153545138171,-8534048807643,-6912013940005,1931404724993,-3882353026601,-10012375259041,4947314122183,-1008300375654,-5591292298475,542120875211,-11834361401577,-4178787042446,-10733992147936,-7329535998513,-9155525001826,6633706513218,-5736498606968,10145116322188,-12430814784903,-9529262711298,-2031733415140,-2383115322132,-6222416382704,705394952528,-3027337322895,10200359279457,-990318029204,-2534192786705,-10742239009872,10990016829124,9448099613231,-651186499214,6730702877508,-6967971172427,3093135295419,-7003705739463,-11152786473993,-3677822543489,-10208036034390,-10016683914409,11314053563277,-9116622579799,4188911946489,3493029027852,5294192935923,7097340179860,4695770200014,-343369064503,2711368127338,-3594684123306,9647749979125,14843271999,8317338221509,-8526832485165,-10767048767551,-5706720611309,-11938808043565,8037787766379,
    ];

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
        query.addWhereIn("pi.patient_id", SAMPLE_PATIENT_IDS);
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
