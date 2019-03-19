# Include only those with an order for an antibiotic, blood culture, or respiratory viral panel within 24 hours
# Exclude any patients assigned to a primary surgery team.
# Find index / first clinical item for each with any admission diagnosis
# Then report clinical item features in terms of time until event (and +/- whether occurs at all)
# Report lab and flowsheet value summary statistics within first 24 hours???
# Custom query for IVF. Time until 1L, 2L, 3L, 4L,... Quantity at ICU treatment team assignment, Quantity by AnyICU, Quantity by AnyVasopressor?

import sys, os;
import time;
from cStringIO import StringIO;
from datetime import datetime, timedelta;
from medinfo.common.Util import stdOpen, log, ProgressDots;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel, modelListFromTable, modelDictFromList, columnFromModelList;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;

from medinfo.dataconversion.DataExtractor import DataExtractor;

"""Amount of time to elapse while still counting item days as contiguous.
Use value just greater than whole number of days to make sure greater than difference calculations"""
CONTIGUOUS_THRESHOLD = timedelta(1,1);

# How much time from patient presentation to look for suspected sepsis items
SUSPECT_INTERVAL = timedelta(1);

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

# Identify antibiotics, focus just on IV orders
#IV_MED_CATEGORY_ID = 72;
#PO_MED_CATEGORY_ID = 73;

def main(argv):
    timer = time.time();
    
    extractor = DataExtractor();

    patientEncounters = queryPatientEncounters(stdOpen("patientEncounters.tab","w"), extractor);    # Maybe just do this first time, then comment out and load from file with line below
    #patientEncounters = extractor.parsePatientEncounterFile(stdOpen("patientEncounters.tab"), list()); # Read from prior file if main query already done to avoid expensive query
    patientIds = set(columnFromModelList(patientEncounters, "patient_id"));

    extractor.queryFlowsheet(stdOpen("Flowsheet.tab.gz","w"), FLOWSHEET_NAMES, patientIds);
    extractor.queryLabResults(stdOpen("LabResults.tab.gz","w"), LAB_BASE_NAMES, patientIds);
    
    # Look for specific IV fluid medication subset
    ivfMedIds = set();
    for row in extractor.loadMapData("Medication.IVFluids"):
        if row["group"] == "isotonic":
            ivfMedIds.add(row["medication_id"]);
    extractor.queryIVFluids(stdOpen("IsotonicIVFluids.tab.gz","w"), ivfMedIds, patientIds);

    extractor.queryClinicalItems(stdOpen("IVAntibiotic.tab","w"), loadIVAntibioticItemIds(extractor), patientIds);
    extractor.queryClinicalItems(stdOpen("BloodCulture.tab","w"), loadBloodCultureItemIds(extractor), patientIds);
    extractor.queryClinicalItems(stdOpen("RespViralPanel.tab","w"), loadRespiratoryViralPanelItemIds(extractor), patientIds);

    extractor.queryClinicalItemsByName(stdOpen("AnyICULifeSupport.tab","w"), ("AnyICULifeSupport",), patientIds);
    extractor.queryClinicalItemsByName(stdOpen("AnyDNR.tab","w"), ("AnyDNR",), patientIds);
    extractor.queryClinicalItemsByName(stdOpen("AnyVasoactive.tab","w"), ("AnyVasoactive",), patientIds);
    extractor.queryClinicalItemsByName(stdOpen("AnyCRRT.tab","w"), ("AnyCRRT",), patientIds);
    extractor.queryClinicalItemsByName(stdOpen("AnyVentilator.tab","w"), ("AnyVentilator",), patientIds);
    extractor.queryClinicalItemsByName(stdOpen("ComfortCare.tab","w"), ("^Comfort Care",), patientIds, col="description", operator="~*");
    extractor.queryClinicalItemsByName(stdOpen("PalliativeConsult.tab","w"), ('consult.*palliative',), patientIds, col="description", operator="~*");

    extractor.queryClinicalItemsByName(stdOpen("Death.tab","w"), ("Death",), patientIds);
    extractor.queryClinicalItemsByName(stdOpen("Birth.tab","w"), ("Birth",), patientIds);
    extractor.queryClinicalItemsByName(stdOpen("Male.tab","w"), ("Male",), patientIds);
    extractor.queryClinicalItemsByName(stdOpen("Female.tab","w"), ("Female",), patientIds);
    extractor.queryClinicalItemsByName(stdOpen("RaceWhiteNonHispanicLatino.tab","w"), ("RaceWhiteNonHispanicLatino",), patientIds);
    extractor.queryClinicalItemsByName(stdOpen("RaceAsian.tab","w"), ("RaceAsian",), patientIds);
    extractor.queryClinicalItemsByName(stdOpen("RaceWhiteHispanicLatino.tab","w"), ("RaceWhiteHispanicLatino",), patientIds);
    extractor.queryClinicalItemsByName(stdOpen("RaceHispanicLatino.tab","w"), ("RaceHispanicLatino",), patientIds);
    extractor.queryClinicalItemsByName(stdOpen("RaceUnknown.tab","w"), ("RaceUnknown",), patientIds);
    extractor.queryClinicalItemsByName(stdOpen("RaceOther.tab","w"), ("RaceOther",), patientIds);
    extractor.queryClinicalItemsByName(stdOpen("RaceBlack.tab","w"), ("RaceBlack",), patientIds);
    extractor.queryClinicalItemsByName(stdOpen("RacePacificIslander.tab","w"), ("RacePacificIslander",), patientIds);
    extractor.queryClinicalItemsByName(stdOpen("RaceNativeAmerican.tab","w"), ("RaceNativeAmerican",), patientIds);

    # Extract out lists of ICD9 prefixes per disease category
    icd9prefixesByDisease = dict();
    for row in extractor.loadMapData("CharlsonComorbidity-ICD9CM"):
        (disease, icd9prefix) = (row["charlson"],row["icd9cm"]);
        if disease not in icd9prefixesByDisease:
            icd9prefixesByDisease[disease] = list();
        icd9prefixesByDisease[disease].append("^ICD9."+icd9prefix);
    for disease, icd9prefixes in icd9prefixesByDisease.iteritems():
        disease = disease.translate(None," ()-/");   # Strip off punctuation
        extractor.queryClinicalItemsByName(stdOpen("Charlson."+disease+".tab","w"), icd9prefixes, patientIds, operator="~*");
    
    # Extract out lists of treatment team names per care category
    teamNameByCategory = dict();
    for row in extractor.loadMapData("TreatmentTeamGroups"):
        (category, teamName) = (row["team_category"],row["treatment_team"]);
        if category not in teamNameByCategory:
            teamNameByCategory[category] = list();
        teamNameByCategory[category].append(teamName);
    for category, teamNames in teamNameByCategory.iteritems():
        extractor.queryClinicalItemsByName(stdOpen("TT."+category+".tab","w"), teamNames, patientIds, col="description");

    timer = time.time() - timer;
    print >> sys.stderr, "%.3f seconds to complete" % timer;

