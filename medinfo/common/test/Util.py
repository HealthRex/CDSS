from . import Const
import sys, os
import math
import logging
import cgi
from collections import UserDict
import unittest
import re;
import json;

import medinfo.common.Util;
from medinfo.common.Const import COMMENT_TAG, NULL_STRING;
from medinfo.db.Model import SQLQuery, RowItemModel;


log = logging.getLogger("CDSS")

handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(Const.LOGGER_FORMAT)

handler.setFormatter(formatter)
# log.addHandler(handler)

# Suppress uninteresting application output
medinfo.common.Util.log.setLevel(Const.APP_LOGGER_LEVEL)

class MedInfoTestCase(unittest.TestCase):
    """Common base class for TestCase classes to add some extra functionality
    """
    def setUp(self):
        """Prep for test case.  Subclass must call this parent method to actually use it.
        """
        unittest.TestCase.setUp(self)

        # Allow free overriding of standard IO, but retain links to original
        self.origStdin  = sys.stdin
        self.origStdout = sys.stdout
        self.origArgv   = sys.argv

        try:
            # Add safety check for DB access during test case
            #   Should use MedInfo.DB.test.Util.DBTestCase instead to redirect DB queries
            #   to avoid potentially running a test case against a "real" production DB
            import medinfo.db.Env;
            medinfo.db.Env.DB_PARAM["HOST"] = "Test_cases_that_include_DB_access_should_inherit_from_MedInfo.DB.test.Util.DBTestCase_for_safety_against_accidentally_overriding_real_DB_data";
        except Exception as exc:
            log.info("No medinfo.db package found.  Not necessary if no DB access planned for testing");

    def tearDown(self):
        """Restore state after test finishes.  Subclass must call this parent method to actually use it.
        """
        unittest.TestCase.tearDown(self)

        sys.stdin   = self.origStdin
        sys.stdout  = self.origStdout
        sys.argv    = self.origArgv

    def assertEqualGeneral( self, verifyValue, sampleValue, precision ):
        """If the verifyValue is a number (float or int) try to convert the sampleValue into
        something more comparable.  If it is a float, use the precision value to do
        an assertAlmostEqual, but revised to not look for decimal places, but significant digits instead.
        In particular, take the ratio of the diff of the values compared to the verify value,
        and see if the fraction is better than 1/10^precision.
        """
        # Check if either is a NoneType before trying to do type conversions
        if verifyValue is None or sampleValue is None:
            return self.assertEqual( verifyValue, sampleValue );

        # First convert the sample value to whatever type the verify value is
        verifyType = type(verifyValue);
        origSample  = sampleValue;
        sampleValue = verifyType(sampleValue);

        if isinstance(verifyValue, bool) and isinstance(origSample, str):
            # If original sample value was a string, need to be more specific about conversion
            # Count as true if first letter of string starts with 't'
            sampleValue = origSample.lower().startswith( str(True)[0].lower() );

        if isinstance(verifyValue, float):
            #print >> sys.stderr, verifyValue;
            #print >> sys.stderr, verifyValue * 10**precision;
            #print >> sys.stderr, sampleValue;
            #print >> sys.stderr, (verifyValue-sampleValue);
            #print >> sys.stderr, (verifyValue-sampleValue)/verifyValue;
            #print >> sys.stderr, abs((verifyValue-sampleValue)/verifyValue) * 10**precision;

            if verifyValue == Const.SENTINEL_ANY_FLOAT:
                # Sentinel value meaning we don't care what the sample value is, as long as it exists
                return True;
            elif abs(verifyValue * 10**precision) < 1.0:
                # Check for near zero value of verify value before doing divide by zero
                return self.assertAlmostEqual( verifyValue, sampleValue, precision );
            else:
                # Large enough numbers that should consider significant digits rather than decimal places
                if abs((verifyValue-sampleValue)/verifyValue) * 10**precision > 1.0:
                    # Difference as a percentage of verify value is larger than the intended precision, let assert fail
                    return self.assertAlmostEqual( verifyValue, sampleValue, precision );
        else:
            return self.assertEqual( verifyValue, sampleValue );

    def assertEqualFile( self, verifyFile, sampleFile, arbitraryLines=None, whitespace=True ):
        """Assumes the two parameters are each File objects and
        does an "assertEqual" on each pair of lines in the two files

        arbitraryLines - Collection of integers designating (non-blank) lines to skip
        whitespace - If set to false, will compare lines ignoring whitespace
        """
        iLine = 0;
        while True:
            verifyLine = verifyFile.readline();
            sampleLine = sampleFile.readline();

            if not whitespace:  # Ignore blank lines
                while verifyLine == "\n":
                    verifyLine = verifyFile.readline();
                while sampleLine == "\n":
                    sampleLine = sampleFile.readline();

            if arbitraryLines is None or iLine not in arbitraryLines:
                if whitespace:
                    self.assertEqual( verifyLine, sampleLine );
                else:
                    self.assertEqualNonWhitespace( verifyLine, sampleLine );

            if len(verifyLine) < 1 and len(sampleLine) < 1:
                # Both files reached end at same time
                return
            iLine += 1;

    def assertEqualNonWhitespace( self, verifyStr, sampleStr ):
        """Assert two strings are equal, ignoring whitespace
        """
        verifySimpleStr = re.sub(r"\s+","", verifyStr);
        sampleSimpleStr = re.sub(r"\s+","", sampleStr);
        errorMsg = verifyStr + "\n!=\n" + sampleStr;
        self.assertEqual(verifySimpleStr, sampleSimpleStr, errorMsg);

    def assertEqualSet(self, verifySet, sampleSet):
        self.assertEqualList(sorted(verifySet), sorted(sampleSet))

    def assertEqualList( self, verifyList, sampleList ):
        """Assumes the two parameters are each lists or tuples and
        does an "assertEqual" on each pair of items.
        Check item by item rather than whole list
        so errors are easier to debug.
        """
        errorStr  = "%d != %d\n" % (len(verifyList), len(sampleList));
        errorStr += str(sampleList);
        self.assertEqual(len(verifyList), len(sampleList), errorStr)

        for verifyItem, sampleItem in zip(verifyList, sampleList):
            self.assertEqual(verifyItem, sampleItem)

    def assertAlmostEqualsList( self, verifyList, sampleList, places=7 ):
        """Assumes the two parameters are each lists or tuples and
        does an "assertAlmostEqual" on each pair of items.
        Check item by item rather than whole list
        so errors are easier to debug.
        """
        errorStr  = "%d != %d\n" % (len(verifyList),len(sampleList));
        errorStr += str(sampleList);

        self.assertEqual(len(verifyList),len(sampleList), errorStr);
        for verifyItem, sampleItem in zip(verifyList, sampleList):
            self.assertAlmostEqual(verifyItem, sampleItem, places);

    def assertEqualTable( self, verifyTable, sampleTable, precision=None ):
        """Assumes the two parameters are each 2D lists or tuples and
        does an "assertEqual" on each pair of items.
        Check item by item rather than whole table or rows,
        so errors are easier to debug.
        If the precision parameter is specified, will do assertEqualGeneral
        instead with option to compare floating point numbers.
        """
        self.assertEqual(len(verifyTable), len(sampleTable))
        for verifyRow, sampleRow in zip(verifyTable, sampleTable):
            #print >> sys.stderr, "Verify: %s" % str(verifyRow);
            #print >> sys.stderr, "Sample: %s" % str(sampleRow);
            self.assertEqual(len(verifyRow),len(sampleRow))
            for verifyItem, sampleItem in zip(verifyRow, sampleRow):
                if precision is None:
                    self.assertEqual(verifyItem, sampleItem)
                else:
                    self.assertEqualGeneral(verifyItem, sampleItem, precision);

    def assertEqualDict( self, verifyDict, sampleDict, targetKeys=None):
        """Assumes two params are two dict and does a assertEqual on each key, val.
        If targetKeys is provided, will only check equality based on those keyed items.
        """
        if targetKeys is None:
            verifyKeyList = list(verifyDict.keys());
            sampleKeyList = list(sampleDict.keys());
            verifyKeyList.sort();
            sampleKeyList.sort();
            self.assertEqual(len(verifyKeyList), len(sampleKeyList));
            for vKey, sKey in zip(verifyKeyList, sampleKeyList):
                self.assertEqual(vKey, sKey);
                msg = 'Dicts diff with vKey : %s = %s, and sKey: %s = %s'
                self.assertEqual(verifyDict[vKey], sampleDict[sKey], msg % (vKey, str(verifyDict[vKey]), sKey, str(sampleDict[sKey])));
        else:
            for key in targetKeys:
                msg = 'Dicts diff with key (%s).  Verify = %s, Sample = %s'
                self.assertEqual(verifyDict[key], sampleDict[key], msg % (key, str(verifyDict[key]), str(sampleDict[key])));


    def assertEqualDictList( self, verifyList, sampleList, targetKeys=None ):
        """Assumes the two parameters are each lists of dictionary objects
        and check if equal based on the specified targetKeys (otherwise assume all)
        """
        self.assertEqual(len(verifyList),len(sampleList) );
        for verifyItem, sampleItem in zip(verifyList, sampleList):
            self.assertEqualDict(verifyItem, sampleItem, targetKeys);

    def assertAlmostEqualsDict( self, verifyDict, sampleDict, msg=None, places=7 ):
        """Assumes two params are two dicts with numeric vals and does an assertAlmostEquals on each val"""
        verifyKeyList = list(verifyDict.keys());
        sampleKeyList = list(sampleDict.keys());
        self.assertEqual(len(verifyKeyList), len(sampleKeyList), msg);
        verifyKeyList.sort(key=lambda x: x if x is not None else -math.inf) # Python2 sort keeps None at the top while Python3 doesn't allow NoneType and int comparison
        sampleKeyList.sort(key=lambda x: x if x is not None else -math.inf) # Python2 sort keeps None at the top while Python3 doesn't allow NoneType and int comparison
        for vKey, sKey in zip(verifyKeyList, sampleKeyList):
            self.assertEqual(vKey, sKey, msg);
            if isinstance(verifyDict[vKey], float):
                self.assertAlmostEqual(verifyDict[vKey], sampleDict[sKey], places=places, msg=msg);
            else:
                self.assertEqual(verifyDict[vKey], sampleDict[sKey], msg=msg);


    def diffDict(inputDict1, inputDict2):
        """Given two input dictionaries assumed to have numerical values,
        return a "diff" dictionary with all of the values in inputDict2
        minus the values from inputDict1.
        """
        resultDict = dict(inputDict2);  # Start with a copy of second dictionary
        for key, value in inputDict1.items():   # Now look for values to substract from 1st dictionary
            if key not in resultDict:
                resultDict[key] = 0;
            resultDict[key] -= value;
        return resultDict;
    diffDict = staticmethod(diffDict);


    def formatDict(inputDict):
        """Format the contents of the input dictionary,
        to easily display each key, value pair, one per line which
        can be easily translated into tab-delimited format for table manipulation.
        """
        dictStrList = ["{"];
        sortedKeys = list(inputDict.keys());
        sortedKeys.sort();
        for key in sortedKeys:
            value = inputDict[key];
            dictStrList.append("%s:\t%s" % (key, value) )
        dictStrList.append("}");

        return str.join("\n", dictStrList);
    formatDict = staticmethod(formatDict);


    def assertEqualStatResults(self, expectedResults, analysisResults, colNames):
        self.assertEqual(len(expectedResults), len(analysisResults))
        for expectedDict, analysisDict in zip(expectedResults, analysisResults):
            #print >> sys.stderr, colNames;
            #print >> sys.stderr, expectedDict.valuesByName(colNames);
            #print >> sys.stderr, analysisDict.valuesByName(colNames);
            for key in colNames:
                expectedValue = expectedDict[key];
                analysisValue = analysisDict[key];
                try:    # Assume numerical values and just check for "close enough"
                    self.assertAlmostEqual( expectedValue, analysisValue, 3 );
                except TypeError:   # Not numbers, then just use generic equals check
                    self.assertEqual( expectedValue, analysisValue );

    def assertEqualStatResultsTextOutput(self, expectedResults, textOutput, colNames):
        # Convert the text output into a structured format to facilitate verification testing
        headerLine = None;
        while headerLine is None:
            nextLine = textOutput.readline();
            if not nextLine.startswith(COMMENT_TAG):
                headerLine = nextLine;
        headers = headerLine.strip().split("\t");

        analysisResults = list();
        for line in textOutput:
            dataChunks = line.strip().split("\t");
            resultModel = RowItemModel( dataChunks, headers );
            # Convert the target elements of interest into numerical values
            for col in colNames:
                if resultModel[col] == NULL_STRING:
                    resultModel[col] = None;
                else:
                    try:
                        resultModel[col] = float(resultModel[col]);
                    except ValueError:
                        pass;   # Not a number, just leave it as original value then
            analysisResults.append(resultModel);

        self.assertEqualStatResults( expectedResults, analysisResults, colNames );

    def extractJSONComment(self, dataFile):
        """Iterate through lines of the file until find a comment line to
        extract out a JSON data object."""
        for line in dataFile:
            if line.startswith(COMMENT_TAG):
                jsonStr = line[1:].strip(); # Remove comment tag and any flanking whitespace
                jsonData = json.loads(jsonStr);
                return jsonData;
        return None;


class MockCGIFieldStorage(UserDict):
    """Mock object to simulate cgi.FieldStorage for testing purposes.
    All methods may not implemented (stupid, no defined
    interfaces / pure virtual abstract classes) so may need to add
    more methods as application uses them.
    """
    def addMockField(self, key, value):
        """Real cgi.FieldStorage instances are readonly, and thus do not
        support such a method.  This is what allows the test developer
        to manufacture a Mock request object.

        >>> mockForm = MockCGIFieldStorage()
        >>> mockForm.addMockField("MyField","MyValue")
        >>> mockForm["MyField"].value
        'MyValue'
        """
        self[key] = cgi.MiniFieldStorage(key,value)

def make_test_suite(module_name):
    """
    Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test".
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(module_name))
    return suite
