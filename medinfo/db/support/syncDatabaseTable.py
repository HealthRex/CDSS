import sys, os, pprint; #pprint is useful for debugging
from sets import Set;
from optparse import OptionParser
from medinfo.db import DBUtil;
from medinfo.db.Model import RowItemModel;
from medinfo.db.Util import ProgressDots;
from CHEM.DB.support import DBCopyFormatter;

def main(argv):
    usageStr =  "usage: %prog [options] <syncTableName>\n"+\
                "   <syncTableName>   Name of the database table to sync from the source DB to the target.\n"+\
                "                     Looks for records by default table ID column.  If not found in target DB,\n"+\
                "                     inserts a new record, otherwise updates the existing record.\n"+\
                "                     A space separated list can be provided to synchronize multiple tables (in order).\n"
                
    parser = OptionParser(usage=usageStr)
    parser.add_option("-c", "--sourceComputer", dest="sourceComputer",  metavar="<sourceComputer>", help="Source database host computer.")
    parser.add_option("-d", "--sourceDatabase", dest="sourceDatabase",  metavar="<sourceDatabase>", help="Source database DSN / name.")
    parser.add_option("-u", "--sourceUsername", dest="sourceUsername",  metavar="<sourceUsername>", help="Source database user name.")
    parser.add_option("-p", "--sourcePassword", dest="sourcePassword",  metavar="<sourcePassword>", help="Source database user password.")
    parser.add_option("-o", "--sourcePort", dest="sourcePort",  metavar="<sourcePort>", help="Source database port.", default=None)
    
    
    parser.add_option("-C", "--targetComputer", dest="targetComputer",  metavar="<targetComputer>", help="Target database host computer.")
    parser.add_option("-D", "--targetDatabase", dest="targetDatabase",  metavar="<targetDatabase>", help="Target database DSN / name.")
    parser.add_option("-U", "--targetUsername", dest="targetUsername",  metavar="<targetUsername>", help="Target database user name.")
    parser.add_option("-P", "--targetPassword", dest="targetPassword",  metavar="<targetPassword>", help="Target database user password.")
    parser.add_option("-O", "--targetPort", dest="targetPort",  metavar="<targetPort>", help="Target database port.", default=None)

    parser.add_option("-r", "--rowIDs", dest="rowIDs",  metavar="<rowIDs>", help="Comma-separated list of IDs to specify which rows to copy / sync.  Leave blank to copy / sync all rows from the source database.");
    parser.add_option('-S', '--syncSequence', dest='syncSequence', action="store_true", help='Add this option to update sequence number from the source table to the target table');
    
    """Assign options (available are above) and args (table names), that were passed via command line when script was executed
    """
    (options, args) = parser.parse_args(argv[1:])

    """Prep conn vars
    """
    sourceConn = None;
    targetConn = None;
    
    """Assign Table names
    """
    syncTableList = args;

    try:
        sourceDB = dict();
        sourceDB["HOST"]= options.sourceComputer;
        sourceDB["DSN"] = options.sourceDatabase;
        sourceDB["UID"] = options.sourceUsername;
        sourceDB["PWD"] = options.sourcePassword;
        if options.sourcePort is not None:
            sourceDB["PORT"] = options.sourcePort;

        targetDB = dict();
        targetDB["HOST"]= options.targetComputer;
        targetDB["DSN"] = options.targetDatabase;
        targetDB["UID"] = options.targetUsername;
        targetDB["PWD"] = options.targetPassword;
        if options.targetPort is not None:
            targetDB["PORT"] = options.targetPort;

        sourceConn = DBUtil.connection( sourceDB );
        targetConn = DBUtil.connection( targetDB );
        
    except Exception, exc:
        print str(exc);
        parser.print_help()
        exit();

    """Check to see if target and source connections are good, and that there were args provided
    """
    if sourceConn is not None and targetConn is not None and len(syncTableList) > 0:
        rowIDStrSet = None;

        """Collect all the rowIDs, if any were provided, and place them individual into an array
           just prep-work for the syncTable function
        """
        if options.rowIDs:
            rowIDStrSet = Set();
            for rowIDStr in options.rowIDs.split(","):
                rowIDStrSet.add(rowIDStr);
        
        """For each table specified, format and sync
        """
        for syncTableName in syncTableList:
            print >> sys.stderr, "Syncing %s" % syncTableName;
            
            ##Resolve formatter to actual class
            myFormatter = None;

            """Sync table data
            """
            syncTable(sourceConn, targetConn, syncTableName, rowIDStrSet, myFormatter);
            
            """Sync sequence number
            """
            if options.syncSequence:
                syncSequence(sourceConn, targetConn, syncTableName)
        
        sourceConn.close();
        targetConn.close();
    else:
        parser.print_help();



