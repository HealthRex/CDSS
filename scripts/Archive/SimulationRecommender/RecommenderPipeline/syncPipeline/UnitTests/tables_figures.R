library(data.table)
library(RPostgreSQL)
library(DBI)
library(tidyverse)
library(dplyr)
library(xlsx)

# FUNCTIONS: AGGREGATE 

# database driver connection
drv <- dbDriver("PostgreSQL")

# connection to database
con <- dbConnect(drv, dbname = "stride_inpatient_2014",
                 host = "localhost", port = 5432,
                 user = "postgres", password = "postgres")

# lists all table names 
# assumes connection is called con 
table.names <- dbListTables(con)

# function to apply the function of all tables 
list_table_head <- function(table_name){
  sql <- paste("select * from ", table_name, "limit 10")
  return(dbGetQuery(con, sql))
}


# creates the first 10 rows of data for each datatable in DB 
base_table <- lapply(table.names, list_table_head)
names(base_table) <- table.names
library(dplyr)
base_table_colnames <- lapply(base_table, colnames)
names(base_table_colnames) <- table.names


# -------------------------------------------------------------------------------
# to do : 
#         Feature: Generate Grading Scheme 
#             1) help visualize processes 
#             2) introduce best grading schemes for each case 
#             3) create a list of common errors seen 
#            
#             4) clean up exploratory analysis 
#             5) convert to python module 
#
#
# 
# ---------------------------------------------------------------------------------

# makes connections to tables 

adf <- function(df){
  return(as.data.frame(df))
}

clinical_item <- tbl(con, "clinical_item")
sim_patient_order <- tbl(con, "sim_patient_order")
sim_state_transition <- tbl(con, "sim_state_transition")
sim_state <- adf(tbl(con,"sim_state"))
sim_user <- tbl(con,"sim_user")
sim_patient_state <- adf(tbl(con,"sim_patient_state"))
sim_result <- adf(tbl(con,"sim_result"))

sim_tracker_result_join <- list(sim_result, 
                                sim_state,
                                sim_patient_state)

sim_tracker_result <- merge(sim_state, sim_patient_state, by = 'sim_state_id')

# TRACKER DF 
tdx <- read.csv('/Users/jonc101/Box Sync/jichiang_folders/clinical_recommender_pipeline/tracker_data/tracker_output/2019_7_31_18_47_tracker_data_join.csv')
path <- setwd()
setwd('/Users/jonc101/Box Sync/jichiang_folders/clinical_recommender_pipeline/tracker_data/tracker_output/')

tracker_df <- merge(sim_tracker_result, tdx, by.x = 'sim_patient_id', by.y = 'patient' )

afib_states <- c("Afib-RVR Initial", 
                 "Afib-RVR Stabilized" ,
                 "Afib-RVR Worse" )

#--------------------------------------------------------------------------------
# meningitis 
#--------------------------------------------------------------------------------
# "Mening Active"                           
# "Meningitis Adequately Treated"           
# "Meningits Worsens"
#--------------------------------------------------------------------------------

mening_states <- c( "Mening Active",                            
                    "Meningitis Adequately Treated",          
                    "Meningits Worsens")

# -------------------------------------------------------------------------------
# pulmonary embolism 
# -------------------------------------------------------------------------------
# "PE-COPD-LungCA"                          
# "PE-COPD-LungCA + Anticoagulation"        
# "PE-COPD-LungCA + O2"                     
# "PE-COPD-LungCA + O2 + Anticoagulation" 
# -------------------------------------------------------------------------------

pulmonary_emolism_states <- c( "PE-COPD-LungCA",                         
                               "PE-COPD-LungCA + Anticoagulation",      
                               "PE-COPD-LungCA + O2",                 
                               "PE-COPD-LungCA + O2 + Anticoagulation")

# -------------------------------------------------------------------------------
# neutropenic fever 
# -------------------------------------------------------------------------------
#  "Neutropenic Fever Treated with IVF"      
#  "Neutropenic Fever Treated with IVF + ABX"
#  "Neutropenic Fever v2"                    
#  "NFever"  
# -------------------------------------------------------------------------------

