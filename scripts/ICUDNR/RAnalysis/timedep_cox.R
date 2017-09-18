##COX---longitudinal
# locf and healthy values were added in SAS, we delete multiple events of DNR, 137 had missing income at baseline, 2100 overall.
#some names truncated as SAS uses only 32 characters in name but all are pre

# income was converted to numeric and divided by 1000 so that change is per 1000unit change
meanlocf$income<-as.numeric(meanlocf$income)
meanlocf$inc<-meanlocf$income/1000
# if we want to categorize we could do <4k,<8k,<12k,<16k,<20k and >20k;

meanlocf= read.table("/Volumes/QSU/Datasets/HM/Jonathan Chen-DNR/Aug_datasets/Meannorm_locf.csv", header = T, sep = ",")
meanlocf<-meanlocf[order(meanlocf$patid,meanlocf$curr_day),] #138647
meanlocf <- meanlocf[which(meanlocf$AnyDNR_pre=='FALSE'),] #129329
meanlocf$income<-as.numeric(meanlocf$income)
meanlocf$inc<-meanlocf$income/1000
#firstday <- meanlocf[meanlocf$curr_day == 0,]
#sum((firstday$AnyDNR_post) & (firstday$AnyDNR_postTimeDays <firstday$daysUntilEnd+1));



minlocf= read.table("/Volumes/QSU/Datasets/HM/Jonathan Chen-DNR/Aug_datasets/Minnorm_locf.csv", header = T, sep = ",")
minlocf<-minlocf[order(minlocf$patid,minlocf$curr_day),] #138647
minlocf <- minlocf[which(minlocf$AnyDNR_pre=='FALSE'),] #129329
minlocf$income<-as.numeric(minlocf$income)
minlocf$inc<-minlocf$income/1000

maxlocf= read.table("/Volumes/QSU/Datasets/HM/Jonathan Chen-DNR/Aug_datasets/Maxnorm_locf.csv", header = T, sep = ",")
maxlocf<-maxlocf[order(maxlocf$patid,maxlocf$curr_day),] #138647
maxlocf <- maxlocf[which(maxlocf$AnyDNR_pre=='FALSE'),] #129329
maxlocf$income<-as.numeric(maxlocf$income)
maxlocf$inc<-maxlocf$income/1000

library(survival)
library(broom)

