# ============================================================
# Embedding eConsult notes using Bio_ClinicalBERT (Hugging Face)
# ============================================================

import os, time, torch
import numpy as np
import pandas as pd
from tqdm import tqdm
from google.cloud import bigquery
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModel
from sklearn.preprocessing import normalize

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID")
SOURCE_TABLE = os.getenv("SOURCE_TABLE")
TARGET_TABLE = os.getenv("TARGET_TABLE")

# -----------------------------
# Initialize BigQuery client
# -----------------------------
bq = bigquery.Client(project=PROJECT_ID)

# -----------------------------
# Query BigQuery: get up to 2 notes per consult
# -----------------------------
query = f"""
SELECT 
  anon_id,
  consult_id,
  econsult_specialty,
  ARRAY_AGG(deid_note_text ORDER BY note_date ASC) AS note_texts
FROM `{SOURCE_TABLE}`
WHERE rank <= 2
  AND deid_note_text IS NOT NULL
GROUP BY anon_id, consult_id, econsult_specialty
"""
print("🔍 Querying BigQuery...")
df = bq.query(query).to_dataframe()
print(f"✅ Loaded {len(df)} consult-level rows")


# -----------------------------
# Combine multiple notes into one text block
# -----------------------------
def combine_notes(notes):
    joined = " [SEP] ".join([n for n in notes if n])
    return joined[:8000]  # trim to 8k chars for safety


df["combined_text"] = df["note_texts"].apply(combine_notes)


# -----------------------------
# Light text cleaning (no SEP removal)
# -----------------------------
def clean_text(text):
    text = text.replace("\n", " ").strip()
    text = " ".join(text.split())
    return text


df["combined_text"] = df["combined_text"].apply(clean_text)

# -----------------------------
# Load Bio_ClinicalBERT model
# -----------------------------
print("🧬 Loading Bio_ClinicalBERT...")
model_name = "emilyalsentzer/Bio_ClinicalBERT"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)
model.eval()

# Use CPU (or GPU if available)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
print(f"💻 Using device: {device}")


# -----------------------------
# Function: Generate embeddings with mean pooling
# -----------------------------
def get_embeddings_batch(text_list):
    """Generate embeddings for a list of texts (batched)."""
    inputs = tokenizer(
        text_list, return_tensors="pt", truncation=True, padding=True, max_length=512
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        last_hidden_state = outputs.last_hidden_state
        embeddings = last_hidden_state.mean(dim=1).cpu().numpy()  # mean pooling
    return embeddings


# -----------------------------
# Encode all texts in batches
# -----------------------------
batch_size = 8  # tune this for your machine (higher = faster, more memory)
texts = df["combined_text"].tolist()
all_embeddings = []

print(f"⚙️ Encoding {len(texts)} notes in batches of {batch_size}...")
for i in tqdm(range(0, len(texts), batch_size), desc="Embedding Bio_ClinicalBERT"):
    batch_texts = texts[i : i + batch_size]
    batch_embs = get_embeddings_batch(batch_texts)
    all_embeddings.extend(batch_embs.tolist())

# -----------------------------
# Normalize embeddings for cosine similarity
# -----------------------------
print("📏 Normalizing embeddings...")
emb_matrix = np.vstack(all_embeddings)
emb_matrix = normalize(emb_matrix, norm="l2")
df["embedding"] = emb_matrix.tolist()

# -----------------------------
# Save locally for reuse
# -----------------------------
local_path = "econsult_embeddings.parquet"
print(f"💾 Saving local copy to {local_path}...")
df[
    ["anon_id", "consult_id", "econsult_specialty", "embedding", "combined_text"]
].to_parquet(local_path)
print("✅ Local .parquet file saved.")

# -----------------------------
# Save results to BigQuery
# -----------------------------
schema = [
    bigquery.SchemaField("anon_id", "STRING"),
    bigquery.SchemaField("consult_id", "INTEGER"),
    bigquery.SchemaField("econsult_specialty", "STRING"),
    bigquery.SchemaField("embedding", "FLOAT64", mode="REPEATED"),
]

print(f"⬆️ Uploading embeddings to {TARGET_TABLE}...")
bq.load_table_from_dataframe(
    df[["anon_id", "consult_id", "econsult_specialty", "embedding"]],
    TARGET_TABLE,
    job_config=bigquery.LoadJobConfig(schema=schema),
).result()

print(
    "🎉 Done! Bio_ClinicalBERT embeddings successfully saved to BigQuery and local .parquet file."
)
