#!/usr/bin/python
"""
Class for transforming STRIDE dataset into patient event logs.

Primary result tables:
* clinical_item_category
* clinical_item
* patient_item

All general postprocessing on these tables should happen here.
"""

import logging
import os
import subprocess
from optparse import OptionParser
import sys
from medinfo.db import DBUtil
from medinfo.cpoe.DataManager import DataManager
from medinfo.common.Util import log, ProgressDots, stdOpen
from LocalEnv import PATH_TO_CDSS

# Switch off the analysis status for any clinical item that occurs for fewer than this percent of patient records
MINIMUM_PATIENT_SUPPORT = 0.01; # 1%
# Likewise for any clinical item that occurs for fewer than this fraction of the total number of patient items
MINIMUM_PATIENT_ITEM_SUPPORT = 0.000001;


class CDSSDataLoader:
    # The order here is significant. Some tables (e.g. clinical_item),
    # reference other tables via  FOREIGN KEY (e.g. clinical_item_category),
    # so tables must be defined in order of their dependencies.
    CDSS_PSQL_TABLES = [
        'clinical_item_category',
        'clinical_item',
        'order_result_stat',
        'patient_item',
        'item_collection',
        'collection_type',
        'item_collection_item',
        'patient_item_collection_link',
        'clinical_item_link',
        'backup_link_patient_item',
        'data_cache',
        'clinical_item_association'
    ]

    STRIDE_TABLE_TRANSFORMER_MAP = {
        'stride_patient': 'medinfo.dataconversion.STRIDEDemographicsConversion',
        'stride_preadmit_med': 'medinfo.dataconversion.STRIDEPreAdmitMedConversion',
        'stride_dx_list': 'medinfo.dataconversion.STRIDEDxListConversion',
        'stride_treatment_team': 'medinfo.dataconversion.STRIDETreatmentTeamConversion',
        'stride_order_med': 'medinfo.dataconversion.STRIDEOrderMedConversion',
        'stride_order_proc': 'medinfo.dataconversion.STRIDEOrderProcConversion',
        'stride_order_results': 'medinfo.dataconversion.STRIDEOrderResultsConversion'
    }

    @staticmethod
    def load_CDSS_from_stride():
        CDSSDataLoader.clear_CDSS_psql_tables()
        CDSSDataLoader.build_CDSS_psql_schemata()
        CDSSDataLoader.build_CDSS_tables()
        # CDSSDataLoader.process_stride_psql_db()

    @staticmethod
    def fetch_scripts_dir():
        # CDSS/medinfo/
        return os.path.join(PATH_TO_CDSS, 'scripts')

    @staticmethod
    def fetch_CDSS_dir():
        # CDSS/scripts/CDSS/
        return os.path.join(CDSSDataLoader.fetch_scripts_dir(), 'CDSS')

    @staticmethod
    def fetch_psql_dir():
        # CDSS/scripts/CDSS/psql/
        return os.path.join(CDSSDataLoader.fetch_CDSS_dir(), 'psql')

    @staticmethod
    def fetch_psql_schemata_dir():
        # CDSS/scripts/CDSS/psql/schemata/
        return os.path.join(CDSSDataLoader.fetch_psql_dir(), 'schemata')

    @staticmethod
    def fetch_psql_indices_dir():
        # CDSS/scripts/CDSS/psql/indices
        return os.path.join(CDSSDataLoader.fetch_psql_dir(), 'indices')

    @staticmethod
    def clear_CDSS_psql_tables():
        log.info('Clearing stride psql tables...')
        for psql_table in CDSSDataLoader.CDSS_PSQL_TABLES:
            log.debug('dropping table %s...' % psql_table)
            DBUtil.execute("DROP TABLE IF EXISTS %s CASCADE;" % psql_table)

    @staticmethod
    def build_CDSS_psql_schemata():
        schemata_dir = CDSSDataLoader.fetch_psql_schemata_dir()
        for psql_table in CDSSDataLoader.CDSS_PSQL_TABLES:
            schema_file_name = '%s.schema.sql' % psql_table
            schema_path = os.path.join(schemata_dir, schema_file_name)
            with open(schema_path, 'r') as schema_file:
                DBUtil.runDBScript(schema_file)

    @staticmethod
    def transform_STRIDE_source_table(stride_source_table):
        # Get module for doing data conversion.
        transformer = CDSSDataLoader.STRIDE_TABLE_TRANSFORMER_MAP[stride_source_table]

        # Build command.
        if stride_source_table == 'stride_patient':
            argv = ['python', '-m', transformer]
        elif stride_source_table == 'stride_preadmit_med':
            argv = ['python', '-m', transformer, '-m', '5', '-s', '2008-01-01']
        elif stride_source_table == 'stride_order_med':
            argv = ['python', '-m', transformer, '-m', '5', '-d', '5', '-s', '2008-01-01']
        elif stride_source_table == 'stride_treatment_team':
            argv = ['python', '-m', transformer, '-a', '-s', '2008-01-01']
        else:
            argv = ['python', '-m', transformer, '-a', '-s', '2008-01-01']

        # Call command.
        log_file = stdOpen('%s.log' % ('_'.join(argv)), 'w')
        subprocess.call(argv, stderr=log_file)

    @staticmethod
    def process_CDSS_psql_db():
        CDSSDataLoader.selectively_deactivate_clinical_item_analysis()
        CDSSDataLoader.selectively_deactivate_clinical_item_recommendation()
        CDSSDataLoader.define_composite_clinical_items()
        CDSSDataLoader.define_virtual_clinical_items()
        CDSSDataLoader.add_clinical_item_synonyms()
        CDSSDataLoader.define_possible_clinical_outcomes()

    @staticmethod
    def selectively_deactivate_clinical_item_analysis():
        log.info('Selectively deactivating clinical item analysis...')
        # Certain clinical items are rote with low or ambiguous information value.
        #   For example, orders for Full Code, Regular Diet, Check and Report Vital Signs, and many "Nursing Orders" that don't include relevant detail
        # Manually prevent analysis for these items.
        analysis_deactivation_command = \
            """
            UPDATE clinical_item
            SET analysis_status = 0
            WHERE name IN (
                'RXCUI854932', 'RXCUI854934', 'RXCUI854936', 'RXCUI854938', # Pneumococcal vaccine components
                'RXCUI854940', 'RXCUI854942', 'RXCUI854944', 'RXCUI854946',
                'RXCUI854948', 'RXCUI854950', 'RXCUI854952', 'RXCUI854954',
                'RXCUI854956', 'RXCUI854958', 'RXCUI854960', 'RXCUI854962',
                'RXCUI854964', 'RXCUI854966', 'RXCUI854968', 'RXCUI854970',
                'RXCUI854972', 'RXCUI854974', 'RXCUI854932', 'RXCUI854934',
                'RXCUI854936', 'RXCUI854938', 'RXCUI854940', 'RXCUI854942',
                'RXCUI854944', 'RXCUI854946', 'RXCUI854948', 'RXCUI854950',
                'RXCUI854952', 'RXCUI854954', 'RXCUI854956', 'RXCUI854958',
                'RXCUI854960', 'RXCUI854962', 'RXCUI854964', 'RXCUI854966',
                'RXCUI854968', 'RXCUI854970', 'RXCUI854972', 'RXCUI854974',
                '146535', 'LABSPR', 'NUR1940', 'NUR1025', 'NUR194000',
                'NUR350', 'NURSE 1500', '146541', '146543', 'COD2', 'DIET990',
                'TRN2', 'POC14', 'LABPOCGLU', '146537'
            );
            """
        DBUtil.execute(analysis_deactivation_command)

        # Remove variants of TPN that are distracting and have a bizarrely long
        # name when amino acid ingredients are unraveled.
        analysis_deactivation_command = \
            """
            UPDATE clinical_item
            SET analysis_status = 0
            WHERE description LIKE 'Alanine-Arginine%%';
            """
        DBUtil.execute(analysis_deactivation_command)

        # Transfusion Blood Product: Not even clear what these are orders for,
        # since there are separate orders for RBCs, platelets, and nursing to
        # transfuse them. By coincidence, total count appears to be ~2x sum of
        # all other blood bank orders.
        analysis_deactivation_command = \
            """
            UPDATE clinical_item
            SET analysis_status = 0
            WHERE name IN (
                'LABTSLIP', 'LABTBP', 'LABTBP9', 'LABTBP10', 'LABTBP11',
                'LABTBP12', 'LABTBP13', 'LABTBP14', 'LABTBP15', 'LABTBP16',
                'LABTBP17', 'LABTBP18', 'LABTBP1', 'LABTBP19', 'LABTBP20',
                'LABTBP21', 'LABTBP22', 'LABTBP23', 'LABTBP24', 'LABTBP25',
                'LABTBP26', 'LABTBP27', 'LABTBP28', 'LABTBP2', 'LABTBP29',
                'LABTBP30', 'LABTBP31', 'LABTBP32', 'LABTBP33', 'LABTBP34',
                'LABTBP35', 'LABTBP36', 'LABTBP37', 'LABTBP38', 'LABTBP3',
                'LABTBP39', 'LABTBP40', 'LABTBP41', 'LABTBP42', 'LABTBP43',
                'LABTBP44', 'LABTBP45', 'LABTBP46', 'LABTBP47', 'LABTBP48',
                'LABTBP4', 'LABTBP49', 'LABTBP50', 'LABTBP51', 'LABTBP52',
                'LABTBP53', 'LABTBP54', 'LABTBP55', 'LABTBP56', 'LABTBP57',
                'LABTBP58', 'LABTBP5', 'LABTBP59', 'LABTBP60', 'LABTBP61',
                'LABTBP62', 'LABTBP63', 'LABTBP64', 'LABTBP65', 'LABTBP66',
                'LABTBP67', 'LABTBP68', 'LABTBP6', 'LABTBP69', 'LABTBP70',
                'LABTBP71', 'LABTBP72', 'LABTBP73', 'LABTBP74', 'LABTBP75',
                'LABTBP76', 'LABTBP77', 'LABTBP78', 'LABTBP7', 'LABTBP79',
                'LABTBP80', 'LABTBP81', 'LABTBP82', 'LABTBP83', 'LABTBP84',
                'LABTBP85', 'LABTBP86', 'LABTBP87', 'LABTBP88', 'LABTBP8',
                'LABTBP89', 'LABTBP90', 'LABTBP91', 'LABTBP92', 'LABTBP93'
            );
            """
        DBUtil.execute(analysis_deactivation_command)

        # Deactivate analysis on result comments.
        # Could try simplifying with "WHERE DESCRIPTION ~* 'comment'"
        analysis_deactivation_command = \
            """
            UPDATE clinical_item
            SET analysis_status = 0
            WHERE NAME IN (
                'BM15CO(Result)', 'UCMT(Result)', 'DOACOM(Result)',
                'PCCOM(Result)', 'SREQ(Result)', 'SREQ(Result)',
                'REVUE(Result)', 'HIACOM(Result)', 'PTCMT(Result)',
                'LEICMT(Result)', 'PF4COM(Result)', 'DIMCOM(Result)',
                'CEPCM(Result)', 'FCMT(Result)', 'SCMT(Result)',
                'CCMT(Result)', 'COM(Result)', 'CTRXNW(Result)',
                '11200R(Result)', 'PLTFCM(Result)', 'QBCRCM(Result)',
                'B2GPCM(Result)', 'DHTLV(Result)', 'ATHCT(Result)',
                'RFCOM(Result)', 'BMBRCT(Result)', 'QBMBRC(Result)',
                'RSVCOM(Result)', 'KITCO(Result)', 'T15CO(Result)',
                'BCRCMT(Result)', 'BCRKCM(Result)', 'BMTCMT(Result)',
                'MTHCMT(Result)', 'MGMCO(Result)', 'SREQ(InRange)',
                'TEGCOM(Result)', 'BMBCMT(Result)', 'BSQCO(Result)',
                'BM11CT(Result)', 'SREQ(Result)', 'VWFPIC(Result)',
                'CEBCM(Result)', 'YIFB2(Result)', 'YPLAB2(Result)',
                'BM14CT(Result)', 'YUOPCO(Result)', 'YFCHY6(Result)',
                'YUBZCO(Result)', 'FBCMT(Result)', 'PPPCOM(Result)',
                'CF32CM(Result)', 'YUMECO(Result)', 'BCMT(Result)',
                'YSTNCO(Result)', 'TCMT(Result)', '11152R(Result)',
                'TMSICO(Result)', 'UCMT(Result)', 'JAKCO(Result)',
                'YHISS5(Result)', 'YHISU5(Result)', 'T11CT(Result)',
                '11996R(Result)', 'KITCO(Result)', 'YVB1W2(Result)',
                'CTSMIS(Result)', 'NJAKCO(Result)', 'T14CMT(Result)',
                'YLCFA9(Result)', 'QFBCRC(Result)', 'TT15CO(Result)',
                'YHISC5(Result)', 'TTCCMT(Result)', 'TBCCMT(Result)',
                'NBTCOM(Result)', 'NBTCBC(Result)', 'FT15CO(Result)',
                'FTCMT(Result)', 'SREQ(Abnormal)', '9078R(Result)',
                '9260R(Result)', 'MGMCOB(Result)', '9584R(Result)',
                '9574R(Result)', '9464R(Result)', '9450R(Result)',
                '12291R(Result)', '9433R(Result)', '9420R(Result)',
                '9181R(Result)', '12486R(Result)', '12473R(Result)',
                '9280R(Result)', '12255R(Result)', '12468R(Result)',
                '12461R(Result)', 'TBCRCT(Result)', '9233R(Result)',
                'HITI2(Result)', '9120R(Result)', 'BGSPR(Result)',
                'BGSPRC(Result)', 'HCHCO(Result)', '9404R(Result)',
                '9391R(Result)', '9207R(Result)', 'ABID2E(Result)',
                'PEDCOM(Result)', '9344R(Result)', '9586R(Result)',
                '9582R(Result)', '9374R(Result)', '9361R(Result)',
                '9099R(Result)', 'PMCOMMENT(Result)'
            );
            """
        DBUtil.execute(analysis_deactivation_command)

        # Normal / Non-Specific Results
        analysis_deactivation_command = \
            """
            UPDATE clinical_item
            SET analysis_status = 0
            WHERE name LIKE '%%(InRange)' OR name LIKE '%%(Result)';
            """
        DBUtil.execute(analysis_deactivation_command)

        # Skip analysis for very rare orders that excessively increase
        # association item list without adding much value. Decide the threshold
        # for "rare" on the fly. Goal is to exclude clinical items such that
        # 95%+ of data is still represented, but greatly reduce vocabulary size. 

        # As a rough heuristic, ignore clinical_items which represent < 0.0001% of all patient items.
        threshold_query = \
            """
            SELECT ROUND(%s * COUNT(patient_item_id)) AS threshold
            FROM patient_item;
            """ % MINIMUM_PATIENT_ITEM_SUPPORT;
        results = DBUtil.execute(threshold_query)
        threshold = results[0][0]
        analysis_deactivation_command = \
            """
            UPDATE clinical_item
            SET analysis_status = 0
            WHERE clinical_item_id IN (
                SELECT clinical_item_id
                FROM patient_item
                GROUP BY clinical_item_id
                HAVING COUNT(patient_item_id) < %s
            );
            """ % threshold
        DBUtil.execute(analysis_deactivation_command)

        # As another rough heuristic, ignore clinical_items which occur for < 1% of all patient records.
        threshold_query = \
            """
            SELECT ROUND(%s * COUNT(distinct patient_id)) AS threshold
            FROM patient_item;
            """ % MINIMUM_PATIENT_SUPPORT;
        results = DBUtil.execute(threshold_query)
        threshold = results[0][0]
        analysis_deactivation_command = \
            """
            UPDATE clinical_item
            SET analysis_status = 0
            WHERE clinical_item_id IN (
                SELECT clinical_item_id
                FROM patient_item
                GROUP BY clinical_item_id
                HAVING COUNT(distinct patient_id) < %s
            );
            """ % threshold
        DBUtil.execute(analysis_deactivation_command)


    @staticmethod
    def selectively_deactivate_clinical_item_recommendation():
        log.info('Selectively deactivating clinical item recommendations...')
        # Certain categories of clinical items don't really make sense to
        # recommend as part of CDSS. Flip the default_recommend bit for these
        # items.

        # Exclude categories including:
        #   source_table    description
        #   order_proc  Nursing
        #   order_proc  Transport
        #   order_proc  BB Call Slip
        #   order_proc  None
        #   order_proc  Pharmacy Supplies
        #   order_proc  Diet Communication
        #   order_proc  Transfer
        #   order_proc  Admission
        #   order_proc  Discharge
        recommendation_deactivation_command = \
            """
            UPDATE clinical_item_category
            SET default_recommend = 0
            WHERE description IN (
                'Nursing', 'Transfer', 'Admission', 'Transport',
                'BB Call Slip', 'None', 'Pharmacy Supplies',
                'Diet Communication', 'Discharge'
            );
            """
        DBUtil.execute(recommendation_deactivation_command)

        # Note: "recommending" diagnoses might actually be useful for a
        # diagnostic tool, but for now exclude the following categories.
        #   source_table    description
        #   stride_order_results    Lab Result
        #   stride_order_results    Point of Care Testing Result
        #   stride_order_results    HIV Lab Restricted Result
        #   stride_order_results    HIV Lab Non-Restricted Result
        #   stride_preadmit_med Preadmit Med
        #   stride_treatment_team   Treatment Team
        #   stride_patient  Demographics
        #	stride_dx_list    Diagnosis (PROBLEM_LIST)
        #	stride_dx_list    Diagnosis (ADMIT_DX)
        recommendation_deactivation_command = \
            """
            UPDATE clinical_item_category
            SET default_recommend = 0
            WHERE source_table IN (
                'stride_order_results',
                'stride_preadmit_med',
                'stride_treatment_team',
                'stride_patient',
                'stride_dx_list'
            );
            """
        DBUtil.execute(recommendation_deactivation_command)

        # Minimize subsequent confusion by propagating category level default_recommend status to individual clinical_items
        recommendation_deactivation_command = \
            """
            UPDATE clinical_item
            SET default_recommend = 0
            WHERE clinical_item_category_id IN
            (   SELECT clinical_item_category_id
                FROM clinical_item_category
                WHERE default_recommend = 0
            );
            """
        DBUtil.execute(recommendation_deactivation_command)


    @staticmethod
    def define_composite_clinical_items():
        log.info('Defining composite clinical items...')
        # Composite certain outcome measures, for example, ICU interventions
        # (sub-categorization based on vasopressors).

        # VASOACTIVE INFUSION
        # Category = Med (Intravenous)
        intravenous_med_cic_id_query = \
            """
            SELECT clinical_item_category_id
            FROM clinical_item_category
            WHERE description = 'Med (Intravenous)';
            """
        results = DBUtil.execute(intravenous_med_cic_id_query)
        intravenous_med_cic_id = results[0][0]
        #   clinical_item_category.description  name    description
        #   Med (Intravenous)   RXCUI3616   Dobutamine*
        #   Med (Intravenous)   RXCUI3628   Dopamine*
        #   Med (Intravenous)   RXCUI3992   Epinephrine*
        #   Med (Intravenous)   RXCUI7512   Norepinephrine*
        #   Med (Intravenous)   RXCUI8163   Phenylephrine*
        #   Med (Intravenous)   MED224819   VASOPRESSIN*
        vasoactive_infusion_id_query = \
            """
            SELECT clinical_item_id
            FROM clinical_item
            WHERE
                clinical_item_category_id = %s AND
                name IN (
                    'RXCUI3616', 'RXCUI3628', 'RXCUI3992', 'RXCUI7512',
                    'RXCUI8163', 'MED224819'
                );
            """ % intravenous_med_cic_id
        results = DBUtil.execute(vasoactive_infusion_id_query)
        vasoactive_infusion_ci_ids = [result[0] for result in results]

        CDSSDataLoader.build_composite_clinical_item(vasoactive_infusion_ci_ids, \
            'AnyVasoactive', 'Any Vasoactive Infusion', intravenous_med_cic_id)

        # CONTINUOUS RENAL REPLACEMENT THERAPY (CRRT)
        # CaCl infusion and IV Citrate are very closely correlated to CRRT use,
        # but are rarely used in other scenarios.
        # Category = Med (CRRT)
        crrt_cic_id_query = \
            """
            SELECT clinical_item_category_id
            FROM clinical_item_category
            WHERE description = 'Med (CRRT)';
            """
        results = DBUtil.execute(crrt_cic_id_query)
        crrt_cic_id = results[0][0]
        #   clinical_item_category.description  name    description
        #   Med (CRRT)  MED205894   BICARB DIALY*
        #   Med (CRRT)  RXCUI36676  Sodium Bicarbonate*
        #   Med (CRRT)  RXCUI205894,36676   BICARB DIALY-Sodium Bicarbonate (CRRT)
        #   Med (CRRT)  MED500028   CRRT*
        #   Med (CRRT)  RXCUI9863   Sodium Chloride*
        #   Med (CRRT)  RXCUI1908   Calcium Gluconate*
        #   Med (CRRT)  RXCUI205894,11295   BICARB DIALY SOLN HEMODIAL SOLN-Water (CRRT)
        #   Nursing NUR4084 CONT RENAL REPLACEMENT THERAPY
        crrt_ci_id_query = \
            """
            SELECT clinical_item_id
            FROM clinical_item
            WHERE
                (
                    clinical_item_category_id = %s AND
                    name IN (
                        'MED205894', 'RXCUI36676', 'RXCUI205894,36676',
                        'MED500028', 'RXCUI9863', 'RXCUI1908',
                        'RXCUI205894,11295'
                    )
                ) OR
                (
                    name = 'NUR4084'
                );
            """ % crrt_cic_id
        results = DBUtil.execute(crrt_ci_id_query)
        crrt_ci_ids = [result[0] for result in results]

        CDSSDataLoader.build_composite_clinical_item(crrt_ci_ids, 'AnyCRRT', \
            'Continuous Renal Replacement Therapy Components', crrt_cic_id)

        # VENTILATOR
        # Category = Respiratory Care
        respiratory_cic_id_query = \
            """
            SELECT clinical_item_category_id
            FROM clinical_item_category
            WHERE description = 'Respiratory Care';
            """
        results = DBUtil.execute(respiratory_cic_id_query)
        respiratory_cic_id = results[0][0]
        #   clinical_item_category.description   name    description
        #   Respiratory Care  RT75    RESP - EXTUBATION
        #   Respiratory Care    RT104   RESP - VENTILATOR SETTINGS
        #   Respiratory Care    RT97	RESP - WEAN VENTILATOR
        #   Respiratory Care    RT90	RESP - SPONTANEOUS BREATHING TRIAL
        #   Respiratory Care    RT130	RESP - REPOSITION ET TUBE
        #   Respiratory Care    RT88	RESP - HIGH FREQUENCY OSCILLATORY VENTILATION
        #   Respiratory Care    RT997	RESP - LUNG PROTECTIVE VENTILATION PROTOCOL
        #   Respiratory Care    RT202	RESP - MONITOR, PERFORM VENTILATOR AND PATIENT ASSESSMENT
        #   Respiratory Care    RT91	RESP - SIMV/PRESSURE SUPPORT
        ventilator_ci_id_query = \
            """
            SELECT clinical_item_id
            FROM clinical_item
            WHERE
                clinical_item_category_id = %s AND
                name IN (
                'RT75', 'RT104', 'RT97', 'RT90', 'RT130', 'RT88', 'RT997',
                'RT202', 'RT91'
                );
            """ % respiratory_cic_id
        results = DBUtil.execute(ventilator_ci_id_query)
        ventilator_ci_ids = [result[0] for result in results]

        CDSSDataLoader.build_composite_clinical_item(ventilator_ci_ids, \
            'AnyVentilator', 'Ventilator Orders', respiratory_cic_id)

        # ICU LIFE SUPPORT
        # Can populate leaf linked items directly, or link to the above
        # intermediate nodes and allow inheritance to pickup the rest.
        # Category = Procedures
        procedures_cic_id_query = \
            """
            SELECT clinical_item_category_id
            FROM clinical_item_category
            WHERE description = 'Procedures';
            """
        results = DBUtil.execute(procedures_cic_id_query)
        procedures_cic_id = results[0][0]
        # Build from the previously defined composite items.
        icu_life_support_id_query = \
            """
            SELECT clinical_item_id
            FROM clinical_item
            WHERE name IN (
                'AnyVasoactive',
                'AnyCRRT',
                'AnyVentilator'
            );
            """
        results = DBUtil.execute(icu_life_support_id_query)
        icu_life_support_ci_ids = [result[0] for result in results]
        CDSSDataLoader.build_composite_clinical_item(icu_life_support_ci_ids, \
            'AnyICULifeSupport', \
            'ICU Life Support (Vasoactives, Ventilator, CRRT)', \
            procedures_cic_id)

        # ICU CARE
        # Any ICU specific (or highly correlated) orders to capture events
        # occuring in the ICU, including other drips, nursing orders, etc.
        # Note that some medications have multiple multiple medications with
        # the same name. Use the descrition to disambiguate.
        med_none_cic_id_query = \
            """
            SELECT clinical_item_category_id
            FROM clinical_item_category
            WHERE description = 'Med (None)';
            """
        results = DBUtil.execute(med_none_cic_id_query)
        med_none_cic_id = results[0][0]
        #   name    description
        #   MED530008	NITROPRUSSIDE IV INFUSION
        #   RXCUI8782	Propofol (Intravenous)
        #   MED530025	DEXMEDETOMIDINE IV INFUSION
        #   MED530004	MIDAZOLAM 50 MG IN D5W 100 ML IV INFUSION
        #   RXCUI8163	Phenylephrine (Intravenous)
        #   RXCUI114200	Citrate (Intravenous)
        #   MED530120	HYDROMORPHONE 10 MG IN 100 ML IV INFUSION (SHC)
        #   RXCUI36676	Sodium Bicarbonate (CRRT)
        #   MED530007	VECURONIUM IV INFUSION
        #   RXCUI4177	Etomidate (Intravenous)
        #   RXCUI10154	Succinylcholine (Intravenous)
        #   MED520130	CALCIUM CHLORIDE 8 G/1000 ML IV INFUSION
        #   MED530009	CISATRACURIUM IV INFUSION
        #   MED530003	FENTANYL  10 MCG/ML IV INFUSION
        #   MED530111	MIDAZOLAM 100 MG IN D5W 100 ML IV INFUSION
        #   MED530114	MILRINONE CUSTOM IV INFUSION
        #   MED530050	DOBUTAMINE IV INFUSION CUSTOM MIXTURE
        #   MED530046	HYDROMORPHONE IV INFUSION
        #   MED530112	MIDAZOLAM IV INFUSION (CUSTOM)
        #   NUR2254	MONITOR PULMONARY ARTERY CATHETER
        #   RT106	RESP - NITRIC OXIDE VENT
        #   NUR2247	MONITOR CENTRAL LINE
        #   NUR1942	EXTERNAL VENTRICULAR DRAIN CARE
        #   NUR1528	MONITOR ARTERIAL LINE
        #   NUR30020	RASS SEDATION ASSESSMENT
        #   NUR1599	MONITOR CARDIAC ASSIST DEVICE
        #   NUR1591	OROGASTRIC TUBE
        #   NUR1529	MONITOR CO/CI
        #   NUR2999	MONITOR SCV02
        #   AnyICULifeSupport	ICU Life Support (Vasopressors,Ventilator,CRRT)
        icu_ci_id_query = \
            """
            SELECT clinical_item_id
            FROM clinical_item
            WHERE
                (
                    name = 'RXCUI8163' AND
                    description = 'Phenylephrine (Intravenous)'
                ) OR
                (
                    name = 'RXCUI36676' AND
                    description = 'Sodium Bicarbonate (CRRT)'
                ) OR
                (
                    name = 'RXCUI10154' AND
                    description = 'Succinylcholine (Intravenous)'
                ) OR
                (
                    name = 'MED530008' AND
                    description = 'NITROPRUSSIDE IV INFUSION'
                ) OR
                name IN (
                    'RXCUI8782', 'MED530025', 'MED530004',
                    'RXCUI114200', 'MED530120', 'MED530007', 'RXCUI4177',
                    'MED520130', 'MED530009', 'MED530003', 'MED530111',
                    'MED530114', 'MED530050', 'MED530046', 'MED530112',
                    'NUR2254', 'RT106', 'NUR2247', 'NUR1942', 'NUR1528',
                    'NUR30020', 'NUR1599', 'NUR1591', 'NUR1529', 'NUR2999',
                    'AnyICULifeSupport'
                    );
            """
        results = DBUtil.execute(icu_ci_id_query)
        icu_ci_ids = [result[0] for result in results]
        CDSSDataLoader.build_composite_clinical_item(icu_ci_ids, 'ICUOrders', \
            'ICU Specific/Correlated Orders', med_none_cic_id)

        # DNR / NON-FULL CODE ORDERS
        # Category = Code Status
        code_status_cic_id_query = \
            """
            SELECT clinical_item_category_id
            FROM clinical_item_category
            WHERE description = 'Code Status';
            """
        results = DBUtil.execute(code_status_cic_id_query)
        code_status_cic_id = results[0][0]
        #   name    description
        #   COD1	DNR
        #   COD7	DNR/C
        #   COD5	DNR/DNE
        #   COD1	DNR/DNI
        dnr_ci_id_query = \
            """
            SELECT clinical_item_id
            FROM clinical_item
            WHERE name IN (
                'COD1', 'COD5', 'COD7'
            );
            """
        results = DBUtil.execute(dnr_ci_id_query)
        dnr_ci_ids = [result[0] for result in results]
        CDSSDataLoader.build_composite_clinical_item(dnr_ci_ids, 'AnyDNR', \
            'Any DNR Code Status', code_status_cic_id)

        # ADMISSION
        admission_cic_id_query = \
            """
            SELECT clinical_item_category_id
            FROM clinical_item_category
            WHERE description = 'Admission';
            """
        results = DBUtil.execute(admission_cic_id_query)
        admission_cic_id = results[0][0]
        # Composite admission orders
        #   name    description
        #   ADT1    ADMIT TO INPATIENT
        #   ADT16	ADMIT POST SURGERY
        #   ADT1	ADMIT/PLACE PATIENT
        #   ADT100	ADMIT TO INPATIENT
        admission_ci_id_query = \
            """
            SELECT clinical_item_id
            FROM clinical_item
            WHERE
                (
                    name = 'ADT16' AND
                    description = 'ADMIT POST SURGERY'
                ) OR
                name IN ('ADT1', 'ADT100');
            """
        results = DBUtil.execute(admission_ci_id_query)
        admission_ci_ids = [result[0] for result in results]
        CDSSDataLoader.build_composite_clinical_item(admission_ci_ids, \
            'AnyAdmit', 'Any Admit (not observation nor outpatient surgery)',
            admission_cic_id)

    @staticmethod
    def build_composite_clinical_item(components, name, description, category_id):
        """
        Simple wrapper around medinfo/cpoe/DataManager.py
        """
        component_str = ','.join([str(id) for id in components])
        log.debug('(%s, %s, %s) = (%s)' % (name, description, category_id, \
                                            component_str))
        composite_arg = '%s|%s|%s|%s' % (component_str, name, description, \
                                            category_id)
        dm = DataManager()
        dm.main(['medinfo/cpoe/DataManager.py', '--compositeRelated', composite_arg])

    @staticmethod
    def define_virtual_clinical_items():
        log.info('Defining virtual clinical items...')
        # READMISSION
        # Readmission defined as a discharge --> admission.
        # First, define a clinical item for Readmission.
        admission_cic_id_query = \
            """
            SELECT clinical_item_category_id
            FROM clinical_item_category
            WHERE description = 'Admission';
            """
        results = DBUtil.execute(admission_cic_id_query)
        admission_cic_id = results[0][0]
        readmission_definition_command = \
            """
            INSERT INTO clinical_item (
                clinical_item_category_id,
                name,
                description,
                analysis_status,
                outcome_interest
            )
            VALUES (
                %s,
                'READT',
                'Readmission',
                1,
                1
            );
            """ % admission_cic_id
        DBUtil.execute(readmission_definition_command)
        # Second, get clinical_item_id for admission, discharge, & readmission.
        admission_ci_id_query = \
            """
            SELECT clinical_item_id
            FROM clinical_item
            WHERE name = 'AnyAdmit';
            """
        results = DBUtil.execute(admission_ci_id_query)
        admission_ci_id = results[0][0]
        discharge_ci_id_query = \
            """
            SELECT clinical_item_id
            FROM clinical_item
            WHERE name = 'ADT12';
            """
        results = DBUtil.execute(discharge_ci_id_query)
        discharge_ci_id = results[0][0]
        readmission_ci_id_query = \
            """
            SELECT clinical_item_id
            FROM clinical_item
            WHERE name = 'READT';
            """
        results = DBUtil.execute(readmission_ci_id_query)
        readmission_ci_id = results[0][0]
        # Third, use TripleAssociationAnalysis to build a new virtual item.
        item_sequence = [discharge_ci_id, admission_ci_id]
        CDSSDataLoader.build_virtual_clinical_item(item_sequence, readmission_ci_id)

    @staticmethod
    def build_virtual_clinical_item(item_sequence, virtual_id):
        """
        Simple wrapper around medinfo/cpoe/TripleAssociationAnalysis.
        """
        sequence_str = ' -> '.join([str(id) for id in item_sequence])
        log.debug('(%s) = (%s)' % (sequence_str, virtual_id))

        build_virtual_item_command = [
            'python', '-m', 'medinfo/cpoe/TripleAssociationAnalysis.py',
            '-s', ','.join([str(id) for id in item_sequence]),
            '-v', str(virtual_id)
            ]

        subprocess.call(build_virtual_item_command)

    @staticmethod
    def add_clinical_item_synonyms():
        log.info('Adding clinical item synonyms...')
        # Add common synonyms to major clinical items, primarily to facilitate
        # user interface simulation order searches by name.

        # Exact mappings between clinical item name and description synonym.
        EXACT_NAME_TO_SYNONYM = {
            'LABMETB': ' [BMP]',
            'LABMETC': ' [CMP]',
            'LABHFP': ' [LFT]',
            'EKG5': ' [EKG]',
            'LABPT': ' [PT/INR]',
        }
        for exact_name, synonym in EXACT_NAME_TO_SYNONYM.iteritems():
            synonym_command = \
                """
                UPDATE clinical_item
                SET description = description || '%s'
                WHERE name = '%s';
                """ % (synonym, exact_name)
            DBUtil.execute(synonym_command)

        # Case insensitive regular expression matches.
        REGEX_TO_SYNONYM = {
            '^xr.*chest': ' [CXR]',
            'urinalysis': ' [UA]'
        }
        for regex, synonym in REGEX_TO_SYNONYM.iteritems():
            synonym_command = \
                """
                UPDATE clinical_item
                SET description = description || '%s'
                WHERE description ~* '%s';
                """ % (synonym, regex)
            print synonym_command
            DBUtil.execute(synonym_command)

        # More complex cases that can't be easily looped.
        synonym_command = \
            """
            UPDATE clinical_item
            SET description = description || ' [NS IVF][Normal Saline]'
            WHERE
                name = 'RXCUI9863' AND
                DESCRIPTION ~* 'intravenous';
            """
        DBUtil.execute(synonym_command)

        synonym_command = \
            """
            UPDATE clinical_item
            SET description = description || ' [ABG]'
            WHERE
                description ~* 'blood gas' AND
                description ~* 'arteria' AND
                name ~* '^LAB|^POC';
            """
        DBUtil.execute(synonym_command)

        synonym_command = \
            """
            UPDATE clinical_item
            SET description = description || ' [VBG]'
            WHERE
                description ~* 'blood gas' AND
                description ~* 'venous' AND
                name ~* '^LAB|^POC';
            """
        DBUtil.execute(synonym_command)

        synonym_command = \
            """
            UPDATE clinical_item
            SET description = description || ' [LR][Lactated Ringer]'
            WHERE description ~* 'lactate.*intraven';
            """
        DBUtil.execute(synonym_command)

        synonym_command = \
            """
            UPDATE clinical_item
            SET description = description || ' [RBC]'
            WHERE
                description ~* 'red blood cell' AND
                name NOT LIKE 'ICD%%';
            """
        DBUtil.execute(synonym_command)

        synonym_command = \
            """
            UPDATE clinical_item
            SET description = description || ' [PLT]'
            WHERE description ~* 'platelet'
            AND description NOT LIKE '%%PLT%%';
            """
        DBUtil.execute(synonym_command)

        synonym_command = \
            """
            UPDATE clinical_item
            SET description = description || ' [FFP]'
            WHERE description ~* 'fresh frozen plasma';
            """
        DBUtil.execute(synonym_command)

    @staticmethod
    def define_possible_clinical_outcomes():
        log.info('Defining possible clinical outcomes')
        # Highlight items that may be of interest for outcome measures.
        outcome_definition_command = \
            """
            UPDATE clinical_item
            SET outcome_interest = 1
            WHERE description IN (
                'ADMIT POST SURGERY', 'ADMIT TO PHASE', 'ADMIT/PLACE PATIENT',
                 'AMIODARONE INFUSION CENTRAL LINE ADMIN',
                 'AMIODARONE INFUSION PERIPH ADMIN', 'AMIODARONE IVPB',
                 'ARGATROBAN 1000 MCG/ML (250 ML) IV INFUSION',
                 'ARTERIAL LINE', 'Amiodarone (Intravenous)',
                 'Bicarb Dialys Soln #16 W/O Ca K (4 Meq/L) -Mg (1.5 Meq/L) Hemodial Soln (CRRT)',
                 'Bicarb Dialys Soln No.8 W-O Ca K (2 Meq/L) -Mg (1 Meq/L) Hemodial Soln (CRRT)',
                 'CALL DIALYSIS RN CAP/DRAIN CAPD', 'CAPD PERITONEAL DIALYSIS',
                 'CAR CATH CORS POSSIBLE', 'CCPD  PERITONEAL DIALYSIS',
                 'CENTRAL LINE', 'CENTRAL LINE CARE', 'COMFORT CARE MEASURES',
                 'CONT RENAL REPLACEMENT THERAPY',
                 'D5W WITH SODIUM BICARBONATE IV INFUSION',
                 'DEXMEDETOMIDINE IV INFUSION', 'DIALYSIS ACCESS',
                 'DIALYSIS CATHETER CARE', 'DIALYZE PATIENT',
                 'DISCHARGE PATIENT', 'DISCHARGE PATIENT WHEN CRITERIA MET',
                 'DNR', 'Death Date', 'Dobutamine (Intravenous)',
                 'Dopamine (Intravenous)', 'EPINEPHRINE IV INFUSION',
                 'Epinephrine (Intravenous)', 'Eptifibatide (Intravenous)',
                 'Fentanyl (Intravenous)', 'HEMODIALYSIS',
                 'HEMODIALYSIS WITH PUF', 'INSERT AIRWAY',
                 'INTERAGENCY REFERRAL TO HOME HOSPICE', 'INTUBATION',
                 'MIDAZOLAM IV INFUSION (CUSTOM)', 'Midazolam (Intravenous)',
                 'Milrinone (Intravenous)', 'NITROPRUSSIDE IV INFUSION',
                 'NON INVASIVE POSTIVE PRESS VENT BIPAP/CPAP',
                 'NON-VIOLENT RESTRAINTS', 'NOREPINEPHRINE IV INFUSION',
                 'Nitroglycerin (Intravenous)', 'OK TO USE CENTRAL LINE',
                 'PARTIAL CODE', 'PATIENT TRANSPORT',
                 'PHENYLEPHRINE IV INFUSION', 'PLACE IN OBSERVATION-CDU',
                 'RESP - EXTUBATION',
                 'RESP - LUNG PROTECTIVE VENTILATION PROTOCOL',
                 'RESP - NON INVASIVE POS. PRESS VENT (BIPAP/CPAP)',
                 'RESP - SPONTANEOUS BREATHING TRIAL',
                 'RESP - VENTILATOR SETTINGS',
                 'RESP - WEAN VENTILATOR',
                 'RESP-CPAP/BIPAP FOR OBSTRUCTIVE SLEEP APNEA',
                 'TRACHEOSTOMY  CARE', 'TRANSFER PATIENT',
                 'TRANSFUSION EMERGENCY ISSUE',
                 'VASOPRESSIN 1 UNIT/ML IV INFUSION'
            );
            """
        DBUtil.execute(outcome_definition_command)

    @staticmethod
    def build_CDSS_indices():
        indices_dir = CDSSDataLoader.fetch_psql_indices_dir()
        for psql_table in CDSSDataLoader.CDSS_PSQL_TABLES:
            indices_file_name = '%s.indices.sql' % psql_table
            indices_path = os.path.join(indices_dir, indices_file_name)
            if os.path.exists(indices_path):
                with open(indices_path, 'r') as indices_file:
                    DBUtil.runDBScript(indices_file)

    @staticmethod
    def build_clinical_item_association_table():
        # Run Pre-Computation Association Analysis
        # Memory intensive, but if can use large amount on 64bit Python saves a
        # lot of DB hits / persistence. Use -a option to specify how many
        # associations to keep in memory before commit to DB.
        # 1,000,000 seems to just fit within 7.5 GB of RAM.
        # Still a DB intensive I/O process that can be helped by moving more
        # database processing to memory than disk.
        # python medinfo/cpoe/AssociationAnalysis.py -i <patientIDFile> -u 10000 -a 900000
        # (Find Patient IDs to work on, by query like
        # 	select distinct patient_id
        # 	from patient_item
        # 	where analyze_date is null
        # 	and patient_id % 10 = -1
        # Use arbitrary mod parameter on patient ID and item dates to select out data subsets
        # )
        #
        # # Helper driver script to break up into multiple processes (beware total memory overhead)
        # nohup python scripts/CDSS/assocAnalysis.py &> log/assocAnalysis &
        pass

