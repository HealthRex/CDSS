
from medinfo.db.Model import SQLQuery;
from medinfo.db import DBUtil;
from medinfo.db.Model import generatePlaceholders;
import re

# GLOBAL DATABASE TABLE NAMES
ORD_V_DIAG_DB = "[ORD_Chan_201406081D].[Src].[Outpat_VDiagnosis]"
ORD_VISIT_DB = "[ORD_Chan_201406081D].[Src].[Outpat_Visit]"
ORD_RX_DB = "[ORD_Chan_201406081D].[Src].[RxOut_RxOutpatFill]"
CDW_NATIONAL_DRUG_DB = "[CDWWork_FY14].[Dim].[NationalDrug]"
CDW_LOCAL_DRUG_DB = "[CDWWork_FY14].[Dim].[LocalDrug]"
ORD_CHEM_DB = "[ORD_Chan_201406081D].[Src].[Chem_PatientLabChem]"
ORD_HF = "[ORD_Chan_201406081D].[Src].[HF_HealthFactor]"
CDW_ICD9 = "[CDWWork_FY14].[Dim].[ICD9]"

class Finding:

    def __init__(self, findingModel):

        self.siteCode = findingModel["SITECODE"];
        #self.reminderIEN = findingModel["P_IEN"];
        self.findingIEN = findingModel["findingIEN"];
        self.queryValues = [findingModel["findingIEN"]]
        if 'queryValues' in findingModel:
            self.queryValues = findingModel['queryValues']

        self.findingIndex = findingModel["findingIndex"]

        # TODO: account for case when both time attributes are blank
        self.startLookupTime = findingModel["BGNNG_DT_TM_9"]
        if self.startLookupTime == "" and "RMNDR_FRQNCY_3" in findingModel:
            self.startLookupTime = findingModel["RMNDR_FRQNCY_3"]

        self.negate = False;
        if "negate" in findingModel:
            self.negate = findingModel["negate"];


    # Abstract Method to write subquery for specific Finding type.
    # Must be written by a Finding subclass.
    # writeSubquery methods will ultimately replace loadFindings[type]
    # methods from VAReminderToQuery.py.
    def writeSubquery(self, findingIndex): raise NotImplementedError("Override me.");

    # Abstract Method to write join query for specific Finding type.
    # Must be written by a Finding subclass.
    # writeSubquery methods will ultimately replace loadFindings[type]
    # methods from VAReminderToQuery.py.
    def writeJoinQuery(self): raise NotImplementedError("Override me.");

class AUTTHFFinding(Finding):
    # Finding for Health Factors
    def __init__(self, findingModel):
        Finding.__init__(self, findingModel);
        self.findingType = "AUTTHF";
        self.tableName = "[ORD_Chan_201406081D].[Src].[HF_HealthFactor]";
        self.targetColumn = "HealthFactorTypeIEN";

    def writeSubquery(self, findingIndex):
        query = SQLQuery();
        query.setPrefix("IF Object_Id('tempdb..#ft%(index)s') IS NOT NULL DROP TABLE #ft%(index)s" % {"index": findingIndex});
        query.addSelect("Sta3n, VisitDateTime AS DateTime, PatientSID, HealthFactorIEN AS FindingIEN");
        query.setInto("#ft%(index)s" % {"index": findingIndex});
        query.addFrom(ORD_HF);

        queryValueString = ", ".join([str(val) for val in sorted(self.queryValues)])
        query.addWhere("Sta3n=%(siteCode)s AND HealthFactorIEN IN (%(queryValueString)s)" % {"siteCode": self.siteCode, "findingIEN": self.findingIEN, "queryValueString": queryValueString});

        return DBUtil.parameterizeQueryString(query);