neutropenic_fever_states <- c("Neutropenic Fever Treated with IVF",
                              "Neutropenic Fever Treated with IVF + ABX",
                              "Neutropenic Fever v2")

# -------------------------------------------------------------------------------
# GIBLEED 
# -------------------------------------------------------------------------------
# "EtOH-GIBleed Active"                     
# "EtOH-GIBleed Bleeding Out"               
# "EtOH-GIBleed Coag Stabilized"            
# "EtOH-GIBleed Post-EGD"   
# -------------------------------------------------------------------------------
gi_bleed_states <- c( "EtOH-GIBleed Active",                     
                      "EtOH-GIBleed Bleeding Out",               
                      "EtOH-GIBleed Coag Stabilized",            
                      "EtOH-GIBleed Post-EGD" )

# -------------------------------------------------------------------------------
# DKA 
# -------------------------------------------------------------------------------
# "DKA Euglycemic"                          
# "DKA Hyperglycemic"                       
# "DKA Onset"
# -------------------------------------------------------------------------------
dka_states <- c("DKA Euglycemic" ,                          
                "DKA Hyperglycemic" ,                       
                "DKA Onset")

# write a function to modularize the above 
# expects remerged order
state_split <- function(state_names, df){
  return(df %>% filter(name %in% state_names))
} 

list_of_states <- list(gi_bleed_states, 
                       mening_states, 
                       pulmonary_emolism_states, 
                       afib_states,
                       neutropenic_fever_states)

state_dataframe_split <- lapply(list_of_states, state_split, df = tracker_df)
remerged_order <- tracker_df
gi_test                  <- state_split(gi_bleed_states, remerged_order)
mening_test              <- state_split(mening_states, remerged_order)
pulmonary_embolism_test  <- state_split(pulmonary_emolism_states, remerged_order)
afib_test                <- state_split(afib_states, remerged_order)
neutropenic_test         <- state_split(neutropenic_fever_states, remerged_order)

gi_test$case                 <- "gi_bleed"
mening_test$case             <- "meningitis"
pulmonary_embolism_test$case <- "pulmonary_embolism"
afib_test$case               <- "atrial_fibrillation"
neutropenic_test$case        <- "neutropenic"

df_grading_pre <- rbind(gi_test, 
                        mening_test,
                        pulmonary_embolism_test, 
                        afib_test, 
                        neutropenic_test)
df_grading  <- df_grading_pre %>% select(sim_state_id, 
                                         clinical_item_id, 
                                         sim_user_id, 
                                         sim_patient_id, 
                                         description.x, 
                                         name.x, 
                                         description.x, 
                                         description.y, 
                                         case)


#View(df_grading_pre)

#grading_data3$description <- grading_data3$`unique(df$description.y)`
#test <-  merge(grading_data3, clinical_item, by = 'description')
setwd("/Users/jonc101/Box Sync/jichiang_folders/clinical_recommender_pipeline/tracker_data/tracker_output/")

df_tracker <- read.csv('tracker_output_v10.csv')

tg <- df_tracker %>% filter(!name_y %in% c('LisaShieh', 'Default User'))

write.csv(tg, 'tracker_output_v11.csv')

tg$ratioOrderFromRecommender <- (tg$orders_from_recommender/tg$unqique_recommended_options)
tg$ratioOrderFromManualSearchVsManualSearchOptions <- (tg$orders_from_manual_search/tg$manual_search_options)

tg_case_split <- split(tg, tg$sim_patient_id)

take_first_row <- function(x){
  return(x[1,])
}

first_case <- bind_rows(lapply(tg_case_split, take_first_row))
#View(first_case)
case_split <- split(first_case, first_case$case)


#unique(case_split$atrial_fibrillation$name_y)
#afib <- case_split$atrial_fibrillation %>% filter(!name_y %in% 'LisaShieh')
#gi_bleed <- case_split$gi_bleed %>% filter(!name_y %in% 'LisaShieh')
#meningitis <- case_split$meningitis %>% filter(!name_y %in% 'LisaShieh')
#neutropenic <- case_split$neutropenic %>% filter(!name_y %in% 'LisaShieh')
#pulmonary_embolism <- case_split$pulmonary_embolism %>% filter(!name_y %in% 'LisaShieh')
#afib$elapsed_time_secs <- as.numeric(as.character(stringr::str_split_fixed(afib$elapsed_time, ':',3)[,2])) * 60 +  as.numeric(as.character(stringr::str_split_fixed(afib$elapsed_time, ':',3)[,3]))

