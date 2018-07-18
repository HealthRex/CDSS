#!/bin/bash

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

# PYTHONPATH
export PYTHONPATH=${PYTHONPATH}:~/healthrex/CDSS
printf 'export PYTHONPATH=${PYTHONPATH}:~/healthrex/CDSS\n' >> ~/.bashrc
printf 'export PYTHONPATH=${PYTHONPATH}:~/healthrex/CDSS\n' >> ~/.bash_profile

# PostgreSQL (https://www.postgresql.org/)
# psql (http://postgresguide.com/utilities/psql.html)
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

# Print success state.
python medinfo/db/test/TestDBUtil.py
