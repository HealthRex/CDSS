library(data.table)
library(RPostgreSQL)
library(DBI)
library(tidyverse)

drv <- dbDriver("PostgreSQL")

con <- dbConnect(drv, dbname = "stride_inpatient_2014",
                 host = "localhost", port = 5432,
                 user = "postgres", password = "MANUALLY CHANGE PASSWORD")