class PSFinding(Finding):
    # Finding for Drug Classes
    def __init__(self, findingModel):
        Finding.__init__(self, findingModel);
        self.findingType = "PS";
        self.tableName = "[CDWWork_FY14].[Dim].[DrugClass]"
        self.targetColumn = "DrugClassIEN"

    def createPSSubquery(self, table2Name, onTable2, joinCriteria2):
        query = SQLQuery();
        query.addSelect("t1.Sta3n, t1.RxOutpatFillSID, t1.FillDateTime AS DateTime, t1.PatientSID");
        query.addFrom("%s as t1" % ORD_RX_DB);

        joinCriteriaColumn1 = "PrimaryDrugClassSID"
        if onTable2:
            joinCriteriaColumn1 = "DrugClassSID"

        # add join
        query.addJoin(table2Name + " AS t2", joinCriteria2);

        # add second join
        placeholders = generatePlaceholders(len(self.queryValues));
        joinCriteria = "t2.%(joinCriteriaColumn1)s=t3.DrugClassSID AND t2.Sta3n=t3.Sta3n \
                    \nAND t3.%(targetColumn)s IN (%(values)s)" % {'values': placeholders, "joinCriteriaColumn1": joinCriteriaColumn1, "targetColumn": self.targetColumn};
        for val in self.queryValues:
            query.addParam(val);
        query.addJoin(self.tableName + " AS t3", joinCriteria);

        # where clause
        query.addWhere("t1.Sta3n=%(siteCode)s" % {"siteCode": self.siteCode});

        return query;

    def writeSubquery(self, findingIndex):
        joinCriteria = "t1.Sta3n=t2.Sta3n AND t1.NationalDrugSID=t2.NationalDrugSID"
        nationalDrugSubquery = self.createPSSubquery(CDW_NATIONAL_DRUG_DB, False, joinCriteria);
        joinCriteria = "t1.Sta3n=t2.Sta3n AND t1.LocalDrugSID=t2.LocalDrugSID"
        localDrugSubquery = self.createPSSubquery(CDW_LOCAL_DRUG_DB, True, joinCriteria);
        query1String = DBUtil.parameterizeQueryString(nationalDrugSubquery);
        query2String = DBUtil.parameterizeQueryString(localDrugSubquery);
        innerQueryString = query1String + '\n UNION \n' + query2String

        tableName = "#ft"+str(findingIndex);
        finalQueryString = "IF Object_Id('tempdb..%(tableName)s') IS NOT NULL DROP TABLE %(tableName)s" % {"tableName": tableName};
        finalQueryString += "\nSELECT Sta3n, DateTime, PatientSID";
        finalQueryString += "\n INTO %(tableName)s" % {"tableName": tableName};
        finalQueryString += "\n FROM (\n %(innerQuery)s \n) AS a" % {"innerQuery": innerQueryString};
        return finalQueryString;

class ORDFinding(Finding):
    # Finding for Orderable Items
    def __init__(self, findingModel):
        Finding.__init__(self, findingModel);
        self.findingType = "ORD";
        self.queryValues = [str(self.findingIEN)]

    def writeSubquery(self, findingIndex):
        query = SQLQuery();
        query.setPrefix("IF Object_Id('tempdb..#ft%(index)s') IS NOT NULL DROP TABLE #ft%(index)s" % {"index": findingIndex});
        query.addSelect("o.Sta3n, o.OrderStartDateTime AS DateTime, o.PatientSID, i.OrderableItemIEN AS FindingIEN");
        query.setInto("#ft%(index)s" % {"index": findingIndex});
        query.addFrom("[ORD_Chan_201406081D].[Src].[CPRSOrder_OrderedItem] AS o");

        # add join
        table2 = "[CDWWork_FY14].[Dim].[OrderableItem] AS i";
        joinCriteria = "o.Sta3n=i.Sta3n AND o.OrderableItemSID=i.OrderableItemSID"
        queryValueString = str.join(", ", self.queryValues);
        joinCriteria += " AND i.OrderableItemIEN IN (%(queryValueString)s)" % {"queryValueString": queryValueString};
        query.addJoin(table2, joinCriteria);

        # where clause
        query.addWhere("o.Sta3n=%(siteCode)s" % {"siteCode": self.siteCode});

        return DBUtil.parameterizeQueryString(query);

