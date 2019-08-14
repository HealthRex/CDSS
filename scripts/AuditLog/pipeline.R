# three lists of data

setwd("/Users/jonc101/Documents/Biomedical_Data_Science/gcp/gcp_read/stroke_module/")
source("source.R")
source("queries.R")
library(ggplot2)
library(dplyr)


stroke_cohort <- read.csv("stroke_cohort.csv")
sc_lab_result <- read.csv("sc_lab_result.csv")
sc_order_proc <- read.csv("sc_order_proc.csv")
sc_order_med  <- read.csv("sc_order_med.csv")

# three lists of data
sc_lab_result$encounter_id <- paste0(sc_lab_result$string_id, "_", sc_lab_result$jc_uid)
sc_order_proc$encounter_id <- paste0(sc_order_proc$string_id, "_", sc_order_proc$jc_uid)
sc_order_med$encounter_id  <- paste0(sc_order_med$string_id,  "_", sc_order_med$jc_uid)


stroke_cohort$encounter_id <- paste0(stroke_cohort$pat_enc_csn_id_coded,"_", stroke_cohort$jc_uid)

stroke_lab  <- merge(stroke_cohort, sc_lab_result, by = "encounter_id")
stroke_proc <- merge(stroke_cohort, sc_order_proc, by = "encounter_id")
stroke_med  <- merge(stroke_cohort, sc_order_med, by = "encounter_id")


stroke_lab$lab_time_difference_tpaOrderTime   <- as.numeric(convert_datetime(stroke_lab$tpaOrderTime) - convert_datetime(stroke_lab$order_time_jittered)) / 60
stroke_proc$proc_time_difference_tpaOrderTime <- as.numeric(convert_datetime(stroke_proc$tpaOrderTime) - convert_datetime(stroke_proc$order_inst_jittered)) / 60
stroke_med$med_time_difference_tpaOrderTime   <- as.numeric(convert_datetime(stroke_med$tpaOrderTime) - convert_datetime(stroke_med$order_time_jittered)) / 60

stroke_lab$ed_time_difference_tpaOrderTime <- as.numeric(convert_datetime(stroke_lab$tpaOrderTime) - convert_datetime(stroke_lab$emergencyAdmitTime)) /60
stroke_proc$ed_time_difference_tpaOrderTime <- as.numeric(convert_datetime(stroke_proc$tpaOrderTime) - convert_datetime(stroke_proc$emergencyAdmitTime)) /60
stroke_med$ed_time_difference_tpaOrderTime <- as.numeric(convert_datetime(stroke_med$tpaOrderTime) - convert_datetime(stroke_med$emergencyAdmitTime)) /60

stroke_lab$ed_time_difference  <- as.numeric(convert_datetime(stroke_lab$tpaOrderTime) - convert_datetime(stroke_lab$emergencyAdmitTime)) /60
stroke_proc$ed_time_difference <- as.numeric(convert_datetime(stroke_proc$tpaOrderTime) - convert_datetime(stroke_proc$emergencyAdmitTime)) /60
stroke_med$ed_time_difference  <- as.numeric(convert_datetime(stroke_med$tpaOrderTime) - convert_datetime(stroke_med$emergencyAdmitTime)) /60

#check to see 12:00 time point orders 
#sort(table(unique(stroke_lab$order_time_jittered)))

stroke_lab_pre  <- stroke_lab  %>% filter(lab_time_difference_tpaOrderTime > 0) 
stroke_proc_pre <- stroke_proc %>% filter(proc_time_difference_tpaOrderTime > 0) 
stroke_med_pre  <- stroke_med  %>% filter(med_time_difference_tpaOrderTime > 0) 

stroke_lab_pre2  <- stroke_lab_pre  %>% filter(ed_time_difference < 0) 
stroke_proc_pre2 <- stroke_proc_pre %>% filter(ed_time_difference < 0) 
stroke_med_pre2  <- stroke_med_pre  %>% filter(ed_time_difference < 0) 

