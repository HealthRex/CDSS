import numpy as np
import pdb
from pulp import *
import pandas as pd
import os, glob
import seaborn as sns
from scipy.stats import kruskal
import scikit_posthocs as sp
from scipy.stats import mannwhitneyu
from dotenv import load_dotenv

# ------------------------
# Credentials
# ------------------------
load_dotenv('./Credentials.env', override=True)

# Explicitly set service account key path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""] = "som-nero-phi-jonc101"

# Load BigQuery
%load_ext google.cloud.bigquery
from google.cloud import bigquery

# Initialize client once
client = bigquery.Client(project="som-nero-phi-jonc101")

# ------------------------
# List all tables in dataset
# ------------------------
def all_available_tables(dataset_name='lpch_core_2024', project_id='som-nero-phi-jonc101'):
    try:
        dataset_ref = client.dataset(dataset_name, project=project_id)
        tables = client.list_tables(dataset_ref)
        return [table.table_id for table in tables]
    except Exception as e:
        print(f"❌ Error fetching tables: {e}")
        return []

# ------------------------
# Backup tables into new dataset
# ------------------------
def backup_tables(table_names, project_id, dataset_name, new_dataset_name='copy_lpch_core_2024'):
    try:
        for table in table_names:
            source_table_id = f"{project_id}.{dataset_name}.{table}"
            destination_table_id = f"{project_id}.{new_dataset_name}.{table}"
            
            print(f"Copying table: {source_table_id} → {destination_table_id}")
            job = client.copy_table(source_table_id, destination_table_id)
            job.result()
            print(f"✔ Successfully copied {table}")
    except Exception as e:
        print(f"❌ Error copying tables: {e}")

# ------------------------
# Identify TIMESTAMP/DATETIME columns
# ------------------------
def all_timestamp_columns(table_name, dataset_name='lpch_core_2024', project_id='som-nero-phi-jonc101'):
    try:
        full_table_name = f"{project_id}.{dataset_name}.{table_name}"
        table = client.get_table(full_table_name)
        return [field.name for field in table.schema if field.field_type in ['TIMESTAMP', 'DATETIME']]
    except Exception as e:
        print(f"❌ Error fetching schema for {table_name}: {e}")
        return []

# ------------------------
# Convert STRING columns that look like dates
# ------------------------
def convert_string_to_datetime(table_name, dataset_name, project_id):
    try:
        full_table_name = f"{project_id}.{dataset_name}.{table_name}"
        table = client.get_table(full_table_name)
        string_columns = [field.name for field in table.schema if field.field_type == "STRING"]

        string_datetime_cols = []
        string_date_cols = []

        for column in string_columns:
            query = f"""
                SELECT 
                    COUNTIF(SAFE.PARSE_DATETIME('%Y-%m-%d %H:%M:%S', {column}) IS NOT NULL) AS datetime_count,
                    COUNTIF(SAFE.PARSE_DATE('%Y-%m-%d', {column}) IS NOT NULL) AS date_count
                FROM `{full_table_name}`;
            """
            results = client.query(query).result()
            for row in results:
                if row.datetime_count > 0:
                    string_datetime_cols.append(column)
                if row.date_count > 0:
                    string_date_cols.append(column)

        return string_datetime_cols, string_date_cols
    except Exception as e:
        print(f"❌ Error processing table {table_name}: {e}")
        return [], []

# ------------------------
# Fix STRING → DATETIME/DATE conversion
# ------------------------
def fix_datetime(datetime_columns, date_columns, table_name, dataset_name, project_id):
    try:
        full_table_name = f"{project_id}.{dataset_name}.{table_name}"
        all_columns = datetime_columns + date_columns

        formatted_expressions = []
        for col in datetime_columns:
            formatted_expressions.append(f"SAFE.PARSE_DATETIME('%Y-%m-%d %H:%M:%S', {col}) AS {col}")
        for col in date_columns:
            formatted_expressions.append(f"SAFE.PARSE_DATE('%Y-%m-%d', {col}) AS {col}")

        query = f"""
            CREATE OR REPLACE TABLE `{full_table_name}` AS
            SELECT * EXCEPT({', '.join(all_columns)}), {', '.join(formatted_expressions)}
            FROM `{full_table_name}`;
        """
        print("Executing query:\n", query)
        job = client.query(query)
        job.result()
        print(f"✔ Converted STRING date columns in `{table_name}`")
    except Exception as e:
        print(f"❌ Error converting datetime columns: {e}")

# ------------------------
# Convert LA timezone → UTC
# ------------------------
def convert_la_to_utc(columns, table_name, dataset_name='lpch_core_2024', project_id='som-nero-phi-jonc101'):
    try:
        full_table_name = f"{project_id}.{dataset_name}.{table_name}"
        utc_columns = [f"TIMESTAMP({col}, 'America/Los_Angeles') AS {col}_utc" for col in columns]

        query = f"""
            CREATE OR REPLACE TABLE `{full_table_name}` AS
            SELECT *, {', '.join(utc_columns)}
            FROM `{full_table_name}`;
        """
        print("Executing query:\n", query)
        job = client.query(query)
        job.result()
        print(f"✔ Updated `{table_name}` with UTC timestamps")
    except Exception as e:
        print(f"❌ Error converting {table_name}: {e}")

# ------------------------
# MAIN EXECUTION
# ------------------------
project_id = "som-nero-phi-jonc101"
dataset_name = "lpch_core_2024"

# 1. List all tables
table_names = all_available_tables(dataset_name=dataset_name, project_id=project_id)
print("Tables found:", table_names)

# 2. Backup all tables
backup_tables(table_names, project_id, dataset_name, new_dataset_name="copy_lpch_core_2024")

# 3. Process each table
for table in table_names:
    print(f"\n--- Processing table: {table} ---")
    # Step A: Handle existing datetime/timestamp columns
    datetime_columns = all_timestamp_columns(table, dataset_name, project_id)
    if datetime_columns:
        convert_la_to_utc(datetime_columns, table, dataset_name, project_id)

    # Step B: Handle string columns that look like dates
    str_datetime_cols, str_date_cols = convert_string_to_datetime(table, dataset_name, project_id)
    if str_datetime_cols or str_date_cols:
        fix_datetime(str_datetime_cols, str_date_cols, table, dataset_name, project_id)

print("\n✅ All LPCH tables processed.")
