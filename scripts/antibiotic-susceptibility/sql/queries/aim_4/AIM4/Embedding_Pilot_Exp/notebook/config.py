# Configuration file for automated error checking

# Data source configuration
EXCEL_PATH = "../data/sampled_df_with_generated_questions.xlsx"
OUTPUT_DIR = "../error_checking/automated_outputs"

# Processing configuration
START_ROW = 0  # Start from first row (0-indexed)
END_ROW = None  # Process all rows (set to a number to limit processing)
DELAY_BETWEEN_CALLS = 1.0  # Seconds between API calls to avoid rate limiting
SKIP_EXISTING_FILES = True  # Skip processing if output files already exist

# Model configuration
MODEL = "gpt-4.1"  # Options: "gpt-4.1", "gemini-2.5-pro"

# Logging configuration
LOG_LEVEL = "INFO"  # Options: "DEBUG", "INFO", "WARNING", "ERROR"
LOG_FILE = "../error_checking/automated_outputs/automated_processing.log"

# Output configuration
SAVE_INPUTS = True  # Save input data for cross-checking
SAVE_PARSER_OUTPUTS = True  # Save parser LLM outputs
SAVE_EVALUATOR_OUTPUTS = True  # Save evaluator LLM outputs
SAVE_SUMMARY = True  # Save processing summary
CREATE_ANALYSIS_DF = True  # Create analysis DataFrame

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