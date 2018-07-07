#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
from datetime import datetime;
import unittest

from Const import RUNNER_VERBOSITY;
from Util import log;

from medinfo.db.test.Util import DBTestCase;
from stride.core.StrideLoader import StrideLoader;
from stride.clinical_item.ClinicalItemDataLoader import ClinicalItemDataLoader; 

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel;

from medinfo.dataconversion.STRIDEPreAdmitMedConversion import STRIDEPreAdmitMedConversion, ConversionOptions;

TEST_START_DATE = datetime(2100,1,1);   # Date in far future to start checking for test records to avoid including existing data in database

class TestSTRIDEPreAdmitMedConversion(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);
        
        log.info("Populate the database with test data")
        StrideLoader.build_stride_psql_schemata()
        ClinicalItemDataLoader.build_clinical_item_psql_schemata();
        
        headers = ["stride_preadmit_med_id","pat_anon_id","contact_date","medication_id","description","thera_class","pharm_class","pharm_subclass"];
        dataModels = \
            [   # Deliberately design dates in far future to facilitate isolated testing
                RowItemModel([-100, -1000, datetime(2113, 7, 6),  -5680, "NORVASC 5 MG PO TABS", "CARDIAC DRUGS", "CALCIUM CHANNEL BLOCKING AGENTS", "Calcium Channel Blockers - Dihydropyridines"], headers ),
                RowItemModel([-110, -2000, datetime(2110, 3, 8),  -6540, "PRILOSEC 20 MG PO CPDR", "GASTROINTESTINAL", "PROTON-PUMP INHIBITORS", "Gastric Acid Secretion Reducing Agents - Proton Pump Inhibitors (PPIs)"], headers ),
                RowItemModel([-120, -2000, datetime(2110, 3, 8),  -8113, "TRIAMCINOLONE 0.1% CREAM", "SKIN PREPS", "TOPICAL ANTI-INFLAMMATORY STEROIDAL", "Dermatological - Glucocorticoid"], headers ),
                # Multiple or no mappings
                RowItemModel([-130, -3000, datetime(2109, 9,20),-126745, "NORETHINDRN ESTRADIOL", "CONTRACEPTIVES", "CONTRACEPTIVES,ORAL", "Contraceptive Oral - Monophasic"], headers ),
                RowItemModel([-140, -4000, datetime(2110, 5, 4),  -28384, "HYDROCODONE-ACETAMINOPHEN 10-325 MG PO TABS", "ANALGESICS", "ANALGESICS, NARCOTICS", "Analgesic Narcotic Hydrocodone Combinations"], headers ),
                # Excessively complex mapping
                RowItemModel([-150, -5000, datetime(2108, 8, 6), -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("stride_preadmit_med", dataModel, retrieveCol="pat_anon_id" );

        # Mapping table to simplify dose
        headers = ["medication_id", "name", "rxcui", "active_ingredient"];
        dataModels = \
            [   # Mappings to active ingredients
                RowItemModel( [ -5680, "NORVASC 5 MG PO TABS", -17767, "Amlodipine"], headers ),
                RowItemModel( [ -6540, "PRILOSEC 20 MG PO CPDR", -7646, "Omeprazole"], headers ),
                RowItemModel( [ -8113, "TRIAMCINOLONE ACETONIDE 0.1 % TP CREA", -10759, "Triamcinolone"], headers ),
                # If multiple active ingredients in a combo, unravel to active components
                RowItemModel( [ -28384, "HYDROCODONE-ACETAMINOPHEN 10-325 MG PO TABS", -161, "Acetaminophen"], headers ),
                RowItemModel( [ -28384, "HYDROCODONE-ACETAMINOPHEN 10-325 MG PO TABS", -5489, "Hydrocodone"], headers ),
                # No mapping entries for Norethindrone+Estradiol
                # Excessive mappings for pneumovax
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854930, "pneumococcal capsular polysaccharide type 1 vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854932, "pneumococcal capsular polysaccharide type 10A vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854934, "pneumococcal capsular polysaccharide type 11A vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854936, "pneumococcal capsular polysaccharide type 12F vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854938, "pneumococcal capsular polysaccharide type 14 vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854940, "pneumococcal capsular polysaccharide type 15B vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854942, "pneumococcal capsular polysaccharide type 17F vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854944, "pneumococcal capsular polysaccharide type 18C vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854946, "pneumococcal capsular polysaccharide type 19A vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854948, "pneumococcal capsular polysaccharide type 19F vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854950, "pneumococcal capsular polysaccharide type 2 vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854952, "pneumococcal capsular polysaccharide type 20 vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854954, "pneumococcal capsular polysaccharide type 22F vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854956, "pneumococcal capsular polysaccharide type 23F vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854958, "pneumococcal capsular polysaccharide type 3 vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854960, "pneumococcal capsular polysaccharide type 33F vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854962, "pneumococcal capsular polysaccharide type 4 vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854964, "pneumococcal capsular polysaccharide type 5 vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854966, "pneumococcal capsular polysaccharide type 6B vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854968, "pneumococcal capsular polysaccharide type 7F vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854970, "pneumococcal capsular polysaccharide type 8 vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854972, "pneumococcal capsular polysaccharide type 9N vaccine"], headers ),
                RowItemModel( [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854974, "pneumococcal capsular polysaccharide type 9V vaccine"], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("stride_mapped_meds", dataModel, retrieveCol="rxcui" );

        self.converter = STRIDEPreAdmitMedConversion();  # Instance to test on

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")

        DBUtil.execute \
        (   """delete from patient_item 
            where clinical_item_id in 
            (   select clinical_item_id
                from clinical_item as ci, clinical_item_category as cic
                where ci.clinical_item_category_id = cic.clinical_item_category_id
                and cic.source_table = 'stride_preadmit_med'
            );
            """
        );
        DBUtil.execute \
        (   """delete from clinical_item 
            where clinical_item_category_id in 
            (   select clinical_item_category_id 
                from clinical_item_category 
                where source_table = 'stride_preadmit_med'
            );
            """
        );
        DBUtil.execute("delete from clinical_item_category where source_table = 'stride_preadmit_med';");

        DBUtil.execute("delete from stride_mapped_meds where rxcui < 0");
        DBUtil.execute("delete from stride_preadmit_med where stride_preadmit_med_id < 0");

        DBTestCase.tearDown(self);

    def test_dataConversion_normalized(self):
        # Run the data conversion on the same data and look for expected records
        log.debug("Run the conversion process...");
        convOptions = ConversionOptions();
        convOptions.startDate = TEST_START_DATE;
        convOptions.normalizeMixtures = True;
        self.converter.convertSourceItems(convOptions);

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
                cic.source_table = 'stride_preadmit_med'
            order by
                pi.external_id desc, ci.external_id desc
            """;
        expectedData = \
            [   # Simple mappings
                [-100, -1000, None, "Preadmit Med", -17767, "RXCUI-17767", "Amlodipine", datetime(2113, 7, 6) ],
                [-110, -2000, None, "Preadmit Med", -7646, "RXCUI-7646", "Omeprazole", datetime(2110, 3, 8) ],
                [-120, -2000, None, "Preadmit Med", -10759, "RXCUI-10759", "Triamcinolone", datetime(2110, 3, 8) ],
                # No mappings
                [-130, -3000, None, "Preadmit Med", -126745, "MED-126745", "NORETHINDRN ESTRADIOL", datetime(2109, 9, 20) ],
                # Multiple mappings
                [-140, -4000, None, "Preadmit Med",  -161, "RXCUI-161", "Acetaminophen", datetime(2110, 5, 4) ],
                [-140, -4000, None, "Preadmit Med", -5489, "RXCUI-5489", "Hydrocodone", datetime(2110, 5, 4) ],
                # Excessively complex mapping
                [-150, -5000, None, "Preadmit Med", -854930, "RXCUI-854930", "Pneumococcal Capsular Polysaccharide Type 1 Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854932, "RXCUI-854932", "Pneumococcal Capsular Polysaccharide Type 10A Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854934, "RXCUI-854934", "Pneumococcal Capsular Polysaccharide Type 11A Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854936, "RXCUI-854936", "Pneumococcal Capsular Polysaccharide Type 12F Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854938, "RXCUI-854938", "Pneumococcal Capsular Polysaccharide Type 14 Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854940, "RXCUI-854940", "Pneumococcal Capsular Polysaccharide Type 15B Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854942, "RXCUI-854942", "Pneumococcal Capsular Polysaccharide Type 17F Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854944, "RXCUI-854944", "Pneumococcal Capsular Polysaccharide Type 18C Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854946, "RXCUI-854946", "Pneumococcal Capsular Polysaccharide Type 19A Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854948, "RXCUI-854948", "Pneumococcal Capsular Polysaccharide Type 19F Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854950, "RXCUI-854950", "Pneumococcal Capsular Polysaccharide Type 2 Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854952, "RXCUI-854952", "Pneumococcal Capsular Polysaccharide Type 20 Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854954, "RXCUI-854954", "Pneumococcal Capsular Polysaccharide Type 22F Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854956, "RXCUI-854956", "Pneumococcal Capsular Polysaccharide Type 23F Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854958, "RXCUI-854958", "Pneumococcal Capsular Polysaccharide Type 3 Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854960, "RXCUI-854960", "Pneumococcal Capsular Polysaccharide Type 33F Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854962, "RXCUI-854962", "Pneumococcal Capsular Polysaccharide Type 4 Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854964, "RXCUI-854964", "Pneumococcal Capsular Polysaccharide Type 5 Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854966, "RXCUI-854966", "Pneumococcal Capsular Polysaccharide Type 6B Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854968, "RXCUI-854968", "Pneumococcal Capsular Polysaccharide Type 7F Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854970, "RXCUI-854970", "Pneumococcal Capsular Polysaccharide Type 8 Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854972, "RXCUI-854972", "Pneumococcal Capsular Polysaccharide Type 9N Vaccine", datetime(2108, 8, 6) ],
                [-150, -5000, None, "Preadmit Med", -854974, "RXCUI-854974", "Pneumococcal Capsular Polysaccharide Type 9V Vaccine", datetime(2108, 8, 6) ],
            ];
        actualData = DBUtil.execute(testQuery);
        self.assertEqualTable( expectedData, actualData );

        # Query for medication class label population
        testQuery = \
            """
            select 
                medication_id,
                name,
                rxcui,
                active_ingredient,
                thera_class,
                pharm_class,
                pharm_subclass
            from stride_mapped_meds as map
            where
                medication_id < 0 and rxcui < 0
            order by
                medication_id desc, rxcui desc
            """;
        expectedData = \
            [
                [ -5680, "NORVASC 5 MG PO TABS", -17767, "Amlodipine", "CARDIAC DRUGS", "CALCIUM CHANNEL BLOCKING AGENTS", "Calcium Channel Blockers - Dihydropyridines"],
                [ -6540, "PRILOSEC 20 MG PO CPDR", -7646, "Omeprazole", "GASTROINTESTINAL", "PROTON-PUMP INHIBITORS", "Gastric Acid Secretion Reducing Agents - Proton Pump Inhibitors (PPIs)"],
                [ -8113, "TRIAMCINOLONE ACETONIDE 0.1 % TP CREA", -10759, "Triamcinolone", "SKIN PREPS", "TOPICAL ANTI-INFLAMMATORY STEROIDAL", "Dermatological - Glucocorticoid"],
                # If multiple active ingredients in a combo, unravel to active components
                [ -28384, "HYDROCODONE-ACETAMINOPHEN 10-325 MG PO TABS", -161, "Acetaminophen", "ANALGESICS", "ANALGESICS, NARCOTICS", "Analgesic Narcotic Hydrocodone Combinations"],
                [ -28384, "HYDROCODONE-ACETAMINOPHEN 10-325 MG PO TABS", -5489, "Hydrocodone", "ANALGESICS", "ANALGESICS, NARCOTICS", "Analgesic Narcotic Hydrocodone Combinations"],
                # No mapping entries for Norethindrone+Estradiol
                # Excessive mappings for pneumovax
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854930, "pneumococcal capsular polysaccharide type 1 vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854932, "pneumococcal capsular polysaccharide type 10A vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854934, "pneumococcal capsular polysaccharide type 11A vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854936, "pneumococcal capsular polysaccharide type 12F vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854938, "pneumococcal capsular polysaccharide type 14 vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854940, "pneumococcal capsular polysaccharide type 15B vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854942, "pneumococcal capsular polysaccharide type 17F vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854944, "pneumococcal capsular polysaccharide type 18C vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854946, "pneumococcal capsular polysaccharide type 19A vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854948, "pneumococcal capsular polysaccharide type 19F vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854950, "pneumococcal capsular polysaccharide type 2 vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854952, "pneumococcal capsular polysaccharide type 20 vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854954, "pneumococcal capsular polysaccharide type 22F vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854956, "pneumococcal capsular polysaccharide type 23F vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854958, "pneumococcal capsular polysaccharide type 3 vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854960, "pneumococcal capsular polysaccharide type 33F vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854962, "pneumococcal capsular polysaccharide type 4 vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854964, "pneumococcal capsular polysaccharide type 5 vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854966, "pneumococcal capsular polysaccharide type 6B vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854968, "pneumococcal capsular polysaccharide type 7F vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854970, "pneumococcal capsular polysaccharide type 8 vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854972, "pneumococcal capsular polysaccharide type 9N vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854974, "pneumococcal capsular polysaccharide type 9V vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
            ];
        actualData = DBUtil.execute(testQuery);
        self.assertEqualTable( expectedData, actualData );


    def test_dataConversion_maxMixtureCount(self):
        # Run the data conversion on the same data and look for expected records
        log.debug("Run the conversion process...");
        convOptions = ConversionOptions();
        convOptions.startDate = TEST_START_DATE;
        convOptions.normalizeMixtures = False;
        convOptions.maxMixtureCount = 5;
        self.converter.convertSourceItems(convOptions);

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
                cic.source_table = 'stride_preadmit_med'
            order by
                pi.external_id desc, ci.external_id desc
            """;
        expectedData = \
            [   # Simple mappings
                [-100, -1000, None, "Preadmit Med", -17767, "RXCUI-17767", "Amlodipine", datetime(2113, 7, 6) ],
                [-110, -2000, None, "Preadmit Med", -7646, "RXCUI-7646", "Omeprazole", datetime(2110, 3, 8) ],
                [-120, -2000, None, "Preadmit Med", -10759, "RXCUI-10759", "Triamcinolone", datetime(2110, 3, 8) ],
                # No mappings
                [-130, -3000, None, "Preadmit Med", -126745, "MED-126745", "NORETHINDRN ESTRADIOL", datetime(2109, 9, 20) ],
                # Multiple mappings
                [-140, -4000, None, "Preadmit Med",  -28384, "MED-28384", "Acetaminophen-Hydrocodone", datetime(2110, 5, 4) ],
                # Excessively complex mapping
                [-150, -5000, None, "Preadmit Med", -95140, "MED-95140", "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", datetime(2108, 8, 6) ],
            ];
        actualData = DBUtil.execute(testQuery);
        self.assertEqualTable( expectedData, actualData );

        # Query for medication class label population
        testQuery = \
            """
            select 
                medication_id,
                name,
                rxcui,
                active_ingredient,
                thera_class,
                pharm_class,
                pharm_subclass
            from stride_mapped_meds as map
            where
                medication_id < 0 and rxcui < 0
            order by
                medication_id desc, rxcui desc
            """;
        expectedData = \
            [
                [ -5680, "NORVASC 5 MG PO TABS", -17767, "Amlodipine", "CARDIAC DRUGS", "CALCIUM CHANNEL BLOCKING AGENTS", "Calcium Channel Blockers - Dihydropyridines"],
                [ -6540, "PRILOSEC 20 MG PO CPDR", -7646, "Omeprazole", "GASTROINTESTINAL", "PROTON-PUMP INHIBITORS", "Gastric Acid Secretion Reducing Agents - Proton Pump Inhibitors (PPIs)"],
                [ -8113, "TRIAMCINOLONE ACETONIDE 0.1 % TP CREA", -10759, "Triamcinolone", "SKIN PREPS", "TOPICAL ANTI-INFLAMMATORY STEROIDAL", "Dermatological - Glucocorticoid"],
                # If multiple active ingredients in a combo, unravel to active components
                [ -28384, "HYDROCODONE-ACETAMINOPHEN 10-325 MG PO TABS", -161, "Acetaminophen", "ANALGESICS", "ANALGESICS, NARCOTICS", "Analgesic Narcotic Hydrocodone Combinations"],
                [ -28384, "HYDROCODONE-ACETAMINOPHEN 10-325 MG PO TABS", -5489, "Hydrocodone", "ANALGESICS", "ANALGESICS, NARCOTICS", "Analgesic Narcotic Hydrocodone Combinations"],
                # No mapping entries for Norethindrone+Estradiol
                # Excessive mappings for pneumovax
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854930, "pneumococcal capsular polysaccharide type 1 vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854932, "pneumococcal capsular polysaccharide type 10A vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854934, "pneumococcal capsular polysaccharide type 11A vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854936, "pneumococcal capsular polysaccharide type 12F vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854938, "pneumococcal capsular polysaccharide type 14 vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854940, "pneumococcal capsular polysaccharide type 15B vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854942, "pneumococcal capsular polysaccharide type 17F vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854944, "pneumococcal capsular polysaccharide type 18C vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854946, "pneumococcal capsular polysaccharide type 19A vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854948, "pneumococcal capsular polysaccharide type 19F vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854950, "pneumococcal capsular polysaccharide type 2 vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854952, "pneumococcal capsular polysaccharide type 20 vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854954, "pneumococcal capsular polysaccharide type 22F vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854956, "pneumococcal capsular polysaccharide type 23F vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854958, "pneumococcal capsular polysaccharide type 3 vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854960, "pneumococcal capsular polysaccharide type 33F vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854962, "pneumococcal capsular polysaccharide type 4 vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854964, "pneumococcal capsular polysaccharide type 5 vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854966, "pneumococcal capsular polysaccharide type 6B vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854968, "pneumococcal capsular polysaccharide type 7F vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854970, "pneumococcal capsular polysaccharide type 8 vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854972, "pneumococcal capsular polysaccharide type 9N vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
                [ -95140, "PNEUMOCOCCAL 23-VALPS VACCINE 25 MCG/0.5 ML INJ INJ", -854974, "pneumococcal capsular polysaccharide type 9V vaccine", "BIOLOGICALS", "GRAM POSITIVE COCCI VACCINES", "Vaccine Bacterial - Gram Positive Cocci"],
            ];
        actualData = DBUtil.execute(testQuery);
        self.assertEqualTable( expectedData, actualData );

def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestSTRIDEPreAdmitMedConversion("test_incColNamesAndTypeCodes"));
    #suite.addTest(TestSTRIDEPreAdmitMedConversion("test_insertFile_skipErrors"));
    #suite.addTest(TestSTRIDEPreAdmitMedConversion('test_executeIterator'));
    #suite.addTest(TestSTRIDEPreAdmitMedConversion('test_dataConversion_maxMixtureCount'));
    suite.addTest(unittest.makeSuite(TestSTRIDEPreAdmitMedConversion));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
