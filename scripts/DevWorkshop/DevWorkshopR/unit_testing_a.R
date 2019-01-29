#unit_testing_b.R
library(lubridate)
library(testthat)

# correct the error one 

first_of_month <- function(mystring){
  yr = substr(mystring, 1, 4)
  mon <- as.numeric(substr(mystring,6,7))
  thismon <- stringr::str_pad(mon , width = 2, pad = 0)
  # hint 
  result <- as.character(paste(yr, thismon, "01", sep = "-"))
  return(result)  
}

first_of_month("2014-12-03")
first_of_month("2014-02-13")
first_of_month("2003-03-15")



setwd("/Users/jonc101/Documents/Biomedical_Data_Science/data_engineer/DevWorkshopR/")
source("02_unit_testing.R")
