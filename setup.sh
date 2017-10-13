#!/bin/bash

##### INSTALL LIBRARIES #####

# Python

# pip

# PostgreSQL

# SciPy (https://scipy.org/index.html)
pip install --user numpy scipy matplotlib ipython jupyter pandas sympy nose

# Pandas (http://pandas.pydata.org/)
pip install --user pandas

# SciKit Learn (http://scikit-learn.org/stable/)
pip install --user sklearn

# gensim (https://radimrehurek.com/gensim/)
pip install --user gensim

##### INITIALIZE DATABASE #####

## Production and Test DBs ##
# Production DB

# Test DB

## CPOE Simulation Tables ##

# sim_user, sim_patient, sim_state, sim_patient_state, sim_state_transition,
# sim_note_type, sim_note, sim_result, sim_state_result, sim_order_result_map,
# sim_patient_order
# Definition: CDSS/medinfo/db/definition/cpoeSimultation.sql


##### VERIFY TESTS PASS #####
