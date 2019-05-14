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

# libraries to read in
library(bigrquery)
library(data.table)
library(feather)
library(reticulate)
library(dplyr)
library(psych)
library(timevis)
library(shiny)

# python libraries 
pandas <- import("pandas")
pa <- import("pyarrow")
pq <- pa$parquet

# Google Project Name 
project <- "mining-clinical-decisions" # put your project ID here

# writes csv to Sync Folder
push_quiver <- function(df, name, env){
  write.csv(df, paste0(env ,name,".csv"))
}

# writes df to feather format to Sync Folder
push_quiver_feather <- function(df, name, env){
  write_feather(df, paste0(env ,name,".feather"))
}

# lists files from Sync Folder
list_quiver_csv <- function(env){
  files <- list.files(env, pattern='*\\.csv', recursive=TRUE)
  return(unlist(as.vector(strsplit(files, ".csv"))))
}

# Lists feather files from Sync Folder
list_quiver_feather <- function(env){
  files <- list.files(env, pattern='*\\.feather', recursive=TRUE)
  return(unlist(as.vector(strsplit(files, ".feather"))))
}

# reads CSV from Sync Folder
read_quiver <- function(file,env){
  return(read.csv(paste0(env,file,".csv")))
}

# reads CSV using fread 
fread_quiver <- function(file,env){
  return(fread(paste0(env,file,".csv")))
}

# reads feather from sync folder
fread_quiver_feather <- function(file,env){
  return(read_feather(paste0(env,file,".feather")))
}


# generic reticulate function to read Parquet file in R
read_parquet <- function(path, columns = NULL) {
  
  path <- path.expand(path)
  path <- normalizePath(path)
  
  if (!is.null(columns)) columns = as.list(columns)
  
  xdf <- pandas$read_parquet(path, columns = columns)
  
  xdf <- as.data.frame(xdf, stringsAsFactors = FALSE)
  
  dplyr::tbl_df(xdf)
  
}


# File Read System 
stroke_cohort       <- fread_quiver("stroke_cohort", sync_environment)
stroke_cohort_demo  <- fread_quiver("stroke_cohort_demo", sync_environment)

# splits patients into individual lists 
patient_list <- split(stroke_cohort,stroke_cohort$jc_uid)

# patient 1: need to convert to timevis format 
p1 <- patient_list$JCcb69cc

# DESIRED DATA FORMAT RESULT 
timevisData <- data.frame(
  id = 1:11,
  content = c("Open", "Open",
              "Open", "Open", "Half price entry",
              "Staff meeting", "Open", "Adults only", "Open", "Hot tub closes",
              "Siesta"),
  start = c("2016-05-01 07:30:00", "2016-05-01 14:00:00",
            "2016-05-01 06:00:00", "2016-05-01 14:00:00", "2016-05-01 08:00:00",
            "2016-05-01 08:00:00", "2016-05-01 08:30:00", "2016-05-01 14:00:00",
            "2016-05-01 16:00:00", "2016-05-01 19:30:00",
            "2016-05-01 12:00:00"),
  end   = c("2016-05-01 12:00:00", "2016-05-01 20:00:00",
            "2016-05-01 12:00:00", "2016-05-01 22:00:00", "2016-05-01 10:00:00",
            "2016-05-01 08:30:00", "2016-05-01 12:00:00", "2016-05-01 16:00:00",
            "2016-05-01 20:00:00", NA,
            "2016-05-01 14:00:00"),
  group = c(rep("lib", 2), rep("gym", 3), rep("pool", 5), NA),
  type = c(rep("range", 9), "point", "background")
)

timevisDataGroups <- data.frame(
  id = c("lib", "gym", "pool"),
  content = c("Lab", "Emergency Room", "CT Head")
)

# write a function to convert single patient to timeline vis data frame format 

# time start is inpatient admit time 

# group1 = time to CT head order 
# group2 = time to TPA order 
# group3 = time from order to admin 
# group4 = time from emergency admit time to inpatient admit time 

start    <- p1 %>% select(emergencyAdmitTime) #admit_time
end  <-  p1 %>% select(ctHeadOrderTime) #ct_order_time
content <- "CT Head Order Time"
group <- "EHR"
type <- "RANGE"
id <- 1
t <- cbind(start,end,content,group,type,id)
colnames(t) <- c("start","end","content","group","type","id")


