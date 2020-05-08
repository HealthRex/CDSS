import sys, os;
import time;
from io import StringIO;
from datetime import datetime, timedelta;
from medinfo.common.Util import stdOpen, log, ProgressDots;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery, RowItemModel, modelListFromTable, modelDictFromList, columnFromModelList;
from medinfo.db.ResultsFormatter import TextResultsFormatter, TabDictReader;

from medinfo.dataconversion.DataExtractor import DataExtractor;

"""Amount of time to elapse while still counting item days as contiguous.
Use value just greater than whole number of days to make sure greater than difference calculations"""
CONTIGUOUS_THRESHOLD = timedelta(1,1);

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

TREATMENT_TEAM_MAP_TEXT = \
"""Medicine\tTt Med Univ (Primary)
CCU-HF\tTt Ccu/Hf (Primary)
Medicine\tTt Pamf Med (Primary)
MICU\tTt Micu (Primary)
HemeOnc\tTt Oncology (Primary)
HemeOnc\tTt Med9 (Primary)
HemeOnc\tTt Hematology (Primary)
Trauma\tTt Acute Care Surgery Trauma (Primary)
CVICU\tTt Cvicu Team (Primary)
SICU\tTt Sicu (Primary)
Cardiology\tTt Cardiac Adult (Primary)
Transplant\tTt Bmt (Primary)
SurgerySpecialty\tTt Neurosurgery Floor (Primary)
SurgerySpecialty\tTt Ortho Arthritis (Joint) (Primary)
SurgerySpecialty\tTt Ortho Trauma (Primary)
Cardiology\tTt Gen Cards (Primary)
SurgerySpecialty\tTt Colorectal Surgery (Primary)
Neurology\tTt Neuro Stroke (Primary)
SurgerySpecialty\tTt Surgical Oncology (Primary)
SurgerySpecialty\tTt Urology (Primary)
Neurology\tTt Neurology (Primary)
SurgerySpecialty\tTt Ent Head And Neck (Primary)
SurgerySpecialty\tTt Minimally Invasive Surgery (Primary)
SurgerySpecialty\tTt Vascular Surgery (Primary)
SurgerySpecialty\tTt General Thoracic (Primary)
SurgerySpecialty\tTt Hpb Surgery (Primary)
SurgerySpecialty\tTt Neurosurgery Spine Floor (Primary)
Medicine\tTt Med Nocturnist (Primary)
Transplant\tTt Lung Transplant (Primary)
SurgerySpecialty\tTt Gyn Onc (Primary)
SurgerySpecialty\tTt Plastic Surgery (Primary)
SurgerySpecialty\tTt Neurosurgery Tumor Floor (Primary)
MICU\tTt Neurosurgery Icu/Resident On-Call (Primary)
Transplant\tTt Med Tx Hep (Primary)
SurgerySpecialty\tTt Ortho Spine (Primary)
Cardiology\tTt Cardiology Ep (Primary)
SurgerySpecialty\tTt Pamf (Neurosurg) (Primary)
SurgerySpecialty\tTt Neurosurgery Vascular Floor (Primary)
Neurology\tTt Neuro Epilepsy Monitor Unit (Primary)
SurgerySpecialty\tTt Ent Specialty (Primary)
Medicine\tTt Cystic Fibrosis Adult (Primary)
Transplant\tTt Kidney Pancreas Transplant (Primary)
Medicine\tTt Acute Pain 2Pain (Primary)
SICU\tTt Neurosurgery Vascular Icu (Primary)
SurgerySpecialty\tTt Ortho Shoulder/Elbow (Primary)
SICU\tTt Neurosurgery Tumor Icu (Primary)
Medicine\tTt Chronic Pain (Primary)
SurgerySpecialty\tTt Gyn Private (Primary)
Medicine\tTt Pulm Htn (Primary)
SurgerySpecialty\tTt Gyn Univ (Primary)
Transplant\tTt Liver Transplant (Primary)
SurgerySpecialty\tTt Ortho Foot/Ankle (Primary)
SurgerySpecialty\tTt Ortho Oncology (Primary)
SurgerySpecialty\tTt Breast Surgery (Primary)
SICU\tTt Neurosurgery Spine Icu (Primary)
SurgerySpecialty\tTt Gen Surg (Primary)
SurgerySpecialty\tTt Ortho Tumor (Primary)
Transplant\tTt Med Tx-Hep (Primary)
Transplant\tTt Heart Lung Transplant (Primary)
Transplant\tTt Heart Transplant/Vad (Primary)
Medicine\tTt Chris Mow (Primary)
Medicine\tTt Med Pamf (Primary)
Medicine\tTt Pain (Primary)
SurgerySpecialty\tTt Neurosurgery (Primary)
Transplant\tTt Pulmonary Transplant (Primary)
Cardiology\tTt Cardiology Arrhythmia (Primary)
SurgerySpecialty\tTt Interventional Radiology (Primary)
SurgerySpecialty\tTt Ent Head Neck (Primary)
SurgerySpecialty\tTt Hand Surgery (Primary)
SurgerySpecialty\tTt Ortho Joint (Primary)
SurgerySpecialty\tTt Ortho Foot Ankle (Primary)
SurgerySpecialty\tTt Ortho Surgery (Primary)
SurgerySpecialty\tTt Interventional Radiology 2Rads (Primary)
SurgerySpecialty\tTt Ortho Hand (Primary)
Psychiatry\tTt Psychiatry (Primary)
SurgerySpecialty\tTt Ortho Sports (Primary)
Cardiology\tTt Cardiology Interventional (Primary)
SurgerySpecialty\tTt Ob University (Primary)
SurgerySpecialty\tTt Pamf(Ortho) (Primary)
SurgerySpecialty\tTt Pamf(Plastics) (Primary)
SurgerySpecialty\tTt Plastic Surgery Consults (Primary)
Medicine\tTt Pamf Med/Cards Admitting (Primary)
Medicine\tTt Med Team (Primary)
SurgerySpecialty\tTt Hearttransplant Surgery (Primary)
Transplant\tTt Med Tx Cards (Primary)
Transplant\tTt Med Tx Renal (Primary)
SurgerySpecialty\tTt Pamf (Gen Surg) (Primary)
SurgerySpecialty\tTt Craniofacial Surgery (Primary)
SurgerySpecialty\tTt Vad (Primary)
SurgerySpecialty\tTt Ophthalmology (Primary)
SurgerySpecialty\tTt Ob San Mateo County (Primary)
SurgerySpecialty\tTt Pamf(Urology) (Primary)
Cardiology\tTt Pamf(Ep) (Primary)
SurgerySpecialty\tTt Pamf(Ent) (Primary)
Medicine\tTt Physical Med Rehab (Primary)
Transplant\tTt Bmt (Bmt) (Primary)
Cardiology\tTt Cardiology (Primary)
"""


