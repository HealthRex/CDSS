from typing import Optional
import time
import gspread
import random
import pandas as pd
import re
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
from transformers import AutoModel, AutoTokenizer
import torch
from sklearn.metrics.pairwise import cosine_similarity
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

from helper_functions import (
    get_auth_keys,
)

def llm_filter_cosine_similarity(
        test,
        cosine_similarity_ner_output_path,
        target_word_list,
        cosine_similarity_cutoff,
        auth_keys_path,
        gsheet_dict,
):

    print(f"\nExpanding Paths")
    cosine_similarity_ner_output_path = os.path.expanduser(cosine_similarity_ner_output_path)
    gsheet_dict["service_account_path"] = os.path.expanduser(gsheet_dict["service_account_path"])
    auth_keys_data = get_auth_keys(auth_keys_path=os.path.expanduser(auth_keys_path))
    print(f"Paths Expanded")

    print(f"\nLoad Data")
    cosine_similarity_ner_output = pd.read_csv(cosine_similarity_ner_output_path)
    print(f"Data Loaded")

    for target_word in target_word_list:
        print(f"Filtering NER Outputs for: {target_word}")
        column_target_word_name = f'{target_word.replace(" ", "_")}_mean_cosine_similarity'
        column_selected_df = cosine_similarity_ner_output[['ner', column_target_word_name]].copy()
        filtered_column_selected_df = column_selected_df[column_selected_df[column_target_word_name] >= cosine_similarity_cutoff]
        print(f"Filtered NER Length for {target_word}: {len(filtered_column_selected_df)}")
        outputs_list = filtered_column_selected_df["ner"].tolist()
        print(outputs_list)

        user_input = input("Type 1 to continue, 0 to stop: ")
        if user_input == "0":
            print("Loop canceled by the user.")
            break
        elif user_input == "1":
            continue
        else:
            print("Invalid input. Continuing to the next target word.")
            continue

if __name__ == "__main__":
    test=False
    cosine_similarity_ner_output_path="/home/ivlopez/llm_data/mimic_llm_output/ner_output/chexpert_dataset/cosine_sim_flan_t5_2024-02-14_16:24:18_mimic_chexpert_filtered_flan_t5_ner_output_2024-01-28_06:46:58.csv"
    target_word_list=["atelectasis", "cardiomegaly", "pulmonary edema", "pleural effusion", "pneumonia", "pneumothorax"]
    cosine_similarity_cutoff=0.8 
    
    auth_keys_path="~/local_credentials/auth_keys.json"
    gsheet_dict={
            "service_account_path": "~/local_credentials/google_service_account.json",
            }
    try:
        llm_filter_cosine_similarity(
            test=test,
            cosine_similarity_ner_output_path=cosine_similarity_ner_output_path,
            target_word_list=target_word_list,
            cosine_similarity_cutoff=cosine_similarity_cutoff,
            auth_keys_path=auth_keys_path,
            gsheet_dict=gsheet_dict,
            )
    except Exception as e:
        raise