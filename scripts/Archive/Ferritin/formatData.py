import sys, os;
import time;
import numpy as np;
from datetime import datetime, timedelta;
from cStringIO import StringIO;
from medinfo.common.Util import stdOpen, log, ProgressDots;
from medinfo.common.Const import NULL_STRING;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel, RowItemFieldComparator, modelListFromTable, modelDictFromList;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;
from medinfo.cpoe.Const import SECONDS_PER_DAY;

LAB_PRE_TIME = timedelta(-14);
LAB_POST_TIME = timedelta(+1);

DX_PRE_TIME = timedelta(-14);
DX_POST_TIME = timedelta(+14);

RX_PRE_TIME = timedelta(-14);
RX_POST_TIME = timedelta(+14);

INDEX_ITEM_BASE_NAME = "FERRITIN";

# Ignore labs with this value, looks like a placeholder when missing information or something
LAB_SENTINEL_VALUE = 10000000.0;

LAB_BASE_NAMES = \
(   'FERRITIN','FE','TRFRN','TRFSAT','YSTFRR',
    'WBC','HGB','HCT','MCV','RDW','PLT',
    'RETIC','RETICAB','LDH','HAPTO','TBIL','IBIL','DBIL',
    'CR','ESR','CRP'
);

def main(argv=None):
    timer = time.time();

    # Final columns to output to patient matrix
    colNames = list();

    patientById = parsePatientFile(stdOpen("patients.tab"), colNames);

    labsByBaseNameByPatientId = parseLabResultsFile(stdOpen("labs.tab"));
    addLabFeatures(labsByBaseNameByPatientId, patientById, colNames, INDEX_ITEM_BASE_NAME, LAB_BASE_NAMES, LAB_PRE_TIME, LAB_POST_TIME);


    log.info("Record presence of items in terms of relative time to each item from index time");
    itemTimesByPatientId = parseClinicalItemFile(stdOpen("admitDx.tab"));
    addClinicalItemFeatures(itemTimesByPatientId, patientById, colNames,"ICD9.208-AdmitDx");
    
    itemTimesByPatientId = parseClinicalItemFile(stdOpen("problemListDx.tab"));
    addClinicalItemFeatures(itemTimesByPatientId, patientById, colNames,"ICD9.208-ProblemListDx");
    
    
    itemTimesByPatientId = parseClinicalItemFile(stdOpen("feSO4Rx.tab"));
    addClinicalItemFeatures(itemTimesByPatientId, patientById, colNames,"ironSO4");
    
    itemTimesByPatientId = parseClinicalItemFile(stdOpen("allEnteralIron.tab"));
    addClinicalItemFeatures(itemTimesByPatientId, patientById, colNames,"ironEnteral");
    
    itemTimesByPatientId = parseClinicalItemFile(stdOpen("ironIV.tab"));
    addClinicalItemFeatures(itemTimesByPatientId, patientById, colNames,"ironIV");
    
    itemTimesByPatientId = parseClinicalItemFile(stdOpen("outpatientIronRx.tab"), patientIdCol="pat_id", timeCol="ordering_date");
    addClinicalItemFeatures(itemTimesByPatientId, patientById, colNames,"ironOutpatient");
    
    itemTimesByPatientId = parseClinicalItemFile(stdOpen("transfusions.tab"));
    addClinicalItemFeatures(itemTimesByPatientId, patientById, colNames,"RBCTransfusion");
    
    patientResults = filterPatients(patientById);

    log.info("Output feature matrix file with row per patient");
    featureMatrixFile = stdOpen("featureMatrix.lab14to1day.tab","w");
    formatter = TextResultsFormatter(featureMatrixFile);
    formatter.formatResultDicts(patientResults, colNames, addHeaderRow=True);

    timer = time.time() - timer;
    print >> sys.stderr, "%.3f seconds to complete" % timer;


