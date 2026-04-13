"""Check what ZIP code format FHIR Patient resource returns."""
import os, requests, json
from requests.auth import HTTPBasicAuth

resp = requests.get(
    os.environ['EPIC_ENV'] + 'api/FHIR/R4/Patient',
    params={'identifier': os.environ['EXAMPLE_MRN']},
    headers={'Epic-Client-ID': os.environ['EPIC_CLIENT_ID'], 'Accept': 'application/json'},
    auth=HTTPBasicAuth(os.environ['secretID'], os.environ['secretpass']),
)
for entry in resp.json().get('entry', [])[:1]:
    print(json.dumps(entry['resource'].get('address', []), indent=2))