def loadIVAntibioticItemIds(extractor):
    # ivMedCategoryId = 72;
    ivMedCategoryId = DBUtil.execute("select clinical_item_category_id from clinical_item_category where description like '%%(Intravenous)'")[0][0];

    # Look for any IV antibiotics based on expected names
    query = SQLQuery();
    query.addSelect("clinical_item_id");
    query.addFrom("clinical_item");
    query.addWhereEqual("analysis_status", 1);
    query.addWhereEqual("clinical_item_category_id", ivMedCategoryId);
    query.openWhereOrClause();
    for row in extractor.loadMapData("IVAntibiotics.Names"):
        query.addWhere("description ~* '%s'" % row["name"] );
    query.closeWhereOrClause();

    ivAntibioticItemIds = set();
    for row in DBUtil.execute(query):
        ivAntibioticItemIds.add(row[0]);
    return ivAntibioticItemIds;

def loadBloodCultureItemIds(extractor):
    # microCategoryId = 15;
    microCategoryId = DBUtil.execute("select clinical_item_category_id from clinical_item_category where description like 'Microbiology'")[0][0];

    # Look for diagnostic tests indicating suspected infection / sepsis
    query = SQLQuery();
    query.addSelect("clinical_item_id");
    query.addFrom("clinical_item");
    query.addWhereEqual("analysis_status", 1);
    query.addWhereIn("clinical_item_category_id", (microCategoryId,) );
    query.addWhere("description ~* '%s'" % 'Blood Culture' );
    bloodCultureItemIds = set();
    for row in DBUtil.execute(query):
        bloodCultureItemIds.add(row[0]);
    return bloodCultureItemIds;

def loadRespiratoryViralPanelItemIds(extractor):
    # labCategoryId = 6;
    labCategoryId = DBUtil.execute("select clinical_item_category_id from clinical_item_category where description like 'Lab'")[0][0];

    query = SQLQuery();
    query.addSelect("clinical_item_id");
    query.addFrom("clinical_item");
    query.addWhereEqual("analysis_status", 1);
    query.addWhereIn("clinical_item_category_id", (labCategoryId,) );
    query.addWhere("description ~* '%s'" % 'Respiratory.*Panel' );
    respiratoryViralPanelItemIds = set();
    for row in DBUtil.execute(query):
        respiratoryViralPanelItemIds.add(row[0]);
    return respiratoryViralPanelItemIds;

