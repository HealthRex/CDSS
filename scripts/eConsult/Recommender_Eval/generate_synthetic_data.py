import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

def generate_synthetic_data(data_dir: str = 'data') -> None:
    """Generate synthetic e-consultation data for testing the recommender system."""
    
    # Set random seed for reproducibility
    random.seed(42)
    np.random.seed(42)
    
    # Define parameters
    n_users = 1000
    n_specialists = 200
    n_interactions = 5000
    
    # Generate user IDs
    user_ids = [f"user_{i}" for i in range(1, n_users + 1)]
    
    # Generate specialist/item IDs (representing different specialists or consultation types)
    item_ids = [f"specialist_{i}" for i in range(1, n_specialists + 1)]
    
    # Generate interactions
    interactions = []
    base_time = datetime(2023, 1, 1)
    
    for _ in range(n_interactions):
        user_id = random.choice(user_ids)
        item_id = random.choice(item_ids)
        
        # Add some bias to make certain specialists more popular
        if random.random() < 0.3:  # 30% chance to pick from top 20 specialists
            item_id = random.choice(item_ids[:20])
        
        # Generate timestamp (spread over 2 years)
        days_offset = random.randint(0, 730)
        hours_offset = random.randint(0, 23)
        minutes_offset = random.randint(0, 59)
        
        timestamp = base_time + timedelta(days=days_offset, hours=hours_offset, minutes=minutes_offset)
        timestamp_unix = int(timestamp.timestamp())
        
        interactions.append({
            'user_id': user_id,
            'item_id': item_id,
            'timestamp': timestamp_unix
        })
    
    # Create DataFrame
    df = pd.DataFrame(interactions)
    
    # Remove duplicates (same user consulting same specialist at same time)
    df = df.drop_duplicates(subset=['user_id', 'item_id', 'timestamp'])
    
    # Sort by timestamp
    df = df.sort_values('timestamp')
    
    # Split data into train/valid/test (80/10/10)
    n_total = len(df)
    train_size = int(0.8 * n_total)
    valid_size = int(0.1 * n_total)
    
    train_df = df[:train_size]
    valid_df = df[train_size:train_size + valid_size]
    test_df = df[train_size + valid_size:]
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Save to CSV files
    train_df.to_csv(f'{data_dir}/train.csv', index=False)
    valid_df.to_csv(f'{data_dir}/valid.csv', index=False)
    test_df.to_csv(f'{data_dir}/test.csv', index=False)

    print(f"Generated synthetic data:")
    print(f"- Train set: {len(train_df)} interactions")
    print(f"- Valid set: {len(valid_df)} interactions")
    print(f"- Test set: {len(test_df)} interactions")
    print(f"- Total users: {df['user_id'].nunique()}")
    print(f"- Total items: {df['item_id'].nunique()}")
    
    # Display sample data
    print(f"\nSample training data:")
    print(train_df.head())

if __name__ == "__main__":
    generate_synthetic_data()