class PSDRUGFinding(Finding):
    # Finding for Drugs
    def __init__(self, findingModel):
        Finding.__init__(self, findingModel);
        self.findingType = "PSDRUG";

    def writePSDRUGJoinCriteria(self):
        joinCriteria = "t1.DrugNameWithoutDose=t2.DrugNameWithoutDose AND t1.Sta3n=t2.Sta3n "
        queryValueString = str.join(", ", [str(val) for val in self.queryValues]);
        joinCriteria += "AND t2.LocalDrugIEN IN (%(queryValueString)s)" % {"queryValueString": queryValueString};
        return joinCriteria

    def writeSubquery(self, findingIndex):
        query = SQLQuery();
        query.setPrefix("IF Object_Id('tempdb..#ft%(findingIndex)s') IS NOT NULL DROP TABLE #ft%(findingIndex)s" % {"findingIndex": findingIndex});
        query.addSelect("t1.Sta3n, t1.FillDateTime AS DateTime, t1.PatientSID, t2.LocalDrugIEN AS FindingIEN");
        query.setInto("#ft%(findingIndex)s" % {"findingIndex": findingIndex});
        query.addFrom(ORD_RX_DB + " AS t1");
        joinCriteria = self.writePSDRUGJoinCriteria();
        query.addJoin("[CDWWork_FY14].[Dim].[LocalDrug] AS t2", joinCriteria);
        query.addWhereEqual("t1.Sta3n", 640);
        return DBUtil.parameterizeQueryString(query);

class PXDFinding(Finding):
    # Finding for Taxonomy (ICD, ICP, or CPT Code Ranges)
    def __init__(self, findingModel):
        Finding.__init__(self, findingModel);
        self.findingType = "PXD";
        self.taxonomies = findingModel["taxonomies"]

    def writePXDJoinSubquery(self):
        allICD9Codes = list()
        allICPCodes = list()
        allCPTCodes = list()
        allICD9Ranges = list()
        allICPRanges = list()
        allCPTRanges = list()
        for t in self.taxonomies:
            allICD9Codes += ["\'%s\'" % code for code in t.ICD9Codes]
            allICPCodes += ["\'%s\'" % code for code in t.ICPCodes]
            allCPTCodes += ["\'%s\'" % code for code in t.CPTCodes]
            allICD9Ranges += [("\'%s\'" % code[0],"\'%s\'" % code[1]) for code in t.ICD9Ranges]
            allICPRanges += [("\'%s\'" % code[0], "\'%s\'" % code[1]) for code in t.ICPRanges]
            allCPTRanges += [("\'%s\'" % code[0],"\'%s\'" % code[1]) for code in t.CPTRanges]


        subquery = ""
        onfirstUnionQuery = True
        if allICD9Codes or allICD9Ranges:
            onfirstUnionQuery = False
            subquery += "SELECT Sta3n, ICD9SID as SID, ICD9Code as Code\n"
            subquery += "FROM [CDWWork_FY14].[Dim].[ICD9]\nWHERE "
            if allICD9Codes:
                subquery += "ICD9Code IN (%(codes)s)" % {"codes": str.join(", ", allICD9Codes)}
            if allICD9Ranges:
                for i,codeRange in enumerate(allICD9Ranges):
                    if i == 0 and not allICD9Codes:
                        subquery += "ICD9Code BETWEEN %s AND %s" % (codeRange[0], codeRange[1])
                    else:
                        subquery += "\nOR ICD9Code BETWEEN %s AND %s" % (codeRange[0], codeRange[1])
        if allICPCodes or allICPRanges:
            if not onfirstUnionQuery:
                onfirstUnionQuery = False
                subquery += "\nUNION\n"
            subquery += "SELECT Sta3n, ICD9ProcedureSID as SID, ICD9ProcedureCode as Code\n"
            subquery += "FROM [CDWWork_FY14].[Dim].[ICD9Procedure]\nWHERE "
            if allICPCodes:

                subquery += "ICD9ProcedureCode IN (%(codes)s)" % {"codes": str.join(", ", allICD9Codes)}
            if allICPRanges:
                for i,codeRange in enumerate(allICPRanges):
                    if i ==0 and not allICPCodes:
                        subquery += "ICD9ProcedureCode BETWEEN %s AND %s" % (codeRange[0], codeRange[1])
                    else:
                        subquery += "\nOR ICD9ProcedureCode BETWEEN %s AND %s" % (codeRange[0], codeRange[1])

        if allCPTCodes or allCPTRanges:
            if not onfirstUnionQuery:
                onfirstUnionQuery = False
                subquery += "\nUNION\n"
            subquery += "SELECT Sta3n, CPTSID as SID, CPTCode as Code\n"
            subquery += "FROM [CDWWork_FY14].[Dim].[CPT]\nWHERE "
            if allCPTCodes:
                subquery += "CPTCode IN (%(codes)s)" % {"codes": str.join(", ", allICD9Codes)}
            if allCPTRanges:
                for i,codeRange in enumerate(allCPTRanges):
                    if i == 0 and not allCPTCodes:
                        subquery += "CPTCode BETWEEN %s AND %s" % (negationString, codeRange[0], codeRange[1])
                    else:
                        subquery += "\nOR CPTCode BETWEEN %s AND %s" % (conjunctionString, negationString, codeRange[0], codeRange[1])

        return subquery

    def writeSubquery(self, findingIndex):
        #[CDWWork_FY14].[Dim].[ICD9]	ICD9Code	(TbVDiag JOIN T2)^(1) on OUT(T1 on $)^(2)
        query = SQLQuery();
        query.setPrefix("IF Object_Id('tempdb..#ft%(findingIndex)s') IS NOT NULL DROP TABLE #ft%(findingIndex)s" % {"findingIndex": findingIndex});
        query.addSelect("t1.Sta3n, t1.VDiagnosisDateTime AS DateTime, t1.PatientSID, \'%s\' AS FindingIEN" % self.findingIEN);
        query.setInto("#ft%(findingIndex)s" % {"findingIndex": findingIndex});
        query.addFrom(ORD_V_DIAG_DB + " AS t1");

        joinCriteria = "t1.ICDSID=i.SID AND t1.Sta3n=i.Sta3n"
        query.addJoin("(\n"+self.writePXDJoinSubquery()+"\n) AS i", joinCriteria);

        query.addWhereEqual("t1.Sta3n", 640);

        return DBUtil.parameterizeQueryString(query);

