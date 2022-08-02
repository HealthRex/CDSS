library(tidyverse)
library(bigrquery)
library(caret)
library(mlbench)
library(tidyverse)
library(glmnet)

# library(DBI)
# library(scales)
# library(sqldf) # https://www.r-bloggers.com/in-between-a-rock-and-a-conditional-join/
# library(fuzzyjoin)
# library(rio)

## warning = TRUE # default
## options(warn = 0) # default
# warning = FALSE
# options(warn = -1)
# options(scipen = 20)

##############################################################################
##### filepaths
dir <- "/Users/kushgupta/Documents/StanfordMD/Projects/Mentors/Chen/Inpatient\ Variability\ Cost\ Reduction/"
filepath0 <- paste0(dir,"code/cohortSelection.sql")
filepath1 <- paste0(dir,"code/comorbiditiesOnAdmission.sql")
filepath2 <- paste0(dir,"code/objectiveFeatures.sql")

##############################################################################
##### import data: comorbidities
sqlQuery0 <- readChar(filepath0, file.info(filepath0)$size)
sqlQuery1 <- readChar(filepath1, file.info(filepath1)$size)
sqlQuery1 <- paste0(sqlQuery0, sqlQuery1)
project <- "som-nero-phi-jonc101-secure" # "mining-clinical-decisions"
results <- bq_project_query(project, sqlQuery1)
tb <- as_tibble(bq_table_download(results, bigint = c("integer64"))) # bigint needed to properly download full PT_ENC_CSN_ID
rm(results)

print(paste0(tb %>% distinct(enc) %>% nrow(), " distinct patient encounters"))

categories <- read_csv(paste0(dir,"data/AHRQ_CCSR_2022/categories.csv"), col_names=c("CCSR", "CCSR_modified", "category"))
categories <- categories %>% select(-CCSR_modified)

##############################################################################
df <- tb %>% select(-c(withinFirst24H, daysFirstDocumentedBeforeAdmsn, ICD10, ICD10_description))

# for each encounter, keep only a single element per unique CCSR corresponding to the earliest that it (meaning any of the ICD10s that map to that given CCSR) was documented
df <- df %>% pivot_longer(cols = starts_with("CCSR"), names_to = "category", values_to = "CCSR", values_drop_na = TRUE)
df <- df %>% distinct(enc, admsnTimeJTR, CCSR, earliestNoted) %>%
        group_by(enc, admsnTimeJTR, CCSR) %>%
        summarise(earliestDocumented = min(earliestNoted)) %>%
        pivot_wider(id_cols = c(enc, admsnTimeJTR), names_from = CCSR, values_from = earliestDocumented, names_sort=TRUE)

# take each CCSR column (values = earliest it was noted for any given pt) and convert to a 3 factor column: 
# (1) POA (present on admission, ie. was documented prior to current encounter's admission time) (2) First24H (earliest documented was w/in 24h of encounter admit time), (3) FALSE (if N/A, meaning never previously documented in pt)
poa_freq <- vector("integer", ncol(df))
first24_freq <- vector("integer", ncol(df))
names(poa_freq) <- names(df)
names(first24_freq) <- names(df)
for (i in 3:ncol(df)) {
  df[[i]] <-ifelse(difftime(df[[i]], df[[2]], units = "days") >= 0, "First24H", "POA")
  df[[i]] <- ifelse(is.na(df[[i]]), "FALSE", df[[i]])
  poa_freq[[i]] <- sum(df[[i]] == "POA")
  first24_freq[[i]] <- sum(df[[i]] == "First24H")
}
ccsr_frequencies <- as_tibble(as.list(poa_freq)) %>% select(-enc,-admsnTimeJTR) %>% 
                      pivot_longer(everything(), names_to="CCSR", values_to="nEncPOA")
ccsr_frequencies <- as_tibble(as.list(first24_freq)) %>% select(-enc,-admsnTimeJTR) %>% 
                      pivot_longer(everything(), names_to="CCSR", values_to="nEncFirst24") %>%
                      inner_join(ccsr_frequencies) %>% 
                      inner_join(categories) %>%
                      arrange(desc(nEncFirst24 * nEncPOA))


