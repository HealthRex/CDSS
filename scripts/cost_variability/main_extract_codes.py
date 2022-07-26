import pdb
import argparse
import sys
import os
import utils.extract_codes as ext_cd
import logging

sys.path.append(os.getcwd())
parser = argparse.ArgumentParser()
parser.add_argument("--table_type", type=str, default='diagnosis', choices = ['diagnosis', 'medication', 'procedure', 'lab'])    

parser.add_argument("--med_patient_id_field_name", type=str, default='anon_id')    
parser.add_argument("--med_code_field_name", type=str, default='pharm_class_abbr')    
parser.add_argument("--med_time_field_name", type=str, default='order_time_jittered') 

parser.add_argument("--proc_patient_id_field_name", type=str, default='anon_id')    
parser.add_argument("--proc_time_field_name", type=str, default='ordering_date_jittered')    
parser.add_argument("--proc_code_field_name", type=str, default='proc_id')    

parser.add_argument("--lab_patient_id_field_name", type=str, default='anon_id')    
parser.add_argument("--lab_time_field_name", type=str, default='order_time_utc')    
# parser.add_argument("--lab_code_field_name", type=str, default='proc_code')    
parser.add_argument("--lab_code_field_name", type=str, default='base_name')    


parser.add_argument("--icd10_field_name", type=str, default='icd10')    
parser.add_argument("--icd9_field_name", type=str, default='icd9')    
parser.add_argument("--diag_time_field_name", type=str, default='start_date_utc')    
parser.add_argument("--diag_patient_id_field_name", type=str, default='anon_id')    




parser.add_argument("--display_step", type=int, default=1000000)    

client_name ="som-nero-phi-jonc101-secure"

if  parser.parse_args().table_type == "diagnosis":
    query_string = "SELECT * FROM `som-nero-phi-jonc101-secure.proj_cms_sf.costUB_with_anonid_filtered_diagnosis` A ORDER BY A.anon_id, A.start_date_utc"
    icd_to_ccs_table_query = "SELECT * FROM `mining-clinical-decisions.mapdata.ahrq_ccsr_diagnosis`"
    icd9_to_icd10_query = "SELECT * FROM `mining-clinical-decisions.mapdata.icd9gem`"
    ext_cd.extract_diagnosis(client_name
                            , query_string
                            , icd_to_ccs_table_query
                            , icd9_to_icd10_query
                            , parser.parse_args().icd10_field_name
                            , parser.parse_args().icd9_field_name
                            , parser.parse_args().diag_time_field_name
                            , parser.parse_args().diag_patient_id_field_name                            
                            , parser.parse_args().display_step)
elif  parser.parse_args().table_type == "medication":
    query_string = "SELECT * FROM `som-nero-phi-jonc101-secure.proj_cms_sf.costUB_with_anonid_filtered_order_med` A ORDER BY A.anon_id, A.order_time_jittered"
    unique_medication_id_query = "SELECT * FROM `som-nero-phi-jonc101-secure.proj_cms_sf.unique_pharm_class_abbr` A WHERE A.pharm_class_abbr is not NULL"
    ext_cd.extract_medication(client_name
                            , query_string
                            , unique_medication_id_query
                            , parser.parse_args().med_code_field_name
                            , parser.parse_args().med_time_field_name
                            , parser.parse_args().med_patient_id_field_name                                                        
                            , parser.parse_args().display_step)

elif  parser.parse_args().table_type == "procedure":
    query_string = "SELECT * FROM `som-nero-phi-jonc101-secure.proj_cms_sf.costUB_with_anonid_filtered_order_proc` A ORDER BY A.anon_id, A.ordering_date_jittered"
    unique_proc_id_query = "SELECT * FROM `som-nero-phi-jonc101-secure.proj_cms_sf.unique_proc_ids` A WHERE A.proc_id is not NULL"    
    num_lines_query = "SELECT COUNT(*) FROM `som-nero-phi-jonc101-secure.proj_cms_sf.costUB_with_anonid_filtered_order_proc`"
    ext_cd.extract_procedure(client_name
                            , query_string
                            , unique_proc_id_query
                            , num_lines_query
                            , parser.parse_args().proc_code_field_name
                            , parser.parse_args().proc_time_field_name
                            , parser.parse_args().proc_patient_id_field_name                             
                            , parser.parse_args().display_step)

elif  parser.parse_args().table_type == "lab":
    query_string = "SELECT * FROM `som-nero-phi-jonc101-secure.proj_cms_sf.costUB_with_anonid_filtered_lab_result` A ORDER BY A.anon_id, A.order_time_utc"
    unique_lab_id_query = "SELECT * FROM `som-nero-phi-jonc101-secure.proj_cms_sf.unique_base_name` A WHERE A.base_name is not NULL"    
    unique_lab_result_flag = "SELECT * FROM `som-nero-phi-jonc101-secure.proj_cms_sf.unique_lab_result_flag` A "    
    num_lines_query = "SELECT COUNT(*) FROM `som-nero-phi-jonc101-secure.proj_cms_sf.costUB_with_anonid_filtered_lab_result`"
    
    ext_cd.extract_labs(client_name
                            , query_string
                            , unique_lab_id_query
                            , unique_lab_result_flag
                            , num_lines_query
                            , parser.parse_args().lab_code_field_name
                            , parser.parse_args().lab_time_field_name
                            , parser.parse_args().lab_patient_id_field_name                             
                            , parser.parse_args().display_step)
