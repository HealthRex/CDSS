#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
from datetime import datetime
import unittest
import sqlite3
from Const import RUNNER_VERBOSITY
from Util import log

from medinfo.db.test.Util import DBTestCase

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel

from medinfo.dataconversion.VAReminderToQuery import VAReminderToQuery

# File path of the SQLite database to test for sample data, reference in medinfo.db.Env.TEST_DB_PARAM.
# Not good to have this dependency, but don't want to include 300MB database in test code
#TEST_DATABASE_FILEPATH = "c:\Box Sync\NoSync\VAAlerts\dave_chan2.sqlite"

class TestVAReminderToQuery(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self)

        log.info("Point to local reminder database with a handful of specific cases manually translated. May require revision of environment variable above to point to different test database location")
        self.converter = VAReminderToQuery()  # Instance to test on

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")

        DBTestCase.tearDown(self)

    def test_dataConversion116(self):
        # Run the data conversion on sample cases and look for expected records

        log.debug("PA-CHF/BETA BLOCKER")
        siteCode = 640
        reminderIEN = 116

        expectedCohortLogic = \
        """-- Cohort: SITECODE=640, IEN=116, PA-CHF/BETA BLOCKER (DOQIT)
        IF Object_Id('tempdb..#ft1') IS NOT NULL DROP TABLE #ft1
        SELECT t1.Sta3n, t1.VDiagnosisDateTime AS DateTime, t1.PatientSID
        INTO #ft1
        FROM [ORD_Chan_201406081D].[Src].[Outpat_VDiagnosis] AS t1
        INNER JOIN (
            SELECT
            FROM [CDWWork_FY14].[Dim].[ICD9]
            ON t1.ICDSID=i.ICD9SID AND t1.Sta3n=i.Sta3n
                AND (i.ICD9Code BETWEEN '428.0' AND '428.0'
                    OR i.ICD9Code BETWEEN '428.1' AND '428.1'
                    OR i.ICD9Code BETWEEN '428.9' AND '428.9'
                    OR i.ICD9Code BETWEEN '402.01' AND '402.01'
                    OR i.ICD9Code BETWEEN '402.11' AND '402.11'
                    OR i.ICD9Code BETWEEN '402.91' AND '402.91'
                    OR i.ICD9Code BETWEEN '404.01' AND '404.01'
                    OR i.ICD9Code BETWEEN '404.03' AND '404.03'
                    OR i.ICD9Code BETWEEN '404.11' AND '404.11'
                    OR i.ICD9Code BETWEEN '404.13' AND '404.13'
                    OR i.ICD9Code BETWEEN '404.91' AND '404.91'
                    OR i.ICD9Code BETWEEN '404.93' AND '404.93'
                    ) AS i
        WHERE t1.Sta3n=640

        IF Object_Id('tempdb..#ft2_sf_AUTTHF') IS NOT NULL DROP TABLE #ft2_sf_AUTTHF
    	SELECT Sta3n, VisitDateTime AS DateTime, PatientSID
        INTO #ft2_sf_AUTTHF
        FROM [ORD_Chan_201406081D].[Src].[HF_HealthFactor]
        WHERE Sta3n=640 AND HealthFactorIEN IN (640228, 640230)

        IF Object_Id('tempdb..#ft2') IS NOT NULL DROP TABLE #ft2
        SELECT *
        INTO #ft2
        FROM #ft2_sf_AUTTHF

        IF Object_Id('tempdb..#Cohort_640_116') IS NOT NULL DROP TABLE #Cohort_640_116
        SELECT v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID, 1 AS Cohort
        INTO #Cohort_640_116
        FROM [ORD_Chan_201406081D].[Src].[Outpat_Visit] AS v
        INNER JOIN #ft1
            ON v.PatientSID=#ft1.PatientSID AND v.Sta3n=#ft1.Sta3n
                AND v.VisitDateTime >= #ft1.DateTime
                AND #ft1.DateTime >= DATEADD(year, -1, v.VisitDateTime)
        INNER JOIN #ft2
            ON v.PatientSID=#ft2.PatientSID AND v.Sta3n=#ft2.Sta3n
                AND v.VisitDateTime >= #ft2.DateTime
                AND #ft2.DateTime >= DATEADD(year, -1, v.VisitDateTime)
        WHERE v.Sta3n=640
        GROUP BY v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID
        """

        expectedResolutionLogic = \
        """
        -- Resolution: SITECODE=640, IEN=116, PA-CHF/BETA BLOCKER (DOQIT)
        IF Object_Id('tempdb..#ft3') IS NOT NULL DROP TABLE #ft3
        SELECT Sta3n, DateTime, PatientSID
        INTO #ft3
        FROM (
            SELECT t1.Sta3n, t1.RxOutpatFillSID, t1.FillDateTime AS DateTime, t1.PatientSID
            FROM [ORD_Chan_201406081D].[Src].[RxOut_RxOutpatFill] AS t1
            INNER JOIN [CDWWork_FY14].[Dim].[NationalDrug] AS t2
                ON t1.Sta3n=t2.Sta3n AND t1.NationalDrugSID=t2.NationalDrugSID
            INNER JOIN [CDWWork_FY14].[Dim].[DrugClass] AS t3
                ON t2.PrimaryDrugClassSID=t3.DrugClassSID AND t2.Sta3n=t3.Sta3n
                    AND t3.DrugClassIEN IN (54)
            WHERE t1.Sta3n=640
            UNION
            SELECT t1.Sta3n, t1.RxOutpatFillSID, t1.FillDateTime AS DateTime, t1.PatientSID
            FROM [ORD_Chan_201406081D].[Src].[RxOut_RxOutpatFill] AS t1
            INNER JOIN [CDWWork_FY14].[Dim].[LocalDrug] AS t2
                ON t1.Sta3n=t2.Sta3n AND t1.LocalDrugSID=t2.LocalDrugSID
            INNER JOIN [CDWWork_FY14].[Dim].[DrugClass] AS t3
                ON t2.DrugClassSID=t3.DrugClassSID AND t2.Sta3n=t3.Sta3n
                    AND t3.DrugClassIEN IN (54)
            WHERE t1.Sta3n=640
        ) AS a


        IF Object_Id('tempdb..#Resolution_640_116') IS NOT NULL DROP TABLE #Resolution_640_116
        SELECT v.VisitSID, 1 AS Resolution
        INTO #Resolution_640_116
        FROM #Cohort_640_116 AS v
        INNER JOIN #ft3
            ON v.PatientSID=#ft3.PatientSID AND v.Sta3n=#ft3.Sta3n
                AND v.VisitDateTime>=#ft3.DateTime
                AND #ft3.DateTime>=DATEADD(year, -1, v.VisitDateTime)
        GROUP BY v.VisitSID
        """

        expectedCombineQuery = \
        """
        -- Combine: SITECODE=640, IEN=116, PA-CHF/BETA BLOCKER (DOQIT)
        IF Object_Id('tempdb..#Visits_640_116') IS NOT NULL DROP TABLE #Visits_640_116
        SELECT '640_116' AS Reminder, c.Sta3n, c.PatientSID, c.VisitSID, c.VisitDateTime, c.Cohort, CASE WHEN r.Resolution=1 THEN 1 ELSE 0 END AS Resolved
        INTO #Visits_640_116
        FROM #Cohort_640_116 AS c
        LEFT JOIN #Resolution_640_116 AS r
            ON c.VisitSID=r.VisitSID
        """

        (cohortLogic, resolutionLogic, combineQuery) = self.converter.convertReminder(siteCode, reminderIEN)

        # Write output to file
        outputFileName = "medinfo/dataconversion/test/programOutput/reminder" + str(reminderIEN) + ".output"
        outputFile = open(outputFileName, "w")
        outputFile.write(str.join('\n\n', [cohortLogic, resolutionLogic, combineQuery]))
        outputFile.close()

        #self.assertEqualFile(StringIO(expectedCohortLogic), StringIO(cohortLogic), whitespace=False)
        #self.assertEqualFile(StringIO(expectedResolutionLogic), StringIO(resolutionLogic), whitespace=False)
        self.assertEqualFile(StringIO(expectedCombineQuery), StringIO(combineQuery), whitespace=False)

    def test_dataConversion179(self):
        # Run the data conversion on sample cases and look for expected records

        log.debug("VA-POS DEPRESSION SCREEN FOLLOWUP")
        siteCode = 640
        reminderIEN = 179

        expectedCohortLogic = \
        """
        -- Cohort: SITECODE=640, IEN=179, VA-POS DEPRESSION SCREEN FOLLOWUP
        IF Object_Id('tempdb..#ft1_sf_AUTTHF') IS NOT NULL DROP TABLE #ft1_sf_AUTTHF
        SELECT Sta3n, VisitDateTime AS DateTime, PatientSID, HealthFactorIEN AS FindingIEN
        INTO #ft1_sf_AUTTHF
        FROM [ORD_Chan_201406081D].[Src].[HF_HealthFactor]
        WHERE Sta3n=640 AND HealthFactorIEN IN (106, 612086, 612893, 640078)

        IF Object_Id('tempdb..#ft1_sf_YTT') IS NOT NULL DROP TABLE #ft1_sf_YTT
        SELECT a.Sta3n, a.DateTime, a.PatientSID, a.FindingIEN
        INTO #ft1_sf_YTT
        FROM  (
        	SELECT s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyResultIEN AS FindingIEN
        	FROM [ORD_Chan_201406081D].[Src].[MH_SurveyResult] AS s
        	INNER JOIN [CDWWork_FY14].[Dim].[SurveyScale] AS ss
		    ON s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND ss.SurveyScaleIEN=515 AND s.RawScore=1
        	WHERE s.Sta3n=640 AND s.SurveySID IN (19)
        	UNION
        	SELECT s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyResultIEN AS FindingIEN
        	FROM [ORD_Chan_201406081D].[Src].[MH_SurveyResult] AS s
        	INNER JOIN [CDWWork_FY14].[Dim].[SurveyScale] AS ss
        		ON s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND ss.SurveyScaleIEN=365 AND s.RawScore>=4
        	WHERE s.Sta3n=640 AND s.SurveySID IN (22)
        	UNION
        	SELECT s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyResultIEN AS FindingIEN
        	FROM [ORD_Chan_201406081D].[Src].[MH_SurveyResult] AS s
        	INNER JOIN [CDWWork_FY14].[Dim].[SurveyScale] AS ss
        		ON s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND ss.SurveyScaleIEN=347 AND s.RawScore>=10
        	WHERE s.Sta3n=640 AND s.SurveySID IN (18)
        	UNION
        	SELECT s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyResultIEN AS FindingIEN
        	FROM [ORD_Chan_201406081D].[Src].[MH_SurveyResult] AS s
        	INNER JOIN [CDWWork_FY14].[Dim].[SurveyScale] AS ss
        		ON s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND ss.SurveyScaleIEN=331 AND s.RawScore>=10
        	WHERE s.Sta3n=640 AND s.SurveySID IN (10)
        	UNION
        	SELECT s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyResultIEN AS FindingIEN
        	FROM [ORD_Chan_201406081D].[Src].[MH_SurveyResult] AS s
        	INNER JOIN [CDWWork_FY14].[Dim].[SurveyScale] AS ss
        		ON s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND ss.SurveyScaleIEN=453 AND s.RawScore>=33
        	WHERE s.Sta3n=640 AND s.SurveySID IN (53)
        	UNION
        	SELECT s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyResultIEN AS FindingIEN
        	FROM [ORD_Chan_201406081D].[Src].[MH_SurveyResult] AS s
        	INNER JOIN [CDWWork_FY14].[Dim].[SurveyScale] AS ss
        		ON s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND ss.SurveyScaleIEN=492 AND s.RawScore>=3
        	WHERE s.Sta3n=640 AND s.SurveySID IN (71)
        	UNION
        	SELECT s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyResultIEN AS FindingIEN
        	FROM [ORD_Chan_201406081D].[Src].[MH_SurveyResult] AS s
        	INNER JOIN [CDWWork_FY14].[Dim].[SurveyScale] AS ss
        		ON s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND ss.SurveyScaleIEN=419 AND s.RawScore>=10
        	WHERE s.Sta3n=640 AND s.SurveySID IN (42)
        	UNION
        	SELECT s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyResultIEN AS FindingIEN
        	FROM [ORD_Chan_201406081D].[Src].[MH_SurveyResult] AS s
        	INNER JOIN [CDWWork_FY14].[Dim].[SurveyScale] AS ss
        		ON s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND ss.SurveyScaleIEN=332 AND s.RawScore>=10
        	WHERE s.Sta3n=640 AND s.SurveySID IN (11)
        ) AS a

        IF Object_Id('tempdb..#ft1') IS NOT NULL DROP TABLE #ft1
         SELECT f.Sta3n, f.DateTime, f.PatientSID, f.FindingIEN
        INTO #ft1
        FROM (
        SELECT * FROM #ft1_sf_AUTTHF
        UNION
        SELECT * FROM #ft1_sf_YTT
        ) AS f

        IF Object_Id('tempdb..#ft2_sf_AUTTHF') IS NOT NULL DROP TABLE #ft2_sf_AUTTHF
         SELECT Sta3n, VisitDateTime AS DateTime, PatientSID, HealthFactorIEN AS FindingIEN
        INTO #ft2_sf_AUTTHF
        FROM [ORD_Chan_201406081D].[Src].[HF_HealthFactor]
        WHERE Sta3n=640 AND HealthFactorIEN IN (105, 612085, 612894, 640076)

        IF Object_Id('tempdb..#ft2_sf_YTT') IS NOT NULL DROP TABLE #ft2_sf_YTT
         SELECT a.Sta3n, a.DateTime, a.PatientSID, a.FindingIEN
        INTO #ft2_sf_YTT
        FROM  (
        	SELECT s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyResultIEN AS FindingIEN
        	FROM [ORD_Chan_201406081D].[Src].[MH_SurveyResult] AS s
        	INNER JOIN [CDWWork_FY14].[Dim].[SurveyScale] AS ss
        		ON s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND ss.SurveyScaleIEN=515 AND s.RawScore=0
        	WHERE s.Sta3n=640 AND s.SurveySID IN (19)
        	UNION
        	SELECT s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyResultIEN AS FindingIEN
        	FROM [ORD_Chan_201406081D].[Src].[MH_SurveyResult] AS s
        	INNER JOIN [CDWWork_FY14].[Dim].[SurveyScale] AS ss
        		ON s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND ss.SurveyScaleIEN=365 AND s.RawScore<4
        	WHERE s.Sta3n=640 AND s.SurveySID IN (22)
        	UNION
        	SELECT s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyResultIEN AS FindingIEN
        	FROM [ORD_Chan_201406081D].[Src].[MH_SurveyResult] AS s
        	INNER JOIN [CDWWork_FY14].[Dim].[SurveyScale] AS ss
        		ON s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND ss.SurveyScaleIEN=347 AND s.RawScore<10
        	WHERE s.Sta3n=640 AND s.SurveySID IN (18)
        	UNION
        	SELECT s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyResultIEN AS FindingIEN
        	FROM [ORD_Chan_201406081D].[Src].[MH_SurveyResult] AS s
        	INNER JOIN [CDWWork_FY14].[Dim].[SurveyScale] AS ss
        		ON s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND ss.SurveyScaleIEN=331 AND s.RawScore<10
        	WHERE s.Sta3n=640 AND s.SurveySID IN (10)
        	UNION
        	SELECT s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyResultIEN AS FindingIEN
        	FROM [ORD_Chan_201406081D].[Src].[MH_SurveyResult] AS s
        	INNER JOIN [CDWWork_FY14].[Dim].[SurveyScale] AS ss
        		ON s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND ss.SurveyScaleIEN=453 AND s.RawScore<33
        	WHERE s.Sta3n=640 AND s.SurveySID IN (53)
        	UNION
        	SELECT s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyResultIEN AS FindingIEN
        	FROM [ORD_Chan_201406081D].[Src].[MH_SurveyResult] AS s
        	INNER JOIN [CDWWork_FY14].[Dim].[SurveyScale] AS ss
        		ON s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND ss.SurveyScaleIEN=492 AND s.RawScore<3
        	WHERE s.Sta3n=640 AND s.SurveySID IN (71)
        	UNION
        	SELECT s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyResultIEN AS FindingIEN
        	FROM [ORD_Chan_201406081D].[Src].[MH_SurveyResult] AS s
        	INNER JOIN [CDWWork_FY14].[Dim].[SurveyScale] AS ss
        		ON s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND ss.SurveyScaleIEN=419 AND s.RawScore<10
        	WHERE s.Sta3n=640 AND s.SurveySID IN (42)
        	UNION
        	SELECT s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyResultIEN AS FindingIEN
        	FROM [ORD_Chan_201406081D].[Src].[MH_SurveyResult] AS s
        	INNER JOIN [CDWWork_FY14].[Dim].[SurveyScale] AS ss
        		ON s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND ss.SurveyScaleIEN=332 AND s.RawScore<10
        	WHERE s.Sta3n=640 AND s.SurveySID IN (11)
        ) AS a


        IF Object_Id('tempdb..#ft2') IS NOT NULL DROP TABLE #ft2
         SELECT f.Sta3n, f.DateTime, f.PatientSID, f.FindingIEN
        INTO #ft2
        FROM (
        SELECT * FROM #ft2_sf_AUTTHF
        UNION
        SELECT * FROM #ft2_sf_YTT
        ) AS f

        IF Object_Id('tempdb..#ff1_ft1') IS NOT NULL DROP TABLE #ff1_ft1
        SELECT v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID, MAX(f.DateTime) AS ComputedDateTime
        INTO #ff1_ft1
        FROM [ORD_Chan_201406081D].[Src].[Outpat_Visit] AS v
        INNER JOIN #ft1 AS f
            ON v.PatientSID=f.PatientSID AND v.Sta3n=f.Sta3n AND v.Sta3n=640
	    AND v.VisitDateTime>f.DateTime
                AND f.DateTime>DATEADD(year, -1, v.VisitDateTime)
        GROUP BY v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID

        IF Object_Id('tempdb..#ff1_ft2') IS NOT NULL DROP TABLE #ff1_ft2
        SELECT v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID, MAX(a.DateTime) AS ComputedDateTime
        INTO #ff1_ft2
        FROM [ORD_Chan_201406081D].[Src].[Outpat_Visit] AS v
        INNER JOIN (
        	SELECT * FROM #ft2 AS f
        	UNION
        	SELECT v2.Sta3n, CAST(0 AS DATETIME) AS DateTime, v2.PatientSID, 0 AS FindingIEN
        	FROM [ORD_Chan_201406081D].[Src].[Outpat_Visit] AS v2
        	WHERE v2.PatientSID NOT IN (
        		SELECT f2.PatientSID
        		FROM #ft2 AS f2
        	)
        ) AS a
        ON v.PatientSID=a.PatientSID AND v.Sta3n=a.Sta3n AND v.Sta3n=640
               AND v.VisitDateTime>a.DateTime
        GROUP BY v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID

        IF Object_Id('tempdb..#ff1') IS NOT NULL DROP TABLE #ff1
        SELECT t1.Sta3n, t1.VisitSID, t1.VisitDateTime, t1.PatientSID
        INTO #ff1
        FROM #ff1_ft1 AS t1
        INNER JOIN #ff1_ft2 AS t2
            ON t1.VisitSID=t2.VisitSID AND t1.PatientSID=t2.PatientSID AND t1.ComputedDateTime>t2.ComputedDateTime

        IF Object_Id('tempdb..#Cohort_640_179') IS NOT NULL DROP TABLE #Cohort_640_179
         SELECT v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID, 1 AS Cohort
        INTO #Cohort_640_179
        FROM [ORD_Chan_201406081D].[Src].[Outpat_Visit] AS v
         INNER JOIN #ft1
        ON v.PatientSID=#ft1.PatientSID AND v.Sta3n=#ft1.Sta3n
                AND v.VisitDateTime >= #ft1.DateTime
        AND #ft1.DateTime>=DATEADD(year, -1, v.VisitDateTime)
         INNER JOIN #ff1
        ON v.PatientSID=#ff1.PatientSID AND v.Sta3n=#ff1.Sta3n
                AND v.VisitDateTime >= #ff1.VisitDateTime
        WHERE v.Sta3n = 640
        GROUP BY v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID
        """

        expectedResolutionLogic = \
        """
        -- Resolution: SITECODE=640, IEN=179, VA-POS DEPRESSION SCREEN FOLLOWUP

        """

        expectedCombineQuery = \
        """
        -- Combine: SITECODE=640, IEN=179, VA-POS DEPRESSION SCREEN FOLLOWUP
        IF Object_Id('tempdb..#Visits_640_179') IS NOT NULL DROP TABLE #Visits_640_179
        SELECT '640_179' AS Reminder, c.Sta3n, c.PatientSID, c.VisitSID, c.VisitDateTime, c.Cohort,
            CASE WHEN r.Resolution=1 THEN 1 ELSE 0 END AS Resolved
        INTO #Visits_640_179
        FROM #Cohort_640_179 AS c
        LEFT JOIN #Resolution_640_179 AS r
            ON c.VisitSID=r.VisitSID
        """

        (cohortLogic, resolutionLogic, combineQuery) = self.converter.convertReminder(siteCode, reminderIEN)

        # Write output to file
        outputFileName = "medinfo/dataconversion/test/programOutput/reminder" + str(reminderIEN) + ".output"
        outputFile = open(outputFileName, "w")
        outputFile.write(str.join('\n\n', [cohortLogic, resolutionLogic, combineQuery]))
        outputFile.close()

        self.assertEqualFile(StringIO(expectedCohortLogic), StringIO(cohortLogic), whitespace=False)
        #self.assertEqualFile(StringIO(expectedResolutionLogic), StringIO(resolutionLogic), whitespace=False)
        #self.assertEqualFile(StringIO(expectedCombineQuery), StringIO(combineQuery), whitespace=False)

    def test_dataConversion206(self):
        # Run the data conversion on sample cases and look for expected records
        # Finding 2 for this reminder actually produces no results, but this query
        # runs the FI(2) as PXRMD(811.5 rather than PXRMD(811.4 pro
        log.debug("PA-SMT Consult Renewal")
        queryData = {
            "siteCode": 640,
            "reminderIEN": 206
        }
        expectedCohortLogic = \
        """-- Cohort: SITECODE=640, IEN=206, PA-SMT CONSULT RENEWAL

        IF Object_Id('tempdb..#ft1') IS NOT NULL DROP TABLE #ft1
    	SELECT Sta3n, VisitDateTime AS DateTime, PatientSID
        INTO #ft1
    	FROM [ORD_Chan_201406081D].[Src].[HF_HealthFactor]
    	WHERE Sta3n=640 AND HealthFactorIEN NOT IN (640280)

        IF Object_Id('tempdb..#ft2_sf_LAB') IS NOT NULL DROP TABLE #ft2_sf_LAB
    	SELECT t1.Sta3n, t1.LabChemSpecimenDateTime AS DateTime, t1.PatientSID
        INTO #ft2_sf_LAB
        FROM [ORD_Chan_201406081D].[Src].[Chem_PatientLabChem] AS t1
    	INNER JOIN [CDWWork_FY14].[Dim].[LabChemTest] AS t2
    		ON t1.LabChemTestSID=t2.LabChemTestSID AND t1.Sta3n=t2.Sta3n
    			AND t2.LabChemTestIEN IN (131)
    	WHERE t1.Sta3n=640

        IF Object_Id('tempdb..#ft2') IS NOT NULL DROP TABLE #ft2
        SELECT *
        INTO #ft2
        FROM #ft2_sf_LAB

        IF Object_Id('tempdb..#ft5') IS NOT NULL DROP TABLE #ft5
    	SELECT Sta3n, VisitDateTime AS DateTime, PatientSID
        INTO #ft5
    	FROM [ORD_Chan_201406081D].[Src].[HF_HealthFactor]
    	WHERE Sta3n=640 AND HealthFactorIEN NOT IN (640281)

        IF Object_Id('tempdb..#Cohort_640_206') IS NOT NULL DROP TABLE #Cohort_640_206
        SELECT v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID, 1 AS Cohort
        INTO #Cohort_640_206
        FROM [ORD_Chan_201406081D].[Src].[Outpat_Visit] AS v
        INNER JOIN #ft1
            ON v.PatientSID=#ft1.PatientSID AND v.Sta3n=#ft1.Sta3n
                AND v.VisitDateTime>=#ft1.DateTime
                AND #ft1.DateTime>=DATEADD(year, -1, v.VisitDateTime)
        INNER JOIN #ft2
            ON v.PatientSID=#ft2.PatientSID AND v.Sta3n=#ft2.Sta3n
                AND v.VisitDateTime>=#ft2.DateTime
                AND #ft2.DateTime>=DATEADD(year, -1, v.VisitDateTime)
        INNER JOIN #ft5
            ON v.PatientSID=#ft5.PatientSID AND v.Sta3n=#ft5.Sta3n
                AND v.VisitDateTime>=#ft5.DateTime
                AND #ft5.DateTime>=DATEADD(year, -1, v.VisitDateTime)
        WHERE v.Sta3n=640
        GROUP BY v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID
        """

        #---- RESOLUTION LOGIC ----

        expectedResolutionLogic = \
        """-- Resolution: SITECODE=640, IEN=206, PA-SMT CONSULT RENEWAL
        IF Object_Id('tempdb..#ft3') IS NOT NULL DROP TABLE #ft3
    	SELECT Sta3n, VExamDateTime AS DateTime, PatientSID, ExamSID AS FindingIEN
        INTO #ft3
    	FROM [ORD_Chan_201406081D].[Src].[Outpat_VExam]
    	WHERE Sta3n=640 AND ExamSID IN (640013)

        IF Object_Id('tempdb..#ft4') IS NOT NULL DROP TABLE #ft4
    	SELECT Sta3n, VExamDateTime AS DateTime, PatientSID, ExamSID AS FindingIEN
        INTO #ft4
    	FROM [ORD_Chan_201406081D].[Src].[Outpat_VExam]
    	WHERE Sta3n=640 AND ExamSID IN (640014)

        IF Object_Id('tempdb..#ft3_4') IS NOT NULL DROP TABLE #ft3_4
        SELECT Sta3n, DateTime, PatientSID, FindingIEN
        INTO #ft3_4
        FROM (
        SELECT * FROM #ft3
        UNION
        SELECT * FROM #ft4
        ) AS a

        IF Object_Id('tempdb..#Resolution_640_206') IS NOT NULL DROP TABLE #Resolution_ 640_206
        SELECT v.VisitSID, 1 AS Resolution
        INTO #Resolution_640_206
        FROM #Cohort_640_206 AS v
        INNER JOIN #ft3_4
            ON v.PatientSID=#ft3_4.PatientSID AND v.Sta3n=#ft3_4.Sta3n
                AND v.VisitDateTime>=#ft3_4.DateTime
                AND ((#ft3_4.DateTime>=DATEADD(year, -1, v.VisitDateTime) AND #ft3_4.FindingIEN='640013')
                    OR (#ft3_4.DateTime>=DATEADD(month, -6, v.VisitDateTime) AND #ft3_4.FindingIEN='640014'))
        GROUP BY v.VisitSID
        """
         ### Assuming that for resolution we check for the Rx fill only 42 days back

        #---- COMBINED OUTPUT ----
        expectedCombineQuery = \
        """
        -- Combine: SITECODE=640, IEN=206, PA-SMT CONSULT RENEWAL
        IF Object_Id('tempdb..#Visits_640_206') IS NOT NULL DROP TABLE #Visits_640_206
        SELECT '640_206' AS Reminder, c.Sta3n, c.PatientSID, c.VisitSID, c.VisitDateTime, c.Cohort, CASE WHEN r.Resolution=1 THEN 1 ELSE 0 END AS Resolved
        INTO #Visits_640_206
        FROM #Cohort_640_206 AS c
        LEFT JOIN #Resolution_640_206 AS r
            ON c.VisitSID=r.VisitSID
        """

        (cohortLogic, resolutionLogic, combineQuery) = self.converter.convertReminder(queryData["siteCode"], queryData["reminderIEN"])

        # Write output to file
        outputFileName = "medinfo/dataconversion/test/programOutput/reminder" + str(queryData["reminderIEN"]) + ".output"
        outputFile = open(outputFileName, "w")
        outputFile.write(str.join('\n\n', [cohortLogic, resolutionLogic, combineQuery]))
        outputFile.close()

        self.assertEqualFile(StringIO(expectedCohortLogic), StringIO(cohortLogic), whitespace=False)
        self.assertEqualFile(StringIO(expectedResolutionLogic), StringIO(resolutionLogic), whitespace=False)
        self.assertEqualFile(StringIO(expectedCombineQuery), StringIO(combineQuery), whitespace=False)

    def test_dataConversion376(self):
        # Run the data conversion on sample cases and look for expected records

        log.debug("WARFARIN - INR NEEDED")
        queryData = {
            "siteCode": 640,
            "reminderIEN": 376,
            "findingsQueryName": "#ft1_2",
            "findingTableName1": "#ft1",
            "findingTableName2": "#ft2",
            "findingIEN": 865
        }
        expectedCohortLogic = \
        """-- Cohort: SITECODE=640, IEN=376, WARFARIN - INR NEEDED
        IF Object_Id('tempdb..#ft1') IS NOT NULL DROP TABLE #ft1
        SELECT Sta3n, DateTime, PatientSID, FindingIEN
        INTO #ft1
        FROM (
            SELECT t1.Sta3n, t1.RxOutpatFillSID, t1.FillDateTime AS DateTime, t1.PatientSID, t3.DrugNameWithoutDoseIEN AS FindingIEN
            FROM [ORD_Chan_201406081D].[Src].[RxOut_RxOutpatFill] AS t1
            INNER JOIN [CDWWork_FY14].[Dim].[NationalDrug] AS t2
                ON t1.Sta3n=t2.Sta3n AND t1.NationalDrugSID=t2.NationalDrugSID
            INNER JOIN [CDWWork_FY14].[Dim].[DrugNameWithoutDose] AS t3
                ON t2.DrugNameWithoutDoseSID=t3.DrugNameWithoutDoseSID AND t2.Sta3n=t3.Sta3n
                    AND t3.DrugNameWithoutDoseIEN IN (865)
            WHERE t1.Sta3n=640
            UNION
            SELECT t1.Sta3n, t1.RxOutpatFillSID, t1.FillDateTime AS DateTime, t1.PatientSID, t3.DrugNameWithoutDoseIEN AS FindingIEN
            FROM [ORD_Chan_201406081D].[Src].[RxOut_RxOutpatFill] AS t1
            INNER JOIN [CDWWork_FY14].[Dim].[LocalDrug] AS t2
                ON t1.Sta3n=t2.Sta3n AND t1.LocalDrugSID=t2.LocalDrugSID
            INNER JOIN [CDWWork_FY14].[Dim].[DrugNameWithoutDose] AS t3
                ON t2.DrugNameWithoutDoseSID=t3.DrugNameWithoutDoseSID AND t2.Sta3n=t3.Sta3n
                    AND t3.DrugNameWithoutDoseIEN IN (865)
            WHERE t1.Sta3n=640
        ) AS a

        IF Object_Id('tempdb..#ft2') IS NOT NULL DROP TABLE #ft2
        SELECT Sta3n, DateTime, PatientSID, FindingIEN
        INTO #ft2
        FROM (
            SELECT t1.Sta3n, t1.RxOutpatFillSID, t1.FillDateTime AS DateTime, t1.PatientSID, t3.DrugNameWithoutDoseIEN AS FindingIEN
            FROM [ORD_Chan_201406081D].[Src].[RxOut_RxOutpatFill] AS t1
            INNER JOIN [CDWWork_FY14].[Dim].[NationalDrug] AS t2
                ON t1.Sta3n=t2.Sta3n AND t1.NationalDrugSID=t2.NationalDrugSID
            INNER JOIN [CDWWork_FY14].[Dim].[DrugNameWithoutDose] AS t3
                ON t2.DrugNameWithoutDoseSID=t3.DrugNameWithoutDoseSID AND t2.Sta3n=t3.Sta3n
                    AND t3.DrugNameWithoutDoseIEN IN (865)
            WHERE t1.Sta3n=640
            UNION
            SELECT t1.Sta3n, t1.RxOutpatFillSID, t1.FillDateTime AS DateTime, t1.PatientSID, t3.DrugNameWithoutDoseIEN AS FindingIEN
            FROM [ORD_Chan_201406081D].[Src].[RxOut_RxOutpatFill] AS t1
            INNER JOIN [CDWWork_FY14].[Dim].[LocalDrug] AS t2
                ON t1.Sta3n=t2.Sta3n AND t1.LocalDrugSID=t2.LocalDrugSID
            INNER JOIN [CDWWork_FY14].[Dim].[DrugNameWithoutDose] AS t3
                ON t2.DrugNameWithoutDoseSID=t3.DrugNameWithoutDoseSID AND t2.Sta3n=t3.Sta3n
                    AND t3.DrugNameWithoutDoseIEN IN (865)
            WHERE t1.Sta3n=640
        ) AS a

        IF Object_Id('tempdb..#ft1_2') IS NOT NULL DROP TABLE #ft1_2
        SELECT Sta3n, DateTime, PatientSID, FindingIEN
        INTO #ft1_2
        FROM (
        SELECT * FROM #ft1
        UNION
        SELECT * FROM #ft2
        ) AS a

        IF Object_Id('tempdb..#Cohort_640_376') IS NOT NULL DROP TABLE #Cohort_640_376
        SELECT v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID, 1 AS Cohort
        INTO #Cohort_640_376
        FROM [ORD_Chan_201406081D].[Src].[Outpat_Visit] AS v
        INNER JOIN #ft1_2
            ON v.PatientSID=#ft1_2.PatientSID AND v.Sta3n=#ft1_2.Sta3n
                AND v.VisitDateTime>=#ft1_2.DateTime
                AND #ft1_2.DateTime>=DATEADD(day, -45, v.VisitDateTime)
        WHERE v.Sta3n=640
        GROUP BY v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID
        """

        #---- RESOLUTION LOGIC ----

        expectedResolutionLogic = \
        """-- Resolution: SITECODE=640, IEN=376, WARFARIN - INR NEEDED
        IF Object_Id('tempdb..#ft4') IS NOT NULL DROP TABLE #ft4
        SELECT t1.Sta3n, t1.LabChemSpecimenDateTime AS DateTime, t1.PatientSID, t2.LabChemTestIEN AS FindingIEN
        INTO #ft4
    	FROM [ORD_Chan_201406081D].[Src].[Chem_PatientLabChem] AS t1
    	INNER JOIN [CDWWork_FY14].[Dim].[LabChemTest] AS t2
    		ON t1.LabChemTestSID=t2.LabChemTestSID AND t1.Sta3n=t2.Sta3n
    			AND t2.LabChemTestIEN IN (5478)
    	WHERE t1.Sta3n=640

        IF Object_Id('tempdb..#ft6') IS NOT NULL DROP TABLE #ft6
    	SELECT Sta3n, VisitDateTime AS DateTime, PatientSID, HealthFactorIEN AS FindingIEN
        INTO #ft6
    	FROM [ORD_Chan_201406081D].[Src].[HF_HealthFactor]
    	WHERE Sta3n=640 AND HealthFactorIEN IN (612280)

        IF Object_Id('tempdb..#ft4_6') IS NOT NULL DROP TABLE #ft4_6
        SELECT Sta3n, DateTime, PatientSID, FindingIEN
        INTO #ft4_6
        FROM (
        SELECT * FROM #ft4
        UNION
        SELECT * FROM #ft6
        ) AS a

        IF Object_Id('tempdb..#Resolution_640_376') IS NOT NULL DROP TABLE #Resolution_640_376
        SELECT v.VisitSID, 1 AS Resolution
        INTO #Resolution_640_376
        FROM #Cohort_640_376 AS v
        INNER JOIN #ft4_6
            ON v.PatientSID=#ft4_6.PatientSID AND v.Sta3n=#ft4_6.Sta3n
                AND v.VisitDateTime>=#ft4_6.DateTime
                AND ((#ft4_6.DateTime>=DATEADD(day, -42, v.VisitDateTime) AND #ft4_6.FindingIEN='5478')
                    OR (#ft4_6.DateTime>=DATEADD(day, -42, v.VisitDateTime) AND #ft4_6.FindingIEN='612280'))
        GROUP BY v.VisitSID
        """
         ### Assuming that for resolution we check for the Rx fill only 42 days back

        #---- COMBINED OUTPUT ----
        expectedCombineQuery = \
        """
        -- Combine: SITECODE=640, IEN=376, WARFARIN - INR NEEDED
        IF Object_Id('tempdb..#Visits_640_376') IS NOT NULL DROP TABLE #Visits_640_376
        SELECT '640_376' AS Reminder, c.Sta3n, c.PatientSID, c.VisitSID, c.VisitDateTime, c.Cohort, CASE WHEN r.Resolution=1 THEN 1 ELSE 0 END AS Resolved
        INTO #Visits_640_376
        FROM #Cohort_640_376 AS c
        LEFT JOIN #Resolution_640_376 AS r
            ON c.VisitSID=r.VisitSID
        """


        (cohortLogic, resolutionLogic, combineQuery) = self.converter.convertReminder(queryData["siteCode"], queryData["reminderIEN"])

        # Write output to file
        outputFileName = "medinfo/dataconversion/test/programOutput/reminder" + str(queryData["reminderIEN"]) + ".output"
        outputFile = open(outputFileName, "w")
        outputFile.write(str.join('\n\n', [cohortLogic, resolutionLogic, combineQuery]))
        outputFile.close()

        self.assertEqualFile(StringIO(expectedCohortLogic), StringIO(cohortLogic), whitespace=False)
        self.assertEqualFile(StringIO(expectedResolutionLogic), StringIO(resolutionLogic), whitespace=False)
        self.assertEqualFile(StringIO(expectedCombineQuery), StringIO(combineQuery), whitespace=False)

    def test_dataConversion392(self):
        # Run the data conversion on sample cases and look for expected records
        # Finding 2 for this reminder actually produces no results, but this query
        # runs the FI(2) as PXRMD(811.5 rather than PXRMD(811.4 pro
        log.debug("Alcohol Use Screen (AUDIT-C)")
        queryData = {
            "siteCode": 640,
            "reminderIEN": 392
        }
        expectedCohortLogic = \
        """-- Cohort: SITECODE=640, IEN=392, PA-ALCOHOL USE SCREEN (AUDIT-C) FY09
        IF Object_Id('tempdb..#ft6_sf_AUTTHF') IS NOT NULL DROP TABLE #ft6_sf_AUTTHF
    	SELECT Sta3n, VisitDateTime AS DateTime, PatientSID, HealthFactorIEN AS FindingIEN
        INTO #ft6_sf_AUTTHF
    	FROM [ORD_Chan_201406081D].[Src].[HF_HealthFactor]
    	WHERE Sta3n=640 AND HealthFactorIEN NOT IN (612962)

        IF Object_Id('tempdb..#ft6_sf_YTT') IS NOT NULL DROP TABLE #ft6_sf_YTT
    	SELECT s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyResultIEN AS FindingIEN
        INTO #ft6_sf_YTT
    	FROM [ORD_Chan_201406081D].[Src].[MH_SurveyResult] AS s
        INNER JOIN [CDWWork_FY14].[Dim].[SurveyScale] AS ss
            ON s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND ss.SurveyScaleIEN=516
    	WHERE s.Sta3n=640 AND s.SurveyResultIEN NOT IN (67)

        IF Object_Id('tempdb..#ft6') IS NOT NULL DROP TABLE #ft6
        SELECT *
        INTO #ft6
        FROM (
        SELECT * FROM #ft6_sf_AUTTHF
        UNION
        SELECT * FROM #ft6_sf_YTT
        ) AS a

        IF Object_Id('tempdb..#Cohort_640_392') IS NOT NULL DROP TABLE #Cohort_640_392
        SELECT v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID, 1 AS Cohort
        INTO #Cohort_640_392
        FROM [ORD_Chan_201406081D].[Src].[Outpat_Visit] AS v
        INNER JOIN #ft6
        ON v.PatientSID=#ft6.PatientSID AND v.Sta3n=#ft6.Sta3n
        AND v.VisitDateTime>=#ft6.DateTime
        AND #ft6.DateTime>=DATEADD(year, -1, v.VisitDateTime)
        WHERE v.Sta3n=640
        GROUP BY v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID
        """

        #---- RESOLUTION LOGIC ----

        expectedResolutionLogic = \
        """-- Resolution: SITECODE=640, IEN=392, PA-ALCOHOL USE SCREEN (AUDIT-C) FY09
        IF Object_Id('tempdb..#ft1') IS NOT NULL DROP TABLE #ft1
    	SELECT s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyIEN
        INTO #ft1
    	FROM [CDWWork_FY14].[Dim].[Survey] AS s
        INNER JOIN [CDWWork_FY14].[Dim].[SurveyScale] AS ss
            ON s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND ss.SurveyScaleIEN=276 \
            AND s.SurveyIEN IN (5)
    	WHERE s.Sta3n=640

        IF Object_Id('tempdb..#ft3_sf_AUTTHF') IS NOT NULL DROP TABLE #ft3_sf_AUTTHF
    	SELECT Sta3n, VisitDateTime AS DateTime, PatientSID
        INTO #ft3_sf_AUTTHF
    	FROM [ORD_Chan_201406081D].[Src].[HF_HealthFactor]
    	WHERE Sta3n=640 AND HealthFactorTypeSID IN (612040)

        IF Object_Id('tempdb..#ft3_sf_YTT') IS NOT NULL DROP TABLE #ft3_sf_YTT
    	SELECT s.Sta3n, s.SurveyGivenDateTime AS DateTime, s.PatientSID, s.SurveyIEN
        INTO #ft3_sf_YTT
    	FROM [CDWWork_FY14].[Dim].[Survey] AS s
        INNER JOIN [CDWWork_FY14].[Dim].[SurveyScale] AS ss
            ON s.Sta3n=ss.Sta3n AND s.SurveyScale=ss.SurveyScaleName AND (
                (s.SurveyIEN IN (5) AND ss.SurveyScaleIEN=276)
                OR (s.SurveyIEN IN (17) AND ss.SurveyScaleIEN=276 AND s.SurveyGivenDateTime<=CONVERT(datetime, '10/1/05'))
                OR (s.SurveyIEN IN (7) AND ss.SurveyScaleIEN=278 AND s.SurveyGivenDateTime<=CONVERT(datetime, '10/1/07')))
    	WHERE Sta3n=640

        IF Object_Id('tempdb..#ft3') IS NOT NULL DROP TABLE #ft3
        SELECT *
        INTO #ft3
        FROM #ft3_sf_AUTTHF UNION (SELECT * FROM #ft3_sf_YTT)

        IF Object_Id('tempdb..#ft4_sf_AUTTHF') IS NOT NULL DROP TABLE #ft4_sf_AUTTHF
    	SELECT Sta3n, VisitDateTime AS DateTime, PatientSID
        INTO #ft4_sf_AUTTHF
    	FROM [ORD_Chan_201406081D].[Src].[HF_HealthFactor]
    	WHERE Sta3n=640 AND HealthFactorTypeSID IN (664106, 674060, 640062)

        IF Object_Id('tempdb..#ft4_sf_PXD') IS NOT NULL DROP TABLE #ft4_sf_PXD
        SELECT t1.Sta3n, t1.VDiagnosisDateTime AS DateTime, t1.PatientSID
        INTO #ft4_sf_PXD
        FROM [ORD_Chan_201406081D].[Src].[Outpat_VDiagnosis] AS t1
        INNER JOIN  (
            --ICD9 query
            SELECT Sta3n, ICD9SID as SID, ICD9Code as Code
            FROM [CDWWork_FY14].[Dim].[ICD9]
            WHERE ICD9Code IN ('157.1', '157.2', '157.3', '197.0', '197.1', '197.2', '197.3', '197.4', '197.5', '197.6', '197.7', '197.8', '198.0', '198.1', '198.2', '198.3', '198.4', '198.5', '198.6', '198.7', '198.81', '198.82', '150.0', '150.1', '150.2', '150.3', '150.4', '150.5', '150.8', '150.9', '155.0', '155.1', '155.2', '157.0', '157.4', '157.8', '157.9')
        ) AS i
            ON t1.ICDSID=i.SID AND t1.Sta3n=i.Sta3n
        		--AND (How to interpret taxonomy when stored as text rather than list of codes?
                    --)
        WHERE t1.Sta3n=640

        IF Object_Id('tempdb..#ft4') IS NOT NULL DROP TABLE #ft4
        SELECT *
        INTO #ft4
        FROM (#ft4_sf_AUTTHF UNION #ft4_sf_PXD)

        IF Object_Id('tempdb..#ft5_sf_AUTTHF') IS NOT NULL DROP TABLE #ft5_sf_AUTTHF
    	SELECT Sta3n, VisitDateTime AS DateTime, PatientSID
        INTO #ft5_sf_AUTTHF
    	FROM [ORD_Chan_201406081D].[Src].[HF_HealthFactor]
    	WHERE Sta3n=640 AND HealthFactorTypeSID IN (612193)

        IF Object_Id('tempdb..#ft4') IS NOT NULL DROP TABLE #ft4
        SELECT *
        INTO #ft4
        FROM (#ft4_sf_AUTTHF)

        IF Object_Id('tempdb..#Resolution_640_392') IS NOT NULL DROP TABLE #Resolution_ 640_392
        SELECT v.VisitSID, 1 AS Resolution
        INTO #Resolution_640_392
        FROM #Cohort_640_392 AS v
        GROUP BY v.VisitSID

        DELETE c
        FROM #Resolution_640_719 AS r
        INNER JOIN (
            SELECT v.VisitSID, 1 AS Resolution
            INTO #Resolution_640_392
            FROM #Cohort_640_392 AS v
            INNER JOIN #ft1
                ON v.PatientSID=#ft1.PatientSID AND v.Sta3n=#ft1.Sta3n AND v.VisitDateTime>=#ft1.DateTime
            INNER JOIN #ft3
                ON v.PatientSID=#ft3.PatientSID AND v.Sta3n=#ft3.Sta3n AND v.VisitDateTime>=#ft3.DateTime
            INNER JOIN #ft4
                ON v.PatientSID=#ft4.PatientSID AND v.Sta3n=#ft4.Sta3n AND v.VisitDateTime>=#ft4.DateTime \
                    AND (#ft4.DateTime>=DATEADD(month, -6, v.VisitDateTime)
            INNER JOIN #ft5
                ON v.PatientSID=#ft5.PatientSID AND v.Sta3n=#ft5.Sta3n AND v.VisitDateTime>=#ft5.DateTime
            GROUP BY v.VisitSID
        ) AS inner
        ON c.VisitSID=inner.VisitSID
        """

        #---- COMBINED OUTPUT ----
        expectedCombineQuery = \
        """
        -- Combine: SITECODE=640, IEN=392, PA-ALCOHOL USE SCREEN (AUDIT-C) FY09
        IF Object_Id('tempdb..#Visits_640_392') IS NOT NULL DROP TABLE #Visits_640_392
        SELECT '640_392' AS Reminder, c.Sta3n, c.PatientSID, c.VisitSID, c.VisitDateTime, c.Cohort, CASE WHEN r.Resolution=1 THEN 1 ELSE 0 END AS Resolved
        INTO #Visits_640_392
        FROM #Cohort_640_392 AS c
        LEFT JOIN #Resolution_640_392 AS r
            ON c.VisitSID=r.VisitSID
        """


        (cohortLogic, resolutionLogic, combineQuery) = self.converter.convertReminder(queryData["siteCode"], queryData["reminderIEN"])

        # Write output to file
        outputFileName = "medinfo/dataconversion/test/programOutput/reminder" + str(queryData["reminderIEN"]) + ".output"
        outputFile = open(outputFileName, "w")
        outputFile.write(str.join('\n\n', [cohortLogic, resolutionLogic, combineQuery]))
        outputFile.close()

        self.assertEqualFile(StringIO(expectedCohortLogic), StringIO(cohortLogic), whitespace=False)
        #self.assertEqualFile(StringIO(expectedResolutionLogic), StringIO(resolutionLogic), whitespace=False)
        #self.assertEqualFile(StringIO(expectedCombineQuery), StringIO(combineQuery), whitespace=False)

    def test_dataConversion596(self):
        # Run the data conversion on sample cases and look for expected records

        log.debug("V21 PBM AMIODARONE")
        siteCode = 640
        reminderIEN = 596

        expectedCohortLogic = \
        """-- Cohort: SITECODE=640, IEN=596, V21 PBM AMIODARONE
        IF Object_Id('tempdb..#ft1') IS NOT NULL DROP TABLE #ft1
        SELECT Sta3n, DateTime, PatientSID
        INTO #ft1
        FROM (
            SELECT t1.Sta3n, t1.RxOutpatFillSID, t1.FillDateTime AS DateTime, t1.PatientSID
            FROM [ORD_Chan_201406081D].[Src].[RxOut_RxOutpatFill] AS t1
            INNER JOIN [CDWWork_FY14].[Dim].[NationalDrug] AS t2
                ON t1.Sta3n=t2.Sta3n AND t1.NationalDrugSID=t2.NationalDrugSID
            INNER JOIN [CDWWork_FY14].[Dim].[DrugNameWithoutDose] AS t3
                ON t2.DrugNameWithoutDoseSID=t3.DrugNameWithoutDoseSID AND t2.Sta3n=t3.Sta3n
                    AND t3.DrugNameWithoutDoseIEN IN (389)
            WHERE t1.Sta3n=640
            UNION
            SELECT t1.Sta3n, t1.RxOutpatFillSID, t1.FillDateTime AS DateTime, t1.PatientSID
            FROM [ORD_Chan_201406081D].[Src].[RxOut_RxOutpatFill] AS t1
            INNER JOIN [CDWWork_FY14].[Dim].[LocalDrug] AS t2
                ON t1.Sta3n=t2.Sta3n AND t1.LocalDrugSID=t2.LocalDrugSID
            INNER JOIN [CDWWork_FY14].[Dim].[DrugNameWithoutDose] AS t3
                ON t2.DrugNameWithoutDoseSID=t3.DrugNameWithoutDoseSID AND t2.Sta3n=t3.Sta3n
                    AND t3.DrugNameWithoutDoseIEN IN (389)
            WHERE t1.Sta3n=640
        )

        IF Object_Id('tempdb..#Cohort_640_596') IS NOT NULL DROP TABLE #Cohort_640_596
        SELECT v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID, 1 AS Cohort
        INTO #Cohort_640_596
        FROM [ORD_Chan_201406081D].[Src].[Outpat_Visit] AS v
        INNER JOIN #ft1
            ON v.PatientSID=#ft1.PatientSID AND v.Sta3n=#ft1.Sta3n
                AND v.VisitDateTime>=#ft1.DateTime
                AND #ft1.DateTime>=DATEADD(day, -30, v.VisitDateTime)
        WHERE v.Sta3n=640
        GROUP BY v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID
        """

        expectedResolutionLogic = \
        """
        -- Resolution: SITECODE=640, IEN=596, V21 PBM AMIODARONE
        IF Object_Id('tempdb..#ft2_sf_AUTTHF') IS NOT NULL DROP TABLE #ft2_sf_AUTTHF
    	SELECT Sta3n, VisitDateTime AS DateTime, PatientSID
        INTO #ft2_sf_AUTTHF
    	FROM [ORD_Chan_201406081D].[Src].[HF_HealthFactor]
    	WHERE Sta3n=640 AND HealthFactorTypeSID IN (754, 640961, 640962)

        IF Object_Id('tempdb..#ft2_sf_LAB') IS NOT NULL DROP TABLE #ft2_sf_LAB
    	SELECT t1.Sta3n, t1.LabChemSpecimenDateTime AS DateTime, t1.PatientSID
        INTO #ft2_sf_LAB
        FROM [ORD_Chan_201406081D].[Src].[Chem_PatientLabChem] AS t1
    	INNER JOIN [CDWWork_FY14].[Dim].[LabChemTest] AS t2
    		ON t1.LabChemTestSID=t2.LabChemTestSID AND t1.Sta3n=t2.Sta3n
    			AND t2.LabChemTestIEN IN (190, 191)
    	WHERE t1.Sta3n=640

        IF Object_Id('tempdb..#ft2') IS NOT NULL DROP TABLE #ft2
        SELECT *
        INTO #ft2
        FROM #ft2_sf_AUTTHF UNION (SELECT * FROM #ft2_sf_LAB)

        IF Object_Id('tempdb..#ft3_sf_AUTTHF') IS NOT NULL DROP TABLE #ft3_sf_AUTTHF
    	SELECT Sta3n, VisitDateTime AS DateTime, PatientSID
        INTO #ft3_sf_AUTTHF
    	FROM [ORD_Chan_201406081D].[Src].[HF_HealthFactor]
    	WHERE Sta3n=640 AND HealthFactorTypeSID IN (755)

        IF Object_Id('tempdb..#ft3_sf_LAB') IS NOT NULL DROP TABLE #ft3_sf_LAB
    	SELECT t1.Sta3n, t1.LabChemSpecimenDateTime AS DateTime, t1.PatientSID
        INTO #ft3_sf_LAB
    	FROM [ORD_Chan_201406081D].[Src].[Chem_PatientLabChem] AS t1
    	INNER JOIN [CDWWork_FY14].[Dim].[LabChemTest] AS t2
    		ON t1.LabChemTestSID=t2.LabChemTestSID AND t1.Sta3n=t2.Sta3n
    			AND t2.LabChemTestIEN IN (110)
    	WHERE t1.Sta3n=640

        IF Object_Id('tempdb..#ft3') IS NOT NULL DROP TABLE #ft3
        SELECT *
        INTO #ft3
        FROM #ft3_sf_AUTTHF UNION (SELECT * FROM #ft3_sf_LAB)

        IF Object_Id('tempdb..#Resolution_640_596') IS NOT NULL DROP TABLE #Resolution_640_596
        SELECT v.VisitSID, 1 AS Resolution
        INTO #Resolution_640_596
        FROM #Cohort_640_596 AS v
        INNER JOIN #ft2
            ON v.PatientSID=#ft2.PatientSID AND v.Sta3n=#ft2.Sta3n
                AND v.VisitDateTime>=#ft2.DateTime
                AND #ft2.DateTime>=DATEADD(month, -6, v.VisitDateTime)
        INNER JOIN #ft3
            ON v.PatientSID=#ft3.PatientSID AND v.Sta3n=#ft3.Sta3n
                AND v.VisitDateTime>=#ft3.DateTime
                AND #ft3.DateTime>=DATEADD(month, -6, v.VisitDateTime)
        GROUP BY v.VisitSID
        """

        expectedCombineQuery = \
        """
        -- Combine: SITECODE=640, IEN=596, V21 PBM AMIODARONE
        IF Object_Id('tempdb..#Visits_640_596') IS NOT NULL DROP TABLE #Visits_640_596
        SELECT '640_596' AS Reminder, c.Sta3n, c.PatientSID, c.VisitSID, c.VisitDateTime, c.Cohort,
            CASE WHEN r.Resolution=1 THEN 1 ELSE 0 END AS Resolved
        INTO #Visits_640_596
        FROM #Cohort_640_596 AS c
        LEFT JOIN #Resolution_640_596 AS r
            ON c.VisitSID=r.VisitSID
        """

        (cohortLogic, resolutionLogic, combineQuery) = self.converter.convertReminder(siteCode, reminderIEN)


        # Write output to file
        outputFileName = "medinfo/dataconversion/test/programOutput/reminder" + str(reminderIEN) + ".output"
        outputFile = open(outputFileName, "w")
        outputFile.write(str.join('\n\n', [cohortLogic, resolutionLogic, combineQuery]))
        outputFile.close()

        self.assertEqualFile(StringIO(expectedCohortLogic), StringIO(cohortLogic), whitespace=False)
        self.assertEqualFile(StringIO(expectedResolutionLogic), StringIO(resolutionLogic), whitespace=False)
        self.assertEqualFile(StringIO(expectedCombineQuery), StringIO(combineQuery), whitespace=False)

    def test_dataConversion719(self):
        # Run the data conversion on sample cases and look for expected records

        log.debug("PA-CONSIDER CLOZAPINE (PSYCHIATRIST ONLY)")
        siteCode = 640
        reminderIEN = 719

        expectedCohortLogic = \
        """-- Cohort: SITECODE=640, IEN=719, PA-CONSIDER CLOZAPINE (PSYCHIATRIST ONLY)
        IF Object_Id('tempdb..#ft1') IS NOT NULL DROP TABLE #ft1
        SELECT t1.Sta3n, t1.VDiagnosisDateTime AS DateTime, t1.PatientSID, '640023' AS FindingIEN
        INTO #ft1
        FROM [ORD_Chan_201406081D].[Src].[Outpat_VDiagnosis] AS t1
        INNER JOIN (
            SELECT Sta3n, ICD9SID as SID, ICD9Code as Code
            FROM [CDWWork_FY14].[Dim].[ICD9]
            WHERE ICD9Code BETWEEN '295.00' AND '295.95'
        ) AS i
        ON t1.ICDSID=i.SID AND t1.Sta3n=i.Sta3n
        WHERE t1.Sta3n=640

        IF Object_Id('tempdb..#ft2_sf_PSDRUG') IS NOT NULL DROP TABLE #ft2_sf_PSDRUG
    	SELECT t1.Sta3n, t1.FillDateTime AS DateTime, t1.PatientSID, t2.LocalDrugIEN AS FindingIEN
        INTO #ft2_sf_PSDRUG
        FROM [ORD_Chan_201406081D].[Src].[RxOut_RxOutpatFill] AS t1
        INNER JOIN [CDWWork_FY14].[Dim].[LocalDrug] AS t2
            ON t1.DrugNameWithoutDose=t2.DrugNameWithoutDose AND t1.Sta3n=t2.Sta3n AND t2.LocalDrugIEN IN (29021, 29022)
        WHERE t1.Sta3n=640

        IF Object_Id('tempdb..#ft2_sf_PSNDF') IS NOT NULL DROP TABLE #ft2_sf_PSNDF
        SELECT Sta3n, DateTime, PatientSID, FindingIEN
        INTO #ft2_sf_PSNDF
        FROM (
            SELECT t1.Sta3n, t1.RxOutpatFillSID, t1.FillDateTime AS DateTime, t1.PatientSID, t3.DrugNameWithoutDoseIEN AS FindingIEN
            FROM [ORD_Chan_201406081D].[Src].[RxOut_RxOutpatFill] AS t1
            INNER JOIN [CDWWork_FY14].[Dim].[NationalDrug] AS t2
                ON t1.Sta3n=t2.Sta3n AND t1.NationalDrugSID=t2.NationalDrugSID
            INNER JOIN [CDWWork_FY14].[Dim].[DrugNameWithoutDose] AS t3
                ON t2.DrugNameWithoutDoseSID=t3.DrugNameWithoutDoseSID AND t2.Sta3n=t3.Sta3n
                    AND t3.DrugNameWithoutDoseIEN IN (2129, 3728, 3725, 3726, 3727)
            WHERE t1.Sta3n=640
        ) AS a

        IF Object_Id('tempdb..#ft2') IS NOT NULL DROP TABLE #ft2
        SELECT f.Sta3n, f.DateTime, f.PatientSID, f.FindingIEN
        INTO #ft2
        FROM (
        SELECT * FROM #ft2_sf_PSDRUG
        UNION
        SELECT * FROM #ft2_sf_PSNDF
        ) AS f

        IF Object_Id('tempdb..#Cohort_640_719') IS NOT NULL DROP TABLE #Cohort_640_719
        SELECT a.Sta3n, a.VisitSID, a.VisitDateTime, a.PatientSID, 1 AS Cohort
        INTO #Cohort_640_719
        FROM (
            SELECT v.Sta3n, v.VisitSID, v.VisitDateTime, v.PatientSID, 1 AS Cohort
            FROM [ORD_Chan_201406081D].[Src].[Outpat_Visit] AS v
            INNER JOIN #ft1
                ON v.PatientSID=#ft1.PatientSID AND v.Sta3n=#ft1.Sta3n
                    AND v.VisitDateTime>=#ft1.DateTime
                    AND #ft1.DateTime>=DATEADD(year, -3, v.VisitDateTime)
            LEFT JOIN #ft2
                ON v.PatientSID=#ft2.PatientSID AND v.Sta3n=#ft2.Sta3n
                    AND v.VisitDateTime>=#ft2.DateTime
                    AND #ft2.DateTime>=DATEADD(day, -30, v.VisitDateTime)
            WHERE (#ft2.FindingIEN IS NULL)
        ) AS a
        WHERE a.Sta3n=640
        GROUP BY a.Sta3n, a.VisitSID, a.VisitDateTime, a.PatientSID
        """

        expectedResolutionLogic = \
        """
        -- Resolution: SITECODE=640, IEN=719, PA-CONSIDER CLOZAPINE (PSYCHIATRIST ONLY)
        IF Object_Id('tempdb..#ft3') IS NOT NULL DROP TABLE #ft3
    	SELECT Sta3n, VisitDateTime AS DateTime, PatientSID
        INTO #ft3
    	FROM [ORD_Chan_201406081D].[Src].[HF_HealthFactor]
    	WHERE Sta3n=640 AND HealthFactorTypeSID IN (640876)


        IF Object_Id('tempdb..#ft4') IS NOT NULL DROP TABLE #ft4
        SELECT Sta3n, VisitDateTime AS DateTime, PatientSID
        INTO #ft4
    	FROM [ORD_Chan_201406081D].[Src].[HF_HealthFactor]
    	WHERE Sta3n=640 AND HealthFactorTypeSID IN (640877)

        IF Object_Id('tempdb..#ft5') IS NOT NULL DROP TABLE #ft5
        SELECT o.Sta3n, o.EnteredDateTime AS DateTime, o.PatientSID
        INTO #ft5
        FROM [ORD_Chan_201406081D].[Src].[CPRSOrder_OrderedItem] as o
        INNER JOIN [CDWWork_FY14].[Dim].[OrderableItem] as i
        	ON o.Sta3n=i.Sta3n AND o.OrderableItemSID=i.OrderableItemSID
        		AND i.OrderableItemIEN IN (13304)
        WHERE o.Sta3n=640

        IF Object_Id('tempdb..#ft3_4_5') IS NOT NULL DROP TABLE #ft3_4_5
        SELECT Sta3n, DateTime, PatientSID
        INTO #ft3_4_5
        FROM #ft3 UNION (SELECT * FROM #ft4) UNION (SELECT * FROM #ft5)

        IF Object_Id('tempdb..#Resolution_640_719') IS NOT NULL DROP TABLE #Resolution_640_719
        SELECT v.VisitSID, 1 AS Resolution
        INTO #Resolution_640_719
        FROM #Cohort_640_719 AS v
        INNER JOIN #ft3_4_5
            ON v.PatientSID=#ft3_4_5.PatientSID AND v.Sta3n=#ft3_4_5.Sta3n
                AND v.VisitDateTime>=#ft3_4_5.DateTime
                AND #ft3_4_5.DateTime>=DATEADD(year, -2, v.VisitDateTime)
        GROUP BY v.VisitSID
        """

        expectedCombineQuery = \
        """
        -- Combine: SITECODE=640, IEN=719, PA-CONSIDER CLOZAPINE (PSYCHIATRIST ONLY)
        IF Object_Id('tempdb..#Visits_640_719') IS NOT NULL DROP TABLE #Visits_640_719
        SELECT '640_719' AS Reminder, c.Sta3n, c.PatientSID, c.VisitSID, c.VisitDateTime, c.Cohort,
            CASE WHEN r.Resolution=1 THEN 1 ELSE 0 END AS Resolved
        INTO #Visits_640_719
        FROM #Cohort_640_719 AS c
        LEFT JOIN #Resolution_640_719 AS r
            ON c.VisitSID=r.VisitSID
        """

        (cohortLogic, resolutionLogic, combineQuery) = self.converter.convertReminder(siteCode, reminderIEN)

        # Write output to file
        outputFileName = "medinfo/dataconversion/test/programOutput/reminder" + str(reminderIEN) + ".output"
        outputFile = open(outputFileName, "w")
        outputFile.write(str.join('\n\n', [cohortLogic, resolutionLogic, combineQuery]))
        outputFile.close()

        self.assertEqualFile(StringIO(expectedCohortLogic), StringIO(cohortLogic), whitespace=False)
        #self.assertEqualFile(StringIO(expectedResolutionLogic), StringIO(resolutionLogic), whitespace=False)
        #self.assertEqualFile(StringIO(expectedCombineQuery), StringIO(combineQuery), whitespace=False)

    def test_dataConversion812(self):
        # Run the data conversion on sample cases and look for expected records

        log.debug("ZZPA-HTN ASSESSMENT BP >=140/90 FY12")
        siteCode = 640
        reminderIEN = 812

        expectedCohortLogic = \
        """
        -- Cohort: SITECODE=640, IEN=812, ZZPA-HTN ASSESSMENT BP >=140/90 FY12

        """

        expectedResolutionLogic = \
        """
        -- Resolution: SITECODE=640, IEN=812, ZZPA-HTN ASSESSMENT BP >=140/90 FY12

        """

        expectedCombineQuery = \
        """
        -- Combine: SITECODE=640, IEN=812, ZZPA-HTN ASSESSMENT BP >=140/90 FY12
        IF Object_Id('tempdb..#Visits_640_812') IS NOT NULL DROP TABLE #Visits_640_812
        SELECT '640_719' AS Reminder, c.Sta3n, c.PatientSID, c.VisitSID, c.VisitDateTime, c.Cohort,
            CASE WHEN r.Resolution=1 THEN 1 ELSE 0 END AS Resolved
        INTO #Visits_640_812
        FROM #Cohort_640_812 AS c
        LEFT JOIN #Resolution_640_812 AS r
            ON c.VisitSID=r.VisitSID
        """

        (cohortLogic, resolutionLogic, combineQuery) = self.converter.convertReminder(siteCode, reminderIEN)

        # Write output to file
        outputFileName = "medinfo/dataconversion/test/programOutput/reminder" + str(reminderIEN) + ".output"
        outputFile = open(outputFileName, "w")
        outputFile.write(str.join('\n\n', [cohortLogic, resolutionLogic, combineQuery]))
        outputFile.close()

        #self.assertEqualFile(StringIO(expectedCohortLogic), StringIO(cohortLogic), whitespace=False)
        #self.assertEqualFile(StringIO(expectedResolutionLogic), StringIO(resolutionLogic), whitespace=False)
        #self.assertEqualFile(StringIO(expectedCombineQuery), StringIO(combineQuery), whitespace=False)

    def test_parseReminderModel(self):
        """Top-level parsing of logic string into stack of items and operators"""
        testModel = {"INTRNL_PTNT_CHRT_LGC_31": "(SEX)&(AGE)&FI(1)&FI(2)"}
        expectedCohortLogicStack = \
            [   {"negate": False, "type": "SEX", "index": None },
                "&",
                {"negate": False, "type": "AGE", "index": None },
                "&",
                {"negate": False, "type": "FI", "index": 1 },
                "&",
                {"negate": False, "type": "FI", "index": 2 },
            ]
        self.converter.parseReminderModel( testModel )
        self.assertEqual(expectedCohortLogicStack, testModel["cohortLogicStack"])

        testModel = {"INTRNL_PTNT_CHRT_LGC_31": "(SEX)&(AGE)&FI(2)&'FI(3)"}
        expectedCohortLogicStack = \
            [   {"negate": False, "type": "SEX", "index": None },
                "&",
                {"negate": False, "type": "AGE", "index": None },
                "&",
                {"negate": False, "type": "FI", "index": 2 },
                "&",
                {"negate": True, "type": "FI", "index": 3 },
            ]
        self.converter.parseReminderModel( testModel )
        self.assertEqual(expectedCohortLogicStack, testModel["cohortLogicStack"])

        testModel = {"INTRNL_PTNT_CHRT_LGC_31": "FI(1)&FF(1)&(FI(5)!FI(6)!FI(7))&FF(2)"}
        expectedCohortLogicStack = \
            [   {"negate": False, "type": "FI", "index": 1 },
                "&",
                {"negate": False, "type": "FF", "index": 1 },
                "&",
                "(",
                    {"negate": False, "type": "FI", "index": 5 },
                    "|",
                    {"negate": True, "type": "FI", "index": 6 },
                    "|",
                    {"negate": True, "type": "FI", "index": 7 },
                ")",
                "&",
                {"negate": False, "type": "FF", "index": 2 },
            ]
        self.converter.parseReminderModel( testModel )
        self.assertEqual(expectedCohortLogicStack, testModel["cohortLogicStack"])

def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite()
    #suite.addTest(TestVAReminderToQuery("test_incColNamesAndTypeCodes"))
    #suite.addTest(TestVAReminderToQuery("test_insertFile_skipErrors"))
    #suite.addTest(TestVAReminderToQuery('test_executeIterator'))
    #suite.addTest(TestVAReminderToQuery('test_dataConversion116'))
    suite.addTest(TestVAReminderToQuery('test_dataConversion179'))
    #suite.addTest(TestVAReminderToQuery('test_dataConversion206'))
    #suite.addTest(TestVAReminderToQuery('test_dataConversion376'))
    #suite.addTest(TestVAReminderToQuery('test_dataConversion392'))
    #suite.addTest(TestVAReminderToQuery('test_dataConversion596'))
    #suite.addTest(TestVAReminderToQuery('test_dataConversion719'))
    #suite.addTest(TestVAReminderToQuery('test_dataConversion812'))
    #suite.addTest(unittest.makeSuite(TestVAReminderToQuery))

    return suite

if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
