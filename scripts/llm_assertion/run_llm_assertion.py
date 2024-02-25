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
import pytz
from datetime import datetime
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
    preprocess_data,
    model_generate_system_content,
    model_create_single_feature_llm_dialogs,
    extract_llm_assertion_output,
    model_assertion,
    save_llm_outputs,
    send_email,
    send_error_email
)

pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def llm_assertion(
        test,
        test_sample_size,
        subset_data,
        subset_sample_size,
        target_word_list,
        initial_data_path,
        end_data_path,
        save_folder_path,
        auth_keys_path,
        synonyms_path,
        assertion_model_name,
        assertion_use_flash_attention_2,
        assertion_torch_dtype,
        assertion_temperature,
        assertion_do_sample,
        assertion_top_p,
        assertion_max_seq_len,
        assertion_max_new_tokens,
        device_map,
        delimiter,
        gsheet_dict,
):
    
    print(f"\nExpanding Paths")
    save_folder_path = os.path.expanduser(save_folder_path)
    gsheet_dict["service_account_path"] = os.path.expanduser(gsheet_dict["service_account_path"])
    auth_keys_data = get_auth_keys(auth_keys_path=os.path.expanduser(auth_keys_path))
    print(f"Paths Expanded")

    print(f"\nBuilding {assertion_model_name} Model")
    print(f"Loading tokenizer")
    tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=assertion_model_name, 
        token=auth_keys_data['HF_API_KEY'][0],
        )
    if assertion_model_name == "m42-health/med42-70b" or assertion_model_name == "meta-llama/Llama-2-70b-hf":
        print(f"Set pad token to be the same as the end-of-sequence (EOS) token")
        tokenizer.pad_token = tokenizer.eos_token
    if assertion_model_name == "mistralai/Mixtral-8x7B-Instruct-v0.1":
        print(f"Set pad token id to be the same as the end-of-sequence (EOS) token id")
        tokenizer.pad_token_id = tokenizer.eos_token_id
    print(f"Loading model")
    if assertion_model_name == 'google/flan-t5-xxl':
        model = AutoModelForSeq2SeqLM.from_pretrained(
        pretrained_model_name_or_path=assertion_model_name,
        token=auth_keys_data['HF_API_KEY'][0],
        device_map=device_map
        )
    else:
        if assertion_use_flash_attention_2:
            print(f"Using flash attention 2")
            model = AutoModelForCausalLM.from_pretrained(
                pretrained_model_name_or_path=assertion_model_name, 
                token=auth_keys_data['HF_API_KEY'][0],
                device_map=device_map,
                torch_dtype=assertion_torch_dtype,
                use_flash_attention_2=assertion_use_flash_attention_2
                )
        else:
            print(f"Not using flash attention 2")
            model = AutoModelForCausalLM.from_pretrained(
                pretrained_model_name_or_path=assertion_model_name, 
                token=auth_keys_data['HF_API_KEY'][0],
                device_map=device_map
                )
    print(f"Build Successful")

    for target_word in target_word_list:
        print(f"\nAssertion Pipeline for Target Word: {target_word}")
        assertion_timestamp = datetime.now().replace(tzinfo=pytz.utc)
        assertion_timestamp = assertion_timestamp.astimezone(pytz.timezone('US/Pacific'))
        assertion_timestamp = assertion_timestamp.strftime('%Y_%m_%d_%H:%M:%S')
    
        print(f"\nCreate Data Path for Target Word")
        formatted_end_data_path = end_data_path.format(target_word=target_word)
        formatted_end_data_path = formatted_end_data_path.replace(" ", "_")
        data_path = f"{initial_data_path}{formatted_end_data_path}"
        data_path = os.path.expanduser(data_path)
        print(f"Data Path: {data_path}")

        print(f"\nLoading data")
        seed = 12345
        ori_data = pd.read_csv(data_path)
        if subset_data:
            print(f"Subsetting full dataset to {subset_sample_size} samples")
            # unique_chart_ids = ori_data['chart_id'].unique()
            # df_chart_ids = pd.DataFrame(unique_chart_ids, columns=['chart_id'])
            # sampled_chart_ids = df_chart_ids.sample(n=sample_chart_id_size, random_state=seed)
            # ori_data = ori_data[ori_data['chart_id'].isin(sampled_chart_ids['chart_id'])]
            ori_data = ori_data.sample(n=subset_sample_size, random_state=seed)
            ori_data = ori_data.head(8000)
            ori_data.reset_index(drop=True, inplace=True)
        ner_extracted_df = ori_data
        print(ner_extracted_df)
        print(f"Data Pull Successful")

        print(f"\nPre-processing Data")
        ner_extracted_df = preprocess_data(
            data_df=ner_extracted_df,
            column_to_process='extracted_text',
            remove_hyphens=True,
            remove_underscores=True
        )
        print(f"Pre-processing Complete")

        print(f"\nCollecting features")
        selected_features_df = get_gsheet_data(
            service_acc_path=gsheet_dict["service_account_path"],
            gsheet=gsheet_dict["feature_gsheet"],
            gsheet_sheet=gsheet_dict["feature_gsheet_sheet"]
        )
        for column in selected_features_df[["target_word", "feature_present", "feature_negated", "feature_uncertain"]]:
            if selected_features_df[column].dtype == 'object':
                selected_features_df[column] = selected_features_df[column].str.lower()
        selected_features_df = selected_features_df[selected_features_df['target_word'] == target_word].reset_index(drop=True)
        print(f"Selected Features")

        print(f"\nCreating Fixed System Content")
        original_column_names_list = gsheet_dict["assertion_system_content_template_index"]
        model_core_name = assertion_model_name.split('/')[-1]
        # Filter list for elements starting with the model_core_name
        filtered_column_names_list = [name for name in original_column_names_list if name.startswith(model_core_name)]
        fixed_system_contents_df = pd.DataFrame()
        for column_name in filtered_column_names_list:
            # Extract the system content template for the current column
            system_content_template = selected_features_df[column_name][0]
            print(f"\nsystem_content_template for {column_name}: \n{system_content_template}")
            # Generate fixed system content
            fixed_system_content = model_generate_system_content(
                delimiter=delimiter,
                features_df=selected_features_df,
                system_content_template=system_content_template,
                uncertainty_label=True,
            )
            # Add the fixed_system_content to the DataFrame under a column named after column_name
            new_column_name = f"{column_name}_content_message"
            fixed_system_contents_df[new_column_name] = fixed_system_content['content_message']
        content_message_column_names_list = fixed_system_contents_df.columns.tolist()
        content_message_df = selected_features_df.join(fixed_system_contents_df, how='left')
        content_message_df = content_message_df.drop(columns=original_column_names_list)
        print(f"\nFixed System Content Created for: {filtered_column_names_list}")

        print(f"\nCollecting Synonyms")
        feature_synonyms = pd.read_csv(synonyms_path)
        feature_synonyms = feature_synonyms[feature_synonyms['target_word'] == target_word]
        feature_synonyms.rename(columns={'ner_list': 'synonyms'}, inplace=True)
        print(f"Synonyms Collected")

        print(f"\nCreating pre_dialogs_df")
        content_message_df_columns_to_select = ['target_word'] + content_message_column_names_list
        merged_feature_df = pd.merge(
            feature_synonyms,
            content_message_df[content_message_df_columns_to_select],
            on='target_word',
            how='left'
            )
        pre_dialogs_df = pd.merge(
            ner_extracted_df,
            merged_feature_df,
            left_on='entity_name',
            right_on='synonyms',
            how='left'
            ).drop(columns=['synonyms'])
        print(f"Creating dialogs")
        dialogs_df = model_create_single_feature_llm_dialogs(
            model_name=assertion_model_name,
            data_df=pre_dialogs_df,
            text_column_name='extracted_text',
            content_message_column_names_list=content_message_column_names_list,
        )
        print(dialogs_df)
        print(f"Total dialogs created: {len(dialogs_df)}")
        test_output = f'dialogs_{filtered_column_names_list[0]}'
        print(f"Example Dialog for {filtered_column_names_list[0]}:\n{dialogs_df[test_output][0]}")

        if test:
            dialogs_df=dialogs_df.head(test_sample_size)

        print(f"\nGenerating LLM Output")
        llm_output = model_assertion(
            model=model,
            tokenizer=tokenizer,
            assertion_model_name=assertion_model_name,
            assertion_max_seq_len=assertion_max_seq_len,
            assertion_max_new_tokens=assertion_max_new_tokens,
            assertion_temperature=assertion_temperature,
            assertion_do_sample=assertion_do_sample,
            assertion_top_p=assertion_top_p,
            dialogs_df=dialogs_df
        )
    
        print(f"\nSaving LLM outputs")
        save_llm_outputs(
            data_path=data_path,
            test=test,
            subset_data=subset_data,
            assertion_timestamp=assertion_timestamp,
            save_folder_path=save_folder_path,
            assertion_model_name=assertion_model_name,
            assertion_use_flash_attention_2=assertion_use_flash_attention_2,
            llm_output=llm_output
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
    test_sample_size=20
    subset_data=False
    subset_sample_size=None
    target_word_list=[
        "atelectasis", 
        "cardiomegaly", 
        "pulmonary edema", 
        "pleural effusion", 
        "pneumonia", 
        "pneumothorax"
        ]
    initial_data_path=f"~/llm_data/mimic_llm_output/extracted_output/chexpert_dataset/"
    end_data_path="{target_word}_extracted_2024-02-17_15:51:22_chexpert_filtered.csv"
    save_folder_path="~/llm_data/mimic_llm_output/assertion_output/chexpert_dataset"
    synonyms_path="~/llm_data/mimic_llm_output/ner_output/chexpert_dataset/chexpert_entity_df_2024-02-17_15:51:22.csv"
    
    # assertion_model_name="m42-health/med42-70b"
    # assertion_model_name="epfl-llm/meditron-70b"
    # assertion_model_name="mistralai/Mixtral-8x7B-Instruct-v0.1"
    # assertion_model_name="google/flan-t5-xxl"
    assertion_model_name="meta-llama/Llama-2-70b-hf"
    assertion_use_flash_attention_2 = False
    assertion_torch_dtype = torch.bfloat16
    assertion_temperature=0.2
    assertion_do_sample=False
    assertion_top_p=0.2
    assertion_max_seq_len=3072
    assertion_max_new_tokens=4
    device_map = "auto"
    delimiter="####"
    auth_keys_path="~/local_credentials/auth_keys.json"
    gsheet_dict={
        "feature_gsheet_sheet": "MIMIC Chexpert Feature List",
        "system_content_messages_gsheet_sheet": "System Content Messages",
        "assertion_system_content_template_index": [
            "med42-70b", "med42-70b_definition", 
            "meditron-70b", "meditron-70b_definition", 
            "Mixtral-8x7B-Instruct-v0.1", "Mixtral-8x7B-Instruct-v0.1_definition",
            "flan-t5-xxl", "flan-t5-xxl_definition",
            "Llama-2-70b-hf", "Llama-2-70b-hf_definition",
            ],

        "service_account_path": "~/local_credentials/google_service_account.json",
        "feature_gsheet": "LLM Features",
        "system_content_messages_gsheet": "System Content Messages",
        }
    try:
        llm_assertion(
            test=test,
            test_sample_size=test_sample_size,
            subset_data=subset_data,
            subset_sample_size=subset_sample_size,
            target_word_list=target_word_list,
            initial_data_path=initial_data_path,
            end_data_path=end_data_path,
            save_folder_path=save_folder_path,
            auth_keys_path=auth_keys_path,
            synonyms_path=synonyms_path,
            assertion_model_name=assertion_model_name,
            assertion_use_flash_attention_2=assertion_use_flash_attention_2,
            assertion_torch_dtype=assertion_torch_dtype,
            assertion_temperature=assertion_temperature,
            assertion_top_p=assertion_top_p,
            assertion_do_sample=assertion_do_sample,
            assertion_max_seq_len=assertion_max_seq_len,
            assertion_max_new_tokens=assertion_max_new_tokens,
            device_map=device_map,
            delimiter=delimiter,
            gsheet_dict=gsheet_dict,
            )
    except Exception as e:
        send_error_email()
        raise