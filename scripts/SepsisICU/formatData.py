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
from medinfo.dataconversion.DataExtractor import DataExtractor;

CHARLSON_PREFIX = "Charlson.";
TREATMENT_TEAM_PREFIX = "TT.";

# Which flowsheet variables to include in final matrix
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
    "Weight_kg"
);
# How far to look back and forward in time for flowsheet data
FLOWSHEET_PRE_TIME_DELTA = timedelta(-1); # Use up to the past day of flowsheet data
FLOWSHEET_POST_TIME_DELTA = timedelta(+1); # Look into the first day of admission data

# Which laboratory items to include in final matrix (may be sparse)
LAB_BASE_NAMES = \
(   # SAPS = f(BUN, Na, K, HCO3, Bili, WBC, PO2)
    # APACHE = f(pH, Na, K, Cr, Hct, WBC, PO2)
    'WBC','HCT','PLT',
    'NA','K','CO2','BUN','CR',
    'TBIL','ALB',
    'LAC',
    'ESR','CRP',
    'TNI',
    'PHA','PO2A','PCO2A',
    'PHV','PO2V','PCO2V',
);
# How far to look back and forward in time for laboratory results
LAB_PRE_TIME_DELTA = timedelta(-1); # Use up to the last day of lab results
LAB_POST_TIME_DELTA = timedelta(+1); # Look into the first day of admission data

# Threshold volumes and Checkpoint Times to note accumulated isotonic IV Fluids
IVF_THRESHOLD_VOLUMES = [500,1000,2000,3000,4000,5000,6000,7000,8000,9000,10000];  # Volumes (mL) of fluid interested in time until encountering
IVF_CHECKPOINT_TIMES = [1*60*60, 2*60*60, 3*60*60, 4*60*60, 12*60*60, 24*60*60, 48*60*60, 72*60*60];  # Time checkpoints (seconds) interested in accumulated fluid volume by that time

def main(argv=None):
    timer = time.time();

    extractor = DataExtractor();

    # Output file
    featureMatrixFile = stdOpen("featureMatrix.SepsisICU.encounters.tab.gz","w");

    # Final columns to output to patient matrix
    colNames = list();

    patientEpisodes = extractor.parsePatientEpisodeFile(stdOpen("patientEpisodes.tab"), colNames);
    #patientIds = set(columnFromModelList(patientEpisodes, "patient_id"));

    log.info("Expand to index dates based start and end dates");	# But only want one entry per patient
    patientByIndexTimeById = extractor.generateDateRangeIndexTimes("edAdmitTime","dischargeTime", patientEpisodes, colNames, timeInterval=None);

    log.info("Populate flowsheet summary statistics");
    flowsheetByNameByPatientId = extractor.parseFlowsheetFile(stdOpen("Flowsheet.tab.gz"));
    extractor.addFlowsheetFeatures(patientByIndexTimeById, flowsheetByNameByPatientId, FLOWSHEET_NAMES, FLOWSHEET_PRE_TIME_DELTA, FLOWSHEET_POST_TIME_DELTA, colNames);

    log.info("Populate laboratory result summary statistics");
    labsByBaseNameByPatientId = extractor.parseLabResultsFile(stdOpen("LabResults.tab.gz"));
    extractor.addLabFeatures(patientByIndexTimeById, labsByBaseNameByPatientId, LAB_BASE_NAMES, LAB_PRE_TIME_DELTA, LAB_POST_TIME_DELTA, colNames);

    log.info("Populate IV Fluid accumulation");
    ivFluidsByPatientId = extractor.parseIVFluidFile(stdOpen("IsotonicIVFluids.tab.gz"));
    extractor.addIVFluidFeatures(patientByIndexTimeById, ivFluidsByPatientId, IVF_THRESHOLD_VOLUMES, IVF_CHECKPOINT_TIMES, colNames);

    log.info("Record presence of items in terms of relative time to each item from index time");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("IVAntibiotic.tab")), patientByIndexTimeById, colNames,"IVAntibiotic");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("BloodCulture.tab")), patientByIndexTimeById, colNames,"BloodCulture");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("RespViralPanel.tab")), patientByIndexTimeById, colNames,"RespViralPanel");

    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("AnyICULifeSupport.tab")), patientByIndexTimeById, colNames,"AnyICULifeSupport");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("AnyDNR.tab")), patientByIndexTimeById, colNames,"AnyDNR");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("AnyVasoactive.tab")), patientByIndexTimeById, colNames,"AnyVasoactive");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("AnyCRRT.tab")), patientByIndexTimeById, colNames,"AnyCRRT");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("AnyVentilator.tab")), patientByIndexTimeById, colNames,"AnyVentilator");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("ComfortCare.tab")), patientByIndexTimeById, colNames,"ComfortCare");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("PalliativeConsult.tab")), patientByIndexTimeById, colNames,"PalliativeConsult");

    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("Death.tab")), patientByIndexTimeById, colNames,"Death");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("Birth.tab")), patientByIndexTimeById, colNames,"Birth");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("Male.tab")), patientByIndexTimeById, colNames,"Male");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("Female.tab")), patientByIndexTimeById, colNames,"Female");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("RaceWhiteNonHispanicLatino.tab")), patientByIndexTimeById, colNames,"RaceWhiteNonHispanicLatino");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("RaceAsian.tab")), patientByIndexTimeById, colNames,"RaceAsian");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("RaceWhiteHispanicLatino.tab")), patientByIndexTimeById, colNames,"RaceWhiteHispanicLatino");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("RaceHispanicLatino.tab")), patientByIndexTimeById, colNames,"RaceHispanicLatino");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("RaceUnknown.tab")), patientByIndexTimeById, colNames,"RaceUnknown");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("RaceOther.tab")), patientByIndexTimeById, colNames,"RaceOther");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("RaceBlack.tab")), patientByIndexTimeById, colNames,"RaceBlack");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("RacePacificIslander.tab")), patientByIndexTimeById, colNames,"RacePacificIslander");
    extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen("RaceNativeAmerican.tab")), patientByIndexTimeById, colNames,"RaceNativeAmerican");
    
    log.info("Systemically Scan for Charlson comorbidities and Treatment Team categories");
    for filename in os.listdir("."):
        if filename.startswith(CHARLSON_PREFIX):
            diseaseName = filename;
            if filename.endswith(".tab"):
                diseaseName = filename[:-len(".tab")];
            extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen(filename)), patientByIndexTimeById, colNames, diseaseName);

        if filename.startswith(TREATMENT_TEAM_PREFIX):
            teamName = filename;
            if filename.endswith(".tab"):
                teamName = filename[:-len(".tab")];
            extractor.addClinicalItemFeatures(extractor.parseClinicalItemFile(stdOpen(filename)), patientByIndexTimeById, colNames, teamName);

    log.info("Output feature matrix file with row per patient day");
    formatter = TextResultsFormatter(featureMatrixFile);
    formatter.formatTuple(colNames);
    for patientId, patientByIndexTime in patientByIndexTimeById.iteritems():
        patientResults = patientByIndexTime.values();
        formatter.formatResultDicts(patientResults, colNames);

    timer = time.time() - timer;
    print >> sys.stderr, "%.3f seconds to complete" % timer;

if __name__ == "__main__":
    main(sys.argv);