#!/bin/bash

# See Wiki page for general starter notes,
#   as this script will NOT fully automate everything,
#   and will make mistakes if you have a different environment
#   (e.g., Windows, already installed PostgreSQL)
#   but gives you an idea of dependencies needed.
#   Better then to just step through this script by hand and see
#   what it's trying to do and replicate them as needed.
# https://github.com/HealthRex/CDSS/wiki/Dev-Environment-Setup
# 
# Walking through the DevWorkshop below can be very helpful for notes on setting things up as well.
# https://github.com/HealthRex/CDSS/blob/master/scripts/DevWorkshop/ReadMe.AWSDevEnvironment.txt
#

##### IDENTIFY PLATFORM #####
echo "IDENTIFY PLATFORM"

# OSX
if [ "$(uname)" = "Darwin" ]
then
    PLATFORM="OSX"

    # Brew (https://brew.sh/)
    if [ "$(command -v brew)" ]
    then
      BREW_VERSION=$(brew --version | sed -n 1p)
      echo "Installed: $BREW_VERSION"
    else
      echo "Installing brew..."
      /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    fi
fi

# Amazon
if [ "$(uname) | grep 'amzn')" ]
then
    PLATFORM="Amazon Linux"
fi

echo "Running setup.sh on $PLATFORM..."
echo ""

##### INSTALL LIBRARIES #####
echo "INSTALL LIBRARIES"

# Python (https://www.python.org/)
if [ "$(command -v python)" ]
then
  PYTHON_VERSION=$(python --version 2>&1)
  echo "Installed: $PYTHON_VERSION"
else
  echo "Installing python..."
fi

# PYTHONPATH environment variable, so Python knows where to find your code files
#   If running in a Unix based environment, .bash_profile are "startup scripts" that will run
#   whenever you start a terminal, so it will set this up for you everytime as a convenience.
export PYTHONPATH=${PYTHONPATH}:~/healthrex/CDSS
printf 'export PYTHONPATH=${PYTHONPATH}:~/healthrex/CDSS\n' >> ~/.bashrc
printf 'export PYTHONPATH=${PYTHONPATH}:~/healthrex/CDSS\n' >> ~/.bash_profile

# PostgreSQL (https://www.postgresql.org/)
# psql (http://postgresguide.com/utilities/psql.html)
# Open-source relational database platform (comparable to MySQL or commercial versions like Oracle)
#   Includes psql command line program to faciltate communicating with PostgreSQL database servers.
if [ "$(command -v postgres)" ]
then
    POSTGRES_BIN=$(command -v postgres)
    POSTGRES_VERSION=$(postgres --version 2>&1)
    echo "Installed: $POSTGRES_VERSION"
else
    echo "Installing postgresql-server..."
    if [ "$PLATFORM" = "Amazon Linux" ]
    then
      sudo yum install postgresql96-server
    fi
    if [ "$PLATFORM" = "OSX" ]
    then
      sudo brew install postgresql
    fi
fi
if [ "$(command -v psql)" ]
then
    PSQL_BIN=$(command -v psql)
    PSQL_VERSION=$(psql --version 2>&1)
    echo "Installed: $PSQL_VERSION"
else
    echo "Installing psql..."
    if [ "$PLATFORM" = "Amazon Linux" ]
    then
      sudo yum install postgresql96
    fi
    if [ "$PLATFORM" = "OSX" ]
    then
      sudo brew install postgresql
    fi
fi

# psycopg2 (http://initd.org/psycopg/)
# Python module, allowing Python to talk to PostgreSQL databases
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
# Python package commonly used for scientific work, facilitating matrix algebra and numerical computations
# pip install --user numpy

# Pandas (http://pandas.pydata.org/)
# Python package to organize data tables into dataframe objects, very similar to R, for convenient manipulation of 2D data
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
# Python package as a common platform for machine learning algorithms and evaluation
# pip install --user sklearn

# gensim (https://radimrehurek.com/gensim/)
# Python package for topic models (latent Dirichlet allocation)
GENSIM_VERSION="$(pip list --format=legacy | grep 'gensim' | sed 's/[)(]//g' | awk '{print $2}')"
if [ -z "$GENSIM_VERSION" ]
then
  echo -n "Installing gensim..."
  pip install --user gensim
  echo "OK"
else
  echo -n "Installed: gensim "
  echo $GENSIM_VERSION
fi

##### VERIFY TESTS PASS #####
# Try running unit tests in the main code repository to make sure things work
# Example below, trying to setup and connect to the database with basic functions
#   Requires your LocalEnv.py points to a TEST database name, 
#   and that the database login user provided has permissions to create (temporary test) databases
python medinfo/db/test/TestDBUtil.py
# More comprehensive test of everything that can be found in the main medinfo application code directory tree
python TestCDSS.py
