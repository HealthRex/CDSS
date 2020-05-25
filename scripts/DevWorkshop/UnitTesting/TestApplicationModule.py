#!/usr/bin/env python
"""Test case for respective module in application package

!!!! This is test demonstration code that goes with the TestFirstDev workshop.
!!!! There are supposed to be bugs in the code. 
!!!! Do NOT commit the fixes back into the code repository.
!!!! The point is to allow new people to encounter, identify, and debug them.
"""

import sys, os
from io import StringIO
import unittest

from ApplicationModule import ApplicationClass;

RUNNER_VERBOSITY=2; # How much log text you want the test runner to express

TEMP_FILENAME = "tempData.TestApplicationModule.txt";
SAMPLE_INPUT_FILE_STR = \
"""To be, or not to be, Ay there's the point,
To Die, to sleep, is that all? Aye all:
No to sleep, to dream, aye marry there it goes,
For in that dream of death, when we awake,
"""

class TestApplicationModule(unittest.TestCase):
    def setUp(self):
        """Prepare state for test cases.
        For example, preparing test input files, database connections and sample data.
        """
        unittest.TestCase.setUp(self);  # Superclass setUp
        
        # Instance to test on
        self.app = ApplicationClass();

        # Sample input lines.
        # Can convert into a "file" by wrapping a StringIO object around it, 
        #   but will illustrate creating temp file here
        self.tempFile = open(TEMP_FILENAME,"w");
        self.tempFile.write(SAMPLE_INPUT_FILE_STR);
        self.tempFile.close();

    def tearDown(self):
        """Restore state from any setUp or test steps.
        For example, deleting any temp files or temp data records in the database.
        """
        if os.path.exists(TEMP_FILENAME):
            os.remove(TEMP_FILENAME);
        unittest.TestCase.tearDown(self);   # Superclass tearDown

    def test_extractWordsByIndex(self):
        # Prepare sample input into application code and respective expected output
        wordIndex = 1;
        inputFile = open(TEMP_FILENAME);
        expectedOutputList = ["To","To","No","For"];
        
        # Run application code against sample input, and collect output
        outputFile = StringIO();    # Empty IO object can write to like a file, but will just save as an in memory string
        self.app.extractWordsByIndex(wordIndex, inputFile, outputFile);
        inputFile.close();
        # Extract the sample results and verify they match the expected results
        actualOutputFileStr = outputFile.getvalue();
        actualOutputList = actualOutputFileStr[:-1].split("\n"); # Get one value per line, ignoring the ending newline
        self.assertEqual(expectedOutputList, actualOutputList);


        ######## More test iterations ########
        # Prepare sample input into application code and respective expected output
        wordIndex = 3;
        inputFile = open(TEMP_FILENAME);
        expectedOutputList = ["or","to","sleep","that"];
        
        # Run application code against sample input, and collect output
        outputFile = StringIO();
        self.app.extractWordsByIndex(wordIndex, inputFile, outputFile);
        inputFile.close();
        # Extract the sample results and verify they match the expected results
        actualOutputFileStr = outputFile.getvalue();
        actualOutputList = actualOutputFileStr[:-1].split("\n"); # Get one value per line, ignoring the ending newline
        self.assertEqual(expectedOutputList, actualOutputList);



        ######## More test iterations ########
        # Prepare sample input into application code and respective expected output
        wordIndex = 10;
        inputFile = open(TEMP_FILENAME);
        expectedOutputList = ["point","","goes",""];

        # Run application code against sample input, and collect output
        outputFile = StringIO();
        self.app.extractWordsByIndex(wordIndex, inputFile, outputFile);
        inputFile.close();
        # Extract the sample results and verify they match the expected results
        actualOutputFileStr = outputFile.getvalue();
        actualOutputList = actualOutputFileStr[:-1].split("\n"); # Get one value per line, ignoring the ending newline
        self.assertEqual(expectedOutputList, actualOutputList);


        ######## More test iterations ########
        # Prepare sample input into application code, but this time expect an Error
        wordIndex = 1.2;    # Invalid index. Must be an integer
        inputFile = open(TEMP_FILENAME);
        
        # Run application code against sample input, and collect output
        expectError = True;
        actualError = False;
        try:
            outputFile = StringIO();
            self.app.extractWordsByIndex(wordIndex, inputFile, outputFile);
        except TypeError:   # Look for a specific "TypeError" because provided a floating point type instead of an integer type value
            actualError = True;
        inputFile.close();
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