meanlocfit<-coxph(Surv(curr_day,end_day, AnyDNR_within1day) ~ ageYears+ inc+self_pay+Female_pre +RaceUnknown_pre + RaceAsian_pre + RaceBlack_pre + all_latinos + RaceOther_pre +  RacePacificIslander_pre + RaceNativeAmerican_pre+ AnyVasoactive_pre + AnyVentilator_pre  + AnyCRRT_pre + Charlson_Cerebrovascular_pre + Charlson_CHF_pre + Charlson_COPD_pre + Charlson_Dementia_pre + Charlson_Diabetes_pre + Charlson_DiabetesComplications_+ Charlson_HemiplegiaParaplegia_p+ Charlson_LiverMild_pre + Charlson_LiverModSevere_pre +Charlson_Malignancy_pre + Charlson_MalignancyMetastatic_p+ Charlson_MI_pre + Charlson_PepticUlcer_pre+ Charlson_PeripheralVascular_pre + Charlson_Renal_pre + Charlson_Rheumatic_pre+ TT_Cardiology_pre + TT_CCU_HF_pre+TT_CCU_pre  + TT_HemeOnc_pre+ TT_Medicine_pre + TT_MICU_pre + TT_Neurology_pre + TT_SICU_pre + TT_SurgerySpecialty_pre + TT_Transplant_pre + TT_Trauma_pre + TT_CVICU_pre+ locf_PO2A_last  + locf_Pulse_last + locf_NA_last + locf_CR_last + locf_HCT_last + locf_WBC_last+ locf_BUN_last + locf_TBIL_last+ locf_K_last + locf_Resp_last + locf_Temp_last + locf_BP_High_Systolic_last +locf_GCSS_last+ locf_CO2_last+ locf_PHA_last, data = meanlocf, ties = "breslow") 
meanlocfit
cox_mean<-tidy(meanlocfit)
cox_mean$set<-rep("meanlocfit",57)
###########         minimum locf      ###############
minlocfit<-coxph(Surv(curr_day,end_day, AnyDNR_within1day) ~ ageYears+ inc+self_pay+Female_pre +RaceUnknown_pre + RaceAsian_pre + RaceBlack_pre + all_latinos + RaceOther_pre +  RacePacificIslander_pre + RaceNativeAmerican_pre+ AnyVasoactive_pre + AnyVentilator_pre  + AnyCRRT_pre + Charlson_Cerebrovascular_pre + Charlson_CHF_pre + Charlson_COPD_pre + Charlson_Dementia_pre + Charlson_Diabetes_pre + Charlson_DiabetesComplications_+ Charlson_HemiplegiaParaplegia_p+ Charlson_LiverMild_pre + Charlson_LiverModSevere_pre +Charlson_Malignancy_pre + Charlson_MalignancyMetastatic_p+ Charlson_MI_pre + Charlson_PepticUlcer_pre+ Charlson_PeripheralVascular_pre + Charlson_Renal_pre + Charlson_Rheumatic_pre+ TT_Cardiology_pre + TT_CCU_HF_pre+TT_CCU_pre  + TT_HemeOnc_pre+ TT_Medicine_pre + TT_MICU_pre + TT_Neurology_pre + TT_SICU_pre + TT_SurgerySpecialty_pre + TT_Transplant_pre + TT_Trauma_pre + TT_CVICU_pre+ locf_PO2A_last  + locf_Pulse_last + locf_NA_last + locf_CR_last + locf_HCT_last + locf_WBC_last+ locf_BUN_last + locf_TBIL_last+ locf_K_last + locf_Resp_last + locf_Temp_last + locf_BP_High_Systolic_last +locf_GCSS_last+ locf_CO2_last+ locf_PHA_last, data = minlocf, ties = "breslow") 
minlocfit
cox_min<-tidy(minlocfit)
cox_min$set<-rep("minlocfit",57)

###########         maximum locf      ###############
maxlocfit<-coxph(Surv(curr_day,end_day, AnyDNR_within1day) ~ ageYears+ inc+self_pay+Female_pre +RaceUnknown_pre + RaceAsian_pre + RaceBlack_pre + all_latinos + RaceOther_pre +  RacePacificIslander_pre + RaceNativeAmerican_pre+ AnyVasoactive_pre + AnyVentilator_pre  + AnyCRRT_pre + Charlson_Cerebrovascular_pre + Charlson_CHF_pre + Charlson_COPD_pre + Charlson_Dementia_pre + Charlson_Diabetes_pre + Charlson_DiabetesComplications_+ Charlson_HemiplegiaParaplegia_p+ Charlson_LiverMild_pre + Charlson_LiverModSevere_pre +Charlson_Malignancy_pre + Charlson_MalignancyMetastatic_p+ Charlson_MI_pre + Charlson_PepticUlcer_pre+ Charlson_PeripheralVascular_pre + Charlson_Renal_pre + Charlson_Rheumatic_pre+ TT_Cardiology_pre + TT_CCU_HF_pre+TT_CCU_pre  + TT_HemeOnc_pre+ TT_Medicine_pre + TT_MICU_pre + TT_Neurology_pre + TT_SICU_pre + TT_SurgerySpecialty_pre + TT_Transplant_pre + TT_Trauma_pre + TT_CVICU_pre+ locf_PO2A_last  + locf_Pulse_last + locf_NA_last + locf_CR_last + locf_HCT_last + locf_WBC_last+ locf_BUN_last + locf_TBIL_last+ locf_K_last + locf_Resp_last + locf_Temp_last + locf_BP_High_Systolic_last +locf_GCSS_last+ locf_CO2_last+ locf_PHA_last, data = maxlocf, ties = "breslow") 
maxlocfit
cox_max<-tidy(maxlocfit)
cox_max$set<-rep("maxlocfit",57)
##################fixed covariates or no missing covars####################
fixedfit<-coxph(Surv(curr_day,end_day, AnyDNR_within1day) ~ ageYears+ inc+self_pay+Female_pre +RaceUnknown_pre + RaceAsian_pre + RaceBlack_pre + all_latinos + RaceOther_pre +  RacePacificIslander_pre + RaceNativeAmerican_pre+ AnyVasoactive_pre + AnyVentilator_pre  + AnyCRRT_pre + Charlson_Cerebrovascular_pre + Charlson_CHF_pre + Charlson_COPD_pre + Charlson_Dementia_pre + Charlson_Diabetes_pre + Charlson_DiabetesComplications_+ Charlson_HemiplegiaParaplegia_p+ Charlson_LiverMild_pre + Charlson_LiverModSevere_pre +Charlson_Malignancy_pre + Charlson_MalignancyMetastatic_p+ Charlson_MI_pre + Charlson_PepticUlcer_pre+ Charlson_PeripheralVascular_pre + Charlson_Renal_pre + Charlson_Rheumatic_pre+ TT_Cardiology_pre + TT_CCU_HF_pre+TT_CCU_pre  + TT_HemeOnc_pre+ TT_Medicine_pre + TT_MICU_pre + TT_Neurology_pre + TT_SICU_pre + TT_SurgerySpecialty_pre + TT_Transplant_pre + TT_Trauma_pre + TT_CVICU_pre, data = meanlocf, ties = "breslow") 
fixedfit
cox_fixed<-tidy(fixedfit)
cox_fixed$set<-rep("fixedfit",42)
####################model excluding certain covariates

