import Const
import sys, os
import logging
import cgi, UserDict
import unittest

import json;

from medinfo.common.Const import COMMENT_TAG, NULL_STRING;
from medinfo.db.Model import SQLQuery, RowItemModel;

from medinfo.db.test.Util import DBTestCase;

import medinfo.analysis.Util;


log = logging.getLogger("CDSS")
log.setLevel(Const.LOGGER_LEVEL)

handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(Const.LOGGER_FORMAT)

handler.setFormatter(formatter)
log.addHandler(handler)

# Suppress uninteresting application output
medinfo.analysis.Util.log.setLevel(Const.APP_LOGGER_LEVEL)


class BaseTestAnalysis(DBTestCase):

    def assertEqualStatResults(self, expectedResults, analysisResults, colNames):
        for expectedDict, analysisDict in zip(expectedResults, analysisResults):
            #print >> sys.stderr, colNames;
            #print >> sys.stderr, expectedDict.valuesByName(colNames);
            #print >> sys.stderr, analysisDict.valuesByName(colNames);
            for key in colNames:
                expectedValue = expectedDict[key];
                analysisValue = analysisDict[key];
                try:    # Assume numerical values and just check for "close enough"
                    self.assertAlmostEquals( expectedValue, analysisValue, 3 );
                except TypeError:   # Not numbers, then just use generic equals check
                    self.assertEqual( expectedValue, analysisValue );
        self.assertEquals(len(expectedResults),len(analysisResults));

    def assertEqualStatResultsTextOutput(self, expectedResults, textOutput, colNames):
        # Convert the text output into a structured format to facilitate verification testing
        headerLine = None;
        while headerLine is None:
            nextLine = textOutput.readline();
            if not nextLine.startswith(COMMENT_TAG):
                headerLine = nextLine;
        headers = headerLine.strip().split("\t");

        analysisResults = list();
        for line in textOutput:
            dataChunks = line.strip().split("\t");
            resultModel = RowItemModel( dataChunks, headers );
            # Convert the target elements of interest into numerical values
            for col in colNames:
                if resultModel[col] == NULL_STRING:
                    resultModel[col] = None;
                else:
                    try:
                        resultModel[col] = float(resultModel[col]);
                    except ValueError:
                        pass;   # Not a number, just leave it as original value then
            analysisResults.append(resultModel);

        self.assertEqualStatResults( expectedResults, analysisResults, colNames );

    def extractJSONComment(self, dataFile):
        """Iterate through lines of the file until find a comment line to
        extract out a JSON data object."""
        for line in dataFile:
            if line.startswith(COMMENT_TAG):
                jsonStr = line[1:].strip(); # Remove comment tag and any flanking whitespace
                jsonData = json.loads(jsonStr);
                return jsonData;
        return None;