class PSNDFFinding(Finding):
    # Finding for Generic Drugs
    def __init__(self, findingModel):
        Finding.__init__(self, findingModel);
        self.findingType = "PSNDF";
        self.tableName = "[CDWWork_FY14].[Dim].[DrugNameWithoutDose]";
        self.targetColumn = "DrugNameWithoutDoseIEN";

    def createPSNDFSubquery(self, table2, joinCriteria2):
        query = SQLQuery();
        query.addSelect("t1.Sta3n, t1.RxOutpatFillSID, t1.FillDateTime AS DateTime, t1.PatientSID, t3.DrugNameWithoutDoseIEN AS FindingIEN");
        query.addFrom("%s as t1" % ORD_RX_DB);

        # add join
        query.addJoin(table2 + " AS t2", joinCriteria2);

        # add second join
        placeholders = generatePlaceholders(len(self.queryValues));
        joinCriteria = "t2.DrugNameWithoutDoseSID=t3.DrugNameWithoutDoseSID AND t2.Sta3n=t3.Sta3n \
                    \nAND t3."+ self.targetColumn+ " IN (%(values)s)" % {'values': placeholders};
        for val in self.queryValues:
            query.addParam(val);
        query.addJoin(self.tableName + " AS t3", joinCriteria);

        # where clause
        query.addWhere("t1.Sta3n=%(siteCode)s" % {"siteCode": self.siteCode});

        return query;

    def writeSubquery(self, findingIndex):
        joinCriteria = "t1.Sta3n=t2.Sta3n AND t1.NationalDrugSID=t2.NationalDrugSID"
        nationalDrugSubquery = self.createPSNDFSubquery(CDW_NATIONAL_DRUG_DB, joinCriteria);
        #joinCriteria = "t1.Sta3n=t2.Sta3n AND t1.LocalDrugSID=t2.LocalDrugSID"
        #localDrugSubquery = self.createPSNDFSubquery(CDW_LOCAL_DRUG_DB, joinCriteria);
        query1String = DBUtil.parameterizeQueryString(nationalDrugSubquery);
        #query2String = DBUtil.parameterizeQueryString(localDrugSubquery);
        # removed localDrug table since leads to duplicates
        innerQueryString = query1String #+ '\n UNION \n' + query2String

        tableName = "#ft"+str(findingIndex);
        finalQueryString = "IF Object_Id('tempdb..%(tableName)s') IS NOT NULL DROP TABLE %(tableName)s" % {"tableName": tableName};
        finalQueryString += "\nSELECT Sta3n, DateTime, PatientSID, FindingIEN";
        finalQueryString += "\n INTO %(tableName)s" % {"tableName": tableName};
        finalQueryString += "\n FROM (\n %(innerQuery)s \n) AS a" % {"innerQuery": innerQueryString};
        return finalQueryString;

