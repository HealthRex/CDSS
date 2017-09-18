"""Various constants for use by the web scripts"""
import Env;

"""Parameter key to pass if don't want the HTML interface, 
just want direct data output like a web service"""
OUTPUT_ONLY = "outputOnly";

"""Default delimiter for parameter value strings"""
VALUE_DELIM = ","

"""Delimiter when working with URLs.  Standard VALUE_DELIM may not be safe"""
URL_DELIM = "|";

"""Application name, for example to identify a common logger object"""
APPLICATION_NAME = "MedInfo.Web.cgibin"

"""Default level for application logging.  Modify these for different scenarios.  See Python logging package documentation for more information"""
LOGGER_LEVEL = Env.LOGGER_LEVEL

"""Default format of logger output"""
LOGGER_FORMAT = "[%(asctime)s %(levelname)s] %(message)s"

