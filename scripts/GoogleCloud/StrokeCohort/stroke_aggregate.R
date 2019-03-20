library(bigrquery)
library(DBI)
library(dplyr)
library(lubridate)
library(stringr)
library(data.table)
library(ggplot2)

path <- "/Users/jonc101/Documents/Biomedical_Data_Science/gcp/gcp_read"
setwd(path)

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

# write a function to remove duplicates in lapply 
remove_duplicate <- function(dt){
  dtx <- dt[!duplicated(dt), ]
  return(dtx)
}




aggregate_event <- function(df){
  df$sub_date<- as.POSIXct(df$order_time_jittered,format="%Y-%m-%d %H:%M:%S")
  df$Day <- as.character( round(df$sub_date , "day" ) )
  testing <- aggregate( df , by = list(df$Day) , length )
  return(testing)
}

aggregate_name <- function(dfx){
  require(dplyr)
  dt <- dfx %>% select(Group.1, order_type) 
  return(dt)
}

list_aggregate_rename <- function(listx){
  # accepts list 
  t <- names(listx)
  
}

bargg <- function(df){
  p4 <- ggplot() + geom_bar(aes(y = order_type, x = as.Date(Group.1), fill = order_event), data = df,
                            stat="identity")
  p4
}

bargg.02 <- function(df){
  p4 <- ggplot() + geom_bar(aes(y = order_type, 
                                x = as.Date(Group.1), 
                                fill = order_event), 
                                data = df,
                                stat="identity") + 
                                xlab("Date") +
                                ylab("Count") +
                                ggtitle( paste0("Count of Stroke Orders Type: ")
                                        ) +
                                theme(plot.title = element_text(hjust = 0.5))
  p4
}

convert_aggregate<- function(df){
  df$sub_date<- as.POSIXct(df$order_time_jittered,format="%Y-%m-%d %H:%M:%S")
  df$Day <- as.character( round(df$sub_date , "day" ) )
  day_split <- split(df, df$order_type)
  df_aggregate_order <- lapply(day_split, aggregate_event)
  df_aggregate <- lapply(df_aggregate_order, aggregate_name)
  event <- bind_rows(df_aggregate, .id = "order_event")
  return(event)
}

#--------------------------------------------------------

# -------------------------------------------------------

# Big Computation: 
# Goal Pull all Referral and Save 

# Sql Call that Pulls the All the Patients that had a description of referral
sql <- "select * from `clinical_inpatient.stroke_ministudy`"

# Project to To Use SQL Query with BQ 
tb <- bq_project_query(project, sql)

# Downloads the data to local environment 
tb.dtx <- bq_table_download(tb)

tb.dtx2 <- tb.dtx[!duplicated(tb.dtx), ]
tb.dtx2$date <- tb.dtx2$contact_date_jittered
tb.dt <- df_convert_date_to_numeric(tb.dtx2)

# Splits the Data into different description 
# Each entry of list is a different referral 

dt.listx <- split(tb.dt, tb.dt$jc_uid)
dt.list <- lapply(dt.listx, remove_duplicate)

# Returns the number of rows in each referral
num_rows <- lapply(dt.list, get_row)

agg_list <- lapply(dt.list, convert_aggregate)
#cplot <- lapply(agg_list, bargg)
cplot.02 <- lapply(agg_list, bargg.02)


cplot.02$JCcb6780
cplot.02$JCcb69b7
cplot.02$JCcb92a7
cplot.02$JCcbf918
cplot.02$JCcc820c
