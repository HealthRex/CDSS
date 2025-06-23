import pandas as pd
import os
import json
import requests
import time
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Any, Optional
import traceback

# Import python-dotenv for .env file support
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file in current directory or parent directory
    if not load_dotenv():  # Try current directory first
        load_dotenv("../.env")  # Try parent directory
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("Warning: python-dotenv not available. Install with: pip install python-dotenv")

# Import tqdm for progress bars
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("Warning: tqdm not available. Install with: pip install tqdm")

# Import configuration
try:
    from config import *
except ImportError:
    # Fallback configuration if config.py is not available
    EXCEL_PATH = "../data/sampled_df_with_generated_questions.xlsx"
    OUTPUT_DIR = "../error_checking/automated_outputs"
    START_ROW = 0
    END_ROW = None
    DELAY_BETWEEN_CALLS = 1.0
    MODEL = "gpt-4.1"
    LOG_LEVEL = "INFO"
    LOG_FILE = "../error_checking/automated_processing.log"
    SAVE_INPUTS = True
    SAVE_PARSER_OUTPUTS = True
    SAVE_EVALUATOR_OUTPUTS = True
    SAVE_SUMMARY = True
    CREATE_ANALYSIS_DF = True
    MAX_RETRIES = 3
    RETRY_DELAY = 5.0

