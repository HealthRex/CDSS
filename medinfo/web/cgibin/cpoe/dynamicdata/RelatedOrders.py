#!/usr/bin/env python
import sys, os;
import time;
import cgi
import cgitb; cgitb.enable();
from cStringIO import StringIO;

from medinfo.common.Const import FALSE_STRINGS;

from medinfo.cpoe.ItemRecommender import RecommenderQuery;
from medinfo.cpoe.ItemRecommender import ItemAssociationRecommender;
from medinfo.cpoe.Const import BASELINE_FIELDS, CORE_FIELDS, PERCENT_FIELDS;

from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, modelListFromTable;
from medinfo.db.Model import RowItemFieldComparator
from medinfo.db.ResultsFormatter import HtmlResultsFormatter;

from medinfo.common.StatsUtil import ContingencyStats;

from medinfo.cpoe.cpoeSim.SimManager import SimManager, ClinicalItemQuery;

from medinfo.web.cgibin.cpoe.dynamicdata.BaseDynamicData import BaseDynamicData;
from medinfo.web.cgibin import Options;
from medinfo.web.cgibin.Util import webDataCache;

CATEGORY_HEADER_TEMPLATE = \
    """
    <tr><td class="spacer" height=10 colspan=100></td></tr>
    <tr><td colspan=%(nPreCols)s></td><td colspan=99><b>%(category_description)s</b></td></tr>
    """;
CONTROLS_TEMPLATE = \
    """
    <input type=checkbox class="orderCheckbox" onClick="selectItem(this)" value="%(clinical_item_id)s|%(name)s|%(description)s">
    """;
DESCRIPTION_TEMPLATE = \
    """<a href="javascript:clickItemById(%(clinical_item_id)s)">%(description)s</a>""";
RELATED_LINK_TEMPLATE = \
    """&nbsp;<a href="javascript:loadRelatedOrders('%(clinical_item_id)s')"><img src="../../resource/graphIcon.png" width=12 height=12 alt="Find Related Orders"></a>""";

