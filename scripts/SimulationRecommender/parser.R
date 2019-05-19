library(data.table)
library(RPostgreSQL)
library(DBI)
library(tidyverse)
library(dplyr)
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

#
split_user_state <- split(split_state$`5000`, split_state$`5000`$sim_user_id) 

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

# -------------------------------------------------------------------------------
# GIBLEED 
# -------------------------------------------------------------------------------
# "EtOH-GIBleed Active"                     
# "EtOH-GIBleed Bleeding Out"               
# "EtOH-GIBleed Coag Stabilized"            
# "EtOH-GIBleed Post-EGD"   
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# DKA 
# -------------------------------------------------------------------------------
# "DKA Euglycemic"                          
# "DKA Hyperglycemic"                       
# "DKA Onset"
# -------------------------------------------------------------------------------

# -------------------------------------------------------------------------------
# Meningitis 
# -------------------------------------------------------------------------------
# "Mening Active"                           
# "Meningitis Adequately Treated"           
# "Meningits Worsens"  
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# Neutropenic Fever 
# -------------------------------------------------------------------------------
# "Neutropenic Fever Treated with IVF"      
# "Neutropenic Fever Treated with IVF + ABX"
# "Neutropenic Fever v2"                    
# "NFever"  
# -------------------------------------------------------------------------------



afib_df <- remerged_order %>% filter(name.x %in% afib_state)
afib_split <- split(afib_df, afib_df$sim_state_id)

# function to find unique orders for each sim state 

afib.40 <- afib_split$`40` %>% select(sim_state_id, clinical_item_id, sim_user_id, sim_patient_id, description.x, name.x, description.x, description.y)
afib.41 <- afib_split$`41` %>% select(sim_state_id, clinical_item_id, sim_user_id, sim_patient_id, description.x, name.x, description.x, description.y)
afib.43 <- afib_split$`43` %>% select(sim_state_id, clinical_item_id, sim_user_id, sim_patient_id, description.x, name.x, description.x, description.y)

unique_orders_afib_40 <- unique(afib.40$description.y)
unique_orders_afib_41 <- unique(afib.41$description.y)
unique_orders_afib_43 <- unique(afib.43$description.y)

total_order_list <- unique(c(unique_orders_afib_40,
                          unique_orders_afib_41,
                          unique_orders_afib_43))





library(xlsx)
write.xlsx(total_order_list, "afib_grading_doctors.xlsx", sheetName = "afib_case_orders", 
           col.names = TRUE, row.names = TRUE, append = FALSE)

write.xlsx(unique_orders_afib_40, "afib_grading_doctors.xlsx", sheetName = "afib_initial", 
           col.names = TRUE, row.names = TRUE, append = TRUE)

write.xlsx(unique_orders_afib_41, "afib_grading_doctors.xlsx", sheetName = "afib_stabilized", 
           col.names = TRUE, row.names = TRUE, append = TRUE)

write.xlsx(unique_orders_afib_43, "afib_grading_doctors.xlsx", sheetName = "afib_worsened", 
           col.names = TRUE, row.names = TRUE, append = TRUE)
