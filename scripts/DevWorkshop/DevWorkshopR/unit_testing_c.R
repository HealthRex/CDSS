#unit_testing_b.R
library(lubridate)
library(testthat)

first_of_month <- function(x) {
  x <- ymd(x)
  #return(rollback(x, roll_to_first = TRUE))
  
  x2 <- as.character(rollback(x, roll_to_first = TRUE))
  return(x2)
}


setwd("/Users/jonc101/Documents/Biomedical_Data_Science/data_engineer/DevWorkshopR/")
source("02_unit_testing.R")


# SHOULD THROW ATTRIBUTE ERROR 