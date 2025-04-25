import warnings
warnings.filterwarnings('ignore', category=UserWarning)  # Suppress all UserWarnings
warnings.filterwarnings('ignore', category=FutureWarning)  # Suppress FutureWarnings

import argparse
import os
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from api.bigquery_api import BigQueryAPI

def validate_year(year):
    """Validate that the year is within the allowed range."""
    if year not in [2021, 2022, 2023, 2024]:
        raise ValueError(f"Year must be between 2021 and 2024, got {year}")
    return year

def create_output_filename(diagnosis_codes, gender, result_type, year, limit):
    """Create a standardized output filename."""
    gender_str = gender if gender else 'all'
    diagnosis_str = '_'.join(diagnosis_codes)
    return f"{diagnosis_str}_{gender_str}_{result_type}_year{year}_limit{limit}.csv"

def main():
    parser = argparse.ArgumentParser(
        description='Query BigQuery for common immediate orders based on diagnosis and patient characteristics'
    )
    
    # Required arguments
    parser.add_argument('--diagnosis', 
                       required=True, 
                       nargs='+',
                       help='Diagnosis codes (e.g., J01.90)')
    
    # Optional arguments
    parser.add_argument('--gender', 
                       default=None,
                       choices=['Male', 'Female'],
                       help='Patient gender to filter by')
    
    parser.add_argument('--type', 
                       default='med',
                       choices=['med', 'proc'],
                       help='Type of results to return (medications or procedures)')
    
    parser.add_argument('--limit', 
                       type=int,
                       default=10,
                       help='Maximum number of results to return')
    
    parser.add_argument('--year', 
                       type=int,
                       default=2022,
                       help='Year of the dataset to use (2021-2024)')
    
    parser.add_argument('--output-dir',
                       default='csv_output',
                       help='Directory to save output files')
    
    args = parser.parse_args()
    
    try:
        # Validate year
        year = validate_year(args.year)
        
        # Initialize API
        api = BigQueryAPI()
        
        # Get results
        print(f"Querying data for year {year}...")
        results = api.get_immediate_orders(
            diagnosis_codes=args.diagnosis,
            patient_gender=args.gender,
            result_type=args.type,
            limit=args.limit,
            year=year
        )
        
        # Create output directory if it doesn't exist
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Generate output filename
        output_filename = create_output_filename(
            args.diagnosis,
            args.gender,
            args.type,
            year,
            args.limit
        )
        output_path = os.path.join(args.output_dir, output_filename)
        
        # Save results
        results.to_csv(output_path, index=False)
        print(f"\nResults saved to: {output_path}")
        print(f"\nQuery Summary:")
        print(f"- Diagnosis codes: {', '.join(args.diagnosis)}")
        print(f"- Gender: {args.gender if args.gender else 'All'}")
        print(f"- Result type: {args.type}")
        print(f"- Year: {year}")
        print(f"- Number of results: {len(results)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()