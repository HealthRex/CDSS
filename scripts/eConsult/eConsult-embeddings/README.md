
# eConsult Embedding System

## Overview
This project extracts and embeds eConsult templates to enable similarity searches between clinical questions and the appropriate eConsult templates. The system uses sentence embeddings and cosine similarity to recommend the most relevant template. It supports both command line use and a REST API server.

---

## Prerequisites

Make sure the following are installed:

- Python 3.8+
- [Uvicorn](https://www.uvicorn.org/) (listed in `requirements.txt`)
- [FastAPI](https://fastapi.tiangolo.com/) (listed in `requirements.txt`)
- Template files (`.docx`) placed in the `data/` directory

---

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository_url>
   cd eConsult-embeddings
   ```

2. **Create and activate a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate        # On Windows: venv\Scripts\activate
   ```

3. **Install all required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## Command Line Usage

### 1. Extract Text from Templates

This script converts all `.docx` templates in the `data/` directory into `.txt` files for embedding.

```bash
python3 embeddings/extract_all_templates.py
```

You should see outputs like:
```bash
✅ Extracted text saved to 'Endocrinology eConsult Checklists FINAL 4.19.22_extracted.txt'
✅ Extracted text saved to 'Cardiology eConsult Checklists_extracted.txt'
```

### 2. Run Embedding & Similarity Search

This script generates embeddings for each template and compares them to your input question.

```bash
python3 embeddings/embedding_generator.py
```

You will be prompted:
```
Enter a clinical question: What are the best insulin management strategies for type 2 diabetes?
```

Then it will return:
```
📊 Cosine Similarity Scores:
Endocrinology eConsult Checklists FINAL 4.19.22.docx: 0.9142
Cardiology eConsult Checklists.docx: 0.4028
Neurology eConsult Checklists.docx: 0.3993
...
🏆 Suggested Template: Endocrinology eConsult Checklists FINAL 4.19.22.docx (Score: 0.9142)
```

---

##  API Usage

### Local Development

Start the API server locally with hot reloading:

```bash
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

The following will be available:
- [http://localhost:8000](http://localhost:8000) → Health check
- [http://localhost:8000/docs](http://localhost:8000/docs) → Swagger UI (interactive testing)

### Example Usage via Swagger UI

1. Visit [http://localhost:8000/docs](http://localhost:8000/docs)
2. Expand the `POST /select-best-template` section
3. Click **"Try it out"**
4. Enter your question as:
   ```json
   {
     "question": "What are the best insulin management strategies for type 2 diabetes?"
   }
   ```
5. Click **"Execute"**

---

## Docker Deployment

### 1. Build the Docker image
```bash
docker build -t econsult-embeddings .
```

### 2. Run the container
```bash
docker run -p 8000:8000 econsult-embeddings
```

Then open [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📬 API Endpoints

### Health Check
```bash
GET /
```
Returns API status.

### Template Selection
```bash
POST /select-best-template
Content-Type: application/json

{
  "question": "What are the best insulin management strategies for type 2 diabetes?"
}
```

**Example Response:**
```json
{
  "question": "What are the best insulin management strategies for type 2 diabetes?",
  "suggested_template": "Endocrinology eConsult Checklists FINAL 4.19.22.docx",
  "similarity_scores": {
    "Endocrinology eConsult Checklists FINAL 4.19.22.docx": 0.9142,
    "Cardiology eConsult Checklists.docx": 0.4028,
    "Neurology eConsult Checklists.docx": 0.3993
  }
}
```

---

## 🧪 API Testing via Code

### Using `curl`:
```bash
curl -X POST "http://localhost:8000/select-best-template" \
     -H "Content-Type: application/json" \
     -d '{"question": "Patient has chest pain and shortness of breath"}'
```

### Using Python:
```python
import requests

response = requests.post(
    "http://localhost:8000/select-best-template",
    json={"question": "Patient has chest pain and shortness of breath"}
)
print(response.json())
```

---

## Troubleshooting Tips

- If `.txt` files are missing in `data/`, run `extract_all_templates.py` first.
- Ensure both `data/` and `embeddings/` directories exist.
- If the app crashes at startup, check for missing template files or broken paths.
- If the API returns empty results, it’s likely the embedding cache is missing or not properly generated.