def syncSequence(sourceConn, targetConn, syncTableName):
    """Uses last_value Query to get the last value for the sequence from a source table
       And then will alter the sequence to start from that same last value on target table 
    """
    try:
        seqName = DBUtil.sequenceName(syncTableName)
        seqValQuery = "SELECT last_value FROM %s" % seqName
                       
        seqVal = DBUtil.execute( seqValQuery, conn=sourceConn )
        seqVal = int(seqVal[0][0]) + 1; # Add 1 to ensure no overlap
        
        print >> sys.stderr, "Last value of sequence %s, will be updated to %d" % (seqName,seqVal)
        
        altValQuery = "ALTER SEQUENCE %s RESTART WITH %d" % (seqName,seqVal)
        DBUtil.execute( altValQuery, conn=targetConn )
    
    except Exception, exc:
        print "syncSequence Failed: ", str(exc)
        parser.print_help()
        exit()

def syncTable(sourceConn, targetConn, syncTableName, rowIDStrSet=None, formatter=None):
    
    if formatter is None:
        idCol = DBUtil.defaultIDColumn(syncTableName);

        idQuery = "select %s from %s" % (idCol, syncTableName);

        # Collect all of the IDs known in the target database and store in memory for rapid lookup
        print >> sys.stderr, "Querying for IDs from Target Database";
        targetIdTable = DBUtil.execute( idQuery, conn=targetConn );
        targetIdSet = Set();
        for row in targetIdTable:
            targetId = row[0];
            targetIdSet.add(targetId);

        # Query data out of the source table, but do it by a cursor so we can stream through large data tables
        print >> sys.stderr, "Querying for Source Data";
        dataQuery = "select * from %s" % (syncTableName);
        sourceCursor = sourceConn.cursor(); 
        sourceCursor.execute(dataQuery);

        colNames = DBUtil.columnNamesFromCursor(sourceCursor);

        targetCursor = targetConn.cursor();
        
        insertQuery = None;
        updateQuery = None;

        progress = ProgressDots();
        row = sourceCursor.fetchone();
        while row is not None:
            dataModel = RowItemModel( row, colNames );
            
            if rowIDStrSet is None or str(dataModel[idCol]) in rowIDStrSet:
                if rowIDStrSet is not None:
                    print >> sys.stderr, "Syncing record: %s" % dataModel[idCol];
                
                if dataModel[idCol] not in targetIdSet:
                    # Row does not yet exist in target database, need to insert it
                    if insertQuery is None:
                        insertQuery = DBUtil.buildInsertQuery( syncTableName, dataModel.keys() );
                    insertParams= dataModel.values();

                    targetCursor.execute( insertQuery, insertParams );

                else:
                    # Row already exists in target database, just update values
                    if updateQuery is None:
                        updateQuery = DBUtil.buildUpdateQuery( syncTableName, dataModel.keys() );
                    updateParams = [];
                    updateParams.extend( dataModel.values() );
                    updateParams.append( dataModel[idCol] );

                    targetCursor.execute( updateQuery, updateParams );
                    
                if progress.GetCounts() % progress.big == 0:
                    targetConn.commit();
            
            row = sourceCursor.fetchone();
            progress.Update();
        progress.PrintStatus();

        targetConn.commit();
    else:
        ##Do something with thr formatter
        ##Set up the formatter
        theFormatter = formatter(syncTableName, targetConn, includeColumnNames=True, autoCommit=True);
        
        #Call DB execute
        res = DBUtil.execute("select * from %s" % syncTableName, includeColumnNames=True, conn=sourceConn, formatter=theFormatter );



if __name__ == "__main__":
    main(sys.argv)
    
