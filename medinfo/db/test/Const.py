"""Various constants for use by the reaction processing module test cases"""

import logging

"""Application name, for example to identify a common logger object"""
APPLICATION_NAME = "MedInfo.DB.test"

"""Default level for application logging.  Modify these for different scenarios.
See Python logging package documentation for more information
"""
LOGGER_LEVEL = logging.DEBUG

"""Default format of logger output"""
LOGGER_FORMAT = "[%(asctime)s %(levelname)s] %(message)s"

"""Verbosity of the test runner"""
RUNNER_VERBOSITY = 2

"""Application logger level.  Set this to higher level to suppress uninteresting
application output during test runs."""
APP_LOGGER_LEVEL = logging.CRITICAL


"""For some test cases with many test points, don't want to abort the entire test if just one item fails"""
ALLOW_MULTIPLE_ERRORS = True;
