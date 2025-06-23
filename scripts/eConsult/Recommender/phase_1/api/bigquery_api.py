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
        result_type: Optional[Union[str, List[str]]] = None,  # Accept str, list, or None
        limit: int = 10,
        year: int = 2024
    ) -> pd.DataFrame:
        """
    Get common orders based on patient parameters and filters.
    result_type can be a string, a list of strings, or None (all).
    Args:
        params (Dict): Dictionary containing patient parameters:
            - patient_age (Optional[int]): Patient age
            - patient_gender (Optional[str]): Patient gender
            - icd10_code (Optional[str]): ICD-10 diagnosis code
        min_patients_for_non_rare_items (int): Minimum number of patients for non-rare items.
        result_type (Optional[Union[str, List[str]]]): 
            One or more result types to return. 
            Options are "lab", "med", and/or "procedure". 
            - If None (default), returns all three types concatenated.
            - If a string, returns only that type.
            - If a list, returns all specified types concatenated.
        limit (int): Maximum number of results to return for each result type.
        year (int): Year of the dataset to use (2022, 2023, or 2024).
        
    Returns:
        pd.DataFrame: Results showing the most common orders, with an added column 'result_type' indicating the source.
        """
        try:
            # Validate year
            if year not in [2022, 2023, 2024]:
                raise ValueError("Year must be between 2022 and 2024")
            
            # Standardize result_type to a list
            allowed_types = {"lab", "med", "procedure"}
            if result_type is None:
                result_types = ["lab", "med", "procedure"]
            elif isinstance(result_type, str):
                if result_type not in allowed_types:
                    raise ValueError(f"result_type must be one of {allowed_types}")
                result_types = [result_type]
            elif isinstance(result_type, list):
                for t in result_type:
                    if t not in allowed_types:
                        raise ValueError(f"Each type in result_type must be one of {allowed_types}")
                result_types = result_type
            else:
                raise ValueError("result_type must be str, list[str], or None")
            
            all_results = []
            for rt in result_types:
                patient_age = params.get('patient_age')
                patient_gender = params.get('patient_gender')
                icd10_code = params.get('icd10_code')

                age_filter = ""
                if patient_age is not None:
                    if patient_age < 18:
                        age_filter = "AND DATE_DIFF(DATE(appt_when_jittered_utc), DATE(birth_date_jittered_utc), YEAR) BETWEEN 0 AND 17"
                    elif patient_age < 45:
                        age_filter = "AND DATE_DIFF(DATE(appt_when_jittered_utc), DATE(birth_date_jittered_utc), YEAR) BETWEEN 18 AND 44"
                    elif patient_age < 65:
                        age_filter = "AND DATE_DIFF(DATE(appt_when_jittered_utc), DATE(birth_date_jittered_utc), YEAR) BETWEEN 45 AND 64"
                    else:
                        age_filter = "AND DATE_DIFF(DATE(appt_when_jittered_utc), DATE(birth_date_jittered_utc), YEAR) >= 65"

                gender_filter = ""
                if patient_gender is not None:
                    gender_filter = f"AND LOWER(demogx.gender) = LOWER('{patient_gender}')"

                diagnosis_filter = ""
                if icd10_code is not None:
                    diagnosis_filter = f"AND dx.icd10 = '{icd10_code}'"

                logger.info(f"Building query for params={params}, type={rt}, year={year}")

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

                if rt == "lab":
                    query += f"""
                    ,cohortEncounterProc AS (
                        select 
                            op.proc_code, op.description, 
                            # cohortEnc.encounter_department,
                            # dm.specialty as order_proc_department,
                            count(distinct cohortEnc.anon_id) as nPatients, 
                            count(distinct cohortEnc.encounterId) as nEncounters
                        from cohortEncounter as cohortEnc
                        join `shc_core_{year}.order_proc` as op on cohortEnc.encounterId = op.pat_enc_csn_id_coded 
                        left join  `shc_core_{year}.dep_map` dm ON op.department_id = dm.department_id
                        where op.ordering_mode = 'Outpatient'
                        and op.order_type IN ('Lab', 'Imaging', 'Point of Care Testing', 'Pathology', 'Microbiology Culture')
                        and dm.specialty IN ('Infectious Diseases', 'Endocrinology', 'Hematology')
                        group by op.proc_code, op.description 
                        # ,dm.specialty, cohortEnc.encounter_department
                    )
                    SELECT 
                        proc_code as itemId, 
                        description,
                        # order_proc_department as order_procdepartment,
                        # encounter_department as encounter_department,
                        round(p.nPatients/c.nPatients *100,2) as patientRate,
                        round(p.nEncounters/c.nEncounters * 100,2) as encounterRate,
                        p.nPatients as nPatientscohortItem,
                        p.nEncounters as nEncounterscohortItem,
                        c.nPatients as nPatientsCohortTotal,
                        c.nEncounters as nEncountersCohortTotal,
                        'lab' as result_type
                    FROM cohortEncounterProc p
                    CROSS JOIN cohortEncounterCount c
                    CROSS JOIN query_params qp
                    WHERE p.nPatients > qp.minPatientsForNonRareItems
                    ORDER BY p.nPatients DESC
                    LIMIT {limit}
                    """
                elif rt == "med":
                    query += f"""
                    ,cohortEncounterMed AS (
                        select 
                            # om.medication_id, 
                            # om.med_description,
                            mm.rxcui_str as medication_description,
                            # cohortEnc.encounter_department,
                            count(distinct cohortEnc.anon_id) as nPatients, 
                            count(distinct cohortEnc.encounterId) as nEncounters
                        from cohortEncounter as cohortEnc
                        join `shc_core_{year}.order_med` as om on cohortEnc.encounterId = om.pat_enc_csn_id_coded
                        left join  `shc_core_{year}.mapped_meds` mm ON om.medication_id = mm.medication_id
                        cross join query_params qp
                        where om.order_class_c not in UNNEST(qp.excludeMedOrderClass)
                        and om.ordering_mode = 'Outpatient'
                        and (mm.rxcui_str IS NOT NULL OR mm.generic_name IS NOT NULL)
                        group by mm.rxcui_str
                        # group by om.medication_id, om.med_description 
                        # ,cohortEnc.encounter_department
                    )
                    SELECT 
                        medication_description as itemId,
                        medication_description as description,
                        # encounter_department as department,
                        round(m.nPatients/c.nPatients *100,2) as patientRate,
                        round(m.nEncounters/c.nEncounters * 100,2) as encounterRate,
                        m.nPatients as nPatientscohortItem,
                        m.nEncounters as nEncounterscohortItem,
                        c.nPatients as nPatientsCohortTotal,
                        c.nEncounters as nEncountersCohortTotal,
                        'med' as result_type
                    FROM cohortEncounterMed m
                    CROSS JOIN cohortEncounterCount c
                    CROSS JOIN query_params qp
                    WHERE m.nPatients > qp.minPatientsForNonRareItems
                    ORDER BY m.nPatients DESC
                    LIMIT {limit}
                    """
                elif rt == "procedure":
                    query += f"""
                    ,cohortEncounterProcedure AS (
                        select 
                            proc.code,
                            proc.description,
                            # cohortEnc.encounter_department,
                            count(distinct proc.anon_id) as nPatients, 
                            count(distinct proc.pat_enc_csn_id_coded) as nEncounters
                        from cohortEncounter as cohortEnc
                        join `som-nero-phi-jonc101.shc_core_{year}.procedure` as proc
                            on cohortEnc.anon_id = proc.anon_id
                            and cohortEnc.encounterId = proc.pat_enc_csn_id_coded
                        group by proc.description, proc.code
                        # , cohortEnc.encounter_department
                    )
                    SELECT 
                        code as itemId,
                        description as description,
                        # encounter_department as department,
                        round(p.nPatients/c.nPatients *100,2) as patientRate,
                        round(p.nEncounters/c.nEncounters * 100,2) as encounterRate,
                        p.nPatients as nPatientscohortItem,
                        p.nEncounters as nEncounterscohortItem,
                        c.nPatients as nPatientsCohortTotal,
                        c.nEncounters as nEncountersCohortTotal,
                        'procedure' as result_type
                    FROM cohortEncounterProcedure p
                    CROSS JOIN cohortEncounterCount c
                    CROSS JOIN query_params qp
                    WHERE p.nPatients > qp.minPatientsForNonRareItems
                    ORDER BY p.nPatients DESC
                    LIMIT {limit}
                    """
                else:
                    raise ValueError("Unknown result_type")

                logger.info("Executing BigQuery query...")
                query_job = self.client.query(query)
                results = query_job.to_dataframe()
                logger.info(f"Query completed successfully. Returned {len(results)} rows.")
                all_results.append(results)

            # Concatenate and return as a single DataFrame
            if all_results:
                return pd.concat(all_results, ignore_index=True)
            else:
                return pd.DataFrame([])  # empty if nothing

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

    df_all = api.get_orders(params)
    df_lab = api.get_orders(params, result_type="lab")
    df_mix = api.get_orders(params, result_type=["lab", "procedure"])


    # Example with partial parameters
    partial_params = {
        'patient_age': 55,
        'patient_gender': None,  # No gender restriction
        'icd10_code': None      # No diagnosis restriction
    }
    df_all_partial = api.get_orders(params)
    df_lab_partial = api.get_orders(params, result_type="lab")
    df_mix_partial = api.get_orders(params, result_type=["lab", "procedure"])
    
    # Print results
    # print("all Results:")
    # df_all.to_csv("all_results_sample.csv", index=False)
    # print(df_all)
    # print(df_all_partial)
    # print("lab Results:")
    # df_lab.to_csv("lab_results_sample.csv", index=False)
    # print(df_lab)

    # print("mix Results:")
    # print(df_mix)
    # df_mix.to_csv("mix_results_sample.csv", index=False)