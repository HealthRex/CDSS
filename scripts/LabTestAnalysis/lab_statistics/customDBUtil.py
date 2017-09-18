#!/usr/bin/env python
"""Utilities for accessing application databases.
Custom DB Util for fetching one row at a time
"""

import sys, os
import time
from datetime import datetime
import json
import csv
from getpass import getpass
from optparse import OptionParser
from medinfo.common.Const import EST_INPUT, COMMENT_TAG, TOKEN_END, NULL_STRING
from medinfo.common.Util import stdOpen, isStdFile, fileLineCount, ProgressDots
from medinfo.common.Util import parseDateValue, asciiSafeStr
from medinfo.db.Model import SQLQuery, RowItemModel
from medinfo.db.Model import modelListFromTable, modelDictFromList
from medinfo.db.Const import DEFAULT_ID_COL_SUFFIX, SQL_DELIM
from medinfo.db.Env import DB_PARAM   # Default connection parameters
# from ResultsFormatter import TextResultsFormatter, TabDictReader
from medinfo.db.Util import log
from medinfo.db import Util

DOUBLE_TOKEN_END = TOKEN_END+TOKEN_END;

###################################################
######### BEGIN Database Specific Stuff ###########
###################################################

from medinfo.db.Env import SQL_PLACEHOLDER, DATABASE_CONNECTOR_NAME

if DATABASE_CONNECTOR_NAME == "psycopg2":
    import psycopg2;
    DB_CONNECTOR_MODULE = psycopg2;
    BOOLEAN = 16;   # Psycopg2 doesn't seem to have a built-in type code constant for BOOLEAN datatype

# Abstract DBAPITypes to check column type codes against
NUMBER = None;
STRING = None;
DATETIME = None;

if DATABASE_CONNECTOR_NAME != "sqlite3":
    # SQLite doesn't have these respective data type entries
    NUMBER = DB_CONNECTOR_MODULE.NUMBER;
    STRING = DB_CONNECTOR_MODULE.STRING;
    DATETIME = DB_CONNECTOR_MODULE.DATETIME;

def connection( connParams=None ):
    """Return a connection to the application database.
    Implementation of this method should change depending upon what
    database is being interfaced to.
    """
    Util.numConnections += 1;

    if connParams is None:
        connParams = DB_PARAM;

    if not connParams.has_key("PWD"):
        connParams["PWD"] = getpass("Enter password for %s on %s@%s: " % (connParams["UID"], connParams["DSN"], connParams["HOST"]) );
        if connParams["PWD"] == "":
            connParams["PWD"] = None;   # Special meaning, no password needed

    if Util.numConnections <= 1:
        log.info("Preparing DB Connection to %(DSN)s@%(HOST)s as %(UID)s" % connParams );

    # PostgreSQL: psycopg2 has slightly different syntax.., need to know if no pass needed..?
    if DATABASE_CONNECTOR_NAME == "psycopg2":
        if (connParams["PWD"] is None):
            if "PORT" in connParams and connParams["PORT"] is not None:
                return psycopg2.connect(host=connParams["HOST"], port=connParams["PORT"], database=connParams["DSN"], user=connParams["UID"]);
            else:
                return psycopg2.connect(host=connParams["HOST"], database=connParams["DSN"], user=connParams["UID"]);
        else:
            if "PORT" in connParams and connParams["PORT"] is not None:
                return psycopg2.connect(host=connParams["HOST"], port=connParams["PORT"], database=connParams["DSN"], user=connParams["UID"], password=connParams["PWD"]);
            else:
                return psycopg2.connect(host=connParams["HOST"], database=connParams["DSN"], user=connParams["UID"], password=connParams["PWD"]);


def identityQuery( tableName , pgSeqName=None):
    """Given a table name, return the SQL query that will return the
    last auto-generated primary key value (i.e. sequences) from that table.
    Abstract this out as the implementation is DB specific.

    Added pgSeqName b/c with long table names the sequence name gets truncated.
    Want to make sure can send in the correct sequence to grab.
    """

    if DATABASE_CONNECTOR_NAME == "psycopg2":
        if pgSeqName is None:
            # currently, NAMEDATALEN is set to 64, so the largest name can be 63 characters
            # the name for a sequence gets cropped before the _seq portion
            pgSeqName = sequenceName( tableName );
        return "select currval('%s')" % pgSeqName; #PostgreSQL

    #return "select @@IDENTITY"  # Access, SQL Server, Sybase

