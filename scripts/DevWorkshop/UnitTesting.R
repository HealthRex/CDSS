# Unit Testing in R 

# Jonathan Chiang 

#install.packages("testthat")
#install.packages("devtools")

# adapted from 
# http://r-pkgs.had.co.nz/tests.html

library(testthat)
library(devtools)

tmp <- tempfile()

#setwd("/Users/jonc101/Documents/Biomedical_Data_Science/data_engineer/")

# A context defines a set of tests that test related functionality. 
# Usually you will have one context per file, 
# but you may have multiple contexts in a single file if you so choose.

context("String length")
library(stringr)

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

test_that("str_length of missing is missing", {
  expect_equal(str_length(NA), NA_integer_)
  expect_equal(str_length(c(NA, 1)), c(NA, 1))
  expect_equal(str_length("NA"), 2)
})

# Example of FAILING A TEST 

test_that("str_length of factor is length of level failure ", {
  expect_equal(str_length(factor("a")), 2)
  expect_equal(str_length(factor("ab")), 3)
  expect_equal(str_length(factor("abc")), 4)
})


# Tests are organised hierarchically: 
# expectations are grouped into tests which are organised in files:
  
# An expectation is the atom of testing. 
# It describes the expected result of a computation: 
# Does it have the right value and right class? 
# Does it produce error messages when it should? 
# An expectation automates visual checking of results in the console. 
# Expectations are functions that start with expect_.

# A test groups together multiple expectations to test the output from a simple function, 
# a range of possibilities for a single parameter from a more complicated function, 
# or tightly related functionality from across multiple functions. 
# This is why they are sometimes called unit as they test one unit of functionality. 
# A test is created with test_that() .

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


