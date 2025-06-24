# Medical Recommender API

A FastAPI-based API that processes clinical cases and recommends medical procedures or medications based on ICD-10 codes.

## Quick Start

### 1. Install Dependencies
```bash
cd phase_1
pip install -r requirements.txt
```

### 2. Run the API
```bash
cd phase_1/api
python fastapi_app.py
```

The API will be available at `http://localhost:8000`

## Data Structure

### Process Clinical Case Request
```json
{
    "clinical_question": "Patient has a history of prostate cancer...",
    "clinical_notes": "What antibiotic should I use for this patient?",
    "specialties": ["Infectious Diseases", "Urology"],
    "limit": 5000
}
```

### Get Orders Request
```json
{
    "icd10_code": "E11.9",
    "patient_age": 45,
    "patient_gender": "female",
    "result_type": null,  // "lab", "procedure", or null for all
    "limit": 10
}
```

### Get Orders from File Request
```json
{
    "result_file_path": "logs/demo/clinical_workflow_20250623225312/result.csv",
    "result_type": "lab",
    "limit": 5
}
```

### Query ICD-10 Request
```json
{
    "result_type": "icd10",
    "specialties": ["Infectious Diseases", "Endocrinology"],
    "limit": 10,
    "query_params": null
}
```

## Test API Commands

### 1. Process a Clinical Case
```bash
curl -s -X POST "http://localhost:8000/process_clinical_case" \
  -H "Content-Type: application/json" \
  -d '{
    "clinical_question": "your question",
    "clinical_notes": "your notes,
    "specialties": ["Infectious Diseases", "Urology"],    
    "limit": 5000                                         
  }' | jq
```

### 2. Get Orders (All Types)
```bash
curl -s -X POST "http://localhost:8000/get_orders" \
  -H "Content-Type: application/json" \
  -d '{
    "icd10_code": "E11.9",
    "patient_age": 45,
    "patient_gender": "female",
    "result_type": null,
    "limit": 10
  }' | jq
```

### 3. Get Orders (Labs Only)
```bash
curl -s -X POST "http://localhost:8000/get_orders" \
  -H "Content-Type: application/json" \
  -d '{
    "icd10_code": "N39.0",
    "patient_age": 60,
    "patient_gender": "male",
    "result_type": "lab",
    "limit": 5
  }' | jq
```

### 4. Get Orders (Procedures Only)
```bash
curl -s -X POST "http://localhost:8000/get_orders" \
  -H "Content-Type: application/json" \
  -d '{
    "icd10_code": "I10",
    "patient_age": 70,
    "patient_gender": "female",
    "result_type": "procedure",
    "limit": 5
  }' | jq
```

### 5. Get Orders from File
```bash
curl -s -X POST "http://localhost:8000/get_orders_from_file" \
  -H "Content-Type: application/json" \
  -d '{
    "result_file_path": "logs/demo/clinical_workflow_20250623225312/result.csv",
    "result_type": "lab",
    "limit": 5
  }' | jq
```

### 6. Query ICD-10 Codes
```bash
curl -s -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "result_type": "icd10",
    "specialties": ["Infectious Diseases", "Endocrinology"],  
    "limit": 10,                                             
    "query_params": null
  }' | jq
```

## API Documentation

Once running, access interactive documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Note

If you don't have `jq` installed, remove `| jq` from the end of each curl command. `jq` just makes the output prettier but is not required.
