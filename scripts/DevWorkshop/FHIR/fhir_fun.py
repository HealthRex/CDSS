from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth
import os
from datetime import datetime

load_dotenv('tds_ds_env_vars.sh')
load_dotenv('env_vars.sh')

def get_patient_identifiers(identifier: str, identifier_type: str = "SHCMRN") -> dict:
    """Return a mapping of identifier type to value for a patient."""
    resp = requests.get(
        f"{os.environ['EPIC_ENV']}api/epic/2010/Common/Patient/GETPATIENTIDENTIFIERS/Patient/Identifiers",
        params={"PatientID": identifier, "PatientIDType": identifier_type},
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Epic-Client-ID": os.environ["EPIC_CLIENT_ID"],
        },
        auth=HTTPBasicAuth(os.environ["secretID"], os.environ["secretpass"]),
        timeout=30,
    )
    data = resp.json()
    return {item["IDType"]: item["ID"] for item in data.get("Identifiers", [])}

def get_binary(binary_url):
    """Download binary content."""
    resp = requests.get(
        f"{os.environ['EPIC_ENV']}api/FHIR/R4/{binary_url}",
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Epic-Client-ID": os.environ["EPIC_CLIENT_ID"],
        },
        auth=HTTPBasicAuth(os.environ["secretID"], os.environ["secretpass"]),
        timeout=30,
    )
    return resp

def format_datetime_for_filename(date_str):
    """Convert datetime string to filename format: 2025-08-25-12-48-58."""
    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    return dt.strftime('%Y-%m-%d-%H-%M-%S')

def get_discharge_summaries(patient_fhir_id, start_date=None, end_date=None):
    """Get discharge summaries for a patient."""
    url = f"{os.environ['EPIC_ENV']}api/FHIR/R4/DocumentReference"
    params = {
        "patient": patient_fhir_id,
        "type": "http://loinc.org|18842-5", # Discharge summary
        "docstatus": "final" # Only final documents
    }
    
    date_params = []
    if start_date:
        date_params.append(f"ge{start_date}")
    if end_date:
        date_params.append(f"le{end_date}")
    
    if date_params:
        params["date"] = date_params
    
    resp = requests.get(
        url,
        params=params,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Epic-Client-ID": os.environ["EPIC_CLIENT_ID"],
            "Accept": "application/json",
        },
        auth=HTTPBasicAuth(os.environ["secretID"], os.environ["secretpass"]),
        timeout=30,
    )
    return resp.json()

def extract_documents(fhir_response, doc_type="text/html"):
    """Extract document info from FHIR response."""
    documents = []
    if "entry" in fhir_response:
        for entry in fhir_response["entry"]:
            resource = entry["resource"]
            date = resource.get("date", "unknown_date")
            
            if "content" in resource:
                for content in resource["content"]:
                    if "attachment" in content:
                        attachment = content["attachment"]
                        if "url" in attachment and attachment["url"].startswith("Binary/"):
                            if attachment["contentType"] == doc_type:
                                documents.append({
                                    "url": attachment["url"],
                                    "date": date
                                })
    return documents

def download_discharge_summaries(mrn, save_directory="dc_summaries", start_date=None, end_date=None, doc_type="text/html"):
    """
    Download discharge summaries for a patient and save them as html files.
    file name format: {identifier}_{datetime_str}.html
    datetime_str is the date of chart closure (i.e. the date indicated as Electronically signed by XX, MD at X/XX/20XX HH:MM AM/PM).

    Args:
        mrn (str): The patient MRN.
        save_directory (str, optional): Directory to save downloaded files. Defaults to "dc_summaries".
        start_date (str, optional): Start date (YYYY-MM-DD) to filter summaries. Defaults to None.
        end_date (str, optional): End date (YYYY-MM-DD) to filter summaries. Defaults to None.
        doc_type (str, optional): MIME type of documents to download ("text/html" or "text/rtf"). Defaults to "text/html".

    Returns:
        dict: The FHIR response containing discharge summaries metadata.
    """
    os.makedirs(save_directory, exist_ok=True)
    
    # Get patient FHIR ID
    patient_fhir_id = get_patient_identifiers(mrn)["FHIR"]
    
    # Get discharge summaries
    fhir_response = get_discharge_summaries(patient_fhir_id, start_date, end_date)
    
    # Extract documents
    documents = extract_documents(fhir_response, doc_type)
    print(f"Found {len(documents)} discharge summaries")
    
    # Download each document
    for i, doc in enumerate(documents):
        print(f"Downloading {i+1}/{len(documents)}: {doc['date']}")
        
        # Download binary content
        binary_resp = get_binary(doc["url"])
        
        # Create filename with full datetime
        datetime_str = format_datetime_for_filename(doc["date"])
        filename = f"{mrn}_{datetime_str}.html"
        
        # Save file
        with open(f"{save_directory}/{filename}", "wb") as f:
            f.write(binary_resp.content)
        
        print(f"Saved: {filename}")
    
    return fhir_response

