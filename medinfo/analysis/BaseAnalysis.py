#!/usr/bin/env python
"""
Base Analysis module to assess results of recommenders / predictors.
"""

import sys, os
import time;
from optparse import OptionParser
from cStringIO import StringIO;
from math import sqrt;
from datetime import timedelta;

from medinfo.common.Const import COMMENT_TAG, VALUE_DELIM;
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel;
from medinfo.db.Model import modelListFromTable, modelDictFromList;
from Util import log;

from Const import OUTCOME_ABSENT, OUTCOME_PRESENT, OUTCOME_IN_QUERY;
from Const import NEGATIVE_OUTCOME_STRS;


class BaseAnalysis:
    connFactory = None;

    def __init__(self):
        self.connFactory = DBUtil.ConnectionFactory();  # Default connection source

    def parseScoreFile(self, inputFile, delim=None, colOutcome=None, colScore=None):
        """Parse the contents of the give input file
        looking for columns of white-space separated data after a header line.
        Expect (1st) column represents an outcome label (see NEGATIVE_OUTCOME_STRS) for acceptable labels.
        Expect (2nd) column represents a (list of) numerical score(s) to predict the outcome.
           If above provided as strings instead of column index numbers, then will interpret as header columns
        """
        if delim is None:   delim = '\t';   # Default to tab-delimited

        headerLine = None;
        for line in inputFile:
            line = line.strip();
            if not line.startswith(COMMENT_TAG):   # Ignore comment lines
                headerLine = line;
                break;
        # Parse out the header line columns
        headers = headerLine.split(delim);
        iColByHeader = dict();
        for iCol, header in enumerate(headers):
            iColByHeader[header] = iCol;

        # Default to first and second columns
        if colOutcome is None:  colOutcome = headers[0];
        if colScore is None:    colScore = headers[1];

        # Translate column headers into indexes or names as needed
        iColOutcome = None;
        if colOutcome in iColByHeader:
            iColOutcome = iColByHeader[colOutcome];
        else:   # Otherwise assume a numerical index
            iColOutcome = int(colOutcome);
        
        iColScoreList = list();
        for colScoreValue in colScore.split(VALUE_DELIM):
            if colScoreValue in iColByHeader:
                iColScoreList.append(iColByHeader[colScoreValue]);
            else:   # Otherwise assume a numerical index
                iColScoreList.append(int(colScoreValue));
        
        # Accumulating data into list of outcome values, then a dictionary keyed by score column names and values equal to matching lists of scores
        outcomes = list();
        scoresById = dict();
        for iColScore in iColScoreList:
            scoreHeader = headers[iColScore];
            scoresById[scoreHeader] = list();
        for line in inputFile:
            line = line.strip();
            if not line.startswith(COMMENT_TAG):   # Ignore comment lines
                # General data line
                chunks = line.split(delim);
                outcome = OUTCOME_PRESENT;
                if chunks[iColOutcome] in NEGATIVE_OUTCOME_STRS:
                    outcome = OUTCOME_ABSENT;    # Assume all other strings represent a positive outcome
                outcomes.append(outcome);
                
                for iColScore in iColScoreList:
                    scoreHeader = headers[iColScore];
                    score = float(chunks[iColScore]);
                    scoresById[scoreHeader].append(score);
        return (outcomes, scoresById);

    def parseScoreModelsFromFile(self, inputFile, colOutcome=None, scoreCols=None):
        """Structured variant of above.  Assume named columns and just return combined dictionary / RowItemModels
        """
        scoreModels = list();
        for scoreModel in TabDictReader(inputFile):
            # Data parsing for any named columns
            if colOutcome is not None:
                outcome = OUTCOME_PRESENT;
                if scoreModel[colOutcome] in NEGATIVE_OUTCOME_STRS:
                    outcome = OUTCOME_ABSENT;
                scoreModel[colOutcome] = outcome;



            # Temporary hack to get P-Fisher-NegLog into dataset
            import math;
            if scoreCols is not None and "P-Fisher-NegLog" in scoreCols:
                p = float(scoreModel["P-Fisher"]);
                logP = -sys.float_info.max;
                if p > 0.0:
                    logP = math.log(p,10);
                if scoreModel["OR"] > 1.0:
                    logP *= -1;
                scoreModel["P-Fisher-NegLog"] = logP;

            if scoreCols is not None:
                for colScore in scoreCols:
                    scoreModel[colScore] = float(scoreModel[colScore]);

            scoreModels.append(scoreModel);
        return scoreModels;
