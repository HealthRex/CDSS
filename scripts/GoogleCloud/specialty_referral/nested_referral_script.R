library(bigrquery)
library(DBI)
library(dplyr)
library(lubridate)
library(stringr)
library(data.table)

# Assigning GCP Project Name
project <- "mining-clinical-decisions" # put your project ID here

#https://console.cloud.google.com/bigquery?project=mining-clinical-decisions&page=savedqueries&sq=103208666750:607c18a7b9254ec4b1543533d242d46d

# Creating DBI connection to Google BigQuery 1
con <- dbConnect(
  bigrquery::bigquery(),
  project = "mining-clinical-decisions",
  dataset = 'datalake_47618' ,
  billing = project
)

# converting a date to numeric from bq string date

date_to_numeric_val <- function(date_column){
  day <- str_split_fixed(date_column, " ",2)[,1]
  time <- str_split_fixed(date_column, " ",2)[,2]
  year <- str_split_fixed(day, "-", 3)[,1]
  month <- str_split_fixed(day, "-", 3)[,2]
  day_time <- str_split_fixed(day, "-", 3)[,3]
  numeric_date <- paste0(year,month,day_time)
  return(numeric_date)  
}

df_convert_date_to_numeric <- function(df){
  df$date_num <- date_to_numeric_val(df$date)
  return(df)
}
# ------------------------------------------------------
# get number of rows through dim()
# accepts dataframe as object
get_row <- function(df){
  rows <- dim(df)[1]
  return(rows)
}

path <- "/Users/jonc101/Documents/Biomedical_Data_Science/gcp/gcp_read"
setwd(path)


#--------------------------------------------------------

# --------------------------------------------------------------------------------------------------
# Big Computation: 
# Goal Pull all Referral and Save 

# Sql Call that Pulls the All the Patients that had a description of referral
sql <- "select * from `datalake_47618.z_subaim_referral_table` where appt_time_jittered > '2014' "

# Project to To Use SQL Query with BQ 
tb <- bq_project_query(project, sql)

# Downloads the data to local environment 
tb.dt <- bq_table_download(tb)

# Splits the Data into different description 
# Each entry of list is a different referral 
referral_list <- split(tb.dt, tb.dt$description)

# Returns the number of rows in each referral
num_rows <- lapply(referral_list, get_row)

# Returns the number of rows in each referral list df 
row_t <- do.call(rbind.data.frame, num_rows)

# write a function to get unique users from each dataframe 

unique_patients <- function(df){
  u.df <- unique(df$jc_uid)
  return(u.df)
}


unique_patients <- lapply(referral_list, unique_patients)
# [1] "JCd4c94e" "JCdce3e5" "JCcbd887" "JCe3e60c" "JCd2638b"
# [6] "JCe659bd"

# SAVED AS CSV FILE: BQ COMPUTING "LOCAL CACHE" 

#   encounter <- tbl(con, "encounter")
#   subaim_encounter <- tbl(con, "z_subaim_")
#   encounter_df <- as_tibble(subaim_encounter)

#   path <- "/Users/jonc101/Documents/Biomedical_Data_Science/gcp/gcp_read"
#   write.csv(encounter_df, "encounter.csv")

encounter_df <- fread('encounter.csv')


# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# WRITE A FUNCTION TO FILTER BY ENCOUNTER 

# takes the dataframe of 
encounter_referral_unique <- function(unique.list, df){
  return(df %>% filter(jc_uid %in% unique.list))
}


# maybe use future.apply 

#t <- sys.time()
encounter_by_referral <- lapply(unique_patients, encounter_referral_unique, df = encounter_df)
#(c <- sys.time() - t)

# need to bind two dataframes together in a list 

## colnames(referral_list[[1]]) equals colnames(encounter_by_referral[[1]])
# clean referral_list 
# convert description to visit_type 
clean_referral_list <- function(df){
  df2 <- df %>% select(jc_uid, pat_enc_csn_id_coded, appt_time_jittered, department_id)
  df2$visit_type <- df$description
  return(df2)
  
  
}

# helper function to remove extra columns 
clean_encounter_by_referral <- function(df){
  return( df %>% select(jc_uid, pat_enc_csn_id_coded, appt_time_jittered, department_id, visit_type) )
}

# helper function to return visits that were NEW PATIENTS 
new_patient_encounter_by_referral <- function(df){
  ptn <- '^NEW.*'
  ndx <- grep(ptn, df$visit_type, perl = T)
  return(df[ndx,])
}


# removes columns and shortens referral list to match encounter by referall
cat_referral_list <- lapply(referral_list, clean_referral_list)
cat_trim_encounter_by_referral <- lapply(encounter_by_referral, clean_encounter_by_referral)
cat_encounter_by_referral <- lapply(cat_trim_encounter_by_referral, new_patient_encounter_by_referral)

unique_encounter_map <- Map(rbind, cat_referral_list, cat_encounter_by_referral)


encounter_referral_patient_list <- lapply(unique_encounter_map, function(x) split(x, x$jc_uid))
# reassignign name to something easier to write

epl <- encounter_referral_patient_list

path <-  "/Users/jonc101/Documents/Biomedical_Data_Science/gcp/gcp_read"

# quiver path 
setwd("/Users/jonc101/Box Sync/Jonathan Chiang's Files/sub_aim_referral")

batch1 <- unique_encounter_map

mapply(
  write.csv,
  x=unique_encounter_map, file=paste(names(unique_encounter_map), "csv", sep="."),
  MoreArgs=list(row.names=FALSE, sep=",")
)

setwd(path)
# make a referral directory:    



