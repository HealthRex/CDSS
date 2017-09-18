"""
Data Structure to store an instance of a Function Finding
and its data and write corresponding subqueries.
"""
import re
from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery;

class FunctionFinding():

    def __init__(self, ffModel):
        self.functionString = ffModel['FNCTN_STR_3']
        self.logicClause = ffModel['logicClause']
        self.index = ffModel['functionFindingIndex']
        self.minAge = ffModel['MIN_AGE_13']
        self.maxAge = ffModel['MAX_AGE_14']
        self.siteCode = ffModel['SITECODE']
        self.logicString = ffModel['LGC_10']

    def writeSubquery(self, findings):
        if self.logicClause.nested:
            return "FunctionFinding writeSubquery method cannot yet handle nested logic string."
        if 'MRD' in self.logicClause.logicString:
            return self.writeMRDSubquery(findings)

    def parseTime(self, timeString):
        timeUnitToSQLUnit = {"H": "hour", "D": "day", "W": "week", "M": "month", "Y": "year"};
        pattern = re.compile(r'([0-9]+)([A-Z]*)');
        matches = re.findall(pattern, timeString);
        if matches:
            timeValue,timeUnit = matches[0];
            if timeUnit == "": # Default unit is day
                timeUnit = "day";
            else:
                timeUnit = timeUnitToSQLUnit[timeUnit];
            return timeValue,timeUnit
        return None

    def writeMRDSubquery(self,findings):
        subqueries = list()
        # Case 1: MRD(<nums>)<operator>MRD(<nums>)
        #pattern = re.compile(r'(MRD)\(([0-9]+)\)(\'*)([>|<|=])(MRD)\(([0-9]+)\)')
        pattern = re.compile(r'(MRD)\(([0-9]+(,[0-9])*)\)(\'*)([>|<|=])(MRD)\(([0-9]+(,[0-9]+)*)\)')
        match = re.findall(pattern, self.logicClause.logicString)
        print '\n'+self.logicClause.logicString
        if match:
            subqueries = self.writeMRDSubquery_Case1(match,findings)

        # TODO: Additional cases

        # Compose final query
        query = SQLQuery()
        query.setPrefix("IF Object_Id('tempdb..#ff%s') IS NOT NULL DROP TABLE #ff%s" % (self.index, self.index))
        # TODO: account for multiple values on either side of function comparison
        query.addSelect("t1.Sta3n, t1.VisitSID, t1.VisitDateTime, t1.PatientSID")
        query.setInto("#ff%s" % (self.index))
        query.addFrom("#ff%s_ft1 AS t1" % (self.index))
        joinCriteria = "t1.VisitSID=t2.VisitSID AND t1.PatientSID=t2.PatientSID AND t1.ComputedDateTime>t2.ComputedDateTime"
        query.addJoin("#ff%s_ft2 AS t2" % (self.index), joinCriteria)
        subqueries += '\n\n' + DBUtil.parameterizeQueryString(query)
        return subqueries
        
    def writeMRDSubquery_Case1(self, match, findings):
        subqueries = list()
        a, leftVals,b,negate,operator,c,rightVals,d = match[0]
        findingIndices = str.split(str(leftVals),',') + str.split(str(rightVals),',')

        # for each involved finding
        for idx in findingIndices:
            subquery = SQLQuery()
            subquery.setPrefix("IF Object_Id('tempdb..#ff%(ffIdx)s_ft%(findingIdx)s') IS NOT NULL DROP TABLE #ff%(ffIdx)s_ft%(findingIdx)s" % {'ffIdx': str(self.index), 'findingIdx': str(idx)})
            if idx in leftVals:
                subquery.addSelect("v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID, MAX(f.DateTime) AS ComputedDateTime")
            else:
                subquery.addSelect("v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID, MAX(a.DateTime) AS ComputedDateTime")
            subquery.setInto("#ff%(ffIdx)s_ft%(findingIdx)s" % {'ffIdx': self.index, 'findingIdx': idx})
            subquery.addFrom("[ORD_Chan_201406081D].[Src].[Outpat_Visit] AS v")

            tempVar = 'f'
            if idx in rightVals:
                tempVar = 'a'
            joinCriteria = "v.PatientSID=%(tempVar)s.PatientSID AND v.Sta3n=%(tempVar)s.Sta3n AND v.Sta3n=640\n\
            AND v.VisitDateTime>%(tempVar)s.DateTime" % {'tempVar': tempVar}
            timeConstraint = self.parseTime(findings[int(idx)].startLookupTime)
            if timeConstraint is not None:
                timeValue,timeUnit = timeConstraint;
                joinCriteria += "\nAND %s.DateTime>DATEADD(%s, -%s, v.VisitDateTime)" % (tempVar, timeUnit, timeValue)
            joinTableClause = "#ft%s AS f"%(idx)
            if idx in rightVals:
                joinTableClause = \
                """(
                	SELECT * FROM #ft%(findingIdx)s AS f
                	UNION
                	SELECT v2.Sta3n, CAST(0 AS DATETIME) AS DateTime, v2.PatientSID, 0 AS FindingIEN
                	FROM [ORD_Chan_201406081D].[Src].[Outpat_Visit] AS v2
                	WHERE v2.PatientSID NOT IN (
                		SELECT f%(findingIdx)s.PatientSID
                		FROM #ft%(findingIdx)s AS f%(findingIdx)s
                	)
                ) AS a""" %{'findingIdx': idx}
            subquery.addJoin(joinTableClause,joinCriteria)
            subquery.addGroupBy("v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID")
            subqueries.append(DBUtil.parameterizeQueryString(subquery))
        return str.join('\n\n',subqueries)

class LogicClause():
    def __init__(self, logicString):
        self.logicString = logicString
        self.subLogicStack = list()
        self.subLogicClauses = dict()
        self.nested = self.decompose()

    def decompose(self):
        nested = '&' in list(self.logicString) or '!' in list(self.logicString)
        if not nested:
            return nested

        # decompose by paratheses groups
        groups = list()
        curStartIdx = 0
        count = 0
        containsComparisonOperator = False

        for i,ch in enumerate(self.logicString):
            if ch in ['>','<','=']:
                containsComparisonOperator = True
            elif ch in ['&','!'] and not containsComparisonOperator and count == 0:
                if i != curStartIdx:
                    nested = True
                    subLogicString = self.logicString[curStartIdx:i]
                    self.subLogicStack.append(subLogicString)
                    self.subLogicClauses[len(self.subLogicStack)-1] = LogicClause(subLogicString)
                self.subLogicStack.append(ch)
                curStartIdx = i+1
            elif ch == "(":
                count += 1
            elif ch == ")":
                count -= 1
                if count == 0 and containsComparisonOperator:
                    subLogicString = self.logicString[curStartIdx:i+1]

                    if subLogicString == self.logicString:
                        return self.__init__(subLogicString[1:-1])

                    self.subLogicStack.append(subLogicString)
                    self.subLogicClauses[len(self.subLogicStack)-1] = LogicClause(subLogicString)
                    containsComparisonOperator = False
                    curStartIdx = i+1
        return nested
