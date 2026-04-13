"""
Test FHIR Condition endpoint to confirm access status.
Shows raw API response to verify if we get real conditions or OperationOutcome errors.

Usage:
    cd AIM2
    source /path/to/env_vars.sh
    python HttpTriggerInference/inference_pipeline_src/tests/test_condition_endpoint.py
"""
import os
import json
import requests
from requests.auth import HTTPBasicAuth

api_prefix = os.environ.get("EPIC_ENV", "")
client_id = os.environ.get("EPIC_CLIENT_ID", "")
username = os.environ.get("secretID", "")
password = os.environ.get("secretpass", "")
mrn = os.environ.get("EXAMPLE_MRN", "")

if not all([api_prefix, client_id, username, password, mrn]):
    print("ERROR: Missing environment variables")
    exit(1)

auth = HTTPBasicAuth(username, password)
headers = {"Epic-Client-ID": client_id, "Accept": "application/json"}

# Step 1: Resolve MRN to FHIR ID
print(f"Looking up patient MRN: {mrn}")
resp = requests.get(
    f"{api_prefix}api/FHIR/R4/Patient",
    params={"identifier": mrn},
    headers=headers,
    auth=auth,
)
fhir_id = None
for entry in resp.json().get("entry", []):
    fhir_id = entry.get("resource", {}).get("id")
    break

if not fhir_id:
    print("ERROR: Could not resolve FHIR ID")
    exit(1)

print(f"FHIR R4 ID: {fhir_id}")

# Step 2: Call Condition endpoint — try several category variants
# FHIR Condition categories: problem-list-item, encounter-diagnosis, health-concern
test_cases = [
    ("All conditions (no category filter)", {"patient": fhir_id}),
    ("Problem list only", {"patient": fhir_id, "category": "problem-list-item"}),
    ("Encounter diagnoses only", {"patient": fhir_id, "category": "encounter-diagnosis"}),
    ("Health concerns only", {"patient": fhir_id, "category": "health-concern"}),
]

for label, params in test_cases:
    print(f"\n--- {label} ---")
    print(f"Params: {params}")
    resp = requests.get(
        f"{api_prefix}api/FHIR/R4/Condition",
        params=params,
        headers=headers,
        auth=auth,
        timeout=60,
    )
    print(f"Status: {resp.status_code}")

    if resp.status_code != 200:
        print(f"Error: {resp.text[:500]}")
        continue

    data = resp.json()
    entries = data.get("entry", [])
    print(f"Total entries: {len(entries)}")

    # Classify entries
    real_conditions = []
    warnings = []
    for e in entries:
        r = e.get("resource", {})
        rt = r.get("resourceType", "unknown")
        if rt == "Condition":
            real_conditions.append(r)
        elif rt == "OperationOutcome":
            warnings.append(r)

    print(f"  Real Condition resources: {len(real_conditions)}")
    print(f"  OperationOutcome warnings: {len(warnings)}")

    # Show sample condition if present
    if real_conditions:
        sample = real_conditions[0]
        print(f"\n  Sample Condition:")
        print(f"    code.text: {sample.get('code', {}).get('text', 'N/A')}")
        print(f"    onsetDateTime: {sample.get('onsetDateTime', 'N/A')}")
        print(f"    recordedDate: {sample.get('recordedDate', 'N/A')}")
        print(f"    clinicalStatus: {sample.get('clinicalStatus', {}).get('coding', [{}])[0].get('code', 'N/A')}")
        print(f"    category: {[c.get('coding', [{}])[0].get('code', '') for c in sample.get('category', [])]}")

    # Show warning if present
    if warnings:
        sample = warnings[0]
        issues = sample.get('issue', [])
        if issues:
            print(f"\n  Warning: {issues[0].get('diagnostics', issues[0].get('details', {}).get('text', 'unknown'))[:300]}")

print("\n=== DONE ===")
