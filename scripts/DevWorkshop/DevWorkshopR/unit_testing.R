# Unit Testing in R 

# Jonathan Chiang 

# ------------------- #
# PACKAGES TO INSTALL # 
# ------------------- # 


#install.packages("testthat")
#install.packages("devtools")
#install.packages("lubridate")

# adapted from 
# http://r-pkgs.had.co.nz/tests.html

library(testthat)
library(devtools)
library(lubridate)
library(stringr)

tmp <- tempfile()

#setwd("/Users/jonc101/Documents/Biomedical_Data_Science/data_engineer/DevWorkshopR")

# A context defines a set of tests that test related functionality. 
# Usually you will have one context per file, 
# but you may have multiple contexts in a single file if you so choose.

context("String length")

test_that("str_length is number of characters", {
  expect_equal(str_length("a"), 1)
  expect_equal(str_length("ab"), 2)
  expect_equal(str_length("abc"), 3)
})

test_that("str_length of factor is length of level", {
  expect_equal(str_length(factor("a")), 1)
  expect_equal(str_length(factor("ab")), 2)
  expect_equal(str_length(factor("abc")), 3)
})


# Example of FAILING A TEST 

test_that("str_length of factor is length of level failure ", {
  expect_equal(str_length(factor("a")), 1)
  expect_equal(str_length(factor("ab")), 2)
  expect_equal(str_length(factor("abcd")), 3)
})


# Tests are organised hierarchically: 
# expectations are grouped into tests which are organised in files:
  
# An expectation is the atom of testing. 
# It describes the expected result of a computation: 
# Does it have the right value and right class? 
# Does it produce error messages when it should? 
# An expectation automates visual checking of results in the console. 
# Expectations are functions that start with expect_.

# called unit as they test one unit of functionality. 

# -----------------------------
# General Tips for Writing Test 
# -----------------------------

# Each test should have an informative name and cover a single unit of functionality. 
# The idea is that when a test fails, you’ll know what’s wrong and where in your code to look for the problem. 
# You create a new test using test_that(), with test name and code block as arguments. 
# The test name should complete the sentence “Test that …”. The code block should be a collection of expectations.




# -----------------------------
# What to test 
# -----------------------------

# Whenever you are tempted to type something into a print statement or a debugger expression, 
# write it as a test instead. — Martin Fowler

# Focus on testing the external interface to your functions
# Strive to test each behaviour in one and only one test
# Avoid testing simple code that you’re confident will work
# Always write a test when you discover a bug




first_of_month <- function(mystring){
  yr = substr(mystring, 1, 4)
  mon <- as.numeric(substr(mystring,6,7))
  lastmon <- stringr::str_pad(mon , width = 2, pad = 0)
  result <- paste(yr, lastmon, "01", sep = "-")
  return(result)  
}


#first_of_month("2018-05-31")
#first_of_month("2018-06-15")



first_of_month <- function(x) {
  x <- ymd(x)
  return(rollback(x, roll_to_first = TRUE))
}


#first_of_month("2018-07-01")
#first_of_month("2018-01-07")

