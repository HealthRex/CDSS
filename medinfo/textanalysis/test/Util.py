from . import Const
import sys, os
import logging
import cgi
from collections import UserDict
import unittest

from medinfo.common.test.Util import MedInfoTestCase;

import medinfo.textanalysis.Util;


log = logging.getLogger("CDSS")
log.setLevel(Const.LOGGER_LEVEL)

handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(Const.LOGGER_FORMAT)

handler.setFormatter(formatter)
log.addHandler(handler)

# Suppress uninteresting application output
medinfo.textanalysis.Util.log.setLevel(Const.APP_LOGGER_LEVEL)
