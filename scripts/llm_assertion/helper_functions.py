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

pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def get_auth_keys(
        auth_keys_path: str
):
    auth_keys_dict = []
    # Check if the file exists and is readable
    if os.path.exists(auth_keys_path):
        try:
            with open(auth_keys_path, 'r') as file:
                auth_keys_dict = json.load(file)
            print("JSON auth data successfully loaded.")
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {str(e)}")
    else:
        print("Auth file does not exist.")

    return auth_keys_dict

def get_gsheet_data(
        service_acc_path: str,
        gsheet: str,
        gsheet_sheet: str,
):
    service_acc = gspread.service_account(filename=service_acc_path)
    gsheet_meta_data = service_acc.open(gsheet)
    gsheet_info = gsheet_meta_data.worksheet(gsheet_sheet)

    gsheet_data = pd.DataFrame(gsheet_info.get_all_records())
    gsheet_data = gsheet_data.loc[:, ~gsheet_data.columns.str.contains('^Unnamed')]

    return gsheet_data

def get_umls_response(
        full_url: str,
        term: str,
        UMLS_API_KEY: str,
):
    response = requests.get(full_url, params={'string': term, 'apiKey': UMLS_API_KEY})
    response.encoding = 'utf-8'

    if response.status_code != 200:
        raise Exception("Error connecting to UMLS API:", response.json())

    data = response.json()
    concepts = [{"name": item["name"], "cui": item["ui"]} for item in data["result"]["results"] if "ui" in item]

    return concepts

def search_umls_for_concepts(
        term: str,
        UMLS_API_KEY: str,
        version: str = "current",
):
    base_uri = "https://uts-ws.nlm.nih.gov"
    content_endpoint = f"/rest/search/{version}"
    full_url = base_uri + content_endpoint

    print(f"\nGetting UMLS concepts for: {term}")

    page = 1
    full_list_concepts = []
    total_pages = 1  # Initialize total_pages

    while page <= total_pages:
        response = requests.get(full_url, params={'string': term, 'apiKey': UMLS_API_KEY, 'pageNumber': page})
        response.encoding = 'utf-8'

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            break

        data = response.json()
        full_list_concepts.extend(data['result']['results'])

        if page == 1:  # Calculate total number of pages on the first page
            total_records = data['result']['recCount']
            total_pages = math.ceil(total_records / data['pageSize'])

        page += 1

    concepts = pd.DataFrame(full_list_concepts)
    concepts = concepts.rename(columns={'ui': 'cui'})
    print(f"Total concepts returned: {len(concepts)}")

    return concepts

def get_synonyms_from_cui(
        cui: str,
        UMLS_API_KEY: str,
        version: str = "current",
):
    BASE_URI = "https://uts-ws.nlm.nih.gov"
    content_endpoint = f"/rest/content/{version}/CUI/{cui}/atoms"
    full_url = BASE_URI + content_endpoint

    page = 1
    synonyms = []
    while True:
        print(f"Page: {page}")
        response = requests.get(full_url, params={'apiKey':UMLS_API_KEY, 'pageNumber':page})
        response.encoding = 'utf-8'

        if response.status_code != 200:
            break

        data = response.json()
        for atom in data['result']:
            if atom.get('language', '').upper() == 'ENG':
                synonyms.append(atom['name'])

        # Check if we have processed all pages
        if page >= data['pageCount']:
            break
        page += 1

    return synonyms

def update_synonyms(
        concepts,
        UMLS_API_KEY: str,
):
    all_synonyms = []
    for index, row in concepts.iterrows():
        cui = row['cui']
        name = row['name']
        print(f"Getting synonyms for: {name} - cui: {cui}")
        syns = get_synonyms_from_cui(
            cui=cui,
            UMLS_API_KEY=UMLS_API_KEY)
        all_synonyms.extend(syns)
    all_synonyms = list(set(synonym.lower() for synonym in all_synonyms))

    return all_synonyms

def load_stanford_moud_data(data_path: str, subset_data: Optional[bool], sample_dataset_size: Optional[int]):
    seed = 12345
    ori_data = pd.read_csv(data_path)
    if subset_data:
        print(f"Subsetting full dataset to {sample_dataset_size} samples")
        ori_data = ori_data.sample(n=sample_dataset_size, random_state=seed)
        ori_data.reset_index(drop=True, inplace=True)

    data_df = ori_data
    data_df.drop('Unnamed: 0', axis=1, inplace=True)
    return data_df

def load_mimic_moud_data(data_path: str, subset_data: Optional[bool], sample_dataset_size: Optional[int]):
    seed = 12345
    ori_data = pd.read_csv(data_path)
    if subset_data:
        print(f"Subsetting full dataset to {sample_dataset_size} samples")
        ori_data = ori_data.sample(n=sample_dataset_size, random_state=seed)
        ori_data.reset_index(drop=True, inplace=True)

    data_df = ori_data[['file_name', 'term', 'class']]
    data_df = data_df.rename(columns={'term': 'text'})
    return data_df