clean_elapsed_time <- function(df){
  afib <- df
  afib$elapsed_time_secs <- as.numeric(as.character(stringr::str_split_fixed(afib$elapsed_time, ':',3)[,2])) * 60 +  as.numeric(as.character(stringr::str_split_fixed(afib$elapsed_time, ':',3)[,3]))
  return(afib)
}

case_split_elapsed_time <- lapply(case_split, clean_elapsed_time)
case_split_elapsed_time$atrial_fibrillation

#summary(case_split_elapsed_time[[1]]$elapsed_time_secs)


elapsed_summary_recommender_on <- function(x){
  x2 <- x %>% filter(recommended_options > 0 )
  return((x2$elapsed_time_secs))
}

elapsed_summary_recommender_off <- function(x){
  x2 <- x %>% filter(recommended_options == 0 )
  return(summary(x2$elapsed_time_secs))
}


total_orders_recommender_on <- function(x){
  x2 <- x %>% filter(recommended_options > 0 )
  iqr(x2$total_orders)
}  


total_orders_recommender_off <- function(x){
  x2 <- x %>% filter(recommended_options == 0 )
  return(summary(x2$total_orders))
} 


# TODO 
total_orders_recommender_on_off_iqr <- function(x){
  #  t(summary(mtcars$mpg))[[1]] 
  x2 <- x %>% filter(recommended_options == 0 )
  iqr_25 <- t(summary(x2$e))[[2]]
  iqr_median <- t(summary(x2$e))[[3]]
  iqr_75 <- t(summary(x2$e))[[4]]
  cbind(iqr)
} 

lapply(case_split_elapsed_time, total_orders_recommender_off_iqr)

mean_elapsed_time_recommender_on_off <- function(x){
  x.on <- x %>% filter(recommended_options > 0 )
  x.off <- x %>% filter(recommended_options == 0 )
  t <- cbind(mean(x.on$elapsed_time_secs), mean(x.off$elapsed_time_secs))
  colnames(t) <- c('on', 'off')
  return(t)
}

mean_total_orders_recommender_on_off <- function(x){
  x.on <- x %>% filter(recommended_options > 0 )
  x.off <- x %>% filter(recommended_options == 0 )
  t <- cbind(mean(x.on$total_orders), mean(x.off$total_orders))
  colnames(t) <- c('on', 'off')
  return(t)
}  

summary_total_orders_recommender_on_off <- function(x){
  x.on <- x %>% filter(recommended_options > 0 )
  x.off <- x %>% filter(recommended_options == 0 )
  t = summary(x.on$total_orders)
  return(t)
}

lapply()

mean_total_num_clicks_recommender_on_off <- function(x){
  x.on <- x %>% filter(recommended_options > 0 )
  x.off <- x %>% filter(recommended_options == 0 )
  t <- cbind(mean(x.on$total_num_clicks), mean(x.off$total_num_clicks))
  colnames(t) <- c('on', 'off')
  return(t)
}  



mean_total_manual_search_recommender_on_off <- function(x){
  x.on <- x %>% filter(recommended_options > 0 )
  x.off <- x %>% filter(recommended_options == 0 )
  t <- cbind(mean(x.on$orders_from_manual_search), mean(x.off$orders_from_manual_search))
  colnames(t) <- c('on', 'off')
  return(t)
}  

ttest_total_manual_search_recommender_on_off <- function(x){
  x.on <- x %>% filter(recommended_options > 0 )
  x.off <- x %>% filter(recommended_options == 0 )
  t <- t.test(x.on$orders_from_manual_search, x.off$orders_from_manual_search)
  return(t)
}  

mean_total_recommender_missed_recommender_on_off <- function(x){
  x.on <- x %>% filter(recommended_options > 0 )
  x.off <- x %>% filter(recommended_options == 0 )
  t <- cbind(mean(x.on$orders_from_recommender_missed), mean(x.off$orders_from_recommender_missed))
  colnames(t) <- c('on', 'off')
  return(t)
}  

