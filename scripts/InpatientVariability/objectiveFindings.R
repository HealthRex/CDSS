library(tidyverse)
library(bigrquery)

# library(DBI)
# library(scales)
# library(sqldf) # https://www.r-bloggers.com/in-between-a-rock-and-a-conditional-join/
# library(fuzzyjoin)
# library(rio)

## warning = TRUE # default
## options(warn = 0) # default
# warning = FALSE
# options(warn = -1)
# options(scipen = 20)

##############################################################################
##### filepaths
dir <- "/Users/kushgupta/Documents/StanfordMD/Projects/Mentors/Chen/Inpatient\ Variability\ Cost\ Reduction/"
filepath1 <- paste0(dir,"code/comorbiditiesOnAdmission.sql")

##############################################################################
##### import data
sqlQuery <- readChar(filepath1, file.info(filepath1)$size)
project <- "som-nero-phi-jonc101-secure" # "mining-clinical-decisions"
results <- bq_project_query(project, sqlQuery)
tb <- as_tibble(bq_table_download(results, bigint = c("integer64"))) # bigint needed to properly download full PT_ENC_CSN_ID
rm(results)


##############################################################################