# app/config.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Charge les variables depuis .env
load_dotenv()

@dataclass(frozen=True)
class Settings:
    # API
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    embed_model: str = os.getenv("EMBED_MODEL", "text-embedding-3-small")

    # Stockage local
    uploads_dir: str = os.getenv("UPLOADS_DIR", "data/uploads")
    chroma_dir: str = os.getenv("CHROMA_DIR", "data/chroma")

    # RAG (paramètres simples)
    top_k: int = int(os.getenv("TOP_K", "5"))

settings = Settings()