##############################################################################
##### import data: objective features
sqlQuery2 <- readChar(filepath2, file.info(filepath2)$size)
sqlQuery2 <- paste0(sqlQuery0, sqlQuery2)
project <- "som-nero-phi-jonc101-secure" # "mining-clinical-decisions"
results <- bq_project_query(project, sqlQuery2)
tb2 <- as_tibble(bq_table_download(results, bigint = c("integer64"))) # bigint needed to properly download full PT_ENC_CSN_ID
rm(results)

print(paste0(tb2 %>% distinct(enc) %>% nrow(), " distinct patient encounters"))
##############################################################################

df2 <- tb2 %>% inner_join(df_topN)
features <- df2 %>% select(-c(enc,admsnTimeJTR,mrn,AdmitTRUE,DischTRUE,JITTER,anon_id,dischTimeJTR,drg))
features <- features %>% select(-drg_c, -LOS)
colNames <- as_tibble(names(features))

## ensure no blanks
# features %>% summarise(across(everything(), sum(is.na))) %>% t()
blanks <- vector("integer", ncol(features))
distincts <- vector("integer", ncol(features))
names(blanks) <- names(features)
names(distincts) <- names(features)
for (i in seq_along(features)) {
  blanks[[i]] = sum(is.na(features[[i]]))
  nDistinct <- length(unique(features[[i]]))
  distincts[[i]] <- nDistinct
  if (nDistinct < 10) { 
    features[[i]] <- as.factor(features[[i]])
  }
}
nBlank <- as_tibble(as.list(blanks)) %>% pivot_longer(everything(), names_to="col", values_to="numBlanks") %>% arrange(desc(numBlanks))
nDistinct <- as_tibble(as.list(distincts)) %>% pivot_longer(everything(), names_to="col", values_to="numDistinct") %>% arrange(desc(numDistinct))


# topN <- unlist(c(ccsr_frequencies[1:n,1]))
# df_topN <- df[,c("enc","admsnTimeJTR",topN)] # df <- df[, (colnames(df) %in% topN)]
# df_topN <- df

##############################################################################

## delete following
# patientFactors[,8:10] <- lapply(patientFactors[,8:10],as.numeric)
# cols <- unlist(lapply(features, as.numeric))  
# cols <- as.numeric(features$cr)
# temp <- features %>% mutate(across(c(1:ncol(features)), as.numeric)) # across(starts_with("first"), as.numeric)

features <- features1

test<-"/Users/kushgupta/Downloads/cost_var_new_features.csv"
test<-read_csv(test)
features<-test[,-1]


