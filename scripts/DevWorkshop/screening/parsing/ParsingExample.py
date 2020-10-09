#!/usr/bin/env python

import sys, os
import time;
import re;
from datetime import datetime;

class ParsingExample:
    """Application module with several functions to implement and test.
    """
    def parseLogicStr(self, logicStr):
        """Parse logic string into computable structured format
        Examples
        (SEX)&(AGE)&FI(1)&FF(1)&(FI(5)!FI(6)!FI(7))&FF(2)
        (SEX)&(AGE)&FI(2)&'FI(3)
        Assumed interpretation:
          ' represents NOT
          ! represents OR
          & represents AND


		Parse it into a computable stack/list of descriptive components, similar to below:

        testStr = "(SEX)&(AGE)&FI(2)&'FI(3)";
        expectedLogicStack = \
            [   {"negate": False, "type": "SEX", "index": None },
                "&",
                {"negate": False, "type": "AGE", "index": None },
                "&",
                {"negate": False, "type": "FI", "index": 2 },
                "&",
                {"negate": True, "type": "FI", "index": 3 },
            ];


        """
        logicStack = list();  # Store components as a stack (list) of items and operators

        ###################### START CODE HERE ########################
        ###################### START CODE HERE ########################
        ###################### START CODE HERE ########################
        ###################### START CODE HERE ########################


        ###################### END CODE HERE ########################
        ###################### END CODE HERE ########################
        ###################### END CODE HERE ########################
        ###################### END CODE HERE ########################

        return logicStack;
