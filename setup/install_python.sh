#!/bin/bash

##### IDENTIFY PLATFORM #####
# OSX
MAC_OSX="OSX"
if [ "$(uname)" = "Darwin" ]
then
    PLATFORM=MAC_OSX
fi

# Amazon
AMAZON_LINUX="Amazon Linux"
if [ "$(uname) | grep 'amzn')" ]
then
    PLATFORM=AMAZON_LINUX
fi

##### INSTALL PYTHON #####
echo "python"

# Python (https://www.python.org/)
if [ "$(command -v python)" ]
then
    PYTHON_VERSION=$(python --version 2>&1)
    echo "  Installed: $PYTHON_VERSION"
else
    echo "  Installing python on $PLATFORM..."
    # Amazon
    if [ "$PLATFORM" = "$AMAZON_LINUX" ]
    then
	sudo yum install python
    fi
    # OSX
    if [ "$PLATFORM" = "$MAC_OSX" ]
    then
	brew install python
    fi
    # Echo version.
    PYTHON_VERSION=$(python --version 2>&1)
    echo "  Installed: $PYTHON_VERSION"
fi