# Set up logging based on config
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomatedErrorChecker:
    def __init__(self, excel_path: str = None, output_dir: str = None):
        """
        Initialize the automated error checker.
        
        Args:
            excel_path: Path to the Excel file containing the data (uses config if None)
            output_dir: Directory to store all outputs (uses config if None)
        """
        # Use config values if not provided
        self.excel_path = excel_path or EXCEL_PATH
        self.output_dir = Path(output_dir or OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different types of outputs
        self.parser_outputs_dir = self.output_dir / "parser_outputs"
        self.evaluator_outputs_dir = self.output_dir / "evaluator_outputs"
        self.inputs_dir = self.output_dir / "inputs"
        self.summary_dir = self.output_dir / "summary"
        
        # Only create directories if saving is enabled in config
        if SAVE_INPUTS:
            self.inputs_dir.mkdir(parents=True, exist_ok=True)
        if SAVE_PARSER_OUTPUTS:
            self.parser_outputs_dir.mkdir(parents=True, exist_ok=True)
        if SAVE_EVALUATOR_OUTPUTS:
            self.evaluator_outputs_dir.mkdir(parents=True, exist_ok=True)
        if SAVE_SUMMARY:
            self.summary_dir.mkdir(parents=True, exist_ok=True)
        
        # Load API key and set up headers
        self.my_key = os.getenv("HEALTHREX_API_KEY")
        if not self.my_key:
            error_msg = "HEALTHREX_API_KEY not found. "
            if DOTENV_AVAILABLE:
                error_msg += "Please create a .env file in the notebook directory or parent directory with:\n"
                error_msg += "HEALTHREX_API_KEY=your_api_key_here"
            else:
                error_msg += "Please set the HEALTHREX_API_KEY environment variable or install python-dotenv:\n"
                error_msg += "pip install python-dotenv\n"
                error_msg += "Then create a .env file with: HEALTHREX_API_KEY=your_api_key_here"
            raise ValueError(error_msg)
        
        self.headers = {
            'Ocp-Apim-Subscription-Key': self.my_key, 
            'Content-Type': 'application/json'
        }
        
        # Load data
        self.data = pd.read_excel(self.excel_path)
        logger.info(f"Loaded {len(self.data)} rows from {self.excel_path}")
        
        # Initialize results storage
        self.results = []
        self.errors = []
        
    def gpt_4_1(self, headers: Dict, prompt: str) -> str:
        """Call GPT-4.1 API"""
        url = "https://apim.stanfordhealthcare.org/openai-eastus2/deployments/gpt-4.1/chat/completions?api-version=2025-01-01-preview"
        payload = json.dumps({
            "model": "gpt-4.1", 
            "messages": [{"role": "user", "content": prompt}]
        })
        response = requests.request("POST", url, headers=headers, data=payload)
        message_content = response.json()["choices"][0]["message"]["content"]
        return message_content

    def gemini_2_5_pro(self, headers: Dict, prompt: str) -> str:
        """Call Gemini 2.5 Pro API"""
        url = "https://apim.stanfordhealthcare.org/gemini-25-pro/gemini-25-pro"
        payload = json.dumps({
            "contents": [{"role": "user", "parts": [{"text": prompt}]}]
        })
        response = requests.request("POST", url, headers=headers, data=payload)
        message_content = response.json()[0]['candidates'][0]['content']['parts'][0]['text']
        return message_content

    def parser_LLM(self, prompt: str, model: str = None) -> str:
        """Call parser LLM"""
        model = model or MODEL
        if model == "gpt-4.1":
            return self.gpt_4_1(self.headers, prompt)
        elif model == "gemini-2.5-pro":
            return self.gemini_2_5_pro(self.headers, prompt)
        else:
            raise ValueError(f"Unsupported model: {model}")

    def evaluator_LLM(self, evaluation_prompt: str, model: str = None) -> str:
        """Call evaluator LLM"""
        model = model or MODEL
        if model == "gpt-4.1":
            return self.gpt_4_1(self.headers, evaluation_prompt)
        elif model == "gemini-2.5-pro":
            return self.gemini_2_5_pro(self.headers, evaluation_prompt)
        else:
            raise ValueError(f"Unsupported model: {model}")

    def prompt_preparation(self, notes: str, patient_message: str) -> str:
        """Prepare the parsing prompt"""
        prompt = f"""You are an expert clinical data extractor. Given the unstructured clinical information below, extract and parse it into the structured JSON format provided.

  **Follow these rules carefully:**

  - **Field Fidelity:** Populate each field using only the explicit information provided in the clinical data. Use "Unknown" or "" for missing or unclear fields, per the template.
  - **Information Granularity:** For list fields (e.g., "history_of_present_illness", "past_medical_history"), enter each bullet, sentence, or clinically distinct concept as a separate item.
  - **Relevance:** Include all clinically relevant complaints or concerns discussed, including those introduced in direct messages by the patient, as symptoms/chief complaints or in new "assessment_and_plan" issues.
  - **Physical Exam:** Record each PE subfield as completely as possible. If side-specific findings are present (e.g., right/left ear), include these in the most granular field appropriate.
  - **Assessment and Plan:** Enter each active issue, including newly raised complaints from the patient, along with provider instructions, recommended follow-up, or referral steps. If a complaint is new (e.g., from a patient message, not the prior note), include your clinical response as an entry.
  - **Instructions:** General instructions (e.g., when to follow up, how to schedule) should be recorded in "general_guidelines"; pharmacy details as specified.
  - **Patient Message:** Always copy the patient's message verbatim.
  - **Additional Notes:** Include any clinical details, context, or provider action plans not clearly fitting in the other structured fields.

  **Strict Guidelines:**
  - Do not infer or hallucinate any data not clearly present.
  - Do not summarize or condense the patient's clinical complaints or history; preserve their language and details in the output.
  - Fields with multiple possible entries (e.g., medications, history, complaints) should be output as complete arrays.

  ### Clinical Information:
  {notes}

  ### Structured JSON Template:
  {{
    "provider_info": {{
      "provider_name": "",
      "department_specialty": "",
      "department_name": "",
      "department_phone": "",
      "primary_care_provider": ""
    }},
    "patient_info": {{
      "patient_name": "",
      "patient_age": ""
    }},
    "visit_info": {{
      "visit_date": "",
      "visit_type": "",
      "location": {{
        "patient": "",
        "provider": ""
      }},
      "chief_complaint": "",
      "history_of_present_illness": [],
      "active_problems": [
        {{
          "problem": "",
          "code": ""
        }}
      ],
      "past_medical_history": [
        {{
          "condition": "",
          "diagnosed": "",
          "medication": "",
          "note": ""
        }}
      ],
      "physical_exam": {{
        "general": "",
        "HEENT": "",
        "respiratory": "",
        "neurological": "",
        "cardiovascular": "",
        "gastrointestinal": "",
        "musculoskeletal": "",
        "skin": "",
        "psych": ""
      }},
      "assessment_and_plan": [
        {{
          "issue": "",
          "instructions": []
        }}
      ]
    }},
    "instructions": {{
      "general_guidelines": [],
      "pharmacy_info": {{
        "default_pharmacy": {{
          "name": "",
          "address": "",
          "phone": "",
          "fax": ""
        }}
      }}
    }},
    "additional_notes": "", 
    "patient_message": "{patient_message}"
  }}

  Respond ONLY with the completed JSON. No additional explanation or commentary."""
        return prompt

    def evaluation_prompt_preparation(self, result_json: str) -> str:
        """Prepare the evaluation prompt"""
        evaluation_prompt = f"""
  Comprehensive Evaluation Prompt
  You are a clinical quality-assessment assistant tasked with evaluating responses generated by an AI model to patient messages.

  Your evaluation involves:

  Message Categorization: Classify the patient's message into a category based on the subject title and the message content.

  Response Evaluation: Provide quantitative scores (0-10) for each defined evaluation dimension.

  Error Identification: Clearly identify specific errors, categorize them (Clinical Error vs Non-Clinical Error), assign a severity score (1-5), and localize the exact text excerpt of each error.

  📌 Scoring Definitions
  Response Quality Dimensions (Score: 0-10):
  Clinical Accuracy (0-10):

  0: Completely incorrect or dangerous advice.

  5: Partially correct but incomplete or with moderate mistakes.

  10: Completely accurate, clinically appropriate, and safe.

  Urgency Recognition (0-10):

  0: Urgency completely unrecognized or incorrectly interpreted, potentially dangerous.

  5: Moderately appropriate urgency recognition, partial omission of critical issues.

  10: Completely correct urgency identification and action advice.

  Professional Consultation Guidance (0-10):

  0: No guidance or completely incorrect guidance.

  5: Partial or incomplete professional guidance.

  10: Excellent and appropriate consultation guidance.

  Sensitivity & Clarity (0-10):

  0: Rude, dismissive, or entirely unclear.

  5: Moderately empathetic, some unclear language or slight dismissiveness.

  10: Fully empathetic, clear, and supportive language.

  Error Severity Definitions (Severity Score: 1-5):
  1: Minor issue unlikely to affect patient care or experience.

  2: Noticeable but unlikely to significantly affect clinical outcome.

  3: Significant error that could lead to patient confusion or delay in care.

  4: Serious error, potentially impacting patient health negatively.

  5: Critical or potentially lethal error requiring immediate correction.

  📑 Structured Output Template
  Return your response strictly in this JSON format:
  {{
    "message_categorization": {{
      "subject": "[provided subject title]",
      "type": "[Appointment Request | Medication Request | Test Result Inquiry | Clinical Advice Request | Referral Request | Administrative Request | General Inquiry| Other (specify)]",
      "reasoning": "[brief reasoning for the chosen category]"
    }},
    "response_evaluation": {{
      "clinical_accuracy": {{
        "score": "[0-10]",
        "reasoning": "[brief reasoning]"
      }},
      "urgency_recognition": {{
        "score": "[0-10]",
        "reasoning": "[brief reasoning]"
      }},
      "professional_consultation_guidance": {{
        "score": "[0-10]",
        "reasoning": "[brief reasoning]"
      }},
      "sensitivity_clarity": {{
        "score": "[0-10]",
        "reasoning": "[brief reasoning]"
      }}
    }},
    "errors_identified": [
      {{
        "type": "[Clinical Error | Non-Clinical Error]",
        "severity": "[1-5]",
        "description": "[brief clear description of the error]",
        "text_excerpt": "[exact problematic text excerpt from response]",
        "error_in_physician_response": "[Yes | No]",
        "reason_for_error_in_physician_response": "[exact text excerpt from actual physician response from the result_json to explain why this error is/isn't in physician response]"
      }}
    ]
  }}

  Task Instructions
  Given the structured data below, perform your evaluation exactly as specified above:
  {result_json}

  Rules:
  Focus solely on evaluating the quality, appropriateness, accuracy, and clarity of the LLM-generated response.

  Do NOT evaluate the physician's actual response (it's provided only for reference as a ground truth).

  Be precise, objective, and adhere strictly to the provided scoring scales and categories.

  If there are no identifiable errors, return "errors_identified": [].

  Do not generate additional narrative commentary outside the JSON structure.
  """
        return evaluation_prompt

    def save_input_data(self, row_idx: int, row_data: Dict[str, Any]) -> str:
        """Save input data for cross-checking"""
        if not SAVE_INPUTS:
            return ""
            
        input_file = self.inputs_dir / f"input_row_{row_idx:04d}.json"
        
        # Check if file already exists
        if input_file.exists():
            logger.info(f"Input file for row {row_idx} already exists, skipping: {input_file}")
            return str(input_file)
            
        input_data = {
            "row_index": row_idx,
            "timestamp": datetime.now().isoformat(),
            "patient_message": row_data.get("Patient Message", ""),
            "actual_response": row_data.get("Actual Response Sent to Patient", ""),
            # "notes": row_data.get("Prompt Sent to LLM", ""),
            "subject": row_data.get("Subject", ""),
            "llm_response": row_data.get("Suggested Response from LLM", ""),
            "parse_prompt": self.prompt_preparation(
                row_data.get("Prompt Sent to LLM", ""),
                row_data.get("Patient Message", "")
            )
        }
        
        with open(input_file, 'w') as f:
            json.dump(input_data, f, indent=2)
        
        return str(input_file)

    def save_parser_output(self, row_idx: int, parser_result: str) -> str:
        """Save parser LLM output"""
        if not SAVE_PARSER_OUTPUTS:
            return ""
            
        parser_file = self.parser_outputs_dir / f"parser_row_{row_idx:04d}.json"
        
        # Check if file already exists
        if parser_file.exists():
            logger.info(f"Parser file for row {row_idx} already exists, skipping: {parser_file}")
            return str(parser_file)
            
        with open(parser_file, 'w') as f:
            json.dump({"parser_output": parser_result}, f, indent=2)
        return str(parser_file)

    def save_evaluator_output(self, row_idx: int, evaluator_result: str) -> str:
        """Save evaluator LLM output"""
        if not SAVE_EVALUATOR_OUTPUTS:
            return ""
            
        evaluator_file = self.evaluator_outputs_dir / f"evaluator_row_{row_idx:04d}.json"
        
        # Check if file already exists
        if evaluator_file.exists():
            logger.info(f"Evaluator file for row {row_idx} already exists, skipping: {evaluator_file}")
            return str(evaluator_file)
            
        with open(evaluator_file, 'w') as f:
            json.dump({"evaluator_output": evaluator_result}, f, indent=2)
        return str(evaluator_file)

    def check_row_already_processed(self, row_idx: int) -> bool:
        """Check if a row has already been fully processed by checking if all output files exist"""
        # If skipping is disabled, always process
        if not SKIP_EXISTING_FILES:
            return False
            
        if not SAVE_INPUTS and not SAVE_PARSER_OUTPUTS and not SAVE_EVALUATOR_OUTPUTS:
            return False  # If no saving is enabled, always process
            
        files_to_check = []
        
        if SAVE_INPUTS:
            input_file = self.inputs_dir / f"input_row_{row_idx:04d}.json"
            files_to_check.append(input_file)
            
        if SAVE_PARSER_OUTPUTS:
            parser_file = self.parser_outputs_dir / f"parser_row_{row_idx:04d}.json"
            files_to_check.append(parser_file)
            
        if SAVE_EVALUATOR_OUTPUTS:
            evaluator_file = self.evaluator_outputs_dir / f"evaluator_row_{row_idx:04d}.json"
            files_to_check.append(evaluator_file)
        
        # Check if all required files exist
        all_exist = all(f.exists() for f in files_to_check)
        
        if all_exist:
            logger.info(f"Row {row_idx} already fully processed, skipping")
            
        return all_exist

    def process_row(self, row_idx: int, row_data: pd.Series) -> Dict[str, Any]:
        """Process a single row of data"""
        try:
            # Check if row has already been processed
            if self.check_row_already_processed(row_idx):
                # Return a result indicating the row was skipped
                return {
                    "row_index": row_idx,
                    "timestamp": datetime.now().isoformat(),
                    "status": "skipped",
                    "message": "Row already processed, files exist"
                }
            
            logger.info(f"Processing row {row_idx + 1}/{len(self.data)}")
            
            # Extract data from row
            patient_message = row_data.get("Patient Message", "")
            actual_response = row_data.get("Actual Response Sent to Patient", "")
            notes = row_data.get("Prompt Sent to LLM", "")
            subject = row_data.get("Subject", "")
            llm_response = row_data.get("Suggested Response from LLM", "")
            
            # Save input data
            input_file = self.save_input_data(row_idx, row_data)
            
            # Step 1: Parse the clinical data
            parse_prompt = self.prompt_preparation(notes, patient_message)
            parser_result = self.parser_LLM(parse_prompt)
            parser_file = self.save_parser_output(row_idx, parser_result)
            
            # Step 2: Prepare evaluation data
            try:
                result_json = json.loads(parser_result)
                result_json["message_subject"] = subject
                result_json["LLM-generated_response"] = llm_response
                result_json["actual_response"] = actual_response
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse parser result for row {row_idx}: {e}")
                result_json = {
                    "message_subject": subject,
                    "LLM-generated_response": llm_response,
                    "actual_response": actual_response,
                    "parse_error": str(e),
                    "raw_parser_output": parser_result
                }
            
            # Step 3: Evaluate the response
            evaluation_prompt = self.evaluation_prompt_preparation(json.dumps(result_json))
            evaluator_result = self.evaluator_LLM(evaluation_prompt)
            evaluator_file = self.save_evaluator_output(row_idx, evaluator_result)
            
            # Create result record
            result = {
                "row_index": row_idx,
                "timestamp": datetime.now().isoformat(),
                "input_file": input_file,
                "parser_file": parser_file,
                "evaluator_file": evaluator_file,
                "patient_message": patient_message,
                "actual_response": actual_response,
                "subject": subject,
                "llm_response": llm_response,
                "parser_result": parser_result,
                "evaluator_result": evaluator_result,
                "status": "success"
            }
            
            logger.info(f"Successfully processed row {row_idx + 1}")
            return result
            
        except Exception as e:
            error_msg = f"Error processing row {row_idx}: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            
            return {
                "row_index": row_idx,
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error_message": str(e),
                "traceback": traceback.format_exc()
            }

    def process_all_data(self, start_row: int = None, end_row: Optional[int] = None, 
                        delay_between_calls: float = None) -> None:
        """Process all data in the Excel file"""
        # Use config values if not provided
        start_row = start_row if start_row is not None else START_ROW
        end_row = end_row if end_row is not None else END_ROW
        delay_between_calls = delay_between_calls if delay_between_calls is not None else DELAY_BETWEEN_CALLS
        
        if end_row is None:
            end_row = len(self.data)
        
        logger.info(f"Starting processing from row {start_row} to {end_row}")
        logger.info(f"Using model: {MODEL}, delay: {delay_between_calls}s")
        
        # Create progress bar if tqdm is available
        if TQDM_AVAILABLE:
            pbar = tqdm(range(start_row, end_row), desc="Processing rows", unit="row")
        else:
            pbar = range(start_row, end_row)
        
        for row_idx in pbar:
            try:
                row_data = self.data.iloc[row_idx]
                result = self.process_row(row_idx, row_data)
                self.results.append(result)
                
                # Update progress bar description with current status
                if TQDM_AVAILABLE:
                    status = result.get("status", "unknown")
                    pbar.set_postfix({"status": status, "row": row_idx + 1})
                
                # Add delay to avoid rate limiting (only for new processing, not skipped rows)
                if delay_between_calls > 0 and result.get("status") != "skipped":
                    time.sleep(delay_between_calls)
                    
            except Exception as e:
                logger.error(f"Unexpected error processing row {row_idx}: {e}")
                self.errors.append({
                    "row_index": row_idx,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                
                # Update progress bar for errors
                if TQDM_AVAILABLE:
                    pbar.set_postfix({"status": "error", "row": row_idx + 1})
        
        # Close progress bar
        if TQDM_AVAILABLE:
            pbar.close()
        
        # Save summary if enabled
        if SAVE_SUMMARY:
            self.save_summary()

    def save_summary(self) -> None:
        """Save processing summary"""
        if not SAVE_SUMMARY:
            return
            
        summary = {
            "processing_timestamp": datetime.now().isoformat(),
            "total_rows": len(self.data),
            "processed_rows": len(self.results),
            "successful_rows": len([r for r in self.results if r.get("status") == "success"]),
            "error_rows": len([r for r in self.results if r.get("status") == "error"]),
            "skipped_rows": len([r for r in self.results if r.get("status") == "skipped"]),
            "errors": self.errors,
            "output_directory": str(self.output_dir),
            "configuration": {
                "excel_path": self.excel_path,
                "model": MODEL,
                "delay_between_calls": DELAY_BETWEEN_CALLS,
                "start_row": START_ROW,
                "end_row": END_ROW
            }
        }
        
        summary_file = self.summary_dir / "processing_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Save all results
        results_file = self.summary_dir / "all_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Processing complete. Summary saved to {summary_file}")
        logger.info(f"All results saved to {results_file}")
        logger.info(f"Summary: {summary['successful_rows']} successful, {summary['error_rows']} errors, {summary['skipped_rows']} skipped")

    def create_analysis_dataframe(self) -> pd.DataFrame:
        """Create a DataFrame for analysis with all results"""
        if not CREATE_ANALYSIS_DF:
            logger.info("Analysis DataFrame creation disabled in config")
            return pd.DataFrame()
            
        analysis_data = []
        skipped_count = 0
        error_count = 0
        
        # Create progress bar for analysis if tqdm is available
        if TQDM_AVAILABLE:
            pbar = tqdm(self.results, desc="Creating analysis DataFrame", unit="result")
        else:
            pbar = self.results
        
        for result in pbar:
            status = result.get("status", "unknown")
            
            if status == "success":
                try:
                    # Parse evaluator result
                    evaluator_json = json.loads(result["evaluator_result"])
                    
                    # Extract key metrics
                    row_data = {
                        "row_index": result["row_index"],
                        "subject": result["subject"],
                        "message_type": evaluator_json.get("message_categorization", {}).get("type", ""),
                        "clinical_accuracy_score": evaluator_json.get("response_evaluation", {}).get("clinical_accuracy", {}).get("score", ""),
                        "urgency_recognition_score": evaluator_json.get("response_evaluation", {}).get("urgency_recognition", {}).get("score", ""),
                        "professional_consultation_score": evaluator_json.get("response_evaluation", {}).get("professional_consultation_guidance", {}).get("score", ""),
                        "sensitivity_clarity_score": evaluator_json.get("response_evaluation", {}).get("sensitivity_clarity", {}).get("score", ""),
                        "num_errors": len(evaluator_json.get("errors_identified", [])),
                        "patient_message": result["patient_message"],
                        "actual_response": result["actual_response"],
                        "llm_response": result["llm_response"],
                        "parser_file": result["parser_file"],
                        "evaluator_file": result["evaluator_file"]
                    }
                    analysis_data.append(row_data)
                    
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse evaluator result for row {result['row_index']}")
                    continue
            elif status == "skipped":
                skipped_count += 1
                logger.debug(f"Skipping row {result['row_index']} in analysis (already processed)")
            elif status == "error":
                error_count += 1
                logger.debug(f"Skipping row {result['row_index']} in analysis (processing error)")
        
        # Close progress bar
        if TQDM_AVAILABLE:
            pbar.close()
        
        df = pd.DataFrame(analysis_data)
        
        # Log summary of analysis DataFrame creation
        logger.info(f"Analysis DataFrame created: {len(df)} rows included, {skipped_count} skipped, {error_count} errors")
        
        # Save analysis DataFrame if summary saving is enabled
        if SAVE_SUMMARY:
            analysis_file = self.summary_dir / "analysis_dataframe.csv"
            df.to_csv(analysis_file, index=False)
            logger.info(f"Analysis DataFrame saved to {analysis_file}")
        
        return df

def main():
    """Main function to run the automated processing"""
    # Initialize processor using config values
    processor = AutomatedErrorChecker()
    
    # Process all data using config values
    processor.process_all_data()
    
    # Create analysis DataFrame if enabled
    if CREATE_ANALYSIS_DF:
        analysis_df = processor.create_analysis_dataframe()
        print(f"Analysis complete. Processed {len(analysis_df)} rows successfully.")
    else:
        print(f"Processing complete. Processed {len(processor.results)} rows.")
    
    # Display summary statistics
    successful = len([r for r in processor.results if r.get("status") == "success"])
    errors = len([r for r in processor.results if r.get("status") == "error"])
    skipped = len([r for r in processor.results if r.get("status") == "skipped"])
    
    print(f"\nProcessing Summary:")
    print(f"  Successful: {successful}")
    print(f"  Errors: {errors}")
    print(f"  Skipped (already processed): {skipped}")
    print(f"  Total: {len(processor.results)}")
    
    print(f"\nResults saved in: {processor.output_dir}")
    print(f"Configuration used:")
    print(f"  Model: {MODEL}")
    print(f"  Delay: {DELAY_BETWEEN_CALLS}s")
    print(f"  Excel: {EXCEL_PATH}")
    print(f"  Output: {OUTPUT_DIR}")

if __name__ == "__main__":
    main() 