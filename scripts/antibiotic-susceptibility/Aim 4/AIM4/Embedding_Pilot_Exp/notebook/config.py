# Configuration file for automated error checking

#  # Whether to include row-level reference pairs in the evaluation prompt
INCLUDE_REFERENCE = True
# Data source configuration
EXCEL_PATH = "../data/strictest/generated_question_set_1_saved_df.xlsx"
OUTPUT_DIR = None
if not INCLUDE_REFERENCE:
    OUTPUT_DIR = "../error_checking_updated_prompt/automated_outputs"
    LOG_FILE =OUTPUT_DIR + "/automated_processing.log"
else:
    OUTPUT_DIR = "../error_checking_updated_prompt/automated_outputs_with_reference"
    LOG_FILE = OUTPUT_DIR + "/automated_processing.log"

# Processing configuration
START_ROW = 0  # Start from first row (0-indexed)
END_ROW = None  # Process all rows (set to a number to limit processing)
DELAY_BETWEEN_CALLS = 1.0  # Seconds between API calls to avoid rate limiting
SKIP_EXISTING_FILES = True  # Skip processing if output files already exist

# Model configuration
MODEL = "gpt-4.1"  # Options: "gpt-4.1", "gemini-2.5-pro"

# Logging configuration
LOG_LEVEL = "INFO"  # Options: "DEBUG", "INFO", "WARNING", "ERROR"


# Output configuration
SAVE_INPUTS = True  # Save input data for cross-checking
SAVE_PARSER_OUTPUTS = True  # Save parser LLM outputs
SAVE_EVALUATOR_OUTPUTS = True  # Save evaluator LLM outputs
SAVE_SUMMARY = True  # Save processing summary
CREATE_ANALYSIS_DF = True  # Create analysis DataFrame

# === Reference Example Configuration ===
NUM_REFERENCE_EXAMPLES = 3 # max is 5
assert NUM_REFERENCE_EXAMPLES <= 5, "NUM_REFERENCE_EXAMPLES must be less than or equal to 5"

# Error handling
MAX_RETRIES = 3  # Maximum number of retries for API calls
RETRY_DELAY = 5.0  # Seconds to wait between retries

# Analysis configuration
SCORE_COLUMNS = [
    'clinical_accuracy_score',
    'urgency_recognition_score', 
    'professional_consultation_score',
    'sensitivity_clarity_score'
]

MESSAGE_TYPES = [
    'Appointment Request',
    'Medication Request', 
    'Test Result Inquiry',
    'Clinical Advice Request',
    'Referral Request',
    'Administrative Request',
    'General Inquiry',
    'Other'
] 