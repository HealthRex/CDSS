#!/usr/bin/env python
"""
Translate results of OutcomePredictionAnalysis into data for a
Receiver Operating Characteristic plot.
"""

import sys, os;
import os.path;
import time;
import math;
import json;
from optparse import OptionParser
from cStringIO import StringIO;
import numpy as np;
#from sklearn.metrics import roc_curve, auc, roc_auc_score;
#import pylab;
from medinfo.db.Model import columnFromModelList;
from medinfo.common.Const import COMMENT_TAG, VALUE_DELIM;
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.common.StatsUtil import ContingencyStats;
from medinfo.db.ResultsFormatter import TextResultsFormatter;
from medinfo.db.Model import RowItemModel;
from Util import log;

from BaseAnalysis import BaseAnalysis;

CONFIDENCE_INTERVAL = 0.95;

class ROCPlot(BaseAnalysis):
    """Convenience class to consolidate construction of Receiver Operating Characteristic
    data, figures, and summary statistics.
    """
    # Whether to analyze on the natural log of the score values rather than direct
    logScores = False;

    def __init__(self):
        BaseAnalysis.__init__(self);
        self.logScores = False;

    def __call__(self, inputFile, colOutcome=None, colScore=None, options=None):
        (outcomes, scoresById) = self.parseScoreFile(inputFile, colOutcome=colOutcome, colScore=colScore);
        analysisResultsByScoreId = dict();
        summaryData = dict();
        for scoreId, scores in scoresById.iteritems():
            (rocData, scoreSummaryData) = self.rocCurve( outcomes, scores, scoreId, options );
            (fpr,tpr,thresholds) = rocData;
            analysisResultsByScoreId[scoreId] = [ (afpr,atpr) for (afpr,atpr) in zip(fpr,tpr)];    # Repackage into a list of 2-ples
            summaryData.update(scoreSummaryData);
        self.addContingencyStatistics(summaryData, scoresById, options);     # Add contingency stats now that we have all the summary data calculated
        return (analysisResultsByScoreId, summaryData);

    def rocCurve(self, outcomes, scores, scoreId=None, options=None):
        """Expect data as a list of outcome value encoded as 0 or +1 for negative and positive results
        and a numerical score for each.
        Just use sklearn's roc_curve implementation
        Additionally returns a summaryData dictionary which will report ROC AUC (c-statistic)

        scoreId - Label to apply to summary statistics
        options - If specified, look for attributes like
            nSamples: Repeat with bootstrap sampling to calculate distribution 
                and confidence interval for c-statistics.  Adapted from
                http://stackoverflow.com/questions/19124239/scikit-learn-roc-curve-with-confidence-intervals
            contingencyStats:   IDs of stats to calculate for multiple scores

        """
        from sklearn.metrics import roc_curve, auc, roc_auc_score;

        if scoreId is None: scoreId = "";
        if self.logScores:  # Option to work with log of extreme values to avoid numerical precision problems
            scores = [math.log(score) for score in scores];
        outcomes = np.array(outcomes);
        scores = np.array(scores);
        
        (fpr,tpr,thresholds) = roc_curve(outcomes,scores);
        fpr = list(fpr);
        tpr = list(tpr);
        rocData = (fpr,tpr,thresholds);
        
        #cStat = roc_auc_score(outcomes,scores);
        # Calculate out components of AUC c-statistic to derive actual value.
        #   Report component values as well to infer binomial distribution statistics,
        #   which can be used to compare the AUC results of two different methods e.g., by chi-square analysis or Fisher exact test
        (pairsCorrect, pairsChecked) = self.aucComponents(outcomes, scores);
        cStat = pairsCorrect / pairsChecked;
        summaryData = \
            {   "%s.ROC-AUC" % scoreId: cStat, 
                "%s.c-statistic" % scoreId: cStat,
                "%s.pairsCorrect" % scoreId: pairsCorrect,
                "%s.pairsChecked" % scoreId: pairsChecked,
            };
        
        if options is not None and options.nSamples is not None:
            nSamples = int(options.nSamples);
            bootstrapCStats = list();
            rng = np.random.RandomState(nSamples);  # For consistency of results, seed random number generator with fixed number
            for i in range(nSamples):
                # bootstrap by sampling with replacement on the prediction indices
                indices = rng.random_integers(0, len(scores) - 1, len(scores));
                if len(np.unique(outcomes[indices])) < 2:
                    # We need at least one positive and one negative sample for ROC AUC
                    # to be defined: reject the sample
                    continue

                cStat = roc_auc_score(outcomes[indices], scores[indices]);
                bootstrapCStats.append(cStat);

            # Record results to summary data
            #summaryData["bootstrapCStats"] = bootstrapCStats;
            ciFractionLow = (1.0-CONFIDENCE_INTERVAL)/2;
            ciFractionHigh = CONFIDENCE_INTERVAL+ciFractionLow;
            bootstrapCStats.sort();
            nBootstraps = len(bootstrapCStats);  # May not be equal to nSamples if some samples were rejected
            summaryData["%s.ROC-AUC-%s-CI" % (scoreId,CONFIDENCE_INTERVAL)] = (bootstrapCStats[int(ciFractionLow*nBootstraps)], bootstrapCStats[int(ciFractionHigh*nBootstraps)]);
        return (rocData , summaryData);

    def aucComponents(outcomes, scores):
        """Calculate out components of AUC c-statistic to derive actual value.
        Assumes outcomes are coded as 0 or 1 for negative and positive and that scores should be higher when predicting positive cases.
        Returns tuple (pairsCorrect, pairsChecked), then the AUC score is pairsChecked / pairsChecked.
        
        Based on the interpretation of taking any pair of a positive and negative example, the AUC
        reports the probability that the score appropriately ranks the positive example higher than the negative example.
        For cases where the scores are equal, pairs are scored 0.5 correct.

        Note that while could just calculate the ROC AUC with sklearn.metrics.roc_auc_score, we may wish to 
        report frequency components to infer binomial distribution statistics.
        These can be used to compare the AUC results of two different methods e.g., by chi-square analysis or Fisher exact test
        to yield a p-value comparing AUC results.
        
        For example,
            Scoring method A yields  80 pairsCorrect out of 100 pairsChecked
            Scoring method B yields 140 pairsCorrect out of 200 pairsChecked
            
        Setup a 2x2 contingency table to determine whether there is independence in the rate of correct pairs depending on the scoring method.
        ct = [  [80, 100-80],
                [140, 200-140],
             ];
        
        pChi2 = scipy.stats.chi_contingency(ct, correction=False)[1];   # 0.0648
        pYatesChi2 = scipy.stats.chi_contingency(ct, correction=True)[1];   # 0.0877
        pFisher = scipy.stats.fisher_exact(ct)[1];  # 0.0725
        """
        pairsCorrect = 0.0;
        pairsChecked = 0;
        
        for (outcome0,score0) in zip(outcomes,scores):
            if outcome0 == 0:    # Negative example
                for (outcome1,score1) in zip(outcomes,scores):
                    if outcome1 != 0:   # Positive example
                        pairsChecked += 1;
                        if score1 > score0:
                            pairsCorrect += 1;
                        elif score1 == score0:
                            pairsCorrect += 0.5;
        
        return (pairsCorrect, pairsChecked);
    aucComponents = staticmethod(aucComponents);

    def aucScore(outcomes, scores):
        """Calculate ROC AUC score.  Use internal functions to remove library dependencies as necessary, 
        but much slower implementation.
        Otherwise performs same function as sklearn.metrics.roc_auc_score;
        """
        auc = None;
        try:
            from sklearn.metrics import roc_auc_score;
            auc = roc_auc_score(outcomes,scores);
        except Exception:
            comp = ROCPlot.aucComponents(outcomes,scores);
            if comp[1] > 0:
                auc = (comp[0]/comp[1]);
        return auc;
    aucScore = staticmethod(aucScore);
    
    def addContingencyStatistics(self, summaryData, scoresById, options):
        """Add contingency stats now that we have all the summary data calculated"""
        if options.baseScoreCol is not None:
            basePairsCorrect = summaryData["%s.pairsCorrect" % options.baseScoreCol];
            basePairsChecked = summaryData["%s.pairsChecked" % options.baseScoreCol];
        
            statIds = options.contingencyStats.split(VALUE_DELIM);

            for scoreId in scoresById.iterkeys():
                pairsCorrect = summaryData["%s.pairsCorrect" % scoreId];
                pairsChecked = summaryData["%s.pairsChecked" % scoreId];
                contStats = ContingencyStats( pairsCorrect, pairsChecked, pairsCorrect+basePairsCorrect, pairsChecked+basePairsChecked );
                for statId in statIds:
                    dataKey = "%s.%s.%s" % (scoreId, statId, options.baseScoreCol);
                    summaryData[dataKey] = contStats[statId];

    def generateFigure(self, analysisResultsByScoreId, summaryData, figureFilename=None, figureTitle=None, rcParams=None, colScoreStr=None):
        """Quickly generate an example visualization figure with pylab (matplotlib)
        """
        import pylab;   # Only import dependencies as needed
        
        if figureTitle is None: # Default to name of generated file
            figureTitle = os.path.basename(figureFilename)

        if rcParams is not None:
            pylab.rcParams.update(rcParams);
        
        scoreIds = analysisResultsByScoreId.keys();
        if colScoreStr is not None:
            # Use pre-specified order of columns, otherwise subject to erratic dictionary key ordering
            scoreIds = colScoreStr.split(VALUE_DELIM);
        
        pylab.clf();
        for scoreId in scoreIds:
            analysisResults = analysisResultsByScoreId[scoreId];
            fpr = [afpr for (afpr,atpr) in analysisResults];
            tpr = [atpr for (afpr,atpr) in analysisResults];
            cStat = summaryData["%s.c-statistic" % scoreId];

            label = '%0.2f' % (cStat);
            ciKey = "%s.ROC-AUC-%s-CI" % (scoreId, CONFIDENCE_INTERVAL)
            if ciKey in summaryData:
                rocAUCCI = summaryData[ciKey];
                label += " (%0.2f, %0.2f)" % (rocAUCCI[0], rocAUCCI[-1],  );
            label += " %s" % scoreId;

            pylab.plot(fpr,tpr, label=label, linewidth=2);
            #pylab.scatter(fpr,tpr); # Data point labels

        pylab.plot([0,1],[0,1], 'k--');
        pylab.xlim([0.0,1.0]);
        pylab.ylim([0.0,1.0]);
        pylab.xlabel('False Positive Rate = 1-Specificity');
        pylab.ylabel('True Positive Rate = Sensitivity');
        pylab.title(figureTitle);
        pylab.legend(loc="lower right", title="ROC c-Statistic (%d%% CI) Method" % (CONFIDENCE_INTERVAL*100),);
        
        if figureFilename is None:
            # No file specified, just try to do a direct display
            pylab.show(block=True);
        else:
            pylab.savefig(figureFilename);

    def analysisHeaders(self, analysisResultsByScoreId):
        headers = list();
        for scoreId in analysisResultsByScoreId:
           headers.extend( ("%s.FPR" % scoreId, "%s.TPR" % scoreId) );
        return headers;

    def formatAnalysisTable(self, analysisResultsByScoreId):
        # Organize results by scoreId into a single table.  Some columns will not be as long as others, so fill with None values
        nScores = len(analysisResultsByScoreId);
        maxNResults = 0;
        for iScore, (scoreId, analysisResults) in enumerate(analysisResultsByScoreId.iteritems()):
            analysisResults = analysisResultsByScoreId[scoreId];
            maxNResults = max(maxNResults, len(analysisResults));
        # Prepopulate table space
        #outputTable = [[None]*(nScores*2)] * maxNResults;    # This does not work directly, for some reason causes multi-row assignment when try to set individual cell values
        outputTable = [[None]*(nScores*2) for iResult in xrange(maxNResults)];

        for iScore, (scoreId, analysisResults) in enumerate(analysisResultsByScoreId.iteritems()):
            analysisResults = analysisResultsByScoreId[scoreId];
            for iResult, (fpr,tpr) in enumerate(analysisResults):
                outputTable[iResult][iScore*2] = fpr;
                outputTable[iResult][iScore*2+1] = tpr;

        colNames = self.analysisHeaders(analysisResultsByScoreId);
        outputTable.insert(0,colNames);    # Insert a mock record to get a header / label row
        return outputTable;
    
    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <inputFile> [<outputFile>]\n"+\
                    "   <inputFile> Tab-delimited file, first two labeled columns expected to represent labeled outcome (0 and non-zero) and score/probability of outcome\n"+\
                    "   <outputFile>    Tab-delimited table specifying TPR (sensitivity) and FPR (1-specificity) for components of a ROC plot.  Comment / header line will be a JSON parseable dictionary of additional summary stats, including the ROC AUC.\n"+\
                    "                       Leave blank or specify \"-\" to send to stdout.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-f", "--figure",  dest="figure",  help="If set, will also try to auto-generate an example figure and store to a file here");
        parser.add_option("-t", "--title",  dest="title",  help="Title caption to apply to generated figure");
        parser.add_option("-r", "--rcParams", dest="rcParams", help="JSON dictionary format string specifying any MatPlotLib RC Params to use when generating figure.  For example: \"{\\\"axes.titlesize\\\":20,'legend.fontsize':20}\".  For more info, see http://matplotlib.org/users/customizing.html ");
        parser.add_option("-n", "--nSamples",  dest="nSamples",  help="If set, bootstrap this many samples of data to calculate multiple ROC AUC c-statistics to produce a distribution and confidence interval");
        parser.add_option("-b", "--baseScoreCol", dest="baseScoreCol", help="Name of the base scoring method against which to compare all others when calculating contingency statistics as below.");
        parser.add_option("-c", "--contingencyStats", dest="contingencyStats", help="Comma-separated list of contingency stat IDs (see medinfo.common.StatsUtil.ContingencyStats) to calculate for different scoring methods against the specified base scoring method.  For example, 'P-Fisher,P-YatesChi2'");
        parser.add_option("-l", "--logScores",  dest="logScores", action="store_true",  help="If set, will do analysis on the natural log / ln of the scores, which can help accomodate extremely large or small scores that disrupt result with loss of numerical precision");
        parser.add_option("-o", "--colOutcome",  dest="colOutcome", help="Index of column to expect outcome values in.  Defaults to 0.  Can specify a string to identify a column header.");
        parser.add_option("-s", "--colScore",  dest="colScore", help="Index of column to expect score values in.  Defaults to 1.  Can specify strings and comma-separated lists to plot multiple curves.");

        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) > 1:
            inputFilename = args[0];
            inputFile = stdOpen(inputFilename);

            self.logScores = options.logScores;
            
            # Run the actual analysis
            (analysisResultsByScoreId, summaryData) = self(inputFile, options.colOutcome, options.colScore, options);
            
            # Generate plot figure
            if options.figure is not None:
                rcParams = None;
                if options.rcParams is not None:
                    rcParams = json.loads(options.rcParams);
                self.generateFigure(analysisResultsByScoreId, summaryData, options.figure, options.title, rcParams, options.colScore );

            # Format the results for output
            outputFilename = None;
            if len(args) > 1:
                outputFilename = args[1];
            outputFile = stdOpen(outputFilename,"w");
            
            # Print comment line with arguments to allow for deconstruction later as well as extra results
            summaryData["argv"] = argv;
            print >> outputFile, COMMENT_TAG, json.dumps(summaryData);

            outputTable = self.formatAnalysisTable(analysisResultsByScoreId);
            
            formatter = TextResultsFormatter( outputFile );
            formatter.formatResultSet( outputTable );
        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = ROCPlot();
    instance.main(sys.argv);
