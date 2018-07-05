#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
from datetime import datetime;
import unittest

from Const import RUNNER_VERBOSITY;
from Util import log;

from medinfo.db.test.Util import DBTestCase;

# Temporary demonstration examples. Should consolidate this into stride data package, and relabel to derived cpoeStats or clinicalItem (and then cpoeSim) tables
from stride.core.StrideLoader import StrideLoader;
from scripts.CDSS.CDSSDataLoader import CDSSDataLoader; 


from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel;

from medinfo.dataconversion.STRIDEDemographicsConversion import STRIDEDemographicsConversion;

TEST_SOURCE_TABLE = "stride_patient";
TEMP_SOURCE_TABLE = "PreTest_patient";

class TestSTRIDEDemographicsConversion(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);
        
        log.info("Populate the database with test data")
        StrideLoader.build_stride_psql_schemata()
        CDSSDataLoader.build_CDSS_psql_schemata();

        # Relabel any existing data to not interfere with the new test data that will be produced
        DBUtil.execute("update clinical_item_category set source_table = '%s' where source_table = '%s';" % (TEMP_SOURCE_TABLE,TEST_SOURCE_TABLE) );
    
        dataTextStr = \
"""pat_id\tdeath_date\tbirth_year\tgender\trace\tethnicity
-100\tNone\t1958\tMALE\tAMERICAN INDIAN OR ALASKA NATIVE\tNON-HISPANIC/NON-LATINO
-200\tNone\t1992\tMALE\tAMERICAN INDIAN OR ALASKA NATIVE\tHISPANIC/LATINO
-300\tNone\t1993\tFEMALE\tASIAN\tNON-HISPANIC/NON-LATINO
-400\t2011-09-28\t1997\tFEMALE\tASIAN\tHISPANIC/LATINO
-500\tNone\t1952\tMALE\tASIAN\tPATIENT REFUSED
-600\tNone\t1984\tMALE\tASIAN\tUNKNOWN
-700\tNone\t1991\tFEMALE\tASIAN - HISTORICAL CONV\tNON-HISPANIC/NON-LATINO
-800\tNone\t1962\tMALE\tASIAN, HISPANIC\tUNKNOWN
-900\tNone\t1972\tMALE\tASIAN, HISPANIC\tHISPANIC/LATINO
-1000\tNone\t1970\tMALE\tASIAN, NON-HISPANIC\tNON-HISPANIC/NON-LATINO
-1100\tNone\t2001\tFEMALE\tASIAN, NON-HISPANIC\tUNKNOWN
-1200\tNone\t1969\tFEMALE\tBLACK OR AFRICAN AMERICAN\tNON-HISPANIC/NON-LATINO
-1300\tNone\t1945\tFEMALE\tBLACK OR AFRICAN AMERICAN\tHISPANIC/LATINO
-1400\tNone\t1945\tFEMALE\tBLACK OR AFRICAN AMERICAN\tUNKNOWN
-1500\t2012-05-02\t1956\tMALE\tBLACK OR AFRICAN AMERICAN\tPATIENT REFUSED
-1600\tNone\t1981\tFEMALE\tBLACK, HISPANIC\tHISPANIC/LATINO
-1700\tNone\t1985\tFEMALE\tBLACK, HISPANIC\tUNKNOWN
-1800\tNone\t1932\tMALE\tBLACK, NON-HISPANIC\tNON-HISPANIC/NON-LATINO
-1900\tNone\t1954\tMALE\tBLACK, NON-HISPANIC\tUNKNOWN
-2000\tNone\t1932\tMALE\tNATIVE AMERICAN, HISPANIC\tHISPANIC/LATINO
-2100\tNone\t1961\tFEMALE\tNATIVE AMERICAN, NON-HISPANIC\tUNKNOWN
-2200\tNone\t1974\tMALE\tNATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER \tNON-HISPANIC/NON-LATINO
-2300\tNone\t1953\tFEMALE\tNATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER \tHISPANIC/LATINO
-2400\tNone\t1943\tFEMALE\tNATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER \tUNKNOWN
-2500\tNone\t1963\tFEMALE\tOTHER\tHISPANIC/LATINO
-2600\tNone\t1974\tMALE\tOTHER\tNON-HISPANIC/NON-LATINO
-2700\tNone\t1963\tFEMALE\tOTHER\tPATIENT REFUSED
-2800\tNone\t2005\tFEMALE\tOTHER\tUNKNOWN
-2900\tNone\t1996\tMALE\tOTHER, HISPANIC\tUNKNOWN
-3000\tNone\t1952\tMALE\tOTHER, HISPANIC\tHISPANIC/LATINO
-3100\tNone\t1983\tFEMALE\tOTHER, HISPANIC\tNON-HISPANIC/NON-LATINO
-3200\tNone\t1971\tFEMALE\tOTHER, NON-HISPANIC\tNON-HISPANIC/NON-LATINO
-3300\tNone\t1976\tMALE\tOTHER, NON-HISPANIC\tUNKNOWN
-3400\tNone\t1995\tFEMALE\tOTHER, NON-HISPANIC\tHISPANIC/LATINO
-3500\tNone\t1982\tMALE\tPACIFIC ISLANDER, NON-HISPANIC\tNON-HISPANIC/NON-LATINO
-3600\tNone\t1940\tMALE\tPACIFIC ISLANDER, NON-HISPANIC\tUNKNOWN
-3700\tNone\t1934\tMALE\tPATIENT REFUSED\tPATIENT REFUSED
-3800\tNone\t1981\tFEMALE\tPATIENT REFUSED\tNON-HISPANIC/NON-LATINO
-3900\tNone\t1998\tMALE\tPATIENT REFUSED\tHISPANIC/LATINO
-4000\tNone\t1978\tMALE\tRACE AND ETHNICITY UNKNOWN\tUNKNOWN
-4100\tNone\t1933\tFEMALE\tRACE AND ETHNICITY UNKNOWN\tNON-HISPANIC/NON-LATINO
-4200\tNone\t1997\tFEMALE\tUNKNOWN\tUNKNOWN
-4300\tNone\t1932\tMALE\tUNKNOWN\tNON-HISPANIC/NON-LATINO
-4400\t2012-11-13\t1947\tFEMALE\tUNKNOWN\tHISPANIC/LATINO
-4500\tNone\t1932\tMALE\tUNKNOWN\tPATIENT REFUSED
-4600\tNone\t1936\tMALE\tUNKNOWN\t
-4700\tNone\t1993\tFEMALE\tWHITE\tNON-HISPANIC/NON-LATINO
-4800\tNone\t1948\tMALE\tWHITE\tHISPANIC/LATINO
-4900\tNone\t1968\tMALE\tWHITE\tUNKNOWN
-5000\tNone\t2003\tFEMALE\tWHITE\tPATIENT REFUSED
-5100\tNone\t1970\tMALE\tWHITE\t
-5200\tNone\t1998\tMALE\tWHITE, HISPANIC\tHISPANIC/LATINO
-5300\tNone\t1986\tMALE\tWHITE, HISPANIC\tUNKNOWN
-5400\tNone\t1997\tFEMALE\tWHITE, HISPANIC\tNON-HISPANIC/NON-LATINO
-5500\tNone\t1964\tMALE\tWHITE, NON-HISPANIC\tNON-HISPANIC/NON-LATINO
-5600\tNone\t1940\tMALE\tWHITE, NON-HISPANIC\tUNKNOWN
-5700\tNone\t1962\tMALE\tWHITE, NON-HISPANIC\tHISPANIC/LATINO
-5800\tNone\t1931\tFEMALE\tNone\tNone
-5900\tNone\t1991\tFEMALE\tNone\tNON-HISPANIC/NON-LATINO
-6000\tNone\t1973\tFEMALE\tNone\tUNKNOWN
-6050\tNone\tNone\tNone\tNone\tNone
-6100\tNone\t1953\tFEMALE\tNone\tHISPANIC/LATINO
"""
        self.patientIds = ["-100","-200","-300","-400","-500","-600","-700","-800","-900","-1000","-1100","-1200","-1300","-1400","-1500","-1600","-1700","-1800","-1900","-2000","-2100","-2200","-2300","-2400","-2500","-2600","-2700","-2800","-2900","-3000","-3100","-3200","-3300","-3400","-3500","-3600","-3700","-3800","-3900","-4000","-4100","-4200","-4300","-4400","-4500","-4600","-4700","-4800","-4900","-5000","-5100","-5200","-5300","-5400","-5500","-5600","-5700","-5800","-5900","-6000","-6050","-6100"];

        # Parse into DB insertion object
        DBUtil.insertFile( StringIO(dataTextStr), "stride_patient", delim="\t", dateColFormats={"death_date": None} );

        self.converter = STRIDEDemographicsConversion();  # Instance to test on

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")

        DBUtil.execute \
        (   """delete from patient_item 
            where clinical_item_id in 
            (   select clinical_item_id
                from clinical_item as ci, clinical_item_category as cic
                where ci.clinical_item_category_id = cic.clinical_item_category_id
                and cic.source_table = '%s'
            );
            """ % TEST_SOURCE_TABLE
        );
        DBUtil.execute \
        (   """delete from clinical_item 
            where clinical_item_category_id in 
            (   select clinical_item_category_id 
                from clinical_item_category 
                where source_table = '%s'
            );
            """ % TEST_SOURCE_TABLE
        );
        DBUtil.execute("delete from clinical_item_category where source_table = '%s';" % TEST_SOURCE_TABLE);
        DBUtil.execute("update clinical_item_category set source_table = '%s' where source_table = '%s';" % (TEST_SOURCE_TABLE,TEMP_SOURCE_TABLE) ); # Reset labels of any prior data

        query = SQLQuery();
        query.delete = True;
        query.addFrom("stride_patient");
        query.addWhere("pat_id < 0");
        DBUtil.execute( query );

        DBTestCase.tearDown(self);

    def test_dataConversion(self):
        # Run the data conversion on the same data and look for expected records
        log.debug("Run the conversion process...");
        self.converter.convertSourceItems(self.patientIds);

        # Just query back for the same data, de-normalizing the data back to a general table
        testQuery = \
            """
            select 
                pi.external_id,
                pi.patient_id,
                pi.encounter_id,
                cic.description,
                ci.external_id,
                ci.name,
                ci.description,
                pi.item_date
            from
                patient_item as pi,
                clinical_item as ci,
                clinical_item_category as cic
            where
                pi.clinical_item_id = ci.clinical_item_id and
                ci.clinical_item_category_id = cic.clinical_item_category_id and
                cic.source_table = '%s'
            order by
                pi.patient_id desc, ci.name
            """ % TEST_SOURCE_TABLE;
        expectedData = \
            [
                [None, -100, None, 'Demographics', None, 'Birth','Birth Year', datetime(1958, 1, 1)],
                [None, -100, None, 'Demographics', None, 'Birth1950s','Birth Decade 1950s', datetime(1958, 1, 1)],
                [None, -100, None, 'Demographics', None, 'Male','Male Gender', datetime(1958, 1, 1)],
                [None, -100, None, 'Demographics', None, 'RaceNativeAmerican','Race/Ethnicity: Native American', datetime(1958, 1, 1)],


                [None, -200, None, 'Demographics', None, 'Birth','Birth Year', datetime(1992, 1, 1)],
                [None, -200, None, 'Demographics', None, 'Birth1990s','Birth Decade 1990s', datetime(1992, 1, 1)],
                [None, -200, None, 'Demographics', None, 'Male','Male Gender', datetime(1992, 1, 1)],
                [None, -200, None, 'Demographics', None, 'RaceNativeAmerican','Race/Ethnicity: Native American', datetime(1992, 1, 1)],


                [None, -300, None, 'Demographics', None, 'Birth','Birth Year', datetime(1993, 1, 1)],
                [None, -300, None, 'Demographics', None, 'Birth1990s','Birth Decade 1990s', datetime(1993, 1, 1)],
                [None, -300, None, 'Demographics', None, 'Female','Female Gender', datetime(1993, 1, 1)],
                [None, -300, None, 'Demographics', None, 'RaceAsian','Race/Ethnicity: Asian', datetime(1993, 1, 1)],


                [None, -400, None, 'Demographics', None, 'Birth','Birth Year', datetime(1997, 1, 1)],
                [None, -400, None, 'Demographics', None, 'Birth1990s','Birth Decade 1990s', datetime(1997, 1, 1)],
                [None, -400, None, 'Demographics', None, 'Death','Death Date', datetime(2011, 9,28)],
                [None, -400, None, 'Demographics', None, 'Female','Female Gender', datetime(1997, 1, 1)],
                [None, -400, None, 'Demographics', None, 'RaceAsian','Race/Ethnicity: Asian', datetime(1997, 1, 1)],


                [None, -500, None, 'Demographics', None, 'Birth','Birth Year', datetime(1952, 1, 1)],
                [None, -500, None, 'Demographics', None, 'Birth1950s','Birth Decade 1950s', datetime(1952, 1, 1)],
                [None, -500, None, 'Demographics', None, 'Male','Male Gender', datetime(1952, 1, 1)],
                [None, -500, None, 'Demographics', None, 'RaceAsian','Race/Ethnicity: Asian', datetime(1952, 1, 1)],


                [None, -600, None, 'Demographics', None, 'Birth','Birth Year', datetime(1984, 1, 1)],
                [None, -600, None, 'Demographics', None, 'Birth1980s','Birth Decade 1980s', datetime(1984, 1, 1)],
                [None, -600, None, 'Demographics', None, 'Male','Male Gender', datetime(1984, 1, 1)],
                [None, -600, None, 'Demographics', None, 'RaceAsian','Race/Ethnicity: Asian', datetime(1984, 1, 1)],


                [None, -700, None, 'Demographics', None, 'Birth','Birth Year', datetime(1991, 1, 1)],
                [None, -700, None, 'Demographics', None, 'Birth1990s','Birth Decade 1990s', datetime(1991, 1, 1)],
                [None, -700, None, 'Demographics', None, 'Female','Female Gender', datetime(1991, 1, 1)],
                [None, -700, None, 'Demographics', None, 'RaceAsian','Race/Ethnicity: Asian', datetime(1991, 1, 1)],


                [None, -800, None, 'Demographics', None, 'Birth','Birth Year', datetime(1962, 1, 1)],
                [None, -800, None, 'Demographics', None, 'Birth1960s','Birth Decade 1960s', datetime(1962, 1, 1)],
                [None, -800, None, 'Demographics', None, 'Male','Male Gender', datetime(1962, 1, 1)],
                [None, -800, None, 'Demographics', None, 'RaceAsian','Race/Ethnicity: Asian', datetime(1962, 1, 1)],


                [None, -900, None, 'Demographics', None, 'Birth','Birth Year', datetime(1972, 1, 1)],
                [None, -900, None, 'Demographics', None, 'Birth1970s','Birth Decade 1970s', datetime(1972, 1, 1)],
                [None, -900, None, 'Demographics', None, 'Male','Male Gender', datetime(1972, 1, 1)],
                [None, -900, None, 'Demographics', None, 'RaceAsian','Race/Ethnicity: Asian', datetime(1972, 1, 1)],


                [None, -1000, None, 'Demographics', None, 'Birth','Birth Year', datetime(1970, 1, 1)],
                [None, -1000, None, 'Demographics', None, 'Birth1970s','Birth Decade 1970s', datetime(1970, 1, 1)],
                [None, -1000, None, 'Demographics', None, 'Male','Male Gender', datetime(1970, 1, 1)],
                [None, -1000, None, 'Demographics', None, 'RaceAsian','Race/Ethnicity: Asian', datetime(1970, 1, 1)],


                [None, -1100, None, 'Demographics', None, 'Birth','Birth Year', datetime(2001, 1, 1)],
                [None, -1100, None, 'Demographics', None, 'Birth2000s','Birth Decade 2000s', datetime(2001, 1, 1)],
                [None, -1100, None, 'Demographics', None, 'Female','Female Gender', datetime(2001, 1, 1)],
                [None, -1100, None, 'Demographics', None, 'RaceAsian','Race/Ethnicity: Asian', datetime(2001, 1, 1)],


                [None, -1200, None, 'Demographics', None, 'Birth','Birth Year', datetime(1969, 1, 1)],
                [None, -1200, None, 'Demographics', None, 'Birth1960s','Birth Decade 1960s', datetime(1969, 1, 1)],
                [None, -1200, None, 'Demographics', None, 'Female','Female Gender', datetime(1969, 1, 1)],
                [None, -1200, None, 'Demographics', None, 'RaceBlack','Race/Ethnicity: Black', datetime(1969, 1, 1)],


                [None, -1300, None, 'Demographics', None, 'Birth','Birth Year', datetime(1945, 1, 1)],
                [None, -1300, None, 'Demographics', None, 'Birth1940s','Birth Decade 1940s', datetime(1945, 1, 1)],
                [None, -1300, None, 'Demographics', None, 'Female','Female Gender', datetime(1945, 1, 1)],
                [None, -1300, None, 'Demographics', None, 'RaceBlack','Race/Ethnicity: Black', datetime(1945, 1, 1)],


                [None, -1400, None, 'Demographics', None, 'Birth','Birth Year', datetime(1945, 1, 1)],
                [None, -1400, None, 'Demographics', None, 'Birth1940s','Birth Decade 1940s', datetime(1945, 1, 1)],
                [None, -1400, None, 'Demographics', None, 'Female','Female Gender', datetime(1945, 1, 1)],
                [None, -1400, None, 'Demographics', None, 'RaceBlack','Race/Ethnicity: Black', datetime(1945, 1, 1)],


                [None, -1500, None, 'Demographics', None, 'Birth','Birth Year', datetime(1956, 1, 1)],
                [None, -1500, None, 'Demographics', None, 'Birth1950s','Birth Decade 1950s', datetime(1956, 1, 1)],
                [None, -1500, None, 'Demographics', None, 'Death','Death Date', datetime(2012, 5, 2)],
                [None, -1500, None, 'Demographics', None, 'Male','Male Gender', datetime(1956, 1, 1)],
                [None, -1500, None, 'Demographics', None, 'RaceBlack','Race/Ethnicity: Black', datetime(1956, 1, 1)],


                [None, -1600, None, 'Demographics', None, 'Birth','Birth Year', datetime(1981, 1, 1)],
                [None, -1600, None, 'Demographics', None, 'Birth1980s','Birth Decade 1980s', datetime(1981, 1, 1)],
                [None, -1600, None, 'Demographics', None, 'Female','Female Gender', datetime(1981, 1, 1)],
                [None, -1600, None, 'Demographics', None, 'RaceBlack','Race/Ethnicity: Black', datetime(1981, 1, 1)],


                [None, -1700, None, 'Demographics', None, 'Birth','Birth Year', datetime(1985, 1, 1)],
                [None, -1700, None, 'Demographics', None, 'Birth1980s','Birth Decade 1980s', datetime(1985, 1, 1)],
                [None, -1700, None, 'Demographics', None, 'Female','Female Gender', datetime(1985, 1, 1)],
                [None, -1700, None, 'Demographics', None, 'RaceBlack','Race/Ethnicity: Black', datetime(1985, 1, 1)],


                [None, -1800, None, 'Demographics', None, 'Birth','Birth Year', datetime(1932, 1, 1)],
                [None, -1800, None, 'Demographics', None, 'Birth1930s','Birth Decade 1930s', datetime(1932, 1, 1)],
                [None, -1800, None, 'Demographics', None, 'Male','Male Gender', datetime(1932, 1, 1)],
                [None, -1800, None, 'Demographics', None, 'RaceBlack','Race/Ethnicity: Black', datetime(1932, 1, 1)],


                [None, -1900, None, 'Demographics', None, 'Birth','Birth Year', datetime(1954, 1, 1)],
                [None, -1900, None, 'Demographics', None, 'Birth1950s','Birth Decade 1950s', datetime(1954, 1, 1)],
                [None, -1900, None, 'Demographics', None, 'Male','Male Gender', datetime(1954, 1, 1)],
                [None, -1900, None, 'Demographics', None, 'RaceBlack','Race/Ethnicity: Black', datetime(1954, 1, 1)],


                [None, -2000, None, 'Demographics', None, 'Birth','Birth Year', datetime(1932, 1, 1)],
                [None, -2000, None, 'Demographics', None, 'Birth1930s','Birth Decade 1930s', datetime(1932, 1, 1)],
                [None, -2000, None, 'Demographics', None, 'Male','Male Gender', datetime(1932, 1, 1)],
                [None, -2000, None, 'Demographics', None, 'RaceNativeAmerican','Race/Ethnicity: Native American', datetime(1932, 1, 1)],


                [None, -2100, None, 'Demographics', None, 'Birth','Birth Year', datetime(1961, 1, 1)],
                [None, -2100, None, 'Demographics', None, 'Birth1960s','Birth Decade 1960s', datetime(1961, 1, 1)],
                [None, -2100, None, 'Demographics', None, 'Female','Female Gender', datetime(1961, 1, 1)],
                [None, -2100, None, 'Demographics', None, 'RaceNativeAmerican','Race/Ethnicity: Native American', datetime(1961, 1, 1)],


                [None, -2200, None, 'Demographics', None, 'Birth','Birth Year', datetime(1974, 1, 1)],
                [None, -2200, None, 'Demographics', None, 'Birth1970s','Birth Decade 1970s', datetime(1974, 1, 1)],
                [None, -2200, None, 'Demographics', None, 'Male','Male Gender', datetime(1974, 1, 1)],
                [None, -2200, None, 'Demographics', None, 'RacePacificIslander','Race/Ethnicity: Pacific Islander', datetime(1974, 1, 1)],


                [None, -2300, None, 'Demographics', None, 'Birth','Birth Year', datetime(1953, 1, 1)],
                [None, -2300, None, 'Demographics', None, 'Birth1950s','Birth Decade 1950s', datetime(1953, 1, 1)],
                [None, -2300, None, 'Demographics', None, 'Female','Female Gender', datetime(1953, 1, 1)],
                [None, -2300, None, 'Demographics', None, 'RacePacificIslander','Race/Ethnicity: Pacific Islander', datetime(1953, 1, 1)],


                [None, -2400, None, 'Demographics', None, 'Birth','Birth Year', datetime(1943, 1, 1)],
                [None, -2400, None, 'Demographics', None, 'Birth1940s','Birth Decade 1940s', datetime(1943, 1, 1)],
                [None, -2400, None, 'Demographics', None, 'Female','Female Gender', datetime(1943, 1, 1)],
                [None, -2400, None, 'Demographics', None, 'RacePacificIslander','Race/Ethnicity: Pacific Islander', datetime(1943, 1, 1)],


                [None, -2500, None, 'Demographics', None, 'Birth','Birth Year', datetime(1963, 1, 1)],
                [None, -2500, None, 'Demographics', None, 'Birth1960s','Birth Decade 1960s', datetime(1963, 1, 1)],
                [None, -2500, None, 'Demographics', None, 'Female','Female Gender', datetime(1963, 1, 1)],
                [None, -2500, None, 'Demographics', None, 'RaceHispanicLatino','Race/Ethnicity: Hispanic/Latino', datetime(1963, 1, 1)],


                [None, -2600, None, 'Demographics', None, 'Birth','Birth Year', datetime(1974, 1, 1)],
                [None, -2600, None, 'Demographics', None, 'Birth1970s','Birth Decade 1970s', datetime(1974, 1, 1)],
                [None, -2600, None, 'Demographics', None, 'Male','Male Gender', datetime(1974, 1, 1)],
                [None, -2600, None, 'Demographics', None, 'RaceOther','Race/Ethnicity: Other', datetime(1974, 1, 1)],


                [None, -2700, None, 'Demographics', None, 'Birth','Birth Year', datetime(1963, 1, 1)],
                [None, -2700, None, 'Demographics', None, 'Birth1960s','Birth Decade 1960s', datetime(1963, 1, 1)],
                [None, -2700, None, 'Demographics', None, 'Female','Female Gender', datetime(1963, 1, 1)],
                [None, -2700, None, 'Demographics', None, 'RaceOther','Race/Ethnicity: Other', datetime(1963, 1, 1)],


                [None, -2800, None, 'Demographics', None, 'Birth','Birth Year', datetime(2005, 1, 1)],
                [None, -2800, None, 'Demographics', None, 'Birth2000s','Birth Decade 2000s', datetime(2005, 1, 1)],
                [None, -2800, None, 'Demographics', None, 'Female','Female Gender', datetime(2005, 1, 1)],
                [None, -2800, None, 'Demographics', None, 'RaceOther','Race/Ethnicity: Other', datetime(2005, 1, 1)],


                [None, -2900, None, 'Demographics', None, 'Birth','Birth Year', datetime(1996, 1, 1)],
                [None, -2900, None, 'Demographics', None, 'Birth1990s','Birth Decade 1990s', datetime(1996, 1, 1)],
                [None, -2900, None, 'Demographics', None, 'Male','Male Gender', datetime(1996, 1, 1)],
                [None, -2900, None, 'Demographics', None, 'RaceHispanicLatino','Race/Ethnicity: Hispanic/Latino', datetime(1996, 1, 1)],


                [None, -3000, None, 'Demographics', None, 'Birth','Birth Year', datetime(1952, 1, 1)],
                [None, -3000, None, 'Demographics', None, 'Birth1950s','Birth Decade 1950s', datetime(1952, 1, 1)],
                [None, -3000, None, 'Demographics', None, 'Male','Male Gender', datetime(1952, 1, 1)],
                [None, -3000, None, 'Demographics', None, 'RaceHispanicLatino','Race/Ethnicity: Hispanic/Latino', datetime(1952, 1, 1)],


                [None, -3100, None, 'Demographics', None, 'Birth','Birth Year', datetime(1983, 1, 1)],
                [None, -3100, None, 'Demographics', None, 'Birth1980s','Birth Decade 1980s', datetime(1983, 1, 1)],
                [None, -3100, None, 'Demographics', None, 'Female','Female Gender', datetime(1983, 1, 1)],
                [None, -3100, None, 'Demographics', None, 'RaceHispanicLatino','Race/Ethnicity: Hispanic/Latino', datetime(1983, 1, 1)],


                [None, -3200, None, 'Demographics', None, 'Birth','Birth Year', datetime(1971, 1, 1)],
                [None, -3200, None, 'Demographics', None, 'Birth1970s','Birth Decade 1970s', datetime(1971, 1, 1)],
                [None, -3200, None, 'Demographics', None, 'Female','Female Gender', datetime(1971, 1, 1)],
                [None, -3200, None, 'Demographics', None, 'RaceOther','Race/Ethnicity: Other', datetime(1971, 1, 1)],


                [None, -3300, None, 'Demographics', None, 'Birth','Birth Year', datetime(1976, 1, 1)],
                [None, -3300, None, 'Demographics', None, 'Birth1970s','Birth Decade 1970s', datetime(1976, 1, 1)],
                [None, -3300, None, 'Demographics', None, 'Male','Male Gender', datetime(1976, 1, 1)],
                [None, -3300, None, 'Demographics', None, 'RaceOther','Race/Ethnicity: Other', datetime(1976, 1, 1)],


                [None, -3400, None, 'Demographics', None, 'Birth','Birth Year', datetime(1995, 1, 1)],
                [None, -3400, None, 'Demographics', None, 'Birth1990s','Birth Decade 1990s', datetime(1995, 1, 1)],
                [None, -3400, None, 'Demographics', None, 'Female','Female Gender', datetime(1995, 1, 1)],
                [None, -3400, None, 'Demographics', None, 'RaceHispanicLatino','Race/Ethnicity: Hispanic/Latino', datetime(1995, 1, 1)],


                [None, -3500, None, 'Demographics', None, 'Birth','Birth Year', datetime(1982, 1, 1)],
                [None, -3500, None, 'Demographics', None, 'Birth1980s','Birth Decade 1980s', datetime(1982, 1, 1)],
                [None, -3500, None, 'Demographics', None, 'Male','Male Gender', datetime(1982, 1, 1)],
                [None, -3500, None, 'Demographics', None, 'RacePacificIslander','Race/Ethnicity: Pacific Islander', datetime(1982, 1, 1)],


                [None, -3600, None, 'Demographics', None, 'Birth','Birth Year', datetime(1940, 1, 1)],
                [None, -3600, None, 'Demographics', None, 'Birth1940s','Birth Decade 1940s', datetime(1940, 1, 1)],
                [None, -3600, None, 'Demographics', None, 'Male','Male Gender', datetime(1940, 1, 1)],
                [None, -3600, None, 'Demographics', None, 'RacePacificIslander','Race/Ethnicity: Pacific Islander', datetime(1940, 1, 1)],


                [None, -3700, None, 'Demographics', None, 'Birth','Birth Year', datetime(1934, 1, 1)],
                [None, -3700, None, 'Demographics', None, 'Birth1930s','Birth Decade 1930s', datetime(1934, 1, 1)],
                [None, -3700, None, 'Demographics', None, 'Male','Male Gender', datetime(1934, 1, 1)],
                [None, -3700, None, 'Demographics', None, 'RaceUnknown','Race/Ethnicity: Unknown', datetime(1934, 1, 1)],


                [None, -3800, None, 'Demographics', None, 'Birth','Birth Year', datetime(1981, 1, 1)],
                [None, -3800, None, 'Demographics', None, 'Birth1980s','Birth Decade 1980s', datetime(1981, 1, 1)],
                [None, -3800, None, 'Demographics', None, 'Female','Female Gender', datetime(1981, 1, 1)],
                [None, -3800, None, 'Demographics', None, 'RaceUnknown','Race/Ethnicity: Unknown', datetime(1981, 1, 1)],


                [None, -3900, None, 'Demographics', None, 'Birth','Birth Year', datetime(1998, 1, 1)],
                [None, -3900, None, 'Demographics', None, 'Birth1990s','Birth Decade 1990s', datetime(1998, 1, 1)],
                [None, -3900, None, 'Demographics', None, 'Male','Male Gender', datetime(1998, 1, 1)],
                [None, -3900, None, 'Demographics', None, 'RaceHispanicLatino','Race/Ethnicity: Hispanic/Latino', datetime(1998, 1, 1)],


                [None, -4000, None, 'Demographics', None, 'Birth','Birth Year', datetime(1978, 1, 1)],
                [None, -4000, None, 'Demographics', None, 'Birth1970s','Birth Decade 1970s', datetime(1978, 1, 1)],
                [None, -4000, None, 'Demographics', None, 'Male','Male Gender', datetime(1978, 1, 1)],
                [None, -4000, None, 'Demographics', None, 'RaceUnknown','Race/Ethnicity: Unknown', datetime(1978, 1, 1)],


                [None, -4100, None, 'Demographics', None, 'Birth','Birth Year', datetime(1933, 1, 1)],
                [None, -4100, None, 'Demographics', None, 'Birth1930s','Birth Decade 1930s', datetime(1933, 1, 1)],
                [None, -4100, None, 'Demographics', None, 'Female','Female Gender', datetime(1933, 1, 1)],
                [None, -4100, None, 'Demographics', None, 'RaceUnknown','Race/Ethnicity: Unknown', datetime(1933, 1, 1)],


                [None, -4200, None, 'Demographics', None, 'Birth','Birth Year', datetime(1997, 1, 1)],
                [None, -4200, None, 'Demographics', None, 'Birth1990s','Birth Decade 1990s', datetime(1997, 1, 1)],
                [None, -4200, None, 'Demographics', None, 'Female','Female Gender', datetime(1997, 1, 1)],
                [None, -4200, None, 'Demographics', None, 'RaceUnknown','Race/Ethnicity: Unknown', datetime(1997, 1, 1)],


                [None, -4300, None, 'Demographics', None, 'Birth','Birth Year', datetime(1932, 1, 1)],
                [None, -4300, None, 'Demographics', None, 'Birth1930s','Birth Decade 1930s', datetime(1932, 1, 1)],
                [None, -4300, None, 'Demographics', None, 'Male','Male Gender', datetime(1932, 1, 1)],
                [None, -4300, None, 'Demographics', None, 'RaceUnknown','Race/Ethnicity: Unknown', datetime(1932, 1, 1)],


                [None, -4400, None, 'Demographics', None, 'Birth','Birth Year', datetime(1947, 1, 1)],
                [None, -4400, None, 'Demographics', None, 'Birth1940s','Birth Decade 1940s', datetime(1947, 1, 1)],
                [None, -4400, None, 'Demographics', None, 'Death','Death Date', datetime(2012,11,13)],
                [None, -4400, None, 'Demographics', None, 'Female','Female Gender', datetime(1947, 1, 1)],
                [None, -4400, None, 'Demographics', None, 'RaceHispanicLatino','Race/Ethnicity: Hispanic/Latino', datetime(1947, 1, 1)],


                [None, -4500, None, 'Demographics', None, 'Birth','Birth Year', datetime(1932, 1, 1)],
                [None, -4500, None, 'Demographics', None, 'Birth1930s','Birth Decade 1930s', datetime(1932, 1, 1)],
                [None, -4500, None, 'Demographics', None, 'Male','Male Gender', datetime(1932, 1, 1)],
                [None, -4500, None, 'Demographics', None, 'RaceUnknown','Race/Ethnicity: Unknown', datetime(1932, 1, 1)],


                [None, -4600, None, 'Demographics', None, 'Birth','Birth Year', datetime(1936, 1, 1)],
                [None, -4600, None, 'Demographics', None, 'Birth1930s','Birth Decade 1930s', datetime(1936, 1, 1)],
                [None, -4600, None, 'Demographics', None, 'Male','Male Gender', datetime(1936, 1, 1)],
                [None, -4600, None, 'Demographics', None, 'RaceUnknown','Race/Ethnicity: Unknown', datetime(1936, 1, 1)],


                [None, -4700, None, 'Demographics', None, 'Birth','Birth Year', datetime(1993, 1, 1)],
                [None, -4700, None, 'Demographics', None, 'Birth1990s','Birth Decade 1990s', datetime(1993, 1, 1)],
                [None, -4700, None, 'Demographics', None, 'Female','Female Gender', datetime(1993, 1, 1)],
                [None, -4700, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino','Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1993, 1, 1)],


                [None, -4800, None, 'Demographics', None, 'Birth','Birth Year', datetime(1948, 1, 1)],
                [None, -4800, None, 'Demographics', None, 'Birth1940s','Birth Decade 1940s', datetime(1948, 1, 1)],
                [None, -4800, None, 'Demographics', None, 'Male','Male Gender', datetime(1948, 1, 1)],
                [None, -4800, None, 'Demographics', None, 'RaceWhiteHispanicLatino','Race/Ethnicity: White (Hispanic/Latino)', datetime(1948, 1, 1)],


                [None, -4900, None, 'Demographics', None, 'Birth','Birth Year', datetime(1968, 1, 1)],
                [None, -4900, None, 'Demographics', None, 'Birth1960s','Birth Decade 1960s', datetime(1968, 1, 1)],
                [None, -4900, None, 'Demographics', None, 'Male','Male Gender', datetime(1968, 1, 1)],
                [None, -4900, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino','Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1968, 1, 1)],


                [None, -5000, None, 'Demographics', None, 'Birth','Birth Year', datetime(2003, 1, 1)],
                [None, -5000, None, 'Demographics', None, 'Birth2000s','Birth Decade 2000s', datetime(2003, 1, 1)],
                [None, -5000, None, 'Demographics', None, 'Female','Female Gender', datetime(2003, 1, 1)],
                [None, -5000, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino','Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(2003, 1, 1)],


                [None, -5100, None, 'Demographics', None, 'Birth','Birth Year', datetime(1970, 1, 1)],
                [None, -5100, None, 'Demographics', None, 'Birth1970s','Birth Decade 1970s', datetime(1970, 1, 1)],
                [None, -5100, None, 'Demographics', None, 'Male','Male Gender', datetime(1970, 1, 1)],
                [None, -5100, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino','Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1970, 1, 1)],


                [None, -5200, None, 'Demographics', None, 'Birth','Birth Year', datetime(1998, 1, 1)],
                [None, -5200, None, 'Demographics', None, 'Birth1990s','Birth Decade 1990s', datetime(1998, 1, 1)],
                [None, -5200, None, 'Demographics', None, 'Male','Male Gender', datetime(1998, 1, 1)],
                [None, -5200, None, 'Demographics', None, 'RaceWhiteHispanicLatino','Race/Ethnicity: White (Hispanic/Latino)', datetime(1998, 1, 1)],


                [None, -5300, None, 'Demographics', None, 'Birth','Birth Year', datetime(1986, 1, 1)],
                [None, -5300, None, 'Demographics', None, 'Birth1980s','Birth Decade 1980s', datetime(1986, 1, 1)],
                [None, -5300, None, 'Demographics', None, 'Male','Male Gender', datetime(1986, 1, 1)],
                [None, -5300, None, 'Demographics', None, 'RaceWhiteHispanicLatino','Race/Ethnicity: White (Hispanic/Latino)', datetime(1986, 1, 1)],


                [None, -5400, None, 'Demographics', None, 'Birth','Birth Year', datetime(1997, 1, 1)],
                [None, -5400, None, 'Demographics', None, 'Birth1990s','Birth Decade 1990s', datetime(1997, 1, 1)],
                [None, -5400, None, 'Demographics', None, 'Female','Female Gender', datetime(1997, 1, 1)],
                [None, -5400, None, 'Demographics', None, 'RaceWhiteHispanicLatino','Race/Ethnicity: White (Hispanic/Latino)', datetime(1997, 1, 1)],


                [None, -5500, None, 'Demographics', None, 'Birth','Birth Year', datetime(1964, 1, 1)],
                [None, -5500, None, 'Demographics', None, 'Birth1960s','Birth Decade 1960s', datetime(1964, 1, 1)],
                [None, -5500, None, 'Demographics', None, 'Male','Male Gender', datetime(1964, 1, 1)],
                [None, -5500, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino','Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1964, 1, 1)],


                [None, -5600, None, 'Demographics', None, 'Birth','Birth Year', datetime(1940, 1, 1)],
                [None, -5600, None, 'Demographics', None, 'Birth1940s','Birth Decade 1940s', datetime(1940, 1, 1)],
                [None, -5600, None, 'Demographics', None, 'Male','Male Gender', datetime(1940, 1, 1)],
                [None, -5600, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino','Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1940, 1, 1)],


                [None, -5700, None, 'Demographics', None, 'Birth','Birth Year', datetime(1962, 1, 1)],
                [None, -5700, None, 'Demographics', None, 'Birth1960s','Birth Decade 1960s', datetime(1962, 1, 1)],
                [None, -5700, None, 'Demographics', None, 'Male','Male Gender', datetime(1962, 1, 1)],
                [None, -5700, None, 'Demographics', None, 'RaceWhiteNonHispanicLatino','Race/Ethnicity: White (Non-Hispanic/Latino)', datetime(1962, 1, 1)],


                [None, -5800, None, 'Demographics', None, 'Birth','Birth Year', datetime(1931, 1, 1)],
                [None, -5800, None, 'Demographics', None, 'Birth1930s','Birth Decade 1930s', datetime(1931, 1, 1)],
                [None, -5800, None, 'Demographics', None, 'Female','Female Gender', datetime(1931, 1, 1)],
                [None, -5800, None, 'Demographics', None, 'RaceUnknown','Race/Ethnicity: Unknown', datetime(1931, 1, 1)],


                [None, -5900, None, 'Demographics', None, 'Birth','Birth Year', datetime(1991, 1, 1)],
                [None, -5900, None, 'Demographics', None, 'Birth1990s','Birth Decade 1990s', datetime(1991, 1, 1)],
                [None, -5900, None, 'Demographics', None, 'Female','Female Gender', datetime(1991, 1, 1)],
                [None, -5900, None, 'Demographics', None, 'RaceUnknown','Race/Ethnicity: Unknown', datetime(1991, 1, 1)],


                [None, -6000, None, 'Demographics', None, 'Birth','Birth Year', datetime(1973, 1, 1)],
                [None, -6000, None, 'Demographics', None, 'Birth1970s','Birth Decade 1970s', datetime(1973, 1, 1)],
                [None, -6000, None, 'Demographics', None, 'Female','Female Gender', datetime(1973, 1, 1)],
                [None, -6000, None, 'Demographics', None, 'RaceUnknown','Race/Ethnicity: Unknown', datetime(1973, 1, 1)],


                [None, -6100, None, 'Demographics', None, 'Birth','Birth Year', datetime(1953, 1, 1)],
                [None, -6100, None, 'Demographics', None, 'Birth1950s','Birth Decade 1950s', datetime(1953, 1, 1)],
                [None, -6100, None, 'Demographics', None, 'Female','Female Gender', datetime(1953, 1, 1)],
                [None, -6100, None, 'Demographics', None, 'RaceHispanicLatino','Race/Ethnicity: Hispanic/Latino', datetime(1953, 1, 1)],


            ];
        actualData = DBUtil.execute(testQuery);
        self.assertEqualTable( expectedData, actualData );


def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestSTRIDEDemographicsConversion("test_incColNamesAndTypeCodes"));
    #suite.addTest(TestSTRIDEDemographicsConversion("test_insertFile_skipErrors"));
    #suite.addTest(TestSTRIDEDemographicsConversion('test_executeIterator'));
    #suite.addTest(TestSTRIDEDemographicsConversion('test_findOrInsertItem'));
    suite.addTest(unittest.makeSuite(TestSTRIDEDemographicsConversion));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