def load_chexpert_data(data_path: str, subset_data: Optional[bool], sample_dataset_size: Optional[int]):
    seed = 12345
    ori_data = pd.read_csv(data_path)
    if subset_data:
        print(f"Subsetting full dataset to {sample_dataset_size} samples")
        ori_data = ori_data.sample(n=sample_dataset_size, random_state=seed)
        ori_data.reset_index(drop=True, inplace=True)

    data_df = ori_data
    return data_df

def preprocess_data(
        data_df: pd.DataFrame,
        column_to_process: str,
        remove_hyphens: bool = False,
        remove_underscores: bool = False,
):
    
    print(f"Convert text to lower case and strip leading/trailing whitespace")
    data_df[column_to_process] = data_df[column_to_process].str.lower().str.strip().str.replace(r'\s+', ' ', regex=True)
    
    if remove_hyphens:
        print(f"Replace hyphens with spaces")
        data_df[column_to_process] = data_df[column_to_process].str.replace('-', ' ', regex=False)
    if remove_underscores:
        print(f"Replace underscores with nothing")
        data_df[column_to_process] = data_df[column_to_process].str.replace('_', '', regex=False)

    print(f"Removing extra whitespace")
    data_df[column_to_process] = data_df[column_to_process].str.strip().str.replace(r'\s+', ' ', regex=True)

    return data_df

def preprocess_chexpert_data(
        data_df: pd.DataFrame,
        column_to_process: str,
        remove_hyphens: bool = False,
        remove_underscores: bool = False,
):
    print(f"Convert text to lower case and strip leading/trailing whitespace")
    data_df[column_to_process] = data_df[column_to_process].str.lower().str.strip().str.replace(r'\s+', ' ', regex=True)
    
    if remove_hyphens:
        print(f"Replace hyphens with spaces")
        data_df[column_to_process] = data_df[column_to_process].str.replace('-', ' ', regex=False)
    if remove_underscores:
        print(f"Replace underscores with nothing")
        data_df[column_to_process] = data_df[column_to_process].str.replace('_', '', regex=False)

    print(f"Removing extra whitespace")
    data_df[column_to_process] = data_df[column_to_process].str.strip().str.replace(r'\s+', ' ', regex=True)

    data_df['chart_id'] = data_df['subject_id'].astype(str) + '_' + data_df['study_id'].astype(str)
    # Create a list of columns in the desired order
    desired_order = ['subject_id', 'study_id', 'chart_id']
    # Add the remaining columns to the list while preserving their order
    remaining_columns = [col for col in data_df.columns if col not in desired_order]
    new_column_order = desired_order + remaining_columns
    # Reassign the columns of DataFrame based on the new order
    data_df = data_df[new_column_order]

    return data_df

def process_list(words):
    # Convert each word to lowercase, replace "_" and "-" with " "
    return [word.lower().replace("_", " ").replace("-", " ") for word in words]

def chexpert_filter_ner_df(input_named_entity_df):
    filtered_named_entity_df = input_named_entity_df[(input_named_entity_df['ner_list'].str.count('[a-zA-Z+]') > 1) & (~input_named_entity_df['ner_list'].str.isdigit())]
    return filtered_named_entity_df

def drop_duplicates_within_group(df):
    return df.drop_duplicates(subset='ner_list', keep='first')

def ner_tokenize_sentences(
        text
):
    # Use NLTK's sentence tokenizer
    sentences = sent_tokenize(text)
    # Convert each sentence to lowercase
    processed_sentences = [sentence.lower() for sentence in sentences]
    return processed_sentences

def ner_process_data(
        data_df: pd.DataFrame,
):
    # Split text by '//' and remove '//' from the text
    data_df['processed_sentences'] = data_df['text'].apply(lambda x: x.split('//'))
    data_df = data_df.explode('processed_sentences').copy()
    data_df['processed_sentences'] = data_df['processed_sentences'].str.replace('//', '', regex=False)

    data_df['processed_sentences'] = data_df['processed_sentences'].apply(ner_tokenize_sentences)
    ner_df = data_df.explode('processed_sentences').copy()
    ner_df.reset_index(drop=True, inplace=True)

    # Strip leading/trailing whitespace and replace multiple spaces with a single space
    ner_df['processed_sentences'] = ner_df['processed_sentences'].str.strip().str.replace(r'\s+', ' ', regex=True)

    # Reset index and add sentence_id
    ner_df = ner_df.reset_index(drop=True)
    ner_df['sentence_id'] = ner_df.index + 1
    return ner_df

def tokenize_text(tokenizer, input_string: str):
    tokenized_output = tokenizer(input_string, return_tensors="pt")
    input_ids = tokenized_output.input_ids
    return_tokens = input_ids[0]
    num_tokens = input_ids.size(1)
    return num_tokens, return_tokens

