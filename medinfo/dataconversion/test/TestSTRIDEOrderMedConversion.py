#!/usr/bin/env python
"""Test case for respective module in application package"""

import sys, os
from cStringIO import StringIO
from datetime import datetime;
import unittest

from Const import RUNNER_VERBOSITY;
from Util import log;

from medinfo.db.test.Util import DBTestCase;

from medinfo.db import DBUtil
from medinfo.db.Model import SQLQuery, RowItemModel;

from medinfo.dataconversion.STRIDEOrderMedConversion import STRIDEOrderMedConversion, ConversionOptions;

TEST_START_DATE = datetime(2100,1,1);   # Date in far future to start checking for test records to avoid including existing data in database

class TestSTRIDEOrderMedConversion(DBTestCase):
    def setUp(self):
        """Prepare state for test cases"""
        DBTestCase.setUp(self);
        
        # Relabel any existing data to not interfere with the new test data that will be produced
        DBUtil.execute("update clinical_item_category set source_table = 'PreTest_order_med' where source_table = 'stride_order_med';");
    
        log.info("Populate the database with test data")
        
        self.orderMedIdStrList = list();
        headers = ["order_med_id", "pat_id", "pat_enc_csn_id", "ordering_date", "medication_id", "description","freq_name","med_route","number_of_doses"];
        dataModels = \
            [   # Deliberately design dates in far future to facilitate isolated testing
                RowItemModel( [ -418063010, "3032765", 111, datetime(2111,12,12, 8,56), 9000000, "ZZZ IMS TEMPLATE","DAILY","PO", None], headers ),
                RowItemModel( [ -418436155, "1607844", 222, datetime(2111,12,20, 0,40), -1080, "BISACODYL 10 MG PR SUPP","DAILY PRN","PR", None], headers ),
                RowItemModel( [ -418436145, "1607844", 222, datetime(2111,12,22, 0,40), -1080, "BISACODYL 10 MG PR SUPP","DAILY","PR", None], headers ),
                RowItemModel( [ -421032269, "2968778", 333, datetime(2112, 2, 8,11,17), -96559, "PIPERACILLIN-TAZOBACTAM-DEXTRS 3.375 GRAM/50 ML IV PGBK","EVERY 6 HOURS","IV", None], headers ),
                RowItemModel( [ -418011851, "-2429057", 444, datetime(2111,12,10,19, 9), -10011, "FAMOTIDINE 20 MG PO TABS","2 TIMES DAILY","PO", None], headers ),
                RowItemModel( [ -418013851, "-2429057", 444, datetime(2111,12,10,19,10), -10012, "FAMOTIDINE 40 MG PO TABS","2 TIMES DAILY","PO", None], headers ),
                RowItemModel( [ -418062652, "3036488", 555, datetime(2111,12,12, 8,30), -5007, "METOPROLOL TARTRATE 5 MG/5 ML IV SOLN 20 mg injection","ONCE","IV", 1], headers ),
                RowItemModel( [ -418062352, "3016488", 666, datetime(2111,12,13, 8,30), -5007, "METOPROLOL TARTRATE 5 MG/5 ML IV SOLN","ONCE","IV", 1], headers ),
                RowItemModel( [ -414321352, "3036588", 777, datetime(2111,12,14, 8,30), -5007, "ZZZ IMS TEMPLATE","ONCE","IV", 1], headers ),

                # Simple mixture in unimportant base
                RowItemModel( [ -395900000, "1234567", 888, datetime(2111, 1, 2, 3, 0), -520102, "CEFEPIME 2 GM IVPB","ONCE","IV", 1], headers ),  
                RowItemModel( [ -395800000, "1234567", 888, datetime(2111, 1,10, 3, 0), -520102, "CEFEPIME 2 GM IVPB","q8h","IV", 6], headers ),  # Fixed number of doses
                RowItemModel( [ -395700000, "1234567", 888, datetime(2111, 3,10, 3, 0), -520102, "CEFEPIME 2 GM IVPB","q8h","IV", None], headers ),  # No dose limit specified

                # Complex mixtures
                RowItemModel( [ -392000000, "1234567", 888, datetime(2111, 4, 1, 3, 0), -530000, "IVF Mix","ONCE","IV", 1], headers ),  
                RowItemModel( [ -391000000, "1234567", 888, datetime(2111, 4, 2, 3, 0), -540000, "Mini TPN","ONCE","IV", 1], headers ),  
                RowItemModel( [ -390000000, "1234567", 888, datetime(2111, 5, 2, 3, 0), -550000, "TPN Adult","Continuous","IV", None], headers ),  
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("stride_order_med", dataModel, retrieveCol="order_med_id" );
            self.orderMedIdStrList.append( str(dataItemId) );

        # Child table for more detailed mixtures
        headers = ["order_med_id", "line", "medication_id", "medication_name","ingredient_type_c","ingredient_type"];
        dataModels = \
            [   # Just a dose combination
                RowItemModel( [ -418063010, 1, -6494, "PREDNISONE 10 MG PO TABS", 3, "Medications",], headers ),
                RowItemModel( [ -418063010, 2, -6498, "PREDNISONE 50 MG PO TABS", 3, "Medications",], headers ),

                # Simple mixture with a base fluid of negligible significance
                RowItemModel( [ -395900000, 1, -87114, "CEFEPIME 2 GRAM IV SOLR", 3, "Medications",], headers ),
                RowItemModel( [ -395900000, 2, -2364, "DEXTROSE 5 % IN WATER (D5W) IV SOLP", 1, "Base",], headers ),
                RowItemModel( [ -395800000, 1, -87114, "CEFEPIME 2 GRAM IV SOLR", 3, "Medications",], headers ),
                RowItemModel( [ -395800000, 2, -2364, "DEXTROSE 5 % IN WATER (D5W) IV SOLP", 1, "Base",], headers ),
                RowItemModel( [ -395700000, 1, -87114, "CEFEPIME 2 GRAM IV SOLR", 3, "Medications",], headers ),
                RowItemModel( [ -395700000, 2, -2364, "DEXTROSE 5 % IN WATER (D5W) IV SOLP", 1, "Base",], headers ),
                
                # IVF Mix
                RowItemModel( [ -392000000, 2, -2367, "DEXTROSE 70 % IN WATER (D70W) IV SOLP", 1, "Base",], headers ),
                RowItemModel( [ -392000000, 3, -7322, "SODIUM CHLORIDE 4 MEQ/ML IV SOLP", 2, "Additives",], headers ),
                RowItemModel( [ -392000000, 5, -116034, "POTASSIUM CHLORIDE 2 MEQ/ML IV SOLP", 2, "Additives",], headers ),

                # Mini mixture, expands
                RowItemModel( [ -391000000, 1, -203799, "PARENTERAL AMINO ACID 10% NO.6 10 % IV SOLP", 1, "Base",], headers ),
                RowItemModel( [ -391000000, 2, -2367, "DEXTROSE 70 % IN WATER (D70W) IV SOLP", 1, "Base",], headers ),
                RowItemModel( [ -391000000, 3, -7322, "SODIUM CHLORIDE 4 MEQ/ML IV SOLP", 2, "Additives",], headers ),
                RowItemModel( [ -391000000, 4, -7351, "SODIUM PHOSPHATE 3 MMOL/ML IV SOLN", 2, "Additives",], headers ),

                # Complex mixture
                RowItemModel( [ -390000000, 1, -203799, "PARENTERAL AMINO ACID 10% NO.6 10 % IV SOLP", 1, "Base",], headers ),
                RowItemModel( [ -390000000, 2, -2367, "DEXTROSE 70 % IN WATER (D70W) IV SOLP", 1, "Base",], headers ),
                RowItemModel( [ -390000000, 3, -7322, "SODIUM CHLORIDE 4 MEQ/ML IV SOLP", 2, "Additives",], headers ),
                RowItemModel( [ -390000000, 4, -7351, "SODIUM PHOSPHATE 3 MMOL/ML IV SOLN", 2, "Additives",], headers ),
                RowItemModel( [ -390000000, 5, -116034, "POTASSIUM CHLORIDE 2 MEQ/ML IV SOLP", 2, "Additives",], headers ),
                RowItemModel( [ -390000000, 6, -1312, "CALCIUM GLUCONATE 100 MG/ML (10%) IV SOLN", 2, "Additives",], headers ),
                RowItemModel( [ -390000000, 7, -4720, "MAGNESIUM SULFATE 4 MEQ/ML (50 %) INJ SOLN", 2, "Additives",], headers ),
                RowItemModel( [ -390000000, 8, -8047, "TRACE ELEM ZN-CUPRIC CL-MN-CR 0.8-0.2-0.16 MG IV SOLN", 2, "Additives",], headers ),
                RowItemModel( [ -390000000, 9, -124215, "MVI, ADULT NO.1 WITH VIT K 3,300 UNIT- 150 MCG/10 ML IV SOLN", 2, "Additives",], headers ),
                RowItemModel( [ -390000000, 10,-540571, "INSULIN REG HUMAN 100 UNITS/ML INJ", 2, "Additives",], headers ),
                
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("stride_order_medmixinfo", dataModel, retrieveCol="order_med_id" );

        # Mapping table to simplify dose
        headers = ["medication_id", "medication_name", "rxcui", "active_ingredient"];
        dataModels = \
            [   # If multiple active ingredients in a combo, unravel to active components
                RowItemModel( [ -96559, "PIPERACILLIN-TAZOBACTAM-DEXTRS 3.375 GRAM/50 ML IV PGBK", -1001, "Piperacillin"], headers ),
                RowItemModel( [ -96559, "PIPERACILLIN-TAZOBACTAM-DEXTRS 3.375 GRAM/50 ML IV PGBK", -1002, "Tazobactam"], headers ),

                # Multiple names / dosage totals for the same medication, use this mapping to narrow to a common ingredient
                RowItemModel( [ -10011, "FAMOTIDINE 20 MG PO TABS", -2001, "Famotidine"], headers ),
                RowItemModel( [ -10012, "FAMOTIDINE 40 MG PO TABS", -2001, "Famotidine"], headers ),
                RowItemModel( [ -1080, "BISACODYL 10 MG PR SUPP", -3001, "Bisacodyl"], headers ),
                RowItemModel( [ -6494, "PREDNISONE 10 MG PO TABS", -4001, "prednisone"], headers ),
                RowItemModel( [ -6498, "PREDNISONE 50 MG PO TABS", -4001, "prednisone"], headers ),

                # Simple mixture
                RowItemModel( [ -87114, "CEFEPIME 2 GRAM IV SOLR", -20481, "cefepime"], headers ),
                RowItemModel( [ -2364, "DEXTROSE 5% IN WATER (D5W) IV SOLP", -4850, "Glucose"], headers ),
                
                # Additional medication level mapping should probably ignored if have mixture components
                RowItemModel( [ -520102, "CEFEPIME 2 GM IVPB", -20481, "cefepime"], headers ),

                # Complex ingredients
                RowItemModel( [ -203799, 'PARENTERAL AMINO ACID 10% NO.6 10 % IV SOLP',   -10898,  'Tryptophan',], headers ),
                RowItemModel( [ -203799, 'PARENTERAL AMINO ACID 10% NO.6 10 % IV SOLP',   -11115,  'Valine',], headers ),
                RowItemModel( [ -203799, 'PARENTERAL AMINO ACID 10% NO.6 10 % IV SOLP',   -4919,   'Glycine',], headers ),
                RowItemModel( [ -203799, 'PARENTERAL AMINO ACID 10% NO.6 10 % IV SOLP',   -5340,   'Histidine',], headers ),
                RowItemModel( [ -203799, 'PARENTERAL AMINO ACID 10% NO.6 10 % IV SOLP',   -6033,   'Isoleucine',], headers ),
                RowItemModel( [ -203799, 'PARENTERAL AMINO ACID 10% NO.6 10 % IV SOLP',   -6308,   'Leucine',], headers ),
                RowItemModel( [ -203799, 'PARENTERAL AMINO ACID 10% NO.6 10 % IV SOLP',   -6536,   'Lysine',], headers ),
                RowItemModel( [ -203799, 'PARENTERAL AMINO ACID 10% NO.6 10 % IV SOLP',   -6837,   'Methionine',], headers ),
                RowItemModel( [ -203799, 'PARENTERAL AMINO ACID 10% NO.6 10 % IV SOLP',   -8156,   'Phenylalanine',], headers ),
                RowItemModel( [ -203799, 'PARENTERAL AMINO ACID 10% NO.6 10 % IV SOLP',   -8737,   'Proline',], headers ),
                RowItemModel( [ -203799, 'PARENTERAL AMINO ACID 10% NO.6 10 % IV SOLP',   -9671,   'Serine',], headers ),
                RowItemModel( [ -203799, 'PARENTERAL AMINO ACID 10% NO.6 10 % IV SOLP',   -10524,  'Threonine',], headers ),
                RowItemModel( [ -203799, 'PARENTERAL AMINO ACID 10% NO.6 10 % IV SOLP',   -10962,  'Tyrosine',], headers ),
                RowItemModel( [ -203799, 'PARENTERAL AMINO ACID 10% NO.6 10 % IV SOLP',   -426,    'Alanine',], headers ),
                RowItemModel( [ -203799, 'PARENTERAL AMINO ACID 10% NO.6 10 % IV SOLP',   -1091,   'Arginine',], headers ),
                RowItemModel( [ -2367,   'DEXTROSE 70% IN WATER (D70W) IV SOLP',  -4850,   'Glucose',], headers ),
                RowItemModel( [ -7322,   'SODIUM CHLORIDE 4 MEQ/ML IV SOLP',  -9863,   'Sodium Chloride',], headers ),
                RowItemModel( [ -7351,   'SODIUM PHOSPHATE 3 MILLIMOLE/ML IV SOLN',   -235496, 'Sodium Phosphate, Monobasic',], headers ),
                RowItemModel( [ -7351,   'SODIUM PHOSPHATE 3 MILLIMOLE/ML IV SOLN',   -236719, 'Sodium Phosphate, Dibasic',], headers ),
                RowItemModel( [ -116034, 'POTASSIUM CHLORIDE 2 MEQ/ML IV SOLP',   -8591,   'Potassium Chloride',], headers ),
                RowItemModel( [ -1312,   'CALCIUM GLUCONATE 100 MG/ML (10%) IV SOLN', -1908,   'Calcium Gluconate',], headers ),
                RowItemModel( [ -4720,   'MAGNESIUM SULFATE 50 % (4 MEQ/ML) INJ SOLN',    -6585,   'Magnesium Sulfate',], headers ),
                RowItemModel( [ -8047,   'TRACE ELEM ZN-CUPRIC CL-MN-CR 0.8-0.2-0.16 MG IV SOLN', -39937,  'zinc chloride',], headers ),
                RowItemModel( [ -8047,   'TRACE ELEM ZN-CUPRIC CL-MN-CR 0.8-0.2-0.16 MG IV SOLN', -21032,  'chromous chloride',], headers ),
                RowItemModel( [ -8047,   'TRACE ELEM ZN-CUPRIC CL-MN-CR 0.8-0.2-0.16 MG IV SOLN', -21579,  'Copper Sulfate',], headers ),
                RowItemModel( [ -8047,   'TRACE ELEM ZN-CUPRIC CL-MN-CR 0.8-0.2-0.16 MG IV SOLN', -29261,  'manganese chloride',], headers ),
                RowItemModel( [ -124215, 'MVI, ADULT NO.1 WITH VIT K 1-5-10-200 MG-MCG-MG-MG IV SOLN',    -8308,   'Vitamin K 1',], headers ),
                RowItemModel( [ -124215, 'MVI, ADULT NO.1 WITH VIT K 1-5-10-200 MG-MCG-MG-MG IV SOLN',    -89905,  'Multivitamin preparation',], headers ),
                RowItemModel( [ -540571, 'INSULIN REG HUMAN 100 UNITS/ML INJ',    -253182, 'Regular Insulin, Human',], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("stride_mapped_meds", dataModel, retrieveCol="rxcui" );

        # Certain items drawn from order sets
        headers = ["order_med_id", "protocol_id","protocol_name","section_name","smart_group"];
        dataModels = \
            [   
                RowItemModel( [ -418436145, -111, "General Admit", "Medications", "Stool Softeners",], headers ),
                RowItemModel( [ -421032269, -111, "General Admit", "Medications", "Antibiotics",], headers ),
                RowItemModel( [ -391000000, -222, "Nutrition", "Infusions", "TPN",], headers ),
            ];
        for dataModel in dataModels:
            (dataItemId, isNew) = DBUtil.findOrInsertItem("stride_orderset_order_med", dataModel, retrieveCol="order_med_id" );
        
        self.converter = STRIDEOrderMedConversion();  # Instance to test on

    def tearDown(self):
        """Restore state from any setUp or test steps"""
        log.info("Purge test records from the database")

        DBUtil.execute \
        (   """delete from patient_item_collection_link
            where item_collection_item_id in 
            (   select item_collection_item_id
                from item_collection_item as ici, item_collection as ic
                where ici.item_collection_id = ic.item_collection_id
                and ic.external_id < 0
            );
            """
        );
        DBUtil.execute \
        (   """delete from item_collection_item
            where item_collection_id in 
            (   select item_collection_id
                from item_collection as ic
                where ic.external_id < 0
            );
            """
        );
        DBUtil.execute("delete from item_collection where external_id < 0;");

        DBUtil.execute \
        (   """delete from patient_item 
            where clinical_item_id in 
            (   select clinical_item_id
                from clinical_item as ci, clinical_item_category as cic
                where ci.clinical_item_category_id = cic.clinical_item_category_id
                and cic.source_table = 'stride_order_med'
            );
            """
        );
        DBUtil.execute \
        (   """delete from clinical_item 
            where clinical_item_category_id in 
            (   select clinical_item_category_id 
                from clinical_item_category 
                where source_table = 'stride_order_med'
            );
            """
        );
        DBUtil.execute("delete from clinical_item_category where source_table = 'stride_order_med';");
        DBUtil.execute("update clinical_item_category set source_table = 'stride_order_med' where source_table = 'PreTest_order_med';"); # Reset labels of any prior data

        DBUtil.execute("delete from stride_orderset_order_med where order_med_id in (%s)" % str.join(",", self.orderMedIdStrList) );
        DBUtil.execute("delete from stride_mapped_meds where rxcui < 0");
        DBUtil.execute("delete from stride_order_medmixinfo where order_med_id in (%s)" % str.join(",", self.orderMedIdStrList) );
        DBUtil.execute("delete from stride_order_med where order_med_id in (%s)" % str.join(",", self.orderMedIdStrList) );

        DBTestCase.tearDown(self);

    def test_dataConversion_normalized(self):
        # Run the data conversion on the same data and look for expected records
        log.debug("Run the conversion process...");
        convOptions = ConversionOptions();
        convOptions.startDate = TEST_START_DATE;
        convOptions.normalizeMixtures = True;
        convOptions.doseCountLimit = 5;
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
                cic.source_table = 'stride_order_med'
            order by
                pi.external_id, ci.external_id
            """;
        expectedData = \
            [
                [ -421032269, 2968778, 333, "Med (IV)", -1002, "RXCUI-1002", "Tazobactam (IV)", datetime(2112,2,8,11,17) ],
                [ -421032269, 2968778, 333, "Med (IV)", -1001, "RXCUI-1001", "Piperacillin (IV)", datetime(2112,2,8,11,17) ],
                #[ -418436155, 1607844, "Med (PR)", -3001, "RXCUI-3001", "Bisacodyl (PR)", datetime(2111,12,20,0,40) ], # Skip PRNs
                [ -418436145, 1607844, 222, "Med (PR)", -3001, "RXCUI-3001", "Bisacodyl (PR)", datetime(2111,12,22,0,40) ],
                [ -418063010, 3032765, 111, "Med (PO)", -4001, "RXCUI-4001", "Prednisone (PO)", datetime(2111,12,12,8,56) ],
                [ -418062652, 3036488, 555, "Med (IV)", -5007, "MED-5007 (<5)", "METOPROLOL TARTRATE 5 MG/5 ML IV SOLN (<5 doses)", datetime(2111,12,12,8,30) ],
                [ -418062352, 3016488, 666, "Med (IV)", -5007, "MED-5007 (<5)", "METOPROLOL TARTRATE 5 MG/5 ML IV SOLN (<5 doses)", datetime(2111,12,13,8,30) ],
                [ -418013851, -2429057, 444, "Med (PO)", -2001, "RXCUI-2001", "Famotidine (PO)", datetime(2111,12,10,19,10) ],
                [ -418011851, -2429057, 444, "Med (PO)", -2001, "RXCUI-2001", "Famotidine (PO)", datetime(2111,12,10,19,9) ],
                [ -414321352, 3036588, 777, "Med (IV)", -5007, "MED-5007 (<5)", "METOPROLOL TARTRATE 5 MG/5 ML IV SOLN (<5 doses)", datetime(2111,12,14,8,30) ],

                # Simple mixture with different dosing counts
                [ -395900000, 1234567, 888, "Med (IV)", -20481, "RXCUI-20481 (<5)", "Cefepime (IV) (<5 doses)", datetime(2111, 1, 2, 3, 0)],   
                [ -395800000, 1234567, 888, "Med (IV)", -20481, "RXCUI-20481", "Cefepime (IV)", datetime(2111, 1,10, 3, 0)],   
                [ -395700000, 1234567, 888, "Med (IV)", -20481, "RXCUI-20481", "Cefepime (IV)", datetime(2111, 3,10, 3, 0)],   

                # IVF Mix
                [ -392000000, 1234567, 888, "Med (IV)", -9863, 'RXCUI-9863 (<5)', 'Sodium Chloride (IV) (<5 doses)', datetime(2111, 4, 1, 3, 0)],   
                [ -392000000, 1234567, 888, "Med (IV)", -8591, 'RXCUI-8591 (<5)', 'Potassium Chloride (IV) (<5 doses)', datetime(2111, 4, 1, 3, 0)],   
                [ -392000000, 1234567, 888, "Med (IV)", -4850, 'RXCUI-4850 (<5)', 'Glucose (IV) (<5 doses)', datetime(2111, 4, 1, 3, 0)],   

                # Mini-Mix
                [ -391000000, 1234567, 888, "Med (IV)", -236719, 'RXCUI-236719 (<5)', 'Sodium Phosphate, Dibasic (IV) (<5 doses)', datetime(2111, 4, 2, 3, 0)],   
                [ -391000000, 1234567, 888, "Med (IV)", -235496, 'RXCUI-235496 (<5)', 'Sodium Phosphate, Monobasic (IV) (<5 doses)', datetime(2111, 4, 2, 3, 0)],   
                [ -391000000, 1234567, 888, "Med (IV)", -11115, 'RXCUI-11115 (<5)', 'Valine (IV) (<5 doses)', datetime(2111, 4, 2, 3, 0)],   
                [ -391000000, 1234567, 888, "Med (IV)", -10962, 'RXCUI-10962 (<5)', 'Tyrosine (IV) (<5 doses)', datetime(2111, 4, 2, 3, 0)],   
                [ -391000000, 1234567, 888, "Med (IV)", -10898, 'RXCUI-10898 (<5)', 'Tryptophan (IV) (<5 doses)', datetime(2111, 4, 2, 3, 0)],   
                [ -391000000, 1234567, 888, "Med (IV)", -10524, 'RXCUI-10524 (<5)', 'Threonine (IV) (<5 doses)', datetime(2111, 4, 2, 3, 0)],   
                [ -391000000, 1234567, 888, "Med (IV)", -9863, 'RXCUI-9863 (<5)', 'Sodium Chloride (IV) (<5 doses)', datetime(2111, 4, 2, 3, 0)],   
                [ -391000000, 1234567, 888, "Med (IV)", -9671, 'RXCUI-9671 (<5)', 'Serine (IV) (<5 doses)', datetime(2111, 4, 2, 3, 0)],   
                [ -391000000, 1234567, 888, "Med (IV)", -8737, 'RXCUI-8737 (<5)', 'Proline (IV) (<5 doses)', datetime(2111, 4, 2, 3, 0)],   
                [ -391000000, 1234567, 888, "Med (IV)", -8156, 'RXCUI-8156 (<5)', 'Phenylalanine (IV) (<5 doses)', datetime(2111, 4, 2, 3, 0)],   
                [ -391000000, 1234567, 888, "Med (IV)", -6837, 'RXCUI-6837 (<5)', 'Methionine (IV) (<5 doses)', datetime(2111, 4, 2, 3, 0)],   
                [ -391000000, 1234567, 888, "Med (IV)", -6536, 'RXCUI-6536 (<5)', 'Lysine (IV) (<5 doses)', datetime(2111, 4, 2, 3, 0)],   
                [ -391000000, 1234567, 888, "Med (IV)", -6308, 'RXCUI-6308 (<5)', 'Leucine (IV) (<5 doses)', datetime(2111, 4, 2, 3, 0)],   
                [ -391000000, 1234567, 888, "Med (IV)", -6033, 'RXCUI-6033 (<5)', 'Isoleucine (IV) (<5 doses)', datetime(2111, 4, 2, 3, 0)],   
                [ -391000000, 1234567, 888, "Med (IV)", -5340, 'RXCUI-5340 (<5)', 'Histidine (IV) (<5 doses)', datetime(2111, 4, 2, 3, 0)],   
                [ -391000000, 1234567, 888, "Med (IV)", -4919, 'RXCUI-4919 (<5)', 'Glycine (IV) (<5 doses)', datetime(2111, 4, 2, 3, 0)],   
                [ -391000000, 1234567, 888, "Med (IV)", -4850, 'RXCUI-4850 (<5)', 'Glucose (IV) (<5 doses)', datetime(2111, 4, 2, 3, 0)],   
                [ -391000000, 1234567, 888, "Med (IV)", -1091, 'RXCUI-1091 (<5)', 'Arginine (IV) (<5 doses)', datetime(2111, 4, 2, 3, 0)],   
                [ -391000000, 1234567, 888, "Med (IV)", -426, 'RXCUI-426 (<5)', 'Alanine (IV) (<5 doses)', datetime(2111, 4, 2, 3, 0)],   

                # Complex mixture
                [ -390000000, 1234567, 888, "Med (IV)", -253182, 'RXCUI-253182', 'Regular Insulin, Human (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -236719, 'RXCUI-236719', 'Sodium Phosphate, Dibasic (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -235496, 'RXCUI-235496', 'Sodium Phosphate, Monobasic (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -89905, 'RXCUI-89905', 'Multivitamin Preparation (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -39937, 'RXCUI-39937', 'Zinc Chloride (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -29261, 'RXCUI-29261', 'Manganese Chloride (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -21579, 'RXCUI-21579', 'Copper Sulfate (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -21032, 'RXCUI-21032', 'Chromous Chloride (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -11115, 'RXCUI-11115', 'Valine (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -10962, 'RXCUI-10962', 'Tyrosine (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -10898, 'RXCUI-10898', 'Tryptophan (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -10524, 'RXCUI-10524', 'Threonine (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -9863, 'RXCUI-9863', 'Sodium Chloride (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -9671, 'RXCUI-9671', 'Serine (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -8737, 'RXCUI-8737', 'Proline (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -8591, 'RXCUI-8591', 'Potassium Chloride (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -8308, 'RXCUI-8308', 'Vitamin K 1 (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -8156, 'RXCUI-8156', 'Phenylalanine (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -6837, 'RXCUI-6837', 'Methionine (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -6585, 'RXCUI-6585', 'Magnesium Sulfate (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -6536, 'RXCUI-6536', 'Lysine (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -6308, 'RXCUI-6308', 'Leucine (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -6033, 'RXCUI-6033', 'Isoleucine (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -5340, 'RXCUI-5340', 'Histidine (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -4919, 'RXCUI-4919', 'Glycine (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -4850, 'RXCUI-4850', 'Glucose (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -1908, 'RXCUI-1908', 'Calcium Gluconate (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -1091, 'RXCUI-1091', 'Arginine (IV)', datetime(2111, 5, 2, 3, 0)],   
                [ -390000000, 1234567, 888, "Med (IV)", -426, 'RXCUI-426', 'Alanine (IV)', datetime(2111, 5, 2, 3, 0)],   
            ];
        actualData = DBUtil.execute(testQuery);
        self.assertEqualTable( expectedData, actualData );



        # Query for orderset links
        testQuery = \
            """
            select 
                pi.external_id,
                ci.description,
                ic.external_id,
                ic.name,
                ic.section,
                ic.subgroup
            from
                patient_item as pi,
                clinical_item as ci,
                clinical_item_category as cic,
                patient_item_collection_link as picl,
                item_collection_item as ici,
                item_collection as ic
            where
                pi.clinical_item_id = ci.clinical_item_id and
                ci.clinical_item_category_id = cic.clinical_item_category_id and
                cic.source_table = 'stride_order_med' and
                pi.patient_item_id = picl.patient_item_id and
                picl.item_collection_item_id = ici.item_collection_item_id and
                ici.item_collection_id = ic.item_collection_id
            order by
                pi.external_id, ci.external_id
            """;
        expectedData = \
            [
                [ -421032269, "Tazobactam (IV)", -111,"General Admit","Medications","Antibiotics"],
                [ -421032269, "Piperacillin (IV)", -111,"General Admit","Medications","Antibiotics"],
                [ -418436145, "Bisacodyl (PR)", -111,"General Admit","Medications","Stool Softeners"],

                # Mini-Mix
                [ -391000000, 'Sodium Phosphate, Dibasic (IV) (<5 doses)', -222, "Nutrition","Infusions","TPN"],   
                [ -391000000, 'Sodium Phosphate, Monobasic (IV) (<5 doses)', -222, "Nutrition","Infusions","TPN"],   
                [ -391000000, 'Valine (IV) (<5 doses)', -222, "Nutrition","Infusions","TPN"],   
                [ -391000000, 'Tyrosine (IV) (<5 doses)', -222, "Nutrition","Infusions","TPN"],   
                [ -391000000, 'Tryptophan (IV) (<5 doses)', -222, "Nutrition","Infusions","TPN"],   
                [ -391000000, 'Threonine (IV) (<5 doses)', -222, "Nutrition","Infusions","TPN"],   
                [ -391000000, 'Sodium Chloride (IV) (<5 doses)', -222, "Nutrition","Infusions","TPN"],   
                [ -391000000, 'Serine (IV) (<5 doses)', -222, "Nutrition","Infusions","TPN"],   
                [ -391000000, 'Proline (IV) (<5 doses)', -222, "Nutrition","Infusions","TPN"],   
                [ -391000000, 'Phenylalanine (IV) (<5 doses)', -222, "Nutrition","Infusions","TPN"],   
                [ -391000000, 'Methionine (IV) (<5 doses)', -222, "Nutrition","Infusions","TPN"],   
                [ -391000000, 'Lysine (IV) (<5 doses)', -222, "Nutrition","Infusions","TPN"],   
                [ -391000000, 'Leucine (IV) (<5 doses)', -222, "Nutrition","Infusions","TPN"],   
                [ -391000000, 'Isoleucine (IV) (<5 doses)', -222, "Nutrition","Infusions","TPN"],   
                [ -391000000, 'Histidine (IV) (<5 doses)', -222, "Nutrition","Infusions","TPN"],   
                [ -391000000, 'Glycine (IV) (<5 doses)', -222, "Nutrition","Infusions","TPN"],   
                [ -391000000, 'Glucose (IV) (<5 doses)', -222, "Nutrition","Infusions","TPN"],   
                [ -391000000, 'Arginine (IV) (<5 doses)', -222, "Nutrition","Infusions","TPN"],   
                [ -391000000, 'Alanine (IV) (<5 doses)', -222, "Nutrition","Infusions","TPN"],   
            ];
        actualData = DBUtil.execute(testQuery);
        self.assertEqualTable( expectedData, actualData );


    def test_dataConversion_denormalized(self):
        # Run the data conversion on the same data and look for expected records
        log.debug("Run the conversion process...");
        convOptions = ConversionOptions();
        convOptions.startDate = TEST_START_DATE;
        convOptions.normalizeMixtures = False;
        convOptions.maxMixtureCount = 5;
        convOptions.doseCountLimit = 5;
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
                cic.source_table = 'stride_order_med'
            order by
                pi.external_id, ci.external_id
            """;
        expectedData = \
            [
                [ -421032269, 2968778, 333, "Med (IV)", -96559, "MED-96559", "Piperacillin-Tazobactam (IV)", datetime(2112,2,8,11,17) ],

                #[ -418436155, 1607844, "Med (PR)", -3001, "RXCUI-3001", "Bisacodyl (PR)", datetime(2111,12,20,0,40) ], # Skip PRNs
                [ -418436145, 1607844, 222, "Med (PR)", -3001, "RXCUI-3001", "Bisacodyl (PR)", datetime(2111,12,22,0,40) ],
                [ -418063010, 3032765, 111, "Med (PO)", -4001, "RXCUI-4001", "Prednisone (PO)", datetime(2111,12,12,8,56) ],
                [ -418062652, 3036488, 555, "Med (IV)", -5007, "MED-5007 (<5)", "METOPROLOL TARTRATE 5 MG/5 ML IV SOLN (<5 doses)", datetime(2111,12,12,8,30) ],
                [ -418062352, 3016488, 666, "Med (IV)", -5007, "MED-5007 (<5)", "METOPROLOL TARTRATE 5 MG/5 ML IV SOLN (<5 doses)", datetime(2111,12,13,8,30) ],
                [ -418013851, -2429057, 444, "Med (PO)", -2001, "RXCUI-2001", "Famotidine (PO)", datetime(2111,12,10,19,10) ],
                [ -418011851, -2429057, 444, "Med (PO)", -2001, "RXCUI-2001", "Famotidine (PO)", datetime(2111,12,10,19,9) ],
                [ -414321352, 3036588, 777, "Med (IV)", -5007, "MED-5007 (<5)", "METOPROLOL TARTRATE 5 MG/5 ML IV SOLN (<5 doses)", datetime(2111,12,14,8,30) ],

                # Simple mixture with different dosing counts
                [ -395900000, 1234567, 888, "Med (IV)", -20481, "RXCUI-20481 (<5)", "Cefepime (IV) (<5 doses)", datetime(2111, 1, 2, 3, 0)], 
                [ -395800000, 1234567, 888, "Med (IV)", -20481, "RXCUI-20481", "Cefepime (IV)", datetime(2111, 1,10, 3, 0)], 
                [ -395700000, 1234567, 888, "Med (IV)", -20481, "RXCUI-20481", "Cefepime (IV)", datetime(2111, 3,10, 3, 0)], 

                # IVF Mixture, composite ingredient description
                [ -392000000, 1234567, 888, "Med (IV)", -888699365, "RXCUI-4850,-8591,-9863 (<5)", "Glucose-Potassium Chloride-Sodium Chloride (IV) (<5 doses)", datetime(2111, 4, 1, 3, 0)], 

                # Mini mixture.  Too many components, just use summary description
                [ -391000000, 1234567, 888, "Med (IV)", -540000, "MED-540000 (<5)", "Mini TPN (<5 doses)", datetime(2111, 4, 2, 3, 0)], # Still aggregated because breaking up into component amino acids results in too many

                # Complex mixture
                [ -390000000, 1234567, 888, "Med (IV)", -550000, "MED-550000", "TPN Adult", datetime(2111, 5, 2, 3, 0)], 

            ];
        actualData = DBUtil.execute(testQuery);
        self.assertEqualTable( expectedData, actualData );


        # Query for orderset links
        testQuery = \
            """
            select 
                pi.external_id,
                ci.description,
                ic.external_id,
                ic.name,
                ic.section,
                ic.subgroup
            from
                patient_item as pi,
                clinical_item as ci,
                clinical_item_category as cic,
                patient_item_collection_link as picl,
                item_collection_item as ici,
                item_collection as ic
            where
                pi.clinical_item_id = ci.clinical_item_id and
                ci.clinical_item_category_id = cic.clinical_item_category_id and
                cic.source_table = 'stride_order_med' and
                pi.patient_item_id = picl.patient_item_id and
                picl.item_collection_item_id = ici.item_collection_item_id and
                ici.item_collection_id = ic.item_collection_id
            order by
                pi.external_id, ci.external_id
            """;
        expectedData = \
            [
                [ -421032269, "Piperacillin-Tazobactam (IV)", -111,"General Admit","Medications","Antibiotics"],
                [ -418436145, "Bisacodyl (PR)", -111,"General Admit","Medications","Stool Softeners"],

                # Mini-Mix
                [ -391000000, 'Mini TPN (<5 doses)', -222, "Nutrition","Infusions","TPN"],   
            ];
        actualData = DBUtil.execute(testQuery);
        self.assertEqualTable( expectedData, actualData );

    def test_dataConversion_maxMixtureCount(self):
        # Run the data conversion on the same data and look for expected records
        log.debug("Run the conversion process...");
        convOptions = ConversionOptions();
        convOptions.startDate = TEST_START_DATE;
        convOptions.normalizeMixtures = False;
        convOptions.maxMixtureCount = 2;
        convOptions.doseCountLimit = 5;
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
                cic.source_table = 'stride_order_med'
            order by
                pi.external_id, ci.external_id
            """;
        expectedData = \
            [
                [ -421032269, 2968778, 333, "Med (IV)", -96559, "MED-96559", "Piperacillin-Tazobactam (IV)", datetime(2112,2,8,11,17) ],

                #[ -418436155, 1607844, "Med (PR)", -3001, "RXCUI-3001", "Bisacodyl (PR)", datetime(2111,12,20,0,40) ], # Skip PRNs
                [ -418436145, 1607844, 222, "Med (PR)", -3001, "RXCUI-3001", "Bisacodyl (PR)", datetime(2111,12,22,0,40) ],
                [ -418063010, 3032765, 111, "Med (PO)", -4001, "RXCUI-4001", "Prednisone (PO)", datetime(2111,12,12,8,56) ],
                [ -418062652, 3036488, 555, "Med (IV)", -5007, "MED-5007 (<5)", "METOPROLOL TARTRATE 5 MG/5 ML IV SOLN (<5 doses)", datetime(2111,12,12,8,30) ],
                [ -418062352, 3016488, 666, "Med (IV)", -5007, "MED-5007 (<5)", "METOPROLOL TARTRATE 5 MG/5 ML IV SOLN (<5 doses)", datetime(2111,12,13,8,30) ],
                [ -418013851, -2429057, 444, "Med (PO)", -2001, "RXCUI-2001", "Famotidine (PO)", datetime(2111,12,10,19,10) ],
                [ -418011851, -2429057, 444, "Med (PO)", -2001, "RXCUI-2001", "Famotidine (PO)", datetime(2111,12,10,19,9) ],
                [ -414321352, 3036588, 777, "Med (IV)", -5007, "MED-5007 (<5)", "METOPROLOL TARTRATE 5 MG/5 ML IV SOLN (<5 doses)", datetime(2111,12,14,8,30) ],

                # Simple mixture with different dosing counts
                [ -395900000, 1234567, 888, "Med (IV)", -20481, "RXCUI-20481 (<5)", "Cefepime (IV) (<5 doses)", datetime(2111, 1, 2, 3, 0)], 
                [ -395800000, 1234567, 888, "Med (IV)", -20481, "RXCUI-20481", "Cefepime (IV)", datetime(2111, 1,10, 3, 0)], 
                [ -395700000, 1234567, 888, "Med (IV)", -20481, "RXCUI-20481", "Cefepime (IV)", datetime(2111, 3,10, 3, 0)], 

                # IVF Mixture, composite ingredient description
                [ -392000000, 1234567, 888, "Med (IV)", -530000, "MED-530000 (<5)", "IVF Mix (<5 doses)", datetime(2111, 4, 1, 3, 0)], 

                # Mini mixture.  Too many components, just use summary description
                [ -391000000, 1234567, 888, "Med (IV)", -540000, "MED-540000 (<5)", "Mini TPN (<5 doses)", datetime(2111, 4, 2, 3, 0)], # Still aggregated because breaking up into component amino acids results in too many

                # Complex mixture
                [ -390000000, 1234567, 888, "Med (IV)", -550000, "MED-550000", "TPN Adult", datetime(2111, 5, 2, 3, 0)], 

            ];
        actualData = DBUtil.execute(testQuery);
   
        self.assertEqualTable( expectedData, actualData );

def suite():
    """Returns the suite of tests to run for this test class / module.
    Use unittest.makeSuite methods which simply extracts all of the
    methods for the given class whose name starts with "test"
    """
    suite = unittest.TestSuite();
    #suite.addTest(TestSTRIDEOrderMedConversion("test_incColNamesAndTypeCodes"));
    #suite.addTest(TestSTRIDEOrderMedConversion("test_insertFile_skipErrors"));
    #suite.addTest(TestSTRIDEOrderMedConversion('test_executeIterator'));
    #suite.addTest(TestSTRIDEOrderMedConversion('test_dataConversion_maxMixtureCount'));
    suite.addTest(unittest.makeSuite(TestSTRIDEOrderMedConversion));
    
    return suite;
    
if __name__=="__main__":
    unittest.TextTestRunner(verbosity=RUNNER_VERBOSITY).run(suite())
