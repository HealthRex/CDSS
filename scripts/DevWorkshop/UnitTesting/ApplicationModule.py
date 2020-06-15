#!/usr/bin/env python
"""
Application module to perform example calculation and data manipulation functions.

!!!! This is test demonstration code that goes with the TestFirstDev workshop.
!!!! There are supposed to be bugs in the code. 
!!!! Do NOT commit the fixes back into the code repository.
!!!! The point is to allow new people to encounter, identify, and debug them.
"""

import sys, os;
import time;
import json;
from optparse import OptionParser
import re;
import string;

COMMENT_TAG = "#";

class ApplicationClass:
    def extractWordsByIndex(self, wordIndex, inputFile, outputFile):
        """Look through each line of the input file
        and output a respective line in the output file 
        containing the k-th word of each input line (k=wordIndex).
        If there is no k-th word, then output an empty string.
        For example, if k=2 and a line of text is "This is an example line", 
        the function should identify the SECOND word of the line: "is".
        """
        k = wordIndex;
        for line in inputFile:
            words = line.split(); # Breakup up the line of text into words separated by whitespace
            selectedWord = "";  # Default to empty string if cannot find a word
            if k < len(words):
                selectedWord = words[k];
            print(selectedWord, file=outputFile);

    def fibonacci(self, n):
        """Simple function to output the n-th Fibonacci number.

        # Fibonacci example
        # Fib(n) = Fib(n-1) + Fib(n-2)
        # Fib(1) = Fib(2) = 1
        #
        #   n       1   2   3   4   5   6   7   8   9   10
        #   Fib(n)  1   1   2   3   5   8   13  21  34  55
        """
        raise NotImplementedError();    # Function not completed yet, stub needs to be implemented

    def main(self, argv):
        """Main method, deigned to parse command-line arguments"""
        usageStr =  "usage: %prog [options] <inputFile> <outputFile>\n"+\
                    "   <inputFile>    Input file to process.\n"+\
                    "   <ouputFile>    Result file to generate.\n"
        parser = OptionParser(usage=usageStr)
        parser.add_option("-w", "--wordIndex",  dest="wordIndex", help="If set wordIndex=k, then look for and output the k-th word of each input line. If there is no k-th word, then output an empty string.");
        parser.add_option("-f", "--fibonacci",  dest="fibonacci", help="If a value is provided, interpret as n, and print out the n-th Fibonacci number to stdout. Fib(n) = Fib(n-1) + Fib(n-2), Fib(<=2) = 1.");
        (options, args) = parser.parse_args(argv[1:])

        print("Starting: "+str.join(" ", argv), file=sys.stderr);
        timer = time.time();
        if options.wordIndex and len(args) > 1:
            # Parse out command-line arguments
            wordIndex = int(options.wordIndex);
            inputFile = open(args[0]);
            outputFile = open(args[1],"w");
            
            # Print comment line with arguments to allow for deconstruction later as well as extra results
            summaryData = {"argv": argv};
            print(COMMENT_TAG, json.dumps(summaryData), file=outputFile);

            # Run application code to process input and send results to output
            self.extractWordsByIndex(wordIndex, inputFile, outputFile);
        
        elif options.fibonacci:
            n = int(options.fibonacci);
            fibonacciResult = self.fibonacci(n);
            print(fibonacciResult);
        
        else:
            parser.print_help()
            sys.exit(-1)

        timer = time.time() - timer;
        print("%.3f seconds to complete" % timer, file=sys.stderr);

if __name__ == "__main__":
    # Python boilerplate to run the code below if run directly from the commandline
    # In this case, just create an instance of the ApplicationClass and run it's "main" method
    instance = ApplicationClass();
    instance.main(sys.argv);