#### excluding po2a resp and pha .....variables that may be collinear with ventilator####
ventillocfit<-coxph(Surv(curr_day,end_day, AnyDNR_within1day) ~ ageYears+ inc+self_pay+Female_pre +RaceUnknown_pre + RaceAsian_pre + RaceBlack_pre + all_latinos + RaceOther_pre +  RacePacificIslander_pre + RaceNativeAmerican_pre+ AnyVasoactive_pre + AnyVentilator_pre  + AnyCRRT_pre + Charlson_Cerebrovascular_pre + Charlson_CHF_pre + Charlson_COPD_pre + Charlson_Dementia_pre + Charlson_Diabetes_pre + Charlson_DiabetesComplications_+ Charlson_HemiplegiaParaplegia_p+ Charlson_LiverMild_pre + Charlson_LiverModSevere_pre +Charlson_Malignancy_pre + Charlson_MalignancyMetastatic_p+ Charlson_MI_pre + Charlson_PepticUlcer_pre+ Charlson_PeripheralVascular_pre + Charlson_Renal_pre + Charlson_Rheumatic_pre+ TT_Cardiology_pre + TT_CCU_HF_pre+TT_CCU_pre  + TT_HemeOnc_pre+ TT_Medicine_pre + TT_MICU_pre + TT_Neurology_pre + TT_SICU_pre + TT_SurgerySpecialty_pre + TT_Transplant_pre + TT_Trauma_pre + TT_CVICU_pre+ + locf_Pulse_last + locf_NA_last + locf_CR_last + locf_HCT_last + locf_WBC_last+ locf_BUN_last + locf_TBIL_last+ locf_K_last + locf_Temp_last + locf_BP_High_Systolic_last +locf_GCSS_last+ locf_CO2_last, data = meanlocf, ties = "breslow") 
ventillocfit
cox_ventillo<-tidy(ventillocfit)
cox_ventillo$set<-rep("ventillocfit",54)

