#!/usr/bin/python
"""
Class for automatically authoring a report with high level summary information
about the patients, treatment teams, and medical decisions in STRIDE data set.
"""

import matplotlib.pyplot as plt
import numpy as np

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery

class STRIDEDescription:
    ADMIT_DX_CATEGORY_ID = 2
    DISCHARGE_CATEGORY_ID = 13
    ADMISSION_CATEGORY_ID = 23
    CODE_STATUS_CATEGORY_ID = 22

    def __init__(self):
        # Initialize DB connection.
        connection = DBUtil.connection()
        self.dbCursor = connection.cursor()

        # Aggressively cache queries as much as possible.
        self.dbCache = {}

        # Collect stats of interest, always collecting annual statistics.
        # print self._getNumUniquePatients()
        # print self._getNumPatientEncounters()
        # print self._getAdmitDateRange()
        # print self._getNumPatientEncountersByMonth()
        print(self._getPatientDemographics())
        #self.plotNumPatientEncountersByMonth()
        #self.plotPatientDemographicsByMonth()

        # Write statistics to textfile report.
        pass

    def _executeCachedDBQuery(self, query):
        # Only query if results not in cache.
        cacheKey = str(query)
        if cacheKey not in self.dbCache:
            self.dbCache[cacheKey] = DBUtil.execute(query)

        return self.dbCache[cacheKey]

    def _getAdmitDateRange(self):
        # Get list of all clinical item IDs matching admit diagnosis.
        # Get this list in advance to make subsequent query run a bit faster.
        admitDxClinicalItemIds = self._getAdmitDxClinicalItemIds()

        # Build query for earliest and latest admissions.
        # SELECT
        #   MIN(item_date) AS first_admit_date,
        #   MAX(item_date) AS last_admit_date,
        # FROM
        #   patient_item
        # WHERE
        #   clinical_item_id in (admitDxClinicalItemIds)
        query = SQLQuery()
        query.addSelect("MIN(item_date) AS first_admit_date")
        query.addSelect("MAX(item_date) AS last_admit_date")
        query.addFrom("patient_item")
        query.addWhereIn("clinical_item_id", admitDxClinicalItemIds)

        # Execute query and return results.
        results = self._executeCachedDBQuery(query)
        firstAdmitDate = DBUtil.parseDateValue(results[0][0]).date()
        lastAdmitDate = DBUtil.parseDateValue(results[0][1]).date()

        return firstAdmitDate, lastAdmitDate

    def _getNumUniquePatients(self):
        # Build query.
        # SELECT
        #   COUNT(DISTINCT patient_id) AS num_unique_patients
        # FROM
        #   patient_item
        query = SQLQuery()
        query.addSelect("COUNT(DISTINCT patient_id) AS num_unique_patients")
        query.addFrom("patient_item")

        # Execute query and return results.
        results = self._executeCachedDBQuery(query)
        numUniquePatients = DBUtil.parseValue(results[0][0], "num_unique_patients")

        return numUniquePatients

    def _getNumPatientEncounters(self):
        # Build query.
        # SELECT
        #   COUNT(DISTINCT encounter_id) AS num_patient_encounters
        # FROM
        #   patient_item
        query = SQLQuery()
        query.addSelect("COUNT(DISTINCT encounter_id) AS num_patient_encounters")
        query.addFrom("patient_item")

        # Execute query and return results.
        results = self._executeCachedDBQuery(query)
        numPatientEncounters = DBUtil.parseValue(results[0][0], "num_patient_encounters")

        return numPatientEncounters

    def plotNumPatientEncountersByMonth(self):
        encountersByMonth = self._getNumPatientEncountersByMonth()
        months = ['%s-%s' % (row[1], row[0]) for row in encountersByMonth]
        xPos = np.arange(len(months))
        values = [row[2] for row in encountersByMonth]

        plt.bar(xPos, values, align='center')
        plt.ylabel('# patient encounters')
        plt.xlabel('month')
        plt.xticks(xPos[0::6], months[0::6], rotation=45, horizontalalignment="right")
        plt.title('Stanford hospital patient encounters by month')
        plt.tight_layout()
        plt.savefig("stanford-inpatient-encounters-by-month.png")

    def _getNumPatientEncountersByMonth(self):
        # Build query.
        # SELECT
        #   CAST(EXTRACT(YEAR FROM noted_date) AS INT) AS admit_year,
        #   CAST(EXTRACT(MONTH FROM noted_date) AS INT) AS admit_month
        #   COUNT(DISTINCT pat_enc_csn_id) AS num_encounters,
        # FROM
        #   stride_dx_list
        # WHERE
        #   data_source = 'ADMIT_DX'
        # GROUP BY
        #   admit_year,
        #   admit_month
        # ORDER BY
        #   admit_year,
        #   admit_month
        query = SQLQuery()
        query.addSelect("CAST(EXTRACT(YEAR FROM noted_date) AS INT) AS admit_year")
        query.addSelect("CAST(EXTRACT(MONTH FROM noted_date) AS INT) AS admit_month")
        query.addSelect("COUNT(DISTINCT pat_enc_csn_id) AS num_encounters")
        query.addFrom("stride_dx_list")
        query.addWhereEqual("data_source", 'ADMIT_DX')
        query.addGroupBy("admit_year")
        query.addGroupBy("admit_month")
        query.addOrderBy("admit_year")
        query.addOrderBy("admit_month")

        # Execute query and return results.
        results = DBUtil.execute(query)
        encountersPerMonth = list()
        for row in results:
            admitYear = row[0]
            admitMonth = row[1]
            numEncounters = row[2]
            encountersPerMonth.append((admitYear, admitMonth, numEncounters))

        return encountersPerMonth

    def plotPatientDemographicsByMonth(self):
        demographicsByMonth = self._getPatientDemographicsByMonth()

        months = ['%s-%s' % (row[1], row[0]) for row in demographicsByMonth]
        xPos = np.arange(len(months))

        # Demographics by Sex by Month
        males = [row[3] for row in demographicsByMonth]
        females = [row[4] for row in demographicsByMonth]
        b1 = plt.bar(xPos, males, align='center')
        b2 = plt.bar(xPos, females, align='center', bottom=males)
        plt.ylabel('# patient encounters')
        plt.xlabel('month')
        plt.xticks(xPos[0::6], months[0::6], rotation=45, horizontalalignment="right")
        plt.title('Stanford hospital patient encounters by sex by month')
        plt.legend((b1[0], b2[0]), ('Male', 'Female'), loc='best')
        plt.tight_layout()
        plt.savefig("stanford-inpatient-encounters-by-sex-by-month.png")
        # Clear figure.
        plt.clf()

        # Demographics by Race by Month
        whites = np.array([row[5] for row in demographicsByMonth])
        asians = np.array([row[6] for row in demographicsByMonth])
        hispanics = np.array([row[7] for row in demographicsByMonth])
        blacks = np.array([row[8] for row in demographicsByMonth])
        pacificIslanders = np.array([row[9] for row in demographicsByMonth])
        others = np.array([row[10] for row in demographicsByMonth])
        unknowns = np.array([row[11] for row in demographicsByMonth])
        b1 = plt.bar(xPos, whites, align='center')
        b2 = plt.bar(xPos, asians, align='center', bottom=whites)
        b3 = plt.bar(xPos, hispanics, align='center', bottom=whites+asians)
        b4 = plt.bar(xPos, blacks, align='center', bottom=whites+asians+hispanics)
        b5 = plt.bar(xPos, pacificIslanders, align='center', bottom=whites+asians+hispanics+blacks)
        b6 = plt.bar(xPos, others, align='center', bottom=whites+asians+hispanics+blacks+pacificIslanders)
        b7 = plt.bar(xPos, unknowns, align='center', bottom=whites+asians+hispanics+blacks+pacificIslanders+others)
        plt.ylabel('# patient encounters')
        plt.xlabel('month')
        plt.title('Stanford hospital patient encounters by race by month')
        plt.xticks(xPos[0::6], months[0::6], rotation=45, horizontalalignment="right")
        plt.legend((b1[0], b2[0], b3[0], b4[0], b5[0], b6[0], b7[0]), \
            ('White', 'Asian', 'Hispanic', 'Black', 'Pacific Islander', 'Other', 'Unknown'),\
                loc='upper left')
        plt.tight_layout()
        plt.savefig('stanford-inpatient-encounters-by-race-by-month.png')
        # Clear figure.
        plt.clf()

        # Demographics by Age by Month
        # Get data from SQL results, relying on order for semantic meaning.
        brackets = list()
        for i in range(12,20):
            bracket = np.array([row[i] for row in demographicsByMonth])
            brackets.append(bracket)

        # Plot bars.
        bars = list()
        cumSum = np.array([0] * len(months))
        for bracket in brackets:
            bar = plt.bar(xPos, bracket, align='center', bottom=cumSum)
            bars.append(bar)
            cumSum += bracket

        plt.ylabel('# patient encounters')
        plt.xlabel('month')
        plt.title('Stanford hospital patient encounters by age by month')
        plt.xticks(xPos[0::6], months[0::6], rotation=45, horizontalalignment="right")
        plt.legend([bar[0] for bar in bars], \
            ('<5', '5 - 17', '18 - 24', '25 - 35', '36 - 54', '55 - 64', '65 - 80', '81+'),\
                loc='upper left')
        plt.tight_layout()
        plt.savefig('stanford-inpatient-encounters-by-age-by-month.png')
        # Clear figure.
        plt.clf()

    def _getPatientDemographicsByMonth(self):
        # Build query.
        query = " \
        SELECT \
            admit_year, \
            admit_month, \
            COUNT(DISTINCT encounter_id) AS num_patient_encounters, \
            SUM(male) AS num_males, \
            SUM(female) AS num_females, \
            SUM(white) AS num_white, \
            SUM(asian) AS num_asian, \
            SUM(hispanic) AS num_hispanic, \
            SUM(black) AS num_black, \
            SUM(pacific_islander) AS num_pacific_islander, \
            SUM(other) AS num_other, \
            SUM(unknown) AS num_unknown, \
            SUM(CASE WHEN admit_year - birth_year <= 5 THEN 1 ELSE 0 END) AS num_lt_5, \
            SUM(CASE WHEN admit_year - birth_year > 5 AND admit_year - birth_year <= 17 THEN 1 ELSE 0 END) AS num_5_17, \
            SUM(CASE WHEN admit_year - birth_year > 17 AND admit_year - birth_year <= 24 THEN 1 ELSE 0 END) AS num_18_24, \
            SUM(CASE WHEN admit_year - birth_year > 24 AND admit_year - birth_year <= 34 THEN 1 ELSE 0 END) AS num_25_35, \
            SUM(CASE WHEN admit_year - birth_year > 34 AND admit_year - birth_year <= 54 THEN 1 ELSE 0 END) AS num_35_55, \
            SUM(CASE WHEN admit_year - birth_year > 54 AND admit_year - birth_year <= 64 THEN 1 ELSE 0 END) AS num_55_65, \
            SUM(CASE WHEN admit_year - birth_year > 64 AND admit_year - birth_year <= 80 THEN 1 ELSE 0 END) AS num_65_80, \
            SUM(CASE WHEN admit_year - birth_year > 80 THEN 1 ELSE 0 END) AS num_gt_80 \
        FROM \
            ( \
            SELECT \
              dl.pat_enc_csn_id AS encounter_id, \
              CAST(EXTRACT(YEAR FROM dl.noted_date) AS INT) AS admit_year, \
              CAST(EXTRACT(MONTH FROM dl.noted_date) AS INT) AS admit_month, \
              CASE WHEN p.gender = 'MALE' THEN 1 ELSE 0 END AS male, \
              CASE WHEN p.gender = 'FEMALE' THEN 1 ELSE 0 END AS female, \
              CASE WHEN p.race LIKE '%WHITE%' THEN 1 ELSE 0 END AS white, \
              CASE WHEN p.race LIKE '%ASIAN%' THEN 1 ELSE 0 END AS asian, \
              CASE WHEN p.race LIKE '% HISPANIC%' THEN 1 ELSE 0 END AS hispanic, \
              CASE WHEN p.race LIKE '%BLACK%' THEN 1 ELSE 0 END AS black, \
              CASE WHEN p.race LIKE '%PACIFIC ISLANDER%' THEN 1 ELSE 0 END AS pacific_islander, \
              CASE WHEN p.race LIKE '%OTHER%' THEN 1 ELSE 0 END AS other, \
              CASE WHEN p.race LIKE '%UNKNOWN%' THEN 1 ELSE 0 END AS unknown, \
              p.birth_year AS birth_year \
            FROM \
              stride_dx_list AS dl \
            JOIN \
              stride_patient AS p \
            ON \
              dl.pat_id = p.pat_id \
            WHERE \
              data_source = 'ADMIT_DX' \
            ) x \
        GROUP BY \
            admit_year, \
            admit_month \
        ORDER BY \
            admit_year, \
            admit_month \
        "

        # Execute query and return results.
        self.dbCursor.execute(query)
        demographicsByMonth = list()
        for row in self.dbCursor:
            demographicsByMonth.append(row)

        return demographicsByMonth

    def _getPatientDemographics(self):
        # Build query.
        query = " \
        SELECT \
            COUNT(DISTINCT patient_id) AS num_patients, \
            SUM(male) AS num_males, \
            SUM(female) AS num_females, \
            SUM(white) AS num_white, \
            SUM(asian) AS num_asian, \
            SUM(hispanic) AS num_hispanic, \
            SUM(black) AS num_black, \
            SUM(pacific_islander) AS num_pacific_islander, \
            SUM(other) AS num_other, \
            SUM(unknown) AS num_unknown, \
            SUM(CASE WHEN admit_year - birth_year <= 5 THEN 1 ELSE 0 END) AS num_lt_5, \
            SUM(CASE WHEN admit_year - birth_year > 5 AND admit_year - birth_year <= 17 THEN 1 ELSE 0 END) AS num_5_17, \
            SUM(CASE WHEN admit_year - birth_year > 17 AND admit_year - birth_year <= 24 THEN 1 ELSE 0 END) AS num_18_24, \
            SUM(CASE WHEN admit_year - birth_year > 24 AND admit_year - birth_year <= 34 THEN 1 ELSE 0 END) AS num_25_34, \
            SUM(CASE WHEN admit_year - birth_year > 34 AND admit_year - birth_year <= 54 THEN 1 ELSE 0 END) AS num_35_54, \
            SUM(CASE WHEN admit_year - birth_year > 54 AND admit_year - birth_year <= 64 THEN 1 ELSE 0 END) AS num_55_64, \
            SUM(CASE WHEN admit_year - birth_year > 64 AND admit_year - birth_year <= 80 THEN 1 ELSE 0 END) AS num_65_80, \
            SUM(CASE WHEN admit_year - birth_year > 80 THEN 1 ELSE 0 END) AS num_gt_80 \
        FROM \
            ( \
            SELECT \
              p.pat_id AS patient_id, \
              CAST(EXTRACT(YEAR FROM dl.noted_date) AS INT) AS admit_year, \
              CASE WHEN p.gender = 'MALE' THEN 1 ELSE 0 END AS male, \
              CASE WHEN p.gender = 'FEMALE' THEN 1 ELSE 0 END AS female, \
              CASE WHEN p.race LIKE '%WHITE%' THEN 1 ELSE 0 END AS white, \
              CASE WHEN p.race LIKE '%ASIAN%' THEN 1 ELSE 0 END AS asian, \
              CASE WHEN p.race LIKE '% HISPANIC%' THEN 1 ELSE 0 END AS hispanic, \
              CASE WHEN p.race LIKE '%BLACK%' THEN 1 ELSE 0 END AS black, \
              CASE WHEN p.race LIKE '%PACIFIC ISLANDER%' THEN 1 ELSE 0 END AS pacific_islander, \
              CASE WHEN p.race LIKE '%OTHER%' THEN 1 ELSE 0 END AS other, \
              CASE WHEN p.race LIKE '%UNKNOWN%' THEN 1 ELSE 0 END AS unknown, \
              p.birth_year AS birth_year \
            FROM \
              stride_dx_list AS dl \
            JOIN \
              stride_patient AS p \
            ON \
              dl.pat_id = p.pat_id \
            WHERE \
              data_source = 'ADMIT_DX' \
            ) x \
        "

        # Execute query and return results.
        self.dbCursor.execute(query)
        demographics = list()
        for row in self.dbCursor:
            demographics.append(row)

        return demographics


    def _getAdmitDxPatientFrequencyRankByYear(self):
        # Get list of all clinical item IDs matching admit diagnosis.
        # Get this list in advance to make subsequent query run a bit faster.
        admitDxClinicalItemIds = self._getAdmitDxClinicalItemIds()

        # Build query for # of unique patients.
        # SELECT
        #   ci.name AS icd_code,
        #   ci.description AS admit_dx,
        #   EXTRACT(YEAR FROM pi.item_date) AS admit_year,
        #   COUNT(DISTINCT pi.patient_id) AS num_unique_patients,
        # FROM
        #   patient_item AS pi
        # JOIN
        #   clinical_item AS ci
        # ON
        #   pi.clinical_item_id = ci.clinical_item_id
        # WHERE
        #   ci.clinical_item_id in (admitDxClinicalItemIds)
        # GROUP BY
        #   icd_code,
        #   admit_dx,
        #   admit_year
        #   num_unique_patients
        # ORDER BY
        #   admit_year,
        #   num_unique_patients DESC
        query = SQLQuery()
        query.addSelect("ci.name AS icd_code")
        query.addSelect("ci.description AS admit_dx")
        query.addSelect("EXTRACT(YEAR FROM pi.item_date) AS admit_year")
        query.addSelect("COUNT(DISTINCT pi.patient_id) AS num_unique_patients")
        query.addFrom("patient_item AS pi")
        query.addJoin("clinical_item AS ci", "pi.clinical_item_id = ci.clinical_item_id")
        query.addWhereIn("ci.clinical_item_id", admitDxClinicalItemIds)
        query.addGroupBy("icd_code")
        query.addGroupBy("admit_dx")
        query.addGroupBy("admit_year")
        query.addGroupBy("num_unique_patients")
        query.addOrderBy("icd_code")
        query.addOrderBy("admit_year")
        query.addOrderBy("num_unique_patients DESC")

        # Execute query.
        results = DBUtil.execute(query)

    def _getAdmitDxClinicalItemIds(self):
        # Build query.
        # SELECT
        #   name AS icd_code,
        #   description AS admit_dx,
        #   clinical_item_id
        # FROM
        #   clinical_item
        # WHERE
        #   clinical_item_category = ADMIT_DX_CATEGORY_ID
        query = SQLQuery()
        query.addSelect("name AS icd_code")
        query.addSelect("description AS admit_dx")
        query.addSelect("clinical_item_id")
        query.addFrom("clinical_item")
        query.addWhereEqual("clinical_item_category_id", self.ADMIT_DX_CATEGORY_ID)

        # Fetch results (potentially from cache).
        results = self._executeCachedDBQuery(query)
        admitDxClinicalItemIds = [row[2] for row in results]

        return admitDxClinicalItemIds

    def _getNumPatients():
        ADMIT_DX_CATEGORY_ID = 2
        query = SQLQuery()
        query.addSelect()
        query.addFrom("patient_item")
        query = \
            """
            SELECT
            """
        print(query)

    def generateCharts():
        pass

    def writeReport():
        # STRIDEDescription.txt
        # Created: {createdDate}
        # The STRIDE data set provides de-identified EHR data for
        # {numUniquePatients} unique Stanford hospital patients across
        # {numUniqueEncounters} hospitalizations from {firstHospitalizationDate}
        # to {lastHospitalizationDate}.
        #
        # PATIENT DEMOGRAPHICS
        # Stanford hospital inpatient demographics have been relatively stable
        # over the time period covered by STRIDE, but deviate significantly from
        # the broader Palo Alto and US populations.
        #
        # Consider the breakdown by sex, age, and race.
        # Sex
        #   population    male (#)    male (%)    female (#)  female(%)   total
        #   Stanford ('09-'14)
        #
        # How do Stanford patient demographics vary from Palo Alto?
        # From the US?
        #
        # For month-by-month demographic breakdowns, please refer to the
        # following charts.
        # * List of charts showing month-by-month demographics.
        #
        # ADMIT DIAGNOSES
        # What are the most common admission diagnoses?
        # How has this changed over time?
        #
        # TREATMENT TEAMS
        #
        # PAYORS
        # Payor distribution
        # Physician tenure

        demographics = self._getPatientDemographics()
        numUniquePatients = demographics[0]


        pass

if __name__ == "__main__":
    d = STRIDEDescription()
