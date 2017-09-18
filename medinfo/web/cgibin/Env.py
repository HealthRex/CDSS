"""Various constants for use by the application modules,
but these can / should be changed depending on the platform / environment
where they are installed.
"""

import sys, os;
import logging

"""Default level for application logging.  Modify these for different scenarios.  
See Python logging package documentation for more information"""
LOGGER_LEVEL = logging.DEBUG
#LOGGER_LEVEL = logging.INFO
#LOGGER_LEVEL = logging.WARNING
#LOGGER_LEVEL = logging.ERROR
#LOGGER_LEVEL = logging.CRITICAL

"""When web scripts are called from some cgi interface, this indicates the 
location of the web cgibin directory (containing the web templates).
Depending upon the particular web server implementation, this may
differ as the starting / run directory of the cgi script may differ
from the actual location of the script file.
"""
#CGIBIN_DIR = "REACT/web/cgibin/" # MS Personal Web Server runs scripts from \Inetpub\Scripts directory no matter where actual script file was
#CGIBIN_DIR = ""                  # The "normal" expected value if script run from same directory as script file
# For better platform independence, derive based on imported module location
import medinfo.web;
WEB_DIR = os.path.dirname(medinfo.web.__file__);

"""SMTP host and e-mail address to send error reports through.
Leave the e-mail address as None to not e-mail error reports.
The CDB_EMAIL will be considered the "from" e-mail address.
"""
SMTP_HOST   = "smtp.ics.uci.edu";
ERROR_EMAIL = None; #"errorspam@ics.uci.edu";
HOST_EMAIL   = "info@reactionexplorer.com";


# Tracking script for traffic monitoring
TRACKING_SCRIPT_TEMPLATE = "";

# If doing plain CGI response, then need to turn on plain text response.  
# Otherwise turn this off to not waste I/O to stdout if using WSGI or mod_python
CGI_TEXT_RESPONSE = False;

# Whether to use a local memory data cache to reduce DB hits for web queries.  If left unchecked, this will result
#   in excessive memory use / leak by the webserver
USE_DATA_CACHE = True;
