#!/usr/bin/env python
"""Miscellaneous utility functions used across the application
"""
from . import Const, Env
import sys, os
import logging

log = logging.getLogger("CDSS")
# log.setLevel(Const.LOGGER_LEVEL)

handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(Const.LOGGER_FORMAT)

handler.setFormatter(formatter)
# log.addHandler(handler)
