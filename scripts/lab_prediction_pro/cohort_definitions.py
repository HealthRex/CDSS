"""
A place for cohort definitions (cohort + labels)
"""
import decimal
import pandas as pd

import pdb

class CohortBuilder():
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

    def __init__(self, client, dataset_name, table_name,
                 working_project_id='mining-clinical-decisions'):
        """
        Initializes dataset_name and table_name for where cohort table will be
        saved on bigquery
        """
        self.client = client
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

class InpatientMortalityCohort(CohortBuilder):
    """
    Defines a cohort for the task of predicting inpatient mortality.
    """

    def __init__(self, client, dataset_name, table_name,
                 working_project_id='mining-clinical-decisions'):
        """
        Initializes dataset_name and table_name for where cohort table will be
        saved on bigquery
        """
        super(InpatientMortalityCohort, self).__init__(
            client, dataset_name, table_name, working_project_id)

    def __call__(self):
        """
        Function that constructs a cohort table for predicting cbc with
        differential results. Done with SQL logic where possible
        """
        query = f"""
        CREATE OR REPLACE TABLE 
        {self.project_id}.{self.dataset_name}.{self.table_name}
        AS (
        -- Use ADT table to get inpatient admits, discharge times if they exist,
        -- and Transfer Out times.
        WITH inpatient_admits as (
        SELECT 
            anon_id, pat_enc_csn_id_coded, 
            CASE WHEN in_event_type IS NOT NULL THEN in_event_type
            ELSE REPLACE(out_event_type, ' ', '') END event_type,
            event_time_jittered_utc
        FROM
            `som-nero-phi-jonc101.shc_core.adt` 
        WHERE
            pat_class = 'Inpatient' AND
            (in_event_type = 'Admission' or out_event_type in 
            ('Discharge', 'Transfer Out'))
        ),
        -- Join to demographics table to get death date for each patient
        admissions_with_death_date as (
        SELECT DISTINCT 
            ia.*, d.death_date_jittered
        FROM
            inpatient_admits ia
        INNER JOIN
            `som-nero-phi-jonc101.shc_core.demographic` d
        USING
            (anon_id)
        ),
        -- Pivot so that we have one column for admission, transfer out and
        -- discharge time (take latest of tranfer out times)
        admissions_wide as (
        SELECT 
            *
        FROM
            admissions_with_death_date
        PIVOT (
            MAX(event_time_jittered_utc) as event_time
            FOR event_type in ('Admission', 'TransferOut', 'Discharge')
        )
            ORDER BY anon_id, event_time_Admission
        )
        -- label is one when date of death exists between admission and
        -- discharge, or between admission and transfer out if discharge
        -- does not exist. 
        SELECT
            anon_id, pat_enc_csn_id_coded observation_id,
            event_time_Admission index_time, 
            CASE WHEN death_date_jittered
            BETWEEN DATE(a.event_time_Admission) AND 
            DATE(a.event_time_Discharge) THEN 1
            WHEN a.event_time_Discharge IS NULL AND 
            death_date_jittered BETWEEN DATE(a.event_time_Admission)
            AND DATE(a.  event_time_TransferOut) THEN 1
            ELSE 0 END label,
            event_time_TransferOut, event_time_Discharge, death_date_jittered
        FROM
            admissions_wide a
        WHERE
            EXTRACT(YEAR FROM event_time_Admission) BETWEEN 2015 and 2020
            AND NOT (event_time_TransferOut IS NULL 
                     AND event_time_Discharge IS NULL)
        )        
        """
        query_job = self.client.query(query)
        query_job.result()

class LongLengthOfStayCohort(CohortBuilder):
    """
    Defines a cohort of patients admitted to hospital, positive label for
    patients who stayed in inpatient setting for seven days or longer. 
    """

    def __init__(self, client, dataset_name, table_name,
                 working_project_id='mining-clinical-decisions'):
        """
        Initializes dataset_name and table_name for where cohort table will be
        saved on bigquery
        """
        super(LongLengthOfStayCohort, self).__init__(
            client, dataset_name, table_name, working_project_id)

    def __call__(self):
        """
        Function that constructs a cohort table for predicting cbc with
        differential results. Done with SQL logic where possible
        """
        query = f"""
        CREATE OR REPLACE TABLE 
        {self.project_id}.{self.dataset_name}.{self.table_name}
        AS (
        -- Use ADT table to get inpatient admits, discharge times if they exist,
        -- and Transfer Out times.
        WITH inpatient_admits as (
        SELECT 
            anon_id, pat_enc_csn_id_coded, 
            CASE WHEN in_event_type IS NOT NULL THEN in_event_type
            ELSE REPLACE(out_event_type, ' ', '') END event_type,
            event_time_jittered_utc
        FROM
            `som-nero-phi-jonc101.shc_core.adt` 
        WHERE
            pat_class = 'Inpatient' AND
            (in_event_type = 'Admission' or out_event_type in 
            ('Discharge', 'Transfer Out'))
        ),

        admissions_wide as (
        SELECT 
            *
        FROM
            inpatient_admits
        PIVOT (
            MAX(event_time_jittered_utc) as event_time
            FOR event_type in ('Admission', 'TransferOut', 'Discharge')
        )
            ORDER BY anon_id, event_time_Admission
        )

        SELECT
            anon_id, pat_enc_csn_id_coded observation_id,
            event_time_Admission index_time, 
            CASE WHEN TIMESTAMP_DIFF(a.event_time_Discharge, 
                                     a.event_time_Admission, DAY)< 7 AND
            a.event_time_Discharge IS NOT NULL THEN 0
            WHEN TIMESTAMP_DIFF(a.event_time_TransferOut,
                                a.event_time_Admission, DAY) < 7 AND
            a.event_time_TransferOut IS NOT NULL AND 
            a.event_time_Discharge IS NULL THEN 0
            ELSE 1 END label,
            TIMESTAMP_DIFF(a.event_time_Discharge,
                           a.event_time_Admission, DAY) time_to_discharge,
            TIMESTAMP_DIFF(a.event_time_TransferOut, 
                           a.event_time_Admission, DAY) time_to_transfer_out,
            event_time_TransferOut, event_time_Discharge
        FROM
            admissions_wide a
        WHERE
            EXTRACT(YEAR FROM event_time_Admission) BETWEEN 2015 and 2020
            AND NOT (event_time_TransferOut IS NULL AND event_time_Discharge
            IS NULL)
        )
        """
        query_job = self.client.query(query)
        query_job.result()



