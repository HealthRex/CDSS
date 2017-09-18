# Extract lab orders with marked results that can distinguish between normal vs. abnormal
# Extract out the preceding clinical information to see how well those results can be predicted

import csv
import sys, os;
import time;
from cStringIO import StringIO;
from datetime import datetime, timedelta;
from medinfo.common.Util import stdOpen, log, ProgressDots;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel, modelListFromTable, modelDictFromList, columnFromModelList;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;

from medinfo.dataconversion.DataExtractor import DataExtractor;

# Specify subset of patient IDs to evaluate if just testing small scale
#SAMPLE_PATIENT_IDS = ("-12432455207729","-12434586418575","-12436949623244","-12428492282572","-12441340721352","-12439806620263","-12420916146030","-12431524026341","-12435846176833","-12425000988930","-12424829659809","-12438987905370","-12427531834455","-12425738548110");
#SAMPLE_PATIENT_IDS = ("-12432455207729","-12434586418575","-12436949623244");
SAMPLE_PATIENT_IDS = None
"""
SAMPLE_PATIENT_IDS = []
with open('scripts/LabTestAnalysis/machine_learning/dataExtraction/random_patient_ids_100.csv', 'rb') as f:
    reader = csv.DictReader(f)
    for line in reader:
        SAMPLE_PATIENT_IDS.append(line['pat_id'])
"""

# Specify start and end date for lab order events to look for (if want to work with smaller sample size to start with)
#START_DATE = datetime(2013,1,1);
#END_DATE = datetime(2014,1,1);


ADMIT_DX_CATEGORY_ID = 2;

# Which lab tests to evaluate prediction for. Call these from command-line (driverExtractData.py)
#LAB_PROC_CODES

FLOWSHEET_NAMES = \
(
    "BP_High_Systolic",
    "BP_Low_Diastolic",
    "FiO2",
    "Glasgow Coma Scale Score",
    "Pulse",
    "Resp",
    "Temp",
    "Urine",
);

RESULT_BASE_NAMES = \
(   # SAPS = f(BUN, Na, K, HCO3, Bili, WBC, PO2)
    # APACHE = f(pH, Na, K, Cr, Hct, WBC, PO2)
    'WBC','HCT','PLT',
    'NA','K','CO2','BUN','CR',
    'TBIL','ALB','CA',
    'LAC',
    'ESR','CRP',
    'TNI',
    'PHA','PO2A','PCO2A',
    'PHV','PO2V','PCO2V',
);

LAB_PRE_TIME_DELTAS = [timedelta(-1),timedelta(-3),timedelta(-7),timedelta(-30),timedelta(-90)]; # Look at lab results from the previous days
LAB_POST_TIME_DELTA = timedelta(+0); # Don't look into the future, otherwise cheating the prediction





def main(argv):
    timer = time.time();

    labProcCode = argv[1];
    startDate = DBUtil.parseDateValue(argv[2]);
    endDate = DBUtil.parseDateValue(argv[3]);
    patientEpisodeFilename = None;
    if len(argv) > 4:
        patientEpisodeFilename = argv[4];


    fileLabel = "%s.%s.%s" % (labProcCode, startDate.strftime("%Y-%m-%d"), endDate.strftime("%Y-%m-%d"));
    
    extractor = DataExtractor();
    extractor.dataCache = dict();   # Don't repeat sub-queries for clinical item ID lookups

    log.info("Extract data for %s" % labProcCode);

    patientEpisodes = None;
    if patientEpisodeFilename is None:
        patientEpisodes = queryPatientEpisodes(stdOpen("patientEpisodes.%s.tab" % fileLabel,"w"), labProcCode, startDate, endDate, extractor);    # Maybe just do this first time, then comment out and load from file with line below
    else:
        patientEpisodes = extractor.parsePatientEpisodeFile(stdOpen(patientEpisodeFilename), list()); # Read from prior file if main query already done to avoid expensive query
    #patientIds = set(columnFromModelList(patientEpisodes, "patient_id"));

    #outFile = sys.stdout;
    outFile = stdOpen("labFeatureMatrix.%s.tab.gz" % fileLabel,"w");
    formatter = TextResultsFormatter(outFile);

    lastPatientId = None;
    colNames = None;
    patientEpisodeByIndexTime = None;

    prog = ProgressDots(total=len(patientEpisodes));
    for patientEpisode in patientEpisodes:
        patientId = patientEpisode["patient_id"];

        if lastPatientId is not None and lastPatientId != patientId:
            # New patient ID so start querying for patient specific data and
            #   populating patient episode data
            tempColNames = populatePatientData(patientEpisodeByIndexTime, extractor);
            if colNames is None:    
                # First row, print header row
                colNames = tempColNames;
                formatter.formatTuple(colNames);
            # Print out patient (episode) data (one row per episode)
            formatter.formatResultDicts(patientEpisodeByIndexTime.values(), colNames);

        if lastPatientId is None or lastPatientId != patientId:
            # Prepare to aggregate patient episode record per patient 
            patientEpisodeByIndexTime = dict();

        patientEpisodeByIndexTime[patientEpisode["order_time"]] = patientEpisode;
        lastPatientId = patientId;
        prog.update();
        outFile.flush();
    # Last Iteration
    populatePatientData(patientEpisodeByIndexTime, extractor);
    formatter.formatResultDicts(patientEpisodeByIndexTime.values(), colNames);
    prog.printStatus();

    outFile.close();

    timer = time.time() - timer;
    print >> sys.stderr, "%.3f seconds to complete" % timer;

