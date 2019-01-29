library(testthat)
library(lubridate)

setwd("/Users/jonc101/Documents/Biomedical_Data_Science/data_engineer/DevWorkshopR/")

test_that ( 
  "June and November", 
  {
    expect_equal(first_of_month("2004-06-15"), as.character("2004-06-01"))
    expect_equal(first_of_month("2009-11-06"), as.character("2009-11-01"))
  }
)

test_that ( 
  "December and January", 
  {
    expect_equal(first_of_month("2018-12-15"), as.character("2018-12-01"))
    expect_equal(first_of_month("2012-01-07"), as.character("2012-01-01"))
    
  }
)

