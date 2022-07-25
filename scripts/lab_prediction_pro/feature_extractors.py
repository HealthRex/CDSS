"""
Defines all feature extractors used by featurizers. A feature extractor is a
self contained module that takes  in a cohort table and appends to or creates a
long form feature matrix in a temporary bigquery table with the following schema
Columns:
    observation_id -- integer
    index_time -- timestamp
    feature_type -- string
    feature_time -- timestamp
    feature_id -- string
    feature -- string
    feature_value -- numeric
"""
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import pandas as pd 

REPLACE_TABLE = True

class FlowsheetBinsExtractor():
    """
    Defines logic to extract vitals from flowsheets
    """

    def __init__(self, cohort_table_id, feature_table_id,
                 flowsheet_descriptions, look_back_days=3, bins=5,
                 project_id='som-nero-phi-jonc101', dataset='shc_core_2021'):
        """
        Tokenizes flowsheets into bins and then writes or appends to temp
        dataset. 
        Args:
            cohort_table: name of cohort table -- used to join to features
            temp_dataset: name of temp dataset with cohort table
            flowsheet_descriptions: list of row_disp_names used for flowsheet
                descriptions
            project_id: name of project you are extracting data from
            dataset: name of dataset you are extracting data from
        Returns:
            df_lup : dataframe with bin thresholds
        """
        self.cohort_table_id = cohort_table_id
        self.feature_table_id = feature_table_id
        self.client = bigquery.Client()
        self.look_back_days = look_back_days
        self.project_id = project_id
        self.dataset = dataset
        self.flowsheet_descriptions = "("
        for i, flow in enumerate(flowsheet_descriptions):
            if i == len(flowsheet_descriptions) - 1:
                self.flowsheet_descriptions += f"'{flow}')"
            else:
                self.flowsheet_descriptions += f"'{flow}', "

    def __call__(self):
        """
        Executes queries and returns all 
        """
        query = f"""
        WITH flowsheet_vals AS (
        SELECT DISTINCT
            labels.observation_id,
            labels.index_time,
            'Vitals' as feature_type,
            f.recorded_time_utc as feature_time,
            GENERATE_UUID() as feature_id,
            f.row_disp_name as feature,
            CAST(f.numerical_val_1 AS float64) as value
        FROM
            {self.cohort_table_id}
             labels
        LEFT JOIN
            {self.project_id}.{self.dataset}.flowsheet f
        ON
            labels.anon_id = f.anon_id
        WHERE
            f.recorded_time_utc < labels.index_time
        AND
            TIMESTAMP_ADD(f.recorded_time_utc,
                          INTERVAL 24*{self.look_back_days} HOUR)
                          >= labels.index_time
        AND
            f.row_disp_name in {self.flowsheet_descriptions}
        AND
            f.numerical_val_1 IS NOT NULL
        ),

        ranked as (
        SELECT DISTINCT
            observation_id, index_time, feature_type,
            feature_time, feature_id, feature,
            PERCENT_RANK() OVER (PARTITION BY feature ORDER BY value) value
        FROM 
            flowsheet_vals
        )

        SELECT DISTINCT
            observation_id, index_time, feature_type,
            feature_time, feature_id,
            CASE WHEN value < 0.2 THEN CONCAT(feature, '_0')
                WHEN value < 0.4 THEN CONCAT(feature, '_1')
                WHEN value < 0.6 THEN CONCAT(feature, '_2')
                WHEN value < 0.8 THEN CONCAT(feature, '_3')
                ELSE CONCAT(feature, '_4')
            END feature,
            1 value
        FROM
            ranked
        """
        query = add_create_or_append_logic(query, self.feature_table_id)
        query_job = self.client.query(query)
        query_job.result()
        df_lup = self.get_bin_thresholds()
        return df_lup

    def get_bin_thresholds(self):
        query = f"""
        WITH flowsheet_vals AS (
        SELECT DISTINCT
            labels.observation_id,
            labels.index_time,
            'Vitals' as feature_type,
            f.recorded_time_utc as feature_time,
            GENERATE_UUID() as feature_id,
            f.row_disp_name as feature,
            CAST(f.numerical_val_1 AS float64) as value
        FROM
            {self.cohort_table_id}
             labels
        LEFT JOIN
            {self.project_id}.{self.dataset}.flowsheet f
        ON
            labels.anon_id = f.anon_id
        WHERE
            f.recorded_time_utc < labels.index_time
        AND
            TIMESTAMP_ADD(f.recorded_time_utc,
                          INTERVAL 24*{self.look_back_days} HOUR)
                          >= labels.index_time
        AND
            f.row_disp_name in {self.flowsheet_descriptions}
        AND
            f.numerical_val_1 IS NOT NULL
        )

        SELECT DISTINCT
            feature,
            PERCENTILE_DISC(value, 0.2) OVER(PARTITION BY feature) min_bin_1,
            PERCENTILE_DISC(value, 0.4) OVER(PARTITION BY feature) min_bin_2,
            PERCENTILE_DISC(value, 0.6) OVER(PARTITION BY feature) min_bin_3,
            PERCENTILE_DISC(value, 0.8) OVER(PARTITION BY feature) min_bin_4,
        FROM 
            flowsheet_vals
        """
        df = pd.read_gbq(query)
        return df

