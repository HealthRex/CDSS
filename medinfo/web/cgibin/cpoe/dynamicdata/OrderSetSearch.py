#!/usr/bin/env python
import sys, os;
import cgi
import cgitb; cgitb.enable();
import json;
import urllib;
from cStringIO import StringIO;

from medinfo.common.Const import FALSE_STRINGS;

from medinfo.cpoe.ItemRecommender import RecommenderQuery;
from medinfo.cpoe.ItemRecommender import ItemAssociationRecommender;
from medinfo.cpoe.Const import BASELINE_FIELDS, CORE_FIELDS;

from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, modelListFromTable;
from medinfo.db.ResultsFormatter import HtmlResultsFormatter;

from medinfo.common.StatsUtil import ContingencyStats;

from medinfo.cpoe.cpoeSim.SimManager import SimManager, ClinicalItemQuery;

from medinfo.web.cgibin.cpoe.dynamicdata.BaseDynamicData import BaseDynamicData;
from medinfo.web.cgibin import Options;

CONTROLS_TEMPLATE = \
    """
    <input type=checkbox onClick="selectOrderSet(this, window.itemLists);" value="%(external_id)s">
    <input type=hidden name="itemListJSON.%(external_id)s" value="%(itemListJSON.quote)s">
    """;
NAME_TEMPLATE = \
    """%(name)s<br>
    <div id="itemSpace.%(external_id)s">
    </div>
    """

class OrderSetSearch(BaseDynamicData):
    """Simple script to (dynamically) relay query and result data
    from the ItemRecommendation module in URL request then HTML table format.
    """
    def __init__(self):
        BaseDynamicData.__init__(self);
        
        self.requestData["searchStr"] = "";
        self.requestData["analysisStatus"] = "1";
        
        self.requestData["dataRows"] = '<tr><td colspan=100 align=center height=200><img src="../../resource/ajax-loader.gif"></td></tr>';
        
        self.addHandler("searchStr", OrderSetSearch.action_orderSetSearch.__name__);

    def action_orderSetSearch(self):
        """Look for pre-defined order sets"""
        manager = SimManager();
        query = ClinicalItemQuery();
        query.parseParams(self.requestData);
        resultIter = manager.orderSetSearch(query);

        # Prepare data for HMTL formatting
        results = list();
        for dataModel in resultIter:
            if dataModel is not None:
                dataModel["nameFormat"] = NAME_TEMPLATE % dataModel;
                dataModel["itemListJSON.quote"] = urllib.quote(json.dumps(dataModel["itemList"]));
                dataModel["controls"] = CONTROLS_TEMPLATE % dataModel;
                results.append(dataModel);

        colNames = ["controls","external_id","nameFormat"];
        formatter = HtmlResultsFormatter( StringIO(), valign="top");
        formatter.formatResultDicts( results, colNames );

        self.requestData["dataRows"] = formatter.getOutFile().getvalue();

    def prepareDisplayHeaders(self, displayFields):
        showCounts = (self.requestData["showCounts"].lower() not in FALSE_STRINGS);

        fieldHeadersHTML  = '<th nowrap>' + str.join('</th><th nowrap>', displayFields) + '</th>';
        if showCounts:
            fieldHeadersHTML += '<th>' + str.join('</th><th>', CORE_FIELDS) + '</th>';

        displayFieldsFormatSuffixed = list();
        for field in displayFields:
            displayFieldsFormatSuffixed.append('%sFormat' % field);
        if showCounts:
            for field in CORE_FIELDS:
                displayFieldsFormatSuffixed.append('%sFormat' % field);
    
        return (fieldHeadersHTML, displayFieldsFormatSuffixed);
    
    def prepareResultRow(self, dataModel, displayFields):
        dataModel["controls"] = CONTROLS_TEMPLATE % dataModel;
        dataModel["name"] = dataModel["name"].replace(",","-");

        if "nB" in dataModel:
            if "nAB" not in dataModel:
                # Baseline query without query items, use matching numbers to ensure calculations will have something to process
                dataModel["nAB"] = dataModel["nB"];
                dataModel["nA"] = dataModel["N"];
            nAB = dataModel["nAB"];
            nA = dataModel["nA"];
            nB = dataModel["nB"];
            N = dataModel["N"];
            contStats = ContingencyStats( nAB, nA, nB, N );
            contStats.normalize(truncateNegativeValues=False);
        
        for field in displayFields:
            if field not in dataModel:
                # Unavailable field, see if it is a derived field that can be calculated
                dataModel[field] = contStats[field];
        
            if field in CORE_FIELDS:
                pass;
            elif abs(dataModel[field]) < 0.01:
                # Allow formatting for very small values
                dataModel["%sFormat" % field] = "%.1e" % dataModel[field];
            else:
                # Default just format as floating point values
                dataModel["%sFormat" % field] = "%.2f" % dataModel[field];
        
        for field in CORE_FIELDS:            
            # Count fields express as integers, assuming available at all
            if field in BASELINE_FIELDS:
                dataModel["%sFormat" % field] = "%d" % dataModel[field];
            else:
                # May have small virtual counts from derived scenarios
                if dataModel[field] > 10:
                    dataModel["%sFormat" % field] = "%.1f" % dataModel[field];
                else:
                    dataModel["%sFormat" % field] = "%.2f" % dataModel[field];
        
# CGI Boilerplate to initiate script
if __name__ == "__main__":
    webController =  OrderSetSearch()
    webController.handleRequest(cgi.FieldStorage())

# WSGI Boilerplate to initiate script
webController = OrderSetSearch()
webController.setFilePath(__file__)
application = webController.wsgiHandler 