num <- 1000
rSquared <- vector("double", num)
numNonZeroCoef <- vector("integer", num)
nonZeroCoef <- vector("list", num)
for (i in 1:num) {
    set.seed(NULL)
    print(paste0("Iteration: ", i))
    
    train.indices <- features$Cost_Direct %>% createDataPartition(p = 0.8, list = FALSE)
    train.data  <- features[train.indices, ]
    test.data <- features[-train.indices, ]
    
    testing <- train.data %>% select(matches("[A-Z]{3}\\d{3}", ignore.case=FALSE))
    nPOA = vector("integer", ncol(testing))
    nFirst24 = vector("integer", ncol(testing))
    nMissing = vector("integer", ncol(testing))
    names(nPOA) <- names(testing)
    names(nFirst24) <- names(testing)
    names(nMissing) <- names(testing)
    for (j in seq_along(testing)) {
      nPOA[[j]] = sum("POA"==(testing[[j]]))
      nFirst24[[j]] = sum("First24H"==testing[[j]])
      nMissing[[j]] = sum("FALSE"==testing[[j]])
    }
    nPOA <- as_tibble(as.list(nPOA)) %>% pivot_longer(everything(), names_to="col", values_to="nPOA") %>% arrange(desc(nPOA))
    nFirst24 <- as_tibble(as.list(nFirst24)) %>% pivot_longer(everything(), names_to="col", values_to="nFirst24") %>% arrange(desc(nFirst24))
    nMissing <- as_tibble(as.list(nMissing)) %>% pivot_longer(everything(), names_to="col", values_to="nMissing") %>% arrange(desc(nMissing))
    frequencies <- nPOA %>% left_join(nMissing, by=c("col")) %>% left_join(nFirst24, by=c("col"))
    n <- 50
    # remove <- frequencies %>% mutate(mult = nPOA * nFirst24 * nMissing) %>% arrange(desc(mult)) %>% filter(row_number() > n) %>% distinct(col)
    remove <- frequencies %>% arrange(nMissing) %>% filter(row_number() > n) %>% distinct(col)
    
    t <- unlist(c(remove))
    features_cleaned <- features %>% select(-all_of(t)) # preferred over select(-t) or select(-c(t))
    
    train.data  <- features_cleaned[train.indices, ]
    test.data <- features_cleaned[-train.indices, ]
    
    ## this doesn't work -> x.test ends up with different ncol as x
    # x <- model.matrix(Cost_Direct~., train.data)[,-1]
    # y <- train.data$Cost_Direct
    # x.test <- model.matrix(Cost_Direct~., test.data)[,-1] # predict test
    
    ## trying to make training and test model.matrix same # features
    modelMatrix <- model.matrix(Cost_Direct~., features_cleaned)[,-1]
    x <- modelMatrix[train.indices,]
    y <- features_cleaned[train.indices,]$Cost_Direct
    x.test <- modelMatrix[-train.indices,]
    
    # # glmnet(x, y, alpha = 1, lambda = NULL)
    # 
    # #RIDGE
    # cv <- cv.glmnet(x, y, alpha = 0) # find best lambda using C-V
    # cv$lambda.min # display best lambda
    # model <- glmnet(x, y, alpha = 0, lambda = cv$lambda.min) # fit model
    # #coef(model) # display coeff
    # #x.test <- model.matrix(Cost_Direct~., test.data)[,-1] # predict test
    # predictions <- model %>% predict(x.test) %>% as.vector() # predict test
    # data.frame(
    #   RMSE = RMSE(predictions, test.data$Cost_Direct),
    #   Rsquare = R2(predictions, test.data$Cost_Direct)
    # )
    
    #LASSO
    cv <- cv.glmnet(x, y, alpha = 1) # find best lambda using C-V
    cv$lambda.min # display best lambda
    model <- glmnet(x, y, alpha = 1, lambda = cv$lambda.min) # fit model
    #coef(model) # display coeff
    modelCoefficients <- coef(model)[1:length(coef(model)),]
    temp <- tibble(colname = names(modelCoefficients), val = as.numeric(modelCoefficients)) %>% filter(val != 0) %>% arrange(desc(val))
    temp$extract <- str_extract(temp$colname, pattern='[A-Z]{3}\\d{3}')
    temp <- temp %>% left_join(categories, by=c("extract"="CCSR"))
    #x.test <- model.matrix(Cost_Direct~., test.data)[,-1] # predict test
    predictions <- model %>% predict(x.test) %>% as.vector() # predict test
    # data.frame(
    #   RMSE = RMSE(predictions, test.data$Cost_Direct),
    #   Rsquare = R2(predictions, test.data$Cost_Direct)
    # )
    rSq <- R2(predictions, test.data$Cost_Direct)
    print(paste0("R Squared: ", rSq))
    rSquared[[i]] <- rSq
    numNonZeroCoef[[i]] <- nrow(temp)
    nonZeroCoef[[i]] <- temp
    
    # rSquared
    # numNonZeroCoef
    # nonZeroCoef

}
AAmissing <- tibble(round(rSquared,2), numNonZeroCoef)

coeff <- nonZeroCoef[[1]]
for (i in 2:num) {
  coeff <- rbind(coeff, nonZeroCoef[[i]])
}

coeff$val <- as.integer(round(coeff$val,0))
coeff <- coeff %>%
  arrange(colname, val) %>% 
  group_by(colname) %>% 
  mutate(value = paste0("val",row_number()),
         numOccurrences = n(),
         avgVal = as.integer(round(mean(val),0)))
coeff <- pivot_wider(coeff, id_cols=c(colname, extract, category, numOccurrences, avgVal), names_from=value, values_from=val) %>% arrange(desc(numOccurrences))

