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
    load_stanford_moud_data,
    load_chexpert_data,
    load_mimic_moud_data,
    preprocess_data,
    preprocess_chexpert_data,
    ner_process_data,
    tokenize_text,
    split_tokens,
    update_chunks,
    decode_chunk,
    update_token_count,
    flan_t5_model_ner,
    remove_delimiter,
    send_email,
    send_error_email
)

pd.set_option('display.max_rows', 10)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def llm_assertion(
        test,
        test_sample,
        data_path,
        subset_data,
        sample_dataset_size,
        auth_keys_path,
        chunk_token_limit,
        overlap_value,
        flan_t5_ner_model_name,
        flan_t5_ner_prompts,
        flan_t5_max_new_tokens,
        flan_t5_max_time,
        flan_t5_temperature,
        flan_t5_top_p,
        flan_t5_no_repeat_ngram_size,
        flan_t5_repetition_penalty,
        save_ner_outputs,
        ner_output_save_path,
        flan_t5_ner_output_save_file_name,
        device_map,
        delimiter,
        gsheet_dict,
):
    ner_timestamp = datetime.now()
    ner_timestamp = ner_timestamp.replace(tzinfo=pytz.utc)
    ner_timestamp = ner_timestamp.astimezone(pytz.timezone('US/Pacific'))
    ner_timestamp = ner_timestamp.strftime('%Y-%m-%d_%H:%M:%S')
    
    print(f"\nExpanding Paths")
    data_path = os.path.expanduser(data_path)
    ner_output_save_path = os.path.expanduser(ner_output_save_path)
    gsheet_dict["service_account_path"] = os.path.expanduser(gsheet_dict["service_account_path"])
    auth_keys_data = get_auth_keys(auth_keys_path=os.path.expanduser(auth_keys_path))
    print(f"Paths Expanded")

    print(f"\nLoading Flan-T5 NER Tokenizer")
    tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=flan_t5_ner_model_name,
        token=auth_keys_data['HF_API_KEY'][0]
        )
    print(f"Loading Flan-T5 NER Model")
    model = AutoModelForSeq2SeqLM.from_pretrained(
        pretrained_model_name_or_path=flan_t5_ner_model_name,
        token=auth_keys_data['HF_API_KEY'][0],
        device_map=device_map
        )
    print(f"Loading Complete")

    print(f"\nLoading data")
    data_df = load_mimic_moud_data(data_path, subset_data, sample_dataset_size)
    print(data_df)
    print(f"Data Pull Successful")

    print(f"\nPre-processing Data")
    data_df = preprocess_data(
        data_df=data_df,
        column_to_process='text',
        remove_hyphens=True,
        remove_underscores=True,
    )
    print(f"Pre-processing Complete")

    print(f"\nGenerating NER DataFrame")
    ner_df = ner_process_data(
        data_df=data_df
    )
    ner_df['temp'] = ner_df['processed_sentences'].apply(lambda x: tokenize_text(tokenizer, x)) # Apply the function and create a temporary column with the tuple
    ner_df['token_count'] = ner_df['temp'].apply(lambda x: x[0]) # Split the tuple into two separate columns
    ner_df['input_ids_processed_sentences'] = ner_df['temp'].apply(lambda x: x[1])
    ner_df.drop(columns=['temp'], inplace=True) # Drop the temporary column

    over_token_limit = ner_df[ner_df['token_count'] > chunk_token_limit] # Filter for token counts > chunk_token_limit
    ner_df = ner_df.drop(over_token_limit.index)
    over_token_limit['chunks'] = over_token_limit.apply(lambda row: split_tokens(row, chunk_token_limit), axis=1) # create token chunks of size chunk_token_limit with blunt ends
    over_token_limit['updated_chunks'] = over_token_limit.apply(lambda row: update_chunks(row, overlap_value), axis=1) # create updated_chunks (sticky end token chunks w/ sticky ends = overlap_value)
    over_token_limit = over_token_limit.drop(['input_ids_processed_sentences', 'chunks'], axis=1)
    over_token_limit = over_token_limit.explode('updated_chunks').reset_index(drop=True)
    over_token_limit['processed_sentences'] = over_token_limit['updated_chunks'].apply(lambda chunk: decode_chunk(chunk, tokenizer)) # decode updated_chunks to create new processed_sentences
    over_token_limit['token_count'] = over_token_limit['updated_chunks'].apply(update_token_count) # find new token counts of new processed_sentences
    over_token_limit.rename(columns={'updated_chunks': 'input_ids_processed_sentences'}, inplace=True)

    ner_df = pd.concat([ner_df, over_token_limit], axis=0, ignore_index=True) # Add new sentences back to ner_df

    ner_df = ner_df[ner_df['processed_sentences'].str.contains(r'[a-zA-Z]', regex=True)] # Keep rows where 'processed_sentences' contains at least one letter
    ner_df['str_len'] = ner_df['processed_sentences'].str.len()
    ner_df = ner_df[ner_df['str_len'] > 3] # Remove 'processed_sentences' with less than 4 characters
    ner_df = ner_df.drop(columns=['str_len', 'input_ids_processed_sentences'])
    ner_df = ner_df.reset_index(drop=True) # Reset index on df
    ner_df['sentence_id'] = ner_df.index + 1 # Set final sentence ID
    print(ner_df)
    print(f"NER DataFrame Generated")

    if test:
        print(f"\n\n***Loading Testing Env Variables***\n\n")
        ner_df = ner_df.head(10)

    print(f"\nPerform Flan-T5 NER")
    flan_t5_ner_output = flan_t5_model_ner(
        ner_df=ner_df,
        column_for_ner='processed_sentences',
        flan_t5_ner_prompts=flan_t5_ner_prompts,
        model=model,
        tokenizer=tokenizer,
        flan_t5_max_new_tokens=flan_t5_max_new_tokens,
        flan_t5_max_time=flan_t5_max_time,
        flan_t5_temperature=flan_t5_temperature,
        flan_t5_top_p=flan_t5_top_p,
        flan_t5_no_repeat_ngram_size=flan_t5_no_repeat_ngram_size,
        flan_t5_repetition_penalty=flan_t5_repetition_penalty
    )
    # print(f"\nRemove Delimiter from NER Output")
    # flan_t5_ner_output['ner_output'] = flan_t5_ner_output['ner_output'].apply(remove_delimiter)
    # flan_t5_ner_output['ner_output']
    # print(f"Delimiter Removed")

    print(f"\nSaving NER Outputs")
    if save_ner_outputs:
        if test:
            save_filename = f"{ner_output_save_path}/TEST_{flan_t5_ner_output_save_file_name}_{ner_timestamp}.csv"
            flan_t5_ner_output.to_csv(save_filename, index=False)
        else:
            save_filename = f"{ner_output_save_path}/{flan_t5_ner_output_save_file_name}_{ner_timestamp}.csv"
            flan_t5_ner_output.to_csv(save_filename, index=False)
    print(f"NER Outputs Saved: {save_filename}")

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
    test_sample=None
    subset_data=False
    sample_dataset_size=None # sample for chexpert 2500
    save_ner_outputs=True

    data_path="~/llm_data/exp_mimic_data/processed_data/OUD_MIMIC_annotations_filtered.csv" # "~/llm_data/exp_mimic_data/processed_data/chexpert_filtered.csv"
    ner_output_save_path="/home/ivlopez/llm_data/mimic_llm_output/ner_output/moud_dataset" # "/home/ivlopez/llm_data/mimic_llm_output/ner_output/chexpert_dataset"
    flan_t5_ner_output_save_file_name="mimic_moud_filtered_flan_t5_ner_output" # "mimic_chexpert_filtered_flan_t5_ner_output"

    chunk_token_limit=100
    overlap_value=5

    flan_t5_ner_prompts={
        "catch_all": "What are all the named entities in this text: ",
        "med_social": "What are all the social determinants of health named entities in this text: ", 
        "clinical": "What are all the clinical named entities in this text: ",
        "medical": "What are all the medical named entities in this text: ",
        }
    # flan_t5_ner_prompts={
    #     "ner_atelectasis": "What are all the named entities in this text related to 'atelectasis': ",
    #     "ner_cardiomegaly": "What are all the named entities in this text related to 'cardiomegaly': ",
    #     "ner_pulmonary_edema": "What are all the named entities in this text related to 'pulmonary edema': ",
    #     "ner_pleural_effusion": "What are all the named entities in this text related to 'pleural effusion': ",
    #     "ner_pneumonia": "What are all the named entities in this text related to 'pneumonia': ",
    #     "ner_pneumothorax": "What are all the named entities in this text related to 'pneumothorax': ",
    #     }

    flan_t5_max_new_tokens=1024
    flan_t5_max_time=300
    flan_t5_temperature=0.2
    flan_t5_top_p=0.9
    flan_t5_no_repeat_ngram_size=3
    flan_t5_repetition_penalty=2.5
    flan_t5_ner_model_name="google/flan-t5-xxl"
    auth_keys_path="~/local_credentials/auth_keys.json"
    device_map = "auto"
    delimiter="####"
    gsheet_dict={
        "service_account_path": "~/local_credentials/google_service_account.json",
        }
    try:
        llm_assertion(
            test=test,
            test_sample=test_sample,
            subset_data=subset_data,
            sample_dataset_size=sample_dataset_size,
            data_path=data_path,
            auth_keys_path=auth_keys_path,
            chunk_token_limit=chunk_token_limit,
            overlap_value=overlap_value,
            flan_t5_ner_model_name=flan_t5_ner_model_name,
            flan_t5_ner_prompts=flan_t5_ner_prompts,
            flan_t5_max_new_tokens=flan_t5_max_new_tokens,
            flan_t5_max_time=flan_t5_max_time,
            flan_t5_temperature=flan_t5_temperature,
            flan_t5_top_p=flan_t5_top_p,
            flan_t5_no_repeat_ngram_size=flan_t5_no_repeat_ngram_size,
            flan_t5_repetition_penalty=flan_t5_repetition_penalty,
            save_ner_outputs=save_ner_outputs,
            ner_output_save_path=ner_output_save_path,
            flan_t5_ner_output_save_file_name=flan_t5_ner_output_save_file_name,
            device_map=device_map,
            delimiter=delimiter,
            gsheet_dict=gsheet_dict,
            )
    except Exception as e:
        send_error_email()
        raise