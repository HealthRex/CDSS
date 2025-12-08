#!/usr/bin/env python3
"""
Real-time Performance Monitor
Monitors your classification progress and suggests optimal settings
"""

import pandas as pd
import pickle
import os
import time
from datetime import datetime, timedelta

def monitor_progress(data_dir):
    """Monitor current progress and suggest optimizations"""
    
    checkpoint_file = os.path.join(data_dir, 'classification_checkpoint.pkl')
    backup_file = os.path.join(data_dir, 'Test_set_df_note_backup.csv')
    
    if not os.path.exists(checkpoint_file) or not os.path.exists(backup_file):
        print("❌ No checkpoint or backup files found. Run classification first.")
        return
    
    # Load current progress
    with open(checkpoint_file, 'rb') as f:
        processed_indices = pickle.load(f)
    
    df = pd.read_csv(backup_file)
    total_rows = len(df)
    results_count = df['llm_prediction_result'].notna().sum()
    remaining = total_rows - results_count
    
    print("📊 Current Progress:")
    print(f"   Total rows: {total_rows:,}")
    print(f"   Processed: {results_count:,}")
    print(f"   Remaining: {remaining:,}")
    print(f"   Progress: {(results_count/total_rows)*100:.1f}%")
    
    # Analyze recent performance if we have enough data
    if results_count > 10:
        # Check for any patterns in processing
        null_count = df['llm_prediction_result'].isna().sum()
        error_count = (df['llm_prediction_result'] == 'ERROR').sum() if 'ERROR' in df['llm_prediction_result'].values else 0
        
        print(f"\n📈 Quality Metrics:")
        print(f"   Successful results: {results_count - error_count:,}")
        print(f"   Errors: {error_count:,}")
        print(f"   Null values: {null_count:,}")
        
        if error_count > 0:
            error_rate = (error_count / results_count) * 100
            print(f"   Error rate: {error_rate:.1f}%")
            
            if error_rate > 5:
                print("   ⚠️ High error rate detected! Consider:")
                print("      • Reducing batch_size")
                print("      • Increasing delay between batches")
                print("      • Reducing concurrent requests")
    
    # Suggest optimizations
    print(f"\n💡 Optimization Suggestions:")
    
    if remaining > 1000:
        print("   • For large remaining workload, consider:")
        print("     - batch_size=15-25 for faster processing")
        print("     - concurrent=6-8 for good throughput")
        print("     - delay=1.0-1.5s between batches")
    
    if remaining < 100:
        print("   • For small remaining workload, consider:")
        print("     - batch_size=5-10 for reliability")
        print("     - concurrent=3-4 to avoid overwhelming API")
        print("     - delay=0.5-1.0s between batches")
    
    # Check if we should run performance test
    if remaining > 500 and results_count < 100:
        print(f"\n🧪 Recommendation: Run performance test to find optimal settings:")
        print(f"   python3 test_batch_performance.py --EHR_IncludeInprompt --test-rows 30")

def estimate_completion_time(data_dir, current_batch_size=10, current_delay=1.0):
    """Estimate completion time based on current settings"""
    
    backup_file = os.path.join(data_dir, 'Test_set_df_note_backup.csv')
    if not os.path.exists(backup_file):
        return
    
    df = pd.read_csv(backup_file)
    total_rows = len(df)
    results_count = df['llm_prediction_result'].notna().sum()
    remaining = total_rows - results_count
    
    if remaining == 0:
        print("✅ All rows completed!")
        return
    
    # Estimate based on current settings
    batches_needed = (remaining + current_batch_size - 1) // current_batch_size
    estimated_time = batches_needed * current_delay
    
    print(f"\n⏱️ Time Estimation (current settings):")
    print(f"   Remaining rows: {remaining:,}")
    print(f"   Batch size: {current_batch_size}")
    print(f"   Delay per batch: {current_delay}s")
    print(f"   Batches needed: {batches_needed:,}")
    print(f"   Estimated time: {estimated_time/60:.1f} minutes ({estimated_time/3600:.1f} hours)")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor Classification Performance')
    parser.add_argument('--data-dir', 
                       default=None,
                       help='Data directory path')
    parser.add_argument('--EHR_IncludeInprompt', action='store_true',
                       help='Whether to include EHR in prompt')
    parser.add_argument('--estimate', action='store_true',
                       help='Show time estimation')
    
    args = parser.parse_args()
    
    # Set default data directory
    if args.data_dir is None:
        base_data_dir = '/Users/sandychen/Desktop/Healthrex_workspace/scripts/Blood_Culture_Stewardship/Adult_refactor/src/data'
        args.data_dir = f'{base_data_dir}/EHR_IncludeInprompt_{args.EHR_IncludeInprompt}'
    
    monitor_progress(args.data_dir)
    
    if args.estimate:
        estimate_completion_time(args.data_dir)