# function to clean data 
# 
library(lubridate)
#with_tz(ymd_hms(stroke_cohort$emergencyAdmitTime),"America/Los_Angeles")

convert_datetime <- function(timeEHR){
  #convert to America_Pacific in lubridate
  # requires format like this
  # "2014-06-18 17:21:00" "2014-08-05 16:14:00" "2014-08-31 19:10:00" "2014-09-02 19:23:00" "2014-09-24 15:27:00" "2014-09-27 16:21:00" "2014-09-27 18:16:00"
  # "2014-09-28 18:46:00" "2014-10-18 15:55:00" "2014-10-29 19:21:00" "2014-10-29 22:53:00" "2014-10-30 18:52:00" "2014-11-10 13:30:00" "2014-11-23 18:21:00"
  # "2014-11-25 11:43:00" "2014-11-29 10:17:00"
  
  #into this format
  
  #[31] "2011-10-17 06:19:00 PDT" "2011-11-06 07:03:00 PST" "2011-11-07 12:36:00 PST" "2011-11-12 03:29:00 PST" "2011-11-16 23:37:00 PST"
  #[36] "2011-11-18 09:11:00 PST" "2011-11-29 05:21:00 PST" "2011-12-11 09:54:00 PST" "2011-12-19 01:49:00 PST" "2011-12-21 04:14:00 PST"
  #[41] "2012-01-04 10:31:00 PST" "2012-01-22 09:31:00 PST" 
  return(with_tz(ymd_hms(timeEHR),"America/Los_Angeles"))
}


find_time_difference <- function(time_start,time_end, jc_uid){
  time_to_ct <- as.numeric(convert_datetime(time_end) - convert_datetime(time_start)) /60
  #return(time_to_ct)
  ct.df <- as_tibble(cbind(jc_uid, time_to_ct))
  colnames(ct.df)[1] <- "id"
  colnames(ct.df)[2] <- "time_diff"
  ct.df$time_diff <- as.numeric(ct.df$time_diff)
  return(ct.df)
}


data_tables <- dbListTables(con)
encounter <- tbl(con, "encounter")
order_med <- tbl(con, "order_med")

#order_med.dt <- 

# function to clean data 
# 
library(lubridate)
#with_tz(ymd_hms(stroke_cohort$emergencyAdmitTime),"America/Los_Angeles")

convert_datetime <- function(timeEHR){
  #convert to America_Pacific in lubridate
  # requires format like this
  # "2014-06-18 17:21:00" "2014-08-05 16:14:00" "2014-08-31 19:10:00" "2014-09-02 19:23:00" "2014-09-24 15:27:00" "2014-09-27 16:21:00" "2014-09-27 18:16:00"
  # "2014-09-28 18:46:00" "2014-10-18 15:55:00" "2014-10-29 19:21:00" "2014-10-29 22:53:00" "2014-10-30 18:52:00" "2014-11-10 13:30:00" "2014-11-23 18:21:00"
  # "2014-11-25 11:43:00" "2014-11-29 10:17:00"
  
  #into this format
  
  #[31] "2011-10-17 06:19:00 PDT" "2011-11-06 07:03:00 PST" "2011-11-07 12:36:00 PST" "2011-11-12 03:29:00 PST" "2011-11-16 23:37:00 PST"
  #[36] "2011-11-18 09:11:00 PST" "2011-11-29 05:21:00 PST" "2011-12-11 09:54:00 PST" "2011-12-19 01:49:00 PST" "2011-12-21 04:14:00 PST"
  #[41] "2012-01-04 10:31:00 PST" "2012-01-22 09:31:00 PST" 
  return(with_tz(ymd_hms(timeEHR),"America/Los_Angeles"))
}


find_time_difference <- function(time_start,time_end, jc_uid){
  time_to_ct <- as.numeric(convert_datetime(time_end) - convert_datetime(time_start)) /60
  #return(time_to_ct)
  ct.df <- as_tibble(cbind(jc_uid, time_to_ct))
  colnames(ct.df)[1] <- "id"
  colnames(ct.df)[2] <- "time_diff"
  ct.df$time_diff <- as.numeric(ct.df$time_diff)
  return(ct.df)
}
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
# ------------------------------------------------------
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

