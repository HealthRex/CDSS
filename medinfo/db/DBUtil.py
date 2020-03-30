#!/usr/bin/env python
"""Utilities for accessing application databases.
Refer to http://www.python.org/topics/database/modules.html
for more information.

Note that besides the primary DB interface module you need to
setup (see the comments in the import sections below), many
of these also depend on the eGenix mx Extensions BASE package.  
mxDateTime in particular.  This is available at...
http://www.egenix.com/files/python/ 

If using different DB-API modules, this module should
be edited in the following places...
    - module import statements
    - Env.SQL_PLACEHOLDER (in Env.py file)
    - connection method (including references to Env constants)
    - identityQuery method
"""

import sys, os
import subprocess
import time;
from datetime import datetime;
import json;
import csv;
from getpass import getpass;
from optparse import OptionParser
from medinfo.common.Const import EST_INPUT, COMMENT_TAG, TOKEN_END, NULL_STRING;
from medinfo.common.Util import stdOpen, isStdFile, fileLineCount, ProgressDots;
from medinfo.common.Util import parseDateValue, asciiSafeStr;
from Model import SQLQuery, RowItemModel;
from Model import modelListFromTable, modelDictFromList;
from Const import DEFAULT_ID_COL_SUFFIX, SQL_DELIM;
from Env import DB_PARAM;   # Default connection parameters
from ResultsFormatter import TextResultsFormatter, TabDictReader;
from Util import log;
from medinfo.db import Util;

DOUBLE_TOKEN_END = TOKEN_END+TOKEN_END;

###################################################
######### BEGIN Database Specific Stuff ###########
###################################################

import Env;
SQL_PLACEHOLDER = Env.SQL_PLACEHOLDER;

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
    
    # MySQLdb
    if Env.DATABASE_CONNECTOR_NAME == "mysql.connector":
        import mysql.connector; 
        conn = mysql.connector.Connect(user=connParams["UID"], password=connParams["PWD"], host=connParams["HOST"], database=connParams["DSN"], buffered=True);
        return conn;
    
    if Env.DATABASE_CONNECTOR_NAME == "MySQLdb":
        import MySQLdb; 
        conn = MySQLdb.connect( host=connParams["HOST"], user=connParams["UID"], passwd=connParams["PWD"], db=connParams["DSN"]);
        return conn;

    # PostgreSQL: psycopg2 has slightly different syntax.., need to know if no pass needed..?
    if Env.DATABASE_CONNECTOR_NAME == "psycopg2":
        import psycopg2; 
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

    if Env.DATABASE_CONNECTOR_NAME == "cx_Oracle":
        import cx_Oracle; 
        connStr = "%(UID)s/%(PWD)s@%(HOST)s/%(DSN)s" % connParams;
        if "PORT" in connParams:
            connStr = "%(UID)s/%(PWD)s@%(HOST)s:%(PORT)s/%(DSN)s" % connParams;
        return cx_Oracle.connect(connStr);

    if Env.DATABASE_CONNECTOR_NAME == "sqlite3":
        import sqlite3;
        return sqlite3.connect(os.path.join(connParams["DATAPATH"], connParams["DSN"]));

def identityQuery( tableName , pgSeqName=None):
    """Given a table name, return the SQL query that will return the
    last auto-generated primary key value (i.e. sequences) from that table.
    Abstract this out as the implementation is DB specific.
    
    Added pgSeqName b/c with long table names the sequence name gets truncated.  
    Want to make sure can send in the correct sequence to grab.  
    """
    if Env.DATABASE_CONNECTOR_NAME in ("mysql.connector", "MySQLdb"):
        return "select last_insert_id()";
    
    if Env.DATABASE_CONNECTOR_NAME == "psycopg2":
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

def createDatabase( dbParams ):
    """Create a database based on the DSN name specified in the dbParams.
    Will likely require logging in first as the user-password specified in the dbParams.
    """
    if Env.DATABASE_CONNECTOR_NAME == "psycopg2":
        # For PostgreSQL, have to connect to some database first before can create a new one. Connect to default "postgres" database to start.
        defaultParams = dict(dbParams);
        defaultParams["DSN"] = "postgres";
        defaultConn = connection(defaultParams);
        defaultConn.autocommit = True;  # Create/Drop Database not allowed in transaction blocks
        try:
            execute("CREATE DATABASE %s" % dbParams["DSN"], conn=defaultConn);
        finally:
            defaultConn.close();
    elif Env.DATABASE_CONNECTOR_NAME == "sqlite3":
        defaultParams = dict(dbParams);
        # Sqlite3 automatically creates a database upon connection
        defaultConn = connection(defaultParams);
        # None for autocommit mode
        defaultConn.isolation_level = None
        defaultConn.close()

