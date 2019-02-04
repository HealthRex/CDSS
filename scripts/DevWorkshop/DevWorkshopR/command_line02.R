#!/usr/bin/env Rscript

# Jonathan Chiang 
# adapted from: https://linuxconfig.org/how-to-access-a-command-line-arguments-using-rscript-gnu-r
# how to write a arg in R script

# ------------------------------- # 
#  make sure R is in your path!   #
# ------------------------------- #

#args = commandArgs(trailingOnly=TRUE)

setwd("/Users/jonc101/Documents/Biomedical_Data_Science/data_engineer/DevWorkshopR/")
source("unit_testing_c.R")

args <- commandArgs(TRUE)

#commandArgs()

print(first_of_month(args[1]))

# "2003-03-15"