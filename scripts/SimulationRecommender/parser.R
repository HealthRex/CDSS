library(data.table)
library(RPostgreSQL)
library(DBI)
library(tidyverse)
library(dplyr)
library(xlsx)
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

clinical_item <- tbl(con, "clinical_item")
sim_patient_order <- tbl(con, "sim_patient_order")
sim_state_transition <- tbl(con, "sim_state_transition")
sim_state <- tbl(con,"sim_state")

# merges two tables (similar to join in sql)
# purpose is to capture the description 
merged_order <- merge(sim_patient_order, 
                      sim_state, 
                      by.x="sim_state_id", 
                      by.y = "sim_state_id")


# finds unique clinical item list 
clinical_items_list <- unique(merged_order$clinical_item_id)

# finds unique sim_state_id's 
sim_state_list <- unique(merged_order$sim_state_id)

# creates clinical_item order key to reduce merge space: 
ordered_clinical_item_table <- clinical_item %>% filter(clinical_item_id %in% clinical_items_list)

# joins tables by clinical item id (creates a dataframe that includes clinical descriptions)
remerged_order <- merge(merged_order, ordered_clinical_item_table, 
                        by.x="clinical_item_id", 
                        by.y="clinical_item_id")

# 
split_state <- split(remerged_order, remerged_order$sim_state_id)


sort(unique(remerged_order$name.x))

#--------------------------------------------------------------------------------
# afib 
#--------------------------------------------------------------------------------
# "Afib-RVR Initial"                        
# "Afib-RVR Stabilized"                     
# "Afib-RVR Worse"
#--------------------------------------------------------------------------------

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
                              "Neutropenic Fever v2",                    
                              "NFever")

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
  return(df %>% filter(name.x %in% state_names))
} 

list_of_states <- list(gi_bleed_states, 
                       mening_states, 
                       pulmonary_emolism_states, 
                       afib_states,
                       neutropenic_fever_states)


state_dataframe_split <- lapply(list_of_states, state_split, df = remerged_order)

gi_test <- state_split(gi_bleed_states, remerged_order)
mening_test <- state_split(mening_states, remerged_order)
pulmonary_embolism_test <- state_split(pulmonary_emolism_states, remerged_order)
afib_test <- state_split(afib_states, remerged_order)
neutropenic_test <- state_split(neutropenic_fever_states, remerged_order)

gi_test$case <- "gi_bleed"
mening_test$case <- "meningitis"
pulmonary_embolism_test$case <- "pulmonary_embolism"
afib_test$case <- "atrial_fibrillation"
neutropenic_test$case <- "neutropenic"

df_grading_pre <- rbind(gi_test, 
         mening_test,
         pulmonary_embolism_test, 
         afib_test, 
         neutropenic_test)

df_grading <- df_grading_pre %>% select(sim_state_id, clinical_item_id, sim_user_id, sim_patient_id, description.x, name.x, description.x, description.y, case)

sim_state_list <- split(df_grading, df_grading$sim_state_id)

unique_orders <- function(df){
  df2 <- as.data.frame(unique(df$description.y))
  df2$case <- as.character(unique(df$case))
  df2$name.x <- as.character(unique(df$name.x))
  return(df2)
}  

unique_sim_state <- lapply(sim_state_list, unique_orders)

grading_data <- bind_rows(unique_sim_state)

grading_data$grade <- NA
grading_data$confidence <- NA
grading_data$group_name <- NA

write.xlsx(grading_data, "grading_doctors.xlsx", sheetName = "unique_orders_case", 
           col.names = TRUE, row.names = TRUE, append = FALSE)


