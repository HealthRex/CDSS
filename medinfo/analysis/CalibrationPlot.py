#!/usr/bin/env python
"""
Translate results of OutcomePredictionAnalysis into data for a Calibration plot.
Usually feed the data (Paired columns of scores and actual outcome labels)
  into an ROC curve analysis program to assess for classifer discrimination.
Calibration curve generally splits scored entries into deciles and compares how well
  the predicted probability match up to the actual outcome frequencies.
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

class CalibrationPlot(BaseAnalysis):
    def __init__(self):
        BaseAnalysis.__init__(self);

    def analysisHeaders(self):
        return ("scoreMin","scoreMax", "totalInstances","observedOutcomes", "predictedOutcomes", "observedRate", "predictedRate");

    def __call__(self, inputFile, nBins, colScore=None):
        (outcomes, scoresById) = self.parseScoreFile(inputFile);
        if colScore is None:
            colScore = list(scoresById.keys())[0];    # Arbitrarily select the first score column found
        scores = scoresById[colScore];
        results = self.binData( outcomes, scores, nBins );
        return results;

    def binData(self, outcomes, scores, nBins):
        """Expect lists of predicted score value and matching outcome values
        encoded as 0 or +1 for negative and positive results.
        Organizes data into nBins of percentile separated scores to compare predicted vs. observed outcome rates
        Returns a list of dictionaries, one for each data bin generated with key-values
            corresponding to bin stats 
            (e.g., scoreMin, scoreMax, 
            totalInstances, observedOutcomes, predictedOutcomes, 
            observedRate, predictedRate)
        """
        results = [];
        
        data = [(score,outcome) for (outcome, score) in zip(outcomes,scores)];  # Repackage into single list of 2-ples to facilitate sorting

        data.sort();
        nData = len(data);
        binSize = nData // nBins;
        for iBin in range(nBins):
            iBinDataMin = iBin*binSize;
            iBinDataMax = (iBin+1)*binSize;
            if (iBin+1) == nBins:
                iBinDataMax = nData;    # Catch any leftovers in the last bin
            
            # Count up summary statistics for the bin
            nBinData = 0;
            nOutcomes = 0;
            scoreSum = 0.0;
            scoreMin = None;
            scoreMax = None;
            for iData in range(iBinDataMin, iBinDataMax):
                (score, outcome) = data[iData];
                if scoreMin is None or score < scoreMin:
                    scoreMin = score;
                if scoreMax is None or score > scoreMax:
                    scoreMax = score;
                scoreSum += score;
                if outcome != 0:
                    nOutcomes += 1;
                nBinData += 1;

            binResults = \
                {   "scoreMin": scoreMin,
                    "scoreMax": scoreMax, 
                    "totalInstances": nBinData,
                    "observedOutcomes": nOutcomes, 
                    "predictedOutcomes": scoreSum, 
                    "observedRate": float(nOutcomes)/nBinData, 
                    "predictedRate": scoreSum/nBinData,
                }
            results.append(binResults);
        return results;        

    def calculateHosmerLemeshow(self, results):
        """Calculate summary statistic to see if there is significant difference in the calibration values
        http://en.wikipedia.org/wiki/Hosmer%E2%80%93Lemeshow_test
        
        Returns HL stat (approaches chi-square distribution), Degrees of Freedom (number of results - 2),
        and P-value for significant difference based on chi-square assumption.
        """
        hlStat = 0.0;
        g = 0;
        for result in results:
            Og = result["observedOutcomes"];
            Eg = result["predictedOutcomes"];
            Ng = result["totalInstances"];
            PIg= result["predictedRate"];

            if Ng > 0:  # Skip bins with no data
                hlStat += (Og-Eg)**2 / (Ng*PIg*(1-PIg));
                g += 1;

        degFreedom = g-2;
        hlP = 1 - chi2.cdf(hlStat, degFreedom);
        
        return (hlStat, degFreedom, hlP);
    
    def generateFigure(self, calibrationResults, figureFilename=None):
        """Quickly generate an example visualization figure with pylab (matplotlib)
        """
        import pylab;   # Only import dependency as needed
        predictedRates = columnFromModelList(calibrationResults,"predictedRate");
        observedRates = columnFromModelList(calibrationResults,"observedRate");
        instanceCounts = columnFromModelList(calibrationResults,"totalInstances");
        
        markerScalar = 20.0 / min(instanceCounts);
        markerWidths = [ instanceCount*markerScalar for instanceCount in instanceCounts ];

        (hlStat, degFreedom, hlP) = self.calculateHosmerLemeshow(calibrationResults);

        xMax = max(predictedRates)*1.05;
        yMax = max(observedRates)*1.05;
        xyMax = max(xMax,yMax);

        pylab.clf();
        pylab.scatter(predictedRates, observedRates, markerWidths, label='P-Hosmer-Lemeshow %0.5f' % hlP);
        pylab.plot([0,xyMax],[0,xyMax], 'k--'); # Diagonal line for optimally calibrated result reference
        pylab.xlim([0.0, xMax]);
        pylab.ylim([0.0, yMax]);
        pylab.xlabel('Predicted Rate');
        pylab.ylabel('Observed Rate');
        pylab.title('Calibration Curve (%s)' % figureFilename );
        pylab.legend(loc="upper left");
        if figureFilename is None:
            # No file specified, just try to do a direct display
            pylab.show(block=True);
        else:
            pylab.savefig(figureFilename);
    
    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <inputFile> [<outputFile>]\n"+\
                    "   <inputFile> Tab-delimited file, first two labeled columns expected to represent labeled outcome (0 and non-zero) and score/probability of outcome\n"+\
                    "   <outputFile>    Tab-delimited table specifying score histogram bin widths, total cases, predicted events, actual events\n"+\
                    "                       Leave blank or specify \"-\" to send to stdout.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-b", "--bins",  dest="nBins",  default=10,    help="Number of bins to separate scores into, defaults to deciles (10)");
        parser.add_option("-f", "--figure",  dest="figure",  help="If set, will also try to auto-generate an example figure and store to a file here");

        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) > 1:
            inputFilename = args[0];
            inputFile = stdOpen(inputFilename);
            
            # Run the actual analysis
            analysisResults = self(inputFile, int(options.nBins));
            
            (hlStat, degFreedom, hlP) = self.calculateHosmerLemeshow(analysisResults);
            
            # Generate plot figure
            if options.figure is not None:
                self.generateFigure(analysisResults, options.figure);

            # Format the results for output
            outputFilename = None;
            if len(args) > 1:
                outputFilename = args[1];
            outputFile = stdOpen(outputFilename,"w");
            
            # Print comment line with arguments to allow for deconstruction later as well as extra results
            print(COMMENT_TAG, json.dumps({"argv":argv, "P-HosmerLemeshow": hlP}), file=outputFile);

            colNames = self.analysisHeaders();
            analysisResults.insert(0, RowItemModel(colNames,colNames) );    # Insert a mock record to get a header / label row
            
            formatter = TextResultsFormatter( outputFile );
            formatter.formatResultDicts( analysisResults, colNames );

        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = CalibrationPlot();
    instance.main(sys.argv);
