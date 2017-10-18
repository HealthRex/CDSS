#!/bin/bash

##### INSTALL LIBRARIES #####

# Homebrew

# Python (https://www.python.org/)
if [ "whereis python" ]
then
  PYTHON_VERSION ="$(python --version)"
  echo -n "Installed: "
  echo "$PYTHON_VERSION"
else
  echo "Installing python..."
fi

# PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:~/healthrex/CDSS"

# psycopg2 (http://initd.org/psycopg/)

# NumPy (https://scipy.org/index.html)
# pip install --user numpy

# Pandas (http://pandas.pydata.org/)
PANDAS_VERSION="$(pip list --format=legacy | grep 'pandas' | sed 's/[)(]//g' | awk '{print $2}')"
if [ -z "$PANDAS" ]
then
  echo -n "Installing pandas..."
  pip install --user pandas
  echo "OK"
else
  echo -n "Installed: pandas "
  echo "$PANDAS"
fi


# SciKit Learn (http://scikit-learn.org/stable/)
# pip install --user sklearn

# gensim (https://radimrehurek.com/gensim/)
# pip install --user gensim

##### INITIALIZE DATABASE #####

## Production and Test DBs ##
# Production DB
# read -p "Enter your PostgreSQL DB username: " psqluname
# echo $psqluname
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
