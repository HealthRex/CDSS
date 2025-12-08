#!/usr/bin/env python3
"""
Batch Size Performance Tester
Tests different batch sizes to find optimal performance
"""

import asyncio
import time
import pandas as pd
import os
import sys
from datetime import datetime
import argparse

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import will be done inside the function to avoid import issues

class BatchPerformanceTester:
    def __init__(self, data_dir, max_concurrent=6, delay_between_requests=1.0, EHR_IncludeInprompt=False):
        self.data_dir = data_dir
        self.max_concurrent = max_concurrent
        self.delay_between_requests = delay_between_requests
        self.EHR_IncludeInprompt = EHR_IncludeInprompt
        
    async def test_batch_size(self, batch_size, test_rows=50):
        """Test a specific batch size with a limited number of rows"""
        print(f"\n🧪 Testing batch size: {batch_size}")
        print(f"   Test rows: {test_rows}")
        print(f"   Concurrent: {self.max_concurrent}")
        print(f"   Delay: {self.delay_between_requests}s")
        
        # Import here to avoid import issues
        from parallel_classify import AsyncClassifier
        
        # Create a temporary classifier for testing
        test_classifier = AsyncClassifier(
            data_dir=self.data_dir,
            max_concurrent=self.max_concurrent,
            delay_between_requests=self.delay_between_requests,
            batch_size=batch_size,
            checkpoint_interval=10,
            EHR_IncludeInprompt=self.EHR_IncludeInprompt
        )
        
        # Load data
        df_original = test_classifier.load_data()
        processed_indices = test_classifier.load_checkpoint()
        df_working = test_classifier.load_working_data(df_original, processed_indices)
        
        # Find rows to test (limit to test_rows)
        rows_to_test = []
        count = 0
        for idx, row in df_working.iterrows():
            if idx not in processed_indices and count < test_rows:
                rows_to_test.append((idx, row['anon_id'], row['deid_note_text'], row['EHR']))
                count += 1
        
        if not rows_to_test:
            print("   ⚠️ No rows available for testing")
            return None
        
        print(f"   📊 Testing with {len(rows_to_test)} rows")
        
        # Create a temporary working DataFrame with only test rows
        test_df = df_working.iloc[[row[0] for row in rows_to_test]].copy()
        test_processed_indices = set()
        
        # Time the processing
        start_time = time.time()
        
        try:
            # Process the test batch
            result_df, result_indices = await test_classifier.process_async(
                test_df, test_processed_indices, target_null_only=False
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Calculate metrics
            successful_rows = result_df['llm_prediction_result'].notna().sum()
            total_rows = len(result_df)
            success_rate = (successful_rows / total_rows) * 100 if total_rows > 0 else 0
            rows_per_second = successful_rows / duration if duration > 0 else 0
            
            # Calculate theoretical max throughput
            batches_needed = (total_rows + batch_size - 1) // batch_size
            theoretical_time = batches_needed * self.delay_between_requests
            efficiency = (duration / theoretical_time) * 100 if theoretical_time > 0 else 0
            
            results = {
                'batch_size': batch_size,
                'test_rows': len(rows_to_test),
                'successful_rows': successful_rows,
                'success_rate': success_rate,
                'duration': duration,
                'rows_per_second': rows_per_second,
                'batches_needed': batches_needed,
                'theoretical_time': theoretical_time,
                'efficiency': efficiency
            }
            
            print(f"   ✅ Results:")
            print(f"      Success rate: {success_rate:.1f}%")
            print(f"      Duration: {duration:.2f}s")
            print(f"      Rows/second: {rows_per_second:.2f}")
            print(f"      Efficiency: {efficiency:.1f}%")
            
            return results
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    async def run_performance_test(self, batch_sizes=[5, 10, 15, 20, 25, 30], test_rows=50):
        """Run performance tests for multiple batch sizes"""
        print("🚀 Starting Batch Size Performance Test")
        print(f"Testing batch sizes: {batch_sizes}")
        print(f"Test rows per batch size: {test_rows}")
        print(f"Max concurrent: {self.max_concurrent}")
        print(f"Delay between batches: {self.delay_between_requests}s")
        
        results = []
        
        for batch_size in batch_sizes:
            result = await self.test_batch_size(batch_size, test_rows)
            if result:
                results.append(result)
            
            # Small delay between tests
            await asyncio.sleep(2)
        
        # Analyze results
        if results:
            self.analyze_results(results)
        else:
            print("❌ No successful test results")
    
    def analyze_results(self, results):
        """Analyze and recommend optimal batch size"""
        print("\n📊 Performance Analysis:")
        print("=" * 80)
        print(f"{'Batch Size':<12} {'Success%':<10} {'Rows/sec':<10} {'Efficiency%':<12} {'Duration':<10}")
        print("-" * 80)
        
        best_throughput = 0
        best_efficiency = 0
        best_overall = 0
        best_batch_size = None
        
        for result in results:
            print(f"{result['batch_size']:<12} {result['success_rate']:<10.1f} {result['rows_per_second']:<10.2f} {result['efficiency']:<12.1f} {result['duration']:<10.2f}")
            
            # Find best performers
            if result['rows_per_second'] > best_throughput:
                best_throughput = result['rows_per_second']
                best_throughput_batch = result['batch_size']
            
            if result['efficiency'] > best_efficiency:
                best_efficiency = result['efficiency']
                best_efficiency_batch = result['batch_size']
            
            # Overall score (weighted combination)
            overall_score = result['rows_per_second'] * 0.7 + result['efficiency'] * 0.3
            if overall_score > best_overall:
                best_overall = overall_score
                best_batch_size = result['batch_size']
        
        print("-" * 80)
        print(f"\n🎯 Recommendations:")
        print(f"   Best throughput: batch_size={best_throughput_batch} ({best_throughput:.2f} rows/sec)")
        print(f"   Best efficiency: batch_size={best_efficiency_batch} ({best_efficiency:.1f}% efficiency)")
        print(f"   Best overall: batch_size={best_batch_size} (score: {best_overall:.2f})")
        
        # Additional recommendations
        print(f"\n💡 Additional Tips:")
        print(f"   • If you're getting 429 errors, reduce batch_size")
        print(f"   • If processing is too slow, increase batch_size")
        print(f"   • Consider your API rate limits when choosing batch_size")
        print(f"   • Monitor success rate - it should be >95%")

async def main():
    parser = argparse.ArgumentParser(description='Test Batch Size Performance')
    parser.add_argument('--data-dir', 
                       default=None,
                       help='Data directory path')
    parser.add_argument('--concurrent', type=int, default=6,
                       help='Max concurrent requests per batch (default: 6)')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay between batches in seconds (default: 1.0)')
    parser.add_argument('--test-rows', type=int, default=50,
                       help='Number of rows to test per batch size (default: 50)')
    parser.add_argument('--batch-sizes', nargs='+', type=int, default=[5, 10, 15, 20, 25, 30],
                       help='Batch sizes to test (default: 5 10 15 20 25 30)')
    parser.add_argument('--EHR_IncludeInprompt', action='store_true',
                       help='Whether to include EHR in prompt')
    
    args = parser.parse_args()
    
    # Set default data directory
    if args.data_dir is None:
        base_data_dir = '/Users/sandychen/Desktop/Healthrex_workspace/scripts/Blood_Culture_Stewardship/Adult_refactor/src/data'
        args.data_dir = f'{base_data_dir}/EHR_IncludeInprompt_{args.EHR_IncludeInprompt}'
    
    # Create and run tester
    tester = BatchPerformanceTester(
        data_dir=args.data_dir,
        max_concurrent=args.concurrent,
        delay_between_requests=args.delay,
        EHR_IncludeInprompt=args.EHR_IncludeInprompt
    )
    
    await tester.run_performance_test(args.batch_sizes, args.test_rows)

if __name__ == "__main__":
    asyncio.run(main())
