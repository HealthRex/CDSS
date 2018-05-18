#http://stackoverflow.com/questions/11561856/add-new-row-to-dataframe

#use script after using load data script

#only select the variables are will be used for regression. Otherwise, multiple inputation will 
#take too long to find values of variables not necessary for regression

variables = c("patient_id", 
              "Birth.preTimeDays", "income","self_pay", "curr_day","Female.pre","RaceUnknown.pre", "RaceAsian.pre",
              "RaceBlack.pre","all_latinos", "RaceOther.pre", "RacePacificIslander.pre", "RaceWhiteNonHispanicLatino.pre"
              ,"AnyCRRT.pre","AnyVasoactive.pre","AnyVentilator.pre","Charlson.AIDSHIV.pre","Charlson.Cerebrovascular.pre",
              "Charlson.CHF.pre","Charlson.COPD.pre","Charlson.Dementia.pre","Charlson.Diabetes.pre",
              "Charlson.DiabetesComplications.pre","Charlson.HemiplegiaParaplegia.pre","Charlson.LiverMild.pre",
              "Charlson.LiverModSevere.pre","Charlson.Malignancy.pre","Charlson.MalignancyMetastatic.pre","Charlson.MI.pre",
              "Charlson.PepticUlcer.pre","Charlson.PeripheralVascular.pre","Charlson.Renal.pre","Charlson.Rheumatic.pre",
              "PO2A.last","PHV.last","Pulse.last","NA.last","CR.last","HCT.last","WBC.last","BUN.last","TBIL.last"
              ,"K.last","Resp.last","Temp.last","Urine.last", "TT.Cardiology.pre", "TT.CCU.HF.pre", "TT.CCU.pre",
              "TT.CVICU.pre", "TT.HemeOnc.pre", "TT.Medicine.pre", "TT.MICU.pre", "TT.Neurology.pre", 
              "TT.SICU.pre", "TT.SurgerySpecialty.pre", "TT.Transplant.pre", "TT.Trauma.pre", "BP_High_Systolic.last", 
              "BP_Low_Diastolic.last", "Glasgow.Coma.Scale.Score.last","Death.within1day")

dependantVariables = c("AnyDNR.within1day","ComfortCare.within1day","PalliativeCare.within1day", "AnyDNR.post", "AnyDNR.pre", "PalliativeConsult.pre", 
                     "PalliativeConsult.post", "ComfortCare.pre", "ComfortCare.post")

df.independentVariables = df[,variables]
df.dependentVariables = df[,dependantVariables]
#to install run > install.packages("Amelia")

#Amelia pkg is a multiple inputatino package
#will calculate the values of missing data entries may take 10 minutes
library(Amelia)
df.amelia = amelia(df.independentVariables)
#Why is it that RaceNativeAmerican.pre is perfectly collinear with another variable??

#Seperates the patients data rows to two groups. patients complete data  where 
#patients have dnr change and the complete data where patients dont have a DNR change

df.amelia.final = df.amelia$imputations$imp5

#merge dependent and independent variables into one data file
for (i in 1:length(dependantVariables)){
  df.amelia.final[dependantVariables[i]] = df.dependentVariables[dependantVariables[i]]
}
