# Quick Start: Read-only FHIR API calls (Stanford Health Care)

Simple Python examples to make (read‑only) FHIR API calls to Epic at Stanford Health Care.

*Created by François Grolleau on 08/28/2025
based on the original documentation put together by Ruoqi Liu
Last update August 28, 2025.*

## Table of Contents
- [Setup and prerequisites](#setup-and-prerequisites)
- [Get all identifiers from MRN or email](#get-all-identifiers-from-mrn-or-email)
- [Get patient demographics from FHIR ID](#get-patient-demographics-from-fhir-id)
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

Common fields returned include: `NationalIdentifier`, `DateOfBirth`, `Email`, `PreferredName`, `GenderIdentity`, `Address`, `LegalName`, `Employment`, `PatientPortal`, `LegalSex`, `MaritalStatus`, `Religion`, `Ethnicity`, `Language`, `PatientType`, `Race`, `Phones`.

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


## Contribute new endpoints

Please add new, minimal examples following this structure:
1. A small function with a short docstring
2. A minimal example usage that demonstrates what the endpoint can achieve

 🚨 **IMPORTANT:** Include zero PHI and do NOT share secrets/keys in this guide; it will be public on GitHub.

Thank you for your contributions!
