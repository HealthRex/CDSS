# Medical Recommender System

This repository contains the Medical Recommender algorithm implementation for the SAGE project, providing intelligent recommendations for medical procedures, lab tests, and medications based on clinical data and ICD-10 codes.

## Project Structure

```
Recommender/
├── .gitignore                 # Git ignore patterns for the project
├── Readme.md                  # This file - project overview
├── requirements.txt           # Python dependencies
└── phase_1/                   # Main implementation phase
    ├── api/                   # FastAPI application and API endpoints
    │   ├── fastapi_app.py     # Main FastAPI application
    │   ├── bigquery_api.py    # BigQuery integration for data retrieval
    │   ├── example_usage.py   # Example usage scripts
    │   ├── demo_api.sh        # Demo script for API testing
    │   └── test_api.txt       # API testing examples
    ├── logs/                  # Application logs and results
    ├── real_data/             # Real clinical data (gitignored)
    ├── Notebook/              # Jupyter notebooks for analysis
    ├── main.py                # Main application entry point
    ├── example_clinical_cases.csv  # Sample clinical cases
    └── README.md              # Detailed API documentation
```

## Quick Start

### 1. Install Dependencies
```bash
cd scripts/eConsult/Recommender
pip install -r requirements.txt
```

### 2. Run the API
```bash
cd phase_1/api
python fastapi_app.py
```

The API will be available at `http://localhost:8000`

## Key Features

- **Clinical Case Processing**: Analyze clinical questions and notes to provide recommendations
- **ICD-10 Based Recommendations**: Get lab tests, procedures, and medications based on diagnosis codes
- **Specialty-Specific Filtering**: Filter recommendations by medical specialties
- **BigQuery Integration**: Direct database queries for real-time clinical data
- **Comprehensive API**: RESTful endpoints for various clinical workflows

## API Endpoints

- `POST /process_clinical_case` - Process clinical cases and get recommendations
- `POST /get_orders` - Get orders based on ICD-10 codes and patient demographics
- `POST /get_orders_from_file` - Process results from log files
- `POST /query` - Query ICD-10 codes by specialty

## Documentation

- **API Documentation**: See `phase_1/README.md` for detailed API usage and examples
- **Interactive Docs**: Access Swagger UI at `http://localhost:8000/docs` when running
- **Examples**: Check `phase_1/api/example_usage.py` for usage examples

## Development

This is Phase 1 of the Medical Recommender system. The project includes:
- FastAPI backend with comprehensive clinical data processing
- BigQuery integration for real-time clinical data access
- Logging and monitoring capabilities
- Example clinical cases and testing utilities

For detailed development information, see the `phase_1/` directory.
