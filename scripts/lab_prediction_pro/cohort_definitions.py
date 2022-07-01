import decimal
import pandas as pd

class CohortBuilder(object):
    """
    A class for constructing a cohort table and saving to a bigquery project.
    A cohort table should have at minimum three columns:
        1. anon_id : the patient id
        2. observation_id : a unique identifier for each observation 
        3. index_time : prediction time for each observation
        4. `label` : binary or multiclass indicating class membership of the
            observations. This may be multiple columns (if in multlilabel
            setting) and will have column names as specified in `label_columns`
            attribute.
    """

    def __init__(self, dataset_name, table_name,
                 working_project_id='mining-clinical-decisions'):
        """
        Initializes dataset_name and table_name for where cohort table will be
        saved on bigquery
        """
        self.project_id = working_project_id
        self.dataset_name = dataset_name
        self.table_name = table_name

    def write_cohort_table(self, overwrite=False, schema=None):
        """
        Writes the cohort dataframe to specified bigquery project, dataset,
        and table with appropriate table schema.

        Args:
            overwrite: if true overwrite existing table
            schema: dictionary of table schema, if None detect automatically. 
        """
        if overwrite:
            if_exists = 'replace'
        else:
            if_exists = 'fail'
        self.df.to_gbq(
            destination_table=f"{self.dataset_name}.{self.table_name}",
            project_id=self.project_id,
            if_exists=if_exists,
            table_schema=schema
        )

class CBCWithDifferentialCohort(CohortBuilder):
    """
    Defines a cohort and labels for CBC with differential models
    """

    def __init__(self, dataset_name, table_name,
        working_project_id='mining-clinical-decisions'):
        """
        Initializes dataset_name and table_name for where cohort table will be
        saved on bigquery
        """
        super(CBCWithDifferentialCohort).__init__(
            dataset_name, table_name, working_project_id)
    
    def build_cohort(self):
        """
        Function that constructs a cohort table for predicting cbc with
        differential results. Done with SQL logic where possible

        """
        project_id = 'som-nero-phi-jonc101'
        dataset = 'shc_core_2021'
        query=f"""
        CREATE OR REPLACE TABLE 
        {self.project_id}.{self.dataset_name}.{self.table_name}
        AS (
        WITH cbcd_lab_results as (
        SELECT DISTINCT
            anon_id,
            order_id_coded,
            order_time_utc as index_time,
            ordering_mode,
            base_name,
            CASE WHEN result_flag is NULL OR result_flag = "Normal" Then 0
            ELSE 1
            END label
        FROM 
            {project_id}.{dataset}.lab_result
        WHERE 
            # Note no inpatient results where proc code was LABCBCD
            UPPER(group_lab_name) = 'CBC WITH DIFFERENTIAL'
        AND
            base_name in ('WBC', 'PLT', 'HCT', 'HGB')
        AND 
            EXTRACT(YEAR FROM order_time_utc) BETWEEN 2015 and 2021
        ),

        # Pivot lab result to wide
        cohort_wide as (
            SELECT 
                * 
            FROM 
                cbcd_lab_results
            PIVOT (
                MAX(label) as label -- should be max of one value or no value 
                FOR base_name in ('WBC', 'PLT', 'HCT', 'HGB')
            )
            WHERE 
                -- only keep labs where all three components result
                label_WBC is not NULL AND
                label_PLT is not NULL AND
                label_HCT is not NULL
        )

        ### 10000 observations randomly sampled per year from train set
        SELECT 
            anon_id, order_id_coded as observation_id, index_time, 
            ordering_mode, label_WBC, label_PLT, label_HCT
        FROM 
            (SELECT *,
                ROW_NUMBER() OVER  (PARTITION BY EXTRACT(YEAR FROM index_time)
                                    ORDER BY RAND()) 
                        AS seqnum
            FROM cohort_wide 
            ) 
        WHERE
            seqnum <= 10000
        )
        
        """
        query_job = self.client.query(query)
        query_job.result()


class MetabolicComprehensiveCohort(CohortBuilder):
    """
    Defines a cohort and labels for metabolic comprehensive tasks
    """

    def __init__(self, dataset_name, table_name,
                 working_project_id='mining-clinical-decisions'):
        """
        Initializes dataset_name and table_name for where cohort table will be
        saved on bigquery
        """
        super(MetabolicComprehensiveCohort).__init__(
            dataset_name, table_name, working_project_id)

    def build_cohort(self):
        """
        Function that constructs a cohort table for predicting cbc with
        differential results. Done with SQL logic where possible

        """
        project_id = 'som-nero-phi-jonc101'
        dataset = 'shc_core_2021'
        query = f"""
        CREATE OR REPLACE TABLE 
        {self.project_id}.{self.dataset_name}.{self.table_name}
        AS (
        WITH cbcd_lab_results as (
        SELECT DISTINCT
            anon_id,
            order_id_coded,
            order_time_utc as index_time,
            ordering_mode,
            base_name,
            CASE WHEN result_flag is NULL OR result_flag = "Normal" Then 0
            ELSE 1
            END label
        FROM 
            {project_id}.{dataset}.lab_result
        WHERE 
            # Note no inpatient results where proc code was LABCBCD
            group_lab_name = 'Metabolic Panel, Comprehensive'
        AND
            base_name in ('NA', 'K', 'CO2' 'BUN', 'CR', 'CA', 'ALB')
        AND 
            EXTRACT(YEAR FROM order_time_utc) BETWEEN 2015 and 2021
        ),

        # Pivot lab result to wide
        cohort_wide as (
            SELECT 
                * 
            FROM 
                cbcd_lab_results
            PIVOT (
                MAX(label) as label -- should be max of one value or no value 
                FOR base_name in ('NA', 'K', 'CO2' 'BUN', 'CR', 'CA', 'ALB')
            )
            WHERE 
                -- only keep labs where all three components result
                label_NA is not NULL AND
                label_K is not NULL AND
                label_CO2 is not NULL
                label_BUN is not NULL AND
                label_CR is not NULL AND
                label_CA is not NULL AND
                label_ALB is not NULL
        )

        ### 10000 observations randomly sampled per year from train set
        SELECT 
            anon_id, order_id_coded as observation_id, index_time, 
            ordering_mode, label_NA, label_K, label_CO2, label_BUN, label_CR,
            label_CA, label_ALB
        FROM 
            (SELECT *,
                ROW_NUMBER() OVER  (PARTITION BY EXTRACT(YEAR FROM index_time)
                                    ORDER BY RAND()) 
                        AS seqnum
            FROM cohort_wide 
            ) 
        WHERE
            seqnum <= 10000
        )
        
        """
        query_job = self.client.query(query)
        query_job.result()


