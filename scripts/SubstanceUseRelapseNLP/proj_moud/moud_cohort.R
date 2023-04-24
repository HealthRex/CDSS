library(stringi)
# library(xlsx)
library(openxlsx)
library(googlesheets4)

source("~/unstructured-data/common_use/helper_functions.R")
source("~/ivan/common_use/get_bigquery_tables.R")
source("~/ivan/common_use/jchen_bigquery_connect.R")

get_oud_diagnosis_codes <- function(cons) {
  
  icd_codes <- tbl(cons$starr_omop_cdm5_deid_updated, "concept") %>% 
    select(concept_id,
           concept_name,
           vocabulary_id,
           concept_code,
           domain_id) %>% 
    filter(tolower(vocabulary_id) %in% c("icd9cm", "icd10cm")) %>% 
    filter(tolower(domain_id) == "condition") #%>% 
  # show_query()
  
  oud_icd_codes <- union_all(union_all(filter(icd_codes, tolower(concept_code) %like% "304.0%"),
                                       filter(icd_codes, tolower(concept_code) %like% "305.5%")),
                             filter(icd_codes, tolower(concept_code) %like% "f11.%")) %>%
    collect()
  
  map_to_snomed <- tbl(cons$starr_omop_cdm5_deid_updated, "concept_relationship") %>% 
    select(concept_id_1,
           concept_id_2,
           relationship_id) %>% 
    filter(tolower(relationship_id) == "maps to") %>% 
    filter(concept_id_1 %in% !!oud_icd_codes$concept_id) %>% 
    distinct(concept_id_2) %>% 
    # show_query() %>% 
    collect() %>% 
    rename(snomed_concept_id = concept_id_2)
  
  oud_diagnosis_codes <- tbl(cons$starr_omop_cdm5_deid_updated, "concept") %>% 
    select(concept_id,
           concept_name,
           vocabulary_id,
           concept_code,
           domain_id) %>% 
    filter(concept_id %in% !!map_to_snomed$snomed_concept_id) %>% 
    collect()
  
  return(oud_diagnosis_codes)
}

get_oud_drug_data <- function(cons, drugs) {
  
  oud_drug_data <- tbl(cons$starr_omop_cdm5_deid_updated, "concept") %>% 
    filter(tolower(concept_name) %like% drugs) %>% 
    select(drug_concept_id = concept_id,
           concept_name,
           concept_code,
           domain_id,
           vocabulary_id,
           concept_class_id) %>% 
    mutate(concept_name = tolower(concept_name)) %>% 
    collect()
  
  return(oud_drug_data)
}

get_oud_drug_era_data <- function(cons, oud_drug_data) {
  
  oud_drug_era_data <- tbl(cons$starr_omop_cdm5_deid_updated, "drug_era") %>% 
    rename_all(tolower) %>% 
    select(-trace_id,
           -unit_id,
           -load_table_id) %>% 
    filter(drug_concept_id %in% !!oud_drug_data$drug_concept_id) %>% 
    collect()
  
  return(oud_drug_era_data)
}

get_oud_drug_exposure_data <- function(cons, oud_drug_data, study_cutoff) {
  
  drug_exposure_data <- tbl(cons$starr_omop_cdm5_deid_updated, "drug_exposure") %>% 
    rename_all(tolower) %>% 
    filter(drug_concept_id %in% !!oud_drug_data$drug_concept_id) %>% 
    select(drug_exposure_id,
           person_id,
           drug_concept_id,
           drug_exposure_start_date,
           drug_exposure_end_date,
           stop_reason,
           refills,
           quantity,
           provider_id,
           visit_occurrence_id) %>% #visit_detail_id, days_supply returned all NA,
    collect() %>% 
    filter(drug_exposure_start_date <= study_cutoff$date) %>% 
    mutate(drug_exposure_end_date = if_else(drug_exposure_end_date >= study_cutoff$date,
                                            study_cutoff$date,
                                            drug_exposure_end_date))
  
  oud_drug_exposure_data <- drug_exposure_data %>% 
    left_join(oud_drug_data %>% 
                select(drug_concept_id, 
                       concept_name), by = c("drug_concept_id")) %>% 
    select(person_id,
           concept_name,
           drug_concept_id,
           everything()) %>% 
    arrange(person_id,
            concept_name,
            drug_exposure_end_date)
  
  return(oud_drug_exposure_data)
}

create_drug_era_table <- function(oud_drug_exposure_data, min_gap) {
  
  #' first need to remove overlapping dates
  remove_overlapping_dates <- oud_drug_exposure_data %>%
    mutate(exposure_length_days = as.integer(difftime(drug_exposure_end_date, drug_exposure_start_date, units = "days"))) %>%
    filter(exposure_length_days > 1) %>% 
    filter(!(stop_reason == "Patient Discharge")) %>%
    select(person_id,
           drug_concept_id,
           drug_exposure_start_date,
           drug_exposure_end_date,
           exposure_length_days) %>% 
    # filter(person_id == 29944554) %>%
    # filter(person_id == 29935645) %>% 
    # group_by(person_id, drug_concept_id) %>%
    group_by(person_id) %>%
    arrange(drug_exposure_start_date) %>% 
    mutate(indx = c(0, cumsum(as.numeric(lead(drug_exposure_start_date)) >
                                cummax(as.numeric(drug_exposure_end_date)))[-n()])) %>%
    # group_by(person_id, drug_concept_id, indx) %>%
    group_by(person_id, indx) %>%
    summarise(drug_exposure_start_date = first(drug_exposure_start_date), drug_exposure_end_date = last(drug_exposure_end_date)) #%>% 
  # view()
  
  #' create drug era table based on size of min_gap
  custom_oud_drug_era_data <- remove_overlapping_dates %>% 
    mutate(medic_period = cumsum(drug_exposure_start_date > lag(drug_exposure_end_date, default = drug_exposure_start_date[1]) + min_gap)) %>%
    # group_by(person_id, drug_concept_id, medic_period) %>%
    group_by(person_id, medic_period) %>%
    summarise(drug_exposure_start_date = first(drug_exposure_start_date), drug_exposure_end_date = last(drug_exposure_end_date)) %>% 
    ungroup() %>% 
    rename(drug_era_start_date = drug_exposure_start_date,
           drug_era_end_date = drug_exposure_end_date) %>% 
    select(-medic_period)
  
  return(custom_oud_drug_era_data)
}

