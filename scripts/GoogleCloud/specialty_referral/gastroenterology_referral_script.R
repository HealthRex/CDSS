library(bigrquery)
library(DBI)
library(dplyr)
library(lubridate)
library(stringr)
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


# Listing Datatables 
data_tables <- dbListTables(con)

# Creating Connection to Cardiology Referral Patients 
cardiology_referral <- tbl(con, "z2_subaim_referral_table_gastro")

# Creating Connection to Event Table of Cardiology Patients with Description New Patient 
cardiology_referral_event <- tbl(con, "z5_subaim_referral_table_gastro")

department_map <- tbl(con, "dep_map")


# reassigning variable names for ease of use
# pulls data from GCP BQ (download)
cdf <- as_tibble(cardiology_referral)
cdn <- as_tibble(cardiology_referral_event)
dep.df <- as_tibble(department_map)

# View Data 

# Compare Population between both data sets  
a1 <- unique(cdf$jc_uid)  
a2 <- unique(cdn$jc_uid)
# write test 

# Creating an Intersecting Patient Population 
same_cohort <- intersect(a1,a2)
# same_cohort2 <- intersect(a2,a1)
# write test 

cdf2 <- cdf %>% filter(jc_uid %in% same_cohort)
cdn2 <- cdn %>% filter(jc_uid %in% same_cohort)

cdf2$date <- cdf2$appt_time_jittered

## exploratory 
# look at unique department places 
visit_department <- unique(cdn2$department_id)
list_of_department <- dep.df %>% filter(department_id %in% visit_department)
unique_speciality <- unique(list_of_department$specialty)

##
cdf3 <- df_convert_date_to_numeric(cdf2)
cdn3 <- df_convert_date_to_numeric(cdn2)

cdf4 <- cdf3 %>% select(jc_uid, description, pat_enc_csn_id_coded, description, visit_type, department_id, date_num) %>% arrange(date_num)
cdn4 <- cdn3 %>% select(jc_uid, description, pat_enc_csn_id_coded, description, visit_type, department_id, date_num) %>% arrange(date_num)

cdf5 <- merge(cdf4, dep.df)
cdn5 <- merge(cdn4, dep.df)

#cardiology_list <- c("Cardiology", "Cardiothoracic Surgery", "Cardiology Lab", "Cardiovascular Medicine", "Vascular Surgery")

cardiology_list <- c("Gastrointestinal", "Gastroenterology")
cdn6 <- cdn5 %>% filter(specialty %in% cardiology_list)

# create new dataframe 
dt2 <- rbind(cdf5, cdn6)


# create a list from  ID 
patient_split <- split(dt2, dt2$jc_uid)

# return a dataframe only if the rows is greater one 


get_row <- function(c){
  t <- dim(c)[1]
  return(t)
}
cond <- sapply(patient_split, function(x) get_row(x) > 1)
rc <- patient_split[cond]


sort_date_num <- function(df){
  return(df %>% arrange(date_num))
}

rc2 <- lapply(rc, sort_date_num)

# update function 
# needs to cover instance where the first occurence is not the same date 

visit_difference <- function(df1){
  df1$dateval <- as.numeric(df1$date_num)
  dfx <- df1 %>% filter(description == "REFERRAL TO GASTROENTEROLOGY")
  mini_df <- dfx[1,] 
  initial_date <- as.numeric(mini_df$date_num[1]) 
  mini_df2 <- df1 %>% filter(description != "REFERRAL TO GASTROENTEROLOGY") %>% filter(dateval > initial_date)
  df3 <- rbind(mini_df, mini_df2)  
  df3$date_num2 <- ymd(df3$date_num)
  return(df3$date_num2[2] - df3$date_num2[1])
}



vis_list <- lapply(rc2, visit_difference)
t <- do.call(rbind.data.frame, vis_list)
colnames(t) <- "visit_difference"
t2 <- t %>% filter(t < 365)
summary(t2)

