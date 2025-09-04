# Quick Start: Read-only FHIR API calls (Stanford Health Care)

Simple Python examples to make (read‑only) FHIR API calls to Epic at Stanford Health Care.

*Created by François Grolleau on 08/28/2025 based on the original documentation put together by Ruoqi Liu*

*Last update August 28, 2025.*

## Table of Contents
- [Setup and prerequisites](#setup-and-prerequisites)
- [Get all identifiers from MRN or email](#get-all-identifiers-from-mrn-or-email)
- [Get patient demographics from FHIR ID](#get-patient-demographics-from-fhir-id)
- [Download patient radiology reports](#download-patient-radiology-reports)
- [Contribute new endpoints](#contribute-new-endpoints)


## Setup and prerequisites

- Python 3.6+ with `requests` installed (`pip install requests`)
- Stanford VPN running on Full traffic, non–split tunnel (setup [here](https://uit.stanford.edu/service/vpn)).
- `env_vars.sh` file: To obtain this file, first email *Jonathan* to request access and receive written permission. Once you have permission, forward the email to *Ruoqi* or *François*, who will SECURE:email you the file. **Keep this file confidential.**

Load all login environment variables in the current shell before running Python:
```bash
source env_vars.sh
```

In python, import this (common to all examples):

```python
import os
import requests
from requests.auth import HTTPBasicAuth
```

## Get all identifiers from MRN or email

```python
def get_patient_identifiers(identifier: str, identifier_type: str = "SHCMRN") -> dict:
    """Return a mapping of identifier type to value for a patient.

    identifier: patient identifier value (e.g., MRN or MyChart email)
    identifier_type: type of identifier provided ("SHCMRN" for MRN, "MYCHARTLOGIN" for email)
    """
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
```

Examples:

- **Get patient email from MRN**
```python
ids = get_patient_identifiers(identifier="1234567", identifier_type="SHCMRN")
print(ids.get("MYCHARTLOGIN"))
```

- **Get patient MRN from email**
```python
ids = get_patient_identifiers(identifier="USER@EXAMPLE.COM", identifier_type="MYCHARTLOGIN")
print(ids.get("SHCMRN"))
```


## Get patient demographics from FHIR ID

Fields returned include: `NationalIdentifier`, `DateOfBirth`, `Email`, `PreferredName`, `GenderIdentity`, `Address`, `LegalName`, `Employment`, `PatientPortal`, `LegalSex`, `MaritalStatus`, `Religion`, `Ethnicity`, `Language`, `PatientType`, `Race`, `Phones`.

```python
def get_demographics(patient_fhir_id: str) -> dict:
    """Return patient demographics given a FHIR patient ID."""
    resp = requests.get(
        f"{os.environ['EPIC_ENV']}api/epic/2019/PatientAccess/Patient/GetPatientDemographics/Patient/Demographics",
        params={"PatientID": patient_fhir_id, "PatientIDType": "FHIR"},
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Epic-Client-ID": os.environ["EPIC_CLIENT_ID"],
        },
        auth=HTTPBasicAuth(os.environ["secretID"], os.environ["secretpass"]),
        timeout=30,
    )
    return resp.json()
```

Example usage (get FHIR ID from MRN first, then demographics):
```python
ids = get_patient_identifiers(identifier="1234567", identifier_type="SHCMRN")
demo = get_demographics(ids["FHIR"])
print(demo)
```

## Download patient radiology reports

Given an MRN, start and end dates, download all radiology reports using the FHIR DocumentReference endpoint.

```python
import re
import os
from datetime import date

def download_radiology_reports(mrn: str, start_date: date, end_date: date, save_directory: str = "./radiology_reports") -> dict:
    """Download all radiology reports for a patient within a date range."""
    # Get patient FHIR ID
    ids = get_patient_identifiers(identifier=mrn, identifier_type="SHCMRN")
    if "FHIR" not in ids:
        raise ValueError(f"No FHIR ID found for MRN {mrn}")
    
    fhir_id = ids["FHIR"]
    
    # Get documents list with proper date filter (multiple date parameters)
    params = {
        "patient": fhir_id,
        "_count": "50",  # Get more documents per API call than the default limit
        "date": [f"ge{start_date.strftime('%Y-%m-%d')}", f"le{end_date.strftime('%Y-%m-%d')}"]
    }
    
    resp = requests.get(
        f"{os.environ['EPIC_ENV']}api/FHIR/R4/DocumentReference",
        params=params,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Epic-Client-ID": os.environ["EPIC_CLIENT_ID"],
        },
        auth=HTTPBasicAuth(os.environ["secretID"], os.environ["secretpass"]),
        timeout=30,
    )
    
    if resp.status_code != 200:
        raise Exception(f"API error {resp.status_code}")
    
    # Parse XML to find all documents with content
    xml_text = resp.text
    entries = re.findall(r'<entry>(.*?)</entry>', xml_text, re.DOTALL)
    
    downloaded_files = []
    failed_downloads = []
    skipped_files = []  # Track files skipped due to date filtering
    
    for entry in entries:
        # Extract document info
        id_match = re.search(r'<id value="([^"]*)"', entry)
        type_match = re.search(r'<type>.*?<text value="([^"]*)"', entry, re.DOTALL)
        date_match = re.search(r'<date value="([^"]*)"', entry)
        url_match = re.search(r'<attachment>.*?<url value="([^"]*)"', entry, re.DOTALL)
        content_type_match = re.search(r'<attachment>.*?<contentType value="([^"]*)"', entry, re.DOTALL)
        
        if id_match and url_match and content_type_match:
            doc_id = id_match.group(1)
            doc_type = type_match.group(1) if type_match else "Unknown"
            doc_date = date_match.group(1) if date_match else "Unknown"
            attachment_url = url_match.group(1)
            content_type = content_type_match.group(1)
            
            # Client-side date validation - skip documents outside date range
            if doc_date != "Unknown":
                try:
                    # Parse the document date (assuming ISO format YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
                    doc_date_obj = date.fromisoformat(doc_date[:10])
                    if doc_date_obj < start_date or doc_date_obj > end_date:
                        skipped_files.append({
                            "document_type": doc_type,
                            "document_date": doc_date,
                            "reason": f"Date {doc_date[:10]} outside range {start_date} to {end_date}"
                        })
                        continue  # Skip this document - outside date range
                except ValueError:
                    # If date parsing fails, we'll still process the document
                    pass
            
            # Download the content
            full_url = f"{os.environ['EPIC_ENV']}api/FHIR/R4/{attachment_url}"
            
            try:
                content_resp = requests.get(
                    full_url,
                    headers={"Epic-Client-ID": os.environ["EPIC_CLIENT_ID"]},
                    auth=HTTPBasicAuth(os.environ["secretID"], os.environ["secretpass"]),
                    timeout=60,
                )
                
                if content_resp.status_code == 200:
                    # Determine filename with date prefix
                    extension = '.pdf' if 'pdf' in content_type.lower() else '.bin'
                    date_prefix = doc_date[:10] if doc_date != "Unknown" else "unknown_date"
                    safe_type = re.sub(r'[^\w\s-]', '', doc_type)[:30]  # Clean filename
                    filename = f"{save_directory}/{date_prefix}_{safe_type}_{doc_id[:8]}{extension}"
                    
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(filename), exist_ok=True)
                    
                    # Save file
                    with open(filename, 'wb') as f:
                        f.write(content_resp.content)
                    
                    downloaded_files.append({
                        "document_type": doc_type,
                        "document_date": doc_date,
                        "filename": filename,
                        "content_type": content_type,
                        "size_bytes": len(content_resp.content)
                    })
                else:
                    failed_downloads.append({
                        "document_type": doc_type,
                        "document_date": doc_date,
                        "error": f"HTTP {content_resp.status_code}"
                    })
            except Exception as e:
                failed_downloads.append({
                    "document_type": doc_type,
                    "document_date": doc_date,
                    "error": str(e)
                })
    
    return {
        "success": len(downloaded_files) > 0,
        "downloaded_count": len(downloaded_files),
        "failed_count": len(failed_downloads),
        "skipped_count": len(skipped_files),
        "downloaded_files": downloaded_files,
        "failed_downloads": failed_downloads,
        "skipped_files": skipped_files
    }
```

Example usage:
```python
from datetime import date, timedelta

# Download all documents from the last 30 days to organized directories
start_date = date.today() - timedelta(days=30)
end_date = date.today()

result = download_radiology_reports(mrn="1234567", start_date=start_date, end_date=end_date, save_directory="./radiology_reports/")

# check results
if result["success"]:
    print(f"Downloaded {result['downloaded_count']} documents")
    for doc in result['downloaded_files']:
        print(f"✅ {doc['document_date'][:10]} - {doc['document_type']}")
        print(f"   File: {doc['filename']} ({doc['size_bytes']:,} bytes)")
else:
    print("No documents found in date range")
```

## Contribute new endpoints

Please add new, minimal examples following this structure:
1. A small function with a short docstring
2. A minimal example usage that demonstrates what the endpoint can achieve

 🚨 **IMPORTANT:** Include zero PHI and do NOT share secret keys in this guide; it will be public on GitHub.

Thank you for your contributions!