if __name__=='__main__':
    log.level = logging.DEBUG

    # Define options for command-line usage.
    usage_str = 'usage: %prog [options]\n'
    parser = OptionParser(usage=usage_str)
    parser.add_option('-s', '--schemata', dest='build_schemata',
                        action='store_true', default=False,
                        help='build STRIDE psql schemata')
    parser.add_option('-t', '--transform', dest='transform_stride_table',
                        metavar='<transform_stride_table>', default=False,
                        help='transform STRIDE tables to CDSS tables')
    parser.add_option('-b', '--backup_psql', dest='backup_psql_tables',
                        action='store_true', default=False,
                        help='backup psql tables to dump files')
    parser.add_option('-d', '--delete', dest='delete_tables',
                        action='store_true', default=False,
                        help='delete CDSS tables')
    parser.add_option('-p', '--process', dest='process_tables',
                        action='store_true', default=False,
                        help='post-process CDSS tables')
    (options, args) = parser.parse_args(sys.argv[1:])

    # Handle command-line usage arguments.
    if options.build_schemata:
        CDSSDataLoader.build_CDSS_psql_schemata()
    elif options.transform_stride_table:
        CDSSDataLoader.transform_STRIDE_source_table(options.transform_stride_table)
    elif options.delete_tables:
        CDSSDataLoader.clear_CDSS_psql_tables()
    elif options.process_tables:
        CDSSDataLoader.process_CDSS_psql_db()