link_provider_and_visit_occurrence_data <- function(cons, mat_patient_thresholds) {
  
  provider_info <- tbl(cons$starr_omop_cdm5_deid_updated, "provider") %>% 
    filter(provider_id %in% !!mat_patient_thresholds$provider_id) %>% 
    select(provider_id,
           provider_name,
           specialty_concept_id) %>% 
    collect()
  
  provider_specialty_info <- tbl(cons$starr_omop_cdm5_deid_updated, "concept") %>% 
    filter(concept_id %in% !!provider_info$specialty_concept_id) %>% 
    select(specialty_concept_id = concept_id,
           provider_specialty = concept_name) %>% 
    collect()
  
  mat_provider_linked <- mat_patient_thresholds %>% 
    left_join(provider_info, by = c("provider_id")) %>% 
    left_join(provider_specialty_info, by = c("specialty_concept_id")) %>% 
    select(-provider_id,
           -specialty_concept_id)
  
  visit_care_sites <- tbl(cons$starr_omop_cdm5_deid_updated, "visit_occurrence") %>% 
    select(care_site_id,
           visit_occurrence_id) %>% 
    filter(visit_occurrence_id %in% !!mat_provider_linked$visit_occurrence_id) %>% 
    collect()
  
  visit_care_site_names <- tbl(cons$starr_omop_cdm5_deid_updated, "care_site") %>% 
    filter(care_site_id %in% !!visit_care_sites$care_site_id) %>% 
    select(care_site_id,
           care_site_name) %>% 
    collect()
  
  care_site_info <- visit_care_sites %>% 
    left_join(visit_care_site_names, by = c("care_site_id")) %>% 
    mutate(care_site_name = tolower(care_site_name))
  
  #first
  visit_occurrence_concept_id <- tbl(cons$starr_omop_cdm5_deid_updated, "visit_occurrence") %>% 
    filter(visit_occurrence_id %in% !!mat_provider_linked$visit_occurrence_id) %>% 
    select(visit_occurrence_id,
           concept_id = visit_concept_id) %>% 
    collect()
  #get visit concept id
  visit_occurrence_info <- tbl(cons$starr_omop_cdm5_deid_updated, "concept") %>% 
    filter(concept_id %in% !!visit_occurrence_concept_id$concept_id) %>% 
    select(concept_id,
           concept_name) %>% 
    collect() %>% 
    left_join(visit_occurrence_concept_id, by = c("concept_id")) %>% 
    rename(visit_name = concept_name) %>% 
    select(-concept_id)
  
  mat_provider_and_visit_info <- mat_provider_linked %>% 
    left_join(visit_occurrence_info, by = c("visit_occurrence_id")) %>% 
    left_join(visit_care_sites, by = c("visit_occurrence_id")) %>% 
    left_join(care_site_info, by = c("care_site_id", "visit_occurrence_id")) %>% 
    select(-visit_occurrence_id,
           -care_site_id) %>% 
    mutate_all(tolower) #%>% 
  # filter_at(vars(starts_with("care_site_name")), any_vars(grepl("^addiction", .)))
  # filter(provider_specialty == "psychiatry")
  
  return(mat_provider_and_visit_info)
}

get_provider_and_visit_stats <- function(mat_provider_and_visit_info) {
  
  care_site_data <- count(mat_provider_and_visit_info, care_site_name) %>% 
    arrange(desc(n))
  provider_specialty_data <- count(mat_provider_and_visit_info, provider_specialty) %>% 
    arrange(desc(n))
  
  mat_provider_visit_stats <- list("care_site_data" = care_site_data,
                                   "provider_specialty_data" = provider_specialty_data)
  
  return(mat_provider_visit_stats)
}

filter_patients_with_diagnosis <- function(cons, oud_drug_era_data, oud_diagnosis_codes) {
  
  diagnosis_person_ids <- tbl(cons$starr_omop_cdm5_deid_updated, "condition_occurrence") %>% 
    rename_all(tolower) %>% 
    filter(condition_concept_id %in% !!oud_diagnosis_codes$concept_id) %>% 
    select(person_id,
           condition_concept_id,
           condition_occurrence_id,
           condition_start_date) %>% 
    collect()
  
  oud_mat_patients <- oud_drug_era_data %>%
    filter(as.integer(person_id) %in% diagnosis_person_ids$person_id)
  
  return(oud_mat_patients)
}

