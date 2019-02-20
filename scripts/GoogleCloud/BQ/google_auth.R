######## bigquery way 
# install bigrquery
# install DBI
# install dplyr 
# Get the name of your project (mining-clinical-decisions)
# Get the name of your dataset (datalake_47618)
# authenticate online with google 
# Can use tidyverse querying or standard sql 
# 



library(bigrquery)
project <- "mining-clinical-decisions" # put your project ID here

sql <- "
        SELECT
          jc_uid, order_type,  description
        FROM
          `datalake_47618.order_proc` 
        WHERE
          jc_uid = 'JCe6e161' 
        LIMIT 5 
      "

sql2 <- "SELECT 
  jc_uid, contact_date_jittered, department_id, visit_type, enc_type
FROM 
`datalake_47618.encounter`
WHERE
enc_type = 'Office Visit' 
and 
visit_type like 'RETURN P%' 
and 
contact_date_jittered > '2014-01-01'
ORDER BY 
contact_date_jittered"


tb <- bq_project_query(project, sql)
tb2 <- bq_project_query(project, sql2)
test3 <- bq_table_download(tb2)
new_p <- test2 
ret_p <- test3


##### TIDYVERSE WAY 


library(DBI)
library(dplyr)
con <- dbConnect(
  bigrquery::bigquery(),
  project = "mining-clinical-decisions",
  dataset = 'datalake_47618' ,
  billing = project
)





data_tables <- dbListTables(con)
encounter <- tbl(con, "encounter")
head(encounter)
test2 <- encounter %>% 
            select(pat_enc_csn_id_coded, inpatient_data_id_coded) %>% 
            head(5)

######
# create a new dataset 

library(DBI)
library(dplyr)
con <- dbConnect(
  bigrquery::bigquery(),
  project = "mining-clinical-decisions",
  dataset = 'datalake_47618' ,
  billing = project
)


