library(data.table)
library(RPostgreSQL)
library(DBI)
library(tidyverse)
library(dplyr)
library(xlsx)

setwd("/Users/jonc101/Box Sync/jichiang_folders/clinical_recommender_pipeline/tracker_data/tracker_output/")
tg <-  read.csv('tracker_output_v11.csv')
#df_tracker <- read.csv('tracker_output_v10.csv')
#tg <- df_tracker %>% filter(!name_y %in% c('LisaShieh', 'Default User'))
#write.csv(tg, 'tracker_output_v11.csv')

tg$ratioOrderFromRecommender <- (tg$orders_from_recommender/tg$unqique_recommended_options)
tg$ratioOrderFromManualSearchVsManualSearchOptions <- (tg$orders_from_manual_search/tg$manual_search_options)

tg_case_split <- split(tg, tg$sim_patient_id)

take_first_row <- function(x){
  return(x[1,])
}

first_case <- bind_rows(lapply(tg_case_split, take_first_row))
#View(first_case)
case_split <- split(first_case, first_case$case)


#unique(case_split$atrial_fibrillation$name_y)
#afib <- case_split$atrial_fibrillation %>% filter(!name_y %in% 'LisaShieh')
#gi_bleed <- case_split$gi_bleed %>% filter(!name_y %in% 'LisaShieh')
#meningitis <- case_split$meningitis %>% filter(!name_y %in% 'LisaShieh')
#neutropenic <- case_split$neutropenic %>% filter(!name_y %in% 'LisaShieh')
#pulmonary_embolism <- case_split$pulmonary_embolism %>% filter(!name_y %in% 'LisaShieh')
#afib$elapsed_time_secs <- as.numeric(as.character(stringr::str_split_fixed(afib$elapsed_time, ':',3)[,2])) * 60 +  as.numeric(as.character(stringr::str_split_fixed(afib$elapsed_time, ':',3)[,3]))

clean_elapsed_time <- function(df){
  afib <- df
  afib$elapsed_time_secs <- as.numeric(as.character(stringr::str_split_fixed(afib$elapsed_time, ':',3)[,2])) * 60 +  as.numeric(as.character(stringr::str_split_fixed(afib$elapsed_time, ':',3)[,3]))
  return(afib)
}

case_split_elapsed_time <- lapply(case_split, clean_elapsed_time)
case_split_elapsed_time$atrial_fibrillation

# summary(case_split_elapsed_time[[1]]$elapsed_time_secs)
# IQR all columns: 
#apply(counts, 2, max)
# return  IQR  for all columns:  



# -------------------------------------------------------------------------------------------------- #
#
#
#                                 TODO 
#
#
#
# --------------------------------------------------------------------------------------------------

