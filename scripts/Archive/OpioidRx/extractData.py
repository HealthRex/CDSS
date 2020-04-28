import sys, os;
import time;
from datetime import datetime, timedelta;
from io import StringIO;
import numpy as np;
import pandas as pd;
from medinfo.common.Util import stdOpen, log, ProgressDots;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel, modelListFromTable, modelDictFromList;
from medinfo.db.ResultsFormatter import TextResultsFormatter;

DATA_RANGE = ( datetime(2012,1,1), datetime(2014,6,5) );
INTERVENTION_DATE = datetime(2013,9,1);
PRE_PERIOD =  ( datetime(2012,11,1), datetime(2013,6,1) );
POST_PERIOD = ( datetime(2013,11,1), datetime(2014,6,1) );

PRIMARY_LOCATIONS = ('STANFORD FAMILY MEDICINE','STANFORD INTERNAL MEDICINE EAST','STANFORD INTERNAL MEDICINE WEST','STANFORD PRIMARY CARE - PORTOLA VALLEY','ZZSTANFORD INT MED HOOV','ZZSTANFORD INTERNAL MEDICINE EAST','ZZSTANFORD INTERNAL MEDICINE WEST')

# Number of opioid prescriptions within observation period to consider chronic prescription / use
CHRONIC_RX_COUNT = 3;

def main(argv):
    timer = time.time();

    outputFilename = argv[1];
    
    preDF = queryPatients(PRE_PERIOD, PRIMARY_LOCATIONS, CHRONIC_RX_COUNT);
    preDF = queryDemographics(preDF, INTERVENTION_DATE);
    preDF = queryDrugScreens(preDF, PRE_PERIOD, PRIMARY_LOCATIONS );
    # queryReferrals
    # queryPrimaryVisits
    # queryReferralVisits
    # queryERVisits
    # queryEROpioidRx
    # queryOpioidQuantity
    # queryProblemList

    postDF = queryPatients(POST_PERIOD, PRIMARY_LOCATIONS, CHRONIC_RX_COUNT);
    postDF = queryDemographics(postDF, INTERVENTION_DATE);
    postDF = queryDrugScreens(postDF, POST_PERIOD, PRIMARY_LOCATIONS );

    patientDF = pd.concat([preDF,postDF]);
    # Drop results as tab-delimited text output
    #outputFile = stdOpen(outputFilename,"w");
    #formatter = TextResultsFormatter(outputFile);
    #formatter.formatResultDicts(patientById.itervalues(), addHeaderRow=True);
    patientDF.to_csv(outputFilename, sep="\t", index=False);

    
    elapsed = time.time() - timer;
    print("%s to complete" % timedelta(0,round(elapsed)), file=sys.stderr);
    
    return patientDF;

def queryPatients(period, locations, rxCount):
    log.info("Select patients fitting criteria in designated time period: (%s,%s)" % period);

    query = SQLQuery();
    query.addSelect("med.pat_id");
    query.addSelect("count(order_med_id)");
    query.addFrom("stride_mapped_meds as map");
    query.addFrom("stride_order_med as med");
    query.addFrom("stride_patient as pat");
    query.addWhere("analysis_status = 1");
    query.addWhere("map.medication_id = med.medication_id");
    query.addWhere("med.pat_id = pat.pat_id");
    query.addWhere("possible_oncology = 0");
    query.addWhereIn("patient_location", locations );
    query.addWhereOp("ordering_datetime",">", period[0] );
    query.addWhereOp("ordering_datetime","<", period[-1] );
    query.addGroupBy("med.pat_id");
    query.addHaving("count(order_med_id) >2");
    
    results = DBUtil.execute(query);
    cols = ["patientId","nOpioidRx"];
    patientDF = pd.DataFrame(results,columns=cols);
    #patientDF.set_index("patientId",drop=False,inplace=True);

    patientDF["periodStart"] = period[0];   # Identify this group of patient records

    return patientDF;

def queryDemographics(patientDF, baseDate):
    log.info("Populate demographics background for %d patients" % len(patientDF) );
    
    query = SQLQuery();
    query.addSelect("pat_id");
    query.addSelect("%d-birth_year as age" % baseDate.year );
    query.addSelect("gender");
    query.addSelect("primary_race");
    query.addFrom("stride_patient");
    query.addWhereIn("pat_id", patientDF["patientId"] );
    
    results = DBUtil.execute(query);
    cols = ["patientId","age","gender","race"];
    newDF = pd.DataFrame(results,columns=cols);
    return patientDF.merge(newDF, how="left");


def queryDrugScreens( patientDF, period, locations ):
    log.info("Populate drug screens by primary locations");

    query = SQLQuery();
    query.addSelect("pat_id");
    query.addSelect("count(distinct order_proc_id)");
    query.addFrom("stride_order_proc_drug_screen");
    query.addWhere("ordering_mode = 'Outpatient'");
    query.addWhereIn("patient_location", locations );
    query.addWhereOp("ordering_date",">", period[0]);
    query.addWhereOp("ordering_date","<", period[-1]);
    query.addWhereIn("pat_id", patientDF["patientId"] );
    query.addGroupBy("pat_id");

    results = DBUtil.execute(query);
    cols = ["patientId","nDrugScreens"];
    newDF = pd.DataFrame(results,columns=cols);
    patientDF = patientDF.merge(newDF, how="left");
    patientDF["nDrugScreens"][np.isnan(patientDF["nDrugScreens"])] = 0;    # Populate default values if no data
    patientDF["nDrugScreens"] = patientDF["nDrugScreens"].astype("int");    # Beware of float conversion somewhere
    return patientDF;


# queryReferrals
# queryPrimaryVisits
# queryReferralVisits
# queryERVisits
# queryEROpioidRx
# queryOpioidQuantity

def queryProblemList(patientDF):
    pass;

    

#######################################################


if __name__ == "__main__":
    main(sys.argv);