class LabResultBinsExtractor():
    """
    Defines logic to extract lab results orders, 
    """

    def __init__(self, cohort_table_id, feature_table_id,
                 base_names, bins=5, look_back_days=14, 
                 project_id='som-nero-phi-jonc101', dataset='shc_core_2021'):
        """
        Args:
            cohort_table: name of cohort table -- used to join to features
            temp_dataset: name of temp dataset with cohort table
            project_id: name of project you are extracting data from
            dataset: name of dataset you are extracting data from
        """
        self.cohort_table_id = cohort_table_id
        self.feature_table_id = feature_table_id
        self.client = bigquery.Client()
        self.num_bins = bins
        self.look_back_days = look_back_days
        self.project_id = project_id
        self.dataset = dataset
        self.base_name_string = "("
        for i, base_name in enumerate(base_names):
            if i == len(base_names) - 1:
                self.base_name_string += f"'{base_name}')"
            else:
                self.base_name_string += f"'{base_name}', "

    def __call__(self):
        """
        Executes queries and returns all 
        """
        query = f"""
        WITH labresults_values AS (
        SELECT DISTINCT
            labels.observation_id,
            labels.index_time,
            'Lab Results' as feature_type,
            lr.result_time_utc as feature_time,
            CAST(lr.order_id_coded AS STRING) as feature_id,
            lr.base_name as feature,
            lr.ord_num_value as value
        FROM
            {self.cohort_table_id}
             labels
        LEFT JOIN
            {self.project_id}.{self.dataset}.lab_result lr
        ON
            labels.anon_id = lr.anon_id
        WHERE
            lr.result_time_utc < labels.index_time
        AND
            TIMESTAMP_ADD(lr.result_time_utc,
                          INTERVAL 24*{self.look_back_days} HOUR)
                          >= labels.index_time
        AND
            lr.base_name in {self.base_name_string}
        AND
            lr.ord_num_value IS NOT NULL
        ),

        ranked as (
        SELECT DISTINCT
            observation_id, index_time, feature_type,
            feature_time, feature_id, feature,
            PERCENT_RANK() OVER (PARTITION BY feature ORDER BY value) value
        FROM 
            labresults_values
        )

        SELECT DISTINCT
            observation_id, index_time, feature_type,
            feature_time, feature_id,
            CASE WHEN value < 0.2 THEN CONCAT(feature, '_0')
                WHEN value < 0.4 THEN CONCAT(feature, '_1')
                WHEN value < 0.6 THEN CONCAT(feature, '_2')
                WHEN value < 0.8 THEN CONCAT(feature, '_3')
                ELSE CONCAT(feature, '_4')
            END feature,
            1 value
        FROM
            ranked
        """
        query = add_create_or_append_logic(query, self.feature_table_id)
        query_job = self.client.query(query)
        query_job.result()
        df_lup = self.get_bin_thresholds()
        return df_lup

    def get_bin_thresholds(self):
        query = f"""
        WITH labresults_values AS (
        SELECT DISTINCT
            labels.observation_id,
            labels.index_time,
            'Lab Results' as feature_type,
            lr.result_time_utc as feature_time,
            CAST(lr.order_id_coded AS STRING) as feature_id,
            lr.base_name as feature,
            lr.ord_num_value as value
        FROM
            {self.cohort_table_id}
             labels
        LEFT JOIN
            {self.project_id}.{self.dataset}.lab_result lr
        ON
            labels.anon_id = lr.anon_id
        WHERE
            lr.result_time_utc < labels.index_time
        AND
            TIMESTAMP_ADD(lr.result_time_utc,
                          INTERVAL 24*{self.look_back_days} HOUR)
                          >= labels.index_time
        AND
            lr.base_name in {self.base_name_string}
        AND
            lr.ord_num_value IS NOT NULL
        )

        SELECT DISTINCT
            feature,
            PERCENTILE_DISC(value, 0.2) OVER(PARTITION BY feature) min_bin_1,
            PERCENTILE_DISC(value, 0.4) OVER(PARTITION BY feature) min_bin_2,
            PERCENTILE_DISC(value, 0.6) OVER(PARTITION BY feature) min_bin_3,
            PERCENTILE_DISC(value, 0.8) OVER(PARTITION BY feature) min_bin_4,
        FROM 
            labresults_values
        """
        df = pd.read_gbq(query)
        return df