class LABFinding(Finding):
    # Finding for Lab Results
    def __init__(self, findingModel):
        Finding.__init__(self, findingModel);
        self.findingType = "LAB";
        self.tableName = "[CDWWork_FY14].[Dim].[LabChemTest]";
        self.targetColumn = "LabChemTestIEN";

    def writeSubquery(self, findingIndex):
        #[CDWWork_FY14].[Dim].[LabChemTest]	LabChemTestIEN	(TbChem JOIN T2)
        query = SQLQuery();
        query.setPrefix("IF Object_Id('tempdb..#ft%(index)s') IS NOT NULL DROP TABLE #ft%(index)s" % {"index": findingIndex});
        query.addSelect("t1.Sta3n, t1.LabChemSpecimenDateTime AS DateTime, t1.PatientSID, t2.LabChemTestIEN AS FindingIEN");
        query.setInto("#ft%(index)s" % {"index": findingIndex});
        query.addFrom("%s as t1" % ORD_CHEM_DB);

        # add join
        queryValueString = ", ".join([str(val) for val in sorted(self.queryValues)])
        joinCriteria = "t1.LabChemTestSID=t2.LabChemTestSID AND t1.Sta3n=t2.Sta3n \
                    \nAND t2."+ self.targetColumn+ " IN (%(queryValueString)s)" % {'queryValueString': queryValueString};
        query.addJoin(self.tableName + " AS t2", joinCriteria);

        query.addWhere("t1.Sta3n=%(siteCode)s" % {"siteCode": self.siteCode});

        return DBUtil.parameterizeQueryString(query);

class PXRMDFinding(Finding):
    # Finding for Term Findings (as in List of Findings)
    # This is specifically Finding type PXRMDF(811.5
    def __init__(self, findingModel):
        Finding.__init__(self, findingModel);
        self.findingType = "PXRMD";
        self.subfindingModels = findingModel["subfindingModels"];

    def mergeFindingModels(self, model1, model2):
        """print "\n Merged models: \n"
        print '\n'
        print model1
        print model2
        """
        mergedModel = model1
        #if mergedModel["merged"]:
        mergedModel["queryValues"] += model2["queryValues"]

        mergedModel["merged"] = True
        return mergedModel

    def writeSubquery(self, findingIndex):
        # Writes the queries associated with given PXRMD Finding
        queryLines = list();

        # Construct subqueries for list findings
        tempSubFindingModels = dict()
        curYTTModelIdx = 0
        for model in self.subfindingModels:
            findingType = model["type"]
            model["queryValues"] = [model["findingIEN"]]
            model["negate"] = self.negate
            if findingType in tempSubFindingModels:# and findingType != "YTT":
                if findingType == "YTT":
                    tempSubFindingModels[findingType].append(model)
                else:
                    tempSubFindingModels[findingType] = self.mergeFindingModels(tempSubFindingModels[findingType], model)
            else:
                if findingType == "YTT":
                    tempSubFindingModels[findingType] = [model]
                else:
                    tempSubFindingModels[findingType] = model

        subtableNames = list();
        self.subFindingModels = tempSubFindingModels
        for findingType, findingModel in sorted(self.subFindingModels.iteritems()):
            if findingType == "YTT":
                subfindingObjects = list()
                for submodel in findingModel:
                    subfindingObjects.append(eval(findingType+"Finding")(submodel))
                sq = writeYTTSubquery(subfindingObjects,str(findingIndex))
                queryLines.append(sq)
                subtableNames.append("#ft"+ str(findingIndex) + "_sf_" + findingType);
            else:
                findingObject = eval(findingType+"Finding")(findingModel);
                sq = findingObject.writeSubquery(str(findingIndex) + "_sf_" + findingType)
                queryLines.append(sq)
                subtableNames.append("#ft"+ str(findingIndex) + "_sf_" + findingType);

        # Construct final union query
        query = SQLQuery();
        query.setPrefix("IF Object_Id('tempdb..#ft%(findingIndex)s') IS NOT NULL DROP TABLE #ft%(findingIndex)s" % {"findingIndex": findingIndex});
        query.addSelect("f.Sta3n, f.DateTime, f.PatientSID, f.FindingIEN");
        query.setInto("#ft%(findingIndex)s" % {"findingIndex": findingIndex});
        fromString = "(\n"
        for i,subtable in enumerate(subtableNames):
            if i > 0:
                fromString += "\nUNION\n"
            fromString += "SELECT * FROM %s" % subtable
        fromString += "\n) AS f"
        query.addFrom(fromString);

        queryLines.append(DBUtil.parameterizeQueryString(query));

        # Skips Function findings
        #print queryLines
        #if queryLines == None:
        #    return ""

        return str.join("\n\n", queryLines);

