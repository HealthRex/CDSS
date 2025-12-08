import os, json, argparse, requests
from dotenv import load_dotenv
from google.cloud import bigquery

PROMPT = """You are an infectious diseases physician classifying bacteremia risk
for a patient getting a blood culture drawn, based on Fabre et al., 2020 (Clin Infect Dis, doi:10.1093/cid/ciaa039).

Risk definitions:
- HIGH: catheter-related bloodstream infection; meningitis/spinal infection; native septic arthritis; severe sepsis/shock; endocarditis/endovascular infection.
- INTERMEDIATE: pyelonephritis; cholangitis; cellulitis with significant comorbidities; severe pneumonia; ventilator-associated pneumonia.
- LOW: isolated fever and/or leukocytosis; non-severe cellulitis; lower UTI; post-operative fever within 48h of surgery.
- Undetermined: if the case does not fit any of the above categories.

Instructions:
- Read the note and structured EHR data if availableand return STRICT JSON only.
- Keys must be:
  - classification: one of HIGH|INTERMEDIATE|LOW|Undetermined
  - confidence: a number between 0 and 1
  - verbatim: 1–3 short quotes copied directly from the note that support your decision
  - rationale: a brief explanation of why the evidence fits the classification
"""

def get_note_from_bq(anon_id: str, note_type_desc: str, note_date: str) -> str:
    """Fetch a note from BigQuery given anon_id, type, and datetime string."""
    client = bigquery.Client()
    query = f"""
    SELECT deid_note_text
    FROM `{os.getenv('BQ_PROJECT')}.{os.getenv('BQ_DATASET')}.{os.getenv('BQ_TABLE')}`
    WHERE anon_id = @anon_id
      AND note_type_desc = @note_type_desc
      AND jittered_note_date = CAST(TIMESTAMP(@note_date) AS DATETIME)
    LIMIT 1
    """
    job = client.query(
        query,
        job_config=bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("anon_id", "STRING", anon_id),
                bigquery.ScalarQueryParameter("note_type_desc", "STRING", note_type_desc),
                bigquery.ScalarQueryParameter("note_date", "STRING", note_date),
            ]
        )
    )
    rows = list(job.result())
    return rows[0]["deid_note_text"] if rows else ""

def classify(anon_id: str, note_text: str, EHR=None):
    classify.prompt = PROMPT
    url = os.getenv("API_URL")
    headers = {
        os.getenv("API_HEADER_KEY"): os.getenv("API_KEY"),
        "Content-Type": "application/json"
    }

    question = f"{PROMPT}\n\nanon_id: {anon_id}\n\nNOTE:\n{note_text}"
    if EHR:
        question += f"structured EHR data is provided below:\n\nEHR:\n{EHR}"
    else:
        question += f"structured EHR data is not provided."
    payload = {
        "model": "gpt-5",
        "messages": [{"role": "user", "content": question}]
    }

    resp = requests.post(url, headers=headers, data=json.dumps(payload))
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]

def main():
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--anon_id", required=True, help="Patient anon_id")
    parser.add_argument("--note_type_desc", default="ED Provider Notes")
    parser.add_argument("--note_date", required=True, help="Datetime string e.g. 2023-01-08 10:12:00")
    args = parser.parse_args()

    note = get_note_from_bq(args.anon_id, args.note_type_desc, args.note_date)
    print(f"note: {note}")
    if not note:
        raise SystemExit("No note found for given parameters.")

    result = classify(args.anon_id, note)
    print(result)

if __name__ == "__main__":
    main()