def sequenceName( tableName ):
    """Acquire the PostgreSQL sequence name for a given table name.
    Usually follows a simple auto-generated naming convention pattern of tableName_idColName_seq,
    but needs to be truncated for excessively long table names.
    The proper way is to truncate the table name and id column name at 29 chars each
    """
    idCol = defaultIDColumn(tableName)
    pgSeqName = tableName[:29] + "_" + idCol[:29] + "_seq"
    return pgSeqName; #PostgreSQL auto generated object name for sequence

###################################################
#########  END  Database Specific Stuff ###########
###################################################

class ConnectionFactory:
    """Simple factory object to encapsulate the primary DBUtil.connection function.
    This way, we can pass around the *means* to produce a connection object,
    without having to pass around an actual connection object (which spares
    the caller the responsibility of having to take care of connection
    committing and closing, etc.
    """

    def __init__(self, connParam=None):
        self.connParam = connParam;

    def connection(self):
        return connection( self.connParam );


def execute( query, parameters=None, includeColumnNames=False, incTypeCodes=False,
            conn=None, connFactory=None, autoCommit=True):
    """
    Execute a single SQL query / command against the database and return a generator to get rows one by one
    """
    # Look for an explicitly specified external connection
    extConn = ( conn is not None );
    if conn is None:
        # If no specific connection object provided, look for a connection factory
        #   to produce one
        if connFactory is not None:
            conn = connFactory.connection();
        else:
            # No connection or factory specified, just fall back on default connection then
            conn = connection();

    if parameters is None:
        parameters = ();

    cur  = conn.cursor()

    if isinstance(query,SQLQuery):
        parameters = tuple(query.getParams());
        query = str(query);

    #log.debug(parameterizeQueryString(query,parameters));

    try:
        timer = time.time();
        try:
            cur.execute( query, parameters )
        except Exception, err:
            log.error(err);
            #log.error(parameterizeQueryString(query,parameters));
            if (not extConn) or autoCommit:
                conn.rollback();
            raise;
        timer = time.time() - timer;
        log.debug("Query Time: (%1.3f sec)" % timer );

        if cur.description != None:

            colNames = None;
            if includeColumnNames:
                colNames = columnNamesFromCursor(cur);
                yield colNames

            row = cur.fetchone()
            count = 0
            while row != None:
                yield list(row)
                count += 1
                row = cur.fetchone()
            log.info("%d Rows Completed", count);
        if (not extConn) or autoCommit:
            conn.commit()
    finally:
        if not extConn:     # If caller supplied their own connection, don't close it
            conn.close();   # Leave it as their responsibility what to do with it

def columnNamesFromCursor(cursor):
    """Given a cursor that was just used to execute a query, return the list
    of column names of the result set.
    """
    colNames = []
    for colDesc in cursor.description:
        colNames.append(colDesc[0])   # First item in each column description should be the name
    return colNames

def runDBScript( scriptFile, skipErrors = False ):
    """Given a DB script file object (caller should handle the opening by filename or other method),
    run each command as a SQL statement, delimited by semicolons (;) at the end of a line.
    
    If there are any errors running a command in the file and the skipErrors parameter is True,
    then this will continue to run the rest of the script, just logging the error message.
    Otherwise, if skipErrors is False, the exception will be raised out of this method.
    """
    conn = connection()
    cur  = conn.cursor()
    
    try:
        sqlLines = [] # As list of lines (strings) until meet semicolon terminator (more efficient than string concatenation)
        for line in scriptFile:
            if not line.startswith(COMMENT_TAG):  # Note, standard SQL comments are auto-ignored ("--" and "/* */")
                sqlLines.append(line)
                if line.strip().endswith(SQL_DELIM):
                    sql = str.join("",sqlLines)
                    log.debug("Executing in Script: "+ sql)
                    try:
                        cur.execute( sql )
                        # Need to "auto-commit" after each command, 
                        #   otherwise a skipped error will rollback 
                        #   any previous commands as well
                        if skipErrors: 
                            conn.commit()    
                    except Exception, err:
                        conn.rollback();    # Reset changes and connection state
                        if skipErrors:
                            log.warning("Error Executing in Script: "+ sql )
                            log.warning(err)
                        else:
                            raise err
                    sqlLines = []
        conn.commit()
    finally:
        conn.close()