# Mini Test:  test length
dim(stroke_lab)[1]  == dim(sc_lab_result)[1]
dim(stroke_proc)[1] == dim(sc_order_proc)[1]
dim(stroke_med)[1]  == dim(sc_order_med)[1]

# Create List Where Each Item is a Patient
stroke_labs_list <- split(stroke_lab_pre, stroke_lab_pre$encounter_id)
stroke_proc_list <- split(stroke_proc_pre, stroke_proc_pre$encounter_id)
stroke_med_list  <- split(stroke_med_pre, stroke_med_pre$encounter_id)

get_labs_before_tpa_order <- function(x){
  num_labs_before_tpa_order = get_row(x)
  x$num_labs_before_tpa_order <- num_labs_before_tpa_order
  return(x)
}

get_procs_before_tpa_order <- function(x){
  num_procs_before_tpa_order = get_row(x)
  x$num_procs_before_tpa_order <- num_procs_before_tpa_order
  return(x)
}

get_meds_before_tpa_order <- function(x){
  num_meds_before_tpa_order = get_row(x)
  x$num_meds_before_tpa_order <- num_meds_before_tpa_order
  return(x)
}

stroke_labs_list2 <- lapply(stroke_labs_list, get_labs_before_tpa_order)
stroke_proc_list2 <- lapply(stroke_proc_list, get_procs_before_tpa_order)
stroke_meds_list2 <- lapply(stroke_med_list, get_meds_before_tpa_order)

get_first_row <- function(df){
  return(df[1,])
}

stroke_lab_one  <- lapply(stroke_labs_list2, get_first_row)
stroke_proc_one <- lapply(stroke_proc_list2, get_first_row)
stroke_meds_one <- lapply(stroke_meds_list2, get_first_row)

stroke_lab_df  <- bind_rows(stroke_lab_one)
stroke_proc_df <- bind_rows(stroke_proc_one)
stroke_meds_df <- bind_rows(stroke_meds_one)

stroke_proc_features <- stroke_proc_df %>% 
  select(encounter_id, 
         num_procs_before_tpa_order)

outersect <- function(x, y) {
  sort(c(setdiff(x, y),
         setdiff(y, x)))
}

# must account for people who recieved 0 procedures and 0 meds 

encounter_id_proc0 <- as.data.frame(outersect(stroke_lab_df$encounter_id, stroke_proc_features$encounter_id))
colnames(encounter_id_proc0)[1] <- "encounter_id"
encounter_id_proc0$num_procs_before_tpa_order <- 0 

stroke_proc_complete <- rbind(stroke_proc_features, encounter_id_proc0)

stroke_meds_features <- stroke_meds_df %>% select(encounter_id, 
                                                  num_meds_before_tpa_order)

encounter_id_meds0 <- as.data.frame(outersect(stroke_lab_df$encounter_id, stroke_meds_features$encounter_id))
colnames(encounter_id_meds0)[1] <- "encounter_id"
encounter_id_meds0$num_meds_before_tpa_order <- 0 

stroke_meds_complete <- rbind(stroke_meds_features, encounter_id_meds0)

stroke_df_pre1 <- merge(stroke_lab_df, stroke_proc_complete, by="encounter_id")
stroke_df_ml <- merge(stroke_df_pre1, stroke_meds_complete, by="encounter_id")



#stroke_labs_features <- stroke_lab_df %>% select(encounter_id, 
#                                                  num_labs_before_tpa_order)
#encounter_id_labs0 <- as.data.frame(outersect(stroke_lab_df$encounter_id, stroke_labs_features$encounter_id))
#colnames(encounter_id_labs0)[1] <- "encounter_id"
#encounter_id_labs0$num_labs_before_tpa_order <- 0 
#stroke_labs_complete <- rbind(stroke_proc_features, encounter_id_labs0)

