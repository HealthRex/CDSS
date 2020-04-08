"""Generate batch of simulated data to gain confidence
in analytic methods being able to reproduce expected results.
"""
import math;
import random;
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db.ResultsFormatter import TextResultsFormatter;

colNames = ["patient_id","curr_day","start","end","timeUntilNoMoreData","timeUntilNoDataOrDNR","AnyDNRatEnd","AnyDNR.postTimeDays","AnyDNR.pre","AnyDNR.within1day","Birth.preTimeDays","income","Female.pre","RaceUnknown.pre","RaceAsian.pre","RaceBlack.pre","all_latinos","RaceOther.pre","RacePacificIslander.pre","AnyVasoactive.pre","AnyVentilator.pre","AnyCRRT.pre","Charlson.Cerebrovascular.pre","Charlson.CHF.pre","Charlson.COPD.pre","Charlson.Dementia.pre","Charlson.Diabetes.pre","Charlson.DiabetesComplications.pre","Charlson.HemiplegiaParaplegia.pre","Charlson.LiverMild.pre","Charlson.LiverModSevere.pre","Charlson.Malignancy.pre","Charlson.MalignancyMetastatic.pre","Charlson.MI.pre","Charlson.PepticUlcer.pre","Charlson.PeripheralVascular.pre","Charlson.Renal.pre","Charlson.Rheumatic.pre","self_pay","PO2A.last","Pulse.last","NA.last","CR.last","HCT.last","WBC.last","BUN.last","TBIL.last","K.last","Resp.last","Temp.last","Urine.last","BP_Low_Diastolic.last","BP_High_Systolic.last","Glasgow.Coma.Scale.Score.last","TT.Cardiology.pre","TT.CCU.HF.pre","TT.CCU.pre","TT.HemeOnc.pre","TT.Medicine.pre","TT.MICU.pre","TT.Neurology.pre","TT.SICU.pre","TT.SurgerySpecialty.pre","TT.Transplant.pre","TT.Trauma.pre","self_pay"];

ofs = stdOpen("simulatedData.ICUDNR.tab","w");
formatter = TextResultsFormatter(ofs);
formatter.formatTuple(colNames);	# Header row

random.seed(987654321);	# Consistent seed for reproducibility
nPatients = 10000;

# Random generator parameters
ageRange = [30,80];
incomeRange = [20000, 200000];
incomeStep = 1000;
femaleRate = 0.5

# Ranges on uniform distribution to assign race labels. Leave ~50% empty for default White race
raceRangesByLabel = \
	{
	"RaceAsian.pre": [0.00, 0.12],
	"all_latinos":   [0.12, 0.25],
	"RaceBlack.pre": [0.25, 0.37],
	"RacePacificIslander.pre": [0.37, 0.38],
	"RaceOther.pre": [0.38, 0.40],
	"RaceUnknown.pre": [0.40, 0.45],
	}

vasoactiveRate = 0.6;
crrtRate = 0.2;
ventilatorRate = 0.6;
# Expect possible changes daily
dailyLifeSupportOnRate = 0.02;
dailyLifeSupportOffRate = 0.05;

# Simplicity, use common rate for different comorbidity occurrence and treatment teams
comorbidityRate = 0.1;
treatmentTeamRate = 0.05;
# Expect possible changes daily
treatmentTeamOnRate = 0.05;
treatmentTeamOffRate = 0.01;

selfPayRate = 0.1;

labMissingRate = 0.0; # 0.3; No missing values for now to keep things simple
labRangeByLabel = \
	{
		"PO2A.last": [50,120],
		"Pulse.last": [50,150],
		"NA.last": [125,155],
		"CR.last": [0,4],
		"HCT.last": [20,40],
		"WBC.last": [5,30],
		"BUN.last": [10,60],
		"TBIL.last": [0,10],
		"K.last": [3,6],
		"Resp.last": [8,30],
		"Temp.last": [97,103],
		"Urine.last": [0,1000],
		"BP_Low_Diastolic.last": [40,80],
		"BP_High_Systolic.last": [80,160],
		"Glasgow.Coma.Scale.Score.last": [5,15],
	};
dailyLabChangeRate = 0.1;

baselineDNRRate = 0.1; 

durationRange = [1,20];

