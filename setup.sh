#!/bin/bash

##### INSTALL LIBRARIES #####
echo "INSTALL LIBRARIES"

# Homebrew

# Python (https://www.python.org/)
if [ "whereis python" ]
then
  PYTHON_VERSION=$(python --version 2>&1)
  echo "Installed: $PYTHON_VERSION"
else
  echo "Installing python..."
fi

# PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:~/healthrex/CDSS"
printf 'export PYTHONPATH="${PYTHONPATH}:~/healthrex/CDSS"\n' >> ~/.bashrc

# psycopg2 (http://initd.org/psycopg/)
PSYCOPG2_VERSION="$(pip list --format=legacy | grep 'psycopg' | sed 's/[)(]//g' | awk '{print $2}')"
if [ -z "$PSYCOPG2_VERSION" ]
then
    echo -n "Installing psycopg2..."
    pip install --user psycopg2
else
    echo -n "Installed: psycopg2 "
    echo $PSYCOPG2_VERSION
fi

# NumPy (https://scipy.org/index.html)
# pip install --user numpy

# Pandas (http://pandas.pydata.org/)
PANDAS_VERSION="$(pip list --format=legacy | grep 'pandas' | sed 's/[)(]//g' | awk '{print $2}')"
if [ -z "$PANDAS_VERSION" ]
then
  echo -n "Installing pandas..."
  pip install --user pandas
  echo "OK"
else
  echo -n "Installed: pandas "
  echo $PANDAS_VERSION
fi


# SciKit Learn (http://scikit-learn.org/stable/)
# pip install --user sklearn

# gensim (https://radimrehurek.com/gensim/)
# pip install --user gensim

##### INITIALIZE DATABASE #####
echo ""
echo "INITIALIZE DATABASE"

## Production DB ##
echo "You will now configure the database environment."
echo "For each prompt, follow the answer recommended by the HealthRex Wiki."
echo ""
# Collect production DB parameters.
echo "First, configure the production database..."
read -p "Enter production DB hostname: " PROD_DB_HOST
read -p "Enter production DB database source name: " PROD_DB_DSN
read -p "Enter production DB user ID: " PROD_DB_UID
read -s -p "Enter production DB user password: " PROD_DB_PWD
echo

# Collect test DB parameters.
echo "Second, configure the test database, on which unittest will run..."
read -p "Enter test DB hostname: " TEST_DB_HOST
read -p "Enter test DB database source name: " TEST_DB_DSN
read -p "Enter test DB user ID: " TEST_DB_UID
read -s -p "Enter test DB user password: " TEST_DB_PWD
echo

# Write production DB parameters to local environment file.
echo "Writing database parameters to CDSS/LocalEnv.py, which is *not* source-controlled..."
# Instantiate LocalEnv.py. "> filename" creates filename if it does not exist,
# and clears it if it already does exist.
> ~/healthrex/CDSS/LocalEnv.py
echo '#!/usr/bin/python' >> ~/healthrex/CDSS/LocalEnv.py
echo '' >> ~/healthrex/CDSS/LocalEnv.py

# Write production DB parameters.
echo 'LOCAL_PROD_DB_PARAM = {}' >> ~/healthrex/CDSS/LocalEnv.py
echo -n 'LOCAL_PROD_DB_PARAM["HOST"] = ' >> ~/healthrex/CDSS/LocalEnv.py
echo $PROD_DB_HOST >> ~/healthrex/CDSS/LocalEnv.py
echo -n 'LOCAL_PROD_DB_PARAM["DSN"] = ' >> ~/healthrex/CDSS/LocalEnv.py
echo $PROD_DB_DSN >> ~/healthrex/CDSS/LocalEnv.py
echo -n 'LOCAL_PROD_DB_PARAM["UID"] = ' >> ~/healthrex/CDSS/LocalEnv.py
echo $PROD_DB_UID >> ~/healthrex/CDSS/LocalEnv.py
echo -n 'LOCAL_PROD_DB_PARAM["PWD"] = ' >> ~/healthrex/CDSS/LocalEnv.py
echo $PROD_DB_PWD >> ~/healthrex/CDSS/LocalEnv.py
echo '' >> ~/healthrex/CDSS/LocalEnv.py

# Write test DB parameters.
echo 'LOCAL_PROD_DB_PARAM = {}' >> ~/healthrex/CDSS/LocalEnv.py
echo -n 'LOCAL_TEST_DB_PARAM["HOST"] = ' >> ~/healthrex/CDSS/LocalEnv.py
echo $TEST_DB_HOST >> ~/healthrex/CDSS/LocalEnv.py
echo -n 'LOCAL_TEST_DB_PARAM["DSN"] = ' >> ~/healthrex/CDSS/LocalEnv.py
echo $TEST_DB_DSN >> ~/healthrex/CDSS/LocalEnv.py
echo -n 'LOCAL_TEST_DB_PARAM["UID"] = ' >> ~/healthrex/CDSS/LocalEnv.py
echo $TEST_DB_UID >> ~/healthrex/CDSS/LocalEnv.py
echo -n 'LOCAL_TEST_DB_PARAM["PWD"] = ' >> ~/healthrex/CDSS/LocalEnv.py
echo $TEST_DB_PWD >> ~/healthrex/CDSS/LocalEnv.py

# psql -f medinfo/db/definition/cpoeStats.sql -U <YourDBUsername> testdb

# Test DB

## CPOE Simulation Tables ##

# sim_user, sim_patient, sim_state, sim_patient_state, sim_state_transition,
# sim_note_type, sim_note, sim_result, sim_state_result, sim_order_result_map,
# sim_patient_order
# Definition: CDSS/medinfo/db/definition/cpoeSimultation.sql


#####

##### VERIFY TESTS PASS #####

# Print success state.
#python medinfo/db/test/TestDBUtil.py
