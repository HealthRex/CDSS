library(survival)
df.cox = df.amelia.final

names(df.cox)[names(df.cox) == "curr_day"] = "start"
df.cox$end = df.cox$start + 1

df.noPrevDNR = df.cox[df.cox$AnyDNR.pre == 0,]

cox.noPrevDnr.dem = coxph(Surv(start, end, AnyDNR.within1day) ~Birth.preTimeDays+ income + Female.pre + 
                            RaceUnknown.pre + RaceAsian.pre + RaceBlack.pre + all_latinos + RaceOther.pre +  RacePacificIslander.pre +
                            self_pay, data = df.noPrevDNR, ties = "breslow")

cox.noPrevDNR.vital = coxph(Surv(start, end, AnyDNR.within1day) ~Birth.preTimeDays+ income + Female.pre + 
                              RaceUnknown.pre + RaceAsian.pre + RaceBlack.pre + all_latinos + 
                              RaceOther.pre +  RacePacificIslander.pre + 
                              + AnyVasoactive.pre + AnyVentilator.pre  + AnyCRRT.pre +
                              Charlson.Cerebrovascular.pre + Charlson.CHF.pre + Charlson.COPD.pre + 
                              Charlson.Dementia.pre + Charlson.Diabetes.pre + Charlson.DiabetesComplications.pre
                            + Charlson.HemiplegiaParaplegia.pre + Charlson.LiverMild.pre + Charlson.LiverModSevere.pre +
                              Charlson.Malignancy.pre + Charlson.MalignancyMetastatic.pre + Charlson.MI.pre + Charlson.PepticUlcer.pre 
                            + Charlson.PeripheralVascular.pre + Charlson.Renal.pre + Charlson.Rheumatic.pre  
                            + self_pay+  PO2A.last  + Pulse.last + NA.last + CR.last + HCT.last + WBC.last
                            + BUN.last + TBIL.last+ K.last + Resp.last + Temp.last + Urine.last
                            + BP_Low_Diastolic.last + BP_High_Systolic.last + Glasgow.Coma.Scale.Score.last
                            + TT.Cardiology.pre + TT.CCU.HF.pre+TT.CCU.pre  + TT.HemeOnc.pre
                            + TT.Medicine.pre + TT.MICU.pre + TT.Neurology.pre + TT.SICU.pre  
                            + TT.SurgerySpecialty.pre + TT.Transplant.pre + TT.Trauma.pre + 
                              self_pay, data = df.noPrevDNR, ties = "breslow")

results.cox.noPrevComfortCare.dem = summary(cox.noPrevDnr.dem)$coef
confint.cox.noPrevComfortCare.dem = confint(cox.noPrevDnr.dem)
write.csv(results.cox.noPrevComfortCare.dem,file = "OR results Cox DNR Dem.csv")
write.csv(confint.cox.noPrevComfortCare.dem, file = "CI results Cox DNR Dem.csv")

results.cox.noPrevComfortCare.vital = summary(cox.noPrevDNR.vital)$coef
confint.cox.noPrevComfortCare.vital = confint(cox.noPrevDNR.vital)
write.csv(results.cox.noPrevComfortCare.vital,file = "OR results Cox DNR Vital.csv")
write.csv(confint.cox.noPrevComfortCare.vital, file = "CI results Cox DNR Vital.csv")

#Pallaitive care 
df.noPrevPalliativeCare = df.cox[df.cox$PalliativeConsult.pre == 0,]

cox.noPrevPalliativeCare.dem  = coxph(Surv(start, end, PalliativeCare.within1day) ~Birth.preTimeDays+ income + Female.pre + 
                                   RaceUnknown.pre + RaceAsian.pre + RaceBlack.pre + all_latinos + 
                                   RaceOther.pre +  RacePacificIslander.pre +
                                   self_pay, data = df.noPrevPalliativeCare, ties = "breslow")

cox.noPrevPalliativeCare.vital = coxph(Surv(start, end, PalliativeCare.within1day) ~Birth.preTimeDays+ income + Female.pre + 
                              RaceUnknown.pre + RaceAsian.pre + RaceBlack.pre + all_latinos + 
                              RaceOther.pre +  RacePacificIslander.pre + 
                              + AnyVasoactive.pre + AnyVentilator.pre  + AnyCRRT.pre +
                              Charlson.Cerebrovascular.pre + Charlson.CHF.pre + Charlson.COPD.pre + 
                              Charlson.Dementia.pre + Charlson.Diabetes.pre + Charlson.DiabetesComplications.pre
                            + Charlson.HemiplegiaParaplegia.pre + Charlson.LiverMild.pre + Charlson.LiverModSevere.pre +
                              Charlson.Malignancy.pre + Charlson.MalignancyMetastatic.pre + Charlson.MI.pre + Charlson.PepticUlcer.pre 
                            + Charlson.PeripheralVascular.pre + Charlson.Renal.pre + Charlson.Rheumatic.pre  
                            + self_pay+  PO2A.last  + Pulse.last + NA.last + CR.last + HCT.last + WBC.last
                            + BUN.last + TBIL.last+ K.last + Resp.last + Temp.last + Urine.last
                            + BP_Low_Diastolic.last + BP_High_Systolic.last + Glasgow.Coma.Scale.Score.last
                            + TT.Cardiology.pre + TT.CCU.HF.pre+TT.CCU.pre  + TT.HemeOnc.pre
                            + TT.Medicine.pre + TT.MICU.pre + TT.Neurology.pre + TT.SICU.pre  
                            + TT.SurgerySpecialty.pre + TT.Transplant.pre + TT.Trauma.pre + 
                              self_pay, data = df.noPrevPalliativeCare, ties = "breslow")

