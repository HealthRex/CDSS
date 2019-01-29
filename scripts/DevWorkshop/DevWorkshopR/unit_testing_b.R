#unit_testing_b.R
library(lubridate)
library(testthat)


first_of_month <- function(mystring){
  mydate <- as.Date(mystring)
  mydate_first_of_month <- floor_date(mydate, "month")
  result <- as.character(mydate_first_of_month )
  return(result)
}

setwd("/Users/jonc101/Documents/Biomedical_Data_Science/data_engineer/DevWorkshopR/")
source("02_unit_testing.R")