def dropDatabase( dbParams ):
    """Drop the database specified by the DSN name specified in the dbParams.
    Will likely require logging in first as the user-password specified.
    """
    if Env.DATABASE_CONNECTOR_NAME == "psycopg2":
    # For PostgreSQL, cannot drop database while connected to it, so connect to default "postgres" database to start.
        defaultParams = dict(dbParams);
        defaultParams["DSN"] = "postgres";
        defaultConn = connection(defaultParams);
        defaultConn.autocommit = True;  # Create/Drop Database not allowed in transaction blocks
        try:
            execute("DROP DATABASE %s" % dbParams["DSN"], conn=defaultConn);
        finally:
            defaultConn.close();
    elif Env.DATABASE_CONNECTOR_NAME == "sqlite3":
        defaultParams = dict(dbParams);
        # Sqlite3 automatically creates a database upon connection
        try:
            os.remove(os.path.join(defaultParams['DATAPATH'], defaultParams["DSN"]))
        except:
            pass

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


def execute( query, parameters=None, includeColumnNames=False, incTypeCodes=False, formatter=None, 
            conn=None, connFactory=None, autoCommit=True):
    """Execute a single SQL query / command against the database.
    If the description attribute is not None, this implies
    this was a select statement that produced a result set which 
    will be returned by the fetchall() method.
    
    If the description is null, then at least return the rowcount
    affected by the query.  This may be -1 or None still
    if it is a non-row affecting command (e.g. create / drop).
    
    If includeColumnNames is true and the query yields a result set,
    then one row (list) will be added to the beginning which contains
    the names of each column as extracted from the cursor.description.
    
    If incTypeCodes is true and the query yields a result set, a row (list)
    will be added to the beginning (but after column names if those are
    included as well), which contains the numerical type codes of
    each column as extracted from the cursor.description.
    
    This method is probably not terribly efficient and should 
    only be used for prototype testing and short command line functions.
    For retrieving data to send to stdout or some other stream,
    add the formatter parameter as an instance of a ResultFormatter
    object to pipe the data through one fetch at a time.  In that case,
    the full results (which are presumably large) will NOT be returned
    by the method.
    
    If the query object is actually a SQLQuery object, then will
    use the SQLQuery.getParams() as the params, and str(SQLQuery)
    as the query string.
    
    If autoCommit is True, will autoCommit.  The function will also autoCommit if an external connection 
    is NOT supplied.  
    """
    # Look for an explicitly specified external connection
    extConn = conn is not None
    if conn is None:
        # If no specific connection object provided, look for a connection factory
        #   to produce one
        if connFactory is not None:
            conn = connFactory.connection()
        else:
            # No connection or factory specified, just fall back on default connection then
            conn = connection()

    cur = conn.cursor()
    
    if isinstance(query, SQLQuery):
        if parameters is None:
            parameters = tuple(query.getParams())
        else:
            parameters = tuple(parameters)
        query = str(query)
    elif parameters is None:
        parameters = ()

    #log.debug(parameterizeQueryString(query,parameters));

    returnValue = None    
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
            returnValue = []

            colNames = None;
            if includeColumnNames:
                colNames = columnNamesFromCursor(cur);
                returnValue.append(colNames)

            if incTypeCodes:
                typeCodes = typeCodesFromCursor(cur);
                returnValue.append(typeCodes);
            
            
            if formatter != None:
                # An output formatter was specified, pipe the data out one row at time
                if includeColumnNames:
                    formatter.formatTuple(colNames)
                
                progress = ProgressDots();
                row = cur.fetchone()
                while row != None:
                    formatter.formatTuple(row)
                    row = cur.fetchone()
                    progress.Update();
                log.info("%d Rows Completed",progress.GetCounts());                

                returnValue = cur.rowcount
            else:
                # No formatter specified, just return the entire result set
                dataTable = list(cur.fetchall());
                for i, row in enumerate(dataTable):
                    dataTable[i] = list(row);
                returnValue.extend(dataTable);
        else:
            returnValue = cur.rowcount
        if (not extConn) or autoCommit: 
            conn.commit()
    finally:
        if not extConn:     # If caller supplied their own connection, don't close it
            conn.close();   # Leave it as their responsibility what to do with it
    
    return returnValue


def columnNamesFromCursor(cursor):
    """Given a cursor that was just used to execute a query, return the list
    of column names of the result set.
    """
    colNames = [];
    for colDesc in cursor.description:
        colNames.append(colDesc[0])   # First item in each column description should be the name
    return colNames;

def typeCodesFromCursor(cursor):
    """Given a cursor that was just used to execute a query, return the 
    list numerical column type codes for the result set.
    """
    typeCodes = [];
    for colDesc in cursor.description:
        typeCodes.append(colDesc[1])   # Second item in each column description should be the code
    return typeCodes;

