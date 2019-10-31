import Const
import sys, os
import logging
import cgi, UserDict
import unittest
from contextlib import contextmanager
from StringIO import StringIO

from medinfo.db.test.Util import DBTestCase;

import medinfo.cpoe.Util;


log = logging.getLogger("CDSS")

handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(Const.LOGGER_FORMAT)

handler.setFormatter(formatter)
log.addHandler(handler)

# Suppress uninteresting application output
medinfo.cpoe.Util.log.setLevel(Const.APP_LOGGER_LEVEL)


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err
