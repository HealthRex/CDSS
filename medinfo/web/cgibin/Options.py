#!/usr/bin/env python
"""Repository for all the select box option tag lists.
Names of select fields should be added / mapped here
to their respective lists if you want BaseWeb.py to
take care of the parameter maintenance.
"""
from medinfo.common.Const import NULL_TAG;

FIELD2VALUE = {}
FIELD2TEXT  = {}

# Sample option field
OPTION_VALUE = [];
OPTION_TEXT = [];
OPTION_VALUE.append("");      OPTION_TEXT.append("Any");
OPTION_VALUE.append("Loudon");  OPTION_TEXT.append("Loudon 4th ed.");
OPTION_VALUE.append("Smith");   OPTION_TEXT.append("Smith 2nd ed.");
OPTION_VALUE.append("Bruice");  OPTION_TEXT.append("Bruice 4th ed.");
OPTION_VALUE.append("Solomons");  OPTION_TEXT.append("Solomons 10th ed.");
OPTION_VALUE.append("Brown_Poon");  OPTION_TEXT.append("Brown &amp; Poon 4th ed.");
OPTION_VALUE.append("Klein");  OPTION_TEXT.append("Klein 1st ed.");
OPTION_VALUE.append("Sample");  OPTION_TEXT.append("Sample");

FIELD2VALUE["textbookSelect"] = OPTION_VALUE;
FIELD2TEXT ["textbookSelect"] = OPTION_TEXT;