CHARLSON_ICD9_MAP_TEXT = \
"""MI\t420
MI\t412
CHF\t398
CHF\t398.91
CHF\t402.01
CHF\t402.11
CHF\t402.91
CHF\t404.01
CHF\t404.03
CHF\t404.11
CHF\t404.13
CHF\t404.91
CHF\t404.93
CHF\t425.4
CHF\t425.5
CHF\t425.6
CHF\t425.7
CHF\t425.8
CHF\t425.9
CHF\t428
PeripheralVascular\t093.0
PeripheralVascular\t437.3
PeripheralVascular\t440
PeripheralVascular\t441
PeripheralVascular\t443.1
PeripheralVascular\t443.2
PeripheralVascular\t443.3
PeripheralVascular\t443.4
PeripheralVascular\t443.5
PeripheralVascular\t443.6
PeripheralVascular\t443.7
PeripheralVascular\t443.8
PeripheralVascular\t443.9
PeripheralVascular\t557.1
PeripheralVascular\t557.9
PeripheralVascular\tV43.4
Cerebrovascular\t362.34
Cerebrovascular\t430
Cerebrovascular\t431
Cerebrovascular\t432
Cerebrovascular\t433
Cerebrovascular\t434
Cerebrovascular\t435
Cerebrovascular\t436
Cerebrovascular\t437
Cerebrovascular\t438
Dementia\t290
Dementia\t294.1
Dementia\t331.2
COPD\t416.8
COPD\t 416.9
COPD\t490
COPD\t491
COPD\t492
COPD\t493
COPD\t494
COPD\t495
COPD\t496
COPD\t497
COPD\t498
COPD\t499
COPD\t500
COPD\t501
COPD\t502
COPD\t503
COPD\t504
COPD\t505
COPD\t506.4
COPD\t508.1
COPD\t 508.8
Rheumatic\t446.5
Rheumatic\t710.0
Rheumatic\t710.1
Rheumatic\t710.2
Rheumatic\t710.3
Rheumatic\t710.4
Rheumatic\t714.0
Rheumatic\t714.1
Rheumatic\t714.2
Rheumatic\t714.8
Rheumatic\t725
Peptic Ulcer\t531
Peptic Ulcer\t532
Peptic Ulcer\t533
Peptic Ulcer\t534
Liver Mild\t070.22
Liver Mild\t070.23
Liver Mild\t 070.32
Liver Mild\t070.33
Liver Mild\t070.44
Liver Mild\t070.54
Liver Mild\t070.6
Liver Mild\t070.9
Liver Mild\t570
Liver Mild\t571
Liver Mild\t573.3
Liver Mild\t573.4
Liver Mild\t573.8
Liver Mild\t 573.9
Liver Mild\tV42.7
Diabetes\t250.0
Diabetes\t250.1
Diabetes\t250.2
Diabetes\t250.3
Diabetes\t250.8
Diabetes\t250.9
DiabetesComplications\t250.4
DiabetesComplications\t250.5
DiabetesComplications\t250.6
DiabetesComplications\t250.7
Hemiplegia Paraplegia\t334.1
Hemiplegia Paraplegia\t342
Hemiplegia Paraplegia\t343
Hemiplegia Paraplegia\t344.0
Hemiplegia Paraplegia\t344.1
Hemiplegia Paraplegia\t344.2
Hemiplegia Paraplegia\t344.3
Hemiplegia Paraplegia\t344.4
Hemiplegia Paraplegia\t344.5
Hemiplegia Paraplegia\t344.6
Hemiplegia Paraplegia\t344.9
Renal\t403.01
Renal\t403.11
Renal\t403.91
Renal\t404.02
Renal\t404.03
Renal\t404.12
Renal\t404.13
Renal\t404.92
Renal\t404.93
Renal\t582
Renal\t583.0
Renal\t583.1
Renal\t583.2
Renal\t583.3
Renal\t583.4
Renal\t583.5
Renal\t583.6
Renal\t583.7
Renal\t585
Renal\t586
Renal\t588.0
Renal\tV42.0
Renal\tV45.1
Renal\tV56
Malignancy\t140
Malignancy\t140
Malignancy\t141
Malignancy\t142
Malignancy\t143
Malignancy\t144
Malignancy\t145
Malignancy\t146
Malignancy\t147
Malignancy\t148
Malignancy\t149
Malignancy\t150
Malignancy\t151
Malignancy\t152
Malignancy\t153
Malignancy\t154
Malignancy\t155
Malignancy\t156
Malignancy\t157
Malignancy\t158
Malignancy\t159
Malignancy\t160
Malignancy\t161
Malignancy\t162
Malignancy\t163
Malignancy\t164
Malignancy\t165
Malignancy\t166
Malignancy\t167
Malignancy\t168
Malignancy\t169
Malignancy\t170
Malignancy\t171
Malignancy\t172
Malignancy\t174
Malignancy\t175
Malignancy\t176
Malignancy\t177
Malignancy\t178
Malignancy\t179
Malignancy\t180
Malignancy\t181
Malignancy\t182
Malignancy\t183
Malignancy\t184
Malignancy\t185
Malignancy\t186
Malignancy\t187
Malignancy\t188
Malignancy\t189
Malignancy\t190
Malignancy\t191
Malignancy\t192
Malignancy\t193
Malignancy\t194
Malignancy\t195.0
Malignancy\t195.1
Malignancy\t195.2
Malignancy\t195.3
Malignancy\t195.4
Malignancy\t195.5
Malignancy\t195.6
Malignancy\t195.7
Malignancy\t195.8
Malignancy\t200
Malignancy\t201
Malignancy\t202
Malignancy\t203
Malignancy\t204
Malignancy\t205
Malignancy\t206
Malignancy\t207
Malignancy\t208
Malignancy\t238.6
Liver ModSevere\t456.0
Liver ModSevere\t456.1
Liver ModSevere\t456.2
Liver ModSevere\t572.2
Liver ModSevere\t572.3
Liver ModSevere\t572.4
Liver ModSevere\t572.5
Liver ModSevere\t572.6
Liver ModSevere\t572.7
Liver ModSevere\t572.8
Malignancy Metastatic\t196
Malignancy Metastatic\t197
Malignancy Metastatic\t198
Malignancy Metastatic\t199
AIDS/HIV\t042
AIDS/HIV\t043
AIDS/HIV\t044
"""

