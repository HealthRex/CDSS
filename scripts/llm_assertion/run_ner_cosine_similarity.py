from typing import Optional
import socket
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
    preprocess_data,
    get_embeddings,
    calculate_cosine_similarity,
    send_email,
    send_error_email
)

def filter_ner_outputs(
        test,
        target_word_dict,
        save_path,
        ner_output_path,
        cosine_similarity_model_name,
        cosine_similarity_max_length,
        device_map,
        cosine_similarity_use_flash_attention_2,
        cosine_similarity_torch_dtype,
        auth_keys_path,
        gsheet_dict
):

    ner_cosine_similarity_timestamp = datetime.now()
    ner_cosine_similarity_timestamp = ner_cosine_similarity_timestamp.replace(tzinfo=pytz.utc)
    ner_cosine_similarity_timestamp = ner_cosine_similarity_timestamp.astimezone(pytz.timezone('US/Pacific'))
    ner_cosine_similarity_timestamp = ner_cosine_similarity_timestamp.strftime('%Y-%m-%d_%H:%M:%S')

    print(f"\nExpanding Paths")
    ner_output_path = os.path.expanduser(ner_output_path)
    gsheet_dict["service_account_path"] = os.path.expanduser(gsheet_dict["service_account_path"])
    auth_keys_path=os.path.expanduser(auth_keys_path)
    print(f"Paths Expanded")

    print(f"\nPulling Auth Keys")
    auth_keys_data = get_auth_keys(auth_keys_path=auth_keys_path)

    print(f"\nLoading NER Output Data")
    ner_output = pd.read_csv(ner_output_path)
    print(ner_output)
    print(f"Data Pull Successful")

    print(f"\nPre-processing NER Output Data")
    ner_output = preprocess_data(
        data_df=ner_output,
        column_to_process='processed_sentences'
    )
    ner_output['ner_output'] = ner_output['ner_output'].apply(ast.literal_eval)
    pre_filtered_ner_output = ner_output.explode('ner_output').reset_index(drop=True)
    # remove ner_output that has less than 2 letters
    pre_filtered_ner_output = pre_filtered_ner_output[pre_filtered_ner_output['ner_output'].str.contains(r'[a-zA-Z].*[a-zA-Z]', regex=True)]
    # remove ner_output that has more than 4 words
    lower_word_count_single_entity_limit = 5
    pre_filtered_ner_output = pre_filtered_ner_output[pre_filtered_ner_output['ner_output'].str.count(r'\w+') <= lower_word_count_single_entity_limit]
    pre_filtered_ner_output['ner_output'] = pre_filtered_ner_output['ner_output'].str.lower().str.strip().str.replace(r'\s+', ' ', regex=True)
    pre_filtered_ner_output = pre_filtered_ner_output.drop_duplicates(subset='ner_output')
    pre_filtered_ner_output = pre_filtered_ner_output['ner_output']
    pre_filtered_ner_output = [word.lower() for word in pre_filtered_ner_output]
    print(f"Pre-processing Complete")

    # print(f"\nLoading UMLS Keywords")
    # ori_umls_list = pd.read_csv(umls_keywords_path)
    # # need to add the umls filter step
    # ori_umls_list['ner_output'] = ori_umls_list['ner_output'].apply(eval)
    # umls_list = ori_umls_list.explode('ner_output').reset_index(drop=True)
    # umls_list = umls_list.drop_duplicates(subset='ner_output')
    # umls_list = umls_list['ner_output']
    # umls_list = [word.lower() for word in umls_list]
    # print(f"Data Pull Successful")

    # print(f"\nLoading LLM Augmentation Keywords")
    # # llm_augmentation_list pulled from gsheet (after being made using prompts on gsheets)
    # llm_augmentation_list = ['Depressed mood', 'Anhedonia', 'Fatigue', 'Feelings of worthlessness', 'Excessive guilt', 'Diminished concentration', 'Indecisiveness', 'Insomnia', 'Hypersomnia', 'Psychomotor agitation', 'Psychomotor retardation', 'Recurrent thoughts of death', 'Suicidal ideation', 'Significant weight loss', 'Weight gain', 'Appetite changes', 'Persistent sadness', 'Lack of interest in activities', 'Withdrawal from social interactions', 'Irritability', 'Low self-esteem', 'Persistent anxiety', 'Hopelessness', 'Helplessness', 'Chronic pain without clear cause', 'Decreased energy', 'Sleep disturbances', 'Crying spells', 'Unexplained physical symptoms', 'Dysthymia', 'Low mood', 'Loss of pleasure', 'Change in appetite', 'Sleep problems', 'Activity level changes', 'Fatigue or loss of energy', 'Feelings of worthlessness', 'Excessive or inappropriate guilt', 'Difficulty thinking', 'Concentration problems', 'Recurrent thoughts of death or suicide', 'Restlessness', 'Lethargy', 'Social withdrawal', 'Lack of motivation', 'Frequent tearfulness', 'Unexplained aches and pains', 'Chronic fatigue', 'Feeling overwhelmed', 'Emotional numbness', 'Excessive worrying', 'Pessimism', 'Irrational guilt', 'Loss of self-esteem', 'Indifference', 'Depersonalization', 'Derealization', 'Somatic complaints', 'Impaired judgment', 'Feelings of despair', 'Chronic low mood', 'Reduced self-care', 'Mood swings', 'Difficulty with decision making', 'Increased self-criticism', 'Reduced self-worth', 'Avoidance of social activities', 'Persistent melancholy', 'Reduced emotional responsiveness', 'Prolonged grief', 'Inability to feel pleasure', 'Feelings of emptiness', 'Reduced libido', 'Isolation', 'Depressive realism', 'Negative thinking patterns', 'Self-loathing', 'Rumination', 'Chronic worry', 'Emotional detachment', 'Lack of future perspective', 'Hopelessness about the future', 'Cognitive distortions', 'Disturbed sleep patterns', 'Eating disorder symptoms', 'Obsessive thoughts', 'Compulsive behaviors', 'Persistent pessimism', 'Lack of concentration', 'Recurrent suicidal behavior', 'Exhaustion', 'Low tolerance to stress', 'Feelings of inadequacy', 'Social dysfunction', 'Reduced work performance', 'Neglecting responsibilities', 'Loss of interest in hobbies', 'Agitation', 'Reduced cognitive function', 'Emotional blunting', 'Feeling overwhelmed by simple tasks', 'Inability to experience joy', 'Disinterest in socializing', 'Persistent sadness', 'Feeling disconnected', 'Lack of energy', 'Substance abuse', 'Neglecting personal hygiene', 'Weight fluctuations', 'Changes in eating habits', 'Excessive guilt', 'Feeling of worthlessness', 'Difficulty facing daily tasks', 'Lack of motivation for self-care', 'Pessimistic outlook on life', 'Emotional instability', 'Recurring thoughts of death', 'Feeling trapped', 'Constant anxiety', 'Avoidance behavior', 'MDD', 'MD', 'MDE', 'UD', 'UPD', 'TRD', 'PDD', 'DYS', 'DD', 'MAD', 'SAD', 'BPAD-MD', 'BP-MDD', 'C-MDD', 'R-MDD', 'AD', 'CC-MDD', 'NC-MDD', 'PD-MD', 'S-MDD', 'M-MDD', 'MOD-MDD', 'GAD-MD', 'PTSD-MD', 'OCD-MD', 'ADHD-MD', 'BPD-MD', 'ASD-MD', 'MDE-R', 'MDE-S', 'Clinical depression', 'Unipolar depression', 'Major depressive disorder', 'Endogenous depression', 'Melancholia', 'Depressive illness', 'Mood disorder', 'Dysthymia', 'Chronic depression', 'Depressive episode', 'Recurrent depression', 'Severe depression', 'Major affective disorder', 'Persistent depressive disorder', 'Neurotic depression', 'Reactive depression', 'Psychotic depression', 'Non-psychotic depression', 'High-functioning depression', 'Seasonal depression', 'Atypical depression', 'Refractory depression', 'Treatment-resistant depression', 'Secondary depression', 'Situational depression', 'Biological depression', 'Endogenous major depression', 'Exogenous depression', 'Organic depressive disorder', 'Postpartum depression', 'Single episode depression', 'Recurrent major depression', 'Psychogenic depression', 'Chronic major depression', 'Idiopathic depression', 'MDD with melancholic features', 'MDD with atypical features', 'MDD with psychotic features', 'MDD with anxious distress', 'MDD with mixed features', 'MDD with seasonal pattern', 'MDD with peripartum onset', 'MDD with catatonic features', 'Intractable depression', 'Severe recurrent depression', 'Moderate depression', 'Mild depression', 'Disabling depression', 'Double depression', 'Subsyndromal depression', 'Masked depression', 'Vegetative depression', 'Somatogenic depression', 'Secondary major depression', 'Late-life depression', 'Early-onset depression', 'Midlife depression', 'Geriatric depression', 'Adolescent depression', 'Young adult depression', 'Depressive state', 'Depressive syndrome', 'Major depressive episode', 'Profound depression', 'Endogenomorphic depression', 'Involutional melancholia', 'Neurovegetative depression', 'Primary depression', 'Secondary depression', 'Constitutional depression', 'Cyclothymic depression', 'Exhaustion depression', 'Psychotic major depression', 'Non-endogenous depression', 'Acute depression', 'Chronic affective disorder', 'Protracted depression', 'Depressive neurosis', 'Reactive depressive psychosis', 'Mixed anxiety and depressive disorder', 'Dysthymic disorder', 'Refractory major depression', 'Melancholic depression', 'Non-melancholic depression', 'Catatonic depression', 'Anxious depression', 'Agitated depression', 'Retarded depression', 'Postnatal depression', 'Premenstrual dysphoric disorder']
    # umls_and_llm_augmented_list = umls_list + llm_augmentation_list
    # umls_and_llm_augmented_list = [re.sub(r'\s+', ' ', element.strip().lower()) for element in umls_and_llm_augmented_list]
    # print(f"Data Pull Successful")

    print(f"\nLoading Tokenizer")
    if cosine_similarity_model_name in "emilyalsentzer/Bio_ClinicalBERT":
        tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=cosine_similarity_model_name, 
            token=auth_keys_data['HF_API_KEY'][0]
            )
        print(f"Loading Model")
        model = AutoModel.from_pretrained(
            pretrained_model_name_or_path=cosine_similarity_model_name, 
            token=auth_keys_data['HF_API_KEY'][0]
            )
    else:
        tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=cosine_similarity_model_name, 
            token=auth_keys_data['HF_API_KEY'][0]
            )
        print(f"Loading Model")
        model = AutoModel.from_pretrained(
            pretrained_model_name_or_path=cosine_similarity_model_name, 
            token=auth_keys_data['HF_API_KEY'][0],
            device_map=device_map
            )
    print(f"Build Successful")

    #### Cosine similarity examples
    # test_text1 = "depression"
    # test_text2 = "mdd"
    # embeddings1 = get_embeddings(text=test_text1, model=model, tokenizer=tokenizer, max_length=cosine_similarity_max_length)
    # embeddings2 = get_embeddings(text=test_text2, model=model, tokenizer=tokenizer, max_length=cosine_similarity_max_length)
    # test_similarity = cosine_similarity(embeddings1, embeddings2)
    # print(test_similarity)
    #### End examples

    if test:
        print(f"\n\n***Test Env Set: Truncating 'pre_filtered_ner_output'***\n\n")
        pre_filtered_ner_output = pre_filtered_ner_output[0:4]

    key_similarity_dfs = []
    for key, target_word_list in target_word_dict.items():
        print(f"\nCalculate Mean Cosine Similarity for {key}")
        all_similarities = {}
        for target_word in target_word_list:
            similarities = calculate_cosine_similarity(target_word, pre_filtered_ner_output, model, tokenizer, cosine_similarity_max_length=cosine_similarity_max_length)
            all_similarities[target_word] = similarities
            print(f"Cosine Similarity Calculated for: {target_word}")
        # Create DataFrame for this key
        pd_df_format_all_similarities = [(ner, similarity) for values in all_similarities.values() for ner, similarity in values]
        key_df = pd.DataFrame(pd_df_format_all_similarities, columns=['ner', 'cosine_similarity'])
        key_mean_cosine_similarity_df = key_df.groupby('ner')['cosine_similarity'].mean().reset_index()
        key_mean_cosine_similarity_df.rename(columns={'cosine_similarity': f'{key.replace(" ", "_")}_mean_cosine_similarity'}, inplace=True)
        # Append to the list
        key_similarity_dfs.append(key_mean_cosine_similarity_df)

    print(f"\nCreate Final DataFrame")
    # Initialize final DataFrame with the first DataFrame in the list
    final_similarity_df = key_similarity_dfs[0]
    # Iteratively merge the rest of the DataFrames
    for df in key_similarity_dfs[1:]:
        final_similarity_df = pd.merge(final_similarity_df, df, on='ner', how='outer')
    
    save_file_extension=os.path.splitext(os.path.basename(ner_output_path))[0]
    if test:
        save_filename=f"{save_path}/TEST_cosine_sim_flan_t5_{ner_cosine_similarity_timestamp}_{save_file_extension}.csv"
        final_similarity_df.to_csv(save_filename, index=False)
    else:
        save_filename=f"{save_path}/cosine_sim_flan_t5_{ner_cosine_similarity_timestamp}_{save_file_extension}.csv"
        final_similarity_df.to_csv(save_filename, index=False)
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
    target_word_dict={
        'atelectasis': [
            "atelectasis"
            ],
        'cardiomegaly': [
            "cardiomegaly"
            ],
        'pulmonary edema': [
            "pulmonary edema",
            ],
        'pleural effusion': [
            "pleural effusion",
            ],
        'pneumonia': [
            "pneumonia",
            ],
        'pneumothorax': [
            "pneumothorax",
            ],
            }
    save_path="/home/ivlopez/llm_data/mimic_llm_output/ner_output/chexpert_dataset"
    ner_output_path="/home/ivlopez/llm_data/mimic_llm_output/ner_output/chexpert_dataset/mimic_chexpert_filtered_flan_t5_ner_output_2024-01-28_06:46:58.csv"
    
    cosine_similarity_model_name="emilyalsentzer/Bio_ClinicalBERT"
    # cosine_similarity_model_name="m42-health/med42-70b"
    # cosine_similarity_model_name="epfl-llm/meditron-70b"
    # cosine_similarity_model_name="meta-llama/Llama-2-7b-hf"
    cosine_similarity_max_length=512
    device_map="auto"
    cosine_similarity_use_flash_attention_2 = False
    cosine_similarity_torch_dtype = None
    auth_keys_path="~/local_credentials/auth_keys.json"
    gsheet_dict={
            "service_account_path": "~/local_credentials/google_service_account.json",
            }
    try:
        filter_ner_outputs(
            test=test,
            target_word_dict=target_word_dict,
            save_path=save_path,
            ner_output_path=ner_output_path,
            cosine_similarity_model_name=cosine_similarity_model_name,
            cosine_similarity_max_length=cosine_similarity_max_length,
            device_map=device_map,
            cosine_similarity_use_flash_attention_2=cosine_similarity_use_flash_attention_2,
            cosine_similarity_torch_dtype=cosine_similarity_torch_dtype,
            auth_keys_path=auth_keys_path,
            gsheet_dict=gsheet_dict
            )
    except Exception as e:
        send_error_email()
        raise