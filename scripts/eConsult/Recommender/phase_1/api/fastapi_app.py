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
from langchain_core.runnables import RunnableLambda
import re
import sys
import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("HEALTHREX_API_KEY")
headers = {'Ocp-Apim-Subscription-Key': api_key, 'Content-Type': 'application/json'}
url = "https://apim.stanfordhealthcare.org/openai-eastus2/deployments/gpt-4.1/chat/completions?api-version=2025-01-01-preview"

def query_llm(my_question):
    payload = json.dumps({
        "model": "gpt-4.1", 
        "messages": [{"role": "user", "content": my_question}]
    })
    response = requests.request("POST", url, headers=headers, data=payload)
    message_content = response.json()["choices"][0]["message"]["content"]
    print(message_content)
    return message_content

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.bigquery_api import BigQueryAPI

app = FastAPI(title="Medical Recommender API")

# Initialize BigQuery client and API
client = bigquery.Client("som-nero-phi-jonc101")
api = BigQueryAPI()

# Set up logging
class NonEmptyFileHandler(logging.FileHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=False):
        super().__init__(filename, mode, encoding, delay=True)
        self.filename = filename
        self._has_logged = False

    def emit(self, record):
        if not self._has_logged:
            self._has_logged = True
            self._open()
        super().emit(record)

    def close(self):
        if self._has_logged:
            super().close()
        else:
            # If no logs were written, remove the empty file
            try:
                os.remove(self.filename)
            except OSError:
                pass

def setup_logging_for_case():
    """
    Set up logging for a new clinical case.
    Creates a new log directory and configures logging.
    Returns the log directory path.
    """
    # Create logs directory with timestamp for this specific case
    log_dir = f"../logs/clinical_workflow_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    os.makedirs(log_dir, exist_ok=True)
    
    # Clear any existing handlers to avoid duplicate logging
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Set up logging with the custom handler for this case
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            NonEmptyFileHandler(os.path.join(log_dir, 'run.log')),
            logging.StreamHandler()
        ]
    )
    
    return log_dir

class ClinicalState(TypedDict):
    clinical_question: str
    clinical_notes: str
    icd10_codes: pd.DataFrame
    patient_age: int | None
    patient_gender: str | None
    icd10_code: str | None
    rationale: str | None
    error: str | None
    retry_count: int
    stopped: bool | None

class QueryRequest(BaseModel):
    result_type: str = "icd10"  # Default to icd10
    limit: int = 10  # Default limit
    query_params: Optional[Dict[str, Any]] = None

class ClinicalCaseRequest(BaseModel):
    clinical_question: str
    clinical_notes: str

class OrderRequest(BaseModel):
    icd10_code: str
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    result_type: Optional[str] = None  # Default to procedure, can be "lab", "med", "procedure", or None for all
    limit: int = 100  # Default limit
    min_patients_for_non_rare_items: int = 10
    year: int = 2024

    @classmethod
    def from_clinical_result(cls, clinical_result: dict, result_type: str = "procedure", limit: int = 100):
        """Create an OrderRequest from the output of process_clinical_case."""
        return cls(
            icd10_code=clinical_result["icd10_code"],
            patient_age=clinical_result["patient_age"],
            patient_gender=clinical_result["patient_gender"],
            result_type=result_type,
            limit=limit
        )

class OrderFromFileRequest(BaseModel):
    result_file_path: str  # Path to the result.csv file
    result_type: Optional[str] = None  # "lab", "med", "procedure", or None for all
    limit: int = 10  # Default limit
    min_patients_for_non_rare_items: int = 10
    year: int = 2024
    custom_filename: Optional[str] = None  # Optional custom filename for the output CSV

def clean_output(output):
    """
    Clean up the output by removing content wrapped in <think> tags and extracting only the actual response.
    """
    # If the output is already a DataFrame, return it directly
    if isinstance(output, pd.DataFrame):
        return output
    
    # Remove all content between <think> tags
    cleaned_output = re.sub(r'<think>.*?</think>', '', output, flags=re.DOTALL)
    
    # Remove any leading/trailing whitespace
    cleaned_output = cleaned_output.strip()
    
    return cleaned_output

