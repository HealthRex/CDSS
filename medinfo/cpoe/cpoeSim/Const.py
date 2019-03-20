"""Various constants for use by the application modules"""

from datetime import datetime, timedelta;


"""Arbitrary base time to start simulations from"""
BASE_TIME = datetime(2010,1,1,12,0);    
TIME_FORMAT = "%m/%d/%Y, %I:%M%p";


"""ID of the default simulation state to fall back on if have no other state-specific results/information"""
DEFAULT_STATE_ID = 0;