get_drug_thresholds <- function(custom_oud_drug_era_data, study_cutoff, label_threshold, remove_doubly_labeled_patients, keep_first_event, keep_all_events, min_gap) {
  
  remove_unknown_patients <- custom_oud_drug_era_data %>%
    filter(!drug_era_start_date >= (study_cutoff$date - label_threshold))
  
  #' create attrition and retention labels
  patient_labels <- remove_unknown_patients %>% 
    mutate(treatment_duration_days = as.integer(difftime(drug_era_end_date, drug_era_start_date, units = "days"))) %>% 
    mutate(threshold_label = ifelse(treatment_duration_days < label_threshold, "attrition", "retention")) %>% 
    arrange(person_id,
            drug_era_start_date) %>% 
    filter(!is.na(threshold_label))
  
  #' remove patients that have both attrition and retention labels
  doubly_labeled_and_non_doubly_labeled <- patient_labels %>%
    mutate(count = 1) %>%
    pivot_wider(id_cols = person_id, names_from = threshold_label, values_from = count, values_fn = sum, values_fill = 0) %>%
    mutate(both_labels = ifelse(retention > 0 & attrition > 0, T, F)) 
  
  if (remove_doubly_labeled_patients) {
    
    print("Removing patients with both labels")
    non_doubly_labeled <- doubly_labeled_and_non_doubly_labeled %>%
      filter(!both_labels)
    
    #' filter out patients with both an attrition and retention label
    oud_mat_thresholds <- patient_labels %>% 
      filter(person_id %in% non_doubly_labeled$person_id) %>%
      mutate(uniq_id = row_number()) %>% 
      select(uniq_id,
             everything())
    
  } else if (keep_first_event) {
    
    print("Keeping only first event for patients with both labels")
    doubly_labeled <- doubly_labeled_and_non_doubly_labeled %>% 
      filter(both_labels)
    
    # doubly_labeled %>% 
    #   filter(person_id == 30067683)
    # patient_labels %>% 
    #   filter(person_id == 30067683) %>% 
    #   arrange(drug_era_start_date)
    
    latest_doubly_label <- patient_labels %>% 
      filter(person_id %in% doubly_labeled$person_id) %>% 
      group_by(person_id) %>% 
      filter(drug_era_start_date == min(drug_era_start_date)) %>% 
      ungroup() #%>% 
    # filter(person_id == 30067683)
    
    non_doubly_labeled <- doubly_labeled_and_non_doubly_labeled %>%
      filter(!both_labels)
    
    #' filter out patients with both an attrition and retention label
    oud_mat_thresholds <- patient_labels %>% 
      filter(person_id %in% non_doubly_labeled$person_id) %>%
      bind_rows(latest_doubly_label) %>% 
      mutate(uniq_id = row_number()) %>% 
      select(uniq_id,
             everything())
    
  } else if (keep_all_events) {
    
    print("Keeping all events")
    oud_mat_thresholds <- patient_labels %>% 
      mutate(uniq_id = row_number()) %>% 
      select(uniq_id,
             everything())
    
  }
  
  return(oud_mat_thresholds)
}

#' add_drug_exposure_id not completed
add_drug_exposure_id <- function(c_oud_mat_thresholds, oud_drug_exposure_data) {
  
  drug_exposure_id_data <- oud_drug_exposure_data %>% 
    rename(drug_era_start_date = drug_exposure_start_date,
           drug_era_end_date = drug_exposure_end_date) %>% 
    distinct(person_id, drug_concept_id, drug_exposure_id, drug_era_start_date)
  
  
  # duplicating rows because some rows in c_oud_mat_thresholds have multiple drug_exposure_ids
  c_oud_mat_thresholds %>% 
    left_join(drug_exposure_id_data, by = c("person_id", "drug_concept_id", "drug_era_start_date"))
  
  return()
}

additional_thresholds <- function(oud_mat_patients) {
  
  oud_mat_additional_thresholds <- oud_mat_patients %>% 
    mutate(treatment_duration_days = as.integer(difftime(drug_era_end_date, drug_era_start_date, units = "days"))) %>% 
    mutate(threshold_label = ifelse(treatment_duration_days <= 30.5,
                                    "within 1 month",
                                    ifelse(treatment_duration_days > 30.5 & treatment_duration_days <= 30.5 * 3,
                                           "within 1-3 months",
                                           ifelse(treatment_duration_days > 30.5 * 3 & treatment_duration_days <= 30.5 * 6,
                                                  "within 3-6 months",
                                                  ifelse(treatment_duration_days > 30.5 * 6 & treatment_duration_days <= 30.5 * 12,
                                                         "within 6-12 months",
                                                         "more than 12 months")))))
  
  return(oud_mat_additional_thresholds)
}

get_total_patient_events_plot <- function(c_oud_mat_thresholds) {
  
  c_oud_mat_thresholds %>% 
    group_by(person_id) %>% 
    mutate(event_counts = 1) %>% 
    summarise(event_counts = n()) %>% 
    arrange(desc(event_counts)) %>% 
    ggplot(aes(x = event_counts)) + 
    geom_histogram(color = "black", 
                   fill = "white",
                   binwidth = 1) +
    geom_vline(aes(xintercept = mean(event_counts)), 
               color = "blue", 
               linetype="dashed") +
    labs(title = "Total patient events", 
         x = "Count", 
         y = "Total Events")
}

