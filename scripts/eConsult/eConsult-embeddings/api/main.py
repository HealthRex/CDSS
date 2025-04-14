from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from embeddings.embedding_generator import run_embedding_pipeline, load_embeddings
import logging

logging.basicConfig(level=logging.DEBUG)

# Prepare document embeddings before serving requests
all_embeddings, embeddings_model = load_embeddings()

app = FastAPI(title="eConsult Embeddings API")


class ClinicalQuestion(BaseModel):
    question: str


@app.get("/")
async def read_root():
    return {"message": "eConsult Embeddings API is running 🚀"}


@app.post("/select-best-template")
def select_best_template(clinical_question: ClinicalQuestion):
    try:
        best_template, similarity_scores = run_embedding_pipeline(
            all_embeddings,
            embeddings_model,
            clinical_question.question
        )

        if best_template:
            return {
                "question": clinical_question.question,
                "suggested_template": best_template,
                "similarity_scores": similarity_scores,
            }
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No relevant templates found.")

    except Exception as e:
        if isinstance(e, HTTPException) and e.status_code == status.HTTP_404_NOT_FOUND:
            # raise 404 exception with correct code instead of 500
            raise e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
