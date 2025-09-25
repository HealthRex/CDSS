# Quick Start: Read-only FHIR API calls (Stanford Health Care)

Simple Python examples to make (read‑only) FHIR API calls to Epic at Stanford Health Care.

*First compiled by François Grolleau (08/2025); later updated and expanded by Wenyuan (Sandy) Chen. Contributions and corrections welcome!*

*Last revised: September 24, 2025.*

## Table of Contents
- [Setup and prerequisites](#setup-and-prerequisites)
- [Get all identifiers from MRN or email](#get-all-identifiers-from-mrn-or-email)
- [Get patient demographics from FHIR ID](#get-patient-demographics-from-fhir-id)
- [Download patient discharge summaries](#download-patient-discharge-summaries)
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

## Download patient discharge summaries

You can automatically download all discharge summaries for a patient by providing their MRN, an optional date range, and your preferred document format (HTML or RTF). The summaries will be saved in your chosen directory, with filenames that include both the MRN and the chart closure date (the date the summary was electronically signed).

Example usage:
```python
from fhir_fun import download_discharge_summaries

res = download_discharge_summaries(mrn=os.environ["EXAMPLE_MRN"], save_directory="dc_summaries", start_date="2025-01-01", end_date="2025-12-31", doc_type="text/html")
```

This will dowload all discharge summaries between the specified dates as HTML files in save_directory. See docstring for more information.


## Contribute new endpoints

We welcome your contributions! To add a new FHIR endpoint example, please follow these guidelines:

1. Provide a concise function with a clear, one-line docstring describing its purpose.
2. Include a minimal example usage that demonstrates how to call the function and what it returns.

If your code is longer than 10 lines, please define it as a function with a well-documented docstring in `fhir_fun.py`. In this `.md` file, only show how to use the function, not the full implementation.

🚨 **IMPORTANT:** Do not include any protected health information (PHI), or secret credentials in your examples. This documentation is public.

Suggested endpoints to document:
- Retrieving radiology reports
- Accessing progress notes
- Fetching lab results
- Other useful FHIR resources

For more details on available FHIR endpoints, check out the Stanford FHIR docs: [https://vendorservices.epic.com/Sandbox/Index](https://vendorservices.epic.com/Sandbox/Index).

Thank you for helping improve our FHIR documentation!