class AUTTEDTFinding(Finding):
    # Finding for Education Topics
    def __init__(self, findingModel):
        Finding.__init__(self, findingModel);
        self.findingType = "AUTTEDT";

    def writeSubquery(self, findingIndex):
        print "AUTTEDTFinding writeSubquery method unwritten! "
        return "AUTTEDTFinding writeSubquery method unwritten! "

class AUTTEXAMFinding(Finding):
    # Finding for Exams
    def __init__(self, findingModel):
        Finding.__init__(self, findingModel);
        self.findingType = "AUTTEXAM";
        self.targetTable = "[ORD_Chan_201406081D].[Src].[Outpat_VExam]"

    def writeSubquery(self, findingIndex):

        query = SQLQuery();
        query.setPrefix("IF Object_Id('tempdb..#ft%(index)s') IS NOT NULL DROP TABLE #ft%(index)s" % {"index": findingIndex});
        query.addSelect("t1.Sta3n, t1.VExamDateTime AS DateTime, t1.PatientSID, t2.ExamIEN AS FindingIEN");
        query.setInto("#ft%(index)s" % {"index": findingIndex});
        query.addFrom(self.targetTable + " AS t1");

        queryValueString = ", ".join([str(val) for val in sorted(self.queryValues)])
        joinCriteria = "t1.Sta3n=640 AND t1.Sta3n=t2.Sta3n AND t1.ExamSID=t2.ExamSID\n"
        joinCriteria += "AND t2.ExamIEN IN (%s)" % (queryValueString)
        query.addJoin("[CDWWork_FY14].[Dim].[Exam] AS t2", joinCriteria)

        return DBUtil.parameterizeQueryString(query);

class AUTTIMMFinding(Finding):
    # Finding for Immunizations
    def __init__(self, findingModel):
        Finding.__init__(self, findingModel);
        self.findingType = "AUTTIMM";

    def writeSubquery(self, findingIndex):
        print "AUTTIMMFinding writeSubquery method unwritten! "
        return "AUTTIMMFinding writeSubquery method unwritten! "

def writeYTTSubquery(subfindings, findingIndex):
    query = SQLQuery()
    query.setPrefix("IF Object_Id('tempdb..#ft%s_sf_YTT') IS NOT NULL DROP TABLE #ft%s_sf_YTT" % (findingIndex, findingIndex))
    query.addSelect("a.Sta3n, a.DateTime, a.PatientSID, a.FindingIEN")
    query.setInto("#ft%s_sf_YTT" % findingIndex)
    fromClauseList = list()
    for subfinding in subfindings:
        fromClauseList.append(subfinding.writeSubquery())
    fromClause = '(\n'+ str.join('\nUNION\n', fromClauseList) + '\n) AS a'
    query.addFrom(fromClause)
    return DBUtil.parameterizeQueryString(query)

