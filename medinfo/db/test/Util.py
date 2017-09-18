import Const
import sys, os
import logging
import cgi, UserDict
import unittest

from medinfo.common.test.Util import MedInfoTestCase;

import medinfo.db.Env;
import medinfo.db.Util;


log = logging.getLogger(__name__)
log.setLevel(Const.LOGGER_LEVEL)

handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(Const.LOGGER_FORMAT)

handler.setFormatter(formatter)
log.addHandler(handler)

# Suppress uninteresting application output
medinfo.db.Util.log.setLevel(Const.APP_LOGGER_LEVEL) 


class DBTestCase(MedInfoTestCase):
    """Common base class for TestCase classes that cinlude queries against the databse.
    Important distinction to help put in hooks to protect a "real" database from
    test queries.
    """
    def setUp(self):
        """Prep for test case.  Subclass must call this parent method to actually use it.
        """
        MedInfoTestCase.setUp(self)
        
        # Override default DB connection params to rest DB, but retain links to original
        self.orig_DB_PARAM = dict(medinfo.db.Env.DB_PARAM);
                
        medinfo.db.Env.DB_PARAM.update(medinfo.db.Env.TEST_DB_PARAM);
       
    def tearDown(self):
        """Restore state after test finishes.  Subclass must call this parent method to actually use it.
        """
        medinfo.db.Env.DB_PARAM.update(self.orig_DB_PARAM);

        MedInfoTestCase.tearDown(self)