#### excluding na cr k BUN co2 .....variables that may be collinear with CCRT####
ccrtlocfit<-coxph(Surv(curr_day,end_day, AnyDNR_within1day) ~ ageYears+ inc+self_pay+Female_pre +RaceUnknown_pre + RaceAsian_pre + RaceBlack_pre + all_latinos + RaceOther_pre +  RacePacificIslander_pre + RaceNativeAmerican_pre+ AnyVasoactive_pre + AnyVentilator_pre  + AnyCRRT_pre + Charlson_Cerebrovascular_pre + Charlson_CHF_pre + Charlson_COPD_pre + Charlson_Dementia_pre + Charlson_Diabetes_pre + Charlson_DiabetesComplications_+ Charlson_HemiplegiaParaplegia_p+ Charlson_LiverMild_pre + Charlson_LiverModSevere_pre +Charlson_Malignancy_pre + Charlson_MalignancyMetastatic_p+ Charlson_MI_pre + Charlson_PepticUlcer_pre+ Charlson_PeripheralVascular_pre + Charlson_Renal_pre + Charlson_Rheumatic_pre+ TT_Cardiology_pre + TT_CCU_HF_pre+TT_CCU_pre  + TT_HemeOnc_pre+ TT_Medicine_pre + TT_MICU_pre + TT_Neurology_pre + TT_SICU_pre + TT_SurgerySpecialty_pre + TT_Transplant_pre + TT_Trauma_pre + TT_CVICU_pre+ locf_PO2A_last  + locf_Pulse_last+ locf_HCT_last + locf_WBC_last+ locf_TBIL_last+locf_Resp_last + locf_Temp_last + locf_BP_High_Systolic_last +locf_GCSS_last+ locf_PHA_last, data = meanlocf, ties = "breslow") 
ccrtlocfit
cox_ccrt<-tidy(ccrtlocfit)
cox_ccrt$set<-rep("ccrtlocfit",52)

#### excluding pulse and sbp .....variables that may be collinear with vaso####
vasolocfit<-coxph(Surv(curr_day,end_day, AnyDNR_within1day) ~ ageYears+ inc+self_pay+Female_pre +RaceUnknown_pre + RaceAsian_pre + RaceBlack_pre + all_latinos + RaceOther_pre +  RacePacificIslander_pre + RaceNativeAmerican_pre+ AnyVasoactive_pre + AnyVentilator_pre  + AnyCRRT_pre + Charlson_Cerebrovascular_pre + Charlson_CHF_pre + Charlson_COPD_pre + Charlson_Dementia_pre + Charlson_Diabetes_pre + Charlson_DiabetesComplications_+ Charlson_HemiplegiaParaplegia_p+ Charlson_LiverMild_pre + Charlson_LiverModSevere_pre +Charlson_Malignancy_pre + Charlson_MalignancyMetastatic_p+ Charlson_MI_pre + Charlson_PepticUlcer_pre+ Charlson_PeripheralVascular_pre + Charlson_Renal_pre + Charlson_Rheumatic_pre+ TT_Cardiology_pre + TT_CCU_HF_pre+TT_CCU_pre  + TT_HemeOnc_pre+ TT_Medicine_pre + TT_MICU_pre + TT_Neurology_pre + TT_SICU_pre + TT_SurgerySpecialty_pre + TT_Transplant_pre + TT_Trauma_pre + TT_CVICU_pre+ locf_PO2A_last + locf_NA_last + locf_CR_last + locf_HCT_last + locf_WBC_last+ locf_BUN_last + locf_TBIL_last+ locf_K_last + locf_Resp_last + locf_Temp_last+locf_GCSS_last+ locf_CO2_last+ locf_PHA_last, data = meanlocf, ties = "breslow") 
vasolocfit
cox_vaso<-tidy(vasolocfit)
cox_vaso$set<-rep("vasolocfit",55)
######################################################################################################################################
###cox models combined for forest plot###########
cox_forest<-rbind(cox_fixed,cox_mean,cox_min,cox_max,cox_ventillo,cox_vaso,cox_ccrt)

# exponentiate extimates and limits and plot forest 
cox_forest$expcoef<-exp(cox_forest$estimate)
cox_forest$explcl<-exp(cox_forest$conf.low)
cox_forest$expucl<-exp(cox_forest$conf.high)
write.csv(cox_forest, file = "/Volumes/QSU/Datasets/HM/Jonathan Chen-DNR/Aug_datasets/cox_forest.csv",row.names=FALSE, na="")