def nextRowModel(cursor):
    """
    """
    nextModel = None;
    nextRow = cursor.fetchone();
    if nextRow is not None:
        nextModel = RowItemModel(nextRow, columnNamesFromCursor(cursor));   # Inefficient because builds column name list each time
    return nextModel;

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
                        log.warning("Error Executing in Script: "+ sql )
                        log.warning(err)
                        if not skipErrors:
                            raise err
                    sqlLines = []
        conn.commit()
    finally:
        conn.close()

def normalizeColName( col ):
    """Normalize column name string for consistent use as dictionary key"""
    normCol = col.strip().lower();
    if normCol.startswith(TOKEN_END) and normCol.endswith(TOKEN_END):
        normCol = normCol[1:-1];
    return normCol;

def insertFile( sourceFile, tableName, columnNames=None, delim=None, idFile=None, skipErrors=False, dateColFormats=None, escapeStrings=False, estInput=None, connFactory=None ):
    """Insert the contents of a whitespace-delimited text file into the database.
    
    For PostgreSQL specifically, consider alternative direct COPY command that can run 10x:
    E.g., gzip -d -c TTeam_2014.tsv.gz | psql -U jonc101 -c "COPY tteamx (  pat_deid,  enc_deid,  relation,  prov_id,  prov_name,  start_date,  end_date ) FROM STDIN WITH (FORMAT csv, DELIMITER E'\t', HEADER, NULL 'None');" resident-access-log-2017

    Inserts the contents of the <sourceFile> into the database
    under the <tableName>.  One line is expected in the <sourceFile>
    per row in the database, with each item delimited by the <delim>
    character.  These items will be inserted under the respective
    order of the given list of columnNames.

    Use the built-in csv module for parsing out lines and managing quotes, etc.
    If delimiter is not specified (None), then default to tab-delimited
    
    If idFile is provided, then will try to run SQL from identityQuery method
    after each insert, and write out the contents, one per line to the idFile.
    Will bypass above step if can find an insert column with the expected default ID column ("tableName_id")
    
    If dateColFormats provided, expect a dictionary keyed by the names of columns
    that should be as interpreted date strings, with values equal to the 
    Python date format string to parse them by.  
    If a format string is not provided, a series of standard date format strings will be attempted 
    (but this is inefficient for repeated date text parsing and error handling).
    
    Returns the total number of rows successfully inserted.
    """
    if columnNames is not None and len(columnNames) < 1:
        columnNames = None; # If empty columnNames list, then reset to null and look for it in first line of data

    reader = TabDictReader(sourceFile, fieldnames=columnNames, delimiter=delim);
    columnNames = reader.fieldnames;

    idCol = defaultIDColumn(tableName);
    iIdCol = None;  # Index of manually specified ID column. May be null
    for iCol, colName in enumerate(columnNames):
        if colName == idCol:
            iIdCol = iCol;

    if dateColFormats is not None:
        # Ensure column keys are normalized
        dateCols = dateColFormats.keys();
        for dateCol in dateCols:
            normalCol = normalizeColName(dateCol);
            dateColFormats[normalCol] = dateColFormats[dateCol];

    conn = None;
    if connFactory is not None:
        conn = connFactory.connection();
    else:
        conn = connection()
    cur  = conn.cursor()
    
    try:
        # Prepare the SQL Statement
        sqlParts = []
        sqlParts.append("insert into")
        sqlParts.append( tableName )

        sqlParts.append("(")
        sqlParts.append( str.join(",", columnNames) );
        sqlParts.append(")")

        sqlParts.append("values")
        sqlParts.append("(")
        for i in range(len(columnNames)):
            sqlParts.append( Env.SQL_PLACEHOLDER )    # Parameter placeholder, depends on DB-API
            sqlParts.append(",")
        sqlParts.pop(); # Remove extra end comma
        sqlParts.append(")")

        sql = str.join(" ",sqlParts)

        log.debug(sql)
        

        # Loop through file and execute insert statement everytime find enough delimited parameters.  
        nInserts = 0
        nCols = len(columnNames)
        params = list();
        progress = ProgressDots(total=estInput);
        for iLine, rowModel in enumerate(reader):
            # Parse out data values from strings
            for iCol, colName in enumerate(columnNames):
                value = parseValue(rowModel[colName], colName, dateColFormats, escapeStrings);
                params.append(value);

            log.debug(params)
            try:
                cur.execute(sql,tuple(params))
                nInserts += cur.rowcount

                if idFile != None:
                    rowId = None;
                    if iIdCol is not None:  # Look for manually assigned ID value first
                        rowId = params[iIdCol];
                    else:
                        cur.execute(identityQuery(tableName));
                        rowId = cur.fetchone()[0];
                    print >> idFile, rowId;

                # Need to "auto-commit" after each command, 
                #   otherwise a skipped error will rollback 
                #   any previous commands as well
                if skipErrors: 
                    conn.commit()    

                progress.Update()

            except Exception, err:
                log.info(sql);
                log.info(tuple(params))
                conn.rollback();    # Reset any changes since the last commit
                if skipErrors:
                    log.warning("Error Executing in Script: "+ sql )
                    log.warning(err)
                else:
                    raise;
            params = list();

        conn.commit()

        return nInserts

    finally:
        conn.close()

    return 0    


