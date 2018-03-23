import sys, os;
import sqlite3;   # Only import as needed
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db.ResultsFormatter import tab2df, df2sql;
from medinfo.db import DBUtil;

inputFilename = "featureMatrix.ICUDNR.removeExtraHeaders.tab.gz";
#inputFilename = "featureMatrix.ICUDNR.sample.tab";

#print >> sys.stderr, "Load whole matrix in memory"
#ifs = stdOpen(inputFilename);
#df = tab2df(ifs);
#
#print >> sys.stderr, "Convert to a SQLite database to test queries"
#conn = sqlite3.connect("featureMatrix.ICUDNR.sqlite");
#df2sql(df,conn=conn);

print >> sys.stderr, "Prepare connection to SQLite database. Skip directly to this step if file previously generated"
conn = sqlite3.connect("featureMatrix.ICUDNR.sqlite");

print >> sys.stderr, "Query Summary Stats"
queryCaptionList = \
	[	("select count(distinct patient_id) from data", "Distinct Patients"),
		("select count(*) from data where firstLifeSupportDate = index_time", "First Life Support Day Records"),
		("select count(distinct patient_id) from data where firstLifeSupportDate = index_time and AnyDNR_pre", "Patients with Any DNR by first Life Sustaining Treatment (LST)"),
		("select count(distinct patient_id) from data where firstLifeSupportDate = index_time and NOT AnyDNR_pre", "Patients without Any DNR by first Life Sustaining Treatment (LST)"),
		("select avg(Birth_preTimeDays)/-365 from data where firstLifeSupportDate = index_time", "Average Age"),
		("select avg(Birth_preTimeDays)/-365.25 from data where firstLifeSupportDate = index_time", "Average Age (counting leap years)"),

		("select sum(Male_pre) from data where firstLifeSupportDate = index_time", "Male Count"),
		("select sum(Female_pre) from data where firstLifeSupportDate = index_time", "Female Count"),
		("select sum(RaceWhiteNonHispanicLatino_pre) from data where firstLifeSupportDate = index_time", "RaceWhiteNonHispanicLatino"),
		("select sum(RaceAsian_pre) from data where firstLifeSupportDate = index_time", "RaceAsian"),
		("select sum(RaceWhiteHispanicLatino_pre) from data where firstLifeSupportDate = index_time", "RaceWhiteHispanicLatino"),
		("select sum(RaceHispanicLatino_pre) from data where firstLifeSupportDate = index_time", "RaceHispanicLatino"),
		("select sum(RaceUnknown_pre) from data where firstLifeSupportDate = index_time", "RaceUnknown"),
		("select sum(RaceOther_pre) from data where firstLifeSupportDate = index_time", "RaceOther"),
		("select sum(RaceBlack_pre) from data where firstLifeSupportDate = index_time", "RaceBlack"),
		("select sum(RacePacificIslander_pre) from data where firstLifeSupportDate = index_time", "RacePacificIslander"),
		("select sum(RaceNativeAmerican_pre) from data where firstLifeSupportDate = index_time", "RaceNativeAmerican"),

		("select avg(julianday(lastContiguousDate)-julianday(firstLifeSupportDate)) from data where firstLifeSupportDate = index_time", "Average Length of Stay/Observation after first LST"),

		("select count(distinct patient_id) from data where firstLifeSupportDate = index_time and AnyDNR_postTimeDays < julianday(lastContiguousDate)-julianday(firstLifeSupportDate)","Any DNR after LST, within observation period"),
		("select count(distinct patient_id) from data where firstLifeSupportDate = index_time and AnyDNR_postTimeDays < julianday(lastContiguousDate)-julianday(firstLifeSupportDate)+1","Any DNR after LST, within observation period +1 day"),

		("select count(distinct patient_id) from data where firstLifeSupportDate = index_time and ComfortCare_postTimeDays < julianday(lastContiguousDate)-julianday(firstLifeSupportDate)","Comfort Care after LST, within observation period"),
		("select count(distinct patient_id) from data where firstLifeSupportDate = index_time and ComfortCare_postTimeDays < julianday(lastContiguousDate)-julianday(firstLifeSupportDate)+1","Comfort Care after LST, within observation period +1 day"),

		("select count(distinct patient_id) from data where firstLifeSupportDate = index_time and Death_postTimeDays < julianday(lastContiguousDate)-julianday(firstLifeSupportDate)","Died after LST, within observation period"),
		("select count(distinct patient_id) from data where firstLifeSupportDate = index_time and Death_postTimeDays < julianday(lastContiguousDate)-julianday(firstLifeSupportDate)+1","Died after LST, within observation period +1 day"),

		("select count(distinct patient_id) from data where firstLifeSupportDate = index_time and AnyDNR_postTimeDays <= Death_postTimeDays and Death_postTimeDays < julianday(lastContiguousDate)-julianday(firstLifeSupportDate)","Died with Any DNR after LST but before Death Date, within observation period"),
		("select count(distinct patient_id) from data where firstLifeSupportDate = index_time and AnyDNR_postTimeDays <= Death_postTimeDays and Death_postTimeDays < julianday(lastContiguousDate)-julianday(firstLifeSupportDate)+1","Died with Any DNR after LST but before Death Date, within observation period +1 day"),

		("select count(distinct patient_id) from data where firstLifeSupportDate = index_time and ComfortCare_postTimeDays <= Death_postTimeDays and Death_postTimeDays < julianday(lastContiguousDate)-julianday(firstLifeSupportDate)","Died with Comfort Care after LST but before Death Date, within observation period"),
		("select count(distinct patient_id) from data where firstLifeSupportDate = index_time and ComfortCare_postTimeDays <= Death_postTimeDays and Death_postTimeDays < julianday(lastContiguousDate)-julianday(firstLifeSupportDate)+1","Died with Comfort Care after LST but before Death Date, within observation period +1 day"),

		("select count(distinct patient_id) from data where firstLifeSupportDate = index_time and AnyDNR_post and Death_postTimeDays < julianday(lastContiguousDate)-julianday(firstLifeSupportDate)","Died with Any DNR after LST, within observation period"),
		("select count(distinct patient_id) from data where firstLifeSupportDate = index_time and AnyDNR_post and Death_postTimeDays < julianday(lastContiguousDate)-julianday(firstLifeSupportDate)+1","Died with Any DNR after LST, within observation period +1 day"),

		("select count(distinct patient_id) from data where firstLifeSupportDate = index_time and ComfortCare_post and Death_postTimeDays < julianday(lastContiguousDate)-julianday(firstLifeSupportDate)","Died with Comfort Care after LST, within observation period"),
		("select count(distinct patient_id) from data where firstLifeSupportDate = index_time and ComfortCare_post and Death_postTimeDays < julianday(lastContiguousDate)-julianday(firstLifeSupportDate)+1","Died with Comfort Care after LST, within observation period +1 day"),

		("select count(distinct patient_id) from data where firstLifeSupportDate = index_time and ComfortCare_post and Death_postTimeDays < julianday(lastContiguousDate)-julianday(firstLifeSupportDate)","Died with Comfort Care after LST, within observation period"),
		("select count(distinct patient_id) from data where firstLifeSupportDate = index_time and ComfortCare_post and Death_postTimeDays < julianday(lastContiguousDate)-julianday(firstLifeSupportDate)+1","Died with Comfort Care after LST, within observation period +1 day"),

		("select count(distinct patient_id) from data where AnyDNR_postTimeDays < 1","Patients with an observed day with DNR within < 1 day"),
		("select count(distinct patient_id) from data where AnyDNR_postTimeDays <= 1","Patients with an observed day with DNR within <= 1 day"),

		("select count(distinct patient_id) from data where ComfortCare_postTimeDays < 1","Patients with an observed day with ComfortCare within < 1 day"),
		("select count(distinct patient_id) from data where ComfortCare_postTimeDays <= 1","Patients with an observed day with ComfortCare within <= 1 day"),

		("select count(distinct patient_id) from data where Death_postTimeDays < 1","Patients with an observed day with Death within < 1 day"),
		("select count(distinct patient_id) from data where Death_postTimeDays <= 1","Patients with an observed day with Death within <= 1 day"),

		("select count(distinct patient_id) from data where Death_preTimeDays > -1","Patients with an observed day with Death > -1 day"),
		("select count(distinct patient_id) from data where Death_preTimeDays >= -1","Patients with an observed day with Death >= -1 day"),

	];
