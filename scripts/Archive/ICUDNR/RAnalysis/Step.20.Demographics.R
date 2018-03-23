##check this: -12428492282572 has DNR on first day and then keeps changing 

# Adapted from Gustavo's 2016 Demographics.R script
# Pre-Conditions: Step.10.DataLoading.R for data loading and pre-processing 
#   Primary patient-day dataframe in variable "df" and one for just the initiall fullCode patients as df.fullCode

#Total rows=138647; Total unique patients=10157
# gives the number of missing values for each column
#apply(newuni, 2, function(x) length(which(!is.na(x))))


# Given a data-frame with one row per patient (presumably first day of interest), calculate and return several summary stats
calculateSummaryStats = function(df)
{
  df.firstDay = df[df$curr_day == 0,];

  summaryStats = list();
  summaryStats["Total Patients (N)"] = nrow(df.firstDay);
  summaryStats["Age (Mean)"] = mean(df.firstDay$ageYears); 
  summaryStats["Age (SD)"] = sd(df.firstDay$ageYears);
  summaryStats["LOS (Mean)"] = mean(df.firstDay$daysUntilEnd)
  summaryStats["LOS (SD)"] = sd(df.firstDay$daysUntilEnd);
  
  summaryStats["Income"] = mean(df.firstDay$income,na.rm=TRUE);
  summaryStats["SD of income"] = sd(df.firstDay$income,na.rm=TRUE)
  summaryStats["Proportion not insured"] = mean(df.firstDay$self_pay)
  summaryStats["Proportion insured"] = 1 - mean(df.firstDay$self_pay)
  summaryStats["Male (N)"] = sum(df.firstDay$Male.pre)
  summaryStats["Male (%)"] = mean(df.firstDay$Male.pre)
  summaryStats["Female (N)"] = sum(df.firstDay$Female.pre)
  summaryStats["Female (%)"] = mean(df.firstDay$Female.pre)
  
  
  summaryStats["White (Non-Hispanic/Latino) (N)"] = sum(df.firstDay$RaceWhiteNonHispanicLatino.pre)
  summaryStats["White (Non-Hispanic/Latino) (%)"] = mean(df.firstDay$RaceWhiteNonHispanicLatino.pre)

  summaryStats["Hispanic/Latino (N)"] = sum(df.firstDay$all_latinos)
  summaryStats["Hispanic/Latino (%)"] = mean(df.firstDay$all_latinos)
  
  summaryStats["Asian (N)"] = sum(df.firstDay$RaceAsian.pre)
  summaryStats["Asian (%)"] = mean(df.firstDay$RaceAsian.pre)
  summaryStats["Native American (N)"] = sum(df.firstDay$RaceNativeAmerican.pre)
  summaryStats["Native American (%)"] = mean(df.firstDay$RaceNativeAmerican.pre)
  
  summaryStats["African American (N)"] = sum(df.firstDay$RaceBlack.pre)
  summaryStats["African American (%)"] = mean(df.firstDay$RaceBlack.pre)
  summaryStats["Pacific Islander (N)"] = sum(df.firstDay$RacePacificIslander.pre)
  summaryStats["Pacific Islander (%)"] = mean(df.firstDay$RacePacificIslander.pre)
  summaryStats["Other Race (N)"] = sum(df.firstDay$RaceOther.pre)
  summaryStats["Other Race (%)"] = mean(df.firstDay$RaceOther.pre)
  summaryStats["Unknown Race (N)"] = sum(df.firstDay$RaceUnknown.pre)
  summaryStats["Unknown Race (%)"] = mean(df.firstDay$RaceUnknown.pre)
  
  summaryStats["Initial Vasoactive Infusions (N)"] = sum((df.firstDay$AnyVasoactive.post) & (df.firstDay$AnyVasoactive.postTimeDays<1));
  summaryStats["Initial Vasoactive Infusions (%)"] = mean((df.firstDay$AnyVasoactive.post) & (df.firstDay$AnyVasoactive.postTimeDays<1));
  summaryStats["Initial Ventilator (N)"] = sum((df.firstDay$AnyVentilator.post) & (df.firstDay$AnyVentilator.postTimeDays<1));
  summaryStats["Initial Ventilator (%)"] = mean((df.firstDay$AnyVentilator.post) & (df.firstDay$AnyVentilator.postTimeDays<1));
  summaryStats["Initial CRRT (N)"] = sum((df.firstDay$AnyCRRT.post) & (df.firstDay$AnyCRRT.postTimeDays<1));
  summaryStats["Initial CRRT (%)"] = mean((df.firstDay$AnyCRRT.post) & (df.firstDay$AnyCRRT.postTimeDays<1));

  summaryStats["Ever Ventilator (N)"] = length(unique(df$patient_id[df$AnyVentilator.pre == 1]))
  summaryStats["Ever Ventilator (%)"] = length(unique(df$patient_id[df$AnyVentilator.pre == 1])) / nrow(df.firstDay)
  summaryStats["Ever Vasoactive (N)"] = length(unique(df$patient_id[df$AnyVasoactive.pre == 1]))
  summaryStats["Ever Vasoactive (%)"] = length(unique(df$patient_id[df$AnyVasoactive.pre == 1]))/ nrow(df.firstDay)
  summaryStats["Ever CRRT (N)"] = length(unique(df$patient_id[df$AnyCRRT.pre == 1]))
  summaryStats["Ever CRRT (%)"] = length(unique(df$patient_id[df$AnyCRRT.pre == 1]))/ nrow(df.firstDay)
  
  summaryStats["DNR at Entry (N)"] = sum(df.firstDay$AnyDNR.pre)
  summaryStats["DNR at entry (%)"] = mean(df.firstDay$AnyDNR.pre)

  summaryStats["Any DNR within Observed Period+1 Day (N)"] = sum((df.firstDay$AnyDNR.post) & (df.firstDay$AnyDNR.postTimeDays < df.firstDay$daysUntilEnd+1));
  summaryStats["Any DNR within Observed Period+1 Day (%)"] = mean((df.firstDay$AnyDNR.post) & (df.firstDay$AnyDNR.postTimeDays < df.firstDay$daysUntilEnd+1));
  summaryStats["Any DNR within Observed Day (N)"] = length(unique(df[df$AnyDNR.within1day,]$patient_id));
  summaryStats["Any DNR within Observed Day (%)"] = length(unique(df[df$AnyDNR.within1day,]$patient_id)) / length(unique(df$patient_id));
  
  summaryStats["Comfort Care after LST within Observed period+1 Day (N)"] = sum((df.firstDay$ComfortCare.post) & (df.firstDay$ComfortCare.postTimeDays < df.firstDay$daysUntilEnd+1));
  summaryStats["Comfort Care  after LST within Observed period+1 Day (%)"] = mean((df.firstDay$ComfortCare.post) & (df.firstDay$ComfortCare.postTimeDays < df.firstDay$daysUntilEnd+1));
  summaryStats["Comfort Care within Observed Day (N)"] = length(unique(df$patient_id[df$ComfortCare.within1day == 1]))
  summaryStats["Comfort Care within Observed Day (%)"] = length(unique(df$patient_id[df$ComfortCare.within1day == 1]))/ nrow(df.firstDay)
  
  summaryStats["Died within observation period+1 (N)"]=sum((df.firstDay$Death.post) & (df.firstDay$Death.postTimeDays < df.firstDay$daysUntilEnd+1));
  summaryStats["Died within observation period+1 (%)"]=mean((df.firstDay$Death.post) & (df.firstDay$Death.postTimeDays < df.firstDay$daysUntilEnd+1));
  
  summaryStats["Died within Observed Day (N)"] = length(unique(df$patient_id[df$Death.within1day]))
  summaryStats["Died within Observed Day (%)"] = length(unique(df$patient_id[df$Death.within1day])) / length(unique(df$patient_id));

    
  summaryStats["Died with Any DNR after LST within observation period+1 (N)"]=sum((df.firstDay$Death.post) &(df.firstDay$AnyDNR.post) & (df.firstDay$Death.postTimeDays < df.firstDay$daysUntilEnd+1));
  summaryStats["Died with Any DNR after LST within observation period+1 (%)"]=mean((df.firstDay$Death.post) & (df.firstDay$AnyDNR.post) & (df.firstDay$Death.postTimeDays < df.firstDay$daysUntilEnd+1));

  summaryStats["Comfort Care after LST but before Death Date, within observation period+1 (N)"]=sum((df.firstDay$Death.post) &(df.firstDay$ComfortCare.post) & (df.firstDay$Death.postTimeDays < df.firstDay$daysUntilEnd+1));
  summaryStats["Comfort Care after LST but before Death Date, within observation period+1 (%)"]=mean((df.firstDay$Death.post) &(df.firstDay$ComfortCare.post) & (df.firstDay$Death.postTimeDays < df.firstDay$daysUntilEnd+1));
  

  return(summaryStats);
}

# Run function to calculate demographics / summary stats
#summaryStats.all = calculateSummaryStats(df);
#write.csv(summaryStats.all, file = "SummaryStats.all.csv");


# Separate run, counting only patients who were Full Code at time of initial LST
summaryStats.fullCode = calculateSummaryStats(df.fullCode);
write.csv(summaryStats.fullCode, file = "SummaryStats_fullCode.csv")



