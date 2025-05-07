from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from google.cloud import bigquery
import pandas as pd
import json
import logging
import datetime
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableLambda
import re
import sys
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.bigquery_api import BigQueryAPI

app = FastAPI(title="Medical Recommender API")

# Initialize BigQuery client and API
client = bigquery.Client("som-nero-phi-jonc101")
api = BigQueryAPI()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'clinical_workflow_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

class ClinicalState(TypedDict):
    clinical_question: str
    clinical_notes: str
    icd10_codes: pd.DataFrame
    patient_age: int | None
    patient_gender: str | None
    icd10_code: str | None
    rationale: str | None
    error: str | None

class QueryRequest(BaseModel):
    result_type: str = "icd10"  # Default to icd10
    limit: int = 100  # Default limit
    query_params: Optional[Dict[str, Any]] = None

class ClinicalCaseRequest(BaseModel):
    clinical_question: str
    clinical_notes: str

class OrderRequest(BaseModel):
    icd10_code: str
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    result_type: str = "proc"  # Default to proc, can be "proc" or "med"
    limit: int = 100  # Default limit
    min_patients_for_non_rare_items: int = 10
    year: int = 2024

    @classmethod
    def from_clinical_result(cls, clinical_result: dict, result_type: str = "proc", limit: int = 100):
        """Create an OrderRequest from the output of process_clinical_case."""
        return cls(
            icd10_code=clinical_result["icd10_code"],
            patient_age=clinical_result["patient_age"],
            patient_gender=clinical_result["patient_gender"],
            result_type=result_type,
            limit=limit
        )

def clean_output(output):
    """Clean up the output by removing content wrapped in <think> tags and extracting only the actual response."""
    if isinstance(output, pd.DataFrame):
        return output
    
    cleaned_output = re.sub(r'<think>.*?</think>', '', output, flags=re.DOTALL)
    cleaned_output = cleaned_output.strip()
    
    return cleaned_output

def log_stage(stage_name: str, input_data: dict, output_data: dict):
    """Log the input and output of each stage."""
    input_copy = input_data.copy()
    output_copy = output_data.copy()
    
    if 'icd10_codes' in input_copy and isinstance(input_copy['icd10_codes'], pd.DataFrame):
        input_copy['icd10_codes'] = input_copy['icd10_codes'].to_string()
    if 'icd10_codes' in output_copy and isinstance(output_copy['icd10_codes'], pd.DataFrame):
        output_copy['icd10_codes'] = output_copy['icd10_codes'].to_string()
    
    logging.info(f"\n{'='*50}")
    logging.info(f"Stage: {stage_name}")
    logging.info(f"Input: {json.dumps(input_copy, indent=2)}")
    logging.info(f"Output: {json.dumps(output_copy, indent=2)}")
    logging.info(f"{'='*50}\n")

def extract_patient_info(state: dict) -> dict:
    """Extract patient age and gender from clinical notes."""
    input_state = state.copy()
    
    llm = ChatGroq(
        model_name="Deepseek-R1-Distill-Llama-70b",
        temperature=0.3,
        api_key= api_key
     
    )
    
    prompt = f"""
    Extract the patient's age and gender from the following clinical notes.
    Return ONLY a JSON object with 'age' and 'gender' fields.
    DO NOT include any other text, thinking process, or explanation.
    The response should start with {{ and end with }}.
    
    Example of expected format:
    {{"age": 55, "gender": "male"}}
    
    Clinical Notes: {state.get('clinical_notes')}
    """
    logging.info(f"LLM Prompt for extract_patient_info:\n{prompt}")
    
    response = llm.invoke([HumanMessage(content=prompt)])
    logging.info(f"LLM Response for extract_patient_info:\n{response.content}")

    try:
        content = clean_output(response.content)        
        info = json.loads(content)
        state['patient_age'] = info['age']
        state['patient_gender'] = info['gender']
    except Exception as e:
        state['error'] = f"Failed to extract patient information: {str(e)}"
    
    log_stage("extract_patient_info", input_state, state)
    return state

