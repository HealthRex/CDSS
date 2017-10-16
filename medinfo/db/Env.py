"""Various constants for use by the application modules,
but these can / should be changed depending on the
platform / environment where they are installed.
"""

import sys, os;
import logging

"""Default level for application logging.  Modify these for different scenarios.
See Python logging package documentation for more information"""
LOGGER_LEVEL = logging.DEBUG
LOGGER_LEVEL = logging.INFO
#LOGGER_LEVEL = logging.WARNING
#LOGGER_LEVEL = logging.ERROR
#LOGGER_LEVEL = logging.CRITICAL

"""Parameter placeholder for SQL queries.  Depends on the DB-API module
used.  Can tell which by the module's paramstyle attribute.
Read the DB-API 2.0 specs for more info. (http://www.python.org/peps/pep-0249.html)
Oracle expects sequential or named items like &1, &2, or :1, :2...
"""
#SQL_PLACEHOLDER = "?"   # "qmark"
SQL_PLACEHOLDER = "%s"  # "format" and "pyFormat"

"""Strings to use for boolean parameters."""
BOOLEAN_STR = dict();
# pyPgSQL
BOOLEAN_STR[True] = str(True);
BOOLEAN_STR[False]= str(False);
# MS Access
#BOOLEAN_STR[True] = str(-1);
#BOOLEAN_STR[False]= str(0);

"""Designate the DB being used, which will afect some DB specific setup steps"""
#DATABASE_CONNECTOR_NAME = "mysql.connector";
#DATABASE_CONNECTOR_NAME = "MySQLdb";
DATABASE_CONNECTOR_NAME = "psycopg2";
#DATABASE_CONNECTOR_NAME = "cx_Oracle";
#DATABASE_CONNECTOR_NAME = "sqlite3";


"""Parameters needed to open a connection to the database.
Dependent upon particular connection interface and database implementation
"""
DB_PARAM = {}
#DB_PARAM["HOST"] = "medinfo-5year-time-assoc2010-2013.cxkturzva06i.us-east-1.rds.amazonaws.com"
#DB_PARAM["HOST"] = "inpatient5year.cxkturzva06i.us-east-1.rds.amazonaws.com"
DB_PARAM["HOST"] = "localhost"
#DB_PARAM["DSN"]  = "medicare"
DB_PARAM["DSN"]  = "medinfo-5year-time"
#DB_PARAM["DSN"]  = "resident-access-log-2017"
#DB_PARAM["DSN"] = "/Users/angelicaperez/Documents/JonChen/sqlite_db/dave_chan2.sqlite"
#DB_PARAM["DSN"]  = "medinfo5yr"
DB_PARAM["UID"]  = "sbala"
DB_PARAM["PWD"]  = "1234"


# Opioid Notes DB
#DB_PARAM["HOST"] = "cci-db-p03";
#DB_PARAM["DSN"] = "stride";
#DB_PARAM["UID"] = "jonc101[opioid]";
#DB_PARAM["PWD"] = "xxx";


"""Parameters needed to open a connection to the database.
Dependent upon particular connection interface and database implementation
"""
TEST_DB_PARAM = {}
#TEST_DB_PARAM["HOST"] = "inpatient5year.cxkturzva06i.us-east-1.rds.amazonaws.com"
TEST_DB_PARAM["HOST"] = "localhost"
TEST_DB_PARAM["DSN"]  = "testdb"
TEST_DB_PARAM["UID"]  = "sbala"
TEST_DB_PARAM["PWD"]  = "1234"

#TEST_DB_PARAM["DSN"] = "c:\Box Sync\NoSync\VAAlerts\dave_chan2.sqlite";
#TEST_DB_PARAM["DSN"] = "/Users/angelicaperez/Documents/JonChen/sqlite_db/dave_chan2.sqlite"


"""Parameters on whether to do additional pre-processing when parsing text / CSV files"""
CSV_EXPAND_QUOTES = True;

def formatDBConnectString( dbParamDict ):
    connStr = ""
    for key, value in dbParamDict.iteritems():
        connStr += "%s=%s;" % (key,value);
    return connStr;