def queryPatientEpisodes(outputFile, labProcCode, startDate, endDate, extractor):
    """ -- Example query elements
    select cast(pat_id as bigint), pat_enc_csn_id, sop.order_proc_id, proc_code, abnormal_yn, count(result_in_range_yn), count(case result_in_range_yn when 'Y' then 1 else null end), count(ord_num_value)
    from stride_order_proc as sop inner join stride_order_results sor on sop.order_proc_id = sor.order_proc_id
    where proc_code = 'LABMETB'
    and pat_id = '2570758452935'
    group by pat_id, pat_enc_csn_id, sop.order_proc_id, proc_code, abnormal_yn

    Query out lab procs vs. results when available, and count up cases where results are all 'Y' for result_in_range_yn

    """

    conn = DBUtil.connection();
    cursor = conn.cursor();
    try:
        # First pass query to get the list of patients with lab result times
        cohortQuery = SQLQuery();
        cohortQuery.addSelect("cast(pat_id as bigint)");
        cohortQuery.addSelect("pat_enc_csn_id");
        cohortQuery.addSelect("sop.order_proc_id");
        cohortQuery.addSelect("proc_code");
        cohortQuery.addSelect("order_time");
        cohortQuery.addSelect("abnormal_yn");
        cohortQuery.addSelect("count(case result_in_range_yn when 'Y' then 1 else null end)");
        cohortQuery.addSelect("count(ord_num_value)");
        cohortQuery.addFrom("stride_order_proc as sop");
        cohortQuery.addFrom("stride_order_results as sor");
        cohortQuery.addWhere("sop.order_proc_id = sor.order_proc_id");
        cohortQuery.addWhereEqual("proc_code", labProcCode);
        if SAMPLE_PATIENT_IDS is not None:
            cohortQuery.addWhereIn("pat_id", SAMPLE_PATIENT_IDS);
        if startDate is not None:
            cohortQuery.addWhereOp("order_time",">=", startDate);
        if endDate is not None:
            cohortQuery.addWhereOp("order_time","<", endDate);
        cohortQuery.addGroupBy("pat_id, pat_enc_csn_id, sop.order_proc_id, proc_code, order_time, abnormal_yn");
        cursor.execute(str(cohortQuery), cohortQuery.params);

        # This design requires full list of patient episodes to be in memory for now. Revise later to allow streaming process (maybe with intermediary patient episode temp file).
        patientEpisodes = list();

        # Collect Build basic patient ID and datetimes
        row = cursor.fetchone();
        while row is not None:
            (patientId, encounterId, orderProcId, procCode, orderTime, abnormalYN, normalResultCount, totalResultCount) = row;
            patientEpisode = \
                RowItemModel \
                (   {   "patient_id": patientId, 
                        "encounter_id": encounterId,
                        "order_proc_id": orderProcId,
                        "proc_code": procCode,
                        "order_time": orderTime,
                        "abnormal": int(abnormalYN == 'Y'), # Convert to binary 1 vs 0
                        "result_normal_count": normalResultCount,
                        "result_total_count": totalResultCount,
                        "all_result_normal": int(normalResultCount == totalResultCount), # Convert to binary 1 vs 0
                    }
                );
            patientEpisodes.append(patientEpisode);

            row = cursor.fetchone();

        # Drop results as tab-delimited text output
        formatter = TextResultsFormatter(outputFile);
        formatter.formatResultDicts(patientEpisodes, addHeaderRow=True);

        return patientEpisodes;
    finally:
        cursor.close();
        conn.close();