case_table_figures <- function(tg){


    x.off <- tg %>% filter(recommended_options == 0 )
    x.on  <- tg %>% filter(recommended_options > 0 )
    
    iqr_column <- function(column_df, colname, on_off){
      
      # RECOMMENDER OFF
      iqr_25 <- t(summary(column_df))[[2]]
      iqr_median <- t(summary(column_df))[[3]]
      iqr_75 <- t(summary(column_df))[[4]]
      
      x_iqr  <- cbind(on_off, colname, round(iqr_25, 2) , round(iqr_median,2), round(iqr_75,2) )
      
      # RECOMMENDER ON
      #x.on_iqr_25 <- t(summary(x.on$column_df))[[2]]
      #x.on_iqr_median <- t(summary(x.on$column_df))[[3]]
      #x.on_iqr_75 <- t(summary(x.on$column_df))[[4]]
      return(x_iqr)
    } 
    
    #  off  
    #  on 
    
    
    
    # num_note_clicks 
    off_num_note_clicks <- iqr_column(x.off$num_note_clicks, 'num_note_clicks', 'off')
    on_num_note_clicks <- iqr_column(x.on$num_note_clicks, 'num_note_clicks', 'on')
    
    # "num_results_review_clicks"    
    off_num_results_review_clicks <- iqr_column(x.off$num_results_review_clicks, 'num_results_review_clicks', 'off')
    on_num_results_review_clicks <- iqr_column(x.on$num_results_review_clicks, 'num_results_review_clicks', 'on')
    
    
    # "recommended_options" 
    off_recommended_options <- iqr_column(x.off$recommended_options, 'recommended_options', 'off')
    on_recommended_options <- iqr_column(x.on$recommended_options, 'recommended_options', 'on')
    
    # unqique_recommended_options" 
    off_unqique_recommended_options <- iqr_column(x.off$unqique_recommended_options, 'unique_recommended_options', 'off')
    on_unqique_recommended_options <- iqr_column(x.on$unqique_recommended_options, 'unique_recommended_options', 'on')
    
    
    # "manual_search_options"        
    off_manual_search_options <- iqr_column(x.off$manual_search_options, 'manual_search_options', 'off')
    on_manual_search_options <- iqr_column(x.on$manual_search_options, 'manual_search_options', 'on')
    
    # "total_orders"    
    off_total_orders <- iqr_column(x.off$total_orders, 'total_orders', 'off')
    on_total_orders <- iqr_column(x.on$total_orders, 'total_orders', 'on')
    
    # "orders_from_recommender"       
    off_orders_from_recommender <- iqr_column(x.off$orders_from_recommender, 'orders_from_recommender', 'off')
    on_orders_from_recommender <- iqr_column(x.on$orders_from_recommender, 'orders_from_recommender', 'on')
    
    # "orders_from_manual_search"
    off_orders_from_manual_search <- iqr_column(x.off$orders_from_manual_search, 'orders_from_manual_search', 'off')
    on_orders_from_manual_search <- iqr_column(x.on$orders_from_manual_search, 'orders_from_manual_search', 'on')
    
    # "orders_from_recommender_missed" 
    off_orders_from_recommender_missed <- iqr_column(x.off$orders_from_recommender_missed, 'orders_from_recommender_missed', 'off')
    on_orders_from_recommender_missed <- iqr_column(x.on$orders_from_recommender_missed, 'orders_from_recommender_missed', 'on')
    
    case  <-  as.data.frame(rbind(off_manual_search_options , on_manual_search_options, off_num_note_clicks, 
            on_num_note_clicks, 
            off_num_results_review_clicks, 
            on_num_results_review_clicks, 
            off_orders_from_manual_search, 
            on_orders_from_manual_search, 
            off_orders_from_recommender,  
            on_orders_from_recommender, 
            off_orders_from_recommender_missed, 
            on_orders_from_recommender_missed, 
            off_recommended_options,
            on_recommended_options, 
            off_total_orders, 
            on_total_orders, 
            off_unqique_recommended_options, 
            on_unqique_recommended_options))
    colnames(case) <- c("recommender status", 'feature', 'iqr_25', 'median', 'iqr_75')                          
    return(case)               
                    
}                  
       
case_split <- split(tg, tg$case)               
lapply(case_split, case_table_figures)    
                         
                               



mean_elapsed_time_recommender_on_off <- function(x){
  x.on <- x %>% filter(recommended_options > 0 )
  x.off <- x %>% filter(recommended_options == 0 )
  t <- cbind(mean(x.on$elapsed_time_secs), mean(x.off$elapsed_time_secs))
  colnames(t) <- c('on', 'off')
  return(t)
}

mean_total_orders_recommender_on_off <- function(x){
  x.on <- x %>% filter(recommended_options > 0 )
  x.off <- x %>% filter(recommended_options == 0 )
  t <- cbind(mean(x.on$total_orders), mean(x.off$total_orders))
  colnames(t) <- c('on', 'off')
  return(t)
}  

summary_total_orders_recommender_on_off <- function(x){
  x.on <- x %>% filter(recommended_options > 0 )
  x.off <- x %>% filter(recommended_options == 0 )
  t = summary(x.on$total_orders)
  return(t)
}


mean_total_num_clicks_recommender_on_off <- function(x){
  x.on <- x %>% filter(recommended_options > 0 )
  x.off <- x %>% filter(recommended_options == 0 )
  t <- cbind(mean(x.on$total_num_clicks), mean(x.off$total_num_clicks))
  colnames(t) <- c('on', 'off')
  return(t)
}  



mean_total_manual_search_recommender_on_off <- function(x){
  x.on <- x %>% filter(recommended_options > 0 )
  x.off <- x %>% filter(recommended_options == 0 )
  t <- cbind(mean(x.on$orders_from_manual_search), mean(x.off$orders_from_manual_search))
  colnames(t) <- c('on', 'off')
  return(t)
}  

ttest_total_manual_search_recommender_on_off <- function(x){
  x.on <- x %>% filter(recommended_options > 0 )
  x.off <- x %>% filter(recommended_options == 0 )
  t <- t.test(x.on$orders_from_manual_search, x.off$orders_from_manual_search)
  return(t)
}  