def split_tokens(
        row,
        chunk_token_limit
):
    # Step 1: Count how many times to half the token_count
    token_count = row['token_count']
    split_count = 0
    while token_count > chunk_token_limit:
        token_count /= 2
        split_count += 1
    
    # Step 2: Split input_ids_processed_sentences
    total_tokens = row['token_count']
    tokens_per_chunk = total_tokens // (2 ** split_count)
    remaining_tokens = total_tokens % (2 ** split_count)

    input_ids = row['input_ids_processed_sentences']  # Assuming the tensor is at the first index
    chunks = []

    start_index = 0
    for i in range(2 ** split_count):
        end_index = start_index + tokens_per_chunk + (1 if i < remaining_tokens else 0)
        chunks.append(input_ids[start_index:end_index])
        start_index = end_index

    return chunks

def update_chunks(
        row,
        overlap
):
    chunks = row['chunks']
    num_chunks = len(chunks)

    # Create a new list to store the updated chunks
    updated_chunks = []

    for i in range(num_chunks):
        # For the first chunk
        if i == 0 and num_chunks > 1:
            updated_chunk = torch.cat((chunks[i], chunks[i+1][:overlap]))
        # For the last chunk
        elif i == num_chunks - 1 and num_chunks > 1:
            updated_chunk = torch.cat((chunks[i-1][-overlap:], chunks[i]))
        # For middle chunks
        elif num_chunks > 2:
            updated_chunk = torch.cat((chunks[i-1][-overlap:], chunks[i], chunks[i+1][:overlap]))
        else:
            # For a single chunk scenario
            updated_chunk = chunks[i]

        updated_chunks.append(updated_chunk)

    return updated_chunks

def decode_chunk(
        chunk,
        tokenizer
):
    return tokenizer.decode(chunk, skip_special_tokens=True)

def update_token_count(
        input_ids
):
    return input_ids.size(0)

def flan_t5_perform_ner(
        text: str, 
        prompt: str, 
        model, 
        tokenizer, 
        flan_t5_max_new_tokens: int,
        flan_t5_max_time: int,
        flan_t5_temperature: float,
        flan_t5_top_p: float,
        flan_t5_no_repeat_ngram_size: int,
        flan_t5_repetition_penalty: float
):
    # Construct the full prompt text
    full_prompt = prompt + text
    input_ids = tokenizer(full_prompt, return_tensors="pt").input_ids.cuda()
    outputs = model.generate(
        input_ids, 
        max_new_tokens=flan_t5_max_new_tokens,
        max_time=flan_t5_max_time, # seconds
        temperature=flan_t5_temperature,
        top_p=flan_t5_top_p,
        no_repeat_ngram_size=flan_t5_no_repeat_ngram_size,
        repetition_penalty=flan_t5_repetition_penalty,
    )
    ner_outputs = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return ner_outputs

def ner_remove_duplicates(lst):
    return list(set(lst))

def flan_t5_model_ner(
        ner_df: pd.DataFrame,
        column_for_ner: str,
        flan_t5_ner_prompts: dict,
        model,
        tokenizer,
        flan_t5_max_new_tokens: int,
        flan_t5_max_time: int,
        flan_t5_temperature: float,
        flan_t5_top_p: float,
        flan_t5_no_repeat_ngram_size: int,
        flan_t5_repetition_penalty: float
):
    total_iterations = len(ner_df)
    sequence_step_size = 100
    print_sequence = list(np.arange(1, total_iterations + sequence_step_size, sequence_step_size))
    if print_sequence[-1] != total_iterations:
        print_sequence[-1] = total_iterations
    step_size = print_sequence if total_iterations >= 100 else list(np.arange(1, total_iterations + 1, 1))

    print("Performing NER")
    # Iterate through the DataFrame with an enumeration for tracking progress
    for i, (index, row) in enumerate(ner_df.iterrows(), start=1):
        for prompt_type, prompt_text in flan_t5_ner_prompts.items():
            # Perform NER for each prompt type
            ner_start_time = datetime.now()
            ner_result = flan_t5_perform_ner(
                text=row[column_for_ner], 
                prompt=prompt_text, 
                model=model, 
                tokenizer=tokenizer, 
                flan_t5_max_new_tokens=flan_t5_max_new_tokens,
                flan_t5_max_time=flan_t5_max_time,
                flan_t5_temperature=flan_t5_temperature,
                flan_t5_top_p=flan_t5_top_p,
                flan_t5_no_repeat_ngram_size=flan_t5_no_repeat_ngram_size,
                flan_t5_repetition_penalty=flan_t5_repetition_penalty
            )
            ner_end_time = datetime.now()
            ner_time_difference = (ner_end_time - ner_start_time).total_seconds()
            # Store the NER result in the DataFrame
            ner_df.at[index, prompt_type] = ner_result
            ner_df.at[index, 'ner_processing_time'] = ner_time_difference
        if i in step_size:
            report_time = ner_end_time.replace(tzinfo=pytz.utc)
            report_time = report_time.astimezone(pytz.timezone('US/Pacific'))
            report_time = report_time.strftime('%Y-%m-%d %H:%M:%S')

            print(f"\n\n##########")
            print(f"Iteration {i}/{total_iterations} completed")
            print(f"Completion time: {report_time}")
            print(f"NER iteration time: {ner_time_difference} seconds")
            print(f"RESULT: {ner_result}")

    # Extracting column names from the prompts dictionary
    prompt_columns = list(flan_t5_ner_prompts.keys())
    # Combine the data from the prompt columns into a new column 'ner_output'
    ner_df['ner_output'] = ner_df[prompt_columns].apply(lambda x: ', '.join(x.dropna()), axis=1)
    # Split 'ner_output' into lists
    ner_df['ner_output'] = ner_df['ner_output'].str.split(', ')
    # Selecting only specific columns
    # selected_df = ner_df.drop(prompt_columns, axis=1) # no longer want to drop these columns
    selected_df = ner_df
    # Remove duplicates in 'ner_output'
    selected_df['ner_output'] = selected_df['ner_output'].apply(ner_remove_duplicates)
    # exploded_data_df = selected_df.explode('ner_output').reset_index(drop=True)

    return selected_df

