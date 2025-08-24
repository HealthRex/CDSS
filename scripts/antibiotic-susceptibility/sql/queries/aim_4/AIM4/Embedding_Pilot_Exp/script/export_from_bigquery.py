from google.cloud import bigquery
import json
import os

def export_bigquery_to_json(output_file="messages_with_embeddings_export.json"):
    client = bigquery.Client()

    query = """
    SELECT `index`, `Thread ID`, `Date Sent`, Subject, `Patient Message`, `Message Sender`, 
           `Actual Response Sent to Patient`, `Recipient Names`, `Recipient IDs`, 
           `Message Department`, `Department Specialty Title`, `embeddings`
    FROM `som-nero-phi-jonc101.rag_embedding_R01.messages_with_embeddings`
    """

    query_job = client.query(query)
    results = query_job.result()

    data = []
    for row in results:
        data.append({
            "id": row["index"],
            "thread_id": row["Thread ID"],
            "date_sent": str(row["Date Sent"]),  # convert timestamp to string
            "subject": row["Subject"],
            "patient_message": row["Patient Message"],
            "message_sender": row["Message Sender"],
            "actual_response": row["Actual Response Sent to Patient"],
            "recipient_names": row["Recipient Names"],
            "recipient_ids": row["Recipient IDs"],
            "message_department": row["Message Department"],
            "department_specialty_title": row["Department Specialty Title"],
            "embedding": row["embeddings"]
        })

    with open(output_file, "w") as f:
        json.dump(data, f)

    print(f"Exported {len(data)} records to {output_file}")

if __name__ == "__main__":
    export_bigquery_to_json()