for query, caption in queryCaptionList:
	print "%s\t%s\t%s" % (DBUtil.execute(query,conn=conn)[0][0], caption, query);


"""
query = "select patient_id, firstLifeSupportDate, index_time from data where firstLifeSupportDate = index_time order by patient_id"
for row in DBUtil.execute(query,conn=conn):
	print row;
"""



""" # Data Columns
patient_id
bpDiastolic
bpSystolic
encounter_id
firstLifeSupportDate
lastContiguousDate
payorTitle
pulse
respirations
temperature
index_time
BP_High_Systolic.min
BP_High_Systolic.max
BP_High_Systolic.median
BP_High_Systolic.mean
BP_High_Systolic.std
BP_High_Systolic.first
BP_High_Systolic.last
BP_High_Systolic.proximate
BP_Low_Diastolic.min
BP_Low_Diastolic.max
BP_Low_Diastolic.median
BP_Low_Diastolic.mean
BP_Low_Diastolic.std
BP_Low_Diastolic.first
BP_Low_Diastolic.last
BP_Low_Diastolic.proximate
FiO2.min
FiO2.max
FiO2.median
FiO2.mean
FiO2.std
FiO2.first
FiO2.last
FiO2.proximate
Glasgow
Coma
Scale
Score.min
Glasgow
Coma
Scale
Score.max
Glasgow
Coma
Scale
Score.median
Glasgow
Coma
Scale
Score.mean
Glasgow
Coma
Scale
Score.std
Glasgow
Coma
Scale
Score.first
Glasgow
Coma
Scale
Score.last
Glasgow
Coma
Scale
Score.proximate
Pulse.min
Pulse.max
Pulse.median
Pulse.mean
Pulse.std
Pulse.first
Pulse.last
Pulse.proximate
Resp.min
Resp.max
Resp.median
Resp.mean
Resp.std
Resp.first
Resp.last
Resp.proximate
Temp.min
Temp.max
Temp.median
Temp.mean
Temp.std
Temp.first
Temp.last
Temp.proximate
Urine.min
Urine.max
Urine.median
Urine.mean
Urine.std
Urine.first
Urine.last
Urine.proximate
WBC.min
WBC.max
WBC.median
WBC.mean
WBC.std
WBC.first
WBC.last
WBC.proximate
HCT.min
HCT.max
HCT.median
HCT.mean
HCT.std
HCT.first
HCT.last
HCT.proximate
PLT.min
PLT.max
PLT.median
PLT.mean
PLT.std
PLT.first
PLT.last
PLT.proximate
NA.min
NA.max
NA.median
NA.mean
NA.std
NA.first
NA.last
NA.proximate
K.min
K.max
K.median
K.mean
K.std
K.first
K.last
K.proximate
CO2.min
CO2.max
CO2.median
CO2.mean
CO2.std
CO2.first
CO2.last
CO2.proximate
BUN.min
BUN.max
BUN.median
BUN.mean
BUN.std
BUN.first
BUN.last
BUN.proximate
CR.min
CR.max
CR.median
CR.mean
CR.std
CR.first
CR.last
CR.proximate
TBIL.min
TBIL.max
TBIL.median
TBIL.mean
TBIL.std
TBIL.first
TBIL.last
TBIL.proximate
ALB.min
ALB.max
ALB.median
ALB.mean
ALB.std
ALB.first
ALB.last
ALB.proximate
LAC.min
LAC.max
LAC.median
LAC.mean
LAC.std
LAC.first
LAC.last
LAC.proximate
ESR.min
ESR.max
ESR.median
ESR.mean
ESR.std
ESR.first
ESR.last
ESR.proximate
CRP.min
CRP.max
CRP.median
CRP.mean
CRP.std
CRP.first
CRP.last
CRP.proximate
TNI.min
TNI.max
TNI.median
TNI.mean
TNI.std
TNI.first
TNI.last
TNI.proximate
PHA.min
PHA.max
PHA.median
PHA.mean
PHA.std
PHA.first
PHA.last
PHA.proximate
PO2A.min
PO2A.max
PO2A.median
PO2A.mean
PO2A.std
PO2A.first
PO2A.last
PO2A.proximate
PCO2A.min
PCO2A.max
PCO2A.median
PCO2A.mean
PCO2A.std
PCO2A.first
PCO2A.last
PCO2A.proximate
PHV.min
PHV.max
PHV.median
PHV.mean
PHV.std
PHV.first
PHV.last
PHV.proximate
PO2V.min
PO2V.max
PO2V.median
PO2V.mean
PO2V.std
PO2V.first
PO2V.last
PO2V.proximate
PCO2V.min
PCO2V.max
PCO2V.median
PCO2V.mean
PCO2V.std
PCO2V.first
PCO2V.last
PCO2V.proximate
AnyICULifeSupport.preTimeDays
AnyICULifeSupport.postTimeDays
AnyICULifeSupport.pre
AnyICULifeSupport.post
AnyDNR.preTimeDays
AnyDNR.postTimeDays
AnyDNR.pre
AnyDNR.post
AnyVasoactive.preTimeDays
AnyVasoactive.postTimeDays
AnyVasoactive.pre
AnyVasoactive.post
AnyCRRT.preTimeDays
AnyCRRT.postTimeDays
AnyCRRT.pre
AnyCRRT.post
AnyVentilator.preTimeDays
AnyVentilator.postTimeDays
AnyVentilator.pre
AnyVentilator.post
ComfortCare.preTimeDays
ComfortCare.postTimeDays
ComfortCare.pre
ComfortCare.post
PalliativeConsult.preTimeDays
PalliativeConsult.postTimeDays
PalliativeConsult.pre
PalliativeConsult.post
Death.preTimeDays
Death.postTimeDays
Death.pre
Death.post
Birth.preTimeDays
Birth.postTimeDays
Birth.pre
Birth.post
Male.preTimeDays
Male.postTimeDays
Male.pre
Male.post
Female.preTimeDays
Female.postTimeDays
Female.pre
Female.post
RaceWhiteNonHispanicLatino.preTimeDays
RaceWhiteNonHispanicLatino.postTimeDays
RaceWhiteNonHispanicLatino.pre
RaceWhiteNonHispanicLatino.post
RaceAsian.preTimeDays
RaceAsian.postTimeDays
RaceAsian.pre
RaceAsian.post
RaceWhiteHispanicLatino.preTimeDays
RaceWhiteHispanicLatino.postTimeDays
RaceWhiteHispanicLatino.pre
RaceWhiteHispanicLatino.post
RaceHispanicLatino.preTimeDays
RaceHispanicLatino.postTimeDays
RaceHispanicLatino.pre
RaceHispanicLatino.post
RaceUnknown.preTimeDays
RaceUnknown.postTimeDays
RaceUnknown.pre
RaceUnknown.post
RaceOther.preTimeDays
RaceOther.postTimeDays
RaceOther.pre
RaceOther.post
RaceBlack.preTimeDays
RaceBlack.postTimeDays
RaceBlack.pre
RaceBlack.post
RacePacificIslander.preTimeDays
RacePacificIslander.postTimeDays
RacePacificIslander.pre
RacePacificIslander.post
RaceNativeAmerican.preTimeDays
RaceNativeAmerican.postTimeDays
RaceNativeAmerican.pre
RaceNativeAmerican.post
Charlson.AIDSHIV.preTimeDays
Charlson.AIDSHIV.postTimeDays
Charlson.AIDSHIV.pre
Charlson.AIDSHIV.post
Charlson.Cerebrovascular.preTimeDays
Charlson.Cerebrovascular.postTimeDays
Charlson.Cerebrovascular.pre
Charlson.Cerebrovascular.post
Charlson.CHF.preTimeDays
Charlson.CHF.postTimeDays
Charlson.CHF.pre
Charlson.CHF.post
Charlson.COPD.preTimeDays
Charlson.COPD.postTimeDays
Charlson.COPD.pre
Charlson.COPD.post
Charlson.Dementia.preTimeDays
Charlson.Dementia.postTimeDays
Charlson.Dementia.pre
Charlson.Dementia.post
Charlson.Diabetes.preTimeDays
Charlson.Diabetes.postTimeDays
Charlson.Diabetes.pre
Charlson.Diabetes.post
Charlson.DiabetesComplications.preTimeDays
Charlson.DiabetesComplications.postTimeDays
Charlson.DiabetesComplications.pre
Charlson.DiabetesComplications.post
Charlson.HemiplegiaParaplegia.preTimeDays
Charlson.HemiplegiaParaplegia.postTimeDays
Charlson.HemiplegiaParaplegia.pre
Charlson.HemiplegiaParaplegia.post
Charlson.LiverMild.preTimeDays
Charlson.LiverMild.postTimeDays
Charlson.LiverMild.pre
Charlson.LiverMild.post
Charlson.LiverModSevere.preTimeDays
Charlson.LiverModSevere.postTimeDays
Charlson.LiverModSevere.pre
Charlson.LiverModSevere.post
Charlson.Malignancy.preTimeDays
Charlson.Malignancy.postTimeDays
Charlson.Malignancy.pre
Charlson.Malignancy.post
Charlson.MalignancyMetastatic.preTimeDays
Charlson.MalignancyMetastatic.postTimeDays
Charlson.MalignancyMetastatic.pre
Charlson.MalignancyMetastatic.post
Charlson.MI.preTimeDays
Charlson.MI.postTimeDays
Charlson.MI.pre
Charlson.MI.post
Charlson.PepticUlcer.preTimeDays
Charlson.PepticUlcer.postTimeDays
Charlson.PepticUlcer.pre
Charlson.PepticUlcer.post
Charlson.PeripheralVascular.preTimeDays
Charlson.PeripheralVascular.postTimeDays
Charlson.PeripheralVascular.pre
Charlson.PeripheralVascular.post
Charlson.Renal.preTimeDays
Charlson.Renal.postTimeDays
Charlson.Renal.pre
Charlson.Renal.post
Charlson.Rheumatic.preTimeDays
Charlson.Rheumatic.postTimeDays
Charlson.Rheumatic.pre
Charlson.Rheumatic.post
TT.Cardiology.preTimeDays
TT.Cardiology.postTimeDays
TT.Cardiology.pre
TT.Cardiology.post
TT.CCU-HF.preTimeDays
TT.CCU-HF.postTimeDays
TT.CCU-HF.pre
TT.CCU-HF.post
TT.CCU.preTimeDays
TT.CCU.postTimeDays
TT.CCU.pre
TT.CCU.post
TT.CVICU.preTimeDays
TT.CVICU.postTimeDays
TT.CVICU.pre
TT.CVICU.post
TT.HemeOnc.preTimeDays
TT.HemeOnc.postTimeDays
TT.HemeOnc.pre
TT.HemeOnc.post
TT.Med.preTimeDays
TT.Med.postTimeDays
TT.Med.pre
TT.Med.post
TT.Medicine.preTimeDays
TT.Medicine.postTimeDays
TT.Medicine.pre
TT.Medicine.post
TT.MICU.preTimeDays
TT.MICU.postTimeDays
TT.MICU.pre
TT.MICU.post
TT.Neurology.preTimeDays
TT.Neurology.postTimeDays
TT.Neurology.pre
TT.Neurology.post
TT.Psychiatry.preTimeDays
TT.Psychiatry.postTimeDays
TT.Psychiatry.pre
TT.Psychiatry.post
TT.SICU.preTimeDays
TT.SICU.postTimeDays
TT.SICU.pre
TT.SICU.post
TT.SurgerySpecialty.preTimeDays
TT.SurgerySpecialty.postTimeDays
TT.SurgerySpecialty.pre
TT.SurgerySpecialty.post
TT.Transplant.preTimeDays
TT.Transplant.postTimeDays
TT.Transplant.pre
TT.Transplant.post
TT.Trauma.preTimeDays
TT.Trauma.postTimeDays
TT.Trauma.pre
TT.Trauma.post
"""