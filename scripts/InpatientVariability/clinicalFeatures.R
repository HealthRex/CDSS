library(tidyverse)
library(bigrquery)

# library(DBI)
# library(scales)
# library(sqldf) # https://www.r-bloggers.com/in-between-a-rock-and-a-conditional-join/
# library(fuzzyjoin)
# library(rio)

# warning = TRUE # default
# options(warn = 0) # default
warning = FALSE
options(warn = -1)
options(scipen = 20)

##### filepaths
dir <- "/Users/kushgupta/Documents/StanfordMD/Projects/Mentors/Chen/Inpatient\ Variability\ Cost\ Reduction/code/"
filepath1 <- paste0(dir,"clinicalFeatures.sql")

##### import data
sqlQuery <- readChar(filepath1, file.info(filepath1)$size)
project <- "som-nero-phi-jonc101-secure" # "mining-clinical-decisions"
results <- bq_project_query(project, sqlQuery)
tb1 <- as_tibble(bq_table_download(results, bigint = c("integer64"))) # bigint needed to properly download full PT_ENC_CSN_ID
rm(results)

##### identify cost categories that have highest relative variance (coefficient of variance): respiratory therapy, implants (many NA's), supplies, ICU, IICU, Accom, Pharmacy
# coefVar <- function(x){
#   stdev = sd(x,na.rm=TRUE)
#   avg = mean(x,na.rm=TRUE)
#   return(stdev/avg)
# }
# cv <- tb %>% summarise(across(starts_with("Cost_"), coefVar)) # %>% t()
# cv <- pivot_longer(cv, cols=starts_with("Cost_"), names_to="category", values_to="coefVar") %>% arrange(desc(coefVar))
# cv
# 
# tb %>% summarise(across(starts_with("Cost_"), sum(is.na))) # %>% t()

##### cleaning table
#mrn, AdmitTRUE, DischTRUE, LOS, Cost_Direct, Cost_Total, anon_id, enc, admsnTimeJTR, dischTimeJTR, drg, drg_c,
#GENDER, CANONICAL_ETHNICITY, CANONICAL_RACE, INTRPTR_NEEDED_YN, INSURANCE_PAYOR_NAME, BMI, CHARLSON_SCORE, N_HOSPITALIZATIONS, DAYS_IN_HOSPITAL,
#firstRT_daysb4dc, firstPT_daysb4dc, firstOT_daysb4dc, firstSLP_daysb4dc, firstSW_daysb4dc,
#medID, med_description, med_route, dose_unit, totalDose, lastAdminJTR, lastOpioidAdminJTR
#ordersetSmartGroup, ordersetProtocol, ordersetTime

cohort <- tb %>% select(enc, Cost_Total) %>% distinct()

patientFactors <- tb %>% select(enc, GENDER, CANONICAL_ETHNICITY, CANONICAL_RACE, INTRPTR_NEEDED_YN, INSURANCE_PAYOR_NAME, BMI, CHARLSON_SCORE, N_HOSPITALIZATIONS, DAYS_IN_HOSPITAL) %>% distinct()
patientFactors[,8:10] <- lapply(patientFactors[,8:10],as.numeric)

### analyze therapy orders
therapyOrders <- tb %>% select(enc, Cost_Total, LOS, firstRT_daysb4dc, firstPT_daysb4dc, firstOT_daysb4dc, firstSLP_daysb4dc, firstSW_daysb4dc) %>% distinct()
therapyOrders <- therapyOrders %>% mutate(across(c(1:ncol(therapyOrders)), as.numeric)) # across(starts_with("first"), as.numeric)
ggplot(data = therapyOrders) + geom_point(mapping = aes(x = firstOT_daysb4dc, y = LOS))
ggplot(data = therapyOrders) + geom_point(mapping = aes(x = firstPT_daysb4dc, y = LOS))
fit1 = lm(Cost_Total ~ firstOT_daysb4dc, data=therapyOrders)
summary(fit1) 
fit2 = lm(Cost_Total ~ firstPT_daysb4dc, data=therapyOrders)
summary(fit2) 
fit3 = lm(Cost_Total ~ firstOT_daysb4dc*firstPT_daysb4dc, data=therapyOrders)
summary(fit3)
par(mfrow=c(2,2))
plot(fit1) # 4 plots get produced by a linear models
plot(fit2)
plot(fit3)
fit1 = lm(LOS ~ firstOT_daysb4dc, data=therapyOrders)
summary(fit1) 
fit2 = lm(LOS ~ firstPT_daysb4dc, data=therapyOrders)
summary(fit2) 
fit3 = lm(LOS ~ firstOT_daysb4dc*firstPT_daysb4dc, data=therapyOrders)
summary(fit3)

