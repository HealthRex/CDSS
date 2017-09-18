#!/usr/bin/env python

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
from medinfo.dataconversion.Taxonomy import *
from medinfo.dataconversion.taxonomyData.TaxonomyReader import *
from medinfo.dataconversion.FunctionFinding import *

# Target database DSN to eventually apply generated queries to
TARGET_DB_DSN = "ORD_Chan_201406081D";
# Here. There.
# Map reminder frequency interval characters (e.g., d, m, y) into SQL date parameter strings
INTERVAL_CHAR_TO_STR = \
{   "d": "day",
    "m": "month",
    "y": "year",
};

# Stores Taxonomy Objects to be used when taxonomy findings need
# further pre-processing (taxonomy stored as text, not value range).
# Taxonomy class described in Taxonomy module.
tr = TaxonomyReader()
TAXONOMIES = tr.createTaxonomyMapping();


class VAReminderToQuery:
    """Data conversion module to
    Read through VA reminder database and parse out contents
    and translate into an executable (SQL) query to identify which
    patients satisfied the reminder on what dates.
    """
    conn = None; # Database connection to read from

    def __init__(self):
        """Default constructor"""
        self.connFactory = DBUtil.ConnectionFactory();  # Default connection source, but Allow specification of alternative DB connection source

    def convertReminder(self, siteCode, reminderIEN):
        """Query for just reminder logic. Simply reuse code from querying for multiple at a time."""
        return list(self.convertReminders(siteCode, [reminderIEN]))[0]; # Assume will generate a list of size 1 and return only result

    def convertReminders(self, siteCode, reminderIENs):
        """Given an individual siteCode and collection of reminderIENs to identify particular reminders,
        query out the relevant information in the source reminder database and stitch together
        data relationships to translate each reminder into SQL queries for the
        cohort, resolution, and combination logic / SQL strings, returned as a list of 3-ples.

        Start with simple design, query for all results in memory, but if too massive on full dataset,
        convert to streaming query ordered by reminder IEN so can synchronously step through each linked table together
        """


        print 'siteCode = ' + str(siteCode);
        print 'reminderIEN = ' + str(reminderIENs)

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
                BGNNG_DT_TM_9, ENDNG_DT_TM_12, MH_SCL_13
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

            # Core function findings query in parallel
            query = SQLQuery();
            query.addSelect\
            ("""P_IEN, IEN, SITECODE,
                FNCTN_FNDNG_NO_X01,
                FNCTN_STR_3, LGC_10,
                MIN_AGE_13, MAX_AGE_14,
                RMNDR_FRQNCY_15, RNK_FRQNCY_16,
                USE_IN_RSLTN_LGC_11,
                USE_IN_PTNT_CHRT_LGC_12
                """
            );
            query.addFrom("FNCTN_FNDNGS_811X925");
            query.addWhereEqual("SITECODE", siteCode );
            query.addWhereIn("P_IEN", reminderIENs );
            query.addOrderBy("P_IEN");
            query.addOrderBy("SITECODE");
            query.addOrderBy("IEN");

            # Execute core function findings query in parallel cursor
            functionFindingsCursor = conn.cursor();
            functionFindingsCursor.execute(str(query), query.params)
            lastFunctionFindingsModel = {"P_IEN":-1, "SITECODE": -1}

            # Iterate through main reminder rows one at a time
            for reminderRow in reminderCursor:
                reminderModel = RowItemModel(reminderRow, reminderCols);

                self.parseReminderModel(reminderModel);
                lastBaselineAgeModel = self.appendBaselineAgeFindingsModel(reminderModel, baselineAgeCursor, lastBaselineAgeModel);
                lastFindingsModel = self.appendFindingsModel(reminderModel, findingsCursor, lastFindingsModel, conn=conn);
                lastFunctionFindingsModel = self.appendFunctionFindingsModel(reminderModel, functionFindingsCursor, lastFunctionFindingsModel, conn=conn)

                cohortLogic = self.buildLogic(reminderModel, True);
                resolutionLogic = "" #self.buildLogic(reminderModel, False);
                combineQuery = "" #self.buildCombineQuery(reminderModel);



                yield (cohortLogic, resolutionLogic, combineQuery); # Yield / return one result at a time
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

    def appendFunctionFindingsModel(self, reminderModel, functionFindingsCursor, lastFunctionFindingsModel, conn):
        """Find rows in functionFindingsCursor pertaining to the given reminderModel
        and add them on as a child list. Assumes the cursor is sorted by P_IEN and SITECODE.
        """
        functionFindingsModels = list();

        while lastFunctionFindingsModel is not None and \
            (   lastFunctionFindingsModel["P_IEN"] <= reminderModel["IEN"] and \
                lastFunctionFindingsModel["SITECODE"] <= reminderModel["SITECODE"]
            ):

            if  (   lastFunctionFindingsModel["P_IEN"] == reminderModel["IEN"] and \
                    lastFunctionFindingsModel["SITECODE"] == reminderModel["SITECODE"]
                ):

                self.parseFunctionFindingsModel(lastFunctionFindingsModel, reminderModel, conn=conn);
                functionFindingsModels.append(lastFunctionFindingsModel);

            lastFunctionFindingsModel = DBUtil.nextRowModel(functionFindingsCursor);

        reminderModel["functionFindingsModels"] = functionFindingsModels;
        return lastFunctionFindingsModel;

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
            while nextToken and ( nextToken[0] in ("&",")", "!") or (nextToken[0] == "(" and nextToken.find("(",1) > -1) ):
                cohortLogicStack.append( nextToken[0] );
                nextToken = nextToken[1:];  # Excise operator character

            # If previous logicItem without an interceding operator, indicates default OR logic?
            if cohortLogicStack and isinstance(cohortLogicStack[-1], dict):
                cohortLogicStack.append("|");

            if nextToken: # Remaining string token to evaluate (not final end parantheses)
                # Extract NOT operator
                negateOp = nextToken[0] in ("'");
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
            while nextToken and ( nextToken[0] in ("&",")", "!") or (nextToken[0] == "(" and nextToken.find("(",1) > -1) ):
                resolutionLogicStack.append( nextToken[0] );
                nextToken = nextToken[1:];  # Excise operator character

            # If previous logicItem without an interceding operator, indicates default OR logic?
            if resolutionLogicStack and isinstance(resolutionLogicStack[-1], dict):
                resolutionLogicStack.append("|");

            if nextToken: # Remaining string token to evaluate (not final end parantheses)
                # Extract NOT operator
                negateOp = nextToken[0] in ("'");
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
        if "MH_SCL_13" in findingsModel:
            findingsModel["scale"] = findingsModel["MH_SCL_13"]
        if "CNDTN_14" in findingsModel:
            findingsModel["condition"] = findingsModel["CNDTN_14"]

        # Run preliminary query to extract data for Finding types PXRMD, PXD, ...
        if findingType == "PXRMD":
            findingsModel["subfindingModels"] = self.runPXRMDPreliminaryQuery(findingsModel, conn);
            for model in findingsModel["subfindingModels"]:
                self.parseFindingsModel(model, reminderModel, conn);
                model["merged"] = False
                model["scale"] = model["MH_SCALE_13"]

        if findingType == "PXD":
            # Run preliminary query & store ICD ranges in finding model
            findingsModel["taxonomies"] = self.runPXDPreliminaryQuery(findingsModel, conn);

        if "USE_IN_RSLTN_LGC_7" in findingsModel:
            findingsModel["useInLogic"] = findingsModel["USE_IN_RSLTN_LGC_7"];
        if "USE_IN_PTNT_CHRT_GC_8" in findingsModel:
            if findingsModel["USE_IN_PTNT_CHRT_GC_8"] != "":
                findingsModel["useInLogic"] = findingsModel["USE_IN_PTNT_CHRT_GC_8"];

    def parseFunctionFindingsModel(self, functionFindingsModel, reminderModel, conn):
        """Pull out findings item data and deposit back into the given findings model

            P_IEN, IEN, SITECODE,
            FNCTN_FNDNG_NO_X01,
            FNCTN_STR_3, LGC_10,
            MIN_AGE_13, MAX_AGE_14,
            RMNDR_FRQNCY_15, RNK_FRQNCY_16,
            USE_IN_RSLTN_LGC_11,
            USE_IN_PTNT_CHRT_LGC_12
        """
        findingIndex = functionFindingsModel["IEN"].split("_",1)[0];   # Pull out index, e.g., 2 from "2_116"
        functionFindingsModel["functionFindingIndex"] = findingIndex
        functionFindingsModel["logicClause"] = LogicClause(functionFindingsModel["FNCTN_STR_3"])

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
        taxonomies = list()
        for resultModel in resultModels:
            codeString = resultModel["TRM_CD_X01"]
            # Pull out codes from string like "Copy from [codeType] range 428.0 to 428.0"
            pattern = re.compile(r'Copy from (.+) range (.+) to (.+)')
            match = re.findall(pattern, codeString)
            if match:
                codeType, startRange, endRange = match[0]
                newTaxonomy = Taxonomy(str(codeType)+"_"+str(startRange))
                newTaxonomy.addCodeRange((str(startRange), str(endRange)), codeType+"_range")
                taxonomies.append(newTaxonomy)
                continue
            # Pull out code ranges from string that only contains taxonomy name
            pattern = re.compile(r'(.*) \(imported\)')

            match = re.findall(pattern, resultModel["TRM_CD_X01"])
            if match:
                newTaxonomy = TAXONOMIES[str(match[0])]
                taxonomies.append(newTaxonomy)
                continue

        return taxonomies;

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

    def getFindingIndices(self, logicStack):
        """ Returns two dicts, one for findings and one for function findings,
            where keys are finding indices and
            values are the finding's negation indicator.
        """
        indices = dict(); # stores finding indices and negation
        ffIndices = dict(); # store function finding indices and negation
        for elem in logicStack:
            if "index" in elem:
                if elem["index"] > 0:
                    if elem["type"] == "FI":
                        indices[elem["index"]] = elem["negate"]
                    else:
                        ffIndices[elem["index"]] = elem["negate"]

        return indices, ffIndices

    def extractFunctionType(self, ffModel):
        # Parses Function Finding function string to determine function type
        # currently assumes MRD
        # TODO: actually parse
        return "MRD"

    def extractExtraFindingIndices(self, findingIndices, ffModel):
        # Parses function string to determine if any additional
        # findings are needed for the computed finding.
        # Currently, only works for MRD Function Findings
        # TODO: Add functionality for other types of Function Findings?
        functionString = ffModel["FNCTN_STR_3"]
        pattern = re.compile(r'MRD\(([0-9]+)\)')
        matches = re.findall(pattern, functionString)
        extraIndices = dict()
        if matches:
            for m in matches:
                if int(m) not in findingIndices:
                    extraIndices[int(m)] = ffModel['negate']

        return extraIndices

    def createFindingObjects(self, reminderModel, logicStack):
        # Returns four containers:
        #   1) findingIndices - dict with finding index keys and corresponding negation boolean values
        #   2) findings - dict with finding index keys and corresponding Finding objects
        #   3) ffIndices - dict with function finding index keys and corresponding negation boolean values
        #   4) functionFindings - dict with function finding index keys and corresponding FunctionFinding objects

        findingIndices, ffIndices = self.getFindingIndices(logicStack);

        functionFindings = dict()
        for ffModel in reminderModel["functionFindingsModels"]:
            idx = ffModel["functionFindingIndex"]
            if int(idx) in ffIndices:
                ffModel["negate"] = ffIndices[int(idx)]
                extraIndices = self.extractExtraFindingIndices(findingIndices, ffModel)
                for key in extraIndices:
                    findingIndices[key] = extraIndices[key]
                #ffTypeName = self.extractFunctionType(ffModel) + "FunctionFinding"
                newFunctionFinding = FunctionFinding(ffModel);
                functionFindings[idx] = newFunctionFinding

        findings = dict();
        for findingModel in reminderModel["findingsModels"]:
            idx = findingModel["findingIndex"]
            if idx in findingIndices:
                findingModel["negate"] = findingIndices[idx]
                findingTypeName = findingModel["type"] + "Finding";
                newFinding = getattr(Finding, findingTypeName)(findingModel);
                findings[findingModel["findingIndex"]] = newFinding;

        return (findingIndices, findings, ffIndices, functionFindings)

    def writeFindingQueries(self, findings):
        queries = dict();
        for idx in findings:
            queries[idx] = findings[idx].writeSubquery(idx);
        return queries

    def writeFunctionFindingQueries(self, functionFindings,findings):
        queries = dict()
        for idx,ff in functionFindings.iteritems():
            queries[idx] = ff.writeSubquery(findings)
        return queries

    def combineFindingQueries(self, logicStack, indices, findings, findingQueries):
        # Creates Combo Finding Subqueries for Findings that are OR'ed in the logic
        """
        print "\n logicStack: "
        print logicStack
        print "\n findings: "
        print findings
        print "\n findingQueries: "
        print findingQueries
        """

        unionQueries = dict();
        unionTableName = "";
        unionTables = list();
        joinTableNames = dict();
        # for each finding in logicStack in reverse order to
        # determine which finding tables must be combined via Union
        # TODO: account for nested logic stacks
        for i in range(len(logicStack)-1,-1, -2):

            findingIndex = str(logicStack[i]["index"]);
            unionTableName = str(findingIndex) + "_" + unionTableName;
            unionTables = ["#ft"+findingIndex] + unionTables;

            onFirstFinding = i < 2;
            andIsNextOperator = i < 2;
            onNegatedFinding = findings[int(findingIndex)].negate
            if i > 1:
                if logicStack[i-2]["index"] is None:
                    onFirstFinding = True;
                if logicStack[i-1] not in ["|", "!"]:
                    andIsNextOperator = True;
            # if all findings have been processed, or
            # we reached an AND operator or
            # a negated finding
            if (onFirstFinding or andIsNextOperator or onNegatedFinding):
                if len(unionTables) > 1: # if we have multiple tables in current query

                    unionTableName = "#ft" + unionTableName[:len(unionTableName)-1];

                    unionString = ""
                    for j,table in enumerate(unionTables):
                        if j is not len(unionTables)-1:
                            unionString += "\nSELECT * FROM %s\nUNION" % (table);
                        else:
                            unionString += "\nSELECT * FROM %s\n" % table;
                    query = \
                    """IF Object_Id('tempdb..%(unionTableName)s') IS NOT NULL DROP TABLE %(unionTableName)s
                    SELECT Sta3n, DateTime, PatientSID, FindingIEN
                    INTO %(unionTableName)s
                    FROM (%(unionString)s) AS a """ % {"unionTableName": unionTableName, "unionString": unionString};

                    unionQueries[unionTableName] = query;
                    joinTableNames[unionTableName] = {"negate": onNegatedFinding, "andOperator": andIsNextOperator};

                else:   # if there is only one table in the current query
                    joinTableName = "#ft" + unionTableName[:len(unionTableName)-1];

                    joinTableNames[joinTableName] = {"negate": onNegatedFinding, "andOperator": andIsNextOperator};

                unionTableName = "";
                unionTables = list();

            if onFirstFinding:   break;

        return joinTableNames, unionQueries; # only works for Warfarin case

    def parseIndicesFromTableName(self, tableName):
        # returns list of finding indices represented in table name string input
        tempString = tableName;
        pattern = re.compile(r'#ft([0-9]+)(.*)');
        atEnd = False;
        relevantFindingIndices = list();
        while not atEnd:
            matches = re.findall(pattern, tempString)
            if matches:
                relevantFindingIndices.append(int(matches[0][0]));
                if matches[0][1] == "":
                    atEnd = True;
                else:
                    tempString = matches[0][1];
                    pattern = re.compile(r'_([0-9]+)(.*)');
        return relevantFindingIndices

    def parseTime(self, timeString):
        pattern = re.compile(r'([0-9]+)([A-Z]*)');
        matches = re.findall(pattern, timeString);
        if matches:
            return matches[0];
        raise StringFormatError(timeString);

    def timeToHours(self, value, unit):
        if unit == "hour" or unit == None:
            return value;
        multiplier = 24;
        if unit == "week":
            multiplier *= 7;
        elif unit == "month":
            multiplier *= 30;
        elif unit == "year":
            multiplier *= 365;
        return value * multiplier

    def computeTimeConstraint(self, joinTableName, findings, reminderModel):
        # Computes join criteria for time constraints of findings represented in join table given

        findingIndices = self.parseIndicesFromTableName(joinTableName);

        timeConstraintString = "v.VisitDateTime >= %s.DateTime" % joinTableName;

        timeConstraintValues = dict();
        timeUnitToSQLUnit = {"H": "hour", "D": "day", "W": "week", "M": "month", "Y": "year"};

        for idx in findingIndices:
            # TODO: account for PXRMD subfindings' specific IEN's and BGNNG_DT_TM_9

            # Skips Function Findings
            if idx not in findings:
                return ""

            finding = findings[idx];
            time = finding.startLookupTime
            # TODO: account for more than one baselineAgeModel
            if time == "":
                time = reminderModel["baselineAgeModels"][0]["RMNDR_FRQNCY_X01"]
            if time == "":
                continue

            timeValue, timeUnit = self.parseTime(time);

            if timeUnit == "": # Default unit is day
                timeUnit = "day";
            else:
                timeUnit = timeUnitToSQLUnit[timeUnit];

            # if we have multiple findings with the same type and IEN
            # use the greater of the two lookback time values
            if finding.findingIEN in timeConstraintValues:
                curValue = timeConstraintValues[finding.findingIEN][0]
                curUnit = timeConstraintValues[finding.findingIEN][1]
                if self.timeToHours(timeValue, timeUnit) < self.timeToHours(curValue, curUnit):
                    continue
            timeConstraintValues[finding.findingIEN] = (timeValue, timeUnit)


        clauses = list();

        if len(timeConstraintValues) > 1:
            for findingIEN, timeTuple in sorted(timeConstraintValues.iteritems()):
                clause = "(%(tableName)s.DateTime>=DATEADD(%(unit)s, -%(value)s, v.VisitDateTime) AND %(tableName)s.FindingIEN='%(findingIEN)s')" % {"tableName": joinTableName, "unit":timeTuple[1], "value": timeTuple[0], "findingIEN": findingIEN};
                clauses.append(clause)

            timeConstraintString += "\nAND (%s)" % str.join("\nOR ", clauses);

        elif len(timeConstraintValues) == 1:
            timeTuple = timeConstraintValues[timeConstraintValues.keys()[0]]
            clause = "%(tableName)s.DateTime>=DATEADD(%(unit)s, -%(value)s, v.VisitDateTime)" % {"tableName": joinTableName, "unit":timeTuple[1], "value": timeTuple[0]};
            timeConstraintString += "\nAND %s" % clause;

        return timeConstraintString

    def computeGenderConstraint(self, findings):
        raise NotImplementedError("Not yet implemented: computeGenderConstraint");

    def computeAgeConstraint(self, findings):
        raise NotImplementedError("Not yet implemented: computeAgeConstraint");

    def composeJoinCriteria(self, joinTableName, findings, reminderModel):
        # TODO: GENDER & AGE CONSTRAINTS
        timeConstraintString = self.computeTimeConstraint(joinTableName, findings, reminderModel);
        #genderConstraint = self.computeGenderConstraint(findings);
        #ageConstraint = self.computeAgeConstraint(findings);

        joinCriteria = """v.PatientSID=%(tableName)s.PatientSID AND v.Sta3n=%(tableName)s.Sta3n
        AND %(timeConstraintString)s""" \
        % {"tableName": joinTableName, "timeConstraintString": timeConstraintString};

        return joinCriteria;

    def buildLogic(self, reminderModel, isCohortLogic):
        # Start with empty list of query logic lines to construct
        logicLines = list();

        # Customize for cohort or resolution logics
        logicStack = None;
        mainSelectClause = "";
        mainFromClause = "";
        mainGroupByClause = "";
        if isCohortLogic:
            reminderModel["curLogicType"] = "Cohort";
            logicStack = reminderModel["cohortLogicStack"]
            mainSelectClause = "a.Sta3n, a.VisitSID, a.VisitDateTime, a.PatientSID, 1 AS Cohort";
            mainFromClause = "(\n" #")[%s].[Src].[Outpat_Visit] AS v" % TARGET_DB_DSN;
            mainGroupByClause = "a.Sta3n, a.VisitSID, a.VisitDateTime, a.PatientSID";
        else:
            reminderModel["curLogicType"] = "Resolution";
            logicStack = reminderModel["resolutionLogicStack"];
            mainSelectClause = "v.VisitSID, 1 AS Resolution";
            mainFromClause = "#Cohort_%(SITECODE)s_%(IEN)s AS v" % reminderModel;
            mainGroupByClause = "v.VisitSID";

        logicLines.append("-- %(curLogicType)s: SITECODE=%(SITECODE)s, IEN=%(IEN)s, %(NM_X01)s" % reminderModel);

        # Construct  logic subqueries for findings
        findingIndices, findings, ffIndices, functionFindings = self.createFindingObjects(reminderModel, logicStack);
        findingQueries = self.writeFindingQueries(findings);
        ffQueries = self.writeFunctionFindingQueries(functionFindings,findings)

        for idx,findingQuery in findingQueries.iteritems():
            logicLines.append(findingQuery);
        for idx,ff in ffQueries.iteritems():
            logicLines.append(ff)

        joinTableNames, finalSubqueries = self.combineFindingQueries(logicStack, findingIndices, findings, findingQueries);

        for idx in finalSubqueries:
            if len(idx) > 4:
                logicLines.append(finalSubqueries[idx]);

        mainTableName = "#%(curLogicType)s_%(SITECODE)s_%(IEN)s" % reminderModel;
        mainQuery = SQLQuery();
        mainQuery.setPrefix("IF Object_Id('tempdb..%(table)s') IS NOT NULL DROP TABLE %(table)s" % {"table": mainTableName} );
        mainQuery.addSelect(mainSelectClause);
        mainQuery.setInto(mainTableName);

        negatedTables = dict()
        innerMainQuery = SQLQuery()
        innerMainQuery.addSelect("v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID, 1 AS Cohort")
        innerMainQuery.addFrom("[ORD_Chan_201406081D].[Src].[Outpat_Visit] AS v")
        for joinTableName in sorted(joinTableNames.keys()):
            negated = joinTableNames[joinTableName]["negate"]

            joinCriteria = self.composeJoinCriteria(joinTableName, findings, reminderModel);
            joinType = "INNER"
            if negated:
                joinType = "LEFT"
                negatedTables[joinTableName] = joinTableNames[joinTableName]
            innerMainQuery.addJoin(joinTableName, joinCriteria, joinType);
        negatedTables_andOperator = list()
        negatedTables_orOperator = list()
        for table in sorted(negatedTables.keys()):
            if negatedTables[table]["andOperator"]:
                negatedTables_andOperator.append(table)
            else:
                negatedTables_orOperator.append(table)

        andString = str.join(" AND ", [x+".FindingIEN IS NULL" for x in negatedTables_andOperator])
        orString = str.join(" OR ", [x+".FindingIEN IS NULL" for x in negatedTables_orOperator])
        conjunctionString = "OR"
        if not orString:
            conjunctionString = ""
        if andString or conjunctionString:
            innerMainQuery.addWhere("(%s) %s %s" % (andString, conjunctionString, orString))

        mainFromClause += DBUtil.parameterizeQueryString(innerMainQuery) + "\n) AS a"
        mainQuery.addFrom(mainFromClause);

        if isCohortLogic:
            mainQuery.addWhereEqual("a.Sta3n", reminderModel["SITECODE"]);
        mainQuery.addGroupBy(mainGroupByClause);

        logicLines.append(DBUtil.parameterizeQueryString(mainQuery));

        # Stitch lines of each component into whole query logic strings
        logicStr = str.join("\n\n", logicLines);


        return logicStr;

    def applyFindingsToCohortQuery(self, mainCohortQuery, findingsModel, reminderModel):
        """Apply findings element as modifications to main cohort query
        (assuming any findings temporary tables already established)
        """
        if "tempTableName" in findingsModel:
            # Add join to temp table to select by the finding criteria
            criteriaLines = list();
            criteriaLines.append("v.PatientSID=%(tempTableName)s.PatientSID AND v.Sta3n=%(tempTableName)s.Sta3n" % findingsModel);
            criteriaLines.append("AND v.VisitDateTime >= %(tempTableName)s.FindingDateTime" % findingsModel);
            # Look for first baseline age model with reminder frequency to apply time threshold
            for baselineAgeModel in reminderModel["baselineAgeModels"]:
                print 'YES IM HERE'
                if "intervalStr" in baselineAgeModel:
                    findingsModel["intervalCount"] = baselineAgeModel["intervalCount"];
                    findingsModel["intervalStr"] = baselineAgeModel["intervalStr"];
                    criteriaLines.append("AND %(tempTableName)s.FindingDateTime >= DATEADD(%(intervalStr)s,-%(intervalCount)d,v.VisitDateTime)" % findingsModel );
                break;  # Only need to do it once
            criteria = str.join("\n", criteriaLines);
            mainCohortQuery.addJoin( findingsModel["tempTableName"], criteria, joinType="INNER");

    def buildCombineQuery(self, reminderModel):
        # Start with empty list of query logic lines to construct
        logicLines = list();
        logicLines.append("-- Combine: SITECODE=%(SITECODE)s, IEN=%(IEN)s, %(NM_X01)s" % reminderModel);

        query = SQLQuery();
        query.setPrefix("IF Object_Id('tempdb..#Visits_%(SITECODE)s_%(IEN)s') IS NOT NULL DROP TABLE #Visits_%(SITECODE)s_%(IEN)s" % reminderModel);
        query.addSelect("'%(SITECODE)s_%(IEN)s' AS Reminder, c.Sta3n, c.PatientSID, c.VisitSID, c.VisitDateTime, c.Cohort, CASE WHEN r.Resolution=1 THEN 1 ELSE 0 END AS Resolved" % reminderModel);
        query.setInto("#Visits_%(SITECODE)s_%(IEN)s" % reminderModel);
        query.addFrom("#Cohort_%(SITECODE)s_%(IEN)s AS c" % reminderModel);
        joinCriteria = "c.VisitSID=r.VisitSID";
        query.addJoin("#Resolution_%(SITECODE)s_%(IEN)s AS r" % reminderModel, joinCriteria, "LEFT");

        logicLines.append(DBUtil.parameterizeQueryString(query));

        # Stitch lines of each component into whole query logic strings
        logicStr = str.join("\n", logicLines );
        return logicStr;

    def main(self, argv):
        """Main method, callable from command line"""
        usageStr =  "usage: %prog [options]\n"
        parser = OptionParser(usage=usageStr)
        #parser.add_option("-s", "--startDate", dest="startDate", metavar="<startDate>",  help="Date string (e.g., 2011-12-15), if provided, will only run conversion on items with ordering time on or after this date.");
        #parser.add_option("-e", "--endDate", dest="endDate", metavar="<endDate>",  help="Date string (e.g., 2011-12-15), if provided, will only run conversion on items with ordering time before this date.");
        (options, args) = parser.parse_args(argv[1:])

        log.info("Starting: "+str.join(" ", argv))
        timer = time.time();
        #self.convertSourceItems(startDate,endDate);

        timer = time.time() - timer;
        log.info("%.3f seconds to complete",timer);

if __name__ == "__main__":
    instance = VAReminderToQuery();
    instance.main(sys.argv);
