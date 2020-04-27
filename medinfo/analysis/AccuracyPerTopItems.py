#!/usr/bin/env python
"""
Translate scored outcome files (e.g., output of OutcomePredictionAnalysis or CombineScoreOutcomeFiles
into plots of accuracy scores with respect to the number of top items considered when
sorting by designated score columns.
"""

import sys, os;
import os.path;
import time;
import json;
from optparse import OptionParser
from io import StringIO;
import pylab;
from medinfo.db.Model import columnFromModelList;
from medinfo.common.Const import COMMENT_TAG, VALUE_DELIM;
from medinfo.common.StatsUtil import ContingencyStats;
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.db.Model import RowItemModel;
from .Util import log;
from .Const import OUTCOME_PRESENT, OUTCOME_ABSENT;

from .BaseAnalysis import BaseAnalysis;

AXIS_DELIM = ":";

class AccuracyPerTopItems(BaseAnalysis):
    def __init__(self):
        BaseAnalysis.__init__(self);

    def __call__(self, inputFile, colOutcome, metricsByScoreCol, maxItems):
        scoreCols = list(metricsByScoreCol.keys());
        scoreModels = self.parseScoreModelsFromFile(inputFile, colOutcome, scoreCols);
        
        # Count up total number of items and positive outcomes
        nPositive = sum([scoreModel[colOutcome] for scoreModel in scoreModels]);    # Assumes outcome labels are 0 and 1 for negative and positive, respectively
        nItems = len(scoreModels);
        
        # Prepare result dictionaries to populate
        resultDicts = [{"ItemsConsidered": i+1} for i in range(maxItems)];
        
        for colScore in scoreCols:
            # Sort by each score column in descending order
            scoreModels.sort(key=lambda model: model[colScore], reverse=True);
            
            nPositiveFound = 0;
            for i in range(maxItems):
                nConsidered = i+1;
                scoreModel = scoreModels[i];
                if scoreModel[colOutcome] == OUTCOME_PRESENT:
                    nPositiveFound += 1;
                
                # Should be able to derive various (accuracy) statistics of interest based on these counts
                contStats = ContingencyStats(nPositiveFound, nConsidered, nPositive, nItems);
                
                # Populate the results based on which metric axes are of interest
                resultDict = resultDicts[i];
                for metric in metricsByScoreCol[colScore]:
                    axisId = str.join(AXIS_DELIM, [metric,colScore]);
                    resultDict[axisId] = contStats[metric];

        return resultDicts;


    def generateFigure(self, resultDicts, summaryData, options=None):
        """Quickly generate an example visualization figure with pylab (matplotlib)
        """
        figureTitle = os.path.splitext(os.path.basename(options.figure))[0];
        if options.title is not None:
            figureTitle = options.title;
        
        rcParams = {"annotation.size": 14}; # Custom parameter not part of matplotlib rc defaults as far as I can tell
        if options.rcParams is not None:
            rcParams.update(json.loads(options.rcParams));
            pylab.rcParams.update(rcParams);
        
        pylab.clf();
        maxItems = len(resultDicts);
        itemsConsideredAxis = columnFromModelList(resultDicts,"ItemsConsidered");
        
        labelIndexes = set();
        if options.labelIndexes is not None:
            labelIndexes.update([int(indexStr) for indexStr in options.labelIndexes.split(VALUE_DELIM)]);
        
        # Data labels
        #   http://stackoverflow.com/questions/22272081/label-python-data-points-on-plot
        axes = pylab.figure().add_subplot(111);

        # Option for differing line styles
        lastMetricScoreCol = (None,None);
        linestyles = ["-","--","-.",":"];
        iLineStyle = 0;
        linestyle = linestyles[iLineStyle];

        # Flag whether data appears to be increasing or decreasing to help guide subsequent legend placement
        isDataIncreasing = None;
        
        # Look into the first item's columns to determine the metrics and axes to plot
        resultKeys = options.axes.split(VALUE_DELIM);
        for iResultKey, resultKey in enumerate(resultKeys):
            if resultKey != "ItemsConsidered":
                (metric,scoreCol) = resultKey.split(AXIS_DELIM);
                if options.cycleLineStyle and metric != lastMetricScoreCol[0]:
                    # New metric, reset the color cycle
                    pylab.gca().set_color_cycle(None);
                    linestyle = linestyles[iLineStyle];
                    iLineStyle = (iLineStyle+1) % len(linestyles);
                
                metricAxis = columnFromModelList(resultDicts, resultKey);
                label = '%s' % (resultKey);
                line = pylab.plot(itemsConsideredAxis, metricAxis, label=label, linestyle=linestyle, linewidth=2)[0];

                # Offset labels to avoid overlap of near values
                offset = (iResultKey % 4) * 2;

                # Add item lables as specified
                for i in labelIndexes:
                    pylab.scatter(itemsConsideredAxis[i], metricAxis[i], color=line.get_color()); # Data points
                    axes.annotate('{:.0%}'.format(metricAxis[i]), xy=(itemsConsideredAxis[i]+offset,metricAxis[i]), xytext=(5,0), textcoords="offset points", color=line.get_color(), size=rcParams['annotation.size']);
        
                # Guide legend placement based on where data lines expected
                isDataIncreasing = (metricAxis[-1] > metricAxis[0]);
                
                lastMetricScoreCol = (metric,scoreCol);
        
        pylab.xlim([1,maxItems]);
        pylab.ylim([0.0,1.05]);
        pylab.grid(True);
        pylab.xlabel('Top K Items Considered');
        pylab.ylabel('Accuracy');
        pylab.title(figureTitle);    
        
        legendLoc = "upper right";
        if isDataIncreasing:
            legendLoc = "upper left";
        pylab.legend(loc=legendLoc, title="Metric:Method");

        if options.figure is None:
            # No file specified, just try to do a direct display
            pylab.show(block=True);
        else:
            pylab.savefig(options.figure);

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <inputFile> [<outputFile>]\n"+\
                    "   <inputFile> Tab-delimited file with columns representing score(s) and labeled outcome(s)\n"+\
                    "   <outputFile> Tab-delimited file with column for number of top items considered up to maxItems and then a column for each axes of interest specified.\n"+\
                    "                       Leave blank or specify \"-\" to send to stdout.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-f", "--figure",  dest="figure",  help="If set, generate an example figure to the named file");
        parser.add_option("-t", "--title",  dest="title",  help="Title caption to apply to generated figure");
        parser.add_option("-r", "--rcParams", dest="rcParams", help="JSON dictionary format string specifying any MatPlotLib RC Params to use when generating figure.  For example: \"{\\\"axes.titlesize\\\":16,\\\"axes.labelsize\\\":16,\\\"legend.fontsize\\\"':16,\\\"figure.figsize\\\":[4,3],\\\"annotation.size\\\":14}\".  For more info, see http://matplotlib.org/users/customizing.html ");
        parser.add_option("-l", "--labelIndexes",  dest="labelIndexes",  help="Comma-separated list of indexes at which to add data-label points to the generated figure");
        parser.add_option("-c", "--cycleLineStyle",  dest="cycleLineStyle",  action="store_true", help="If set, will reuse colors, but vary line-styles for multiple plots.  Default is cycle through colors only.");
        parser.add_option("-m", "--maxItems",  dest="maxItems",  help="If set, maximum number of top items to consider in the accuracy plots");
        parser.add_option("-o", "--colOutcome",  dest="colOutcome", help="Name of column to look for outcome values.");
        parser.add_option("-x", "--axes",  dest="axes", help="Comma-separated list of colon-separated metrics to plot.  For example, recall:score1,precision:score2 will plot recall vs. top items scored by score 1 and precision vs. top items scored by score2.");

        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) > 0:
            summaryData = {"argv": argv};

            inputFilename = args[0];
            inputFile = stdOpen(inputFilename);

            maxItems = int(options.maxItems);
            
            # Parse out the metrics to plot and score columns to sort by
            metricsByScoreCol = dict();
            for metric2scoreStr in options.axes.split(VALUE_DELIM):
                (metric,scoreCol) = metric2scoreStr.split(AXIS_DELIM);
                if scoreCol not in metricsByScoreCol:
                    metricsByScoreCol[scoreCol] = set();
                metricsByScoreCol[scoreCol].add(metric);
            
            # Run the actual analysis
            resultDicts = self(inputFile, options.colOutcome, metricsByScoreCol, maxItems);
            
            # Generate plot figure
            if options.figure is not None:
                self.generateFigure(resultDicts, summaryData, options);

            # Format the results for output
            outputFilename = None;
            if len(args) > 1:
                outputFilename = args[1];
            outputFile = stdOpen(outputFilename,"w");
            
            # Print comment line with arguments to allow for deconstruction later as well as extra results
            print(COMMENT_TAG, json.dumps(summaryData), file=outputFile);
            # Insert a header row
            resultDicts.insert(0, RowItemModel(list(resultDicts[0].keys()),list(resultDicts[0].keys())) );
            
            formatter = TextResultsFormatter( outputFile );
            formatter.formatResultDicts( resultDicts );
        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = AccuracyPerTopItems();
    instance.main(sys.argv);
