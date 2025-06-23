import os
import traceback
from typing import Tuple, Dict, List

from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import marshal

DATA_DIR = os.environ.get("DATA_DIR", "data/json")


def load_template_text(file_path):
    with open(file_path, "r") as f:
        return f.read()


def split_text(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    return splitter.split_text(text)


def create_embeddings():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )
    return embeddings


def compute_cosine_similarity(query_embedding, template_embeddings):
    if len(template_embeddings) == 0:
        return []
    similarities = cosine_similarity([query_embedding], template_embeddings)
    return similarities


def run_embedding_pipeline(all_embeddings: Dict[str, Tuple[List[str], List[List[float]]]],
                           embeddings_model: HuggingFaceEmbeddings,
                           clinical_question: str):
    # ✅ Embed clinical question
    question_embedding = embeddings_model.embed_query(clinical_question)

    # ✅ Compute cosine similarity
    similarity_scores = {}
    for txt_file, (texts, embeddings) in all_embeddings.items():
        similarities = compute_cosine_similarity(question_embedding, embeddings)
        if len(similarities) > 0:
            max_similarity = np.max(similarities)
            similarity_scores[txt_file] = max_similarity
        else:
            similarity_scores[txt_file] = 0.0  # Handle empty similarities

    # ✅ Select best template
    if similarity_scores:
        best_template = max(similarity_scores, key=similarity_scores.get)
        return best_template, similarity_scores
    else:
        return None, {}


def load_embeddings():
    try:
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
        embeddings_model = create_embeddings()
        all_embeddings = {}
        for txt_file, texts in all_template_data.items():
            try:
                embeddings_file = open(os.path.join(DATA_DIR, txt_file + "_embedding.bin"), "rb")
            except FileNotFoundError:
                embeddings = embeddings_model.embed_documents(texts)
                with open(os.path.join(DATA_DIR, txt_file + "_embedding.bin"), "wb") as embeddings_file:
                    marshal.dump(embeddings, embeddings_file)
            else:
                with embeddings_file:
                    embeddings = marshal.load(embeddings_file)
            all_embeddings[txt_file] = (texts, embeddings)
            print(f"✅ Embeddings created for {txt_file}")
    except Exception as e:
        print(f"Failed to load model or curves: {str(e)}")
        print(traceback.format_exc())
        raise
    return all_embeddings, embeddings_model


def load_embeddings_json():
    try:
        # ✅ Load extracted .txt files
        json_files = [os.path.join(root, f) for root, _, files in os.walk(DATA_DIR) for f in files if f.endswith(".json")]
        all_template_data = {}

        for json_file in json_files:
            template_text = load_template_text(json_file)
            split_texts = split_text(template_text)
            all_template_data[json_file] = split_texts
            print(f"✅ Loaded text from {json_file}")

        # ✅ Create embeddings for each template
        embeddings_model = create_embeddings()
        all_embeddings = {}
        for json_file, texts in all_template_data.items():
            try:
                embeddings_file = open(json_file + "_embedding.bin", "rb")
            except FileNotFoundError:
                embeddings = embeddings_model.embed_documents(texts)
                with open(json_file + "_embedding.bin", "wb") as embeddings_file:
                    marshal.dump(embeddings, embeddings_file)
            else:
                with embeddings_file:
                    embeddings = marshal.load(embeddings_file)
            all_embeddings[json_file] = (texts, embeddings)
            print(f"✅ Embeddings created for {json_file}")
    except Exception as e:
        print(f"Failed to load model or curves: {str(e)}")
        print(traceback.format_exc())
        raise
    return all_embeddings, embeddings_model
