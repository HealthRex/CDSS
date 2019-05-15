library(data.table)
library(RPostgreSQL)
library(DBI)
library(tidyverse)
#library(bigrquery)
library(dplyr)
# database driver connection
drv <- dbDriver("PostgreSQL")

# connection to database
con <- dbConnect(drv, dbname = "stride_inpatient_2014",
                 host = "localhost", port = 5432,
                 user = "postgres", password = "MANUALLY CHANGE ")


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

sql =       "
            select
                a.sim_patient_order_id, a.sim_user_id, a.sim_state_id, a.relative_time_start, a.sim_state_id,
                b.description as clin_description,
                c.description as state_description
            from
                sim_patient_order as a,
                clinical_item as b,
                sim_state_transition as c
            where a.clinical_item_id = c.clinical_item_id
            and b.clinical_item_id = b.clinical_item_id



            "
clinical_item <- tbl(con, "clinical_item")
sim_patient_order <- tbl(con, "sim_patient_order")
sim_state_transition <- tbl(con, "sim_state_transition")

df.spo <- sim_patient_order
df.sst <- sim_state_transition

spo <- as.data.frame(df.spo)
dim(spo)
merged_order <- merge(spo,df.sst, by.x="clinical_item_id", by.y = "clinical_item_id")
clinical_items_list <- unique(merged_order$clinical_item_id)

ordered_clinical_item_table <- clinical_item %>% filter(clinical_item_id %in% clinical_items_list)

ordered_clinical_item_table


remerged_order <- merge(merged_order, ordered_clinical_item_table, by.x="clinical_item_id", by.y="clinical_item_id")

View(remerged_order)

clean.df <- 

sim_groups <- split(remerged_order, remerged_order$sim_state_id)

sim_groups$`2`