def parsePatientFile(patientFile, colNames):
    log.info("Parse patient file");
    patientFile = stdOpen("patients.tab");
    patientById = dict();
    for patient in TabDictReader(patientFile):
        patientId = int(patient["patient_id"]);
        patient["patient_id"] = patientId;
        patientById[patientId] = patient;

    colNames.extend(["patient_id","dialysis","surgery"]);
    return patientById;    


def parseClinicalItemFile(itemFile, patientIdCol="patient_id", timeCol="item_date"):
    prog = ProgressDots();
    itemTimesByPatientId = dict();
    for itemData in TabDictReader(itemFile):
        patientId = int(itemData[patientIdCol]);
        itemTime = DBUtil.parseDateValue(itemData[timeCol]);

        itemData[patientIdCol] = patientId;
        itemData[timeCol] = itemTime;

        if patientId not in itemTimesByPatientId:
            itemTimesByPatientId[patientId] = list();
        itemTimesByPatientId[patientId].append( itemTime );

        prog.update();
    prog.printStatus();

    return itemTimesByPatientId;

def addClinicalItemFeatures(itemTimesByPatientId, patientById, colNames, itemLabel):
    # Find items most proximate before and after the index item for each patient
    # Record timedelta separating items found from index item
    preTimeLabel = "%s.preTimeDays" % itemLabel;
    postTimeLabel = "%s.postTimeDays" % itemLabel;
    preLabel = "%s.pre" % itemLabel;
    postLabel = "%s.post" % itemLabel;
    
    for patientId, patient in patientById.iteritems():
        # Initialize values to null for not found
        patient[preTimeLabel] = None;
        patient[postTimeLabel] = None;
        patient[preLabel] = False;
        patient[postLabel] = False;
        
        if "index_time" in patient and patientId in itemTimesByPatientId:  # Index item exists and have items to lookup against
            indexTime = patient["index_time"];

            for itemTime in itemTimesByPatientId[patientId]:
                timeDiffDays = (itemTime - indexTime).total_seconds() / SECONDS_PER_DAY;
                if timeDiffDays < 0: # Item occurred prior to index time
                    if patient[preTimeLabel] is None:
                        patient[preTimeLabel] = timeDiffDays;
                        patient[preLabel] = True;
                    elif abs(timeDiffDays) < abs(patient[preTimeLabel]):
                        # Found an item time more proximate to the index time
                        patient[preTimeLabel] = timeDiffDays;
                else:   # Item occurred after index time
                    if patient[postTimeLabel] is None:
                        patient[postTimeLabel] = timeDiffDays;
                        patient[postLabel] = True;
                    elif abs(timeDiffDays) < abs(patient[postTimeLabel]):
                        # Found an item time more proximate to the index time
                        patient[postTimeLabel] = timeDiffDays;

    colNames.append(preTimeLabel);
    colNames.append(postTimeLabel);
    colNames.append(preLabel);
    colNames.append(postLabel);

def parseLabResultsFile(labFile):
    log.info("Parse lab results file");
    prog = ProgressDots();
    labsByBaseNameByPatientId = dict(); # Dictionary of dictionaries of lists of result items
    for labResult in TabDictReader(labFile):
        if labResult["ord_num_value"] is not None and labResult["ord_num_value"] != NULL_STRING:
            patientId = int(labResult["pat_id"]);
            labBaseName = labResult["base_name"];
            resultValue = float(labResult["ord_num_value"]);
            resultTime = DBUtil.parseDateValue(labResult["result_time"]);

            if resultValue < LAB_SENTINEL_VALUE:    # Skip apparent placeholder values
                labResult["pat_id"] = labResult["patient_id"] = patientId;
                labResult["ord_num_value"] = resultValue;
                labResult["result_time"] = resultTime;

                if patientId not in labsByBaseNameByPatientId:
                    labsByBaseNameByPatientId[patientId] = dict();
                if labBaseName not in labsByBaseNameByPatientId[patientId]:
                    labsByBaseNameByPatientId[patientId][labBaseName] = list();
                labsByBaseNameByPatientId[patientId][labBaseName].append( labResult );

        prog.update();
    prog.printStatus();
    return labsByBaseNameByPatientId;

