#!/usr/bin/env python3
"""
Rerun script for existing final result file with null values
Uses the existing parallel_classify.py logic but works with your final result file
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

class RerunExistingFileClassifier:
    def __init__(self, final_result_file, max_concurrent=4, checkpoint_interval=10, delay_between_requests=1.0, EHR_IncludeInprompt=False):
        self.final_result_file = final_result_file
        self.max_concurrent = max_concurrent
        self.checkpoint_interval = checkpoint_interval
        self.delay_between_requests = delay_between_requests
        self.new_column_name = 'llm_prediction_result'
        self.EHR_IncludeInprompt = EHR_IncludeInprompt
        
        # Create a rerun directory based on the final result file
        self.rerun_dir = os.path.join(os.path.dirname(final_result_file), 'rerun_null_rows')
        
        # File paths
        self.checkpoint_file = os.path.join(self.rerun_dir, 'rerun_checkpoint.pkl')
        self.df_backup_file = os.path.join(self.rerun_dir, 'rerun_working_backup.csv')
        
        # Async-safe counters
        self.processed_count = 0
        self.error_count = 0
        self.lock = asyncio.Lock()
        
        # Rate limiting
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.last_request_time = 0
        
        # Adaptive rate limiting
        self.recent_429_errors = 0
        self.adaptive_delay = delay_between_requests
        self.last_429_check = time.time()
        
        # Circuit breaker for extreme rate limiting
        self.circuit_breaker_active = False
        self.circuit_breaker_until = 0
        
        # API configuration
        self.api_url = os.getenv("API_URL")
        self.api_headers = {
            os.getenv("API_HEADER_KEY"): os.getenv("API_KEY"),
            "Content-Type": "application/json"
        }
        
        # Create rerun directory
        os.makedirs(self.rerun_dir, exist_ok=True)
        print(f"✅ Rerun directory ready: {self.rerun_dir}")
        print(f"✅ Max concurrent requests: {max_concurrent}")
        print(f"✅ Delay between requests: {delay_between_requests}s")
        
    def load_final_result_data(self):
        """Load the final result file and identify null rows"""
        print(f"Loading final result file: {self.final_result_file}")
        
        if not os.path.exists(self.final_result_file):
            raise FileNotFoundError(f"Final result file not found: {self.final_result_file}")
        
        df_final = pd.read_csv(self.final_result_file)
        print(f"✅ Loaded final result data: {df_final.shape}")
        
        # Check if the prediction column exists
        if self.new_column_name not in df_final.columns:
            raise ValueError(f"Column '{self.new_column_name}' not found in final result file")
        
        # Identify null rows
        null_mask = df_final[self.new_column_name].isna()
        null_indices = df_final[null_mask].index.tolist()
        
        print(f"✅ Found {len(null_indices)} rows with null values in '{self.new_column_name}' column")
        print(f"✅ Total rows: {len(df_final)}, Null rows: {len(null_indices)}")
        
        return df_final, null_indices
    
    def load_checkpoint(self):
        """Load existing rerun progress if available"""
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'rb') as f:
                processed_indices = pickle.load(f)
            print(f"✅ Loaded rerun checkpoint with {len(processed_indices)} processed rows")
            return processed_indices
        else:
            print("Starting fresh rerun - no checkpoint found")
            return set()
    
    def load_working_data(self, df_final, null_indices, processed_indices):
        """Load working data from final result file, only process null rows"""
        print("Creating working DataFrame from final result file...")
        df_working = df_final.copy()
        
        # Filter to only include null rows that haven't been processed yet
        remaining_null_indices = [idx for idx in null_indices if idx not in processed_indices]
        
        print(f"✅ Working with {len(remaining_null_indices)} remaining null rows to process")
        print(f"✅ Already processed in this rerun: {len(processed_indices)}")
        
        return df_working, remaining_null_indices
    
    async def classify_single_row(self, session, row_data):
        """Classify a single row with rate limiting and retry logic"""
        idx, anon_id, note_text, EHR = row_data
        if not self.EHR_IncludeInprompt:
            EHR = None
        
        max_retries = 5
        base_delay = 1.0
        
        for attempt in range(max_retries):
            async with self.semaphore:  # Limit concurrent requests
                try:
                    # Adaptive rate limiting: ensure minimum delay between requests
                    async with self.lock:
                        current_time = time.time()
                        
                        # Check circuit breaker
                        if self.circuit_breaker_active and current_time < self.circuit_breaker_until:
                            print(f"🔴 Circuit breaker active, waiting {self.circuit_breaker_until - current_time:.1f}s more...")
                            await asyncio.sleep(5)  # Wait 5 seconds and try again
                            continue
                        elif self.circuit_breaker_active:
                            self.circuit_breaker_active = False
                            print(f"🟢 Circuit breaker deactivated, resuming normal operation")
                        
                        # Check if we need to adapt delay based on recent 429 errors
                        if current_time - self.last_429_check > 60:  # Check every minute
                            if self.recent_429_errors > 20:  # Extreme rate limiting
                                self.circuit_breaker_active = True
                                self.circuit_breaker_until = current_time + 300  # 5 minute cooldown
                                print(f"🔴 Circuit breaker activated! Too many 429 errors ({self.recent_429_errors}). Pausing for 5 minutes...")
                                await asyncio.sleep(5)
                                continue
                            elif self.recent_429_errors > 10:  # Too many 429s
                                self.adaptive_delay = min(self.adaptive_delay * 1.5, 10.0)  # Increase delay, max 10s
                                print(f"🐌 Adaptive rate limiting: increased delay to {self.adaptive_delay:.1f}s due to {self.recent_429_errors} recent 429 errors")
                            elif self.recent_429_errors < 2:  # Very few 429s
                                self.adaptive_delay = max(self.adaptive_delay * 0.9, self.delay_between_requests)  # Decrease delay, min original
                                if self.adaptive_delay > self.delay_between_requests:
                                    print(f"🚀 Adaptive rate limiting: decreased delay to {self.adaptive_delay:.1f}s")
                            
                            self.recent_429_errors = 0
                            self.last_429_check = current_time
                        
                        # Apply adaptive delay
                        time_since_last = current_time - self.last_request_time
                        if time_since_last < self.adaptive_delay:
                            sleep_time = self.adaptive_delay - time_since_last
                            await asyncio.sleep(sleep_time)
                        self.last_request_time = time.time()
                    
                    # Make the API request
                    result = await self.make_api_request(session, anon_id, note_text, EHR)
                    return idx, result, None
                    
                except aiohttp.ClientResponseError as e:
                    if e.status == 429:  # Rate limit error
                        # Track 429 errors for adaptive rate limiting
                        async with self.lock:
                            self.recent_429_errors += 1
                        
                        if attempt < max_retries - 1:
                            # Exponential backoff: 1s, 2s, 4s, 8s, 16s
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
                
                # Save working DataFrame (final result structure + accumulated successful results)
                df_working.to_csv(self.df_backup_file, index=False)
                
                successful_results = df_working[self.new_column_name].notna().sum()
                total_rows = len(df_working)
                completion_pct = (successful_results / total_rows) * 100
                
                print(f"Rerun checkpoint saved: {len(processed_indices)} processed, {successful_results}/{total_rows} successful ({completion_pct:.1f}%)")
    
    async def process_async(self, df_working, remaining_null_indices, processed_indices):
        """Process null rows asynchronously with rate limiting"""
        if not remaining_null_indices:
            print("✅ All null rows already processed!")
            return df_working, processed_indices
        
        print(f"Processing {len(remaining_null_indices)} null rows with max {self.max_concurrent} concurrent requests...")
        print(f"Rate limit: {self.delay_between_requests}s between requests")
        
        # Prepare data for processing
        rows_to_process = []
        for idx in remaining_null_indices:
            row = df_working.iloc[idx]
            rows_to_process.append((idx, row['anon_id'], row['deid_note_text'], row['EHR']))
        
        # Create aiohttp session
        connector = aiohttp.TCPConnector(limit=self.max_concurrent)
        timeout = aiohttp.ClientTimeout(total=300)  # 5 minute timeout
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Create tasks for all rows
            tasks = [
                self.classify_single_row(session, row_data) 
                for row_data in rows_to_process
            ]
            
            # Process with progress bar
            results = []
            with tqdm(total=len(tasks), desc="Processing null rows") as pbar:
                for coro in asyncio.as_completed(tasks):
                    idx, result, error = await coro
                    
                    # Only save successful results to checkpoint and working DataFrame
                    if result != "ERROR" and result is not None and result.strip():
                        # ONLY write successful results to working DataFrame
                        df_working.at[idx, self.new_column_name] = result
                        # ONLY add successful rows to processed_indices
                        processed_indices.add(idx)
                        
                        # Update success counter
                        async with self.lock:
                            self.processed_count += 1
                            print(f"✅ Successfully processed row {idx}")
                    else:
                        # Handle errors - DON'T write to DataFrame, DON'T add to processed_indices
                        # This row will be retried on next run
                        async with self.lock:
                            self.error_count += 1
                            if error:
                                print(f"❌ Error processing row {idx}: {error} - will retry later")
                            else:
                                print(f"❌ Empty or invalid result for row {idx} - will retry later")
                    
                    # Save checkpoint periodically (only successful rows)
                    if len(processed_indices) % self.checkpoint_interval == 0:
                        await self.save_checkpoint(processed_indices, df_working)
                    
                    pbar.update(1)
        
        return df_working, processed_indices
    
    def save_final_results(self, df_working):
        """Save final results with timestamp"""
        print("Rerun complete! Saving final results...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save to rerun directory
        rerun_filename = os.path.join(self.rerun_dir, f'rerun_completed_{timestamp}.csv')
        df_working.to_csv(rerun_filename, index=False)
        
        # Also update the original final result file
        df_working.to_csv(self.final_result_file, index=False)
        
        print(f"✅ Rerun results saved to: {rerun_filename}")
        print(f"✅ Original final result file updated: {self.final_result_file}")
        return rerun_filename
    
    def cleanup(self):
        """Clean up temporary files"""
        files_to_remove = [self.checkpoint_file, self.df_backup_file]
        for file_path in files_to_remove:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Removed: {os.path.basename(file_path)}")
        print("✅ Cleanup complete!")
    
    async def run(self):
        """Main async processing pipeline for rerunning null rows"""
        start_time = time.time()
        
        try:
            # Load final result data and identify null rows
            df_final, null_indices = self.load_final_result_data()
            processed_indices = self.load_checkpoint()
            df_working, remaining_null_indices = self.load_working_data(df_final, null_indices, processed_indices)
            
            # Count existing successful results
            existing_results = df_working[self.new_column_name].notna().sum()
            
            print(f"Starting rerun processing:")
            print(f"  Total rows: {len(df_working)}")
            print(f"  Original null rows: {len(null_indices)}")
            print(f"  Already processed in rerun: {len(processed_indices)}")
            print(f"  Remaining to process: {len(remaining_null_indices)}")
            print(f"  Existing successful results: {existing_results}")
            print(f"  Max concurrent: {self.max_concurrent}")
            print(f"  Rate limit: {self.delay_between_requests}s between requests")
            
            # Process asynchronously
            df_working, processed_indices = await self.process_async(df_working, remaining_null_indices, processed_indices)
            
            # Save final checkpoint before cleanup
            if len(processed_indices) > 0:
                await self.save_checkpoint(processed_indices, df_working)
            
            # Save final results
            final_filename = self.save_final_results(df_working)
            
            # Only clean up if ALL null rows are complete
            final_null_count = df_working[self.new_column_name].isna().sum()
            if final_null_count == 0:
                print(f"\n🎉 All {len(df_working)} rows completed successfully! Cleaning up...")
                self.cleanup()
            else:
                print(f"\n⚠️ {final_null_count} rows still have null values. Keeping checkpoints for next run.")
                print("Run the script again to continue processing remaining null rows.")
            
            # Summary
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\n🎉 Rerun Summary:")
            print(f"  Null rows processed: {self.processed_count}")
            print(f"  Errors encountered: {self.error_count}")
            if self.processed_count > 0:
                print(f"  Success rate: {((self.processed_count - self.error_count) / self.processed_count * 100):.1f}%")
                print(f"  Average time per row: {duration / self.processed_count:.2f} seconds")
            print(f"  Total time: {duration:.1f} seconds")
            print(f"  Final file: {final_filename}")
            
        except Exception as e:
            print(f"❌ Error during rerun processing: {e}")
            raise


async def main():
    parser = argparse.ArgumentParser(description='Rerun Null Rows from Existing Final Result File')
    parser.add_argument('--final-result-file', 
                       default='/Users/sandychen/Desktop/Healthrex_workspace/scripts/Blood_Culture_Stewardship/Adult_refactor/src/data/EHR_IncludeInprompt_True/Test_set_df_note_with_predictions_20251003_103018 copy.csv',
                       help='Path to the final result CSV file with null values')
    parser.add_argument('--concurrent', type=int, default=4,
                       help='Max concurrent requests (default: 4)')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('--checkpoint-interval', type=int, default=10,
                       help='Save checkpoint every N rows (default: 10)')
    parser.add_argument('--EHR_IncludeInprompt', action='store_true',
                       help='Whether to include EHR in prompt')
    args = parser.parse_args()
    
    # Create and run rerun classifier
    classifier = RerunExistingFileClassifier(
        final_result_file=args.final_result_file,
        max_concurrent=args.concurrent,
        delay_between_requests=args.delay,
        checkpoint_interval=args.checkpoint_interval,
        EHR_IncludeInprompt=args.EHR_IncludeInprompt,
    )
    
    await classifier.run()


if __name__ == "__main__":
    asyncio.run(main())