def log_stage(stage_name: str, input_data: dict, output_data: dict):
    """Log the input and output of each stage."""
    input_copy = input_data.copy()
    output_copy = output_data.copy()
    
    if 'icd10_codes' in input_copy and isinstance(input_copy['icd10_codes'], pd.DataFrame):
        input_copy['icd10_codes'] = "check separate file for icd10_codes"
    if 'icd10_codes' in output_copy and isinstance(output_copy['icd10_codes'], pd.DataFrame):
        output_copy['icd10_codes'] = "check separate file for icd10_codes"
    
    logging.info(f"\n{'='*50}")
    logging.info(f"Summary of Stage: {stage_name}")
    logging.info(f"Input: {json.dumps(input_copy, indent=2)}")
    logging.info(f"Output: {json.dumps(output_copy, indent=2)}")
    logging.info(f"{'='*50}\n")

def stopper_node(state: dict) -> dict:
    state = state.copy()
    state['stopped'] = True
    state['error'] = f"Stopped after {state.get('retry_count', 0)} retries. Manual review required."
    log_stage("stopper_node", state, state)
    return state

def extract_patient_info(state: dict) -> dict:
    """Extract patient age and gender from clinical notes."""
    input_state = state.copy()
    
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
    
    response = query_llm(prompt)
    logging.info(f"LLM Response for extract_patient_info:\n{response}")

    try:
        # Clean the response to handle markdown code block
        content = clean_output(response)        
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
    state['retry_count'] += 1
    
    input_state = state.copy()
    
    raw_prompt = f"""
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
    
    """
    prompt = raw_prompt + f"Available ICD-10 Codes: {state['icd10_codes'].to_string()}"
    logging.info(f"LLM Prompt for match_icd10_code:\n{raw_prompt} + available ICD-10 codes")
    response = query_llm(prompt)
    logging.info(f"LLM Response for match_icd10_code:\n{response}")
    try:
        output = clean_output(response)
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
    # Check if the code is in the provided list
    valid_codes = state['icd10_codes']['icd10'].tolist()
    if state.get('icd10_code') not in valid_codes:
        logging.warning(f"Invalid code {state.get('icd10_code')}, will rerun matching...")
        print(f"Invalid code {state.get('icd10_code')}, will rerun matching...")
        state['error'] = f"Invalid code {state.get('icd10_code')}, not in provided list"
        state['icd10_code'] = None
        state['rationale'] = None
    else:
        # Clear any previous errors if validation passes
        state['error'] = None
    log_stage("validate_icd10_code_exists", input_state, state)
    return state

def validate_icd10_clinical_match(state: dict) -> dict:
    """Validate if the matched ICD-10 code is clinically appropriate."""
    input_state = state.copy()
    
    raw_prompt = f"""
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
    """
    prompt = raw_prompt + f"Available ICD-10 Codes: {state['icd10_codes'].to_string()}"
    logging.info(f"LLM Prompt for validate_icd10_clinical_match:\n{raw_prompt} + available ICD-10 codes")
    
    response = query_llm(prompt)
    logging.info(f"LLM Response for validate_icd10_clinical_match:\n{response}")
    try:
        output = clean_output(response)
        validation = json.loads(output)
        logging.info(f"Validation result: {validation}")
        
        if not validation['is_valid']:
            print("Invalid match, will rerun matching...")
            state['error'] = f"Invalid match: {validation['reason']}"
            state['icd10_code'] = None
            state['rationale'] = None
            return state
        else:
             # Clear any previous errors if validation passes
            state['error'] = None
    except Exception as e:
        logging.error(f"Validation error: {str(e)}")
        state['error'] = f"Failed to validate ICD-10 code: {str(e)}"
        return state
    
    log_stage("validate_icd10_clinical_match", input_state, state)
    return state

def create_clinical_graph(MAX_RETRIES = 3) -> StateGraph:
    workflow = StateGraph(dict)
    
    # Add nodes
    workflow.add_node("extract_patient_info", RunnableLambda(extract_patient_info))
    workflow.add_node("match_icd10_code", RunnableLambda(match_icd10_code))
    workflow.add_node("validate_icd10_code_exists", RunnableLambda(validate_icd10_code_exists))
    workflow.add_node("validate_icd10_clinical_match", RunnableLambda(validate_icd10_clinical_match))
    # Add stopper node
    workflow.add_node("stopper", RunnableLambda(stopper_node))

  
    # Add basic edges
    workflow.add_edge("extract_patient_info", "match_icd10_code")
    workflow.add_edge("match_icd10_code", "validate_icd10_code_exists")

    # Helper to increment retry count
    def check_and_route(state, next_node):
        if state.get("error"):
            # Only increment retry_count when a retry will actually happen
            if state.get("retry_count", 0) >= MAX_RETRIES:
                return "stopper"
            return "match_icd10_code"
        else:
            return next_node
        

        
    # Conditional for code existence validation
    workflow.add_conditional_edges(
        "validate_icd10_code_exists",
        lambda x: check_and_route(x, "validate_icd10_clinical_match"),
        {
            "match_icd10_code": "match_icd10_code",
            "validate_icd10_clinical_match": "validate_icd10_clinical_match",
            "stopper": "stopper"
        }
    )

    # Conditional for clinical validation
    workflow.add_conditional_edges(
        "validate_icd10_clinical_match",
        lambda x: check_and_route(x, END),
        {
            "match_icd10_code": "match_icd10_code",
            END: END,
            "stopper": "stopper"
        }
    )
    workflow.set_entry_point("extract_patient_info")
    
    return workflow.compile()