### analyze opioids (only considering columns that are mostly NA <- inspected manually to do this)
opioids <- tb %>% select(enc, Cost_Total, dischTimeJTR, med_description, totalDose, lastOpioidAdminJTR) %>% distinct()
opioids$oralMME <- NA
opioids <- opioids %>% mutate(oralMME = ifelse(med_description=="HYDROMORPHONE 1 MG/ML INJ SYRG",totalDose * 20,oralMME)) # convert to oral MME
opioids <- opioids %>% mutate(oralMME = ifelse(med_description=="OXYCODONE 5 MG PO TABS",totalDose * 1.5,oralMME)) # convert to oral MME
opioids <- opioids %>% mutate(oralMME = ifelse(med_description=="OXYCODONE 5 MG/5 ML PO SOLN",totalDose * 1.5,oralMME)) # convert to oral MME
opioids <- opioids %>% mutate(oralMME = ifelse(med_description=="FENTANYL CITRATE (PF) 50 MCG/ML INJ SOLN (WRAPPER RECORD)",totalDose * 0.3,oralMME)) # convert to oral MME
opioids <- opioids %>% mutate(oralMME = ifelse(med_description=="TRAMADOL 50 MG PO TABS",totalDose * 0.1,oralMME)) # convert to oral MME
ggplot(data = opioids) + 
  geom_point(mapping = aes(x = (oralMME), y = Cost_Total, color = med_description)) +
  geom_smooth(method='lm', se=FALSE, mapping = aes(x = (oralMME), y = Cost_Total, color= med_description)) +
  xlim(0,1000)
opioids <- opioids %>% group_by(enc) %>% mutate(totalOralMME = sum(oralMME))
ggplot(data = opioids) + 
  geom_point(mapping = aes(x = totalOralMME, y = Cost_Total)) +
  geom_smooth(method='lm', se=TRUE, mapping = aes(x = totalOralMME, y = Cost_Total))
  xlim(0,1000)
opioids <- pivot_wider(opioids, names_from = med_description, values_from = oralMME)
opioids$lastOpioidAdmin_daysb4dc <- as.numeric(difftime(opioids$dischTimeJTR, opioids$lastOpioidAdminJTR, units="days")) # a$admsnTimeJTR - as.difftime(as.integer(a$JITTER),units="days")
opioids <- opioids %>% select(-dischTimeJTR,-lastOpioidAdminJTR)
opioids <- opioids %>% select(-enc)
fit1 = lm(Cost_Total ~ `HYDROMORPHONE 1 MG/ML INJ SYRG`, data=opioids)
fit2 = lm(Cost_Total ~ `OXYCODONE 5 MG PO TABS`, data=opioids)
fit3 = lm(Cost_Total ~ `FENTANYL CITRATE (PF) 50 MCG/ML INJ SOLN (WRAPPER RECORD)`, data=opioids)
fit4 = lm(Cost_Total ~ `HYDROMORPHONE 1 MG/ML INJ SYRG` * `OXYCODONE 5 MG PO TABS` * `FENTANYL CITRATE (PF) 50 MCG/ML INJ SOLN (WRAPPER RECORD)`, data=opioids)
summary(fit1) 
summary(fit2) 
summary(fit3) 
summary(fit4) 
print(paste("significant predictors are:", "HYDROMORPHONE 1 MG/ML INJ SYRG"))

ordersets <- tb %>% select(enc, ordersetProtocol, ordersetTime) %>% distinct()
ordersets <- ordersets %>% group_by(enc, ordersetProtocol) %>% summarise(lastOrdered = max(ordersetTime)) %>% filter(!is.na(lastOrdered))
ordersets <- pivot_wider(ordersets, names_from = ordersetProtocol, values_from = lastOrdered)
ordersets <- cbind(ordersets[,1], as_tibble(!is.na(ordersets[,2:ncol(ordersets)])))

features <- cohort %>% 
              left_join(patientFactors) %>%
              left_join(therapyOrders) %>%
              left_join(opioids) %>%
              inner_join(ordersets)
features <- features %>% select(-c(enc))

fit7 = lm(Cost_Total ~ `ANE PACU `, data=features)
summary(fit7) 

fit1 = lm(
  as.formula(paste(colnames(features)[1], "~",
             paste(colnames(features)[c(2:10,12,13)], collapse = "+"), #don't work: 8,9,10
             sep = ""
  )),
  data=features,
  na.action=na.exclude #,na.action=na.omit
)
summary(fit1) 

missing <- function(x) { sum(is.na(x))}

####
opioids
SQL coalesce --> if value is NULL, replace with 0. if not NULL, give back actual value. 
Jon thoughts: why do we have NAs for opioids... unexpected
convert to morphine equivalents --> if we control for ME, does IV vs PO make difference?
see if epidurals / spinals / IV lidocaine reduced costs

PT/OT is interesting, positive coefficient is curious
do both LOS and total Cost --> expect LOS to go down and Cost to perhaps stay even as PT_daysb4dc goes up

ask Rocky about ask Rocky about ask Rocky about plots