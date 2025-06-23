import requests
import json
import pandas as pd
import os
import datetime

def process_clinical_case_and_get_orders(
    clinical_question: str,
    clinical_notes: str,
    result_type: str = None,
    limit: int = 10
):
    """
    Process a clinical case and get orders in one flow.
    
    Args:
        clinical_question: The clinical question to answer
        clinical_notes: The clinical notes to analyze
        result_type: "lab", "med", or "procedure"; None for all types
        limit: Maximum number of results to return
    
    Returns:
        dict: The orders data
    """
    # Base URL for the API
    base_url = "http://localhost:8000"
    
    # Step 1: Process the clinical case
    clinical_case_url = f"{base_url}/process_clinical_case"
    clinical_case_data = {
        "clinical_question": clinical_question,
        "clinical_notes": clinical_notes
    }
    
    print("Processing clinical case...")
    clinical_response = requests.post(clinical_case_url, json=clinical_case_data)
    clinical_response.raise_for_status()  # Raise an exception for bad status codes
    clinical_result = clinical_response.json()
    
    print("\nClinical Case Result:")
    print(json.dumps(clinical_result, indent=2))
    
    # Check if processing was successful
    if clinical_result.get("error") or clinical_result.get("stopped"):
        print(f"Clinical case processing failed: {clinical_result.get('error', 'Unknown error')}")
        return None
    
    # Step 2: Get orders using the clinical result
    orders_url = f"{base_url}/get_orders"
    orders_data = {
        "icd10_code": clinical_result["icd10_code"],
        "patient_age": clinical_result["patient_age"],
        "patient_gender": clinical_result["patient_gender"],
        "result_type": result_type,
        "limit": limit
    }
    
    if result_type is None:
        print(f"\nGetting lab/med/procedure orders...")
    else:
        print(f"\nGetting {result_type} orders...")
    orders_response = requests.post(orders_url, json=orders_data)
    orders_response.raise_for_status()
    orders_result = orders_response.json()
    
    print(f"\n{result_type.capitalize() if result_type else 'All'} Orders Result:")
    print(json.dumps(orders_result, indent=2))
    
    return orders_result

def process_clinical_case_only(
    clinical_question: str,
    clinical_notes: str
):
    """
    Process a clinical case only and return the result file path.
    
    Args:
        clinical_question: The clinical question to answer
        clinical_notes: The clinical notes to analyze
    
    Returns:
        dict: The clinical result and file path
    """
    # Base URL for the API
    base_url = "http://localhost:8000"
    
    # Process the clinical case
    clinical_case_url = f"{base_url}/process_clinical_case"
    clinical_case_data = {
        "clinical_question": clinical_question,
        "clinical_notes": clinical_notes
    }
    
    print("Processing clinical case...")
    clinical_response = requests.post(clinical_case_url, json=clinical_case_data)
    clinical_response.raise_for_status()
    clinical_result = clinical_response.json()
    
    print("\nClinical Case Result:")
    print(json.dumps(clinical_result, indent=2))
    
    # Check if processing was successful
    if clinical_result.get("error") or clinical_result.get("stopped"):
        print(f"Clinical case processing failed: {clinical_result.get('error', 'Unknown error')}")
        return None
    
    # The result.csv file is automatically saved by the FastAPI server
    # Since the log directory is now created dynamically with a timestamp,
    # we can't predict the exact path. The user should check the logs directory
    # for the most recent clinical_workflow_* folder.
    print("\nNote: The result.csv file has been saved to a new log directory.")
    print("Check the ../logs/ directory for the most recent clinical_workflow_* folder.")
    print("You can use the get_orders_from_file() function with the specific path to get orders.")
    
    return {
        "clinical_result": clinical_result,
        "result_file_path": "See logs directory for exact path"
    }

def get_orders_from_file(
    result_file_path: str,
    result_type: str = None,
    limit: int = 10,
    custom_filename: str = None
):
    """
    Get orders from a previously saved result.csv file.
    
    Args:
        result_file_path: Path to the result.csv file
        result_type: "lab", "med", or "procedure"; None for all types
        limit: Maximum number of results to return
        custom_filename: Optional custom filename for the output CSV (without .csv extension)
    
    Returns:
        dict: The orders data including the path where orders were saved
    """
    # Base URL for the API
    base_url = "http://localhost:8000"
    
    # Get orders from file
    orders_url = f"{base_url}/get_orders_from_file"
    orders_data = {
        "result_file_path": result_file_path,
        "result_type": result_type,
        "limit": limit
    }
    
    # Add custom filename if provided
    if custom_filename:
        orders_data["custom_filename"] = custom_filename

    print(f"\nGetting {result_type.capitalize() if result_type else 'All'} orders from file...")
    
    if custom_filename:
        print(f"Using custom filename: {custom_filename}")
    
    orders_response = requests.post(orders_url, json=orders_data)
    orders_response.raise_for_status()
    orders_result = orders_response.json()
    
    print(f"\n{result_type.capitalize() if result_type else 'All'} Orders Result from File:")
    print(json.dumps(orders_result, indent=2))
    
    # Show where the orders were saved
    if orders_result.get("orders_file_path"):
        print(f"\nOrders saved to: {orders_result['orders_file_path']}")
    
    return orders_result