get_person_info <- function(c_oud_mat_thresholds) {
  
  person_info <- tbl(cons$starr_omop_cdm5_deid_updated, "person") %>% 
    rename_all(tolower) %>% 
    filter(person_id %in% !!c_oud_mat_thresholds$person_id) %>% 
    select(person_id,
           year_of_birth,
           month_of_birth,
           day_of_birth,
           race_concept_id,
           ethnicity_concept_id,
           gender_concept_id) %>% 
    collect() %>% 
    unite(birth_date, c(year_of_birth, month_of_birth, day_of_birth), sep = "-") %>% 
    mutate(birth_date = as.Date(ymd(birth_date)))
  
  oud_mat_person_info <- c_oud_mat_thresholds %>% 
    left_join(person_info, by = c("person_id")) %>% 
    mutate(age_at_start = as.integer(difftime(drug_era_start_date, birth_date, units = "weeks")) / 52.1429) %>% 
    select(uniq_id,
           race_concept_id,
           ethnicity_concept_id,
           gender_concept_id,
           age_at_start)
  
  return(oud_mat_person_info)
}

get_diagnosis_data <- function(c_oud_mat_thresholds, observation_window, oud_diagnosis_codes) {
  
  #' collect condition_concept_id for each patient
  diagnosis_data <- tbl(cons$starr_omop_cdm5_deid_updated, "condition_occurrence") %>% 
    rename_all(tolower) %>% 
    filter(person_id %in% !!c_oud_mat_thresholds$person_id,
           !condition_concept_id %in% !!oud_diagnosis_codes$concept_id) %>% 
    select(person_id,
           concept_id = condition_concept_id,
           observation_date = condition_start_date) %>% 
    group_by(person_id, concept_id) %>% 
    distinct(observation_date) %>%
    ungroup() %>% 
    collect()
  
  #' join condition_concept_id data on patient_id
  mat_patient_diagnosis_data <- c_oud_mat_thresholds %>% 
    left_join(diagnosis_data, by = c("person_id")) %>% 
    filter((observation_date >= drug_era_start_date - observation_window) & 
             (observation_date <= drug_era_start_date)) %>% 
    arrange(uniq_id, concept_id, observation_date)
  
  return(mat_patient_diagnosis_data)
}

get_procedure_data <- function(c_oud_mat_thresholds, observation_window) {
  
  #' collect concept_id for each patient
  procedure_data <- tbl(cons$starr_omop_cdm5_deid_updated, "procedure_occurrence") %>% 
    rename_all(tolower) %>% 
    filter(person_id %in% !!c_oud_mat_thresholds$person_id) %>% 
    select(person_id,
           concept_id = procedure_concept_id,
           observation_date = procedure_date) %>% 
    group_by(person_id, concept_id) %>% 
    distinct(observation_date) %>%
    ungroup() %>% 
    collect()
  
  #' join concept_id data on patient_id
  mat_patient_procedure_data <- c_oud_mat_thresholds %>% 
    left_join(procedure_data, by = c("person_id")) %>% 
    filter((observation_date >= drug_era_start_date - observation_window) & 
             (observation_date <= drug_era_start_date)) %>%  
    arrange(uniq_id, concept_id, observation_date)
  
  return(mat_patient_procedure_data)
}

get_drug_exposure_data <- function(c_oud_mat_thresholds, observation_window, oud_drug_data) {
  
  #' collect concept_id for each patient
  drug_data <- tbl(cons$starr_omop_cdm5_deid_updated, "drug_exposure") %>% 
    rename_all(tolower) %>% 
    filter(person_id %in% !!c_oud_mat_thresholds$person_id,
           !drug_concept_id %in% !!oud_drug_data$drug_concept_id) %>% 
    select(person_id,
           concept_id = drug_concept_id,
           observation_date = drug_exposure_start_date) %>% 
    group_by(person_id, concept_id) %>% 
    distinct(observation_date) %>%
    ungroup() %>% 
    collect()
  
  #' join concept_id data on patient_id
  mat_patient_drug_data <- c_oud_mat_thresholds %>% 
    left_join(drug_data, by = c("person_id")) %>% 
    filter((observation_date >= drug_era_start_date - observation_window) & 
             (observation_date <= drug_era_start_date)) %>%  
    arrange(uniq_id, concept_id, observation_date)
  
  return(mat_patient_drug_data)
}

get_nlp_note_data <- function(c_oud_mat_thresholds, observation_window) {
  
  #' collect note data for each patient
  note_data <- tbl(cons$starr_omop_cdm5_deid_updated, "note") %>% 
    rename_all(tolower) %>% 
    filter(person_id %in% !!c_oud_mat_thresholds$person_id) %>% 
    select(person_id,
           note_id,
           observation_date = note_date) %>% 
    group_by(person_id, observation_date) %>% 
    distinct(note_id) %>%
    ungroup() %>% 
    collect()
  
  #' join note data on patient_id
  mat_patient_note_data <- c_oud_mat_thresholds %>% 
    left_join(note_data, by = c("person_id")) %>% 
    filter((observation_date >= drug_era_start_date - observation_window) & 
             (observation_date <= drug_era_start_date)) %>% 
    arrange(uniq_id, note_id, observation_date)
  
  
  #' collect note_nlp data for each patient
  note_nlp_data <- tbl(cons$starr_omop_cdm5_deid_updated, "note_nlp") %>%
    rename_all(tolower) %>%
    select(note_id,
           concept_id = note_nlp_concept_id,
           term_exists) %>% 
    filter(note_id %in% !!mat_patient_note_data$note_id,
           term_exists == "Y") %>%
    select(-term_exists) %>% 
    distinct(note_id, concept_id) %>%
    collect()
  
  #' join condition_concept_id data on patient_id
  mat_patient_nlp_note_data <- mat_patient_note_data %>% 
    left_join(note_nlp_data, by = c("note_id")) %>% 
    select(-note_id) %>% 
    arrange(uniq_id, concept_id, observation_date)
  
  return(mat_patient_nlp_note_data)
}

