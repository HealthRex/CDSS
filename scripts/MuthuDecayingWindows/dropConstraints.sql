ALTER TABLE patient_item drop constraint patient_item_pkey;
ALTER TABLE patient_item drop constraint patient_item_clinical_item_fkey;
drop index index_patient_item_clinical_item_id_date;

drop index index_patient_item_patient_id_date;
drop index index_patient_item_external_id;

drop index index_patient_item_encounter_id_date;


ALTER TABLE patient_item drop constraint patient_item_composite;