#!/usr/bin/env python
import sys, os
import time;
from datetime import datetime;
from optparse import OptionParser
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery;
from medinfo.db.Model import RowItemModel, modelListFromTable, modelDictFromList;

from Util import log;
from Env import DATE_FORMAT;

DEFAULT_SOURCE_TABLE = "jchi_accesslog_script";
NULL_GROUP_ID = 0;  # Metric Group ID to assign if null/None indicated
NULL_GROUP_NAME = "Null Group";

class STRIDEAccessLogConversion:
    """Data conversion module to take STRIDE provided user AccessLog data
    into normalized structured data tables to facilitate subsequent analysis.
    """
    connFactory = None; # Allow specification of alternative DB connection source
    
    sourceTableName = None;
    
    # Local caches to track lookup values
    userBySID = None;
    metricLineDescriptionsById = None;
    metricById = None;
    metricGroupById = None;
    
    def __init__(self):
        """Default constructor"""
        self.connFactory = DBUtil.ConnectionFactory();  # Default connection source

        self.sourceTableName = DEFAULT_SOURCE_TABLE;    # Customizable parameter to facilitate test cases
        
        self.userBySID = dict();
        self.metricLineDescriptionsById = dict();
        self.metricById = dict();
        self.metricGroupById = dict();

    def convertSourceItems(self, userSIDs=None, limit=None, offset=None):
        """Primary run function to process the contents of the source table
        and convert them into normalized data table entries.
        """
        log.info("Conversion for patients: %s" % userSIDs);
        progress = ProgressDots();
        conn = self.connFactory.connection();
        try:
            for i, sourceItem in enumerate(self.querySourceItems(userSIDs, limit, offset, progress=progress, conn=conn)):
                self.convertSourceItem(sourceItem, conn=conn);
                progress.Update();

            # Go through accumulated metric description lines into single entries for the metric table
            self.updateMetricDescriptionLines();
        finally:
            conn.close();
        progress.PrintStatus();


    def querySourceItems(self, userSIDs, limit=None, offset=None, progress=None, conn=None):
        """Query the database for list of all AccessLogs 
        and yield the results one at a time.  If userSIDs provided, only return items matching those IDs.
        """
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();

        # Column headers to query for that map to respective fields in analysis table
        headers = ["user_id", "user_name", "de_pat_id", "access_datetime", "metric_id", "metric_name", "line_count", "description", "metric_group_num", "metric_group_name"];
        
        query = SQLQuery();
        for header in headers:
            query.addSelect( header );
        query.addFrom(self.sourceTableName);
        if userSIDs is not None:
            query.addWhereIn("user_id", userSIDs);
        query.setLimit(limit);
        query.setOffset(offset);

        # Query to get an estimate of how long the process will be
        if progress is not None:
            progress.total = DBUtil.execute(query.totalQuery(), conn=conn)[0][0];

        cursor = conn.cursor();
        # Do one massive query, but yield data for one item at a time.
        cursor.execute( str(query), tuple(query.params) );

        row = cursor.fetchone();
        while row is not None:
            rowModel = RowItemModel( row, headers );
            yield rowModel;
            row = cursor.fetchone();

        # Slight risk here.  Normally DB connection closing should be in finally of a try block,
        #   but using the "yield" generator construct forbids us from using a try, finally construct.
        cursor.close();

        if not extConn:
            conn.close();

    def convertSourceItem(self, sourceItem, conn=None):
        """Given an individual sourceItem record, produce / convert it into an equivalent
        item record in the analysis database.
        """
        extConn = conn is not None;
        if not extConn:
            conn = self.connFactory.connection();
        try:
            # Normalize sourceItem data into hierachical components (metric group -> metric -> metric line and user -> access_log).
            #   Expect relatively small number of lookup values, so these should only have to be instantiated
            #   in a first past, with subsequent calls just yielding back in memory cached copies
            user = self.userFromSourceItem(sourceItem, conn=conn);
            metricGroup = self.metricGroupFromSourceItem(sourceItem, conn=conn);
            metric = self.metricFromSourceItem(sourceItem, metricGroup, conn=conn);
            metricLine = self.metricLineFromSourceItem(sourceItem, metric, conn=conn);
            accessLog = self.accessLogFromSourceItem(sourceItem, user, metric, metricLine, conn=conn);
        finally:
            if not extConn:
                conn.close();

    def userFromSourceItem(self, sourceItem, conn):
        # Load or produce a user record model for the given sourceItem
        userSID = sourceItem["user_id"];
        if userSID not in self.userBySID:
            # User does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            userId = int(userSID[1:]);  # Trim out leading S and parse remainder of SID as integer
            user = \
                RowItemModel \
                (   {   "user_id":  userId, # Somewhat confusing remap of "user_id" in source data to "sid" to reserve user_id for the integer component
                        "sid":  userSID,
                        "name": sourceItem["user_name"],
                    }
                );
            (userId, isNew) = DBUtil.findOrInsertItem("user", user, conn=conn);
            self.userBySID[userSID] = user;
        return self.userBySID[userSID];
    
    def metricGroupFromSourceItem(self, sourceItem, conn):
        # Load or produce a metricGroup record model for the given sourceItem
        metricGroupId = sourceItem["metric_group_num"]; # Map num to Id
        metricGroupName = sourceItem["metric_group_name"];
        if metricGroupId is None:
            metricGroupId = NULL_GROUP_ID;
            metricGroupName = NULL_GROUP_NAME;
        if metricGroupId not in self.metricGroupById:
            # MetricGroup does not yet exist in the local cache.  Check if in database table (if not, persist a new record)
            metricGroup = \
                RowItemModel \
                (   {   "metric_group_id": metricGroupId,
                        "name": metricGroupName,
                    }
                );
            (metricGroupId, isNew) = DBUtil.findOrInsertItem("metric_group", metricGroup, conn=conn);
            self.metricGroupById[metricGroupId] = metricGroup;
        return self.metricGroupById[metricGroupId];

    def metricFromSourceItem(self, sourceItem, metricGroup, conn):
        metricId = sourceItem["metric_id"];
        if metricId not in self.metricById:
            metric = \
                RowItemModel \
                (   {   "metric_id": metricId,
                        "metric_group_id": metricGroup["metric_group_id"], 
                        "name": sourceItem["metric_name"],
                    }
                );
            (metricId, isNew) = DBUtil.findOrInsertItem("metric", metric, conn=conn);
            self.metricById[metricId] = metric;
        return self.metricById[metricId];

    def metricLineFromSourceItem(self, sourceItem, metric, conn):
        metricId = sourceItem["metric_id"];
        targetLine = sourceItem["line_count"];
        iTargetLine = targetLine-1; # Change from 1 to 0-based indexing
        
        if metricId not in self.metricLineDescriptionsById:
            self.metricLineDescriptionsById[metricId] = list();
        nCurrentLines = len(self.metricLineDescriptionsById[metricId]);
        nMissingLines = targetLine - nCurrentLines;
        for i in xrange(nMissingLines):
            self.metricLineDescriptionsById[metricId].append('XXX');    # Placeholder values
        
        self.metricLineDescriptionsById[metricId][iTargetLine] = sourceItem["description"];

        return targetLine;

    def accessLogFromSourceItem(self, sourceItem, user, metric, metricLine, conn):
        # Produce an access log for the given sourceItem with links to the lookup user and metric
        # Only record once for multi-line descriptions, so check the line number
        accessLog = None;
        if metricLine == 1:
            accessLog = \
                RowItemModel \
                (   {   "user_id":  user["user_id"],
                        "de_pat_id":  sourceItem["de_pat_id"],
                        "metric_id":  metric["metric_id"],
                        "access_datetime":  sourceItem["access_datetime"],
                    }
                );
            insertQuery = DBUtil.buildInsertQuery("access_log", accessLog.keys() );
            insertParams= accessLog.values();
            DBUtil.execute( insertQuery, insertParams, conn=conn );
        return accessLog;

    def updateMetricDescriptionLines(self):
        for metricId, descriptionLines in self.metricLineDescriptionsById.iteritems():
            description = str.join(' ', descriptionLines);
            DBUtil.updateRow("metric", {"description": description}, metricId );

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options]\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-i", "--userSIDs", dest="userSIDs", metavar="<userSIDs>",  help="Comma separated list of user SIDs to convert AccessLog data for.  Leave blank to attempt conversion for all available");
        parser.add_option("-l", "--limit", dest="limit", metavar="<limit>",  help="Number of records to process before stopping");
        parser.add_option("-o", "--offset", dest="offset", metavar="<offset>",  help="Number of records to skip before start converting");
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();

        userSIDs = None;
        if options.userSIDs is not None:
            userSIDs = options.userSIDs.split(",");

        limit = None;
        if options.limit is not None:
            limit = int(options.limit);
        offset = None;
        if options.offset is not None:
            offset = int(options.offset);
        
        self.convertSourceItems(userSIDs, limit, offset);

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = STRIDEAccessLogConversion();
    instance.main(sys.argv);
