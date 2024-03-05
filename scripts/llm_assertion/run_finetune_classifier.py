import pandas as pd
import numpy as np
import torch
import os
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer

pd.set_option('display.max_rows', 50)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

def aggregate_llm_labels(
        series
):
    if (series == 1).any():
        return 1
    elif (series == 0).any():
        return 0
    else:
        return 2

def finetune_classifier():

    print(f"\nSetting Parameters")
    seed = 1234
    model_name = "emilyalsentzer/Bio_ClinicalBERT" # can also explore gemma-3b and 7b, and other models
    llm_data_path = "~/llm_data/moud_llm_output/assertion_output/google-flan-t5-xxl_assertion_2024_02_17_17:21:55_major_depression_extracted_2024-02-02_14:31:48_train_moud_note_df_2023-11-08.csv"
    column_for_llm_label = "result_flan-t5-xxl"
    max_token_len = 512 # bio clinBERT, can also explore gemma-3b and 7b, and other models
    batch_size = 8
    num_folds = 10
    learning_rate = 5e-5 # will be tuned
    num_train_epochs = 10 # will be tuned
    metric_for_evaluation = 'auc' # we need to build this function

    print(f"\nSending Model to CUDA")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') # CUDA should always be available

    print(f"\nLoading Data")
    llm_data_df = pd.read_csv(os.path.expanduser(llm_data_path))
    data_with_full_text = pd.read_csv(os.path.expanduser(data_with_full_text_path))

    print(f"\nData Processing")
    # what is going to be given to the candidate model for fine-tuning
    # goal: pd df with columns: text, label, aggregate labels


    for col in llm_data_df.columns:
        if col.startswith('result_'):
            llm_data_df[col] = llm_data_df[col].str.replace(r'[\[\]]', '', regex=True).astype(int)
    aggregated_llm_labeled_data = llm_data_df.groupby('chart_id').agg({col: aggregate_llm_labels for col in llm_data_df.columns if col.startswith('result_')}).reset_index()
    merged_text_df = aggregated_llm_labeled_data.merge(data_with_full_text, on='chart_id', how='left')
    merged_text_df['text'] = merged_text_df['text'].apply(clean_text)
    
    llm_data_df = llm_data_df[['text', 'result_flan-t5-xxl']]