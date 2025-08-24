from google.cloud import bigquery
import pandas as pd
from typing import List, Optional, Union
import logging

logger = logging.getLogger(__name__)

class BigQueryAPI:
    def __init__(self, project_id: str = "som-nero-phi-jonc101"):
        """Initialize the BigQuery API client.
        
        Args:
            project_id (str): Google Cloud project ID
        """
        try:
            self.client = bigquery.Client(project_id)
            logger.info(f"Successfully initialized BigQuery client for project {project_id}")
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery client: {str(e)}")
            raise Exception(f"Failed to initialize BigQuery client. Please ensure you have valid Google Cloud credentials set up. Error: {str(e)}")
        
    def get_immediate_orders(
        self,
        diagnosis_codes: List[str],
        patient_gender: Optional[str] = None,
        min_patients_for_non_rare_items: int = 10,
        result_type: str = "med",  # Options: "proc", "med"
        limit: int = 10,
        year: int = 2021  # Default to 2021 if not specified
    ) -> pd.DataFrame:
        """Get common immediate orders based on diagnosis/complaint and patient gender.
        
        Args:
            diagnosis_codes (List[str]): List of diagnosis codes to analyze
            patient_gender (Optional[str]): Patient gender to filter by (e.g. 'Male', 'Female')
            min_patients_for_non_rare_items (int): Minimum number of patients for non-rare items
            result_type (str): Type of results to return ("proc" or "med")
            limit (int): Maximum number of results to return
            year (int): Year of the dataset to use (2021-2024)
            
        Returns:
            pd.DataFrame: Results showing most common immediate orders
        """
        try:
            # Validate year
            if year not in [2021, 2022, 2023, 2024]:
                raise ValueError("Year must be between 2021 and 2024")
                
            # Format parameters for the query
            gender_param = f"'{patient_gender}'" if patient_gender else "NULL"
            
            logger.info(f"Building query for diagnosis_codes={diagnosis_codes}, gender={patient_gender}, type={result_type}, year={year}")
            
            query = f"""
            WITH 
            params AS 
            (
                select 
                    {min_patients_for_non_rare_items} as minPatientsForNonRareItems,
                    {gender_param} as targetGender
            ),
            
            targetEncounters AS
            (
                select distinct
                    enc.anon_id, 
                    enc.pat_enc_csn_id_coded as encounterId,
                    enc.appt_when_jittered as encounterDateTime,
                    demo.gender
                from `shc_core_{year}.encounter` as enc
                    join shc_core_{year}.diagnosis as dx on enc.pat_enc_csn_id_coded = dx.pat_enc_csn_id_jittered
                    join `shc_core_{year}.demographic` as demo on enc.anon_id = demo.anon_id,
                    params
                where visit_type like 'NEW PATIENT%'
                and appt_status = 'Completed'
                and dx.icd10 in ({','.join([f"'{code}'" for code in diagnosis_codes])})
                and (params.targetGender is NULL or demo.gender = params.targetGender)
            ),
            
            encounterCount AS
            (
                select count(distinct anon_id) as totalPatients, count(distinct encounterId) as totalEncounters
                from targetEncounters
            )
            """
            
            if result_type == "proc":
                query += f"""
                SELECT * FROM (
                    WITH
                    encounterProc AS
                    (
                        select 
                            op.proc_code, op.description, 
                            count(distinct enc.anon_id) as itemPatients, 
                            count(distinct enc.encounterId) as itemEncounters
                        from targetEncounters as enc
                        join `shc_core_{year}.order_proc` as op on enc.encounterId = op.pat_enc_csn_id_coded 
                        group by proc_code, description
                    )
                    SELECT 
                        proc_code as itemId, 
                        description,
                        (itemEncounters / totalEncounters) as encounterRate,
                        itemEncounters as nEncounters,
                        totalEncounters,
                        itemPatients as nPatients,
                        totalPatients
                    FROM encounterProc, encounterCount, params
                    WHERE itemPatients > params.minPatientsForNonRareItems
                    ORDER BY itemEncounters DESC, itemId, description
                )
                """
            elif result_type == "med":
                # Handle different year schemas for order_class_c
                if year == 2021:
                    order_class_filter = "where order_class_c != 3"  # For 2021, order_class_c is an integer
                else:
                    order_class_filter = "where order_class_c != '3'"  # For 2022+, order_class_c is a string
                
                query += f"""
                SELECT * FROM (
                    WITH
                    encounterMed AS
                    (
                        select 
                            om.medication_id, om.med_description,
                            count(distinct enc.anon_id) as itemPatients, 
                            count(distinct enc.encounterId) as itemEncounters
                        from targetEncounters as enc
                        join `shc_core_{year}.order_med` as om on enc.encounterId = om.pat_enc_csn_id_coded
                        {order_class_filter}  -- Exclude historical medications
                        group by medication_id, med_description
                    )
                    SELECT 
                        medication_id as itemId, 
                        med_description as description,
                        (itemEncounters / totalEncounters) as encounterRate,
                        itemEncounters as nEncounters,
                        totalEncounters,
                        itemPatients as nPatients,
                        totalPatients
                    FROM encounterMed, encounterCount, params
                    WHERE itemPatients > params.minPatientsForNonRareItems
                    ORDER BY itemEncounters DESC, itemId, description
                )
                """
            
            query += f" LIMIT {limit}"
            
            logger.info("Executing BigQuery query...")
            query_job = self.client.query(query)
            results = query_job.to_dataframe()
            logger.info(f"Query completed successfully. Returned {len(results)} rows.")
            return results
            
        except Exception as e:
            logger.error(f"Error in get_immediate_orders: {str(e)}", exc_info=True)
            raise Exception(f"Failed to execute BigQuery query: {str(e)}") 