"""Various constants for use by the application modules"""

import sys;
import logging
import Env

"""Application name","for example to identify a common logger object"""
APPLICATION_NAME = "medinfo.cpoe.app"

"""Default level for application logging.  Modify these for different scenarios.  See Python logging package documentation for more information"""
LOGGER_LEVEL = Env.LOGGER_LEVEL

"""Default format of logger output"""
LOGGER_FORMAT = "[%(asctime)s %(levelname)s] %(message)s"

"""Sentinel ID value for medications indicating a template value to be filled in by child mixture information"""
TEMPLATE_MEDICATION_ID = 9000000;
"""Prefix for generic medication descriptions"""
TEMPLATE_MEDICATION_PREFIX = "ZZZ";

"""Sentinel result value when no specific numeric value reported"""
SENTINEL_RESULT_VALUE = 9999999;

"""String flag labels for different result classifications"""
FLAG_IN_RANGE = "InRange";
FLAG_HIGH = "High";
FLAG_LOW = "Low";
FLAG_RESULT = "Result";
FLAG_ABNORMAL = "Abnormal";

"""Z score value to treat a result as abnormally high / low.  Number of standard deviations from the mean."""
Z_SCORE_LIMIT = 2;

"""Collection Type ID to designate system order sets"""
COLLECTION_TYPE_ORDERSET = 4;