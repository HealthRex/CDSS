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

clinical_item <- tbl(con, "clinical_item")
sim_patient_order <- tbl(con, "sim_patient_order")
sim_state_transition <- tbl(con, "sim_state_transition")
sim_state <- tbl(con,"sim_state")

merged_order <- merge(sim_patient_order, sim_state, by.x="sim_state_id", by.y = "sim_state_id")
clinical_items_list <- unique(merged_order$clinical_item_id)
sim_state_list <- unique(merged_order$sim_state_id)
ordered_clinical_item_table <- clinical_item %>% filter(clinical_item_id %in% clinical_items_list)
remerged_order <- merge(merged_order, ordered_clinical_item_table, by.x="clinical_item_id", by.y="clinical_item_id")

