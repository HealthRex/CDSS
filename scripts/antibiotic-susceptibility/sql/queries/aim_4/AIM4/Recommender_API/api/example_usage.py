import requests
import json

def process_clinical_case_and_get_orders(
    clinical_question: str,
    clinical_notes: str,
    result_type: str = "proc",
    limit: int = 100
):
    """
    Process a clinical case and get orders in one flow.
    
    Args:
        clinical_question: The clinical question to answer
        clinical_notes: The clinical notes to analyze
        result_type: Either "proc" for procedures or "med" for medications
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
    
    # Step 2: Get orders using the clinical result
    orders_url = f"{base_url}/get_orders"
    orders_data = {
        "icd10_code": clinical_result["icd10_code"],
        "patient_age": clinical_result["patient_age"],
        "patient_gender": clinical_result["patient_gender"],
        "result_type": result_type,
        "limit": limit
    }
    
    print("\nGetting orders...")
    orders_response = requests.post(orders_url, json=orders_data)
    orders_response.raise_for_status()
    orders_result = orders_response.json()
    
    print("\nOrders Result:")
    print(json.dumps(orders_result, indent=2))
    
    return orders_result

if __name__ == "__main__":
    # Example usage
    clinical_question = "Could this patient have stable angina?"
    clinical_notes = """
    55-year-old male presents with chest pain on exertion for the past 2 weeks.
    Pain is substernal, radiates to left arm, and is relieved with rest.
    No associated symptoms. Past medical history includes hypertension.
    No family history of CAD. Smokes 1 pack per day for 20 years.
    """
    
    # Get procedures
    print("Getting procedures...")
    proc_results = process_clinical_case_and_get_orders(
        clinical_question=clinical_question,
        clinical_notes=clinical_notes,
        result_type="proc",
        limit=10
    )
    
    # Get medications
    print("\nGetting medications...")
    med_results = process_clinical_case_and_get_orders(
        clinical_question=clinical_question,
        clinical_notes=clinical_notes,
        result_type="med",
        limit=10
    ) 