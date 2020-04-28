#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from io import StringIO
import unittest

from .ApplicationModule import ApplicationClass;

RUNNER_VERBOSITY=2; # How much log text you want the test runner to express

class TestApplicationModule(unittest.TestCase):
    def setUp(self):
        """Prepare state for test cases.
        For example, preparing test input files, database connections and sample data.
        """
        unittest.TestCase.setUp(self);
        
        # Instance to test on
        self.app = ApplicationClass();

        # Sample input file string. Convert into a "file" format by wrapping a StringIO object around it
        self.SAMPLE_INPUT_FILE_STR = \
        """To be, or not to be, Ay there's the point,
To Die, to sleep, is that all? Aye all:
No to sleep, to dream, aye marry there it goes,
For in that dream of death, when we awake,
"""
    def tearDown(self):
        """Restore state from any setUp or test steps.
        For example, deleting any temp files or temp data records in the database.
        """
        unittest.TestCase.tearDown(self);

    def test_extractWordsByIndex(self):
        # Prepare sample input into application code
        wordIndex = 0;
        inputFile = StringIO(self.SAMPLE_INPUT_FILE_STR);
        outputFile = StringIO();    # Empty IO object can write to like a file, but will just save as an in memory string
        
        # Run application code against sample input, and collect output
        self.app.extractWordsByIndex(wordIndex, inputFile, outputFile);
        actualOutputFileStr = outputFile.getvalue();
        actualOutputList = actualOutputFileStr[:-1].split("\n"); # Get one value per line, ignoring the ending newline
        
        # Define expected output of a successful application run, and verify the actual results match
        expectedOutputList = ["To","To","No","For"];
        self.assertEqual(expectedOutputList, actualOutputList);



        ######## More test iterations ########
        # Prepare sample input into application code
        wordIndex = 2;
        inputFile = StringIO(self.SAMPLE_INPUT_FILE_STR);
        outputFile = StringIO();    # Empty IO object can write to like a file, but will just save as an in memory string
        
        # Run application code against sample input, and collect output
        self.app.extractWordsByIndex(wordIndex, inputFile, outputFile);
        actualOutputFileStr = outputFile.getvalue();
        actualOutputList = actualOutputFileStr[:-1].split("\n"); # Get one value per line, ignoring the ending newline
        
        # Define expected output of a successful application run, and verify the actual results match
        expectedOutputList = ["or","to","sleep","that"];
        self.assertEqual(expectedOutputList, actualOutputList);



        ######## More test iterations ########
        # Prepare sample input into application code
        wordIndex = 9;
        inputFile = StringIO(self.SAMPLE_INPUT_FILE_STR);
        outputFile = StringIO();    # Empty IO object can write to like a file, but will just save as an in memory string
        
        # Run application code against sample input, and collect output
        self.app.extractWordsByIndex(wordIndex, inputFile, outputFile);
        actualOutputFileStr = outputFile.getvalue();
        actualOutputList = actualOutputFileStr[:-1].split("\n"); # Get one value per line, ignoring the ending newline
        
        # Define expected output of a successful application run, and verify the actual results match
        expectedOutputList = ["point","","goes",""];
        self.assertEqual(expectedOutputList, actualOutputList);



        ######## More test iterations ########
        # Prepare sample input into application code
        wordIndex = 1.2;    # Invalid index. Must be an integer
        inputFile = StringIO(self.SAMPLE_INPUT_FILE_STR);
        outputFile = StringIO();    # Empty IO object can write to like a file, but will just save as an in memory string
        
        # Run application code against sample input, and collect output
        expectError = True;
        actualError = False;
        try:
            self.app.extractWordsByIndex(wordIndex, inputFile, outputFile);
            actualOutputFileStr = outputFile.getvalue();
            actualOutputList = actualOutputFileStr[:-1].split("\n"); # Get one value per line, ignoring the ending newline
        except TypeError:
            actualError = True;
        # In this case, expect an error to have occurred (invalid wordIndex)
        self.assertEqual(expectError, actualError);

    #def test_fibonacci(self):
    #    # Do something here???
    #    raise NotImplementedError("Needs to be added");

def suite():
    suite = unittest.TestSuite();
    # Automatically looks for any method whose name starts with "test" and assumes it is a test case
    suite.addTest(unittest.makeSuite(TestApplicationModule));   

    # Alternatively, you can itemize individual functions to test
    #suite.addTest(TestApplicationModule('test_extractWordsByIndex'));
    #suite.addTest(TestApplicationModule('test_fibonacci'));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
