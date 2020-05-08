#!/usr/bin/env python
"""
Run external regression modules on query-outcome data
"""

import sys, os
import time;
import json;
from datetime import timedelta;
from optparse import OptionParser
from io import StringIO;

from sklearn.linear_model import LinearRegression, Lasso, LogisticRegression;
from numpy import array;

from medinfo.db.Model import columnFromModelList;
from medinfo.common.Const import COMMENT_TAG;
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.common.StatsUtil import ContingencyStats;
from medinfo.db.ResultsFormatter import TextResultsFormatter;
from medinfo.db.Model import RowItemModel;
from medinfo.cpoe.ItemRecommender import RecommenderQuery;
from medinfo.cpoe.ItemRecommender import ItemAssociationRecommender;
from .Util import log;
from .Const import OUTCOME_ABSENT, OUTCOME_PRESENT, OUTCOME_IN_QUERY;

from .BaseAnalysis import BaseAnalysis;

class RegressionAnalysis(BaseAnalysis):
    def __init__(self):
        BaseAnalysis.__init__(self);

    def fileToMatrixes(self, inputFile, outcomeId, externalQueryIds=None):
        """Extract out feature and outcome matrixes from inputFiles
        If externalQueryIds specified, use that to key the feature matrix
        """
    
        allQueryItemIds = set();    # Track all feature variables available
        allOutcomeIds = set();  # Track all dependent variables to assess
        
        rowModels = list();
        
        headers = None;
        for line in inputFile:
            line = line.strip();
            if not line.startswith(COMMENT_TAG):   # Ignore comment lines
                if headers is None:
                    # Separate out header line
                    headers = line.split("\t");
                else:
                    # General data line
                    chunks = line.split("\t");
                    
                    rowModel = RowItemModel(chunks,headers);
                    
                    # Pull out query items
                    rowModel["queryItemIds"] = set(json.loads(rowModel["queryItemIdsJSON"]));
                    allQueryItemIds.update(rowModel["queryItemIds"]);
                    
                    # Pull out any outcome variables
                    outcomeInQuery = False;
                    for key,value in rowModel.items():
                        if key.startswith("outcome."):
                            aOutcomeId = int(key[len("outcome."):]);
                            allOutcomeIds.add(aOutcomeId);
                            if int(value) == OUTCOME_IN_QUERY:  # Flag trivial cases where outcome event already occurred during query period
                                outcomeInQuery = True;
                    if not outcomeInQuery:
                        rowModels.append(rowModel);

        # Now convert results into feature and output matrixes
        if outcomeId in allQueryItemIds:
            allQueryItemIds.remove(outcomeId);
        allQueryItemIdList = list(allQueryItemIds);
        if externalQueryIds:
            allQueryItemIdList = list(externalQueryIds);
        allQueryItemIdList.sort();
        nFeatures = len(allQueryItemIdList);
        nPatients = len(rowModels);
        featureMatrix = [[0]*nFeatures]*nPatients; # Pre-allocate 2-D array, defaulted to 0 values
        
        allOutcomeIdList = list(allOutcomeIds);
        allOutcomeIdList.sort();
        nOutcomes = len(allOutcomeIdList);
        outcomeMatrix = [0]*nPatients;  # Only due for single specified outcomeId for now

        for iPatient, rowModel in enumerate(rowModels):
            for iItem, queryItemId in enumerate(allQueryItemIdList):
                if queryItemId in rowModel["queryItemIds"]:
                    featureMatrix[iPatient][iItem] = 1;
            outcomeHeader = "outcome.%s" % outcomeId;
            outcomeMatrix[iPatient] = json.loads(rowModel[outcomeHeader]);
        
        # Return as numpy arrays for subsequent efficient access
        return (array(featureMatrix), array(outcomeMatrix), allQueryItemIdList, rowModels);

    def train(self, trainX, trainY):
        #model = LinearRegression();
        #model = Lasso(alpha=0.05);
        model = LogisticRegression(penalty='L1');
        model.fit(trainX, trainY);
        return model;        

    def predict(self, testFile, model, queryIds, outcomeId, options=None):
        """Pull out test data and use model to predict outcome scores for comparison"""
        (testX, testY, queryIds, rowModels) = self.fileToMatrixes(testFile, outcomeId, queryIds);
        print(model.coef_, file=sys.stderr)
        print(model.intercept_, file=sys.stderr)

        for queryId, b in zip(queryIds, model.coef_[0]):
            if b != 0:
                print(queryId, b, file=sys.stderr);

        #print lr.predict( testX );
        testYscore = model.predict_proba(testX);
        
        analysisResults = list();
        for (outcome,scoreArr,rowModel) in zip(testY, testYscore, rowModels):
            resultRowModel = RowItemModel([outcome, scoreArr[0], rowModel["patient_id"], rowModel["queryItemIdsJSON"]], self.analysisHeaders(outcomeId) );
            analysisResults.append( resultRowModel );
        return analysisResults;

    def analysisHeaders(self, outcomeId):
        colNames = list();
        
        colNames.append("outcome.%s" % outcomeId );
        colNames.append("score.%s" % outcomeId );
        
        colNames.append("patient_id");
        colNames.append("queryItemIdList");
        
        return colNames;


    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <trainFile> <testFile> [<outputFile>]\n"+\
                    "   <trainFile> Tab-delimited file, queryItemIdsJSON expected to be parseable into lists of query items as well as an outcome.X column\n"+\
                    "   <testFile> Same structure as trainFile, but with test cases to assess prediction scoring\n"+\
                    "   <outputFile>    Tab-delimited that can be used for ROC analysis with columns for outcome and predicted score\n"+\
                    "";
        parser = OptionParser(usage=usageStr)
        parser.add_option("-o", "--outcomeItemId", dest="outcomeItemId", help="Outcome item IDs to assess get prediction scores for");

        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) > 2:
            trainFile = stdOpen(args[0]);
            testFile = stdOpen(args[1]);
            
            outcomeId = int(options.outcomeItemId);
            
            # Run the actual analysis
            (featureMatrix, outcomeMatrix, queryIds, rowModels) = self.fileToMatrixes(trainFile, outcomeId);
            model = self.train(featureMatrix,outcomeMatrix);
            analysisResults = self.predict(testFile, model, queryIds, outcomeId);

            # Format the results for output
            outputFilename = None;
            if len(args) > 2:
                outputFilename = args[2];
            outputFile = stdOpen(outputFilename,"w");
            
            # Print comment line with arguments to allow for deconstruction later as well as extra results
            print(COMMENT_TAG, json.dumps({"argv":argv}), file=outputFile);

            colNames = self.analysisHeaders(outcomeId);
            analysisResults.insert(0, RowItemModel(colNames,colNames) );    # Insert a mock record to get a header / label row
            
            formatter = TextResultsFormatter( outputFile );
            formatter.formatResultDicts( analysisResults, colNames );

        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = RegressionAnalysis();
    instance.main(sys.argv);