def chexpert_flan_t5_model_ner(
        ner_df: pd.DataFrame,
        column_for_ner: str,
        flan_t5_ner_prompts: dict,
        model,
        tokenizer,
        flan_t5_ner_max_length: int
):
    total_iterations = len(ner_df)
    sequence_step_size = 100
    print_sequence = list(np.arange(1, total_iterations + sequence_step_size, sequence_step_size))
    if print_sequence[-1] != total_iterations:
        print_sequence[-1] = total_iterations
    step_size = print_sequence if total_iterations >= 100 else list(np.arange(1, total_iterations + 1, 1))

    print("Performing NER")
    # Iterate through the DataFrame with an enumeration for tracking progress
    for i, (index, row) in enumerate(ner_df.iterrows(), start=1):
        for prompt_type, prompt_text in flan_t5_ner_prompts.items():
            # Perform NER for each prompt type
            ner_start_time = datetime.now()
            ner_result = flan_t5_perform_ner(
                text=row[column_for_ner], 
                prompt=prompt_text, 
                model=model, 
                tokenizer=tokenizer, 
                flan_t5_ner_max_length=flan_t5_ner_max_length
            )
            ner_end_time = datetime.now()
            ner_time_difference = (ner_end_time - ner_start_time).total_seconds()
            # Store the NER result in the DataFrame
            ner_df.at[index, prompt_type] = ner_result
            ner_df.at[index, 'ner_processing_time'] = ner_time_difference
        if i in step_size:
            report_time = ner_end_time.replace(tzinfo=pytz.utc)
            report_time = report_time.astimezone(pytz.timezone('US/Pacific'))
            report_time = report_time.strftime('%Y-%m-%d %H:%M:%S')

            print(f"\n\n##########")
            print(f"Iteration {i}/{total_iterations} completed")
            print(f"Completion time: {report_time}")
            print(f"NER iteration time: {ner_time_difference} seconds")
            print(f"RESULT: {ner_result}")
    
    # Extracting column names from the prompts dictionary
    prompt_columns = list(flan_t5_ner_prompts.keys())
    # Combine the data from the prompt columns into a new column 'ner_output'
    ner_df['ner_output'] = ner_df[prompt_columns].apply(lambda x: ', '.join(x.dropna()), axis=1)
    # Split 'ner_output' into lists
    ner_df['ner_output'] = ner_df['ner_output'].str.split(', ')
    # Selecting only specific columns
    selected_df = ner_df.drop(prompt_columns, axis=1)
    # Remove duplicates in 'ner_output'
    selected_df['ner_output'] = selected_df['ner_output'].apply(ner_remove_duplicates)
    # exploded_data_df = selected_df.explode('ner_output').reset_index(drop=True)

    return selected_df

def remove_delimiter(
        item
):
    if isinstance(item, list):
        # Process each string in the list and remove empty strings
        cleaned_list = [' '.join(s.replace('####', '').split()) for s in item]
        return [s for s in cleaned_list if s]  # Filter out empty strings
    elif isinstance(item, str):
        # Process the string
        return ' '.join(item.replace('####', '').split())
    else:
        return item  # Return as is if not a string or list

def get_embeddings(text, model, tokenizer, max_length):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=max_length)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1)

