#!/usr/bin/env python
"""Test case for respective module in parent package"""

import sys, os
import cStringIO
import unittest
from math import sqrt, exp, log as ln;

import Const, Util

from medinfo.common.StatsUtil import AggregateStats, ContingencyStats, UnrecognizedStatException;
from medinfo.common.test.Util import MedInfoTestCase

class TestAggregateStats(MedInfoTestCase):
    def setUp(self):
        MedInfoTestCase.setUp(self);

        # Data to test on
        self.DATA = [ -5, -4, -3, -2, -1,  0, +5, +4, +3, +2, +1, None]

        # Data weights to test against
        self.WEIGHTS =[  0,  0,  1,  1,  2,  2,  3,  3,  4,  4,  5,  5 ]
    
        # Expected function results
        self.MIN = -5.0
        self.MAX = +5.0
        
        self.MEAN   = 0.0
        self.MEAN_W = 1.8

        self.STD_DEV    = 3.31662479
        self.STD_DEV_W  = 2.264950331
        
        self.RMSD   = self.STD_DEV
        self.RMSD_W = self.STD_DEV_W
        
        self.N_NON_NAN_VALUES           = 11
        self.N_NON_ZERO_WEIGHTED_VALUES = 9
        
        # Instance to test on
        self.aAggregateStats = AggregateStats(self.DATA,self.WEIGHTS)

    def tearDown(self):
        MedInfoTestCase.tearDown(self);

    def test_minMax(self):
        self.assertAlmostEquals(self.MIN, self.aAggregateStats.min())
        self.assertAlmostEquals(self.MAX, self.aAggregateStats.max())

    def test_meanStdDev(self):
        self.assertAlmostEquals(self.MEAN,   self.aAggregateStats.mean())
        self.assertAlmostEquals(self.STD_DEV,self.aAggregateStats.stdDev())

    def test_weightedMeanStdDev(self):
        self.assertAlmostEquals(self.MEAN_W,     self.aAggregateStats.meanW())
        self.assertAlmostEquals(self.STD_DEV_W,  self.aAggregateStats.stdDevW())

    def test_rmsd(self):
        self.assertAlmostEquals(self.RMSD,   self.aAggregateStats.rmsd(self.MEAN))
        self.assertAlmostEquals(self.RMSD_W, self.aAggregateStats.rmsdW(self.MEAN_W))

        Util.log.debug("Negative test case");
        self.assertNotAlmostEquals(self.RMSD_W,  self.aAggregateStats.rmsd(self.MEAN))
        self.assertNotAlmostEquals(self.RMSD,    self.aAggregateStats.rmsdW(self.MEAN_W))

    def test_counts(self):
        self.assertEquals( self.N_NON_NAN_VALUES,            self.aAggregateStats.countNonNull() )
        self.assertEquals( self.N_NON_ZERO_WEIGHTED_VALUES,  self.aAggregateStats.countNonZeroWeight() )

    def test_incrementStats(self):

        mean = 3.0;
        variance = 2.5;
        totalWeight = 5;
        
        value = 6;
        weight = 2;
        
        (newMean, newVariance, newWeight) = AggregateStats.incrementStats(value, weight, mean, variance, totalWeight);

        expectedMean = 3.857;
        expectedVariance = 3.81;
        expectedWeight = 7;
        
        self.assertAlmostEquals(expectedMean, newMean, 3);
        self.assertAlmostEquals(expectedVariance, newVariance, 3);
        self.assertAlmostEquals(expectedWeight, newWeight, 3);