get_reduced_note_nlp <- function(c_mat_patient_nlp_note_data) {
  
  feature_set <- c_mat_patient_nlp_note_data %>% 
    distinct(uniq_id, person_id, concept_id, .keep_all = TRUE)
  
  nlp_retention_patients <- feature_set %>% 
    filter(threshold_label == "retention") %>% 
    filter(!concept_id == 0)
  
  nlp_attrition_patients <- feature_set %>% 
    filter(threshold_label == "attrition") %>% 
    filter(!concept_id == 0)
  
  #' separating into "retention" and "attrition" count tables
  retention_data <- nlp_retention_patients %>% 
    count(concept_id) %>% 
    rename(n_retention = n)
  
  attrition_data <- nlp_attrition_patients %>% 
    count(concept_id) %>% 
    rename(n_attrition = n)
  
  #' calculating diagnosis stats
  feature_stats <- retention_data %>% 
    left_join(attrition_data, by = c("concept_id")) %>% 
    mutate_at(vars(starts_with("n_")), .funs = list(~ifelse(is.na(.x), 0, .x))) %>% 
    mutate(percent_retention = n_retention / length(unique(nlp_retention_patients$uniq_id)),
           percent_attrition = n_attrition / length(unique(nlp_attrition_patients$uniq_id))) %>% 
    filter(percent_retention >= 0.05 & percent_attrition >= 0.05) %>% 
    mutate(attrition_retention_ratio = percent_attrition / percent_retention)
  
  nlp_feature_names <- tbl(cons$starr_omop_cdm5_deid_updated, "concept") %>% 
    filter(concept_id %in% !!feature_stats$concept_id) %>% 
    select(concept_id,
           concept_name) %>% 
    collect() %>% 
    left_join(feature_stats, by = c("concept_id")) %>% 
    arrange(desc(attrition_retention_ratio)) %>% 
    head(round(nrow(feature_stats)*.05))
  
  #need to select correct columns
  c_mat_patient_nlp_note_data_reduced <- feature_set %>% 
    filter(concept_id %in% nlp_feature_names$concept_id)
  
  return(c_mat_patient_nlp_note_data_reduced)
}

generate_feature_matrix <- function(all_feature_data) {
  
  feature_list <- all_feature_data #%>% 
  # select(-feature_id)
  
  # concept_names <- tbl(cons$starr_omop_cdm5_deid_updated, "concept") %>% 
  #   select(concept_id,
  #          concept_name) %>% 
  #   filter(concept_id %in% !!unique(feature_list$concept_id)) %>% 
  #   collect()
  
  
  # named_concept_table <- feature_list %>% 
  #   left_join(concept_names, by = c("concept_id")) %>% 
  #   select(-concept_id) %>% 
  #   mutate(concept_name = tolower(gsub(" ", "_", concept_name))) %>% 
  #   # mutate(concept_name = gsub("\\?|:|\\[|\\]|,|\\%|'|-|/|\\(|\\)", "", concept_name))
  #   mutate(concept_name = gsub("[^_[:^punct:]]|_+\\b|\\b_+", "", concept_name, perl = TRUE)) %>% 
  #   mutate(concept_name = stri_trans_general(str = concept_name, id = "Latin-ASCII")) #%>% 
  #   # mutate(concept_name = gsub('[[:digit:]]+', "num", concept_name))
  
  c_mat_feature_matrix <- feature_list %>% 
    mutate(concept_id = sub("^", "id_", concept_id)) %>% 
    mutate(concept_id = paste0(concept_id, "_", feature_id)) %>% 
    select(-feature_id) %>% 
    mutate(count = 1) %>% 
    pivot_wider(id_cols = c(uniq_id, person_id, drug_concept_id, drug_era_start_date, 
                            drug_era_end_date, treatment_duration_days, threshold_label),
                names_from = concept_id,
                values_from = count, 
                values_fn = sum, 
                values_fill = 0)
  
  return(c_mat_feature_matrix)
}

data_processing_features <- function(all_feature_data) {
  
  features <- unique(all_feature_data$feature_id)
  selected_features <- map_dfr(features, 
                               function(feature_) {
                                 
                                 feature_set <- all_feature_data %>% 
                                   filter(feature_id == feature_)
                                 
                                 #' separating into "retention" and "attrition" count tables
                                 retention_data <- feature_set %>% 
                                   filter(threshold_label == "retention") %>% 
                                   count(concept_id) %>% 
                                   rename(n_retention = n)
                                 
                                 attrition_data <- feature_set %>% 
                                   filter(threshold_label == "attrition") %>% 
                                   count(concept_id) %>% 
                                   rename(n_attrition = n) 
                                 
                                 #' calculating diagnosis stats
                                 feature_stats <- retention_data %>% 
                                   left_join(attrition_data, by = c("concept_id")) %>% 
                                   mutate_at(vars(starts_with("n_")), .funs = list(~ifelse(is.na(.x), 0, .x))) %>% 
                                   mutate(percent_retention = n_retention / sum(retention_data$n_retention),
                                          percent_attrition = n_attrition / sum(attrition_data$n_attrition),
                                          attrition_retention_ratio = percent_attrition / percent_retention) %>% 
                                   arrange(desc(attrition_retention_ratio))
                                 
                                 filtered_features <- feature_stats %>% 
                                   filter(attrition_retention_ratio >= 2) %>%
                                   # filter((attrition_retention_ratio >= 2) | (attrition_retention_ratio <= 0.5)) %>%
                                   select(concept_id)
                                 
                                 return(tibble("filtered_features" = filtered_features$concept_id,
                                               "feature_id" = feature_))
                               })
  
  return(selected_features)
}