def calculate_cosine_similarity(target_text, text_list, model, tokenizer, cosine_similarity_max_length):
    target_embedding = get_embeddings(target_text, model, tokenizer, cosine_similarity_max_length)
    similarities = []
    
    for text in text_list:
        text_embedding = get_embeddings(text, model, tokenizer, cosine_similarity_max_length)
        sim = cosine_similarity(target_embedding, text_embedding)
        similarities.append((text, sim[0][0]))

    return similarities

def entity_location_search(
        spacy_doc_df: pd.DataFrame,
        synonym_list: list
):
    ner_list = []
    for index, row in spacy_doc_df.iterrows():  # Iterate through rows of doc_df
        doc = row['doc']
        chart_id = row['chart_id']  # Get the 'chart_id' value from doc_df
        # doc_text = ' '.join([token.text for token in doc])
        for ent in doc.ents:
            entity_name = ent.text
            entity_start_location = ent.start
            entity_end_location = ent.end

            ner_list.append({
                'chart_id': chart_id,
                'doc_format': doc,
                # 'text': doc_text,
                'entity_name': entity_name,
                'entity_start': entity_start_location,
                'entity_end': entity_end_location,
            })
    full_ner_df = pd.DataFrame(ner_list)
    mask = full_ner_df['entity_name'].isin(synonym_list)
    ner_df = full_ner_df[mask]

    return ner_df

def extract_text_using_ner_location(
        ner_data_df: pd.DataFrame,
        n_words_before_ner: int,
        n_words_after_ner: int
):
    ner_data_df['extracted_text'] = ''
    for index, row in ner_data_df.iterrows():
        entity_start = row['entity_start']
        entity_end = row['entity_end']
        doc_format = row['doc_format']

        # Split the text into words -- don't need this anymore because doc_format is already split and this only works on string format text
        # words = text.split()

        # Calculate the start and end indices for the extraction
        start_index = max(0, entity_start - n_words_before_ner)
        end_index = min(len(doc_format), entity_end + n_words_after_ner)

        # Extract the words within the specified range
        extracted_doc_text = doc_format[start_index:end_index]

        # Join the extracted words back into a text string -- don't need this anymore because not running text.split() fn
        # extracted_doc_text = ' '.join(extracted_chars)

        # Turn extracted_doc_text into string format -- need this now because I am extracting text from a SpaCy doc
        extracted_text = ' '.join([token.text for token in extracted_doc_text])
        cleaned_extracted_text = extracted_text.replace('\n', ' ').strip()  # Replace \n with space and remove leading/trailing spaces
        cleaned_extracted_text = ' '.join(cleaned_extracted_text.split())  # Replace consecutive spaces with a single space

        # Update the 'extracted_text' column in the DataFrame
        ner_data_df.at[index, 'extracted_text'] = cleaned_extracted_text

    # Reset index
    ner_data_df = ner_data_df.reset_index(drop=True)

    return ner_data_df

def run_context_extraction(
            test,
            data_df,
            named_entity_df,
            target_word,
            info_retrieval,
            save_extracted_outputs,
            data_path,
            extraction_timestamp,
            save_folder_path,
):

    print(f"\nFiltering Named Entity Data - Target Word: {target_word}")
    selected_synonyms = named_entity_df[named_entity_df['target_word'] == target_word]
    selected_synonyms = selected_synonyms['ner_list']
    print(f"Named Entity Data Filtered - Total Size: {len(selected_synonyms)}")

    nlp = medspacy.load()
    print(f"\nCurrent SpaCy NLP Pipeline: {nlp.pipe_names}")

    print(f"\nBuilding SpaCy TargetRules from Synonym List")
    final_synonym_list = [word.lower() for word in selected_synonyms]
    target_rules = []
    for item in final_synonym_list:
        target_rule = TargetRule(item, 'CONDITION')
        target_rules.append(target_rule)
    # Add the dynamically generated TargetRules to the medspacy_target_matcher pipe
    nlp.get_pipe('medspacy_target_matcher').add(target_rules)
    print(f"{len(final_synonym_list)} TargetRules successfully added to Target Matcher pipe")

    print(f"\nBuilding SpaCy Doc List Dataframe")
    doc_list = []
    chart_id_list = []
    total_iterations = len(data_df)
    sequence_step_size = 100
    print_sequence = list(np.arange(1, total_iterations + sequence_step_size, sequence_step_size))
    if print_sequence[-1] != total_iterations:
        print_sequence[-1] = total_iterations
    step_size = print_sequence if total_iterations >= 100 else list(np.arange(1, total_iterations + 1, 1))
    for i, (text, chart_id) in enumerate(zip(data_df['text'], data_df['chart_id']), start=1):
        doc = nlp(text)
        doc_list.append(doc)
        chart_id_list.append(chart_id)
        if i in step_size:
            report_time = datetime.now().replace(tzinfo=pytz.utc)
            report_time = report_time.astimezone(pytz.timezone('US/Pacific'))
            report_time = report_time.strftime('%Y-%m-%d %H:%M:%S')

            print(f"\n##########")
            print(f"Target feature: {target_word}")
            print(f"Iteration {i}/{total_iterations} completed")
            print(f"Completion time: {report_time}\n")
    # Create a DataFrame with 'doc' and 'chart_id' columns
    doc_df = pd.DataFrame({'doc': doc_list, 'chart_id': chart_id_list})
    print(f"SpaCy Doc Dataframe Complete")

    print(f"\nFinding Entities and Their Locations")
    ner_location_df = entity_location_search(
        spacy_doc_df=doc_df,
        synonym_list=final_synonym_list
    )
    print(f"Search Completed")

    print(f"\nExtracting Essential Text")
    ner_extracted_df = extract_text_using_ner_location(
        ner_data_df=ner_location_df,
        n_words_before_ner=info_retrieval['n_words_before_ner'],
        n_words_after_ner=info_retrieval['n_words_after_ner']
    )
    print(f"Extraction complete")

    print(f"\nCreate 'extraction_id' Column")
    ner_extracted_df['extraction_id'] = (ner_extracted_df.index + 1).astype(str) + "_" + ner_extracted_df['chart_id'].astype(str)
    columns = ['chart_id', 'extraction_id'] + [col for col in ner_extracted_df.columns if col not in ['chart_id', 'extraction_id']]
    ner_extracted_df = ner_extracted_df[columns]
    print(f"Column Created")

    print(f"\nSaving Context Extraction Dataframe")
    if save_extracted_outputs:
        save_filename = os.path.splitext(os.path.basename(data_path))[0]
        target_word = target_word.replace(" ", "_")
        if test:
            save_filename = f"{save_folder_path}/TEST_{target_word}_extracted_{extraction_timestamp}_{save_filename}.csv"
            ner_extracted_df.to_csv(save_filename, index=False)
        else:
            save_filename = f"{save_folder_path}/{target_word}_extracted_{extraction_timestamp}_{save_filename}.csv"
            ner_extracted_df.to_csv(save_filename, index=False)
        print(f"Saved: {save_filename}")

