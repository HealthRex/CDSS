import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

DATA_DIR = "data"


def load_template_text(file_path):
    with open(file_path, "r") as f:
        return f.read()


def split_text(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_text(text)


def create_embeddings(texts):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return embeddings


def compute_cosine_similarity(query_embedding, template_embeddings):
    if len(template_embeddings) == 0:
        return []
    similarities = cosine_similarity([query_embedding], template_embeddings)
    return similarities


if __name__ == "__main__":
    # ✅ Load extracted .txt files
    txt_files = [f for f in os.listdir(DATA_DIR) if f.endswith("_extracted.txt")]
    all_template_data = {}

    for txt_file in txt_files:
        txt_path = os.path.join(DATA_DIR, txt_file)
        template_text = load_template_text(txt_path)
        split_texts = split_text(template_text)
        all_template_data[txt_file] = split_texts
        print(f"✅ Loaded text from {txt_file}")

    # ✅ Create embeddings for each template
    embeddings_model = create_embeddings(
        [" ".join(texts) for texts in all_template_data.values()]
    )
    all_embeddings = {}
    for txt_file, texts in all_template_data.items():
        embeddings = embeddings_model.embed_documents(texts)
        all_embeddings[txt_file] = (texts, embeddings)
        print(f"✅ Embeddings created for {txt_file}")

    # ✅ Input clinical question
    clinical_question = input("\nEnter a clinical question: ")
    question_embedding = embeddings_model.embed_query(clinical_question)

    # ✅ Compute and display cosine similarity
    print("\n📊 Cosine Similarity Scores:")
    similarity_scores = {}
    for txt_file, (texts, embeddings) in all_embeddings.items():
        similarities = compute_cosine_similarity(question_embedding, embeddings)
        if len(similarities) > 0:
            max_similarity = np.max(similarities)
            similarity_scores[txt_file] = max_similarity
            print(f"{txt_file}: {max_similarity:.4f}")
        else:
            print(f"{txt_file}: No valid similarities found.")

    # ✅ Suggest the best template
    if similarity_scores:
        best_template = max(similarity_scores, key=similarity_scores.get)
        print(
            f"\n🏆 Suggested Template: {best_template} (Score: {similarity_scores[best_template]:.4f})"
        )
    else:
        print(
            "\n⚠️ No relevant templates found. Please try a different clinical question."
        )
