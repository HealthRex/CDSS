#!/usr/bin/env python
"""
Simple Python CGI script to test web interface to molecule file processing modules
"""

import cgi
import cgitb; cgitb.enable()

from cStringIO import StringIO;
import time


from medinfo.db import DBUtil
from medinfo.db.Env import DB_PARAM
from medinfo.db.ResultsFormatter import TextResultsFormatter, HtmlResultsFormatter
from medinfo.web.cgibin.admin.BaseAdminWeb import BaseAdminWeb

# Parameter key to pass if don't want the HTML interface, 
#   just want direct data output like a web service
OUTPUT_ONLY = "outputOnly";

class DBUtilWeb(BaseAdminWeb):
    def __init__(self):
        BaseAdminWeb.__init__(self)

        self.addHandler(self.requestData["WEB_CLASS"], DBUtilWeb.action_default.__name__)
        self.addHandler(OUTPUT_ONLY, DBUtilWeb.action_outputOnly.__name__)
        self.addHandler("insert", DBUtilWeb.action_input.__name__)
        self.addHandler("update", DBUtilWeb.action_update.__name__)

    def initializeRequestData(self):
        # Default values to place in template htm file
        self.requestData["input"]         = "select * \nfrom pg_tables\nwhere schemaname = 'public'"
        self.requestData["incCols"]       = "checked"
        self.requestData["outputOnly"]    = ""
        self.requestData["table"]         = ""
        self.requestData["columnNames"]   = ""
        self.requestData["delim"]         = ""
        self.requestData["resultsHtml"]   = ""
        self.requestData["resultsText"]   = ""
        self.requestData["resultsInfo"]   = ""
        self.requestData["dbHOST"]        = DB_PARAM["HOST"]
        self.requestData["dbPORT"]        = ""; # Just use blank for default
        if "PORT" in DB_PARAM:
            self.requestData["dbPORT"]    = DB_PARAM["PORT"]
        self.requestData["dbDSN"]         = DB_PARAM["DSN"]
        self.requestData["dbUID"]         = DB_PARAM["UID"]
        self.requestData["dbPWD"]         = ""    # Don't supply password, user must know it

        self.outputOnly = False

    def action_default(self):
        # Read checkboxes by presence or absence of field
        self.requestData["incCols"] = ""  # Checkboxes not passed if unchecked, so extra step to ensure uncheck is persisted
        incCols = False
        if self.mForm.has_key("incCols"):
            self.requestData["incCols"] = self.mForm["incCols"].value
            incCols = True
        
        # Point to the specified database
        connFactory = self.connectionFactory()
        
        timer = time.time()
        # Just execute a normal query, possibly with a result set
        results = DBUtil.execute( self.mForm["input"].value, includeColumnNames=incCols, connFactory=connFactory )
        if type(results) == list:   # Result set, format as table
            formatter = TextResultsFormatter(StringIO())
            formatter.formatResultSet(results)
            self.requestData["resultsText"] = formatter.getOutFile().getvalue()

            headerRowFormat = None;
            if incCols: headerRowFormat = "th";

            formatter = HtmlResultsFormatter(StringIO(),headerRowFormat);
            formatter.formatResultSet(results)
            self.requestData["resultsHtml"] = formatter.getOutFile().getvalue()

            self.requestData["resultsInfo"] = "(%d rows) " % len(results)
        else:
            self.requestData["resultsText"] = "%d rows affected (or other return code)" % results
        timer = time.time() - timer
        self.requestData["resultsInfo"] += "(%1.3f seconds)" % timer

    def action_input(self):
        # Point to the specified database
        connFactory = self.connectionFactory()

        inputFile   = StringIO(self.mForm["input"].value);
        table       = self.requestData["table"];
        columnNames = None; # If None specified, will default to using first data row
        if self.requestData["columnNames"].strip() != "": columnNames = self.requestData["columnNames"].split();
        delim = None;
        if self.requestData["delim"] != "":   delim = self.requestData["delim"];
        # Correct escape character delimiter
        if delim == '\\t':  delim = '\t'

        nInserts = \
            DBUtil.insertFile \
            (   inputFile, 
                table, 
                columnNames, 
                delim,
                connFactory=connFactory
            )
        
        self.requestData["resultsText"]  = "%d rows inserted\n" % nInserts

    def action_update(self):
        # Point to the specified database
        connFactory = self.connectionFactory()

        sourceFile  = StringIO(self.mForm["input"].value);
        tableName   = self.requestData["table"];
        
        columnNames = None; # If None specified, will default to using first data row
        if self.requestData["columnNames"].strip() != "": 
            columnNames = self.requestData["columnNames"].split();
        
        nIdCols = 1;    # Assume always must be 1 for now
        
        delim = None;
        if self.requestData["delim"] != "":   
            delim = self.requestData["delim"];
        # Correct escape character delimiter
        if delim == '\\t':  
            delim = '\t'

        nUpdates = \
            DBUtil.updateFromFile \
            (   sourceFile, 
                tableName, 
                columnNames, 
                nIdCols,
                delim,
                connFactory=connFactory
            );

        self.requestData["resultsText"]  = "%d rows updated\n" % nUpdates

    def connectionFactory(self):
        """Prepare a connection factory to the database specified
        by the current request parameters.
        """
        
        connParams = dict();
        
        for key, value in self.requestData.iteritems():
            if key.startswith("db"):    # Look for db parameters
                tagKey = key[len("db"):];
                if len(value) > 0: 
                    connParams[tagKey] = value;
                else:
                    connParams[tagKey] = None

        return DBUtil.ConnectionFactory(connParams);

    def action_outputOnly(self):
        self.outputOnly = True

    def response(self):
        if self.outputOnly:
            # Don't do normal HTML template output, output data directly
            print "Content-type: text/plain"
            print
            print self.requestData["resultsText"]
        else:
            # Defer to superclass implementation
            BaseAdminWeb.response(self)
            
# CGI Boilerplate to initiate script
if __name__ == "__main__":
    webController =  DBUtilWeb()
    webController.handleRequest(cgi.FieldStorage())

# WSGI Boilerplate to initiate script
webController = DBUtilWeb()
webController.setFilePath(__file__)
application = webController.wsgiHandler 
