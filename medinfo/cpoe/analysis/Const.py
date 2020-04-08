"""Various constants for use by the application modules"""

import sys;
import logging
from . import Env
from datetime import timedelta;

"""Application name","for example to identify a common logger object"""
APPLICATION_NAME = "medinfo.cpoe.analysis.app"

"""Default level for application logging.  Modify these for different scenarios.  See Python logging package documentation for more information"""
LOGGER_LEVEL = Env.LOGGER_LEVEL

"""Default format of logger output"""
LOGGER_FORMAT = "[%(asctime)s %(levelname)s] %(message)s"


"""Admit diagnosis category generally recorded with date level resolution vs. orders recorded with time resolution.  
Means Admit Dx will look like it occurs at midnight, even though orders may not show up until 5pm.  
If looking for "first 4 hours" of orders then, will only look from midnight-4am and find nothing.  
So look for the NEXT item to define the admission start time.
Exception if next item >=1 day away (option here), suggesting that items themselves are recorded with day level precision 
instead of time, so just start from the base item time.
"""
MAX_BASE_ITEM_TIME_RESOLUTION = timedelta(1);    # 1 day
