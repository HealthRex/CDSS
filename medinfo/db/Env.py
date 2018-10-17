"""Various constants for use by the application modules,
but these can / should be changed depending on the
platform / environment where they are installed.
"""

import sys, os;
import logging
import LocalEnv;

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
# #SQL_PLACEHOLDER = "?"   # "qmark"
# SQL_PLACEHOLDER = "%s"  # "format" and "pyFormat"
SQL_PLACEHOLDER = LocalEnv.SQL_PLACEHOLDER

"""Strings to use for boolean parameters."""
BOOLEAN_STR = dict();
# pyPgSQL
BOOLEAN_STR[True] = str(True);
BOOLEAN_STR[False]= str(False);
# MS Access
#BOOLEAN_STR[True] = str(-1);
#BOOLEAN_STR[False]= str(0);

# """Designate the DB being used, which will afect some DB specific setup steps"""
# #DATABASE_CONNECTOR_NAME = "mysql.connector";
# #DATABASE_CONNECTOR_NAME = "MySQLdb";
# DATABASE_CONNECTOR_NAME = "psycopg2";
# #DATABASE_CONNECTOR_NAME = "cx_Oracle";
# #DATABASE_CONNECTOR_NAME = "sqlite3";
DATABASE_CONNECTOR_NAME = LocalEnv.DATABASE_CONNECTOR_NAME

"""Parameters needed to open a connection to the database.
Dependent upon particular connection interface and database implementation

Note that Env.py reads database, user, and password specifications from LocalEnv.py
"""
DB_PARAM = {}
DB_PARAM = LocalEnv.LOCAL_PROD_DB_PARAM

# Opioid Notes DB
#DB_PARAM["HOST"] = "cci-db-p03";
#DB_PARAM["DSN"] = "stride";
#DB_PARAM["UID"] = "jonc101[opioid]";
#DB_PARAM["PWD"] = "xxx";


"""Parameters needed to open a connection to the database.
Dependent upon particular connection interface and database implementation
"""
TEST_DB_PARAM = {}
TEST_DB_PARAM = LocalEnv.LOCAL_TEST_DB_PARAM

#TEST_DB_PARAM["DSN"] = "c:\Box Sync\NoSync\VAAlerts\dave_chan2.sqlite";
#TEST_DB_PARAM["DSN"] = "/Users/angelicaperez/Documents/JonChen/sqlite_db/dave_chan2.sqlite"


"""Parameters on whether to do additional pre-processing when parsing text / CSV files.
Seems necessary for STRIDE 2008-2014-2017 Order Proc dumps?
"""
CSV_EXPAND_QUOTES = True;

def formatDBConnectString( dbParamDict ):
    connStr = ""
    for key, value in dbParamDict.iteritems():
        connStr += "%s=%s;" % (key,value);
    return connStr;
