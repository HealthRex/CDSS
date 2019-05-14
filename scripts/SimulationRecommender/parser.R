library(data.table)
library(RPostgreSQL)
library(DBI)
library(tidyverse)

# database driver connection
drv <- dbDriver("PostgreSQL")

# connection to database
con <- dbConnect(drv, dbname = "stride_inpatient_2014",
                 host = "localhost", port = 5432,
                 user = "postgres", password = "MANUALLY CHANGE PASSWORD")


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
#
#
#
#
# 
# ---------------------------------------------------------------------------------