def addLabFeatures(labsByBaseNameByPatientId, patientById, colNames, indexItemBaseName, labBaseNames, labPreTime, labPostTime):
    log.info("Sort lab results by result time for each patient and find items within specified time period to aggregate");
    prog = ProgressDots();
    for iPatient, (patientId, labsByBaseName) in enumerate(labsByBaseNameByPatientId.iteritems()):
        # Look for the first result of the index item (ferritin)
        indexItem = None;
        if indexItemBaseName in labsByBaseName:
            for labResult in labsByBaseName[indexItemBaseName]:
                if indexItem is None or labResult["result_time"] < indexItem["result_time"]:
                    indexItem = labResult;

        if indexItem is not None:   # Skip this patient if no index item found, should not be possible since pre-screened for relevant patients
            indexTime = indexItem["result_time"];

            patient = patientById[patientId];
            patient["index_time"] = indexTime;

            preTimeLimit = indexTime+labPreTime;
            postTimeLimit = indexTime+labPostTime;

            # Init values for each lab of interest to an empty list
            for labBaseName in labBaseNames:
                # Default to null for all values
                patient["%s.min" % labBaseName] = None;
                patient["%s.max" % labBaseName] = None;
                patient["%s.median" % labBaseName] = None;
                patient["%s.mean" % labBaseName] = None;
                patient["%s.std" % labBaseName] = None;
                patient["%s.first" % labBaseName] = None;
                patient["%s.last" % labBaseName] = None;
                patient["%s.proximate" % labBaseName] = None;
                
                proximateValue = None;
                if labBaseName in labsByBaseName:   # Not all patients will have all labs checked
                    proximateItem = None;   # Item closest to the index item in time
                    valueList = list();
                    for labResult in labsByBaseName[labBaseName]:
                        resultTime = labResult["result_time"];
                        if preTimeLimit <= resultTime and resultTime < postTimeLimit:
                            # Occurs within time frame of interest, so record this value
                            valueList.append(labResult["ord_num_value"]);
                            
                        if proximateItem is None or (abs(resultTime-indexTime) < abs(proximateItem["result_time"]-indexTime)):
                            proximateItem = labResult;
                    proximateValue = proximateItem["ord_num_value"];
                
                    if len(valueList) > 0:
                        patient["%s.min" % labBaseName] = np.min(valueList);
                        patient["%s.max" % labBaseName] = np.max(valueList);
                        patient["%s.median" % labBaseName] = np.median(valueList);
                        patient["%s.mean" % labBaseName] = np.mean(valueList);
                        patient["%s.std" % labBaseName] = np.std(valueList);
                        patient["%s.first" % labBaseName] = valueList[0];   # Assumes previously sorted 
                        patient["%s.last" % labBaseName] = valueList[-1];   #   by result_time
                    patient["%s.proximate" % labBaseName] = proximateValue;

                prog.update();
    colNames.extend(colsFromLabBaseNames(labBaseNames));
    prog.printStatus();

def colsFromLabBaseNames(labBaseNames):
    suffixes = ["min","max","median","mean","std","first","last","proximate"];
    for labBaseName in labBaseNames:
        for suffix in suffixes:
            colName = "%s.%s" % (labBaseName, suffix);
            yield colName;
            
def filterPatients(patientById):
    log.info("Deidentify patient IDs and build data list with adequate data");
    patientResults = list();
    for iPatient, patient in enumerate(patientById.itervalues()):
        # Further deidentify patients by applying sequential ID
        patient["pat_id"] = patient["patient_id"] = iPatient;
        # Only accept patients where an index item and times were found
        if "index_time" in patient:
            patientResults.append(patient);
    return patientResults;

if __name__ == "__main__":
    main(sys.argv);