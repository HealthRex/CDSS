from typing import Optional, Callable
import socket
import time
import gspread
import random
import pandas as pd
import re
import gc
import ast
import numpy as np
import os
import json
import requests
from datetime import datetime
import pytz
import nltk
from nltk.tokenize import sent_tokenize
import spacy
import spacy.cli
import medspacy
from medspacy.context import ConTextRule
from medspacy.ner import TargetRule
from medspacy.visualization import visualize_ent
from transformers import AutoModelForCausalLM, AutoModel, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from sklearn.metrics.pairwise import cosine_similarity
import accelerate
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# nltk.download('punkt')
# spacy.cli.download("en_core_web_sm")

from helper_functions import (
    get_auth_keys,
    get_gsheet_data,
    load_chexpert_data,
    preprocess_data,
    preprocess_chexpert_data,
    process_list,
    chexpert_filter_ner_df,
    drop_duplicates_within_group,
    entity_location_search,
    extract_text_using_ner_location,
    run_context_extraction,
    send_email,
    send_error_email
)

pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def context_extraction(
        test,
        test_sample_size,
        subset_data,
        sample_dataset_size,
        save_named_entity_df,
        project_name,
        entity_df_filename,
        data_path,
        data_ner_output_path,
        umls_ner_output_path,
        save_folder_path,
        auth_keys_path,
        info_retrieval,
        save_extracted_outputs,
        gsheet_dict,
):
    extraction_timestamp = datetime.now()
    extraction_timestamp = extraction_timestamp.replace(tzinfo=pytz.utc)
    extraction_timestamp = extraction_timestamp.astimezone(pytz.timezone('US/Pacific'))
    extraction_timestamp = extraction_timestamp.strftime('%Y-%m-%d_%H:%M:%S')

    print(f"\nExpanding Paths")
    data_path = os.path.expanduser(data_path)
    data_ner_output_path = os.path.expanduser(data_ner_output_path)
    umls_ner_output_path = os.path.expanduser(umls_ner_output_path)
    save_folder_path = os.path.expanduser(save_folder_path)
    gsheet_dict["service_account_path"] = os.path.expanduser(gsheet_dict["service_account_path"])
    auth_keys_data = get_auth_keys(auth_keys_path=os.path.expanduser(auth_keys_path))
    print(f"Paths Expanded")

    print(f"\nLoading data")
    data_df = load_chexpert_data(data_path, subset_data, sample_dataset_size)
    print(data_df)
    print(f"Data Pull Successful")

    print(f"\nPre-processing Data")
    data_df = preprocess_chexpert_data(
        data_df=data_df,
        column_to_process='text',
        remove_hyphens=True,
        remove_underscores=True,
    )
    print(f"Pre-processing Complete")
    
    print(f"\nGetting Feature")
    selected_features_df = get_gsheet_data(
        service_acc_path=gsheet_dict["service_account_path"],
        gsheet=gsheet_dict["feature_gsheet"],
        gsheet_sheet=gsheet_dict["feature_gsheet_sheet"]
    )
    selected_features_df = selected_features_df[selected_features_df['filter']==1]
    target_word_list = selected_features_df['target_word'].str.lower()
    print(f"Selected Features:\n{selected_features_df}")

    print(f"\nLoading Entity NER/Synonym Data")
    print(f"Loading Text LLM+Cosine Similarity Filtered NER Data")
    data_ner_output = pd.read_csv(data_ner_output_path)
    data_ner_output['target_word'] = data_ner_output['target_word'].str.lower()
    data_ner_output = data_ner_output[data_ner_output['target_word'].isin(target_word_list)]
    data_ner_output['ner_list'] = data_ner_output['ner_list'].apply(lambda x: ast.literal_eval(x))
    data_ner_output['ner_list'] = data_ner_output['ner_list'].apply(process_list)
    print(f"Loading UMLS NER Data")
    umls_ner_output = pd.read_csv(umls_ner_output_path)
    umls_ner_output = umls_ner_output[['target_word', 'ner_output']]
    umls_ner_output['target_word'] = umls_ner_output['target_word'].str.lower()
    umls_ner_output['ner_output'] = umls_ner_output['ner_output'].apply(lambda x: ast.literal_eval(x))
    umls_ner_output['ner_output'] = umls_ner_output['ner_output'].apply(process_list)
    umls_ner_output.rename(columns={'ner_output': 'ner_list'}, inplace=True)
    print(f"Loading LLM Augmentation Data")
    llm_augmentations = get_gsheet_data(
        service_acc_path=gsheet_dict["service_account_path"],
        gsheet=gsheet_dict["synonym_gsheet"],
        gsheet_sheet=gsheet_dict["synonym_gsheet_sheet"]
    )
    llm_augmentations['target_word'] = llm_augmentations['target_word'].str.lower()
    llm_augmentations = llm_augmentations[llm_augmentations['target_word'].isin(target_word_list)]
    llm_augmentations['ner_list'] = llm_augmentations['ner_list'].apply(lambda x: ast.literal_eval(x))
    llm_augmentations['ner_list'] = llm_augmentations['ner_list'].apply(process_list)
    print(f"All NER Data Loaded")
    
    print(f"\nGenerate Final Named Entity DataFrame")
    named_entity_df = pd.concat([data_ner_output, umls_ner_output, llm_augmentations])
    named_entity_df = named_entity_df.explode('ner_list').reset_index(drop=True)
    named_entity_df = named_entity_df.groupby('target_word', group_keys=False).apply(lambda x: x.drop_duplicates(subset='ner_list', keep='first')).reset_index(drop=True)
    if project_name == 'chexpert':
        print(f"Running Chexpert NER Filter")
        named_entity_df = chexpert_filter_ner_df(named_entity_df) # only for chexpert dataset
    print(f"Generated Final Named Entity DataFrame")

    if save_named_entity_df:
        print(f"Saving named_entity_df")
        entity_df_filename = entity_df_filename.format(project_name=project_name, timestamp=extraction_timestamp)
        named_entity_df.to_csv(entity_df_filename, index=False)

    for target_word in target_word_list:
        run_context_extraction(
            test=test,
            data_df=data_df,
            named_entity_df=named_entity_df,
            target_word=target_word,
            info_retrieval=info_retrieval,
            save_extracted_outputs=save_extracted_outputs,
            data_path=data_path,
            extraction_timestamp=extraction_timestamp,
            save_folder_path=save_folder_path,
        )

    print(f"\nSending user task completion email")
    hostname = socket.gethostname()
    send_email(
        smtp_server="smtp.gmail.com",
        smtp_password=auth_keys_data['GMAIL_SMTP_PASSWORD'][0],
        from_email="iv.lopez.machine.learning@gmail.com",
        to_email="lopezivan256@gmail.com",
        message_subject=f"{hostname}: VM Task Completed",
        email_text=f"Your VM task has successfully completed."
    )

