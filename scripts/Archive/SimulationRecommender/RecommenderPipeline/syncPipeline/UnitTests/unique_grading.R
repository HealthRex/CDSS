library(data.table)
library(RPostgreSQL)
library(DBI)
library(tidyverse)
library(dplyr)
library(xlsx)

# FUNCTIONS: AGGREGATE 

# database driver connection
drv <- dbDriver("PostgreSQL")

# connection to database
con <- dbConnect(drv, dbname = "stride_inpatient_2014",
                 host = "localhost", port = 5432,
                 user = "postgres", password = "")

adf <- function(df){
  return(as.data.frame(df))
}

sim_patient_order <- tbl(con, "sim_patient_order")
spo <-  adf(sim_patient_order)

clinical_item <- tbl(con, "clinical_item")
ci <-  adf(clinical_item)

sim_state <- tbl(con, "sim_state")
ss <-  adf(sim_state)


# split on sim_state_id  


# generate unique sim_state_order 

split_unique_orders <- function(x){
  clinical_item_id <-  as.data.frame(unique(x$clinical_item_id))
  colnames(clinical_item_id) <- 'clinical_item_id'
  return(clinical_item_id)
}



join_unique_orders_name <- function(x){
# ASSUMES ci is clinical_item_table 
  y <- ci %>% select(clinical_item_id, description)
  return(merge(x, y, by = 'clinical_item_id' ))
}

return_unique_orders <- function(x){
  sim_state_split <- split(x, x$sim_state_id)
  list_of_unique_orders <- lapply(sim_state_split, split_unique_orders)
  order_description <- lapply(list_of_unique_orders, join_unique_orders_name)
  name_vector_order  <- names(order_description)
  ndf <- adf(name_vector_order)
  colnames(ndf)  <-  'sim_state_id'
  state_df <- merge(ndf,sim_state, by =  'sim_state_id')
  names(name_vector_order)  <-  state_df$description
  return(ndf)
  }

return_unique_orders <- function(x){
  sim_state_split <- split(x, x$sim_state_id)
  list_of_unique_orders <- lapply(sim_state_split, split_unique_orders)
  order_description <- lapply(list_of_unique_orders, join_unique_orders_name)
  clinical_state_orders <-  bind_rows(order_description)
  #name_vector_order  <- names(order_description)
  #ndf <- adf(name_vector_order)
  #colnames(ndf)  <-  'sim_state_id'
  #state_df <- merge(ndf,sim_state, by =  'sim_state_id')
  #names(name_vector_order)  <-  state_df$description
  return(clinical_state_orders)
}


mening_state_id <- c(30,31,32)
pulmonary_emolism_state_id <- c( 10, 11,12,8)
neutropenic_fever_state_id <- c(5000,5001,5002,5003)
gi_bleed_state_id <- c(14,15,16,17)
afib_state_id <- c(40,41,43,46,42,45,44)


unique_meningitis_30 <- return_unique_orders(spo %>% filter(sim_state_id  == 30))
unique_meningitis_31 <- return_unique_orders(spo %>% filter(sim_state_id  ==  31))
unique_meningitis_32 <- return_unique_orders(spo %>% filter(sim_state_id  == 32))

unique_meningitis_30$sim_state_id <- 30
unique_meningitis_31$sim_state_id <- 31
unique_meningitis_32$sim_state_id <- 32


unique_pe_10 <- return_unique_orders(spo %>% filter(sim_state_id  == 10))
unique_pe_11 <- return_unique_orders(spo %>% filter(sim_state_id  == 11))
unique_pe_12 <- return_unique_orders(spo %>% filter(sim_state_id  == 12))
unique_pe_8 <- return_unique_orders(spo %>% filter(sim_state_id  == 8))

unique_pe_8$sim_state_id  <- 8
unique_pe_10$sim_state_id  <- 10
unique_pe_11$sim_state_id  <- 11
unique_pe_12$sim_state_id  <- 12

unique_neutropenic_5000 <- return_unique_orders(spo %>% filter(sim_state_id  == 5000))
unique_neutropenic_5001 <- return_unique_orders(spo %>% filter(sim_state_id  == 5001))
unique_neutropenic_5002 <- return_unique_orders(spo %>% filter(sim_state_id  == 5002))
unique_neutropenic_5003 <- return_unique_orders(spo %>% filter(sim_state_id  == 5003))

unique_neutropenic_5000$sim_state_id  <- 5000
unique_neutropenic_5001$sim_state_id  <- 5001
unique_neutropenic_5002$sim_state_id  <- 5002
unique_neutropenic_5003$sim_state_id  <- 5003

unique_gi_14 <- return_unique_orders(spo %>% filter(sim_state_id  == 14))
unique_gi_15 <- return_unique_orders(spo %>% filter(sim_state_id  == 15))
unique_gi_16 <- return_unique_orders(spo %>% filter(sim_state_id  == 16))
unique_gi_17 <- return_unique_orders(spo %>% filter(sim_state_id  == 17))

unique_gi_14$sim_state_id  <- 14
unique_gi_15$sim_state_id  <- 15
unique_gi_16$sim_state_id  <- 16
unique_gi_17$sim_state_id  <- 17



unique_afib_40 <- return_unique_orders(spo %>% filter(sim_state_id  == 40))
unique_afib_41 <- return_unique_orders(spo %>% filter(sim_state_id  == 41))
unique_afib_42 <- return_unique_orders(spo %>% filter(sim_state_id  == 42))
unique_afib_43 <- return_unique_orders(spo %>% filter(sim_state_id  == 43))
unique_afib_44 <- return_unique_orders(spo %>% filter(sim_state_id  == 44))
unique_afib_45 <- return_unique_orders(spo %>% filter(sim_state_id  == 45))
unique_afib_46 <- return_unique_orders(spo %>% filter(sim_state_id  == 46))

unique_afib_40$sim_state_id  <- 40
unique_afib_41$sim_state_id  <- 41
unique_afib_42$sim_state_id  <- 42
unique_afib_43$sim_state_id  <- 43
unique_afib_44$sim_state_id  <- 44
unique_afib_45$sim_state_id  <- 45
unique_afib_46$sim_state_id  <- 46


