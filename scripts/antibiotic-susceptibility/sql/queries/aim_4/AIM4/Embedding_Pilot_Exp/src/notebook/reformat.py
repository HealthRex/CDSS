import json
import pandas as pd
from pathlib import Path


def process_labeler_results(labeler_results_path, input_data_path=None, output_dir=None, index_set = None):
    """
    Process labeler results from JSONL file and optionally merge with input data.
    
    Args:
        labeler_results_path (str): Path to the labeler results JSONL file
        input_data_path (str, optional): Path to the input data JSONL file for merging
        output_dir (str, optional): Directory to save output CSV files
    
    Returns:
        tuple: (df, df_true, merged_df_true) where:
            - df: Complete DataFrame with all records
            - df_true: DataFrame with only records where subdomain_yes=True
            - merged_df_true: df_true merged with input data (if input_data_path provided)
    """
    
    # Load labeler results data
    with open(labeler_results_path, 'r') as f:
        data = [json.loads(line) for line in f if line.strip()]
    
    records = []
    
    for entry in data:
        index = entry['index']
        domain = entry['domain']
        subdomains = entry['subdomains']
        
        # Track if *any* subdomain_yes is True for this domain
        any_subdomain_yes = False
        for sd in subdomains:
            subdomain = sd['subdomain']
            subdomain_yes = sd['yes']
            subdomain_rationale = sd['rationale']
            
            error_codes = sd['error_codes']
            # Track if *any* error_code_yes is True for this subdomain
            any_error_code_yes = False
            for ec in error_codes:
                error_code = ec['error_code']
                error_code_yes = ec['yes']
                error_code_rationale = ec['rationale']
                # if error_code_yes:
                    # any_error_code_yes = True
                records.append({
                    'index': index,
                    'domain': domain,
                    'subdomain': subdomain,
                    'subdomain_yes': subdomain_yes,
                    'subdomain_rationale': subdomain_rationale,
                    'error_code': error_code,
                    'error_code_yes': error_code_yes,
                    'error_code_rationale': error_code_rationale,
                })
        
        #     # If NO error_code_yes=True for this subdomain, record a default
        #     if not any_error_code_yes:
        #         records.append({
        #             'index': index,
        #             'domain': domain,
        #             'subdomain': subdomain,
        #             'subdomain_yes': subdomain_yes,
        #             'subdomain_rationale': subdomain_rationale,
        #             'error_code': "no matched",
        #             'error_code_yes': False,
        #             'error_code_rationale': "no matched error codes",
        #         })
            
        #     # Track at domain level if any subdomain_yes
        #     if subdomain_yes:
        #         any_subdomain_yes = True
        
        # # If NO subdomain_yes=True for this domain, record a default
        # if not any([sd['yes'] for sd in subdomains]):
        #     records.append({
        #         'index': index,
        #         'domain': domain,
        #         'subdomain': "no matched subdomains",
        #         'subdomain_yes': False,
        #         'subdomain_rationale': "no matched subdomain",
        #         'error_code': "no matched",
        #         'error_code_yes': False,
        #         'error_code_rationale': "no matched error codes",
        #     })
    
    df = pd.DataFrame(records)
    df = df[df["index"].isin(index_set)]
    df_true = df[(df["subdomain_yes"] == True)]
    df_true = df_true[df_true["index"].isin(index_set)]
    
    merged_df_true = None
    if input_data_path:
        # Load input data
        with open(input_data_path, 'r') as f:
            input_data = [json.loads(line) for line in f if line.strip()]
            input_data = pd.DataFrame(input_data).drop_duplicates()
            input_data = input_data[input_data["index"].isin(index_set)]

        
        # Merge with input data
        merged_df_true = df_true.merge(input_data, on="index", how="inner")
        # df_true_columns = df_true.columns.difference(['index'])  # exclude the join column
        # for col in df_true_columns:
        #     merged_df_true[col] = merged_df_true[col].fillna("No Error At All")
    
    # Save output files if output_dir is provided
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(output_path / "raw_df.csv", index=False)
        df_true.to_csv(output_path / "df_true.csv", index=False)
        
        if merged_df_true is not None:
            merged_df_true.to_csv(output_path / "merged_df_true.csv", index=False)
    
    return df, df_true, merged_df_true

def find_index (input_path):
    with open(input_path, 'r') as f:
        data = [json.loads(line) for line in f if line.strip()]
        return set([entry["index"] for entry in data])


def main(parent_path, index_set):
    """
    Example usage of the process_labeler_results function.
    """
    # Example paths - adjust these to match your actual file structure
    labeler_results_path = f"{parent_path}/labeler_results.jsonl"
    input_data_path = f"{parent_path}/identifier_results_input.jsonl"
    output_dir = f"{parent_path}"
    
    # Process the data
    df, df_true, merged_df_true = process_labeler_results(
        labeler_results_path=labeler_results_path,
        input_data_path=input_data_path,
        output_dir=output_dir,
        index_set=index_set
    )
    
    print(f"Total records: {len(df)}")
    print(f"Records with subdomain_yes=True: {len(df_true)}")
    if merged_df_true is not None:
        print(f"Merged records: {len(merged_df_true)}")
    
    return df, df_true, merged_df_true


if __name__ == "__main__":
    index_set = find_index("src/DSPy_results_batch_1000_dedup_with_prev_msg_w_ref/identifier_results.jsonl")
    df, df_true, merged_df_true = main("src/DSPy_results_batch_1000_dedup_with_prev_msg", index_set) 
    df, df_true, merged_df_true = main("src/DSPy_results_batch_1000_dedup_with_prev_msg_w_ref", index_set) 