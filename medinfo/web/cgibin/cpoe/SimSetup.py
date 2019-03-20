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
from medinfo.cpoe.cpoeSim.Const import BASE_TIME, TIME_FORMAT;
from medinfo.cpoe.cpoeSim.SimManager import SimManager;

from medinfo.web.cgibin.cpoe.BaseCPOEWeb import BaseCPOEWeb

from medinfo.web.cgibin import Options;

class SimSetup(BaseCPOEWeb):
    def __init__(self):
        BaseCPOEWeb.__init__(self)
        self.requestData["userOptions"] = "";
        self.requestData["patientOptions"] = "";
        self.requestData["stateOptions"] = "";

        self.addHandler("createUser", SimSetup.action_createUser.__name__);
        self.addHandler("createPatient", SimSetup.action_createPatient.__name__);
        self.addHandler("copyPatientTemplate", SimSetup.action_copyPatientTemplate.__name__);

    def action_final(self): # Do as last step, so will capture any just completed creation steps
        """Load lists of users, patients, and states to select from"""
        manager = SimManager();
        
        userModels = manager.loadUserInfo();
        valueList = list();
        textList = list();
        for userModel in userModels:
            valueList.append(str(userModel["sim_user_id"]));
            textList.append(userModel["name"]);
        self.requestData["userOptions"] = self.optionTagsFromList(valueList, textList);

        patientModels = manager.loadPatientInfo();
        valueList = list();
        textList = list();
        for patientModel in patientModels:
            valueList.append(str(patientModel["sim_patient_id"]));
            textList.append("%(name)s" % patientModel);
        self.requestData["patientOptions"] = self.optionTagsFromList(valueList, textList);
        
        stateModels = manager.loadStateInfo();
        valueList = list();
        textList = list();
        for stateModel in stateModels:
            valueList.append(str(stateModel["sim_state_id"]));
            textList.append("%(name)s" % stateModel);
        self.requestData["stateOptions"] = self.optionTagsFromList(valueList, textList);

    def action_createUser(self):
        manager = SimManager();
        userData = {"name": self.requestData["sim_user_name"] };
        manager.createUser(userData);
    
    def action_createPatient(self):
        manager = SimManager();
        patientData = \
            {   "age_years": int(self.requestData["sim_patient_age_years"]),
                "gender": self.requestData["sim_patient_gender"],
                "name": self.requestData["sim_patient_name"],
            };
        initialStateId = int(self.requestData["sim_state_id"]);
        manager.createPatient( patientData, initialStateId );

    def action_copyPatientTemplate(self):
        manager = SimManager();
        patientData = \
            {   "name": self.requestData["sim_patient_name"],
            };
        templatePatientId = int(self.requestData["sim_patient_id"]);
        manager.copyPatientTemplate( patientData, templatePatientId );

if __name__ == "__main__":
    webController =  SimSetup()
    webController.handleRequest(cgi.FieldStorage())

# WSGI Boilerplate to initiate script
if __name__.startswith("_mod_wsgi_"):
    webController = SimSetup()
    webController.setFilePath(__file__)
    application = webController.wsgiHandler 