if __name__ == "__main__":
    cases = pd.read_csv("phase_1/real_data/icd.csv")
    clinical_question = cases.iloc[0]["Question"]
    clinical_notes = cases.iloc[0]["Summary"]
    
    # # Option 1: Get comprehensive recommendations (lab tests, medications, and procedures)
    # print("=" * 80)
    # print("COMPREHENSIVE RECOMMENDATIONS")
    # print("=" * 80)
    # comprehensive_results = process_clinical_case_and_get_orders(
    #     clinical_question=clinical_question,
    #     clinical_notes=clinical_notes,
    #     result_type=None,  # None gets all types
    #     limit=10
    # )
    
    # # Option 2: Get only lab tests
    # print("\n" + "=" * 80)
    # print("LAB TESTS ONLY")
    # print("=" * 80)
    # lab_results = process_clinical_case_and_get_orders(
    #     clinical_question=clinical_question,
    #     clinical_notes=clinical_notes,
    #     result_type="lab",
    #     limit=10
    # )
    
    # # Option 3: Get only medications
    # print("\n" + "=" * 80)
    # print("MEDICATIONS ONLY")
    # print("=" * 80)
    # med_results = process_clinical_case_and_get_orders(
    #     clinical_question=clinical_question,
    #     clinical_notes=clinical_notes,
    #     result_type="med",
    #     limit=10
    # )
    
    # # Option 4: Get only procedures
    # print("\n" + "=" * 80)
    # print("PROCEDURES ONLY")
    # print("=" * 80)
    # proc_results = process_clinical_case_and_get_orders(
    #     clinical_question=clinical_question,
    #     clinical_notes=clinical_notes,
    #     result_type="procedure",
    #     limit=10
    # )
    
    # # Option 5: Get all types in a single call
    # print("\n" + "=" * 80)
    # print("ALL TYPES IN SINGLE CALL")
    # print("=" * 80)
    # all_results = process_clinical_case_and_get_orders(
    #     clinical_question=clinical_question,
    #     clinical_notes=clinical_notes,
    #     result_type=None,  # None gets all types
    #     limit=10
    # )
    
    # NEW: Separated clinical processing and order retrieval
    
    # Option 6: Process clinical case only and save to file
    # print("=" * 80)
    # print("SEPARATED CLINICAL PROCESSING")
    # print("=" * 80)
    # clinical_result = process_clinical_case_only(
    #     clinical_question=clinical_question,
    #     clinical_notes=clinical_notes
    # )
    
    # if True:
        # result_file_path = "phase_1/logs/clinical_workflow_20250623110531/result.csv"
        # print(f"\nClinical case processed and saved to: {result_file_path}")
        
        # # Option 7: Get orders from the saved file
        # print("\n" + "=" * 80)
        # print("GETTING ORDERS FROM SAVED FILE")
        # print("=" * 80)
        
        # # Note: Since we don't have the exact path, we'll demonstrate with a placeholder
        # # In practice, users would provide the actual path from the logs directory
        # print("\nNote: To get orders from the saved file, use get_orders_from_file() with the actual path.")
        # print("Example: get_orders_from_file('../logs/clinical_workflow_20241201120000/result.csv', 'lab', 5)")
        
        # Option 8: Demonstrate using a specific result file path
        # Uncomment and modify the path below to use an existing result.csv file
        # print("\n--- Lab Tests from File ---")
        # specific_file_path = "phase_1/logs/clinical_workflow_20250623110531/result.csv"  # Modify this path
        # if os.path.exists(specific_file_path):
        #     lab_from_file = get_orders_from_file(specific_file_path, "lab", 5)
        # else:
        #     print(f"File not found: {specific_file_path}")
        
        # Option 9: Get comprehensive recommendations from file
        # print("\n" + "=" * 80)
        # print("COMPREHENSIVE RECOMMENDATIONS FROM FILE")
        # print("=" * 80)
        # comprehensive_from_file = get_comprehensive_recommendations_from_file(specific_file_path, 5)
        
        # Option 10: Get orders with custom filenames
        # print("\n" + "=" * 80)
        # print("ORDERS WITH CUSTOM FILENAMES")
        # print("=" * 80)
        
        # Single order type with custom filename
        # custom_lab = get_orders_from_file(
        #     specific_file_path, 
        #     "lab", 
        #     5, 
        #     "patient_1_lab_tests"
        # )
        
        # Comprehensive recommendations with custom filenames
        # custom_filenames = {
        #     "lab": "patient_123_lab_orders",
        #     "med": "patient_123_medications", 
        #     "procedure": "patient_123_procedures"
        # }
        # comprehensive_custom = get_comprehensive_recommendations_from_file(
        #     specific_file_path, 
        #     5, 
        #     custom_filenames
        # )
    
    # Option 11: Demonstrate using a specific result file path
    # Uncomment and modify the path below to use an existing result.csv file
    # print("\n" + "=" * 80)
    # print("USING SPECIFIC RESULT FILE")
    # print("=" * 80)
    # specific_file_path = "../logs/clinical_workflow_20241201120000/result.csv"  # Modify this path
    # if os.path.exists(specific_file_path):
    #     specific_orders = get_orders_from_file(specific_file_path, "lab", 10)
    # else:
    #     print(f"File not found: {specific_file_path}")
    
    # print("\nNote: All results have been automatically saved to CSV files by the FastAPI server.")
    # print("Each clinical case now creates its own log directory with a unique timestamp.")