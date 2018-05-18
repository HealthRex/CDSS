#!/usr/bin/env python
import sys;
from math import log;
from math import sqrt, exp, log as ln;
from scipy.stats import chi2_contingency;
from scipy.stats import fisher_exact;

"""Count values less than this in the contingency stats table will be considered degenerate and needing normalization.
Will correct such values by the given adjustment value.
"""
DEGENERATE_VALUE_THRESHOLD = 0.0; # 0.000001;  # Not small enough as Bayes style estimators can yield very small values in scientific notation, which is fine as long as report ratios of small numbers.  Stuck with risk of trying to compare floating point equality to 0 precisely
DEGENERATE_VALUE_ADJUSTMENT = 0.5;

class ContingencyStats:
    """Convenience module for setting up contingency (2x2) tables,
    and calculating derived statistics.
    Roughly order the 2 components A informing B, which can generally be interpreted as 
        Evidence/Data informing Hypothesis
        Diagnostic Test informing actual Disease
        Risk Factor informing Disease
    """
    def __init__(self, nAB, nA, nB, N):
        """Setup 2x2 table based on occurence totals
        - nAB: Number of cases where both event A and B occur
        - nA: Number of cases where A occurs
        - nB: Number of cases where B occurs
        - N: Number of total cases
        
        If you know the table elements already, you can always init with all 0s
        and then manually set the ct table directly
        """
        # Keep references to original values to avoid potentially losing numerical precision information from calculations
        self.nAB = float(nAB);
        self.nA = float(nA);
        self.nB = float(nB);
        self.N = float(N);
        
        self.ct = [ [None,None], [None,None] ];
        self.ct[0][0] = float(nAB);
        self.ct[0][1] = float(nA-nAB);
        self.ct[1][0] = float(nB-nAB);
        self.ct[1][1] = float(N-nA-nB+nAB);
        
    def normalize(self,truncateNegativeValues=False):
        """Check for irregular table values like negative or zero values and adjust them to avoid calculation failures
        """
        ct = self.ct;   # Convenience short-hand
        if truncateNegativeValues:
            # If any negative values, means there was some irregularity in the initial data.  
            # Will prevent proper calculation of P-values by Fisher or Chi2 methods
            for i in (0,1):
                for j in (0,1):
                    if ct[i][j] < 0.0:
                        ct[i][j] = 0.0;

        # If any zero values, change or add a small delta value to ALL fields to avoid divide by zero when calculating things like oddsRatio
        hasDegenerateValues = False;
        for i in (0,1):
            for j in (0,1):
                if abs(ct[i][j]) <= DEGENERATE_VALUE_THRESHOLD:
                    hasDegenerateValues = True;
        if hasDegenerateValues:
            for i in (0,1):
                for j in (0,1):
                    if abs(ct[i][j]) <= DEGENERATE_VALUE_THRESHOLD:
                        ct[i][j] = DEGENERATE_VALUE_ADJUSTMENT;
                    else:
                        ct[i][j] += DEGENERATE_VALUE_ADJUSTMENT;
    
    def calc(self, statId):
        """Return a calculated statistic by an identifying name"""
        ct = self.ct;   # Short-hand convenience
        nAB = self.nAB;
        nA = self.nA;
        nB = self.nB;
        N = self.N;
        
        if statId in ("total","N"):   
            return N;   #ct[0][0]+ct[0][1]+ct[1][0]+ct[1][1];

        elif statId in ("nA",):
            return nA;  #ct[0][0]+ct[0][1];
        
        elif statId in ("nB",):
            return nB;  #ct[0][0]+ct[1][0];
        
        elif statId in ("nAB","support",):   
            return ct[0][0];
        
        elif statId in ("P(A)",):
            return self["nA"] / self["total"];
        
        elif statId in ("P(!A)",):
            return 1-self["P(A)"];
        
        elif statId in ("P(B)","prevalence","preTestProbability","baselineFreq"):
            return self["nB"] / self["total"];
        
        # Reference for SE(prevalence):
        # https://stats.stackexchange.com/questions/9449/how-do-you-compute-confidence-intervals-for-positive-predictive-value
        elif statId in ("SE(prevalence)"):  # Standard error for prevalence
            return sqrt( (self["prevalence"]*(1-self["prevalence"]))/self["total"] );

        # Note that this assumes the prevalence estimate is normally / Gaussian distributed
        #   if we assume that ~2 std errors from mean estimate reflect ~95% confidence interval.
        # This is not true however, as probabilities like prevalence and PPV have values constrained
        #   to [0,1], so a Beta distribution is a better description. 
        # I'm not sure that there is a closed form expression for the 95% confidence interval of
        #   a Beta distribution parameter estimate. This one may be good enough in most cases,
        #   but may sometimes yield negative of >1 values that don't make sense if limited data.
        #   If you want a more robust estimate, it would likely require bootstrapping 
        #   to empirically estimate confidence intervals by simulating random resampling.
        # https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval
        elif statId in ("prevalence95CILow"):
            return self["prevalence"] - 1.96*self["SE(prevalence)"]

        elif statId in ("prevalence95CIHigh"):
            return self["prevalence"] + 1.96*self["SE(prevalence)"]

        elif statId in ("P(!B)",):
            return 1-self["P(B)"];
        
        elif statId in ("P(AB)",):
            return self["nAB"] / self["total"];
        
        elif statId in ("P(B|A)","positivePredictiveValue","PPV","precision","postTestProbability","confidence","conditionalFreq","truePositiveAccuracy"):
            try:
                return ct[0][0] / (ct[0][0]+ct[0][1]);
            except ZeroDivisionError:
                # Try again using original values that may have been very small and suppressed to 0 by loss of numerical precision
                return nAB / nA;

        # Reference for SE(PPV): 
        # https://stats.stackexchange.com/questions/9449/how-do-you-compute-confidence-intervals-for-positive-predictive-value
        elif statId in ("SE(PPV)"):  
            return sqrt( (self["PPV"]*(1-self["PPV"]))/(ct[0][0]+ct[0][1]) );

        elif statId in ("PPV95CILow"):
            return self["PPV"] - 1.96*self["SE(PPV)"]

        elif statId in ("PPV95CIHigh"):
            return self["PPV"] + 1.96*self["SE(PPV)"]

        elif statId in ("P(!B|A)",):
            return 1-self["P(B|A)"];
        
        elif statId in ("P(B|!A)",):
            return ct[1][0] / (ct[1][0]+ct[1][1]);
        
        elif statId in ("P(!B|!A)","negativePredictiveValue","NPV","inversePrecision","trueNegativeAccuracy"):
            return 1-self["P(B|!A)"];
        
        elif statId in ("P(A|B)","truePositiveRate","TPR","sensitivity","sens","recall"):
            return ct[0][0] / (ct[0][0]+ct[1][0]);
        
        elif statId in ("P(!A|B)","falseNegativeRate","FNR","missRate"):
            return 1-self["P(A|B)"];
        
        elif statId in ("P(A|!B)","falsePositiveRate","FPR","fallout"):
            return ct[0][1] / (ct[0][1]+ct[1][1]);
        
        elif statId in ("P(!A|!B)","trueNegativeRate","TNR","specificity","spec","inverseRecall"):
            return 1-self["P(A|!B)"];
        
        elif statId in ("F1","F1-score"):
            precision = self["precision"];
            recall = self["recall"];
            if precision+recall == 0.0:
                return 0.0;
            else:
                return 2*precision*recall / (precision+recall);
            
        elif statId in ("positiveLikelihoodRatio","+LR","LR+","LR"):
            return self["P(A|B)"] / self["P(A|!B)"];
            
        elif statId in ("negativeLikelihoodRatio","-LR","LR-"):
            return self["P(!A|B)"] / self["P(!A|!B)"];
            
        elif statId in ("oddsRatio","OR"):
            return (ct[0][0]/ct[0][1]) / (ct[1][0]/ct[1][1]);

        elif statId in ("SE(ln(OR))"):  # Standard error of the log of the odds ratio
            return sqrt(1/ct[0][0] + 1/ct[0][1] + 1/ct[1][0] + 1/ct[1][1]);
        
        elif statId in ("oddsRatio95CILow","OR95CILow"):
            return exp( ln(self["OR"]) - 1.96*self["SE(ln(OR))"] );
            
        elif statId in ("oddsRatio95CIHigh","OR95CIHigh"):
            return exp( ln(self["OR"]) + 1.96*self["SE(ln(OR))"] );

        elif statId in ("relativeRisk","RR"):
            return self["P(B|A)"] / self["P(B|!A)"];

        elif statId in ("SE(ln(RR))"):  
            # Standard error of the log of the relative risk ratio
            # http://www.medcalc.org/calc/relative_risk.php
            return sqrt(1/ct[0][0] + 1/ct[1][0] + 1/(ct[0][0]+ct[0][1]) + 1/(ct[1][0]+ct[1][1]) );
        
        elif statId in ("relativeRisk95CILow","RR95CILow"):
            return exp( ln(self["RR"]) - 1.96*self["SE(ln(RR))"] );
            
        elif statId in ("relativeRisk95CIHigh","RR95CIHigh"):
            return exp( ln(self["RR"]) + 1.96*self["SE(ln(RR))"] );
            
        elif statId in ("interest","freqRatio","TF*IDF","tfidf","lift","P(B|A)/P(B)"):
            return self["P(B|A)"] / self["P(B)"];
        
        elif statId in ("YatesChi2",):
            try:
                (chi2, chi2P, dof, expected) = chi2_contingency(ct, True);
                return chi2;
            except ValueError:
                # Probably negative values in table, don't know how to interpret
                return 0.0;
            
        elif statId in ("P-YatesChi2",):
            try:
                (chi2, chi2P, dof, expected) = chi2_contingency(ct, True);
                return chi2P;
            except ValueError:
                # Probably negative values in table, don't know how to interpret
                return 1.0;

        elif statId in ("P-YatesChi2-NegLog",):
            try:
                (chi2, chi2P, dof, expected) = chi2_contingency(ct, True);
                oddsRatio = self["OR"];
                
                logP = -sys.float_info.max;
                if chi2P > 0.0:
                    logP = log(chi2P,10);

                if oddsRatio > 1.0:
                    return -logP;
                else:
                    return logP;
            except ValueError, exc:
                # Likely from negative table values.  Return default / uncertain value
                return 0.0;
            
        elif statId in ("P-Chi2",):
            try:
                (chi2, chi2P, dof, expected) = chi2_contingency(ct, False);
                return chi2P;
            except ValueError:
                # Probably negative values in table, don't know how to interpret
                return 1.0;
            
        elif statId in ("P-Chi2-NegLog",):
            try:
                (chi2, chi2P, dof, expected) = chi2_contingency(ct, False);
                oddsRatio = self["OR"];
                
                logP = -sys.float_info.max;
                if chi2P > 0.0:
                    logP = log(chi2P,10);

                if oddsRatio > 1.0:
                    return -logP;
                else:
                    return logP;
            except ValueError, exc:
                # Likely from negative table values.  Return default / uncertain value
                return 0.0;
            
        elif statId in ("P-Fisher",):
            try:
                (oddsRatio, fisherP) = fisher_exact(ct);
                return fisherP;
            except ValueError, exc:
                # Negative table values.  Return default / uncertain value
                return 1.0;
        
        elif statId in ("P-Fisher-Complement",):    
            # Complement (1-alpha) or (alpha-1) such that sorting in descending in order will naturally bring the most significant positive associations to the top and most significant negative associations to the bottom
            try:
                (oddsRatio, fisherP) = fisher_exact(ct);
                if oddsRatio > 1.0:
                    return (1-fisherP);
                else:
                    return (fisherP-1);
            except ValueError, exc:
                return 0.0;

        elif statId in ("P-Fisher-NegLog",):
            # Negated if odds ratio positive such that sorting in descending in order will bring the most significant positive associations to the top and most significant negative associations to the bottom
            #   Slight improvement over P-Fisher-Complement, otherwise very small P-values will lose numerical precision
            try:
                (oddsRatio, fisherP) = fisher_exact(ct);

                logP = -sys.float_info.max;
                if fisherP > 0.0:
                    logP = log(fisherP,10);

                if oddsRatio > 1.0:
                    return -logP;
                else:
                    return logP;
            except ValueError, exc:
                # Likely from negative table values.  Return default / uncertain value
                return 0.0;
        else:
            raise UnrecognizedStatException("Unrecognized statistic ID: [%s]" % statId );

    def __getitem__(self, key):
        """Short-hand for access calc function"""
        return self.calc(key);