class MedicationExtractor():
    """
    Defines logic to extract medication orders
    """

    def __init__(self, cohort_table_id, feature_table_id, 
                 look_back_days=28, project_id='som-nero-phi-jonc101',
                 dataset='shc_core_2021'):
        """
        Args:
            cohort_table: name of cohort table -- used to join to features
            project_id: name of project you are extracting data from
            dataset: name of dataset you are extracting data from
        """
        self.cohort_table_id = cohort_table_id
        self.look_back_days = look_back_days
        self.project_id = project_id
        self.dataset = dataset
        self.feature_table_id = feature_table_id
        self.client = bigquery.Client()

    def __call__(self):
        """
        Executes queries and returns all 
        """
        query = f"""
        SELECT DISTINCT
            labels.observation_id,
            labels.index_time,
            'Medications' as feature_type,
            meds.order_inst_utc as feature_time,
            CAST(meds.order_med_id_coded as STRING) as feature_id,
            meds.med_description as feature,
            1 as value
        FROM
            {self.cohort_table_id}
            labels
        LEFT JOIN
            {self.project_id}.{self.dataset}.order_med meds
        ON
            labels.anon_id = meds.anon_id
        WHERE 
            CAST(meds.order_inst_utc as TIMESTAMP) < labels.index_time
        AND
            TIMESTAMP_ADD(meds.order_inst_utc,
                          INTERVAL 24*{self.look_back_days} HOUR)
                          >= labels.index_time
        """
        query = add_create_or_append_logic(query, self.feature_table_id)
        query_job = self.client.query(query)
        query_job.result()