def get_cv_cath_reports(patient_fhir_id, start_date=None, end_date=None):
    """Get CV Cath Procedure reports for a patient from DocumentReference."""
    url = f"{os.environ['EPIC_ENV']}api/FHIR/R4/DocumentReference"
    params = {
        "patient": patient_fhir_id,
    }
    
    date_params = []
    if start_date:
        date_params.append(f"ge{start_date}")
    if end_date:
        date_params.append(f"le{end_date}")
    
    if date_params:
        params["date"] = date_params
    
    resp = requests.get(
        url,
        params=params,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Epic-Client-ID": os.environ["EPIC_CLIENT_ID"],
            "Accept": "application/json",
        },
        auth=HTTPBasicAuth(os.environ["secretID"], os.environ["secretpass"]),
        timeout=30,
    )
    return resp.json()

def extract_cv_cath_pdfs(fhir_response):
    """Extract CV Cath Procedure PDF documents from DocumentReference FHIR response."""
    documents = []
    
    if "entry" in fhir_response:
        for entry in fhir_response["entry"]:
            resource = entry["resource"]
            description = resource.get("description", "")
            
            # Look for CV Cath Procedure documents
            if "cath" in description.lower() and "procedure" in description.lower():
                date = resource.get("date", "unknown_date")
                
                if "content" in resource:
                    for content in resource["content"]:
                        if "attachment" in content:
                            attachment = content["attachment"]
                            content_type = attachment.get("contentType", "")
                            
                            # Only PDF files
                            if content_type == "application/pdf" and "url" in attachment:
                                documents.append({
                                    "url": attachment["url"],
                                    "date": date,
                                    "description": description
                                })
    return documents

def download_cv_cath_reports(mrn, save_directory="cv_cath", start_date=None, end_date=None):
    """
    Download CV Cath Procedure PDF reports for a patient.
    file name format: {identifier}_{datetime_str}.pdf
    
    Args:
        mrn (str): The patient MRN.
        save_directory (str, optional): Directory to save downloaded files. Defaults to "cv_cath".
        start_date (str, optional): Start date (YYYY-MM-DD) to filter reports. Defaults to None.
        end_date (str, optional): End date (YYYY-MM-DD) to filter reports. Defaults to None.
    
    Returns:
        dict: The FHIR response containing the reports metadata.
    """
    os.makedirs(save_directory, exist_ok=True)
    
    # Get patient FHIR ID
    patient_fhir_id = get_patient_identifiers(mrn)["FHIR"]
    
    # Get CV Cath reports from DocumentReference
    fhir_response = get_cv_cath_reports(patient_fhir_id, start_date, end_date)
    
    # Extract CV Cath PDF documents
    documents = extract_cv_cath_pdfs(fhir_response)
    print(f"Found {len(documents)} CV Cath Procedure reports")
    
    # Download each document
    for i, doc in enumerate(documents):
        print(f"Downloading {i+1}/{len(documents)}: {doc['date']}")
        
        # Download binary content
        binary_resp = get_binary(doc["url"])
        
        # Create filename with full datetime
        datetime_str = format_datetime_for_filename(doc["date"])
        filename = f"{mrn}_{datetime_str}.pdf"
        
        # Save file
        with open(f"{save_directory}/{filename}", "wb") as f:
            f.write(binary_resp.content)
        
        print(f"Saved: {filename}")
    
    return fhir_response

# Example usage
# res = download_discharge_summaries(mrn="1234567", save_directory="dc_summaries", start_date="2025-01-01", end_date="2025-12-31", doc_type="text/html")
# res = download_cv_cath_reports(mrn="1234567", save_directory="cv_cath", start_date="2025-10-01", end_date="2025-10-31")