results.cox.noPrevPalliativeCare.dem = summary(cox.noPrevPalliativeCare.dem)$coef
confint.cox.noPrevPalliativeCare.dem = confint(cox.noPrevPalliativeCare.dem)
write.csv(results.cox.noPrevPalliativeCare.dem,file = "OR results Cox Pall dem.csv")
write.csv(confint.cox.noPrevPalliativeCare.dem, file = "CI results Cox Pall dem.csv")

results.cox.noPrevPalliativeCare.vital = summary(cox.noPrevPalliativeCare.vital)$coef
confint.cox.noPrevPalliativeCare.vital = confint(cox.noPrevPalliativeCare.vital)
write.csv(results.cox.noPrevPalliativeCare.vital,file = "OR results Cox pall vital.csv")
write.csv(confint.cox.noPrevPalliativeCare.vital, file = "CI results Cox pall vital.csv")

#Comfort Care
df.noPrevComfortCare = df.cox[df.cox$ComfortCare.pre == 0,]

cox.noPrevComfortCare.dem = coxph(Surv(start, end, ComfortCare.within1day) ~Birth.preTimeDays+ income + Female.pre + 
                                   RaceUnknown.pre + RaceAsian.pre + RaceBlack.pre + all_latinos + 
                                   RaceOther.pre +  RacePacificIslander.pre +
                                   self_pay, data = df.noPrevComfortCare, ties = "breslow")

cox.noPrevComfortCare.vital = coxph(Surv(start, end, PalliativeCare.within1day) ~Birth.preTimeDays+ income + Female.pre + 
                                         RaceUnknown.pre + RaceAsian.pre + RaceBlack.pre + all_latinos + 
                                         RaceOther.pre +  RacePacificIslander.pre + 
                                         + AnyVasoactive.pre + AnyVentilator.pre  + AnyCRRT.pre +
                                         Charlson.Cerebrovascular.pre + Charlson.CHF.pre + Charlson.COPD.pre + 
                                         Charlson.Dementia.pre + Charlson.Diabetes.pre + Charlson.DiabetesComplications.pre
                                       + Charlson.HemiplegiaParaplegia.pre + Charlson.LiverMild.pre + Charlson.LiverModSevere.pre +
                                         Charlson.Malignancy.pre + Charlson.MalignancyMetastatic.pre + Charlson.MI.pre + Charlson.PepticUlcer.pre 
                                       + Charlson.PeripheralVascular.pre + Charlson.Renal.pre + Charlson.Rheumatic.pre  
                                       + self_pay+  PO2A.last  + Pulse.last + NA.last + CR.last + HCT.last + WBC.last
                                       + BUN.last + TBIL.last+ K.last + Resp.last + Temp.last + Urine.last
                                       + BP_Low_Diastolic.last + BP_High_Systolic.last + Glasgow.Coma.Scale.Score.last
                                       + TT.Cardiology.pre + TT.CCU.HF.pre+TT.CCU.pre  + TT.HemeOnc.pre
                                       + TT.Medicine.pre + TT.MICU.pre + TT.Neurology.pre + TT.SICU.pre  
                                       + TT.SurgerySpecialty.pre + TT.Transplant.pre + TT.Trauma.pre + 
                                         self_pay, data = df.noPrevComfortCare, ties = "breslow")

results.cox.noPrevComfortCare.dem = summary(cox.noPrevComfortCare.dem)$coef
confint.cox.noPrevComfortCare.dem = confint(cox.noPrevComfortCare.dem)
write.csv(results.cox.noPrevComfortCare.dem,file = "OR results Cox Comfort Care dem.csv")
write.csv(confint.cox.noPrevComfortCare.dem, file = "CI results Cox Comfort Care dem.csv")

results.cox.noPrevComfortCare.vital = summary(cox.noPrevComfortCare.vital)$coef
confint.cox.noPrevComfortCare.vital = confint(cox.noPrevComfortCare.vital)
write.csv(results.cox.noPrevComfortCare.vital,file = "OR results Cox Comfort Care vital.csv")
write.csv(confint.cox.noPrevComfortCare.vital, file = "CI results Cox Comfort Care vital.csv")