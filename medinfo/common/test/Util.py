import Const
import sys, os
import logging
import cgi, UserDict
import unittest
import re;

import medinfo.common.Util;

log = logging.getLogger(__name__)
log.setLevel(Const.LOGGER_LEVEL)

handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(Const.LOGGER_FORMAT)

handler.setFormatter(formatter)
log.addHandler(handler)

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
        except Exception, exc:
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

    def assertEqualList( self, verifyList, sampleList ):
        """Assumes the two parameters are each lists or tuples and
        does an "assertEqual" on each pair of items.
        Check item by item rather than whole list
        so errors are easier to debug.
        """
        errorStr  = "%d != %d\n" % (len(verifyList),len(sampleList));
        errorStr += str(sampleList);

        for verifyItem, sampleItem in zip(verifyList, sampleList):
            self.assertEqual(verifyItem, sampleItem)
        self.assertEqual(len(verifyList),len(sampleList), errorStr)

    def assertAlmostEqualsList( self, verifyList, sampleList ):
        """Assumes the two parameters are each lists or tuples and
        does an "assertAlmostEqual" on each pair of items.
        Check item by item rather than whole list
        so errors are easier to debug.
        """
        errorStr  = "%d != %d\n" % (len(verifyList),len(sampleList));
        errorStr += str(sampleList);

        self.assertEqual(len(verifyList),len(sampleList), errorStr)
        for verifyItem, sampleItem in zip(verifyList, sampleList):
            self.assertAlmostEquals(verifyItem, sampleItem)


    def assertEqualTable( self, verifyTable, sampleTable, precision=None ):
        """Assumes the two parameters are each 2D lists or tuples and
        does an "assertEqual" on each pair of items.
        Check item by item rather than whole table or rows,
        so errors are easier to debug.
        If the precision parameter is specified, will do assertEqualGeneral
        instead with option to compare floating point numbers.
        """
        for verifyRow, sampleRow in zip(verifyTable, sampleTable):
            #print >> sys.stderr, "Verify: %s" % str(verifyRow);
            #print >> sys.stderr, "Sample: %s" % str(sampleRow);
            for verifyItem, sampleItem in zip(verifyRow, sampleRow):
                if precision is None:
                    self.assertEqual(verifyItem, sampleItem)
                else:
                    self.assertEqualGeneral(verifyItem, sampleItem, precision);
            self.assertEqual(len(verifyRow),len(sampleRow))
        self.assertEqual(len(verifyTable),len(sampleTable))

    def assertEqualDict( self, verifyDict, sampleDict, targetKeys=None):
        """Assumes two params are two dict and does a assertEqual on each key, val.
        If targetKeys is provided, will only check equality based on those keyed items.
        """
        if targetKeys is None:
            verifyKeyList = verifyDict.keys();
            sampleKeyList = sampleDict.keys();
            verifyKeyList.sort();
            sampleKeyList.sort();
            for vKey, sKey in zip(verifyKeyList, sampleKeyList):
                self.assertEquals(vKey, sKey);
                msg = 'Dicts diff with vKey : %s = %s, and sKey: %s = %s'
                self.assertEquals(verifyDict[vKey], sampleDict[sKey], msg % (vKey, str(verifyDict[vKey]), sKey, str(sampleDict[sKey])));
            self.assertEqual(len(verifyKeyList), len(sampleKeyList));
        else:
            for key in targetKeys:
                msg = 'Dicts diff with key (%s).  Verify = %s, Sample = %s'
                self.assertEquals(verifyDict[key], sampleDict[key], msg % (key, str(verifyDict[key]), str(sampleDict[key])));


    def assertEqualDictList( self, verifyList, sampleList, targetKeys=None ):
        """Assumes the two parameters are each lists of dictionary objects
        and check if equal based on the specified targetKeys (otherwise assume all)
        """
        for verifyItem, sampleItem in zip(verifyList, sampleList):
            self.assertEqualDict(verifyItem, sampleItem, targetKeys);
        self.assertEqual(len(verifyList),len(sampleList) );

    def assertAlmostEqualsDict( self, verifyDict, sampleDict, msg=None, places=7 ):
        """Assumes two params are two dicts with numeric vals and does an assertAlmostEquals on each val"""
        verifyKeyList = verifyDict.keys();
        sampleKeyList = sampleDict.keys();
        self.assertEqual(len(verifyKeyList), len(sampleKeyList), msg);
        verifyKeyList.sort();
        sampleKeyList.sort();
        for vKey, sKey in zip(verifyKeyList, sampleKeyList):
            self.assertEquals(vKey, sKey, msg);
            if isinstance(verifyDict[vKey], float):
                self.assertAlmostEquals(verifyDict[vKey], sampleDict[sKey], places=places, msg=msg);
            else:
                self.assertEquals(verifyDict[vKey], sampleDict[sKey], msg=msg);


    def diffDict(inputDict1, inputDict2):
        """Given two input dictionaries assumed to have numerical values,
        return a "diff" dictionary with all of the values in inputDict2
        minus the values from inputDict1.
        """
        resultDict = dict(inputDict2);  # Start with a copy of second dictionary
        for key, value in inputDict1.iteritems():   # Now look for values to substract from 1st dictionary
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
        sortedKeys = inputDict.keys();
        sortedKeys.sort();
        for key in sortedKeys:
            value = inputDict[key];
            dictStrList.append("%s:\t%s" % (key, value) )
        dictStrList.append("}");

        return str.join("\n", dictStrList);
    formatDict = staticmethod(formatDict);


class MockCGIFieldStorage(UserDict.UserDict):
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
