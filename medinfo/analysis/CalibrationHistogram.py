#!/usr/bin/env python
"""
Translate results of OutcomePredictionAnalysis into data for a Calibration plot.
Usually feed the data (Paired columns of scores and actual outcome labels)
  into an ROC curve analysis program to assess for classifer discrimination.
Calibration curve generally splits scored entries into deciles and compares how well
  the predicted probability match up to the actual outcome frequencies.
Instead of implementation that splits data into 10 equal sized groups,
  instead break up into probability range from 0.0 to 1.0 with specified number
  of equal sized bins in between

"""

import sys, os
import time;
from optparse import OptionParser
from io import StringIO;
import json;
from scipy.stats import chi2;
from medinfo.db.Model import columnFromModelList;
from medinfo.common.Const import COMMENT_TAG;
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db.ResultsFormatter import TextResultsFormatter;
from medinfo.db.Model import RowItemModel;
from .Util import log;

from .BaseAnalysis import BaseAnalysis;
from .CalibrationPlot import CalibrationPlot;

MIN_VALUE = 0.0;
MAX_VALUE = 1.0;

class CalibrationHistogram(CalibrationPlot):
    """Reuse entire structure of CalibrationPlot class, just change the data binning process"""

    def __init__(self):
        CalibrationPlot.__init__(self);

    def binData(self, outcomes, scores, nBins):
        """Expect lists of predicted score value and matching outcome values
        encoded as 0 or +1 for negative and positive results.
        Organizes data into nBins of equal numerical value, but possibly different quantities
         and thencompare predicted vs. observed outcome rates
        Returns a list of dictionaries, one for each data bin generated with key-values
            corresponding to bin stats 
            (e.g., scoreMin, scoreMax, 
            totalInstances, observedOutcomes, predictedOutcomes, 
            observedRate, predictedRate)
        """
        # Setup empty data first
        results = list();
        binSize = (MAX_VALUE - MIN_VALUE) / nBins;
        for iBin in range(nBins):
            binData = \
                {   "scoreMin": MIN_VALUE + binSize * iBin,
                    "scoreMax": MIN_VALUE + binSize * (iBin+1), 
                    "totalInstances": 0,
                    "observedOutcomes": 0.0, 
                    "predictedOutcomes": 0.0, 
                    "observedRate": None,
                    "predictedRate": None,
                };
            results.append(binData);
        
        data = [(score,outcome) for (outcome, score) in zip(outcomes,scores)];  # Repackage into single list of 2-ples to facilitate sorting
        nData = len(data);

        # Iterate through data to accrue bin data
        for (score, outcome) in data:
            iBin = int( (score - MIN_VALUE) / binSize );    # Integer conversion will naturally take floor of value

            results[iBin]["totalInstances"] += 1;
            if outcome != 0:
                results[iBin]["observedOutcomes"] += 1;
            results[iBin]["predictedOutcomes"] += score;

        # Another pass to calculate bin summary stats
        for iBin in range(nBins):
            if results[iBin]["totalInstances"] > 0: # Don't try to calculate for empty bins
                results[iBin]["observedRate"] = results[iBin]["observedOutcomes"] / results[iBin]["totalInstances"];
                results[iBin]["predictedRate"] = results[iBin]["predictedOutcomes"] / results[iBin]["totalInstances"];

        return results;        


if __name__ == "__main__":
    instance = CalibrationHistogram();
    instance.main(sys.argv);