class TestContingencyStats(MedInfoTestCase):
    def setUp(self):
        MedInfoTestCase.setUp(self);

        # Data to test on
        self.TEST_NAB = 20;
        self.TEST_NA = 30;
        self.TEST_NB = 40;
        self.TEST_TOTAL = 100;
        
        # Corresponds to contingency table:
        #           B+  B-  Total
        #   A+      20  10  30
        #   A-      20  50  70
        #   Total   40  60  100

        # Expected function results
        self.EXPECTED = \
            {   "nAB":  20,
                "nA": 30,
                "nB": 40,
                "N": 100,
            
                "support": 20,
                "confidence":  20/30.0,
                "prevalence":  40/100.0,
                "interest": (20/30.0) / (40/100.0),

                "truePositiveRate": 20/40.0,
                "trueNegativeRate": 50/60.0,

                "falseNegativeRate": 1-20/40.0,
                "falsePositiveRate": 1-50/60.0,

                "positivePredictiveValue": 20/30.0,
                "negativePredictiveValue": 50/70.0,

                "positiveLikelihoodRatio": (20/40.0) / (1-50/60.0),
                "negativeLikelihoodRatio": (1-20/40.0) / (50/60.0),
                
                "oddsRatio": (20/10.0) / (20/50.0),
                "oddsRatio95CILow": exp( ln((20/10.0)/(20/50.0)) - 1.96*sqrt(1/20.0 + 1/10.0 + 1/20.0 + 1/50.0) ),
                "oddsRatio95CIHigh": exp( ln((20/10.0)/(20/50.0)) + 1.96*sqrt(1/20.0 + 1/10.0 + 1/20.0 + 1/50.0) ),

                "relativeRisk": (20/30.0) / (20/70.0),
                "relativeRisk95CILow": exp( ln((20/30.0)/(20/70.0)) - 1.96*sqrt(1/20.0 + 1/20.0 + 1/30.0 + 1/70.0) ),
                "relativeRisk95CIHigh": exp( ln((20/30.0)/(20/70.0)) + 1.96*sqrt(1/20.0 + 1/20.0 + 1/30.0 + 1/70.0) ),
                
                "P-Chi2": 0.00036,
                "P-Chi2-NegLog": 3.437,
                "YatesChi2": 11.161,
                "P-YatesChi2": 0.001,
                "P-YatesChi2-NegLog": 3.07806,
                "P-Fisher": 0.001,
                "P-Fisher-Complement": 0.999,
                "P-Fisher-NegLog": 3.167,
            };
            
        # Add some synonyms
        synonymsByStatId = \
            {   "confidence":   ("conditionalFreq",),
                "prevalence":   ("baselineFreq",),
                "interest":     ("freqRatio",),

                "truePositiveRate": ("TPR","sensitivity","P(A|B)"),
                "trueNegativeRate": ("TNR","specificity","P(!A|!B)"),
                "falseNegativeRate": ("FNR","P(!A|B)"),
                "falsePositiveRate": ("FPR","P(A|!B)"),

                "positivePredictiveValue": ("PPV","P(B|A)"),
                "negativePredictiveValue": ("NPV","P(!B|!A)"),

                "positiveLikelihoodRatio": ("+LR",),
                "negativeLikelihoodRatio": ("-LR",),
                
                "oddsRatio": ("OR",),
                "oddsRatio95CILow": ("OR95CILow",),
                "oddsRatio95CIHigh": ("OR95CIHigh",),

                "relativeRisk": ("RR",),
                "relativeRisk95CILow": ("RR95CILow",),
                "relativeRisk95CIHigh": ("RR95CIHigh",),
            }
        for statId, synonymIds in synonymsByStatId.iteritems():
            for synonymId in synonymIds:
                self.EXPECTED[synonymId] = self.EXPECTED[statId];
            
    def test_contingencyStats(self):
        contStats = ContingencyStats( self.TEST_NAB, self.TEST_NA, self.TEST_NB, self.TEST_TOTAL );
        
        for statId, expectedValue in self.EXPECTED.iteritems():
            Util.log.debug(statId);
            testValue = contStats.calc(statId);
            self.assertAlmostEquals( expectedValue, testValue, 3 );

    def test_contingencyStats_normalize(self):
        # Set test values that will result in divide by zero or negative unless normalize somehow
        nAB = 10;
        nA = 15;
        nB = 25;    # nB exceeds N, which should not make sense
        N = 20;
        
        # Makes table like
        #       B+  B-
        #   A+  10  5
        #   A-  15 -10        

        # Normalization should negative values to make
        #       B+  B-
        #   A+  10  5
        #   A-  15  0
        
        # Add small delta to all values to avoid zeros
        #       B+      B-
        #   A+  10.5    5.5
        #   A-  15.5    0.5

        contStats = ContingencyStats( nAB, nA, nB, N );
        
        expected = \
            {   "sensitivity": 0.4,
                "specificity": 2.0, # Makes no sense with negative numbers
            }
        for statId, expectedValue in expected.iteritems():
            Util.log.debug(statId);
            testValue = contStats.calc(statId);
            self.assertAlmostEquals( expectedValue, testValue, 3 );
        
        expected = \
            {   "P-Fisher": 1.0,    # Cannot calculate this properly with negative numbers
                "P-Fisher-Complement": 0.0,
                "P-Fisher-NegLog": 0.0,
            }

        Util.log.debug("Expect calculation error with default values returned");
        for statId, expectedValue in expected.iteritems():
            Util.log.debug(statId);
            testValue = contStats.calc(statId);
            self.assertAlmostEquals( expectedValue, testValue, 3 );
        
        Util.log.debug("Now redo while adding normalization option");
        expected = \
            {   "oddsRatio": (10.5/5.5) / (15.5/0.5),
                "relativeRisk": (10.5/(10.5+5.5)) / (15.5/(15.5+0.5)),
                "sensitivity": (10.5/(10.5+15.5)),
                "specificity": (0.5/(0.5+5.5)),
                "P-Fisher": 0.04214,    # Cannot calculate this properly with negative numbers
                "P-Fisher-Complement": -0.95786,
                "P-Fisher-NegLog": -1.375,
            }

        contStats.normalize(truncateNegativeValues=True);
        for statId, expectedValue in expected.iteritems():
            Util.log.debug(statId);
            testValue = contStats.calc(statId);
            self.assertAlmostEquals( expectedValue, testValue, 3 );

    def test_precisionTolerance(self):
        # Try setting very small values and validating that won't lose values during numerical changes
        nAB = 1.5e-160;
        nA = 3.0e-180;  # Doesn't make sense that is smaller than nAB, but NaiveBayes estimates can result in such cases
        nB = 1000.0;
        N =  15000.0;
        contStats = ContingencyStats( nAB, nA, nB, N );
        
        expected = \
            {   "PPV": 5e+19,
                "sensitivity": 1.5e-163,
                "specificity": 1.0, # Precision inevitably lost here
            }
        for statId, expectedValue in expected.iteritems():
            Util.log.debug(statId);
            testValue = contStats.calc(statId);
            self.assertAlmostEquals( expectedValue, testValue, 3 );