#############################################################################################################
#
#
#########################COMFORT CARE MODEL################################################################

meanlocf= read.table("/Volumes/QSU/Datasets/HM/Jonathan Chen-DNR/Aug_datasets/Meannorm_locf.csv", header = T, sep = ",")
meanlocf<-meanlocf[order(meanlocf$patid,meanlocf$curr_day),] #138647
meanclocf <- meanlocf[which(meanlocf$ComfortCare_pre=='FALSE'),] #137336
meanclocf$income<-as.numeric(meanclocf$income)
meanclocf$inc<-meanclocf$income/1000
#firstday <- meanclocf[meanclocf$curr_day == 0,]
#sum((firstday$ComfortCare_post) & (firstday$ComfortCare_postTimeDays <firstday$daysUntilEnd+1));


minlocf= read.table("/Volumes/QSU/Datasets/HM/Jonathan Chen-DNR/Aug_datasets/Minnorm_locf.csv", header = T, sep = ",")
minlocf<-minlocf[order(minlocf$patid,minlocf$curr_day),] 
minclocf <- minlocf[which(minlocf$ComfortCare_pre=='FALSE'),] 
minclocf$income<-as.numeric(minclocf$income)
minclocf$inc<-minclocf$income/1000

maxlocf= read.table("/Volumes/QSU/Datasets/HM/Jonathan Chen-DNR/Aug_datasets/Maxnorm_locf.csv", header = T, sep = ",")
maxlocf<-maxlocf[order(maxlocf$patid,maxlocf$curr_day),] 
maxclocf <- maxlocf[which(maxlocf$ComfortCare_pre=='FALSE'),] 
maxclocf$income<-as.numeric(maxclocf$income)
maxclocf$inc<-maxclocf$income/1000

library(survival)
library(broom)

meanclocfit<-coxph(Surv(curr_day,end_day,ComfortCare_within1day) ~ ageYears+ inc+self_pay+Female_pre +RaceUnknown_pre + RaceAsian_pre + RaceBlack_pre + all_latinos + RaceOther_pre +  RacePacificIslander_pre + RaceNativeAmerican_pre+ AnyVasoactive_pre + AnyVentilator_pre  + AnyCRRT_pre + Charlson_Cerebrovascular_pre + Charlson_CHF_pre + Charlson_COPD_pre + Charlson_Dementia_pre + Charlson_Diabetes_pre + Charlson_DiabetesComplications_+ Charlson_HemiplegiaParaplegia_p+ Charlson_LiverMild_pre + Charlson_LiverModSevere_pre +Charlson_Malignancy_pre + Charlson_MalignancyMetastatic_p+ Charlson_MI_pre + Charlson_PepticUlcer_pre+ Charlson_PeripheralVascular_pre + Charlson_Renal_pre + Charlson_Rheumatic_pre+ TT_Cardiology_pre + TT_CCU_HF_pre+TT_CCU_pre  + TT_HemeOnc_pre+ TT_Medicine_pre + TT_MICU_pre + TT_Neurology_pre + TT_SICU_pre + TT_SurgerySpecialty_pre + TT_Transplant_pre + TT_Trauma_pre + TT_CVICU_pre+ locf_PO2A_last  + locf_Pulse_last + locf_NA_last + locf_CR_last + locf_HCT_last + locf_WBC_last+ locf_BUN_last + locf_TBIL_last+ locf_K_last + locf_Resp_last + locf_Temp_last + locf_BP_High_Systolic_last +locf_GCSS_last+ locf_CO2_last+ locf_PHA_last, data = meanclocf, ties = "breslow") 
meanclocfit
cox_cmean<-tidy(meanclocfit)
cox_cmean$set<-rep("cc_meanlocfit",57)
###########         minimum locf      ###############
minclocfit<-coxph(Surv(curr_day,end_day,ComfortCare_within1day) ~ ageYears+ inc+self_pay+Female_pre +RaceUnknown_pre + RaceAsian_pre + RaceBlack_pre + all_latinos + RaceOther_pre +  RacePacificIslander_pre + RaceNativeAmerican_pre+ AnyVasoactive_pre + AnyVentilator_pre  + AnyCRRT_pre + Charlson_Cerebrovascular_pre + Charlson_CHF_pre + Charlson_COPD_pre + Charlson_Dementia_pre + Charlson_Diabetes_pre + Charlson_DiabetesComplications_+ Charlson_HemiplegiaParaplegia_p+ Charlson_LiverMild_pre + Charlson_LiverModSevere_pre +Charlson_Malignancy_pre + Charlson_MalignancyMetastatic_p+ Charlson_MI_pre + Charlson_PepticUlcer_pre+ Charlson_PeripheralVascular_pre + Charlson_Renal_pre + Charlson_Rheumatic_pre+ TT_Cardiology_pre + TT_CCU_HF_pre+TT_CCU_pre  + TT_HemeOnc_pre+ TT_Medicine_pre + TT_MICU_pre + TT_Neurology_pre + TT_SICU_pre + TT_SurgerySpecialty_pre + TT_Transplant_pre + TT_Trauma_pre + TT_CVICU_pre+ locf_PO2A_last  + locf_Pulse_last + locf_NA_last + locf_CR_last + locf_HCT_last + locf_WBC_last+ locf_BUN_last + locf_TBIL_last+ locf_K_last + locf_Resp_last + locf_Temp_last + locf_BP_High_Systolic_last +locf_GCSS_last+ locf_CO2_last+ locf_PHA_last, data = minclocf, ties = "breslow") 
#minclocfit
cox_cmin<-tidy(minclocfit)
cox_cmin$set<-rep("cc_minlocfit",57)

