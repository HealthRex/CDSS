#!/usr/bin/env python
import sys, os;
import cgi
import cgitb; cgitb.enable();
from cStringIO import StringIO;

from medinfo.common.Const import FALSE_STRINGS;

from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, modelListFromTable;
from medinfo.db.ResultsFormatter import HtmlResultsFormatter;

from medinfo.cpoe.SimManager import SimManager;

from medinfo.web.cgibin.cpoe.dynamicdata.BaseDynamicData import BaseDynamicData;
from medinfo.web.cgibin import Options;

class NewOrders(BaseDynamicData):
    """Simple script to (dynamically) relay query and result data
    from the ItemRecommendation module in URL request then HTML table format.
    """
    def __init__(self):
        BaseDynamicData.__init__(self);
        
        self.requestData["sim_user_id"] = "";
        self.requestData["sim_patient_id"] = "";
        self.requestData["sim_time"] = "";
        self.requestData["newOrderItemId"] = list();
        self.requestData["discontinuePatientOrderId"] = list();
        
        self.addHandler("clinicalItemIds", NewOrders.action_default.__name__);
        self.addHandler("signOrders", NewOrders.action_signOrders.__name__);
        
    def action_default(self):
        """Present currently selected set of pending clinical item orders"""

    def action_signOrders(self):
        """Commit the pended orders into active orders in the database record."""
        userId = int(self.requestData["sim_user_id"]);
        patientId = int(self.requestData["sim_patient_id"]);
        simTime = int(self.requestData["sim_time"]);
        
        if isinstance(self.requestData["newOrderItemId"], str):
            # Single item, represent as list of size 1
            self.requestData["newOrderItemId"] = [self.requestData["newOrderItemId"]];
        # Convert to list of integers
        orderItemIds = [int(itemIdStr) for itemIdStr in self.requestData["newOrderItemId"]];

        if isinstance(self.requestData["discontinuePatientOrderId"], str):
            # Single item, represent as list of size 1
            self.requestData["discontinuePatientOrderId"] = [self.requestData["discontinuePatientOrderId"]];
        # Convert to list of integers
        discontinuePatientOrderIds = [int(itemIdStr) for itemIdStr in self.requestData["discontinuePatientOrderId"]];
        
        manager = SimManager();
        manager.signOrders(userId, patientId, simTime, orderItemIds, discontinuePatientOrderIds);

        
# CGI Boilerplate to initiate script
if __name__ == "__main__":
    webController =  NewOrders()
    webController.handleRequest(cgi.FieldStorage())

# WSGI Boilerplate to initiate script
if __name__.startswith("_mod_wsgi_"):
    webController = NewOrders()
    webController.setFilePath(__file__)
    application = webController.wsgiHandler 