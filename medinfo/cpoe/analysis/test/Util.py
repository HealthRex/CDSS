import Const
import sys, os
import logging
import cgi, UserDict
import unittest

import json;

from medinfo.common.Const import COMMENT_TAG, NULL_STRING;
from medinfo.db.Model import SQLQuery, RowItemModel;

import medinfo.cpoe.analysis.Util;


log = logging.getLogger("CDSS")
# log.setLevel(Const.LOGGER_LEVEL)

handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter(Const.LOGGER_FORMAT)

handler.setFormatter(formatter)
log.addHandler(handler)

# Suppress uninteresting application output
medinfo.cpoe.analysis.Util.log.setLevel(Const.APP_LOGGER_LEVEL)
