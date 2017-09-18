"""Various constants for use by the application modules"""

import sys;
import logging
import Env

"""Delimiter of SQL commands in a DB script file"""
SQL_DELIM = ";"

"""Default suffix for database table id fields, particularly the primary key, but also
foreign key columns that reference other tables."""
DEFAULT_ID_COL_SUFFIX = "_id";

"""Wildcard string used in SQL queries"""
SQL_WILDCARD = "%";

"""Default level for application logging.  Modify these for different scenarios.  See Python logging package documentation for more information"""
LOGGER_LEVEL = Env.LOGGER_LEVEL

"""Default format of logger output"""
LOGGER_FORMAT = "[%(asctime)s %(levelname)s] %(message)s"
