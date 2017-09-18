#!/usr/bin/env python
import sys, os;
import cgi
import cgitb; cgitb.enable();
from cStringIO import StringIO;

from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, modelListFromTable;

from medinfo.cpoe.DataManager import DataManager;

from medinfo.web.cgibin.cpoe.dynamicdata.BaseDynamicData import BaseDynamicData;
from medinfo.web.cgibin import Options;

class ClinicalItemData(BaseDynamicData):
    """Simple script to (dynamically) retrieve basic data from clinical_item table,
    and prepare them in JSON (JavaScript Object Notation) format to facilitate
    dynamic / asynchronous page updating
    """

    def __init__(self):
        BaseDynamicData.__init__(self);
        
        self.requestData["clinical_item_category_id"] = ""; # Input categories to display for, may be comma-separated list
        self.requestData["orderBy"] = "name";

        self.requestData["optionValuesJSON"] = "[]";
        self.requestData["optionTextsJSON"] = "[]";
        
        self.addHandler("updateCounts", ClinicalItemData.action_updateCounts.__name__);
        self.addHandler("clinical_item_category_id", ClinicalItemData.action_default.__name__);
        
    def action_updateCounts(self):
        # Update the summary counts to facilitate future rapid queries
        dataManager = DataManager();
        dataManager.updateClinicalItemCounts();

    def action_default(self):
        # Convert query category ID(s) into a list, even of size 1
        categoryIds = self.requestData["clinical_item_category_id"].split(",");
    
        query = SQLQuery();
        query.addSelect("ci.clinical_item_id");
        query.addSelect("ci.name");
        query.addSelect("ci.description");
        query.addSelect("ci.item_count");
        query.addFrom("clinical_item as ci");
        query.addWhere("analysis_status = 1");  # Ignore specified items
        query.addWhereIn("ci.clinical_item_category_id", categoryIds );
        query.addOrderBy( self.requestData["orderBy"] );
        
        resultTable = DBUtil.execute( query, includeColumnNames=True );
        resultModels = modelListFromTable( resultTable );
        
        optionValues = [];
        optionTexts = [];
        
        displayFields = ("name","description","item_count");
        
        for resultModel in resultModels:
            optionValues.append( str(resultModel["clinical_item_id"]) );
            
            orderField = self.requestData["orderBy"].split()[0];
            orderValue = resultModel[orderField];
            textValueList = [str(orderValue)];
            for field in displayFields:
                if field != orderField:
                    textValueList.append(str(resultModel[field]));

            textValue = str.join(" - ", textValueList );
            
            optionTexts.append(textValue);

        # Conveniently, Python string representation coincides with JavaScript
        self.requestData["optionValuesJSON"] = str(optionValues);
        self.requestData["optionTextsJSON"] = str(optionTexts);

# CGI Boilerplate to initiate script
if __name__ == "__main__":
    webController =  ClinicalItemData()
    webController.handleRequest(cgi.FieldStorage())

# WSGI Boilerplate to initiate script
webController = ClinicalItemData()
webController.setFilePath(__file__)
application = webController.wsgiHandler 