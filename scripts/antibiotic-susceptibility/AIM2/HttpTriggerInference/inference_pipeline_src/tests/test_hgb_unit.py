"""
Test Epic lab API — tries multiple lab types to verify API access and check HGB units.

Usage:
    cd AIM2
    source /path/to/env_vars.sh
    EXAMPLE_MRN=12345678 python HttpTriggerInference/inference_pipeline_src/tests/test_hgb_unit.py
"""
import os
import json
import requests
from requests.auth import HTTPBasicAuth

api_prefix = os.environ.get("EPIC_ENV", "")
client_id = os.environ.get("EPIC_CLIENT_ID", "")
username = os.environ.get("secretID", "")
password = os.environ.get("secretpass", "")
example_mrn = os.environ.get("EXAMPLE_MRN", "")

if not all([api_prefix, client_id, username, password, example_mrn]):
    print("ERROR: Missing environment variables. Run: source env_vars.sh")
    exit(1)

auth = HTTPBasicAuth(username, password)
headers = {"Epic-Client-ID": client_id, "Accept": "application/json"}

# Step 1: Resolve MRN to FHIR IDs
print(f"Looking up patient MRN: {example_mrn}")
resp = requests.get(
    f"{api_prefix}api/FHIR/R4/Patient",
    params={"identifier": example_mrn},
    headers=headers,
    auth=auth,
)
patient_data = resp.json()
fhir_r4_id = None
fhir_stu3_id = None

for entry in patient_data.get("entry", []):
    resource = entry.get("resource", {})
    fhir_r4_id = resource.get("id")
    for ident in resource.get("identifier", []):
        id_type = ident.get("type", {}).get("text", "")
        if id_type == "FHIR STU3":
            fhir_stu3_id = ident.get("value")
    break

print(f"FHIR R4 ID: {fhir_r4_id}")
print(f"FHIR STU3 ID: {fhir_stu3_id}")

# Use whichever ID we have — prefer STU3 since that's what the lab API expects
patient_id = fhir_stu3_id or fhir_r4_id
if not patient_id:
    print("ERROR: Could not resolve any FHIR ID")
    exit(1)

# Step 2: Try multiple lab types with longer lookback
lab_types = ["hgb", "wbc", "plt", "na", "cr", "bun", "hco3", "lactate"]
print(f"\nUsing PatientID={patient_id} (FHIR STU3)")
print(f"Lookback: 365 days")
print(f"Testing lab types: {lab_types}\n")

for lab_name in lab_types:
    lab_packet = {
        "PatientID": patient_id,
        "PatientIDType": "FHIR STU3",
        "UserID": username[4:],
        "UserIDType": "External",
        "NumberDaysToLookBack": 365,
        "MaxNumberOfResults": 5,
        "FromInstant": "",
        "ComponentTypes": [{"Value": lab_name, "Type": "base-name"}],
    }

    resp = requests.post(
        f"{api_prefix}api/epic/2014/Results/Utility/GETPATIENTRESULTCOMPONENTS/ResultComponents",
        headers={"Content-Type": "application/json; charset=utf-8", "Epic-Client-ID": client_id},
        auth=auth,
        json=lab_packet,
    )

    lab_response = resp.json()
    components = lab_response.get("ResultComponents") or []

    if not components:
        print(f"  {lab_name}: no results")
        continue

    values = []
    for component in components:
        raw_value = component.get("Value")
        units = component.get("Units")
        instant = component.get("Instant", "")
        if raw_value:
            numeric_chars = "0123456789-."
            num_str = "".join(c for c in raw_value[0] if c in numeric_chars)
            if num_str:
                values.append(float(num_str))
            print(f"  {lab_name}: value={raw_value}, units={units}, date={instant}")

    if values:
        print(f"  → Numeric values: {values}")
        if lab_name == "hgb":
            avg = sum(values) / len(values)
            if avg < 30:
                print(f"  → HGB in g/dL. Models expect ~9700. NEED x1000 conversion.")
            elif avg > 1000:
                print(f"  → HGB already scaled. No conversion needed.")

print("\nDone.")