prog = ProgressDots(total=nPatients);
for iPatient in range(nPatients):
	rowData = \
		{
			"patient_id":iPatient,
			"Birth.preTimeDays": random.randint(ageRange[0], ageRange[-1]),
			"income": random.randrange(incomeRange[0], incomeRange[-1], incomeStep),
			"Female.pre": (random.random() < femaleRate)+0,

			"AnyVasoactive.pre": (random.random() < vasoactiveRate)+0,	# Add 0 to convert boolean to 0 or 1
			"AnyVentilator.pre": (random.random() < ventilatorRate)+0,
			"AnyCRRT.pre": (random.random() < crrtRate)+0,

			"Charlson.Cerebrovascular.pre": (random.random() < comorbidityRate)+0,
			"Charlson.CHF.pre": (random.random() < comorbidityRate)+0,
			"Charlson.COPD.pre": (random.random() < comorbidityRate)+0,
			"Charlson.Dementia.pre": (random.random() < comorbidityRate)+0,
			"Charlson.Diabetes.pre": (random.random() < comorbidityRate)+0,
			"Charlson.DiabetesComplications.pre": (random.random() < comorbidityRate)+0,
			"Charlson.HemiplegiaParaplegia.pre": (random.random() < comorbidityRate)+0,
			"Charlson.LiverMild.pre": (random.random() < comorbidityRate)+0,
			"Charlson.LiverModSevere.pre": (random.random() < comorbidityRate)+0,
			"Charlson.Malignancy.pre": (random.random() < comorbidityRate)+0,
			"Charlson.MalignancyMetastatic.pre": (random.random() < comorbidityRate)+0,
			"Charlson.MI.pre": (random.random() < comorbidityRate)+0,
			"Charlson.PepticUlcer.pre": (random.random() < comorbidityRate)+0,
			"Charlson.PeripheralVascular.pre": (random.random() < comorbidityRate)+0,
			"Charlson.Renal.pre": (random.random() < comorbidityRate)+0,
			"Charlson.Rheumatic.pre": (random.random() < comorbidityRate)+0,

			"self_pay": (random.random() < selfPayRate)+0,

			"TT.Cardiology.pre": (random.random() < treatmentTeamRate)+0,
			"TT.CCU.HF.pre": (random.random() < treatmentTeamRate)+0,
			"TT.CCU.pre": (random.random() < treatmentTeamRate)+0,
			"TT.HemeOnc.pre": (random.random() < treatmentTeamRate)+0,
			"TT.Medicine.pre": (random.random() < treatmentTeamRate)+0,
			"TT.MICU.pre": (random.random() < treatmentTeamRate)+0,
			"TT.Neurology.pre": (random.random() < treatmentTeamRate)+0,
			"TT.SICU.pre": (random.random() < treatmentTeamRate)+0,
			"TT.SurgerySpecialty.pre": (random.random() < treatmentTeamRate)+0,
			"TT.Transplant.pre": (random.random() < treatmentTeamRate)+0,
			"TT.Trauma.pre": (random.random() < treatmentTeamRate)+0,
		}

	# Pick a single race label
	raceRandom = random.random();
	for label, raceRange in raceRangesByLabel.items():
		rowData[label] = (raceRandom >= raceRange[0] and raceRandom < raceRange[-1])+0;

	# Fill in lab values
	for label, labRange in labRangeByLabel.items():
		if (random.random() < labMissingRate):
			rowData[label] = "NA";
		else:
			rowData[label] = random.randint(labRange[0], labRange[-1]);

	lengthOfStay = random.randint(durationRange[0],durationRange[-1]);

	# Fill in outcome values based on simulated model for a custom DNR rate
	# What fraction of patients will get DNR before discharge. Effectively logit function so using logs to convert adjusted hazard ratios in coefficients
	############## Logit function here to translate patient variables into hazard rate. 
	# Simulate per day time since should be a per day hazard function
	# p = event rate / probability, range [0,1]
	# odds = p / 1-p, range [0,+inf]
	# log odds = logit function, range [-inf,+inf]
	# Estimate log odds with linear regression function: beta0 + beta1 x1 + beta2 x2 + ... + epsilon
	# Algebra--> Estimate p = e^logit / 1+e^logit, range [0,1]
	# Beta values: How much the log odds should change for each increment / decrement of covariate. e^Beta is respective change in odds
	beta0 = math.log( baselineDNRRate / (1-baselineDNRRate) );
	logitEstimate = beta0 + 1*rowData["Charlson.MalignancyMetastatic.pre"] - 0.5*rowData["AnyVentilator.pre"] + 0.01*rowData["Birth.preTimeDays"];
	dailyDNRRate = math.exp(logitEstimate) / (1+math.exp(logitEstimate));

	# Simulate dnrEventRate per day
	dnrOccurs = False;
	dnrDay = None;
	for iDay in range(1,lengthOfStay):
		if (random.random() < dailyDNRRate):
			dnrDay = iDay;
			dnrOccurs = True;
			break;	# Don't need to keep looking
	rowData["AnyDNRatEnd"] = dnrOccurs + 0;

	# Generate daily data
	for iDay in range(lengthOfStay):
		rowData["curr_day"] = rowData["start"] = iDay;
		rowData["end"] = iDay + 1;
		rowData["timeUntilNoMoreData"] = lengthOfStay - rowData["start"];
		rowData["timeUntilNoDataOrDNR"] = rowData["timeUntilNoMoreData"];
		if dnrOccurs:
			rowData["AnyDNR.pre"] = (iDay >= dnrDay)+0;
			rowData["AnyDNR.within1day"] = (iDay+1 == dnrDay)+0;
			rowData["AnyDNR.postTimeDays"] = dnrDay - iDay;
			if rowData["AnyDNR.postTimeDays"] < 0:
				rowData["AnyDNR.postTimeDays"] = "NA";
			else:
				rowData["timeUntilNoDataOrDNR"] = min(rowData["timeUntilNoMoreData"], rowData["AnyDNR.postTimeDays"]);
		else:
			rowData["AnyDNR.pre"] = 0;
			rowData["AnyDNR.within1day"] = 0;
			rowData["AnyDNR.postTimeDays"] = "NA";
		formatter.formatResultDict(rowData, colNames);
	prog.update();
ofs.close();