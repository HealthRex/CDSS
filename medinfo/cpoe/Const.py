"""Various constants for use by the application modules"""

import sys;
import logging
import Env
from datetime import datetime, timedelta;

"""Application name","for example to identify a common logger object"""
APPLICATION_NAME = "medinfo.cpoe.app"

"""Default level for application logging.  Modify these for different scenarios.  See Python logging package documentation for more information"""
LOGGER_LEVEL = Env.LOGGER_LEVEL

"""Default format of logger output"""
LOGGER_FORMAT = "[%(asctime)s %(levelname)s] %(message)s"

"""Assorted date/time constants to facilitate stats analysis of clinical item pair associations"""
SECONDS_PER_DAY = 60*60*24;
DELTA_NAME_BY_SECONDS = \
    {   
        0: "Zero",
        3600: "1 hour",
        7200: "2 hours",
        21600: "6 hours",
        43200: "12 hours",
        86400: "1 day",
        172800: "2 days",
        345600: "4 days",
        604800: "1 week",
        1209600: "2 weeks",
        2592000: "1 month",
        7776000: "3 months",
        15552000: "6 months",
        31536000: "1 year",
        63072000: "2 years",
        126144000: "4 years",
    }
"""Similar list but starting in units of 1 day"""
DELTA_NAME_BY_DAYS = dict();
for seconds, label in DELTA_NAME_BY_SECONDS.iteritems():
    days = seconds/ SECONDS_PER_DAY;
    if days > 0:
        DELTA_NAME_BY_DAYS[days] = label;

    
"""Option keys for selecting a recommendation aggregation method"""
AGGREGATOR_OPTIONS = ("weighted","unweighted","SerialBayes","NaiveBayes");

"""Option key prefixes for selecting a counting method for item associations"""
COUNT_PREFIX_OPTIONS = ("","patient_","encounter_");


"""Core fields to always show with results"""
#CORE_FIELDS = ["nAB","nA","nB","nA!B","nB!A","n!A!B","N"];
BASELINE_FIELDS = ["nB","N"];
CORE_FIELDS = ["nAB","nA","nB","N"];

"""Fields to format as percentages"""
PERCENT_FIELDS = ["PPV","prevalence","sensitivity","specificity","precision","recall"];

"""Constants to define what item collection types are described by different identifiers
"""
COLLECTION_TYPE_ORDER_SET = 4;

"""Section name for Ad-Hoc orders that generally should not be considered as part of standard order sets.
These are the "ad-hoc" individual orders that users can tack on to an order set at any one time.
"""
AD_HOC_SECTION = "Ad-hoc Orders";

"""Arbitrary base time to start simulations from"""
BASE_TIME = datetime(2010,1,1,12,0);    
TIME_FORMAT = "%m/%d/%Y, %I:%M%p";


"""ID of the default simulation state to fall back on if have no other state-specific results/information"""
DEFAULT_STATE_ID = 0;