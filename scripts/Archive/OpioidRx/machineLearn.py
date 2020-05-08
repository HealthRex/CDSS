import sys, os;
import time;
from datetime import timedelta;
from io import StringIO;
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

INPUT_COLS = ["postIntervention","age","Male","White","Black or African American","nOpioidRx"];
OUTCOME_COL = "hasDrugScreens";

MODELS = \
        [   DummyClassifier(),
            DummyClassifier('most_frequent'),
            LogisticRegression(), 
            #LogisticRegression(penalty="l1"), #    "LASSO" for logistic regression
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

DATE_COLS = ["periodStart"];

def main(argv):
    timer = time.time();
    inFilename = argv[1];
    df = dataFrame = pd.read_table(inFilename, parse_dates=DATE_COLS);
    
    ySeries = df[OUTCOME_COL];  # Outcome column
    xDF = df[INPUT_COLS];
    #testModels(xDF, ySeries);
    model = logisticRegressionInterpret(xDF,ySeries);

    elapsed = time.time() - timer;
    print("%s seconds to complete" % timedelta(0, round(elapsed)), file=sys.stderr);
    
    return model;

def logisticRegressionInterpret(xDF,ySeries):
    model = LogisticRegression();
    model.fit(xDF,ySeries);
    print(np.exp(model.coef_))
    print(model.intercept_)
    return model;
    
    
def testModels(xDF,ySeries,kFolds=10,models=None,scoreFxns=None):
    # kFolds = Number of cross validation folds
    
    #model.fit(xDF,ySeries);
    #yPred = model.predict(xDF);
    #print precision_recall_fscore_support(ySeries,yPred);
    if models is None:
        models = MODELS;
    if scoreFxns is None:
        scoreFxns = SCORE_FXNS;

    for scoreFxn in scoreFxns:
        for model in models:
            scores = cross_val_score(model,xDF,ySeries,cv=kFolds, scoring=scoreFxn);
            print("%.2f (%.2f, %.2f) %s.%s" % (scores.mean(), scores.mean()-scores.std()*2, scores.mean()+scores.std()*2, str(scoreFxn), type(model).__name__));

if __name__ == "__main__":
    main(sys.argv);