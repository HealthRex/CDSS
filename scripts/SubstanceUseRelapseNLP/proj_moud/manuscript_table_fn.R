manuscript_table <- function(cons, bq_dataset, split_dfs) {
  
  table_abstracted_data <- tbl(cons$mcd_ivan_db, bq_dataset) %>% 
    collect() 
  
  length(unique(split_dfs$train$person_id))
  length(unique(split_dfs$test$person_id))
  
  
  split_dfs$train %>% 
    distinct(person_id, female) %>% 
    pull(female) %>% 
    sum()
  split_dfs$train %>% 
    distinct(person_id, male) %>% 
    pull(male) %>% 
    sum()
  split_dfs$test %>% 
    distinct(person_id, female) %>% 
    pull(female) %>% 
    sum()
  split_dfs$test %>% 
    distinct(person_id, male) %>% 
    pull(male) %>% 
    sum()
  
  demographic_names <- split_dfs$train %>% 
    select(-uniq_id,
           -person_id,
           -age_at_start,
           -female,
           -male,
           -starts_with("id_")) %>% 
    names()
  
  demographic_table_train <- map(demographic_names,
                                 function(demographic_names_) {
                                   
                                   table_output <- split_dfs$train %>% 
                                     select(-uniq_id,
                                            -age_at_start,
                                            -female,
                                            -male,
                                            -starts_with("id_")) %>% 
                                     distinct(person_id, .keep_all = TRUE) %>% 
                                     select(-person_id) %>% 
                                     count(!!sym(demographic_names_))
                                   
                                   return(table_output)
                                 })
  demographic_table_test <- map(demographic_names,
                                function(demographic_names_) {
                                  
                                  table_output <- split_dfs$test %>% 
                                    select(-uniq_id,
                                           -age_at_start,
                                           -female,
                                           -male,
                                           -starts_with("id_")) %>% 
                                    distinct(person_id, .keep_all = TRUE) %>% 
                                    select(-person_id) %>% 
                                    count(!!sym(demographic_names_))
                                  
                                  return(table_output)
                                })
  
  split_dfs$train %>% 
    mutate(age_breaks = age_at_start %>% 
             cut(breaks = c(-Inf, 25, 45, 60, Inf), 
                 labels = c(" 18-25", " 26-45", " 46-60", " >60s"))) %>% 
    count(age_breaks)
  split_dfs$test %>% 
    mutate(age_breaks = age_at_start %>% 
             cut(breaks = c(-Inf, 25, 45, 60, Inf), 
                 labels = c(" 18-25", " 26-45", " 46-60", " >60s"))) %>% 
    count(age_breaks)
  
  train_test_age <- list("train_age" = split_dfs$train$age_at_start,
                         "test_age" = split_dfs$test$age_at_start)
  median_age <- imap(train_test_age, ~MedianCI(x = .x, 
                                               conf.level = 0.95, 
                                               sides = c("two.sided"),
                                               na.rm = FALSE, 
                                               method = c("exact")))
  
  train_test <- c("train", "test")
  treatment_duration_list <- map(train_test,
                                 function(train_test_) {
                                   
                                   MedianCI(split_dfs[[train_test_]] %>% 
                                              left_join(table_abstracted_data %>% 
                                                          select(person_id,
                                                                 treatment_duration_days), by = c("person_id")) %>% 
                                              pull(treatment_duration_days), 
                                            conf.level = 0.95, 
                                            sides = c("two.sided"),
                                            na.rm = FALSE, 
                                            method = c("exact")) %>% 
                                     broom::tidy()
                                   
                                 }) %>% 
    setNames(train_test)
  
  person_id_events_list <- map(train_test,
                               function(train_test_) {
                                 
                                 person_id_events <- split_dfs[[train_test_]] %>% 
                                   group_by(person_id) %>% 
                                   mutate(person_id_events = row_number()) %>% 
                                   select(person_id,
                                          person_id_events) %>% 
                                   filter(person_id_events == max(person_id_events))
                                 
                                 MedianCI(person_id_events %>% 
                                            pull(person_id_events), 
                                          conf.level = 0.95, 
                                          sides = c("two.sided"),
                                          na.rm = FALSE, 
                                          method = c("exact")) %>% 
                                   broom::tidy()
                                 
                               }) %>% 
    setNames(train_test)
  
  group_names <- c("diagnosis", "drug", "procedure", "note_nlp")
  train_feature_lists <- map(group_names,
                             function(group_names_) {
                               
                               split_dfs$train %>% 
                                 select(person_id,
                                        ends_with(group_names_)) %>% 
                                 group_by(person_id) %>%
                                 summarize(across(everything(), sum)) %>% 
                                 mutate_at(vars(starts_with("id_")), .funs = list(~ifelse(.x >= 1, 1, .x))) %>% 
                                 mutate(unique_var_counts = rowSums(select(., -person_id) > 0))
                               
                             }) %>% 
    setNames(group_names)
  test_feature_lists <- map(group_names,
                            function(group_names_) {
                              
                              split_dfs$test %>% 
                                select(person_id,
                                       ends_with(group_names_)) %>% 
                                group_by(person_id) %>%
                                summarize(across(everything(), sum)) %>% 
                                mutate_at(vars(starts_with("id_")), .funs = list(~ifelse(.x >= 1, 1, .x))) %>% 
                                mutate(unique_var_counts = rowSums(select(., -person_id) > 0))
                              
                            }) %>% 
    setNames(group_names)
  
  train_median_ci_for_feature_lists <- map(group_names,
                                           function(group_names_) {
                                             
                                             MedianCI(train_feature_lists[[group_names_]]$unique_var_counts, 
                                                      conf.level = 0.95, 
                                                      sides = c("two.sided"),
                                                      na.rm = FALSE, 
                                                      method = c("exact")) %>% 
                                               broom::tidy()
                                             
                                           }) %>% 
    setNames(group_names)
  test_median_ci_for_feature_lists <- map(group_names,
                                          function(group_names_) {
                                            
                                            MedianCI(test_feature_lists[[group_names_]]$unique_var_counts, 
                                                     conf.level = 0.95, 
                                                     sides = c("two.sided"),
                                                     na.rm = FALSE, 
                                                     method = c("exact")) %>% 
                                              broom::tidy()
                                            
                                          }) %>% 
    setNames(group_names)
  
  
  
}
