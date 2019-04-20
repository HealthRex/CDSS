#!/usr/bin/env python
import sys, os;
import cgi
import cgitb; cgitb.enable();
from cStringIO import StringIO;

from datetime import datetime, timedelta;

from medinfo.common.Util import isTrueStr;

from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, modelListFromTable;
from medinfo.db.ResultsFormatter import HtmlResultsFormatter;

from medinfo.cpoe.cpoeSim.Const import BASE_TIME, TIME_FORMAT;
from medinfo.cpoe.cpoeSim.SimManager import SimManager;

from medinfo.web.cgibin.cpoe.dynamicdata.BaseDynamicData import BaseDynamicData;
from medinfo.web.cgibin.cpoe.dynamicdata.RelatedOrders import RELATED_LINK_TEMPLATE;
from medinfo.web.cgibin import Options;

CATEGORY_HEADER_TEMPLATE = \
    """
    <tr>
        <td colspan=100 align=center><b>%(category_description)s</b></td>
    </tr>
    """
LINE_TEMPLATE_BY_ACTIVE = \
    {   True: """
            <tr>
                <td valign=top align=center><b>%(category_description.format)s</b></td>
                <td valign=top>%(description)s</td>
                <td valign=top align=center><input type=button value="X" onClick="discontinueOrder('%(sim_patient_order_id)s|%(clinical_item_id)s|%(name)s|%(description)s')"></td>
            </tr>
            """,
        False: """
            <tr>
                <td valign=top align=center><b>%(category_description.format)s</b></td>
                <td valign=top>%(description)s</td>
                <td valign=top align=center nowrap>%(start_time.format)s<br>%(end_time.format)s</td>
                <td valign=top align=center nowrap>
                    <a href="javascript:loadRelatedOrders('%(clinical_item_id)s')"><img src="../../resource/graphIcon.png" width=12 height=12 alt="Find Related Orders"></a>
                    <a href="javascript:discontinueOrder('%(sim_patient_order_id)s|%(clinical_item_id)s|%(name)s|%(description)s')"><img src="../../resource/cancelIcon.svg" width=12 height=12 alt="Cancel/Discontinue Order"></a>
                </td>
            </tr>
            """,
    };

class ActiveOrders(BaseDynamicData):
    """Simple script to (dynamically) relay query and result data
    from the ItemRecommendation module in URL request then HTML table format.
    """
    def __init__(self):
        BaseDynamicData.__init__(self);
        
        self.requestData["sim_patient_id"] = "";
        self.requestData["sim_time"] = "";
        self.requestData["loadActive"] = "false";    # Default to showing whole order history instead of just active (not inactive / completed) orders
        
        self.requestData["activeCompleted"] = "Active";
        self.requestData["activeOrderButtonClass"] = "buttonSelected";
        self.requestData["completedOrderButtonClass"] = "";
        self.requestData["historyTime"] = "";
        self.requestData["detailTable"] = "";
        
        self.addHandler("sim_patient_id", ActiveOrders.action_default.__name__);
        
    def action_default(self):
        """Present currently selected set of pending clinical item orders"""
        patientId = int(self.requestData["sim_patient_id"]);
        simTime = int(self.requestData["sim_time"]);
        loadActive = isTrueStr(self.requestData["loadActive"]);
        if not loadActive:
            self.requestData["activeCompleted"] = "Completed";
            self.requestData["activeOrderButtonClass"] = "";
            self.requestData["completedOrderButtonClass"] = "buttonSelected";
            self.requestData["historyTime"] = "Time";

        manager = SimManager();
        patientOrders = manager.loadPatientOrders(patientId, simTime, loadActive=loadActive);
        
        lastPatientOrder = None;
        htmlLines = list();
        for patientOrder in patientOrders:
            self.formatPatientOrder(patientOrder, lastPatientOrder);
            htmlLines.append( LINE_TEMPLATE_BY_ACTIVE[loadActive] % patientOrder );
            lastPatientOrder = patientOrder;
        self.requestData["detailTable"] = str.join("\n", htmlLines );

    def formatPatientOrder(self, patientOrder, lastPatientOrder):
        """Populate patient order model with some formatted fields
        """
        startTime = BASE_TIME + timedelta(0, patientOrder["relative_time_start"]);
        patientOrder["start_time.format"] =  startTime.strftime(TIME_FORMAT);
        patientOrder["end_time.format"] = "";
        if patientOrder["relative_time_end"] is not None:
            endTime = BASE_TIME + timedelta(0, patientOrder["relative_time_end"]);
            patientOrder["end_time.format"] = "<i>(%s)</i>" % endTime.strftime(TIME_FORMAT);

        if lastPatientOrder is None or patientOrder["category_description"] != lastPatientOrder["category_description"]:
            patientOrder["category_description.format"] = patientOrder["category_description"];   # Only show category for first item for more of a less redundant tree layout
        else:
            patientOrder["category_description.format"] = "";   # Blank for subsequent lines

# CGI Boilerplate to initiate script
if __name__ == "__main__":
    webController =  ActiveOrders()
    webController.handleRequest(cgi.FieldStorage())

# WSGI Boilerplate to initiate script
if __name__.startswith("_mod_wsgi_"):
    webController = ActiveOrders()
    webController.setFilePath(__file__)
    application = webController.wsgiHandler 