#stroke_df_ml <- merge(stroke_df_pre2, stroke_labs_complete, by="encounter_id")

# converting data long to wide 

test = stroke_labs_list2[[1]]

# x1 x2 x3 x4 (association) 

# THINGS HAPPEN BEFORE: TEST: OCCURED AT MIDNIGHT: (TIMING CAVEAT)
# Y VARIABLE (TIME BETWEEN) EXPLICIT FUNCTION TIME DIFFERENE BETWEEN
# counts: 

# BEFORE ED ADMIT (TIME BEFORE THEY REACHED)
# Outcomes: linear regression: 

# [1] lm(y1, x1,x2,x3,x4) counts with age gender demographics 
# [2] Plots: 
# regression trees: 

# data_wide <- spread(olddata_long, condition, measurement)

colnames(stroke_df_ml)

ggplotRegression <- function (fit) {
  
  require(ggplot2)
  
  ggplot(fit$model, aes_string(x = names(fit$model)[2], y = names(fit$model)[1])) + 
    geom_point() +
    stat_smooth(method = "lm", col = "red") +
    labs(title = paste("Adj R2 = ",signif(summary(fit)$adj.r.squared, 5),
                       "Intercept =",signif(fit$coef[[1]],5 ),
                       " Slope =",signif(fit$coef[[2]], 5),
                       " P =",signif(summary(fit)$coef[2,4], 5)))
}

fit1 <- lm(ed_time_difference_tpaOrderTime ~ num_labs_before_tpa_order, data = stroke_df_ml)
fit2 <- lm(ed_time_difference_tpaOrderTime ~ num_procs_before_tpa_order, data = stroke_df_ml)
fit3 <- lm(ed_time_difference_tpaOrderTime ~ num_meds_before_tpa_order, data = stroke_df_ml)

ggplotRegression(fit1)
ggplotRegression(fit2)
ggplotRegression(fit3)


stroke_df_ml <- stroke_df_ml %>% 
  filter(num_procs_before_tpa_order < 300) %>%
  filter(num_meds_before_tpa_order < 300) %>%
  filter(num_meds_before_tpa_order < 300)  

#summary(fit1)

#stroke_lab_df$age <- convert_datetime(stroke_lab_df$order_time_jittered) - convert_datetime(stroke_lab$birth_date_jittered) 
stroke_df_ml$age <- year(ymd_hms(stroke_df_ml$emergencyAdmitTime)) - year(ymd_hms(stroke_df_ml$birth_date_jittered))

# cyclical treatment of time 
stroke_df_ml$ed_hour_sin_admit <- sin(2*pi*hour(stroke_df_ml$emergencyAdmitTime)/24)
stroke_df_ml$ed_hour_cos_admit <- cos(2*pi*hour(stroke_df_ml$emergencyAdmitTime)/24)

stroke_df_ml$ed_month_sin_admit <- sin(2*pi*month(stroke_df_ml$emergencyAdmitTime)/12)
stroke_df_ml$ed_month_cos_admit <- cos(2*pi*month(stroke_df_ml$emergencyAdmitTime)/12)

ml.fit <- lm(ed_time_difference_tpaOrderTime ~ num_labs_before_tpa_order + 
                                               num_meds_before_tpa_order + 
                                               num_procs_before_tpa_order +
                                               gender + 
                                               canonical_race + 
                                              age + 
                                              ed_hour_sin_admit + 
                                              ed_hour_cos_admit + 
                                              ed_month_sin_admit + 
                                              ed_month_cos_admit, 
                                               data=stroke_df_ml)



plot(stroke_df_ml$ed_time_difference_tpaOrderTime, stroke_df_ml$num_labs_before_tpa_order)
plot(stroke_df_ml$ed_time_difference_tpaOrderTime, stroke_df_ml$num_meds_before_tpa_order)
plot(stroke_df_ml$ed_time_difference_tpaOrderTime, stroke_df_ml$num_procs_before_tpa_order)

