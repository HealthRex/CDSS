import Const
import sys, os
import logging
import cgi, UserDict
import unittest

import json;

#from medinfo.db.test.Util import MedInfoTestCase;
from medinfo.common.test.Util import MedInfoTestCase;

import medinfo.analysis.Util;


log = logging.getLogger("CDSS")
log.setLevel(Const.LOGGER_LEVEL)

handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(Const.LOGGER_FORMAT)

handler.setFormatter(formatter)
log.addHandler(handler)

# Suppress uninteresting application output
medinfo.analysis.Util.log.setLevel(Const.APP_LOGGER_LEVEL)


class BaseTestAnalysis(MedInfoTestCase):
    def noFunction(self):
        # USed to have some analysis support functions, but moved up to MedInfoTestCase for more general usage
        pass;
