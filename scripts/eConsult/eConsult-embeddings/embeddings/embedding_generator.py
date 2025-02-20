import os
from docx import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

DATA_DIR = "data"

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    extracted_text = []
    for para in doc.paragraphs:
        if para.text.strip():
            extracted_text.append(para.text.strip())
    return extracted_text

def save_extracted_text(text_list, save_path):
    with open(save_path, "w") as f:
        for line in text_list:
            f.write(line + "\n")

def load_template_text(file_path):
    with open(file_path, "r") as f:
        return f.read()

def split_text(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_text(text)

def create_embeddings(texts):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return embeddings

def create_faiss_index(texts, embeddings):
    vector_store = FAISS.from_texts(texts, embeddings)
    return vector_store

def compute_cosine_similarity(query_embedding, template_embeddings):
    similarities = cosine_similarity([query_embedding], template_embeddings)
    return similarities

if __name__ == "__main__":
    # ✅ Extract text from all .docx files and save as .txt
    templates_dir = DATA_DIR
    docx_files = [f for f in os.listdir(templates_dir) if f.endswith('.docx')]
    
    all_template_data = {}
    
    for docx_file in docx_files:
        docx_path = os.path.join(templates_dir, docx_file)
        extracted_text = extract_text_from_docx(docx_path)

        # Save extracted text
        txt_filename = docx_file.replace(".docx", ".txt")
        txt_path = os.path.join(DATA_DIR, txt_filename)
        save_extracted_text(extracted_text, txt_path)
        print(f"✅ Extracted and saved text from {docx_file} to {txt_filename}")

        # Load saved text for embedding
        template_text = load_template_text(txt_path)
        split_texts = split_text(template_text)

        # Store for embedding and similarity search
        all_template_data[docx_file] = split_texts

    # ✅ Create embeddings for each template
    embeddings_model = create_embeddings([" ".join(texts) for texts in all_template_data.values()])
    all_embeddings = {}
    for docx_file, texts in all_template_data.items():
        embeddings = embeddings_model.embed_documents(texts)
        all_embeddings[docx_file] = (texts, embeddings)
        print(f"✅ Embeddings created for {docx_file}")

    # ✅ Input clinical question
    clinical_question = input("\nEnter a clinical question: ")
    question_embedding = embeddings_model.embed_query(clinical_question)

    # ✅ Compute and display cosine similarity for each template
    print("\n📊 Cosine Similarity Scores:")
    similarity_scores = {}
    for docx_file, (texts, embeddings) in all_embeddings.items():
        similarities = compute_cosine_similarity(question_embedding, embeddings)
        max_similarity = np.max(similarities)
        similarity_scores[docx_file] = max_similarity
        print(f"{docx_file}: {max_similarity:.4f}")

    # ✅ Suggest the best template
    best_template = max(similarity_scores, key=similarity_scores.get)
    print(f"\n🏆 Suggested Template: {best_template} (Score: {similarity_scores[best_template]:.4f})")
