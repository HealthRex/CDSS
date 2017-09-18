import Const
import sys, os
import logging
import cgi, UserDict
import unittest

from medinfo.common.test.Util import MedInfoTestCase;

import medinfo.textanalysis.Util;


log = logging.getLogger(__name__)
log.setLevel(Const.LOGGER_LEVEL)

handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(Const.LOGGER_FORMAT)

handler.setFormatter(formatter)
log.addHandler(handler)

# Suppress uninteresting application output
medinfo.textanalysis.Util.log.setLevel(Const.APP_LOGGER_LEVEL) 