#View(stroke_df_ml)
ggplot(stroke_df_ml, aes(x = num_meds_before_tpa_order, y = ed_time_difference_tpaOrderTime)) + 
  geom_point() +
  stat_smooth(method = "lm", col = "red")

ggplot(stroke_df_ml, aes(x = num_procs_before_tpa_order, y = ed_time_difference_tpaOrderTime)) + 
  geom_point() +
  stat_smooth(method = "lm", col = "red")

ggplot(stroke_df_ml, aes(x = num_labs_before_tpa_order, y = ed_time_difference_tpaOrderTime)) + 
  geom_point() +
  stat_smooth(method = "lm", col = "red")

stroke_df_ml_col <- stroke_df_ml %>% select(ed_time_difference_tpaOrderTime, 
                                            num_labs_before_tpa_order , 
                                              num_meds_before_tpa_order , 
                                              num_procs_before_tpa_order ,
                                              age , 
                                              ed_hour_sin_admit , 
                                              ed_hour_cos_admit ,
                                              ed_month_sin_admit , 
                                              ed_month_cos_admit)

library(rsample)      # data splitting 
library(randomForest) # basic implementation
library(ranger)       # a faster implementation of randomForest
library(caret)        # an aggregator package for performing many machine learning models
library(h2o)          # an extremely fast java-based platformset.seed(123)
ames_split <- initial_split(stroke_df_ml_col, prop = .7)
ames_train <- training(ames_split)
ames_test  <- testing(ames_split)

# for reproduciblity
set.seed(123)

# default RF model
m1 <- randomForest(
  formula = ed_time_difference_tpaOrderTime ~ .,
  data    = ames_train
)

plot(m1)

which.min(m1$mse)

sqrt(m1$mse[which.min(m1$mse)])


# create training and validation data 
set.seed(123)
valid_split <- initial_split(ames_train, .8)

# training data
ames_train_v2 <- analysis(valid_split)

# validation data
ames_valid <- assessment(valid_split)
x_test <- ames_valid[setdiff(names(ames_valid), "ed_time_difference_tpaOrderTime")]
y_test <- ames_valid$ed_time_difference_tpaOrderTime

rf_oob_comp <- randomForest(
  formula =  ed_time_difference_tpaOrderTime ~ .,
  data    = ames_train_v2,
  xtest   = x_test,
  ytest   = y_test
)

# extract OOB & validation errors
oob <- sqrt(rf_oob_comp$mse)
validation <- sqrt(rf_oob_comp$test$mse)

# compare error rates
tibble::tibble(
  `Out of Bag Error` = oob,
  `Test error` = validation,
  ntrees = 1:rf_oob_comp$ntree
) %>%
  gather(Metric, RMSE, -ntrees) %>%
  ggplot(aes(ntrees, RMSE, color = Metric)) +
  geom_line() +
  xlab("Number of trees")



lab_rows <- stroke_lab_pre %>% 
  group_by(group_lab_name) %>%
  summarise(no_rows = length(group_lab_name)) %>% 
  arrange(desc(no_rows))

proc_rows <- stroke_proc_pre %>% 
  group_by(description) %>%
  summarise(no_rows = length(description))%>% 
  arrange(desc(no_rows))

med_rows <- stroke_med_pre %>% 
  group_by(med_description)%>%
  summarise(no_rows = length(med_description))%>% 
  arrange(desc(no_rows))

labAll_rows <- stroke_lab %>% 
  group_by(group_lab_name) %>%
  summarise(no_rows = length(group_lab_name)) %>% 
  arrange(desc(no_rows))

procAll_rows <- stroke_proc %>% 
  group_by(description) %>%
  summarise(no_rows = length(description))%>% 
  arrange(desc(no_rows))

medAll_rows <- stroke_med %>% 
  group_by(med_description)%>%
  summarise(no_rows = length(med_description))%>% 
  arrange(desc(no_rows))

# function to decode a history of information: 