###########         maximum locf      ###############
maxclocfit<-coxph(Surv(curr_day,end_day,ComfortCare_within1day) ~ ageYears+ inc+self_pay+Female_pre +RaceUnknown_pre + RaceAsian_pre + RaceBlack_pre + all_latinos + RaceOther_pre +  RacePacificIslander_pre + RaceNativeAmerican_pre+ AnyVasoactive_pre + AnyVentilator_pre  + AnyCRRT_pre + Charlson_Cerebrovascular_pre + Charlson_CHF_pre + Charlson_COPD_pre + Charlson_Dementia_pre + Charlson_Diabetes_pre + Charlson_DiabetesComplications_+ Charlson_HemiplegiaParaplegia_p+ Charlson_LiverMild_pre + Charlson_LiverModSevere_pre +Charlson_Malignancy_pre + Charlson_MalignancyMetastatic_p+ Charlson_MI_pre + Charlson_PepticUlcer_pre+ Charlson_PeripheralVascular_pre + Charlson_Renal_pre + Charlson_Rheumatic_pre+ TT_Cardiology_pre + TT_CCU_HF_pre+TT_CCU_pre  + TT_HemeOnc_pre+ TT_Medicine_pre + TT_MICU_pre + TT_Neurology_pre + TT_SICU_pre + TT_SurgerySpecialty_pre + TT_Transplant_pre + TT_Trauma_pre + TT_CVICU_pre+ locf_PO2A_last  + locf_Pulse_last + locf_NA_last + locf_CR_last + locf_HCT_last + locf_WBC_last+ locf_BUN_last + locf_TBIL_last+ locf_K_last + locf_Resp_last + locf_Temp_last + locf_BP_High_Systolic_last +locf_GCSS_last+ locf_CO2_last+ locf_PHA_last, data = maxclocf, ties = "breslow") 
#maxclocfit
cox_cmax<-tidy(maxclocfit)
cox_cmax$set<-rep("cc_maxlocfit",57)
##################fixed covariates or no missing covars####################
fixedfitc<-coxph(Surv(curr_day,end_day,ComfortCare_within1day) ~ ageYears+ income+self_pay+Female_pre +RaceUnknown_pre + RaceAsian_pre + RaceBlack_pre + all_latinos + RaceOther_pre +  RacePacificIslander_pre + RaceNativeAmerican_pre+ AnyVasoactive_pre + AnyVentilator_pre  + AnyCRRT_pre + Charlson_Cerebrovascular_pre + Charlson_CHF_pre + Charlson_COPD_pre + Charlson_Dementia_pre + Charlson_Diabetes_pre + Charlson_DiabetesComplications_+ Charlson_HemiplegiaParaplegia_p+ Charlson_LiverMild_pre + Charlson_LiverModSevere_pre +Charlson_Malignancy_pre + Charlson_MalignancyMetastatic_p+ Charlson_MI_pre + Charlson_PepticUlcer_pre+ Charlson_PeripheralVascular_pre + Charlson_Renal_pre + Charlson_Rheumatic_pre+ TT_Cardiology_pre + TT_CCU_HF_pre+TT_CCU_pre  + TT_HemeOnc_pre+ TT_Medicine_pre + TT_MICU_pre + TT_Neurology_pre + TT_SICU_pre + TT_SurgerySpecialty_pre + TT_Transplant_pre + TT_Trauma_pre + TT_CVICU_pre, data = meanclocf, ties = "breslow") 
#fixedfitc
cox_cfixed<-tidy(fixedfitc)
cox_cfixed$set<-rep("cc_fixedfit",42)
####################model excluding certain covariates