def model_generate_system_content(
        delimiter: str,
        features_df: pd.DataFrame,
        system_content_template: str,
        uncertainty_label: bool,
):
    # if uncertainty_label:
    fixed_system_content = pd.DataFrame()
    for index, row in features_df.iterrows():
        fixed_system_content.at[index, 'content_message'] = system_content_template.format(
            delimiter=delimiter,
            target_word_format_str=row['target_word'].lower(),
            feature_present_format_str=row['feature_present'].lower(),
            feature_negated_format_str=row['feature_negated'].lower(),
            feature_uncertain_format_str=row['feature_uncertain'].lower(),
            definition_format_str=row['definition'],
            example_1=row['example_1'],
            example_2=row['example_2'],
            example_3=row['example_3'],
            example_4=row['example_4'],
            example_5=row['example_5'],
            prompt="{prompt}"
        )
    # else:
    #     fixed_system_content = pd.DataFrame()
    #     for index, row in features_df.iterrows():
    #         fixed_system_content.at[index, 'content_message'] = system_content_template.format(
    #             delimiter=delimiter,
    #             feature_present_format_str=row['feature_present'],
    #             feature_negated_format_str=row['feature_negated'],
    #             prompt="{prompt}"
    #         )
    return fixed_system_content

def model_create_single_feature_llm_dialogs(
        model_name,
        data_df: pd.DataFrame,
        content_message_column_names_list: list,
        text_column_name: str = 'text',
):
    print(f"model: {model_name}")

    # Initialize loop_data list
    loop_data = []
    # Iterate through rows of data_df
    for index, row in data_df.iterrows():
        # Initialize a dictionary for the current row
        row_data = {
            'chart_id': row['chart_id'],
            'extraction_id': row['extraction_id'],
            'entity_name': row['entity_name'],
            'feature': row['target_word'],
            text_column_name: row[text_column_name],
        }
        
        # Create separate 'dialogs' columns for each content message
        for column_name in content_message_column_names_list:
            if column_name in data_df.columns:
                # Generate the suffix for the dialogs column by removing 'content_message'
                suffix = column_name.replace('_content_message', '')
                new_column_name = f'dialogs_{suffix}'
                
                # Format the content message with the provided text, if necessary
                formatted_content_message = row[column_name].format(prompt=row[text_column_name])
                
                # Add the formatted message to the row_data with the new column name
                row_data[new_column_name] = formatted_content_message
        
        # Add the current row's data to loop_data
        loop_data.append(row_data)
    
    # Create a new DataFrame using loop_data
    dialogs_df = pd.DataFrame(loop_data)
    return dialogs_df

