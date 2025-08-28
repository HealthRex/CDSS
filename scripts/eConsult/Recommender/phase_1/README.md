# Medical Recommender API - Phase 1

A comprehensive FastAPI-based API that processes clinical cases and provides intelligent recommendations for medical procedures, lab tests, and medications based on ICD-10 codes, patient demographics, and clinical context.

## Overview

This API serves as the core recommendation engine for the Medical Recommender system, offering:
- **Clinical Case Analysis**: Process natural language clinical questions and notes
- **ICD-10 Based Recommendations**: Get targeted recommendations based on diagnosis codes
- **Specialty-Specific Filtering**: Filter results by medical specialties
- **Multi-Modal Output**: Support for labs, procedures, and medications
- **Real-time Processing**: Fast response times for clinical decision support

## Table of Contents

- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Data Structures](#data-structures)
- [Usage Examples](#usage-examples)
- [Testing](#testing)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites
- Python 3.8+
- pip package manager
- Access to required clinical databases

### 1. Install Dependencies
```bash
cd scripts/eConsult/Recommender
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy and edit environment template if needed
cp .env.template .env
# Edit .env with your configuration
```

### 3. Run the API
```bash
cd phase_1/api
python fastapi_app.py
```

The API will be available at `http://localhost:8000`

### 4. Verify Installation
```bash
# Health check
curl http://localhost:8000/health

# Access interactive documentation
open http://localhost:8000/docs
```

## API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/process_clinical_case` | POST | Process clinical cases and get recommendations |
| `/get_orders` | POST | Get orders based on ICD-10 codes and demographics |
| `/get_orders_from_file` | POST | Process results from log files |
| `/query` | POST | Query ICD-10 codes by specialty |
| `/health` | GET | API health check |

### Response Format
All endpoints return JSON responses with the following structure:
```json
{
  "status": "success|error",
  "data": {...},
  "message": "Description of the result",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Data Structures

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
    "result_type": null,  // "lab", "procedure", "med" or null for all
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

## Usage Examples

### Python Client Example
```python
import requests
import json

# Base URL
base_url = "http://localhost:8000"

# Process clinical case
def process_clinical_case():
    url = f"{base_url}/process_clinical_case"
    payload = {
        "clinical_question": "Patient has a history of prostate cancer...",
        "clinical_notes": "What antibiotic should I use for this patient?",
        "specialties": ["Infectious Diseases", "Urology"],
        "limit": 5000
    }
    
    response = requests.post(url, json=payload)
    return response.json()

# Get orders by ICD-10
def get_orders(icd10_code, patient_age, patient_gender):
    url = f"{base_url}/get_orders"
    payload = {
        "icd10_code": icd10_code,
        "patient_age": patient_age,
        "patient_gender": patient_gender,
        "result_type": None,  # All types
        "limit": 10
    }
    
    response = requests.post(url, json=payload)
    return response.json()
```

## Testing

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

### Testing Tools

**Note**: If you don't have `jq` installed, remove `| jq` from the end of each curl command. `jq` just makes the output prettier but is not required.

**Install jq**:
```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq

# Windows (with Chocolatey)
choco install jq
```

## Configuration

### Environment Variables
```bash
# Database connection
DATABASE_URL=your_database_url
API_KEY=your_api_key

# API settings
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

### API Settings
- **Rate Limiting**: Configurable per endpoint
- **Authentication**: API key-based authentication
- **Logging**: Comprehensive request/response logging
- **Caching**: Redis-based response caching (optional)

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

#### 2. Database Connection Issues
- Verify database credentials in `.env`
- Check network connectivity
- Ensure database service is running

#### 3. Import Errors
```bash
# Reinstall dependencies
pip uninstall -r requirements.txt
pip install -r requirements.txt
```

### Logs
Check the `logs/` directory for detailed error logs and API usage statistics.

### Support
For technical support or feature requests, please refer to the main project documentation or create an issue in the project repository.

---

## Additional Resources

- **Interactive API Docs**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`
- **Example Scripts**: See `api/example_usage.py` for more examples
- **Demo Scripts**: Check `api/demo_api.sh` for automated testing