#### excluding po2a resp and pha .....variables that may be collinear with ventilator####
ventilclocfit<-coxph(Surv(curr_day,end_day,ComfortCare_within1day) ~ ageYears+ inc+self_pay+Female_pre +RaceUnknown_pre + RaceAsian_pre + RaceBlack_pre + all_latinos + RaceOther_pre +  RacePacificIslander_pre + RaceNativeAmerican_pre+ AnyVasoactive_pre + AnyVentilator_pre  + AnyCRRT_pre + Charlson_Cerebrovascular_pre + Charlson_CHF_pre + Charlson_COPD_pre + Charlson_Dementia_pre + Charlson_Diabetes_pre + Charlson_DiabetesComplications_+ Charlson_HemiplegiaParaplegia_p+ Charlson_LiverMild_pre + Charlson_LiverModSevere_pre +Charlson_Malignancy_pre + Charlson_MalignancyMetastatic_p+ Charlson_MI_pre + Charlson_PepticUlcer_pre+ Charlson_PeripheralVascular_pre + Charlson_Renal_pre + Charlson_Rheumatic_pre+ TT_Cardiology_pre + TT_CCU_HF_pre+TT_CCU_pre  + TT_HemeOnc_pre+ TT_Medicine_pre + TT_MICU_pre + TT_Neurology_pre + TT_SICU_pre + TT_SurgerySpecialty_pre + TT_Transplant_pre + TT_Trauma_pre + TT_CVICU_pre+ + locf_Pulse_last + locf_NA_last + locf_CR_last + locf_HCT_last + locf_WBC_last+ locf_BUN_last + locf_TBIL_last+ locf_K_last + locf_Temp_last + locf_BP_High_Systolic_last +locf_GCSS_last+ locf_CO2_last, data = meanclocf, ties = "breslow") 
#ventilclocfit
cox_cventillo<-tidy(ventilclocfit)
cox_cventillo$set<-rep("cc_ventillocfit",54)