def populatePatientData(patientEpisodeByIndexTime, extractor):
    """Query for specific data relating to the patient designated by the patientEpisodes
    given and populate those episodes with relative data / features.
    Return list of output column names to expect based on populated results.
    """
    # Look for the patient ID based on the contents of the patientEpisodes
    patientId = None;
    labProcCode = None;
    for patientEpisode in patientEpisodeByIndexTime.itervalues():
        patientId = patientEpisode["patient_id"];
        labProcCode = patientEpisode["proc_code"];
        break;

    tempColNames = \
        ["patient_id", "encounter_id", "order_proc_id", "proc_code", "order_time", 
            "abnormal", "result_normal_count", "result_total_count", "all_result_normal"];

    if patientId is not None:
        # Basic Demographics (Age + Gender)
        eventTimes = extractor.parseClinicalItemData_singlePatient( modelListFromTable(extractor.queryClinicalItemsByName(("Birth",), [patientId])) );
        tempColNames.extend( extractor.addClinicalItemFeatures_singlePatient(eventTimes, patientEpisodeByIndexTime, "Birth", daysBins=[]) );
        eventTimes = extractor.parseClinicalItemData_singlePatient( modelListFromTable(extractor.queryClinicalItemsByName(("Male",), [patientId])) );
        tempColNames.extend( extractor.addClinicalItemFeatures_singlePatient(eventTimes, patientEpisodeByIndexTime, "Male", daysBins=[]) );
        eventTimes = extractor.parseClinicalItemData_singlePatient( modelListFromTable(extractor.queryClinicalItemsByName(("Female",), [patientId])) );
        tempColNames.extend( extractor.addClinicalItemFeatures_singlePatient(eventTimes, patientEpisodeByIndexTime, "Female", daysBins=[]) );

        # Race
        eventTimes = extractor.parseClinicalItemData_singlePatient( modelListFromTable(extractor.queryClinicalItemsByName(("RaceWhiteNonHispanicLatino",), [patientId])) );
        tempColNames.extend( extractor.addClinicalItemFeatures_singlePatient(eventTimes, patientEpisodeByIndexTime, "RaceWhiteNonHispanicLatino", daysBins=[]) );
        eventTimes = extractor.parseClinicalItemData_singlePatient( modelListFromTable(extractor.queryClinicalItemsByName(("RaceAsian",), [patientId])) );
        tempColNames.extend( extractor.addClinicalItemFeatures_singlePatient(eventTimes, patientEpisodeByIndexTime, "RaceAsian", daysBins=[]) );
        eventTimes = extractor.parseClinicalItemData_singlePatient( modelListFromTable(extractor.queryClinicalItemsByName(("RaceWhiteHispanicLatino",), [patientId])) );
        tempColNames.extend( extractor.addClinicalItemFeatures_singlePatient(eventTimes, patientEpisodeByIndexTime, "RaceWhiteHispanicLatino", daysBins=[]) );
        eventTimes = extractor.parseClinicalItemData_singlePatient( modelListFromTable(extractor.queryClinicalItemsByName(("RaceHispanicLatino",), [patientId])) );
        tempColNames.extend( extractor.addClinicalItemFeatures_singlePatient(eventTimes, patientEpisodeByIndexTime, "RaceHispanicLatino", daysBins=[]) );
        eventTimes = extractor.parseClinicalItemData_singlePatient( modelListFromTable(extractor.queryClinicalItemsByName(("RaceUnknown",), [patientId])) );
        tempColNames.extend( extractor.addClinicalItemFeatures_singlePatient(eventTimes, patientEpisodeByIndexTime, "RaceUnknown", daysBins=[]) );
        eventTimes = extractor.parseClinicalItemData_singlePatient( modelListFromTable(extractor.queryClinicalItemsByName(("RaceOther",), [patientId])) );
        tempColNames.extend( extractor.addClinicalItemFeatures_singlePatient(eventTimes, patientEpisodeByIndexTime, "RaceOther", daysBins=[]) );
        eventTimes = extractor.parseClinicalItemData_singlePatient( modelListFromTable(extractor.queryClinicalItemsByName(("RaceBlack",), [patientId])) );
        tempColNames.extend( extractor.addClinicalItemFeatures_singlePatient(eventTimes, patientEpisodeByIndexTime, "RaceBlack", daysBins=[]) );
        eventTimes = extractor.parseClinicalItemData_singlePatient( modelListFromTable(extractor.queryClinicalItemsByName(("RacePacificIslander",), [patientId])) );
        tempColNames.extend( extractor.addClinicalItemFeatures_singlePatient(eventTimes, patientEpisodeByIndexTime, "RacePacificIslander", daysBins=[]) );
        eventTimes = extractor.parseClinicalItemData_singlePatient( modelListFromTable(extractor.queryClinicalItemsByName(("RaceNativeAmerican",), [patientId])) );
        tempColNames.extend( extractor.addClinicalItemFeatures_singlePatient(eventTimes, patientEpisodeByIndexTime, "RaceNativeAmerican", daysBins=[]) );

        # Look for most recent any Admit Dx to mark time since admission date
        eventTimes = extractor.parseClinicalItemData_singlePatient( modelListFromTable(extractor.queryClinicalItemsByCategory((ADMIT_DX_CATEGORY_ID,), [patientId])) );
        tempColNames.extend( extractor.addClinicalItemFeatures_singlePatient(eventTimes, patientEpisodeByIndexTime, "AdmitDxDate", daysBins=[]) );

        # Assign time features to reflect time of year (seasonality) and time of day (daily cycle) patterns 
        tempColNames.extend(extractor.addTimeCycleFeatures_singlePatient(patientEpisodeByIndexTime, "order_time", "month"));
        tempColNames.extend(extractor.addTimeCycleFeatures_singlePatient(patientEpisodeByIndexTime, "order_time", "hour"));

        # Extract out lists of ICD9 prefixes per disease category
        icd9prefixesByDisease = dict();
        for row in extractor.loadMapData("CharlsonComorbidity-ICD9CM"):
            (disease, icd9prefix) = (row["charlson"],row["icd9cm"]);
            if disease not in icd9prefixesByDisease:
                icd9prefixesByDisease[disease] = list();
            icd9prefixesByDisease[disease].append("^ICD9."+icd9prefix);
        for disease, icd9prefixes in icd9prefixesByDisease.iteritems():
            disease = disease.translate(None," ()-/");   # Strip off punctuation
            eventTimes = extractor.parseClinicalItemData_singlePatient( modelListFromTable(extractor.queryClinicalItemsByName(icd9prefixes, [patientId], operator="~*")) );
            tempColNames.extend( extractor.addClinicalItemFeatures_singlePatient(eventTimes, patientEpisodeByIndexTime, disease) );

        # Extract out lists of treatment team names per care category
        teamNameByCategory = dict();
        for row in extractor.loadMapData("TreatmentTeamGroups"):
            (category, teamName) = (row["team_category"],row["treatment_team"]);
            if category not in teamNameByCategory:
                teamNameByCategory[category] = list();
            teamNameByCategory[category].append(teamName);
        for category, teamNames in teamNameByCategory.iteritems():
            eventTimes = extractor.parseClinicalItemData_singlePatient( modelListFromTable(extractor.queryClinicalItemsByName(teamNames, [patientId], col="description")) );
            tempColNames.extend( extractor.addClinicalItemFeatures_singlePatient(eventTimes, patientEpisodeByIndexTime, category) );

        # Key feature should be stats on how often the given lab proc_code has been ordered recently
        eventTimes = extractor.parseClinicalItemData_singlePatient( modelListFromTable(extractor.queryClinicalItemsByName((labProcCode,), [patientId])) );
        tempColNames.extend( extractor.addClinicalItemFeatures_singlePatient(eventTimes, patientEpisodeByIndexTime, labProcCode) );

        # Additional key feature is results of previous orders for the same lab test
        resultBaseNames = set(RESULT_BASE_NAMES);   # Start with common lab results to include regardless
        for row in extractor.loadMapData("LabResultMap"):
            if row["proc_code"] == labProcCode and row["base_name"] not in resultBaseNames:
                resultBaseNames.add(row["base_name"]);
        labResultTable = extractor.queryLabResults(resultBaseNames, [patientId]);
        labsByBaseName = extractor.parseLabResultsData_singlePatient(modelListFromTable(labResultTable));
        for preTimeDelta in LAB_PRE_TIME_DELTAS:
            tempColNames.extend( extractor.addLabFeatures_singlePatient(patientEpisodeByIndexTime, labsByBaseName, resultBaseNames, preTimeDelta, LAB_POST_TIME_DELTA) );

    return tempColNames;

if __name__ == "__main__":
    main(sys.argv);