def updateFromFile( sourceFile, tableName, columnNames=None, nIdCols=1, delim=None, skipErrors=False, connFactory=None  ):
    """Update the database with the contents of a whitespace-delimited text file.
    
    Updates the contents of the <tableName> with the data from the <sourceFile>.  
    One line is expected in the <sourceFile> per row in the database, with each item 
    delimited by the <delim> character (specify None for any whitespace).  
    These items will be inserted under the respective order of the given list of 
    <columnNames>.  If the columnNames parameter is not provided, assume the
    first line of the <sourceFile> contains the column names.

    To know which rows to update, assume the FIRST column listed in <columnNames> is
    the ID column to identify rows by.  In that case, the data value there from the
    <sourceFile> will not be used to update the row, but will instead be used to
    identify the row to update the rest of the data by.  If more than one column
    is necessary to identify a row (composite key), indicate how many of the
    first columns in <columnNames> should be used with <nIdCols>.  Note that these key ID 
    values must not be None / null.  The query looks for rows where columnname = value,
    and the = operator always returns false when the value is null.

    Returns the total number of rows successfully updated.
    """
    if columnNames is None or len(columnNames) < 1:
        headerLine = sourceFile.readline();
        columnNames = headerLine.split(delim);
    
    conn = None;
    if connFactory is not None:
        conn = connFactory.connection();
    else:
        conn = connection()
    cur  = conn.cursor()

    nCols = len(columnNames);
    
    try:
        # Prepare the SQL Statement
        sql = [];
        sql.append("update");
        sql.append( tableName );
        sql.append("set");

        # Data Columns
        for i in xrange(nIdCols,nCols):
            sql.append(columnNames[i]);
            sql.append("=");
            sql.append(Env.SQL_PLACEHOLDER);
            sql.append(",");
        sql.pop();  # Remove extra comma at end

        # ID Columns
        sql.append("where")
        for i in xrange(nIdCols):
            sql.append(columnNames[i]);
            sql.append("=");
            sql.append(Env.SQL_PLACEHOLDER);
            sql.append("and");
        sql.pop();  # Remove extra comma at end

        sql = str.join(" ",sql);

        log.debug(sql)

        # Loop through file and execute update statement for every line
        progress = ProgressDots()
        for iLine, line in enumerate(sourceFile):
            if not line.startswith(COMMENT_TAG):
                try:
                    line = line[:-1];    # Strip the newline character
                    params = line.split(delim);
                    
                    # Special handling for null / None string
                    for iParam in xrange(len(params)):
                        if params[iParam] == "" or params[iParam] == NULL_STRING:   # Treat blank strings as NULL
                            params[iParam] = None;

                    # Reposition ID columns to end of parameter list
                    idParams = params[:nIdCols];
                    dataParams = params[nIdCols:];
                    paramTuple = dataParams;
                    paramTuple.extend( idParams );
                    paramTuple = tuple(paramTuple);
                    
                    cur.execute(sql, paramTuple);

                    # Need to "auto-commit" after each command, 
                    #   otherwise a skipped error will rollback 
                    #   any previous commands as well
                    if skipErrors:
                        conn.commit()    

                    progress.Update()

                except Exception, err:
                    conn.rollback();    # Reset changes and connection state
                    log.critical(sql);
                    log.critical(paramTuple);
                    log.warning("Error Executing in Script: %s", parameterizeQueryString(sql,paramTuple) );
                    if skipErrors:
                        log.warning(err)
                    else:
                        raise err

        conn.commit()

        return progress.GetCounts();

    finally:
        conn.close()

    return 0    


def dumpTableToCsv(table_name, file_name, conn_params=None):
    if conn_params is None:
        conn_params = DB_PARAM

    psql_env = os.environ.copy()
    psql_env["PGPASSWORD"] = conn_params["PWD"]
    process = subprocess.Popen(['psql', '-U', conn_params["UID"], '-d', conn_params["DSN"],
                                '-c', '\\COPY {} TO \'{}\' DELIMITER \',\' CSV HEADER;'.format(table_name, file_name)],
                               env=psql_env)
    process.wait()