#### excluding na cr k BUN co2 .....variables that may be collinear with CCRT####
ccrtclocfit<-coxph(Surv(curr_day,end_day,ComfortCare_within1day) ~ ageYears+ inc+self_pay+Female_pre +RaceUnknown_pre + RaceAsian_pre + RaceBlack_pre + all_latinos + RaceOther_pre +  RacePacificIslander_pre + RaceNativeAmerican_pre+ AnyVasoactive_pre + AnyVentilator_pre  + AnyCRRT_pre + Charlson_Cerebrovascular_pre + Charlson_CHF_pre + Charlson_COPD_pre + Charlson_Dementia_pre + Charlson_Diabetes_pre + Charlson_DiabetesComplications_+ Charlson_HemiplegiaParaplegia_p+ Charlson_LiverMild_pre + Charlson_LiverModSevere_pre +Charlson_Malignancy_pre + Charlson_MalignancyMetastatic_p+ Charlson_MI_pre + Charlson_PepticUlcer_pre+ Charlson_PeripheralVascular_pre + Charlson_Renal_pre + Charlson_Rheumatic_pre+ TT_Cardiology_pre + TT_CCU_HF_pre+TT_CCU_pre  + TT_HemeOnc_pre+ TT_Medicine_pre + TT_MICU_pre + TT_Neurology_pre + TT_SICU_pre + TT_SurgerySpecialty_pre + TT_Transplant_pre + TT_Trauma_pre + TT_CVICU_pre+ locf_PO2A_last  + locf_Pulse_last+ locf_HCT_last + locf_WBC_last+ locf_TBIL_last+locf_Resp_last + locf_Temp_last + locf_BP_High_Systolic_last +locf_GCSS_last+ locf_PHA_last, data = meanclocf, ties = "breslow") 
ccrtclocfit
cox_c_ccrt<-tidy(ccrtclocfit)
cox_c_ccrt$set<-rep("cc_ccrtlocfit",52)

#### excluding pulse and sbp .....variables that may be collinear with vaso####
vasoclocfit<-coxph(Surv(curr_day,end_day,ComfortCare_within1day) ~ ageYears+ inc+self_pay+Female_pre +RaceUnknown_pre + RaceAsian_pre + RaceBlack_pre + all_latinos + RaceOther_pre +  RacePacificIslander_pre + RaceNativeAmerican_pre+ AnyVasoactive_pre + AnyVentilator_pre  + AnyCRRT_pre + Charlson_Cerebrovascular_pre + Charlson_CHF_pre + Charlson_COPD_pre + Charlson_Dementia_pre + Charlson_Diabetes_pre + Charlson_DiabetesComplications_+ Charlson_HemiplegiaParaplegia_p+ Charlson_LiverMild_pre + Charlson_LiverModSevere_pre +Charlson_Malignancy_pre + Charlson_MalignancyMetastatic_p+ Charlson_MI_pre + Charlson_PepticUlcer_pre+ Charlson_PeripheralVascular_pre + Charlson_Renal_pre + Charlson_Rheumatic_pre+ TT_Cardiology_pre + TT_CCU_HF_pre+TT_CCU_pre  + TT_HemeOnc_pre+ TT_Medicine_pre + TT_MICU_pre + TT_Neurology_pre + TT_SICU_pre + TT_SurgerySpecialty_pre + TT_Transplant_pre + TT_Trauma_pre + TT_CVICU_pre+ locf_PO2A_last + locf_NA_last + locf_CR_last + locf_HCT_last + locf_WBC_last+ locf_BUN_last + locf_TBIL_last+ locf_K_last + locf_Resp_last + locf_Temp_last+locf_GCSS_last+ locf_CO2_last+ locf_PHA_last, data = meanclocf, ties = "breslow") 
vasoclocfit
cox_cvaso<-tidy(vasoclocfit)
cox_cvaso$set<-rep("cc_vasolocfit",55)
######################################################################################################################################
###cox models combined for forest plot###########
cox_cforest<-rbind(cox_cfixed,cox_cmean,cox_cmin,cox_cmax,cox_cventillo,cox_cvaso,cox_c_ccrt)

# exponentiate extimates and limits and plot forest 
cox_cforest$expcoef<-exp(cox_cforest$estimate)
cox_cforest$explcl<-exp(cox_cforest$conf.low)
cox_cforest$expucl<-exp(cox_cforest$conf.high)
write.csv(cox_cforest, file = "/Volumes/QSU/Datasets/HM/Jonathan Chen-DNR/Aug_datasets/cc_cox_forest.csv",row.names=FALSE, na="")