data_processing_on_note_nlp <- function(processed_features, c_mat_patient_nlp_note_data) {
  
  feature_set <- c_mat_patient_nlp_note_data
  
  #' separating into "retention" and "attrition" count tables
  retention_data <- feature_set %>% 
    filter(threshold_label == "retention") %>% 
    count(concept_id) %>% 
    rename(n_retention = n)
  
  attrition_data <- feature_set %>% 
    filter(threshold_label == "attrition") %>% 
    count(concept_id) %>% 
    rename(n_attrition = n) 
  
  #' calculating diagnosis stats
  feature_stats <- retention_data %>% 
    left_join(attrition_data, by = c("concept_id")) %>% 
    mutate_at(vars(starts_with("n_")), .funs = list(~ifelse(is.na(.x), 0, .x))) %>% 
    mutate(percent_retention = n_retention / sum(retention_data$n_retention),
           percent_attrition = n_attrition / sum(attrition_data$n_attrition),
           attrition_retention_ratio = percent_attrition / percent_retention) %>% 
    arrange(desc(attrition_retention_ratio))
  
  note_nlp_limit <- count(processed_features, feature_id) %>%
    pull(n) %>%
    mean(.) %>%
    round(., 0)
  # note_nlp_limit <- round(nrow(feature_stats) * 0.01, 0)
  
  filtered_features <- feature_stats %>% 
    filter(attrition_retention_ratio >= 2) %>%
    # filter((attrition_retention_ratio >= 2) | (attrition_retention_ratio <= 0.5)) %>%
    head(note_nlp_limit) %>% 
    select(filtered_features = concept_id) %>% 
    mutate(feature_id = "note_nlp")
  
  processed_features_w_note_nlp <- processed_features %>% 
    bind_rows(filtered_features)
  
  return(processed_features_w_note_nlp)
}

processed_feature_matrix <- function(all_feature_data, all_selected_features_format) {
  
  features <- unique(all_feature_data$feature_id)
  processed_feature_list <- map_dfr(features,
                                    function(feature_) {
                                      
                                      diagnosis_features <- all_selected_features_format %>% 
                                        filter(feature_id == feature_)
                                      
                                      processed_feature_list <- all_feature_data %>% 
                                        filter(feature_id == feature_,
                                               concept_id %in% diagnosis_features$filtered_features)
                                      
                                      return(processed_feature_list)
                                    }) %>% 
    arrange(uniq_id)
  
  missing_processed_c_mat_feature_matrix <- generate_feature_matrix(processed_feature_list)
  
  missing_uniq_ids <- setdiff(all_feature_data$uniq_id, missing_processed_c_mat_feature_matrix$uniq_id)
  missing_df <- tibble("uniq_id" = missing_uniq_ids) %>% 
    left_join(all_feature_data %>% 
                distinct(uniq_id, person_id, drug_concept_id, drug_era_start_date, drug_era_end_date, treatment_duration_days, threshold_label), by = c("uniq_id"))
  
  processed_c_mat_feature_matrix <- missing_processed_c_mat_feature_matrix %>% 
    bind_rows(missing_df) %>% 
    arrange(uniq_id)
  
  return(processed_c_mat_feature_matrix)
}

additional_diagnosis_calculation <- function(mat_patient_additional_diagnosis, oud_mat_person_info) {
  
  #' preventing duplication of mat_patient_additional_diagnosis data by removing
  #' duplicates in oud_mat_person_info
  patient_threshold_info <- oud_mat_person_info %>%
    distinct(person_id, threshold_label)
  
  #' joining threshold label to "additional diagnosis" table
  diagnosis_calculation <- mat_patient_additional_diagnosis %>%
    #   filter(person_id %in% patient_threshold_info$person_id) %>% # don't need this because no longer creating "patient_threshold_info" table
    left_join(patient_threshold_info, by = c("person_id"))
  
  #' separating into "retention" and "attrition" count tables
  retention_diagnosis <- diagnosis_calculation %>% 
    filter(threshold_label == "retention") %>% 
    count(concept_name) %>% 
    rename(n_retention = n)
  
  attrition_diagnosis <- diagnosis_calculation %>% 
    filter(threshold_label == "attrition") %>% 
    count(concept_name) %>% 
    rename(n_attrition = n) 
  
  #' calculating diagnosis stats
  diagnosis_stats <- retention_diagnosis %>% 
    left_join(attrition_diagnosis, by = c("concept_name")) %>% 
    mutate(percent_retention = n_retention / sum(retention_diagnosis$n_retention),
           percent_attrition = n_attrition / sum(attrition_diagnosis$n_attrition),
           attrition_retention_ratio = percent_attrition / percent_retention) %>% 
    arrange(desc(attrition_retention_ratio))
  
  return(diagnosis_stats)
}

