import Const
import sys, os
import logging
import cgi, UserDict
import unittest

from medinfo.db.test.Util import DBTestCase;

import medinfo.cpoe.Util;


log = logging.getLogger(Const.APPLICATION_NAME)
log.setLevel(Const.LOGGER_LEVEL)

handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(Const.LOGGER_FORMAT)

handler.setFormatter(formatter)
log.addHandler(handler)

# Suppress uninteresting application output
medinfo.cpoe.Util.log.setLevel(Const.APP_LOGGER_LEVEL) 