summary(AAmissing$`round(rSquared, 2)`)
summary(AAmissing$numNonZeroCoef)

# R Squared: 95% CI: [0.00, 0.27], mean: 0.1021
# # non-zero coefficients: 95% CI: [4, 34], mean: 15.21


View(coeff)
View(AAmissing)


##############################################################################

# /*buckets AS

  #CCSR AHRQ mappings
  #CCSR IN ('CIR007','CIR008') -- hypertension ± associated secondary complications
  #CCSR IN ('CIR011') -- Coronary atherosclerosis and other heart disease
  #CCSR IN ('CIR017') -- cardiac dysrhythmias
  #CCSR IN ('CIR019') -- heart failure
  #CCSR IN ('CIR020','CIR021','CIR022','CIR023','CIR024','CIR025') -- cerebrovascular disease, infarction / ischemia, sequelae
  #CCSR IN ('CIR026') -- peripheral / visceral vascular disease
  #CCSR IN ('DIG012') -- Intestinal obstruction and ileus
  #CCSR IN ('END002',  'END003',  'END004',  'END005',  'END006',  'END007',  'END008',  'END009') -- Diabetes, Obesity
  #CCSR IN ('FAC002','FAC007') -- mental health related encounter
  #CCSR IN ('FAC019') -- Socioeconomic/psychosocial factors
  #CCSR IN ('GEN001') -- Nephritis; nephrosis; renal sclerosis
  #CCSR IN ('GEN003') -- chronic kidney disease
  #CCSR IN ('INF006') -- HIV infection
  #CCSR IN ('INF007') -- Hepatitis
  #CCSR IN ('INF012') -- Coronavirus disease – 2019 (COVID-19)
  #CCSR IN ('MUS006') -- Osteoarthritis
  #CCSR IN ('MUS013') -- Osteoporosis
  #CCSR IN ('MBD001','MBD003') -- Schizo, Bipolar
  #CCSR IN ('MBD002') -- Depressive disorders
  #CCSR IN ('MBD010') -- Feeding and eating disorders
  #CCSR IN ('MBD012', 'MBD027') -- Suicidal ideation/attempt/intentional self-harm
  #CCSR IN ('MBD017','MBD018','MBD019','MBD020','MBD021','MBD022','MBD023','MBD024','MBD025','MBD026','MBD028','MBD029','MBD030','MBD031','MBD032','MBD033') -- substance abuse: EtOH, opioids, cannabis, sedatives, etc. 
  #CCSR LIKE "%NVS%" -- all neuro conditions
  #CCSR IN ('NEO001','NEO002','NEO003','NEO004','NEO005','NEO006','NEO007','NEO008','NEO009','NEO010') -- cancer - ENT
  #CCSR IN ('NEO011') -- cancer - heart
  #CCSR IN ('NEO012','NEO013','NEO014','NEO015','NEO016','NEO017','NEO018','NEO019','NEO020','NEO021') -- cancer - GI
  #CCSR IN ('NEO022') -- cancer - pulm
  #CCSR IN ('NEO023','NEO024') -- cancer - bone
  #CCSR IN ('NEO025','NEO026','NEO027','NEO028') -- cancer - skin
  #CCSR IN ('NEO029','NEO030') -- cancer - breast
  #CCSR IN ('NEO031','NEO032','NEO033','NEO034','NEO035','NEO036','NEO037','NEO038') -- cancer - female repro
  #CCSR IN ('NEO039','NEO040','NEO041','NEO042') -- cancer - male repro
  #CCSR IN ('NEO043','NEO044','NEO045','NEO046','NEO047') -- cancer - urinary
  #CCSR IN ('NEO048','NEO049') -- cancer - nervous
  #CCSR IN ('NEO050','NEO051','NEO052','NEO053','NEO054','NEO055','NEO056') -- cancer - endocrine
  #CCSR IN ('NEO057','NEO058') -- cancer - lymphoma
  #CCSR IN ('NEO059','NEO060','NEO061','NEO062','NEO063','NEO064') -- cancer - leukemia
  #CCSR IN ('NEO065','NEO066','NEO067','NEO068','NEO069','NEO070','NEO071','NEO072') -- cancer - other
  
  