ttest_total_recommender_missed_recommender_on_off <- function(x){
  x.on <- x %>% filter(recommended_options > 0 )
  x.off <- x %>% filter(recommended_options == 0 )
  t <- t.test(x.on$orders_from_recommender_missed, x.off$orders_from_recommender_missed)
  #colnames(t) <- c('on', 'off')
  return(t)
}  




ttest_total_recommender_missed_list  <- lapply(case_split_elapsed_time, ttest_total_recommender_missed_recommender_on_off )
ttest_total_manual_search_list  <- lapply(case_split_elapsed_time, ttest_total_manual_search_recommender_on_off) 


mean_elapsed_time_list  <- lapply(case_split_elapsed_time, mean_elapsed_time_recommender_on_off )
mean_total_orders_list <- lapply(case_split_elapsed_time, mean_total_orders_recommender_on_off )
mean_total_recommender_missed_list  <- lapply(case_split_elapsed_time, mean_total_recommender_missed_recommender_on_off )
mean_total_manual_search_recommender_list <- lapply(case_split_elapsed_time, mean_total_manual_search_recommender_on_off)
mean_total_num_clicks_list <- lapply(case_split_elapsed_time, mean_total_num_clicks_recommender_on_off)


View(case_split_elapsed_time)

cases_elapsed <- names(mean_elapsed_time_list)
cases_total_orders <- names(mean_elapsed_time_list)
cases_total_recommender_missed <- names(mean_total_manual_search_recommender_list)
cases_total_manual_search_recommener_list <- names(mean_total_manual_search_recommender_list)
cases_total_num_clicks_list <- names(mean_total_num_clicks_list)

elapsed_time <- as.data.frame(cbind(t(bind_rows(mean_elapsed_time_list))))
colnames(elapsed_time) <- c('on', 'off')
elapsed_time$metric <- 'elapsed_time'
elapsed_time$case <- rownames(elapsed_time)

total_orders <- as.data.frame(cbind(t(bind_rows(mean_total_orders_list))))
colnames(total_orders) <- c('on', 'off')
total_orders$metric <- 'total_number_of_orders'
total_orders$case <- rownames(total_orders)

total_recommender_missed <- as.data.frame(cbind(t(bind_rows(mean_total_recommender_missed_list))))
colnames(total_recommender_missed) <- c('on', 'off')
total_recommender_missed$metric <- 'total_number_recommender_missed'
total_recommender_missed$case <- rownames(total_recommender_missed)

total_manual_search <- as.data.frame(cbind(t(bind_rows(mean_total_manual_search_recommender_list))))
colnames(total_manual_search) <- c('on', 'off')
total_manual_search$metric <- 'orders_from_manual_search'
total_manual_search$case <- rownames(total_manual_search)

total_num_clicks<- as.data.frame(cbind(t(bind_rows(mean_total_num_clicks_list))))
colnames(total_num_clicks) <- c('on', 'off')
total_num_clicks$metric <- 'total_number_clicks'
total_num_clicks$case <- rownames(total_num_clicks)




setwd("/Users/jonc101/Box Sync/jichiang_folders/clinical_recommender_pipeline/")

table3v2<- rbind(elapsed_time, 
          total_orders, 
          total_recommender_missed, 
          total_manual_search, 
          total_num_clicks)
table3v3 <- table3v2
table3v3$on  <- round(table3v2$on,2)
table3v3$off <- round(table3v2$off,2)

#View(table3v3)

#write.csv(table3v3, 'table3v3.csv')

#lapply(case_split_elapsed_time, elapsed_summary_recommender_off)
#lapply(case_split_elapsed_time, elapsed_summary_recommender_on)
#lapply(case_split_elapsed_time, total_orders_recommender_on)
#lapply(case_split_elapsed_time, total_orders_recommender_off)

library(testthat)
#assertthat::are_equal()

setwd("/Users/jonc101/Box Sync/jichiang_folders/clinical_recommender_pipeline/")

load('case_split_elapsed_time.rda')

View(case_split_elapsed_time)
case_split_elapsed_time$atrial_fibrillation



spo <- adf(sim_patient_order)
table_of_orders <- table(spo$sim_patient_order_id)
View(table_of_orders)