class CBCWithDifferentialCohort(CohortBuilder):
    """
    Defines a cohort and labels for CBC with differential models
    """

    def __init__(self, client, dataset_name, table_name,
        working_project_id='mining-clinical-decisions'):
        """
        Initializes dataset_name and table_name for where cohort table will be
        saved on bigquery
        """
        super(CBCWithDifferentialCohort, self).__init__(client, dataset_name,
            table_name, working_project_id)
    
    def __call__(self):
        """
        Function that constructs a cohort table for predicting cbc with
        differential results. Done with SQL logic where possible
        """
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
            som-nero-phi-jonc101.shc_core_2021.lab_result
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
                label_HCT is not NULL AND
                label_HGB is not NULL
        )

        ### 10000 observations randomly sampled per year from train set
        SELECT 
            anon_id, order_id_coded as observation_id, index_time, 
            ordering_mode, label_WBC, label_PLT, label_HCT, label_HGB
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

    def __init__(self, client, dataset_name, table_name,
                 working_project_id='mining-clinical-decisions'):
        """
        Initializes dataset_name and table_name for where cohort table will be
        saved on bigquery
        """
        super(MetabolicComprehensiveCohort, self).__init__(client,
            dataset_name, table_name, working_project_id)

    def __call__(self):
        """
        Function that constructs a cohort table for predicting cbc with
        differential results. Done with SQL logic where possible

        """
        query = f"""
        CREATE OR REPLACE TABLE 
        {self.project_id}.{self.dataset_name}.{self.table_name}
        AS (
        WITH metabolic_comp as (
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
            som-nero-phi-jonc101.shc_core_2021.lab_result
        WHERE 
            # Note no inpatient results where proc code was LABCBCD
            group_lab_name = 'Metabolic Panel, Comprehensive'
        AND
            base_name in ('NA', 'K', 'CO2', 'BUN', 'CR', 'CA', 'ALB')
        AND 
            EXTRACT(YEAR FROM order_time_utc) BETWEEN 2015 and 2021
        ),

        # Pivot lab result to wide
        cohort_wide as (
            SELECT 
                * 
            FROM 
                metabolic_comp
            PIVOT (
                MAX(label) as label -- should be max of one value or no value 
                FOR base_name in ('NA', 'K', 'CO2', 'BUN', 'CR', 'CA', 'ALB')
            )
            WHERE 
                -- only keep labs where all three components result
                label_NA is not NULL AND
                label_K is not NULL AND
                label_CO2 is not NULL AND
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

    def __init__(self, client, dataset_name, table_name,
                 working_project_id='mining-clinical-decisions'):
        """
        Initializes dataset_name and table_name for where cohort table will be
        saved on bigquery
        """
        super(MagnesiumCohort, self).__init__(client,
            dataset_name, table_name, working_project_id)

    def __call__(self):
        """
        Function that constructs a cohort table for predicting cbc with
        differential results. Done with SQL logic where possible

        """
        query = f"""
        CREATE OR REPLACE TABLE 
        {self.project_id}.{self.dataset_name}.{self.table_name}
        AS (
        WITH magnesium_results as (
        SELECT DISTINCT
            anon_id, order_id_coded, order_time_utc as index_time,
            ordering_mode, base_name,
            CASE WHEN result_flag is NULL OR result_flag = "Normal" Then 0
            ELSE 1 END label
        FROM 
            som-nero-phi-jonc101.shc_core_2021.lab_result
        WHERE 
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
                magnesium_results
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

    def __init__(self, client, dataset_name, table_name,
                 working_project_id='mining-clinical-decisions'):
        """
        Initializes dataset_name and table_name for where cohort table will be
        saved on bigquery
        """
        super(BloodCultureCohort, self).__init__(client,
            dataset_name, table_name, working_project_id)

    def __call__(self):
        """
        Function that constructs a cohort table for predicting blood culture
        results: positive vs negative (but say COAG NEG STAPH is neg)

        """
        query = f"""
        CREATE OR REPLACE TABLE 
        {self.project_id}.{self.dataset_name}.{self.table_name}
        AS (
        WITH blood_culture_results as (
        SELECT DISTINCT
            anon_id, order_id_coded, order_time_utc as index_time, 
            ordering_mode,
            MAX(CASE WHEN result_flag is NULL OR result_flag = "Normal" Then 0
            ELSE 1 END) label_blood
        FROM 
            som-nero-phi-jonc101.shc_core_2021.lab_result
        WHERE 
            proc_code in ('LABBLC', 'LABBLC2')
        AND 
            EXTRACT(YEAR FROM order_time_utc) BETWEEN 2015 and 2021
        GROUP BY
        anon_id, order_id_coded, order_time_utc, ordering_mode

        )
        ### 10000 observations randomly sampled per year from train set
        SELECT 
            anon_id, order_id_coded as observation_id, index_time, 
            ordering_mode, label_blood
        FROM 
            (SELECT *,
                ROW_NUMBER() OVER  (PARTITION BY EXTRACT(YEAR FROM index_time)
                                    ORDER BY RAND()) 
                        AS seqnum
            FROM blood_culture_results 
            ) 
        WHERE
            seqnum <= 10000
        )
        """
        query_job = self.client.query(query)
        query_job.result()


class UrineCultureCohort(CohortBuilder):
    """
    Constructs a cohort table for predicting whether urine culture was positive.

    What we will do is find all urine cultures (irrespective of whether
    was triggered by urinalysis and train a model that predicts result of the
    culture. The index time will be defined as the time of the urine culture
    order if the urine culture was not triggered by a urinalysis, otherwise
    will be the time of the urinalysis order. 
    """

    def __init__(self, client, dataset_name, table_name,
                 working_project_id='mining-clinical-decisions'):
        """
        Initializes dataset_name and table_name for where cohort table will be
        saved on bigquery
        """
        super(UrineCultureCohort, self).__init__(client,
            dataset_name, table_name, working_project_id)

    def __call__(self):
        """
        Function that constructs a cohort table for predicting whether urine
        culture or urinalysis was positive. This will likely need to be 
        """
        query = f"""
        CREATE OR REPLACE TABLE 
        {self.project_id}.{self.dataset_name}.{self.table_name}
        AS (
        WITH urine_cultures AS (
        SELECT DISTINCT 
            anon_id, order_id_coded, order_time_utc, ordering_mode,
            MAX(CASE WHEN result_flag is NULL OR result_flag = "Normal" 
            Then 0 ELSE 1 END) label_urine
        FROM 
            som-nero-phi-jonc101.shc_core_2021.lab_result
        WHERE 
            proc_code = "LABURNC"
        GROUP BY 
            anon_id, order_id_coded, order_time_utc, ordering_mode
        ),
        uas as (
        SELECT DISTINCT 
            anon_id, order_id_coded, order_time_utc, proc_code
        FROM 
            som-nero-phi-jonc101.shc_core_2021.lab_result
        WHERE 
            proc_code = "LABUAPRN"
        ),
        matching_uas AS (
        SELECT DISTINCT 
            c.*, ua.proc_code ua_proc_code, ua.order_time_utc ua_order_time 
        FROM 
            urine_cultures c
        LEFT JOIN 
            uas ua
        USING 
            (anon_id)
        WHERE 
            ua.order_time_utc < c.order_time_utc OR ua.proc_code is NULL
        ),

        matching_uas_2 AS (
        SELECT DISTINCT 
            anon_id, order_id_coded observation_id, 
            CASE WHEN ua_proc_code IS NULL THEN order_time_utc
            WHEN TIMESTAMP_DIFF(order_time_utc, ua_order_time, HOUR) > 24 
            THEN order_time_utc
            ELSE ua_order_time END index_time, ordering_mode, label_urine,
        FROM 
            matching_uas
        ),

        cohort AS (
        SELECT DISTINCT
            anon_id, observation_id,
            FIRST_VALUE(index_time) 
            OVER (PARTITION BY observation_id ORDER BY index_time ASC)
            index_time,
            ordering_mode,
            label_urine
        FROM 
            matching_uas_2
        WHERE 
            EXTRACT(YEAR FROM index_time) BETWEEN 2015 and 2021
        )

        ### 10000 observations max randomly sampled per year
        SELECT 
            anon_id, observation_id, index_time, ordering_mode, label_urine
        FROM 
            (SELECT 
            *,
            ROW_NUMBER() OVER  (PARTITION BY EXTRACT(YEAR FROM index_time)
                                ORDER BY RAND()) 
                        AS seqnum
            FROM cohort 
            ) 
        WHERE
            seqnum <= 10000
        )
        """
        query_job = self.client.query(query)
        query_job.result()