def main(argv):
    timer = time.time();
    
    extractor = DataExtractor();

    #patientById = queryPatients(stdOpen("patients.tab","w"));
    patientById = extractor.parsePatientFile(stdOpen("patients.tab"), list()); # Read from prior file if main query already done to avoid expensive query

    extractor.queryFlowsheet(FLOWSHEET_NAMES, patientById, stdOpen("Flowsheet.tab.gz","w"));

    extractor.queryLabResults(LAB_BASE_NAMES, patientById, stdOpen("LabResults.tab.gz","w"));

    extractor.queryClinicalItemsByName(("AnyICULifeSupport",), patientById, stdOpen("AnyICULifeSupport.tab","w"));
    extractor.queryClinicalItemsByName(("AnyDNR",), patientById, stdOpen("AnyDNR.tab","w"));
    extractor.queryClinicalItemsByName(("AnyVasoactive",), patientById, stdOpen("AnyVasoactive.tab","w"));
    extractor.queryClinicalItemsByName(("AnyCRRT",), patientById, stdOpen("AnyCRRT.tab","w"));
    extractor.queryClinicalItemsByName(("AnyVentilator",), patientById, stdOpen("AnyVentilator.tab","w"));
    extractor.queryClinicalItemsByName(("^Comfort Care",), patientById, stdOpen("ComfortCare.tab","w"), col="description", operator="~*");
    extractor.queryClinicalItemsByName(('consult.*palliative',), patientById, stdOpen("PalliativeConsult.tab","w"), col="description", operator="~*");

    extractor.queryClinicalItemsByName(("Death",), patientById, stdOpen("Death.tab","w"));
    extractor.queryClinicalItemsByName(("Birth",), patientById, stdOpen("Birth.tab","w"));
    extractor.queryClinicalItemsByName(("Male",), patientById, stdOpen("Male.tab","w"));
    extractor.queryClinicalItemsByName(("Female",), patientById, stdOpen("Female.tab","w"));
    extractor.queryClinicalItemsByName(("RaceWhiteNonHispanicLatino",), patientById, stdOpen("RaceWhiteNonHispanicLatino.tab","w"));
    extractor.queryClinicalItemsByName(("RaceAsian",), patientById, stdOpen("RaceAsian.tab","w"));
    extractor.queryClinicalItemsByName(("RaceWhiteHispanicLatino",), patientById, stdOpen("RaceWhiteHispanicLatino.tab","w"));
    extractor.queryClinicalItemsByName(("RaceHispanicLatino",), patientById, stdOpen("RaceHispanicLatino.tab","w"));
    extractor.queryClinicalItemsByName(("RaceUnknown",), patientById, stdOpen("RaceUnknown.tab","w"));
    extractor.queryClinicalItemsByName(("RaceOther",), patientById, stdOpen("RaceOther.tab","w"));
    extractor.queryClinicalItemsByName(("RaceBlack",), patientById, stdOpen("RaceBlack.tab","w"));
    extractor.queryClinicalItemsByName(("RacePacificIslander",), patientById, stdOpen("RacePacificIslander.tab","w"));
    extractor.queryClinicalItemsByName(("RaceNativeAmerican",), patientById, stdOpen("RaceNativeAmerican.tab","w"));

    # Extract out lists of ICD9 prefixes per disease category
    icd9prefixesByDisease = dict();
    for line in StringIO(CHARLSON_ICD9_MAP_TEXT):
        (disease, icd9prefix) = line.strip().split("\t");
        if disease not in icd9prefixesByDisease:
            icd9prefixesByDisease[disease] = list();
        icd9prefixesByDisease[disease].append("^ICD9."+icd9prefix);
    for disease, icd9prefixes in icd9prefixesByDisease.items():
        disease = disease.translate(None," ()-/");   # Strip off punctuation
        extractor.queryClinicalItemsByName(icd9prefixes, patientById, stdOpen("Charlson."+disease+".tab","w"), operator="~*");
    
    # Extract out lists of treatment team names per care category
    teamNameByCategory = dict();
    for line in StringIO(TREATMENT_TEAM_MAP_TEXT):
        (category, teamName) = line.strip().split("\t");
        if category not in teamNameByCategory:
            teamNameByCategory[category] = list();
        teamNameByCategory[category].append(teamName);
    for category, teamNames in teamNameByCategory.items():
        extractor.queryClinicalItemsByName(teamNames, patientById, stdOpen("TT."+category+".tab","w"), col="description");
    
    timer = time.time() - timer;
    print("%.3f seconds to complete" % timer, file=sys.stderr);

