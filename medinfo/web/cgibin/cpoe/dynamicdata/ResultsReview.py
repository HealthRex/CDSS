#!/usr/bin/env python
import sys, os;
import cgi
import cgitb; cgitb.enable();
from io import StringIO;

from datetime import datetime, timedelta;

from medinfo.common.Const import FALSE_STRINGS;

from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, modelListFromTable;
from medinfo.db.ResultsFormatter import HtmlResultsFormatter;

from medinfo.cpoe.cpoeSim.SimManager import SimManager;
from medinfo.cpoe.cpoeSim.Const import BASE_TIME, TIME_FORMAT;

from medinfo.web.cgibin.cpoe.dynamicdata.BaseDynamicData import BaseDynamicData;
from medinfo.web.cgibin import Options;

GROUP_HEADER_TEMPLATE = \
    """
    <tr>
        <td colspan=100 align=center><b>%(spacer)s%(groupString)s</b></td>
    </tr>
    """
LINE_TEMPLATE = \
    """
    <tr>
        <td align=center>%(result_time.format)s
        <td align=center>%(name)s</td>
        <td align=right>%(num_value)s</td>
        <td align=left><i>%(result_flag)s</i> %(text_value)s</td>
        <td align=left>%(description)s</td>
    </tr>
    """;

PENDING_ORDER_LINE_TEMPLATE = \
    """
    <tr>
        <td align=center>%(order_time.format)s
        <td align=center>%(name)s</td>
        <td align=left>%(description)s</td>
        <td align=right>%(time_until_result.format)s</td>
    </tr>
    """;
EMPTY_RESULTS_LINE = \
    """
    <tr>
        <td align=center colspan=100>No results pending</td>
    </tr>
    """;


class ResultsReview(BaseDynamicData):
    """Simple script to (dynamically) relay query and result data
    """
    def __init__(self):
        BaseDynamicData.__init__(self);
        
        self.requestData["sim_patient_id"] = "";
        self.requestData["sim_time"] = "";
        
        self.requestData["detailTable"] = "";
        self.requestData["pendingResultOrdersTable"] = EMPTY_RESULTS_LINE;
        
        self.addHandler("sim_patient_id", ResultsReview.action_default.__name__);
        
    def action_default(self):
        """Present currently unlocked set of results"""
        patientId = int(self.requestData["sim_patient_id"]);
        simTime = int(self.requestData["sim_time"]);
        
        manager = SimManager();

        # Load and format the results available so far
        results = manager.loadResults(patientId, simTime);
        lastGroupStrings = ['New']; # Sentinel value that will be different than first real data row
        lenLastGroupStrings = len(lastGroupStrings);
        htmlLines = list();
        for dataModel in results:
            self.formatDataModel(dataModel);
            for i, groupString in enumerate(dataModel["groupStrings"]):
                if i >= lenLastGroupStrings or groupString != lastGroupStrings[i]:
                    htmlLines.append( GROUP_HEADER_TEMPLATE % {"spacer": " &nbsp; "*i, "groupString": groupString });
            htmlLines.append( LINE_TEMPLATE % dataModel );
            lastGroupStrings = dataModel["groupStrings"];
            lenLastGroupStrings = len(lastGroupStrings);
        self.requestData["detailTable"] = str.join("\n", htmlLines );

        # Load and format information on any pending result orders
        pendingResultOrders = manager.loadPendingResultOrders(patientId, simTime);
        htmlLines = list();
        for dataModel in pendingResultOrders:
            self.formatPendingResultOrderModel(dataModel);
            htmlLines.append( PENDING_ORDER_LINE_TEMPLATE % dataModel );
        self.requestData["pendingResultOrdersTable"] = str.join("\n", htmlLines );
        if len(pendingResultOrders) < 1: # Leave default "no results pending" message if don't find any
            self.requestData["pendingResultOrdersTable"] = EMPTY_RESULTS_LINE;

    def formatDataModel(self, dataModel):
        """Populate dataModel with formatted items"""
        dataModel["groupStrings"] = dataModel["group_string"].split(">");
        dataModel["lastGroup"] = dataModel["groupStrings"][-1];
        if dataModel["num_value"] is not None and dataModel["num_value"].is_integer():
            dataModel["num_value"] = int(dataModel["num_value"]);
        for key in ("num_value","text_value","result_flag"):
            if dataModel[key] is None:
                dataModel[key] = "";
        dataModel["result_time.format"] = (BASE_TIME + timedelta(0,dataModel["result_relative_time"])).strftime(TIME_FORMAT);

    def formatPendingResultOrderModel(self, dataModel):
        """Populate dataModel with formatted items"""
        dataModel["order_time.format"] = (BASE_TIME + timedelta(0,dataModel["relative_time_start"])).strftime(TIME_FORMAT);
        dataModel["time_until_result.format"] = dataModel["time_until_result"] / 60;    # Convert time in seconds into minutes

        
# CGI Boilerplate to initiate script
if __name__ == "__main__":
    webController =  ResultsReview()
    webController.handleRequest(cgi.FieldStorage())

# WSGI Boilerplate to initiate script
if __name__.startswith("_mod_wsgi_"):
    webController = ResultsReview()
    webController.setFilePath(__file__)
    application = webController.wsgiHandler 