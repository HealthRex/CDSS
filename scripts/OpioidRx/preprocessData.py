import sys, os;
import time;
from datetime import datetime, timedelta;
from cStringIO import StringIO;
from medinfo.common.Util import stdOpen, log, ProgressDots;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel, modelListFromTable, modelDictFromList;
from medinfo.db.ResultsFormatter import TextResultsFormatter;

import pandas as pd;
import numpy as np;
from sklearn.preprocessing import Imputer;
from sklearn.preprocessing import LabelBinarizer;

RACE_OPTIONS = ["White","Black or African American"];
DEFAULT_RACE = "OtherRace";
DATE_COLS = ["periodStart"];


def main(argv):
    timer = time.time();
    inFile = stdOpen(argv[1]);
    outFile = stdOpen(argv[2],"w");
    df = dataFrame = pd.read_table(inFile, parse_dates=DATE_COLS);

    df = binarizeGender(df);
    df = binarizeRace(df, RACE_OPTIONS, DEFAULT_RACE);
    df = binarizePeriod(df);
    df["hasDrugScreens"] = (df["nDrugScreens"] > 0)*1;  # Convert to binary outcome measure

    df.to_csv(outFile,sep="\t",index=False);

    elapsed = time.time() - timer;
    print >> sys.stderr, "%s seconds to complete" % timedelta(0, round(elapsed));
    
    return df;

def binarizeGender(df):
    proc = LabelBinarizer();
    binaryValues = proc.fit_transform(df["gender"]);
    binaryDF = pd.DataFrame(binaryValues, columns=[proc.classes_[1]]);  # Single label for expected binary case
    extendedDF = df.join(binaryDF);
    return extendedDF;
    
def binarizeRace(df, raceOptions, defaultRace):
    # Ensure no NaN values, otherwise label function will bomb
    df["race"].replace(np.NaN, defaultRace);
    df["race"] = df["race"].astype("string");
    
    proc = LabelBinarizer();
    binaryValues = proc.fit_transform(df["race"]);
    binaryDF = pd.DataFrame(binaryValues, columns=proc.classes_);
    # Due to low counts, merge non-prominent races into generic "OtherRace" Category
    usedRaceDF = binaryDF[raceOptions]; # Pull out label options we'll keep
    usedRaceDF[defaultRace] = 1-usedRaceDF.any(axis=1);   # Look for any (OR logic) labels present for binary 0, 1 values, then negate result to get all non-label optioned cases
    extendedDF = df.join(usedRaceDF);
    return extendedDF;
    
def binarizePeriod(df):
    proc = LabelBinarizer();
    binaryValues = proc.fit_transform(df["periodStart"]);
    label = "postIntervention";
    if proc.classes_[1] < proc.classes_[0]:
        label = "preIntervention";
    binaryDF = pd.DataFrame(binaryValues, columns=[label]);  # Single label for expected binary case
    extendedDF = df.join(binaryDF);
    return extendedDF;
    
    
"""
def imputeMissingValues(preDF):
    # Fill in any missing values with means of ones available
    imp = Imputer();
    preArr = np.array(preDF);   # Convert to array/matrix format for sklearn compatibility
    imputedArr = imp.fit_transform(preArr);
    imputedDF = pd.DataFrame(imputedArr);
    imputedDF.index = preDF.index;
    imputedDF.columns = preDF.columns;
    return imputedDF;

def featureSelection(preDF, outcomeSeries, nFeatures):
    ySeries = outcomeSeries;
    xDF = preDF.drop(ySeries.name, axis=1);
    
    selector = SelectKBest(chi2, nFeatures);    # Select most informative features by chi2 with outcome
    xTransformArray = selector.fit_transform(xDF, ySeries);
    xSelectDF = pd.DataFrame(xTransformArray);
    xSelectDF.columns = selector.transform(xDF.columns)[0]; # Re-Map column labels
    xSelectDF.index = xDF.index;
    
    return xSelectDF;
"""

if __name__ == "__main__":
    main(sys.argv);