#!/usr/bin/env python
"""
Gives a summary of the reminder in question.
"""

import sys, os
import time;
import re;
from pdb import set_trace as t
from datetime import datetime;
from optparse import OptionParser
from medinfo.common.Util import stdOpen, ProgressDots;
from medinfo.db import DBUtil;
from medinfo.db.Model import SQLQuery;
from medinfo.db.Model import RowItemModel, modelListFromTable, modelDictFromList;
from Util import log;
from Env import DATE_FORMAT;
import Finding;
from Error import *;

# Target database DSN to eventually apply generated queries to
TARGET_DB_DSN = "ORD_Chan_201406081D";
# Here. There.
# Map reminder frequency interval characters (e.g., d, m, y) into SQL date parameter strings
INTERVAL_CHAR_TO_STR = \
{   "d": "day",
    "m": "month",
    "y": "year",
};
# DictionarY mapping Finding type to tuple t = (t[0], t[1])
# Where t[0] = target database name
#       t[1] = target column name
# These came from spreadsheet "AboutFindings.xlsx" in GoogleDrive
# But may be wrong, there are discrepancies between the spreadsheet and the
# manual examples.
FINDINGS_TARGET_DB_MAP = \
{   "PXRMD": ("RMNDR_TERM_FNDNGS_811x52", ""),
    "PSNDF": ("[CDWWork_FY14].[Dim].[DrugNameWithoutDose]", "DrugNameWithoutDoseIEN"),
    "LABS": ("[CDWWork_FY14].[Dim].[LabChemTest]", "LabChemTestIEN"),
    "AUTTHF": ("[ORD_Chan_201406081D].[Src].[HF_HealthFactor]", "HealthFactorTypeIEN")
};


