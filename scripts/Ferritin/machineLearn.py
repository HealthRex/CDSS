import sys, os;
import time;
from cStringIO import StringIO;
from medinfo.common.Util import stdOpen, log, ProgressDots;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel, modelListFromTable, modelDictFromList;
from medinfo.db.ResultsFormatter import TextResultsFormatter;

import pandas as pd;
import numpy as np;
from sklearn_pandas import DataFrameMapper;
from sklearn.feature_selection import SelectKBest, chi2;
from sklearn.preprocessing import Imputer;
from sklearn.linear_model import LogisticRegression, Lasso;
from sklearn.lda import LDA;
from sklearn.naive_bayes import BernoulliNB;
from sklearn.neighbors import NearestCentroid, KNeighborsClassifier;
from sklearn.svm import SVC;
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier;
from sklearn.dummy import DummyClassifier;
from sklearn.metrics import accuracy_score, auc, confusion_matrix, precision_recall_fscore_support, precision_score, recall_score;
from sklearn.cross_validation import KFold, cross_val_score;

availableDiagnostics = ['WBC.last', 'HGB.last', 'HCT.last', 'MCV.last', 'RDW.last', 'PLT.last', 'TBIL.last', 'CR.last', 'ESR.last', 'CRP.last',];
availableDiagnostics.extend(["surgery","dialysis"]);
availableDiagnostics.extend(["FE.last","TRFRN.last","TRFSAT.last","FERRITIN.last"]);
ironDiagnostics = ["FERRITIN.last","FE.last","TRFRN.last","TRFSAT.last","YSTFRR.last"];
outcomeDiagnostics = ["FERRITIN.last"];
outcomeRx = ["ironOutpatient.post"];

MODELS = \
        [   DummyClassifier(),
            DummyClassifier('most_frequent'),
            LogisticRegression(), 
            LDA(),
            #Lasso(alpha=1),
            #Lasso(alpha=2),
            BernoulliNB(), 
            NearestCentroid(), 
            KNeighborsClassifier(), 
            SVC(), 
            RandomForestClassifier(), 
            AdaBoostClassifier()
        ];
SCORE_FXNS = \
        (   
            #"accuracy",
            #"f1",
            "precision",
            #"recall"
        );

def readDataFrame(filename):
    dataFile = open(filename);
    dataFrame = pd.read_table(dataFile, na_values=[str(None)]);    # Primary dataframe
    return dataFrame;

def filterDataFrame(df):
    # Composite single filter to reduce data frame size
    #   Negation signs cause looking for cases where do NOT have prior transfusion, surgery, or dialysis
    #   * multiplication on boolean values operates as element-wise AND combination
    comboFilter = \
        (   
            #-(df["surgery"] == 1) *     # Exclude if surgical patients.  Should have good PPV, but poor sensitivity since just based on admit order and diet type
            #-(df["dialysis"] == 1) *    # Exclude if any dialysis orders
            -df["ICD9.208-AdmitDx.pre"] *
            -df["ICD9.208-ProblemListDx.pre"] *
            -df["ironSO4.pre"] *    # Prior iron prescription
            -df["ironEnteral.pre"] *    # Prior iron prescription
            -df["ironIV.pre"] *    # Prior iron prescription
            -df["RBCTransfusion.pre"] # Exclude if prior RBC transfusion
        );
    
    subDF = df[comboFilter];

    # Extract out subset of features to consider    
    eligibleFeatures = list(availableDiagnostics);
    #eligibleFeatures.extend(outcomeDiagnostics);
    eligibleFeatures.extend(outcomeRx);
    

    # Dataframe subset only counting eligible feature / predictor variables
    subDF = subDF[eligibleFeatures];
    
    return subDF;

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
    
    selector = SelectKBest(chi2, nFeatures);
    xTransformArray = selector.fit_transform(xDF, ySeries);
    xSelectDF = pd.DataFrame(xTransformArray);
    xSelectDF.columns = selector.transform(xDF.columns)[0]; # Re-Map column labels
    xSelectDF.index = xDF.index;
    
    return xSelectDF;

def testModels(xDF,ySeries,kFolds=10):
    # kFolds = Number of cross validation folds
    
    #model.fit(xDF,ySeries);
    #yPred = model.predict(xDF);
    #print precision_recall_fscore_support(ySeries,yPred);
    models = MODELS;
    scoreFxns = SCORE_FXNS;
    for scoreFxn in scoreFxns:
        for model in models:
            scores = cross_val_score(model,xDF,ySeries,cv=kFolds, scoring=scoreFxn);
            print "%.2f (%.2f, %.2f) %s.%s" % (scores.mean(), scores.mean()-scores.std()*2, scores.mean()+scores.std()*2, str(scoreFxn), type(model).__name__);

def driver(dataFrame):
    timer = time.time();

    df = dataFrame;
    
    subDF = filterDataFrame(df);

    imputedDF = imputeMissingValues(subDF);  

    outcomeSeries = (1-imputedDF["ironOutpatient.post"]);
    print("== Outpatient Iron Prescription, Post, %d%% ==" % (sum(outcomeSeries)*100/len(outcomeSeries)) );
    selectedDF = featureSelection(imputedDF, outcomeSeries, 'all'); # But drop outcome variable, otherwise cheating prediction
    testModels(selectedDF, outcomeSeries);

    """
    # http://www.aafp.org/afp/2013/0115/p98.pdf
    # Binary outcome, whether ferritin level > 100.  If so, largely excludes iron deficiency, even inflammed.  
    #   <30 consistent with iron def.  30-100 ambiguous
    outcomeSeries = (imputedDF["FERRITIN.last"] > 100);
    print("== Ferritin > 100, %d%% ==" % (sum(outcomeSeries)*100/len(outcomeSeries)) );
    selectedDF = featureSelection(imputedDF, outcomeSeries, 'all'); # But drop outcome variable, otherwise cheating prediction
    testModels(selectedDF, outcomeSeries);

    outcomeSeries = (imputedDF["FERRITIN.last"] > 50);
    print("== Ferritin > 50, %d%% ==" % (sum(outcomeSeries)*100/len(outcomeSeries)) );
    testModels(selectedDF, outcomeSeries);

    outcomeSeries = (imputedDF["FERRITIN.last"] > 200);
    print("== Ferritin > 200, %d%% ==" % (sum(outcomeSeries)*100/len(outcomeSeries)) );
    testModels(selectedDF, outcomeSeries);

    outcomeSeries = (imputedDF["FERRITIN.last"] > 150);
    print("== Ferritin > 150, %d%% ==" % (sum(outcomeSeries)*100/len(outcomeSeries)) );
    testModels(selectedDF, outcomeSeries);

    outcomeSeries = (imputedDF["FERRITIN.last"] < 50);
    print("== Ferritin < 50, %d%% ==" % (sum(outcomeSeries)*100/len(outcomeSeries)) );
    testModels(selectedDF, outcomeSeries);
    """
    
    timer = time.time() - timer;
    print >> sys.stderr, "%.3f seconds to complete" % timer;
    
    return (selectedDF, imputedDF);

if __name__ == "__main__":
    main(sys.argv);