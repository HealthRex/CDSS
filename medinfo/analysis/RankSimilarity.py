#!/usr/bin/env python
"""
Given two score files, report similarity score between the rank ordering defined in each file.

"""

import sys, os;
import os.path;
import time;
import json;
from optparse import OptionParser
from cStringIO import StringIO;
from medinfo.db.Model import columnFromModelList;
from medinfo.common.Const import COMMENT_TAG, VALUE_DELIM;
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.db.Model import RowItemModel;
from medinfo.db.Model import RowItemFieldComparator, columnFromModelList;
from Util import log;

from BaseAnalysis import BaseAnalysis;

class ComparisonOptions:
    """Simple struct to store data"""
    def __init__(self):
        self.idCol1 = None;
        self.idCol2 = None;
        self.scoreCol1 = None;
        self.scoreCol2 = None;
        self.descSort1 = False;
        self.descSort2 = False;
    
    def loadFromOptionAttributes(options):
        self.idCol1 = options.idCol1;
        self.idCol2 = options.idCol2;
        self.scoreCol1 = options.scoreCol1;
        self.scoreCol2 = options.scoreCol2;
        self.descSort1 = options.descSort1;
        self.descSort2 = options.descSort2;

class RankSimilarity(BaseAnalysis):
    def __init__(self):
        BaseAnalysis.__init__(self);

    def __call__(self, inputFile1, inputFile2, options):
        # Parse out the files into score models for each row
        scoreModels1 = self.parseScoreModelsFromFile(inputFile1, scoreCols=[options.scoreCol1]);
        scoreModels2 = self.parseScoreModelsFromFile(inputFile2, scoreCols=[options.scoreCol2]);
        
        # Sort the results by the specified score column and sort order
        scoreModels1.sort( RowItemFieldComparator(options.scoreCol1, options.descSort1) );
        scoreModels2.sort( RowItemFieldComparator(options.scoreCol2, options.descSort2) );
        
        # Pull out the sorted list of key items for each
        itemList1 = columnFromModelList( scoreModels1, options.idCol1 );
        itemList2 = columnFromModelList( scoreModels2, options.idCol2 );

        # Calculate available ranked list similarity measures
        resultDict = dict();
        resultDict["RBO"] = self.calcRBO( itemList1, itemList2 );
        self.populateQueryCounts(scoreModels1, scoreModels2, resultDict);
        
        return resultDict;

    def populateQueryCounts(self, scoreModels1, scoreModels2, resultDict):
        """Pull out the number of query items available for each set of data.
        Just hard code this in for now, can make a general column extraction option later.
        """
        resultDict["nA1"] = scoreModels1[0]["nA"];
        resultDict["nA2"] = scoreModels2[0]["nA"];
    
    def calcRBO(self, l1, l2, p=0.98):
        """
        # Downloaded from work referenced below:
        #
        # @author: Ritesh Agrawal
        # @Date: 13 Feb 2013
        # @Description: This is an implementation of rank biased overlap score 
        # (Refererence: http://www.umiacs.umd.edu/~wew/papers/wmz10_tois.pdf). 
        # This is a modified implementation of  https://github.com/maslinych/linis-scripts/blob/master/rbo_calc.py
        # It is a linear implementation of the RBO and assumes there are no
        # duplicates and doesn't handle for ties. 
        #
        Calculates Ranked Biased Overlap (RBO) score. 
        l1 -- Ranked List 1
        l2 -- Ranked List 2
        """
        if l1 == None: l1 = []
        if l2 == None: l2 = []

        sl,ll = sorted([(len(l1), l1),(len(l2),l2)])
        s, S = sl
        l, L = ll
        if s == 0: return 0

        # Calculate the overlaps at ranks 1 through l 
        # (the longer of the two lists)
        ss = set([]) # contains elements from the smaller list till depth i
        ls = set([]) # contains elements from the longer list till depth i
        x_d = {0: 0}
        sum1 = 0.0
        for i in range(l):
            x = L[i]
            y = S[i] if i < s else None
            d = i + 1

            # if two elements are same then 
            # we don't need to add to either of the set
            if x == y: 
                x_d[d] = x_d[d-1] + 1.0
            # else add items to respective list
            # and calculate overlap
            else: 
                ls.add(x) 
                if y != None: ss.add(y)
                x_d[d] = x_d[d-1] + (1.0 if x in ss else 0.0) + (1.0 if y in ls else 0.0)     
            #calculate average overlap
            sum1 += x_d[d]/d * pow(p, d)

        sum2 = 0.0
        for i in range(l-s):
            d = s+i+1
            sum2 += x_d[d]*(d-s)/(d*s)*pow(p,d)

        sum3 = ((x_d[l]-x_d[s])/l+x_d[s]/s)*pow(p,l)

        # Equation 32
        rbo_ext = (1-p)/p*(sum1+sum2)+sum3
        return rbo_ext

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <inputFile1> <inputFile2> [<outputFile>]\n"+\
                    "   <inputFile1> Tab-delimited file with columns representing score(s) and item IDs / labels\n"+\
                    "   <inputFile2> Tab-delimited file with columns representing score(s) and item IDs / labels\n"+\
                    "   <outputFile> Tab-delimited file with columns to specify parameters and labeled rank similarity scores.\n"+\
                    "                       Leave blank or specify \"-\" to send to stdout.\n"+\
                    " (See scripts/CDSS/rankSimilarity.py helper script to organize results of multiple queries)\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-i", "--idCol1",  dest="idCol1",  help="Name of item ID column in input file 1 to join against the other input file.");
        parser.add_option("-I", "--idCol2",  dest="idCol2",  help="Name of item ID column in input file 1 to join against the other input file.");
        
        parser.add_option("-s", "--scoreCol1",  dest="scoreCol1",  help="Name of score column in input file 1 to sort items by, defining their rank order.");
        parser.add_option("-d", "--descSort1",  dest="descSort1",  action="store_true", help="If set, will sort input 1 by scoreCol1 in *descending* order.  (Important because ranking measures prioritize value of top ranks.)");

        parser.add_option("-S", "--scoreCol2",  dest="scoreCol2",  help="Name of score column in input file 2 to sort items by, defining their rank order.");
        parser.add_option("-D", "--descSort2",  dest="descSort2",  action="store_true", help="If set, will sort input 2 by scoreCol2 in *descending* order.  (Important because ranking measures prioritize value of top ranks.)");

        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) > 0:
            summaryData = {"argv": argv};

            inputFile1 = stdOpen(args[0]);
            inputFile2 = stdOpen(args[1]);

            # Run the actual analysis
            resultDict = self(inputFile1, inputFile2, options);
            
            # Format the results for output
            outputFilename = None;
            if len(args) > 2:
                outputFilename = args[2];
            outputFile = stdOpen(outputFilename,"w");
            
            # Print comment line with arguments to allow for deconstruction later as well as extra results
            print >> outputFile, COMMENT_TAG, json.dumps(summaryData);
            formatter = TextResultsFormatter( outputFile );
            # Insert a header row
            headerCols = resultDict.keys();
            formatter.formatResultDict( RowItemModel(resultDict.keys(),resultDict.keys()), headerCols );
            formatter.formatResultDict( resultDict, headerCols );
        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = RankSimilarity();
    instance.main(sys.argv);
