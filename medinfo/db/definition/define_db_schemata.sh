#!/bin/bash

# Wrapper shell function for creating single DB schema definitions.
# Handles whether tables exist or not.
# Note that function relies on schema definition file named {table_name}.sql.
function define_schema_if_undefined() {
  local DB_HOST=$1
  local DB_DSN=$2
  local DB_UID=$3
  local DB_TABLE=$4

  if [ "$(psql --host=$DB_HOST --dbname=$DB_DSN --username=$DB_UID -c '\d' | grep -w $DB_TABLE )" ]
  then
    echo "Initialized: $DB_TABLE"
  else
    echo "Initializing $DB_TABLE..."
    psql --quiet --host=$DB_HOST --dbname=$DB_DSN --username=postgres --file=medinfo/db/definition/tables/$DB_TABLE.sql
  fi
}

# Wrapper shell function for creating all DB schemata.
# Note that schemata must be defined in this order due to schema dependencies.
function define_schemata() {
  local DB_HOST=$1
  local DB_DSN=$2
  local DB_UID=$3

  ##### CPOE STATISTICS #####
  echo "Initializing CPOE statistics tables..."
  CPOE_STATS_TABLES=( \
    clinical_item_category \
    clinical_item \
    patient_item \
    clinical_item_association \
    order_result_stat \
    data_cache \
    backup_link_patient_item \
    clinical_item_link \
    item_collection \
    collection_type \
    item_collection_item \
    patient_item_collection_link \
  )
  for TABLE in ${CPOE_STATS_TABLES[*]}
  do
    define_schema_if_undefined $DB_HOST $DB_DSN $DB_UID $TABLE
  done

  ##### CPOE SIMULATION #####
  echo "Initializing CPOE simulation tables..."
  CPOE_SIM_TABLES=( \
    sim_user  \
    sim_patient \
    sim_state \
    sim_patient_state \
    sim_state_transition \
    sim_note_type \
    sim_note \
    sim_result \
    sim_state_result \
    sim_order_result_map \
    sim_patient_order \
  )
  for TABLE in ${CPOE_SIM_TABLES[*]}
  do
    define_schema_if_undefined $DB_HOST $DB_DSN $DB_UID $TABLE
  done

  ##### OPIOID RX #####
  echo "Initializing Opioid Rx tables..."
  OPIOID_RX_TABLES=(  \
    stride_mapped_meds \
    stride_order_med \
    stride_order_proc_drug_screen \
    stride_patient \
    stride_order_proc_referrals_n_consults \
    stride_pat_enc \
    stride_problem_list \
    stride_icd9_cm \
  )
  for TABLE in ${OPIOID_RX_TABLES[*]}
  do
    define_schema_if_undefined $DB_HOST $DB_DSN $DB_UID $TABLE
  done
}
