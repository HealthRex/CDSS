
import unittest
from medinfo.dataconversion.Finding import *
from Const import RUNNER_VERBOSITY
from medinfo.db.test.Util import DBTestCase
from cStringIO import StringIO
from medinfo.dataconversion.Taxonomy import *


# Module to test Finding.py methods

class TestFinding(DBTestCase):
    def setUp(self):
        DBTestCase.setUp(self)

    # Tests check output of each Finding subclass's
    # writeSubquery(findingIndex) method.
    def test_PXRMDFinding(self):
        # Expected Ouput specific to WARFARIN example,
        # With Reminder Code 376 and findingIEN 612280
        siteCode = 640
        reminderIEN = 596
        findingIEN = 694
        findingIndex = 2
        subfindingModels = [\
        {'findingIEN': 754, 'type': 'AUTTHF', 'findingIndex': 'sf_AUTTHF', 'BGNNG_DT_TM_9': '', 'merged': False, 'SITECODE': siteCode},
        {'findingIEN': 640962, 'type': 'AUTTHF', 'findingIndex': 'sf_AUTTHF', 'BGNNG_DT_TM_9': '', 'merged': False, 'SITECODE': siteCode},
        {'findingIEN': 640961, 'type': 'AUTTHF', 'findingIndex': 'sf_AUTTHF', 'BGNNG_DT_TM_9': '', 'merged': False, 'SITECODE': siteCode},
        {'findingIEN': 191, 'type': 'LAB', 'findingIndex': 'sf_LAB', 'BGNNG_DT_TM_9': '', 'merged': False, 'SITECODE': siteCode},
        {'findingIEN': 190, 'type': 'LAB', 'findingIndex': 'sf_LAB', 'BGNNG_DT_TM_9': '', 'merged': False, 'SITECODE': siteCode}
        ]
        sampleFindingModel = {'findingIndex': findingIndex, 'RMNDR_FRQNCY_3': u'', \
                'type': u'PXRMD', 'findingIndex': findingIndex, 'RNK_FRQNCY_6': u'', \
                 'FNDNG_ITM_X01': u'865PSNDF(50.6,', 'MIN_AGE_1': u'', 'negate': False, \
                 'USE_IN_RSLTN_LGC_7': u'', 'USE_IN_PTNT_CHRT_GC_8': u'&', 'P_IEN': reminderIEN, \
                'IEN': u'1_116', 'BGNNG_DT_TM_9': u'T-6M', 'findingIEN': findingIEN, 'MAX_AGE_2': u'', 'SITECODE': siteCode, "subfindingModels": subfindingModels}

        # expected ouput for positive term finding
        positiveExpectedOutput = \
        """
        IF Object_Id('tempdb..#ft%(findingIndex)s_sf_AUTTHF') IS NOT NULL DROP TABLE #ft%(findingIndex)s_sf_AUTTHF
    	SELECT Sta3n,VisitDateTime AS DateTime,PatientSID, HealthFactorIEN AS FindingIEN
        INTO #ft%(findingIndex)s_sf_AUTTHF
    	FROM [ORD_Chan_201406081D].[Src].[HF_HealthFactor]
    	WHERE Sta3n=640 AND HealthFactorIEN IN (754,640961,640962)

        IF Object_Id('tempdb..#ft%(findingIndex)s_sf_LAB') IS NOT NULL DROP TABLE #ft%(findingIndex)s_sf_LAB
    	SELECT t1.Sta3n,t1.LabChemSpecimenDateTime AS DateTime,t1.PatientSID, t2.LabChemTestIEN AS FindingIEN
        INTO #ft%(findingIndex)s_sf_LAB
    	FROM [ORD_Chan_201406081D].[Src].[Chem_PatientLabChem] AS t1
    	INNER JOIN [CDWWork_FY14].[Dim].[LabChemTest] AS t2
    		ON t1.LabChemTestSID=t2.LabChemTestSID AND t1.Sta3n=t2.Sta3n
    			AND t2.LabChemTestIEN IN (190,191)
    	WHERE t1.Sta3n=640

        IF Object_Id('tempdb..#ft%(findingIndex)s') IS NOT NULL DROP TABLE #ft%(findingIndex)s
        SELECT f.Sta3n, f.DateTime, f.PatientSID, f.FindingIEN
        INTO #ft%(findingIndex)s
        FROM (
        SELECT * FROM #ft%(findingIndex)s_sf_AUTTHF
        UNION
        SELECT * FROM #ft%(findingIndex)s_sf_LAB
        ) AS f
        """ % {'siteCode': siteCode, 'findingIEN': findingIEN, 'reminderIEN': reminderIEN, 'findingIndex': findingIndex}

        query = PXRMDFinding(sampleFindingModel).writeSubquery(findingIndex)
        queryText = DBUtil.parameterizeQueryString(query)
        print "\nTesting Positive Finding Output: "
        self.assertEqualFile(StringIO(positiveExpectedOutput), StringIO(queryText), whitespace=False)
        print "ok\n"

    # Tests check output of each Finding subclass's
    # writeSubquery(findingIndex) method.
    def test_AUTTHFFinding(self):
        # Expected Output specific to WARFARIN example,
        # With Reminder Code 376 and findingIEN 612280
        siteCode = 640
        reminderIEN = 376
        findingIEN = 612280
        findingIndex = 6
        sampleFindingModel = {'findingIndex': findingIndex, 'RMNDR_FRQNCY_3': u'', 'type': u'PSNDF', 'index': 1, 'RNK_FRQNCY_6': u'', 'FNDNG_ITM_X01': u'865PSNDF(50.6,', 'MIN_AGE_1': u'', 'USE_IN_RSLTN_LGC_7': u'', 'USE_IN_PTNT_CHRT_GC_8': u'&', 'P_IEN': u'376', \
                'IEN': u'1_376', 'BGNNG_DT_TM_9': u'T-45D', 'findingIEN': findingIEN, 'MAX_AGE_2': u'', 'SITECODE': u'640', 'negate': False}

        positiveExpectedOutput = \
        """
        IF Object_Id('tempdb..#ft%(findingIndex)s') IS NOT NULL DROP TABLE #ft%(findingIndex)s
        SELECT Sta3n,VisitDateTime AS DateTime,PatientSID, HealthFactorIEN AS FindingIEN
        INTO #ft%(findingIndex)s
	    FROM [ORD_Chan_201406081D].[Src].[HF_HealthFactor]
	    WHERE Sta3n=%(siteCode)s AND HealthFactorIEN IN (%(findingIEN)s)
        """ % {'siteCode': siteCode, 'findingIEN': findingIEN, 'reminderIEN': reminderIEN, 'findingIndex': findingIndex}

        query = AUTTHFFinding(sampleFindingModel).writeSubquery(findingIndex)
        queryText = DBUtil.parameterizeQueryString(query)
        print "\nTesting Positive Finding Output: "
        self.assertEqualFile(StringIO(positiveExpectedOutput), StringIO(queryText), whitespace=False)
        print 'ok\n'

    def test_PXDFinding(self):
        # Tests PXD Finding from example PA-CHF/BETA BLOCKER (DOQIT),
        # With Reminder Code 116 and findingIEN 40

        siteCode = 640
        reminderIEN = 116
        findingIEN = 40
        findingIndex = 1

        taxonomies = []

        tModels = [ \
            {'name': 'ICD_428.0','CPTCodes': [],'ICD9Codes': [],'CPTRanges': [],'ICD9Ranges': [('428.0', '428.0')],'ICPCodes': [],'ICPRanges': []},
            {'name': 'ICD_428.1','CPTCodes': [],'ICD9Codes': [],'CPTRanges': [],'ICD9Ranges': [('428.1', '428.1')],'ICPCodes': [],'ICPRanges': []},
            {'name': 'ICD_428.9','CPTCodes': [],'ICD9Codes': [],'CPTRanges': [],'ICD9Ranges': [('428.9', '428.9')],'ICPCodes': [],'ICPRanges': []},
            {'name': 'ICD_402.01','CPTCodes': [],'ICD9Codes': [],'CPTRanges': [],'ICD9Ranges': [('402.01', '402.01')],'ICPCodes': [],'ICPRanges': []},
            {'name': 'ICD_402.11','CPTCodes': [],'ICD9Codes': [],'CPTRanges': [],'ICD9Ranges': [('402.11', '402.11')],'ICPCodes': [],'ICPRanges': []},
            {'name': 'ICD_402.91','CPTCodes': [],'ICD9Codes': [],'CPTRanges': [],'ICD9Ranges': [('402.91', '402.91')],'ICPCodes': [],'ICPRanges': []},
            {'name': 'ICD_404.01','CPTCodes': [],'ICD9Codes': [],'CPTRanges': [],'ICD9Ranges': [('404.01', '404.01')],'ICPCodes': [],'ICPRanges': []},
            {'name': 'ICD_404.03','CPTCodes': [],'ICD9Codes': [],'CPTRanges': [],'ICD9Ranges': [('404.03', '404.03')],'ICPCodes': [],'ICPRanges': []},
            {'name': 'ICD_404.11','CPTCodes': [],'ICD9Codes': [],'CPTRanges': [],'ICD9Ranges': [('404.11', '404.11')],'ICPCodes': [],'ICPRanges': []},
            {'name': 'ICD_404.13','CPTCodes': [],'ICD9Codes': [],'CPTRanges': [],'ICD9Ranges': [('404.13', '404.13')],'ICPCodes': [],'ICPRanges': []},
            {'name': 'ICD_404.91','CPTCodes': [],'ICD9Codes': [],'CPTRanges': [],'ICD9Ranges': [('404.91', '404.91')],'ICPCodes': [],'ICPRanges': []},
            {'name': 'ICD_404.93','CPTCodes': [],'ICD9Codes': [],'CPTRanges': [],'ICD9Ranges': [('404.93', '404.93')],'ICPCodes': [],'ICPRanges': []}
            ]
        for model in tModels:
            t = Taxonomy(model['name'])
            for key in model:
                setattr(t, key, model[key])
            taxonomies.append(t)

        sampleFindingModel = {'RMNDR_FRQNCY_3': u'', 'scale': u'', \
        'type': u'PXD', 'negate': False, 'RNK_FRQNCY_6': u'', \
        'FNDNG_ITM_X01': u'40;PXD(811.2,', 'MIN_AGE_1': u'', \
        'USE_IN_RSLTN_LGC_7': u'', 'USE_IN_PTNT_CHRT_GC_8': u'&', \
        'P_IEN': u'116', 'useInLogic': u'&', 'MH_SCL_13': u'', \
        'IEN': u'1_116', 'findingIEN': 40, 'BGNNG_DT_TM_9': u'', \
        'findingIndex': 1, 'MAX_AGE_2': u'', 'taxonomies': taxonomies,\
        'SITECODE': siteCode
        }

        positiveExpectedOutput = \
        """
        IF Object_Id('tempdb..#ft1') IS NOT NULL DROP TABLE #ft1
         SELECT t1.Sta3n, t1.VDiagnosisDateTime AS DateTime, t1.PatientSID
        INTO #ft1
        FROM [ORD_Chan_201406081D].[Src].[Outpat_VDiagnosis] AS t1
         INNER JOIN (
        SELECT Sta3n, ICD9SID as SID, ICD9Code as Code
        FROM [CDWWork_FY14].[Dim].[ICD9]
        WHERE ICD9Code BETWEEN '428.0' AND '428.0'
        OR ICD9Code BETWEEN '428.1' AND '428.1'
        OR ICD9Code BETWEEN '428.9' AND '428.9'
        OR ICD9Code BETWEEN '402.01' AND '402.01'
        OR ICD9Code BETWEEN '402.11' AND '402.11'
        OR ICD9Code BETWEEN '402.91' AND '402.91'
        OR ICD9Code BETWEEN '404.01' AND '404.01'
        OR ICD9Code BETWEEN '404.03' AND '404.03'
        OR ICD9Code BETWEEN '404.11' AND '404.11'
        OR ICD9Code BETWEEN '404.13' AND '404.13'
        OR ICD9Code BETWEEN '404.91' AND '404.91'
        OR ICD9Code BETWEEN '404.93' AND '404.93'
        ) AS i
        ON t1.ICDSID=i.SID AND t1.Sta3n=i.Sta3n
        WHERE t1.Sta3n = 640
        """

        query = PXDFinding(sampleFindingModel).writeSubquery(findingIndex)
        queryText = DBUtil.parameterizeQueryString(query)
        print "\nTesting Positive Finding Output: "
        self.assertEqualFile(StringIO(positiveExpectedOutput), StringIO(queryText), whitespace=False)
        print 'ok\n'

    def test_PSNDFFinding(self):
        # Tests PSNDF Finding from example WARFARIN - INR NEEDED,
        # With Reminder Code 376 and findingIEN 865

        siteCode = 640
        reminderIEN = 376
        findingIEN = 865
        findingIndex = 1

        sampleFindingModel = {'RMNDR_FRQNCY_3': u'', 'scale': u'', \
        'type': u'PSNDF', 'negate': False, 'RNK_FRQNCY_6': u'', \
        'FNDNG_ITM_X01': u'865;PSNDF(50.6,', 'MIN_AGE_1': u'', \
        'USE_IN_RSLTN_LGC_7': u'', 'USE_IN_PTNT_CHRT_GC_8': u'&', \
        'P_IEN': u'376', 'useInLogic': u'&', 'MH_SCL_13': u'', \
        'IEN': u'1_376', 'findingIEN': 865, 'BGNNG_DT_TM_9': u'T-45D', \
        'findingIndex': 1, 'MAX_AGE_2': u'', 'SITECODE': u'640'}


        positiveExpectedOutput = \
        """
        IF Object_Id('tempdb..#ft1') IS NOT NULL DROP TABLE #ft1
        SELECT Sta3n, DateTime, PatientSID, FindingIEN
         INTO #ft1
         FROM (
         SELECT t1.Sta3n, t1.RxOutpatFillSID, t1.FillDateTime AS DateTime, t1.PatientSID, t3.DrugNameWithoutDoseIEN AS FindingIEN
        FROM [ORD_Chan_201406081D].[Src].[RxOut_RxOutpatFill]   AS t1
         INNER JOIN [CDWWork_FY14].[Dim].[NationalDrug] AS t2
        ON t1.Sta3n=t2.Sta3n AND t1.NationalDrugSID=t2.NationalDrugSID
         INNER JOIN [CDWWork_FY14].[Dim].[DrugNameWithoutDose] AS t3
        ON t2.DrugNameWithoutDoseSID=t3.DrugNameWithoutDoseSID AND t2.Sta3n=t3.Sta3n
        AND t3.DrugNameWithoutDoseIEN IN (865)
        WHERE t1.Sta3n=640
        ) AS a
        """

        query = PSNDFFinding(sampleFindingModel).writeSubquery(findingIndex)
        queryText = DBUtil.parameterizeQueryString(query)
        print "\nTesting Positive Finding Output: "
        self.assertEqualFile(StringIO(positiveExpectedOutput), StringIO(queryText), whitespace=False)
        print 'ok\n'

    def test_LABFinding(self):
        # Tests LAB Finding from example WARFARIN - INR NEEDED,
        # With Reminder Code 376 and findingIEN 5478

        siteCode = 640
        reminderIEN = 376
        findingIEN = 5478
        findingIndex = 4

        sampleFindingModel = {'RMNDR_FRQNCY_3': u'', 'scale': u'', \
        'type': u'LAB', 'negate': False, 'RNK_FRQNCY_6': u'', \
        'FNDNG_ITM_X01': u'5478;LAB(60,', 'MIN_AGE_1': u'', \
        'USE_IN_RSLTN_LGC_7': u'!', 'USE_IN_PTNT_CHRT_GC_8': u'', \
        'P_IEN': u'376', 'useInLogic': u'!', 'MH_SCL_13': u'', \
        'IEN': u'4_376', 'findingIEN': 5478, 'BGNNG_DT_TM_9': u'', \
        'findingIndex': 4, 'MAX_AGE_2': u'', 'SITECODE': u'640'}


        positiveExpectedOutput = \
        """
        IF Object_Id('tempdb..#ft4') IS NOT NULL DROP TABLE #ft4
         SELECT t1.Sta3n, t1.LabChemSpecimenDateTime AS DateTime, t1.PatientSID, t2.LabChemTestIEN AS FindingIEN
        INTO #ft4
        FROM [ORD_Chan_201406081D].[Src].[Chem_PatientLabChem]   AS t1
         INNER JOIN [CDWWork_FY14].[Dim].[LabChemTest] AS t2
        ON t1.LabChemTestSID=t2.LabChemTestSID AND t1.Sta3n=t2.Sta3n
        AND t2.LabChemTestIEN IN (5478)
        WHERE t1.Sta3n=640
        """

        query = LABFinding(sampleFindingModel).writeSubquery(findingIndex)
        queryText = DBUtil.parameterizeQueryString(query)
        print "\nTesting Positive Finding Output: "
        self.assertEqualFile(StringIO(positiveExpectedOutput), StringIO(queryText), whitespace=False)
        print 'ok\n'

    def test_YTTFinding(self):
        # Tests YTT Finding from example PA-ALCOHOL USE SCREEN (AUDIT-C) FY09,
        # With Reminder Code 392 and findingIEN 67
        siteCode = 640
        reminderIEN = 392
        findingIEN = 67
        findingIndex = '6_sf_YTT'
        sampleFindingModel = {\
        'INTRNL_CNDTN_22': u'I +V>10', 'IEN': u'2_767', \
        'findingIEN': 67, 'negate': False, 'RETRIEVALTIME': u'2015-07-01 06:40:23', \
        'USE_INCTV_PRBLMS_10': u'', 'USE_STRT_DT_27': u'', \
        'scale': u'516', 'MH_SCALE_13': u'516', 'type': u'YTT', \
        'merged': False, 'FNDNG_ITM_X01': u'67;YTT(601.71,', \
        'CNDTN_14': u'I +V>10', 'P_IEN': u'767', 'CNDTN_CS_SNSTV_15': u'', \
        'RXTYP_16': u'', 'BGNNG_DT_TM_9': u'', 'ENDNG_DT_TM_12': u'', \
        'condition': u'>10', 'V_SBSCRPT_LST_23': u'', 'queryValues': [67],\
         'CMPTD_FNDNG_PRMTR_26': u'', 'findingIndex': "6_sf_YTT", \
         'INCLD_VST_DATA_28': u'', 'OCCRNC_CNT_17': u'', \
         'WTHN_CTGRY_RNK_11': u'', 'SITECODE': u'640', 'USE_STS_IN_SRCH_18': u''}

        positiveExpectedOutput = \
        """
        IF Object_Id('tempdb..#ft6_sf_YTT') IS NOT NULL DROP TABLE #ft6_sf_YTT
         SELECT s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyResultIEN AS FindingIEN
        INTO #ft6_sf_YTT
        FROM [ORD_Chan_201406081D].[Src].[MH_SurveyResult] AS s
         INNER JOIN [CDWWork_FY14].[Dim].[SurveyScale] AS ss
        ON s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND ss.SurveyScaleIEN=516 AND s.RawScore>10
        WHERE s.Sta3n=640 AND s.SurveyResultIEN IN (67)
        """
        query = YTTFinding(sampleFindingModel).writeSubquery(findingIndex)
        queryText = DBUtil.parameterizeQueryString(query)
        print "\nTesting Positive Finding Output: "
        self.assertEqualFile(StringIO(positiveExpectedOutput), StringIO(queryText), whitespace=False)
        print 'ok\n'

    def test_ORDFinding(self):
        # Tests ORD Finding from example PA-CONSIDER CLOZAPINE (PSYCHIATRIST ONLY),
        # With Reminder Code 719 and findingIEN 13304

        siteCode = 640
        reminderIEN = 719
        findingIEN = 13304
        findingIndex = 5

        sampleFindingModel = {'RMNDR_FRQNCY_3': u'', 'scale': u'', \
        'type': u'ORD', 'negate': False, 'RNK_FRQNCY_6': u'', \
        'FNDNG_ITM_X01': u'13304;ORD(101.43,', 'MIN_AGE_1': u'', \
        'USE_IN_RSLTN_LGC_7': u'!', 'USE_IN_PTNT_CHRT_GC_8': u'', \
        'P_IEN': u'719', 'useInLogic': u'!', 'MH_SCL_13': u'', \
        'IEN': u'5_719', 'findingIEN': 13304, 'BGNNG_DT_TM_9': u'', \
        'findingIndex': 5, 'MAX_AGE_2': u'', 'SITECODE': u'640'}

        positiveExpectedOutput = \
        """
        IF Object_Id('tempdb..#ft5') IS NOT NULL DROP TABLE #ft5
         SELECT o.Sta3n, o.OrderStartDateTime AS DateTime, o.PatientSID, i.OrderableItemIEN AS FindingIEN
        INTO #ft5
        FROM [ORD_Chan_201406081D].[Src].[CPRSOrder_OrderedItem] AS o
         INNER JOIN [CDWWork_FY14].[Dim].[OrderableItem] AS i
        ON o.Sta3n=i.Sta3n AND o.OrderableItemSID=i.OrderableItemSID AND i.OrderableItemIEN IN (13304)
        WHERE o.Sta3n=640
        """

        query = ORDFinding(sampleFindingModel).writeSubquery(findingIndex)
        queryText = DBUtil.parameterizeQueryString(query)
        print "\nTesting Positive Finding Output: "
        self.assertEqualFile(StringIO(positiveExpectedOutput), StringIO(queryText), whitespace=False)
        print 'ok\n'

    def test_GMRDFinding(self):
        # Tests GMRD Finding from example ZZPA-HTN ASSESSMENT BP >=140/90 FY12
        # With Reminder Code 812 and findingIEN 1

        siteCode = 640
        reminderIEN = 812
        findingIEN = 1
        findingIndex = 11

        sampleFindingModel = {'RMNDR_FRQNCY_3': u'', 'scale': u'', \
        'type': u'GMRD', 'negate': False, 'RNK_FRQNCY_6': u'', \
        'FNDNG_ITM_X01': u'1;GMRD(120.51,', 'MIN_AGE_1': u'', \
        'USE_IN_RSLTN_LGC_7': u'', 'USE_IN_PTNT_CHRT_GC_8': u'&', \
        'P_IEN': u'812', 'useInLogic': u'&', 'MH_SCL_13': u'', \
        'IEN': u'11_812', 'findingIEN': 1, 'BGNNG_DT_TM_9': u'', \
        'findingIndex': 11, 'MAX_AGE_2': u'', 'SITECODE': u'640'}

        positiveExpectedOutput = \
        """
        IF Object_Id('tempdb..#ft11') IS NOT NULL DROP TABLE #ft11
         SELECT t1.Sta3n, t1.VitalSignTakenDateTime AS DateTime, t1.PatientSID, t2.VitalTypeIEN AS FindingIEN
        INTO #ft11
        FROM [ORD_Chan_201406081D].[Src].[Vital_VitalSign] AS t1
        INNER JOIN [CDWWork_FY14].[Dim].[VitalType] AS t2
            ON t1.Sta3n=t2.Sta3n AND t1.VitalTypeSID=t2.VitalTypeSID AND t2.VitalTypeIEN IN (1)
        WHERE t1.Sta3n=640
        """

        query = GMRDFinding(sampleFindingModel).writeSubquery(findingIndex)
        queryText = DBUtil.parameterizeQueryString(query)
        print "\nTesting Positive Finding Output: "
        self.assertEqualFile(StringIO(positiveExpectedOutput), StringIO(queryText), whitespace=False)
        print 'ok\n'

    def test_AUTTEXAMFinding(self):
        # Tests AUTTEXAM Finding from example PA-SMT CONSULT RENEWAL,
        # With Reminder Code 206 and findingIEN 640013

        siteCode = 640
        reminderIEN = 206
        findingIEN = 640013
        findingIndex = 3

        sampleFindingModel = {'RMNDR_FRQNCY_3': u'', 'scale': u'', \
        'type': u'AUTTEXAM', 'negate': False, 'RNK_FRQNCY_6': u'', \
        'FNDNG_ITM_X01': u'640013;AUTTEXAM(', 'MIN_AGE_1': u'', \
        'USE_IN_RSLTN_LGC_7': u'!', 'USE_IN_PTNT_CHRT_GC_8': u'', \
        'P_IEN': u'206', 'useInLogic': u'!', 'MH_SCL_13': u'', \
        'IEN': u'3_206', 'findingIEN': 640013, 'BGNNG_DT_TM_9': u'T-1Y', \
        'findingIndex': 3, 'MAX_AGE_2': u'', 'SITECODE': u'640'}

        positiveExpectedOutput = \
        """
        IF Object_Id('tempdb..#ft3') IS NOT NULL DROP TABLE #ft3
         SELECT t1.Sta3n, t1.VExamDateTime AS DateTime, t1.PatientSID, t2.ExamIEN AS FindingIEN
        INTO #ft3
        FROM [ORD_Chan_201406081D].[Src].[Outpat_VExam] AS t1
        INNER JOIN [CDWWork_FY14].[Dim].[Exam] AS t2
            ON t1.Sta3n=640 AND t1.Sta3n=t2.Sta3n AND t1.ExamSID=t2.ExamSID
                AND t2.ExamIEN IN (640013)
        """

        query = AUTTEXAMFinding(sampleFindingModel).writeSubquery(findingIndex)
        queryText = DBUtil.parameterizeQueryString(query)
        print "\nTesting Positive Finding Output: "
        self.assertEqualFile(StringIO(positiveExpectedOutput), StringIO(queryText), whitespace=False)
        print 'ok\n'

    def test_PSDRUGFinding(self):
        # Tests PSDRUG Finding from example PA-CONSIDER CLOZAPINE (PSYCHIATRIST ONLY),
        # With Reminder Code 719 and findingIENs [29021, 29022]
        # as part of PXRMDFinding index 2

        siteCode = 640
        reminderIEN = 719
        findingIEN = [29021, 29022]
        findingIndex = "2_sf_PSDRUG"

        sampleFindingModel = {'INTRNL_CNDTN_22': u'', 'IEN': u'4_46',\
         'findingIEN': 29021, 'negate': False, 'RETRIEVALTIME': u'2015-07-01 06:40:12', \
         'USE_INCTV_PRBLMS_10': u'', 'USE_STRT_DT_27': u'', 'scale': u'', \
         'MH_SCALE_13': u'', 'type': u'PSDRUG', 'merged': True, \
         'FNDNG_ITM_X01': u'29021;PSDRUG(', 'CNDTN_14': u'', \
         'P_IEN': u'46', 'CNDTN_CS_SNSTV_15': u'', 'RXTYP_16': u'A', \
         'BGNNG_DT_TM_9': u'', 'ENDNG_DT_TM_12': u'', \
         'V_SBSCRPT_LST_23': u'', 'queryValues': [29021, 29022], \
         'CMPTD_FNDNG_PRMTR_26': u'', 'findingIndex': 4, \
         'INCLD_VST_DATA_28': u'', 'OCCRNC_CNT_17': u'', \
         'WTHN_CTGRY_RNK_11': u'', 'SITECODE': u'640', \
         'USE_STS_IN_SRCH_18': u''}

        positiveExpectedOutput = \
        """
        IF Object_Id('tempdb..#ft2_sf_PSDRUG') IS NOT NULL DROP TABLE #ft2_sf_PSDRUG
         SELECT t1.Sta3n, t1.RxOutpatFillSID, t1.FillDateTime AS DateTime, t1.PatientSID, t2.LocalDrugIEN AS FindingIEN
        INTO #ft2_sf_PSDRUG
        FROM [ORD_Chan_201406081D].[Src].[RxOut_RxOutpatFill] AS t1
         INNER JOIN [CDWWork_FY14].[Dim].[LocalDrug] AS t2
        ON t1.DrugNameWithoutDose=t2.DrugNameWithoutDose AND t1.Sta3n=t2.Sta3n AND t2.LocalDrugIEN IN (29021, 29022)
        WHERE t1.Sta3n = 640
        """

        query = PSDRUGFinding(sampleFindingModel).writeSubquery(findingIndex)
        queryText = DBUtil.parameterizeQueryString(query)
        print "\nTesting Positive Finding Output: "
        self.assertEqualFile(StringIO(positiveExpectedOutput), StringIO(queryText), whitespace=False)
        print 'ok\n'

    """
    def test_template(self):
        # TODO: Update description
        # Tests YTT Finding from example PA-ALCOHOL USE SCREEN (AUDIT-C) FY09,
        # With Reminder Code 392 and findingIEN 67

        # TODO: Insert sample data
        siteCode = 640
        reminderIEN =
        findingIEN =
        findingIndex =

        # TODO: Insert sample model
        sampleFindingModel = {\

        }

        # TODO: Insert output
        positiveExpectedOutput = \


        # TODO: Update Finding type
        query = AUTTHFFinding(sampleFindingModel).writeSubquery(findingIndex)
        queryText = DBUtil.parameterizeQueryString(query)
        print "\nTesting Positive Finding Output: "
        self.assertEqualFile(StringIO(positiveExpectedOutput), StringIO(queryText), whitespace=False)
        print 'ok\n'

        sampleFindingModel["negate"] = True

        # TODO: Insert output
        negatedExpectedOutput = \


        # TODO: Update Finding type
        query = AUTTHFFinding(sampleFindingModel).writeSubquery(findingIndex)
        queryText = DBUtil.parameterizeQueryString(query)
        print "\nTesting Negated Finding Output: "
        self.assertEqualFile(StringIO(negatedExpectedOutput), StringIO(queryText), whitespace=False)

    """

# Create target test suite
def suite():
    suite = unittest.TestSuite()
    suite.addTest(TestFinding("test_AUTTHFFinding"))
    suite.addTest(TestFinding("test_PXDFinding"))
    suite.addTest(TestFinding("test_PSNDFFinding"))
    suite.addTest(TestFinding("test_ORDFinding"))
    suite.addTest(TestFinding("test_GMRDFinding"))
    suite.addTest(TestFinding("test_AUTTEXAMFinding"))
    suite.addTest(TestFinding("test_PSDRUGFinding"))
    suite.addTest(TestFinding("test_LABFinding"))
    suite.addTest(TestFinding("test_PXRMDFinding"))
    suite.addTest(TestFinding("test_YTTFinding"))
    return suite

if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
