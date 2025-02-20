# eConsult Embedding System

## Overview
This project extracts and embeds eConsult templates to enable similarity searches between clinical questions and the appropriate eConsult templates. The system uses embeddings to recommend the most relevant template based on cosine similarity scores.


## Installation
1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd eConsult-embeddings

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## How to Use
✅ 1. Extract Text from Templates
This script will extract text from all .docx templates and save them as .txt files in the data/ folder.
```bash
python3 embeddings/extract_all_templates.py
```

You will see outputs like:
```bash
✅ Extracted text saved to 'Endocrinology eConsult Checklists FINAL 4.19.22_extracted.txt'
✅ Extracted text saved to 'Cardiology eConsult Checklists_extracted.txt'
...
```

✅ 2. Run Embedding & Similarity Search
Use this script to embed all templates and run similarity searches against a clinical question.
```bash
python3 embeddings/embedding_generator.py
```

You will be prompted to enter a clinical question:
```bash
Enter a clinical question: What are the best insulin management strategies for type 2 diabetes?
```

The system will output cosine similarity scores for each template and recommend the best match:
```bash
📊 Cosine Similarity Scores:
Endocrinology eConsult Checklists FINAL 4.19.22.docx: 0.9142
Cardiology eConsult Checklists.docx: 0.4028
Neurology eConsult Checklists.docx: 0.3993
...
🏆 Suggested Template: Endocrinology eConsult Checklists FINAL 4.19.22.docx (Score: 0.9142)
```
