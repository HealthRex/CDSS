"""Various constants for use by the application modules,
but these can / should be changed depending on the
platform / environment where they are installed.
"""

import sys, os;
import logging

"""Default level for application logging.  Modify these for different scenarios.
See Python logging package documentation for more information"""
LOGGER_LEVEL = logging.DEBUG
# LOGGER_LEVEL = logging.INFO
#LOGGER_LEVEL = logging.WARNING
# LOGGER_LEVEL = logging.ERROR
#LOGGER_LEVEL = logging.CRITICAL


DATE_FORMAT = "%Y-%m-%d";
