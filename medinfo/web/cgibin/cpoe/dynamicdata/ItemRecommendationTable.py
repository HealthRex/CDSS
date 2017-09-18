#!/usr/bin/env python
import sys, os;
import cgi
import cgitb; cgitb.enable();
from cStringIO import StringIO;

from medinfo.common.Const import FALSE_STRINGS;

from medinfo.cpoe.ItemRecommender import RecommenderQuery;
from medinfo.cpoe.ItemRecommender import ItemAssociationRecommender;
from medinfo.cpoe.Const import BASELINE_FIELDS, CORE_FIELDS;

from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, modelListFromTable;
from medinfo.db.ResultsFormatter import HtmlResultsFormatter;

from medinfo.common.StatsUtil import ContingencyStats;

from medinfo.web.cgibin.cpoe.dynamicdata.BaseDynamicData import BaseDynamicData;
from medinfo.web.cgibin import Options;
from medinfo.web.cgibin.Util import webDataCache;

CONTROLS_TEMPLATE = \
    """
    <input type=checkbox onClick="document.forms[0].clinicalItemSelected.options.add( new Option('%(name)s - %(description)s', '%(clinical_item_id)s') ); this.disabled = true;">
    """;
class ItemRecommendationTable(BaseDynamicData):
    """Simple script to (dynamically) relay query and result data
    from the ItemRecommendation module in URL request then HTML table format.
    """
    def __init__(self):
        BaseDynamicData.__init__(self);
        
        self.requestData["queryItemIds"] = "";
        self.requestData["targetItemIds"] = "";
        self.requestData["excludeItemIds"] = "";
        self.requestData["excludeCategoryIds"] = "";
        self.requestData["timeDeltaMax"] = "";
        self.requestData["sortField"] = "PPV";
        self.requestData["sortReverse"] = "True";
        self.requestData["resultCount"] = "10";
        self.requestData["invertQuery"] = "";
        self.requestData["showCounts"] = "";
        self.requestData["countPrefix"] = "";
        self.requestData["aggregationMethod"] = "weighted";

        self.requestData["fieldHeaders"] = "";
        self.requestData["dataRows"] = "";
        
        self.addHandler("resultCount", ItemRecommendationTable.action_default.__name__);

        self.recommender = ItemAssociationRecommender();  # Instance to test on
        self.recommender.dataManager.dataCache = webDataCache;

        
    def action_default(self):

        query = RecommenderQuery();
        query.parseParams(self.requestData);
        displayFields = query.getDisplayFields();

        recommendedData = self.recommender( query );

        if len(recommendedData) > 0:
            # Denormalize results with links to clinical item descriptions
            self.recommender.formatRecommenderResults(recommendedData);
        
        # Format for HTML and add a control field for interaction with the data
        for dataModel in recommendedData:
            self.prepareResultRow(dataModel, displayFields);
        
        # Display fields should append Format suffix to identify which version to display, but use original for header labels
        (self.requestData["fieldHeaders"], displayFieldsFormatSuffixed) = self.prepareDisplayHeaders(displayFields);
        
        colNames = ["controls","rank","name","description","category_description"];
        colNames.extend(displayFieldsFormatSuffixed);
        formatter = HtmlResultsFormatter( StringIO(), valign="middle", align="center");
        formatter.formatResultDicts( recommendedData, colNames );

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
            elif dataModel[field] == sys.float_info.max:
                dataModel["%sFormat" % field] = "MaxOverflow";  # Symbolic representation of very large value
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
    webController =  ItemRecommendationTable()
    webController.handleRequest(cgi.FieldStorage())

# WSGI Boilerplate to initiate script
webController = ItemRecommendationTable()
webController.setFilePath(__file__)
application = webController.wsgiHandler 