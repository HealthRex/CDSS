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

  psql --quiet --host=$DB_HOST --dbname=$DB_DSN --username=postgres --file=medinfo/db/definition/define_db_schemata.sql
}
