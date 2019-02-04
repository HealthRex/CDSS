#!/usr/bin/env Rscript

# Jonathan Chiang 
# adapted from: https://linuxconfig.org/how-to-access-a-command-line-arguments-using-rscript-gnu-r
# how to write a arg in R script

# ------------------------------- # 
#  make sure R is in your path!   #
# ------------------------------- #

args <- commandArgs(TRUE)

# -----------------------------------------------
# MODULE  
# -----------------------------------------------

# 1) Hello World 

#print("Hello R")

# 2) Simple Addition 

#print(as.double(args[1]) + as.double(args[2]))

#-----------------------------------------------