convert_aggregate_date<- function(df){
  df$sub_date<- as.POSIXct(df$min_time,format="%Y-%m-%d %H:%M:%S")
  df$Day <- as.character( round(df$sub_date , "day" ) )
  day_split <- split(df, df$order_type)
  df_aggregate_order <- lapply(day_split, aggregate_event)
  df_aggregate <- lapply(df_aggregate_order, aggregate_name)
  event <- bind_rows(df_aggregate, .id = "order_event")
  return(event)
}

plot_density_difference <- function(dataframe){
  #ct.df2 <- dataframe %>% filter(time_diff < 100)
  pg2  <- ggplot(dataframe, aes(x=time_diff)) + 
    geom_histogram(aes(y=..density..),      # Histogram with density instead of count on y-axis
                   binwidth=1,
                   colour="black", fill="white") +
    geom_density(alpha=.2, fill="#FF6666")   # Overlay with transparent density plot 
  return(pg2)
}

# TO DO function to download data by sql query into R 

download_bq <- function(project, sql){
  tb <- bq_project_query(project, sql)
  tb.dtx <- bq_table_download(tb)
  return(tb.dtx)
  
}

#--------------------------------------------------------

# -------------------------------------------------------

# Big Computation: 
# Goal Pull all Referral and Save 

# Sql Call that Pulls the All the Patients that had a description of referral
#sql <- "select * from `clinical_inpatient.stroke_ministudy`"
sql <- "
select 
  opCT.jc_uid, 
cast(opCT.pat_enc_csn_id_coded as string) as string_id, 
admit.event_type,  
admit.pat_class, 
admit.effective_time_jittered as emergencyAdmitTime, 
min(opCT.order_inst_jittered) as ctHeadOrderTime,
dc.dx_name,
dc.icd10
from 
datalake_47618.adt as admit, 
datalake_47618.order_proc as opCT,
datalake_47618.diagnosis_code as dc

where admit.event_type_c = 1 -- Admission
and admit.pat_class_c = '112' -- Emergency Services
and TIMESTAMP_ADD(TIMESTAMP(admit.effective_time_jittered), INTERVAL -60 MINUTE) < TIMESTAMP(opCT.order_inst_jittered)
and TIMESTAMP_ADD(TIMESTAMP(admit.effective_time_jittered), INTERVAL 60 MINUTE) >= TIMESTAMP(opCT.order_inst_jittered)
and opCT.proc_code like 'IMGCTH%' -- CT Head orders
and admit.pat_enc_csn_id_coded = opCT.pat_enc_csn_id_coded
and dc.pat_enc_csn_id_coded = admit.pat_enc_csn_id_coded 
and dc.pat_enc_csn_id_coded = opCT.pat_enc_csn_id_coded
group by 
opCT.jc_uid,
opCT.pat_enc_csn_id_coded,
admit.event_type, 
admit.pat_class, 
admit.effective_time_jittered,
dc.dx_name,
dc.icd10
"

# Creating DBI connection to Google BigQuery 1
con <- dbConnect(
  bigrquery::bigquery(),
  project = "mining-clinical-decisions",
  dataset = 'starr_datalake2018' ,
  billing = project
)


data <- download_bq(project, sql)

data_split <- split(data, data$string_id)
stroke_cohort <- data
test1 <- find_time_difference(stroke_cohort$emergencyAdmitTime, stroke_cohort$ctHeadOrderTime, stroke_cohort$jc_uid)
View(data_split$`131003886752`)

table_dx_name <- as.data.frame(table(data$dx_name))
colnames(table_dx_name)
newdata <- table_dx_name[order(-table_dx_name$Freq),] 
View(newdata)
test1$event <- "Er to CT Order"

plot_density_difference(test1)

# find diagnoses associated with ct scan 
library(DBI)
library(bigrquery)
dbTableList <-dbListTables(con)
diagnoses <- tbl(con, "diagnosis_code")


data$pat_enc_csn_id_coded 

