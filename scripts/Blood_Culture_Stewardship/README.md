The cohort for blood culutre prediction analysis has been generated and saved as som-nero-phi-jonc101.blood_culture_stewardship.cohort.
 
Table Descriptions:
 
Columns:
 
anon_id: Patient's anonymized ID.
pat_enc_csn_id_coded: Patient encounter code.
order_proc_id_coded: Blood culture order ID code.
blood_culture_order_datetime: UTC datetime of the culture order.
order_year: Year the order was taken (to be used later for splitting the dataset into training, validation, and test sets).
ed_arrival_datetime: UTC time of admission to the ED.
positive_blood_culture: Indicates if the blood culture is positive and not contaminated, excluding gram-positive rods and coagulase-negative staphylococci.
positive_blood_culture_in_week: Indicates if there are any consecutive positive orders for the patient within a week.
earliest_iv_antibiotic_datetime: UTC datetime of the earliest IV antibiotic administration (the list may need to be cleaned as it includes all IV medicines with an ABX class).
earliest_iv_antibiotic: Name of the earliest IV antibiotic administered.
min_, max_, avg_, and median_ of vital signs: Measured from 24 hours before to 2 hours after the culture order.
min_, max_, avg_, and median_ of labs: Measured from 24 hours before to 2 hours after the culture order.