def findOrInsertItem(tableName, searchDict, insertDict=None, retrieveCol=None, forceUpdate=False, autoCommit=True, conn=None, connFactory=None):
    """Search the named table in database for a row whose attributes match the key-value pairs specified in searchDict.  

    If one exists, then return the column (probably the primary key) named by retrieveCol.  
    Otherwise, insert a row into the table with the data specified in the insertDict key-value pairs
    and try accessing the retrieveCol again (presumably the one just inserted).  
    
    If forceUpdate is specified as True, then, even if the row already exists in the database, 
    update the row to match the contents of the insertDict.
    
    The connection object to the database (conn) can be specified, otherwise it will just default 
    to that returned by the connection() method.  If no insertDict is specified, use the searchDict 
    as necessary.  If no retrieveCol is specified, then will attempt to find the default primary 
    key column based on the table name.

    Returns a tuple (col, isNew) where col is the value of the retrieveCol and isNew is a boolean 
    indicating if this came from a new row just inserted or if it was just taken from an existing record.
    """
    extConn = ( conn is not None );
    if insertDict == None:
        insertDict = searchDict 
    if conn == None:
        # If no specific connection object provided, look for a connection factory to produce one
        if connFactory is not None:
            conn = connFactory.connection();
        else:
            # No connection or factory specified, just fall back on default connection then
            conn = connection();
    
    try:
        cur = conn.cursor()

        # Create the query for checking if it's already in the database
        searchQuery = SQLQuery();
        
        if retrieveCol == None:
            searchQuery.addSelect(defaultIDColumn(tableName));
        else:
            searchQuery.addSelect(retrieveCol);
        searchQuery.addFrom(tableName)

        for i, (col, value) in enumerate(searchDict.iteritems()):
            if value is not None:
                searchQuery.addWhereEqual(col, value);
            else:
                # Equals operator doesn't work for null values
                searchQuery.addWhereOp(col,"is",value);

        # Convert query as a model into a single string
        searchParams= searchQuery.params;
        searchQuery = str(searchQuery);
        log.debug("Before Select Query: "+ parameterizeQueryString( searchQuery, searchParams ) );

        # Check if the retrieveCol is already in the database, 
        #   by these search criteria
        cur.execute( searchQuery, searchParams );
        result = cur.fetchone()
        
        log.debug("After Select/fetchone Query: "+ parameterizeQueryString( searchQuery, searchParams ) );
        
        rowExisted = result is not None;
        
        if ( rowExisted ):
            if forceUpdate:
                # Item already exists, but want to force an update with the insertDict contents
                updateRow( tableName, insertDict, searchDict.values(), searchDict.keys(), conn=conn );
                cur.execute( searchQuery, searchParams );
                result = cur.fetchone()
            return (result[0], not rowExisted)
        else:
            # Item does not yet exist.  Insert it, then get the retrieveCol again.
            insertRow( tableName, insertDict, conn=conn, cursor=cur );
            
            # allow user to not commit when providing his/her own connection
            if not extConn or autoCommit:
                conn.commit();

        # Now that insert or update has completed, try to retrieve the data again,
        # using sequences if possible
        #if retrieveCol is None:
            #cur.execute(identityQuery(tableName));
        #else:
        # comment out the above because it wasn't working for some tables.
        cur.execute( searchQuery, searchParams );
        result = cur.fetchone()
        if (result != None):
            # Returning data from the just inserted item
            return (result[0], not rowExisted)
        else:
            log.warning("For table "+tableName+", could not find "+ str(searchDict) +" even after inserting "+ str(insertDict) )
            return (None, None)
    finally:
        if not extConn:
            conn.close();   # If we opened the connection ourselves, then close it ourselves

def insertRow(tableName, insertDict, conn=None, cursor=None):
    """Insert a record into the named table based on the contents of the provided row dictionary (RowItemModel)"""
    extConn = ( conn is not None );
    if not extConn: conn = connection();
    extCursor = (cursor is not None);
    if cursor is None:
        cursor = conn.cursor();
    try:
        insertQuery = buildInsertQuery( tableName, insertDict.keys() );
        insertParams= insertDict.values();

        # Convert component list into string
        log.debug( parameterizeQueryString( insertQuery, insertParams ) );

        cursor.execute( insertQuery,insertParams );
    finally:
        if not extCursor:
            cursor.close();
        if not extConn:
            conn.close();

def updateRow(tableName, rowDict, idValue, idCol=None, conn=None):
    """Adapted from Jocelyne's function.  Given a dictionary object (RowItemModel)
    representing a row of a database table, and identified by the key value(s),
    update the database to match the dictionary object.

    idCol is the name of the key column(s).  Will assume a default based on the 
        table name if this not supplied.  Or, supply a list of values if a composite key is used.
    idValue has the value of the key columns used to identify the row we wish to update.  
        Again, supply a list if a composite key is used.
    """
    extConn = ( conn is not None );

    if conn     == None: conn = connection();
    if idCol    == None: idCol = defaultIDColumn( tableName );
    if not isinstance( idValue, list ): idValue = [idValue];    # Convert to list of size 1
    if not isinstance( idCol, list ):   idCol = [idCol];

    query = buildUpdateQuery(tableName, rowDict.keys(), idCol, idValue );
    params = [];
    params.extend( rowDict.values() );
    params.extend( idValue );

    try:
        cursor = conn.cursor()
        cursor.execute( query, tuple(params) );
        conn.commit()
    finally:
        if not extConn:
            conn.close();