def match_icd10_code(state: dict) -> dict:
    """Match clinical information to ICD-10 code."""
    state['error'] = None
    input_state = state.copy()
        
    llm = ChatGroq(
        model="Deepseek-R1-Distill-Llama-70b",
        api_key= api_key
    )
    
    prompt = f"""
    Match the clinical information to the most appropriate ICD-10 code from the provided list.
    Return ONLY a JSON object with exactly two fields: 'icd10_code' and 'rationale'.
    DO NOT include any other text, thinking process, or explanation.
    The response should start with {{ and end with }}.

    Example of expected format:
    {{"icd10_code": "xxx", "rationale": "xxxxx"}}

    
    Clinical Question: {state.get('clinical_question')}
    Clinical Notes: {state.get('clinical_notes')}
    Patient Age: {state.get('patient_age')}
    Patient Gender: {state.get('patient_gender')}
    
    Available ICD-10 Codes:
    {state.get('icd10_codes')}
    """
    logging.info(f"LLM Prompt for match_icd10_code:\n{prompt}")
    response = llm.invoke([HumanMessage(content=prompt)])
    logging.info(f"LLM Response for match_icd10_code:\n{response.content}")
    try:
        output = clean_output(response.content)
        match = json.loads(output)
        state['icd10_code'] = match['icd10_code']
        state['rationale'] = match['rationale']
    except:
        state['error'] = "Failed to match ICD-10 code"
    log_stage("match_icd10_code", input_state, state)
    return state

def validate_icd10_code_exists(state: dict) -> dict:
    """Validate if the ICD-10 code exists in the provided list."""
    input_state = state.copy()
    valid_codes = state['icd10_codes']['icd10'].tolist()
    if state.get('icd10_code') not in valid_codes:
        logging.warning(f"Invalid code {state.get('icd10_code')}, will rerun matching...")
        state['error'] = f"Invalid code {state.get('icd10_code')}, not in provided list"
        state['icd10_code'] = None
        state['rationale'] = None
    else:
        state['error'] = None
    log_stage("validate_icd10_code_exists", input_state, state)
    return state

def validate_icd10_clinical_match(state: dict) -> dict:
    """Validate if the matched ICD-10 code is clinically appropriate."""
    input_state = state.copy()
    llm = ChatGroq(
        model_name="Deepseek-R1-Distill-Llama-70b",
        temperature=0.3,
        api_key= api_key
    )
    
    prompt = f"""
    Validate if the matched ICD-10 code is appropriate for the clinical case.
    Return ONLY a JSON object with exactly two fields: 'is_valid' (boolean) and 'reason' (string).
    DO NOT include any other text, thinking process, or explanation.

    Example of expected format:
    {{"is_valid": true, "reason": "The code I10 matches the patient's hypertension diagnosis"}}
    or
    {{"is_valid": false, "reason": "The code I10 is too general for this specific case"}}

    Current Match:
    ICD-10 Code: {state.get('icd10_code')}
    Rationale: {state.get('rationale')}

    Clinical Question: {state.get('clinical_question')}
    Clinical Notes: {state.get('clinical_notes')}
    Patient Age: {state.get('patient_age')}
    Patient Gender: {state.get('patient_gender')}
    
    Available ICD-10 Codes:
    {state['icd10_codes'].to_string()}
    """
    logging.info(f"LLM Prompt for validate_icd10_clinical_match:\n{prompt}")
    
    response = llm.invoke([HumanMessage(content=prompt)])
    logging.info(f"LLM Response for validate_icd10_clinical_match:\n{response.content}")
    try:
        output = clean_output(response.content)
        validation = json.loads(output)
        logging.info(f"Validation result: {validation}")
        
        if not validation['is_valid']:
            state['error'] = f"Invalid match: {validation['reason']}"
            state['icd10_code'] = None
            state['rationale'] = None
            return state
        else:
            state['error'] = None
    except Exception as e:
        logging.error(f"Validation error: {str(e)}")
        state['error'] = f"Failed to validate ICD-10 code: {str(e)}"
        return state
    
    log_stage("validate_icd10_clinical_match", input_state, state)
    return state

