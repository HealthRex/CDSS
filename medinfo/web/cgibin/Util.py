#!/usr/bin/env python
"""Miscellaneous utility functions
"""
import Env;
import Const
import sys, os
import logging

log = logging.getLogger(Const.APPLICATION_NAME)
log.setLevel(Const.LOGGER_LEVEL)

handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(Const.LOGGER_FORMAT)

handler.setFormatter(formatter)
log.addHandler(handler)

"""Persistent cache object to store query results in local memory for reuse later"""
webDataCache = None;
if Env.USE_DATA_CACHE:
    webDataCache = dict();