def deleteRows(tableName, idValues, idCol=None, conn=None):
    """
    Delete rows from the designated table based on the specified idValue (list).
    
    idCol is the name of the key column(s).  
        Will assume a default based on the  table name if this not supplied.
    idValues has the list of values of the key column used to identify the rows we wish to delete.  
    """
    if len(idValues) < 1:
        # Nothing productive to do.
        return;
    
    extConn = ( conn is not None );

    if conn     == None: conn = connection();
    if idCol    == None: idCol = defaultIDColumn( tableName );

    try:
        cursor = conn.cursor()

        params = idValues;
        paramPlaceholders = str.join(",", [Env.SQL_PLACEHOLDER]*len(params) );

        query = """delete from %s where %s in (%s)""" % (tableName, idCol, paramPlaceholders);

        cursor.execute( query, tuple(params) );

        conn.commit()
    finally:
        if not extConn:
            conn.close();

def parseValue(chunk,colName,dateColFormats=None,escapeStrings=False):
    """As needed, parse the input string value into an object representation.
    In particular, convert NULL_STRINGs into None values,
    and if the colName is found in the dateColFormats, try converting
    the string object into a datetime object.
    """
    normalCol = colName.lower();    # Normalize against capitalization variation
    
    returnValue = chunk;
    if chunk is None or chunk == "" or chunk == NULL_STRING:     # Treat blanks as None/NULL
        returnValue = None;
    elif dateColFormats is not None and normalCol in dateColFormats:
        # This value intended to be intended as datetime object.  Try parsing it out
        dateFormat = dateColFormats[normalCol];
        returnValue = parseDateValue(chunk,dateFormat);
    elif chunk is not None and escapeStrings:
        # Generic string value, but run through escape encoder so weird non-ascii characters don't make DB process crash
        returnValue = chunk.encode('string_escape');
        #returnValue = asciiSafeStr(chunk);  # Clean up any weird unicode characters

    return returnValue;

def defaultIDColumn(tableName):
    """Given a DB table's name, return the default name
    for the primary key ID column.
    """
    return tableName + DEFAULT_ID_COL_SUFFIX;

def defaultForeignKeyTable(foreignKeyName):
    """Given the column name of a foreign key in a table, assume it is named by convention
    and return the name of the table that it references.  If the provided name does not
    appear to be a default / conventional foreign key name, returns None.
    """
    if foreignKeyName.endswith(DEFAULT_ID_COL_SUFFIX):
        return foreignKeyName[0:-len(DEFAULT_ID_COL_SUFFIX)];
    return None;

def smallestAvailableValue(tableName, column, absoluteMinimum=0, conn=None, connFactory=None):
    """Returns the smallest value that does NOT exist
    as one of the column entries in the given table, but which
    is still greater than the absoluteMinimum.
    Only makes sense for integer columns.
    This is a means to look for unused ID numbers.

    Uses a highly specialized database query using an except (essentially a Set "diff" operator)
    and offsets of IDs by 1 (assumes integers with smallest interval being 1).
    """
    queryDict = {"tableName": tableName, "column": column, "absoluteMinimum": absoluteMinimum };
    
    minAvailableValue = \
        execute \
        (   """
            select 
                min(%(column)s)+1
            from
            (
                select %(column)s
                from %(tableName)s
                where %(column)s > %(absoluteMinimum)s

                except

                select %(column)s-1
                from %(tableName)s
                where %(column)s > %(absoluteMinimum)s

            ) as valuessWithBlankAbove
            """ % queryDict,
            conn=conn,
            connFactory=connFactory
        )[0][0];
    return minAvailableValue;

def buildUpdateQuery(tableName, colNames, idColName=None, idValue=None):
    """Given a table and a list of column names under that table,
    including the primary key ID column, construct a parameterized SQL update query.
    
    May need to supply sample idValues even though they won't be a part of the query directly.
    If any values are null, will have to use a different comparison operator ('is' instead of '=').
    """
    if idColName is None:   idColName = defaultIDColumn(tableName);
    if isinstance(idColName,str):  idColName = [idColName];    # List of size 1
    
    if idValue is None:    idValue = idColName; # Just a same sized placeholder then
    if not isinstance(idValue, list):   idValue = [idValue];
    
    # Prepare the SQL Statement
    sql = [];
    sql.append("update");
    sql.append( tableName );
    sql.append("set");

    # Data Column Values
    for col in colNames:
        sql.append(col);
        sql.append("=");
        sql.append(Env.SQL_PLACEHOLDER);
        sql.append(",");
    sql.pop();  # Remove extra comma at end
    
    # ID Columns
    sql.append("where")
    for col, value in zip(idColName, idValue):
        sql.append(col);
        if value is not None:
            sql.append("=");
        else:
            # Equals operator doesn't work for null values
            sql.append("is");
        sql.append(Env.SQL_PLACEHOLDER);
        sql.append("and");
    sql.pop();  # Remove extra "and" at end

    sql = str.join(" ",sql);
    return sql;

