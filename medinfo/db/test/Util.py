import Const
import sys, os
import logging
import cgi, UserDict
import unittest

from medinfo.common.test.Util import MedInfoTestCase;
from medinfo.db import DBUtil;

import medinfo.db.Env;
import medinfo.db.Util;


log = logging.getLogger("CDSS")

#handler = logging.StreamHandler(sys.stderr)
#formatter = logging.Formatter(Const.LOGGER_FORMAT)

#handler.setFormatter(formatter)
#log.addHandler(handler)

# Suppress uninteresting application output
medinfo.db.Util.log.setLevel(Const.APP_LOGGER_LEVEL)


class DBTestCase(MedInfoTestCase):
    orig_DB_PARAM = None;
    testDBCreated = False;

    """Common base class for TestCase classes that cinlude queries against the databse.
    Important distinction to help put in hooks to protect a "real" database from
    test queries.
    """
    def setUp(self):
        """Prep for test case.  Subclass must call this parent method to actually use it.
        """
        MedInfoTestCase.setUp(self)

        # if medinfo.db.Env.DB_PARAM["DSN"] == medinfo.db.Env.TEST_DB_PARAM["DSN"]:
        #     quit("Please use different names for production and test databases!")

        # Override default DB connection params to test DB, but retain links to original
        self.orig_DB_PARAM = dict(medinfo.db.Env.DB_PARAM);

        medinfo.db.Env.DB_PARAM.update(medinfo.db.Env.TEST_DB_PARAM);

        # Create the temporary test database to work with
        try:
            DBUtil.createDatabase(medinfo.db.Env.DB_PARAM);
            self.testDBCreated = True;  # If error on above (e.g., database already exists), will have aborted with a database error before this
        except DBUtil.DB_CONNECTOR_MODULE.ProgrammingError, err:
            # Error on database creation, probably because existing one already there
            # Drop existing database if already there, but beware!
            # Beware of accidentally dropping an existing production database! This may still be necessary to cleanup if accidentally left a test database instance behind
            DBUtil.dropDatabase(medinfo.db.Env.DB_PARAM)    
            DBUtil.createDatabase(medinfo.db.Env.DB_PARAM);
            self.testDBCreated = True;  # If error on above (e.g., database already exists), will have aborted with a database error before this

    def tearDown(self):
        """Restore state after test finishes.  Subclass must call this parent method to actually use it.
        """
        # Drop the temporary test database, but make sure we created it ourselves, so we don't accidentally drop a production database
        if self.testDBCreated:
            DBUtil.dropDatabase(medinfo.db.Env.DB_PARAM);

        medinfo.db.Env.DB_PARAM.update(self.orig_DB_PARAM);

        MedInfoTestCase.tearDown(self)
