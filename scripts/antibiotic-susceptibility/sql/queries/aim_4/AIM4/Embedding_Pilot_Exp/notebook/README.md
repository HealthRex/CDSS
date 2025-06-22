# Automated Error Checking System

This system automates the processing of clinical data from an Excel file, performing structured parsing and evaluation of LLM-generated responses to patient messages.

## Overview

The system processes each row in the Excel file through two main steps:
1. **Parser LLM**: Extracts structured clinical information from unstructured notes
2. **Evaluator LLM**: Evaluates the quality and accuracy of LLM-generated responses

## Files

- `automated_error_checking.py`: Standalone Python script for batch processing
- `automated_error_checking_notebook.ipynb`: Jupyter notebook for interactive processing
- `config.py`: Configuration file for easy customization
- `actual_error_checking.ipynb`: Original manual processing notebook

## Setup

1. **API Key Configuration**: Set your API key using one of these methods:

   **Option A: Using .env file (Recommended)**
   ```bash
   # Create .env file with your API key
   echo "HEALTHREX_API_KEY=your_actual_api_key_here" > .env
   ```

   **Option B: Environment variable**
   ```bash
   export HEALTHREX_API_KEY="your_api_key_here"
   ```

2. **Dependencies**: Install required packages:
   ```bash
   pip install pandas requests tqdm openpyxl python-dotenv
   ```

3. **Data**: Ensure your Excel file is in the correct location (default: `../data/sampled_df_with_generated_questions.xlsx`)

## Usage

### Option 1: Jupyter Notebook (Recommended for Development)

1. Open `automated_error_checking_notebook.ipynb`
2. Modify configuration in the first cell if needed
3. Run all cells to process the data
4. View progress and results interactively

### Option 2: Python Script (Recommended for Production)

```bash
python automated_error_checking.py
```

### Option 3: Custom Configuration

1. Modify `config.py` to change settings
2. Import and use the `AutomatedErrorChecker` class:

```python
from automated_error_checking import AutomatedErrorChecker
from config import *

# Initialize processor
processor = AutomatedErrorChecker(EXCEL_PATH, OUTPUT_DIR)

# Process all data
processor.process_all_data(
    start_row=START_ROW,
    end_row=END_ROW,
    delay_between_calls=DELAY_BETWEEN_CALLS
)

# Create analysis DataFrame
analysis_df = processor.create_analysis_dataframe()
```

## Configuration

Edit `config.py` to customize:

- **Data Source**: Excel file path and output directory
- **Processing**: Start/end rows, delay between API calls
- **Model**: Choose between GPT-4.1 and Gemini 2.5 Pro
- **Output**: Control what gets saved
- **Error Handling**: Retry settings

## Output Structure

The system creates a structured output directory:

```
automated_outputs/
├── inputs/                    # Input data for each row
│   ├── input_row_0000.json
│   ├── input_row_0001.json
│   └── ...
├── parser_outputs/            # Parser LLM outputs
│   ├── parser_row_0000.json
│   ├── parser_row_0001.json
│   └── ...
├── evaluator_outputs/         # Evaluator LLM outputs
│   ├── evaluator_row_0000.json
│   ├── evaluator_row_0001.json
│   └── ...
└── summary/                   # Summary files
    ├── processing_summary.json
    ├── all_results.json
    └── analysis_dataframe.csv
```

## Data Storage Format

### Input Data (`inputs/input_row_XXXX.json`)
```json
{
  "row_index": 0,
  "timestamp": "2024-01-01T12:00:00",
  "patient_message": "...",
  "actual_response": "...",
  "notes": "...",
  "subject": "...",
  "llm_response": "...",
  "parse_prompt": "..."
}
```

### Parser Output (`parser_outputs/parser_row_XXXX.json`)
```json
{
  "parser_output": "{\"provider_info\": {...}, \"patient_info\": {...}, ...}"
}
```

### Evaluator Output (`evaluator_outputs/evaluator_row_XXXX.json`)
```json
{
  "evaluator_output": "{\"message_categorization\": {...}, \"response_evaluation\": {...}, \"errors_identified\": [...]}"
}
```

### Analysis DataFrame (`summary/analysis_dataframe.csv`)
Contains extracted metrics for easy analysis:
- Row index and subject
- Message type classification
- Quality scores (0-10) for each dimension
- Number of errors identified
- File paths for cross-referencing

## Key Features

### 1. **Comprehensive Data Storage**
- All inputs saved for cross-checking
- Raw LLM outputs preserved
- Structured analysis data

### 2. **Error Handling**
- Graceful handling of API failures
- Detailed error logging
- Retry mechanisms

### 3. **Progress Tracking**
- Real-time progress updates
- Detailed logging
- Processing summary

### 4. **Flexible Configuration**
- Easy customization via config file
- Support for different models
- Configurable processing parameters

### 5. **Analysis Ready**
- Pre-processed DataFrame for analysis
- Extracted metrics and scores
- Cross-reference capabilities

## Analysis Examples

### Load and analyze results:
```python
import pandas as pd

# Load analysis DataFrame
df = pd.read_csv("automated_outputs/summary/analysis_dataframe.csv")

# View score distributions
print(df[['clinical_accuracy_score', 'urgency_recognition_score']].describe())

# Filter by message type
clinical_requests = df[df['message_type'] == 'Clinical Advice Request']

# Find rows with errors
error_rows = df[df['num_errors'] > 0]
```

### Cross-reference with original data:
```python
import json

# Load specific evaluator output
with open("automated_outputs/evaluator_outputs/evaluator_row_0000.json") as f:
    evaluator_data = json.load(f)

# Access detailed evaluation
evaluation = json.loads(evaluator_data['evaluator_output'])
print(f"Clinical accuracy score: {evaluation['response_evaluation']['clinical_accuracy']['score']}")
```

## Troubleshooting

### Common Issues:

1. **API Key Not Set**
   - Ensure `HEALTHREX_API_KEY` environment variable is set
   - Check API key validity

2. **Rate Limiting**
   - Increase `DELAY_BETWEEN_CALLS` in config
   - Check API usage limits

3. **JSON Parsing Errors**
   - Check LLM outputs for malformed JSON
   - Review parser prompts

4. **Memory Issues**
   - Process data in smaller batches
   - Reduce `END_ROW` to limit processing

### Logs:
- Check `automated_processing.log` for detailed error information
- Review `processing_summary.json` for overall statistics

## Performance Tips

1. **Batch Processing**: Use `START_ROW` and `END_ROW` to process data in chunks
2. **Rate Limiting**: Adjust `DELAY_BETWEEN_CALLS` based on API limits
3. **Model Selection**: Choose appropriate model for your use case
4. **Error Recovery**: Use retry mechanisms for transient failures

## Security Notes

- API keys are stored in environment variables
- No sensitive data is logged
- Input data is preserved for audit trails
- All outputs are stored locally 