def create_clinical_graph() -> StateGraph:
    workflow = StateGraph(dict)
    
    # Add nodes
    workflow.add_node("extract_patient_info", RunnableLambda(extract_patient_info))
    workflow.add_node("match_icd10_code", RunnableLambda(match_icd10_code))
    workflow.add_node("validate_icd10_code_exists", RunnableLambda(validate_icd10_code_exists))
    workflow.add_node("validate_icd10_clinical_match", RunnableLambda(validate_icd10_clinical_match))
    
    # Add basic edges
    workflow.add_edge("extract_patient_info", "match_icd10_code")
    workflow.add_edge("match_icd10_code", "validate_icd10_code_exists")
    
    # Define conditional edges
    workflow.add_conditional_edges(
        "validate_icd10_code_exists",
        lambda x: "match_icd10_code" if x.get("error") else "validate_icd10_clinical_match",
        {
            "match_icd10_code": "match_icd10_code",
            "validate_icd10_clinical_match": "validate_icd10_clinical_match"
        }
    )
    
    workflow.add_conditional_edges(
        "validate_icd10_clinical_match",
        lambda x: "match_icd10_code" if x.get("error") else END,
        {
            "match_icd10_code": "match_icd10_code",
            END: END
        }
    )
    
    workflow.set_entry_point("extract_patient_info")
    
    return workflow.compile()

@app.post("/query")
async def query_data(request: QueryRequest):
    try:
        if request.result_type == "icd10":
            # Query for ICD10 codes
            query = """
            select distinct icd10, count(icd10) as count 
            from som-nero-phi-jonc101.shc_core_2024.diagnosis
            group by icd10
            order by count desc
            limit @limit
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("limit", "INT64", request.limit)
                ]
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid result_type. Must be 'icd10' ")

        # Execute the query
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        
        # Convert to DataFrame and then to dict for JSON response
        df = results.to_dataframe()
        return {"data": df.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process_clinical_case")
async def process_clinical_case(request: ClinicalCaseRequest):
    try:
        # Get ICD10 codes
        query = """
        select distinct icd10, count(icd10) as count 
        from som-nero-phi-jonc101.shc_core_2024.diagnosis
        group by icd10
        order by count desc
        limit 400
        """
        query_job = client.query(query)
        results = query_job.result()
        icd10_codes_df = results.to_dataframe()

        # Create the graph
        graph = create_clinical_graph()
        
        # Initialize state
        initial_state = {
            "clinical_question": request.clinical_question,
            "clinical_notes": request.clinical_notes,
            "icd10_codes": icd10_codes_df,
            "patient_age": None,
            "patient_gender": None,
            "icd10_code": None,
            "rationale": None,
            "error": None
        }
        
        # Run the graph
        config = {"recursion_limit": 100}
        result = graph.invoke(initial_state, config=config)
        
        # Clean up the result
        clean_result = {
            "patient_age": result.get("patient_age"),
            "patient_gender": result.get("patient_gender"),
            "icd10_code": result.get("icd10_code"),
            "rationale": result.get("rationale"),
            "error": result.get("error")
        }
        
        return clean_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_orders")
async def get_orders(request: OrderRequest):
    try:
        if request.result_type not in ["proc", "med"]:
            raise HTTPException(status_code=400, detail="Invalid result_type. Must be 'proc' or 'med'")

        # Prepare parameters for the BigQueryAPI
        params = {
            'patient_age': request.patient_age,
            'patient_gender': request.patient_gender,
            'icd10_code': request.icd10_code
        }

        # Use the existing BigQueryAPI to get orders
        results = api.get_orders(
            params=params,
            min_patients_for_non_rare_items=request.min_patients_for_non_rare_items,
            result_type=request.result_type,
            limit=request.limit,
            year=request.year
        )
        
        return {
            "icd10_code": request.icd10_code,
            "result_type": request.result_type,
            "patient_age": request.patient_age,
            "patient_gender": request.patient_gender,
            "data": results.to_dict(orient="records")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 