class YTTFinding(Finding):
    # Finding for Mental Health Tests
    def __init__(self, findingModel):
        Finding.__init__(self, findingModel);
        self.findingType = "YTT";
        self.scale = findingModel["scale"]
        self.hasCondition = False
        if "condition" in findingModel:

            condition = str(findingModel["CNDTN_14"])
            pattern = re.compile(r'I \+V([\']*)([<|>|=])([0-9]+)')
            match = re.findall(pattern, condition)
            if match:
                isNot, operator, value = match[0]
                condition = operator+value
                if isNot:
                    if operator == '=':
                        condition = "!="+value
                    if operator == ">":
                        condition = "<="+value
                    if operator == "<":
                        condition = ">="+value
                findingModel["condition"] = condition #match[0]
                self.condition = findingModel["condition"]
                self.hasCondition = True

    def writeSubquery(self):
        query = SQLQuery();
        query.addSelect("s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyResultIEN AS FindingIEN");
        query.addFrom("[ORD_Chan_201406081D].[Src].[MH_SurveyResult] AS s");
        joinCriteria = "s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND ss.SurveyScaleIEN=%s" %(self.scale)
        if self.hasCondition:
            joinCriteria += " AND s.RawScore%s" % (self.condition)
        queryValueString = ", ".join([str(val) for val in sorted(self.queryValues)])
        query.addJoin("[CDWWork_FY14].[Dim].[SurveyScale] AS ss", joinCriteria)
        queryValueString = ", ".join([str(val) for val in sorted(self.queryValues)])
        whereString = "s.Sta3n=%(siteCode)s AND s.SurveySID IN (%(queryValueString)s)" % {"siteCode": self.siteCode, "findingIEN": self.findingIEN, "queryValueString": queryValueString};
        query.addWhere(whereString)
        return DBUtil.parameterizeQueryString(query);

class RAMISFinding(Finding):
    # Finding for Radiology Procedures
    def __init__(self, findingModel):
        Finding.__init__(self, findingModel);
        self.findingType = "RAMIS";

    def writeSubquery(self, findingIndex):
        print "RAMISFinding writeSubquery method unwritten! "
        return "RAMISFinding writeSubquery method unwritten! "

class AUTTSKFinding(Finding):
    # Finding for Skin Tests
    def __init__(self, findingModel):
        Finding.__init__(self, findingModel);
        self.findingType = "AUTTSK";

    def writeSubquery(self, findingIndex):
        print "AUTTSKFinding writeSubquery method unwritten! "
        return "AUTTSKFinding writeSubquery method unwritten! "

class GMRDFinding(Finding):
    # Findings for Vitals
    def __init__(self, findingModel):
        Finding.__init__(self, findingModel);
        self.findingType = "GMRD";
        self.tableName = "";

    def writeSubquery(self, findingIndex):
        query = SQLQuery();
        query.setPrefix("IF Object_Id('tempdb..#ft%(index)s') IS NOT NULL DROP TABLE #ft%(index)s" % {"index": findingIndex});
        query.addSelect("t1.Sta3n, t1.VitalSignTakenDateTime AS DateTime, t1.PatientSID, t2.VitalTypeIEN AS FindingIEN");
        query.setInto("#ft%(index)s" % {"index": findingIndex});
        query.addFrom("[ORD_Chan_201406081D].[Src].[Vital_VitalSign] AS t1")

        queryValueString = ", ".join([str(val) for val in sorted(self.queryValues)])
        joinCriteria = "t1.Sta3n=t2.Sta3n AND t1.VitalTypeSID=t2.VitalTypeSID AND t2.VitalTypeIEN IN (%(queryValueString)s)" % {"siteCode": self.siteCode, "findingIEN": self.findingIEN, "queryValueString": queryValueString};
        query.addJoin("[CDWWork_FY14].[Dim].[VitalType] AS t2", joinCriteria)

        query.addWhere("t1.Sta3n=%(siteCode)s" % {'siteCode': self.siteCode})

        return DBUtil.parameterizeQueryString(query);


def test():
    p = LABFinding({"findingIEN": 80});
    query = p.writeSubquery(1);
    print DBUtil.parameterizeQueryString(query);


#test();
