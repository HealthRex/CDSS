-- Wrapper script to define all DB schema.
-- Note that the order in which schema are defined may be significant,
-- as some schema definitions reference previous schema.

-- CPOE Statistics
\i medinfo/db/definition/tables/clinical_item_category.sql
\i medinfo/db/definition/tables/clinical_item.sql
\i medinfo/db/definition/tables/patient_item.sql
\i medinfo/db/definition/tables/clinical_item_association.sql
\i medinfo/db/definition/tables/order_result_stat.sql
\i medinfo/db/definition/tables/data_cache.sql
\i medinfo/db/definition/tables/backup_link_patient_item.sql
\i medinfo/db/definition/tables/clinical_item_link.sql
\i medinfo/db/definition/tables/item_collection.sql
\i medinfo/db/definition/tables/collection_type.sql
\i medinfo/db/definition/tables/item_collection_item.sql
\i medinfo/db/definition/tables/patient_item_collection_link.sql

-- CPOE Simultation
\i medinfo/db/definition/tables/sim_user.sql
\i medinfo/db/definition/tables/sim_patient.sql
\i medinfo/db/definition/tables/sim_state.sql
\i medinfo/db/definition/tables/sim_patient_state.sql
\i medinfo/db/definition/tables/sim_state_transition.sql
\i medinfo/db/definition/tables/sim_note_type.sql
\i medinfo/db/definition/tables/sim_note.sql
\i medinfo/db/definition/tables/sim_result.sql
\i medinfo/db/definition/tables/sim_state_result.sql
\i medinfo/db/definition/tables/sim_order_result_map.sql
\i medinfo/db/definition/tables/sim_patient_order.sql

-- Opioid RX
\i medinfo/db/definition/tables/stride_mapped_meds.sql
\i medinfo/db/definition/tables/stride_order_med.sql
\i medinfo/db/definition/tables/stride_order_proc_drug_screen.sql
\i medinfo/db/definition/tables/stride_patient.sql
\i medinfo/db/definition/tables/stride_order_proc_referrals_n_consults.sql
\i medinfo/db/definition/tables/stride_pat_enc.sql
\i medinfo/db/definition/tables/stride_problem_list.sql
\i medinfo/db/definition/tables/stride_icd9_cm.sql
