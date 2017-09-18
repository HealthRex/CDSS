import sys, os;
import time;
from cStringIO import StringIO;

import numpy as np;
import pylab as pl;
from scipy.stats import ttest_ind;

from medinfo.common.Util import stdOpen, log, ProgressDots;
from medinfo.common.Const import NULL_STRING;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel, RowItemFieldComparator, modelListFromTable, modelDictFromList;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;

outcomeNames = ("pre_iron_rx","post_iron_rx");

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
    for outcomeName in outcomeNames:
        patient[outcomeName] = int(patient[outcomeName]);
    patientById[patientId] = patient;

log.info("Create histograms of each metric split against each outcome");
for outcomeName in outcomeNames:
    for labBaseName in labBaseNames:
        labCommonName = labCommonByBaseName[labBaseName];
        
        # Build lab value datasets separated by outcome value
        labValuesByOutcome = {0:list(), 1:list()};  # Start with empty lists for each outcome

        for patient in patientById.itervalues():
            outcome = patient[outcomeName];
            labValue = patient[labBaseName];
            if labValue is not None:    # Skip patients if don't have a value to count
                labValuesByOutcome[outcome].append(labValue);

        # Trim off tails to avoid extreme values
        for outcome, labValues in labValuesByOutcome.iteritems():
            nValues = len(labValues);
            labValues.sort();
            labValuesByOutcome[outcome] = labValues[int(0.05*nValues):int(0.95*nValues)];

        # t-Test for independence
        (tStat, pValue) = ttest_ind( labValuesByOutcome[0], labValuesByOutcome[1], equal_var=False);
        
        # Histogram plotting
        pl.clf();
        nBins = 25;
        data = labValuesByOutcome.values();
        label = ["%s-%s" % (outcomeName,outcome) for outcome in labValuesByOutcome.iterkeys()];

        (n, bins, patches) = pl.hist( data, nBins, histtype='bar', label=label);
        pl.legend();
        pl.xlabel("%s - %s" % (labBaseName, labCommonName) );
        pl.ylabel("Count");
        pl.title("%s vs. %s\n(%d vs. %d items) (p = %.1e)" % (outcomeName, labCommonName, len(labValuesByOutcome[0]), len(labValuesByOutcome[1]), pValue ) );
        pl.savefig("%s-%s.png" % (outcomeName, labBaseName) );

timer = time.time() - timer;
print >> sys.stderr, "%.3f seconds to complete" % timer;
