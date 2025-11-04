# 🧬 eConsult Embedding Pipeline using Bio_ClinicalBERT

This repository contains a Python pipeline that generates **clinical note embeddings** for eConsult data using **Bio_ClinicalBERT**, a transformer model pretrained on biomedical and clinical text.  
The embeddings are normalized and stored in both **BigQuery** and a local `.parquet` file for downstream tasks such as similarity search, specialty referral routing, and retrieval-augmented generation (RAG).

---

## 🧠 Overview

The pipeline performs the following steps:

1. **Load environment variables**  
   Reads project configuration (BigQuery table names and project ID) from a `.env` file.

2. **Query eConsult data from BigQuery**  
   Retrieves up to two de-identified clinical notes per consult (`rank <= 2`) and groups them by patient-consult-specialty.

3. **Preprocess and combine notes**  
   Joins multiple notes per consult into a single text string separated by `[SEP]`, trims to 8,000 characters, and lightly cleans whitespace.

4. **Generate embeddings with Bio_ClinicalBERT**  
   Uses mean pooling on token representations to create a fixed-size embedding per consult.  
   Runs on GPU if available; otherwise defaults to CPU.

5. **Normalize embeddings**  
   L2-normalizes all embeddings for consistent cosine similarity calculations.

6. **Save results**  
   - Uploads embeddings and metadata to a specified BigQuery table.  
   - Saves a local copy (`econsult_embeddings.parquet`) for easy reuse.

---

## ⚙️ Environment Setup

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/econsult-embeddings.git
cd econsult-embeddings
