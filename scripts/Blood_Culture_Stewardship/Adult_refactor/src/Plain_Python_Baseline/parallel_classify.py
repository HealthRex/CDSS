#!/usr/bin/env python3
"""
Async LLM Classification Script
Processes Test_set_df_note with LLM predictions using async processing with rate limiting
"""

import pandas as pd
import pickle
import os
from datetime import datetime
from tqdm.asyncio import tqdm
import asyncio
import aiohttp
import time
import argparse
import sys
import json
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to path to import classify
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from prompt import PROMPT
print(PROMPT)

class AsyncClassifier:
    def __init__(self, data_dir, max_concurrent=6, checkpoint_interval=10, delay_between_requests=1.0, EHR_IncludeInprompt=False, batch_size=10):
        self.data_dir = data_dir  # EHR-specific directory for results
        self.max_concurrent = max_concurrent
        self.checkpoint_interval = checkpoint_interval
        self.delay_between_requests = delay_between_requests  # seconds between batches
        self.batch_size = batch_size
        self.new_column_name = 'llm_prediction_result'
        self.EHR_IncludeInprompt = EHR_IncludeInprompt
        
        # Base data directory (where original data is stored)
        self.base_data_dir = '/Users/sandychen/Desktop/Healthrex_workspace/scripts/Blood_Culture_Stewardship/Adult_refactor/src/data'
        
        # File paths
        self.checkpoint_file = os.path.join(data_dir, 'classification_checkpoint_new.pkl')
        self.df_backup_file = os.path.join(data_dir, 'Test_set_df_note_backup_new.csv')
        self.original_file = os.path.join(self.base_data_dir, 'Test_set_df_note_ORIGINAL_new.csv')  # Always read from base directory
        
        # Async-safe counters
        self.processed_count = 0
        self.error_count = 0
        self.lock = asyncio.Lock()
        
        # Rate limiting - simplified approach
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # API configuration
        self.api_url = os.getenv("API_URL")
        self.api_headers = {
            os.getenv("API_HEADER_KEY"): os.getenv("API_KEY"),
            "Content-Type": "application/json"
        }
        
        # Create data directory
        os.makedirs(data_dir, exist_ok=True)
        print(f"✅ Data directory ready: {data_dir}")
        print(f"✅ Max concurrent requests: {max_concurrent}")
        print(f"✅ Batch size: {batch_size}")
        print(f"✅ Delay between batches: {delay_between_requests}s")
    
    def batchify(self, lst, batch_size):
        """Split list into batches of specified size"""
        for i in range(0, len(lst), batch_size):
            yield lst[i:i + batch_size]
        
    def load_data(self):
        """Load the original data and create working copy"""
        print("Loading original data...")
        
        if os.path.exists(self.original_file):
            df_original = pd.read_csv(self.original_file)
            print(f"✅ Loaded original data: {df_original.shape}")
        else:
            raise FileNotFoundError(f"Original data file not found: {self.original_file}")
            
        return df_original
    
    def load_checkpoint(self):
        """Load existing progress if available"""
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'rb') as f:
                processed_indices = pickle.load(f)
            print(f"✅ Loaded checkpoint with {len(processed_indices)} processed rows")
            return processed_indices
        else:
            print("Starting fresh - no checkpoint found")
            return set()
    
    def load_working_data(self, df_original, processed_indices):
        """Load working data - always maintain original structure, accumulate successful results"""
        print("Creating working DataFrame from original data...")
        df_working = df_original.copy()
        
        # Initialize results column
        if self.new_column_name not in df_working.columns:
            df_working[self.new_column_name] = None
            print(f"✅ Initialized column: {self.new_column_name}")
        
        # If we have previous successful results, load them
        if os.path.exists(self.df_backup_file) and len(processed_indices) > 0:
            print("Loading previous successful results...")
            try:
                df_backup = pd.read_csv(self.df_backup_file)
                
                if self.new_column_name in df_backup.columns:
                    # Only restore results for rows that are in processed_indices (verified successful)
                    restored_count = 0
                    for idx in processed_indices:
                        if idx < len(df_backup) and idx < len(df_working):
                            if pd.notna(df_backup.at[idx, self.new_column_name]):
                                df_working.at[idx, self.new_column_name] = df_backup.at[idx, self.new_column_name]
                                restored_count += 1
                    
                    print(f"✅ Restored {restored_count} previous successful results")
                else:
                    print("⚠️ No results column found in backup, starting fresh")
                
            except Exception as e:
                print(f"⚠️ Could not load previous results: {e}")
                print("Starting fresh...")
        
        # Validate consistency
        current_results = df_working[self.new_column_name].notna().sum()
        expected_results = len(processed_indices)
        
        if current_results != expected_results:
            print(f"⚠️ Inconsistency detected: {current_results} results vs {expected_results} processed indices")
            print("This is normal if some previous results were corrupted")
        
        return df_working
    
    async def classify_single_row(self, session, row_data):
        """Classify a single row with simple retry logic"""
        idx, anon_id, note_text, EHR = row_data
        if not self.EHR_IncludeInprompt:
            EHR = None
        
        max_retries = 3
        base_delay = 0.5
        
        for attempt in range(max_retries):
            async with self.semaphore:  # Limit concurrent requests
                try:
                    # Make the API request
                    result = await self.make_api_request(session, anon_id, note_text, EHR)
                    return idx, result, None
                    
                except aiohttp.ClientResponseError as e:
                    if e.status == 429:  # Rate limit error
                        if attempt < max_retries - 1:
                            # Simple exponential backoff: 0.5s, 1s, 2s
                            retry_delay = base_delay * (2 ** attempt)
                            print(f"Rate limit hit for row {idx}, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})")
                            await asyncio.sleep(retry_delay)
                            continue
                        else:
                            return idx, "ERROR", f"Max retries exceeded: {str(e)}"
                    else:
                        return idx, "ERROR", str(e)
                except Exception as e:
                    if attempt < max_retries - 1:
                        retry_delay = base_delay * (2 ** attempt)
                        print(f"Error for row {idx}, retrying in {retry_delay}s: {str(e)}")
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        return idx, "ERROR", str(e)
        
        return idx, "ERROR", "Max retries exceeded"
    
    async def make_api_request(self, session, anon_id, note_text, EHR):
        """Make async API request to LLM"""
        # Get the prompt from the classify module
    
        question = f"{PROMPT}\n\nanon_id: {anon_id}\n\nNOTE:\n{note_text}"
        note_text = re.sub(r'\s+', ' ', note_text.replace('\n', ' ')).strip()
        if EHR:
            question += f"structured EHR data is provided below:\n\nEHR:\n{EHR}"
        else:
            question += f"structured EHR data is not provided."
        # print(f"question: {question}")
        # print(f"EHR: {EHR}")
        # print(f"anon_id: {anon_id}")
        # print(f"note_text: {note_text}")
        payload = {
            "model": "gpt-5",
            "messages": [{"role": "user", "content": question}]
        }
        
        async with session.post(
            self.api_url, 
            headers=self.api_headers, 
            json=payload,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return data["choices"][0]["message"]["content"]
    
    async def save_checkpoint(self, processed_indices, df_working):
        """Save checkpoint and incremental backup - only successful results"""
        async with self.lock:
            if len(processed_indices) > 0:
                # Save checkpoint (set of successfully processed row indices)
                with open(self.checkpoint_file, 'wb') as f:
                    pickle.dump(processed_indices, f)
                
                # Save working DataFrame (original structure + accumulated successful results)
                # This always contains ALL original rows, with successful results filled in
                df_working.to_csv(self.df_backup_file, index=False)
                
                successful_results = df_working[self.new_column_name].notna().sum()
                total_rows = len(df_working)
                completion_pct = (successful_results / total_rows) * 100
                
                print(f"Checkpoint saved: {len(processed_indices)} processed, {successful_results}/{total_rows} successful ({completion_pct:.1f}%)")
    
    async def process_async(self, df_working, processed_indices, target_null_only=False):
        """Process rows asynchronously with batched approach"""
        # Prepare data for processing
        rows_to_process = []
        for idx, row in df_working.iterrows():
            if idx not in processed_indices:
                # If targeting null only, only process rows with null values
                if target_null_only and pd.notna(row[self.new_column_name]):
                    continue
                rows_to_process.append((idx, row['anon_id'], row['deid_note_text'], row['EHR']))
        
        if not rows_to_process:
            if target_null_only:
                print("✅ All null rows already processed!")
            else:
                print("✅ All rows already processed!")
            return df_working, processed_indices
        
        print(f"Processing {len(rows_to_process)} rows in batches of {self.batch_size}")
        print(f"Max concurrent requests per batch: {self.max_concurrent}")
        print(f"Delay between batches: {self.delay_between_requests}s")
        
        # Create aiohttp session
        connector = aiohttp.TCPConnector(limit=self.max_concurrent)
        timeout = aiohttp.ClientTimeout(total=300)  # 5 minute timeout
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Process in batches
            for i, batch in enumerate(self.batchify(rows_to_process, self.batch_size)):
                print(f"Processing batch {i+1} with {len(batch)} rows...")
                
                # Create tasks for current batch
                tasks = [
                    self.classify_single_row(session, row_data) 
                    for row_data in batch
                ]
                
                # Process batch with progress bar
                batch_results = []
                with tqdm(total=len(tasks), desc=f"Batch {i+1}") as pbar:
                    for coro in asyncio.as_completed(tasks):
                        idx, result, error = await coro
                        batch_results.append((idx, result, error))
                        
                        # Only save successful results to checkpoint and working DataFrame
                        if result != "ERROR":
                            # ONLY write successful results to working DataFrame
                            df_working.at[idx, self.new_column_name] = result
                            # ONLY add successful rows to processed_indices
                            processed_indices.add(idx)
                            
                            # Update success counter
                            async with self.lock:
                                self.processed_count += 1
                        else:
                            # Handle errors - DON'T write to DataFrame, DON'T add to processed_indices
                            # This row will be retried on next run
                            async with self.lock:
                                self.error_count += 1
                                if error:
                                    print(f"Error processing row {idx}: {error} - will retry later")
                        
                        pbar.update(1)
                
                # Save checkpoint after each batch
                if len(processed_indices) > 0:
                    await self.save_checkpoint(processed_indices, df_working)
                
                # Add delay between batches (except for the last batch)
                total_batches = len(list(self.batchify(rows_to_process, self.batch_size)))
                if i < total_batches - 1:
                    print(f"Waiting {self.delay_between_requests}s before next batch...")
                    await asyncio.sleep(self.delay_between_requests)
        
        return df_working, processed_indices
    
    def save_final_results(self, df_working):
        """Save final results with timestamp"""
        print("Processing complete! Saving final results...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_filename = os.path.join(self.data_dir, f'Test_set_df_note_with_predictions_{timestamp}.csv')
        df_working.to_csv(final_filename, index=False)
        print(f"✅ Final results saved to: {final_filename}")
        return final_filename
    
    def cleanup(self):
        """Clean up temporary files"""
        files_to_remove = [self.checkpoint_file, self.df_backup_file]
        for file_path in files_to_remove:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Removed: {os.path.basename(file_path)}")
        print("✅ Cleanup complete!")
    
    async def run(self):
        """Main async processing pipeline"""
        start_time = time.time()
        
        try:
            # Load data
            df_original = self.load_data()
            processed_indices = self.load_checkpoint()
            df_working = self.load_working_data(df_original, processed_indices)
            
            # Validate data integrity
            if len(df_working) != len(df_original):
                print(f"⚠️ Warning: Working DataFrame size ({len(df_working)}) != Original size ({len(df_original)})")
            
            # Count existing successful results
            existing_results = df_working[self.new_column_name].notna().sum()
            
            print(f"Starting async processing:")
            print(f"  Total rows: {len(df_working)}")
            print(f"  Already processed: {len(processed_indices)}")
            print(f"  Existing successful results: {existing_results}")
            print(f"  Remaining: {len(df_working) - len(processed_indices)}")
            print(f"  Max concurrent: {self.max_concurrent}")
            print(f"  Rate limit: {self.delay_between_requests}s between requests")
            
            # Process asynchronously
            df_working, processed_indices = await self.process_async(df_working, processed_indices)
            
            # Check for null values before finishing
            null_count = df_working[self.new_column_name].isna().sum()
            if null_count > 0:
                print(f"\n⚠️ Found {null_count} rows with null values in '{self.new_column_name}' column")
                print("Continuing processing until all rows are complete...")
                
                # Continue processing null rows only
                df_working, processed_indices = await self.process_async(df_working, processed_indices, target_null_only=True)
                
                # Check again after additional processing
                null_count = df_working[self.new_column_name].isna().sum()
                if null_count > 0:
                    print(f"\n⚠️ Still {null_count} rows with null values remaining")
                    print("Saving current progress and stopping. Run again to continue processing remaining null rows.")
                else:
                    print(f"\n✅ All rows now have predictions! No null values remaining.")
            
            # Save final checkpoint before cleanup
            if len(processed_indices) > 0:
                await self.save_checkpoint(processed_indices, df_working)
            
            # Save final results
            final_filename = self.save_final_results(df_working)
            
            # Only clean up if ALL rows are complete (no null values)
            final_null_count = df_working[self.new_column_name].isna().sum()
            if final_null_count == 0:
                print(f"\n🎉 All {len(df_working)} rows completed successfully! Cleaning up...")
                # self.cleanup()
            else:
                print(f"\n⚠️ {final_null_count} rows still have null values. Keeping checkpoints for next run.")
                print("Run the script again to continue processing remaining null rows.")
            
            # Summary
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\n🎉 Processing Summary:")
            print(f"  Total rows processed: {self.processed_count}")
            print(f"  Errors encountered: {self.error_count}")
            if self.processed_count > 0:
                print(f"  Success rate: {((self.processed_count - self.error_count) / self.processed_count * 100):.1f}%")
                print(f"  Average time per row: {duration / self.processed_count:.2f} seconds")
            print(f"  Total time: {duration:.1f} seconds")
            print(f"  Final file: {final_filename}")
            
        except Exception as e:
            print(f"❌ Error during processing: {e}")
            raise


async def main():
    parser = argparse.ArgumentParser(description='Async LLM Classification with Batched Processing')
    parser.add_argument('--data-dir', 
                       default=None,
                       help='Data directory path (if not specified, will be set based on EHR_IncludeInprompt)')
    parser.add_argument('--concurrent', type=int, default=6,
                       help='Max concurrent requests per batch (default: 6)')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay between batches in seconds (default: 1.0)')
    parser.add_argument('--batch-size', type=int, default=10,
                       help='Number of rows per batch (default: 10)')
    parser.add_argument('--checkpoint-interval', type=int, default=10,
                       help='Save checkpoint every N rows (default: 10)')
    parser.add_argument('--EHR_IncludeInprompt', action='store_true',
                       help='Whether to include EHR in prompt')
    args = parser.parse_args()
    
    # Set default data directory based on EHR_IncludeInprompt if not provided
    if args.data_dir is None:
        base_data_dir = '/Users/sandychen/Desktop/Healthrex_workspace/scripts/Blood_Culture_Stewardship/Adult_refactor/src/data'
        args.data_dir = f'{base_data_dir}/EHR_IncludeInprompt_{args.EHR_IncludeInprompt}_new'
    
    # Create and run async classifier
    classifier = AsyncClassifier(
        data_dir=args.data_dir,
        max_concurrent=args.concurrent,
        delay_between_requests=args.delay,
        batch_size=args.batch_size,
        checkpoint_interval=args.checkpoint_interval,
        EHR_IncludeInprompt=args.EHR_IncludeInprompt,
    )
    
    await classifier.run()


if __name__ == "__main__":
    asyncio.run(main())
