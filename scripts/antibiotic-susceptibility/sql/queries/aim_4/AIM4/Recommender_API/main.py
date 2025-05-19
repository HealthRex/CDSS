from fastapi import FastAPI, Query
from typing import List, Optional
import pandas as pd
from pydantic import BaseModel
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = str(Path(__file__).parent)
sys.path.append(project_root)

from api.bigquery_api import BigQueryAPI

app = FastAPI(title="Antibiotic Susceptibility API")

class ResponseModel(BaseModel):
    descriptions: List[str]

@app.get("/query", response_model=ResponseModel)
async def query_data(
    diagnosis: str = Query(..., description="Diagnosis code (e.g., J01.90)"),
    gender: str = Query(..., description="Patient gender (Male/Female)"),
    type: str = Query(..., description="Type of results (med/proc)"),
    limit: int = Query(10, description="Maximum number of results to return"),
    year: int = Query(2021, description="Year of the dataset to use (2021-2024)")
):
    """
    Query the antibiotic susceptibility data based on diagnosis, gender, type, limit, and year.
    Returns a list of descriptions from BigQuery.
    """
    # Validate year
    if year not in [2021, 2022, 2023, 2024]:
        raise ValueError("Year must be between 2021 and 2024")
    
    # Validate gender
    if gender not in ["Male", "Female"]:
        raise ValueError("Gender must be either 'Male' or 'Female'")
    
    # Validate type
    if type not in ["med", "proc"]:
        raise ValueError("Type must be either 'med' or 'proc'")
    
    try:
        # Initialize BigQuery API
        api = BigQueryAPI()
        
        # Get results directly from BigQuery
        results = api.get_immediate_orders(
            diagnosis_codes=[diagnosis],
            patient_gender=gender,
            result_type=type,
            limit=limit,
            year=year
        )
        
        # Extract descriptions
        descriptions = results['description'].tolist()
        
        return ResponseModel(descriptions=descriptions)
        
    except Exception as e:
        raise Exception(f"Error querying BigQuery: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)