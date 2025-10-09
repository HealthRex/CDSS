import pandas as pd
from datetime import datetime


def split_data(baseline_path='econsult_data/econsult_baseline_proc.csv',
               pred_path='econsult_data/econsult_pred_proc.csv',
               output_dir='data',
               train_ratio=0.7,
               valid_ratio=0.15,
               test_ratio=0.15):
    """
    Split temporal data into train/validation/test sets for RecBole format.
    
    Args:
        baseline_path (str): Path to baseline CSV file
        pred_path (str): Path to prediction CSV file
        output_dir (str): Directory to save split files
        train_ratio (float): Ratio for training set (default: 0.7)
        valid_ratio (float): Ratio for validation set (default: 0.15)
        test_ratio (float): Ratio for test set (default: 0.15)
    
    Returns:
        dict: Summary of split counts
    """
    # Validate ratios
    if abs(train_ratio + valid_ratio + test_ratio - 1.0) > 1e-6:
        raise ValueError("Ratios must sum to 1.0")
    
    # -----------------------------
    # Load your data
    # -----------------------------
    baseline = pd.read_csv(baseline_path, parse_dates=['order_time_jittered'])
    pred = pd.read_csv(pred_path, parse_dates=['order_time_jittered'])

    # Ensure index_date is parsed correctly
    baseline['index_date'] = pd.to_datetime(baseline['index_date'], errors='coerce')
    pred['index_date'] = pd.to_datetime(pred['index_date'], errors='coerce')

    # -----------------------------
    # Step 1. Combine unique queries
    # -----------------------------
    all_index_dates = (
        pd.concat([baseline[['index_date']], pred[['index_date']]])
        .drop_duplicates()
        .sort_values('index_date')
        .reset_index(drop=True)
    )

    # Temporal split
    n = len(all_index_dates)
    train_end = int(train_ratio * n)
    val_end = int((train_ratio + valid_ratio) * n)

    all_index_dates['split'] = 'train'
    all_index_dates.loc[train_end:val_end, 'split'] = 'valid'
    all_index_dates.loc[val_end:, 'split'] = 'test'

    # -----------------------------
    # Step 2. Merge split info back
    # -----------------------------
    baseline = baseline.merge(all_index_dates, on='index_date', how='left')
    pred = pred.merge(all_index_dates, on='index_date', how='left')

    # -----------------------------
    # Step 3. Combine and standardize for RecBole
    # -----------------------------
    # RecBole interaction format: user_id, item_id, timestamp
    baseline_formatted = baseline.rename(columns={
        'index_date': 'user_id',
        'proc_code': 'item_id',
        'order_time_jittered': 'timestamp'
    })[['user_id', 'item_id', 'timestamp', 'split']]

    pred_formatted = pred.rename(columns={
        'index_date': 'user_id',
        'proc_code': 'item_id',
        'order_time_jittered': 'timestamp'
    })[['user_id', 'item_id', 'timestamp', 'split']]

    # Combine baseline (context) and prediction (action) interactions
    combined = pd.concat([baseline_formatted, pred_formatted])

    # -----------------------------
    # Step 4. Save per split
    # -----------------------------
    split_counts = {}
    for split in ['train', 'valid', 'test']:
        subset = combined[combined['split'] == split]
        subset[['user_id', 'item_id', 'timestamp']].to_csv(f'{output_dir}/{split}.csv', index=False)
        split_counts[split] = len(subset)

    print("✅ Data split complete:")
    print(f"Train: {split_counts['train']} rows")
    print(f"Valid: {split_counts['valid']} rows")
    print(f"Test:  {split_counts['test']} rows")
    
    return split_counts


if __name__ == "__main__":
    # Run the function when script is executed directly
    split_data()
