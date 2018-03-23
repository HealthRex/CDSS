# Load source table to data frame
# Adapted from on Gustavo's version (2016) and pre-processing

setwd("C:/GoogleDrive/ICUDNR/Data/");
dataFile = gzfile("featureMatrix.ICUDNR.removeExtraHeaders.tab.gz");
rawDF = read.table(dataFile, header = T, sep = "\t", na.strings = "None");
df = rawDF;

df_income = read.csv("Chen_income_vs_zip.csv");

####RK## 
#df = read.table("/Volumes/QSU/Datasets/HM/Jonathan Chen-DNR/featureMatrix.ICUDNR.removeExtraHeaders.tab", header = T, sep = "\t", na.strings = "None")
#df_income = read.csv("/Volumes/QSU/Datasets/HM/Jonathan Chen-DNR/Chen_income_vs_zip.csv"); #I resaved file without opeing in excel first and now does ok
###df_income <- read.csv("/Volumes/QSU/Datasets/HM/Jonathan Chen-DNR/Chen_income_vs_zip.csv", colClasses=c(PAT_ID=character))
########
# Join estimated income information

# Pull out income ranges
df_income$char = as.character(df_income$INCOME_RANGE)
for (i in 1:nrow(df_income))
{
  # Flatten end ranges <$20K to $20K and >$200K to $200K
  if (df_income$char[i] == "<20000") { df_income$char[i] = "20000"; }
  if (df_income$char[i] == ">200000") { df_income$char[i] = "200000"; }

  # Just pull out lead end of range
  df_income$char[i] = strsplit(df_income$char[i], split = "-")[[1]][1];
}
df_income$numb = strtoi(df_income$char);# Convert string to integer number
# Steps to map patient estimated income to primary dataframe records based on patientID link
map = df_income$numb;
names(map) = df_income$PAT_ID;
df$income = map[as.character(df$patient_id)];


# Convert and X.pre or X.post columns from Python "True" "False" strings into logical binary values
cols = colnames(df);
for (i in 1:length(cols))
{
  if ( endsWith(cols[i],".pre") || endsWith(cols[i],".post") )
  {
    df[,cols[i]] = as.logical(df[,cols[i]]);
  }
}


# Include information on health insurance: not available, self pay, or private 
df$No_ins_info = is.na(df$payorTitle);
df$No_ins_info = as.numeric(df$No_ins_info);

#df$self_pay = as.numeric(df$payorTitle) == 1 | as.numeric(df$payorTitle) == 75
df$self_pay = df$payorTitle == 'OTHER' | df$payorTitle == "set([OTHER])";
df$self_pay[is.na(df$self_pay)] = FALSE;

# Magic numbers below should not be relied upon. IF going to do at all, look for value strings as above self_pay example
#df$priv_ins = as.numeric(df$payorTitle) > 1 & as.numeric(df$payorTitle) < 31 | as.numeric(df$payorTitle) > 76
#df$priv_ins[is.na(df$priv_ins)] = FALSE
#
#df$pub_ins = as.numeric(df$payorTitle) > 30 & as.numeric(df$payorTitle) < 75
#df$pub_ins[is.na(df$pub_ins)] = FALSE 
#
#df$wk_comp = as.numeric(df$payorTitle) > 76
#df$wk_comp[is.na(df$wk_comp)] = FALSE



# Find all patient days that are within 1 day of DNR change - Primary Outcome
df$AnyDNR.within1day = FALSE;
df$AnyDNR.within1day[df$AnyDNR.postTimeDays < 1] = TRUE;


# Comfort Care and palliative care - Secondary Outcomes
df$ComfortCare.within1day = FALSE;
df$ComfortCare.within1day[df$ComfortCare.postTimeDays < 1] = TRUE;

df$PalliativeCare.within1day = FALSE;
df$PalliativeCare.within1day[df$PalliativeConsult.postTimeDays < 1] = TRUE;

