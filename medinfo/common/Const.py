"""Various constants for use by the application modules"""

import sys;
import logging
import Env

"""If specify this as the name of an input/output file, interpret as user wants to use stdin or stdout"""
STD_FILE = "-"

"""File extension to identify GZipped files"""
GZIP_EXT = ".gz";

"""Tag to mark comments in processed files"""
COMMENT_TAG = "#"

"""Tag to indicate a multi-part or multi-line parameter counts as a single token"""
TOKEN_END = '"'

"""Delimiter for multiple parameter values"""
VALUE_DELIM = ",";

"""Null string used to represent DB null value"""
NULL_STRING = str(None);

"""Null tag used to represent DB null value"""
NULL_TAG = "<NULL>";

"""Lower case strings that will be interpreted as a boolean False value"""
FALSE_STRINGS = ("","0","false","f",str(False));

"""Single common instance of an empty set to save on instantiation costs when have many of them"""
EMPTY_SET = frozenset();

"""Not functionally important","just indicates an estimate of the number
of lines in input files to hint a proper scale for the progress indicators.
If you do not wish to see those dot indicators","set this value to 0."""
EST_INPUT = Env.EST_INPUT

"""Updates to process before reporting progress"""
PROG_BIG = 1000;
PROG_SMALL = 25;
PROG_BIG_TIME = 60; # 1 minute per big update
PROG_SMALL_TIME = 1; # 1 second per small update


"""Default level for application logging.  Modify these for different scenarios.  See Python logging package documentation for more information"""
LOGGER_LEVEL = Env.LOGGER_LEVEL

"""Default format of logger output"""
LOGGER_FORMAT = "[%(asctime)s %(levelname)s] %(module)s.%(funcName)s.%(lineno)d: %(message)s"

"""Default datetime format parsers.  Will be attempted in sequential order.
See Python documentation for formatting codes.
https://docs.python.org/2/library/time.html
"""
DEFAULT_DATE_FORMATS = \
    [   "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%m/%d/%y %H:%M:%S",
        "%m/%d/%y %H:%M",
        "%m/%d/%y",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y",
        "%d-%b-%y",
        "%b %d, %Y %I:%M %p",
    ];
