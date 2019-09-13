"""Various constants for use by the application modules,
but these can / should be changed depending on the 
platform / environment where they are installed.
"""

import sys, os;
import logging
import socket

"""Default level for application logging.  Modify these for different scenarios.  
See Python logging package documentation for more information"""
#LOGGER_LEVEL = logging.DEBUG
LOGGER_LEVEL = logging.INFO
#LOGGER_LEVEL = logging.WARNING
#LOGGER_LEVEL = logging.ERROR
#LOGGER_LEVEL = logging.CRITICAL

"""Not functionally important, just indicates an estimate of the number
of lines in input files to hint a proper scale for the progress indicators.
If you do not wish to see those dot indicators, set this value to 0.

Several usages divide this value by 200 to indicate the desired number
of total dots ~200.  Thus, do not set the value < 200 or else there
will effectively be no results, unless that is your desired behavior (set to 0)
"""
EST_INPUT = 10000

"""Local host name and IP address which can be translated by DNS.
On ICS computers, has annoying habit of just giving back the prefix (e.g., "contact6",
instead of the entire name "contact6.ics.uci.edu", so may have to do some extra work here.
"""
try:    
    HOSTNAME = socket.gethostname();
    IP_ADDR  = socket.gethostbyname(HOSTNAME);
except:
    HOSTNAME = 'localhost'
    IP_ADDR = '127.0.0.1'

LAB_TYPE = "panel"  # can be panel, component or mixed