class RelatedOrders(BaseDynamicData):
    """Simple script to (dynamically) relay query and result data
    from the ItemRecommendation module in URL request then HTML table format.
    """
    def __init__(self):
        BaseDynamicData.__init__(self);

        self.requestData["searchStr"] = "";
        self.requestData["analysisStatus"] = "1";

        self.requestData["sim_patient_id"] = "";
        self.requestData["sim_time"] = "";

        self.requestData["sourceTables"] = "stride_order_proc,stride_order_med";    # Default comma-separated list of source tables to expect orders to reside in
        self.requestData["queryItemIds"] = "";
        self.requestData["targetItemIds"] = "";
        self.requestData["excludeItemIds"] = "";
        self.requestData["excludeCategoryIds"] = "";
        self.requestData["timeDeltaMax"] = "86400"; # Look for recommendations likely within 24 hours
        self.requestData["sortField"] = "";
        self.requestData["enableRecommender"] = "True";  # By default, asssume recommender is enabled
        self.requestData["displayFields"] = ""; #"prevalence","PPV","RR","P-YatesChi2"
        self.requestData["sortReverse"] = "True";
        self.requestData["nPreCols"] = "1";
        self.requestData["groupByCategory"] = "True";
        self.requestData["resultCount"] = "10"; # Default for related order search
        self.requestData["invertQuery"] = "";
        self.requestData["showCounts"] = "";
        self.requestData["countPrefix"] = "patient_";
        self.requestData["aggregationMethod"] = "weighted";

        self.requestData["title"] = "Order Search Results";
        self.requestData["fieldHeaders"] = "";
        self.requestData["dataRows"] = '<tr><td colspan=100 align=center height=200><img src="../../resource/ajax-loader.gif"></td></tr>';

        self.addHandler("searchStr", RelatedOrders.action_orderSearch.__name__);
        self.addHandler("RelatedOrders", RelatedOrders.action_default.__name__);

    def action_orderSearch(self):
        """Search for orders by query string"""
        manager = SimManager();
        query = ClinicalItemQuery();
        query.parseParams(self.requestData);
        query.sourceTables = self.requestData["sourceTables"].split(",");
        results = manager.clinicalItemSearch(query);

        lastModel = None;
        for dataModel in results:
            dataModel["controls"] = CONTROLS_TEMPLATE % dataModel;
            dataModel["nPreCols"] = self.requestData["nPreCols"];
            dataModel["category_description.format"] = "";
            if lastModel is None or lastModel["category_description"] != dataModel["category_description"]:
                dataModel["category_description.format"] = "<b>%s</b>" % dataModel["category_description"];   # Only show category if new
            lastModel = dataModel;

        colNames = ["controls","description"];   # "name" for order code. ,"category_description.format"
        lastModel = None;
        htmlLines = list();
        for dataModel in results:
            newCategory = (lastModel is None or lastModel["category_description"] != dataModel["category_description"] );
            showCategory = (self.requestData["groupByCategory"] and newCategory);   # Limit category display if many repeats
            if showCategory:
                htmlLines.append( CATEGORY_HEADER_TEMPLATE % dataModel );
            htmlLines.append( self.formatRowHTML(dataModel, colNames, showCategory) );
            lastModel = dataModel;
        self.requestData["dataRows"] = str.join("\n", htmlLines );

    def action_default(self):
        """Look for related orders by association / recommender methods"""
        # If patient is specified then modify query and exclusion list based on items already ordered for patient
        recentItemIds = set();
        if self.requestData["sim_patient_id"]:
            patientId = int(self.requestData["sim_patient_id"]);
            simTime = int(self.requestData["sim_time"]);

            # Track recent item IDs (orders, diagnoses, unlocked results, etc. that related order queries will be based off of)
            manager = SimManager();
            recentItemIds = manager.recentItemIds(patientId, simTime);

        # Recommender Instance to test on
        self.recommender = ItemAssociationRecommender();
        self.recommender.dataManager.dataCache = webDataCache;  # Allow caching of data for rapid successive queries

        query = RecommenderQuery();
        if self.requestData["sortField"] == "":
            self.requestData["sortField"] = "P-YatesChi2-NegLog";   # P-Fisher-NegLog should yield better results, but beware, much longer to calculate
        query.parseParams(self.requestData);
        if len(query.excludeItemIds) == 0:
            query.excludeItemIds = self.recommender.defaultExcludedClinicalItemIds();
        if len(query.excludeCategoryIds) == 0:
            query.excludeCategoryIds = self.recommender.defaultExcludedClinicalItemCategoryIds();
        #query.fieldList.extend( ["prevalence","PPV","RR"] );
        displayFields = list();
        if self.requestData["displayFields"] != "":
            displayFields = self.requestData["displayFields"].split(",");

        # Exclude items already ordered for the patient from any recommended list
        query.excludeItemIds.update(recentItemIds);
        if not query.queryItemIds:  # If no specific query items specified, then use the recent patient item IDs
            query.queryItemIds.update(recentItemIds);

        recommendedData = self.recommender( query );

        if len(recommendedData) > 0:
            # Denormalize results with links to clinical item descriptions
            self.recommender.formatRecommenderResults(recommendedData);

        # Display fields should append Format suffix to identify which version to display, but use original for header labels
        (self.requestData["fieldHeaders"], displayFieldsFormatSuffixed) = self.prepareDisplayHeaders(displayFields);

        # Format for HTML and add a control field for interaction with the data
        for dataModel in recommendedData:
            self.prepareResultRow(dataModel, displayFields);

        # Try organize by category
        if self.requestData["groupByCategory"]:
            recommendedData = self.recommender.organizeByCategory(recommendedData);

        colNames = ["controls"];   # "name" for code. ,"category_description"
        colNames.extend(displayFieldsFormatSuffixed);
        colNames.extend(["description"]);

        lastModel = None;
        htmlLines = list();
        for dataModel in recommendedData:
            newCategory = (lastModel is None or lastModel["category_description"] != dataModel["category_description"] );
            showCategory = (self.requestData["groupByCategory"] and newCategory);   # Limit category display if many repeats
            if showCategory:
                htmlLines.append( CATEGORY_HEADER_TEMPLATE % dataModel );
            htmlLines.append( self.formatRowHTML(dataModel, colNames, showCategory) );
            lastModel = dataModel;
        self.requestData["dataRows"] = str.join("\n", htmlLines );

    def prepareDisplayHeaders(self, displayFields):
        showCounts = (self.requestData["showCounts"].lower() not in FALSE_STRINGS);

        fieldHeadersHTML  = "";
        for displayField in displayFields:
            fieldHeadersHTML += '<th nowrap>' + displayField + '</th>';
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
        dataModel["nPreCols"] = len(displayFields)+1;   # Track spacer columns leading up to order description. +1 for control column
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
            elif field in PERCENT_FIELDS:
                # Format as a percentage
                dataModel["%sFormat" % field] = "%d%%" % (dataModel[field]*100);
            elif abs(dataModel[field]) < 0.01:
                # Allow formatting for very small values
                dataModel["%sFormat" % field] = "%.0e" % dataModel[field];
            elif abs(dataModel[field]) < 1:
                # Smaller value, show more significant digits
                dataModel["%sFormat" % field] = "%.2f" % dataModel[field];
            else:
                # Default just format as limited floating point values
                dataModel["%sFormat" % field] = "%.1f" % dataModel[field];

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

    def formatRowHTML(self, dataModel, colNames, showCategory=True):
        """Specific formatting for row data elements
        """
        htmlList = list();
        htmlList.append('<tr valign=top>');
        for col in colNames:
            if col == "category_description":  # Blank out repeat categories
                if showCategory:
                    htmlList.append('<td align=center><b>%(category_description)s</b></td>' % dataModel);
                else:
                    htmlList.append('<td></td>');
            elif col == "description":
                htmlList.append('<td align=left>');
                htmlList.append( DESCRIPTION_TEMPLATE % dataModel);
                # Only include related link if recommender is enabled
                if self.requestData['enableRecommender'] == "True":
                    htmlList.append( RELATED_LINK_TEMPLATE % dataModel);
                htmlList.append('</td>');
            else:
                htmlList.append('<td align=right>%s</td>' % dataModel[col]);
        htmlList.append('</tr>');
        return str.join("\n", htmlList);

# CGI Boilerplate to initiate script
if __name__ == "__main__":
    webController =  RelatedOrders()
    webController.handleRequest(cgi.FieldStorage())

# WSGI Boilerplate to initiate script
webController = RelatedOrders()
webController.setFilePath(__file__)
application = webController.wsgiHandler