def queryPatients(outputFile):
    log.info("Select patients with any ICU life support orders and follow contiguous date trail for apparent hospitalization (long query >20 min)...");
    
    conn = DBUtil.connection();
    cursor = conn.cursor();
    try:
        anyLifeSupportItemId = DBUtil.execute("select clinical_item_id from clinical_item where name = 'AnyICULifeSupport'", conn=conn)[0][0];

        patientById = dict();
        query = \
            """select pi.patient_id, date_trunc('day',pi.item_date), min(pi.encounter_id), count(pi.patient_item_id)
            from patient_item as pi,
            (
                select pi2.patient_id, min(pi2.item_date) as firstLifeSupportDate
                    from patient_item as pi2
                    where pi2.clinical_item_id = %s
                    group by pi2.patient_id
            ) as piX
            where pi.patient_id = piX.patient_id
            and pi.item_date >= piX.firstLifeSupportDate
            group by pi.patient_id, date_trunc('day',pi.item_date)
            order by pi.patient_id, date_trunc('day',pi.item_date)
            """ % anyLifeSupportItemId;
        cursor.execute(query);

        row = cursor.fetchone();
        while row is not None:
            (patientId, itemDate, encounterId, itemCount) = row;
            patientId = int(patientId);
            if patientId not in patientById:
                patientById[patientId] = \
                    RowItemModel \
                    (   {   "patient_id":patientId, 
                            "firstLifeSupportDate":itemDate, 
                            "lastContiguousDate":itemDate, 
                            "encounter_id":encounterId, # Assumes single value that won't be overwritten
                            "payorTitle": None, # Default encounter data to null in case can't find it later
                            "bpSystolic": None,
                            "bpDiastolic": None,
                            "temperature": None,
                            "pulse": None,
                            "respirations": None,
                        }
                    );
            if (itemDate - patientById[patientId]["lastContiguousDate"]) <= CONTIGUOUS_THRESHOLD:
                patientById[patientId]["lastContiguousDate"] = itemDate;
            if patientById[patientId]["encounter_id"] is None:
                patientById[patientId]["encounter_id"] = encounterId;
            row = cursor.fetchone();

        # Second query phase to link to encounter information (e.g., insurance, admitting vital signs)
        encounterIds = columnFromModelList(iter(patientById.values()), "encounter_id");
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
            if patientById[patientId]["payorTitle"] is None:
                patientById[patientId]["payorTitle"] = set();   # Single encounters may have multiple payors to track
            patientById[patientId]["payorTitle"].add(payorTitle);
            patientById[patientId]["bpSystolic"] = bpSystolic;
            patientById[patientId]["bpDiastolic"] = bpDiastolic;
            patientById[patientId]["temperature"] = temperature;
            patientById[patientId]["pulse"] = pulse;
            patientById[patientId]["respirations"] = respirations;
            row = cursor.fetchone();
        
        if patientById[patientId]["payorTitle"] is not None:    # Condense to single string
            payorList = list(patientById[patientId]["payorTitle"]);
            payorList.sort();
            patientById[patientId]["payorTitle"] = str.join(",", payorList);
        
        # Drop results as tab-delimited text output
        formatter = TextResultsFormatter(outputFile);
        formatter.formatResultDicts(iter(patientById.values()), addHeaderRow=True);

        return patientById;    
    finally:
        cursor.close();
        conn.close();

if __name__ == "__main__":
    main(sys.argv);