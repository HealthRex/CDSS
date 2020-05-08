#!/usr/bin/env python
"""
Simple Python CGI script to test web interface to molecule file processing modules
"""

import sys
import cgi
import cgitb; cgitb.enable()

from io import StringIO;
import time

from medinfo.db import DBUtil
from medinfo.db.ResultsFormatter import TextResultsFormatter, HtmlResultsFormatter
from medinfo.cpoe.Const import DELTA_NAME_BY_SECONDS;

from medinfo.web.cgibin.cpoe.BaseCPOEWeb import BaseCPOEWeb

from medinfo.web.cgibin import Options;

class ItemRecommenderWeb(BaseCPOEWeb):
    def __init__(self):
        BaseCPOEWeb.__init__(self)
        # Initialize default values to place in template htm file

        # If not already available, build a list of order / item categories to select from
        if "clinicalItemCategoryAvailable" not in Options.FIELD2VALUE:
            resultTable = \
                DBUtil.execute \
                (   """select 
                       cic.clinical_item_category_id,
                       cic.description,
                       cic.default_recommend,
                       count(ci.name)
                    from 
                       clinical_item as ci,
                       clinical_item_category as cic
                    where
                       ci.clinical_item_category_id = cic.clinical_item_category_id and
                       ci.analysis_status = 1
                    group by
                       cic.clinical_item_category_id,
                       cic.description,
                       cic.default_recommend
                    order by
                       count(ci.name) desc
                    """
                );
            optionValues = [];
            optionTexts = [];
            
            excludeOptionValues = [];
            excludeOptionTexts = [];
            
            for (categoryId, categoryDescr, defaultRecommend, itemCount) in resultTable:
                opValue = str(categoryId);
                opText = "(%d) %s" % (itemCount, categoryDescr);
                
                optionValues.append( opValue );
                optionTexts.append( opText );
                
                if not defaultRecommend:
                    # Don't want this included by default, add to exclusion list
                    excludeOptionValues.append( opValue );
                    excludeOptionTexts.append( opText );

            Options.FIELD2VALUE["clinicalItemCategoryAvailable"] = optionValues;
            Options.FIELD2TEXT ["clinicalItemCategoryAvailable"] = optionTexts;

            Options.FIELD2VALUE["clinicalItemCategoryExcluded"] = excludeOptionValues;
            Options.FIELD2TEXT ["clinicalItemCategoryExcluded"] = excludeOptionTexts;

        self.requestData["clinicalItemCategoryOptions"] = self.optionTagsFromField("clinicalItemCategoryAvailable");
        self.requestData["clinicalItemCategoryExcludedOptions"] = self.optionTagsFromField("clinicalItemCategoryExcluded");

        # If not already available, build a list of order / item categories to exclude by default
        if "clinicalItemExcluded" not in Options.FIELD2VALUE:
            resultTable = \
                DBUtil.execute \
                (   """select 
                       ci.clinical_item_id,
                       ci.name,
                       ci.description
                    from 
                       clinical_item as ci
                    where
                       ci.default_recommend = 0
                    order by
                       ci.name
                    """
                );
            excludeOptionValues = [];
            excludeOptionTexts = [];
            
            for (clinicalItemId, itemName, itemDescription) in resultTable:
                opValue = str(clinicalItemId);
                opText = "%s - %s" % (itemName, itemDescription);
                
                excludeOptionValues.append( opValue );
                excludeOptionTexts.append( opText );

            Options.FIELD2VALUE["clinicalItemExcluded"] = excludeOptionValues;
            Options.FIELD2TEXT ["clinicalItemExcluded"] = excludeOptionTexts;

        self.requestData["clinicalItemExcludedOptions"] = self.optionTagsFromField("clinicalItemExcluded");

        if "timeDeltaMax" not in Options.FIELD2VALUE:
            secondsOptions = list(DELTA_NAME_BY_SECONDS.keys());
            secondsOptions.sort();
            Options.FIELD2VALUE["timeDeltaMax"] = [str(seconds) for seconds in secondsOptions];
            Options.FIELD2TEXT ["timeDeltaMax"] = [DELTA_NAME_BY_SECONDS[seconds] for seconds in secondsOptions];
        self.requestData["timeDeltaMaxOptions"] = self.optionTagsFromList(Options.FIELD2VALUE["timeDeltaMax"], Options.FIELD2TEXT["timeDeltaMax"],"86400");

        if "filterField" not in Options.FIELD2VALUE:
            optionPairs = \
            [   
                ("baselineFreq", "Baseline Freq (nB/N)"),
                ("conditionalFreq", "Conditional Freq (nAB/nA)"),
                ("freqRatio", "Freq Ratio = (nAB/nA) / (nB/N)"),
                
                ("OR", "Odds Ratio (OR)"),
                ("OR95CILow", "OR 95% CI, Low"),
                ("OR95CIHigh", "OR 95% CI, High"),
                ("RR", "Relative Risk (RR)"),
                ("RR95CILow", "RR 95% CI, Low"),
                ("RR95CIHigh", "RR 95% CI, High"),
                ("LR", "Positive Likelihood Ratio (LR)"),
                ("LR-", "Negative Likelihood Ratio (LR-)"),
                
                ("sensitivity","Sensitivity"),
                ("specificity","Specificity"),
                ("PPV","Positive Predictive Value (PPV)"),
                ("NPV","Negative Predictive Value (NPV)"),
                
                ("prevalence","Prevalence"),
                
                ("P-YatesChi2", "P-value (Yates-Chi2)"),
                ("P-YatesChi2-NegLog", "P-value (Yates-Chi2), Negative Log"),
                ("P-Fisher", "P-value (Fisher)"),
                ("P-Fisher-NegLog", "P-value (Fisher), Negative Log"),
                #("P-Fisher-Complement", "P-value (Fisher), Complement (1-p)"),
                
                ("nAB", "nAB (query-target co-ocurrences) "),
                ("nA", "nA (query item instances)"),
                ("nB", "nB (target item instances)"),
                ("N", "N (patients)"),
            ];
            optionValues = list();
            optionTexts = list();
            for (value, text) in optionPairs:
                optionValues.append(value);
                optionTexts.append(text);
            Options.FIELD2VALUE["filterField"] = optionValues;
            Options.FIELD2TEXT ["filterField"] = optionTexts;

        self.requestData["sortFieldOptions"] = self.optionTagsFromList(Options.FIELD2VALUE["filterField"], Options.FIELD2TEXT["filterField"], "PPV");
        self.requestData["filterField1Options"] = self.optionTagsFromList(Options.FIELD2VALUE["filterField"], Options.FIELD2TEXT["filterField"],"prevalence");
        self.requestData["filterField2Options"] = self.optionTagsFromList(Options.FIELD2VALUE["filterField"], Options.FIELD2TEXT["filterField"],"PPV");
        self.requestData["filterField3Options"] = self.optionTagsFromList(Options.FIELD2VALUE["filterField"], Options.FIELD2TEXT["filterField"],"RR");
        self.requestData["filterField4Options"] = self.optionTagsFromList(Options.FIELD2VALUE["filterField"], Options.FIELD2TEXT["filterField"],"sensitivity");
        self.requestData["filterField5Options"] = self.optionTagsFromList(Options.FIELD2VALUE["filterField"], Options.FIELD2TEXT["filterField"],"P-YatesChi2");

        self.addHandler(self.requestData["WEB_CLASS"], ItemRecommenderWeb.action_default.__name__)

    def initializeRequestData(self):
        self.requestData["resultsHtml"]   = ""
        self.requestData["resultsText"]   = ""
        self.requestData["resultsInfo"]   = ""

    def action_default(self):
        # Read checkboxes by presence or absence of field
        self.requestData["incCols"] = ""  # Checkboxes not passed if unchecked, so extra step to ensure uncheck is persisted
        incCols = False
        if "incCols" in self.mForm:
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

if __name__ == "__main__":
    print("hello", file=sys.stderr)
    webController =  ItemRecommenderWeb()
    webController.handleRequest(cgi.FieldStorage())

# WSGI Boilerplate to initiate script
webController = ItemRecommenderWeb()
webController.setFilePath(__file__)
application = webController.wsgiHandler 