class ReminderSnapshot:
    """
    Produces a readable summary of the reminder in question.
    """
    conn = None; # Database connection to read from

    def __init__(self):
        """Default constructor"""
        self.connFactory = DBUtil.ConnectionFactory();  # Default connection source, but Allow specification of alternative DB connection source


    def convertReminder(self, siteCode, reminderIEN):
        """Query for just reminder logic. Simply reuse code from querying for multiple at a time."""
        #list(
        self.convertReminders(siteCode, [reminderIEN]) #)[0] # Assume will generate a list of size 1 and return only result

    def convertReminders(self, siteCode, reminderIENs):
        """Given an individual siteCode and collection of reminderIENs to identify particular reminders,
        query out the relevant information in the source reminder database and stitch together
        data relationships to translate each reminder into SQL queries for the
        cohort, resolution, and combination logic / SQL strings, returned as a list of 3-ples.

        Start with simple design, query for all results in memory, but if too massive on full dataset,
        convert to streaming query ordered by reminder IEN so can synchronously step through each linked table together
        """


        print 'siteCode = ' + str(siteCode);
        print 'reminderIEN = ' + str(reminderIENs) + '\n'

        conn = self.connFactory.connection();
        try:
            # Primary reminder query
            query = SQLQuery();
            query.addSelect\
            ("""IEN, SITECODE, NM_X01,
                SEX_SPCFC_1X9,
                INTRNL_PTNT_CHRT_LGC_31, PTNT_CHRT_FNDNGS_LST_33,
                INTRNL_RSLTN_LGC_35, RSLTN_FNDNGS_LST_37,
                DO_IN_ADVNC_TM_FRM_1X3"""
            );
            query.addFrom("RMNDR_DFNTN_811X9");
            query.addWhereEqual("SITECODE", siteCode);
            query.addWhereIn("IEN", reminderIENs );
            query.addOrderBy("IEN");
            query.addOrderBy("SITECODE");

            # Execute primary reminder query
            reminderCursor = conn.cursor();
            reminderCursor.execute( str(query), query.params )
            reminderCols = DBUtil.columnNamesFromCursor(reminderCursor);

            # Baseline age findings query in parallel
            query = SQLQuery();
            query.addSelect\
            ("""P_IEN, IEN, SITECODE,
                RMNDR_FRQNCY_X01,
                MINMM_AGE_1, MAXMM_AGE_2"""
            );
            query.addFrom("BSLN_AGE_FNDNGS_811X97");
            query.addWhereEqual("SITECODE", siteCode );
            query.addWhereIn("P_IEN", reminderIENs );
            query.addOrderBy("P_IEN");
            query.addOrderBy("SITECODE");

            # Execute baseline age findings query in parallel cursor
            # (Avoid simple or even outer join due to variable one-to-many relationship. Some reminders with no age findings. Some reminders with multiple.)
            baselineAgeCursor = conn.cursor();
            baselineAgeCursor.execute( str(query), query.params )
            lastBaselineAgeModel = {"P_IEN":-1, "SITECODE":-1}; # Mock model with sentinel values to trigger subsequent loops

            # Core findings query in parallel
            query = SQLQuery();
            query.addSelect\
            ("""P_IEN, IEN, SITECODE,
                FNDNG_ITM_X01,
                MIN_AGE_1, MAX_AGE_2,
                RMNDR_FRQNCY_3, RNK_FRQNCY_6,
                USE_IN_RSLTN_LGC_7,
                USE_IN_PTNT_CHRT_GC_8,
                BGNNG_DT_TM_9
                """
            );
            query.addFrom("FINDINGS_811X902");
            query.addWhereEqual("SITECODE", siteCode );
            query.addWhereIn("P_IEN", reminderIENs );
            query.addOrderBy("P_IEN");
            query.addOrderBy("SITECODE");
            query.addOrderBy("IEN");

            # Execute core findings query in parallel cursor
            findingsCursor = conn.cursor();
            findingsCursor.execute( str(query), query.params )
            lastFindingsModel = {"P_IEN":-1, "SITECODE":-1}; # Mock model with sentinel values to trigger subsequent loops

            # Iterate through main reminder rows one at a time
            for reminderRow in reminderCursor:
                reminderModel = RowItemModel(reminderRow, reminderCols);

                self.parseReminderModel(reminderModel);
                lastBaselineAgeModel = self.appendBaselineAgeFindingsModel(reminderModel, baselineAgeCursor, lastBaselineAgeModel);
                lastFindingsModel = self.appendFindingsModel(reminderModel, findingsCursor, lastFindingsModel, conn=conn);

                for key in reminderModel:
                    print '\n'+key+ ": "

                    if key in ["baselineAgeModels", "cohortLogicStack", "resolutionLogicStack", "findingsModels"]:
                        for i, elem in enumerate(reminderModel[key]):
                            if key in ["baselineAgeModels", "findingsModels"]:
                                print "Model " + str(i)
                                for col in elem:
                                    if col == "subfindingModels":
                                        print "subfindings: "
                                        for subIdx, sub in enumerate(elem[col]):
                                            print "\nSubfinding " + str(subIdx)
                                            for subKey in sub:
                                                print subKey + ": " + str(sub[subKey])
                                    else:
                                        print col + ": " + str(elem[col])
                                print '\n'
                            else:
                                print str(i) + ": " + str(elem)
                    else:
                        print reminderModel[key]

        finally:
            conn.close();

    def appendBaselineAgeFindingsModel(self, reminderModel, baselineAgeCursor, lastBaselineAgeModel):
        """Find rows in baselineAgeCursor pertaining to the given reminderModel
        and add them on as a child list. Assumes the cursor is sorted by P_IEN and SITECODE.
        """
        baselineAgeModels = list();

        while lastBaselineAgeModel is not None and \
            (   lastBaselineAgeModel["P_IEN"] <= reminderModel["IEN"] and \
                lastBaselineAgeModel["SITECODE"] <= reminderModel["SITECODE"]
            ):
            if  (   lastBaselineAgeModel["P_IEN"] == reminderModel["IEN"] and \
                    lastBaselineAgeModel["SITECODE"] == reminderModel["SITECODE"]
                ):
                self.parseBaselineAgeModel(lastBaselineAgeModel, reminderModel);
                baselineAgeModels.append(lastBaselineAgeModel);

            lastBaselineAgeModel = DBUtil.nextRowModel(baselineAgeCursor);

        reminderModel["baselineAgeModels"] = baselineAgeModels;
        return lastBaselineAgeModel;

    def appendFindingsModel(self, reminderModel, findingsCursor, lastFindingsModel, conn):
        """Find rows in findingsCursor pertaining to the given reminderModel
        and add them on as a child list. Assumes the cursor is sorted by P_IEN and SITECODE.
        """
        findingsModels = list();

        while lastFindingsModel is not None and \
            (   lastFindingsModel["P_IEN"] <= reminderModel["IEN"] and \
                lastFindingsModel["SITECODE"] <= reminderModel["SITECODE"]
            ):

            if  (   lastFindingsModel["P_IEN"] == reminderModel["IEN"] and \
                    lastFindingsModel["SITECODE"] == reminderModel["SITECODE"]
                ):
                self.parseFindingsModel(lastFindingsModel, reminderModel, conn=conn);
                findingsModels.append(lastFindingsModel);


            lastFindingsModel = DBUtil.nextRowModel(findingsCursor);

        reminderModel["findingsModels"] = findingsModels;
        return lastFindingsModel;

    def parseReminderModel(self, reminderModel):
        """Pull out cohort and resolution base information
        from strings in reminder model into computable
        structured format and deposit back into model
        """
        # E.g., Cohort logic (INTRNL_PTNT_CHRT_LGC_31)
        # (SEX)&(AGE)&FI(1)&FF(1)&(FI(5)!FI(6)!FI(7))&FF(2)
        # (SEX)&(AGE)&FI(2)&'FI(3)
        # Assumed interpretation:
        #   ! or ' represents NOT
        #   & represents AND logic
        #   No operator represents OR logic
        cohortLogicStack = list();  # Store components as a stack (list) of items and operators
        cohortLogicStr = reminderModel["INTRNL_PTNT_CHRT_LGC_31"];
        nextEndPos = cohortLogicStr.find(")"); # Expect each next token item to end with a closed paranthesis
        while nextEndPos > -1:
            nextToken = cohortLogicStr[:nextEndPos+1];    # Excise apparent next token
            cohortLogicStr = cohortLogicStr[nextEndPos+1:];

            # Extract connecting operators if find & or ). If first character is "(" could be
            #   new open parantheses, but first check there is more than one in the token, or may just get the
            #   leading character of "(SEX)" or "(AGE)"
            while nextToken and ( nextToken[0] in ("&",")") or (nextToken[0] == "(" and nextToken.find("(",1) > -1) ):
                cohortLogicStack.append( nextToken[0] );
                nextToken = nextToken[1:];  # Excise operator character

            # If previous logicItem without an interceding operator, indicates default OR logic?
            if cohortLogicStack and isinstance(cohortLogicStack[-1], dict):
                cohortLogicStack.append("|");

            if nextToken: # Remaining string token to evaluate (not final end parantheses)
                # Extract NOT operator
                negateOp = nextToken[0] in ("'","!");
                if negateOp:
                    nextToken = nextToken[1:];

                # See if logicItem has a sub-index number by looking for open parantheses in middle of string
                logicType = re.sub(r"[^A-Za-z]","", nextToken);  # Default to just taking alphabetical characters of token
                logicIndex = None;
                openParenPos = nextToken.find("(");
                if openParenPos > 0:   # NOT the whole token as item (i.e., (SEX) or (AGE)) so look for sub-index
                    logicIndex = int(nextToken[openParenPos+1:-1]);   # Expect index number to be between parantheses
                logicItem = {"negate": negateOp, "type": logicType, "index": logicIndex }

                cohortLogicStack.append( logicItem );
            nextEndPos = cohortLogicStr.find(")");

        reminderModel["cohortLogicStack"] = cohortLogicStack;
        """
        reminderModel["INTRNL_RSLTN_LGC_35"];

        """
        resolutionLogicStack = list();  # Store components as a stack (list) of items and operators
        resolutionLogicStr = reminderModel["INTRNL_RSLTN_LGC_35"];
        nextEndPos = resolutionLogicStr.find(")"); # Expect each next token item to end with a closed paranthesis
        while nextEndPos > -1:
            nextToken = resolutionLogicStr[:nextEndPos+1];    # Excise apparent next token
            resolutionLogicStr = resolutionLogicStr[nextEndPos+1:];

            # Extract connecting operators if find & or ). If first character is "(" could be
            #   new open parantheses, but first check there is more than one in the token, or may just get the
            #   leading character of "(SEX)" or "(AGE)"
            while nextToken and ( nextToken[0] in ("&",")") or (nextToken[0] == "(" and nextToken.find("(",1) > -1) ):
                resolutionLogicStack.append( nextToken[0] );
                nextToken = nextToken[1:];  # Excise operator character

            # If previous logicItem without an interceding operator, indicates default OR logic?
            if resolutionLogicStack and isinstance(resolutionLogicStack[-1], dict):
                resolutionLogicStack.append("|");

            if nextToken: # Remaining string token to evaluate (not final end parantheses)
                # Extract NOT operator
                negateOp = nextToken[0] in ("'","!");
                if negateOp:
                    nextToken = nextToken[1:];

                # See if logicItem has a sub-index number by looking for open parantheses in middle of string
                logicType = re.sub(r"[^A-Za-z]","", nextToken);  # Default to just taking alphabetical characters of token
                logicIndex = None;
                openParenPos = nextToken.find("(");
                if openParenPos > 0:   # NOT the whole token as item (i.e., (SEX) or (AGE)) so look for sub-index
                    logicIndex = int(nextToken[openParenPos+1:-1]);   # Expect index number to be between parantheses
                logicItem = {"negate": negateOp, "type": logicType, "index": logicIndex }

                resolutionLogicStack.append( logicItem );
            nextEndPos = resolutionLogicStr.find(")");

        reminderModel["resolutionLogicStack"] = resolutionLogicStack;

    def parseBaselineAgeModel(self, baselineAgeModel, reminderModel):
        """Pull out baseline age findings item data and deposit back into the given model in parsed / structured form
        """
        # Reminder frequency like 10Y -> 10 years or 30D -> 30 Days
        intervalCount = int(baselineAgeModel["RMNDR_FRQNCY_X01"][:-1]);
        intervalChar = baselineAgeModel["RMNDR_FRQNCY_X01"][-1].lower();
        intervalStr = INTERVAL_CHAR_TO_STR[intervalChar];
        baselineAgeModel["intervalCount"] = intervalCount;
        baselineAgeModel["intervalStr"] = intervalStr;

    def parseFindingsModel(self, findingsModel, reminderModel, conn):
        """Pull out findings item data and deposit back into the given findings model
        """
        findingIndex = findingsModel["IEN"].split("_",1)[0];   # Pull out index, e.g., 2 from "2_116"
        itemStr = findingsModel["FNDNG_ITM_X01"];   # For example, "53;PXRMD(811.5,"
        (findingIEN, remainderStr) = itemStr.split(";", 1); # E.g., 53
        (findingType, tableListStr) = remainderStr.split("(",1); # E.g., PXRMD

        findingsModel["findingIndex"] = int(findingIndex);
        findingsModel["findingIEN"] = int(findingIEN);
        findingsModel["type"] = findingType;
        findingsModel["SITECODE"] = reminderModel["SITECODE"];

        # Run preliminary query to extract data for Finding types PXRMD, PXD, ...
        if findingType == "PXRMD":
            findingsModel["subfindingModels"] = self.runPXRMDPreliminaryQuery(findingsModel, conn);
            for model in findingsModel["subfindingModels"]:
                self.parseFindingsModel(model, reminderModel, conn);

        if findingType == "PXD":
            # Run preliminary query & store ICD ranges in finding model
            findingsModel["icdCodeRanges"] = self.runPXDPreliminaryQuery(findingsModel, conn);

        if "USE_IN_RSLTN_LGC_7" in findingsModel:
            findingsModel["useInLogic"] = findingsModel["USE_IN_RSLTN_LGC_7"];
        if "USE_IN_PTNT_CHRT_GC_8" in findingsModel:
            if findingsModel["USE_IN_PTNT_CHRT_GC_8"] != "":
                findingsModel["useInLogic"] = findingsModel["USE_IN_PTNT_CHRT_GC_8"];

    def runPXDPreliminaryQuery(self, findingsModel, conn):
        # Runs a preliminary query on PXD Finding to extract ICD code
        # ranges.

        query = SQLQuery();
        query.addSelect("*");
        query.addFrom("SLCTD_CDS_811X23");
        query.addWhereEqual("P_IEN", findingsModel["findingIEN"]);
        query.addWhereEqual("SITECODE", findingsModel["SITECODE"]);
        query.addOrderBy("IEN");

        resultTable = DBUtil.execute(query, includeColumnNames=True, conn=conn);
        resultModels = modelListFromTable(resultTable)

        # Extract out detail data item values
        icdCodeRanges = list();
        for resultModel in resultModels:
            # Pull out ICD codes from string like "Copy from ICD range 428.0 to 428.0"
            if resultModel["TRM_CD_X01"].startswith("Copy from"):
                endStr = resultModel["TRM_CD_X01"][len("Copy from ICD range "):];   # Remove prefix statement
                icdCodeRange = tuple(endStr.split(" to ")); # Extract out a list like ["428.0","428.0"];
                icdCodeRanges.append(icdCodeRange);

        return icdCodeRanges;

    def runPXRMDPreliminaryQuery(self, findingsModel, conn):
        # Runs a preliminary query on PXRMD Finding to extract list of
        # subfindings.

        # TODO: make preliminary query recursive for cases where
        # subfinding is also PXRMD type.

        query = SQLQuery();
        query.addSelect("*");
        query.addFrom("RMNDR_TERM_FNDNGS_811x52");
        query.addWhereEqual("P_IEN", findingsModel["findingIEN"]);
        query.addWhereEqual("SITECODE", findingsModel["SITECODE"]);
        query.addOrderBy("IEN");

        resultTable = DBUtil.execute(query, includeColumnNames=True, conn=conn);
        return modelListFromTable(resultTable);


def main():
    SITECODE = "640"
    IEN = "640046"

    snap = ReminderSnapshot();
    snap.convertReminder(SITECODE, IEN);

    #(cohortLogic, resolutionLogic, combineQuery) = self.converter.convertReminder(queryData[SITECODE], IEN);



if __name__ == "__main__":
    main();