# Death (Previous version looked at preTimeDays >= -1, since death gets recorded with day level precision so looking if got recorded at last midnight?)
df$Death.within1day = FALSE;
df$Death.within1day[df$Death.postTimeDays < 1] = TRUE;




# Translate index_time to days since initial life support day and until last contiguous date
df$curr_day = as.numeric(difftime(df$index_time, df$firstLifeSupportDate, units = "days"));
df$daysUntilEnd = as.numeric(difftime(df$lastContiguousDate, df$index_time, units = "days"));

# Convert age in days to age in integer years. 
df$ageYears = df$Birth.preTimeDays / -365.25;

# Combine both latinos groups (RaceHispanicLatino and RaceWhiteHispanicLatino)
df$all_latinos = (df$RaceHispanicLatino.pre | df$RaceWhiteHispanicLatino.pre );



# Subset to only first day records or to those with no prior DNR order (i.e., starts LST while Full Code)
df.firstDay.all = df[df$curr_day == 0,];#n=10590
df.firstDay.fullCode = df.firstDay.all[!df.firstDay.all$AnyDNR.pre,];#n=10157
df.fullCode = df[df$patient_id %in% df.firstDay.fullCode$patient_id,];#This set excludes the 433 who had DNR at the time of LS n=138647
df.fullCode$patid<-paste("ID",df.fullCode$patient_id)
str(df.fullCode$patid)

######################################keeping only selected vars from above

selvars<-c("patient_id","patid","encounter_id","ageYears","PO2A.last","CO2.last","PHA.last","RacePacificIslander.pre","RaceNativeAmerican.pre","all_latinos","AnyCRRT.pre","AnyVasoactive.pre", "AnyVentilator.pre","BP_High_Systolic.last","BUN.last","Charlson.CHF.pre","Charlson.COPD.pre","Charlson.Diabetes.pre", "Charlson.DiabetesComplications.pre", "Charlson.HemiplegiaParaplegia.pre", "Charlson.LiverMild.pre","Charlson.LiverModSevere.pre", "Charlson.MalignancyMetastatic.pre","Charlson.MI.pre", "Charlson.PepticUlcer.pre", "Charlson.PeripheralVascular.pre", "Charlson.Renal.pre", "Charlson.Rheumatic.pre", "CR.last", "Female.pre","Glasgow.Coma.Scale.Score.last","HCT.last","K.last","NA.last","Pulse.last","RaceAsian.pre","RaceBlack.pre","RaceUnknown.pre","Resp.last","self_pay",  "TBIL.last","Temp.last", "TT.Cardiology.pre","TT.CCU.HF.pre",  "TT.HemeOnc.pre","TT.Medicine.pre","TT.MICU.pre","TT.Neurology.pre","TT.SICU.pre","TT.SurgerySpecialty.pre", "TT.Transplant.pre","TT.Trauma.pre","WBC.last","Birth.preTimeDays","Charlson.Cerebrovascular.pre","Charlson.Dementia.pre","Charlson.Malignancy.pre","RaceOther.pre","TT.CCU.pre","TT.CVICU.pre","Death.within1day","Death.postTimeDays","Death.preTimeDays","Death.post",  "Death.pre","ComfortCare.within1day","ComfortCare.preTimeDays","ComfortCare.postTimeDays","ComfortCare.pre",  "ComfortCare.post","AnyDNR.pre","AnyDNR.post","AnyDNR.postTimeDays","AnyDNR.within1day","AnyDNR.preTimeDays","daysUntilEnd","income","curr_day","Charlson.DiabetesComplications.pre","Charlson.Rheumatic.pre","TT.SICU.pre")
myvars <- names(df.fullCode) %in% selvars
selvardata <- df.fullCode[myvars]
#write.csv(selvardata, file = "/Volumes/QSU/Datasets/HM/Jonathan Chen-DNR/dnrvars.csv",row.names=FALSE, na="")

# Additional deidentification steps (suppress ages >90 years)
selvardata$ageYears[selvardata$ageYears>90] = 90
write.csv(selvardata, file = "dnrvars.csv",row.names=TRUE, na="")