class MagnesiumCohort(CohortBuilder):
    """
    Defines a cohort and labels for magnesium prediction models
    """

    def __init__(self, dataset_name, table_name,
                 working_project_id='mining-clinical-decisions'):
        """
        Initializes dataset_name and table_name for where cohort table will be
        saved on bigquery
        """
        super(MagnesiumCohort).__init__(
            dataset_name, table_name, working_project_id)

    def build_cohort(self):
        """
        Function that constructs a cohort table for predicting cbc with
        differential results. Done with SQL logic where possible

        """
        project_id = 'som-nero-phi-jonc101'
        dataset = 'shc_core_2021'
        query = f"""
        CREATE OR REPLACE TABLE 
        {self.project_id}.{self.dataset_name}.{self.table_name}
        AS (
        WITH cbcd_lab_results as (
        SELECT DISTINCT
            anon_id,
            order_id_coded,
            order_time_utc as index_time,
            ordering_mode,
            base_name,
            CASE WHEN result_flag is NULL OR result_flag = "Normal" Then 0
            ELSE 1
            END label
        FROM 
            {project_id}.{dataset}.lab_result
        WHERE 
            # Note no inpatient results where proc code was LABCBCD
            UPPER(group_lab_name) = 'MAGNESIUM, SERUM/PLASMA'
        AND
            base_name = 'MG'
        AND 
            EXTRACT(YEAR FROM order_time_utc) BETWEEN 2015 and 2021
        ),

        # Pivot lab result to wide
        cohort_wide as (
            SELECT 
                * 
            FROM 
                cbcd_lab_results
            PIVOT (
                MAX(label) as label -- should be max of one value or no value 
                FOR base_name in ('MG')
            )
            WHERE 
                -- only keep labs where all three components result
                label_MG is not NULL 
        )

        ### 10000 observations randomly sampled per year from train set
        SELECT 
            anon_id, order_id_coded as observation_id, index_time, 
            ordering_mode, label_MG
        FROM 
            (SELECT *,
                ROW_NUMBER() OVER  (PARTITION BY EXTRACT(YEAR FROM index_time)
                                    ORDER BY RAND()) 
                        AS seqnum
            FROM cohort_wide 
            ) 
        WHERE
            seqnum <= 10000
        )
        
        """
        query_job = self.client.query(query)
        query_job.result()


class BloodCultureCohort(CohortBuilder):
    """
    Defines a cohort and labels for blood culture prediction models
    """

    def __init__(self, dataset_name, table_name,
                 working_project_id='mining-clinical-decisions'):
        """
        Initializes dataset_name and table_name for where cohort table will be
        saved on bigquery
        """
        super(BloodCultureCohort).__init__(
            dataset_name, table_name, working_project_id)

    def build_cohort(self):
        """
        Function that constructs a cohort table for predicting blood culture
        results: positive vs negative (but say COAG NEG STAPH is neg)

        """
        project_id = 'som-nero-phi-jonc101'
        dataset = 'shc_core_2021'
        query = f"""
        CREATE OR REPLACE TABLE 
        {self.project_id}.{self.dataset_name}.{self.table_name}
        AS (
        WITH cbcd_lab_results as (
        SELECT DISTINCT
            anon_id,
            order_id_coded,
            order_time_utc as index_time,
            ordering_mode,
            base_name,
            CASE WHEN result_flag is NULL OR result_flag = "Normal" Then 0
            ELSE 1
            END label
        FROM 
            {project_id}.{dataset}.lab_result
        WHERE 
            proc_code in ('LABBLC', 'LABBLC2')
        AND
            base_name = 'CULT'
        AND 
            EXTRACT(YEAR FROM order_time_utc) BETWEEN 2015 and 2021
        ),

        ### 10000 observations randomly sampled per year from train set
        SELECT 
            anon_id, order_id_coded as observation_id, index_time, 
            ordering_mode, label
        FROM 
            (SELECT *,
                ROW_NUMBER() OVER  (PARTITION BY EXTRACT(YEAR FROM index_time)
                                    ORDER BY RAND()) 
                        AS seqnum
            FROM cohort_wide 
            ) 
        WHERE
            seqnum <= 10000
        )
        """
        query_job = self.client.query(query)
        query_job.result()
