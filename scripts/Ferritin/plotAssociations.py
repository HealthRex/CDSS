import sys, os;
import time;
from cStringIO import StringIO;

import numpy as np;
import pylab as pl;
from matplotlib.colors import LogNorm;

from medinfo.common.Util import stdOpen, log, ProgressDots;
from medinfo.common.Const import NULL_STRING;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel, RowItemFieldComparator, modelListFromTable, modelDictFromList;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;

INDEX_ITEM_BASE_NAME = "FERRITIN";

labBaseNames = \
(   'FERRITIN','FE','TRFRN','TRFSAT','YSTFRR',
    'WBC','HGB','HCT','MCV','RDW','PLT',
    'RETIC','RETICAB','LDH','HAPTO','TBIL','IBIL','DBIL',
    'CR','ESR','CRP',
);
labCommonByBaseName = \
{   
    'DBIL': 'CONJUGATED BILI',
    'RDW': 'RDW(RDW)',
    'PLT': 'PLATELET COUNT(PLT)',
    'ESR': 'ESR, (AUTOMATED)',
    'HCT': 'HCT(CALC), ISTAT',
    'TRFRN': 'TRANSFERRIN(TRFRN)',
    'LDH': 'LDH, TOTAL, SER/PLAS',
    'RETIC': 'RETIC, %(RETPC)',
    'CRP': 'C-REACTIVE PROTEIN(CRP)',
    'IBIL': 'BILIRUBIN, INDIRECT, SER/PLAS',
    'FERRITIN': 'FERRITIN(FER)',
    'TBIL': 'TOTAL BILIRUBIN(TBIL)',
    'WBC': 'WBC(WBC)',
    'CR': 'CREATININE, SER/PLAS(CR)',
    'HAPTO': 'HAPTOGLOBIN(HAP)',
    'MCV': 'MCV(MCV)',
    'RETICAB': 'RETIC, ABS(RETABS)',
    'HGB': 'HGB(CALC), ISTAT',
    'YSTFRR': 'SOL TRANSFERR REC',
    'TRFSAT': 'TRANSFERRIN SAT',
    'FE': 'IRON, TOTAL'
}

timer = time.time();

featureMatrixFile = stdOpen("featureMatrix.tab");

log.info("Parse feature matrix file");
patientById = dict();
for patient in TabDictReader(featureMatrixFile):
    patientId = int(patient["patient_id"]);
    patient["patient_id"] = patientId;
    for labBaseName in labBaseNames:
        if patient[labBaseName] == NULL_STRING:
            patient[labBaseName] = None;
        else:
            patient[labBaseName] = float(patient[labBaseName]);
    patientById[patientId] = patient;

log.info("Create plots against each metric against the index lab");
for labBaseName in labBaseNames:
    # Construct independent (x) and dependent (y) vectors from available feature data
    yList = list();
    xList = list();
    for patient in patientById.itervalues():
        indexValue = patient[INDEX_ITEM_BASE_NAME];
        featureValue = patient[labBaseName];
        
        if featureValue is not None:    # Skip patients if don't have a value to plot
            yList.append(indexValue);
            xList.append(featureValue);

    nItems = len(xList);
    
    pl.clf();
    pl.plot(xList, yList, 'r.');   # Scatter plot 

    # http://matplotlib.org/examples/pylab_examples/hist2d_log_demo.html
    #pl.hist2d(xList, yList, bins=200, norm=LogNorm());
    #pl.colorbar();

    # http://stackoverflow.com/questions/6148207/linear-regression-with-matplotlib-numpy        
    #fit = pl.polyfit(xList,yList,1);    # Fit 1 dimensional polynomial (i.e., linear regression)
    #fit_fn = pl.poly1d(fit) # fit_fn is now a function which takes in x and returns an estimate for y
    #pl.plot(xList, fit_fn(xList), '--k');   # Fitted line
    
    # Avoid plotting outliers by limiting to 95 percentile values
    yList.sort();
    xList.sort();
    
    yMin = 0;   # yList[int(0.05*len(yList))];
    yMax = yList[int(0.95*nItems)];

    xMin = xList[int(0.05*nItems)];
    xMax = xList[int(0.95*nItems)];

    pl.plot(xList, [100]*nItems, '--');   # Ferritin thresholds
    
    pl.xlim(xMin, xMax);
    pl.ylim(yMin, yMax);

    labCommonName = labCommonByBaseName[labBaseName];
    indexCommonName = labCommonByBaseName[INDEX_ITEM_BASE_NAME];
    
    #pl.grid();
    pl.xlabel("%s - %s" % (labBaseName, labCommonName) );
    pl.ylabel("%s - %s" % (INDEX_ITEM_BASE_NAME, indexCommonName) );
    pl.title("%s vs. %s (%d items)" % (indexCommonName, labCommonName, nItems) );
    pl.savefig("%s-%s.png" % (INDEX_ITEM_BASE_NAME, labBaseName) );

timer = time.time() - timer;
print >> sys.stderr, "%.3f seconds to complete" % timer;