get_demographic_data <- function(c_oud_mat_person_info) {
  
  #' load in "concept" table and filter for race and gender concept_ids
  person_info_concept_data <- tbl(cons$starr_omop_cdm5_deid_updated, "concept") %>% 
    rename_all(tolower) %>% 
    select(concept_id,
           concept_name) %>% 
    filter(concept_id %in% !!c(c_oud_mat_person_info$race_concept_id, 
                               c_oud_mat_person_info$gender_concept_id,
                               c_oud_mat_person_info$ethnicity_concept_id)) %>% 
    collect()
  
  #' get race and gender concept names
  race_info <- c_oud_mat_person_info %>% 
    rename(concept_id = race_concept_id) %>% 
    left_join(person_info_concept_data, by = c("concept_id")) %>% 
    rename(race = concept_name) %>% 
    select(uniq_id,
           race)
  
  gender_info <- c_oud_mat_person_info %>% 
    rename(concept_id = gender_concept_id) %>% 
    left_join(person_info_concept_data, by = c("concept_id")) %>% 
    rename(sex = concept_name) %>% 
    transmute(uniq_id,
              sex = tolower(sex))
  
  ethnicity_info <- c_oud_mat_person_info %>% 
    rename(concept_id = ethnicity_concept_id) %>% 
    left_join(person_info_concept_data, by = c("concept_id")) %>% 
    rename(ethnicity = concept_name) %>% 
    transmute(uniq_id,
              ethnicity)
  
  #' combine data
  patient_demographics <- race_info %>% 
    left_join(gender_info, by = c("uniq_id")) %>% 
    left_join(ethnicity_info, by = c("uniq_id")) %>% 
    left_join(c_oud_mat_person_info %>% 
                select(uniq_id, age_at_start), by = c("uniq_id")) %>% 
    mutate(race_count = 1,
           sex_count = 1,
           ethnicity_count = 1) %>% 
    spread(race, race_count, fill = 0) %>% 
    spread(sex, sex_count, fill = 0) %>% 
    spread(ethnicity, ethnicity_count, fill = 0) %>% 
    rename_all(function(col_name) tolower(gsub(" ", "_", col_name))) %>% 
    select(-no_matching_concept)
  
  return(patient_demographics)
}

processed_feature_matrix_new <- function(all_feature_data) {
  
  feature_ids <- unique(all_feature_data$feature_id)
  
  all_selected_features <- map_dfr(feature_ids, 
                                   function(feature_ids_) {
                                     
                                     print(glue("Selecting {feature_ids_} features"))
                                     feature_matrix <- all_feature_data %>% 
                                       filter(feature_id == feature_ids_) %>% 
                                       distinct(uniq_id, concept_id, .keep_all = TRUE) %>% 
                                       mutate(concept_id = sub("^", "id_", concept_id)) %>% 
                                       mutate(count = 1) %>% 
                                       pivot_wider(id_cols = c(uniq_id, threshold_label), 
                                                   names_from = concept_id,
                                                   values_from = count,
                                                   values_fill = 0) %>% 
                                       select(-uniq_id)
                                     
                                     filtered_features <- feature_matrix %>% 
                                       tbl_summary(by = threshold_label,
                                                   missing = "no") %>% 
                                       add_p()
                                     
                                     selected_variables <- filtered_features$meta_data %>% 
                                       filter(p.value <= 0.05) %>% 
                                       select(filtered_features = variable) %>% 
                                       mutate(feature_id = feature_ids_)
                                     
                                     return(selected_variables)
                                   })
  
  return(all_selected_features) 
}

