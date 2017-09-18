import sys, os;
import time;
from cStringIO import StringIO;
from medinfo.common.Util import stdOpen, log, ProgressDots;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel, modelListFromTable, modelDictFromList;
from medinfo.db.ResultsFormatter import TextResultsFormatter;

def main(argv):
    timer = time.time();

    patientById = queryPatients(stdOpen("patients.tab","w"));
    #queryLabResults(stdOpen("labs.tab","w"), patientById); # Time intensive, ~20 minutes

    queryClinicalItems(stdOpen("transfusions.tab","w"), (3648,), patientById);  # RBC Transfusions
    queryClinicalItems(stdOpen("problemListDx.tab","w"), (14568,14606,14847,20636), patientById); # Iron Def Anemia Problem List
    queryClinicalItems(stdOpen("admitDx.tab","w"), (17172,20125,21873), patientById); # Iron Def Admission Diagnosis

    ##################################################
    # Iron prescription ID notes
    
    # Mostly oral supplements and vitamins, dominated by ferrous sulfate
    ironSulfateItemIds = (34,1044,1047,1280,1386);  # Mostly first one for PO route, others are smattering of feeding tube route
    # Dominated by first PO Multi-Vitamin (2800 vs 90 for second)
    otherEnteralIronItemIds = (83,208,349,732,1188,1376,1460,1707,1768,1996,2000,2085,2140,2162,2322,2569,2855,3124,3130,3234,3241,3242,3305,3309,3367,3380,3384,3414,3532);
    allEnteralIronItemIds = set(ironSulfateItemIds).union(otherEnteralIronItemIds);
    # IV iron formulations
    ivIronClinicalItemIds = (893,1129,720,1304,1490,3403);

    queryClinicalItems(stdOpen("feSO4Rx.tab","w"), ironSulfateItemIds, patientById); # FeSO4 (Enteral, primarily PO)
    queryClinicalItems(stdOpen("allEnteralIron.tab","w"), allEnteralIronItemIds, patientById); # All Enteral Iron formulations, including FeSO4, FeGluconate, and assorted MVI, etc.
    queryClinicalItems(stdOpen("ironIV.tab","w"), ivIronClinicalItemIds, patientById); # IV Iron (sucrose, dextran, gluconate, etc.)

    queryOutpatientIronRx(stdOpen("outpatientIronRx.tab","w"), patientById);
    
    timer = time.time() - timer;
    print >> sys.stderr, "%.3f seconds to complete" % timer;

def queryPatients(outputFile):
    log.info("Select patients with any result for a ferritin test");
    patientById = dict();
    query = \
        """select distinct pat_id
        from 
          stride_order_results as sor,
          stride_order_proc as sop
        where 
          sor.order_proc_id = sop.order_proc_id and
          base_name = 'ferritin'
        """;
    results = DBUtil.execute(query);
    for (patientId,) in results:
        patientId = int(patientId);
        patientById[patientId] = RowItemModel({"patient_id": patientId});
        

    log.info("Patients with admit or diet orders for surgery"); # Not perfectly accurate for isolating surgical patients
    for patient in patientById.itervalues():
        patient["surgery"] = 0; # Default to 0 / false
    query = \
        """select distinct patient_id
        from patient_item
        where clinical_item_id in (3614,4177,4220)
        """;
    results = DBUtil.execute(query);
    for (patientId,) in results:
        if patientId in patientById:
            patientById[patientId]["surgery"] = 1;

    log.info("Patients with an order for dialysis");    # (Does not differentiate acute vs. chronic.  Includes peritoneal)
    for patient in patientById.itervalues():
        patient["dialysis"] = 0; # Default to 0 / false
    query = \
        """select distinct patient_id
        from patient_item
        where clinical_item_id in (1815,3783,4322)
        """;
    results = DBUtil.execute(query);
    for (patientId,) in results:
        if patientId in patientById:
            patientById[patientId]["dialysis"] = 1;

    # Drop results as tab-delimited text output
    formatter = TextResultsFormatter(outputFile);
    formatter.formatResultDicts(patientById.itervalues(), addHeaderRow=True);

    return patientById;    

#######################################################

def queryClinicalItems(outputFile,clinicalItemIds,patientById):
    log.info("Query Clinical Items: %s" % str(clinicalItemIds) );
    formatter = TextResultsFormatter(outputFile);

    colNames = ["patient_id","item_date"];

    query = SQLQuery();
    for col in colNames:
        query.addSelect(col);
    query.addFrom("patient_item");
    query.addWhereIn("clinical_item_id", clinicalItemIds );
    query.addWhereIn("patient_id", patientById.viewkeys() );
    query.addOrderBy("patient_id");
    query.addOrderBy("item_date");

    DBUtil.execute( query, includeColumnNames=True, formatter=formatter );  # Stream output to formatter to avoid keeping results in memory

#######################################################

def queryLabResults(outputFile, patientById):
    log.info("Query out lab results, takes a while");
    labBaseNames = \
    (   'ferritin','fe','trfrn','trfsat','ystfrr',
        'wbc','hgb','hct','mcv','rdw','plt',
        'retic','reticab','ldh','hapto','tbil','ibil','dbil',
        'cr','esr','crp'
    );

    formatter = TextResultsFormatter(outputFile);

    # Query rapid when filter by lab result type, limited to X records.  
    # Filtering by patient ID drags down substantially until preloaded table by doing a count on the SOR table?
    colNames = ["pat_id","base_name","common_name","ord_num_value","reference_unit","result_flag","sor.result_time"];

    query = SQLQuery();
    for col in colNames:
        query.addSelect(col);
    query.addFrom("stride_order_results as sor, stride_order_proc as sop");
    query.addWhere("sor.order_proc_id = sop.order_proc_id");
    query.addWhereIn("base_name", labBaseNames );
    query.addWhereIn("pat_id", patientById.viewkeys() );
    query.addOrderBy("pat_id");
    query.addOrderBy("sor.result_time");

    DBUtil.execute( query, includeColumnNames=True, formatter=formatter );  # Stream output to formatter to avoid keepign all results in memory

###########################################
def queryOutpatientIronRx(outputFile, patientById):
    log.info("Query outpatient Iron prescriptions");

    # Medication IDs derived by mapping through Iron as an ingredient
    poIronIngredientMedicationIds = (3065,3066,3067,3071,3074,3077,3986,7292,11050,25006,26797,34528,39676,78552,79674,83568,84170,85151,96118,112120,112395,113213,126035,198511,200455,201994,201995,203679,207059,207404,208037,208072);
    # Medication IDs directly from prescriptions, formulations that did not map through RxNorm
    poIronDirectMedicationIds = (111354,540526,205010,121171,111320,82791,93962,201795,206722,201068,116045,208725,111341,206637,112400,210256,77529,20844,83798,205523,112428,125474,111343);
    allEnteralIronMedicationIds = set(poIronIngredientMedicationIds).union(poIronDirectMedicationIds);
    
    formatter = TextResultsFormatter(outputFile);

    colNames = ["pat_id","ordering_date"];

    query = SQLQuery();
    for col in colNames:
        query.addSelect(col);
    query.addFrom("stride_order_med");
    query.addWhereIn("medication_id", allEnteralIronMedicationIds );
    query.addWhereIn("pat_id", patientById.viewkeys() );
    query.addOrderBy("pat_id");
    query.addOrderBy("ordering_date");

    DBUtil.execute( query, includeColumnNames=True, formatter=formatter );  # Stream output to formatter to avoid keepign all results in memory


if __name__ == "__main__":
    main(sys.argv);