def buildInsertQuery(tableName, colNames):
    """Given a table and a list of column names under that table,
    construct a parameterized SQL insert query
    """
    query = ["insert into %s (" % tableName];
    
    # Column Names
    for col in colNames:
        query.append("%s" % col);
        query.append(",");
    query[-1] = ")";    # Drop the last extraneous ","
    
    # Value placeholders
    query.append("values (");
    for col in colNames:
        query.append("%s" % Env.SQL_PLACEHOLDER);
        query.append(",");
    query[-1] = ")";        
    
    query = str.join(" ", query);
    return query;


def parameterizeQueryString( query, params=None ):
    """Given a SQL query string and tuple of parameters,
    replace all of the Env.SQL_PLACEHOLDER strings in the query
    with the respective representation of the parameters.
    For the most part, this will just be the string representation
    of the parameter except in the case of str objects which
    should be enclosed in ' quote marks, and have all such internal
    quote marks "escaped" to \'
    
    This is usually done internally by the DB-API modules, but this
    replicates the behavior externally for the purpose of generating
    query strings.
    
    Instead of providing the query as a string and a parameter tuple,
    you can instead just provide a SQLQuery object and this will
    use the string representation of that, and the params contents in it.
    """
    if isinstance(query,SQLQuery):
        params = query.getParams();
        query = str(query);

    # Make sure all of the Env.SQL_PLACEHOLDERS are Python string replacement vars
    query = query.replace(Env.SQL_PLACEHOLDER,"%s");
    
    # Modify parameter list if any text-based variables to replace
    if params:
        modParams = [];
        for i, param in enumerate(params):
            if isinstance(param,str):
                param = "'"+ param.replace("'","\\'") +"'"
            modParams.append(param);
        query = query % tuple(modParams);
    return query;

def loadTableAsDict( tableName, connFactory=None ):
    """Load the contents of the named table into a dictionary.  Data are RowItemModels
    representing the contents and keys are the respective row item IDs.
    """
    dataTable = execute("select * from %s" % tableName, includeColumnNames=True, connFactory=connFactory);
    dataModels = modelListFromTable(dataTable);
    dataModelsById = modelDictFromList(dataModels, defaultIDColumn(tableName) );
    return dataModelsById;

def loadRecordModelById( tableName, idValue, idCol=None, conn=None, connFactory=None ):
    """Load an individual record model by an ID value 
    that is presumed to exist and be unique.
    """
    if idCol is None:
        idCol = defaultIDColumn(tableName);
    query = "select * from %s where %s = %s" % (tableName, idCol, Env.SQL_PLACEHOLDER);
    params = (idValue,);
    dataTable = execute( query, params, includeColumnNames=True, conn=conn, connFactory=connFactory);
    dataModels = modelListFromTable(dataTable);
    keyModel = dataModels[0];   # Assume that exactly 1 row item will exist
    return keyModel;

