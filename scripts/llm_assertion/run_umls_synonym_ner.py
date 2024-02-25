from typing import Optional, Callable
import socket
import time
import math
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
from nltk.tokenize import sent_tokenize, word_tokenize
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

from helper_functions import (
    get_auth_keys,
    search_umls_for_concepts,
    update_synonyms,
    get_synonyms_from_cui,
    flan_t5_model_ner,
    send_email,
    send_error_email
)

pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def umls_synonym_ner(
        test,
        save_ner_outputs,
        proj_filename,
        umls_ner_output_save_path,
        target_word_list,
        keep_rootSource,
        flan_t5_ner_model_name,
        flan_t5_ner_prompts,
        flan_t5_max_new_tokens,
        flan_t5_max_time,
        flan_t5_temperature,
        flan_t5_top_p,
        flan_t5_no_repeat_ngram_size,
        flan_t5_repetition_penalty,
        device_map,
        gsheet_dict,
):
    umls_timestamp = datetime.now()
    umls_timestamp = umls_timestamp.replace(tzinfo=pytz.utc)
    umls_timestamp = umls_timestamp.astimezone(pytz.timezone('US/Pacific'))
    umls_timestamp = umls_timestamp.strftime('%Y-%m-%d_%H:%M:%S')
    
    print(f"\nExpanding Paths")
    umls_ner_output_save_path = os.path.expanduser(umls_ner_output_save_path)
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
    print(f"Build Complete")

    combined_flan_t5_ner_output = pd.DataFrame()
    for target_word in target_word_list:
        print(f"\nSelected Target Word: {target_word}")

        print(f"\nCollecting UMLS Concepts for Target Word")
        umls_concepts = search_umls_for_concepts(term=target_word, UMLS_API_KEY=auth_keys_data['UMLS_API_KEY'][0])
        umls_concepts = umls_concepts[umls_concepts['rootSource'].isin(keep_rootSource)]
        print(f"Get UMLS Synonyms")
        all_synonyms_list = update_synonyms(concepts=umls_concepts, UMLS_API_KEY=auth_keys_data['UMLS_API_KEY'][0])
        print(f"Combine UMLS Concepts and Synonyms")
        umls_concepts_list = umls_concepts['name'].tolist()
        umls_concepts_synonyms_list = umls_concepts_list+all_synonyms_list
        print(f"Target Word UMLS Synonyms Collected")
        
        print(f"\nGenerating NER DataFrame")
        ner_df = pd.DataFrame(umls_concepts_synonyms_list, columns=['synonyms'])
        ner_df['synonyms'] = ner_df['synonyms'].str.replace(r'\([^)]*\)', '', regex=True) # remove parentheses and the text within the parenthesis
        ner_df['synonyms'] = ner_df['synonyms'].str.lower().str.strip().str.replace(r'\s+', ' ', regex=True)
        ner_df.drop_duplicates('synonyms', inplace=True)
        ner_df.reset_index(drop=True, inplace=True)
        ner_df['sentence_id'] = ner_df.index + 1
        print(f"NER DataFrame Generated:\n{ner_df}")

        if test:
            print(f"\n\n****Creating Test Variables****\n\n")
            ner_df=ner_df.head(10)

        print(f"\nPerform NER")
        flan_t5_ner_output = flan_t5_model_ner(
            ner_df=ner_df,
            column_for_ner='synonyms',
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
        print(f"NER Complete")

        flan_t5_ner_output['target_word'] = target_word
        combined_flan_t5_ner_output = pd.concat([combined_flan_t5_ner_output, flan_t5_ner_output], ignore_index=True, sort=False)

    print(f"\nSaving NER Outputs")
    if save_ner_outputs:
        if test:
            save_filename = f"{umls_ner_output_save_path}/TEST_umls_{proj_filename}_flan_t5_ner_output_{umls_timestamp}.csv"
            combined_flan_t5_ner_output.to_csv(save_filename, index=False)
        else:
            save_filename = f"{umls_ner_output_save_path}/umls_{proj_filename}_flan_t5_ner_output_{umls_timestamp}.csv"
            combined_flan_t5_ner_output.to_csv(save_filename, index=False)
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
    save_ner_outputs=True
    proj_filename="chexpert"
    umls_ner_output_save_path="/home/ivlopez/llm_data/mimic_llm_output/ner_output/chexpert_dataset"
    target_word_list=["atelectasis", "cardiomegaly", "pulmonary edema", "pleural effusion", "pneumonia", "pneumothorax"]

    keep_rootSource=['MTH', 'SNOMEDCT_US']
    flan_t5_ner_prompts={
            "catch_all": "What are all the named entities in this text: ",
            "med_social": "What are all the social determinants of health named entities in this text: ", 
            "clinical": "What are all the clinical named entities in this text: ",
            "medical": "What are all the medical named entities in this text: ",
            }
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
        umls_synonym_ner(
            test=test,
            save_ner_outputs=save_ner_outputs,
            proj_filename=proj_filename,
            umls_ner_output_save_path=umls_ner_output_save_path,
            target_word_list=target_word_list,
            flan_t5_ner_model_name=flan_t5_ner_model_name,
            keep_rootSource=keep_rootSource,
            flan_t5_ner_prompts=flan_t5_ner_prompts,
            flan_t5_max_new_tokens=flan_t5_max_new_tokens,
            flan_t5_max_time=flan_t5_max_time,
            flan_t5_temperature=flan_t5_temperature,
            flan_t5_top_p=flan_t5_top_p,
            flan_t5_no_repeat_ngram_size=flan_t5_no_repeat_ngram_size,
            flan_t5_repetition_penalty=flan_t5_repetition_penalty,
            device_map=device_map,
            gsheet_dict=gsheet_dict,
            )
    except Exception as e:
        send_error_email()
        raise