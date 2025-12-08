#!/usr/bin/env python3
"""
Main Runner Script
Complete pipeline: data preparation + parallel LLM classification
"""

import pandas as pd
import os
import sys
from datetime import datetime
import argparse

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from prepare_test_data import prepare_data_complete
from parallel_classify import AsyncClassifier
import asyncio

async def main():
    """
    Main async function to run the complete pipeline
    """
    parser = argparse.ArgumentParser(description='Complete Async LLM Classification Pipeline')
    parser.add_argument('--data-dir', 
                       default=None,
                       help='Data directory path (if not specified, will be set based on EHR_IncludeInprompt)')
    parser.add_argument('--concurrent', type=int, default=6,
                       help='Max concurrent requests (default: 6)')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay between batches in seconds (default: 1.0)')
    parser.add_argument('--batch-size', type=int, default=10,
                       help='Number of rows per batch (default: 10)')
    parser.add_argument('--checkpoint-interval', type=int, default=10,
                       help='Save checkpoint every N rows (default: 10)')
    parser.add_argument('--EHR_IncludeInprompt', action='store_true',
                       help='Whether to include EHR in prompt')
    
    args = parser.parse_args()
    
    # Original data is always in the base data directory (not EHR-specific)
    base_data_dir = '/Users/sandychen/Desktop/Healthrex_workspace/scripts/Blood_Culture_Stewardship/Adult_refactor/src/data'
    
    # Set default data directory based on EHR_IncludeInprompt if not provided
    if args.data_dir is None:
        args.data_dir = f'{base_data_dir}/EHR_IncludeInprompt_{args.EHR_IncludeInprompt}_new'
    
    print("🚀 Starting Complete Async LLM Classification Pipeline")
    print(f"Original data location: {base_data_dir}")
    print(f"Results will be saved to: {args.data_dir}")
    print(f"Max concurrent: {args.concurrent}")
    print(f"Batch size: {args.batch_size}")
    print(f"Delay between batches: {args.delay}s")
    print(f"Checkpoint interval: {args.checkpoint_interval}")
    print(f"EHR Include Inprompt: {args.EHR_IncludeInprompt}")
    original_file = os.path.join(base_data_dir, 'Test_set_df_note_ORIGINAL.csv')
    
    # Step 1: Data preparation (if needed)
    if not os.path.exists(original_file):
        print("📊 Original data file not found. Preparing data from BigQuery...")
        try:
            # Prepare data in the base directory
            prepare_data_complete(base_data_dir)
        except Exception as e:
            print(f"❌ Error during data preparation: {e}")
            return
    else:
        print("📋 Original data file exists. Proceeding with classification.")
    
    # Step 2: Run async classification
    print("\n🔄 Starting async LLM classification with rate limiting...")
    try:
        classifier = AsyncClassifier(
            data_dir=args.data_dir,
            max_concurrent=args.concurrent,
            delay_between_requests=args.delay,
            batch_size=args.batch_size,
            checkpoint_interval=args.checkpoint_interval,
            EHR_IncludeInprompt=args.EHR_IncludeInprompt
        )
        
        await classifier.run()
        
    except Exception as e:
        print(f"❌ Error during classification: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
