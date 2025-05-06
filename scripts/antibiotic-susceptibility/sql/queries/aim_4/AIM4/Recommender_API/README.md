# Medical Recommender API

A FastAPI-based API that processes clinical cases and recommends medical procedures or medications based on ICD-10 codes.

## Setup

1. Install required packages:
```bash
pip install fastapi uvicorn requests google-cloud-bigquery pandas langchain-groq langgraph
```

2. Set up Google Cloud credentials:
   - Make sure you have the Google Cloud SDK installed
   - Authenticate using `gcloud auth application-default login`
   - The application uses the project "som-nero-phi-jonc101"

## Running the API

1. Start the FastAPI server:
```bash
cd Recommender_API
uvicorn api.fastapi_app:app --reload --port 8002
```

The API will be available at `http://localhost:8002`

## API Endpoints

### 1. Process Clinical Case
Processes clinical notes to extract patient information and determine the appropriate ICD-10 code.

**Endpoint:** `POST /process_clinical_case`

**Request Body:**
```json
{
    "clinical_question": "Could this patient have stable angina?",
    "clinical_notes": "55-year-old male presents with chest pain on exertion..."
}
```

**Response:**
```json
{
    "patient_age": 55,
    "patient_gender": "male",
    "icd10_code": "I25.10",
    "rationale": "Patient presents with typical symptoms of stable angina...",
    "error": null
}
```

### 2. Get Orders
Retrieves recommended procedures or medications based on the ICD-10 code and patient information.

**Endpoint:** `POST /get_orders`

**Request Body:**
```json
{
    "icd10_code": "I25.10",
    "patient_age": 55,
    "patient_gender": "male",
    "result_type": "proc",  // or "med"
    "limit": 10,
    "min_patients_for_non_rare_items": 10,
    "year": 2024
}
```

**Response:**
```json
{
    "icd10_code": "I25.10",
    "result_type": "proc",
    "patient_age": 55,
    "patient_gender": "male",
    "data": [
        {
            "itemId": "PROC123",
            "description": "Cardiac Stress Test",
            "patientRate": 45.5,
            "encounterRate": 30.2,
            "nPatientscohortItem": 150,
            "nEncounterscohortItem": 75,
            "nPatientsCohortTotal": 330,
            "nEncountersCohortTotal": 248
        }
        // ... more items
    ]
}
```

## Example Usage

You can use the provided example script to test the API:

```bash
cd Recommender_API/api
python example_usage.py
```

Or use curl commands:

```bash
# Process clinical case
curl -X POST "http://localhost:8002/process_clinical_case" \
     -H "Content-Type: application/json" \
     -d '{
         "clinical_question": "Could this patient have stable angina?",
         "clinical_notes": "55-year-old male with chest pain on exertion..."
     }'

# Get orders
curl -X POST "http://localhost:8002/get_orders" \
     -H "Content-Type: application/json" \
     -d '{
         "icd10_code": "I25.10",
         "patient_age": 55,
         "patient_gender": "male",
         "result_type": "proc",
         "limit": 10
     }'
```

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8002/docs`
- ReDoc: `http://localhost:8002/redoc`

## Logging

The API logs its operations to `clinical_workflow.log` in the directory where the server is started. You can monitor the logs in real-time using:

```bash
tail -f clinical_workflow.log
``` 