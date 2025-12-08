from pathlib import Path
from dotenv import load_dotenv
import os


class Config:
    def __init__(self):
        # === Load environment variables ===
        load_dotenv()

        # === Directories ===
        self.proj_root = Path(__file__).resolve().parents[1]
        self.data_dir = self.proj_root / "data"
        self.templates_dir = self.data_dir / "templates"
        self.results_dir = self.proj_root / "results"
        self.results_dir.mkdir(exist_ok=True)

        # === Models ===
        self.llm_model = "gpt-5"
        self.securegpt_url = (
            "https://apim.stanfordhealthcare.org/openai-eastus2/"
            "deployments/gpt-5/chat/completions?api-version=2024-12-01-preview"
        )

        # ✅ Load API key from .env
        self.securegpt_api_key = os.getenv("SECUREGPT_API_KEY")

        # === Evaluation ===
        self.top_k_templates = 5