class TestUnitTestTools(MedInfoTestCase):
    def test_assertEqualsGeneral(self):
        # Should allow option of verifying equal values by number of significant digits, not just decimal places
        self.assertEqualGeneral(0.12345, 0.1235, 3);   # Equal within 3 significant digits, similar to decimal points
        foundError = False;
        try:
            self.assertEqualGeneral(0.12345, 0.122, 3);   # NOT equal within 3 decimal points significant digits
        except AssertionError:
            foundError = True;
        self.assertTrue(foundError);

        self.assertEqualGeneral(12345.101, 12345.001, 3);   # Equal within 3 significant digits even though not decimal places
        foundError = False;
        try:
            self.assertEqualGeneral(12345.0, 12400.0, 3);   # NOT equal within 3 sig digits, expect exception
        except AssertionError:
            foundError = True;
        self.assertTrue(foundError);

        self.assertEqualGeneral(-0.12345, -0.1235, 3);   # Negative value equal within 3 significant digits, similar to decimal points
        foundError = False;
        try:
            self.assertEqualGeneral(-0.12345, -0.122, 3);   # Negative values NOT equal within 3 decimal points significant digits
        except AssertionError:
            foundError = True;
        self.assertTrue(foundError);
        self.assertEqualGeneral(-0.12345, -0.122, 2);   # Negative values equal within 2 decimal points significant digits

        self.assertEqualGeneral(-12345.101, -12345.001, 3);   # Negative values Equal within 3 significant digits even though not decimal places
        foundError = False;
        try:
            self.assertEqualGeneral(-12345.0, -12400.0, 3);   # NOT equal within 3 sig digits, expect exception
        except AssertionError:
            foundError = True;
        self.assertTrue(foundError);
        self.assertEqualGeneral(-12345.0, -12400.0, 2);   # Equal within 2 sig digits

        self.assertEqualGeneral(0.0, 0.0, 3);   # Zero Equal within 3 sig digits
        self.assertEqualGeneral(0.0, 0.0001, 3);   
        self.assertEqualGeneral(0.0, -0.0001, 3);   
        self.assertEqualGeneral(0.0001, 0.0, 3);   
        self.assertEqualGeneral(-0.0001, 0.0, 3);   
        foundError = False;
        try:
            self.assertEqualGeneral(0.0, -0.01, 3);   # NOT equal within 3 sig digits, expect exception
        except AssertionError:
            foundError = True;
        self.assertTrue(foundError);
        foundError = False;
        try:
            self.assertEqualGeneral(0.0, +0.01, 3);   # NOT equal within 3 sig digits, expect exception
        except AssertionError:
            foundError = True;
        self.assertTrue(foundError);

        # Positive values can still be equivalent to negative values if small enough difference
        self.assertEqualGeneral(-0.0001, +0.0001, 3);   
        foundError = False;
        try:
            self.assertEqualGeneral(-0.0001, +0.0001, 4); # Not equal within 4 digits  expect exception
        except AssertionError:
            foundError = True;
        self.assertTrue(foundError);

def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    suite.addTest(unittest.makeSuite(TestAggregateStats));
    suite.addTest(unittest.makeSuite(TestContingencyStats));
    suite.addTest(unittest.makeSuite(TestUnitTestTools));
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=Const.RUNNER_VERBOSITY).run(suite())

