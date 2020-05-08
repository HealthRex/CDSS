#!/usr/bin/env python
"""Miscellaneous utility functions used across the application
"""
from . import Const, Env
import sys, os
import logging
import urllib.request, urllib.parse, urllib.error;
import time;
import math;

log = logging.getLogger("CDSS")

handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(Const.LOGGER_FORMAT)

handler.setFormatter(formatter)
# log.addHandler(handler)

# Global Support variable to monitor how may connections have been created
numConnections = 0;

def main(argv):
    """Main method, callable from command line"""
    pass

if __name__ == "__main__":
    main(sys.argv)