class PatientProblemExtractor():
    """
    Defines logic to extract diagnoses on the patient's problem list
    """

    def __init__(self, cohort_table_id, feature_table_id,
                 project_id='som-nero-phi-jonc101', dataset='shc_core_2021'):
        """
        Args:
            cohort_table: name of cohort table -- used to join to features
            project_id: name of project you are extracting data from
            dataset: name of dataset you are extracting data from
        """
        self.cohort_table_id = cohort_table_id
        self.feature_table_id = feature_table_id
        self.client = bigquery.Client()
        self.project_id = project_id
        self.dataset = dataset

    def __call__(self):
        """
        Executes queries and returns all 
        """
        query = f"""
        SELECT
            labels.observation_id,
            labels.index_time,
            'Diagnoses' as feature_type,
            CAST(dx.start_date_utc as TIMESTAMP) as feature_time,
            GENERATE_UUID() as feature_id,
            dx.icd10 as feature,
            1 value
        FROM
            {self.cohort_table_id}
            labels
        LEFT JOIN
            {self.project_id}.{self.dataset}.diagnosis dx
        ON
            labels.anon_id = dx.anon_id
        WHERE 
            CAST(dx.start_date_utc as TIMESTAMP) < labels.index_time
        AND
            source = 2 --problem list only
        """
        query = add_create_or_append_logic(query, self.feature_table_id)
        query_job = self.client.query(query)
        query_job.result()

class SexExtractor():
    """
    Defines logic to extract sex as feature from dataset
    """

    def __init__(self, cohort_table_id, feature_table_id,
                 project_id='som-nero-phi-jonc101', dataset='shc_core_2021'):
        """
        Args:
            cohort_table: name of cohort table -- used to join to features
            project_id: name of project you are extracting data from
            dataset: name of dataset you are extracting data from
        """
        self.cohort_table_id = cohort_table_id
        self.feature_table_id = feature_table_id
        self.client = bigquery.Client()
        self.project_id = project_id
        self.dataset = dataset

    def __call__(self):
        """
        Executes queries and returns all 
        """
        query = f"""
        SELECT DISTINCT
            labels.observation_id,
            labels.index_time,
            'Demographics' as feature_type,
            labels.index_time as feature_time,
            GENERATE_UUID() as feature_id,
            CASE WHEN demo.GENDER is NULL then 'sex_missing'
            ELSE CONCAT('sex_', demo.GENDER) END feature,
            1 value
        FROM
            {self.cohort_table_id}
            labels
        LEFT JOIN
            {self.project_id}.{self.dataset}.demographic demo
        ON
            labels.anon_id = demo.ANON_ID
        """
        query = add_create_or_append_logic(query, self.feature_table_id)
        query_job = self.client.query(query)
        query_job.result()

class RaceExtractor():
    """
    Defines logic to extract race as feature from dataset
    """

    def __init__(self, cohort_table_id, feature_table_id,
                 project_id='som-nero-phi-jonc101', dataset='shc_core_2021'):
        """
        Args:
            cohort_table: name of cohort table -- used to join to features
            project_id: name of project you are extracting data from
            dataset: name of dataset you are extracting data from
        """
        self.cohort_table_id = cohort_table_id
        self.feature_table_id = feature_table_id
        self.client = bigquery.Client()
        self.project_id = project_id
        self.dataset = dataset

    def __call__(self):
        """
        Executes queries and returns all 
        """
        query = f"""
        SELECT DISTINCT
            labels.observation_id,
            labels.index_time,
            'Demographics' as feature_type,
            labels.index_time as feature_time,
            GENERATE_UUID() as feature_id,
            CASE WHEN demo.CANONICAL_RACE is NULL then 'race_missing'
            ELSE CONCAT('race_', demo.CANONICAL_RACE) END feature,
            1 value
        FROM
            {self.cohort_table_id}
            labels
        LEFT JOIN
            {self.project_id}.{self.dataset}.demographic demo
        ON
            labels.anon_id = demo.ANON_ID
        """
        query = add_create_or_append_logic(query, self.feature_table_id)
        query_job = self.client.query(query)
        query_job.result()