if (F) {
  
  # # run this and enter '0' if you need to authenticate a new Google account
  # googlesheets4::gs4_deauth()
  # googlesheets4::gs4_auth()
  
  update_date <- "2022_08_10"
  study_cutoff <- tibble(date = as.Date("2023-01-31"))
  # update_date <- "2022_09_05"
  # update_date <- "2022_10_02"
  # update_date <- "2022_12_03"
  print(glue("Getting all cons for billing @ {gcloud_billing}"))
  cons <- get_bq_cons(update_date, gcloud_billing = gcloud_billing)
  
  print(glue("Getting OUD SNOMED codes"))
  oud_diagnosis_codes <- get_oud_diagnosis_codes(cons)
  
  drugs <- c("%buprenorphine%naloxone%")
  print(glue("Getting drug concept IDs for {length(drugs)} drugs"))
  oud_drug_data <- get_oud_drug_data(cons, drugs)
  
  print(glue("Getting patient drug exposure for {nrow(oud_drug_data)} drugs concept IDs"))
  oud_drug_exposure_data <- get_oud_drug_exposure_data(cons, oud_drug_data, study_cutoff)
  
  print("Create custom drug era table")
  min_gap <- 30
  custom_oud_drug_era_data <- create_drug_era_table(oud_drug_exposure_data, min_gap) %>% 
    mutate(drug_concept_id = "bup-nal concept id")
  
  print(glue("Creating threshold labels"))
  label_threshold = 180
  remove_doubly_labeled_patients = F
  keep_first_event = T
  keep_all_events = T
  c_oud_mat_thresholds <- get_drug_thresholds(custom_oud_drug_era_data, study_cutoff, label_threshold, remove_doubly_labeled_patients, keep_first_event, keep_all_events, min_gap)
  total_patient_events_plot <- get_total_patient_events_plot(c_oud_mat_thresholds)
  
  count(c_oud_mat_thresholds, threshold_label)
  
  #' not completed due to joining duplication issue
  # print(glue("Add drug_exposure_id to table"))
  # add_drug_exposure_id(c_oud_mat_thresholds, oud_drug_exposure_data)
  
  observation_window = 90
  print(glue("Getting patient demographic data"))
  c_oud_mat_person_info <- get_person_info(c_oud_mat_thresholds)
  c_patient_demographics <- get_demographic_data(c_oud_mat_person_info)
  print(glue("Getting patient diagnosis data"))
  c_mat_patient_diagnosis_data <- get_diagnosis_data(c_oud_mat_thresholds, observation_window, oud_diagnosis_codes)
  print(glue("Getting patient procedure data"))
  c_mat_patient_procedure_data <- get_procedure_data(c_oud_mat_thresholds, observation_window)
  print(glue("Getting patient drug exposure data"))
  c_mat_patient_drug_data <- get_drug_exposure_data(c_oud_mat_thresholds, observation_window, oud_drug_data)
  print(glue("Getting patient nlp_note data"))
  c_mat_patient_nlp_note_data <- get_nlp_note_data(c_oud_mat_thresholds, observation_window)
  c_mat_patient_nlp_note_data_reduced <- get_reduced_note_nlp(c_mat_patient_nlp_note_data)
  
  print(glue("Generate feature matrix"))
  all_feature_data <- c_mat_patient_diagnosis_data %>% 
    mutate(feature_id = "diagnosis") %>% 
    bind_rows(c_mat_patient_procedure_data %>% 
                mutate(feature_id = "procedure")) %>% 
    bind_rows(c_mat_patient_drug_data %>% 
                mutate(feature_id = "drug")) %>% 
    bind_rows(c_mat_patient_nlp_note_data_reduced %>%
                mutate(feature_id = "note_nlp")) %>%
    filter(!concept_id == 0)
  
  all_selected_features <- processed_feature_matrix_new(all_feature_data)
  all_selected_features_format <- all_selected_features %>% 
    # rename(filtered_features = variable) %>% 
    mutate(filtered_features = gsub("id_", "", filtered_features))
  new_processed_feature_matrix <- processed_feature_matrix(all_feature_data, all_selected_features_format) %>% 
    mutate_at(vars(starts_with("id_")), .funs = list(~ifelse(.x >= 1, 1, .x))) %>% 
    mutate_at(vars(starts_with("id_")), .funs = list(~ifelse(is.na(.x), 0, .x)))
  
  processed_feature_matrix_w_demographics <- new_processed_feature_matrix %>% 
    left_join(c_patient_demographics, by = c("uniq_id"))
  
  #' additional stats start
  # c_oud_mat_additional_thresholds <- additional_thresholds(custom_oud_drug_era_data)
  # 
  # print(glue("Getting patient demographic info"))
  # c_oud_mat_person_info <- get_person_info(c_oud_mat_thresholds)
  # 
  # print(glue("Getting patient additional diagnosis"))
  # c_mat_patient_additional_diagnosis <- get_diagnosis_data(c_oud_mat_person_info, observation_window)
  # 
  # print(glue("Getting diagnosis stats table"))
  # c_diagnosis_stats <- additional_diagnosis_calculation(c_mat_patient_additional_diagnosis, c_oud_mat_person_info)
  # 
  # print(glue("Getting patient demographic data"))
  # c_patient_demographics <- get_demographic_data(c_oud_mat_person_info) %>% 
  #   map(~.x %>%
  #         mutate(attrition_retention_ratio = ifelse(attrition_retention_ratio == Inf, "Inf", attrition_retention_ratio)))
  #' additional stats end
  
  # sheet_link = "https://docs.google.com/spreadsheets/d/1ow-sZR9ejKmtsL5Rnu0SxtO7vMozdILiArCMNNAOoys/edit#gid=0"
  # sheet_append(sheet_link, c_patient_demographics$sex, sheet = "sex")
  # sheet_append(sheet_link, c_patient_demographics$race, sheet = "race")
  
  print(glue("Prep data for ML"))
  abstracted_data <- processed_feature_matrix_w_demographics %>% 
    rename(outcome = threshold_label) %>% 
    mutate(outcome = as.double(ifelse(outcome == "attrition", 1, 0)),
           data_created_at = Sys.Date()) %>%  
    select(uniq_id, 
           person_id,
           drug_concept_id,
           drug_era_start_date,
           drug_era_end_date,
           treatment_duration_days,
           outcome,
           data_created_at,
           everything())
  
  print("Upload data to BigQuery")
  generate_date = Sys.Date()
  note_nlp_present = "note_nlp"
  # version_df = "v4_" # patients with both labels --> only keep first event
  # version_df = "v5_" # keep all patient events
  version_df = "v6_" # merging all drug concept IDs for suboxone
  bq_table_name = paste0("abstracted_data_", version_df, update_date, "_label_threshold_", label_threshold, "_obs_window_", observation_window, "_", note_nlp_present, "_updated_", generate_date)
  # bq_table_name = paste0("abstracted_data_", version_df, update_date, "_label_threshold_", label_threshold, "_obs_window_", observation_window, "_updated_", generate_date)
  bq_table_name
  upload_to_bigquery(table_id = bq_table_name, data_to_upload = abstracted_data)
  
  
}