class UnrecognizedStatException(Exception):
    def __init__( self, initStr ):
        Exception.__init__(self, initStr);

class AggregateStats:
    """Simple statistics utility.  Given a set of numbers,
    calculate aggregate statistics like min, max, mean, 
    standard deviation, etc, with the option of having weightd data points.
    """
    
    def __init__( self, dataSet, weights=None ):
        """Initialization constructor"""
        self.dataSet = dataSet
        self.weights = weights

    def mean(self):
        """Return the mean / average of the data set, ignoring None values"""
        if self.mMean == None:
            nullCount = 0
            self.mMean = 0.0;
            for item in self.dataSet:
                if item == None:
                    nullCount += 1
                else:
                    self.mMean += item
            self.mMean = self.mMean / (len(self.dataSet)-nullCount)
        return self.mMean

    def stdDev(self):
        """Return the standard deviation of the data set, ignoring None values"""
        if self.mStdDev == None:
            self.mStdDev = self.rmsd( self.mean() )
        return self.mStdDev

    def meanW(self):
        """Return the weighted mean / average of the data set, ignoring None and zero-weighted values
        """
        if self.mMeanW == None:
            self.mMeanW = 0.0
            totalWeight = 0.0
            for item, weight in zip(self.dataSet,self.weights):
                if item != None and weight > 0.0:
                    self.mMeanW += item*weight
                    totalWeight += weight
            self.mMeanW = self.mMeanW / totalWeight
        return self.mMeanW

    def stdDevW(self):
        """Return the weighted standard deviation of the data set, ignoring None and zero-weighted values.
        """
        if self.mStdDevW == None:
            self.mStdDevW = self.rmsdW( self.meanW() )
        return self.mStdDevW

    def rmsd( self, value ):
        """Return the root-mean-square deviation for the data set 
        with respect to a value.  Returns the equivalent of the 
        standard deviation function, but using the value in place 
        of the mean.
        """
        nullCount = 0
        rmsd = 0.0
        for item in self.dataSet:
            if item == None:
                nullCount += 1
            else:
                rmsd = rmsd + (value-item)*(value-item)

        rmsd = rmsd / (len(self.dataSet)-nullCount-1)   # -1 for unbiased estimate
        rmsd = sqrt(rmsd)
        return rmsd

    """Return the weighted root-mean-square deviation for the data set 
    with respect to a value.  Returns the equivalent of the weighted 
    standard deviation function, but using the value in place of the mean.
    """
    def rmsdW( self, value ):
        nonZeroWeights = 0
        rmsdW = 0.0
        totalWeight = 0.0
        
        for item, weight in zip(self.dataSet,self.weights):
            if item != None and weight > 0.0:
                rmsdW = rmsdW + (value-item)*(value-item)*weight
                totalWeight = totalWeight + weight
                nonZeroWeights += 1

        rmsdW = rmsdW / ( (nonZeroWeights-1)*totalWeight/nonZeroWeights )   # -1 for unbiased estimate
        rmsdW = sqrt(rmsdW)
        return rmsdW

    def min(self):
        """Return the minimum value in the data set"""
        if self.mMin == None:
            self.mMin = self.dataSet[0]
            for item in self.dataSet:
                if item != None and item < self.mMin:
                    self.mMin = item
        return self.mMin

    def max(self):
        """Return the maximum value in the data set"""
        if self.mMax == None:
            self.mMax = self.dataSet[0]
            for item in self.dataSet:
                if item != None and item > self.mMax:
                    self.mMax = item
        return self.mMax

    def countNonNull(self):
        """Returns the number of values in the data set that are not None"""
        count = 0
        for item in self.dataSet:
            if item != None:
                count += 1
        return count

    def countNonZeroWeight(self):
        """Returns the number of values in the data set that are 
        both not None and whose respective weight value is greater than 0.
        """
        count = 0;
        for item, weight in zip(self.dataSet,self.weights):
            if item != None and weight > 0.0:
                count += 1
        return count

    """Data set to calculate statistics off of"""
    dataSet = None
    """Set of weights to apply to each data point"""
    weights = None

    """Calcuated aggregate values.  Store after first calc."""
    mMean   = None
    mStdDev = None
    mMeanW  = None
    mStdDevW= None
    mMin    = None
    mMax    = None

    def incrementStats(value, weight, mean, variance, totalWeight):
        """Given the mean, variance and count (totalWeight) for a previous data sample,
        calculate the new, revised (incremented) stats based on adding
        one more data item to the sample with the given value and weight contribution (use 1 if simple counts).

        Assumes that the variance is for an unbiased population sample.
        I.e., the value is scaled by 1/(n-1) instead of 1/n.
        """
        newWeight = totalWeight + weight;
        newMean = mean;
        newVariance = variance;

        if newWeight > 0:
            newMean = (mean*totalWeight + value*weight) / (newWeight);

        if totalWeight > 0 and newWeight > 0 and (newWeight-1) > 0:
            # Need more than 1 data point to define a meaningful variance
            # Deconstruct and reconstruct variance in several steps        
            biasedVariance = variance * (totalWeight-1)/totalWeight;
            expectedSquareValue = biasedVariance + mean*mean;
            sumSquares = expectedSquareValue * totalWeight;

            newExpectedSquareValue = (sumSquares + weight*value*value) / (newWeight);
            newBiasedVariance = newExpectedSquareValue - newMean*newMean;
            newVariance = newBiasedVariance * (newWeight) / (newWeight-1);

        return (newMean, newVariance, newWeight);
    incrementStats = staticmethod(incrementStats);
    