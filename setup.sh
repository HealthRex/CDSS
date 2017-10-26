#!/bin/bash

##### IDENTIFY PLATFORM #####
echo "IDENTIFY PLATFORM"

# OSX
if [ $(uname) = "Darwin" ]
then
    PLATFORM="OSX"
    echo "Running setup.sh on OSX..."

    # Brew (https://brew.sh/)
    if [ "$(command -v brew)" ]
    then
      BREW_VERSION=$(brew --version | sed -n 1p)
      echo "Installed: $BREW_VERSION"
    else
      echo "Installing brew..."
      /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    fi

    echo ""
fi

# Amazon
if [ "$(uname | grep 'amzn')" ]
then
    PLATFORM="Amazon Linux"
    echo "Running setup.sh on Amazon Linux..."
    echo ""
fi

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
    if [ PLATFORM = "Amazon Linux" ]
    then
      sudo yum install postgresql-server
    fi
    if [ PLATFORM = "OSX" ]
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
    if [ PLATFORM = "Amazon Linux" ]
    then
      sudo yum install postgresql
    fi
    if [ PLATFORM = "OSX" ]
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
# pip install --user gensim

##### INITIALIZE DATABASE #####
echo ""
echo "INITIALIZE DATABASE"

## PostgreSQL Server ##
sudo service postgresql initdb
sudo service postgresql start

# Set password for postgres user.
echo ""
echo "Use postgres command line to set password for default postgres user (run '\password postgres')."
echo "Use the password defined by 'PostgreSQL User `postgres`' in LastPass."
echo "After setting password, quit with '\q'."
read -p "Press ENTER to continue."
sudo -u postgres psql --username=postgres

# Allow password-based postgres login.
if [ PLATFORM="Amazon Linux" ]
then
    echo ""
    echo "Use vi to edit line 80 of pg_hba.conf to read 'local\tall\tall\tmd5'"
    echo "Use vi to edit line 80, 82, and 84 of pg_hba.conf to read 'local\tall\tall\tmd5'"
    read -p "Press ENTER to continue."
    sudo vi /var/lib/pgsql9/data/pg_hba.conf
    sudo service postgresql restart
fi

## Production DB ##
echo "You will now configure the database environment."
echo "For each prompt, follow the answer recommended by the HealthRex Wiki."
read -p "Press ENTER to continue."
echo ""
# Collect production DB parameters.
echo "First, configure the production database..."
read -p "Enter production DB hostname: " PROD_DB_HOST
read -p "Enter production DB database source name: " PROD_DB_DSN
read -p "Enter production DB user ID: " PROD_DB_UID
read -s -p "Enter production DB user password: " PROD_DB_PWD
echo

# Confirm production DB already exists or create it.
# if [ "$(psql -lqt | cut -d \| -f 1 | grep -qw $PROD_DB_DSN)" ]

# Confirm production user already exists or create it.
if [ "$(psql --dbname=postgres --username=postgres -tAc "SELECT rolname from pg_roles WHERE rolname='$PROD_DB_UID'" | grep $PROD_DB_UID)" ]
then
    echo "Confirmed: Prod user $PROD_DB_UID exists in DB."
else
    psql --host=$PROD_DB_HOST --dbname=postgres --username=postgres -c "SET client_min_messages = ERROR; CREATE USER $PROD_DB_UID WITH SUPERUSER CREATEROLE CREATEDB PASSWORD '$PROD_DB_PWD';"
    echo "Created: Prod user $PROD_DB_UID."
fi

# Confirm production DSN already exists or create it.
if [ "$(psql --username=postgres -lqt | cut -d \| -f 1 | grep -qw $PROD_DB_DSN)" ]
then
    echo "Confirmed: Prod data source $PROD_DB_DSN exists in DB."
else
    psql --host=$PROD_DB_HOST --username=postgres -c "SET client_min_messages = ERROR; CREATE DATABASE $PROD_DB_DSN OWNER $PROD_DB_UID;"
    echo "Created: Prod data source $PROD_DB_DSN owned by $PROD_DB_UID."
fi

# Collect test DB parameters.
echo ""
echo "Second, configure the test database, on which unittest will run..."
read -p "Enter test DB hostname: " TEST_DB_HOST
read -p "Enter test DB database source name: " TEST_DB_DSN
read -p "Enter test DB user ID: " TEST_DB_UID
read -s -p "Enter test DB user password: " TEST_DB_PWD
echo

# Write production DB parameters to local environment file.
echo ""
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

# Confirm test user already exists or create it.
if [ "$(psql --dbname=postgres --username=postgres -tAc "SELECT rolname from pg_roles WHERE rolname='$TEST_DB_UID'" | grep $TEST_DB_UID)" ]
then
    echo "Confirmed: Test user $TEST_DB_UID exists in DB."
else
    psql --host=$TEST_DB_HOST --dbname=postgres --username=postgres -c "SET client_min_messages = ERROR; CREATE USER $TEST_DB_UID WITH SUPERUSER CREATEROLE CREATEDB PASSWORD '$TEST_DB_PWD';"
    echo "Created: Test user $TEST_DB_UID."
fi

# Confirm test DSN already exists or create it.
if [ "$(psql --username=postgres -lqt | cut -d \| -f 1 | grep -qw $TEST_DB_DSN)" ]
then
    echo "Confirmed: Test data source $TEST_DB_DSN exists in DB."
else
    psql --host=$TEST_DB_HOST --username=postgres -c "SET client_min_messages = ERROR; CREATE DATABASE $TEST_DB_DSN OWNER $TEST_DB_UID;"
    echo "Created: Test data source $TEST_DB_DSN owned by $TEST_DB_UID."
fi

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

# Define schema based on various .sql files in medinfo/db/definition/.
source ./medinfo/db/definition/define_db_schemata.sh
define_schemata $TEST_DB_HOST $TEST_DB_DSN postgres

#####

##### VERIFY TESTS PASS #####

# Print success state.
#python medinfo/db/test/TestDBUtil.py
