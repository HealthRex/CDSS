from google.cloud import bigquery
import pandas as pd
from typing import List, Optional, Union, Dict
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
        
    def get_orders(
        self,
        params: Dict[str, Union[str, int, None]],
        min_patients_for_non_rare_items: int = 10,
        result_type: str = "med",  # Options: "proc", "med"
        limit: int = 100,
        year: int = 2024  # Default to 2024 if not specified
    ) -> pd.DataFrame:
        """Get common orders based on patient parameters and filters.
        
        Args:
            params (Dict): Dictionary containing patient parameters:
                - patient_age (Optional[int]): Patient age
                - patient_gender (Optional[str]): Patient gender
                - icd10_code (Optional[str]): ICD-10 diagnosis code
            min_patients_for_non_rare_items (int): Minimum number of patients for non-rare items
            result_type (str): Type of results to return ("proc" or "med")
            limit (int): Maximum number of results to return
            year (int): Year of the dataset to use (2022-2024)
            
        Returns:
            pd.DataFrame: Results showing most common orders
        """
        try:
            # Validate year
            if year not in [2022, 2023, 2024]:
                raise ValueError("Year must be between 2022 and 2024")
            
            # Extract parameters
            patient_age = params.get('patient_age')
            patient_gender = params.get('patient_gender')
            icd10_code = params.get('icd10_code')
            
            # Build age filter if provided
            age_filter = ""
            # if patient_age is not None:
                # age_filter = f"AND DATE_DIFF(DATE(appt_when_jittered_utc), DATE(birth_date_jittered_utc), YEAR) = {patient_age}"
            if patient_age is not None:
                # Map single age to age group
                if patient_age < 18:
                    age_filter = "AND DATE_DIFF(DATE(appt_when_jittered_utc), DATE(birth_date_jittered_utc), YEAR) >= 0 AND DATE_DIFF(DATE(appt_when_jittered_utc), DATE(birth_date_jittered_utc), YEAR) <= 17"
                elif patient_age < 45:
                    age_filter = "AND DATE_DIFF(DATE(appt_when_jittered_utc), DATE(birth_date_jittered_utc), YEAR) >= 18 AND DATE_DIFF(DATE(appt_when_jittered_utc), DATE(birth_date_jittered_utc), YEAR) <= 44"
                elif patient_age < 65:
                    age_filter = "AND DATE_DIFF(DATE(appt_when_jittered_utc), DATE(birth_date_jittered_utc), YEAR) >= 45 AND DATE_DIFF(DATE(appt_when_jittered_utc), DATE(birth_date_jittered_utc), YEAR) <= 64"
                else:
                    age_filter = "AND DATE_DIFF(DATE(appt_when_jittered_utc), DATE(birth_date_jittered_utc), YEAR) >= 65"
            
            # Build gender filter if provided
            gender_filter = ""
            if patient_gender is not None:
                gender_filter = f"AND LOWER(demogx.gender) = LOWER('{patient_gender}')"
            
            # Build diagnosis filter if provided
            diagnosis_filter = ""
            if icd10_code is not None:
                diagnosis_filter = f"AND dx.icd10 = '{icd10_code}'"
            
            logger.info(f"Building query for params={params}, type={result_type}, year={year}")
            
            query = f"""
            WITH query_params AS (
                select 
                    ['3'] as excludeMedOrderClass,
                    {min_patients_for_non_rare_items} as minPatientsForNonRareItems
            ),

            cohortEncounter AS (
                select distinct
                    enc.anon_id, 
                    demogx.birth_date_jittered_utc as birthDateTime,
                    demogx.gender as gender,
                    pat_enc_csn_id_coded as encounterId,
                    appt_when_jittered_utc as encounterDateTime,
                    dx.icd9, dx.icd10, dx_name,
                    dm.specialty as encounter_department,
                    DATE_DIFF(DATE(appt_when_jittered_utc), DATE(birth_date_jittered_utc), YEAR) as age_when_encountered
                from `shc_core_{year}.encounter` as enc
                    join `shc_core_{year}.diagnosis` as dx on enc.pat_enc_csn_id_coded = dx.pat_enc_csn_id_jittered
                    left join  `shc_core_{year}.dep_map` dm ON enc.department_id = dm.department_id
                    left join `shc_core_{year}.demographic` as demogx on demogx.anon_id = enc.anon_id
                # where visit_type like 'NEW PATIENT%'
                where LOWER(enc.appt_type) IN ('appointment', 'office visit', 'telemedicine')
                and appt_status = 'Completed'
                {diagnosis_filter}
                {gender_filter}
                {age_filter}
            ),

            cohortEncounterCount AS (
                select count(distinct anon_id) as nPatients, count(distinct encounterId) as nEncounters
                from cohortEncounter
            )"""
            
            if result_type == "proc":
                query += f"""
                ,cohortEncounterProc AS (
                    select 
                        op.proc_code, op.description, cohortEnc.encounter_department,
                        dm.specialty as order_proc_department,
                        count(distinct cohortEnc.anon_id) as nPatients, 
                        count(distinct cohortEnc.encounterId) as nEncounters
                    from cohortEncounter as cohortEnc
                    join `shc_core_{year}.order_proc` as op on cohortEnc.encounterId = op.pat_enc_csn_id_coded 
                    left join  `shc_core_{year}.dep_map` dm ON op.department_id = dm.department_id
                    where op.ordering_mode = 'Outpatient'
                    and op.order_type IN ('Lab', 'Imaging', 'Point of Care Testing', 'Pathology', 'Microbiology Culture')
                    and dm.specialty IN ('Infectious Diseases', 'Endocrinology', 'Hematology')
                    group by op.proc_code, op.description, dm.specialty, cohortEnc.encounter_department
                )
                SELECT 
                    proc_code as itemId, 
                    description,
                    order_proc_department as order_procdepartment,
                    encounter_department as encounter_department,
                    round(p.nPatients/c.nPatients *100,2) as patientRate,
                    round(p.nEncounters/c.nEncounters * 100,2) as encounterRate,
                    p.nPatients as nPatientscohortItem,
                    p.nEncounters as nEncounterscohortItem,
                    c.nPatients as nPatientsCohortTotal,
                    c.nEncounters as nEncountersCohortTotal
                FROM cohortEncounterProc p
                CROSS JOIN cohortEncounterCount c
                CROSS JOIN query_params qp
                WHERE p.nPatients > qp.minPatientsForNonRareItems
                ORDER BY p.nPatients DESC
                """
            elif result_type == "med":
                query += f"""
                ,cohortEncounterMed AS (
                    select 
                        om.medication_id, 
                        om.med_description,
                        cohortEnc.encounter_department,
                        count(distinct cohortEnc.anon_id) as nPatients, 
                        count(distinct cohortEnc.encounterId) as nEncounters
                    from cohortEncounter as cohortEnc
                    join `shc_core_{year}.order_med` as om on cohortEnc.encounterId = om.pat_enc_csn_id_coded
                    left join  `shc_core_{year}.mapped_meds` mm ON om.medication_id = mm.medication_id
                    cross join query_params qp
                    where om.order_class_c not in UNNEST(qp.excludeMedOrderClass)
                    and om.ordering_mode = 'Outpatient'
                    and (mm.rxcui_str IS NOT NULL OR mm.generic_name IS NOT NULL)
                    group by om.medication_id, om.med_description, cohortEnc.encounter_department
                )
                SELECT 
                    medication_id as itemId,
                    med_description as description,
                    encounter_department as department,
                    round(m.nPatients/c.nPatients *100,2) as patientRate,
                    round(m.nEncounters/c.nEncounters * 100,2) as encounterRate,
                    m.nPatients as nPatientscohortItem,
                    m.nEncounters as nEncounterscohortItem,
                    c.nPatients as nPatientsCohortTotal,
                    c.nEncounters as nEncountersCohortTotal
                FROM cohortEncounterMed m
                CROSS JOIN cohortEncounterCount c
                CROSS JOIN query_params qp
                WHERE m.nPatients > qp.minPatientsForNonRareItems
                ORDER BY m.nPatients DESC
                """
            
            query += f" LIMIT {limit}"
            
            logger.info("Executing BigQuery query...")
            query_job = self.client.query(query)
            results = query_job.to_dataframe()
            logger.info(f"Query completed successfully. Returned {len(results)} rows.")
            return results
            
        except Exception as e:
            logger.error(f"Error in get_orders: {str(e)}", exc_info=True)
            raise Exception(f"Failed to execute BigQuery query: {str(e)}") 

if __name__ == "__main__":
    # Initialize the API
    api = BigQueryAPI()
    
    # Example with all parameters
    params = {
        'patient_age': 55,
        'patient_gender': 'male',
        'icd10_code': 'I10'
    }

    # Get medication orders
    med_results = api.get_orders(
        params=params,
        result_type='med',
        limit=100
    )

    # Get procedure orders
    proc_results = api.get_orders(
        params=params,
        result_type='proc',
        limit=100
    )

    # Example with partial parameters
    partial_params = {
        'patient_age': 55,
        'patient_gender': None,  # No gender restriction
        'icd10_code': None      # No diagnosis restriction
    }
    
    # Print results
    print("\nMedication Results:")
    print(med_results)
    print("\nProcedure Results:")
    print(proc_results)