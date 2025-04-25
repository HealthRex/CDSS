# HealthRex Recommender API

This API allows you to query common medications and procedures associated with specific diagnoses from Stanford Health Care data.

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone [repository-url]
   cd Recommender_API
   ```

2. **Install required packages**
   You can use either conda or pip:

   Using conda:
   ```bash
   conda install -c conda-forge google-cloud-bigquery pandas
   ```

   Using pip:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Cloud credentials**
   - You'll need access to the Stanford Health Care BigQuery project
   - Make sure you have the appropriate credentials file (service account key)
   - Set the environment variable:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
     ```

## Usage

The API can be run from the command line using the `run_api.py` script. Here are some examples:

### Basic Usage
```bash
python scripts/run_api.py --diagnosis J01.90 --gender Female --type med --limit 10 --year 2022
```

### Parameters
- `--diagnosis`: One or more diagnosis codes (required)
- `--gender`: Patient gender (optional, choices: 'Female', 'Male')
- `--type`: Type of results ('med' or 'proc', defaults to 'med')
- `--limit`: Number of results to return (defaults to 10)
- `--year`: Year of the dataset to use (2021-2024, defaults to 2022)
- `--output-dir`: Directory to save output files (defaults to 'csv_output')

### Examples

1. Get medications for sinusitis in female patients from 2022 data:
   ```bash
   python scripts/run_api.py --diagnosis J01.90 --gender Female --type med --limit 10 --year 2022
   ```

2. Get procedures for sinusitis in all patients from 2021 data:
   ```bash
   python scripts/run_api.py --diagnosis J01.90 --type proc --limit 15 --year 2021
   ```

3. Get medications for multiple diagnosis codes from 2023 data:
   ```bash
   python scripts/run_api.py --diagnosis J01.90 J01.91 --gender Male --type med --year 2023
   ```

### Output
- Results are saved as CSV files in the specified output directory (default: `csv_output`)
- Filenames follow the format: `[diagnosis]_[gender]_[type]_year[year]_limit[limit].csv`
  - Example: `J01.90_Female_med_year2022_limit10.csv`
- Each CSV contains:
  - Item ID (medication or procedure code)
  - Description
  - Encounter rate
  - Number of encounters
  - Total encounters
  - Number of patients
  - Total patients

### Features
- Automatic warning suppression for cleaner output
- Input validation for year and gender parameters
- Detailed query summary in the output
- Error handling with informative messages

## Project Structure
```
Recommender_API/
├── api/
│   ├── __init__.py
│   └── bigquery_api.py
├── scripts/
│   └── run_api.py
├── csv_output/
├── requirements.txt
└── README.md
```

## Troubleshooting

1. **Module not found errors**
   - Make sure all required packages are installed
   - Verify your Python environment is active

2. **Authentication errors**
   - Check that your Google Cloud credentials are properly set up
   - Verify you have access to the BigQuery project

3. **Query errors**
   - Verify that the diagnosis codes are correct
   - Check that the specified year has data available
   - Ensure gender values are either 'Male' or 'Female' if specified

## Support
For any issues or questions, please contact [your contact information]