if __name__ == "__main__":
    test=False
    test_sample_size=None
    subset_data=True
    sample_dataset_size=2500

    save_named_entity_df=True
    project_name='chexpert'
    entity_df_filename="/home/ivlopez/llm_data/mimic_llm_output/ner_output/chexpert_dataset/{project_name}_entity_df_{timestamp}.csv"
    data_path="~/llm_data/exp_mimic_data/processed_data/chexpert_filtered.csv"
    data_ner_output_path="/home/ivlopez/llm_data/mimic_llm_output/ner_output/chexpert_dataset/final_llm_cosine_sim_flan_t5_2024-02-14_16:24:18_mimic_chexpert_filtered_flan_t5_ner_output_2024-01-28_06:46:58.csv"
    umls_ner_output_path="/home/ivlopez/llm_data/mimic_llm_output/ner_output/chexpert_dataset/umls_chexpert_flan_t5_ner_output_2024-02-14_10:10:38.csv"
    save_folder_path="/home/ivlopez/llm_data/mimic_llm_output/extracted_output/chexpert_dataset"
    info_retrieval={
        "n_words_before_ner": 150,
        "n_words_after_ner": 150
    }
    save_extracted_outputs=True
    
    auth_keys_path="~/local_credentials/auth_keys.json"
    gsheet_dict={
        "feature_gsheet_sheet": "MIMIC Chexpert Feature List",
        "system_content_messages_gsheet_sheet": None,
        "synonym_gsheet_sheet": "Mimic Chexpert LLM Augmentation",

        "service_account_path": "~/local_credentials/google_service_account.json",
        "feature_gsheet": "LLM Features",
        "synonym_gsheet": "LLM Synonyms",
        }
    try:
        context_extraction(
            test=test,
            test_sample_size=test_sample_size,
            subset_data=subset_data,
            sample_dataset_size=sample_dataset_size,
            data_path=data_path,
            save_named_entity_df=save_named_entity_df,
            project_name=project_name,
            entity_df_filename=entity_df_filename,
            data_ner_output_path=data_ner_output_path,
            umls_ner_output_path=umls_ner_output_path,
            save_folder_path=save_folder_path,
            auth_keys_path=auth_keys_path,
            info_retrieval=info_retrieval,
            save_extracted_outputs=save_extracted_outputs,
            gsheet_dict=gsheet_dict,
            )
    except Exception as e:
        send_error_email()
        raise