mean_total_recommender_missed_recommender_on_off <- function(x){
  x.on <- x %>% filter(recommended_options > 0 )
  x.off <- x %>% filter(recommended_options == 0 )
  t <- cbind(mean(x.on$orders_from_recommender_missed), mean(x.off$orders_from_recommender_missed))
  colnames(t) <- c('on', 'off')
  return(t)
}  

ttest_total_recommender_missed_recommender_on_off <- function(x){
  x.on <- x %>% filter(recommended_options > 0 )
  x.off <- x %>% filter(recommended_options == 0 )
  t <- t.test(x.on$orders_from_recommender_missed, x.off$orders_from_recommender_missed)
  #colnames(t) <- c('on', 'off')
  return(t)
}  




ttest_total_recommender_missed_list  <- lapply(case_split_elapsed_time, ttest_total_recommender_missed_recommender_on_off )
ttest_total_manual_search_list  <- lapply(case_split_elapsed_time, ttest_total_manual_search_recommender_on_off) 


mean_elapsed_time_list  <- lapply(case_split_elapsed_time, mean_elapsed_time_recommender_on_off )
mean_total_orders_list <- lapply(case_split_elapsed_time, mean_total_orders_recommender_on_off )
mean_total_recommender_missed_list  <- lapply(case_split_elapsed_time, mean_total_recommender_missed_recommender_on_off )
mean_total_manual_search_recommender_list <- lapply(case_split_elapsed_time, mean_total_manual_search_recommender_on_off)
mean_total_num_clicks_list <- lapply(case_split_elapsed_time, mean_total_num_clicks_recommender_on_off)


View(case_split_elapsed_time)

cases_elapsed <- names(mean_elapsed_time_list)
cases_total_orders <- names(mean_elapsed_time_list)
cases_total_recommender_missed <- names(mean_total_manual_search_recommender_list)
cases_total_manual_search_recommener_list <- names(mean_total_manual_search_recommender_list)
cases_total_num_clicks_list <- names(mean_total_num_clicks_list)

elapsed_time <- as.data.frame(cbind(t(bind_rows(mean_elapsed_time_list))))
colnames(elapsed_time) <- c('on', 'off')
elapsed_time$metric <- 'elapsed_time'
elapsed_time$case <- rownames(elapsed_time)

total_orders <- as.data.frame(cbind(t(bind_rows(mean_total_orders_list))))
colnames(total_orders) <- c('on', 'off')
total_orders$metric <- 'total_number_of_orders'
total_orders$case <- rownames(total_orders)

total_recommender_missed <- as.data.frame(cbind(t(bind_rows(mean_total_recommender_missed_list))))
colnames(total_recommender_missed) <- c('on', 'off')
total_recommender_missed$metric <- 'total_number_recommender_missed'
total_recommender_missed$case <- rownames(total_recommender_missed)

total_manual_search <- as.data.frame(cbind(t(bind_rows(mean_total_manual_search_recommender_list))))
colnames(total_manual_search) <- c('on', 'off')
total_manual_search$metric <- 'orders_from_manual_search'
total_manual_search$case <- rownames(total_manual_search)

total_num_clicks<- as.data.frame(cbind(t(bind_rows(mean_total_num_clicks_list))))
colnames(total_num_clicks) <- c('on', 'off')
total_num_clicks$metric <- 'total_number_clicks'
total_num_clicks$case <- rownames(total_num_clicks)




setwd("/Users/jonc101/Box Sync/jichiang_folders/clinical_recommender_pipeline/")

table3v2<- rbind(elapsed_time, 
          total_orders, 
          total_recommender_missed, 
          total_manual_search, 
          total_num_clicks)
table3v3 <- table3v2
table3v3$on  <- round(table3v2$on,2)
table3v3$off <- round(table3v2$off,2)

#View(table3v3)

#write.csv(table3v3, 'table3v3.csv')

#lapply(case_split_elapsed_time, elapsed_summary_recommender_off)
#lapply(case_split_elapsed_time, elapsed_summary_recommender_on)
#lapply(case_split_elapsed_time, total_orders_recommender_on)
#lapply(case_split_elapsed_time, total_orders_recommender_off)

library(testthat)
#assertthat::are_equal()

setwd("/Users/jonc101/Box Sync/jichiang_folders/clinical_recommender_pipeline/")

load('case_split_elapsed_time.rda')

View(case_split_elapsed_time)
case_split_elapsed_time$atrial_fibrillation



spo <- adf(sim_patient_order)
table_of_orders <- table(spo$sim_patient_order_id)
#View(table_of_orders)