def extract_llm_assertion_output(decoded_results, model_name):
    # Define the pattern to match text between ^|prompter|^: and ^|assistant|^:
    # We use re.DOTALL to allow the dot (.) to match newlines as well
    if model_name == "m42-health/med42-70b" or model_name == "meta-llama/Llama-2-70b-hf":
        pattern = re.compile(r"\<\|assistant\|\>: label:(.*)", re.DOTALL)
    if model_name == "epfl-llm/meditron-70b":
        pattern = re.compile(r"Assistant: label:(.*)", re.DOTALL)
    if model_name == "mistralai/Mixtral-8x7B-Instruct-v0.1":
        pattern = re.compile(r"\[/INST\] Model answer(.*)", re.DOTALL)
    if model_name == 'google/flan-t5-xxl':
        pattern = re.compile(r"<pad>\s*(\d)\s*</s>")
    
    # Search for the pattern and extract the text
    match = pattern.search(decoded_results)

    # Remove leading and trailing whitespace
    formatted_decoded_results = match.group(1).strip()
    
    pattern2 = re.compile(r'\d+')
    
    # Search for the pattern and extract the number
    numbers = pattern2.findall(formatted_decoded_results)
    formatted_decoded_results =  [int(num) for num in numbers]
    
    return formatted_decoded_results

def model_assertion(
        model,
        tokenizer,
        assertion_model_name,
        assertion_max_seq_len: int,
        assertion_max_new_tokens: int,
        assertion_temperature: float,
        assertion_top_p: float,
        assertion_do_sample: bool,
        dialogs_df: pd.DataFrame
):
    print(f"Getting Dialog Column Names")
    dialog_columns = [col for col in dialogs_df.columns if col.startswith('dialogs_')]
    print(f"Performing Assertion on: {dialog_columns}")

    print(f"Create 'assertion_text' from 'extracted_text'")
    dialogs_df['assertion_text'] = dialogs_df['extracted_text'].apply(lambda x: '#### ' + x + ' ####')
    dialogs_df.drop('extracted_text', axis=1, inplace=True)

    print("Initializing Assertion Loop")
    llm_output = []
    total_iterations = len(dialogs_df) * len(dialog_columns)
    sequence_step_size = 100
    print_sequence = list(np.arange(1, total_iterations + sequence_step_size, sequence_step_size))
    if print_sequence[-1] != total_iterations:
        print_sequence[-1] = total_iterations
    step_size = print_sequence if total_iterations >= 100 else list(np.arange(1, total_iterations + 1, 1))
    global_iteration = 0
    print(f"Performing Assertion")
    for index, row in dialogs_df.iterrows():
        assertion_data = {}
        for dialog_column in dialog_columns:
            global_iteration += 1
            suffix = dialog_column.replace('dialogs_', '')
            # Model assertion
            tokenized_inputs = tokenizer(
                row[dialog_column], 
                max_length=assertion_max_seq_len, 
                truncation=True,
                # padding='max_length', # Ensure padding to max_length - don't think this is necessary for transformer models (BERT, GPT, etc) unless you are doing batch processing
                return_tensors='pt',
                return_attention_mask=True  # Include attention mask
                )
            total_tokens = tokenized_inputs["input_ids"].size(1)
            input_ids = tokenized_inputs["input_ids"].cuda()
            attention_mask = tokenized_inputs["attention_mask"].cuda()
            # Run model.generate()
            assertion_start_time = datetime.now()
            if assertion_model_name == 'google/flan-t5-xxl':
                results = model.generate(
                    inputs=input_ids, 
                    attention_mask=attention_mask,
                    temperature=assertion_temperature,
                    top_p=assertion_top_p,
                    do_sample=assertion_do_sample,
                    max_new_tokens=assertion_max_new_tokens,
                    eos_token_id=tokenizer.eos_token_id, 
                    pad_token_id=tokenizer.pad_token_id, 
                    max_time=60, # seconds
                    no_repeat_ngram_size=3,
                    repetition_penalty=2.5,
                    )
            else:
                results = model.generate(
                    inputs=input_ids, 
                    attention_mask=attention_mask, # Add attention mask
                    temperature=assertion_temperature, 
                    top_p=assertion_top_p,
                    do_sample=assertion_do_sample,
                    eos_token_id=tokenizer.eos_token_id, 
                    pad_token_id=tokenizer.pad_token_id, 
                    max_new_tokens=assertion_max_new_tokens,
                    )
            assertion_end_time = datetime.now()
            total_assertion_time = (assertion_end_time - assertion_start_time).total_seconds()
            decoded_results = tokenizer.decode(results[0])
            formatted_decoded_results = extract_llm_assertion_output(decoded_results, model_name=assertion_model_name)

            assertion_data.update({
                f'{dialog_column}': row[dialog_column],
                f'total_tokens_{suffix}': total_tokens,
                f'result_{suffix}': formatted_decoded_results,
                f'assertion_time_{suffix}': total_assertion_time,
                })

            if global_iteration in step_size:
                report_time = assertion_end_time.replace(tzinfo=pytz.utc)
                report_time = report_time.astimezone(pytz.timezone('US/Pacific'))
                report_time = report_time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"\n\n##########")
                print(f"Dialog type: {suffix}")
                print(f"Report time: {report_time}")
                print(f"LLM dialog chart ID: {row['chart_id']}")
                print(f"Processing iteration {global_iteration}/{total_iterations}")
                print(f"Total characters: {len(row['assertion_text'])}")
                print(f"Total words: {len(row['assertion_text'].split())}")
                print(f"Total tokens: {total_tokens}")
                content = f"Text: {row['assertion_text']}"
                print(content[:300] + " ...")
                
                print(f"\nTotal assertion time: {total_assertion_time} seconds")
                print(f"RESULTS: {formatted_decoded_results}")
                print(f"Recording LLM output: chart ID {row['chart_id']}")
                print(f"Chart ID {row['chart_id']} output recorded")
                print(f"##########\n\n")

        llm_output.append({
            'prediction_id': index+1,
            'chart_id': row['chart_id'],
            'extraction_id': row['extraction_id'],
            'entity_name': row['entity_name'],
            'feature': row['feature'],
            'text': row['assertion_text'],
            **assertion_data,
        })

    llm_output = pd.DataFrame(llm_output)
    # Organize columns based on specified prefixes and fixed column names
    llm_output_columns = llm_output.columns.tolist()
    fixed_columns = ['prediction_id', 'chart_id', 'extraction_id', 'entity_name', 'feature', 'text']
    total_tokens_columns = [col for col in llm_output_columns if col.startswith('total_tokens_')]
    assertion_time_columns = [col for col in llm_output_columns if col.startswith('assertion_time_')]
    result_columns = [col for col in llm_output_columns if col.startswith('result_')]
    # Combine all columns in the desired order
    ordered_columns = fixed_columns + dialog_columns + total_tokens_columns + assertion_time_columns + result_columns
    # Order dataframe
    llm_output = llm_output[ordered_columns]

    return llm_output