def main(argv):
    """Main method, callable from command line"""
    usageStr =  "usage: %prog [options] <query> [<outputFile>]\n"+\
                "   <query>         Query to execute (probably enclosed in quotes (\"))\n"+\
                "   <outputFile>    If query yields a result set, then that will be output\n"+\
                "                       to the named file.  Specify \"-\" to send to stdout.\n"
    parser = OptionParser(usage=usageStr)
    parser.add_option("-c", "--incCols",    dest="incCols",     action="store_true",    help="If set when executing a SELECT statement, then a line will be added before the result set with the names of the data columns.")
    parser.add_option("-C", "--incCommand", dest="incCommand",  action="store_true",    help="If set when executing a SELECT statement, then add a comment header line with the command-line argv.")
    parser.add_option("-s", "--script",     dest="script",      action="store_true",    help="Interpret the first argument <query> as the name of a DB (SQL) script to run instead.  Use \"-\" to specify stdin.")
    parser.add_option("-i", "--input",      dest="input",       metavar="<inputFile>",  help="Open the named whitespace-delimted file and insert its contents into the database.  Use with -t option.  The remaining \"normal\" arguments are expected and will be taken as the ordered list of column names the file data is to be inserted under.  Alternatively, the first row of the file will be considered the column names.  Use \"-\" to specify stdin.")
    parser.add_option("-u", "--update",     dest="update",      metavar="<dataFile>",   help="Open the named whitespace-delimted file and update its contents into the database.  Use with -t and -n options.  The remaining \"normal\" arguments are expected and will be taken as the ordered list of column names the file data is to be updated under.  Alternatively, the first row of the file will be considered the column names.  Use \"-\" to specify stdin.");
    parser.add_option("-t", "--table",      dest="table",       metavar="<tableName>",  help="If inserting / updating a file with the -i or -u option, specify the name of the DB table to insert into")
    parser.add_option("-d", "--delim",      dest="delim",       metavar="<delimiter>",  help="If inserting / updating a file with the -i or -u  option, specify the character to delimit values by.  Default to \\t tabs, but can specify something else. Alternatively, this can be used to specify what delimiter to use when formatting query output.")
    parser.add_option("-n", "--nIdCols",    dest="nIdCols",     default="1",            help="If updating a file with the -u  option, assume that the first column is the ID column not to update into the database, but to identify the respective row to update.  If more than 1 column is needed, specify with this option.")
    parser.add_option("-o", "--output",     dest="output",      metavar="<outputFile>", help="If inserting a file with the -i option and want to get generated ID numbers from the inserted rows, specify this file to send them to.")
    parser.add_option("-e", "--skipErrors", dest="skipErrors",  action="store_true",    help="If inserting or updating a file or running a script with the -s option, keep running the remainder of the inserts or script commands even if one causes an exception.")
    parser.add_option("-f", "--dateColFormats", dest="dateColFormats",  metavar="<dateColFormats>",    help="If inserting a file, can specify columns that should be interpreted as date strings to be parsed into datetime objects.  Provide comma-separated list, and optional | separated Python date parsing format (e.g., 'MyDateTime1|%m/%d/%Y %H:%M:%S,MyDateTime2').  http://docs.python.org/library/datetime.html#strftime-strptime-behavior.")
    parser.add_option("-x", "--escapeStrings", dest="escapeStrings",  action="store_true",    help="If inserting a file, can set whether to run all input strings through escape filter to avoid special characters compromising inserts.")
    (options, args) = parser.parse_args(argv[1:])

    # Correct escape character delimiter
    if options.delim == "\\t":  options.delim = "\t";

    log.info("Starting: "+str.join(" ", argv))
    timer = time.time();
    if options.script and len(args) > 0:
        runDBScript( stdOpen(args[0],"r",sys.stdin), options.skipErrors )
    elif options.input is not None and options.table is not None:
        inputFile   = stdOpen(options.input,"r",sys.stdin)
        outputFile  = None
        if options.output != None:
            outputFile = stdOpen(options.output,"w",sys.stdout)
        
        dateColFormats = None;
        if options.dateColFormats is not None:
            dateColFormats = dict();
            colDateFormatComponents = options.dateColFormats.split(",");
            for colDateFormatComponent in colDateFormatComponents:
                colFormatChunks = colDateFormatComponent.split("|");
                colName = colFormatChunks[0];
                formatStr = None;
                if len(colFormatChunks) > 1:
                    formatStr = colFormatChunks[1];
                dateColFormats[colName] = formatStr;
        
        # If reading from a file (not standard input stream), do an extra pass to get size estimate to facilitate progress tracker
        estInput = None;
        if not isStdFile(options.input):
            lineCountFile = stdOpen(options.input);
            estInput = fileLineCount(lineCountFile);

        nInserts = insertFile( inputFile, options.table, args, options.delim, outputFile, options.skipErrors, dateColFormats=dateColFormats, escapeStrings=options.escapeStrings, estInput=estInput );
        log.info("%d rows successfully inserted",nInserts)
    elif options.update is not None and options.table is not None:
        sourceFile  = stdOpen(options.update,"r",sys.stdin);
        nIdCols = int(options.nIdCols);
        nUpdates = updateFromFile( sourceFile, options.table, args, nIdCols, options.delim, options.skipErrors );
        log.info("%d row updates completed",nUpdates);
    elif len(args) > 0:
        outFile = "-"   # Default to stdout if no outputFile specified
        if len(args) > 1: outFile = args[1]
        outFile = stdOpen( outFile, "w", sys.stdout )
        
        if options.incCommand:
            summaryData = {"argv": argv};
            print >> outFile, COMMENT_TAG, json.dumps(summaryData);

        textFormatter = TextResultsFormatter(outFile, options.delim)

        results = execute( args[0], formatter=textFormatter, includeColumnNames=options.incCols )

        log.info("%d rows affected (or other return code)",results);
    else:
        parser.print_help()
        sys.exit(-1)

    timer = time.time() - timer;
    log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    main(sys.argv)