def queryPatientEncounters(outputFile, extractor):
    log.info("Select patient admissions with provider category of Tt Pamf Med (Primary) or Tt Med Univ (Primary)");

    conn = DBUtil.connection();
    cursor = conn.cursor();
    try:
        # # Clinical item category for admission diagnoses
        # # ADMIT_DX_CATEGORY_ID = 2;
        # admitDxCategoryId = DBUtil.execute("select clinical_item_category_id from clinical_item_category where description like '%%ADMIT_DX%%'", conn=conn)[0][0];

        # # Look for items indicating suspected infection / sepsis
        # ivAntibioticItemIds = loadIVAntibioticItemIds(extractor);
        # bloodCultureItemIds = loadBloodCultureItemIds(extractor);
        # respiratoryViralPanelItemIds = loadRespiratoryViralPanelItemIds(extractor);

        # # Merge IV antibiotics and blood cultures, respiratory panels as items that suggest sepsis is suspected
        # suspectSepsisItemIds = ivAntibioticItemIds.union(bloodCultureItemIds.union(respiratoryViralPanelItemIds));
        # suspectSepsisItemIdsStr = str.join(',', [str(itemId) for itemId in suspectSepsisItemIds]);   # Convert to comma-separated string via a str.join function on list contracture

        # # Look for primary surgery teams to exclude
        # excludeTeamCategory = "SurgerySpecialty";
        # excludeTreatmentTeams = list();
        # for row in extractor.loadMapData("TreatmentTeamGroups"):
        #     if row["team_category"] == excludeTeamCategory:
        #         excludeTreatmentTeams.append(row["treatment_team"]);
        # query = SQLQuery();
        # query.addSelect("clinical_item_id");
        # query.addFrom("clinical_item");
        # query.addWhereIn("description", excludeTreatmentTeams );
        # excludeTeamItemIds = set();
        # for row in DBUtil.execute(query, conn=conn):
        #     excludeTeamItemIds.add(row[0]);
        # excludeTeamItemIdsStr = str.join(',', [str(itemId) for itemId in excludeTeamItemIds]);   # Convert to comma-separated string via a str.join function on list contracture

        # First pass query to get the list of patients and emergency department presentation times
        cohortQuery = \
        """
        select adt1.pat_anon_id, adt1.pat_enc_csn_anon_id, adt1.shifted_transf_in_dt_tm as edAdmitTime, adt2.shifted_transf_out_dt_tm as dischargeTime
        from stride_adt as adt1, stride_adt as adt2
        where 
            adt1.pat_anon_id in
            (select patient_id from patient_item inner join clinical_item on patient_item.clinical_item_id = clinical_item.clinical_item_id where clinical_item.clinical_item_category_id = 161 AND clinical_item.description = '%s') 
        and adt1.pat_enc_csn_anon_id = adt2.pat_enc_csn_anon_id
        """ % ("Tt Pamf Med (Primary)");

        print >> sys.stderr, cohortQuery;
        cursor.execute(cohortQuery);

        patientEncounters = list();
        patientEncounterById = dict();

        # Collect Build basic patient ID and 
        #   ED presentation dates and Discharge date/time
        prog = ProgressDots();
        row = cursor.fetchone();
        while row is not None:
            (patientId, encounterId, edAdmitTime, dischargeTime) = row;
            #patientId = int(patientId);
            patientEncounter = \
                RowItemModel \
                (   {   "patient_id":patientId, 
                        "edAdmitTime":edAdmitTime, 
                        "dischargeTime":dischargeTime, 
                        "encounter_id":encounterId,
                        "payorTitle": None, # Default encounter data to null in case can't find it later
                        "bpSystolic": None,
                        "bpDiastolic": None,
                        "temperature": None,
                        "pulse": None,
                        "respirations": None,
                    }
                );
            patientEncounters.append(patientEncounter);
            if patientEncounter["encounter_id"] not in patientEncounterById:
                patientEncounterById[patientEncounter["encounter_id"]] = patientEncounter;

            prog.update();
            row = cursor.fetchone();
        prog.printStatus();

        # Second query phase to link to encounter information (e.g., insurance, admitting vital signs)
        encounterIds = columnFromModelList(patientEncounters, "encounter_id");
        query = SQLQuery();
        query.addSelect("pat_id");
        query.addSelect("pat_enc_csn_id");
        query.addSelect("title");
        query.addSelect("bp_systolic");
        query.addSelect("bp_diastolic");
        query.addSelect("temperature");
        query.addSelect("pulse");
        query.addSelect("respirations");
        query.addFrom("stride_patient_encounter");
        query.addWhereIn("pat_enc_csn_id", encounterIds);
        cursor.execute(str(query), query.params);
        row = cursor.fetchone();
        while row is not None:
            (patientId, encounterId, payorTitle, bpSystolic, bpDiastolic, temperature, pulse, respirations) = row;
            if encounterId in patientEncounterById:
                patientEncounter = patientEncounterById[encounterId];
                if patientEncounter["payorTitle"] is None:
                    patientEncounter["payorTitle"] = set();   # Single encounters may have multiple payors to track
                patientEncounter["payorTitle"].add(payorTitle);
                patientEncounter["bpSystolic"] = bpSystolic;
                patientEncounter["bpDiastolic"] = bpDiastolic;
                patientEncounter["temperature"] = temperature;
                patientEncounter["pulse"] = pulse;
                patientEncounter["respirations"] = respirations;
            row = cursor.fetchone();
        
        # Drop results as tab-delimited text output
        formatter = TextResultsFormatter(outputFile);
        formatter.formatResultDicts(patientEncounters, addHeaderRow=True);

        return patientEncounters;
    finally:
        cursor.close();
        conn.close();

if __name__ == "__main__":
    main(sys.argv);
