#!/usr/bin/env python
"""
Application module to perform some calculation or data manipulation functions.
"""

import sys, os;
import time;
import json;
from optparse import OptionParser
from cStringIO import StringIO;

from medinfo.common.Util import stdOpen, log;
from medinfo.common.Const import COMMENT_TAG;

class ApplicationClass:
    def extractWordsByIndex(self, wordIndex, inputFile, outputFile):
        """Look through each line of the input file
        and output a respective line in the output file containing the k-th word of each input line (k=wordIndex).
        If there is no k-th word, then output an empty string.
        """
        k = wordIndex;
        for line in inputFile:
            words = line.split();
            selectedWord = "";  # Default to empty string if cannot find a word
            if k < len(words):
                selectedWord = words[k];
            print >> outputFile, selectedWord;

    #def fibonacciExample(???):
        """
        # Fibonacci example
        # Fib(n) = Fib(n-1) + Fib(n-2)
        # Fib(1) = Fib(2) = 1
        #
        #   n       1   2   3   4   5   6   7   8   9   10
        #   Fib(n)  1   1   2   3   5   8   13  21  34  55
        """

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options] <inputFile> <outputFile>\n"+\
                    "   <inputFile>    Input file to process. Specify \"-\" to read from stdin.\n"+\
                    "   <ouputFile>    Result file to generate.  Specify \"-\" to send to stdout.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-w", "--wordIndex",  dest="wordIndex", help="If set wordIndex=k, then look for and output the k-th word of each input line. If there is no k-th word, then output an empty string.");
        parser.add_option("-f", "--fibonacci",  dest="fibonacci", action="store_true", help="If set, count up the number of words in each line of the input file and output it back, along with the Fibonacci number for that number. (e.g., Fib(n) = Fib(n-1) + Fib(n-2) and Fib(1) = 1.");
        parser.add_option("-c", "--cooccurrence",  dest="cooccurrence", action="store_true", help="If set, count up the number of lines in the input file that each word and each co-occuring word pair occurs in.");
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        if len(args) > 1:
            inputFile = stdOpen(args[0]);
            outputFile = stdOpen(args[1],"w");
            
            # Print comment line with arguments to allow for deconstruction later as well as extra results
            summaryData = {"argv": argv};
            print >> outputFile, COMMENT_TAG, json.dumps(summaryData);

            if options.wordIndex:
                wordIndex = int(options.wordIndex);
                self.extractWordsByIndex(wordIndex, inputFile, outputFile);
            if options.fibonacci:
                # Do something...???
                pass;
            if options.cooccurrence:
                # Do something...???
                pass;

        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = ApplicationClass();
    instance.main(sys.argv);