class AgeExtractor():
    """
    Defines logic to extract age as feature from dataset
    """

    def __init__(self, cohort_table_id, feature_table_id, bins=5,
                 project_id='som-nero-phi-jonc101', dataset='shc_core_2021'):
        """
        Args:
            cohort_table: name of cohort table -- used to join to features
            project_id: name of project you are extracting data from
            dataset: name of dataset you are extracting data from
        """
        self.cohort_table_id = cohort_table_id
        self.feature_table_id = feature_table_id
        self.client = bigquery.Client()
        self.num_bins = bins
        self.project_id = project_id
        self.dataset = dataset
     
    def __call__(self):
        """
        Executes queries and returns all 
        """
        query = f"""
        WITH age_values as (
        SELECT DISTINCT
            labels.observation_id,
            labels.index_time,
            'Demographics' as feature_type,
            labels.index_time as feature_time,
            GENERATE_UUID() as feature_id,
            'Age' as feature,
            DATE_DIFF(
                CAST(labels.index_time AS date), demo.BIRTH_DATE_JITTERED, YEAR)
            as value
        FROM
            {self.cohort_table_id}
            labels
        INNER JOIN
            {self.project_id}.{self.dataset}.demographic demo
        ON
            labels.anon_id = demo.ANON_ID
        ),
        ranked as (
        SELECT DISTINCT
            observation_id, index_time, feature_type,
            feature_time, feature_id, feature,
            PERCENT_RANK() OVER (PARTITION BY feature ORDER BY value) value
        FROM
            age_values
        )

        SELECT DISTINCT
            observation_id, index_time, feature_type,
            feature_time, feature_id,
            CASE WHEN value < 0.2 THEN CONCAT(feature, '_0')
                WHEN value < 0.4 THEN CONCAT(feature, '_1')
                WHEN value < 0.6 THEN CONCAT(feature, '_2')
                WHEN value < 0.8 THEN CONCAT(feature, '_3')
                ELSE CONCAT(feature, '_4')
            END feature,
            1 value
        FROM
            ranked
        """
        query = add_create_or_append_logic(query, self.feature_table_id)
        query_job = self.client.query(query)
        query_job.result()
        df_lup = self.get_bin_thresholds()
        return df_lup
    
    def get_bin_thresholds(self):
        query = f"""
        WITH age_values as (
        SELECT DISTINCT
            labels.observation_id,
            labels.index_time,
            'Demographics' as feature_type,
            labels.index_time as feature_time,
            GENERATE_UUID() as feature_id,
            'Age' as feature,
            DATE_DIFF(
                CAST(labels.index_time AS date), demo.BIRTH_DATE_JITTERED, YEAR)
            as value
        FROM
            {self.cohort_table_id}
            labels
        INNER JOIN
            {self.project_id}.{self.dataset}.demographic demo
        ON
            labels.anon_id = demo.ANON_ID
        )

        SELECT DISTINCT
            feature,
            PERCENTILE_DISC(value, 0.2) OVER(PARTITION BY feature) min_bin_1,
            PERCENTILE_DISC(value, 0.4) OVER(PARTITION BY feature) min_bin_2,
            PERCENTILE_DISC(value, 0.6) OVER(PARTITION BY feature) min_bin_3,
            PERCENTILE_DISC(value, 0.8) OVER(PARTITION BY feature) min_bin_4,
        FROM 
            age_values
        """
        df = pd.read_gbq(query)
        return df

def table_exists(feature_table_id):
    """
    Check if table exists
    """
    client = bigquery.Client()
    try:
        client.get_table(f'{feature_table_id}')
        return True
    except NotFound:
        return False

def add_create_or_append_logic(query, feature_table_id):
    """
    Adds SQL logic to either append or create a new feature matrix from result
    of user supplied SQL query. 
    """
    global REPLACE_TABLE
    exists = table_exists(feature_table_id)
    if exists and REPLACE_TABLE == False:
        query = f"""
        INSERT INTO
            {feature_table_id}
        {query}
        """
    else:
        query = f"""
        CREATE OR REPLACE TABLE {feature_table_id} AS (
        {query}
        )
        """
        REPLACE_TABLE = False
    return query
