"""
Test FHIR Procedure endpoint to confirm access status.
Shows raw API response to verify if we get real procedures or OperationOutcome errors.

Usage:
    cd AIM2
    source /path/to/env_vars.sh
    python HttpTriggerInference/inference_pipeline_src/tests/test_procedure_endpoint.py
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

# Step 2: Call Procedure endpoint with large lookback
print(f"\n--- Calling FHIR R4 Procedure endpoint (3 year lookback) ---")
resp = requests.get(
    f"{api_prefix}api/FHIR/R4/Procedure",
    params={"patient": fhir_id, "date": "ge2023-01-01"},
    headers=headers,
    auth=auth,
    timeout=60,
)

print(f"Status: {resp.status_code}")
data = resp.json()

entries = data.get("entry", [])
print(f"Total entries returned: {len(entries)}")
print()

for i, entry in enumerate(entries[:5]):
    resource = entry.get("resource", {})
    resource_type = resource.get("resourceType", "unknown")
    print(f"Entry {i}: resourceType={resource_type}")
    print(json.dumps(resource, indent=2, default=str)[:800])
    print()

# Summary
real_procedures = [e for e in entries if e.get("resource", {}).get("resourceType") == "Procedure"]
warnings = [e for e in entries if e.get("resource", {}).get("resourceType") == "OperationOutcome"]
print(f"=== SUMMARY ===")
print(f"Real Procedure resources: {len(real_procedures)}")
print(f"OperationOutcome warnings: {len(warnings)}")
if warnings:
    print("CONFIRMED: Procedure endpoint is blocked — returns OperationOutcome instead of real data")
if real_procedures:
    print("Procedure endpoint is working — real procedure data available")
if not entries:
    print("No entries returned at all")
