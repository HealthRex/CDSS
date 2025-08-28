"""
Main script to process real clinical data from CommonOrders.xlsx
Processes cases one by one with delays to avoid rate limiting.
"""

import os
import time
import requests
import pandas as pd
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
XLSX_FILE = "real_data/CommonOrders.xlsx"
DELAY_BETWEEN_CASES = 45  # seconds to avoid rate limiting

def process_single_case(anon_id: str, candidate: str, question: str, note: str) -> Dict[str, Any]:
    """Process a single clinical case through the API."""
    
    payload = {
        "anon_id": str(anon_id),
        "candidate": str(candidate),
        "question": str(question),
        "note": str(note),
        "specialties": ["Infectious Diseases", "Emergency Medicine", "Internal Medicine"],
        "order_limits": {"lab": 30, "med": 30, "procedure": 30},
        "min_patients_for_non_rare_items": 10,
        "year": 2024
    }
    
    print(f"\n{'='*60}")
    print(f"Processing: {anon_id} - {candidate}")
    print(f"Question: {question[:80]}...")
    print(f"{'='*60}")
    
    try:
        response = requests.post(f"{API_BASE_URL}/process_comprehensive_clinical_case", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                clinical_result = result.get('clinical_result', {})
                orders = result.get('orders', {})
                
                print(f"✅ Success!")
                print(f"  ICD-10: {clinical_result.get('icd10_code')}")
                print(f"  Patient Age: {clinical_result.get('patient_age')}")
                print(f"  Patient Gender: {clinical_result.get('patient_gender')}")
                print(f"  Orders - Lab: {len(orders.get('lab', []))}, Med: {len(orders.get('med', []))}, Procedure: {len(orders.get('procedure', []))}")
                print(f"  Log directory: {result.get('case_log_dir')}")
                return {"success": True, "result": result}
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                return {"success": False, "error": result.get('error')}
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return {"success": False, "error": f"API Error {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return {"success": False, "error": str(e)}

def main():
    """Main function to process all cases from the XLSX file."""
    
    print("🚀 Processing Real Clinical Data from CommonOrders.xlsx")
    print("=" * 60)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/docs")
        if response.status_code != 200:
            print("❌ API is not running. Please start the FastAPI server first:")
            print("   cd api")
            print("   python fastapi_app.py")
            return
        print("✅ API is running and accessible")
    except:
        print("❌ Cannot connect to API. Please start the FastAPI server first:")
        print("   cd api")
        print("   python fastapi_app.py")
        return
    
    # Check if XLSX file exists
    if not os.path.exists(XLSX_FILE):
        print(f"❌ XLSX file not found: {XLSX_FILE}")
        print("Please make sure the file exists in the real_data/ directory.")
        return
    
    # Load XLSX data
    try:
        print(f"\n📊 Loading data from {XLSX_FILE}...")
        df = pd.read_excel(XLSX_FILE)
        print(f"✅ Loaded {len(df)} cases")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst few rows:")
        print(df.head(3).to_string())
        
    except ImportError as e:
        if "openpyxl" in str(e):
            print("❌ Missing dependency: openpyxl")
            print("💡 Install it with: pip install openpyxl")
            print("   Or: conda install openpyxl")
            return
        else:
            print(f"❌ Import error: {e}")
            return
    except Exception as e:
        print(f"❌ Error reading XLSX: {e}")
        print("💡 Make sure you have openpyxl installed: pip install openpyxl")
        return
    
    # Process all cases
    print(f"\n🔄 Processing {len(df)} cases with {DELAY_BETWEEN_CASES}s delays...")
    
    successful_cases = 0
    failed_cases = 0
    results = []
    
    for index, row in df.iterrows():
        case_num = index + 1
        
        # Process the case
        result = process_single_case(
            anon_id=row['anon_id'],
            candidate=row['Candidate'], 
            question=row['Question'],
            note=row['Note']
        )
        
        results.append({
            "case_num": case_num,
            "anon_id": row['anon_id'],
            "candidate": row['Candidate'],
            "success": result["success"],
            "error": result.get("error")
        })
        
        if result["success"]:
            successful_cases += 1
        else:
            failed_cases += 1
        
        # Delay between cases (except for the last one)
        if case_num < len(df):
            print(f"\n⏳ Waiting {DELAY_BETWEEN_CASES} seconds before next case...")
            time.sleep(DELAY_BETWEEN_CASES)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Total cases processed: {len(df)}")
    print(f"Successful: {successful_cases}")
    print(f"Failed: {failed_cases}")
    print(f"Success rate: {(successful_cases/len(df))*100:.1f}%")
    
    # Show failed cases
    if failed_cases > 0:
        print(f"\n❌ Failed Cases:")
        for result in results:
            if not result["success"]:
                print(f"  Case {result['case_num']}: {result['anon_id']} - {result['candidate']} - {result['error']}")
    
    print(f"\n📁 Check the logs/single/ directory for generated case folders and files.")
    print("Each case will have its own folder with anon_id and candidate in the name!")

if __name__ == "__main__":
    main()
