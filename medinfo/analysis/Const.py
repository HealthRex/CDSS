"""Various constants for use by the application modules"""

import sys;
import logging
import Env
from datetime import timedelta;

"""Default level for application logging.  Modify these for different scenarios.  See Python logging package documentation for more information"""
LOGGER_LEVEL = Env.LOGGER_LEVEL

"""Default format of logger output"""
LOGGER_FORMAT = "[%(asctime)s %(levelname)s] %(message)s"


# Code values for outcome existence labels
OUTCOME_ABSENT  =  0;
OUTCOME_PRESENT = +1;
OUTCOME_IN_QUERY = +2;

# Strings that will be interpreted as a negative outcome
NEGATIVE_OUTCOME_STRS = set(["0","-1","False","FALSE"]);