@app.post("/query")
async def query_data(request: QueryRequest):
    try:
        if request.result_type == "icd10":
            # Query for ICD10 codes with specialty filtering (matching notebook)
            query = """
            select distinct icd10, dx_name, dm.specialty, count(icd10) as count 
            from som-nero-phi-jonc101.shc_core_2024.diagnosis as dx
            JOIN `som-nero-phi-jonc101.shc_core_2024.dep_map` dm
              ON dx.dept_id = dm.department_id
            where dm.specialty IN ('Infectious Diseases', 'Endocrinology', 'Hematology')
            group by icd10,dx_name,dm.specialty
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
        # Set up logging for this specific clinical case
        log_dir = setup_logging_for_case()
        
        # Get ICD10 codes with specialty filtering (matching notebook)
        query = """
        select distinct icd10, dx_name, dm.specialty, count(icd10) as count 
        from som-nero-phi-jonc101.shc_core_2024.diagnosis as dx
        JOIN `som-nero-phi-jonc101.shc_core_2024.dep_map` dm
          ON dx.dept_id = dm.department_id
        where dm.specialty IN ('Infectious Diseases', 'Endocrinology', 'Hematology')
        group by icd10,dx_name,dm.specialty
        order by count desc
        limit 10000
        """
        query_job = client.query(query)
        results = query_job.result()
        icd10_codes_df = results.to_dataframe()
        
        # Clean duplicates like in notebook
        icd10_codes_df = icd10_codes_df.drop_duplicates(subset=["icd10"])
        
        # Save to log directory like in notebook
        icd10_codes_df.to_csv(os.path.join(log_dir, "top_icd10_codes_cleaned.csv"), index=False)

        # Create the graph
        graph = create_clinical_graph(MAX_RETRIES=10)
        
        # Initialize state (matching notebook exactly)
        initial_state = {
            "clinical_question": request.clinical_question,
            "clinical_notes": request.clinical_notes,
            "icd10_codes": icd10_codes_df[["icd10"]],  # Only icd10 column like in notebook
            "patient_age": None,
            "patient_gender": None,
            "icd10_code": None,
            "rationale": None,
            "error": None,
            "retry_count": 0,
            "stopped": False
        }
        
        # Log start like in notebook
        logging.info(f"\n{'='*50}")
        logging.info("Starting new clinical case processing")
        logging.info(f"Clinical Question: {request.clinical_question}")
        logging.info(f"Clinical Notes: {request.clinical_notes}")
        logging.info(f"{'='*50}\n")
        
        # Run the graph
        config = {"recursion_limit": 100}  # Increase from default 25 to 100
        result = graph.invoke(initial_state, config=config)
        
        # Clean up the result
        clean_result = {
            "patient_age": result.get("patient_age"),
            "patient_gender": result.get("patient_gender"),
            "icd10_code": result.get("icd10_code"),
            "rationale": result.get("rationale"),
            "error": result.get("error"),
            "retry_count": result.get("retry_count"),
            "stopped": result.get("stopped")
        }
        
        # Clean NaN values for JSON serialization
        for key, value in clean_result.items():
            if pd.isna(value):
                clean_result[key] = None
        
        # Log final result like in notebook
        logging.info(f"\n{'='*50}")
        logging.info("Final Result:")
        logging.info(json.dumps(clean_result, indent=2))
        logging.info(f"{'='*50}\n")
        
        # Save result to CSV like in notebook
        result_df = pd.DataFrame([clean_result])
        result_df.to_csv(os.path.join(log_dir, "result.csv"), index=False)
        
        return clean_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_orders")
async def get_orders(request: OrderRequest):
    try:
        if request.result_type is not None and request.result_type not in ["lab", "med", "procedure"]:
            raise HTTPException(status_code=400, detail="Invalid result_type. Must be 'lab', 'med', 'procedure', or None for all types")

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
        
        # Save orders to CSV if we have a log directory set up
        if not results.empty:
            # Check if we have a log directory set up (from a previous clinical case)
            # If not, create a temporary one for this order request
            try:
                # Try to get the current log directory from the logging configuration
                current_handlers = logging.root.handlers
                log_dir = None
                for handler in current_handlers:
                    if isinstance(handler, NonEmptyFileHandler):
                        log_dir = os.path.dirname(handler.filename)
                        break
                
                if log_dir is None:
                    # No log directory set up, create a temporary one
                    log_dir = f"../logs/orders_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                    os.makedirs(log_dir, exist_ok=True)
                
                orders_filename = f"orders_{request.result_type if request.result_type else 'all'}.csv"
                results.to_csv(os.path.join(log_dir, orders_filename), index=False)
            except Exception as e:
                # If saving fails, just log it but don't fail the request
                print(f"Warning: Could not save orders to CSV: {str(e)}")
        
        return {
            "icd10_code": request.icd10_code,
            "result_type": request.result_type,
            "patient_age": request.patient_age,
            "patient_gender": request.patient_gender,
            "data": results.to_dict(orient="records")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_orders_from_file")
async def get_orders_from_file(request: OrderFromFileRequest):
    try:
        # Validate result_type
        if request.result_type is not None and request.result_type not in ["lab", "med", "procedure"]:
            raise HTTPException(status_code=400, detail="Invalid result_type. Must be 'lab', 'med', 'procedure', or None for all types")

        # Read the result.csv file
        if not os.path.exists(request.result_file_path):
            raise HTTPException(status_code=404, detail=f"Result file not found: {request.result_file_path}")
        
        result_df = pd.read_csv(request.result_file_path)
        
        # Check if the file has the expected columns
        expected_columns = ["patient_age", "patient_gender", "icd10_code", "rationale", "error", "retry_count", "stopped"]
        missing_columns = [col for col in expected_columns if col not in result_df.columns]
        if missing_columns:
            raise HTTPException(status_code=400, detail=f"Invalid result file format. Missing columns: {missing_columns}")
        
        # Get the first row (assuming single clinical case result)
        clinical_result = result_df.iloc[0].to_dict()
        
        # Clean NaN values for JSON serialization
        for key, value in clinical_result.items():
            if pd.isna(value):
                clinical_result[key] = None
        
        # Check if clinical processing was successful
        if (pd.notna(clinical_result.get("error")) and clinical_result.get("error")) or clinical_result.get("stopped"):
            raise HTTPException(status_code=400, detail=f"Clinical processing failed: {clinical_result.get('error', 'Unknown error')}")
        
        # Prepare parameters for the BigQueryAPI
        params = {
            'patient_age': clinical_result["patient_age"],
            'patient_gender': clinical_result["patient_gender"],
            'icd10_code': clinical_result["icd10_code"]
        }

        # Use the existing BigQueryAPI to get orders
        results = api.get_orders(
            params=params,
            min_patients_for_non_rare_items=request.min_patients_for_non_rare_items,
            result_type=request.result_type,
            limit=request.limit,
            year=request.year
        )
        
        # Save orders to CSV in the same directory as the result file
        if not results.empty:
            # Get the directory of the result file
            result_dir = os.path.dirname(request.result_file_path)
            
            # Use custom filename if provided, otherwise use default naming
            if request.custom_filename:
                # Ensure the filename has .csv extension
                if not request.custom_filename.endswith('.csv'):
                    orders_filename = f"{request.custom_filename}.csv"
                else:
                    orders_filename = request.custom_filename
            else:
                orders_filename = f"orders_from_file_{request.result_type if request.result_type else 'all'}.csv"
            
            orders_file_path = os.path.join(result_dir, orders_filename)
            results.to_csv(orders_file_path, index=False)
            
            # Log the save location
            logging.info(f"Orders saved to: {orders_file_path}")
        
        return {
            "result_file_path": request.result_file_path,
            "clinical_result": clinical_result,
            "result_type": request.result_type,
            "limit": request.limit,
            "min_patients_for_non_rare_items": request.min_patients_for_non_rare_items,
            "year": request.year,
            "custom_filename": request.custom_filename,
            "orders_file_path": orders_file_path if not results.empty else None,
            "data": results.to_dict(orient="records")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
    