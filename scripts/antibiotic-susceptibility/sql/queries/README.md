  Study Cohort
  
  1. Create Study Cohort: microbiology_cultures_cohort_query.sql
  
  2. Extract Demographic Features:microbiology_cultures_demographics.sql
  3. Extracting  Hospital department type (inpatient, outpatient, ER, ICU): microbiology_cultures_ward_info.sql
  4. Intermediate Tables :
     1. class_subtype_lookup to creates a table named class_subtype_lookup in BigQuery that contains antibiotics, their classes, and specific subtypes:prior_abx_class_subtype_lookup.sql
     2. Extracting medications  a patient having been treated with before specimen collection:time-to-event-augmented-queries/medication_exposure.sql
6. Extracting exposure to a class of antibiotics before specimen collection: time-to-event-augmented-queries/antibiotic_class_exposure.sql
7. Extracting exposure to a sub-class of antibiotics before specimen collection: time-to-event-augmented-queries/antibiotic_subtype_exposure.sql
8. Extracting comorbidities: time-to-event-augmented-queries/comorbidities.sql
9. Extracting patient's past resistance to specific antibiotics:time-to-event-augmented-queries/microbial_resistance.sql
10. Extracting patients  previous infection with a specific pathogen:time-to-event-augmented-queries/previous_infecting_organisms.sql
11. Extracting patient prior procedures: time-to-event-augmented-queries/prior_procedures.sql
12. Indicating whether the patient has been in a nursing home:time-to-event-augmented-queries/nursing_home_visits.sql
13. Extracting patients ADI scores: microbiology_cultures_adi_scores.sql

