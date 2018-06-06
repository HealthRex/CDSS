#!/usr/bin/env python
"""
Simple Python CGI script to test web interface to molecule file processing modules
"""

import sys;
import cgi
import cgitb; cgitb.enable()

from cStringIO import StringIO;
import time
from datetime import datetime, timedelta;

from medinfo.db import DBUtil
from medinfo.db.ResultsFormatter import HtmlResultsFormatter
from medinfo.cpoe.Const import BASE_TIME, TIME_FORMAT;
from medinfo.cpoe.SimManager import SimManager;

from medinfo.web.cgibin.cpoe.BaseCPOEWeb import BaseCPOEWeb

from medinfo.web.cgibin import Options;
from medinfo.web.cgibin.cpoe.dynamicdata.ActiveOrders import ActiveOrders;
from medinfo.web.cgibin.cpoe.dynamicdata.NotesReview import NotesReview;
from medinfo.web.cgibin.cpoe.dynamicdata.ResultsReview import ResultsReview;
from medinfo.web.cgibin.cpoe.dynamicdata.NewOrders import NewOrders;
from medinfo.web.cgibin.cpoe.dynamicdata.RelatedOrders import RelatedOrders;

class PatientCareFrame(BaseCPOEWeb):
    def __init__(self):
        BaseCPOEWeb.__init__(self)
        # Initialize default values to place in template htm file
        self.requestData["sim_user_id"] = "";
        self.requestData["sim_patient_id"] = "";
        self.requestData["sim_state_id"] = "";
        self.requestData["sim_time"] = "0";

        self.requestData["currentDataPage"] = NotesReview.__name__;
        self.requestData["autoQuery"] = "";
        self.requestData["maxResults"] = "50";  # Maximum of results to show when searching for orders

        self.requestData["newOrderItemId"] = list();
        self.requestData["discontinuePatientOrderId"] = list();

        # Sub-Table / Dynamically loaded data
        self.requestData["currentDataTable"] = "";
        self.requestData["dataEntryTable"] = "";
        self.requestData["searchResultsTable"] = "";

        # Map strings to sub-page class lookups. Could use importlib and getattr to do dynamic reflection
        #   but this makes it more explicit what is happening.
        self.pageClassByName = dict();
        for subPageClass in [NotesReview,ResultsReview,ActiveOrders]:
            self.pageClassByName[subPageClass.__name__] = subPageClass;

        self.addHandler("signOrders", PatientCareFrame.action_signOrders.__name__);
        self.addHandler("sim_patient_id", PatientCareFrame.action_default.__name__);

    def action_signOrders(self):
        """Call sub-page action to update information before proceeding to default render"""
        subData = NewOrders();
        subData.requestData["sim_user_id"] = self.requestData["sim_user_id"];
        subData.requestData["sim_patient_id"] = self.requestData["sim_patient_id"];
        subData.requestData["sim_time"] = self.requestData["sim_time"];
        subData.requestData["newOrderItemId"] = self.requestData["newOrderItemId"];
        subData.requestData["discontinuePatientOrderId"] = self.requestData["discontinuePatientOrderId"];
        subData.action_signOrders();

        # Advance the simulated time after orders signed.
        # Otherwise bizarre patterns where simulation states can undergo multiple changes within zero time.
        # Advance one minute (60) seconds per item ordered
        simTime = int(self.requestData["sim_time"]);
        deltaSeconds = len(subData.requestData["newOrderItemId"]) * 60;
        self.requestData["sim_time"] = simTime + deltaSeconds;

    def action_default(self):
        """Render the details for the specified patient information, including controls to modify"""
        userId = int(self.requestData["sim_user_id"]);
        patientId = int(self.requestData["sim_patient_id"]);
        simTime = int(self.requestData["sim_time"]);

        manager = SimManager();
        userModel = manager.loadUserInfo([userId])[0];  # Assume found good single match
        patientModel = manager.loadPatientInfo([patientId], simTime)[0];
        #print >> sys.stderr, "Loaded %(sim_patient_id)s in state %(sim_state_id)s at %(relative_time_start)s" % patientModel

        for key, value in userModel.iteritems():
            self.requestData["sim_user."+key] = value;
        for key, value in patientModel.iteritems():
            self.requestData["sim_patient."+key] = value;
        self.requestData["sim_time.format"] = (BASE_TIME + timedelta(0,simTime)).strftime(TIME_FORMAT);

        subData = self.pageClassByName[self.requestData["currentDataPage"]]();
        subData.requestData["sim_user_id"] = self.requestData["sim_user_id"];
        subData.requestData["sim_patient_id"] = self.requestData["sim_patient_id"];
        subData.requestData["sim_time"] = self.requestData["sim_time"];
        subData.action_default();
        self.requestData["currentDataTable"] = subData.populatedTemplate();

        subData = NewOrders();
        subData.action_default();
        self.requestData["dataEntryTable"] = subData.populatedTemplate();

        #subData = RelatedOrders();
        #subData.action_default();
        #self.requestData["searchResultsTable"] = subData.populatedTemplate();
        #self.requestData["searchResultsTable"] = '<br><br><img src="../../resource/ajax-loader.gif">';  # Defer to AJAX dynamic loading to avoid holding up page load

if __name__ == "__main__":
    webController =  PatientCareFrame()
    webController.handleRequest(cgi.FieldStorage())

# WSGI Boilerplate to initiate script
if __name__.startswith("_mod_wsgi_"):
    webController = PatientCareFrame()
    webController.setFilePath(__file__)
    application = webController.wsgiHandler