def save_llm_outputs(
        data_path: str,
        test: bool,
        subset_data: bool,
        assertion_timestamp: str,
        save_folder_path: str,
        assertion_model_name: str,
        assertion_use_flash_attention_2: bool,
        llm_output: pd.DataFrame
):
    # Extract the base filename (with extension) from the path
    base_data_filename = os.path.basename(data_path)
    # Remove the file extension
    save_data_name = os.path.splitext(base_data_filename)[0]

    # Get model used
    model_used = assertion_model_name.replace('/', '-')

    if assertion_use_flash_attention_2:
        model_used = f"{model_used}_flash"

    if subset_data:
        file_name = f"{model_used}_assertion_subset_{assertion_timestamp}_{save_data_name}.csv"
    else:
        file_name = f"{model_used}_assertion_{assertion_timestamp}_{save_data_name}.csv"

    if test:
        file_name = f"TEST_{file_name}"

    # Specify the path to your Downloads folder
    save_location = os.path.expanduser(save_folder_path)
    file_path = os.path.join(save_location, file_name)
    # Save the DataFrame to the .csv file in your Downloads folder
    llm_output.to_csv(file_path, index=False)

    return print(f"Save complete: {file_path}")

def send_email(
        smtp_password: str,
        smtp_server: str,
        from_email: str,
        to_email: str,
        message_subject: str,
        email_text: str,
):
    smtp_server = smtp_server  # Replace with your SMTP server
    smtp_port = 587  # Replace with your SMTP server's port number
    smtp_username = from_email  # Replace with your SMTP server username
    smtp_password = smtp_password  # Replace with your SMTP server password
    from_email = from_email  # Replace with your email address
    to_email = to_email  # Replace with the recipient's email address

    # Create message
    message = MIMEMultipart()
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = message_subject
    body = email_text
    message.attach(MIMEText(body, 'plain'))

    # Send the email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()  # Can be omitted
        server.starttls()  # Secure the connection
        server.ehlo()  # Can be omitted
        server.login(smtp_username, smtp_password)
        server.sendmail(from_email, to_email, message.as_string())
        server.close()
        print('Email sent successfully')
    except Exception as e:
        print(f'Failed to send email: {e}')

def send_error_email(
        auth_keys_path: str = "~/local_credentials/auth_keys.json"
):  
    auth_keys_data = get_auth_keys(auth_keys_path=os.path.expanduser(auth_keys_path))
    hostname = socket.gethostname()
    send_email(
        smtp_server="smtp.gmail.com",
        smtp_password=auth_keys_data['GMAIL_SMTP_PASSWORD'][0],
        from_email="iv.lopez.machine.learning@gmail.com",
        to_email="lopezivan256@gmail.com",
        message_subject=f"{hostname}: VM TASK FAILED",
        email_text=f"Your VM task has failed to complete."
        )